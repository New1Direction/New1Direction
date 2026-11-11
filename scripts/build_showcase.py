#!/usr/bin/env python3
"""Draw the two product showcases and the section headings.

The showcases frame real product screenshots (from assets/src/) in a tilted
browser window and a phone. A picture shown through <img> cannot load other
files, so each screenshot is resized with ffmpeg and stored inside the SVG.

Run from the repo root:  python3 scripts/build_showcase.py   (needs ffmpeg)
"""
from __future__ import annotations

import base64
import subprocess
from html import escape
from pathlib import Path

from city_config import THEMES
from pixelfont import pixel_cells

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SOURCES = ASSETS / "src"

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

WIDTH, HEIGHT = 1200, 640
JPEG_QUALITY = "4"   # ffmpeg's scale: 2 is best, 31 is worst

# Brand colours taken from the products themselves.
MINT = "#5fe3a1"
CREAM = "#f6f1e7"
SAGE = "#8fb39e"

HEADINGS = {
    "building": "what i'm building",
    "agents": "agents that keep receipts",
    "more": "more things i made",
}


def embedded(name: str, width: int, as_png: bool = False) -> str:
    """A screenshot from assets/src, resized to `width`, as a data URI."""
    source = SOURCES / name
    codec = ["-c:v", "png"] if as_png else ["-c:v", "mjpeg", "-q:v", JPEG_QUALITY]
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(source), "-vf", f"scale={width}:-1:flags=lanczos", "-frames:v", "1", *codec, "-f", "image2pipe", "-"],
        check=True,
        capture_output=True,
    )
    kind = "png" if as_png else "jpeg"
    return f"data:image/{kind};base64,{base64.b64encode(result.stdout).decode('ascii')}"


def browser_window(clip_id: str, image: str, width: int, view_height: int, image_height: int, address: str, glow: str) -> str:
    """A browser frame. A screenshot taller than the frame pans slowly."""
    bar = 36
    pan = max(0, image_height - view_height)
    panning = f'class="pan" style="--pan:-{pan}px"' if pan else ""
    return f"""
    <rect x="-1" y="-1" width="{width + 2}" height="{bar + view_height + 2}" rx="15" fill="{glow}" fill-opacity="0.35"/>
    <rect width="{width}" height="{bar + view_height}" rx="14" fill="#15171c"/>
    <circle cx="20" cy="18" r="5" fill="#ff5f57"/><circle cx="38" cy="18" r="5" fill="#febc2e"/><circle cx="56" cy="18" r="5" fill="#28c840"/>
    <rect x="{width / 2 - 130}" y="8" width="260" height="20" rx="10" fill="#0b0c10"/>
    <text x="{width / 2}" y="22.5" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="#8b90a0">{escape(address)}</text>
    <clipPath id="{clip_id}"><path d="M0 {bar} H{width} V{bar + view_height - 14} a14 14 0 0 1 -14 14 H14 a14 14 0 0 1 -14 -14 Z"/></clipPath>
    <g clip-path="url(#{clip_id})"><image {panning} href="{image}" x="0" y="{bar}" width="{width}" height="{image_height}" preserveAspectRatio="none"/>
      <rect class="sheen" x="-260" y="{bar}" width="170" height="{view_height}" fill="#ffffff" fill-opacity="0.06" transform="skewX(-18)"/></g>"""


SHARED_STYLE = f"""
    .float {{ animation: float 7s ease-in-out infinite; }}
    .bob {{ animation: float 5.5s ease-in-out -2s infinite; }}
    .pan {{ animation: pan 14s ease-in-out infinite alternate; }}
    .sheen {{ animation: sheen 8s ease-in-out infinite; }}
    .halo {{ animation: breathe 9s ease-in-out infinite; }}
    @keyframes float {{ 0%, 100% {{ translate: 0 0; }} 50% {{ translate: 0 -9px; }} }}
    @keyframes pan {{ 0%, 12% {{ transform: translateY(0); }} 88%, 100% {{ transform: translateY(var(--pan)); }} }}
    @keyframes sheen {{ 0%, 55% {{ translate: 0 0; }} 85%, 100% {{ translate: 1300px 0; }} }}
    @keyframes breathe {{ 0%, 100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
    {REDUCED_MOTION}"""


