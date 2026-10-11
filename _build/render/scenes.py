"""Editorial compositions: home hero, category banners, story/spotlight images.

blender -b -P _build/render/scenes.py -- [--preview] [--force] NAME [NAME ...] | ALL
Output: _build/renders/<name>.png (category banners: cat_<code>.png)
"""
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402

import models_core as mc  # noqa: E402
import models_court as ct  # noqa: E402
import models_gear as gr  # noqa: E402
import studio as st  # noqa: E402

R = math.radians
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders")
GREEN = "#1D4536"
rng = random.Random(21)


def balls(pts, colour="optic", kind="outdoor"):
    for x, y in pts:
        mc.ball(colour, kind, loc=(x, y, 0.037), rot=ct.rand_rot(rng))


def group(build, loc=(0, 0, 0), rot_z=0.0, rot_x=0.0):
    """Build a model, then move/rotate everything it created as one unit."""
    before = set(bpy.context.scene.objects)
    build()
    new = [o for o in bpy.context.scene.objects if o not in before and o.parent is None]
    e = st.parent_all(new, "grp")
    e.location = loc
    e.rotation_euler = (rot_x, 0, rot_z)
    return e


def standing(sku, x, y, yaw, lean=8):
    p = mc.paddle(sku)
    p.rotation_euler = (R(90 - lean), 0, R(yaw))
    p.location = (x, y, 0)
    return p


def hero():
    st.backdrop(GREEN, rough=0.95)
    standing("TS-APX14", 0.16, 0.16, -30, 10)
    standing("TS-SIG-RAW", 0.36, 0.04, -12, 8)
    standing("TS-KLC16-VOLT", 0.58, 0.12, 20, 8)
    balls([(0.47, -0.17), (0.66, -0.1), (0.27, -0.2)])
    st.soft_lights(target=(0.38, 0, 0.2), scale=1.1, key=1.6)
    st.camera((0.14, 0, 0.215), azimuth_deg=-4, elev_deg=6, dist=1.72, lens=50, dof=8)
    return (1920, 960, 48)


def cat_paddles():
    st.backdrop("#E6DFD2")
    standing("TS-DZC16", -0.24, 0.04, -14)
    standing("TS-HYB13", 0.0, 0.0, 4)
    standing("TS-BLP14", 0.24, 0.05, 18)
    balls([(0.13, -0.18), (-0.12, -0.2)])
    st.soft_lights(target=(0, 0, 0.2), scale=1.2)
    st.camera((0, 0, 0.21), azimuth_deg=-4, elev_deg=6, dist=1.95, lens=60, dof=8)
    return (1200, 900, 40)


def cat_balls():
    st.backdrop(GREEN, rough=0.95)
    ct.bucket48(loc=(0.05, 0.08, 0))
    ct.tube("t40", "optic", 3, loc=(-0.25, -0.02, 0))
    ct.tube("pink", "pink", 3, loc=(-0.16, 0.14, 0))
    balls([(0.25, -0.15), (0.32, -0.04), (-0.06, -0.2), (0.15, -0.26)])
    st.soft_lights(target=(0, 0, 0.15), scale=1.0, key=1.6)
    st.camera((0.0, 0, 0.16), azimuth_deg=-6, elev_deg=14, dist=1.75, lens=60, dof=8)
    return (1200, 900, 40)


def cat_bags():
    st.backdrop("#E0C9B4")
    group(lambda: gr.backpack("forest"), (-0.2, 0.12, 0), R(-15))
    group(gr.duffel, (0.18, -0.08, 0), R(18))
    st.soft_lights(target=(0, 0, 0.2), scale=1.5)
    st.camera((0.0, 0, 0.22), azimuth_deg=-18, elev_deg=12, dist=2.3, lens=60, dof=8)
    return (1200, 900, 40)


def cat_apparel():
    st.backdrop("#7F998F")
    group(lambda: gr.cap("forest"), (-0.13, 0.03, 0), R(-25))
    group(lambda: gr.visor("optic"), (0.15, -0.02, 0), R(30))
    gr.wristband("chalk", loc=(0.02, -0.16, 0))
    gr.headband("clay", loc=(-0.2, -0.17, 0.0))
    st.soft_lights(target=(0, 0, 0.06), scale=0.75)
    st.camera((0.01, -0.02, 0.06), azimuth_deg=-10, elev_deg=22, dist=1.15, lens=60, dof=5)
    return (1200, 900, 40)


