"""Render product shots.

blender -b -P _build/render/render.py -- [--preview] [--force] [--threads N] SKU[:n] [SKU[:n] ...]
  --preview  400x500 @ 12 samples into _build/renders/preview/
  SKU:n      only shot n (1-based)
  ALL        every SKU in shots.SHOTS
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import studio as st  # noqa: E402
from shots import SHOTS  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders")


def main(argv):
    if "--list" in argv:
        print("SKULIST", " ".join(SHOTS))
        return
    preview = "--preview" in argv
    force = "--force" in argv
    threads = 4
    if "--threads" in argv:
        threads = int(argv[argv.index("--threads") + 1])
    args = [a for a in argv if not a.startswith("--") and not a.isdigit()]
    if args == ["ALL"]:
        args = list(SHOTS)
    for a in args:
        sku, _, only = a.partition(":")
        for n, build in enumerate(SHOTS[sku], 1):
            if only and int(only) != n:
                continue
            out = os.path.join(OUT, "preview" if preview else "", f"{sku}_{n}.png")
            if os.path.exists(out) and not force and not preview:
                print("skip", out)
                continue
            if preview:
                st.reset(400, 500, 12, threads=threads)
            else:
                st.reset(800, 1000, 32, threads=threads)
            st.backdrop()
            build()
            t = time.time()
            st.render(out)
            print(f"RENDERED {sku}_{n} in {time.time() - t:.1f}s", flush=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
