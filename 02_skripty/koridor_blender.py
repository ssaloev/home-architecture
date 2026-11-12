# -*- coding: utf-8 -*-
"""Коридор + прихожая — 3D по картинке заказчика (12.11.2026): тёплые кремовые стены, шкафы до потолка
с длинными чёрными ручками, акцентная стена из реек под дуб + зеркало с подсветкой + подвесная консоль,
потолок с подсветкой по периметру и рядом крупных круглых светильников по центру, пол дуб + дорожка.
Запуск: blender -b --factory-startup -P koridor_blender.py -- [quick] [floor=oak|grey] [shots=1,2]"""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "quick" in ARGS
OPT = dict(a.split("=", 1) for a in ARGS if "=" in a)
FLOOR = OPT.get("floor", "oak")
SHOTS = OPT.get("shots", "1,2,3,4").split(",")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "08_vizualizacii", "koridor"); os.makedirs(OUT, exist_ok=True)
PH = os.path.join(os.path.dirname(HERE), "03_materialy", "polyhaven")
H = 2.70          # перекрытие
HC = 2.62         # подвесной потолок (центр)
SL = 0.08         # ширина паза с LED по периметру

for c in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for b in list(c):
        try: c.remove(b)
        except Exception: pass
sc = bpy.context.scene
def W(x, z, h): return Vector((x, -z, h))
def hexlin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c) + (1.0,)
def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexlin(color); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m
def tex(m, t, scale, tint, k=2.0, nstr=0.4):
    d = os.path.join(PH, t)
    if not os.path.isdir(d): return m
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    def T(fn, col):
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(d, fn), check_existing=True)
        if not col: n.image.colorspace_settings.name = "Non-Color"
        n.projection = "BOX"; n.projection_blend = 0.3; nt.links.new(mp.outputs[0], n.inputs["Vector"]); return n
    tn = T("nor.jpg", False); nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b.inputs["Normal"])
    td = T("diff.jpg", True); bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(td.outputs["Color"], bw.inputs[0])
    mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = k; nt.links.new(bw.outputs[0], mm.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
    mx.inputs[6].default_value = hexlin(tint); nt.links.new(mm.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m
def emis(name, col, s):
    e = bpy.data.materials.new(name); e.use_nodes = True; nt = e.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = hexlin(col); em.inputs[1].default_value = s
    nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs[0]); return e
def box(name, x0, z0, x1, z1, h0, h1, m, bevel=0.0):
    x0, x1 = min(x0, x1), max(x0, x1); z0, z1 = min(z0, z1), max(z0, z1)
    bm = bmesh.new()
    vs = [bm.verts.new(W(x, z, h)) for (x, z, h) in [(x0, z0, h0), (x1, z0, h0), (x1, z1, h0), (x0, z1, h0), (x0, z0, h1), (x1, z0, h1), (x1, z1, h1), (x0, z1, h1)]]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 3; md.limit_method = "ANGLE"
        for p in o.data.polygons: p.use_smooth = True
    return o
def cyl(name, x, z, h, r, depth, m, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=W(x, z, h))
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m)
    bpy.ops.object.shade_smooth(); return o
def import_ph(name, cx, cz, target_w, rot_deg=0.0, h0=0.0):
    f = os.path.join(PH, name, "model.gltf")
    if not os.path.exists(f): return []
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f)
    objs = [o for o in bpy.data.objects if o not in before]; roots = [o for o in objs if o.parent is None]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    k = target_w / max(1e-6, (mx_.x - mn.x)); ctr = (mn + mx_) / 2
    T_ = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T_ @ r.matrix_world
    return objs