def repoing() -> str:
    explore = embedded("repoing-explore.png", 1100)
    analytics = embedded("repoing-analytics.png", 640)
    main_w, main_view = 640, 386
    main_image_h = round(main_w * 926 / 1375)
    side_w = 300
    side_h = round(side_w * 990 / 1375)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="repo.ing: the market layer for open source. Launch a market for any public GitHub repo. Every trade pays the builders. Shown: the live Explore page listing repository markets.">
  <title>repo.ing</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1512"/><stop offset="1" stop-color="#090b11"/></linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{MINT}" stop-opacity="0.34"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/></radialGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="26" stdDeviation="26" flood-color="#000" flood-opacity="0.55"/></filter>
    <clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="24"/></clipPath>
    <clipPath id="side"><rect width="{side_w}" height="{side_h}" rx="12"/></clipPath>
  </defs>
  <style>{SHARED_STYLE}</style>
  <g clip-path="url(#frame)">
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)"/>
    <circle class="halo" cx="860" cy="330" r="460" fill="url(#glow)"/>
    <text x="64" y="196" font-family="{SANS}" font-size="72" font-weight="800" letter-spacing="-3" fill="#ffffff">repo.ing</text>
    <text x="66" y="242" font-family="{SANS}" font-size="25" font-weight="600" fill="{MINT}">The market layer for open source.</text>
    <text x="66" y="290" font-family="{SANS}" font-size="19" fill="#ffffff" fill-opacity="0.74">Launch a market for any public GitHub repo.</text>
    <text x="66" y="318" font-family="{SANS}" font-size="19" fill="#ffffff" fill-opacity="0.74">Every trade pays the builders.</text>
    <rect x="66" y="356" width="196" height="48" rx="24" fill="{MINT}"/>
    <text x="164" y="386.5" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="700" fill="#06281a">Explore markets</text>
    <text x="284" y="386" font-family="{MONO}" font-size="15" fill="#ffffff" fill-opacity="0.5">repo.ing</text>
    <g class="float"><g transform="translate(528 128) matrix(1 -0.055 0 1 0 0)" filter="url(#shadow)">
      {browser_window("mainclip", explore, main_w, main_view, main_image_h, "repo.ing/explore", MINT)}
    </g></g>
    <g class="bob"><g transform="translate(404 420) matrix(1 -0.055 0 1 0 0)" filter="url(#shadow)">
      <rect x="-1" y="-1" width="{side_w + 2}" height="{side_h + 2}" rx="13" fill="{MINT}" fill-opacity="0.4"/>
      <g clip-path="url(#side)"><image href="{analytics}" width="{side_w}" height="{side_h}" preserveAspectRatio="none"/></g>
    </g></g>
  </g>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="23.5" fill="none" stroke="{MINT}" stroke-opacity="0.22"/>
