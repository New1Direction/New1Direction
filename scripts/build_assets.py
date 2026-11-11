#!/usr/bin/env python3
"""Draw the project cards into assets/. Each card has its own small animated
illustration and the repo's live star count from data/stats.json.

Run from the repo root:  python3 scripts/build_assets.py
GitHub shows these through <img>, so they use no scripts or web fonts.
Motion is CSS-only and switches off for people who prefer reduced motion.
"""
from __future__ import annotations

import json
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
STATS = ROOT / "data" / "stats.json"

# The dusk palette shared with the city.
CORAL = "#ff7a59"
CREAM = "#f6f1e7"
MIST = "#a9a4c2"
SPARK = "#7ad7f0"
PANEL = "#110f20"
INSET = "#0b0a17"
LINE = "#2b2545"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

CARD_WIDTH, CARD_HEIGHT = 600, 176
ART_X, ART_Y, ART_W, ART_H = 426, 50, 146, 100
BLURB_WRAP = 43

LANGUAGE_COLORS = {"Rust": "#dea584", "Python": "#6ea8dc", "TypeScript": "#5b9bd5", "JavaScript": "#f1e05a"}


# Each drawing fits a 146x100 box and returns (svg, css).
def art_chain() -> tuple[str, str]:
    """korg: a chain of blocks, sealed one after another."""
    blocks = "".join(
        f'<rect class="blk" style="animation-delay:{i * 0.9:.1f}s" x="{8 + i * 48}" y="34" width="32" height="32" rx="7" fill="none" stroke="{CREAM}" stroke-width="2"/>'
        f'<rect class="seal" style="animation-delay:{i * 0.9:.1f}s" x="{17 + i * 48}" y="43" width="14" height="14" rx="3" fill="{CORAL}"/>'
        for i in range(3)
    )
    links = "".join(f'<line x1="{40 + i * 48}" y1="50" x2="{56 + i * 48}" y2="50" stroke="{MIST}" stroke-width="2"/>' for i in range(2))
    css = """
    .seal { opacity: 0; animation: seal 3.6s ease-in-out infinite; }
    .blk { animation: blk 3.6s ease-in-out infinite; }
    @keyframes seal { 0%, 8% { opacity: 0; } 20%, 82% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes blk { 0%, 8% { stroke-opacity: .35; } 20%, 82% { stroke-opacity: 1; } 100% { stroke-opacity: .35; } }"""
    return links + blocks, css


def art_checks() -> tuple[str, str]:
    """korgex: lines of work, each ticked off as it is recorded."""
    rows = "".join(
        f'<rect x="8" y="{14 + i * 22}" width="{width}" height="8" rx="4" fill="{MIST}" fill-opacity="0.45"/>'
        f'<path class="tick" style="animation-delay:{i * 0.7:.1f}s" d="M{118} {18 + i * 22} l5 5 l9 -10" fill="none" stroke="{CORAL}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        for i, width in enumerate([86, 62, 98, 74])
    )
    css = """
    .tick { stroke-dasharray: 22; stroke-dashoffset: 22; animation: tick 4.4s ease-out infinite; }
    @keyframes tick { 0%, 6% { stroke-dashoffset: 22; } 16%, 86% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: 22; } }"""
    return rows, css


def art_burn() -> tuple[str, str]:
    """ningen-shikkaku: a key on a countdown that fades when time runs out."""
    art = (
        f'<circle cx="73" cy="50" r="38" fill="none" stroke="{LINE}" stroke-width="5"/>'
        f'<circle class="ring" cx="73" cy="50" r="38" fill="none" stroke="{CORAL}" stroke-width="5" stroke-linecap="round" transform="rotate(-90 73 50)"/>'
        f'<g class="key"><circle cx="62" cy="50" r="9" fill="none" stroke="{CREAM}" stroke-width="3.2"/>'
        f'<path d="M71 50 H94 M86 50 V58 M93 50 V56" fill="none" stroke="{CREAM}" stroke-width="3.2" stroke-linecap="round"/></g>'
    )
    css = """
    .ring { stroke-dasharray: 239; animation: ring 6s linear infinite; }
    .key { animation: key 6s linear infinite; }
    @keyframes ring { 0% { stroke-dashoffset: 0; } 84%, 100% { stroke-dashoffset: 239; } }
    @keyframes key { 0%, 70% { opacity: 1; } 84%, 94% { opacity: 0; } 100% { opacity: 1; } }"""
    return art, css