def grain(m, c1, c2, sc_len=2.0, sc_fine=260.0, bump=0.08, vertical=True):
    """бамбуковый шпон: тонкие волокна (вертикальные) + лёгкая неравномерность тона"""
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (sc_fine, sc_fine, sc_len) if vertical else (sc_len, sc_len, sc_fine)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[1].position = 0.7
    cr.color_ramp.elements[0].color = hexlin(c2); cr.color_ramp.elements[1].color = hexlin(c1)
    nt.links.new(nz.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.0004
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    return m
def shade(hx, k):
    h = hx.lstrip("#"); c = [max(0, min(255, int(int(h[i:i + 2], 16) * k))) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(c)
WALLC = "#" + OPT.get("walls", "BDBBB5")
import numpy as np
def plank_floor(A, B, PL=0.6, PW=0.09):
    OFFS = [0, 160, 80, 200, 40, 120, 220, 100]; PHs = [0, 1, 1, 0, 1, 0, 0, 1]
    tw, th = 2 * PL, 8 * PW; nx, ny = 2048, 1024
    xs = (np.arange(nx) + 0.5) / nx * tw; ys = (np.arange(ny) + 0.5) / ny * th
    XX, YY = np.meshgrid(xs, ys); row = (YY // PW).astype(int) % 8
    off = np.array(OFFS)[row] / 240 * PL; u = (XX - off) % tw; k = (u // PL).astype(int)
    tone = (k + np.array(PHs)[row]) % 2
    A_, B_ = (np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)]) / 255 for c in (A, B))
    col = np.where(tone[..., None] == 0, A_, B_)
    pid = row * 4 + k; rng = np.random.default_rng(7)
    col = col + rng.normal(0, 0.012, 64)[pid % 64][..., None] + (np.sin((XX * 48 / PL + np.sin(YY * 90 + pid) * 0.6) * (6 + (pid % 5))) * 0.012)[..., None]
    seam = (np.minimum(u % PL, PL - u % PL) < 0.0012) | (np.minimum(YY % PW, PW - YY % PW) < 0.0010)
    col[seam] *= 0.84; col = np.clip(col, 0, 1) ** 2.2
    img = bpy.data.images.new("ламинат", nx, ny, alpha=False); px = np.ones((ny, nx, 4), np.float32); px[..., :3] = col
    img.pixels.foreach_set(px.ravel()); img.pack()
    m = mat("Пол — ламинат серый 600×90", "#D5D4D0", 0.42); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Cubic"
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / tw, 1 / th, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], t.inputs["Vector"]); nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m
M = dict(wall=tex(mat("Бамбуковые панели серые", WALLC, 0.38), "washed_grey_oak_veneer", 1.6, WALLC, 1.55, 0.7),
         ward=mat("Шкафы крем матовые", "#" + OPT.get("ward", "2F2F31"), 0.55),
         slat=tex(mat("Рейки дуб", "#C9A57A", 0.5), "washed_grey_oak_veneer", 2.0, "#C79F72", 1.6),
         floor=(plank_floor("D5D4D0", "C4C3BE") if FLOOR == "oak"
                else mat("Пол светло-серый", "#CFCDC8", 0.5)),
         rug=mat("Дорожка", "#" + OPT.get("rug", "9C9890"), 1.0),
         ceil=mat("Потолок", "#EEE8DF", 0.9), door=mat("Двери крем", "#" + OPT.get("door", "E2E0DB"), 0.45),
         black=mat("Чёрный матовый", "#1C1B1A", 0.35, 0.3), console=mat("Консоль крем", "#E8DFD2", 0.4),
         mirror=mat("Зеркало", "#E3E7E8", 0.02, 1.0), pouf=mat("Пуф букле", "#E3DACD", 1.0),
         vase=mat("Ваза керамика", "#D8CFC2", 0.8), shade=emis("Абажур", "#FFE2B8", 3.0), led=emis("LED", "#FFE6C8", 6),
         disc=emis("Светильник", "#FFF0D8", 9), glass=mat("Стекло тёмное", "#3A2E22", 0.1))

# ---------------------------------------------------------------- геометрия по плану (kvartira.json)
CX0, CX1, CZ0, CZ1 = 1.945, 9.945, 6.672, 7.909        # коридор
PX0, PX1, PZ1 = 1.945, 3.455, 9.509                     # прихожая (до входной двери)
KX0, KX1, KZ1 = 6.0, 9.945, 8.418                       # карман под шкафы
T = 0.15
box("Пол", 0.5, 4.0, 11, 10.5, -0.05, 0, M["floor"])
box("Перекрытие", 0.5, 4.0, 11, 10.5, H, H + 0.05, M["ceil"])
def wall(x0, z0, x1, z1, openings=(), along="x"):
    """стена с проёмами (a0, a1, h): along — вдоль какой оси идёт стена"""
    a0, a1 = (x0, x1) if along == "x" else (z0, z1)
    cuts = sorted(openings); p = a0
    def seg(s0, s1, h0, h1):
        if s1 - s0 < 1e-3: return
        if along == "x": box("Стена", s0, z0, s1, z1, h0, h1, M["wall"])
        else: box("Стена", x0, s0, x1, s1, h0, h1, M["wall"])
    for (o0, o1, oh) in cuts:
        seg(p, o0, 0, H); seg(o0, o1, oh, H); p = o1
    seg(p, a1, 0, H)
