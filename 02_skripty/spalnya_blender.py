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
X0, X1, Z0, Z1 = 10.232, 14.913, 4.836, 7.516   # 17.11 обмер
H, HC, SL = 2.70, 2.62, 0.08
WZ0, WZ1, WS, WT = 5.618, 7.182, 0.80, 2.40      # окно на правой стене (x = X1)
DZ0, DZ1, DH = 6.716, 7.516, 2.10                   # дверь на левой стене (x = X0)

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
def import_bk(name, cx, cz, h0=0.0, rot_deg=0.0, target=None, axis="w", scl=None, drop=()):
    f = os.path.join(BK, name + ".blend")
    if not os.path.exists(f): print("NO MODEL", name); return []
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [n for n in src.objects]
    objs = [o for o in dst.objects if o is not None and o.type not in ("LIGHT", "CAMERA") and not any(o.name.startswith(d_) for d_ in drop)]
    for o in objs: sc.collection.objects.link(o)
    roots = [o for o in objs if o.parent is None or o.parent not in objs]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    if not pts: return objs
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = {"w": max(mx_.x - mn.x, mx_.y - mn.y), "h": mx_.z - mn.z}[axis]
    k = (target / size) if target else 1.0; ctr = (mn + mx_) / 2
    T_ = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z") @ (Matrix.Diagonal((*scl, 1.0)) if scl else Matrix.Scale(k, 4)) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T_ @ r.matrix_world
    return objs

WALLC = "#" + OPT.get("walls", "BDBBB5"); GRAF = "#" + OPT.get("ward", "2F2F31")
M = dict(wall=tex(mat("Бамбуковые панели серые", WALLC, 0.38), "washed_grey_oak_veneer", 1.6, WALLC, 1.55, 0.7),
         seam=mat("Шов панелей", "#2E2C2A", 0.6), floor=plank_floor(*OPT.get("floor", "5B5B59-555553").split("-")),   # 14.11: пол везде один — дымчатый дуб 7E6A58
         ward=mat("Графит матовый", GRAF, 0.45), frame=mat("Рамки фасадов", "#3A3A3D", 0.45),
         top=mat("Столешница камень", "#E9E6E0", 0.15), brass=mat("Латунь", "#B8925A", 0.25, 1.0),
         ceil=mat("Потолок", "#EEECE7", 0.9), door=mat("Двери", "#E2E0DB", 0.45), black=mat("Чёрный", "#1C1B1A", 0.35, 0.3),
         tv=mat("ТВ", "#0A0A0B", 0.2), wframe=mat("Рама окна", "#F2F1EE", 0.4), glass=mat("Стекло", "#FFFFFF", 0.0, transm=1.0),
         curt=mat("Шторы", "#" + OPT.get("curt", "1E2A44"), 0.95), tulle=mat("Тюль", "#F6F3EE", 0.9, transm=0.5, alpha=0.7),
         led=emis("LED", "#FFE6C8", 6), spot=emis("Спот", "#FFF4E2", 12))
# 13.11.2026 (заказчик): ВСЯ мебель — орех, как в первой гостиной (american walnut, тон #5E4434); вернуть графит: oreh=0
_MB = OPT.get("mebel", "sb")   # 14.11 ВЫБРАН вар.2: фасады слоновая кость, ТВ-тумбы орех   # 14.11: варианты палитр: oreh | dub | white | mushroom | grafit
if _MB == "oreh":
    M["ward"] = tex(mat("Шпон орех (как гостиная)", "#5C4636", 0.45), "american_walnut_veneer", 1.6, "#5E4434", 2.2)
elif _MB == "dub":
    M["ward"] = tex(mat("Шпон дуб светлый", "#C9A87F", 0.45), "washed_grey_oak_veneer", 1.6, "#CBAA80", 2.0)
elif _MB == "dymdub":   # дымчатый дуб — в тон полу «тёплого графита»
    M["ward"] = tex(mat("Шпон дуб дымчатый", "#6A5646", 0.45), "washed_grey_oak_veneer", 1.6, "#6B5747", 1.45)
elif _MB == "umber":    # умбра — тёплый графитово-коричневый матовый
    M["ward"] = mat("Фасады умбра", "#4A4038", 0.5)
elif _MB in ("white", "mushroom", "ivory"):
    M["ward"] = mat("Фасады " + _MB, {"white": "#ECE8E1", "mushroom": "#A89A8A", "ivory": "#E4DCCD"}[_MB], 0.5)
# 17.11.2026 (заказчик): СЕРО-БЕЛАЯ — встроенные шкафы белые, отдельная мебель/тумбы/полки серые, ручки чёрные (своя мебель уже серая)
if _MB == "sb":
    M["ward"] = mat("Фасады серо-белые", "#C9C9C5", 0.5)   # 17.11 (заказчик: «мебель точно серая, как у нас»): единый цвет фасадов всей квартиры
    M["oreh_tv"] = tex(mat("Шпон чёрный орех (ТВ-тумбы)", "#3A2B22", 0.42), "black_walnut_veneer_02", 1.6, "#3B2C23", 2.0)   # 17.11 заказчик: ТВ-тумбы — тёмный орех, как раньше
    if "frame" in M: M["frame"] = mat("Рамки серые", "#7E7D7A", 0.45)
elif _MB != "grafit" and OPT.get("tvoreh", "1") != "1":   # tvoreh=1 — ТВ-тумбы остаются орех
    M["oreh_tv"] = M["ward"]
    if "frame" in M: M["frame"] = mat("Рамки фасадов", "#4A3628" if _MB == "oreh" else "#8C8478", 0.45)
