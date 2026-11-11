#!/usr/bin/env python3
"""Generate the project cards into assets/. The city is drawn by build_city.py.

Run from the repo root:  python3 scripts/build_assets.py
GitHub shows these through <img>, so they use no scripts or web fonts.
Motion is CSS-only and switches off for people who prefer reduced motion.
"""
from __future__ import annotations

import textwrap
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# The dusk palette shared with the city.
CORAL = "#ff7a59"
CREAM = "#f6f1e7"
MIST = "#a9a4c2"
PANEL = "#110f20"
LINE = "#2b2545"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"



def write(name: str, svg: str) -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(svg.strip() + "\n", encoding="utf-8")


def text_lines(lines: list[str], x: int, y: int, step: int, attrs: str) -> str:
    return "\n".join(
        f'<text x="{x}" y="{y + i * step}" {attrs}>{escape(line)}</text>'
        for i, line in enumerate(lines)
    )


# --------------------------------------------------------------- small cards
LANGUAGE_COLORS = {"Rust": "#dea584", "Python": "#6ea8dc", "TypeScript": "#5b9bd5", "JavaScript": "#f1e05a"}

SMALL_CARDS = [
    ("korg", "Rust", "A tamper-evident, replayable ledger of what an AI agent did and why."),
    ("korgex", "Python", "A coding agent for any model that keeps a checkable record of every change."),
    ("ningen-shikkaku", "Rust", "Secrets for AI agents that live in locked memory and vanish when your session ends."),
    ("OntologyEX", "Python", "Point an agent at a repo and get back the business it runs, every claim cited."),
    ("webmcp-anything", "TypeScript", "Turn any URL into tools an AI agent can call. One endpoint, no per-site build."),
    ("RepoLens", "JavaScript", "A Chrome extension with a straight answer on whether a repo is ready to use."),
    ("okto", "Python", "A self-healing local proxy for AI agent traffic: inspect, repair and replay."),
    ("thumper", "Rust", "The fast local runner under korgex, with warm sandboxes and self-repair."),
]


def small_card(name: str, language: str, blurb: str) -> str:
    width, height = 600, 150
    lines = textwrap.wrap(blurb, 58)[:2]
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(name)}: {escape(blurb)}">
  <title>{escape(name)}</title>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14.5" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="28" y="33" width="10" height="10" rx="2.5" fill="{CORAL}"/>
  <text x="50" y="45" font-family="{MONO}" font-size="21" font-weight="700" fill="{CREAM}">{escape(name)}</text>
  {text_lines(lines, 28, 80, 24, f'font-family="{SANS}" font-size="16.5" fill="{MIST}"')}
  <circle cx="{width - 34}" cy="38" r="5" fill="{LANGUAGE_COLORS[language]}"/>
  <text x="{width - 46}" y="43" text-anchor="end" font-family="{SANS}" font-size="14" fill="{MIST}">{language}</text>
</svg>"""


def main() -> None:
    for name, language, blurb in SMALL_CARDS:
        write(f"card-{name.lower()}.svg", small_card(name, language, blurb))
    print(f"Cards drawn: {len(SMALL_CARDS)}")


if __name__ == "__main__":
    main()