# север коридора: двери в гостиную и комнату, проход к кухне
wall(CX0, CZ0 - T, 9.145, CZ0, [(2.145, 2.945, 2.1), (8.145, 8.945, 2.1)])
box("Стена к кухне лев", 9.145 - 0.0, 4.2, 9.145 + 0.0 + 0.001, CZ0, 0, H, M["wall"])
box("Торец к кухне", 9.0, 5.2, 10.2, 5.35, 0, H, M["wall"])
# юг коридора: стена ванной с дверью; карман со шкафами
wall(PX1, CZ1, KX0, CZ1 + T, [(4.255, 5.055, 2.1)])
box("Стена кармана", KX0, KZ1, CX1, KZ1 + T, 0, H, M["wall"]); box("Торец кармана", KX0 - T, CZ1, KX0, KZ1, 0, H, M["wall"])
# восток: дверь в спальню 2
wall(CX1, CZ0, CX1 + T, CZ1, [(6.75, 7.55, 2.1)], along="z")
# запад: дверь в санузел + стены прихожей + входная дверь
wall(CX0 - T, CZ0, CX0, PZ1, [(7.0, 7.8, 2.1)], along="z")
box("Прихожая вост", PX1, CZ1, PX1 + T, PZ1, 0, H, M["wall"])
wall(PX0, PZ1, PX1, PZ1 + T, [(2.254, 3.145, 2.1)])

# швы бамбуковых листов (1220 мм) — тонкая тёмная V-канавка
M["seam"] = mat("Шов панелей", "#2E2C2A", 0.6)
def seams(axis, fixed, a0, a1, n_, skip=()):
    p = a0 + 1.22
    while p < a1 - 0.15:
        if not any(s0 - 0.05 < p < s1 + 0.05 for (s0, s1) in skip):
            if axis == "x": box("Шов", p - 0.008, fixed, p + 0.008, fixed + n_ * 0.0008, 0.08, HC, M["seam"])
            else: box("Шов", fixed, p - 0.008, fixed + n_ * 0.0008, p + 0.008, 0.08, HC, M["seam"])
        p += 1.22
seams("x", CZ0, CX0, 9.145, +1, skip=((2.145, 2.945), (8.145, 8.945)))
seams("x", CZ1, PX1, KX0, -1, skip=((4.255, 5.055),))
seams("z", PX1, CZ1, PZ1, -1)
seams("z", PX0, CZ0, 7.95, +1, skip=((7.0, 7.8),))
for (a0, a1, f, ax_, n_) in ((CX0, PX1, PZ1, "x", -1),):
    pass
# ---------------------------------------------------------------- двери: крем, тонкая чёрная рамка, чёрная ручка
def door(x0, z0, x1, z1, axis, side, entry=False):
    """axis x: дверь в стене вдоль x на z0 (лицо со стороны side=+1 к +z или -1)"""
    fr = 0.03
    if axis == "x":
        zf = z0
        box("Полотно", x0 + fr, zf - 0.02, x1 - fr, zf + 0.02, 0, 2.1 - fr, M["door"], 0.003)
        for (a, b_) in ((x0, x0 + fr), (x1 - fr, x1)): box("Рамка", a, zf - 0.03, b_, zf + 0.03, 0, 2.1, M["black"], 0.002)
        box("Рамка", x0, zf - 0.03, x1, zf + 0.03, 2.1 - fr, 2.1, M["black"], 0.002)
        hx = x1 - 0.09 if not entry else x0 + 0.09; dz = side * 0.025
        box("Ручка", hx - 0.006, zf + dz, hx + 0.006, zf + dz + side * 0.05, 1.0, 1.02, M["black"], 0.003)
        box("Ручка", (hx if entry else hx - 0.12), zf + dz + side * 0.04, (hx + 0.12 if entry else hx), zf + dz + side * 0.055, 1.0, 1.02, M["black"], 0.003)
        if entry:
            box("Глазок", (x0 + x1) / 2 - 0.008, zf + side * 0.02, (x0 + x1) / 2 + 0.008, zf + side * 0.025, 1.55, 1.566, M["black"])
            box("Замок", hx - 0.015, zf + side * 0.02, hx + 0.015, zf + side * 0.03, 1.12, 1.22, M["black"], 0.002)
    else:
        xf = x0
        box("Полотно", xf - 0.02, z0 + fr, xf + 0.02, z1 - fr, 0, 2.1 - fr, M["door"], 0.003)
        for (a, b_) in ((z0, z0 + fr), (z1 - fr, z1)): box("Рамка", xf - 0.03, a, xf + 0.03, b_, 0, 2.1, M["black"], 0.002)
        box("Рамка", xf - 0.03, z0, xf + 0.03, z1, 2.1 - fr, 2.1, M["black"], 0.002)
        hz = z1 - 0.09; dx = side * 0.025
        box("Ручка", xf + dx, hz - 0.006, xf + dx + side * 0.05, hz + 0.006, 1.0, 1.02, M["black"], 0.003)
        box("Ручка", xf + dx + side * 0.04, hz - 0.12, xf + dx + side * 0.055, hz, 1.0, 1.02, M["black"], 0.003)