try: M["tulle"].blend_method = "BLEND"
except Exception: pass

# ---------------- коробка комнаты
T = 0.2
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["floor"])
# 14.11 (заказчик): обои «тауп, рогожка» вместо панелей, без швов листов; панели: oboi=0
OBOI = OPT.get("oboi", "rough_linen:8E8E8B")   # 14.11 вар.2: тёплый серый лён
if OBOI and OBOI != "0":
    _t, _c = OBOI.split(":")
    M["wall"] = tex(mat("Обои " + _t, "#" + _c, 0.85), _t, 2.5, "#" + _c, 1.9, 0.6)
else: OBOI = None

# ================= СПАЛЬНЯ 2 — вариант 3 (12.11.2026)
T = 0.2
BC = 12.60                                   # 17.11 обмер: ось кровати (кровать 11.90–13.30, правая тумба до ниши к лоджии)
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["floor"])
LZ0, LZ1, LX0, LX1 = 2.327, 3.545, 13.745, 14.745     # лоджия Б и тамбур (план)
box("Стена верх", X0 - T, Z0 - T, LX0, Z0, 0, H, M["wall"])
box("Тамбур стена лев", LX0 - 0.15, LZ0 - 0.2, LX0, Z0, 0, H, M["wall"]); box("Тамбур стена прав", LX1, LZ0 - 0.2, LX1 + T, Z0, 0, H, M["wall"])
box("Тамбур потолок", LX0 - 0.15, LZ0 - 0.2, LX1 + T, Z0 + SL + 0.01, HC, H + 0.05, M["ceil"])
M["log"] = mat("Лоджия штукатурка", "#D9D6D0", 0.9)
box("Лоджия пол", LX0, LZ0, LX1, Z0, -0.05, 0, M["floor"]); box("Лоджия стена верх", LX0 - 0.15, LZ0 - 0.2, LX1 + T, LZ0, 0, H, M["log"])
for (a0, a1) in ((LX0, 13.89), (14.618, LX1)): box("Простенок двери", a0, LZ1, a1, LZ1 + 0.09, 0, H, M["wall"])
box("Над дверью лоджии", 13.89, LZ1, 14.618, LZ1 + 0.09, 2.10, H, M["wall"])
for (a0, a1) in ((13.89, 13.95), (14.558, 14.618)): box("Рама двери", a0, LZ1 + 0.02, a1, LZ1 + 0.07, 0, 2.10, M["wframe"], 0.003)
box("Рама двери", 13.89, LZ1 + 0.02, 14.618, LZ1 + 0.07, 2.04, 2.10, M["wframe"], 0.003); box("Импост", 13.89, LZ1 + 0.02, 14.618, LZ1 + 0.07, 0.85, 0.91, M["wframe"], 0.003)
box("Стекло двери лоджии", 13.95, LZ1 + 0.04, 14.558, LZ1 + 0.05, 0.0, 2.04, M["glass"])
M["acw2"] = mat("Наружный блок", "#EDEDEA", 0.4)
box("Наружный блок Н3", 13.85, LZ0 + 0.05, 14.65, LZ0 + 0.35, 0.02, 0.57, M["acw2"], 0.01)
box("Стена низ", X0 - T, Z1, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена лев", X0 - T, Z0, X0, DZ0, 0, H, M["wall"]); box("Стена лев2", X0 - T, DZ1, X0, Z1, 0, H, M["wall"]); box("Над дверью", X0 - T, DZ0, X0, DZ1, DH, H, M["wall"])
box("Стена прав", X1, Z0, X1 + T, WZ0, 0, H, M["wall"]); box("Стена прав2", X1, WZ1, X1 + T, Z1, 0, H, M["wall"])
box("Под окном", X1, WZ0, X1 + T, WZ1, 0, WS, M["wall"]); box("Над окном", X1, WZ0, X1 + T, WZ1, WT, H, M["wall"])
box("Перекрытие", X0 - T, Z0 - T, X1 + T, Z1 + T, H, H + 0.05, M["ceil"])
NI = 0.16
box("Потолок", X0 + SL, Z0 + SL, X1 - NI - SL, Z1 - SL, HC, H, M["ceil"]); box("Потолок у прохода", LX0 - 0.15, Z0 - 0.01, X1 - NI - SL, Z0 + SL, HC, H, M["ceil"])
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
    if OBOI: return
    for p in xs: box("Шов", p - 0.008, fixed, p + 0.008, fixed + n_ * 0.0008, 0.08, HC, M["seam"])
def seam_z(fixed, n_, zs):
    if OBOI: return
    for p in zs: box("Шов", fixed, p - 0.008, fixed + n_ * 0.0008, p + 0.008, 0.08, HC, M["seam"])
seam_x(Z1, -1, [x for x in (BC - 0.8 - 1.22, BC - 0.8, BC + 0.8, BC + 0.8 + 1.22) if X0 + 0.15 < x < X1 - 0.15])   # стена ТВ: швы по краям тумбы, за ТВ цельный лист
seam_x(Z0, +1, [x for x in (BC - 1.83, BC - 0.61, BC + 0.61, BC + 1.83) if X0 + 0.65 < x < LX0 - 0.1])   # стена за кроватью: листы 1220 симметрично кровати
seam_z(X1, -1, [])
# 13.11 (по заказчику): стены прохода в лоджию — тоже бамбуковые панели: швы листов + шов в углах
_pm = (LZ1 + 0.09 + Z0) / 2
seam_z(LX0, +1, [_pm, Z0 - 0.008]); seam_z(LX1, -1, [_pm, Z0 - 0.008])
seam_x(LZ1 + 0.09, +1, [LX0 + 0.075, LX1 - 0.07])
for (a, b, c, d) in ((X0 + 0.6, Z0, LX0, Z0 + 0.015), (X0, Z1 - 0.015, X1, Z1), (X1 - 0.015, LZ1 + 0.09, X1, Z1), (X0, Z0 + 1.10, X0 + 0.015, DZ0), (X0, DZ1, X0 + 0.015, Z1), (LX0, LZ1 + 0.09, LX0 + 0.015, Z0)):   # плинтус до углов (12.11)
    box("Плинтус", a, b, c, d, 0, 0.08, M["wall"], 0.002)

# ---------------- стена за кроватью: мягкие вертикальные панели + рамка орех + подсветка
M["soft"] = mat("Мягкие панели серо-бежевые", "#" + OPT.get("soft", "8C8580"), 0.95)
M["walnut"] = tex(mat("Орех", "#5A3E2B", 0.45), "washed_grey_oak_veneer", 2.0, "#6B4A33", 1.4)
HW0, HW1, HH = BC - 1.45, BC + 1.45, 1.30
# (убрано 12.11: мягкие панели на стене) box("Рамка орех", HW0 - 0.04, Z0, HW1 + 0.04, Z0 + 0.03, 0.0, HH + 0.04, M["walnut"], 0.004)
# (убрано 12.11: мягкие панели на стене) npn = 10; pw = (HW1 - HW0) / npn
# (убрано 12.11: мягкие панели на стене) for i in range(npn):
# (убрано 12.11: мягкие панели на стене) a = HW0 + i * pw
# (убрано 12.11: мягкие панели на стене) box("Мягкая панель", a + 0.004, Z0 + 0.03, a + pw - 0.004, Z0 + 0.075, 0.12, HH, M["soft"], 0.02)
# (убрано 12.11: мягкие панели на стене) box("LED над изголовьем", HW0, Z0 + 0.02, HW1, Z0 + 0.03, HH + 0.045, HH + 0.05, M["led"])

# ---------------- кровать 1600 + тумбочки + подвесы
# кровать под заказ (12.11): подиум графит «парящий» с подсветкой, мягкое изголовье со стёжкой, подвесные тумбочки
CUSTOM = OPT.get("bed", "model") == "custom"   # 17.11 (проверка: кровать из коробок пересекалась) — по умолчанию настоящая модель
M["hbf"] = mat("Изголовье ткань графит-серая", "#" + OPT.get("hb", "5E5E62"), 0.95)
M["linen"] = mat("Бельё белое", "#F2F0EC", 0.9); M["duvet"] = mat("Покрывало серое", "#" + OPT.get("duv", "B4B5B3"), 0.95); M["plaid"] = mat("Плед графит", "#3C3C3F", 0.95)
zh = Z0 + 0.005
if CUSTOM:
    box("Подиум", BC - 0.76, zh + 0.02, BC + 0.76, zh + 2.12, 0.10, 0.34, M["ward"], 0.012)
    box("Цоколь", BC - 0.64, zh + 0.12, BC + 0.64, zh + 2.0, 0.0, 0.10, M["black"])
    for (a0, b0, a1, b1) in ((BC - 0.66, zh + 2.0, BC + 0.66, zh + 2.01), (BC - 0.66, zh + 0.12, BC - 0.65, zh + 2.0), (BC + 0.65, zh + 0.12, BC + 0.66, zh + 2.0)):
        box("LED подиума", a0, b0, a1, b1, 0.085, 0.095, M["led"])
    box("Матрас", BC - 0.70, zh + 0.14, BC + 0.70, zh + 2.08, 0.34, 0.56, M["linen"], 0.05)
    box("Покрывало", BC - 0.76, zh + 0.72, BC + 0.76, zh + 2.12, 0.40, 0.60, M["duvet"], 0.05)
    # 13.11 (по заказчику): плед — мягкая ткань: перегиб через край кровати, свес по бокам, складки (сетка + solidify + subsurf)
    def drape(name, cx, z0_, z1_, top, half, drop, m, r=0.045, nu=90, nv=24, amp=0.012):
        Lh = half + math.pi * r / 2 + drop
        bm = bmesh.new(); rows = []
        for j in range(nv + 1):
            zz = z0_ + (z1_ - z0_) * j / nv; row = []
            for i in range(nu + 1):
                u = -Lh + 2 * Lh * i / nu; s = 1 if u >= 0 else -1; a = abs(u)
                if a <= half: x, h = a, top
                elif a <= half + math.pi * r / 2:
                    t = (a - half) / r; x, h = half + r * math.sin(t), top - r + r * math.cos(t)
                else: x, h = half + r + 0.01 * (a - half - math.pi * r / 2) / drop, top - r - (a - half - math.pi * r / 2)
                w_ = amp * (math.sin(zz * 41 + u * 7) * 0.6 + math.sin(zz * 17 - u * 13) * 0.4)
                if a > half: x += w_ * 0.8
                else: h += w_ * 0.35
                row.append(bm.verts.new(W(cx + s * x, zz, h)))
            rows.append(row)
        for j in range(nv):
            for i in range(nu): bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
        sd = o.modifiers.new("t", "SOLIDIFY"); sd.thickness = 0.006
        ss = o.modifiers.new("s", "SUBSURF"); ss.levels = 1; ss.render_levels = 2
        for p in o.data.polygons: p.use_smooth = True
        return o
    drape("Плед", BC, zh + 1.60, zh + 2.02, 0.606, 0.762, 0.24, M["plaid"])
    def _pillow(fn, cx, cz, h0, w, tilt, mm, rot=0.0):
        objs = import_bk(fn, cx, cz, h0, rot, w)
        p = W(cx, cz, h0)
        R_ = Matrix.Translation(p) @ Matrix.Rotation(math.radians(tilt), 4, "X") @ Matrix.Translation(-p)
        for o_ in objs:
            if o_.parent is None or o_.parent not in objs: o_.matrix_world = R_ @ o_.matrix_world
            if o_.type == "MESH":
                for i_ in range(len(o_.data.materials)): o_.data.materials[i_] = mm
                if not o_.data.materials: o_.data.materials.append(mm)
    for xx in (BC - 0.36, BC + 0.36):            # спальные 50×70, наклонены к изголовью
        _pillow("podushka_spalnaya", xx, zh + 0.36, 0.50, 0.70, -28, M["linen"])
    for xx in (BC - 0.24, BC + 0.24):            # декоративные 45×45, серые
        _pillow("podushka_dekor", xx, zh + 0.58, 0.55, 0.48, -18, M["plaid"])
    nch = 8; cw = 1.60 / nch
    for i in range(nch):
        a = BC - 0.80 + i * cw
        # 13.11 (по заказчику): мягкие «пухлые» каналы — овальное сечение, скруглённый верх, глубокие швы между ними
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=cw / 2 - 0.003, depth=0.95, location=W(a + cw / 2, zh + 0.075, 0.775))
        ch = bpy.context.active_object; ch.name = "Изголовье канал"; ch.scale = (1, 0.055 / (cw / 2 - 0.003), 1); ch.data.materials.append(M["hbf"])
        bv = ch.modifiers.new("b", "BEVEL"); bv.width = 0.045; bv.segments = 8; bv.limit_method = "ANGLE"
        ch.modifiers.new("s", "SUBSURF").levels = 1
        for pp in ch.data.polygons: pp.use_smooth = True
    box("Изголовье основа", BC - 0.80, zh, BC + 0.80, zh + 0.07, 0.30, 1.24, M["hbf"], 0.01)
    box("LED за изголовьем", BC - 0.78, zh, BC + 0.78, zh + 0.01, 1.255, 1.26, M["led"])
    for xx in (BC - 1.025, BC + 1.025):          # подвесные тумбочки графит 350
        box("Тумбочка подвесная", xx - 0.175, Z0 + 0.005, xx + 0.175, Z0 + 0.40, 0.40, 0.62, M["ward"], 0.006)
        box("Шов ящика", xx - 0.175, Z0 + 0.399, xx + 0.175, Z0 + 0.402, 0.508, 0.512, M["black"])
        box("Ручка", xx - 0.07, Z0 + 0.40, xx + 0.07, Z0 + 0.415, 0.555, 0.565, M["black"], 0.003)
        box("LED под тумбочкой", xx - 0.15, Z0 + 0.03, xx + 0.15, Z0 + 0.37, 0.394, 0.398, M["led"])
