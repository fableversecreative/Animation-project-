"""Blender (Cycles CPU) background plates for the 0-6 s comparison.
python3 plates.py OUTDIR SCALE SAMPLES name[,name...]
Plates cover design coords x -108..1188, y -192..2112 (1.2x overscan of 1080x1920).
Writes OUT/<name>.png (tone-mapped) and OUT/<name>.json (projected anchor points in design coords)."""
import bpy, bmesh, math, sys, os, json, random, time
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[1]; SCALE = float(sys.argv[2]); SAMPLES = int(sys.argv[3]); NAMES = sys.argv[4].split(',')
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v3zip', 'fableverse_engine', 'v2', 'blender', 'textures')
os.makedirs(OUT, exist_ok=True)
PW, PH = int(1296 * SCALE), int(2304 * SCALE)
R = random.Random(7)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 4
    sc.render.resolution_x = PW; sc.render.resolution_y = PH; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
    sc.render.film_transparent = False
    return sc

def mat(name, col, rough=0.8, metal=0.0, emit=None, estr=0.0, trans=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit:
        for nm in ('Emission Color', 'Emission'):
            if nm in b.inputs: b.inputs[nm].default_value = (*emit, 1); break
        b.inputs['Emission Strength'].default_value = estr
    if trans:
        for nm in ('Transmission Weight', 'Transmission'):
            if nm in b.inputs: b.inputs[nm].default_value = trans; break
    return m

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

def link(o): bpy.context.scene.collection.objects.link(o); return o

def mesh_obj(name, verts, faces, m=None):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); link(o)
    if m: o.data.materials.append(m)
    return o

