#!/usr/bin/env python3
"""Editorial images composed (PIL only, no rendering) from finished product renders in _build/renders/jpg.

Writes into _build/renders/jpg: cat_<code>.jpg, story.jpg, spotlight.jpg, workshop.jpg and placeholder.jpg.
The home hero is NOT made here (see _build/hero/); never write hero.jpg from this script.
Categories without product photography get a typographic court-line banner in the brand palette.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "textures"))
from gen_textures import draw_mark, fraunces, hex_rgb, inter  # noqa: E402

JPG = os.path.join(HERE, "..", "renders", "jpg")


def load(name):
    return Image.open(os.path.join(JPG, name + ".jpg")).convert("RGB")


def backdrop_colour(im):
    w, h = im.size
    px = [im.getpixel((x, y)) for x, y in ((8, 8), (w - 8, 8), (8, h // 2), (w - 8, h // 2))]
    return tuple(sum(c[i] for c in px) // len(px) for i in range(3))


def strip(names, size, crop_w=430, overlap=70, shift=0):
    """Seamless studio panorama: centre strips of several renders feather-blended side by side."""
    tiles = [load(n) for n in names]
    W, H = size
    th = H
    scaled = []
    for t in tiles:
        k = th / t.height
        t = t.resize((round(t.width * k), th), Image.LANCZOS)
        cw = round(crop_w * k)
        x0 = (t.width - cw) // 2 + round(shift * k)
        scaled.append(t.crop((x0, 0, x0 + cw, th)))
    bg = backdrop_colour(tiles[0])
    canvas = Image.new("RGB", (W, H), bg)
    ov = round(overlap * th / 1000)
    total = sum(s.width for s in scaled) - ov * (len(scaled) - 1)
    x = (W - total) // 2
    for i, s in enumerate(scaled):
        mask = Image.new("L", s.size, 255)
        md = ImageDraw.Draw(mask)
        for k in range(ov):
            a = int(255 * k / ov)
            if i > 0:
                md.line([(k, 0), (k, th)], fill=a)
            md.line([(s.width - 1 - k, 0), (s.width - 1 - k, th)], fill=a if i < len(scaled) - 1 else 255)
        # soften the outer edges of the panorama into the flat backdrop too
        if i == 0:
            for k in range(ov):
                md.line([(k, 0), (k, th)], fill=int(255 * k / ov))
        if i == len(scaled) - 1:
            for k in range(ov):
                md.line([(s.width - 1 - k, 0), (s.width - 1 - k, th)], fill=int(255 * k / ov))
        canvas.paste(s, (x, 0), mask)
        x += s.width - ov
    return canvas


def court_banner(title, sub, bg, line, accent, size=(1200, 900)):
    W, H = size
    im = Image.new("RGB", size, hex_rgb(bg))
    d = ImageDraw.Draw(im, "RGBA")
    lc = hex_rgb(line) + (70,)
    m = 70
    d.rectangle([m, m, W - m, H - m], outline=lc, width=6)  # court outline
    d.line([(W // 2, m), (W // 2, H - m)], fill=hex_rgb(line) + (110,), width=8)  # net
    for x in (W // 2 - 190, W // 2 + 190):  # kitchen lines
        d.line([(x, m), (x, H - m)], fill=lc, width=6)
    for x0, x1 in ((m, W // 2 - 190), (W // 2 + 190, W - m)):  # centre service lines
        d.line([(x0, H // 2), (x1, H // 2)], fill=lc, width=6)
    d.rectangle([W // 2 - 190, m, W // 2 + 190, H - m], fill=hex_rgb(line) + (14,))
    plate = Image.new("RGBA", size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    draw_mark(pd, W / 2, H * (0.36 if title else 0.5), 3.2 if title else 4.2, hex_rgb(accent) + (255,), hex_rgb(line) + (255,))
    if not title:
        im.paste(plate, (0, 0), plate)
        return im
    f = fraunces(96, 500)
    tw = pd.textlength(title, font=f)
    pd.text(((W - tw) / 2, H * 0.52), title, font=f, fill=hex_rgb(line) + (255,))
    f2 = inter(26, 600)
    sub = sub.upper()
    sw = sum(pd.textlength(c, font=f2) for c in sub) + 5 * (len(sub) - 1)
    x = (W - sw) / 2
    for c in sub:
        pd.text((x, H * 0.66), c, font=f2, fill=hex_rgb(accent) + (255,))
        x += pd.textlength(c, font=f2) + 5
    im.paste(plate, (0, 0), plate)
    return im


def placeholder(bg):
    W, H = 800, 1000
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im, "RGBA")
    ink = (23, 58, 46)
    draw_mark(d, W / 2, H * 0.42, 4.2, (23, 58, 46, 55), (23, 58, 46, 55))
    f = inter(24, 600)
    t = "STUDIO PHOTO COMING SOON"
    tw = sum(d.textlength(c, font=f) for c in t) + 4 * (len(t) - 1)
    x = (W - tw) / 2
    for c in t:
        d.text((x, H * 0.58), c, font=f, fill=ink + (120,))
        x += d.textlength(c, font=f) + 4
    return im


def save(im, name, q=84):
    if name == "hero":
        raise SystemExit("hero.jpg is made in _build/hero, not here")
    im.save(os.path.join(JPG, name + ".jpg"), "JPEG", quality=q, optimize=True, progressive=True)
    print("wrote", name, im.size)


def main():
    save(strip(["TS-DZC16_1", "TS-HYB13_1", "TS-BLP14_1"], (1200, 900), crop_w=404, overlap=40, shift=-4), "cat_paddles")
    save(strip(["TS-T40-3_1", "TS-T40-48_1", "TS-G26-6_1"], (1200, 900), crop_w=470), "cat_balls")
    save(strip(["TS-BAG-CLUB-FOREST_1", "TS-BAG-TOUR_1", "TS-BAG-SLING_1"], (1200, 900), crop_w=560), "cat_bags")
    save(court_banner("", "", "#B9573A", "#F4F0E6", "#D9F24F"),
         "cat_apparel")
    save(court_banner("", "", "#2E5E4A", "#F4F0E6", "#D9F24F"),
         "cat_training")
    save(court_banner("", "", "#1F3550", "#F4F0E6", "#9ED2E4"), "cat_accessories")
    sig = load("TS-SIG-RAW_3")
    save(sig.crop((0, 33, 800, 33 + 933)), "story")
    spot = load("TS-SIG-RAW_1")
    save(spot.crop((0, 140, 800, 940)), "spotlight")
    save(strip(["TS-KLC16-GLACIER_1", "TS-APX14_1", "TS-SIG-RAW_1", "TS-DZC16_1"], (1600, 1000), crop_w=404, overlap=40, shift=-4), "workshop")
    save(placeholder(backdrop_colour(load("TS-SIG-RAW_1"))), "placeholder", q=88)


if __name__ == "__main__":
    main()