else:
  # 18.11 (выбор заказчика: кровать 3 — серая бокс-спринг, матрас 1400×2000 — модель сужена по ширине 0,86, длина как есть)
  _bed = import_bk("krovat_boxspring", BC, Z0 + 0.02 + 1.155, 0.0, 0, scl=(0.86, 1.0, 1.0))
  bpy.context.view_layer.update()
  for _o in _bed:   # покрывало — по ширине кровати (+4 см), чтобы не закрывало тумбочки
      if _o.name.startswith("BedCover"): _o.matrix_world = Matrix.Translation(W(BC, 0, 0)) @ Matrix.Diagonal((0.86, 1.0, 1.0, 1.0)) @ Matrix.Translation(-W(BC, 0, 0)) @ _o.matrix_world
  for (xx, rot) in ((BC - 0.955, 180), (BC + 0.955, 180)):   # тумбочки 1 (белые с ящиками, как были)
    for _o in import_bk("tumbochka_noir", xx, Z0 + 0.24, 0.0, 0, scl=(0.71, 0.85, 1.25)):   # 18.11 заказчик: «с обеих сторон шкафчики» — 450×400, h≈570, вровень с матрасом:
        if _o.type != "MESH": continue
        for _sl in _o.material_slots:
            _m = _sl.material; _b = next((n for n in _m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (_m and _m.use_nodes) else None
            if _b is not None and not _b.inputs["Metallic"].is_linked and _b.inputs["Metallic"].default_value > 0.5: _sl.material = M["black"]; continue
            _sl.material = M["ward"]
for xx in (BC - 0.955, BC + 0.955):   # 18.11 (выбор заказчика: свет 5 — тонкий подвес чёрный с золотом), низ h=1,10 над тумбочкой
    _pv = import_bk("podves_cherny_zoloto", xx, Z0 + 0.25, 1.10, 0, H - 1.10, "h")
    _pc = W(xx, Z0 + 0.25, (1.10 + H) / 2); _fl = Matrix.Translation(_pc) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation(-_pc)
    for _o in _pv:   # 18.11 (заказчик: «висят вверх»): в модели чашка внизу — переворачиваем: чашка к потолку, плафон вниз
        if _o.parent is None or _o.parent not in _pv: _o.matrix_world = _fl @ _o.matrix_world
    lt = bpy.data.lights.new("Подвес", "POINT"); lt.energy = 6; lt.color = (1, 0.85, 0.65); lt.shadow_soft_size = 0.03
    o = bpy.data.objects.new("Подвес", lt); o.location = W(xx, Z0 + 0.25, 1.06); sc.collection.objects.link(o)

# ---------------- встроенный шкаф графит (левая стена, до потолка)
b0, b1, wx = Z0, Z0 + 1.10, X0 + 0.60           # 17.11 заказчик: шкаф 1100 у верхнего угла; дверь — в торце коридора
box("Шкаф", X0, b0, wx, b1, 0, HC, M["ward"])
n = 4; w = (b1 - b0) / n
for k in range(n):
    u0, u1 = b0 + k * w + 0.07, b0 + (k + 1) * w - 0.07
    if k: box("Шов", wx, b0 + k * w - 0.0015, wx + 0.002, b0 + k * w + 0.0015, 0.02, HC - 0.02, M["black"])
    hz = b0 + (k + 1) * w - 0.05 if k % 2 == 0 else b0 + k * w + 0.05
    box("Ручка чёрная", wx + 0.012, hz - 0.008, wx + 0.035, hz + 0.008, 0.70, 1.55, M["black"], 0.004)

# ---------------- дверь (левая стена)
xf = X0 - 0.05
box("Полотно", xf - 0.02, DZ0 + 0.03, xf + 0.02, DZ1 - 0.03, 0, DH - 0.03, M["door"], 0.003)
for (a, b) in ((DZ0, DZ0 + 0.03), (DZ1 - 0.03, DZ1)): box("Рамка", xf - 0.03, a, xf + 0.03, b, 0, DH, M["black"], 0.002)
box("Рамка", xf - 0.03, DZ0, xf + 0.03, DZ1, DH - 0.03, DH, M["black"], 0.002)
box("Ручка", xf + 0.02, DZ1 - 0.10, xf + 0.07, DZ1 - 0.09, 1.0, 1.02, M["black"]); box("Ручка", xf + 0.055, DZ1 - 0.22, xf + 0.07, DZ1 - 0.09, 1.0, 1.02, M["black"])   # петли у шкафа, ручка у угла — дверь открывается к ТВ-стене


def oreh_tv_unit(a0, a1, wall_x=None, wall_z=None, D=0.40, UH=0.30, ndoors=6, name="ТВ-тумба орех"):
    """13.11.2026 (заказчик: «везде, где телевизор — такой стиль»): низкая тумба h300 как в гостиной — рифлёный шпон ореха,
    дверцы, латунные ручки-планки. wall_x — тумба у стены x=const (вдоль z от a0 до a1), wall_z — у стены z=const (вдоль x)."""
    if "oreh_tv" not in M: M["oreh_tv"] = tex(mat("Шпон орех (как гостиная)", "#5C4636", 0.45), "american_walnut_veneer", 1.6, "#5E4434", 2.2)
    if "brass" not in M: M["brass"] = mat("Латунь", "#B8925A", 0.25, metal=1.0)
    m = M["oreh_tv"]
    def bx(n, p0, p1, d0, d1, h0, h1, mm, bev=0.0):     # p — вдоль стены, d — от стены
        if wall_x is not None:
            sg = 1 if wall_x < 5.0 + 999 and d1 >= 0 else 1
            box(n, wall_x + d0 * WS_, p0, wall_x + d1 * WS_, p1, h0, h1, mm, bev) if WS_ > 0 else box(n, wall_x + d1 * WS_, p0, wall_x + d0 * WS_, p1, h0, h1, mm, bev)
        else:
            box(n, p0, wall_z + d0 * WS_, p1, wall_z + d1 * WS_, h0, h1, mm, bev) if WS_ > 0 else box(n, p0, wall_z + d1 * WS_, p1, wall_z + d0 * WS_, h0, h1, mm, bev)
    bx(name + " корпус", a0, a1, 0, D - 0.02, 0.0, UH, m)
    p = a0 + 0.01
    while p < a1 - 0.02:
        bx(name + " рифление", p, p + 0.02, D - 0.02, D, 0.01, UH - 0.005, m, 0.006); p += 0.03
    bx(name + " крышка", a0 - 0.005, a1 + 0.005, 0, D + 0.005, UH, UH + 0.02, m, 0.003)
    dw = (a1 - a0) / ndoors
    for k in range(ndoors):
        c = a0 + (k + 0.5) * dw
        if k: bx(name + " шов", a0 + k * dw - 0.002, a0 + k * dw + 0.002, D - 0.001, D + 0.001, 0.01, UH - 0.005, M["black"])
        bx(name + " ручка латунь", c - min(0.13, dw * 0.35), c + min(0.13, dw * 0.35), D + 0.002, D + 0.016, UH - 0.06, UH - 0.048, M["brass"], 0.004)
WS_ = 1
# ---------------- ТВ напротив кровати: 13.11 — низкая рифлёная тумба орех h300 (как в гостиной) + ТВ 55"
t0, t1 = BC - 0.70, BC + 0.70                # 17.11 обмер: тумба ПОДВЕСНАЯ 1400×300 (комната 2680 — у пола свободно)
ORT = OPT.get("orehtv", "0") == "1"
if ORT:
    WS_ = -1; oreh_tv_unit(t0, t1, wall_z=Z1, ndoors=4)
else:
    box("ТВ-тумба", t0, Z1 - 0.30, t1, Z1, 0.30, 0.62, M["oreh_tv"] if "oreh_tv" in M else M["ward"]); box("Столешница", t0 - 0.01, Z1 - 0.31, t1 + 0.01, Z1, 0.62, 0.645, M["top"], 0.003)
for k in (range(2) if not ORT else ()):
    u0, u1 = t0 + k * 0.7 + 0.003, t0 + (k + 1) * 0.7 - 0.003
    box("Фасад", u0, Z1 - 0.32, u1, Z1 - 0.30, 0.305, 0.615, M["oreh_tv"] if "oreh_tv" in M else M["ward"], 0.002)
    box("Ручка", (u0 + u1) / 2 - 0.1, Z1 - 0.335, (u0 + u1) / 2 + 0.1, Z1 - 0.32, 0.55, 0.562, M["black"], 0.003)
box("ТВ 55", BC - 0.62, Z1 - 0.045, BC + 0.62, Z1 - 0.01, 1.0, 1.70, M["tv"], 0.004)

# ---------------- туалетный столик с зеркалом (угол у окна) + пуф + растение
# 18.11 (выбор заказчика: столик 2 — орех с круглым зеркалом LED, сужен до 800; пуф 2 — мех)
import_bk("stolik_oreh_zerkalo", 14.15, Z1 - 0.265, 0.0, 180, scl=(0.82, 1.0, 1.0), drop=("Cylinder.001",))
import_bk("puf_meh", 14.15, Z1 - 0.75, 0.0, 0, 0.44)
# растение убрано 12.11 по просьбе заказчика
# большое зеркало в пол с LED-подсветкой (правая стена под кондиционером), 800×1850
def rmirror(name, z0, z1, h0, h1, x, r, m, dep):
    bpy.ops.mesh.primitive_plane_add(size=1); o = bpy.context.active_object; o.name = name
    o.scale = (z1 - z0, h1 - h0, 1); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.affect = "VERTICES"; md.width = r; md.segments = 12
    o.modifiers.new("s", "SOLIDIFY").thickness = dep
    o.rotation_euler = (math.radians(90), 0, math.radians(90)); o.location = W(x, (z0 + z1) / 2, (h0 + h1) / 2)
    o.data.materials.append(m); return o
MZ0, MZ1 = 4.86, 5.56                        # 17.11 обмер: между углом и окном
rmirror("Подсветка зеркала", MZ0 - 0.015, MZ1 + 0.015, 0.115, 2.015, X1 - 0.02, 0.003, M["led"], 0.004)
rmirror("Зеркало в пол", MZ0, MZ1, 0.13, 2.0, X1 - 0.03, 0.002, mat("Зеркало", "#E3E7E8", 0.02, 1.0), 0.01)
area(W(X1 - 0.05, (MZ0 + MZ1) / 2, 1.07), 0.02, 12, rot=(0, math.radians(-90), 0), sy=1.8) if False else None

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
ac_unit(("B", Z1), 14.15, 2.54, flip="acflip" in ARGS)   # 17.11 обмер: К3 над туалетным столиком (правая стена занята зеркалом/окном)
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
# (убрано 12.11: мягкие панели на стене) area(W(BC, Z0 + 0.06, HH + 0.06), HW1 - HW0, 15, sy=0.02, color=(1, 0.86, 0.66))
for xx in (11.515, 13.30):                    # 4 круглых спота (план света: 2×2)
    for zz in (5.393, 6.425):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.045, depth=0.004, location=W(xx, zz, HC - 0.002)); bpy.context.active_object.data.materials.append(M["spot"])
        bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.006, location=W(xx, zz, HC - 0.003)); bpy.context.active_object.data.materials.append(M["black"])
        lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = 10; lt.spot_size = math.radians(70); lt.spot_blend = 0.6; lt.color = (1, 0.92, 0.82)
        o = bpy.data.objects.new("Спот", lt); o.location = W(xx, zz, HC - 0.02); sc.collection.objects.link(o)
