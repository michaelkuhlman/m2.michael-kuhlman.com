"""Bags & covers and apparel/headwear models. Z up, ground z=0, camera looks from -Y."""
import math
import os

import bpy
import bmesh
from mathutils import Vector

import models_core as mc
import shapes as sh
import studio as st

IN = mc.IN
TEX = st.TEX
COL = {"forest": "#1F4A3C", "sand": "#D9CDB4", "charcoal": "#33393A", "optic": "#D9F24F", "clay": "#C9603A",
       "chalk": "#EFEADF", "kitchen": "#173A2E", "ink": "#16201C", "glacier": "#9ED2E4"}


def tex(name):
    return os.path.join(TEX, name)


def fabric(name, colour, rough=0.86, scale=900.0, strength=0.12, sheen=0.35):
    m = st.mat(name, colour, rough=rough, sheen=sheen, spec=0.3)
    return st.add_proc_bump(m, "noise", scale=scale, strength=strength, distance=0.0005)


def webbing(colour="#1A1F1D"):
    m = st.mat("webbing_" + colour, colour, rough=0.7, sheen=0.3)
    return st.add_proc_bump(m, "wave", scale=900, strength=0.2, distance=0.0003, direction="X")


def zipper(points, colour="#15191A"):
    return sh.curve_tube("zip", points, 0.0032, st.mat("zip", colour, rough=0.35))


def front_patch(name, w, h, loc, tilt=0.0):
    return sh.decal("patch", tex(f"patch_{name}.png"), w, h, loc, (math.radians(90 - tilt), 0, 0), rough=0.7)


# ------------------------------------------------------------------ bags
def backpack(colour="forest"):
    c = COL[colour]
    fab = fabric("bp_" + colour, c)
    acc = COL["kitchen"] if colour == "sand" else "#173229"
    body = sh.pillow("bp_body", (0.30, 0.17, 0.46), fab, loc=(0, 0, 0.235))
    base = sh.pillow("bp_base", (0.305, 0.175, 0.07), st.mat("tpu", "#1D2422", rough=0.45), loc=(0, 0, 0.035))
    pocket = sh.pillow("bp_pocket", (0.25, 0.06, 0.22), fab, loc=(0, -0.085, 0.155))
    zipper([(-0.13, -0.079, 0.10), (-0.135, -0.081, 0.36), (-0.06, -0.082, 0.445), (0.06, -0.082, 0.445),
            (0.135, -0.081, 0.36), (0.13, -0.079, 0.10)], acc)
    zipper([(-0.11, -0.118, 0.245), (0.0, -0.121, 0.252), (0.11, -0.118, 0.245)], acc)
    sh.rbox("pull", (0.012, 0.004, 0.03), 0.002, st.mat("pull", COL["optic"], rough=0.4), loc=(0.09, -0.124, 0.232))
    sh.curve_tube("handle", [(-0.04, 0.0, 0.455), (-0.035, 0.0, 0.50), (0.035, 0.0, 0.50), (0.04, 0.0, 0.455)],
                  0.008, webbing())
    for sx in (-1, 1):
        sh.curve_tube("strap", [(sx * 0.08, 0.09, 0.44), (sx * 0.15, 0.13, 0.36), (sx * 0.165, 0.13, 0.16),
                                (sx * 0.15, 0.10, 0.05)], 0.012, fabric("strap", "#1A1F1D", scale=600))
    front_patch("chalk" if colour == "forest" else "forest", 0.085, 0.051, (0, -0.1165, 0.19))
    return [body, pocket]


def duffel():
    c = COL["charcoal"]
    fab = fabric("duffel", c)
    body = sh.pillow("duf_body", (0.58, 0.28, 0.29), fab, loc=(0, 0, 0.145))
    sh.pillow("duf_end", (0.04, 0.17, 0.17), fab, loc=(0.29, 0, 0.13))
    for sx in (-0.12, 0.12):
        sh.curve_tube("h", [(sx, -0.105, 0.24), (sx, -0.06, 0.40), (sx, 0.06, 0.40), (sx, 0.105, 0.24)], 0.011,
                      webbing("#121615"))
        sh.rbox("tab", (0.05, 0.004, 0.06), 0.003, st.mat("leather", "#7C5136", rough=0.55),
                loc=(sx, -0.137, 0.24))
    zipper([(-0.26, 0.0, 0.285), (0.0, 0.0, 0.292), (0.26, 0.0, 0.285)], "#0E1110")
    zipper([(-0.25, -0.139, 0.06), (0.0, -0.142, 0.06), (0.25, -0.139, 0.06)], COL["optic"])
    front_patch("charcoal", 0.11, 0.066, (0.0, -0.1435, 0.15))
    return [body]


