"""Third Shot Supply Co. - brand constants and SVG logo builder.

Text is converted to outlines with fontTools, so the SVGs render identically
everywhere (no webfont dependency). Run:  python3 _build/brand/brand.py
Outputs go to _build/brand/out/ and are copied into the theme by _build/scripts/sync_brand.sh.
"""
import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "out")

PALETTE = {
    "kitchen": "#173A2E",   # primary deep court green
    "court": "#2E5E4A",     # mid green
    "chalk": "#F4F0E6",     # page background
    "sand": "#E7DFCF",      # panels
    "optic": "#D9F24F",     # ball yellow accent
    "clay": "#D0663F",      # sale / secondary accent
    "ink": "#13201B",       # text
}

_font_cache = {}


def font(name, **axes):
    key = (name, tuple(sorted(axes.items())))
    if key not in _font_cache:
        f = TTFont(os.path.join(FONTS, name))
        _font_cache[key] = instantiateVariableFont(f, axes) if axes else f
    return _font_cache[key]


def text_path(txt, fnt, size, x=0.0, y=0.0, tracking=0.0):
    """Return (svg path d, advance width) for txt at baseline (x, y)."""
    gs = fnt.getGlyphSet()
    cmap = fnt.getBestCmap()
    upm = fnt["head"].unitsPerEm
    scale = size / upm
    pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    cx = x
    for ch in txt:
        gname = cmap.get(ord(ch))
        if gname is None:
            continue
        tp = TransformPen(pen, (scale, 0, 0, -scale, cx, y))
        gs[gname].draw(tp)
        cx += gs[gname].width * scale + tracking
    return pen.getCommands(), cx - x - tracking


def mark(ox, oy, s, ball, line, holes=None, bg=None):
    """Third-shot drop: a dashed trajectory clears the net and lands as the ball.

    Drawn in an 80x80 design box, placed at (ox, oy) and scaled by s (1.0 = 80px).
    """
    holes = holes or line
    t = lambda x, y: (ox + x * s, oy + y * s)
    parts = []
    if bg:
        parts.append(f'<rect x="{ox:.2f}" y="{oy:.2f}" width="{80 * s:.2f}" height="{80 * s:.2f}" rx="{18 * s:.2f}" fill="{bg}"/>')
    # net post + tape
    nx0, ny0 = t(36, 66); nx1, ny1 = t(36, 42)
    parts.append(f'<path d="M{nx0:.2f} {ny0:.2f} L{nx1:.2f} {ny1:.2f}" stroke="{line}" stroke-width="{4.2 * s:.2f}" stroke-linecap="round"/>')
    gx0, gy0 = t(8, 66); gx1, gy1 = t(72, 66)
    parts.append(f'<path d="M{gx0:.2f} {gy0:.2f} L{gx1:.2f} {gy1:.2f}" stroke="{line}" stroke-width="{2.4 * s:.2f}" stroke-linecap="round" opacity="0.55"/>')
    # dashed arc
    ax0, ay0 = t(9, 58); qx, qy = t(30, 2); ax1, ay1 = t(52, 44)
    parts.append(f'<path d="M{ax0:.2f} {ay0:.2f} Q{qx:.2f} {qy:.2f} {ax1:.2f} {ay1:.2f}" fill="none" stroke="{line}" '
                 f'stroke-width="{3.6 * s:.2f}" stroke-linecap="round" stroke-dasharray="{0.1 * s:.2f} {7.2 * s:.2f}"/>')
    # ball
    bx, by = t(60, 52); r = 12.5 * s
    parts.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{r:.2f}" fill="{ball}"/>')
    for i in range(7):
        a = i * 2 * 3.14159265 / 7 + 0.4
        hx, hy = bx + 0.55 * r * math.cos(a), by + 0.55 * r * math.sin(a)
        parts.append(f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="{r * 0.11:.2f}" fill="{holes}" fill-opacity="0.35"/>')
    parts.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{r * 0.11:.2f}" fill="{holes}" fill-opacity="0.35"/>')
    return "\n  ".join(parts)


def logo_horizontal(fg, ball, arc, sub=None):
    serif = font("Fraunces.ttf", opsz=96, wght=600, SOFT=50, WONK=0)
    sans = font("Inter.ttf", opsz=14, wght=600)
    d1, w1 = text_path("Third Shot", serif, 46, x=84, y=46)
    d2, w2 = text_path("SUPPLY CO.", sans, 11.5, x=86, y=66, tracking=3.1)
    width = math.ceil(84 + max(w1, w2) + 4)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 76" width="{width}" height="76" role="img" aria-label="Third Shot Supply Co.">
  <title>Third Shot Supply Co.</title>
  {mark(0, 0, 0.95, ball, arc, holes=fg)}
  <path d="{d1}" fill="{fg}"/>
  <path d="{d2}" fill="{sub or fg}"/>
</svg>
'''


def favicon(bg, ball, arc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  {mark(0, 0, 0.8, ball, arc, holes=bg, bg=bg)}
</svg>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    p = PALETTE
    files = {
        "logo.svg": logo_horizontal(p["kitchen"], p["optic"], p["kitchen"], sub=p["court"]),
        "logo-light.svg": logo_horizontal(p["chalk"], p["optic"], p["chalk"], sub=p["optic"]),
        "favicon.svg": favicon(p["kitchen"], p["optic"], p["chalk"]),
        "mark.svg": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80">'
                    f'{mark(0, 0, 1, p["optic"], p["kitchen"])}</svg>\n',
        "mark-light.svg": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80">'
                          f'{mark(0, 0, 1, p["optic"], p["chalk"], holes=p["kitchen"])}</svg>\n',
    }
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w") as fh:
            fh.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main()