area(W((LX0 + LX1) / 2, (LZ1 + Z0) / 2, HC - 0.05), 0.6, 25, sy=0.5)          # свет в тамбуре
area(W((LX0 + LX1) / 2, (LZ0 + LZ1) / 2, H - 0.1), 0.6, 30, sy=0.6)           # свет в лоджии
box("Торец стены у прохода", LX0 - 0.15, Z0 - 0.2, LX0 + 0.01, Z0 + 0.01, 0, HC, M["wall"])
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.3

# 17.11 обмер: бетонная балка по линии Г, 2,52 м от стены с дверью; низ — по замеру потолка (пока 2,52 от пола)
box("Балка", 12.752, Z0, 13.102, Z1, float(OPT.get("beam", "2.52")), HC + 0.01, M["ceil"])

# ---------------- камеры
exec(open(os.path.join(PROJ, "02_skripty", "decor_common.py"), encoding="utf-8").read())   # 17.11: декор (decor=0 — без него)
CAMS = {"1": ("1_ot_dveri_k_krovati", W(10.95, 7.25, 1.50), W(13.4, 4.4, 1.0), 15),
        "2": ("2_ot_okna_k_shkafu", W(14.35, 4.75, 1.50), W(10.5, 7.1, 1.05), 15),
        "3": ("3_krovat_pryamo", W(BC, 7.35, 1.45), W(BC, Z0, 1.0), 16),
        "4": ("4_prohod_v_lodzhiyu", W(12.9, 7.2, 1.5), W(14.25, 3.0, 1.1), 18)}
