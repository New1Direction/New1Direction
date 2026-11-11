#!/usr/bin/env python3
"""Draw the four-in-a-row game: the board, a side panel that says whose turn
it is, and one "drop" button per column.

The README places the board and panel side by side, and the seven buttons
directly under the board's seven columns, so each button is its own link.

Run from the repo root:  python3 scripts/build_game.py
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from city_config import THEMES
from game import COLUMNS, ROWS, new_game

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
GAME = ROOT / "data" / "game.json"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

CELL = 100                      # one board column is 100 units wide
BOARD_W, BOARD_H = COLUMNS * CELL, ROWS * CELL + 40
PANEL_W = 500
BUTTON_H = 66
DISC = 37

TEAM_NAMES = {"a": "Sunset", "b": "Moonlight"}


def team_colors(theme: dict) -> dict:
    return {"a": theme["accent"], "b": theme["lit_guest"]}


def load_game() -> dict:
    try:
        return json.loads(GAME.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return new_game()


def board(theme_name: str, game: dict) -> str:
    theme = THEMES[theme_name]
    colors = team_colors(theme)
    last = game.get("last") or {}
    line = {tuple(cell) for cell in game.get("line", [])}
    discs = []
    for row in range(ROWS):
        for column in range(COLUMNS):
            cx, cy = column * CELL + CELL / 2, 20 + row * CELL + CELL / 2
            team = game["board"][row][column]
            discs.append(f'<circle cx="{cx}" cy="{cy}" r="{DISC}" fill="{theme["cell_a"]}"/>')
            if team not in colors:
                continue
            classes = []
            style = ""
            if (row, column) == (last.get("row"), last.get("column")):
                classes.append("drop")
                style = f' style="--fall:-{cy + DISC:.0f}px"'
            if (row, column) in line:
                classes.append("win")
            discs.append(
                f'<circle class="{" ".join(classes)}"{style} cx="{cx}" cy="{cy}" r="{DISC}" fill="{colors[team]}"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{DISC - 9}" fill="none" stroke="#000" stroke-opacity="0.14" stroke-width="3"/>'
            )
    filled = sum(row.count("a") + row.count("b") for row in game["board"])
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{BOARD_W}" height="{BOARD_H}" viewBox="0 0 {BOARD_W} {BOARD_H}" role="img" aria-label="Four in a row board with {filled} discs played.">
  <title>Four in a row</title>
  <style>
    .drop {{ animation: drop .9s cubic-bezier(.3, 0, .5, 1) both; }}
    .win {{ animation: win 1.1s ease-in-out infinite; }}
    @keyframes drop {{ 0% {{ transform: translateY(var(--fall)); }} 70% {{ transform: translateY(0); }} 82% {{ transform: translateY(-14px); }} 100% {{ transform: translateY(0); }} }}
    @keyframes win {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
    {REDUCED_MOTION}
  </style>
  <rect x="0.5" y="0.5" width="{BOARD_W - 1}" height="{BOARD_H - 1}" rx="26" fill="{theme["cell_b"]}" stroke="{theme["ground"]}"/>
  {''.join(discs)}
</svg>"""


