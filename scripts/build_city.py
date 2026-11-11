#!/usr/bin/env python3
"""Draw the living city: a sky with a headline made of lights, one tower per
repo, and a ticker of the people who lit a window.

Run from the repo root:  python3 scripts/build_city.py
Each piece is drawn twice, as night (dark theme) and dawn (light theme).
The art is plain SVG with CSS motion, which GitHub shows through <img>.
"""
from __future__ import annotations

import json
import math
from datetime import date
from html import escape
from pathlib import Path

from city_config import THEMES, TOWERS
from pixelfont import pixel_cells

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

ACTIVE_WITHIN_DAYS = 30
TICKER_NAMES = 24

HEADLINE = "i like computers"


def load(name: str, fallback):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback


def write(name: str, svg: str) -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(svg.strip() + "\n", encoding="utf-8")


def scatter(*parts: int) -> int:
    """A repeatable 0-99 value, so the same data always draws the same city."""
    value = 17
    for part in parts:
        value = (value * 131 + part * 73 + 29) % 9973
    return value % 100


# ------------------------------------------------------------------- the sky
def sky(theme_name: str) -> str:
    theme = THEMES[theme_name]
    width, height = 1200, 330
    is_night = theme_name == "dark"
    top, upper, lower, horizon = theme["sky"]
    headline, end_x = pixel_cells(HEADLINE, 64, 86, 11.2, theme["ink"])
    stars = "".join(
        f'<circle class="st st{i % 3}" cx="{(i * 197 + 40) % width}" cy="{14 + (i * 83) % 150}" '
        f'r="{1 + (i % 3) * 0.45:.2f}" fill="{theme["orb"]}"/>'
        for i in range(46)
    ) if is_night else ""
    drifting = (
        # Night: slow aurora ribbons. Dawn: soft clouds.
        f'<g filter="url(#blur)" opacity="0.5">'
        f'<ellipse class="au au1" cx="860" cy="70" rx="330" ry="34" fill="{theme["spark"]}"/>'
        f'<ellipse class="au au2" cx="1010" cy="118" rx="270" ry="26" fill="{theme["accent"]}"/>'
        f'<ellipse class="au au3" cx="700" cy="40" rx="240" ry="20" fill="#9b8cff"/></g>'
        if is_night else
        f'<g filter="url(#blur)" opacity="0.85">'
        f'<ellipse class="au au1" cx="900" cy="80" rx="210" ry="26" fill="#ffffff"/>'
        f'<ellipse class="au au2" cx="1050" cy="140" rx="170" ry="20" fill="#ffffff"/>'
        f'<ellipse class="au au3" cx="700" cy="46" rx="150" ry="16" fill="#ffffff"/></g>'
    )
    shooting = (
        f'<g class="sh sh1"><line x1="0" y1="0" x2="-90" y2="-26" stroke="{theme["orb"]}" stroke-width="2.2" stroke-linecap="round" stroke-opacity="0.9"/></g>'
        f'<g class="sh sh2"><line x1="0" y1="0" x2="-70" y2="-20" stroke="{theme["spark"]}" stroke-width="1.8" stroke-linecap="round" stroke-opacity="0.9"/></g>'
        if is_night else ""
    )
    orb = (
        f'<circle cx="1118" cy="62" r="26" fill="{theme["orb"]}"/><circle cx="1129" cy="55" r="23" fill="{top}"/>'
        if is_night else
        f'<circle class="sun" cx="1040" cy="250" r="64" fill="{theme["orb"]}"/>'
    )
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="i like computers. ares builds open source that earns, chat that feels like home, and AI agents that keep their receipts.">
  <title>i like computers</title>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{top}"/><stop offset="0.45" stop-color="{upper}"/>
      <stop offset="0.8" stop-color="{lower}"/><stop offset="1" stop-color="{horizon}"/>
    </linearGradient>
    <linearGradient id="melt" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff"/><stop offset="0.76" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="m"><rect width="{width}" height="{height}" rx="20" fill="url(#melt)"/></mask>
    <filter id="blur" x="-30%" y="-200%" width="160%" height="500%"><feGaussianBlur stdDeviation="26"/></filter>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{theme["glow"]}" stop-opacity="0.6"/><stop offset="1" stop-color="{theme["glow"]}" stop-opacity="0"/></radialGradient>
  </defs>
  <style>
    .px {{ animation: sweep 7s ease-in-out infinite; }}
    .st {{ animation: twinkle 4s ease-in-out infinite; }}
    .st1 {{ animation-delay: -1.4s; }} .st2 {{ animation-delay: -2.7s; }}
    .au {{ animation: drift 18s ease-in-out infinite alternate; }}
    .au2 {{ animation-duration: 24s; animation-direction: alternate-reverse; }} .au3 {{ animation-duration: 30s; }}
    .sh {{ opacity: 0; animation: shoot 11s linear infinite; }}
    .sh2 {{ animation-delay: 6.2s; animation-duration: 14s; }}
    .sun {{ animation: breathe 9s ease-in-out infinite; transform-origin: 1040px 250px; }}
    .caret {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes sweep {{ 0%, 14%, 100% {{ fill: {theme["ink"]}; }} 6% {{ fill: {theme["accent"]}; }} }}
    @keyframes twinkle {{ 0%, 100% {{ opacity: .8; }} 50% {{ opacity: .12; }} }}
    @keyframes drift {{ from {{ transform: translateX(-70px); }} to {{ transform: translateX(70px); }} }}
    @keyframes shoot {{ 0% {{ opacity: 0; transform: translate(380px, -10px); }} 2% {{ opacity: 1; }} 9% {{ opacity: 0; transform: translate(900px, 150px); }} 100% {{ opacity: 0; transform: translate(900px, 150px); }} }}
    @keyframes breathe {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.06); }} }}
    @keyframes blink {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: 0; }} }}
    {REDUCED_MOTION}
  </style>
  <g mask="url(#m)">
    <rect width="{width}" height="{height}" fill="url(#sky)"/>
    <circle cx="{1118 if is_night else 1040}" cy="{62 if is_night else 250}" r="{110 if is_night else 150}" fill="url(#halo)"/>
    {drifting}
    {stars}
    {shooting}
    {orb}
    <text x="64" y="58" font-family="{MONO}" font-size="16" fill="{theme["soft"]}" letter-spacing="0.6">ares / New1Direction</text>
    {headline}
    <rect class="caret" x="{end_x + 2:.1f}" y="86" width="9" height="76" rx="2.5" fill="{theme["accent"]}"/>
    <text x="64" y="206" font-family="{SANS}" font-size="22" fill="{theme["ink"]}" fill-opacity="0.88">Open source that earns. Chat that feels like home.</text>
    <text x="64" y="236" font-family="{SANS}" font-size="22" fill="{theme["ink"]}" fill-opacity="0.88">AI agents that keep their receipts.</text>
  </g>
