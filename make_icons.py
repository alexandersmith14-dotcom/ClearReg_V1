"""Generate the favicon and home-screen icons.

Run after changing the branding, same as make_og_image.py. Output is committed
so the published page can reference it.

The design deliberately echoes og-image.png: navy field, white mark, green
rule along the bottom. Someone who saw the LinkedIn card should recognise the
tab icon as the same thing.

The mark is Check Spike — a checkmark that keeps going into the same
flat-then-peak spike shape used across the rest of the identity ("flat until
it isn't"), rendered as plain line segments rather than a font glyph so it
matches the SVG mark in the page header exactly.

The green rule is a proportion of the icon (10%) rather than a fixed pixel
height, the same reasoning as before: at 16px a fixed 14px rule (this card's
proportion) would be sub-pixel and vanish.
"""
import json

from PIL import Image, ImageDraw

NAVY = (0, 59, 106)
GREEN = (174, 209, 54)
WHITE = (255, 255, 255)

RULE_FRACTION = 0.10      # green bar height, as a share of the icon
CAP_FRACTION = 0.66       # target height of the mark, as a share of the field

# Check Spike, in its native 64-unit coordinate space (same path as the SVG
# mark in dashboard.html's .pagehead and the regwatch-logomark artifact).
GLYPH_PTS = [(10, 34), (22, 46), (40, 18), (46, 18), (50, 10), (54, 18), (60, 18)]
DOT_PT, DOT_R_SRC = (50, 10), 4.0
SRC_X0, SRC_X1 = 10, 60
SRC_Y0, SRC_Y1 = 10, 46


def render(size, padding=0.0):
    """One icon. `padding` insets the artwork for maskable (croppable) icons."""
    img = Image.new("RGB", (size, size), NAVY)
    d = ImageDraw.Draw(img)

    inset = round(size * padding)
    inner = size - 2 * inset

    rule = max(1, round(inner * RULE_FRACTION))
    d.rectangle([inset, size - inset - rule, size - inset, size - inset - 1], fill=GREEN)

    field_top, field_bottom = inset, size - inset - rule
    field_h = field_bottom - field_top
    src_w, src_h = SRC_X1 - SRC_X0, SRC_Y1 - SRC_Y0

    scale = (field_h * CAP_FRACTION) / src_h
    glyph_w, glyph_h = src_w * scale, src_h * scale
    ox = inset + (inner - glyph_w) / 2 - SRC_X0 * scale
    oy = field_top + (field_h - glyph_h) / 2 - SRC_Y0 * scale

    def to_px(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    pts = [to_px(p) for p in GLYPH_PTS]
    stroke_w = max(1, round(scale * 4.4))
    d.line(pts, fill=WHITE, width=stroke_w, joint="curve")
    # line() doesn't round the end caps the way the SVG's stroke-linecap does;
    # a filled circle at every vertex (including both ends) approximates it.
    r = stroke_w / 2
    for p in pts:
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=WHITE)

    dx, dy = to_px(DOT_PT)
    dr = DOT_R_SRC * scale
    d.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=GREEN)
    return img


def main():
    written = []

    # Multi-size .ico still has the broadest support, and is what a browser
    # reaches for when no <link rel="icon"> matches.
    ico = render(48)
    ico.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    written.append("favicon.ico")

    for size in (16, 32, 180, 192, 512):
        # 180 is Apple's home-screen size; iOS rounds the corners itself and
        # composites on black, so the artwork must stay full-bleed and opaque.
        name = "apple-touch-icon.png" if size == 180 else f"icon-{size}.png"
        render(size).save(name, "PNG", optimize=True)
        written.append(name)

    # Android masks icons to whatever shape the launcher uses and can crop up to
    # 20% off each edge. The padded variant keeps the mark inside that safe
    # zone; without it the spike loses its tip on a circular launcher.
    render(512, padding=0.20).save("icon-maskable-512.png", "PNG", optimize=True)
    written.append("icon-maskable-512.png")

    manifest = {
        "name": "Regulatory update tracker — community banks & fintechs",
        "short_name": "Mihari",
        "description": "Daily federal regulatory updates for community banks and "
                       "fintechs, in plain English.",
        # Relative, because the site is served from a /regwatch/ subpath rather
        # than a domain root. An absolute "/" would break the installed app.
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#003b6a",
        "theme_color": "#003b6a",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open("site.webmanifest", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    written.append("site.webmanifest")

    print("Wrote " + ", ".join(written))


if __name__ == "__main__":
    main()