# 18.11: полные вертикальные кадры пол–потолок: 4 стены (v1–v4), 4 угла (v5–v8)
CAMS.update({"v1": ("v1_izgolove", W(BC, Z1 - 0.10, 1.3), W(BC, Z0, 1.3), 15),
             "v2": ("v2_tv_stena", W(BC, Z0 + 0.30, 1.3), W(BC, Z1, 1.3), 15),
             "v3": ("v3_shkaf_dver", W(X1 - 0.55, 6.30, 1.3), W(X0, 6.30, 1.3), 15),
             "v4": ("v4_okno_stolik", W(X0 + 0.15, 6.60, 1.3), W(X1, 6.60, 1.3), 15),
             "v5": ("v5_ugol_shkaf", W(13.55, Z1 - 0.70, 1.3), W(X0, Z0, 1.3), 15),
             "v6": ("v6_ugol_lodzhiya", W(X0 + 0.75, Z1 - 0.25, 1.3), W(X1, Z0, 1.3), 15),
             "v7": ("v7_ugol_dver", W(X1 - 0.25, Z0 + 0.30, 1.3), W(X0, Z1, 1.3), 15),
             "v8": ("v8_ugol_stolik", W(X0 + 0.75, Z0 + 1.30, 1.3), W(X1, Z1, 1.3), 15)})