def sling():
    fab = fabric("sling", COL["charcoal"], scale=1400, strength=0.18)
    body = sh.pillow("sling", (0.22, 0.075, 0.31), fab, loc=(0, 0, 0.155))
    body.rotation_euler = (0, math.radians(-12), 0)
    sh.curve_tube("strap", [(0.07, 0.0, 0.29), (0.10, 0.0, 0.42), (0.02, 0.01, 0.52), (-0.12, 0.01, 0.46),
                            (-0.17, 0.0, 0.25), (-0.15, 0.0, 0.05)], 0.0, webbing("#141818"), flat=0.038)
    zipper([(-0.06, -0.039, 0.27), (0.04, -0.04, 0.275), (0.10, -0.038, 0.22)], COL["optic"])
    pt = front_patch("charcoal", 0.075, 0.045, (0.01, -0.0405, 0.14))
    pt.rotation_euler = (math.radians(90), math.radians(-12), 0)
    return [body]


def cover(colour="forest", with_grip=True, name="cover"):
    """Neoprene cover over a paddle head (paddle grip visible)."""
    p = mc.paddle("TS-SIG-RAW")
    for ch in p.children:
        if ch.name.endswith("_face") or ch.name.endswith("_edge"):
            ch.hide_render = True
    L, W, HL = p["length"], p["width"], 5.25 * IN
    pts = mc.rounded_rect_pts(-W / 2 - 0.006, HL - 0.3 * IN, W / 2 + 0.006, L + 0.006, 2.1 * IN, 3.0 * IN)
    bm = bmesh.new()
    bm.faces.new([bm.verts.new((x, y, 0)) for x, y in pts])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = st.link(bpy.data.objects.new(name, me))
    sol = ob.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = 0.03
    sol.offset = 0
    bv = ob.modifiers.new("bv", "BEVEL")
    bv.width = 0.012
    bv.segments = 6
    ss = ob.modifiers.new("ss", "SUBSURF")
    ss.levels = ss.render_levels = 1
    neo = st.mat("neo_" + colour, COL[colour], rough=0.62, sheen=0.2, spec=0.35)
    st.add_proc_bump(neo, "noise", scale=1800, strength=0.08, distance=0.0003)
    ob.data.materials.append(neo)
    st.smooth(ob)
    ob.parent = p
    printname = "kitchen" if colour == "optic" else "chalk"
    d = sh.decal("print", tex(f"print_{printname}.png"), 0.16, 0.10, (0, L * 0.62, 0.0162), (0, 0, 0), rough=0.6)
    d.parent = p
    zp = [(x * 1.0, y, 0) for x, y in mc.rounded_rect_pts(-W / 2 - 0.0085, HL + 1.4 * IN, W / 2 + 0.0085, L + 0.0085,
                                                          2.1 * IN, 3.0 * IN)]
    top = [q for q in zp if q[1] > HL + 1.6 * IN]
    z = sh.curve_tube("zipc", top, 0.0028, st.mat("zipc", "#121615", rough=0.35), smooth_pts=False)
    z.parent = p
    return p


def hard_case():
    fab = st.mat("eva", COL["charcoal"], rough=0.6, spec=0.35)
    st.add_proc_bump(fab, "noise", scale=260, strength=0.18, distance=0.0008)
    L, W = 0.47, 0.235
    pts = mc.rounded_rect_pts(-W / 2, 0, W / 2, L, 0.06, 0.06)
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    bm.faces.new(vs)
    me = bpy.data.meshes.new("case")
    bm.to_mesh(me)
    ob = st.link(bpy.data.objects.new("case", me))
    sol = ob.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = 0.055
    sol.offset = 0
    bv = ob.modifiers.new("bv", "BEVEL")
    bv.width = 0.02
    bv.segments = 8
    ob.data.materials.append(fab)
    st.smooth(ob)
    zp = [(x, y, 0) for x, y in mc.rounded_rect_pts(-W / 2 - 0.001, -0.001, W / 2 + 0.001, L + 0.001, 0.06, 0.06)]
    z = sh.curve_tube("zipcase", zp, 0.004, st.mat("zipcase", COL["optic"], rough=0.4), cyclic=True,
                      smooth_pts=False)
    d = sh.decal("patchc", tex("patch_charcoal.png"), 0.12, 0.072, (0, L * 0.6, 0.0285), (0, 0, 0), rough=0.6)
    h = sh.curve_tube("hcase", [(W / 2 + 0.002, 0.15, 0.0), (W / 2 + 0.03, 0.2, 0.0), (W / 2 + 0.03, 0.27, 0.0),
                                (W / 2 + 0.002, 0.32, 0.0)], 0.0, webbing(), flat=0.02)
    root = st.parent_all([ob, z, d, h], "case_root")
    return root


