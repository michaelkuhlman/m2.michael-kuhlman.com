#!/usr/bin/env python3
"""Crop/resize the raw Gemini images (~/m2-gemini-raw/<id>.jpeg) into _build/renders/jpg/<id>.jpg.

Studio shots get a gentle per-channel white balance so the backdrop matches the theme's photo tile colour
(@ts-photo #F7EDD9), which keeps the product grid even. Usage: post.py [id ...]  (default: all available)
"""
import os, sys
from PIL import Image, ImageStat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import shots

RAW = os.path.expanduser('~/m2-gemini-raw')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'renders', 'jpg')
TARGET = (247, 237, 217)


def balance(im):
    w, h = im.size
    pw, ph = w // 14, h // 14
    boxes = [(0, 0, pw, ph), (w - pw, 0, w, ph), (0, h - ph, pw, h), (w - pw, h - ph, w, h),
             (w // 2 - pw // 2, 0, w // 2 + pw // 2, ph)]
    means = [ImageStat.Stat(im.crop(b)).mean for b in boxes]
    m = [sum(c[i] for c in means) / len(means) for i in range(3)]
    gains = [max(0.92, min(1.08, TARGET[i] / max(m[i], 1))) for i in range(3)]
    chans = [c.point(lambda v, g=g: min(255, int(v * g + 0.5))) for c, g in zip(im.split(), gains)]
    return Image.merge('RGB', chans)


def crop_to(im, tw, th):
    w, h = im.size
    r = tw / th
    if w / h > r:
        nw = int(h * r); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w / r); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
    return im.resize((tw, th), Image.LANCZOS)


def main(ids):
    done = []
    for s in shots():
        if ids and s['id'] not in ids:
            continue
        src = os.path.join(RAW, s['id'] + '.jpeg')
        if not os.path.exists(src):
            continue
        im = Image.open(src).convert('RGB')
        if 'chalk-cream paper backdrop' in s['prompt']:
            im = balance(im)
        for name, size in [(s['id'], s['crop'])] + list(s.get('extra') or []):
            crop_to(im, *size).save(os.path.join(OUT, name + '.jpg'), quality=86, optimize=True, progressive=True)
        done.append(s['id'])
    print(len(done), 'written:', ' '.join(done))


if __name__ == '__main__':
    main(set(sys.argv[1:]))