def art_pulse() -> tuple[str, str]:
    """thumper: a heartbeat that keeps running."""
    beat = "M4 56 H38 L48 30 L60 78 L72 20 L84 62 L92 56 H142"
    art = (
        f'<path d="{beat}" fill="none" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>'
        f'<path class="beat" d="{beat}" fill="none" stroke="{CORAL}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    css = """
    .beat { stroke-dasharray: 70 300; animation: beat 2.4s linear infinite; }
    @keyframes beat { from { stroke-dashoffset: 70; } to { stroke-dashoffset: -300; } }"""
    return art, css


def art_graph() -> tuple[str, str]:
    """OntologyEX: a map of how the parts of a business connect."""
    nodes = [(24, 50), (62, 20), (62, 80), (104, 34), (124, 74)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (2, 4)]
    art = "".join(
        f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="{MIST}" stroke-opacity="0.55" stroke-width="1.8"/>'
        for a, b in edges
    ) + "".join(
        f'<circle class="node" style="animation-delay:{i * 0.55:.2f}s" cx="{x}" cy="{y}" r="8" fill="{CREAM}"/>'
        for i, (x, y) in enumerate(nodes)
    )
    css = f"""
    .node {{ animation: node 3.3s ease-in-out infinite; }}
    @keyframes node {{ 0%, 100% {{ fill: {CREAM}; }} 12% {{ fill: {CORAL}; }} 30% {{ fill: {CREAM}; }} }}"""
    return art, css


def art_plug() -> tuple[str, str]:
    """webmcp-anything: a web address turning into tools."""
    tools = "".join(
        f'<rect class="tool" style="animation-delay:{0.9 + i * 0.35:.2f}s" x="112" y="{16 + i * 26}" width="22" height="18" rx="5" fill="{CREAM}"/>'
        for i in range(3)
    )
    art = (
        f'<rect x="4" y="38" width="62" height="24" rx="12" fill="none" stroke="{CREAM}" stroke-width="2"/>'
        f'<circle cx="17" cy="50" r="4" fill="{SPARK}"/><rect x="26" y="47" width="30" height="6" rx="3" fill="{MIST}"/>'
        f'<path class="wire" d="M68 50 H88 M88 50 C100 50 98 25 112 25 M88 50 H112 M88 50 C100 50 98 77 112 77" fill="none" stroke="{CORAL}" stroke-width="2" stroke-linecap="round"/>'
        + tools
    )
    css = f"""
    .wire {{ stroke-dasharray: 5 7; animation: wire 1.2s linear infinite; }}
    .tool {{ animation: tool 3.6s ease-in-out infinite; }}
    @keyframes wire {{ to {{ stroke-dashoffset: -24; }} }}
    @keyframes tool {{ 0%, 100% {{ fill: {CREAM}; }} 10% {{ fill: {CORAL}; }} 28% {{ fill: {CREAM}; }} }}"""
    return art, css


def art_lens() -> tuple[str, str]:
    """RepoLens: a lens sweeping across a repo."""
    lines = "".join(
        f'<rect x="8" y="{16 + i * 20}" width="{width}" height="8" rx="4" fill="{MIST}" fill-opacity="0.45"/>'
        for i, width in enumerate([112, 84, 124, 70])
    )
    art = lines + (
        f'<g class="lens"><circle cx="34" cy="44" r="22" fill="{PANEL}" fill-opacity="0.55" stroke="{CORAL}" stroke-width="3.2"/>'
        f'<line x1="50" y1="60" x2="64" y2="76" stroke="{CORAL}" stroke-width="4.5" stroke-linecap="round"/>'
        f'<path d="M24 46 l7 7 l13 -15" fill="none" stroke="{CREAM}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>'
    )
    css = """
    .lens { animation: lens 5s ease-in-out infinite alternate; }
    @keyframes lens { from { transform: translateX(0); } to { transform: translateX(72px); } }"""
    return art, css


def art_stream() -> tuple[str, str]:
    """okto: broken packets go in one side and come out mended."""
    packets = "".join(f'<rect x="{-150 + i * 30}" y="42" width="16" height="16" rx="4"/>' for i in range(11))
    art = (
        f'<clipPath id="in"><rect x="0" y="0" width="73" height="100"/></clipPath><clipPath id="out"><rect x="73" y="0" width="73" height="100"/></clipPath>'
        f'<g clip-path="url(#in)"><g class="flow" fill="{CORAL}" transform="skewX(-14)">{packets}</g></g>'
        f'<g clip-path="url(#out)"><g class="flow" fill="{CREAM}">{packets}</g></g>'
        f'<rect x="69" y="14" width="8" height="72" rx="4" fill="{SPARK}"/>'
    )
    css = """
    .flow { animation: flow 2.4s linear infinite; }
    @keyframes flow { from { translate: 0 0; } to { translate: 60px 0; } }"""
    return art, css


CARDS = [
    ("korg", "Rust", "A tamper-evident, replayable ledger of what an AI agent did and why.", art_chain),
    ("korgex", "Python", "A coding agent for any model that keeps a checkable record of every change.", art_checks),
    ("ningen-shikkaku", "Rust", "Secrets for AI agents that live in locked memory and vanish when your session ends.", art_burn),
    ("thumper", "Rust", "The fast local runner under korgex, with warm sandboxes and self-repair.", art_pulse),
    ("OntologyEX", "Python", "Point an agent at a repo and get back the business it runs, every claim cited.", art_graph),
    ("webmcp-anything", "TypeScript", "Turn any URL into tools an AI agent can call. One endpoint, no per-site build.", art_plug),
    ("RepoLens", "JavaScript", "A Chrome extension with a straight answer on whether a repo is ready to use.", art_lens),
    ("okto", "Python", "A self-healing local proxy for AI agent traffic: inspect, repair and replay.", art_stream),
]


def load_stats() -> dict:
    try:
        return json.loads(STATS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def card(name: str, language: str, blurb: str, draw, stars: int | None) -> str:
    art, css = draw()
    lines = textwrap.wrap(blurb, BLURB_WRAP)[:3]
    text = "\n".join(
        f'<text x="28" y="{84 + i * 23}" font-family="{SANS}" font-size="16" fill="{MIST}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    star_text = "" if stars is None else f'<text x="{CARD_WIDTH - 28}" y="33" text-anchor="end" font-family="{SANS}" font-size="14" fill="{CREAM}" fill-opacity="0.85">★ {stars}</text>'
    spoken = f"{name}: {blurb} {language}." + ("" if stars is None else f" {stars} stars.")
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" role="img" aria-label="{escape(spoken)}">
  <title>{escape(name)}</title>
  <style>{css}
    {REDUCED_MOTION}
  </style>
  <rect x="0.5" y="0.5" width="{CARD_WIDTH - 1}" height="{CARD_HEIGHT - 1}" rx="16.5" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="{ART_X - 10}" y="{ART_Y - 6}" width="{ART_W + 20}" height="{ART_H + 12}" rx="12" fill="{INSET}"/>
  <text x="28" y="48" font-family="{MONO}" font-size="21" font-weight="700" fill="{CREAM}">{escape(name)}</text>
  <circle cx="{CARD_WIDTH - 148}" cy="28" r="5" fill="{LANGUAGE_COLORS[language]}"/>
  <text x="{CARD_WIDTH - 138}" y="33" font-family="{SANS}" font-size="14" fill="{MIST}">{language}</text>
  {star_text}
  {text}
  <g transform="translate({ART_X} {ART_Y})">{art}</g>
</svg>"""


def main() -> None:
    stats = load_stats()
    ASSETS.mkdir(exist_ok=True)
    for name, language, blurb, draw in CARDS:
        stars = stats.get(name, {}).get("stars")
        (ASSETS / f"card-{name.lower()}.svg").write_text(card(name, language, blurb, draw, stars).strip() + "\n", encoding="utf-8")
    print(f"Cards drawn: {len(CARDS)}")


if __name__ == "__main__":
    main()
