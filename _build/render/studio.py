"""Studio helpers for Blender (Cycles): scene reset, cyc backdrop, softbox lights, camera, materials.

Art direction (all product shots share it):
- warm sand cyc backdrop, soft key from upper left, cool-neutral fill right, gentle rim from behind
- AgX view transform, 85 mm lens, slight depth of field on hero angles
"""
import math
import os

import bpy
import bmesh
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(ROOT, "..", "textures", "out")

BACKDROP = "#B8B2A6"


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def col(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), a)


def reset(width=800, height=1000, samples=32, threads=3):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = samples
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.05
    s.cycles.use_denoising = True
    s.cycles.denoiser = "OPENIMAGEDENOISE"
    s.cycles.max_bounces = 6
    s.cycles.diffuse_bounces = 3
    s.cycles.glossy_bounces = 3
    s.cycles.transmission_bounces = 6
    s.cycles.transparent_max_bounces = 6
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.blur_glossy = 1.0
    s.render.threads_mode = "FIXED"
    s.render.threads = threads
    s.render.resolution_x = width
    s.render.resolution_y = height
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGB"
    s.render.film_transparent = False
    s.view_settings.view_transform = "Khronos PBR Neutral"
    s.view_settings.look = "None"
    s.view_settings.exposure = -0.6
    s.unit_settings.system = "METRIC"
    world(0.35)
    return s


def world(strength=0.35, colour="#F2EEE6"):
    w = bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = col(colour)
    bg.inputs[1].default_value = strength


def backdrop(colour=BACKDROP, width=8.0, depth=6.0, height=4.0, radius=1.2, wall_y=1.2, rough=0.85):
    """Seamless cyc: floor + quarter-round cove + back wall."""
    bm = bmesh.new()
    prof = []
    y0 = -depth
    prof.append((y0, 0.0))
    steps = 24
    for k in range(steps + 1):
        a = k / steps * math.pi / 2
        prof.append((wall_y - radius + math.sin(a) * radius, radius - math.cos(a) * radius))
    prof.append((wall_y, height))
    rows = []
    for x in (-width / 2, width / 2):
        rows.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for k in range(len(prof) - 1):
        bm.faces.new((rows[0][k], rows[1][k], rows[1][k + 1], rows[0][k + 1]))
    me = bpy.data.meshes.new("Backdrop")
    bm.to_mesh(me)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("Backdrop", me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat("Backdrop", colour, rough=rough, spec=0.2))
    return ob


def retint_backdrop(colour):
    """Change the cyc colour after it was created (e.g. darker for light products)."""
    ob = bpy.data.objects.get("Backdrop")
    if ob:
        ob.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = col(colour)


def big_backdrop(colour=BACKDROP):
    """Replace the cyc with a room-sized one (nets, ladders)."""
    ob = bpy.data.objects.get("Backdrop")
    if ob:
        bpy.data.objects.remove(ob)
    return backdrop(colour, width=80.0, depth=40.0, height=20.0, radius=6.0, wall_y=30.0)


