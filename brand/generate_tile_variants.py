"""Generate the four Greenwich-tunnel dashboard-tile state variants.

The source asset (``greenwich_tunnel_tile_v8.svg``) contains one working
(green) panel on the NORTH slot and one out-of-service (red) panel on the
SOUTH slot. This script splits the two panels out of the source, then
assembles four combinations by shifting their x-coordinates and swapping
the labels so every variant keeps both panel slots populated:

* ``ww`` – north working, south working
* ``wb`` – north working, south out-of-service (the original layout)
* ``bw`` – north out-of-service, south working
* ``bb`` – north out-of-service, south out-of-service

Run with ``poetry run python brand/generate_tile_variants.py``; output lands
in ``brand/tiles/``.
"""

from __future__ import annotations

from pathlib import Path

SOURCE = Path("C:/Users/Hypercubian/Downloads/greenwich_tunnel_tile_v8.svg")
OUTPUT_DIR = Path(__file__).parent / "tiles"

# Line ranges (1-indexed) derived from the source file.
HEADER_LINES = (1, 10)        # <svg>, <title>, <desc>, <defs>, heading <text>s
NORTH_PANEL_LINES = (11, 83)  # green panel at slot x~40..320 (label centre 180)
SOUTH_PANEL_LINES = (85, 157)  # red panel at slot x~360..640 (label centre 500)
FOOTER_LINES = (159, 164)     # dashed tunnel line + "370m under the Thames" + </svg>

# Shifts required to move a panel from its source slot to the opposite slot.
# Every top-level coordinate in each panel differs by exactly +/- 320.
# Aggressive 3x scale so the text is genuinely readable when the SVG is
# rendered at typical dashboard card widths (~400-500 px). At 3x every text
# element projects to 40-45 actual px on a 500-px card.
FONT_SIZE_SCALE = [
    ("font-size:15px", "font-size:45px"),  # main title
    ("font-size:14px", "font-size:42px"),  # North / South panel headers
    ("font-size:12px", "font-size:36px"),  # subtitle, entrance names, pill text, footer
]

# With 36px pill text the source pill geometry (height 30, widths 100/140) no
# longer fits. Scale them up and widen to house the larger strings while keeping
# them centred on their panel (center-x = 180 north / 500 south).
PILL_SHAPE_PATCHES = [
    # Working pill (north by default)
    (
        '<rect x="130" y="290" width="100" height="30" rx="15"',
        '<rect x="90" y="275" width="180" height="55" rx="27"',
    ),
    ('<circle cx="150" cy="305" r="5"', '<circle cx="120" cy="302.5" r="10"'),
    ('x="188" y="305"', 'x="200" y="306"'),
    # Out of service pill (south by default)
    (
        '<rect x="430" y="290" width="140" height="30" rx="15"',
        '<rect x="370" y="275" width="260" height="55" rx="27"',
    ),
    ('<circle cx="450" cy="305" r="5"', '<circle cx="410" cy="302.5" r="10"'),
    ('x="506" y="305"', 'x="520" y="306"'),
]

NORTH_TO_SOUTH = [
    ('x="40"', 'x="360"'),
    ("translate(180,185)", "translate(500,185)"),
    ('x="180"', 'x="500"'),
    ('x="90"', 'x="410"'),        # working-pill rect (widened to 180)
    ('cx="120"', 'cx="440"'),     # working-pill dot
    ("translate(155,330)", "translate(475,330)"),
    ('x="200"', 'x="520"'),       # working-pill text anchor
    (">North<", ">South<"),
    (">Island Gardens<", ">Greenwich<"),
]

SOUTH_TO_NORTH = [
    ('x="360"', 'x="40"'),
    ("translate(500,185)", "translate(180,185)"),
    ('x="500"', 'x="180"'),
    ('x="370"', 'x="50"'),        # out-of-service pill rect (widened to 260)
    ('cx="410"', 'cx="90"'),      # out-of-service pill dot
    ("translate(475,330)", "translate(155,330)"),
    ('x="520"', 'x="200"'),       # out-of-service pill text anchor
    (">South<", ">North<"),
    (">Greenwich<", ">Island Gardens<"),
]


def _apply(text: str, replacements: list[tuple[str, str]]) -> str:
    """Apply an ordered list of literal substring replacements to ``text``."""
    for src, dst in replacements:
        if src not in text:
            raise RuntimeError(f"expected substring not found while shifting panel: {src!r}")
        text = text.replace(src, dst)
    return text


def _slice(lines: list[str], span: tuple[int, int]) -> str:
    """Return the contents of ``lines`` for the inclusive 1-indexed ``span``."""
    start, end = span
    return "".join(lines[start - 1 : end])


def main() -> None:
    """Read the source SVG and emit the four state combinations."""
    raw = SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    header = _slice(raw, HEADER_LINES)
    north_panel_green = _slice(raw, NORTH_PANEL_LINES)
    south_panel_red = _slice(raw, SOUTH_PANEL_LINES)
    footer = _slice(raw, FOOTER_LINES)

    # Rebuild pills to accommodate the larger text before any other transforms.
    for src, dst in PILL_SHAPE_PATCHES:
        north_panel_green = north_panel_green.replace(src, dst)
        south_panel_red = south_panel_red.replace(src, dst)

    # Cross-positioned variants of each coloured panel.
    south_panel_green = _apply(north_panel_green, NORTH_TO_SOUTH)
    north_panel_red = _apply(south_panel_red, SOUTH_TO_NORTH)

    variants = {
        "ww": header + north_panel_green + south_panel_green + footer,
        "wb": header + north_panel_green + south_panel_red + footer,
        "bw": header + north_panel_red + south_panel_green + footer,
        "bb": header + north_panel_red + south_panel_red + footer,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg in variants.items():
        # Bump every text font-size so the rendered tile stays legible at dashboard
        # widths (a ~400px card would otherwise shrink the 12px source text to ~7px).
        for src, dst in FONT_SIZE_SCALE:
            svg = svg.replace(src, dst)
        path = OUTPUT_DIR / f"greenwich_tunnel_tile_{name}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {path} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
