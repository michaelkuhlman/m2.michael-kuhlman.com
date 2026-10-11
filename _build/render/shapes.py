"""Generic mesh builders with sensible UVs: lathe, rounded box, ring/tube, ribbon, curve tubes, decals."""
import math

import bpy
import bmesh
from mathutils import Vector

import studio as st


def lathe(name, profile, segments=64, material=None, cap_top=False, cap_bottom=False, smooth=True):
    """Revolve a (radius, z) profile around Z. UV: u = angle, v = normalised profile length."""
    bm = bmesh.new()
    rings = []
    for k in range(segments):
        a = 2 * math.pi * k / segments
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    uv = bm.loops.layers.uv.new("UVMap")
    lens = [0.0]
    for i in range(1, len(profile)):
        (r0, z0), (r1, z1) = profile[i - 1], profile[i]
        lens.append(lens[-1] + math.hypot(r1 - r0, z1 - z0))
    total = lens[-1] or 1.0
    for k in range(segments):
        k2 = (k + 1) % segments
        u0, u1 = k / segments, (k + 1) / segments
        for i in range(len(profile) - 1):
            f = bm.faces.new((rings[k][i], rings[k2][i], rings[k2][i + 1], rings[k][i + 1]))
            uvs = [(u0, lens[i] / total), (u1, lens[i] / total), (u1, lens[i + 1] / total), (u0, lens[i + 1] / total)]
            for lp, c in zip(f.loops, uvs):
                lp[uv].uv = c
    if cap_bottom:
        bm.faces.new([rings[k][0] for k in reversed(range(segments))])
    if cap_top:
        bm.faces.new([rings[k][-1] for k in range(segments)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = st.link(bpy.data.objects.new(name, me))
    if smooth:
        st.smooth(ob, 35)
    if material:
        ob.data.materials.append(material)
    return ob


def rbox(name, size, radius, material=None, segments=6, loc=(0, 0, 0), subsurf=0):
    """Rounded box with bevel modifier; size = full (x, y, z)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True, location=False)
    if radius > 0:
        bv = ob.modifiers.new("bevel", "BEVEL")
        bv.width = min(radius, min(size) / 2 - 1e-5)
        bv.segments = segments
        bv.limit_method = "NONE"
    if subsurf:
        ss = ob.modifiers.new("ss", "SUBSURF")
        ss.levels = ss.render_levels = subsurf
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=max(size))
    bpy.ops.object.mode_set(mode="OBJECT")
    st.smooth(ob, 30)
    if material:
        ob.data.materials.append(material)
    return ob


def pillow(name, size, material=None, levels=3, crease=0.0, loc=(0, 0, 0)):
    """Soft, stuffed shape: cube + subdivision (bags, towels)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True, location=False)
    bv = ob.modifiers.new("bevel", "BEVEL")
    bv.width = min(size) * 0.18
    bv.segments = 2
    ss = ob.modifiers.new("ss", "SUBSURF")
    ss.levels = ss.render_levels = levels
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=max(size))
    bpy.ops.object.mode_set(mode="OBJECT")
    st.smooth(ob)
    if material:
        ob.data.materials.append(material)
    return ob


def ring(name, r_out, r_in, height, material=None, segments=64, bevel=0.0, z0=0.0):
    """Hollow cylinder (tape roll, wristband, cup)."""
    b = bevel
    prof = [(r_in + b, z0), (r_out - b, z0)]
    if b:
        prof = [(r_in + b, z0), (r_out - b, z0)]
        arc = [(r_out - b + b * math.sin(t * math.pi / 8), z0 + b - b * math.cos(t * math.pi / 8)) for t in range(1, 5)]
        prof += arc
        prof += [(r_out, z0 + height - b)]
        prof += [(r_out - b + b * math.cos(t * math.pi / 8), z0 + height - b + b * math.sin(t * math.pi / 8))
                 for t in range(1, 5)]
        prof += [(r_in + b, z0 + height)]
        prof += [(r_in + b - b * math.sin(t * math.pi / 8), z0 + height - b + b * math.cos(t * math.pi / 8))
                 for t in range(1, 5)]
        prof += [(r_in, z0 + b)]
        prof += [(r_in + b - b * math.cos(t * math.pi / 8), z0 + b - b * math.sin(t * math.pi / 8))
                 for t in range(1, 5)]
    else:
        prof = [(r_in, z0), (r_out, z0), (r_out, z0 + height), (r_in, z0 + height), (r_in, z0)]
    return lathe(name, prof, segments, material)


def curve_tube(name, points, radius, material=None, cyclic=False, resolution=12, smooth_pts=True, flat=None):
    """Tube (or flat ribbon if flat=(width)) along a list of 3D points (NURBS-smoothed)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("NURBS" if smooth_pts else "POLY")
    sp.points.add(len(points) - 1)
    for k, p in enumerate(points):
        sp.points[k].co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = cyclic
    sp.use_endpoint_u = not cyclic
    sp.order_u = 4 if len(points) >= 4 else len(points)
    cu.resolution_u = resolution
    if flat:
        cu.extrude = flat / 2
        cu.bevel_depth = 0.0
        cu.offset = 0
    else:
        cu.bevel_depth = radius
        cu.bevel_resolution = 4
    cu.use_fill_caps = True
    ob = st.link(bpy.data.objects.new(name, cu))
    if material:
        ob.data.materials.append(material)
    return ob


def decal(name, image_path, width, height, loc, rot, rough=0.5, alpha=True, emission=0.0):
    """Image plane (labels, patches, prints) with alpha from the PNG."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = (width, height, 1)
    m = bpy.data.materials.new(name + "_m")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    img = bpy.data.images.load(image_path, check_existing=True)
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    ob.data.materials.append(m)
    return ob


def image_mat(name, image_path, rough=0.5, coat=0.0, bump=None, sheen=0.0, metal=0.0):
    """Principled material whose base colour comes from an image (UV mapped)."""
    m = st.mat(name, "#FFFFFF", rough=rough, coat=coat, sheen=sheen, metal=metal)
    st.add_image(m, image_path)
    if bump:
        st.add_proc_bump(m, *bump)
    return m


def bend(ob, axis="Z", angle_deg=30, origin=None):
    """Simple deform bend."""
    md = ob.modifiers.new("bend", "SIMPLE_DEFORM")
    md.deform_method = "BEND"
    md.deform_axis = axis
    md.angle = math.radians(angle_deg)
    return md


def apply_all(ob):
    bpy.context.view_layer.objects.active = ob
    for md in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)
    return ob


def bbox_world(objs):
    pts = []
    for o in objs:
        if o.type in ("MESH", "CURVE"):
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi
