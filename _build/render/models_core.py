"""Paddle and ball models.

Paddle: built lying in the XY plane (face normal +Z), butt cap at the origin, head toward +Y.
Ball: centred at the origin, radius 37 mm, holes cut with a boolean against a collection of cylinders.
"""
import math
import os

import bpy
import bmesh
from mathutils import Vector

import studio as st
from specs import PADDLES, SHAPES, BALL_COLOURS

IN = 0.0254  # metres per inch


def rounded_rect_pts(x0, y0, x1, y1, rt, rb, n=14):
    """Counter-clockwise outline with top radius rt and bottom radius rb."""
    pts = []
    corners = [((x1 - rb, y0 + rb), rb, -90), ((x1 - rt, y1 - rt), rt, 0),
               ((x0 + rt, y1 - rt), rt, 90), ((x0 + rb, y0 + rb), rb, 180)]
    for (cx, cy), r, a0 in corners:
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def paddle(sku, name=None):
    spec = PADDLES[sku]
    L, W, HL, rt, rb = SHAPES[spec["shape"]]
    L, W, HL, rt, rb = L * IN, W * IN, HL * IN, rt * IN, rb * IN
    t = spec["thick"] / 1000.0 + 0.0016  # core + skins
    head_y0 = HL - 0.35 * IN
    pts = rounded_rect_pts(-W / 2, head_y0, W / 2, L, rt, rb)
    parts = []

    # --- face slab ---
    bm = bmesh.new()
    bottom = [bm.verts.new((x, y, 0)) for x, y in pts]
    top = [bm.verts.new((x, y, t)) for x, y in pts]
    ftop = bm.faces.new(top)
    fbot = bm.faces.new(list(reversed(bottom)))
    n = len(pts)
    for k in range(n):
        bm.faces.new((bottom[k], bottom[(k + 1) % n], top[(k + 1) % n], top[k]))
    uv = bm.loops.layers.uv.new("UVMap")
    for f in (ftop, fbot):
        for lp in f.loops:
            x, y = lp.vert.co.x, lp.vert.co.y
            u = (x + W / 2) / W
            if f is fbot:
                u = 1 - u
            lp[uv].uv = (u, y / L)
    me = bpy.data.meshes.new(f"{sku}_face")
    bm.to_mesh(me)
    face = st.link(bpy.data.objects.new(f"{sku}_face", me))
    face.location.z = -t / 2
    fm = st.mat(f"{sku}_facemat", spec["base_col"], rough=0.42, coat=0.5, coat_rough=0.12)
    base = spec["base"]
    if base == "raw":
        fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.62
        fm.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.0
    elif base == "wood":
        fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
        fm.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.2
    elif base == "solid":
        fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.34
    st.add_image(fm, os.path.join(st.TEX, f"{sku}_face.png"), os.path.join(st.TEX, f"{sku}_bump.png"),
                 bump_strength=0.25 if base in ("raw", "carbon") else 0.08)
    face.data.materials.append(fm)
    parts.append(face)

    # --- edge guard: tube along the outline ---
    if spec.get("edge"):
        cu = bpy.data.curves.new(f"{sku}_edge", "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for k, (x, y) in enumerate(pts):
            sp.points[k].co = (x, y, 0, 1)
        sp.use_cyclic_u = True
        cu.bevel_depth = t / 2 + 0.0011
        cu.bevel_resolution = 4
        edge = st.link(bpy.data.objects.new(f"{sku}_edge", cu))
        edge.data.materials.append(st.mat(f"{sku}_edgemat", spec["edge"], rough=0.38, coat=0.3))
        parts.append(edge)
    else:  # wood: rounded profile sides only, darker stain
        face.data.materials.append(st.mat(f"{sku}_side", "#8E6A44", rough=0.6))
        for p in face.data.polygons:
            if abs(p.normal.z) < 0.5:
                p.material_index = 1

    # --- handle + grip ---
    gw, gt = 1.36 * IN, 0.92 * IN
    grip_top = HL + 0.25 * IN
    bpy.ops.mesh.primitive_cube_add(size=1)
    grip = bpy.context.object
    grip.name = f"{sku}_grip"
    grip.scale = (gw, grip_top - 0.15 * IN, gt)
    grip.location = (0, (grip_top + 0.15 * IN) / 2, 0)
    bpy.ops.object.transform_apply(scale=True, location=False)
    bv = grip.modifiers.new("bevel", "BEVEL")
    bv.width = gt * 0.47
    bv.segments = 6
    gm = st.mat(f"{sku}_gripmat", spec["grip"], rough=0.78, sheen=0.25)
    st.add_proc_bump(gm, "wave", scale=42.0, strength=0.9, distance=0.0012, rot=(0, math.radians(12), 0))
    grip.data.materials.append(gm)
    st.smooth(grip)
    parts.append(grip)

    # finishing tape collar at the top of the grip
    bpy.ops.mesh.primitive_cube_add(size=1)
    collar = bpy.context.object
    collar.scale = (gw + 0.0018, 0.42 * IN, gt + 0.0018)
    collar.location = (0, grip_top - 0.12 * IN, 0)
    bpy.ops.object.transform_apply(scale=True, location=False)
    b2 = collar.modifiers.new("bevel", "BEVEL")
    b2.width = (gt + 0.0016) * 0.42
    b2.segments = 5
    collar.data.materials.append(st.mat(f"{sku}_collar", spec["accent"], rough=0.45))
    st.smooth(collar)
    parts.append(collar)

    # butt cap
    bpy.ops.mesh.primitive_cube_add(size=1)
    cap = bpy.context.object
    cap.scale = (gw + 0.003, 0.30 * IN, gt + 0.003)
    cap.location = (0, 0.04 * IN, 0)
    bpy.ops.object.transform_apply(scale=True, location=False)
    b3 = cap.modifiers.new("bevel", "BEVEL")
    b3.width = (gt + 0.003) * 0.48
    b3.segments = 6
    cap.data.materials.append(st.mat(f"{sku}_cap", spec["edge"] or "#5A3E26", rough=0.4, coat=0.4))
    st.smooth(cap)
    parts.append(cap)

    # optional weight bars (Coach's Weighted Trainer)
    if spec.get("weights"):
        steel = st.mat("steel", "#B9BDC0", rough=0.25, metal=1.0)
        for sx in (-1, 1):
            for side in (-1, 1):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=3.4 * IN, vertices=32)
                bar = bpy.context.object
                bar.rotation_euler = (math.radians(90), 0, 0)
                bar.location = (sx * (W / 2 - 0.8 * IN), head_y0 + 3.1 * IN, side * (t / 2 + 0.0035))
                bar.data.materials.append(steel)
                st.smooth(bar)
                parts.append(bar)

    root = st.parent_all(parts, name or sku)
    root["length"] = L
    root["width"] = W
    root["thick"] = t
    return root


# ---------------------------------------------------------------- balls
_ball_mesh_cache = {}


def fib_points(n):
    pts = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - (i + 0.5) / n * 2
        r = math.sqrt(1 - y * y)
        pts.append(Vector((math.cos(ga * i) * r, math.sin(ga * i) * r, y)))
    return pts


def ball_mesh(holes=40, hole_d=0.0079, radius=0.037, shell=0.0028):
    key = (holes, hole_d)
    if key in _ball_mesh_cache:
        try:
            _ball_mesh_cache[key].name  # raises ReferenceError after a scene reset
            return _ball_mesh_cache[key]
        except ReferenceError:
            del _ball_mesh_cache[key]
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, radius=radius)
    b = bpy.context.object
    sol = b.modifiers.new("shell", "SOLIDIFY")
    sol.thickness = shell
    sol.offset = -1
    bpy.ops.object.modifier_apply(modifier="shell")
    coll = bpy.data.collections.new("holes")
    bpy.context.scene.collection.children.link(coll)
    for p in fib_points(holes):
        bpy.ops.mesh.primitive_cylinder_add(radius=hole_d / 2, depth=0.03, vertices=20)
        c = bpy.context.object
        c.location = p * radius
        c.rotation_euler = p.to_track_quat("Z", "Y").to_euler()
        for cc in c.users_collection:
            cc.objects.unlink(c)
        coll.objects.link(c)
    bo = b.modifiers.new("holes", "BOOLEAN")
    bo.operation = "DIFFERENCE"
    bo.operand_type = "COLLECTION"
    bo.collection = coll
    bo.solver = "EXACT"
    bpy.context.view_layer.objects.active = b
    bpy.ops.object.modifier_apply(modifier="holes")
    for c in list(coll.objects):
        bpy.data.objects.remove(c)
    bpy.data.collections.remove(coll)
    me = b.data
    bpy.data.objects.remove(b)
    for p in me.polygons:
        p.use_smooth = True
    _ball_mesh_cache[key] = me
    return me


def ball(colour="optic", kind="outdoor", loc=(0, 0, 0.037), rot=(0, 0, 0), glow=False):
    holes, d = (40, 0.0079) if kind == "outdoor" else (26, 0.0112)
    me = ball_mesh(holes, d)
    ob = st.link(bpy.data.objects.new("ball", me))
    ob.location = loc
    ob.rotation_euler = rot
    key = f"ballmat_{colour}"
    m = bpy.data.materials.get(key)
    if not m:
        m = st.mat(key, BALL_COLOURS.get(colour, colour), rough=0.36 if kind == "outdoor" else 0.5,
                   sss=0.12, spec=0.45)
        if glow:
            b = m.node_tree.nodes["Principled BSDF"]
            b.inputs["Emission Color"].default_value = st.col("#C9F57A")
            b.inputs["Emission Strength"].default_value = 0.25
    if not me.materials:
        me.materials.append(m)
    ob.material_slots[0].link = "OBJECT"
    ob.material_slots[0].material = m
    return ob