door(2.145, CZ0 - 0.07, 2.945, None, "x", +1)
door(8.145, CZ0 - 0.07, 8.945, None, "x", +1)
door(4.255, CZ1 + 0.07, 5.055, None, "x", -1)
door(CX1 + 0.07, 6.75, None, 7.55, "z", -1)
door(CX0 - 0.07, 7.0, None, 7.8, "z", +1)
door(2.254, PZ1 + 0.08, 3.145, None, "x", -1, entry=True)
# видеодомофон у входной двери
box("Домофон", PX1 - 0.005, 9.29, PX1, 9.46, 1.45, 1.57, M["black"], 0.003)
box("Экран", PX1 - 0.007, 9.305, PX1 - 0.005, 9.445, 1.47, 1.55, M["glass"])
# плинтус с LED-подсветкой снизу (светится на пол), в тон стен
M["skirt"] = mat("Плинтус алюм. крем", "#DCD1C1", 0.35, 0.2)
M["led_floor"] = emis("LED плинтус", "#FFE0B8", 60)
SK = []   # (a0, a1, fixed, axis, n)  axis x: стена вдоль x на z=fixed, n — куда смотрит лицо
for (a0, a1) in ((CX0, 2.145), (2.945, 8.145), (8.945, 9.145)): SK.append((a0, a1, CZ0, "x", +1))
for (a0, a1) in ((PX1, 4.255), (5.055, KX0)): SK.append((a0, a1, CZ1, "x", -1))
for (a0, a1) in ((CZ0, 7.0), (7.8, 7.95)): SK.append((a0, a1, PX0, "z", +1))
for (a0, a1) in ((CZ1, 8.05), (9.25, PZ1)): SK.append((a0, a1, PX1, "z", -1))
for (a0, a1) in ((CZ0, 6.75), (7.55, CZ1)): SK.append((a0, a1, CX1, "z", -1))
# LED в плинтусе — только вдоль длинных стен коридора; в прихожей и на торцах — обычный плинтус
SK_LED = []   # 12.11: LED в плинтусах убран по решению заказчика
for (a0, a1, f, ax_, n_) in SK:
    led = False
    hb = 0.015 if led else 0.0
    if ax_ == "x":
        box("Плинтус", a0, f, a1, f + n_ * 0.018, hb, 0.08, M["skirt"], 0.002)
        if led: box("LED плинтус", a0, f + n_ * 0.004, a1, f + n_ * 0.012, 0.010, 0.014, M["led_floor"])
    else:
        box("Плинтус", f, a0, f + n_ * 0.018, a1, hb, 0.08, M["skirt"], 0.002)

# ---------------------------------------------------------------- шкафы до потолка в кармане, длинные чёрные ручки
WT = HC - 0.06
nfr = 6; fw = (CX1 - KX0) / nfr
box("Шкаф корпус", KX0, CZ1 + 0.02, CX1, KZ1, 0.0, WT, M["ward"])
for i in range(nfr):
    a = KX0 + i * fw
    box("Фасад", a + 0.002, CZ1, a + fw - 0.002, CZ1 + 0.02, 0.07, WT, M["ward"], 0.002)
    if i % 2 == 0: hx = a + fw - 0.05
    else: hx = a + 0.05
    box("Ручка шкафа", hx - 0.007, CZ1 - 0.018, hx + 0.007, CZ1, 0.55, 1.75, M["black"], 0.003)
