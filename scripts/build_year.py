#!/usr/bin/env python3
"""Draw the last year of contributions as a city seen from above.

Every day is one building: the busier the day, the taller it stands. The
buildings rise in a wave when the picture loads, and a beacon marks today.

Run from the repo root:  python3 scripts/build_year.py
"""
from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path

from city_config import THEMES

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CALENDAR = ROOT / "data" / "calendar.json"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

WIDTH, HEIGHT = 1200, 720
HALF_W, HALF_H = 19.0, 9.5          # half the width and height of one ground tile
ORIGIN_X, ORIGIN_Y = 156.0, 128.0   # where week 0, Sunday sits
TILE = 0.84                         # buildings cover this share of their tile
EMPTY_HEIGHT = 3.0
MIN_HEIGHT, MAX_HEIGHT = 9.0, 86.0
RISE_SECONDS_PER_STEP = 0.022

# Roof, left wall and right wall for each activity level, quiet to busiest.
RAMPS = {
    "dark": [
        ("#211a3b", "#17122b", "#1c1633"),
        ("#7a3346", "#4f2030", "#63283a"),
        ("#c24a33", "#7d2f22", "#9c3b29"),
        ("#ff7a59", "#a84a35", "#d16045"),
        ("#ffe2c4", "#c98f6b", "#e8b38c"),
    ],
    "light": [
        ("#ece5d6", "#d3cbb8", "#dfd7c6"),
        ("#f6c3b2", "#d99c8a", "#e8af9d"),
        ("#f08a6c", "#c26248", "#d97558"),
        ("#e2553a", "#a93a25", "#c5482f"),
        ("#8f2a18", "#5c190d", "#752012"),
    ],
}


def load_calendar() -> dict:
    try:
        return json.loads(CALENDAR.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"total": 0, "weeks": []}


def percentile(values: list[int], share: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * share))] if ordered else 0


def level_for(count: int, ceiling: int) -> int:
    """0 for a quiet day, then four steps up to the busiest days."""
    if count <= 0:
        return 0
    return min(4, 1 + int(3 * min(count, ceiling) / max(ceiling, 1) + 0.5))


def height_for(count: int, ceiling: int) -> float:
    if count <= 0:
        return EMPTY_HEIGHT
    share = min(count, ceiling) / max(ceiling, 1)
    # A square root keeps ordinary days visible next to the huge ones.
    return MIN_HEIGHT + (MAX_HEIGHT - MIN_HEIGHT) * share ** 0.5


def longest_streak(days: list[dict]) -> int:
    best = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        best = max(best, run)
    return best


def points(*pairs: tuple[float, float]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pairs)


def building(week: int, weekday: int, height: float, ramp: tuple[str, str, str], delay: float) -> str:
    """One box, drawn as a roof and the two walls that face the viewer."""
    cx = ORIGIN_X + (week - weekday) * HALF_W
    cy = ORIGIN_Y + (week + weekday) * HALF_H + HALF_H   # centre of the ground tile
    w, h = HALF_W * TILE, HALF_H * TILE
    back, right, front, left = (cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)
    lift = lambda p: (p[0], p[1] - height)  # noqa: E731
    roof, left_wall, right_wall = ramp
    return (
        f'<g class="b" style="animation-delay:{delay:.2f}s;transform-origin:{cx:.1f}px {cy + h:.1f}px">'
        f'<polygon points="{points(lift(left), lift(front), front, left)}" fill="{left_wall}"/>'
        f'<polygon points="{points(lift(front), lift(right), right, front)}" fill="{right_wall}"/>'
        f'<polygon points="{points(lift(back), lift(right), lift(front), lift(left))}" fill="{roof}"/>'
        f"</g>"
    )


def month_labels(weeks: list[list[dict]], color: str) -> str:
    """Month names along the front edge, where each month begins."""
    labels = []
    seen = None
    for index, week in enumerate(weeks):
        month = week[0]["date"][5:7]
        if month == seen:
            continue
        seen = month
        name = date.fromisoformat(week[0]["date"]).strftime("%b")
        x = ORIGIN_X + (index - 7) * HALF_W - 4
        y = ORIGIN_Y + (index + 7) * HALF_H + 26
        labels.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="{MONO}" font-size="13" fill="{color}">{name}</text>')
    return "".join(labels[1:])  # the first week is usually a partial month


