# -*- coding: utf-8 -*-
"""Комната (вторая гостиная) — 12.11.2026: серые бамбуковые панели с видимыми листами (без лепнины),
пол серый ламинат 600×90, встроенные шкаф и ТВ-тумба графит с латунью, кремовый диван + 2 серых кресла (BlenderKit),
мраморный столик, потолок: паз с LED по периметру + споты.
Запуск: blender -b --factory-startup -P komnata_blender.py -- [quick] [shots=1,2,3] [curt=hex] [exp=-1.0]"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "quick" in ARGS
OPT = dict(a.split("=", 1) for a in ARGS if "=" in a)
SHOTS = OPT.get("shots", "1,2,3").split(",")
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, "08_vizualizacii", "komnata"); os.makedirs(OUT, exist_ok=True)
PH = os.path.join(PROJ, "03_materialy", "polyhaven"); BK = os.path.join(PROJ, "03_materialy", "blenderkit")
X0, X1, Z0, Z1 = 5.745, 8.945, 0.309, 6.545
H, HC, SL = 2.70, 2.62, 0.08
WX0, WX1, WS, WT = 6.273, 8.437, 0.80, 2.40
DX0, DX1, DH = 8.145, 8.945, 2.10

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

# ---------------- коробка комнаты
T = 0.2
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["floor"])
box("Стена лев", X0 - T, Z0 - T, X0, Z1 + T, 0, H, M["wall"]); box("Стена прав", X1, Z0 - T, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена низ", X0, Z1, DX0, Z1 + T, 0, H, M["wall"]); box("Над дверью", DX0, Z1, DX1, Z1 + T, DH, H, M["wall"])
box("Окно лев", X0, Z0 - T, WX0, Z0, 0, H, M["wall"]); box("Окно прав", WX1, Z0 - T, X1, Z0, 0, H, M["wall"])
box("Под окном", WX0, Z0 - T, WX1, Z0, 0, WS, M["wall"]); box("Над окном", WX0, Z0 - T, WX1, Z0, WT, H, M["wall"])
box("Перекрытие", X0 - T, Z0 - T, X1 + T, Z1 + T, H, H + 0.05, M["ceil"])
box("Потолок", X0 + SL, Z0 + 0.16 + SL, X1 - SL, Z1 - SL, HC, H, M["ceil"])          # подвесной, паз с LED по периметру
box("Ниша штор", X0, Z0, X1, Z0 + 0.16, H - 0.001, H, M["ceil"])
for (a0, b0, a1, b1) in ((X0 + 0.01, Z0 + 0.17, X0 + 0.03, Z1 - 0.01), (X1 - 0.03, Z0 + 0.17, X1 - 0.01, Z1 - 0.01), (X0, Z1 - 0.03, X1, Z1 - 0.01), (X0, Z0 + 0.17, X1, Z0 + 0.19)):
    box("LED паз", a0, b0, a1, b1, HC + 0.03, HC + 0.035, M["led"])
# окно
box("Подоконник", WX0 - 0.03, Z0 - 0.12, WX1 + 0.03, Z0 + 0.04, WS - 0.03, WS, M["wframe"], 0.005)
for a in np.linspace(WX0, WX1, 4):
    box("Импост", a - 0.03, Z0 - 0.12, a + 0.03, Z0 - 0.06, WS, WT, M["wframe"], 0.004)
for (h0, h1) in ((WS, WS + 0.06), (WT - 0.06, WT)): box("Рама", WX0, Z0 - 0.12, WX1, Z0 - 0.06, h0, h1, M["wframe"], 0.004)
box("Стекло", WX0, Z0 - 0.095, WX1, Z0 - 0.085, WS, WT, M["glass"])
# швы листов 1220 (вертикальные), кроме зоны окна/двери/шкафа/тумбы
def seams(axis, fixed, a0, a1, n_, skip=()):
    p = a0 + 1.22
    while p < a1 - 0.15:
        if not any(s0 - 0.05 < p < s1 + 0.05 for (s0, s1) in skip):
            if axis == "x": box("Шов", p - 0.008, fixed, p + 0.008, fixed + n_ * 0.0008, 0.08, HC, M["seam"])
            else: box("Шов", fixed, p - 0.008, fixed + n_ * 0.0008, p + 0.008, 0.08, HC, M["seam"])
        p += 1.22
tm = 3.436
# левая стена (ТВ): швы симметрично ТВ — по краям тумбы (tm±1.55), дальше шагом 1220 наружу
for zz in [tm - 1.55 - 1.22 * i for i in range(0, 3)] + [tm + 1.55 + 1.22 * i for i in range(0, 3)]:
    if Z0 + 0.15 < zz < 5.945 - 0.05: box("Шов", X0, zz - 0.008, X0 + 0.0008, zz + 0.008, 0.08, HC, M["seam"])
seams("z", X1, Z0, Z1, -1)
seams("x", Z0, X0, X1, +1, skip=((WX0, WX1),))
# плинтус в тон стен
for (a, b, c, d) in ((X0, Z0, X0 + 0.015, Z1), (X1 - 0.015, Z0, X1, Z1), (WX1, Z0, X1, Z0 + 0.015), (X0, Z0, WX0, Z0 + 0.015)):
    box("Плинтус", a, b, c, d, 0, 0.08, M["wall"], 0.002)

# ---------------- дверь (как в коридоре: крем, тонкая чёрная рамка)
zf = Z1 + 0.05
box("Полотно", DX0 + 0.03, zf - 0.02, DX1 - 0.03, zf + 0.02, 0, DH - 0.03, M["door"], 0.003)
for (a, b) in ((DX0, DX0 + 0.03), (DX1 - 0.03, DX1)): box("Рамка", a, zf - 0.03, b, zf + 0.03, 0, DH, M["black"], 0.002)
box("Рамка", DX0, zf - 0.03, DX1, zf + 0.03, DH - 0.03, DH, M["black"], 0.002)
box("Ручка", DX0 + 0.08, zf - 0.07, DX0 + 0.09, zf - 0.02, 1.0, 1.02, M["black"]); box("Ручка", DX0 + 0.08, zf - 0.07, DX0 + 0.20, zf - 0.055, 1.0, 1.02, M["black"])

# ---------------- встроенный шкаф графит у двери (до потолка), фасады с рамками, латунные ручки
WH = HC
a0, a1, b0 = X0, DX0 - 0.03, Z1 - 0.60
box("Шкаф", a0, b0, a1, Z1, 0, WH, M["ward"])
n = 4; w = (a1 - a0) / n
for k in range(n):
    u0, u1 = a0 + k * w + 0.07, a0 + (k + 1) * w - 0.07
    for (p0, p1, q0, q1) in ((u0, u1, WH - 0.2, WH - 0.17), (u0, u1, 0.15, 0.18), (u0, u0 + 0.03, 0.15, WH - 0.17), (u1 - 0.03, u1, 0.15, WH - 0.17)):
        box("Рамка фасада", p0, b0 - 0.012, p1, b0, q0, q1, M["frame"], 0.003)
    if k: box("Шов", a0 + k * w - 0.0015, b0 - 0.002, a0 + k * w + 0.0015, b0, 0.02, WH - 0.02, M["black"])
    hx = a0 + (k + 1) * w - 0.05 if k % 2 == 0 else a0 + k * w + 0.05
    box("Ручка латунь", hx - 0.008, b0 - 0.035, hx + 0.008, b0 - 0.012, 0.70, 1.55, M["brass"], 0.004)

# ---------------- ТВ-зона: встроенная напольная тумба 3,1 м + ТВ 85"
k0, k1, KD, KH = tm - 1.55, tm + 1.55, 0.45, 0.62
box("ТВ-тумба", X0, k0, X0 + KD - 0.02, k1, 0.08, KH, M["ward"]); box("Цоколь", X0, k0 + 0.02, X0 + KD - 0.06, k1 - 0.02, 0, 0.08, M["black"])
box("Столешница", X0, k0 - 0.01, X0 + KD + 0.01, k1 + 0.01, KH, KH + 0.025, M["top"], 0.004)
dw = (k1 - k0) / 4
for k in range(4):
    u0, u1 = k0 + k * dw + 0.003, k0 + (k + 1) * dw - 0.003
    if OPT.get("tvzone", "G") == "G" and k in (1, 2):
        box("Фасад над камином", X0 + KD - 0.02, u0, X0 + KD, u1, 0.53, KH - 0.005, M["ward"], 0.002); continue
    box("Фасад", X0 + KD - 0.02, u0, X0 + KD, u1, 0.085, KH - 0.005, M["ward"], 0.002)
    mz = (u0 + u1) / 2; box("Ручка", X0 + KD, mz - 0.11, X0 + KD + 0.014, mz + 0.11, KH - 0.115, KH - 0.103, M["brass"], 0.004)
TVZ = OPT.get("tvzone", "G")   # 12.11: выбран G — рейки + электрокамин
TX = X0
if TVZ:                                    # акцентная стена за ТВ на ширину тумбы, до потолка, LED по краям
    za0, za1, d_ = k0, k1, 0.03
    if TVZ == "A":
        M["slat"] = tex(mat("Рейки дуб", "#C9A57A", 0.5), "washed_grey_oak_veneer", 2.0, "#BF9A6E", 1.6)
        box("Фон реек", X0, za0, X0 + 0.012, za1, KH + 0.025, HC, M["seam"])
        nr = int((za1 - za0) / 0.045)
        for i in range(nr):
            a = za0 + i * (za1 - za0) / nr
            box("Рейка", X0 + 0.012, a + 0.006, X0 + d_, a + (za1 - za0) / nr - 0.006, KH + 0.025, HC, M["slat"], 0.005)
    else:
        M["acc"] = (tex(mat("Панель под мрамор", "#EDEBE6", 0.2), "marble_01", 0.45, "#EEECE7", 1.25, 0.2) if TVZ == "B" else mat("Панель графит", "#3A3A3C", 0.35))
        box("Акцентная панель", X0, za0, X0 + d_, za1, KH + 0.025, HC, M["acc"])
    if TVZ in ("A", "B", "C"):
        for zz in (za0 - 0.006, za1 + 0.006):
            box("LED край", X0 + 0.004, zz - 0.004, X0 + 0.012, zz + 0.004, KH + 0.03, HC - 0.01, M["led"])
    TX = X0 + d_
    def slats(a0, a1, h0, h1, col="#3A3A3C"):
        M.setdefault("slatd", mat("Рейки графит", col, 0.45))
        box("Фон реек", X0, a0, X0 + 0.012, a1, h0, h1, M["black"])
        nr = int((a1 - a0) / 0.045)
        for i in range(nr):
            a = a0 + i * (a1 - a0) / nr; box("Рейка", X0 + 0.012, a + 0.007, X0 + 0.035, a + (a1 - a0) / nr - 0.007, h0, h1, M["slatd"], 0.004)
    def lit_niche(a0, a1, h0, h1, shelves=3, dep=0.30):
        box("Ниша фон", X0, a0, X0 + 0.01, a1, h0, h1, M["slat"] if "slat" in M else M["top"])
        for (b0, b1) in ((a0 - 0.03, a0), (a1, a1 + 0.03)): box("Ниша борт", X0, b0, X0 + dep, b1, h0, h1, M["ward"])
        for h in [h0 + (h1 - h0) * (i + 1) / (shelves + 1) for i in range(shelves)] + [h0, h1 - 0.03]:
            box("Полка", X0, a0, X0 + dep, a1, h, h + 0.03, M["ward"])
            box("LED полки", X0 + 0.02, a0 + 0.02, X0 + 0.04, a1 - 0.02, h - 0.004, h, M["led"])
            lt = bpy.data.lights.new("LED полки", "AREA"); lt.size = dep * 0.8; lt.size_y = a1 - a0 - 0.04; lt.energy = 6; lt.color = (1, 0.88, 0.7)
            o = bpy.data.objects.new("LED полки", lt); o.location = W(X0 + dep / 2, (a0 + a1) / 2, h - 0.01); sc.collection.objects.link(o)
    if TVZ in ("D", "G"):
        M["slat"] = tex(mat("Дуб", "#C9A57A", 0.5), "washed_grey_oak_veneer", 2.0, "#BF9A6E", 1.6)
        slats(tm - 1.05, tm + 1.05, KH + 0.025, HC); TX = X0 + 0.035
        if TVZ == "D": lit_niche(tm + 1.12, k1 - 0.02, KH + 0.025, HC - 0.05, 4)
        if TVZ == "G":   # электрокамин в тумбе: чёрная рамка, глубокая ниша, стекло, языки пламени, угли
            fw, f0, f1 = 0.62, 0.20, 0.50
            box("Камин рамка", X0 + KD - 0.005, tm - fw - 0.03, X0 + KD + 0.004, tm + fw + 0.03, f0 - 0.03, f1 + 0.03, M["black"], 0.002)
            box("Камин ниша", X0 + 0.08, tm - fw, X0 + KD - 0.004, tm + fw, f0, f0 + 0.005, M["black"])
            box("Камин задник", X0 + 0.08, tm - fw, X0 + 0.085, tm + fw, f0, f1, M["black"])
            for (zz0, zz1) in ((tm - fw, tm - fw + 0.005), (tm + fw - 0.005, tm + fw)): box("Камин бок", X0 + 0.08, zz0, X0 + KD - 0.004, zz1, f0, f1, M["black"])
            box("Камин верх", X0 + 0.08, tm - fw, X0 + KD - 0.004, tm + fw, f1 - 0.005, f1, M["black"])
            M["coal"] = mat("Угли", "#151515", 0.6); box("Угли", X0 + 0.15, tm - fw + 0.05, X0 + 0.28, tm + fw - 0.05, f0, f0 + 0.04, M["coal"], 0.01)
            fl = bpy.data.materials.new("Пламя"); fl.use_nodes = True; nt = fl.node_tree; [nt.nodes.remove(n) for n in list(nt.nodes)]
            out = nt.nodes.new("ShaderNodeOutputMaterial"); mix = nt.nodes.new("ShaderNodeMixShader"); tr = nt.nodes.new("ShaderNodeBsdfTransparent"); em = nt.nodes.new("ShaderNodeEmission")
            em.inputs[0].default_value = hexlin("#FF7A1E"); em.inputs[1].default_value = 6
            tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (14, 14, 3.5)
            nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Detail"].default_value = 4
            gr = nt.nodes.new("ShaderNodeSeparateXYZ"); mt = nt.nodes.new("ShaderNodeMath"); mt.operation = "SUBTRACT"
            ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[1].position = 0.5
            nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], nz.inputs["Vector"])
            nt.links.new(tc.outputs["Object"], gr.inputs[0])
            nt.links.new(nz.outputs["Fac"], mt.inputs[0]); nt.links.new(gr.outputs["Z"], mt.inputs[1])
            nt.links.new(mt.outputs[0], ramp.inputs[0])
            nt.links.new(ramp.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs[0])
            try: fl.blend_method = "BLEND"
            except Exception: pass
            pl_ = box("Пламя", X0 + 0.20, tm - fw + 0.06, X0 + 0.205, tm + fw - 0.06, f0 + 0.03, f1 - 0.04, fl)
            # Object-координаты пламени: высота 0..~0.5 → чтобы языки шли вверх, смещаем origin
            pl_.data.transform(Matrix.Translation(Vector((0, 0, -(f0 + 0.03))))); pl_.location = Vector((0, 0, f0 + 0.03))
            box("Камин стекло", X0 + KD - 0.004, tm - fw, X0 + KD - 0.001, tm + fw, f0, f1, M["glass"])
            lt = bpy.data.lights.new("Камин", "AREA"); lt.size = 1.1; lt.size_y = 0.2; lt.energy = 8; lt.color = (1, 0.55, 0.22)
            o = bpy.data.objects.new("Камин", lt); o.location = W(X0 + KD - 0.1, tm, 0.33); o.rotation_euler = (0, math.radians(90), 0); sc.collection.objects.link(o)
    if TVZ == "E":
        M["slat"] = tex(mat("Дуб", "#C9A57A", 0.5), "washed_grey_oak_veneer", 2.0, "#BF9A6E", 1.6)
        lit_niche(k0 + 0.03, k0 + 0.55, KH + 0.025, HC - 0.1, 3); lit_niche(k1 - 0.55, k1 - 0.03, KH + 0.025, HC - 0.1, 3)
    if TVZ == "F":
        M["slat"] = tex(mat("Дуб", "#C9A57A", 0.5), "washed_grey_oak_veneer", 2.0, "#BF9A6E", 1.6)
        cw = 0.55
        for (a0_, a1_) in ((k0, k0 + cw), (k1 - cw, k1)):
            box("Колонна", X0, a0_, X0 + KD, a1_, KH + 0.025, HC, M["ward"])
            box("Ручка", X0 + KD, (a0_ + a1_) / 2 - 0.007 + (0.2 if a0_ == k0 else -0.2), X0 + KD + 0.015, (a0_ + a1_) / 2 + 0.007 + (0.2 if a0_ == k0 else -0.2), 1.0, 1.8, M["brass"], 0.003)
        box("Антресоль", X0, k0 + cw, X0 + KD, k1 - cw, 2.10, HC, M["ward"])
        box("Ниша ТВ фон", X0, k0 + cw, X0 + 0.02, k1 - cw, KH + 0.025, 2.10, M["slat"])
        box("LED ниши", X0 + 0.25, k0 + cw + 0.02, X0 + 0.27, k1 - cw - 0.02, 2.094, 2.098, M["led"])
        lt = bpy.data.lights.new("LED ниши", "AREA"); lt.size = 0.3; lt.size_y = k1 - k0 - 2 * cw; lt.energy = 25; lt.color = (1, 0.88, 0.7)
        o = bpy.data.objects.new("LED ниши", lt); o.location = W(X0 + 0.2, tm, 2.09); sc.collection.objects.link(o)
        TX = X0 + 0.02
box("ТВ 85\"", TX + 0.01, tm - 0.95, TX + 0.045, tm + 0.95, 0.85, 1.92, M["tv"], 0.004)

# ---------------- мягкая мебель (BlenderKit): диван у правой стены лицом к ТВ, 2 кресла, мраморный столик
_sofa = import_bk("divan_krem", X1 - 0.50, tm, 0.0, -90, 2.25)
# диван заказчика: серо-голубой трикотажный чехол (по фото 12.11)
M["knit"] = mat("Ткань мебели серая (комплект Peru)", "#" + OPT.get("sofa", "8A8B8F"), 0.85)
_nt = M["knit"].node_tree; _b = _nt.nodes["Principled BSDF"]
_tc = _nt.nodes.new("ShaderNodeTexCoord"); _w = _nt.nodes.new("ShaderNodeTexWave"); _w.inputs["Scale"].default_value = 180; _w.inputs["Distortion"].default_value = 1.5
_nt.links.new(_tc.outputs["Object"], _w.inputs["Vector"]); _bp = _nt.nodes.new("ShaderNodeBump"); _bp.inputs["Strength"].default_value = 0.08
_nt.links.new(_w.outputs["Fac"], _bp.inputs["Height"]); _nt.links.new(_bp.outputs[0], _b.inputs["Normal"])
if "Sheen Weight" in _b.inputs: _b.inputs["Sheen Weight"].default_value = 0.6
for o in _sofa:
    if o.type != "MESH": continue
    for sl in o.material_slots:
        m_ = sl.material
        bb = next((n for n in m_.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (m_ and m_.use_nodes) else None
        if bb is not None and not bb.inputs["Metallic"].is_linked and bb.inputs["Metallic"].default_value > 0.5: continue
        sl.material = M["knit"]
_ch = import_bk("kreslo_peru", 6.85, 1.85, 0.0, 0, 1.0) + import_bk("kreslo_peru", 6.85, 5.0, 0.0, 180, 1.0)
for o in _ch:
    if o.type != "MESH": continue
    for sl in o.material_slots:
        m_ = sl.material
        bb = next((n for n in m_.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (m_ and m_.use_nodes) else None
        if bb is not None and not bb.inputs["Metallic"].is_linked and bb.inputs["Metallic"].default_value > 0.5: continue
        sl.material = M["knit"]

import_bk("stol_mramor", 7.15, tm, 0.0, 90, 1.10)
import_bk("tyulpany", 7.10, tm - 0.15, 0.47, 0, 0.32, "h")
import_bk("knigi", 7.20, tm + 0.25, 0.47, 20)
import_bk("rastenie_bolshoe", X1 - 0.40, Z0 + 0.55, 0.0, 0, 1.55, "h")

# ---------------- шторы (волна) + тюль из ниши
def drape(name, a0, a1, zc, amp, waves, m):
    bm = bmesh.new(); nu = int((a1 - a0) / 0.02); rows = []
    for j, h in enumerate((0.0, H - 0.02)):
        rows.append([bm.verts.new(W(a0 + (a1 - a0) * i / nu, zc + amp * math.sin(2 * math.pi * waves * i / nu), h)) for i in range(nu + 1)])
    for i in range(nu): bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    so = o.modifiers.new("s", "SOLIDIFY"); so.thickness = 0.006
    for p in o.data.polygons: p.use_smooth = True
drape("Тюль", X0 + 0.03, X1 - 0.03, Z0 + 0.05, 0.025, (X1 - X0) / 0.12, M["tulle"])
drape("Штора лев", X0 + 0.02, WX0 + 0.20, Z0 + 0.11, 0.04, 6, M["curt"])
drape("Штора прав", WX1 - 0.20, X1 - 0.02, Z0 + 0.11, 0.04, 6, M["curt"])

# ---------------- свет
def area(loc, size, energy, rot=(0, 0, 0), color=(1, 0.95, 0.88), sy=None, spread=None):
    lt = bpy.data.lights.new("A", "AREA"); lt.energy = energy; lt.color = color; lt.shape = "RECTANGLE"; lt.size = size; lt.size_y = sy or size
    if spread: lt.spread = math.radians(spread)
    o = bpy.data.objects.new("A", lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
area(W((WX0 + WX1) / 2, Z0 - 0.4, 1.6), WX1 - WX0, 400, rot=(math.radians(-90), 0, 0), sy=WT - WS, color=(0.95, 0.97, 1.0))   # дневной свет в окно
for (x0_, z0_, x1_, z1_) in ((X0 + 0.04, Z0 + 0.2, X0 + 0.04, Z1), (X1 - 0.04, Z0 + 0.2, X1 - 0.04, Z1), (X0, Z1 - 0.04, X1, Z1 - 0.04), (X0, Z0 + 0.21, X1, Z0 + 0.21)):
    L = max(abs(x1_ - x0_), abs(z1_ - z0_)); hz = abs(x1_ - x0_) > abs(z1_ - z0_)
    area(W((x0_ + x1_) / 2, (z0_ + z1_) / 2, HC + 0.02), L if hz else 0.03, 30 * L, sy=0.03 if hz else L, spread=80)
for zz in (1.6, 3.4, 5.2):           # 6 спотов: 2 ряда по 3
    for xx in (X0 + 0.9, X1 - 0.9):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.04, depth=0.004, location=W(xx, zz, HC - 0.002)); bpy.context.active_object.data.materials.append(M["spot"])
        lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = 8; lt.spot_size = math.radians(70); lt.spot_blend = 0.6; lt.color = (1, 0.92, 0.82)
        o = bpy.data.objects.new("Спот", lt); o.location = W(xx, zz, HC - 0.02); sc.collection.objects.link(o)
if TVZ in ("A", "B", "C"):
    for zz in (k0 - 0.006, k1 + 0.006):
        lt = bpy.data.lights.new("LED край", "AREA"); lt.shape = "RECTANGLE"; lt.size = 0.02; lt.size_y = HC - KH - 0.05; lt.energy = 25; lt.color = (1, 0.88, 0.7)
        o = bpy.data.objects.new("LED край", lt); o.location = W(X0 + 0.03, zz, (KH + HC) / 2); o.rotation_euler = (0, math.radians(90), 0); sc.collection.objects.link(o)
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.3

# ---------------- камеры
CAMS = {"1": ("1_ot_dveri_k_oknu", W(X1 - 0.45, Z1 - 0.95, 1.45), W(X0 + 0.9, Z0 + 1.0, 1.05), 16),
        "2": ("2_ot_okna_k_shkafu", W(X0 + 0.9, Z0 + 0.6, 1.45), W(X1 - 0.6, Z1 - 0.4, 1.0), 16),
        "3": ("3_tv_zona", W(X1 - 0.35, tm, 1.30), W(X0, tm, 1.30), 18)}
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