def pouch():
    fab = st.mat("pouch", COL["forest"], rough=0.62, sheen=0.2)
    st.add_proc_bump(fab, "noise", scale=1800, strength=0.08, distance=0.0003)
    body = sh.pillow("pouch", (0.11, 0.08, 0.15), fab, loc=(0, 0, 0.075))
    sh.ring("rim", 0.04, 0.034, 0.012, st.mat("rim", "#121615", rough=0.5), z0=0.142)
    mc.ball("optic", loc=(0, 0, 0.16))
    steel = st.mat("steel", "#C4C8CA", rough=0.22, metal=1.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.0035, major_segments=48, minor_segments=12)
    cb = bpy.context.object
    cb.scale = (0.7, 1.0, 1.6)
    cb.rotation_euler = (math.radians(90), 0, math.radians(10))
    cb.location = (0.066, 0.0, 0.17)
    cb.data.materials.append(steel)
    st.smooth(cb)
    front_patch("chalk", 0.06, 0.036, (0, -0.0405, 0.07))
    return [body]


# ------------------------------------------------------------------ headwear
def _brim(name, inner_r, mat, depth=0.072, tilt=8, spread=128):
    """Curved cap brim in front (-Y)."""
    bm = bmesh.new()
    n = 28
    inner, outer = [], []
    a0, a1 = math.radians(270 - spread / 2), math.radians(270 + spread / 2)
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        x, y = math.cos(a), math.sin(a)
        inner.append((inner_r[0] * x, inner_r[1] * y))
        f = math.sin((k / n) * math.pi)
        outer.append((inner_r[0] * x * 1.02, inner_r[1] * y - depth * f ** 0.6))
    vi = [bm.verts.new((x, y, 0)) for x, y in inner]
    vo = [bm.verts.new((x, y, 0)) for x, y in outer]
    for k in range(n):
        bm.faces.new((vi[k], vi[k + 1], vo[k + 1], vo[k]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = st.link(bpy.data.objects.new(name, me))
    for v in ob.data.vertices:  # curve down at the sides, tilt down at the front
        v.co.z -= 2.2 * v.co.x ** 2 + math.tan(math.radians(tilt)) * max(0.0, -v.co.y - inner_r[1] * 0.5)
    sol = ob.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = 0.004
    ss = ob.modifiers.new("ss", "SUBSURF")
    ss.levels = ss.render_levels = 1
    ob.data.materials.append(mat)
    st.smooth(ob)
    return ob


def cap(colour="forest"):
    c = COL[colour]
    tw = fabric("twill_" + colour, c, scale=1500, strength=0.1, sheen=0.4)
    rx, ry, rz = 0.093, 0.101, 0.085
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=72, ring_count=36)
    cr = bpy.context.object
    bm = bmesh.new()
    bm.from_mesh(cr.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.001], context="VERTS")
    bm.to_mesh(cr.data)
    cr.scale = (rx, ry, rz)
    bpy.ops.object.transform_apply(scale=True)
    cr.modifiers.new("sol", "SOLIDIFY").thickness = 0.002
    cr.data.materials.append(tw)
    st.smooth(cr)
    cr.location.z = 0.012
    seam = st.mat("seam_" + colour, c, rough=0.9)
    for k in range(6):
        phi = math.radians(30 + 60 * k)
        pts = []
        for j in range(10):
            th = math.radians(4 + 86 * j / 9)
            pts.append((rx * 1.004 * math.sin(th) * math.cos(phi), ry * 1.004 * math.sin(th) * math.sin(phi),
                        0.012 + rz * 1.004 * math.cos(th)))
        sh.curve_tube("seam", pts, 0.0009, seam)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0085, location=(0, 0, 0.012 + rz + 0.002))
    bt = bpy.context.object
    bt.scale.z = 0.45
    bt.data.materials.append(tw)
    st.smooth(bt)
    _brim("brim", (rx, ry), tw).location.z = 0.012
    patch = "chalk" if colour in ("forest", "clay") else "forest"
    a = math.radians(32)
    d = sh.decal("cap_patch", tex(f"patch_{patch}.png"), 0.062, 0.037,
                 (0, -ry * math.cos(a) - 0.0015, 0.012 + rz * math.sin(a)), (math.radians(90 - 32), 0, 0), rough=0.7)
    return [cr]


