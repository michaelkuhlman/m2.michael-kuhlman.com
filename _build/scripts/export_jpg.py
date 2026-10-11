#!/usr/bin/env python3
"""Convert finished renders (_build/renders/*.png) to web JPGs in _build/renders/jpg/.

Product shots stay 800x1000 (Magento resizes per view.xml). Editorial scenes keep their size.
Only converts when the PNG is newer than the JPG. The JPGs are tracked in git so the catalogue can be
re-seeded without re-rendering (bin/magento thirdshot:demo:seed).
"""
import glob
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "renders")
DST = os.path.join(SRC, "jpg")


def main():
    os.makedirs(DST, exist_ok=True)
    n = 0
    for png in sorted(glob.glob(os.path.join(SRC, "*.png"))):
        name = os.path.splitext(os.path.basename(png))[0]
        jpg = os.path.join(DST, name + ".jpg")
        if os.path.exists(jpg) and os.path.getmtime(jpg) >= os.path.getmtime(png):
            continue
        im = Image.open(png).convert("RGB")
        quality = 84 if name.startswith("TS-") else 82
        im.save(jpg, "JPEG", quality=quality, optimize=True, progressive=True, subsampling="4:2:0")
        n += 1
    print(f"exported {n} jpg(s) to {DST}")


if __name__ == "__main__":
    main()
