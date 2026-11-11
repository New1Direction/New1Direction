"""The page's own pixel alphabet, used for the headline and section headings."""

# A 5x7 pixel alphabet drawn for this page. It only has the letters the page uses.
GLYPHS = {
    "i": ["#", ".", "#", "#", "#", "#", "#"],
    "l": ["#.", "#.", "#.", "#.", "#.", "#.", ".#"],
    "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "c": [".....", ".....", ".###.", "#...#", "#....", "#...#", ".###."],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
    "p": [".....", ".....", "####.", "#...#", "####.", "#....", "#...."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
    "t": ["..#..", "..#..", "#####", "..#..", "..#..", "..#.#", "...#."],
    "r": [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    "g": [".....", ".....", ".####", "#...#", ".####", "....#", ".###."],
    "h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "'": ["#", "#", ".", ".", ".", ".", "."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
}


def pixel_cells(text: str, x0: float, y0: float, pitch: float, fill: str, sweep_step: float = 0.045) -> tuple[str, float]:
    """`text` as lit squares. Returns the SVG and the x position where it ends.

    Each square carries an animation delay by column, so a `.px` animation
    sweeps across the words from left to right.
    """
    cell = pitch * 0.78
    radius = pitch * 0.2
    cells = []
    column = 0
    for letter in text:
        glyph = GLYPHS[letter]
        for row, bits in enumerate(glyph):
            for offset, bit in enumerate(bits):
                if bit != "#":
                    continue
                x = x0 + (column + offset) * pitch
                y = y0 + row * pitch
                delay = (column + offset) * sweep_step
                cells.append(
                    f'<rect class="px" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{y:.1f}" '
                    f'width="{cell:.1f}" height="{cell:.1f}" rx="{radius:.1f}" fill="{fill}"/>'
                )
        column += len(glyph[0]) + 1
    return "".join(cells), x0 + column * pitch