def area_light(name, loc, target, energy, size, colour="#FFFFFF", shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.shape = shape
    ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.color = col(colour)[:3]
    ob = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    return ob


def soft_lights(target=(0, 0, 0.15), scale=1.0, key=1.0):
    """Three-point softbox setup scaled to the product size (scale ~ object size in metres / 0.4)."""
    t = Vector(target)
    s = scale
    area_light("Key", t + Vector((-1.1, -1.0, 1.05)) * s, t, 130 * s * s * key, 1.1 * s, "#FFF8F0")
    area_light("Fill", t + Vector((1.3, -0.7, 0.45)) * s, t, 38 * s * s, 1.4 * s, "#EEF2F6")
    area_light("Rim", t + Vector((0.5, 1.2, 1.25)) * s, t, 70 * s * s, 0.7 * s, "#FFFFFF")
    area_light("Top", t + Vector((0.0, -0.2, 1.8)) * s, t, 30 * s * s, 1.6 * s, "#FFFAF2")


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(target, azimuth_deg=-20, elev_deg=12, dist=1.6, lens=85, dof=None, shift_y=0.0):
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cd.sensor_width = 36
    cd.shift_y = shift_y
    ob = bpy.data.objects.new("Cam", cd)
    bpy.context.collection.objects.link(ob)
    az, el = math.radians(azimuth_deg), math.radians(elev_deg)
    t = Vector(target)
    ob.location = t + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
    look_at(ob, t)
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = (ob.location - t).length
        cd.dof.aperture_fstop = dof
    bpy.context.scene.camera = ob
    return ob


def fit_distance(objs, lens=85, margin=1.18, aspect=0.8):
    """Distance so the bounding sphere of objs fits the frame (portrait aspect = w/h)."""
    pts = []
    for o in objs:
        pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    centre = sum(pts, Vector()) / len(pts)
    r = max((p - centre).length for p in pts)
    fov_w = 2 * math.atan(36 / 2 / lens)
    fov_h = 2 * math.atan(36 / aspect / 2 / lens) if aspect < 1 else fov_w / aspect
    fov = min(fov_w, fov_h) if aspect < 1 else fov_h
    return centre, r * margin / math.sin(fov / 2)


def mat(name, colour, rough=0.5, metal=0.0, coat=0.0, coat_rough=0.08, spec=0.5, sss=0.0, alpha=1.0,
        trans=0.0, sheen=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col(colour)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["IOR"].default_value = ior
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.01, 0.01, 0.01)
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    return m


def add_image(m, path, bump_path=None, bump_strength=0.15, non_color=False):
    """Plug an image texture into Base Color (+ optional bump map) of material m."""
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    img = bpy.data.images.load(path, check_existing=True)
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    tx.interpolation = "Cubic"
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if bump_path:
        bi = bpy.data.images.load(bump_path, check_existing=True)
        bi.colorspace_settings.name = "Non-Color"
        bt = nt.nodes.new("ShaderNodeTexImage")
        bt.image = bi
        bn = nt.nodes.new("ShaderNodeBump")
        bn.inputs["Strength"].default_value = bump_strength
        bn.inputs["Distance"].default_value = 0.0004
        nt.links.new(bt.outputs["Color"], bn.inputs["Height"])
        nt.links.new(bn.outputs["Normal"], b.inputs["Normal"])
    return tx


def add_proc_bump(m, kind="wave", scale=60.0, strength=0.3, distance=0.001, rot=(0, 0, 0), mapping="Object",
                  direction="Z", wave_type="BANDS", profile="SAW"):
    """Procedural bump (wave = wrapped grip, noise = fabric/terry, voronoi = knit-ish)."""
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = rot
    nt.links.new(tc.outputs[mapping], mp.inputs["Vector"])
    if kind == "wave":
        t = nt.nodes.new("ShaderNodeTexWave")
        t.wave_type = wave_type
        if wave_type == "BANDS":
            t.bands_direction = direction
        else:
            t.rings_direction = "SPHERICAL" if direction == "S" else direction
        t.wave_profile = profile
        t.inputs["Scale"].default_value = scale
        t.inputs["Distortion"].default_value = 0.5
        out = t.outputs["Fac"]
    elif kind == "voronoi":
        t = nt.nodes.new("ShaderNodeTexVoronoi")
        t.inputs["Scale"].default_value = scale
        out = t.outputs["Distance"]
    else:
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = 8.0
        out = t.outputs["Fac"]
    nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
    bn = nt.nodes.new("ShaderNodeBump")
    bn.inputs["Strength"].default_value = strength
    bn.inputs["Distance"].default_value = distance
    nt.links.new(out, bn.inputs["Height"])
    nt.links.new(bn.outputs["Normal"], b.inputs["Normal"])
    return m


def link(ob):
    bpy.context.collection.objects.link(ob)
    return ob


def smooth(ob, angle=40):
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        ob.data.set_sharp_from_angle(angle=math.radians(angle))
    except AttributeError:
        pass
    return ob


def parent_all(objs, name="Group"):
    e = bpy.data.objects.new(name, None)
    link(e)
    for o in objs:
        o.parent = e
    return e


def render(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