def year(theme_name: str, calendar: dict) -> str:
    theme = THEMES[theme_name]
    ramps = RAMPS[theme_name]
    weeks = calendar["weeks"]
    days = [day for week in weeks for day in week]
    counts = [day["count"] for day in days]
    ceiling = max(1, percentile([c for c in counts if c > 0], 0.95))
    total = calendar.get("total", sum(counts))
    active = sum(1 for c in counts if c > 0)
    busiest = max(days, key=lambda day: day["count"], default={"date": "", "count": 0})
    busiest_date = date.fromisoformat(busiest["date"]).strftime("%b %-d") if busiest["date"] else ""

    # Far buildings first, so nearer ones are painted over them.
    placed = sorted(
        ((w, d, day) for w, week in enumerate(weeks) for d, day in enumerate(week)),
        key=lambda item: (item[0] + item[1], item[0]),
    )
    boxes = "".join(
        building(w, d, height_for(day["count"], ceiling), ramps[level_for(day["count"], ceiling)], (w + d) * RISE_SECONDS_PER_STEP)
        for w, d, day in placed
    )

    beacon = ""
    if weeks and weeks[-1]:
        w, d = len(weeks) - 1, len(weeks[-1]) - 1
        bx = ORIGIN_X + (w - d) * HALF_W
        by = ORIGIN_Y + (w + d) * HALF_H + HALF_H - height_for(weeks[-1][-1]["count"], ceiling)
        beacon = (
            f'<g class="today"><line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{by - 34:.1f}" stroke="{theme["spark"]}" stroke-width="1.6"/>'
            f'<circle class="ping" cx="{bx:.1f}" cy="{by - 34:.1f}" r="5" fill="{theme["spark"]}" style="transform-origin:{bx:.1f}px {by - 34:.1f}px"/>'
            f'<circle cx="{bx:.1f}" cy="{by - 34:.1f}" r="3.4" fill="{theme["spark"]}"/>'
            f'<text x="{bx - 12:.1f}" y="{by - 44:.1f}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{theme["spark"]}">today</text></g>'
        )

    summary = f"{total:,} contributions in the last year, on {active} days. Longest streak {longest_streak(days)} days. Busiest day {busiest_date} with {busiest['count']:,}."
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(summary)}">
  <title>A year of work, seen from above</title>
  <style>
    .b {{ animation: rise 1.1s cubic-bezier(.2, .8, .2, 1) both; }}
    .ping {{ animation: ping 1.8s ease-out infinite; }}
    .today {{ animation: fade 1s ease-out 1.6s both; }}
    .words {{ animation: fade 1.2s ease-out .4s both; }}
    .comet {{ opacity: 0; animation: comet 9s linear 2s infinite; }}
    @keyframes rise {{ from {{ transform: scaleY(0); opacity: 0; }} to {{ transform: scaleY(1); opacity: 1; }} }}
    @keyframes ping {{ 0% {{ transform: scale(1); opacity: .9; }} 100% {{ transform: scale(3.4); opacity: 0; }} }}
    @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes comet {{ 0% {{ opacity: 0; transform: translate(520px, 20px); }} 3% {{ opacity: 1; }} 14% {{ opacity: 0; transform: translate(1120px, 200px); }} 100% {{ opacity: 0; transform: translate(1120px, 200px); }} }}
    {REDUCED_MOTION}
  </style>
  <g class="comet"><line x1="0" y1="0" x2="-80" y2="-24" stroke="{theme["spark"]}" stroke-width="2" stroke-linecap="round"/></g>
  {boxes}
  {beacon}
  {month_labels(weeks, theme["soft"])}
  <g class="words">
    <text x="1160" y="70" text-anchor="end" font-family="{SANS}" font-size="30" font-weight="800" letter-spacing="-0.8" fill="{theme["ink"]}">A year of work, seen from above</text>
    <text x="1160" y="100" text-anchor="end" font-family="{SANS}" font-size="17" fill="{theme["soft"]}">Every building is one day. Busier days stand taller.</text>
    <text x="48" y="560" font-family="{SANS}" font-size="76" font-weight="800" letter-spacing="-3" fill="{theme["accent"]}">{total:,}</text>
    <text x="50" y="592" font-family="{SANS}" font-size="19" fill="{theme["ink"]}">contributions in the last year</text>
    <text x="50" y="634" font-family="{MONO}" font-size="15" fill="{theme["soft"]}">{active} active days</text>
    <text x="50" y="658" font-family="{MONO}" font-size="15" fill="{theme["soft"]}">longest streak {longest_streak(days)} days</text>
    <text x="50" y="682" font-family="{MONO}" font-size="15" fill="{theme["soft"]}">busiest day {busiest_date} · {busiest["count"]:,}</text>
  </g>
</svg>"""


def main() -> None:
    calendar = load_calendar()
    if not calendar["weeks"]:
        print("No calendar data yet; skipping the year view.")
        return
    ASSETS.mkdir(exist_ok=True)
    for theme_name in THEMES:
        (ASSETS / f"year-{theme_name}.svg").write_text(year(theme_name, calendar).strip() + "\n", encoding="utf-8")
    print(f"Year drawn: {sum(len(week) for week in calendar['weeks'])} days")


if __name__ == "__main__":
    main()
