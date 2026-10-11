"""Ball packaging, court & training gear and accessories. Z up, ground z=0, camera from -Y."""
import math
import os
import random

import bpy
from mathutils import Vector

import models_core as mc
import shapes as sh
import studio as st

TEX = st.TEX
IN = mc.IN
COL = {"forest": "#1F4A3C", "kitchen": "#173A2E", "chalk": "#EFEADF", "optic": "#D9F24F", "clay": "#C9603A",
       "charcoal": "#2E3434", "coral": "#EC7A5C", "glacier": "#9ED2E4", "kraft": "#B98C5C", "sand": "#D9CDB4",
       "ink": "#16201C", "volt": "#D9F24F"}


def tex(n):
    return os.path.join(TEX, n)


def clear_plastic(name="pet", tint="#F4F8F6"):
    """Thin clear plastic: mostly transparent with a glossy sheen (avoids dark thin-shell refraction)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    out = nt.nodes["Material Output"]
    pb = nt.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = st.col(tint)
    pb.inputs["Roughness"].default_value = 0.05
    pb.inputs["Specular IOR Level"].default_value = 0.6
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    fr = nt.nodes.new("ShaderNodeLayerWeight")
    fr.inputs["Blend"].default_value = 0.35
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs["Fresnel"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(pb.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


def rand_rot(rng):
    return (rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28))


# ------------------------------------------------------------------ ball packaging
def tube(label="t40", colour="optic", n=3, kind="outdoor", loc=(0, 0, 0), glow=False):
    rng = random.Random(7)
    h = 0.012 + n * 0.0752 + 0.004
    x, y, z0 = loc
    t = sh.lathe("tube", [(0.0388, 0.0), (0.0388, h)], 96, clear_plastic())
    t.modifiers.new("sol", "SOLIDIFY").thickness = 0.0009
    cap = st.mat("tubecap", COL["kitchen"], rough=0.4)
    for zc in (0.0, h - 0.004):
        c = sh.ring("cap", 0.0405, 0.0, 0.016, cap, bevel=0.003, z0=-0.006 if zc == 0 else 0)
        c.location = (x, y, z0 + zc)
    lab = sh.lathe("label", [(0.0392, h * 0.5 - 0.042), (0.0392, h * 0.5 + 0.042)], 96,
                   sh.image_mat("lab_" + label, tex(f"wrap_{label}.png"), rough=0.45))
    for o in (t, lab):
        o.location = (x, y, z0)
    for k in range(n):
        mc.ball(colour, kind, loc=(x, y, z0 + 0.012 + 0.037 + k * 0.0752), rot=rand_rot(rng), glow=glow)
    return t


def pyramid(colour, kind="outdoor", loc=(0, 0, 0), glow=False, seed=3):
    """6 balls: 3 + 2 + 1."""
    rng = random.Random(seed)
    r = 0.037
    x0, y0, _ = loc
    pts = [(-2 * r, 0, r), (0, 0, r), (2 * r, 0, r), (-r, 0, r + 2 * r * 0.866), (r, 0, r + 2 * r * 0.866),
           (0, 0, r + 4 * r * 0.866)]
    for (x, y, z) in pts:
        mc.ball(colour, kind, loc=(x0 + x, y0 + y + 0.0, z), rot=rand_rot(rng), glow=glow)


def box12(loc=(0, 0, 0)):
    rng = random.Random(11)
    kraft = st.mat("kraft", COL["kraft"], rough=0.85)
    st.add_proc_bump(kraft, "noise", scale=900, strength=0.1, distance=0.0004)
    W, D, H, t = 0.32, 0.245, 0.075, 0.004
    x, y, z = loc
    sh.rbox("bot", (W, D, t), 0.001, kraft, loc=(x, y, z + t / 2))
    for sx in (-1, 1):
        sh.rbox("wx", (t, D, H), 0.001, kraft, loc=(x + sx * (W / 2 - t / 2), y, z + H / 2))
        sh.rbox("wy", (W, t, H), 0.001, kraft, loc=(x, y + sx * (D / 2 - t / 2), z + H / 2))
    lid = sh.rbox("lid", (W, t, D), 0.001, kraft, loc=(x, y + D / 2 + 0.03, z + H + D / 2 - 0.02))
    lid.rotation_euler = (math.radians(-14), 0, 0)
    d = sh.decal("lidprint", tex("box_t40_12.png"), 0.26, 0.108, (x, y + D / 2 + 0.03 - 0.0035, z + H + D / 2 - 0.02),
                 (math.radians(90 - 14), 0, 0), rough=0.7)
    d2 = sh.decal("frontprint", tex("box_kraft.png"), 0.2, 0.083 * 0.83, (x, y - D / 2 - 0.0006, z + H / 2),
                  (math.radians(90), 0, 0), rough=0.8)
    for i in range(4):
        for j in range(3):
            mc.ball("optic", loc=(x + (i - 1.5) * 0.0765, y + (j - 1) * 0.0765, z + t + 0.037), rot=rand_rot(rng))
    return lid


def bucket48(loc=(0, 0, 0)):
    rng = random.Random(5)
    x, y, z = loc
    pl = st.mat("bucket", COL["forest"], rough=0.38, coat=0.2)
    prof = [(0.0, 0.0), (0.108, 0.0), (0.112, 0.004), (0.135, 0.255), (0.142, 0.262), (0.142, 0.268)]
    b = sh.lathe("bucket", prof, 96, pl)
    b.modifiers.new("sol", "SOLIDIFY").thickness = 0.003
    lab = sh.lathe("blabel", [(0.1165, 0.06), (0.1305, 0.205)], 96,
                   sh.image_mat("bl", tex("wrap_bucket.png"), rough=0.4))
    lab.location = b.location = (x, y, z)
    wire = st.mat("wire", "#C9CDCF", rough=0.25, metal=1.0)
    sh.curve_tube("handle", [(x - 0.14, y, z + 0.235), (x - 0.12, y - 0.02, z + 0.36), (x, y - 0.03, z + 0.41),
                             (x + 0.12, y - 0.02, z + 0.36), (x + 0.14, y, z + 0.235)], 0.0028, wire)
    # heap of balls on top
    r = 0.037
    for layer, (zz, rad) in enumerate([(0.225, 0.10), (0.27, 0.07), (0.31, 0.02)]):
        k = 0
        ring_r = [0.0, 0.075, 0.105] if layer == 0 else ([0.0, 0.07] if layer == 1 else [0.0])
        for rr in ring_r:
            n = 1 if rr == 0 else int(2 * math.pi * rr / (2 * r * 1.02))
            off = rng.uniform(0, 1)
            for i in range(n):
                a = 2 * math.pi * (i + off) / n
                px, py = x + rr * math.cos(a), y + rr * math.sin(a)
                if layer == 1 and rr == 0:
                    continue
                mc.ball("optic", loc=(px, py, z + zz + rng.uniform(-0.004, 0.004)), rot=rand_rot(rng))
                k += 1
    return b


# ------------------------------------------------------------------ court & training
def net_material(colour="#1A1E1D", cell=0.045, line=0.12):
    m = bpy.data.materials.new("netmat")
    m.use_nodes = True
    nt = m.node_tree
    out = nt.nodes["Material Output"]
    pb = nt.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = st.col(colour)
    pb.inputs["Roughness"].default_value = 0.7
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mx = []
    for axis in ("X", "Y"):  # plane-local axes
        mth = nt.nodes.new("ShaderNodeMath")
        mth.operation = "PINGPONG"
        mth.inputs[1].default_value = cell / 2
        nt.links.new(sep.outputs[axis], mth.inputs[0])
        lt = nt.nodes.new("ShaderNodeMath")
        lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = cell * line / 2
        nt.links.new(mth.outputs[0], lt.inputs[0])
        mx.append(lt)
    mxn = nt.nodes.new("ShaderNodeMath")
    mxn.operation = "MAXIMUM"
    nt.links.new(mx[0].outputs[0], mxn.inputs[0])
    nt.links.new(mx[1].outputs[0], mxn.inputs[1])
    nt.links.new(mxn.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(pb.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


def net_system(length=6.7):
    steel = st.mat("powder", "#1D2221", rough=0.45, coat=0.2)
    tape = st.mat("tape", "#F2EFE7", rough=0.5)
    for sx in (-1, 1):
        x = sx * length / 2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.019, depth=0.9, location=(x, 0, 0.45), vertices=32)
        bpy.context.object.data.materials.append(steel)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.019, depth=0.62, location=(x, 0, 0.02), vertices=32,
                                            rotation=(math.radians(90), 0, 0))
        bpy.context.object.data.materials.append(steel)
        for sy in (-1, 1):
            sh.ring("foot", 0.024, 0.0, 0.02, st.mat("rubber", "#111111", rough=0.8), z0=0).location = (x, sy * 0.3, 0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.53), rotation=(math.radians(90), 0, 0))
    n = bpy.context.object
    n.scale = (length, 0.72, 1)
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    n.data.materials.append(net_material())
    sh.rbox("headband", (length, 0.004, 0.055), 0.001, tape, loc=(0, 0, 0.87))
    sh.rbox("strap", (0.05, 0.005, 0.72), 0.001, tape, loc=(0, 0, 0.53))
    sh.decal("netlogo", tex("print_kitchen.png"), 0.11, 0.07, (length * 0.25, -0.0035, 0.87),
             (math.radians(90), 0, 0))
    sh.decal("netlogo2", tex("print_kitchen.png"), 0.11, 0.07, (-length * 0.25, -0.0035, 0.87),
             (math.radians(90), 0, 0))
    return n


def retriever():
    rng = random.Random(2)
    before = set(bpy.context.scene.objects)
    an = st.mat("anod", COL["forest"], rough=0.3, metal=0.85)
    L = 0.95
    t = sh.lathe("rtube", [(0.041, 0.04), (0.041, L)], 96, an)
    t.modifiers.new("sol", "SOLIDIFY").thickness = 0.0015
    grip = st.mat("foam", "#1A1D1C", rough=0.85)
    st.add_proc_bump(grip, "noise", scale=500, strength=0.3)
    sh.lathe("rgrip", [(0.0435, L - 0.2), (0.0445, L - 0.19), (0.0445, L - 0.01), (0.043, L)], 96, grip)
    sh.ring("rcap", 0.044, 0.0, 0.02, st.mat("rc", COL["optic"], rough=0.4), bevel=0.004, z0=L - 0.004)
    steel = st.mat("spring", "#C9CDCF", rough=0.25, metal=1.0)
    sh.ring("rring", 0.043, 0.039, 0.012, steel, z0=0.035)
    for k in range(10):
        a = 2 * math.pi * k / 10
        sh.curve_tube("wire", [(0.041 * math.cos(a), 0.041 * math.sin(a), 0.04),
                               (0.045 * math.cos(a), 0.045 * math.sin(a), 0.015),
                               (0.03 * math.cos(a), 0.03 * math.sin(a), -0.012)], 0.0012, steel)
    objs = [o for o in bpy.context.scene.objects if o not in before and o.parent is None]
    root = st.parent_all(objs, "retriever")
    for k in range(4):
        mc.ball("optic", loc=(0.0, 0.0, 0.04 + 0.08 * k + 0.12), rot=rand_rot(rng)).parent = root
    return root


def dish_cone(colour, loc=(0, 0, 0)):
    m = st.mat("cone_" + colour, COL[colour], rough=0.42, spec=0.4)
    prof = [(0.022, 0.05), (0.03, 0.05), (0.05, 0.043), (0.075, 0.025), (0.09, 0.008), (0.095, 0.0)]
    c = sh.lathe("cone", prof, 96, m)
    c.modifiers.new("sol", "SOLIDIFY").thickness = 0.0022
    c.location = loc
    return c


def ladder(rungs=7):
    strap = st.mat("lstrap", "#151918", rough=0.7, sheen=0.3)
    rung = st.mat("lrung", COL["optic"], rough=0.4)
    span = 0.5
    for sx in (-1, 1):
        sh.rbox("lad", (0.045, rungs * 0.44, 0.004), 0.0015, strap, loc=(sx * span / 2, 0, 0.002))
    for k in range(rungs):
        sh.rbox("rung", (span + 0.05, 0.055, 0.012), 0.004, rung, loc=(0, (k - (rungs - 1) / 2) * 0.44, 0.006))


def rebounder():
    frame = st.mat("rframe", "#1E2322", rough=0.45, coat=0.2)
    W, H = 0.95, 0.9
    tilt = math.radians(14)
    pts = [(-W / 2, 0, 0.05), (-W / 2, 0, H), (W / 2, 0, H), (W / 2, 0, 0.05)]
    rect = sh.curve_tube("rframe", pts, 0.014, frame, smooth_pts=False, cyclic=True)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, (H + 0.05) / 2), rotation=(math.radians(90), 0, 0))
    n = bpy.context.object
    n.scale = (W - 0.03, H - 0.08, 1)
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    n.data.materials.append(net_material("#1A1E1D", cell=0.03, line=0.14))
    tgt = sh.rbox("target", (0.34, 0.004, 0.08), 0.001, st.mat("tgt", COL["optic"], rough=0.5), loc=(0, -0.003, 0.38))
    root = st.parent_all([rect, n, tgt], "reb")
    root.rotation_euler = (-tilt, 0, 0)
    for sx in (-1, 1):
        sh.curve_tube("leg", [(sx * W / 2, H * math.sin(tilt) + 0.0, H * math.cos(tilt)), (sx * W / 2, 0.5, 0.0)],
                      0.012, frame, smooth_pts=False)
        sh.curve_tube("base", [(sx * W / 2, -0.04, 0.012), (sx * W / 2, 0.52, 0.012)], 0.012, frame,
                      smooth_pts=False)
    return root


def line_kit():
    vinyl = st.mat("vinyl", "#F2F0EA", rough=0.4)
    rub = {c: st.mat("rub_" + c, COL[c], rough=0.6) for c in ("optic", "clay")}
    r1 = sh.ring("roll", 0.06, 0.036, 0.05, vinyl, bevel=0.002)
    r1.location = (-0.08, 0.05, 0.0)
    core = sh.ring("core", 0.036, 0.032, 0.05, st.mat("cardb", COL["kraft"], rough=0.8))
    core.location = r1.location
    r2 = sh.ring("roll2", 0.055, 0.036, 0.05, vinyl, bevel=0.002)
    r2.rotation_euler = (math.radians(90), 0, math.radians(20))
    r2.location = (0.12, 0.12, 0.055)
    sh.curve_tube("tail", [(-0.02, 0.05, 0.001), (0.05, -0.05, 0.001), (0.12, -0.15, 0.001), (0.22, -0.2, 0.001)],
                  0, vinyl, flat=0.05).modifiers.new("s", "SOLIDIFY").thickness = 0.0012
    for k, (x, y, a, c) in enumerate([(-0.2, -0.15, 10, "optic"), (-0.05, -0.25, -15, "clay"),
                                      (0.2, 0.0, 30, "optic"), (-0.24, 0.1, 60, "clay")]):
        lg = sh.rbox("L1", (0.12, 0.03, 0.006), 0.002, rub[c], loc=(0.045, 0, 0.003))
        lg2 = sh.rbox("L2", (0.03, 0.12, 0.006), 0.002, rub[c], loc=(0, 0.045, 0.003))
        e = st.parent_all([lg, lg2], "L")
        e.location = (x, y, 0)
        e.rotation_euler = (0, 0, math.radians(a))


# ------------------------------------------------------------------ accessories
def roll(colour, r_out, r_in, width, loc=(0, 0, 0), rot=(0, 0, 0), perforated=False, name="roll"):
    m = st.mat(name + colour, colour, rough=0.55 if not perforated else 0.7, sheen=0.2)
    if perforated:
        st.add_proc_bump(m, "voronoi", scale=420, strength=0.35, distance=0.0008)
    else:
        st.add_proc_bump(m, "wave", scale=300, strength=0.2, distance=0.0003, wave_type="RINGS", direction="Z")
    r = sh.ring(name, r_out, r_in, width, m, bevel=0.0015)
    r.location = loc
    r.rotation_euler = rot
    return r


def tape_tail(colour, pts, width, perforated=False):
    m = st.mat("tail" + colour, colour, rough=0.55)
    if perforated:
        st.add_proc_bump(m, "voronoi", scale=420, strength=0.35, distance=0.0008)
    t = sh.curve_tube("tail", pts, 0, m, flat=width)
    t.modifiers.new("s", "SOLIDIFY").thickness = 0.0008
    return t


def bottle(colour="#1F4A3C"):
    body = st.mat("powder", colour, rough=0.55, spec=0.4)
    st.add_proc_bump(body, "noise", scale=3000, strength=0.05)
    prof = [(0.0, 0.0), (0.036, 0.0), (0.0395, 0.004), (0.0395, 0.205), (0.037, 0.228), (0.03, 0.242),
            (0.0275, 0.248)]
    b = sh.lathe("bottle", prof, 128, body)
    lab = sh.lathe("blab", [(0.0397, 0.07), (0.0397, 0.18)], 128, sh.image_mat("bw", tex("wrap_bottle.png"), rough=0.55))
    lab.rotation_euler = (0, 0, math.radians(90))  # label centre (u=0.5) faces the camera (-Y)
    steel = st.mat("bsteel", "#C2C6C8", rough=0.3, metal=1.0)
    st.add_proc_bump(steel, "wave", scale=2000, strength=0.05, direction="Z")
    sh.lathe("bbase", [(0.036, -0.0005), (0.0398, 0.0035), (0.0398, 0.012)], 128, steel)
    capm = st.mat("bcap", "#16201C", rough=0.45)
    sh.ring("bcap", 0.031, 0.0, 0.032, capm, bevel=0.004, z0=0.247)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.018, minor_radius=0.005, location=(0, 0, 0.287),
                                     rotation=(math.radians(90), 0, 0))
    lp = bpy.context.object
    lp.scale = (1.0, 1.0, 0.8)
    lp.data.materials.append(capm)
    st.smooth(lp)
    return b


def towel(colour, loc, rot_z=0.0, size=(0.34, 0.17, 0.04)):
    m = st.mat("towel" + colour, colour, rough=0.92, sheen=0.7, spec=0.2)
    st.add_proc_bump(m, "voronoi", scale=180, strength=0.45, distance=0.0015)
    t = sh.pillow("towel", size, m, levels=2, loc=loc)
    t.rotation_euler = (0, 0, rot_z)
    for k in (-1, 1):
        f = sh.rbox("fold", (size[0] * 0.98, 0.004, size[2] * 0.6), 0.002, m,
                    loc=(loc[0], loc[1] + k * size[1] * 0.25, loc[2] + size[2] * 0.36))
        f.parent = t
        f.location = (0, k * size[1] * 0.25, size[2] * 0.36)
        f.hide_render = True
    return t


def towel_roll(colour, loc, rot_z=0.0, length=0.3, r=0.048):
    """Rolled microfibre towel lying on its side: spiral end via ring bands, waffle bump."""
    m = st.mat("towelr" + colour, colour, rough=0.93, sheen=0.8, spec=0.2)
    st.add_proc_bump(m, "voronoi", scale=260, strength=0.35, distance=0.0012)
    prof = [(0.004, 0.0), (r - 0.012, 0.0)]
    prof += [(r - 0.012 + 0.012 * math.sin(t * math.pi / 8), 0.012 - 0.012 * math.cos(t * math.pi / 8)) for t in range(1, 5)]
    prof += [(r, length - 0.012)]
    prof += [(r - 0.012 + 0.012 * math.cos(t * math.pi / 8), length - 0.012 + 0.012 * math.sin(t * math.pi / 8))
             for t in range(1, 5)]
    prof += [(0.004, length)]
    t = sh.lathe("troll", prof, 96, m)
    spiral = st.mat("towelend" + colour, colour, rough=0.95, sheen=0.8, spec=0.2)
    st.add_proc_bump(spiral, "wave", scale=95, strength=0.9, distance=0.003, wave_type="RINGS", direction="Z",
                     profile="SIN")
    for z in (-0.0005, length + 0.0005):
        bpy.ops.mesh.primitive_circle_add(radius=r - 0.004, vertices=64, fill_type="NGON", location=(0, 0, z))
        cap = bpy.context.object
        cap.data.materials.append(spiral)
        cap.parent = t
    t.rotation_euler = (0, math.radians(90), rot_z)
    t.location = loc
    return t


def eraser(loc=(0, 0, 0), rot_z=0.0, sleeve=True):
    m = st.mat("crepe", "#D2A15E", rough=0.85, sss=0.25, spec=0.3)
    st.add_proc_bump(m, "noise", scale=160, strength=0.6, distance=0.0015)
    e = sh.rbox("eraser", (0.088, 0.052, 0.032), 0.006, m, loc=loc)
    e.rotation_euler = (0, 0, rot_z)
    if sleeve:
        kraft = st.mat("sleeve", COL["kraft"], rough=0.85)
        s = sh.rbox("sleeve", (0.05, 0.0545, 0.0345), 0.002, kraft)
        s.parent = e
        d = sh.decal("sleevep", tex("card_eraser.png"), 0.05, 0.0175, (0, -0.0274, 0), (math.radians(90), 0, 0),
                     rough=0.8, alpha=False)
        d.parent = e
    return e


def lead_card(loc=(0, 0, 0)):
    c = sh.rbox("card", (0.09, 0.0025, 0.13), 0.002, st.mat("cardw", "#EFEADF", rough=0.7))
    d = sh.decal("cardp", tex("card_lead.png"), 0.09, 0.1286, (0, -0.0014, 0), (math.radians(90), 0, 0),
                 rough=0.7, alpha=False)
    lead = st.mat("lead", "#8F9497", rough=0.45, metal=0.9)
    st.add_proc_bump(lead, "noise", scale=900, strength=0.08)
    strips = []
    for k in range(4):
        s = sh.rbox("strip", (0.0064, 0.0008, 0.05), 0.0002, lead, loc=(-0.0225 + k * 0.015, -0.0019, -0.033))
        strips.append(s)
    root = st.parent_all([c, d] + strips, "leadcard")
    root.location = loc
    return root


def walnut_mount():
    wall = st.mat("wall", "#E3DCCF", rough=0.9)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.03, 0.5), rotation=(math.radians(90), 0, 0))
    w = bpy.context.object
    w.scale = (3, 2, 1)
    w.data.materials.append(wall)
    wal = sh.image_mat("walnut", tex("walnut.png"), rough=0.45, coat=0.25)
    plank = sh.rbox("plank", (0.42, 0.028, 0.1), 0.004, wal, loc=(0, 0.015, 0.36))
    brass = st.mat("brass", "#C8A055", rough=0.25, metal=1.0)
    for x in (-0.16, -0.06, 0.06, 0.16):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.06, location=(x, -0.025, 0.375),
                                            rotation=(math.radians(90), 0, 0), vertices=32)
        bpy.context.object.data.materials.append(brass)
        st.smooth(bpy.context.object)
    for sku, x in (("TS-KLC16-VOLT", -0.11), ("TS-APX14", 0.11)):
        p = mc.paddle(sku)
        p.rotation_euler = (math.radians(90), 0, 0)
        hl = mc.SHAPES[mc.PADDLES[sku]["shape"]][2]
        p.location = (x, -0.035, 0.381 - (hl - 0.35) * IN)
    return plank