box("Цоколь", KX0, CZ1 + 0.06, CX1, CZ1 + 0.07, 0, 0.07, M["black"])
box("LED над шкафом", KX0, CZ1 + 0.03, CX1, CZ1 + 0.05, WT + 0.01, WT + 0.015, M["led"])

# ---------------------------------------------------------------- акцентная стена напротив шкафов: рейки дуб + зеркало с подсветкой + консоль
SA0, SA1 = 5.55, 7.45; zw = CZ0
MX0, MX1, MH0, MH1 = 6.05, 6.95, 1.12, 2.12
mz = zw + 0.05
def rrect(name, x0, x1, h0, h1, z0, z1, r, m, along_z=None):
    bpy.ops.mesh.primitive_plane_add(size=1); o = bpy.context.active_object; o.name = name
    o.scale = (x1 - x0, h1 - h0, 1); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.affect = "VERTICES"; md.width = r; md.segments = 10
    so = o.modifiers.new("s", "SOLIDIFY"); so.thickness = z1 - z0
    o.rotation_euler = (math.radians(90), 0, 0); o.location = W((x0 + x1) / 2, z1, (h0 + h1) / 2)
    if along_z is not None:      # x0..x1 — это отрезок по z, along_z = координата x лица
        o.rotation_euler = (math.radians(90), 0, math.radians(90)); o.location = W(along_z, (x0 + x1) / 2, (h0 + h1) / 2)
    o.data.materials.append(m); return o

# ---------------------------------------------------------------- прихожая (запад): шкаф хозяев + открытая зона для одежды гостей
HX1 = PX0 + 0.40
box("Шкаф прих корпус", PX0, 7.95, HX1 - 0.02, 8.70, 0, WT, M["ward"])
for (a, b_) in ((7.95, 8.325), (8.325, 8.70)):
    box("Фасад прих", HX1 - 0.02, a + 0.002, HX1, b_ - 0.002, 0.07, WT, M["ward"], 0.002)
hz = 8.325
for d_ in (-0.05, 0.05):
    box("Ручка прих", HX1, hz + d_ - 0.007, HX1 + 0.018, hz + d_ + 0.007, 0.55, 1.75, M["black"], 0.003)
box("Цоколь прих", HX1 - 0.07, 7.95, HX1 - 0.06, 8.70, 0, 0.07, M["black"])
# гостевая зона: рейки дуб на стене, штанга с плечиками, полка для шапок, скамья
GZ0, GZ1 = 8.72, 9.30
box("Гост рейки фон", PX0, GZ0, PX0 + 0.012, GZ1, 0, WT, M["slat"])
ng = int((GZ1 - GZ0) / 0.045)
for k in range(ng):
    a = GZ0 + k * (GZ1 - GZ0) / ng
    box("Рейка", PX0 + 0.012, a + 0.006, PX0 + 0.035, a + (GZ1 - GZ0) / ng - 0.006, 0, WT, M["slat"], 0.006)
box("Боковина гост", PX0, GZ0 - 0.02, HX1, GZ0, 0, WT, M["ward"])
box("Полка шапки", PX0 + 0.035, GZ0, HX1 - 0.03, GZ1, 1.92, 1.95, M["ward"], 0.003)
box("LED полка", HX1 - 0.06, GZ0, HX1 - 0.045, GZ1, 1.915, 1.92, M["led"])
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.012, depth=GZ1 - GZ0 - 0.02, location=W(PX0 + 0.22, (GZ0 + GZ1) / 2, 1.82))
o = bpy.context.active_object; o.rotation_euler = (math.radians(90), 0, 0); o.data.materials.append(M["black"])
for z in (8.86, 9.00, 9.14):        # плечики для гостей (дуб)
    box("Плечики", PX0 + 0.04, z - 0.008, PX0 + 0.40, z + 0.008, 1.70, 1.73, M["slat"], 0.006)
    box("Крюк плечиков", PX0 + 0.215, z - 0.004, PX0 + 0.225, z + 0.004, 1.73, 1.82, M["black"])