def prim(kind, m=None, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(**kw)
    o = bpy.context.object
    if m: o.data.materials.append(m)
    return o

def smooth(o):
    for p in o.data.polygons: p.use_smooth = True

def camera(loc, look, lens, fstop=None, focus=None):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; cd.clip_start = 0.02; cd.clip_end = 3000
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop; cd.dof.focus_distance = focus
    co = bpy.data.objects.new('cam', cd); link(co)
    co.location = loc
    d = Vector(look) - Vector(loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    return co

def sun_light(elev, azim, energy, col):
    d = Vector((math.sin(azim) * math.cos(elev), math.cos(azim) * math.cos(elev), math.sin(elev)))
    l = bpy.data.lights.new('sun', 'SUN'); l.energy = energy; l.color = col; l.angle = math.radians(1.5)
    o = bpy.data.objects.new('sun', l); link(o)
    o.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    return d

def sky_world(elev, azim, strength=1.0):
    w = bpy.data.worlds.new('w'); bpy.context.scene.world = w
    try: w.use_nodes = True
    except Exception: pass
    nt = w.node_tree; nt.nodes.clear()
    sk = nt.nodes.new('ShaderNodeTexSky'); bg = nt.nodes.new('ShaderNodeBackground'); out = nt.nodes.new('ShaderNodeOutputWorld')
    try: sk.sky_type = 'MULTIPLE_SCATTERING'
    except Exception: sk.sky_type = 'HOSEK_WILKIE'
    try:
        sk.sun_elevation = elev; sk.sun_rotation = -azim; sk.sun_disc = True; sk.altitude = 200
        sk.air_density = 1.2; sk.aerosol_density = 2.5
    except Exception as e: print('sky opts', e)
    bg.inputs['Strength'].default_value = strength
    nt.links.new(sk.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])

def img_mat(name, path, rough=0.7, scale=(1, 1), bump=0.15):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale[0], scale[1], 1)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tx.inputs['Vector'])
    nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    if bump:
        bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = bump
        nt.links.new(tx.outputs['Color'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    return m

def noise_mat(name, cols, scale=6.0, rough=0.9, bump=0.3, detail=6):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = detail
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].color = (*cols[0], 1); el[1].color = (*cols[-1], 1)
    for i, c in enumerate(cols[1:-1]):
        e = el.new((i + 1) / (len(cols) - 1)); e.color = (*c, 1)
    nt.links.new(nz.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    if bump:
        bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = bump
        nt.links.new(nz.outputs['Fac'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    return m

# ---------------- FIELD ----------------
def grass_blade_mat():
    m = bpy.data.materials.new('blade'); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.55
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].color = (*srgb('2c4a1a'), 1); el[1].color = (*srgb('b8c860'), 1); e = el.new(0.55); e.color = (*srgb('5f8a2e'), 1)
    oi = nt.nodes.new('ShaderNodeObjectInfo'); hue = nt.nodes.new('ShaderNodeHueSaturation')
    mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = 3.3
    nt.links.new(tc.outputs['Object'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mth.inputs[0]); nt.links.new(mth.outputs[0], cr.inputs['Fac'])
    nt.links.new(cr.outputs['Color'], hue.inputs['Color'])
    m2 = nt.nodes.new('ShaderNodeMapRange'); m2.inputs['To Min'].default_value = 0.47; m2.inputs['To Max'].default_value = 0.53
    nt.links.new(oi.outputs['Random'], m2.inputs['Value']); nt.links.new(m2.outputs['Result'], hue.inputs['Hue'])
    nt.links.new(hue.outputs['Color'], b.inputs['Base Color'])
    for nm in ('Subsurface Weight',):
        if nm in b.inputs: b.inputs[nm].default_value = 0.25
    return m

def blade_obj(h=0.32, w=0.014):
    v = [(-w, 0, 0), (w, 0, 0), (-w * 0.75, 0.01, h * 0.45), (w * 0.75, 0.01, h * 0.45), (-w * 0.35, 0.04, h * 0.8), (w * 0.35, 0.04, h * 0.8), (0, 0.08, h)]
    f = [(0, 1, 3, 2), (2, 3, 5, 4), (4, 5, 6)]
    o = mesh_obj('blade', v, f, grass_blade_mat()); o.location = (0, 0, -50); return o

def scatter(emitter, inst, count, size_rand=0.5, seed=1):
    mod = emitter.modifiers.new('ps', 'PARTICLE_SYSTEM'); ps = emitter.particle_systems[-1]; ps.seed = seed
    s = ps.settings; s.type = 'HAIR'; s.count = count; s.hair_length = 1.0
    s.use_advanced_hair = True; s.render_type = 'OBJECT'; s.instance_object = inst
    s.particle_size = 1.0; s.size_random = size_rand
    s.use_rotations = True; s.rotation_mode = 'NOR'; s.phase_factor_random = 2.0; s.rotation_factor_random = 0.12
    s.emit_from = 'FACE'; s.distribution = 'RAND'; s.use_emit_random = True
    try: s.use_rotation_instance = True
    except Exception: pass
    emitter.show_instancer_for_render = True
    return s

def tree_pine(x, y, s):
    mt = TREE_M[R.randrange(3)]
    tr = prim('cylinder', BARK, radius=0.18 * s, depth=2.5 * s, location=(x, y, 1.25 * s), vertices=8)
    for k in range(3):
        c = prim('cone', mt, radius1=(2.3 - k * 0.6) * s, depth=(3.6 - k * 0.6) * s, location=(x, y, (2.4 + k * 1.6) * s), vertices=10)

def tree_round(x, y, s):
    mt = LEAF_M[R.randrange(3)]
    prim('cylinder', BARK, radius=0.22 * s, depth=3.0 * s, location=(x, y, 1.5 * s), vertices=8)
    for k in range(4):
        o = prim('ico_sphere', mt, radius=R.uniform(1.6, 2.3) * s, location=(x + R.uniform(-1.2, 1.2) * s, y + R.uniform(-1, 1) * s, (4.0 + R.uniform(-0.6, 1.2)) * s), subdivisions=2)
        smooth(o)

def build_field(sun_elev, sun_az):
    global TREE_M, LEAF_M, BARK
    sky_world(sun_elev, sun_az, 1.0)
    sun_light(sun_elev, sun_az, 4.5, (1.0, 0.78, 0.55))
    ground = prim('plane', noise_mat('ground', [srgb('3c5a22'), srgb('6a8a34'), srgb('a6a85a')], 3.0, 0.95, 0.4), size=800, location=(0, 300, 0))
    # near grass carpet (two densities)
    blade = blade_obj()
    flowerW = prim('ico_sphere', mat('fw', srgb('fbf7ee'), 0.6), radius=0.018, location=(0, 0, -60), subdivisions=1)
    flowerY = prim('ico_sphere', mat('fy', srgb('f2c83a'), 0.6), radius=0.016, location=(0, 0, -60), subdivisions=1)
    e1 = prim('plane', mat('e', srgb('3c5a22')), size=1, location=(0, 12, 0.001)); e1.scale = (40, 36, 1)
    bpy.ops.object.transform_apply(scale=True)
    scatter(e1, blade, 300000, 0.55, 3)
    e2 = prim('plane', mat('e2', srgb('3c5a22')), size=1, location=(0, -2.0, 0.002)); e2.scale = (7, 9, 1)
    bpy.ops.object.transform_apply(scale=True)
    scatter(e2, blade, 160000, 0.5, 5)
    e3 = prim('plane', mat('e3', srgb('3c5a22')), size=1, location=(0, 10, 0.003)); e3.scale = (30, 26, 1)
    bpy.ops.object.transform_apply(scale=True)
    s = scatter(e3, flowerW, 2600, 0.4, 7); s3 = scatter(e3, flowerY, 1800, 0.4, 9)
    # forest edge
    TREE_M = [mat('p%d' % i, srgb(c), 0.9) for i, c in enumerate(('2b4a2a', '35583a', '2f5232'))]
    LEAF_M = [mat('l%d' % i, srgb(c), 0.9) for i, c in enumerate(('4f7a36', '5f8a3e', '6a9440'))]
    BARK = mat('bark', srgb('4a3626'), 0.9)
    for i in range(110):
        x = R.uniform(-80, 80); y = R.uniform(55, 95); s_ = R.uniform(0.9, 1.6)
        (tree_pine if R.random() < 0.6 else tree_round)(x, y, s_)
    # distant hills (aerial perspective colours)
    for k, (yy, h, col) in enumerate(((180, 26, '7f9a86'), (320, 55, 'a3b4bc'))):
        hp = prim('plane', mat('h%d' % k, srgb(col), 1.0), size=1, location=(0, yy, -2)); hp.scale = (900, 140, 1)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.modifier_add(type='SUBSURF'); hp.modifiers[-1].levels = 0; hp.modifiers[-1].render_levels = 0
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=60); bpy.ops.object.mode_set(mode='OBJECT')
        tx = bpy.data.textures.new('ht%d' % k, 'CLOUDS'); tx.noise_scale = 60 + k * 30
        dm = hp.modifiers.new('d', 'DISPLACE'); dm.texture = tx; dm.strength = h; dm.mid_level = 0.2
        smooth(hp)
    # atmosphere: warm haze cards between depth layers
    for yy, a in ((45, 0.18), (105, 0.42), (240, 0.5)):
        hm = bpy.data.materials.new('haze%d' % yy); hm.use_nodes = True; nt = hm.node_tree; nt.nodes.clear()
        tr = nt.nodes.new('ShaderNodeBsdfTransparent'); em = nt.nodes.new('ShaderNodeEmission'); mx = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputMaterial')
        em.inputs['Color'].default_value = (1.0, 0.72, 0.45, 1); em.inputs['Strength'].default_value = 2.2
        mx.inputs['Fac'].default_value = a
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
        hp = prim('plane', hm, size=1, location=(0, yy, 12)); hp.scale = (1200, 1, 30); hp.rotation_euler = (math.pi / 2, 0, 0)
    # far camp: tents + tricolour flags (left, mid distance)
    canvas = mat('canvas', srgb('efe6d4'), 0.85); pole = mat('pole', srgb('4a3626'), 0.8)
    fb, fw, fr = mat('fb', srgb('2a4fa8'), 0.7), mat('fw2', srgb('f6f1e6'), 0.7), mat('fr', srgb('d23a34'), 0.7)
    for i in range(9):
        x = -26 + i * 3.2 + R.uniform(-0.6, 0.6); y = 34 + (i % 3) * 2.5
        prim('cone', canvas, radius1=1.4, depth=2.4, location=(x, y, 1.2), vertices=12)
        if i % 3 == 0:
            prim('cylinder', pole, radius=0.03, depth=4.2, location=(x, y, 2.1), vertices=6)
            for k, mm in enumerate((fb, fw, fr)):
                p = prim('plane', mm, size=1, location=(x + 0.25 + k * 0.5, y, 3.75)); p.scale = (0.25, 1, 0.42); p.rotation_euler = (math.pi / 2, 0, 0)
    # a few rocks
    rock = mat('rock', srgb('8a8278'), 0.85)
    for i in range(14):
        o = prim('ico_sphere', rock, radius=R.uniform(0.12, 0.45), location=(R.uniform(-10, 10), R.uniform(3, 30), 0), subdivisions=2)
        o.scale = (1.4, 1.0, 0.55); smooth(o)

# ---------------- MAP TABLE ----------------
def build_map():
    sc = bpy.context.scene
    w = bpy.data.worlds.new('w'); sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.016, 0.012, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    tab = prim('plane', img_mat('wood', os.path.join(TEX, 'wood_floor.png'), 0.45, (1.2, 1.2), 0.25), size=2.2, location=(0, 0, 0))
    par = prim('plane', img_mat('parch', os.path.join(TEX, 'parchment.png'), 0.85, (1, 1), 0.08), size=1, location=(0, 0.02, 0.004))
    par.scale = (0.56, 0.78, 1); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=40); bpy.ops.object.mode_set(mode='OBJECT')
    for v in par.data.vertices:                                     # gently curled edges
        ex = max(0, abs(v.co.x) - 0.22) / 0.06; ey = max(0, abs(v.co.y) - 0.34) / 0.05
        v.co.z += 0.006 * ex ** 2 + 0.008 * ey ** 2 + 0.0015 * math.sin(v.co.x * 23 + v.co.y * 17)
    smooth(par)
    brass = mat('brass', srgb('c99a3a'), 0.28, 1.0); glass = mat('glass', (0.9, 0.95, 1.0), 0.02, 0.0, trans=1.0)
    face = mat('cface', srgb('f1e6c8'), 0.6)
    cx, cy = 0.27, -0.32                                            # brass compass (bottom right)
    prim('cylinder', brass, radius=0.075, depth=0.022, location=(cx, cy, 0.011), vertices=48)
    prim('torus', brass, major_radius=0.075, minor_radius=0.008, location=(cx, cy, 0.022))
    prim('cylinder', face, radius=0.066, depth=0.002, location=(cx, cy, 0.023), vertices=48)
    nd = prim('cone', mat('needle', srgb('b8302a'), 0.4), radius1=0.006, depth=0.1, location=(cx, cy, 0.026), vertices=4); nd.rotation_euler = (math.pi / 2, 0, 0.6)
    prim('cylinder', glass, radius=0.068, depth=0.004, location=(cx, cy, 0.03), vertices=48)
    # candle (top left) + flame + warm light
    wax = mat('wax', srgb('efe3c4'), 0.5)
    prim('cylinder', brass, radius=0.07, depth=0.012, location=(-0.27, 0.36, 0.006), vertices=32)
    prim('cylinder', wax, radius=0.028, depth=0.16, location=(-0.27, 0.36, 0.09), vertices=24)
    fl = prim('uv_sphere', mat('flame', (1, 0.6, 0.2), 0.5, emit=(1.0, 0.62, 0.22), estr=40), radius=0.012, location=(-0.27, 0.36, 0.185)); fl.scale = (1, 1, 2.2)
    pl = bpy.data.lights.new('candle', 'POINT'); pl.energy = 18; pl.color = (1.0, 0.62, 0.3); pl.shadow_soft_size = 0.02
    po = bpy.data.objects.new('candle', pl); po.location = (-0.27, 0.36, 0.2); link(po)
    # ink pot + quill (top right)
    ink = mat('ink', srgb('141018'), 0.08)
    prim('cylinder', ink, radius=0.04, depth=0.06, location=(0.28, 0.36, 0.03), vertices=32)
    # wax seal + coins (bottom left)
    prim('cylinder', mat('seal', srgb('9a1e22'), 0.35), radius=0.03, depth=0.008, location=(-0.26, -0.34, 0.004), vertices=32)
    for i in range(3): prim('cylinder', brass, radius=0.016, depth=0.003, location=(-0.18 + i * 0.03, -0.37 + i * 0.012, 0.0015 + i * 0.003), vertices=24)
    # warm key light from window (top-left) + soft fill
    al = bpy.data.lights.new('key', 'AREA'); al.energy = 60; al.size = 0.8; al.color = (1.0, 0.86, 0.68)
    ao = bpy.data.objects.new('key', al); ao.location = (-1.0, 0.9, 1.4); link(ao)
    ao.rotation_euler = (Vector((0, 0, 0)) - ao.location).to_track_quat('-Z', 'Y').to_euler()
    fl2 = bpy.data.lights.new('fill', 'AREA'); fl2.energy = 8; fl2.size = 1.5; fl2.color = (0.75, 0.82, 1.0)
    fo = bpy.data.objects.new('fill', fl2); fo.location = (0.9, -0.8, 1.2); link(fo)
    fo.rotation_euler = (Vector((0, 0, 0)) - fo.location).to_track_quat('-Z', 'Y').to_euler()
    return par

# ---------------- render + tone map ----------------
def proj(cam, pts):
    sc = bpy.context.scene
    out = {}
    for k, p in pts.items():
        v = world_to_camera_view(sc, cam, Vector(p))
        out[k] = (-108 + v.x * 1296, -192 + (1 - v.y) * 2304, v.z)
    return out

def tonemap(lin, ev):
    lum = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    key = float(np.exp(np.mean(np.log(np.clip(lum, 1e-4, 1e4)))))
    ev = math.log2(0.20 / key) + ev
    x = lin[..., :3] * (2.0 ** ev)
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14                 # ACES fitted curve
    y = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    y = np.where(y <= 0.0031308, 12.92 * y, 1.055 * np.power(y, 1 / 2.4) - 0.055)
    return np.clip(y * 255 + 0.5, 0, 255).astype(np.uint8)

def render(name, cam, pts, ev):
    sc = bpy.context.scene
    exr = os.path.join(OUT, name + '.exr'); sc.render.filepath = exr
    t0 = time.time(); bpy.ops.render.render(write_still=True); dt = time.time() - t0
    im = bpy.data.images.load(exr); px = np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], 4)[::-1]
    np.save(os.path.join(OUT, name + '_lin.npy'), np.clip(px[..., :3], 0, 6e4).astype(np.float16))
    import cv2
    cv2.imwrite(os.path.join(OUT, name + '.png'), tonemap(px, ev)[..., ::-1])
    json.dump(dict(points=proj(cam, pts), seconds=dt, ev=ev), open(os.path.join(OUT, name + '.json'), 'w'), indent=1)
    print('PLATE', name, '%.1f s' % dt, flush=True)