sc.render.engine = "CYCLES"
# 17.11: ИНСТРУМЕНТ ПРОВЕРКИ (аргумент qa): выгрузить сцену для qa_check.py и выйти без рендера
if "qa" in ARGS:
    PROJ = globals().get("PROJ") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exec(open(os.path.join(PROJ, "02_skripty", "qa_dump.py"), encoding="utf-8").read()); import sys as _s; _s.exit(0)
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
# ---- 14.11: БЫСТРЫЙ ПРОСМОТР (аргумент fast): EEVEE, 1280×720, файлы q_*.jpg — финал (Cycles) не перезаписывается
if "fast" in ARGS:
    for _e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try: sc.render.engine = _e; break
        except Exception: pass
    try:
        _ee = sc.eevee; _ee.taa_render_samples = 32
        for _a, _v in (("use_raytracing", True), ("use_shadows", True), ("use_gtao", True), ("use_bloom", True)):
            if hasattr(_ee, _a): setattr(_ee, _a, _v)
    except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720; QUICK = True
    sc.view_settings.exposure = sc.view_settings.exposure + 0.7   # EEVEE без полного отражённого света — темнее Cycles
# ---- 14.11: РЕАЛИЗМ (аргумент real): фаски на всех мебельных деталях, небо HDRI в окне, долгий расчёт, ровная камера 24 мм
if "real" in ARGS:
    for _o in [o for o in sc.objects if o.type == "MESH" and len(o.data.vertices) <= 24 and not o.name.startswith(("Пол", "Стена", "Потолок", "Окно", "Над", "Под", "Стекло"))]:
        _d = max(_o.dimensions); 
        if _d < 0.01: continue
        _b = _o.modifiers.new("fаска", "BEVEL"); _b.width = min(0.004, min(x for x in _o.dimensions if x > 0) * 0.3); _b.segments = 2; _b.limit_method = "ANGLE"
    _hd = os.path.join(PROJ, "03_materialy", "hdri", "sky.hdr")
    if os.path.exists(_hd):
        _w = sc.world or bpy.data.worlds.new("W"); sc.world = _w; _w.use_nodes = True; _nt = _w.node_tree
        _bg = _nt.nodes.get("Background") or _nt.nodes.new("ShaderNodeBackground"); _env = _nt.nodes.new("ShaderNodeTexEnvironment")
        _env.image = bpy.data.images.load(_hd, check_existing=True); _nt.links.new(_env.outputs["Color"], _bg.inputs["Color"]); _bg.inputs["Strength"].default_value = 1.0
    sc.cycles.samples = int(OPT.get("samples", "700")); sc.cycles.adaptive_threshold = 0.01
    sc.cycles.max_bounces = 12; sc.cycles.diffuse_bounces = 6; sc.cycles.glossy_bounces = 6; sc.cycles.sample_clamp_indirect = 8
    try: sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    if OPT.get("plus", "1") == "1":   # 14.11: IES, порталы окон, шторы со складками, потёртости (real_plus.py)
        exec(open(os.path.join(PROJ, "02_skripty", "real_plus.py"), encoding="utf-8").read())
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080; QUICK = False; tag = tag if "tag" in OPT else "_real"
# ---- 17.11 (заказчик: «ничего не видно — где что, какой пол»): кадр 0 — ОБЩИЙ ВИД СВЕРХУ без потолка, вертикальный (телефон)
if "0" in SHOTS and "0" not in CAMS:
    _cx = (X0 + X1) / 2; _L = Z1 - Z0
    CAMS["0"] = (("open_" if globals().get("OPENC") else "") + "0_obshiy_sverhu", W(_cx, Z1 - 0.10 * _L, HC + 2.4), W(_cx, Z0 + 0.40 * _L, 0.0), 24)   # с нижнего торца: верх кадра = верх плана, как на чертеже