def visor(colour="chalk"):
    c = COL[colour]
    knit = fabric("knit_" + colour, c, scale=1300, strength=0.12, sheen=0.3)
    rx, ry = 0.093, 0.101
    band = sh.ring("band", 1.0, 0.97, 0.052, knit, segments=96, z0=0.0)
    band.scale = (rx, ry, 1.0)
    band.location.z = 0.012
    sw = sh.ring("sweat", 0.97, 0.93, 0.05, fabric("terry", "#F4F0E6", scale=600, strength=0.3), segments=96)
    sw.scale = (rx, ry, 1.0)
    sw.location.z = 0.013
    _brim("vbrim", (rx, ry), knit, depth=0.075, tilt=10).location.z = 0.016
    pr = "kitchen" if colour in ("chalk", "optic") else "chalk"
    sh.decal("vprint", tex(f"print_{pr}.png"), 0.07, 0.044, (0, -ry - 0.0012, 0.04), (math.radians(90), 0, 0))
    return [band]


def bucket_hat():
    c = "#CDBF9F"
    rip = fabric("ripstop", c, rough=0.75, scale=500, strength=0.08, sheen=0.2)
    prof = [(0.0, 0.088), (0.04, 0.088), (0.068, 0.086), (0.078, 0.08), (0.084, 0.05), (0.09, 0.012),
            (0.092, 0.006), (0.12, -0.012), (0.15, -0.03), (0.162, -0.037)]
    h = sh.lathe("bucket", prof, 96, rip)
    h.modifiers.new("sol", "SOLIDIFY").thickness = 0.0025
    h.location.z = 0.04
    m2 = st.mat("stitch", c, rough=0.8)
    for r in (0.11, 0.125, 0.14, 0.153):
        z = 0.04 + (-0.012 - (r - 0.12) * 0.6) if r > 0.12 else 0.04 + 0.006 - (r - 0.092) * 0.64
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.0007, major_segments=128, minor_segments=6,
                                         location=(0, 0, z + 0.0016))
        bpy.context.object.data.materials.append(m2)
    for a in (-60, 60):
        aa = math.radians(a - 90)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.002, location=(0.085 * math.cos(aa), 0.085 * math.sin(aa), 0.04 + 0.06),
                                            rotation=(math.radians(90), 0, aa + math.radians(90)))
        bpy.context.object.data.materials.append(st.mat("eyelet", "#2A2F2D", rough=0.3, metal=0.6))
    return [h]


def beanie():
    c = COL["charcoal"]
    knit = st.mat("beanie", c, rough=0.9, sheen=0.6, spec=0.25)
    st.add_proc_bump(knit, "wave", scale=55, strength=0.6, distance=0.002, mapping="UV", direction="X",
                     profile="SIN")
    prof = [(0.0, 0.205), (0.03, 0.203), (0.06, 0.19), (0.083, 0.16), (0.095, 0.12), (0.098, 0.085),
            (0.099, 0.075), (0.106, 0.072), (0.107, 0.04), (0.106, 0.004), (0.1, 0.0)]
    b = sh.lathe("beanie", prof, 128, knit)
    b.modifiers.new("sol", "SOLIDIFY").thickness = 0.004
    sh.decal("leather", tex("patch_leather.png"), 0.05, 0.033, (0, -0.1075, 0.037), (math.radians(90), 0, 0),
             rough=0.55)
    return [b]


def headband(colour="chalk", loc=(0, 0, 0), rot=(0, 0, 0)):
    m = fabric("hb_" + colour, COL[colour], scale=1200, strength=0.15, sheen=0.4)
    r = sh.ring("hb", 0.088, 0.083, 0.05, m, segments=96, bevel=0.002)
    r.scale = (1.0, 1.12, 1.0)
    r.location = loc
    r.rotation_euler = rot
    return r


def wristband(colour="chalk", loc=(0, 0, 0), rot=(0, 0, 0)):
    m = st.mat("terry_" + colour, COL[colour], rough=0.95, sheen=0.8, spec=0.2)
    st.add_proc_bump(m, "noise", scale=2600, strength=0.55, distance=0.0012)
    r = sh.ring("wb", 0.043, 0.031, 0.078, m, segments=96, bevel=0.006)
    r.location = loc
    r.rotation_euler = rot
    return r
