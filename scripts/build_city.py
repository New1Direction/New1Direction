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
GARDEN_GREENS = ["#5fbf7a", "#3f9d63", "#2f7a4d"]

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
def season_of(today: date) -> str:
    """Northern-hemisphere seasons by calendar month."""
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(today.month, "autumn")


def is_celebration(today: date, joined: str) -> bool:
    """New Year's Day, or the anniversary of joining GitHub."""
    if (today.month, today.day) == (1, 1):
        return True
    try:
        start = date.fromisoformat(joined)
    except ValueError:
        return False
    return (today.month, today.day) == (start.month, start.day) and today.year > start.year


def weather(theme: dict, today: date, is_night: bool) -> tuple[str, str]:
    """Snow, petals, fireflies or leaves, depending on the season."""
    season = season_of(today)
    count = 26
    pieces = []
    for i in range(count):
        x = 30 + (i * 173) % 1140
        delay = -(i * 0.83) % 11
        duration = 9 + (i * 7) % 6
        style = f"animation-delay:-{delay:.1f}s;animation-duration:{duration}s"
        if season == "winter":
            pieces.append(f'<circle class="fall" style="{style}" cx="{x}" cy="-10" r="{2 + i % 3}" fill="#ffffff" fill-opacity="0.85"/>')
        elif season == "spring":
            pieces.append(f'<ellipse class="fall sway" style="{style}" cx="{x}" cy="-10" rx="5" ry="2.6" fill="#ffb7c9" fill-opacity="0.9"/>')
        elif season == "autumn":
            color = [theme["accent"], "#e0a23a", "#b5462c"][i % 3]
            pieces.append(f'<path class="fall sway" style="{style}" d="M{x} -10 q7 -7 12 0 q-5 7 -12 0z" fill="{color}" fill-opacity="0.9"/>')
        else:
            y = 40 + (i * 59) % 190
            glow = "#ffe58a" if is_night else "#e09a1f"
            pieces.append(f'<circle class="fly" style="{style}" cx="{x}" cy="{y}" r="2.6" fill="{glow}"/>')
    css = """
    .fall { animation: fall 11s linear infinite; }
    .sway { animation-name: fallsway; }
    .fly { animation: fly 6s ease-in-out infinite; }
    @keyframes fall { from { transform: translateY(0); } to { transform: translateY(360px); } }
    @keyframes fallsway { 0% { transform: translate(0, 0) rotate(0deg); } 25% { transform: translate(26px, 90px) rotate(60deg); } 50% { transform: translate(-8px, 180px) rotate(140deg); } 75% { transform: translate(22px, 270px) rotate(220deg); } 100% { transform: translate(0, 360px) rotate(300deg); } }
    @keyframes fly { 0%, 100% { opacity: .1; transform: translate(0, 0); } 50% { opacity: 1; transform: translate(14px, -10px); } }"""
    return "".join(pieces), css


def fireworks(theme: dict) -> tuple[str, str]:
    bursts = []
    for i, (x, y, color) in enumerate([(760, 80, theme["accent"]), (930, 130, theme["spark"]), (620, 120, "#ffe58a")]):
        rays = "".join(
            f'<line x1="0" y1="-8" x2="0" y2="-46" stroke="{color}" stroke-width="2.4" stroke-linecap="round" transform="rotate({angle})"/>'
            for angle in range(0, 360, 30)
        )
        bursts.append(f'<g transform="translate({x} {y})"><g class="burst" style="animation-delay:{i * 0.9:.1f}s">{rays}</g></g>')
    css = """
    .burst { opacity: 0; animation: burst 3.6s ease-out infinite; }
    @keyframes burst { 0% { opacity: 0; transform: scale(.1); } 12% { opacity: 1; } 55% { opacity: .9; transform: scale(1); } 100% { opacity: 0; transform: scale(1.15); } }"""
    return "".join(bursts), css


def sky(theme_name: str, today: date, joined: str) -> str:
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
    falling, falling_css = weather(theme, today, is_night)
    party, party_css = fireworks(theme) if is_celebration(today, joined) else ("", "")
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
    @keyframes blink {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: 0; }} }}{falling_css}{party_css}
    {REDUCED_MOTION}
  </style>
  <g mask="url(#m)">
    <rect width="{width}" height="{height}" fill="url(#sky)"/>
    <circle cx="{1118 if is_night else 1040}" cy="{62 if is_night else 250}" r="{110 if is_night else 150}" fill="url(#halo)"/>
    {drifting}
    {stars}
    {shooting}
    {orb}
    {party}
    {falling}
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


