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

# Dusk palette, carried over from the old banner's horizon.
NIGHT = "#0b0a17"
INDIGO = "#1a1430"
PLUM = "#43203a"
EMBER = "#c24a33"
CORAL = "#ff7a59"
CREAM = "#f6f1e7"
MIST = "#a9a4c2"
SPARK = "#7ad7f0"
SAGE = "#5b7768"
SAGE_DARK = "#33473c"
PANEL = "#110f20"
LINE = "#2b2545"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def write(name: str, svg: str) -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(svg.strip() + "\n", encoding="utf-8")


def text_lines(lines: list[str], x: int, y: int, step: int, attrs: str) -> str:
    return "\n".join(
        f'<text x="{x}" y="{y + i * step}" {attrs}>{escape(line)}</text>'
        for i, line in enumerate(lines)
    )


# ------------------------------------------------------------ flagship cards
def repoing() -> str:
    width, height = 600, 360
    # A market chart drawn in the same cells as the skyline.
    points = [(40, 300), (96, 286), (150, 292), (204, 262), (258, 270), (312, 232), (366, 240), (420, 196), (474, 206), (528, 158), (560, 142)]
    path = "M" + " L".join(f"{x},{y}" for x, y in points)
    area = path + f" L560,{height} L40,{height} Z"
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{CREAM}"/>' for x, y in points[1:-1:2])
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="repo.ing: the market layer for open source. Launch a market for any public GitHub repo. Every trade pays the builders.">
  <title>repo.ing</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{INDIGO}"/><stop offset="1" stop-color="{NIGHT}"/></linearGradient>
    <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CORAL}" stop-opacity="0.34"/><stop offset="1" stop-color="{CORAL}" stop-opacity="0"/></linearGradient>
    <clipPath id="c"><rect width="{width}" height="{height}" rx="18"/></clipPath>
  </defs>
  <style>
    .line {{ stroke-dasharray: 720; animation: draw 6s ease-in-out infinite; }}
    .tip {{ animation: pulse 2s ease-in-out infinite; transform-origin: 560px 142px; }}
    @keyframes draw {{ 0% {{ stroke-dashoffset: 720; }} 45%, 100% {{ stroke-dashoffset: 0; }} }}
    @keyframes pulse {{ 0%, 100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(2.1); opacity: .25; }} }}
    {REDUCED_MOTION}
  </style>
  <g clip-path="url(#c)">
    <rect width="{width}" height="{height}" fill="url(#bg)"/>
    <path d="{area}" fill="url(#fill)"/>
    <path class="line" d="{path}" fill="none" stroke="{CORAL}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    {dots}
    <circle class="tip" cx="560" cy="142" r="6" fill="{CORAL}"/>
    <circle cx="560" cy="142" r="5" fill="{CREAM}"/>
    <text x="40" y="74" font-family="{SANS}" font-size="44" font-weight="800" fill="{CREAM}" letter-spacing="-1.6">repo.ing</text>
    <text x="40" y="110" font-family="{SANS}" font-size="20" font-weight="600" fill="{CORAL}">The market layer for open source.</text>
    {text_lines(["Launch a market for any public GitHub repo.", "Every trade pays the builders."], 40, 144, 25, f'font-family="{SANS}" font-size="17" fill="{CREAM}" fill-opacity="0.78"')}
    <text x="40" y="332" font-family="{MONO}" font-size="14" fill="{MIST}">repo.ing</text>
    <text x="560" y="332" text-anchor="end" font-family="{MONO}" font-size="14" fill="{MIST}">live on Solana</text>
  </g>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="17.5" fill="none" stroke="{LINE}"/>
</svg>"""


def ohiyo() -> str:
    width, height = 600, 360

    def bubble(x: int, y: int, w: int, fill: str, cls: str, label: str, color: str) -> str:
        return (
            f'<g class="b {cls}"><rect x="{x}" y="{y}" width="{w}" height="38" rx="19" fill="{fill}"/>'
            f'<text x="{x + 18}" y="{y + 25}" font-family="{SANS}" font-size="16" fill="{color}">{escape(label)}</text></g>'
        )

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Ohiyo: group chat that feels like home. Free, open source and self-hostable, with text, voice, video and screen share.">
  <title>Ohiyo</title>
  <defs><clipPath id="c"><rect width="{width}" height="{height}" rx="18"/></clipPath></defs>
  <style>
    .b {{ animation: pop 7s ease-in-out infinite; transform-box: fill-box; transform-origin: 0 100%; }}
    .b2 {{ animation-delay: .8s; }} .b3 {{ animation-delay: 1.6s; }}
    .d {{ animation: hop 1.2s ease-in-out infinite; transform-box: fill-box; }}
    .d2 {{ animation-delay: .15s; }} .d3 {{ animation-delay: .3s; }}
    @keyframes pop {{ 0% {{ opacity: 0; transform: scale(.6); }} 8%, 100% {{ opacity: 1; transform: scale(1); }} }}
    @keyframes hop {{ 0%, 60%, 100% {{ transform: translateY(0); }} 30% {{ transform: translateY(-5px); }} }}
    {REDUCED_MOTION}
  </style>
  <g clip-path="url(#c)">
    <rect width="{width}" height="{height}" fill="{CREAM}"/>
    <circle cx="560" cy="330" r="150" fill="{SAGE}" fill-opacity="0.12"/>
    <text x="40" y="74" font-family="{SANS}" font-size="44" font-weight="800" fill="{SAGE_DARK}" letter-spacing="-1.6">Ohiyo</text>
    <text x="40" y="110" font-family="{SANS}" font-size="20" font-weight="600" fill="{SAGE}">Group chat that feels like home.</text>
    {text_lines(["Free, open source and self-hostable.", "Text, voice, video and screen share."], 40, 144, 25, f'font-family="{SANS}" font-size="17" fill="{SAGE_DARK}" fill-opacity="0.8"')}
    {bubble(300, 196, 196, "#ffffff", "b1", "movie night at 8?", SAGE_DARK)}
    {bubble(366, 244, 194, SAGE, "b2", "bringing snacks!", CREAM)}
    <g class="b b3"><rect x="300" y="292" width="76" height="38" rx="19" fill="#ffffff"/>
      <circle class="d" cx="324" cy="311" r="4.5" fill="{SAGE}"/><circle class="d d2" cx="338" cy="311" r="4.5" fill="{SAGE}"/><circle class="d d3" cx="352" cy="311" r="4.5" fill="{SAGE}"/></g>
    <text x="40" y="332" font-family="{MONO}" font-size="14" fill="{SAGE}">ohiyo.gg</text>
  </g>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="17.5" fill="none" stroke="#dcd5c4"/>
</svg>"""


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
    write("repoing.svg", repoing())
    write("ohiyo.svg", ohiyo())
    for name, language, blurb in SMALL_CARDS:
        write(f"card-{name.lower()}.svg", small_card(name, language, blurb))
    print(f"Cards drawn: {2 + len(SMALL_CARDS)}")


if __name__ == "__main__":
    main()