</svg>"""


# ---------------------------------------------------------------- the towers
def tower_rows(stars: int, is_flagship: bool) -> int:
    """Taller with more stars. The sign needs at least ten floors to fit."""
    rows = 10 + round(2.6 * math.log2(1 + stars)) + (3 if is_flagship else 0)
    return max(10, min(19, rows))


def is_active(pushed: str, today: date) -> bool:
    try:
        return (today - date.fromisoformat(pushed)).days <= ACTIVE_WITHIN_DAYS
    except ValueError:
        return False


def tower(theme_name: str, index: int, config: dict, stats: dict, guest_windows: int, today: date) -> str:
    theme = THEMES[theme_name]
    name = config["repo"]
    is_flagship = bool(config.get("flagship"))
    stars = int(stats.get("stars", 0))
    width, height, ground_y = 100, 330, 296
    columns, pitch, cell = 5, 14, 11
    rows = tower_rows(stars, is_flagship)
    left = 8
    top = ground_y - rows * pitch

    slots = [(row, col) for row in range(rows) for col in range(columns)]
    ranked = sorted(slots, key=lambda slot: scatter(index, slot[0], slot[1], 7))
    star_lit = set(ranked[: min(len(slots) // 3, 2 + stars * 2)])
    guest_lit = set(sorted(
        (slot for slot in slots if slot not in star_lit),
        key=lambda slot: scatter(index, slot[1], slot[0], 3),
    )[:guest_windows])

    cells = []
    for row, col in slots:
        x = left + col * pitch
        y = ground_y - (row + 1) * pitch
        delay = scatter(index, row, col) % 4
        if (row, col) in star_lit:
            cells.append(f'<rect class="w w{delay}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.4" fill="{theme["lit_star"]}"/>')
        elif (row, col) in guest_lit:
            cells.append(f'<rect class="w w{delay}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.4" fill="{theme["lit_guest"]}"/>')
        else:
            shade = theme["cell_a"] if (row + col) % 2 else theme["cell_b"]
            cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.4" fill="{shade}"/>')

    center = left + (columns * pitch - (pitch - cell)) / 2
    spire = 22 if is_flagship else 12
    beacon = (
        f'<circle class="beacon" cx="{center}" cy="{top - spire - 3}" r="3.2" fill="{theme["accent"]}"/>'
        if is_active(stats.get("pushed", ""), today) else ""
    )
    sign_color = theme["accent"] if is_flagship else theme["ink"]
    sign_x = left + columns * pitch + 13
    label = f"{name}: {stars} star{'' if stars == 1 else 's'}" + (", updated this month" if beacon else "")
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
  <title>{escape(name)}</title>
  <style>
    .w {{ animation: glow 5s ease-in-out infinite; }}
    .w1 {{ animation-delay: -1.3s; }} .w2 {{ animation-delay: -2.6s; }} .w3 {{ animation-delay: -3.9s; }}
    .beacon {{ animation: beacon 1.6s ease-in-out infinite; }}
    .sign {{ animation: neon 6s steps(1) infinite; animation-delay: -{index * 0.7:.1f}s; }}
    @keyframes glow {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .3; }} }}
    @keyframes beacon {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .15; }} }}
    @keyframes neon {{ 0%, 100% {{ opacity: 1; }} 91% {{ opacity: .35; }} 93% {{ opacity: 1; }} 95% {{ opacity: .5; }} 97% {{ opacity: 1; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="{center - 1}" y="{top - spire}" width="2" height="{spire}" fill="{theme["ground"]}"/>
  {beacon}
  {''.join(cells)}
  <text class="sign" transform="translate({sign_x} {ground_y - 4}) rotate(-90)" font-family="{MONO}" font-size="12.5" font-weight="700" letter-spacing="0.8" fill="{sign_color}">{escape(name)}</text>
  <rect x="0" y="{ground_y}" width="{width}" height="2" fill="{theme["ground"]}"/>
  <text x="{center}" y="{ground_y + 22}" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{theme["soft"]}">★ {stars}</text>
</svg>"""


