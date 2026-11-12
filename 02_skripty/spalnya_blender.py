# -*- coding: utf-8 -*-
"""Спальня 2 — вариант 3: серые панели, мягкое изголовье-стена, линейный свет.
Запуск: blender -b --factory-startup -P spalnya_blender.py -- [quick] [shots=1,2,3]"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "quick" in ARGS
OPT = dict(a.split("=", 1) for a in ARGS if "=" in a)
SHOTS = OPT.get("shots", "1,2,3").split(",")
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, "08_vizualizacii", "spalnya2"); os.makedirs(OUT, exist_ok=True)
PH = os.path.join(PROJ, "03_materialy", "polyhaven"); BK = os.path.join(PROJ, "03_materialy", "blenderkit")
X0, X1, Z0, Z1 = 10.072, 14.745, 4.327, 7.491
H, HC, SL = 2.70, 2.62, 0.08
WZ0, WZ1, WS, WT = 5.618, 7.182, 0.80, 2.40      # окно на правой стене (x = X1)
DZ0, DZ1, DH = 6.60, 7.40, 2.10                   # дверь на левой стене (x = X0)

for c in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for b in list(c):
        try: c.remove(b)
        except Exception: pass
sc = bpy.context.scene
def W(x, z, h): return Vector((x, -z, h))
def hexlin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c) + (1.0,)
def mat(name, color, rough=0.5, metal=0.0, transm=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexlin(color); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if transm and "Transmission Weight" in b.inputs: b.inputs["Transmission Weight"].default_value = transm
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
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
def import_bk(name, cx, cz, h0=0.0, rot_deg=0.0, target=None, axis="w"):
    f = os.path.join(BK, name + ".blend")
    if not os.path.exists(f): print("NO MODEL", name); return []
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [n for n in src.objects]
    objs = [o for o in dst.objects if o is not None and o.type not in ("LIGHT", "CAMERA")]
    for o in objs: sc.collection.objects.link(o)
    roots = [o for o in objs if o.parent is None or o.parent not in objs]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    if not pts: return objs
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = {"w": max(mx_.x - mn.x, mx_.y - mn.y), "h": mx_.z - mn.z}[axis]
    k = (target / size) if target else 1.0; ctr = (mn + mx_) / 2
    T_ = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T_ @ r.matrix_world
    return objs

WALLC = "#" + OPT.get("walls", "BDBBB5"); GRAF = "#" + OPT.get("ward", "2F2F31")
M = dict(wall=tex(mat("Бамбуковые панели серые", WALLC, 0.38), "washed_grey_oak_veneer", 1.6, WALLC, 1.55, 0.7),
         seam=mat("Шов панелей", "#2E2C2A", 0.6), floor=plank_floor("D5D4D0", "C4C3BE"),
         ward=mat("Графит матовый", GRAF, 0.45), frame=mat("Рамки фасадов", "#3A3A3D", 0.45),
         top=mat("Столешница камень", "#E9E6E0", 0.15), brass=mat("Латунь", "#B8925A", 0.25, 1.0),
         ceil=mat("Потолок", "#EEECE7", 0.9), door=mat("Двери", "#E2E0DB", 0.45), black=mat("Чёрный", "#1C1B1A", 0.35, 0.3),
         tv=mat("ТВ", "#0A0A0B", 0.2), wframe=mat("Рама окна", "#F2F1EE", 0.4), glass=mat("Стекло", "#FFFFFF", 0.0, transm=1.0),
         curt=mat("Шторы", "#" + OPT.get("curt", "8A8B8F"), 0.95), tulle=mat("Тюль", "#F6F3EE", 0.9, transm=0.5, alpha=0.7),
         led=emis("LED", "#FFE6C8", 6), spot=emis("Спот", "#FFF4E2", 12))
try: M["tulle"].blend_method = "BLEND"
except Exception: pass


# ================= СПАЛЬНЯ 2 — вариант 3 (12.11.2026)
T = 0.2
BC = 12.71                                   # ось кровати (между шкафом и правой стеной)
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["floor"])
box("Стена верх", X0 - T, Z0 - T, X1 + T, Z0, 0, H, M["wall"]); box("Стена низ", X0 - T, Z1, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена лев", X0 - T, Z0, X0, DZ0, 0, H, M["wall"]); box("Стена лев2", X0 - T, DZ1, X0, Z1, 0, H, M["wall"]); box("Над дверью", X0 - T, DZ0, X0, DZ1, DH, H, M["wall"])
box("Стена прав", X1, Z0, X1 + T, WZ0, 0, H, M["wall"]); box("Стена прав2", X1, WZ1, X1 + T, Z1, 0, H, M["wall"])
box("Под окном", X1, WZ0, X1 + T, WZ1, 0, WS, M["wall"]); box("Над окном", X1, WZ0, X1 + T, WZ1, WT, H, M["wall"])
box("Перекрытие", X0 - T, Z0 - T, X1 + T, Z1 + T, H, H + 0.05, M["ceil"])
NI = 0.16
box("Потолок", X0 + SL, Z0 + SL, X1 - NI - SL, Z1 - SL, HC, H, M["ceil"])
for (a0, b0, a1, b1) in ((X0 + 0.01, Z0, X0 + 0.03, Z1), (X1 - NI - 0.03, Z0, X1 - NI - 0.01, Z1), (X0, Z0 + 0.01, X1 - NI, Z0 + 0.03), (X0, Z1 - 0.03, X1 - NI, Z1 - 0.01)):
    box("LED паз", a0, b0, a1, b1, HC + 0.03, HC + 0.035, M["led"])
for xx in (11.25, 14.15):                     # 2 линейных светильника вдоль комнаты
    box("Линия света", xx - 0.02, Z0 + 0.35, xx + 0.02, Z1 - 0.35, HC - 0.004, HC, M["spot"])
# окно (правая стена)
box("Подоконник", X1 - 0.04, WZ0 - 0.03, X1 + 0.12, WZ1 + 0.03, WS - 0.03, WS, M["wframe"], 0.005)
for a in np.linspace(WZ0, WZ1, 3): box("Импост", X1 + 0.06, a - 0.03, X1 + 0.12, a + 0.03, WS, WT, M["wframe"], 0.004)
for (h0, h1) in ((WS, WS + 0.06), (WT - 0.06, WT)): box("Рама", X1 + 0.06, WZ0, X1 + 0.12, WZ1, h0, h1, M["wframe"], 0.004)
box("Стекло", X1 + 0.085, WZ0, X1 + 0.095, WZ1, WS, WT, M["glass"])
def seam_x(fixed, n_, xs):
    for p in xs: box("Шов", p - 0.008, fixed, p + 0.008, fixed + n_ * 0.0008, 0.08, HC, M["seam"])
def seam_z(fixed, n_, zs):
    for p in zs: box("Шов", fixed, p - 0.008, fixed + n_ * 0.0008, p + 0.008, 0.08, HC, M["seam"])
seam_x(Z1, -1, [11.3, BC - 0.61, BC + 0.61])
seam_z(X1, -1, [4.95])
for (a, b, c, d) in ((X0 + 0.6, Z0, X1, Z0 + 0.015), (X0, Z1 - 0.015, X1, Z1), (X1 - 0.015, Z0, X1, Z1)):
    box("Плинтус", a, b, c, d, 0, 0.08, M["wall"], 0.002)

# ---------------- стена за кроватью: мягкие вертикальные панели + рамка орех + подсветка
M["soft"] = mat("Мягкие панели серо-бежевые", "#" + OPT.get("soft", "8C8580"), 0.95)
M["walnut"] = tex(mat("Орех", "#5A3E2B", 0.45), "washed_grey_oak_veneer", 2.0, "#6B4A33", 1.4)
HW0, HW1, HH = BC - 1.45, BC + 1.45, 1.30
box("Рамка орех", HW0 - 0.04, Z0, HW1 + 0.04, Z0 + 0.03, 0.0, HH + 0.04, M["walnut"], 0.004)
npn = 10; pw = (HW1 - HW0) / npn
for i in range(npn):
    a = HW0 + i * pw
    box("Мягкая панель", a + 0.004, Z0 + 0.03, a + pw - 0.004, Z0 + 0.075, 0.12, HH, M["soft"], 0.02)
box("LED над изголовьем", HW0, Z0 + 0.02, HW1, Z0 + 0.03, HH + 0.045, HH + 0.05, M["led"])

# ---------------- кровать 1600 + тумбочки + подвесы
_bed = import_bk("krovat_myagkaya", BC, Z0 + 0.08 + 1.05, 0.0, 0, 1.80)
for (xx, rot) in ((BC - 1.20, 180), (BC + 1.20, 180)):
    import_bk("tumbochka_noir", xx, Z0 + 0.26, 0.0, 0, 0.55)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.003, depth=H - 1.32, location=W(xx, Z0 + 0.30, (H + 1.32) / 2)); bpy.context.active_object.data.materials.append(M["black"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.06, depth=0.24, location=W(xx, Z0 + 0.30, 1.20)); o_ = bpy.context.active_object; o_.data.materials.append(M["brass"]); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.05, depth=0.004, location=W(xx, Z0 + 0.30, 1.079)); bpy.context.active_object.data.materials.append(M["spot"])
    lt = bpy.data.lights.new("Подвес", "POINT"); lt.energy = 6; lt.color = (1, 0.85, 0.65); lt.shadow_soft_size = 0.05
    o = bpy.data.objects.new("Подвес", lt); o.location = W(xx, Z0 + 0.30, 1.05); sc.collection.objects.link(o)

# ---------------- встроенный шкаф графит (левая стена, до потолка)
b0, b1, wx = Z0, 6.509, X0 + 0.60
box("Шкаф", X0, b0, wx, b1, 0, HC, M["ward"])
n = 4; w = (b1 - b0) / n
for k in range(n):
    u0, u1 = b0 + k * w + 0.07, b0 + (k + 1) * w - 0.07
    for (p0, p1, q0, q1) in ((u0, u1, HC - 0.2, HC - 0.17), (u0, u1, 0.15, 0.18), (u0, u0 + 0.03, 0.15, HC - 0.17), (u1 - 0.03, u1, 0.15, HC - 0.17)):
        box("Рамка фасада", wx, p0, wx + 0.012, p1, q0, q1, M["frame"], 0.003)
    if k: box("Шов", wx, b0 + k * w - 0.0015, wx + 0.002, b0 + k * w + 0.0015, 0.02, HC - 0.02, M["black"])
    hz = b0 + (k + 1) * w - 0.05 if k % 2 == 0 else b0 + k * w + 0.05
    box("Ручка латунь", wx + 0.012, hz - 0.008, wx + 0.035, hz + 0.008, 0.70, 1.55, M["brass"], 0.004)

# ---------------- дверь (левая стена)
xf = X0 - 0.05
box("Полотно", xf - 0.02, DZ0 + 0.03, xf + 0.02, DZ1 - 0.03, 0, DH - 0.03, M["door"], 0.003)
for (a, b) in ((DZ0, DZ0 + 0.03), (DZ1 - 0.03, DZ1)): box("Рамка", xf - 0.03, a, xf + 0.03, b, 0, DH, M["black"], 0.002)
box("Рамка", xf - 0.03, DZ0, xf + 0.03, DZ1, DH - 0.03, DH, M["black"], 0.002)
box("Ручка", xf + 0.02, DZ1 - 0.10, xf + 0.07, DZ1 - 0.09, 1.0, 1.02, M["black"]); box("Ручка", xf + 0.055, DZ1 - 0.22, xf + 0.07, DZ1 - 0.09, 1.0, 1.02, M["black"])

# ---------------- ТВ напротив кровати: подвесная тумба графит + ТВ 55"
t0, t1 = BC - 0.8, BC + 0.8
box("ТВ-тумба", t0, Z1 - 0.40, t1, Z1, 0.30, 0.62, M["ward"]); box("Столешница", t0 - 0.01, Z1 - 0.41, t1 + 0.01, Z1, 0.62, 0.645, M["top"], 0.003)
for k in range(2):
    u0, u1 = t0 + k * 0.8 + 0.003, t0 + (k + 1) * 0.8 - 0.003
    box("Фасад", u0, Z1 - 0.42, u1, Z1 - 0.40, 0.305, 0.615, M["ward"], 0.002)
    box("Ручка", (u0 + u1) / 2 - 0.1, Z1 - 0.435, (u0 + u1) / 2 + 0.1, Z1 - 0.42, 0.55, 0.562, M["brass"], 0.003)
box("ТВ 55", BC - 0.62, Z1 - 0.045, BC + 0.62, Z1 - 0.01, 1.0, 1.70, M["tv"], 0.004)

# ---------------- туалетный столик с зеркалом (угол у окна) + пуф + растение
box("Столик", 13.75, Z1 - 0.40, 14.55, Z1, 0.72, 0.75, M["top"], 0.004)
box("Ящик столика", 13.77, Z1 - 0.40, 14.53, Z1, 0.58, 0.72, M["ward"], 0.003)
box("Зеркало подсв.", 13.80, Z1 - 0.025, 14.50, Z1 - 0.02, 1.0, 1.85, M["led"])
box("Зеркало", 13.82, Z1 - 0.03, 14.48, Z1 - 0.025, 1.02, 1.83, mat("Зеркало", "#E3E7E8", 0.02, 1.0))
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.2, depth=0.44, location=W(14.15, Z1 - 0.65, 0.22)); bpy.context.active_object.data.materials.append(M["soft"])
import_bk("rastenie_bolshoe", X1 - 0.30, Z0 + 0.30, 0.0, 0, 1.2, "h")

# ---------------- кондиционер К3 (план: правая стена, z 4.60–5.40, верх h=2500) + розетка h=2200
ACZ0, ACZ1 = 4.60, 5.40
M["acw"] = mat("Кондиционер белый", "#F3F3F1", 0.35)
def ac_unit(wall, along, top=2.50, flip=False, width=1.10):
    """Кондиционер (BlenderKit Midea) на стене: wall = ('R'|'L'|'T'|'B', координата стены); along — центр вдоль стены."""
    f = os.path.join(BK, "kondicioner_slim.blend")
    if not os.path.exists(f): return
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [n for n in src.objects]
    objs = [o for o in dst.objects if o is not None and o.type not in ("LIGHT", "CAMERA")]
    for o in objs: sc.collection.objects.link(o)
    roots = [o for o in objs if o.parent is None or o.parent not in objs]
    side, wc = wall
    rz = {"R": -90, "L": 90, "T": 0, "B": 180}[side] + (180 if flip else 0)
    R = Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X") @ Matrix.Scale(width / 0.715, 4)
    for r in roots: r.matrix_world = R @ r.matrix_world
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    if side == "R": tgt = Vector((wc - (mx.x - mn.x) / 2 - 0.01, -along, top - (mx.z - mn.z) / 2))
    elif side == "L": tgt = Vector((wc + (mx.x - mn.x) / 2 + 0.01, -along, top - (mx.z - mn.z) / 2))
    elif side == "T": tgt = Vector((along, -(wc + (mx.y - mn.y) / 2 + 0.01), top - (mx.z - mn.z) / 2))
    else: tgt = Vector((along, -(wc - (mx.y - mn.y) / 2 - 0.01), top - (mx.z - mn.z) / 2))
    d = tgt - (mn + mx) / 2
    for r in roots: r.matrix_world = Matrix.Translation(d) @ r.matrix_world
ac_unit(("R", X1), (ACZ0 + ACZ1) / 2, 2.54, flip="acflip" in ARGS)
# ---------------- шторы на правой стене
def drape_z(name, a0, a1, xc, amp, waves, m):
    bm = bmesh.new(); nu = int((a1 - a0) / 0.02); rows = []
    for h in (0.0, H - 0.02):
        rows.append([bm.verts.new(W(xc + amp * math.sin(2 * math.pi * waves * i / nu), a0 + (a1 - a0) * i / nu, h)) for i in range(nu + 1)])
    for i in range(nu): bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    o.modifiers.new("s", "SOLIDIFY").thickness = 0.006
    for p in o.data.polygons: p.use_smooth = True
drape_z("Тюль", ACZ1 + 0.05, Z1 - 0.03, X1 - 0.05, 0.025, (Z1 - WZ0) / 0.12, M["tulle"])
drape_z("Штора 1", ACZ1 + 0.05, WZ0 + 0.20, X1 - 0.11, 0.04, 6, M["curt"])
drape_z("Штора 2", WZ1 - 0.20, Z1 - 0.02, X1 - 0.11, 0.04, 4, M["curt"])

# ---------------- свет
def area(loc, size, energy, rot=(0, 0, 0), color=(1, 0.95, 0.88), sy=None, spread=None):
    lt = bpy.data.lights.new("A", "AREA"); lt.energy = energy; lt.color = color; lt.shape = "RECTANGLE"; lt.size = size; lt.size_y = sy or size
    if spread: lt.spread = math.radians(spread)
    o = bpy.data.objects.new("A", lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
area(W(X1 + 0.5, (WZ0 + WZ1) / 2, 1.6), WZ1 - WZ0, 350, rot=(0, math.radians(-90), 0), sy=WT - WS, color=(0.95, 0.97, 1.0))
for (x0_, z0_, x1_, z1_) in ((X0 + 0.04, Z0, X0 + 0.04, Z1), (X1 - NI - 0.04, Z0, X1 - NI - 0.04, Z1), (X0, Z0 + 0.04, X1, Z0 + 0.04), (X0, Z1 - 0.04, X1, Z1 - 0.04)):
    L = max(abs(x1_ - x0_), abs(z1_ - z0_)); hz = abs(x1_ - x0_) > abs(z1_ - z0_)
    area(W((x0_ + x1_) / 2, (z0_ + z1_) / 2, HC + 0.02), L if hz else 0.03, 30 * L, sy=0.03 if hz else L, spread=80)
for xx in (11.25, 14.15):
    area(W(xx, (Z0 + Z1) / 2, HC - 0.01), 0.04, 60, sy=Z1 - Z0 - 0.7)
area(W(BC, Z0 + 0.06, HH + 0.06), HW1 - HW0, 15, sy=0.02, color=(1, 0.86, 0.66))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.3

# ---------------- камеры
CAMS = {"1": ("1_ot_dveri_k_krovati", W(10.95, 7.25, 1.50), W(13.4, 4.4, 1.0), 15),
        "2": ("2_ot_okna_k_shkafu", W(14.35, 4.75, 1.50), W(10.5, 7.1, 1.05), 15),
        "3": ("3_krovat_pryamo", W(BC, 7.35, 1.45), W(BC, Z0, 1.0), 16)}

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
sc.cycles.samples = 48 if QUICK else 160; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = (960, 540) if QUICK else (1920, 1080)
sc.render.image_settings.file_format = "JPEG"
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
sc.view_settings.exposure = float(OPT.get("exp", "-0.6"))
tag = OPT.get("tag", "")
for s_ in SHOTS:
    if s_ not in CAMS: continue
    n_, loc, tgt, lens = CAMS[s_]
    cd = bpy.data.cameras.new(n_); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02
    co = bpy.data.objects.new(n_, cd); co.location = loc; co.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(co)
    sc.camera = co; sc.render.filepath = os.path.join(OUT, ("q_" if QUICK else "") + n_ + tag + ".jpg"); bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
