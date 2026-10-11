"""Packaging labels, patches and prints (system python3 + PIL). Output: _build/textures/out/*.png

python3 _build/textures/labels.py
"""
import os

from PIL import Image, ImageDraw

import numpy as np

from gen_textures import OUT, draw_mark, fraunces, hex_rgb, inter, text_center, wood

P = {
    "kitchen": "#173A2E", "court": "#2E5E4A", "chalk": "#F4F0E6", "sand": "#E7DFCF", "optic": "#D9F24F",
    "clay": "#D0663F", "ink": "#13201B", "charcoal": "#2A2F2D", "pink": "#F08DB0", "forest": "#1F4A3C",
    "kraft": "#B88B5A", "glacier": "#9ED2E4",
}


def rgba(h, a=255):
    return hex_rgb(h) + (a,)


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, name), optimize=True)
    print("label", name, img.size)


def patch(name, bg, fg, ball, w=600, h=360, wordmark=True, radius=60, border=None):
    """Woven / embroidered patch: rounded rect, mark + wordmark."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, w - 4, h - 4], radius=radius, fill=rgba(bg))
    if border:
        d.rounded_rectangle([18, 18, w - 18, h - 18], radius=radius - 14, outline=rgba(border), width=6)
    if wordmark:
        draw_mark(d, w / 2, h * 0.36, 2.0, rgba(ball), rgba(fg))
        text_center(d, w / 2, h * 0.58, "Third Shot", fraunces(int(h * 0.2)), rgba(fg))
    else:
        draw_mark(d, w / 2, h / 2, min(w, h) / 95, rgba(ball), rgba(fg))
    save(img, f"patch_{name}.png")


def print_mark(name, fg, ball, w=800, h=500, sub=None):
    """Transparent print: mark + wordmark (+ optional sub line)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_mark(d, w / 2, h * 0.3, 3.0, rgba(ball), rgba(fg))
    text_center(d, w / 2, h * 0.56, "Third Shot", fraunces(int(h * 0.2)), rgba(fg))
    if sub:
        text_center(d, w / 2, h * 0.84, sub, inter(int(h * 0.065), 700), rgba(fg), spacing=10)
    save(img, f"print_{name}.png")


def wrap_label(name, bg, fg, accent, title, sub, w=2048, h=640, band=True, tiles=2):
    """Cylindrical wrap label (tube, bucket, bottle). Repeats the lockup `tiles` times around."""
    img = Image.new("RGBA", (w, h), rgba(bg))
    d = ImageDraw.Draw(img)
    if band:
        d.rectangle([0, int(h * 0.06), w, int(h * 0.1)], fill=rgba(accent))
        d.rectangle([0, int(h * 0.9), w, int(h * 0.94)], fill=rgba(accent))
    for k in range(tiles):
        cx = (k + 0.5) * w / tiles
        draw_mark(d, cx, h * 0.27, h / 220, rgba(accent), rgba(fg))
        text_center(d, cx, h * 0.43, title, inter(int(h * 0.13), 800), rgba(fg), spacing=int(h * 0.02))
        text_center(d, cx, h * 0.62, sub, inter(int(h * 0.055), 600), rgba(accent), spacing=int(h * 0.012))
        text_center(d, cx, h * 0.73, "THIRD SHOT SUPPLY CO.", inter(int(h * 0.04), 600), rgba(fg),
                    spacing=int(h * 0.012))
    save(img, f"wrap_{name}.png")


def card(name, bg, fg, accent, title, sub, w=700, h=1000):
    """Backing card / sleeve front."""
    img = Image.new("RGBA", (w, h), rgba(bg))
    d = ImageDraw.Draw(img)
    d.ellipse([w / 2 - 40, 40, w / 2 + 40, 120], fill=rgba(fg, 0))
    d.rounded_rectangle([w / 2 - 70, 50, w / 2 + 70, 100], radius=25, fill=rgba("#000000", 0), outline=rgba(fg),
                        width=4)  # hang hole outline
    draw_mark(d, w / 2, h * 0.24, 2.6, rgba(accent), rgba(fg))
    text_center(d, w / 2, h * 0.36, "Third Shot", fraunces(int(h * 0.07)), rgba(fg))
    d.rectangle([60, int(h * 0.5), w - 60, int(h * 0.505)], fill=rgba(accent))
    text_center(d, w / 2, h * 0.54, title, inter(int(h * 0.055), 800), rgba(fg), spacing=6)
    text_center(d, w / 2, h * 0.62, sub, inter(int(h * 0.028), 600), rgba(accent), spacing=5)
    save(img, f"card_{name}.png")


