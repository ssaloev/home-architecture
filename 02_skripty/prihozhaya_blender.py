# -*- coding: utf-8 -*-
"""Прихожая — 3D по согласованному (11.2026): бамбуковые панели Dekorchi светло-серые гладкие,
за скамьёй рифлёные рейки под орех с крючками, тёмная скамья-обувница, консоль с зеркалом. Без неоклассики.
Запуск: blender -b --factory-startup -P prihozhaya_blender.py -- [quick]"""
import bpy, bmesh, math, os, sys, json
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "quick" in ARGS
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "08_vizualizacii", "prihozhaya"); os.makedirs(OUT, exist_ok=True)
PH = os.path.join(os.path.dirname(HERE), "03_materialy", "polyhaven")
R = next(r for r in D["rooms"] if r["name"] == "Прихожая"); X0, X1, Z0, Z1 = R["rects"][0]
H = 2.65
ENT = next(d for d in D["doors"] if d["type"] == "entry")["rect"]; EX0, EX1 = ENT[0], ENT[0] + ENT[2]

for c in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for b in list(c):
        try: c.remove(b)
        except Exception: pass
sc = bpy.context.scene
def W(x, z, h): return Vector((x, -z, h))
def hexlin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c) + (1.0,)
def mat(name, color, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexlin(color); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if coat and "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    return m
def tex(m, t, scale, tint=None, k=2.0):
    d = os.path.join(PH, t)
    if not os.path.isdir(d): return m
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    def T(fn, col):
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(d, fn), check_existing=True)
        if not col: n.image.colorspace_settings.name = "Non-Color"
        n.projection = "BOX"; n.projection_blend = 0.3; nt.links.new(mp.outputs[0], n.inputs["Vector"]); return n
    tn = T("nor.jpg", False); nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.5
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b.inputs["Normal"])
    if tint:
        td = T("diff.jpg", True); bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(td.outputs["Color"], bw.inputs[0])
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = k; nt.links.new(bw.outputs[0], mm.inputs[0])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
        mx.inputs[6].default_value = hexlin(tint); nt.links.new(mm.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m
def box(name, x0, z0, x1, z1, h0, h1, m, bevel=0.0):
    bm = bmesh.new()
    vs = [bm.verts.new(W(x, z, h)) for (x, z, h) in [(x0, z0, h0), (x1, z0, h0), (x1, z1, h0), (x0, z1, h0), (x0, z0, h1), (x1, z0, h1), (x1, z1, h1), (x0, z1, h1)]]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 3; md.limit_method = "ANGLE"
        for p in o.data.polygons: p.use_smooth = True
    return o

FLOOR = next((x.split("=")[1] for x in ARGS if x.startswith("floor=")), "grey")
PW = float(next((x.split("=")[1] for x in ARGS if x.startswith("pw=")), "1.22"))   # ширина листа бамбуковой панели
def grain(m, c1, c2, sc_len=3.0, sc_fine=420.0, bump=0.15, vertical=False):
    """процедурный бамбуковый шпон: тонкие волокна"""
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (sc_fine, sc_fine, sc_len) if vertical else (sc_len, sc_len, sc_fine)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.65
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[1].position = 0.7
    cr.color_ramp.elements[0].color = hexlin(c2); cr.color_ramp.elements[1].color = hexlin(c1)
    nt.links.new(nz.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.0005
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    return m
M = dict(panel=grain(mat("Бамбуковые панели тёмно-серые", "#55534F", 0.5), "#5C5A56", "#4A4845"),
         seam=mat("Профиль бронза", "#3A3026", 0.35, 0.8),
         bronze=mat("Бронза тёмная", "#3B3129", 0.3, 0.85),
         dark=mat("Скамья тёмная", "#2E2A27", 0.4), cushion=mat("Сиденье", "#3E3A37", 0.9),
         ceil=mat("Потолок", "#EFEDE8", 0.9), door=mat("Входная дверь", "#2C2825", 0.35),
         floor=(grain(mat("Пол дуб", "#C9A57E", 0.45), "#CFAB82", "#B88F64", 2.0, 60.0, 0.05) if FLOOR == "oak" else mat("Пол светло-серый", "#CFCDC8", 0.5)),
         mirror=mat("Зеркало", "#DDE3E6", 0.02, 1.0),
         console=grain(mat("Консоль орех", "#6E4E36", 0.45), "#4E3626", "#3A281C", 3.0, 300.0, 0.05))
def emis(name, col, s):
    e = bpy.data.materials.new(name); e.use_nodes = True; nt = e.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = hexlin(col); em.inputs[1].default_value = s
    nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs[0]); return e
M["led"] = emis("LED", "#FFD9A8", 12); M["disc"] = emis("Плафон", "#FFE6C4", 6)

T = 0.2; PT = 0.012; GAP = 0.003; TOP = H - 0.07      # листы до TOP, выше — теневой паз с LED
box("Пол", X0 - 1, Z0 - 2, X1 + 1, Z1 + T, -0.05, 0, M["floor"])
box("Стена лев", X0 - T, Z0 - 2, X0, Z1 + T, 0, H, M["seam"])
box("Стена прав", X1, Z0 - 2, X1 + T, Z1 + T, 0, H, M["seam"])
box("Стена у двери лев", X0, Z1, EX0, Z1 + T, 0, H, M["seam"]); box("Стена у двери прав", EX1, Z1, X1, Z1 + T, 0, H, M["seam"])
box("Над дверью", EX0, Z1, EX1, Z1 + T, 2.1, H, M["seam"])
box("Потолок", X0 - 1, Z0 - 2, X1 + 1, Z1 + T, H, H + 0.05, M["ceil"])
# бамбуковые листы ~1220 мм на всю высоту, только вертикальные швы
def sheets(axis, fixed, a0, a1, sign, door=None):
    xs = [a0]; p = a0 + PW
    while p < a1 - 0.2: xs.append(p); p += PW
    xs.append(a1)
    if door:                                   # швы по краям наличника
        xs = sorted(set([x for x in xs if not (door[0] - 0.15 < x < door[1] + 0.15)] + [door[0], door[1]]))
    for u0, u1 in zip(xs[:-1], xs[1:]):
        hb, ht = 0.0, TOP
        if door and u0 >= door[0] - 1e-6 and u1 <= door[1] + 1e-6: hb = door[2]
        c0, c1 = u0 + GAP / 2, u1 - GAP / 2
        if axis == "x": box("Лист", fixed, c0, fixed + sign * PT, c1, hb, ht, M["panel"], 0.001)
        else: box("Лист", c0, fixed, c1, fixed + sign * PT, hb, ht, M["panel"], 0.001)
sheets("x", X0, Z0 - 2, Z1, +1)
sheets("x", X1, Z0 - 2, Z1, -1)
sheets("z", Z1, X0, X1, -1, door=(EX0 - 0.06, EX1 + 0.06, 2.16 + GAP))
for (nm, x0_, z0_, x1_, z1_) in (("LED лев", X0 + 0.002, Z0 - 2, X0 + 0.008, Z1), ("LED прав", X1 - 0.008, Z0 - 2, X1 - 0.002, Z1),
                                ("LED дверь", X0, Z1 - 0.008, X1, Z1 - 0.002)):
    box(nm, x0_, z0_, x1_, z1_, TOP + 0.012, TOP + 0.02, M["led"])
def area(loc, size, energy, rot=(0, 0, 0), color=(1, 0.86, 0.68), sy=None, spread=None):
    lt = bpy.data.lights.new("A", "AREA"); lt.energy = energy; lt.color = color; lt.shape = "RECTANGLE"; lt.size = size; lt.size_y = sy or size
    if spread: lt.spread = math.radians(spread)
    o = bpy.data.objects.new("A", lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
L = Z1 - (Z0 - 2)
area(W(X0 + 0.03, (Z0 - 2 + Z1) / 2, TOP + 0.01), 0.03, 60, sy=L, spread=70)
area(W(X1 - 0.03, (Z0 - 2 + Z1) / 2, TOP + 0.01), 0.03, 60, sy=L, spread=70)
area(W((X0 + X1) / 2, Z1 - 0.03, TOP + 0.01), X1 - X0, 20, sy=0.03, spread=70)
# входная дверь + наличник бронза
box("Входная дверь", EX0, Z1 - 0.005, EX1, Z1 + 0.02, 0, 2.1, M["door"], 0.004)
for (a0, a1) in ((EX0 - 0.06, EX0), (EX1, EX1 + 0.06)): box("Наличник", a0, Z1 - PT - 0.006, a1, Z1, 0, 2.16, M["bronze"], 0.002)
box("Наличник верх", EX0 - 0.06, Z1 - PT - 0.006, EX1 + 0.06, Z1, 2.1, 2.16, M["bronze"], 0.002)
box("Ручка", EX0 + 0.07, Z1 - 0.07, EX0 + 0.09, Z1 - 0.005, 1.0, 1.02, M["bronze"], 0.003)
box("Ручка", EX0 + 0.07, Z1 - 0.07, EX0 + 0.20, Z1 - 0.05, 1.0, 1.02, M["bronze"], 0.003)
# крючки, скамья (левая стена)
xp = X0 + PT
for z in np.linspace(8.45, 9.15, 4):
    box("Крючок", xp, z - 0.008, xp + 0.06, z + 0.008, 1.68, 1.70, M["bronze"], 0.004)
    box("Крючок", xp + 0.05, z - 0.008, xp + 0.065, z + 0.008, 1.70, 1.74, M["bronze"], 0.003)
box("Скамья корпус", xp, 8.35, xp + 0.36, 9.25, 0.06, 0.46, M["dark"], 0.006)
box("Скамья ниша", xp + 0.02, 8.38, xp + 0.365, 9.22, 0.08, 0.30, M["cushion"], 0.003)
box("Скамья сиденье", xp, 8.35, xp + 0.37, 9.25, 0.46, 0.51, M["cushion"], 0.012)
box("Подсветка скамьи", xp + 0.02, 8.38, xp + 0.35, 9.22, 0.02, 0.025, M["led"])
# консоль + зеркало + 2 вертикальных бра (правая стена)
xq = X1 - PT
box("Консоль", xq - 0.25, 8.40, xq, 9.10, 0.80, 0.86, M["console"], 0.004)
box("Зеркало рама", xq - 0.02, 8.55, xq, 8.95, 1.10, 1.90, M["bronze"], 0.004)
box("Зеркало", xq - 0.025, 8.57, xq - 0.015, 8.93, 1.12, 1.88, M["mirror"])
for z in (8.44, 9.06):
    box("Бра корпус", xq - 0.035, z - 0.012, xq, z + 0.012, 1.20, 1.80, M["bronze"], 0.004)
    box("Бра свет", xq - 0.038, z - 0.006, xq - 0.034, z + 0.006, 1.24, 1.76, M["led"])
    area(W(xq - 0.05, z, 1.5), 0.02, 6, rot=(0, math.radians(90), 0), sy=0.5)
# 2 накладных круглых светильника
for z in (8.3, 9.1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.16, depth=0.05, location=W((X0 + X1) / 2, z, H - 0.025))
    bpy.context.active_object.data.materials.append(M["bronze"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.145, depth=0.01, location=W((X0 + X1) / 2, z, H - 0.052))
    bpy.context.active_object.data.materials.append(M["disc"])
    lt = bpy.data.lights.new("Плафон", "AREA"); lt.shape = "DISK"; lt.size = 0.28; lt.energy = 35; lt.color = (1, 0.88, 0.72)
    o = bpy.data.objects.new("Плафон", lt); o.location = W((X0 + X1) / 2, z, H - 0.06); sc.collection.objects.link(o)
area(W((X0 + X1) / 2, Z0 - 1.0, H - 0.08), 1.2, 40)
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.3

CAMS = [("1_ot_koridora_k_dveri", W((X0 + X1) / 2 + 0.1, Z0 - 0.9, 1.5), W((X0 + X1) / 2 - 0.1, Z1, 1.15), 16),
        ("2_skamya", W(X1 - 0.15, Z0 - 0.3, 1.45), W(X0, 8.8, 1.0), 18)]
sc.render.engine = "CYCLES"
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    for dv in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = dv; pr.get_devices()
            for d in pr.devices: d.use = True
            sc.cycles.device = "GPU"; break
        except Exception: continue
except Exception: pass
sc.cycles.samples = 48 if QUICK else 384; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = (960, 540) if QUICK else (1920, 1080)
sc.render.image_settings.file_format = "JPEG"
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
sc.view_settings.exposure = -1.1
for (n, loc, tgt, lens) in CAMS:
    cd = bpy.data.cameras.new(n); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02
    co = bpy.data.objects.new(n, cd); co.location = loc; co.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(co)
    sc.camera = co; sc.render.filepath = os.path.join(OUT, ("q_" if QUICK else "") + n + ".jpg"); bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