box("Скамья гост", PX0 + 0.035, GZ0, HX1 - 0.03, GZ1, 0.42, 0.46, M["ward"], 0.004)
box("Сиденье гост", PX0 + 0.04, GZ0 + 0.01, HX1 - 0.04, GZ1 - 0.01, 0.46, 0.51, M["pouf"], 0.012)
box("LED под скамьёй", PX0 + 0.05, GZ0, HX1 - 0.05, GZ1, 0.415, 0.42, M["led"])
# восток прихожей: узкая обувница-слим 240 мм с откидными секциями, подвесная, у входной двери
SZ0, SZ1, SD = 8.05, 9.25, 0.24
# обувница slim с 3 откидными секциями (обувь стоит под углом — много пар при глубине 240) + 2 ящика сверху
box("Обувница корпус", PX1 - SD + 0.02, SZ0, PX1, SZ1, 0.10, 1.20, M["ward"])
box("Цоколь обувн", PX1 - SD + 0.06, SZ0 + 0.03, PX1, SZ1 - 0.03, 0.0, 0.10, M["black"])
fx = PX1 - SD
for i, (h0, h1) in enumerate(((0.105, 0.40), (0.405, 0.70), (0.705, 1.00))):
    tilt = 0.035 if i == 1 else 0.0                       # средняя секция приоткрыта — видно, что откидная
    o = box("Откидная секция", fx - tilt, SZ0 + 0.003, fx + 0.02, SZ1 - 0.003, h0, h1, M["ward"], 0.003)
    box("Ручка секции", fx - tilt - 0.016, (SZ0 + SZ1) / 2 - 0.16, fx - tilt, (SZ0 + SZ1) / 2 + 0.16, h1 - 0.05, h1 - 0.038, M["black"], 0.003)
    if tilt:   # пары обуви внутри видны в щель
        for k in range(5):
            zc = SZ0 + 0.13 + k * 0.23
            box("Обувь", fx + 0.0, zc - 0.05, fx + 0.10, zc + 0.05, h1 - 0.12, h1 - 0.03, M["black" if k % 2 else "console"], 0.02)
for (a0, a1) in ((SZ0, (SZ0 + SZ1) / 2), ((SZ0 + SZ1) / 2, SZ1)):
    box("Ящик", fx, a0 + 0.003, fx + 0.02, a1 - 0.003, 1.005, 1.195, M["ward"], 0.003)
    box("Ручка ящика", fx - 0.016, (a0 + a1) / 2 - 0.08, fx, (a0 + a1) / 2 + 0.08, 1.09, 1.102, M["black"], 0.003)
box("Столешница обувницы", fx - 0.01, SZ0 - 0.01, PX1, SZ1 + 0.01, 1.20, 1.23, M["slat"], 0.003)
box("Поднос ключи", PX1 - 0.19, 8.85, PX1 - 0.05, 9.07, 1.23, 1.245, M["black"], 0.004)

# зеркало с подсветкой над обувницей (восток прихожей)
rrect("Подсветка зеркала", 8.14, 8.96, 1.31, 2.13, 0, 0.004, 0.14, M["led"], along_z=PX1 - 0.036)
rrect("Зеркало", 8.15, 8.95, 1.32, 2.12, 0, 0.01, 0.13, M["mirror"], along_z=PX1 - 0.03)

# ---------------------------------------------------------------- дорожка-ковёр
# дорожка убрана 12.11 (заказчик: ковры не нужны)

# ---------------------------------------------------------------- потолок: подвесная плоскость, паз с LED по периметру, ряд крупных круглых светильников
box("Потолок коридор", CX0 + SL, CZ0 + SL, CX1 - SL, CZ1 - SL, HC, H, M["ceil"])
box("Потолок прихожая", PX0 + SL, CZ1 - SL, PX1 - SL, PZ1 - SL, HC, H, M["ceil"])
box("Потолок над шкафом", KX0, CZ1, CX1, KZ1, WT + 0.06, H, M["ceil"])
box("Угол паза", PX1 - SL - 0.01, CZ1 - SL - 0.01, PX1 + 0.01, CZ1 + 0.01, HC, H, M["ceil"])
box("Угол паза2", CX0 - 0.01, CZ1 - SL - 0.01, CX0 + SL + 0.01, CZ1 + 0.01, HC, H, M["ceil"])
def strip(x0, z0, x1, z1):
    box("LED паз", x0, z0, x1, z1, HC + 0.03, HC + 0.035, M["led"])