def share_guest_windows(total: int, towers: int) -> list[int]:
    """Spread visitor windows across the towers, one at a time."""
    return [total // towers + (1 if i < total % towers else 0) for i in range(towers)]


# ---------------------------------------------------------------- the ticker
def ticker(theme_name: str, visitors: list[dict]) -> str:
    theme = THEMES[theme_name]
    width, height = 1200, 46
    count = len(visitors)
    if count == 0:
        message = "No windows lit yet. Be the first to light one."
    else:
        names = "   ".join(f"@{v['login']}" for v in reversed(visitors[-TICKER_NAMES:]))
        message = f"{count} window{'' if count == 1 else 's'} lit by visitors   ·   latest:   {names}"
    # Rough width of the text, so the loop is seamless for any length.
    run = max(width, int(len(message) * 9.4) + 120)
    line = f'<text y="29" font-family="{MONO}" font-size="15" fill="{theme["ink"]}" fill-opacity="0.9">{escape(message)}</text>'
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(message)}">
  <title>Windows lit by visitors</title>
  <defs><clipPath id="c"><rect x="44" width="{width - 60}" height="{height}"/></clipPath></defs>
  <style>
    .run {{ animation: scroll {max(18, run // 55)}s linear infinite; }}
    .dot {{ animation: pulse 1.8s ease-in-out infinite; }}
    @keyframes scroll {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{run}px); }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="22.5" fill="{theme["cell_a"]}" fill-opacity="0.55" stroke="{theme["ground"]}"/>
  <circle class="dot" cx="24" cy="23" r="5" fill="{theme["lit_guest"] if count else theme["accent"]}"/>
  <g clip-path="url(#c)"><g class="run">
    <g transform="translate(52 0)">{line}</g>
    <g transform="translate({52 + run} 0)">{line}</g>
  </g></g>
</svg>"""


def main() -> None:
    stats = load("stats.json", {})
    visitors = load("visitors.json", [])
    today = date.today()
    shares = share_guest_windows(len(visitors), len(TOWERS))
    for theme_name in THEMES:
        write(f"sky-{theme_name}.svg", sky(theme_name))
        write(f"ticker-{theme_name}.svg", ticker(theme_name, visitors))
        for index, config in enumerate(TOWERS):
            slug = config["repo"].lower().replace(".", "-")
            write(
                f"tower-{slug}-{theme_name}.svg",
                tower(theme_name, index, config, stats.get(config["repo"], {}), shares[index], today),
            )
    print(f"City drawn: {len(TOWERS)} towers, {len(visitors)} visitor windows")


if __name__ == "__main__":
    main()
