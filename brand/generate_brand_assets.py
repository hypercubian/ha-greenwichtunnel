"""Generate the Greenwich Foot Tunnel Lifts brand assets.

Produces the four PNGs that home-assistant/brands expects for a custom
integration: ``icon.png``, ``icon@2x.png``, ``logo.png``, ``logo@2x.png``.

Run with ``poetry run python brand/generate_brand_assets.py``.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TEAL = (15, 118, 110, 255)        # tailwind tunnel-700, matches greenwichlifts.co.uk
WHITE = (255, 255, 255, 255)
SHADOW = (0, 0, 0, 40)

BRAND_DIR = Path(__file__).parent


def _rounded_background(size: int) -> Image.Image:
    """Return a teal rounded-square background."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = int(size * 0.22)
    draw.rounded_rectangle(
        (0, 0, size - 1, size - 1),
        radius=radius,
        fill=TEAL,
    )
    return img


def _draw_tunnel(img: Image.Image) -> None:
    """Draw a cross-section tunnel arch with a lift cage inside on ``img``."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Tunnel arch: semicircle on top + rectangle on bottom, outlined in white.
    margin = int(w * 0.18)
    arch_w = w - 2 * margin
    arch_top = int(h * 0.22)
    arch_bottom = int(h * 0.82)
    arch_mid = arch_top + arch_w // 2
    line = max(6, int(w * 0.045))

    # Arch outline.
    draw.arc(
        (margin, arch_top, margin + arch_w, arch_top + arch_w),
        start=180,
        end=360,
        fill=WHITE,
        width=line,
    )
    # Left and right walls down to the floor.
    draw.line(
        (margin, arch_mid, margin, arch_bottom),
        fill=WHITE,
        width=line,
    )
    draw.line(
        (margin + arch_w, arch_mid, margin + arch_w, arch_bottom),
        fill=WHITE,
        width=line,
    )
    # Floor.
    draw.line(
        (margin, arch_bottom, margin + arch_w, arch_bottom),
        fill=WHITE,
        width=line,
    )

    # Lift cage inside the tunnel — filled rectangle with a single solid up arrow.
    lift_w = int(arch_w * 0.38)
    lift_h = int((arch_bottom - arch_top) * 0.52)
    lift_x = margin + (arch_w - lift_w) // 2
    lift_y = arch_bottom - lift_h - line
    draw.rectangle(
        (lift_x, lift_y, lift_x + lift_w, lift_y + lift_h),
        fill=WHITE,
    )
    # Upward arrow cut out of the lift cage in teal.
    cx = lift_x + lift_w // 2
    arrow_top_y = lift_y + int(lift_h * 0.22)
    arrow_bottom_y = lift_y + int(lift_h * 0.78)
    arrow_span = int(lift_w * 0.28)
    arrow_stem = max(4, line // 2)
    # Triangle head.
    draw.polygon(
        (
            (cx, arrow_top_y),
            (cx - arrow_span, arrow_top_y + arrow_span),
            (cx + arrow_span, arrow_top_y + arrow_span),
        ),
        fill=TEAL,
    )
    # Stem down from the triangle.
    draw.rectangle(
        (
            cx - arrow_stem,
            arrow_top_y + arrow_span,
            cx + arrow_stem,
            arrow_bottom_y,
        ),
        fill=TEAL,
    )


def make_icon(size: int) -> Image.Image:
    """Return a single square icon at ``size`` × ``size`` pixels."""
    img = _rounded_background(size)
    _draw_tunnel(img)
    return img


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "C:/Windows/Fonts/segoeuib.ttf",  # Segoe UI Bold
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def make_logo(height: int) -> Image.Image:
    """Return a wide logo: icon on the left, wordmark on the right."""
    icon = make_icon(height)
    font = _load_font(int(height * 0.32))
    text = "Greenwich Foot Tunnel"

    # Measure text.
    tmp = Image.new("RGBA", (1, 1))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    gap = int(height * 0.15)
    canvas_w = height + gap + text_w + gap
    canvas = Image.new("RGBA", (canvas_w, height), (0, 0, 0, 0))
    canvas.paste(icon, (0, 0), icon)

    draw = ImageDraw.Draw(canvas)
    text_x = height + gap
    text_y = (height - text_h) // 2 - bbox[1]
    draw.text((text_x, text_y), text, fill=TEAL, font=font)
    return canvas


def main() -> None:
    """Write all four PNGs into the brand directory."""
    make_icon(256).save(BRAND_DIR / "icon.png")
    make_icon(512).save(BRAND_DIR / "icon@2x.png")
    make_logo(256).save(BRAND_DIR / "logo.png")
    make_logo(512).save(BRAND_DIR / "logo@2x.png")
    print("Wrote icon.png, icon@2x.png, logo.png, logo@2x.png")


if __name__ == "__main__":
    main()