def cat_training():
    st.backdrop("#E6DFD2")
    for i, c in enumerate(["volt", "coral", "glacier"]):
        for k in range(3):
            ct.dish_cone(c, loc=(-0.3 + i * 0.2, -0.05, k * 0.009))
    r = ct.retriever()
    r.rotation_euler = (R(90), 0, R(-70))
    r.location = (0.25, 0.25, 0.045)
    balls([(0.1, -0.2), (0.2, -0.12), (-0.05, -0.24)])
    st.soft_lights(target=(0, 0, 0.05), scale=1.2)
    st.camera((0.0, 0.0, 0.04), azimuth_deg=-8, elev_deg=38, dist=1.9, lens=60, dof=8)
    return (1200, 900, 40)


def cat_accessories():
    st.backdrop(GREEN, rough=0.95)
    ct.bottle()
    for c, x, y in (("#EFEADF", 0.14, -0.04), ("#D9F24F", 0.21, 0.04)):
        ct.roll(c, 0.026, 0.009, 0.028, loc=(x, y, 0))
    ct.eraser(loc=(-0.15, -0.06, 0.016), rot_z=R(20))
    ct.towel_roll("#C9603A", (-0.2, 0.16, 0.048)).rotation_euler = (0, R(90), R(15))
    st.soft_lights(target=(0, 0, 0.1), scale=0.8, key=1.6)
    st.camera((0.02, 0, 0.1), azimuth_deg=-8, elev_deg=20, dist=1.25, lens=60, dof=5.6)
    return (1200, 900, 40)


def story():
    """Overhead flat lay of a match-day kit on court green."""
    st.backdrop(GREEN, rough=0.95)
    p = mc.paddle("TS-SIG-RAW")
    p.rotation_euler = (R(-3.2), 0, R(-24))
    p.location = (-0.04, -0.24, p["thick"] / 2 + 0.0135)
    group(ct.bottle, (-0.12, 0.22, 0.04), R(-35), R(90))
    ct.towel_roll("#EFEADF", (0.1, 0.27, 0.048)).rotation_euler = (0, R(90), R(-15))
    balls([(0.2, -0.1), (0.25, -0.02), (0.15, -0.17)])
    gr.wristband("chalk", loc=(-0.22, -0.12, 0.0))
    ct.roll("#D9F24F", 0.026, 0.009, 0.028, loc=(0.18, 0.08, 0))
    st.soft_lights(target=(0, 0, 0), scale=1.1, key=1.6)
    st.camera((0.0, 0.02, 0.0), azimuth_deg=-3, elev_deg=89.5, dist=1.55, lens=60)
    return (1200, 1400, 40)


def spotlight():
    st.backdrop("#121A17", rough=0.95)
    standing("TS-SIG-RAW", 0.0, 0.0, -24, 8)
    balls([(0.13, -0.11)])
    st.soft_lights(target=(0, 0, 0.2), scale=1.0, key=1.8)
    st.camera((0.02, 0, 0.21), azimuth_deg=-14, elev_deg=8, dist=1.45, lens=85, dof=4)
    return (1200, 1200, 40)


def workshop():
    ct.walnut_mount()
    st.soft_lights(target=(0, 0, 0.45), scale=1.3)
    st.camera((0, 0, 0.52), azimuth_deg=-14, elev_deg=6, dist=1.25, lens=50, dof=6)
    return (1600, 1000, 40)


SCENES = {"hero": hero, "cat_paddles": cat_paddles, "cat_balls": cat_balls, "cat_bags": cat_bags,
          "cat_apparel": cat_apparel, "cat_training": cat_training, "cat_accessories": cat_accessories,
          "story": story, "spotlight": spotlight, "workshop": workshop}


def main(argv):
    preview = "--preview" in argv
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("--")]
    if names == ["ALL"]:
        names = list(SCENES)
    for n in names:
        out = os.path.join(OUT, "preview" if preview else "", n + ".png")
        if os.path.exists(out) and not force and not preview:
            print("skip", out)
            continue
        st.reset(800, 600, 12, threads=3)
        w, h, samples = SCENES[n]()
        s = bpy.context.scene
        if preview:
            w, h, samples = w // 3, h // 3, 12
        s.render.resolution_x, s.render.resolution_y = w, h
        s.cycles.samples = samples
        t = time.time()
        st.render(out)
        print(f"RENDERED {n} in {time.time() - t:.1f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
