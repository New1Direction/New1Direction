#!/usr/bin/env python3
"""Refresh the data the city is drawn from.

- data/stats.json: stars and last-push date for each tower's repo.
- data/visitors.json: people who lit a window (one entry per GitHub login).
- data/calendar.json: the last year of daily contribution counts.
- data/extras.json: the account's join date and repo.ing's public fee figure.
- data/avatars/: a small copy of each visitor's avatar, for the ticker.
- data/votes.json: one rooftop-garden vote per visitor.

Runs in GitHub Actions. A visitor's login arrives in the VISITOR environment
variable and is checked against GitHub's own username rules before use.
An issue's title arrives in ISSUE_TITLE and is only ever compared against the
fixed list of vote titles. Nothing from an issue's body is read.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from city_config import OWNER, TOWERS

DATA = Path(__file__).resolve().parent.parent / "data"
STATS = DATA / "stats.json"
VISITORS = DATA / "visitors.json"
CALENDAR = DATA / "calendar.json"
EXTRAS = DATA / "extras.json"
VOTES = DATA / "votes.json"
AVATARS = DATA / "avatars"
HIDDEN = DATA / "hidden.txt"

LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
MAX_VISITORS = 500
API_TIMEOUT_SECONDS = 20
AVATAR_PIXELS = 48
AVATARS_KEPT = 24
MAX_AVATAR_BYTES = 60_000
REPOING_BADGE = "https://repo.ing/api/badge/1388219884"
FEES_PATTERN = re.compile(r"([0-9][0-9.,]*) SOL in indexed builder fees")
VOTE_PREFIX = "vote for "


def load_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback


def save_json(path: Path, value) -> None:
    DATA.mkdir(exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_repo(name: str) -> dict | None:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{name}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-city"},
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            repo = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"warning: could not read {name}: {error}", file=sys.stderr)
        return None
    return {
        "stars": int(repo.get("stargazers_count", 0)),
        # Day precision keeps the file from changing on every run.
        "pushed": str(repo.get("pushed_at", ""))[:10],
    }


def refreshed_stats(previous: dict) -> dict:
    """Latest stats per repo, keeping the previous value if a fetch fails."""
    stats = {}
    for tower in TOWERS:
        name = tower["repo"]
        latest = fetch_repo(name) or previous.get(name)
        if latest:
            stats[name] = latest
    return stats


CALENDAR_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_calendar() -> dict | None:
    """The last year of contributions, as {"total": n, "weeks": [[{date, count}]]}."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("warning: no token, so the contribution calendar was not refreshed", file=sys.stderr)
        return None
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": CALENDAR_QUERY, "variables": {"login": OWNER}}).encode(),
        headers={"Authorization": f"Bearer {token}", "User-Agent": "profile-city"},
    )
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            calendar = json.load(response)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        return {
            "total": int(calendar["totalContributions"]),
            "weeks": [
                [{"date": str(day["date"]), "count": int(day["contributionCount"])} for day in week["contributionDays"]]
                for week in calendar["weeks"]
            ],
        }
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError) as error:
        print(f"warning: could not read the contribution calendar: {error}", file=sys.stderr)
        return None


def hidden_logins() -> set[str]:
    try:
        lines = HIDDEN.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set()
    return {line.strip().lower() for line in lines if line.strip() and not line.startswith("#")}


def with_visitor(visitors: list[dict], login: str) -> list[dict]:
    """Add `login` once. Invalid names and repeat visits change nothing.
    App accounts such as `dependabot[bot]` fail the pattern, so they are skipped."""
    if not LOGIN_PATTERN.fullmatch(login):
        print(f"skipping visitor {login!r}: not a plain user login", file=sys.stderr)
        return visitors
    if any(v["login"].lower() == login.lower() for v in visitors):
        return visitors
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (visitors + [{"login": login, "at": today}])[-MAX_VISITORS:]


def fetch_bytes(url: str, limit: int) -> bytes | None:
    request = urllib.request.Request(url, headers={"User-Agent": "profile-city"})
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            data = response.read(limit + 1)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"warning: could not fetch {url}: {error}", file=sys.stderr)
        return None
    return data if len(data) <= limit else None


def refreshed_extras(previous: dict) -> dict:
    """Join date and repo.ing's public builder-fee figure. Old values are
    kept when a source can't be read, so the page never shows a guess."""
    extras = dict(previous)
    user = fetch_bytes(f"https://api.github.com/users/{OWNER}", 100_000)
    if user:
        try:
            extras["joined"] = str(json.loads(user)["created_at"])[:10]
        except (ValueError, KeyError):
            pass
    badge = fetch_bytes(REPOING_BADGE, 20_000)
    match = FEES_PATTERN.search(badge.decode("utf-8", "replace")) if badge else None
    if match:
        extras["repoing_fees_sol"] = match.group(1)
    return extras


def save_avatar(login: str) -> None:
    """Keep a small copy of a visitor's avatar for the ticker."""
    path = AVATARS / f"{login.lower()}.b64"
    if path.exists():
        return
    image = fetch_bytes(f"https://github.com/{login}.png?size={AVATAR_PIXELS}", MAX_AVATAR_BYTES)
    kind = "png" if image and image[:8] == b"\x89PNG\r\n\x1a\n" else "jpeg" if image and image[:2] == b"\xff\xd8" else None
    if not kind:
        return
    AVATARS.mkdir(parents=True, exist_ok=True)
    path.write_text(f"data:image/{kind};base64,{base64.b64encode(image).decode('ascii')}\n", encoding="utf-8")


def with_vote(votes: dict, login: str, title: str) -> dict:
    """Record `login`'s vote if the title names a real tower. One vote each;
    voting again moves it."""
    if not LOGIN_PATTERN.fullmatch(login) or not title.lower().startswith(VOTE_PREFIX):
        return votes
    wanted = title[len(VOTE_PREFIX):].strip().lower()
    choice = next((tower["repo"] for tower in TOWERS if tower["repo"].lower() == wanted), None)
    if choice is None:
        print("skipping vote: not one of the towers", file=sys.stderr)
        return votes
    return {**votes, login.lower(): choice}


def main() -> None:
    save_json(STATS, refreshed_stats(load_json(STATS, {})))
    calendar = fetch_calendar()
    if calendar:
        save_json(CALENDAR, calendar)

    save_json(EXTRAS, refreshed_extras(load_json(EXTRAS, {})))

    visitors = load_json(VISITORS, [])
    votes = load_json(VOTES, {})
    login = os.environ.get("VISITOR", "").strip()
    title = os.environ.get("ISSUE_TITLE", "").strip()
    if login:
        # Voting also lights a window: either way, you were here.
        visitors = with_visitor(visitors, login)
        votes = with_vote(votes, login, title)
    hidden = hidden_logins()
    visitors = [v for v in visitors if v["login"].lower() not in hidden]
    votes = {voter: choice for voter, choice in votes.items() if voter not in hidden}
    for visitor in visitors[-AVATARS_KEPT:]:
        save_avatar(visitor["login"])
    save_json(VISITORS, visitors)
    save_json(VOTES, votes)
    print(f"{len(visitors)} windows lit, {len(votes)} votes")


if __name__ == "__main__":
    main()
