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

M = dict(panel=tex(mat("Панели светло-серые", "#CFCFCB", 0.6), "white_plaster_02", 1.0, None),
         wood=tex(mat("Рейки под орех", "#6E4E36", 0.5), "washed_grey_oak_veneer", 3.0, "#7A5638", 1.8),
         dark=mat("Скамья тёмная", "#26262A", 0.4), cushion=mat("Сиденье", "#3A3A3E", 0.9),
         ceil=mat("Потолок", "#F1F1EE", 0.9), door=mat("Входная дверь", "#2A2A2C", 0.35), floor=mat("Пол светло-серый", "#CFCDC8", 0.5),
         brass=mat("Латунь", "#B8925A", 0.25, 1.0), mirror=mat("Зеркало", "#DDE3E6", 0.02, 1.0),
         console=tex(mat("Консоль орех", "#6E4E36", 0.5), "washed_grey_oak_veneer", 3.0, "#7A5638", 1.8),
         led=None)
e = bpy.data.materials.new("LED"); e.use_nodes = True; nt = e.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = hexlin("#FFE2B8"); em.inputs[1].default_value = 10
nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs[0]); M["led"] = e

T = 0.2
box("Пол", X0 - 1, Z0 - 2, X1 + 1, Z1 + T, -0.05, 0, M["floor"])
box("Стена лев", X0 - T, Z0 - 2, X0, Z1 + T, 0, H, M["panel"])
box("Стена прав", X1, Z0 - 2, X1 + T, Z1 + T, 0, H, M["panel"])
box("Стена у двери лев", X0, Z1, EX0, Z1 + T, 0, H, M["panel"]); box("Стена у двери прав", EX1, Z1, X1, Z1 + T, 0, H, M["panel"])
box("Над дверью", EX0, Z1, EX1, Z1 + T, 2.1, H, M["panel"])
box("Потолок", X0 - 1, Z0 - 2, X1 + 1, Z1 + T, H, H + 0.05, M["ceil"])
box("Входная дверь", EX0, Z1 + 0.03, EX1, Z1 + 0.08, 0, 2.1, M["door"], 0.004)
box("Ручка", EX0 + 0.06, Z1 + 0.0, EX0 + 0.08, Z1 + 0.03, 0.95, 1.25, M["brass"], 0.003)
box("Плинтус", X0, Z0 - 2, X0 + 0.012, Z1, 0, 0.08, M["panel"]); box("Плинтус", X1 - 0.012, Z0 - 2, X1, Z1, 0, 0.08, M["panel"])
# рейки под орех за скамьёй (левая стена) + крючки
ra, rb = 8.25, 9.35
box("Рейки фон", X0, ra, X0 + 0.012, rb, 0, H, M["wood"])
n = int((rb - ra) / 0.04)
for k in range(n):
    z = ra + k * (rb - ra) / n
    box("Рейка", X0 + 0.012, z + 0.004, X0 + 0.032, z + (rb - ra) / n - 0.004, 0, H, M["wood"], 0.004)
for z in np.linspace(ra + 0.15, rb - 0.15, 5):
    box("Крючок", X0 + 0.032, z - 0.008, X0 + 0.09, z + 0.008, 1.68, 1.70, M["dark"], 0.004)
    box("Крючок", X0 + 0.08, z - 0.008, X0 + 0.095, z + 0.008, 1.70, 1.74, M["dark"], 0.003)
# скамья-обувница тёмная
box("Скамья корпус", X0 + 0.032, 8.35, X0 + 0.38, 9.25, 0.06, 0.46, M["dark"], 0.006)
box("Скамья ниша", X0 + 0.05, 8.38, X0 + 0.385, 9.22, 0.08, 0.30, M["cushion"], 0.003)
box("Скамья сиденье", X0 + 0.032, 8.35, X0 + 0.39, 9.25, 0.46, 0.50, M["cushion"], 0.01)
box("Подсветка скамьи", X0 + 0.05, 8.38, X0 + 0.37, 9.22, 0.02, 0.025, M["led"])
# консоль орех + зеркало (правая стена)
box("Консоль", X1 - 0.25, 8.40, X1, 9.10, 0.80, 0.86, M["console"], 0.004)
box("Зеркало рама", X1 - 0.025, 8.53, X1, 8.97, 1.13, 1.87, M["dark"], 0.004)
box("Зеркало", X1 - 0.03, 8.56, X1 - 0.02, 8.94, 1.16, 1.84, M["mirror"])

def area(loc, size, energy, rot=(0, 0, 0), color=(1, 0.9, 0.78), sy=None):
    lt = bpy.data.lights.new("A", "AREA"); lt.energy = energy; lt.color = color; lt.shape = "RECTANGLE"; lt.size = size; lt.size_y = sy or size
    o = bpy.data.objects.new("A", lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
for z in (8.3, 9.1):                                # 2 точечных светильника
    lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = 25; lt.spot_size = math.radians(80); lt.spot_blend = 0.6; lt.color = (1, 0.9, 0.78)
    o = bpy.data.objects.new("Спот", lt); o.location = W((X0 + X1) / 2, z, H - 0.02); sc.collection.objects.link(o)
    box("Спот", (X0 + X1) / 2 - 0.04, z - 0.04, (X0 + X1) / 2 + 0.04, z + 0.04, H - 0.004, H - 0.001, M["led"])
area(W((X0 + X1) / 2, Z0 - 1.0, H - 0.05), 1.4, 80)   # свет из коридора
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
sc.view_settings.exposure = -0.2
for (n, loc, tgt, lens) in CAMS:
    cd = bpy.data.cameras.new(n); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02
    co = bpy.data.objects.new(n, cd); co.location = loc; co.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(co)
    sc.camera = co; sc.render.filepath = os.path.join(OUT, ("q_" if QUICK else "") + n + ".jpg"); bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
