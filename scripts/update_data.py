#!/usr/bin/env python3
"""Refresh the data the city is drawn from.

- data/stats.json: stars and last-push date for each tower's repo.
- data/visitors.json: people who lit a window (one entry per GitHub login).

Runs in GitHub Actions. A visitor's login arrives in the VISITOR environment
variable and is checked against GitHub's own username rules before use.
Nothing from an issue's title or body is ever read here.
"""
from __future__ import annotations

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
HIDDEN = DATA / "hidden.txt"

LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
MAX_VISITORS = 500
API_TIMEOUT_SECONDS = 20


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


def main() -> None:
    save_json(STATS, refreshed_stats(load_json(STATS, {})))

    visitors = load_json(VISITORS, [])
    login = os.environ.get("VISITOR", "").strip()
    if login:
        visitors = with_visitor(visitors, login)
    hidden = hidden_logins()
    visitors = [v for v in visitors if v["login"].lower() not in hidden]
    save_json(VISITORS, visitors)
    print(f"{len(visitors)} windows lit")


if __name__ == "__main__":
    main()
