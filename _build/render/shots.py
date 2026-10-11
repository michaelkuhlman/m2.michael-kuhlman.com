"""Shot list: SKU -> list of shot builders. Each builder populates the scene and places the camera.

Output files: _build/renders/<SKU>_<n>.png (n from 1). Configurable children get their own hero shots;
parents without own shots (TS-KLC16, TS-COVER...) reuse children images in the seeder.
"""
import math
import random

import bpy

import models_core as mc
import models_court as ct
import models_gear as gr
import studio as st

R = math.radians


def cam(target, dist, az=-15, el=10, lens=85, dof=None, scale=1.0, key=1.0):
    st.soft_lights(target=target, scale=scale, key=key)
    st.camera(target, azimuth_deg=az, elev_deg=el, dist=dist, lens=lens, dof=dof)


# ---------------------------------------------------------------- paddles
def paddle_hero(sku, ball="optic"):
    def b():
        p = mc.paddle(sku)
        p.rotation_euler = (R(90 - 8), 0, R(-22))
        mc.ball(ball, loc=(0.125, -0.10, 0.037), rot=(0.3, 0.2, 0.1))
        cam((0.012, 0, 0.205), 1.38, az=-12, el=9, dof=5.6)
    return b


def paddle_flat(sku, balls=("optic", "optic")):
    def b():
        p = mc.paddle(sku)
        p.rotation_euler = (0, 0, R(-14))
        p.location = (-0.01, -0.2, p["thick"] / 2 + 0.0135)
        # rest the slab on the grip thickness: tilt so the head touches the floor
        p.rotation_euler = (R(-3.2), 0, R(-14))
        rng = random.Random(len(sku))
        for k, c in enumerate(balls):
            mc.ball(c, loc=(0.125 + 0.035 * k, -0.095 - 0.085 * k, 0.037), rot=ct.rand_rot(rng))
        cam((0.03, -0.01, 0.0), 1.36, az=-4, el=89.5, lens=85)
    return b


def paddle_detail(sku):
    def b():
        p = mc.paddle(sku)
        p.rotation_euler = (R(-3.2), 0, R(35))
        p.location = (0.07, -0.17, p["thick"] / 2 + 0.0135)
        mc.ball("optic", loc=(-0.13, -0.06, 0.037))
        cam((-0.01, -0.02, 0.02), 0.95, az=-25, el=34, lens=85, dof=4, scale=0.8)
    return b


def paddle_pair(a, c):
    def b():
        for sku, x, yaw in ((a, -0.118, -12), (c, 0.118, 14)):
            p = mc.paddle(sku)
            p.rotation_euler = (R(90 - 7), 0, R(yaw))
            p.location = (x, 0.02 if x < 0 else -0.02, 0)
        cam((0.0, 0, 0.21), 1.55, az=-8, el=8, dof=8)
    return b


# ---------------------------------------------------------------- balls
def balls_tube(label, colour, n=3, kind="outdoor", glow=False, extra=1):
    def b():
        ct.tube(label, colour, n, kind, loc=(-0.035, 0.0, 0.0), glow=glow)
        rng = random.Random(1)
        for k in range(extra):
            mc.ball(colour, kind, loc=(0.075 + 0.02 * k, -0.07 - 0.06 * k, 0.037), rot=ct.rand_rot(rng), glow=glow)
        cam((0.01, 0, 0.13), 0.95, az=-10, el=12, dof=5.6, scale=0.6)
    return b


def balls_macro(colour, kind="outdoor", glow=False):
    def b():
        rng = random.Random(4)
        for k, (x, y) in enumerate([(0, 0), (-0.06, 0.07), (0.075, 0.06)]):
            mc.ball(colour, kind, loc=(x, y, 0.037), rot=ct.rand_rot(rng), glow=glow)
        cam((0, 0.03, 0.035), 0.68, az=-18, el=18, dof=3.5, scale=0.45)
    return b