def panel(theme_name: str, game: dict) -> str:
    theme = THEMES[theme_name]
    colors = team_colors(theme)
    winner = game.get("winner")
    last = game.get("last") or {}
    score = game.get("score", {})
    if winner in colors:
        headline, headline_color = f"{TEAM_NAMES[winner]} wins!", colors[winner]
        hint = ["Drop a disc to start", "the next game."]
    elif winner == "draw":
        headline, headline_color = "It's a draw.", theme["ink"]
        hint = ["Drop a disc to start", "the next game."]
    else:
        turn = game["turn"]
        headline, headline_color = f"{TEAM_NAMES[turn]} to move", colors[turn]
        hint = ["Press a column below", "to drop a disc."]
    last_line = f"Last move: @{last['login']}" if last.get("login") else "No moves yet. Go first."
    spoken = f"Four in a row, played by visitors. {headline} {last_line}. Score: Sunset {score.get('a', 0)}, Moonlight {score.get('b', 0)}."
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}" height="{BOARD_H}" viewBox="0 0 {PANEL_W} {BOARD_H}" role="img" aria-label="{escape(spoken)}">
  <title>Whose turn it is</title>
  <style>
    .turn {{ animation: turn 1.6s ease-in-out infinite; }}
    @keyframes turn {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .3; }} }}
    {REDUCED_MOTION}
  </style>
  <text x="44" y="92" font-family="{MONO}" font-size="19" fill="{theme["soft"]}">visitors vs visitors</text>
  <text x="42" y="150" font-family="{SANS}" font-size="50" font-weight="800" letter-spacing="-1.8" fill="{theme["ink"]}">Four in a row</text>
  <circle class="turn" cx="62" cy="236" r="19" fill="{headline_color}"/>
  <text x="96" y="249" font-family="{SANS}" font-size="36" font-weight="700" letter-spacing="-0.8" fill="{headline_color}">{escape(headline)}</text>
  <text x="44" y="316" font-family="{SANS}" font-size="25" fill="{theme["ink"]}" fill-opacity="0.82">{hint[0]}</text>
  <text x="44" y="350" font-family="{SANS}" font-size="25" fill="{theme["ink"]}" fill-opacity="0.82">{hint[1]}</text>
  <text x="44" y="420" font-family="{MONO}" font-size="20" fill="{theme["soft"]}">{escape(last_line)}</text>
  <rect x="44" y="476" width="412" height="1.5" fill="{theme["ground"]}"/>
  <circle cx="58" cy="528" r="13" fill="{colors["a"]}"/>
  <text x="84" y="536" font-family="{SANS}" font-size="23" fill="{theme["ink"]}">Sunset</text>
  <text x="246" y="538" text-anchor="end" font-family="{SANS}" font-size="30" font-weight="800" fill="{theme["ink"]}">{score.get("a", 0)}</text>
  <circle cx="290" cy="528" r="13" fill="{colors["b"]}"/>
  <text x="316" y="536" font-family="{SANS}" font-size="23" fill="{theme["ink"]}">Moonlight</text>
  <text x="456" y="538" text-anchor="end" font-family="{SANS}" font-size="30" font-weight="800" fill="{theme["ink"]}">{score.get("b", 0)}</text>
  <text x="44" y="596" font-family="{SANS}" font-size="18" fill="{theme["soft"]}">One move at a time. Nobody moves twice in a row.</text>
</svg>"""


def button(theme_name: str, column: int, game: dict) -> str:
    theme = THEMES[theme_name]
    is_over = bool(game.get("winner"))
    color = theme["ink"] if is_over else team_colors(theme)[game["turn"]]
    is_full = not is_over and game["board"][0][column] != "."
    opacity = 0.25 if is_full else 1
    label = f"Drop a disc in column {column + 1}" + (" (full)" if is_full else "")
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{CELL}" height="{BUTTON_H}" viewBox="0 0 {CELL} {BUTTON_H}" role="img" aria-label="{label}">
  <title>{label}</title>
  <style>
    .arrow {{ animation: nudge 1.4s ease-in-out infinite; animation-delay: -{column * 0.2:.1f}s; }}
    @keyframes nudge {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(5px); }} }}
    {REDUCED_MOTION}
  </style>
  <g opacity="{opacity}">
    <rect x="12.5" y="8.5" width="75" height="48" rx="24" fill="{theme["cell_a"]}" stroke="{color}" stroke-opacity="0.7" stroke-width="1.5"/>
    <path class="arrow" d="M50 20 V40 M40 31 L50 41 L60 31" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>"""


def spacer(theme_name: str) -> str:
    """Fills the space under the panel, next to the row of buttons."""
    theme = THEMES[theme_name]
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}" height="{BUTTON_H}" viewBox="0 0 {PANEL_W} {BUTTON_H}" role="img" aria-label="Each arrow drops a disc into the column above it.">
  <title>How to play</title>
  <path d="M30 33 H10 M18 25 L10 33 L18 41" fill="none" stroke="{theme["soft"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="44" y="40" font-family="{SANS}" font-size="20" fill="{theme["soft"]}">each arrow drops a disc in its column</text>
</svg>"""


def main() -> None:
    game = load_game()
    ASSETS.mkdir(exist_ok=True)
    for theme_name in THEMES:
        files = {
            f"game-board-{theme_name}.svg": board(theme_name, game),
            f"game-panel-{theme_name}.svg": panel(theme_name, game),
            f"game-spacer-{theme_name}.svg": spacer(theme_name),
            **{f"game-drop-{column + 1}-{theme_name}.svg": button(theme_name, column, game) for column in range(COLUMNS)},
        }
        for name, svg in files.items():
            (ASSETS / name).write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"Game drawn: {game['moves']} moves, winner {game.get('winner') or 'none yet'}")


if __name__ == "__main__":
    main()