</svg>"""


def ohiyo() -> str:
    chat = embedded("ohiyo-chat-1600.webp", 1100)
    phone = embedded("ohiyo-phone-780.webp", 380)
    icon = embedded("ohiyo-icon.png", 176, as_png=True)
    main_w = 620
    main_view = round(main_w * 813 / 1600)
    phone_w, phone_h = 178, 356
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Ohiyo: group chat that feels like home. Free, open source and self-hostable, with text, voice, video and screen share. Shown: a group chat on desktop and on a phone.">
  <title>Ohiyo</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#191612"/><stop offset="1" stop-color="#0e0d0b"/></linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{CREAM}" stop-opacity="0.2"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></radialGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="26" stdDeviation="26" flood-color="#000" flood-opacity="0.6"/></filter>
    <clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="24"/></clipPath>
    <clipPath id="screen"><rect x="7" y="7" width="{phone_w}" height="{phone_h}" rx="22"/></clipPath>
    <clipPath id="logo"><rect width="76" height="76" rx="18"/></clipPath>
  </defs>
  <style>{SHARED_STYLE}</style>
  <g clip-path="url(#frame)">
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)"/>
    <circle class="halo" cx="360" cy="330" r="460" fill="url(#glow)"/>
    <g class="float"><g transform="translate(44 150) matrix(1 0.055 0 1 0 0)" filter="url(#shadow)">
      {browser_window("mainclip", chat, main_w, main_view, main_view, "app.ohiyo.gg", CREAM)}
    </g></g>
    <g class="bob"><g transform="translate(560 226) matrix(1 0.055 0 1 0 0)" filter="url(#shadow)">
      <rect width="{phone_w + 14}" height="{phone_h + 14}" rx="28" fill="#23211d" stroke="{CREAM}" stroke-opacity="0.35"/>
      <g clip-path="url(#screen)"><image href="{phone}" x="7" y="7" width="{phone_w}" height="{phone_h}" preserveAspectRatio="none"/></g>
      <rect x="{(phone_w + 14) / 2 - 26}" y="13" width="52" height="7" rx="3.5" fill="#000" fill-opacity="0.7"/>
    </g></g>
    <g transform="translate(804 108)" clip-path="url(#logo)"><image href="{icon}" width="76" height="76"/></g>
    <text x="800" y="268" font-family="{SANS}" font-size="72" font-weight="800" letter-spacing="-3" fill="{CREAM}">Ohiyo</text>
    <text x="804" y="312" font-family="{SANS}" font-size="22" font-weight="600" fill="{SAGE}">Group chat that feels like home.</text>
    <text x="804" y="358" font-family="{SANS}" font-size="18" fill="{CREAM}" fill-opacity="0.74">Free, open source and self-hostable.</text>
    <text x="804" y="385" font-family="{SANS}" font-size="18" fill="{CREAM}" fill-opacity="0.74">Text, voice, video and screen share.</text>
    <rect x="804" y="420" width="166" height="48" rx="24" fill="{CREAM}"/>
    <text x="887" y="450.5" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="700" fill="#1d1a15">Open Ohiyo</text>
    <text x="990" y="450" font-family="{MONO}" font-size="15" fill="{CREAM}" fill-opacity="0.5">ohiyo.gg</text>
  </g>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="23.5" fill="none" stroke="{CREAM}" stroke-opacity="0.2"/>
</svg>"""


def heading(theme_name: str, text: str) -> str:
    """A section heading in the page's pixel lights, with a dotted rule."""
    theme = THEMES[theme_name]
    width, height, pitch = 1200, 66, 5.4
    cells, end_x = pixel_cells(text, 2, 14, pitch, theme["ink"], sweep_step=0.03)
    rule = "".join(
        f'<rect x="{x:.1f}" y="{14 + 6 * pitch:.1f}" width="{pitch * 0.78:.1f}" height="{pitch * 0.78:.1f}" rx="1" fill="{theme["ground"]}"/>'
        for x in [end_x + 14 + i * pitch * 2 for i in range(int((width - end_x - 16) / (pitch * 2)))]
    )
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(text)}">
  <title>{escape(text)}</title>
  <style>
    .px {{ animation: sweep 8s ease-in-out infinite; }}
    @keyframes sweep {{ 0%, 12%, 100% {{ fill: {theme["ink"]}; }} 5% {{ fill: {theme["accent"]}; }} }}
    {REDUCED_MOTION}
  </style>
  {cells}
  {rule}
</svg>"""


def main() -> None:
    (ASSETS / "showcase-repoing.svg").write_text(repoing().strip() + "\n", encoding="utf-8")
    (ASSETS / "showcase-ohiyo.svg").write_text(ohiyo().strip() + "\n", encoding="utf-8")
    for slug, text in HEADINGS.items():
        for theme_name in THEMES:
            (ASSETS / f"heading-{slug}-{theme_name}.svg").write_text(heading(theme_name, text).strip() + "\n", encoding="utf-8")
    print("Showcases and headings drawn")


if __name__ == "__main__":
    main()