def tower(theme_name: str, index: int, config: dict, stats: dict, guest_windows: int, today: date, has_garden: bool = False) -> str:
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
    garden = ""
    if has_garden:
        right = left + columns * pitch - (pitch - cell)
        bushes = "".join(
            f'<circle class="leaf" style="animation-delay:-{i * 0.5:.1f}s" cx="{left + 6 + i * 11.5:.1f}" cy="{top - 5 - (i % 2) * 3}" r="{6 + (i % 3)}" fill="{GARDEN_GREENS[i % 3]}"/>'
            for i in range(6)
        )
        garden = (
            f'<rect x="{left - 1}" y="{top - 4}" width="{right - left + 2}" height="5" rx="2" fill="{GARDEN_GREENS[2]}"/>{bushes}'
            f'<circle cx="{left + 14}" cy="{top - 13}" r="2.2" fill="#ffd166"/><circle cx="{left + 44}" cy="{top - 12}" r="2.2" fill="#ff8fab"/>'
        )
    sign_color = theme["accent"] if is_flagship else theme["ink"]
    sign_x = left + columns * pitch + 13
    label = ("Rooftop garden winner. " if has_garden else "") + f"{name}: {stars} star{'' if stars == 1 else 's'}" + (", updated this month" if beacon else "")
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
  <title>{escape(name)}</title>
  <style>
    .w {{ animation: glow 5s ease-in-out infinite; }}
    .w1 {{ animation-delay: -1.3s; }} .w2 {{ animation-delay: -2.6s; }} .w3 {{ animation-delay: -3.9s; }}
    .beacon {{ animation: beacon 1.6s ease-in-out infinite; }}
    .sign {{ animation: neon 6s steps(1) infinite; animation-delay: -{index * 0.7:.1f}s; }}
    .leaf {{ animation: leaf 4s ease-in-out infinite; transform-box: fill-box; transform-origin: 50% 100%; }}
    @keyframes leaf {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.12); }} }}
    @keyframes glow {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .3; }} }}
    @keyframes beacon {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .15; }} }}
    @keyframes neon {{ 0%, 100% {{ opacity: 1; }} 91% {{ opacity: .35; }} 93% {{ opacity: 1; }} 95% {{ opacity: .5; }} 97% {{ opacity: 1; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="{center - 1}" y="{top - spire}" width="2" height="{spire}" fill="{theme["ground"]}"/>
  {beacon}
  {''.join(cells)}
  {garden}
  <text class="sign" transform="translate({sign_x} {ground_y - 4}) rotate(-90)" font-family="{MONO}" font-size="12.5" font-weight="700" letter-spacing="0.8" fill="{sign_color}">{escape(name)}</text>
  <rect x="0" y="{ground_y}" width="{width}" height="2" fill="{theme["ground"]}"/>
  <text x="{center}" y="{ground_y + 22}" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{theme["soft"]}">★ {stars}</text>
</svg>"""


def share_guest_windows(total: int, towers: int) -> list[int]:
    """Spread visitor windows across the towers, one at a time."""
    return [total // towers + (1 if i < total % towers else 0) for i in range(towers)]


# ---------------------------------------------------------------- the ticker
def avatar_for(login: str) -> str | None:
    try:
        return (DATA / "avatars" / f"{login.lower()}.b64").read_text(encoding="utf-8").strip()
    except OSError:
        return None


def ticker(theme_name: str, visitors: list[dict]) -> str:
    theme = THEMES[theme_name]
    width, height = 1200, 54
    count = len(visitors)
    char = 9.1  # rough width of one monospace letter at this size
    if count == 0:
        lead = "No windows lit yet. Be the first to light one."
    else:
        lead = f"{count} window{'' if count == 1 else 's'} lit by visitors"
    parts = [f'<text x="0" y="33" font-family="{MONO}" font-size="15" fill="{theme["ink"]}" fill-opacity="0.9">{escape(lead)}</text>']
    x = len(lead) * char + 34
    defs = []
    for index, visitor in enumerate(reversed(visitors[-TICKER_NAMES:])):
        login = visitor["login"]
        image = avatar_for(login)
        if image:
            defs.append(f'<clipPath id="a{index}"><circle cx="{x + 15:.0f}" cy="27" r="15"/></clipPath>')
            parts.append(f'<image href="{image}" x="{x:.0f}" y="12" width="30" height="30" clip-path="url(#a{index})"/>')
        else:
            parts.append(f'<circle cx="{x + 15:.0f}" cy="27" r="15" fill="{theme["cell_b"]}"/>')
        parts.append(f'<circle cx="{x + 15:.0f}" cy="27" r="15" fill="none" stroke="{theme["lit_guest"]}" stroke-opacity="0.6"/>')
        parts.append(f'<text x="{x + 38:.0f}" y="33" font-family="{MONO}" font-size="15" fill="{theme["ink"]}">@{escape(login)}</text>')
        x += 38 + (len(login) + 1) * char + 30
    # The strip repeats after `run` pixels, so the loop is seamless at any length.
    run = max(width, int(x) + 60)
    line = "".join(parts)
    spoken = lead + ("" if not count else ". Latest: " + ", ".join(v["login"] for v in reversed(visitors[-TICKER_NAMES:])))
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(spoken)}">
  <title>Windows lit by visitors</title>
  <defs><clipPath id="c"><rect x="44" width="{width - 60}" height="{height}"/></clipPath>{''.join(defs)}</defs>
  <style>
    .run {{ animation: scroll {max(20, run // 50)}s linear infinite; }}
    .dot {{ animation: pulse 1.8s ease-in-out infinite; }}
    @keyframes scroll {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{run}px); }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="26.5" fill="{theme["cell_a"]}" fill-opacity="0.55" stroke="{theme["ground"]}"/>
  <circle class="dot" cx="26" cy="27" r="5" fill="{theme["lit_guest"] if count else theme["accent"]}"/>
  <g clip-path="url(#c)"><g class="run">
    <g transform="translate(56 0)">{line}</g>
    <g transform="translate({56 + run} 0)">{line}</g>
  </g></g>
</svg>"""


# ------------------------------------------------------------------ the vote
def tally(votes: dict) -> dict[str, int]:
    counts = {tower["repo"]: 0 for tower in TOWERS}
    for choice in votes.values():
        if choice in counts:
            counts[choice] += 1
    return counts


def garden_winner(counts: dict[str, int]) -> str | None:
    """The tower with the most votes. Ties go to the tower further left."""
    best = max(counts.values(), default=0)
    return next((name for name, votes in counts.items() if votes == best), None) if best else None


def vote_button(theme_name: str, name: str, votes: int, is_winning: bool) -> str:
    theme = THEMES[theme_name]
    fill = GARDEN_GREENS[1] if is_winning else theme["cell_a"]
    ink = "#ffffff" if is_winning else theme["ink"]
    label = f"Vote for {name} to get the rooftop garden. {votes} vote{'' if votes == 1 else 's'} so far."
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="44" viewBox="0 0 100 44" role="img" aria-label="{escape(label)}">
  <title>Vote for {escape(name)}</title>
  <rect x="9.5" y="6.5" width="77" height="30" rx="15" fill="{fill}" stroke="{GARDEN_GREENS[0] if is_winning else theme["ground"]}"/>
  <path d="M27 27 q-6 -11 6 -13 q2 11 -6 13z" fill="{'#ffffff' if is_winning else GARDEN_GREENS[0]}"/>
  <text x="56" y="26.5" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="700" fill="{ink}">{votes}</text>
</svg>"""


# --------------------------------------------------------- repo.ing, live
REPOING_MINT = "#5fe3a1"


def fees_strip(fees_sol: str) -> str:
    """One live figure from repo.ing's public badge. Dark on both themes,
    to sit under the repo.ing showcase."""
    width, height = 1200, 64
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(fees_sol)} SOL in builder fees earned by the repo.ing repository's own market, including paid and unpaid fees. Refreshed daily from repo.ing.">
  <title>repo.ing builder fees</title>
  <style>
    .live {{ animation: live 1.8s ease-in-out infinite; }}
    @keyframes live {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .2; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="18.5" fill="#0b120f" stroke="{REPOING_MINT}" stroke-opacity="0.28"/>
  <circle class="live" cx="34" cy="32" r="6" fill="{REPOING_MINT}"/>
  <text x="54" y="41" font-family="{SANS}" font-size="27" font-weight="800" letter-spacing="-0.6" fill="{REPOING_MINT}">{escape(fees_sol)} SOL</text>
  <text x="{66 + len(fees_sol + ' SOL') * 15.5:.0f}" y="39" font-family="{SANS}" font-size="18" fill="#ffffff" fill-opacity="0.82">in builder fees earned by the repo.ing repo's own market</text>
  <text x="{width - 28}" y="38" text-anchor="end" font-family="{MONO}" font-size="13" fill="#ffffff" fill-opacity="0.45">live from repo.ing, daily</text>
</svg>"""


def main() -> None:
    stats = load("stats.json", {})
    visitors = load("visitors.json", [])
    extras = load("extras.json", {})
    counts = tally(load("votes.json", {}))
    winner = garden_winner(counts)
    today = date.today()
    shares = share_guest_windows(len(visitors), len(TOWERS))
    if extras.get("repoing_fees_sol"):
        write("repoing-fees.svg", fees_strip(str(extras["repoing_fees_sol"])))
    for theme_name in THEMES:
        write(f"sky-{theme_name}.svg", sky(theme_name, today, str(extras.get("joined", ""))))
        write(f"ticker-{theme_name}.svg", ticker(theme_name, visitors))
        for index, config in enumerate(TOWERS):
            name = config["repo"]
            slug = name.lower().replace(".", "-")
            write(
                f"tower-{slug}-{theme_name}.svg",
                tower(theme_name, index, config, stats.get(name, {}), shares[index], today, has_garden=name == winner),
            )
            write(f"vote-{slug}-{theme_name}.svg", vote_button(theme_name, name, counts[name], name == winner))
    print(f"City drawn: {len(TOWERS)} towers, {len(visitors)} visitor windows, garden on {winner or 'no tower yet'}")


if __name__ == "__main__":
    main()