def balls_pyramid(colour, kind="outdoor", label=None, glow=False):
    def b():
        ct.pyramid(colour, kind, glow=glow)
        if label:
            ct.tube(label, colour, 3, kind, loc=(0.16, 0.09, 0.0), glow=glow)
        cam((0.03, 0.03, 0.08), 1.0, az=-12, el=14, dof=5.6, scale=0.6)
    return b


def box12_shot():
    def b():
        ct.box12()
        cam((0, 0.02, 0.07), 1.3, az=-14, el=38, dof=8, scale=0.8)
    return b


def bucket_shot(with_tube=False):
    def b():
        ct.bucket48()
        rng = random.Random(9)
        for x, y in ((0.2, -0.08), (0.27, 0.02), (-0.2, -0.1)):
            mc.ball("optic", loc=(x, y, 0.037), rot=ct.rand_rot(rng))
        if with_tube:
            ct.tube("t40", "optic", 3, loc=(-0.24, 0.08, 0))
            ct.box12(loc=(0.05, 0.38, 0))
        cam((0, 0, 0.17), 1.65 if not with_tube else 2.0, az=-14, el=14, dof=8, scale=0.9)
    return b


# ---------------------------------------------------------------- bags
def generic(build, target, dist, az=-18, el=12, dof=6.3, scale=1.0, lens=85):
    def b():
        build()
        cam(target, dist, az=az, el=el, dof=dof, scale=scale, lens=lens)
    return b


def cover_shot(colour, flat=False):
    def b():
        p = gr.cover(colour)
        if flat:
            p.rotation_euler = (R(-3), 0, R(-12))
            p.location = (0, -0.2, 0.03)
            cam((0, 0, 0), 1.3, az=-4, el=89.5)
        else:
            p.rotation_euler = (R(90 - 8), 0, R(-20))
            mc.ball("optic", loc=(0.13, -0.1, 0.037))
            cam((0.01, 0, 0.21), 1.42, az=-12, el=9, dof=5.6)
    return b


def case_shot(flat=False):
    def b():
        c = gr.hard_case()
        if flat:
            c.rotation_euler = (0, 0, R(-12))
            c.location = (0, -0.22, 0.0285)
            mc.ball("optic", loc=(0.19, 0.05, 0.037))
            cam((0.03, 0, 0), 1.6, az=-4, el=89.5)
        else:
            c.rotation_euler = (R(90 - 10), 0, R(-25))
            c.location = (0, 0, 0.0)
            cam((0, 0, 0.22), 1.5, az=-12, el=10, dof=5.6)
    return b


def pouch_shot():
    def b():
        gr.pouch()
        mc.ball("optic", loc=(0.1, -0.06, 0.037))
        cam((0.02, 0, 0.09), 0.85, az=-20, el=14, dof=4, scale=0.5)
    return b


# ---------------------------------------------------------------- apparel
LIGHT = "#A8A091"


def hat_shot(fn, *args, az=-28, el=16, dist=0.85, target=(0, 0, 0.07), dark_bg=False):
    def b():
        if dark_bg or "chalk" in args:
            st.retint_backdrop(LIGHT)
        fn(*args)
        cam(target, dist, az=az, el=el, dof=4, scale=0.55)
    return b


def headband_shot():
    def b():
        st.retint_backdrop(LIGHT)
        gr.headband("chalk", loc=(-0.04, 0.03, 0.0), rot=(0, 0, R(15)))
        gr.headband("charcoal", loc=(0.06, -0.06, 0.0), rot=(R(78), 0, R(-20))).location.z = 0.088
        cam((0.01, 0, 0.06), 1.0, az=-15, el=24, dof=5, scale=0.6)
    return b


def wrist_shot():
    def b():
        st.retint_backdrop(LIGHT)
        gr.wristband("chalk", loc=(-0.045, 0.02, 0.0))
        gr.wristband("chalk", loc=(0.06, -0.04, 0.043), rot=(R(90), 0, R(25)))
        mc.ball("optic", loc=(0.03, 0.09, 0.037))
        cam((0.01, 0.01, 0.04), 0.75, az=-15, el=18, dof=4, scale=0.5)
    return b