_RES0 = (sc.render.resolution_x, sc.render.resolution_y)
for s_ in SHOTS:
    if s_ not in CAMS: continue
    _top = (s_ == "0")
    for _o in sc.objects:
        if _o.type == "MESH" and ("потол" in _o.name.lower() or _o.name.startswith("Перекрытие")): _o.hide_render = _top
    if _top:
        if not bpy.data.objects.get("Свет сверху"):
            _ld = bpy.data.lights.new("Свет сверху", "AREA"); _ld.energy = 60 * (X1 - X0) * (Z1 - Z0); _ld.size = max(X1 - X0, Z1 - Z0); _ld.color = (1.0, 0.97, 0.92)
            _lo = bpy.data.objects.new("Свет сверху", _ld); _lo.location = W((X0 + X1) / 2, (Z0 + Z1) / 2, HC + 1.2); sc.collection.objects.link(_lo)
        bpy.data.objects["Свет сверху"].hide_render = False
        sc.render.resolution_x, sc.render.resolution_y = 1200, 1600
        if not globals().get("_EXP0_SET"): _EXP0 = sc.view_settings.exposure; _EXP0_SET = True
        sc.view_settings.exposure = _EXP0 + float(OPT.get("topexp", "-1.6"))     # без потолка света больше — экспозиция ниже, плитка остаётся графитом
        if sc.world and sc.world.use_nodes:
            for _n in sc.world.node_tree.nodes:
                if _n.type == "BACKGROUND": _n.inputs[1].default_value = 0.15   # фон вокруг комнаты тёмный, не голубое небо
    else:
        if bpy.data.objects.get("Свет сверху"): bpy.data.objects["Свет сверху"].hide_render = True
        if globals().get("_EXP0_SET"): sc.view_settings.exposure = _EXP0
        sc.render.resolution_x, sc.render.resolution_y = _RES0
    n_, loc, tgt, lens = CAMS[s_]
    cd = bpy.data.cameras.new(n_); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02
    co = bpy.data.objects.new(n_, cd); co.location = loc; co.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(co)
    if "real" in ARGS and not _top:     # ровная камера (вертикали вертикальны), объектив ~22–24 мм, вверх/вниз — сдвигом
        _dv = tgt - loc; _hd2 = math.hypot(_dv.x, _dv.y); co.rotation_euler = (math.radians(90), 0, math.atan2(_dv.y, _dv.x) - math.radians(90))
        cd.lens = max(lens, float(OPT.get("lensmin", "17")))   # 17.11: без сверхширокого искажения (13 мм растягивал предметы)
        cd.shift_y = max(-0.3, min(0.3, (_dv.z / max(_hd2, 0.3)) * cd.lens / 36 * 0.85))
        if s_.startswith("v"):   # 17.11 (заказчик: «как с телефона — вся стена сверху донизу, пол и потолок»): вертикальный кадр 9:16,
            _hc_ = globals().get("HC", 2.65)          # камера ровно на середине высоты, объектив — чтобы пол и потолок у дальней стены влезли
            co.location.z = _hc_ / 2; cd.shift_y = 0.0; cd.sensor_fit = "VERTICAL"; cd.sensor_height = 36
            cd.lens = max(11.0, 18.0 * _hd2 / (_hc_ / 2 + 0.60))   # 18.11 (заказчик: «всё от верха до низу»): запас 60 см — пол и потолок целиком в кадре
            if s_ in ("v1", "v2"): cd.lens = min(cd.lens, 16.0)   # 18.11: кровать с тумбочками с обеих сторон целиком
            sc.render.resolution_x, sc.render.resolution_y = (1620, 2880) if OPT.get("print", "0") == "1" else (1080, 1920)   # print=1 — для печати альбома (½ A4 при 300 dpi)
            if OPT.get("print", "0") == "1":
                sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01; sc.cycles.use_denoising = True
                sc.render.image_settings.quality = 95
    sc.camera = co; sc.render.filepath = os.path.join(OUT, ("q_" if QUICK else "") + n_ + tag + ".jpg"); bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