strip(CX0 + 0.01, CZ0 + 0.01, CX1 - 0.01, CZ0 + 0.03)
strip(PX1, CZ1 - 0.03, CX1, CZ1 - 0.01)
strip(CX0 + 0.01, CZ0, CX0 + 0.03, PZ1 - 0.01); strip(PX1 - 0.03, CZ1, PX1 - 0.01, PZ1 - 0.01)
strip(PX0, PZ1 - 0.03, PX1, PZ1 - 0.01); strip(CX1 - 0.03, CZ0, CX1 - 0.01, CZ1)
def area(loc, size, energy, rot=(0, 0, 0), color=(1, 0.95, 0.88), sy=None, spread=None, shape="RECTANGLE"):
    lt = bpy.data.lights.new("A", "AREA"); lt.energy = energy; lt.color = color; lt.shape = shape; lt.size = size; lt.size_y = sy or size
    if spread: lt.spread = math.radians(spread)
    o = bpy.data.objects.new("A", lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
    return o
K = 30                       # Вт на метр паза (смыв света по стенам)
for (x0, z0, x1, z1) in ((CX0, CZ0 + 0.04, CX1, CZ0 + 0.04), (PX1, CZ1 - 0.04, CX1, CZ1 - 0.04),
                          (CX0 + 0.04, CZ0, CX0 + 0.04, PZ1), (PX1 - 0.04, CZ1, PX1 - 0.04, PZ1), (PX0, PZ1 - 0.04, PX1, PZ1 - 0.04),
                          (CX1 - 0.04, CZ0, CX1 - 0.04, CZ1)):
    L = max(abs(x1 - x0), abs(z1 - z0)); horiz = abs(x1 - x0) > abs(z1 - z0)
    area(W((x0 + x1) / 2, (z0 + z1) / 2, HC + 0.02), L if horiz else 0.03, K * L, sy=0.03 if horiz else L, spread=80)
# крупные круглые светильники Ø240 по центру
DL = [(x, (CZ0 + CZ1) / 2) for x in (2.75, 3.95, 5.15, 6.35, 7.55, 8.75)] + [((PX0 + PX1) / 2, 8.55), ((PX0 + PX1) / 2, 9.15)]
for (x, z) in DL:
    cyl("Светильник обод", x, z, HC - 0.004, 0.125, 0.008, M["black"])
    cyl("Светильник", x, z, HC - 0.009, 0.112, 0.004, M["disc"])
    lt = bpy.data.lights.new("Даунлайт", "AREA"); lt.shape = "DISK"; lt.size = 0.22; lt.energy = float(OPT.get("dl", "5")); lt.color = (1, 0.93, 0.84)
    o = bpy.data.objects.new("Даунлайт", lt); o.location = W(x, z, HC - 0.015); sc.collection.objects.link(o)
# мягкий отражённый свет лампы и зеркала
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.05

# свет от плинтусов на пол
for (a0, a1, f, ax_, n_) in SK_LED:
    L = a1 - a0
    if ax_ == "x": area(W((a0 + a1) / 2, f + n_ * 0.03, 0.012), L, 18 * L, sy=0.02, color=(1, 0.9, 0.78))
    else: area(W(f + n_ * 0.03, (a0 + a1) / 2, 0.012), 0.02, 18 * L, sy=L, color=(1, 0.9, 0.78))
# ---------------------------------------------------------------- камеры
CAMS = {"1": ("1_koridor_k_prihozhey", W(9.75, 7.29, 1.45), W(2.6, 7.29, 1.38), 18),
        "2": ("2_vhodnaya_dver", W(2.85, 7.45, 1.50), W(2.6, 9.6, 1.0), 14),
        "4": ("4_prihozhaya_gosti", W(3.25, 9.35, 1.45), W(1.95, 8.4, 1.05), 15),
        "3": ("3_prihozhaya_zerkalo", W(2.35, 9.3, 1.5), W(3.455, 8.35, 1.25), 16)}
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
sc.cycles.samples = 64 if QUICK else 160; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = (960, 640) if QUICK else (1920, 1280)
sc.render.image_settings.file_format = "JPEG"
try:
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = float(OPT.get("exp", "-2.0"))
tag = OPT.get("tag", "")
for s in SHOTS:
    if s not in CAMS: continue
    n, loc, tgt, lens = CAMS[s]
    cd = bpy.data.cameras.new(n); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02
    co = bpy.data.objects.new(n, cd); co.location = loc; co.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(co)
    sc.camera = co; sc.render.filepath = os.path.join(OUT, ("q_" if QUICK else "") + n + tag + ".jpg"); bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
