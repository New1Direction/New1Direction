#!/usr/bin/env python3
"""Draw the street under the towers, with traffic, and the "recently shipped"
feed of real commits from data/shipped.json.

Run from the repo root:  python3 scripts/build_street.py
"""
from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path

from city_config import THEMES

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SHIPPED = ROOT / "data" / "shipped.json"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

WIDTH = 1200
STREET_HEIGHT = 46
FEED_HEIGHT = 62
SECONDS_PER_LINE = 4

# (lane y, length, seconds to cross, start delay, drives right?, body colour key)
VEHICLES = [
    (10, 34, 13, 0.0, True, "accent"),
    (10, 26, 17, -6.0, True, "spark"),
    (10, 58, 21, -11.0, True, "soft"),      # a bus
    (27, 30, 15, -3.0, False, "ink"),
    (27, 26, 11, -8.0, False, "accent"),
    (27, 34, 19, -14.0, False, "spark"),
]


def vehicle(theme: dict, index: int, lane: int, length: int, seconds: int, delay: float, heads_right: bool, color: str, is_night: bool) -> str:
    front = length if heads_right else 0
    back = 0 if heads_right else length
    beam_to = front + (60 if heads_right else -60)
    beam = (
        f'<path d="M{front} 2 L{beam_to} -5 L{beam_to} 16 L{front} 9 Z" fill="#fff3c4" fill-opacity="0.16"/>'
        if is_night else ""
    )
    return (
        f'<g class="v {"right" if heads_right else "left"}" style="animation-duration:{seconds}s;animation-delay:{delay}s">'
        f'<g transform="translate(0 {lane})">{beam}'
        f'<rect width="{length}" height="11" rx="4" fill="{theme[color]}"/>'
        f'<rect x="{length * 0.28:.0f}" y="2" width="{length * 0.44:.0f}" height="4" rx="2" fill="{theme["cell_a"]}" fill-opacity="0.75"/>'
        f'<circle cx="{front + (-2 if heads_right else 2)}" cy="5.5" r="1.8" fill="#fff3c4"/>'
        f'<circle cx="{back + (2 if heads_right else -2)}" cy="5.5" r="1.6" fill="#ff4d4d"/>'
        f"</g></g>"
    )


def street(theme_name: str) -> str:
    theme = THEMES[theme_name]
    is_night = theme_name == "dark"
    dashes = "".join(f'<rect x="{x}" y="22" width="22" height="2" rx="1" fill="{theme["soft"]}" fill-opacity="0.5"/>' for x in range(8, WIDTH, 52))
    traffic = "".join(vehicle(theme, i, *spec, is_night) for i, spec in enumerate(VEHICLES))
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{STREET_HEIGHT}" viewBox="0 0 {WIDTH} {STREET_HEIGHT}" role="img" aria-label="A street with traffic running under the towers.">
  <title>The street</title>
  <defs><clipPath id="road"><rect width="{WIDTH}" height="{STREET_HEIGHT}" rx="10"/></clipPath></defs>
  <style>
    .v {{ animation: linear infinite; }}
    .right {{ animation-name: right; }}
    .left {{ animation-name: left; }}
    @keyframes right {{ from {{ transform: translateX(-130px); }} to {{ transform: translateX({WIDTH + 70}px); }} }}
    @keyframes left {{ from {{ transform: translateX({WIDTH + 70}px); }} to {{ transform: translateX(-130px); }} }}
    {REDUCED_MOTION}
  </style>
  <g clip-path="url(#road)">
    <rect width="{WIDTH}" height="{STREET_HEIGHT}" fill="{theme["cell_a"]}"/>
    <rect width="{WIDTH}" height="1.5" fill="{theme["ground"]}"/>
    <rect y="{STREET_HEIGHT - 1.5}" width="{WIDTH}" height="1.5" fill="{theme["ground"]}"/>
    {dashes}
    {traffic}
  </g>
</svg>"""


def how_long_ago(when: str, today: date) -> str:
    try:
        days = (today - date.fromisoformat(when)).days
    except ValueError:
        return ""
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 14:
        return f"{days} days ago"
    if days < 60:
        return f"{days // 7} weeks ago"
    return f"{days // 30} months ago"


def feed(theme_name: str, commits: list[dict], today: date) -> str:
    """The latest commits, shown one at a time."""
    theme = THEMES[theme_name]
    cycle = max(1, len(commits)) * SECONDS_PER_LINE
    visible = 100 / max(1, len(commits))
    lines = "".join(
        f'<g class="line" style="animation-delay:{i * SECONDS_PER_LINE}s">'
        f'<text x="212" y="38" font-family="{MONO}" font-size="16" font-weight="700" fill="{theme["accent"]}">{escape(c["repo"])}</text>'
        f'<text x="{224 + len(c["repo"]) * 9.8:.0f}" y="38" font-family="{SANS}" font-size="16.5" fill="{theme["ink"]}">{escape(c["subject"])}</text>'
        f'<text x="{WIDTH - 26}" y="38" text-anchor="end" font-family="{MONO}" font-size="13" fill="{theme["soft"]}">{how_long_ago(c["date"], today)}</text>'
        f"</g>"
        for i, c in enumerate(commits)
    )
    spoken = "Recently shipped: " + "; ".join(f'{c["repo"]}: {c["subject"]}' for c in commits)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{FEED_HEIGHT}" viewBox="0 0 {WIDTH} {FEED_HEIGHT}" role="img" aria-label="{escape(spoken)}">
  <title>Recently shipped</title>
  <style>
    .line {{ opacity: 0; animation: show {cycle}s ease-in-out infinite; }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes show {{ 0% {{ opacity: 0; transform: translateY(8px); }} {visible * 0.12:.1f}% {{ opacity: 1; transform: none; }} {visible * 0.9:.1f}% {{ opacity: 1; transform: none; }} {visible:.1f}%, 100% {{ opacity: 0; transform: translateY(-8px); }} }}
    @keyframes blink {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: 0; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{FEED_HEIGHT - 1}" rx="16.5" fill="{theme["cell_a"]}" fill-opacity="0.55" stroke="{theme["ground"]}"/>
  <text x="26" y="38" font-family="{MONO}" font-size="15" fill="{theme["soft"]}">recently shipped</text>
  <rect class="cursor" x="186" y="22" width="9" height="20" rx="2" fill="{theme["accent"]}"/>
  {lines}
</svg>"""


def main() -> None:
    try:
        commits = json.loads(SHIPPED.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        commits = []
    ASSETS.mkdir(exist_ok=True)
    today = date.today()
    for theme_name in THEMES:
        (ASSETS / f"street-{theme_name}.svg").write_text(street(theme_name).strip() + "\n", encoding="utf-8")
        if commits:
            (ASSETS / f"feed-{theme_name}.svg").write_text(feed(theme_name, commits, today).strip() + "\n", encoding="utf-8")
    print(f"Street drawn, feed has {len(commits)} commits")


if __name__ == "__main__":
    main()