# ---- 17.11: РАЗВЕРТКИ как у SM (аргумент elev): ортогональный вид на каждую стену из 3D — для листов разверток;
#      elev ewalls=T,R,B,L edepth=1.2 (сколько метров перед стеной видно) esamples=96 shots=0 → OUT/elev_<стена>.jpg
if "elev" in ARGS:
    _hc = globals().get("HC", 2.65); sc.view_settings.exposure += float(OPT.get("eexp", "1.0")); sc.render.engine = "CYCLES"; sc.cycles.samples = int(OPT.get("esamples", "96")); sc.cycles.use_denoising = True
    for _w in OPT.get("ewalls", "T,R,B,L").split(","):
        _L = (X1 - X0) if _w in "TB" else (Z1 - Z0); _dep = (Z1 - Z0) if _w in "TB" else (X1 - X0)
        _cx, _cz = (X0 + X1) / 2, (Z0 + Z1) / 2
        _pos = {"T": (_cx, Z1 - 0.03), "B": (_cx, Z0 + 0.03), "L": (X1 - 0.03, _cz), "R": (X0 + 0.03, _cz)}[_w]
        _rz = {"T": 0, "B": 180, "L": 90, "R": -90}[_w]
        cd = bpy.data.cameras.new("elev_" + _w); cd.type = "ORTHO"; cd.ortho_scale = max(_L, _hc)
        cd.clip_start = max(0.01, _dep - 0.03 - float(OPT.get("edepth", "1.2"))); cd.clip_end = _dep + 0.2
        co = bpy.data.objects.new("elev_" + _w, cd); co.location = W(_pos[0], _pos[1], _hc / 2)
        co.rotation_euler = (math.radians(90), 0, math.radians(_rz)); sc.collection.objects.link(co)
        _rx = 1800; sc.render.resolution_x = _rx; sc.render.resolution_y = int(_rx * _hc / _L) if _L >= _hc else _rx
        if _L < _hc: sc.render.resolution_x = int(_rx * _L / _hc)
        sc.camera = co; sc.render.filepath = os.path.join(OUT, "elev_" + _w + ".jpg"); bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)