def sleeve(name, bg, fg, accent, title, sub, w=1200, h=420):
    """Landscape cardboard sleeve (eraser band)."""
    img = Image.new("RGBA", (w, h), rgba(bg))
    d = ImageDraw.Draw(img)
    draw_mark(d, w * 0.2, h * 0.5, 2.4, rgba(accent), rgba(fg))
    d.text((w * 0.36, h * 0.2), "Third Shot", font=fraunces(int(h * 0.16)), fill=rgba(fg))
    d.text((w * 0.36, h * 0.48), title, font=inter(int(h * 0.12), 800), fill=rgba(fg))
    d.text((w * 0.36, h * 0.68), sub, font=inter(int(h * 0.055), 600), fill=rgba(accent))
    save(img, f"card_{name}.png")


def box_print(name, fg, accent, title, sub, w=1200, h=500):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_mark(d, w * 0.14, h * 0.5, 2.6, rgba(accent), rgba(fg))
    lo = inter(int(h * 0.2), 800)
    d.text((w * 0.27, h * 0.2), title, font=lo, fill=rgba(fg))
    d.text((w * 0.275, h * 0.55), sub, font=inter(int(h * 0.075), 600), fill=rgba(fg))
    d.text((w * 0.275, h * 0.7), "THIRD SHOT SUPPLY CO.", font=inter(int(h * 0.06), 600), fill=rgba(accent))
    save(img, f"box_{name}.png")


def main():
    k, c, o = P["kitchen"], P["chalk"], P["optic"]
    patch("forest", k, c, o)
    patch("chalk", c, k, o)
    patch("clay", P["clay"], c, o)
    patch("sand", P["sand"], k, P["clay"])
    patch("charcoal", P["charcoal"], c, o)
    patch("leather", "#8C5A3A", "#F1DCC2", "#F1DCC2", w=420, h=280, radius=30)
    patch("round_optic", o, k, k, w=400, h=400, wordmark=False, radius=200)
    print_mark("chalk", c, o)
    print_mark("kitchen", k, o)
    print_mark("ink", P["ink"], P["clay"])
    print_mark("chalk_plain", c, c)
    wrap_label("t40", k, c, o, "TOUR 40", "OUTDOOR  -  3 BALLS")
    wrap_label("glow", P["ink"], c, "#B8F27A", "TWILIGHT GLOW", "OUTDOOR  -  3 BALLS")
    wrap_label("pink", "#3B1F2B", c, P["pink"], "TOUR 40 PINK", "OUTDOOR  -  6 BALLS")
    wrap_label("g26", P["clay"], c, o, "GYM 26", "INDOOR  -  6 BALLS")
    wrap_label("bucket", k, c, o, "TOUR 40", "PRACTICE BUCKET  -  48 BALLS", w=2400, h=700, tiles=2)
    wrap_label("bottle", P["forest"], c, o, "COURT", "INSULATED  -  24 OZ", w=1600, h=1100, band=False, tiles=1)
    card("lead", c, k, P["clay"], "LEAD TUNING", "4 STRIPS  -  1/4 IN  -  6 G EACH")
    sleeve("eraser", P["kraft"], P["ink"], k, "FACE ERASER", "GRIT-FREE CREPE RUBBER")
    box_print("t40_12", c, o, "TOUR 40", "OUTDOOR  -  12 BALLS")
    box_print("kraft", P["ink"], k, "TOUR 40", "OUTDOOR  -  12 BALLS")
    rgb, _ = wood(2048, 512, "#6B4329", seed=9)
    rgb = np.rot90(rgb)
    save(Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB"), "walnut.png")


if __name__ == "__main__":
    main()
