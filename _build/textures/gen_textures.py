"""Generate paddle face artwork + bump maps (system python3: PIL + numpy).

Usage: python3 _build/textures/gen_textures.py [SKU ...]
Writes _build/textures/out/<SKU>_face.png and <SKU>_bump.png. The face texture spans the
paddle outline's bounding box (width x total length); the handle part is hidden by the grip.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "render"))
from specs import PADDLES, SHAPES  # noqa: E402

FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "out")
PPI = 128  # pixels per inch


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def inter(size, wght=700):
    f = ImageFont.truetype(os.path.join(FONTS, "Inter.ttf"), size)
    f.set_variation_by_axes([28, wght])
    return f


def fraunces(size, wght=600):
    f = ImageFont.truetype(os.path.join(FONTS, "Fraunces.ttf"), size)
    f.set_variation_by_axes([144, wght, 50, 0])
    return f


def noise(h, w, scale, seed):
    """Cheap smooth value noise via upscaled random grid."""
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, h // scale + 2), max(2, w // scale + 2)))
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def carbon_weave(h, w, base, tow=16, contrast=0.22, seed=1):
    """2x2 twill weave. Returns (rgb float array, bump float array)."""
    yy, xx = np.mgrid[0:h, 0:w]
    ci, cj = yy // tow, xx // tow
    horiz = ((ci + cj) % 4) < 2
    fy, fx = (yy % tow) / tow, (xx % tow) / tow
    across = np.where(horiz, fy, fx)
    along = np.where(horiz, fx, fy)
    tube = np.sin(across * math.pi) ** 0.6           # rounded tow profile
    sheen = 0.55 + 0.45 * np.where(horiz, 1.0, 0.55)  # anisotropic look
    fibre = 0.92 + 0.08 * np.sin(along * math.pi * 2 * 3 + across * 40)
    shade = (1 - contrast) + contrast * tube * sheen * fibre
    shade *= 0.94 + 0.06 * noise(h, w, 64, seed)
    rgb = np.array(hex_rgb(base), np.float32)[None, None, :] / 255.0 * shade[..., None]
    return rgb, tube


def raw_carbon(h, w, base, seed=2):
    rgb, tube = carbon_weave(h, w, base, tow=10, contrast=0.07, seed=seed)
    grit = noise(h, w, 2, seed + 1) * 0.06 + noise(h, w, 24, seed + 2) * 0.05
    rgb = rgb * (0.95 + grit[..., None])
    bump = 0.5 * tube + 0.5 * noise(h, w, 2, seed + 3)
    return rgb, bump


def wood(h, w, base, seed=3):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = noise(h, w, 400, seed) * 22 + noise(h, w, 90, seed + 1) * 3 + yy * 0.012
    rings = np.sin((xx + warp) / 5.5) * 0.5 + 0.5
    rings = rings ** 4 * (0.6 + 0.4 * noise(h, w, 30, seed + 5))
    streak = noise(h, w, 6, seed + 2)
    streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).resize((w // 8, h)).resize((w, h)),
                        np.float32) / 255.0
    shade = 0.86 + 0.08 * (1 - rings) + 0.07 * streak
    rgb = np.array(hex_rgb(base), np.float32)[None, None, :] / 255.0 * shade[..., None]
    return rgb, 0.6 * rings + 0.4 * streak


def solid(h, w, base, seed=4):
    shade = 0.985 + 0.015 * noise(h, w, 80, seed)
    rgb = np.array(hex_rgb(base), np.float32)[None, None, :] / 255.0 * shade[..., None]
    return rgb, noise(h, w, 3, seed + 1) * 0.3


def draw_mark(d, cx, cy, s, ball, line):
    """Brand mark (net + dashed drop arc + ball) centred near (cx, cy); s = px per design unit."""
    ox, oy = cx - 40 * s, cy - 40 * s
    t = lambda x, y: (ox + x * s, oy + y * s)
    d.line([t(36, 66), t(36, 42)], fill=line, width=max(2, int(4.2 * s)))
    d.line([t(8, 66), t(72, 66)], fill=line, width=max(1, int(2.4 * s)))
    p0, q, p1 = t(9, 58), t(30, 2), t(52, 44)
    for i in range(9):
        u = i / 8.0
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * q[0] + u * u * p1[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * q[1] + u * u * p1[1]
        r = 1.9 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=line)
    bx, by = t(60, 52)
    r = 12.5 * s
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=ball)


def text_center(d, cx, y, txt, fnt, fill, spacing=0):
    if spacing:
        widths = [d.textlength(c, font=fnt) for c in txt]
        total = sum(widths) + spacing * (len(txt) - 1)
        x = cx - total / 2
        for c, cw in zip(txt, widths):
            d.text((x, y), c, font=fnt, fill=fill)
            x += cw + spacing
    else:
        tw = d.textlength(txt, font=fnt)
        d.text((cx - tw / 2, y), txt, font=fnt, fill=fill)


def paddle_face(sku, spec):
    L, W, HL, rt, rb = SHAPES[spec["shape"]]
    w, h = int(W * PPI), int(L * PPI)
    head_h = int((L - HL) * PPI)
    base = spec["base"]
    if base == "carbon":
        rgb, bump = carbon_weave(h, w, spec["base_col"])
    elif base == "raw":
        rgb, bump = raw_carbon(h, w, spec["base_col"])
    elif base == "wood":
        rgb, bump = wood(h, w, spec["base_col"])
    else:
        rgb, bump = solid(h, w, spec["base_col"])
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB")
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    acc = hex_rgb(spec["accent"]) + (255,)
    ink = hex_rgb(spec["ink"]) + (255,)
    pat = spec["pattern"]
    i = PPI  # one inch in px
    cx = w / 2
    if pat == "lines":  # court diagram: inset frame, kitchen line, centre line
        m = int(0.55 * i)
        lw = int(0.07 * i)
        d.rounded_rectangle([m, m, w - m, head_h - int(0.35 * i)], radius=int(1.1 * i), outline=acc, width=lw)
        ky = int(head_h * 0.62)
        d.line([(m, ky), (w - m, ky)], fill=acc, width=lw)
        d.line([(cx, ky), (cx, head_h - int(0.35 * i))], fill=acc, width=lw)
        d.rectangle([m, ky, w - m, ky + int(0.5 * i)], fill=acc[:3] + (70,))
    elif pat == "band":
        pts = [(0, head_h * 0.30), (w, head_h * 0.12), (w, head_h * 0.12 + 1.5 * i), (0, head_h * 0.30 + 1.5 * i)]
        d.polygon(pts, fill=acc)
        off = 1.85 * i
        d.polygon([(0, pts[0][1] + off), (w, pts[1][1] + off), (w, pts[1][1] + off + 0.12 * i),
                   (0, pts[0][1] + off + 0.12 * i)], fill=acc)
    elif pat == "split":
        d.polygon([(0, 0), (w, 0), (w, head_h * 0.18), (0, head_h * 0.46)], fill=acc)
        d.line([(0, head_h * 0.46 + 0.3 * i), (w, head_h * 0.18 + 0.3 * i)], fill=ink, width=int(0.06 * i))
    elif pat == "chevron":
        for k in range(3):
            y0 = head_h * 0.52 + k * 0.62 * i
            d.line([(0.4 * i, y0), (cx, y0 + 1.6 * i), (w - 0.4 * i, y0)], fill=acc if k == 0 else ink,
                   width=int(0.2 * i if k == 0 else 0.07 * i), joint="curve")
    elif pat == "dots":
        for row in range(9):
            for col in range(7):
                x = (col + 0.5 + (row % 2) * 0.5) * (w / 7.0)
                y = 0.5 * i + row * 0.62 * i
                r = (0.16 - row * 0.014) * i
                if r > 0.02 * i:
                    d.ellipse([x - r, y - r, x + r, y + r], fill=acc)
    elif pat == "signature":
        d.line([(0.6 * i, 0.9 * i), (w - 0.6 * i, 0.9 * i)], fill=acc, width=int(0.06 * i))
        d.line([(0.6 * i, head_h - 0.9 * i), (w - 0.6 * i, head_h - 0.9 * i)], fill=acc, width=int(0.06 * i))

    # brand mark + wordmark, upper-middle
    mark_y = head_h * (0.27 if pat != "split" else 0.33)
    if pat == "band":
        mark_y = head_h * 0.50
    elif pat == "dots":
        mark_y = head_h * 0.56
    if pat == "dots":
        ty_override = head_h * 0.56 + 2.65 * i
    else:
        ty_override = None
    draw_mark(d, cx, mark_y, 0.042 * i, acc if pat not in ("band", "split") else ink, ink)
    text_center(d, cx, mark_y + 1.22 * i, "Third Shot", fraunces(int(0.62 * i)), ink)
    # model name near the throat
    ty = head_h - 2.05 * i
    if pat == "lines":
        ty = head_h * 0.62 - 1.05 * i
    if ty_override:
        ty = ty_override
    text_center(d, cx, ty, spec["title"], inter(int(0.38 * i), 800), ink, spacing=int(0.07 * i))
    text_center(d, cx, ty + 0.52 * i, spec["sub"], inter(int(0.2 * i), 600), acc if pat not in ("band",) else ink,
                spacing=int(0.06 * i))
    img = Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")
    # graphics are printed: flatten bump under them
    alpha = np.asarray(over.split()[3], np.float32) / 255.0
    bump = bump * (1 - alpha) + 0.5 * alpha
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, f"{sku}_face.png"), optimize=True)
    Image.fromarray((np.clip(bump, 0, 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.6)) \
        .save(os.path.join(OUT, f"{sku}_bump.png"))
    print("face", sku, img.size)


if __name__ == "__main__":
    want = sys.argv[1:] or list(PADDLES)
    for s in want:
        paddle_face(s, PADDLES[s])