SUN_E, SUN_A = math.radians(6), math.radians(13)
for name in NAMES:
    reset()
    if name == 'hero':          # S1 low hero angle, sun low behind Napoleon's right
        build_field(SUN_E, SUN_A)
        cam = camera((0.45, -4.2, 0.28), (0.0, 0.0, 1.25), 20)
        render(name, cam, dict(feet=(0, 0, 0), head=(0, 0, 1.7), flag=(1.6, 0.8, 0)), 0.2)
    elif name == 'cu':          # S3 close-up, shallow depth of field
        build_field(SUN_E, SUN_A)
        cam = camera((0.0, -2.6, 1.3), (0.0, 0.0, 1.25), 70, 1.6, 2.6)
        render(name, cam, dict(feet=(0, 0, 0), head=(0, 0, 1.7)), 0.2)
    elif name == 'rab':         # S4 rabbit eye-level close-up
        build_field(SUN_E, SUN_A)
        cam = camera((0.0, -1.15, 0.16), (0.0, 0.0, 0.17), 38, 2.0, 1.15)
        render(name, cam, dict(feet=(0, 0, 0), head=(0, 0, 0.38)), 0.2)
    elif name == 'map':         # S2 map table, near top-down
        par = build_map()
        cam = camera((0.0, -0.30, 1.42), (0.0, 0.0, 0.0), 38)
        render(name, cam, dict(tl=(-0.28, 0.41, 0.006), tr=(0.28, 0.41, 0.006), br=(0.28, -0.37, 0.006), bl=(-0.28, -0.37, 0.006)), 0.0)