# ---------------------------------------------------------------- training
def net_shot(close=False):
    def b():
        st.big_backdrop()
        st.world(1.6, "#F4EFE6")
        ct.net_system()
        if close:
            mc.ball("optic", loc=(3.0, -0.25, 0.037))
            st.soft_lights(target=(3.2, 0, 0.5), scale=2.2)
            st.camera((3.0, 0, 0.4), azimuth_deg=-35, elev_deg=22, dist=2.6, lens=50, dof=8)
        else:
            st.soft_lights(target=(0, 0, 0.45), scale=4.5)
            st.camera((0.9, 0, 0.3), azimuth_deg=-58, elev_deg=26, dist=5.4, lens=35)
    return b


def retriever_shot():
    def b():
        r = ct.retriever()
        r.rotation_euler = (R(90), 0, R(-55))
        r.location = (0.39, 0.27, 0.045)
        rng = random.Random(3)
        for x, y in ((0.47, 0.4), (0.3, 0.42), (0.55, 0.22)):
            mc.ball("optic", loc=(x, y, 0.037), rot=ct.rand_rot(rng))
        cam((0.07, 0.08, 0.03), 3.2, az=-8, el=58, dof=None, scale=1.4)
    return b


def cones_shot():
    def b():
        cols = ["volt", "coral", "glacier", "chalk"]
        for i, c in enumerate(cols):
            x, y = (-0.11 + 0.22 * (i % 2), -0.1 + 0.2 * (i // 2))
            for k in range(3):
                ct.dish_cone(c, loc=(x, y, k * 0.009))
        ct.dish_cone("volt", loc=(0.26, -0.24, 0)).rotation_euler = (0, 0, 0)
        st.retint_backdrop(LIGHT)
        cam((0.06, -0.04, 0.02), 1.75, az=-12, el=34, dof=8, scale=0.8)
    return b


def generic_court(build, target, dist, az=-15, el=25, scale=1.0, lens=85, dof=8):
    return generic(build, target, dist, az=az, el=el, dof=dof, scale=scale, lens=lens)


# ---------------------------------------------------------------- accessories
def overgrip_shot():
    def b():
        st.retint_backdrop(LIGHT)
        for k, (c, x, y) in enumerate((("#EFEADF", -0.06, 0.03), ("#2A2F2D", 0.0, 0.08), ("#D9F24F", 0.06, 0.02))):
            ct.roll(c, 0.026, 0.009, 0.028, loc=(x, y, 0))
        ct.tape_tail("#D9F24F", [(0.06, -0.005, 0.0012), (0.07, -0.06, 0.0012), (0.05, -0.12, 0.0012),
                                 (0.0, -0.16, 0.0012)], 0.025)
        cam((0.0, 0.0, 0.02), 0.72, az=-12, el=38, dof=4, scale=0.45)
    return b


def grip_shot():
    def b():
        ct.roll("#2A2F2D", 0.034, 0.01, 0.026, loc=(-0.02, 0.03, 0), perforated=True, name="cush")
        ct.tape_tail("#2A2F2D", [(-0.02, -0.004, 0.0012), (0.0, -0.06, 0.0012), (0.05, -0.1, 0.0012),
                                 (0.11, -0.12, 0.0012)], 0.026, perforated=True)
        ct.roll("#D9F24F", 0.016, 0.009, 0.019, loc=(0.07, 0.05, 0), name="fin")
        cam((0.02, 0.0, 0.015), 0.7, az=-10, el=40, dof=4, scale=0.45)
    return b


def edge_shot():
    def b():
        p = mc.paddle("TS-SIG-RAW")
        p.rotation_euler = (R(-3.2), 0, R(115))
        p.location = (0.12, 0.08, p["thick"] / 2 + 0.0135)
        clear = ct.clear_plastic("edgetape", "#E8EEF0")
        r = ct.sh.ring("edge", 0.05, 0.038, 0.025, clear, bevel=0.0015)
        r.location = (-0.07, -0.05, 0)
        core = ct.sh.ring("ecore", 0.038, 0.034, 0.025, st.mat("ecore", "#B98C5C", rough=0.8))
        core.location = r.location
        r2 = ct.sh.ring("edge2", 0.046, 0.038, 0.025, clear, bevel=0.0015)
        r2.rotation_euler = (R(90), 0, R(30))
        r2.location = (0.0, -0.13, 0.046)
        c2 = ct.sh.ring("ecore2", 0.038, 0.034, 0.025, st.mat("ecore", "#B98C5C", rough=0.8))
        c2.rotation_euler = r2.rotation_euler
        c2.location = r2.location
        cam((-0.02, -0.06, 0.02), 0.8, az=-12, el=30, dof=4, scale=0.5)
    return b


def lead_shot():
    def b():
        st.retint_backdrop(LIGHT)
        c = ct.lead_card(loc=(0, 0.02, 0.066))
        c.rotation_euler = (R(-12), 0, R(8))
        lead = st.mat("leadr", "#8F9497", rough=0.4, metal=0.9)
        r = ct.sh.ring("leadroll", 0.03, 0.02, 0.0127, lead, bevel=0.001)
        r.location = (0.075, -0.06, 0)
        cam((0.01, 0, 0.06), 0.72, az=-12, el=10, dof=4, scale=0.45)
    return b


def eraser_shot():
    def b():
        ct.eraser(loc=(-0.03, 0.02, 0.016), rot_z=R(8))
        ct.eraser(loc=(0.075, -0.05, 0.016), rot_z=R(-25), sleeve=False)
        cam((0.02, -0.01, 0.015), 0.62, az=-14, el=24, dof=3.5, scale=0.4)
    return b


def bottle_shot(second=False):
    def b():
        ct.bottle()
        if second:
            gr.wristband("chalk", loc=(0.08, -0.06, 0.0))
        cam((0.0, 0, 0.14), 0.95, az=-14, el=8, dof=5, scale=0.55)
    return b


def towel_shot():
    def b():
        st.retint_backdrop(LIGHT)
        for (c, px, z) in (("#CDBF9F", -1, 0.048), ("#1F4A3C", 1, 0.048), ("#C9603A", 0, 0.137)):
            cx, cy = px * 0.045 * 1.0, px * -0.026
            ct.towel_roll(c, (cx - 0.075, cy - 0.13, z), rot_z=0.0).rotation_euler = (0, R(90), R(60))
        cam((0.0, 0, 0.07), 1.3, az=-30, el=22, dof=6, scale=0.7)
    return b


def mount_shot():
    def b():
        ct.walnut_mount()
        st.soft_lights(target=(0, 0, 0.45), scale=1.1)
        st.camera((0, 0, 0.5), azimuth_deg=-10, elev_deg=4, dist=1.9, lens=85, dof=8)
    return b


# ---------------------------------------------------------------- table
def _shots():
    S = {}
    for s in ("TS-KLC16-VOLT", "TS-KLC16-CORAL", "TS-KLC16-GLACIER"):
        S[s] = [paddle_hero(s), paddle_flat(s)]
    S["TS-KLC16"] = [paddle_detail("TS-KLC16-VOLT"), paddle_pair("TS-KLC16-CORAL", "TS-KLC16-GLACIER")]
    for s in ("TS-APX14", "TS-DZC16", "TS-SIG-RAW", "TS-HYB13", "TS-BLP14", "TS-DCF", "TS-ROOK", "TS-JR",
              "TS-WOOD", "TS-WTR"):
        S[s] = [paddle_hero(s), paddle_flat(s), paddle_detail(s)]
    S["TS-SET-START"] = [paddle_pair("TS-ROOK", "TS-DCF"), cover_shot("forest")]
    S["TS-T40-3"] = [balls_tube("t40", "optic"), balls_macro("optic")]
    S["TS-T40-12"] = [box12_shot(), balls_macro("optic")]
    S["TS-T40-48"] = [bucket_shot()]
    S["TS-G26-6"] = [balls_pyramid("optic", "indoor", "g26"), balls_macro("optic", "indoor")]
    S["TS-GLOW-3"] = [balls_tube("glow", "glow", glow=True), balls_macro("glow", glow=True)]
    S["TS-T40-PINK"] = [balls_pyramid("pink", "outdoor", "pink"), balls_macro("pink")]
    S["TS-T40-BULK"] = [bucket_shot(with_tube=True)]
    S["TS-BAG-CLUB-FOREST"] = [generic(lambda: gr.backpack("forest"), (0, 0, 0.25), 1.75, az=-24, el=10)]
    S["TS-BAG-CLUB-SAND"] = [generic(lambda: gr.backpack("sand"), (0, 0, 0.25), 1.75, az=-24, el=10)]
    S["TS-BAG-CLUB"] = [generic(lambda: gr.backpack("forest"), (0, 0, 0.25), 1.75, az=35, el=14)]
    S["TS-BAG-TOUR"] = [generic(gr.duffel, (0, 0, 0.17), 1.9, az=-22, el=16, scale=1.2),
                        generic(gr.duffel, (0, 0, 0.15), 1.9, az=20, el=30, scale=1.2)]
    S["TS-BAG-SLING"] = [generic(gr.sling, (0, 0, 0.24), 1.45, az=-18, el=10)]
    for c in ("forest", "optic", "clay"):
        S["TS-COVER-" + c.upper()] = [cover_shot(c)]
    S["TS-COVER"] = [cover_shot("forest", flat=True)]
    S["TS-CASE"] = [case_shot(), case_shot(flat=True)]
    S["TS-POUCH"] = [pouch_shot()]
    for c in ("forest", "chalk", "clay"):
        S["TS-CAP-" + c.upper()] = [hat_shot(gr.cap, c)]
    S["TS-CAP"] = [hat_shot(gr.cap, "forest", az=60, el=20)]
    for c in ("chalk", "optic", "forest"):
        S["TS-VISOR-" + c.upper()] = [hat_shot(gr.visor, c, target=(0, 0, 0.045))]
    S["TS-VISOR"] = [hat_shot(gr.visor, "forest", az=55, el=22, target=(0, 0, 0.045))]
    S["TS-BUCKET"] = [hat_shot(gr.bucket_hat, az=-20, el=18, dist=1.0, target=(0, 0, 0.07), dark_bg=True)]
    S["TS-BEANIE"] = [hat_shot(gr.beanie, az=-18, el=12, dist=0.9, target=(0, 0, 0.1))]
    S["TS-HEADBAND"] = [headband_shot()]
    S["TS-WRIST"] = [wrist_shot()]
    S["TS-NET"] = [net_shot(), net_shot(close=True)]
    S["TS-RETRIEVER"] = [retriever_shot()]
    S["TS-CONES"] = [cones_shot()]
    S["TS-LINES"] = [generic_court(lambda: (st.retint_backdrop(LIGHT), ct.line_kit()), (0, -0.04, 0.02), 1.3, az=-10, el=52)]
    S["TS-REBOUND"] = [generic_court(lambda: (ct.rebounder(), mc.ball("optic", loc=(0.2, -0.35, 0.037))),
                                     (0, 0.1, 0.42), 3.0, az=-28, el=10, scale=1.8)]
    S["TS-LADDER"] = [generic_court(lambda: (st.big_backdrop(), ct.ladder()), (0, 0.25, 0.0), 2.7, az=-22, el=40,
                                    scale=2.0, lens=50)]
    S["TS-OVERGRIP"] = [overgrip_shot()]
    S["TS-GRIP"] = [grip_shot()]
    S["TS-EDGE"] = [edge_shot()]
    S["TS-LEAD"] = [lead_shot()]
    S["TS-ERASER"] = [eraser_shot()]
    S["TS-BOTTLE"] = [bottle_shot(), bottle_shot(second=True)]
    S["TS-TOWEL"] = [towel_shot()]
    S["TS-MOUNT"] = [mount_shot()]
    return S


SHOTS = _shots()
