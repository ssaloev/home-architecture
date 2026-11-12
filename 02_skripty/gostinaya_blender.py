# -*- coding: utf-8 -*-
"""Гостиная — 3D-сцена и ракурсы по СОГЛАСОВАННЫМ решениям (11.2026).
Запуск без окна:  blender -b --factory-startup -P gostinaya_blender.py -- [quick] [shots=1,2]
Размеры комнаты, окна, двери, мебель — из data/kvartira.json.
Согласовано: стены NCS S 1002-Y + молдинги в тон; пол — палубная доска, беленый дуб 2 тона через раз,
поперёк комнаты; без люстры: скрытый LED по периметру + световая рамка 0,6 от стен + 2 бра-шара;
диван 2400 округлый букле + 2 кресла «буквой П», стол овал 1200×700 мрамор на тёмном основании;
ТВ-тумба подвесная в цвет стен, ТВ в рамке молдинга; шторы тюль + плотные в нише; ковёр молочный.
"""
import bpy, bmesh, math, os, sys, json
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "quick" in ARGS
KREM = "krem" in ARGS
OPTC = dict(a.split("=", 1) for a in ARGS if a.startswith(("tumba=", "tumbaf=", "tumbatex=")))
GREYW = "greywalls" in ARGS    # 12.11: стены — серые бамбуковые панели (фактура шпона, сатин), как в коридоре          # 12.11.2026: стиль заказчика — крем + дуб + латунь, встроенная мебель
SHOTS = None
VARIANTS = None; VAR = "A"; SOFA = None; CHAIR = None; CEIL = 0; NIGHT = False; FL = None; PLANK = (1.2, 0.15); TAG = ""; WMODE = None; W2 = "#C2BDB3"
for a in ARGS:
    if a.startswith("shots="): SHOTS = [int(v) for v in a[6:].split(",")]
    if a.startswith("var="): VAR = a[4:]
    if a.startswith("sofa="): SOFA = "#" + a[5:]
    if a.startswith("chair="): CHAIR = "#" + a[6:]
    if a.startswith("floor="): FL = a[6:].split("-")            # светлый-тёмный hex
    if a.startswith("plank="): PLANK = tuple(float(v) for v in a[6:].split("x"))
    if a.startswith("tag="): TAG = a[4:]
    if a.startswith("ceil="): CEIL = int(a[5:])
    if a == "night": NIGHT = True
    if a.startswith("variants="): VARIANTS = a[9:]
    if a.startswith("walls="): WMODE, W2 = a[6:].split(":")[0], "#" + a[6:].split(":")[1]
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "08_vizualizacii", "gostinaya")
os.makedirs(OUT, exist_ok=True)

R = next(r for r in D["rooms"] if r["name"] == "Гостиная")
X0, X1, Z0, Z1 = R["rects"][0]
H = D["meta"]["ceiling_h"]
WIN = next(w for w in D["windows"] if w["rect"][0] < X1 and w["rect"][0] + w["rect"][2] > X0 and w["rect"][1] < Z0 + 0.1)
WX0, WX1 = WIN["rect"][0], WIN["rect"][0] + WIN["rect"][2]; WS, WT = WIN["sill"], WIN["top"]
DOOR = next(d for d in D["doors"] if d["name"] == "в гостиную")
DX0, DX1, DH = DOOR["rect"][0], DOOR["rect"][0] + DOOR["rect"][2], DOOR["h"]
FURN = [f for f in D["furniture"] if X0 - 0.05 <= f["x"] <= X1 and Z0 - 0.05 <= f["z"] <= Z1]
def F(prefix): return [f for f in FURN if f["name"].startswith(prefix)]
L = R["lights"]; FO = L.get("frame_off", 0.6)

# ---------------------------------------------------------------- сцена
for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images):
    for b in list(coll):
        try: coll.remove(b)
        except Exception: pass
sc = bpy.context.scene

def W(x, z, h): return Vector((x, -z, h))            # план (x вправо, z вниз) -> Blender

def hexlin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c) + (1.0,)

def inp(n, *names):
    for k in names:
        if k in n.inputs: return n.inputs[k]
    return None

def mat(name, color, rough=0.5, metal=0.0, coat=0.0, bump=0.0, bscale=200.0, sheen=0.0, transm=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexlin(color) if isinstance(color, str) else color
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if coat and inp(b, "Coat Weight", "Clearcoat"): inp(b, "Coat Weight", "Clearcoat").default_value = coat
    if sheen and inp(b, "Sheen Weight", "Sheen"): inp(b, "Sheen Weight", "Sheen").default_value = sheen
    if transm and inp(b, "Transmission Weight", "Transmission"): inp(b, "Transmission Weight", "Transmission").default_value = transm
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    if bump:
        tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = bscale
        if "Detail" in tx.inputs: tx.inputs["Detail"].default_value = 8
        bn = nt.nodes.new("ShaderNodeBump"); bn.inputs["Strength"].default_value = bump
        nt.links.new(tx.outputs["Fac"], bn.inputs["Height"]); nt.links.new(bn.outputs["Normal"], b.inputs["Normal"])
    return m

def emit(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = hexlin(color); e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o.inputs[0]); return m

def marble(name):
    m = mat(name, "#F2F0EC", rough=0.12, coat=0.6); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 2.5
    if "Detail" in n1.inputs: n1.inputs["Detail"].default_value = 12
    if "Distortion" in n1.inputs: n1.inputs["Distortion"].default_value = 6
    nt.links.new(tc.outputs["Object"], n1.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 1.6
    if "Distortion" in wv.inputs: wv.inputs["Distortion"].default_value = 9
    nt.links.new(n1.outputs["Color"], wv.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = hexlin("#8E8E8C"); el[1].position = 0.12; el[1].color = hexlin("#F3F1ED")
    nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    return m

def floor_mat():
    """Палубная доска 1200×150 поперёк комнаты, 2 тона через раз (беленый дуб «почти как стены»)."""
    PL, PW = PLANK; OFFS = [0, 160, 80, 200, 40, 120, 220, 100]; PH = [0, 1, 1, 0, 1, 0, 0, 1]
    tw, th = 2 * PL, 8 * PW; nx, ny = 2048, 1024
    xs = (np.arange(nx) + 0.5) / nx * tw; ys = (np.arange(ny) + 0.5) / ny * th
    XX, YY = np.meshgrid(xs, ys)
    row = (YY // PW).astype(int) % 8
    off = np.array(OFFS)[row] / 240 * PL
    u = (XX - off) % tw; k = (u // PL).astype(int); ph = np.array(PH)[row]
    tone = (k + ph) % 2
    A, B = (np.array([0xEC, 0xE7, 0xDE]) / 255, np.array([0xDC, 0xD4, 0xC5]) / 255) if VAR != "C" else (np.array([0xE8, 0xDF, 0xCE]) / 255, np.array([0xD3, 0xC3, 0xAA]) / 255)
    if FL: A, B = (np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)]) / 255 for c in FL)
    col = np.where(tone[..., None] == 0, A, B)
    rng = np.random.default_rng(7)
    pid = row * 4 + k                                     # своя «доска» -> лёгкая разнотонность и волокна
    jit = rng.normal(0, 0.012, 64)[pid % 64][..., None]
    grain = (np.sin((XX * 40 / PL * 1.2 + np.sin(YY * 90 + pid) * 0.6) * (6 + (pid % 5))) * 0.012)[..., None]
    col = col + jit + grain
    seamx = (np.minimum(u % PL, PL - u % PL) < 0.0012); seamy = (np.minimum(YY % PW, PW - YY % PW) < 0.0010)
    col[seamx | seamy] *= 0.86
    col = np.clip(col, 0, 1) ** 2.2
    global FLOOR_IMG
    img = bpy.data.images.new("пол_палуба", nx, ny, alpha=False); FLOOR_IMG = img
    px = np.ones((ny, nx, 4), np.float32); px[..., :3] = col
    img.pixels.foreach_set(px.ravel()); img.pack()
    m = mat("Пол — беленый дуб", "#ECE7DE", rough=0.42, coat=0.15); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Cubic"
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / tw, 1 / th, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], t.inputs["Vector"])
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m

PH = os.path.join(os.path.dirname(HERE), "03_materialy", "polyhaven")
def _img(path, color=True):
    im = bpy.data.images.load(path, check_existing=True)
    if not color: im.colorspace_settings.name = "Non-Color"
    return im
def pbr(m, tex, scale, tint=None, use_diff=False, nstr=1.0, rough_mul=1.0):
    """Готовые текстуры Poly Haven: нормаль + шероховатость (+ диффуз, или его яркость × наш цвет)."""
    d = os.path.join(PH, tex)
    if not os.path.isdir(d): return m
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    def T(fn, col):
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = _img(os.path.join(d, fn), col); t.projection = "BOX"; t.projection_blend = 0.3
        nt.links.new(mp.outputs[0], t.inputs["Vector"]); return t
    tn = T("nor.jpg", False); nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nstr
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b.inputs["Normal"])
    tr = T("rough.jpg", False); mr = nt.nodes.new("ShaderNodeMath"); mr.operation = "MULTIPLY"; mr.inputs[1].default_value = rough_mul
    nt.links.new(tr.outputs["Color"], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    if use_diff:
        td = T("diff.jpg", True)
        if tint:
            bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(td.outputs["Color"], bw.inputs[0])
            mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = 2.2; nt.links.new(bw.outputs[0], mm.inputs[0])
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
            mx.inputs[6].default_value = hexlin(tint); nt.links.new(mm.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
        else:
            nt.links.new(td.outputs["Color"], b.inputs["Base Color"])
    return m

M = {
    "wall": mat("Стены светло-серые NCS S 1500-N", "#CBCCC8", rough=0.85),
    "mold": mat("Молдинги в тон", "#D3D4D0", rough=0.8),
    "wall2": mat("Стены 2-й цвет", W2, rough=0.85),
    "ceil": mat("Потолок", "#F1EFEA", rough=0.9),
    "floor": floor_mat(),
    "boucle": mat("Букле молочное", "#ECE5D8", rough=0.95, bump=0.35, bscale=420, sheen=0.4),
    "chair": mat("Кресла букле", CHAIR or "#7B9C88", rough=0.6, bump=0.05, bscale=900, sheen=1.0),
    "shell": mat("Кресла — оболочка", "#6E8F7C", rough=0.6, bump=0.05, bscale=900, sheen=1.0),
    "wood": mat("Ножки — тёмное дерево", "#5A4636", rough=0.45),
    "seam": mat("Кант-строчка", "#9DB8A6", rough=0.55, sheen=1.0),
    "sofa": mat("Диван букле", SOFA or "#7B9C88", rough=0.6, bump=0.05, bscale=900, sheen=1.0),
    "marble": marble("Мрамор белый"),
    "dark": mat("Тёмное основание", "#2A2826", rough=0.35),
    "rug": mat("Ковёр светло-серый", "#CFCDC6", rough=1.0, bump=0.25, bscale=600),
    "tumba": mat("Шкаф и тумба — тёплый грейж (на тон темнее стен)", "#B9B2A6", rough=0.45),
    "tumba_frame": mat("Рамки фасадов", "#C6C0B5", rough=0.45),
    "tv": mat("ТВ", "#0A0A0B", rough=0.22),
    "frame": mat("Рама окна", "#F2F1EE", rough=0.4),
    "glass": mat("Стекло", "#FFFFFF", rough=0.0, transm=1.0),
    "tulle": mat("Тюль", "#F6F3EE", rough=0.9, transm=0.55, alpha=0.65),
    "drape": mat("Шторы плотные зелёные", "#3F4E3C", rough=0.95, sheen=0.5, bump=0.1, bscale=300),
    "brass": mat("Латунь", "#B8925A", rough=0.25, metal=1.0),
    "black": mat("Чёрный металл", "#151515", rough=0.4, metal=0.6),
    "door": mat("Дверь", "#EEEBE4", rough=0.5),
    "globe": emit("Шар бра", "#FFE6C2", 4.0),
    "led": emit("LED 4000K", "#FFEBD2", 8.0),
    "frame_led": emit("Световая рамка", "#FFF0DC", 12.0),
}
if KREM:
    for k, c in (("wall", "#E4D9C9"), ("mold", "#EAE1D3"), ("tumba", "#" + OPTC.get("tumba", "4A4A4C")), ("tumba_frame", "#" + OPTC.get("tumbaf", "57575A")), ("rug", "#E2D9CB")):
        M[k].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = hexlin(c)
    M["top"] = mat("Столешница камень крем", "#EFE9DF", rough=0.15)
if GREYW:
    for k, c in (("wall", "#BDBBB5"), ("mold", "#C9C7C1")):
        M[k].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = hexlin(c)
for k in ("tulle",):
    try: M[k].blend_method = "BLEND"
    except Exception: pass

def obj(name, bm, material, bevel=0.0, seg=3, smooth=False, sub=0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    o.data.materials.append(material)
    if bevel:
        md = o.modifiers.new("bevel", "BEVEL"); md.width = bevel; md.segments = seg; md.limit_method = "ANGLE"
    if sub:
        md = o.modifiers.new("sub", "SUBSURF"); md.levels = sub; md.render_levels = sub
    if smooth or bevel or sub:
        for p in o.data.polygons: p.use_smooth = True
    return o

def box(name, x0, z0, x1, z1, h0, h1, material, bevel=0.0, seg=3):
    bm = bmesh.new()
    vs = [bm.verts.new(W(x, z, h)) for (x, z, h) in
          [(x0, z0, h0), (x1, z0, h0), (x1, z1, h0), (x0, z1, h0), (x0, z0, h1), (x1, z0, h1), (x1, z1, h1), (x0, z1, h1)]]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(name, bm, material, bevel, seg)

def ellipse_prism(name, cx, cz, rx, rz, h0, h1, material, seg=64, bevel=0.0):
    bm = bmesh.new(); lo, hi = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg; x, z = cx + rx * math.cos(a), cz + rz * math.sin(a)
        lo.append(bm.verts.new(W(x, z, h0))); hi.append(bm.verts.new(W(x, z, h1)))
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(seg):
        j = (i + 1) % seg; bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj(name, bm, material, bevel, 4)
    for p in o.data.polygons: p.use_smooth = True
    return o

def sphere(name, cx, cz, h, r, material):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r)
    bmesh.ops.translate(bm, verts=bm.verts, vec=W(cx, cz, h))
    o = obj(name, bm, material)
    for p in o.data.polygons: p.use_smooth = True
    return o

def wbox(side, a0, a1, n0, n1, h0, h1, material, bevel=0.0, seg=3, name="Молдинг"):
    """Бокс в координатах стены: a — вдоль стены, n — от стены в комнату, h — высота."""
    if side == "L": return box(name, X0 + n0, a0, X0 + n1, a1, h0, h1, material, bevel, seg)
    if side == "R": return box(name, X1 - n1, a0, X1 - n0, a1, h0, h1, material, bevel, seg)
    if side == "T": return box(name, a0, Z0 + n0, a1, Z0 + n1, h0, h1, material, bevel, seg)
    if side == "B": return box(name, a0, Z1 - n1, a1, Z1 - n0, h0, h1, material, bevel, seg)

def wellip(side, a, h, ra, rh, rn, material, name="Декор"):
    """Сплюснутый эллипсоид на стене (розетка/лист лепнины)."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=1.0)
    for v in bm.verts:
        ca, cn, ch = v.co.x * ra, max(v.co.y, -0.2) * rn + rn * 0.2, v.co.z * rh
        if side == "L": v.co = W(X0 + cn, a + ca, h + ch)
        if side == "R": v.co = W(X1 - cn, a + ca, h + ch)
        if side == "T": v.co = W(a + ca, Z0 + cn, h + ch)
        if side == "B": v.co = W(a + ca, Z1 - cn, h + ch)
    o = obj(name, bm, material)
    for pp in o.data.polygons: pp.use_smooth = True
    return o

def mold_strip(side, a0, a1, h0, h1, horiz):
    """Профильный молдинг 55 мм: полка + скруглённое тело + валик (даёт свет и тень)."""
    if horiz:
        wbox(side, a0, a1, 0.0, 0.006, h0, h1, M["mold"], 0.002, 2)
        wbox(side, a0, a1, 0.0, 0.017, h0 + 0.010, h1 - 0.010, M["mold"], 0.007, 4)
        wbox(side, a0, a1, 0.0, 0.024, h0 + 0.004, h0 + 0.016, M["mold"], 0.005, 4)
    else:
        wbox(side, a0, a1, 0.0, 0.006, h0, h1, M["mold"], 0.002, 2)
        wbox(side, a0 + 0.010, a1 - 0.010, 0.0, 0.017, h0, h1, M["mold"], 0.007, 4)
        wbox(side, a0 + 0.004, a0 + 0.016, 0.0, 0.024, h0, h1, M["mold"], 0.005, 4)

# профиль классического молдинга 70×24 мм: полочка — оволо — выкружка — валик — полочка
_PRF = [(-0.035, 0), (-0.035, 0.005), (-0.030, 0.006), (-0.026, 0.008), (-0.022, 0.013), (-0.016, 0.018), (-0.010, 0.021),
        (-0.004, 0.022), (0.002, 0.020), (0.006, 0.015), (0.010, 0.012), (0.014, 0.013), (0.018, 0.016), (0.022, 0.016),
        (0.026, 0.012), (0.029, 0.008), (0.032, 0.006), (0.035, 0.004), (0.035, 0)]
_prof = None
def profile_obj():
    global _prof
    if _prof: return _prof
    cu = bpy.data.curves.new("профиль", "CURVE"); cu.dimensions = "2D"
    sp = cu.splines.new("POLY"); sp.points.add(len(_PRF) - 1)
    for k, (x, y) in enumerate(_PRF): sp.points[k].co = (x, y, 0, 1)
    _prof = bpy.data.objects.new("профиль", cu); sc.collection.objects.link(_prof); _prof.hide_render = True
    return _prof
_AX = {"L": ((0, 1, 0), (1, 0, 0), -1), "R": ((0, -1, 0), (-1, 0, 0), 1), "T": ((1, 0, 0), (0, -1, 0), 1), "B": ((-1, 0, 0), (0, 1, 0), -1)}
def wall_matrix(side):
    from mathutils import Matrix
    xl, zl, _ = _AX[side]; yl = (0, 0, 1)
    org = {"L": (X0, 0, 0), "R": (X1, 0, 0), "T": (0, -Z0, 0), "B": (0, -Z1, 0)}[side]
    m = Matrix(((xl[0], yl[0], zl[0], org[0]), (xl[1], yl[1], zl[1], org[1]), (xl[2], yl[2], zl[2], org[2]), (0, 0, 0, 1)))
    return m

def swept_frame(side, a0, a1, h0, h1, inset=0.035):
    """Рамка: классический профиль, выдавленный по прямоугольнику на стене (углы — «на ус»)."""
    sg = _AX[side][2]
    cu = bpy.data.curves.new("рамка", "CURVE"); cu.dimensions = "2D"; cu.fill_mode = "NONE"
    cu.bevel_mode = "OBJECT"; cu.bevel_object = profile_obj(); cu.use_fill_caps = False
    sp = cu.splines.new("POLY"); pts = [(a0 + inset, h0 + inset), (a1 - inset, h0 + inset), (a1 - inset, h1 - inset), (a0 + inset, h1 - inset)]
    sp.points.add(3)
    for k, (a, h) in enumerate(pts): sp.points[k].co = (sg * a, h, 0.0005, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new("Молдинг", cu); o.matrix_world = wall_matrix(side); sc.collection.objects.link(o)
    o.data.materials.append(M["mold"])
    return o

def _spiral(cx, cy, r0, r1, a0, turns, n=40):
    return [(cx + (r0 + (r1 - r0) * k / n) * math.cos(a0 + 2 * math.pi * turns * k / n),
             cy + (r0 + (r1 - r0) * k / n) * math.sin(a0 + 2 * math.pi * turns * k / n)) for k in range(n + 1)]
def _arc(p0, p1, bulge, n=24):
    (x0, y0), (x1, y1) = p0, p1; nx, ny = -(y1 - y0), (x1 - x0)
    return [(x0 + (x1 - x0) * t + nx * bulge * math.sin(math.pi * t), y0 + (y1 - y0) * t + ny * bulge * math.sin(math.pi * t)) for t in (k / n for k in range(n + 1))]
# уголок-акант в единичных координатах (угол рамки в 0,0; внутрь +u, +v), (точки, толщина начала, конца)
ACANTH = [
    (_spiral(0.27, 0.27, 0.20, 0.035, math.radians(200), 1.15), 1.0, 0.35),        # главный завиток
    (_arc((0.05, 0.10), (0.30, 0.05), 0.25), 0.9, 0.6),
    (_arc((0.30, 0.05), (0.95, 0.06), 0.10), 0.75, 0.15),                            # лист вдоль верха
    (_arc((0.10, 0.05), (0.05, 0.30), -0.25), 0.9, 0.6),
    (_arc((0.05, 0.30), (0.06, 0.95), -0.10), 0.75, 0.15),                           # лист вдоль бока
    (_arc((0.42, 0.10), (0.58, 0.20), 0.35), 0.55, 0.15), (_arc((0.60, 0.07), (0.76, 0.16), 0.35), 0.45, 0.12),
    (_arc((0.10, 0.42), (0.20, 0.58), -0.35), 0.55, 0.15), (_arc((0.07, 0.60), (0.16, 0.76), -0.35), 0.45, 0.12),
    (_spiral(0.48, 0.48, 0.07, 0.015, 0.0, 0.9, 20), 0.55, 0.2),                     # малый завиток к центру
]
def acanthus(side, ac, hc, du, dv, size=0.15, thick=0.012):
    """Объёмный лепной уголок: завитки и листья — кривые с переменной толщиной (как гипс)."""
    sg = _AX[side][2]
    cu = bpy.data.curves.new("акант", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = thick; cu.bevel_resolution = 4; cu.use_fill_caps = True
    for (pts, r0, r1) in ACANTH:
        sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
        for k, (u, v) in enumerate(pts):
            t = k / max(1, len(pts) - 1)
            a = ac + du * u * size; h = hc + dv * v * size
            sp.points[k].co = (sg * a, h, thick * 0.55, 1); sp.points[k].radius = r0 + (r1 - r0) * t
    o = bpy.data.objects.new("Лепнина акант", cu); o.matrix_world = wall_matrix(side); sc.collection.objects.link(o)
    o.data.materials.append(M["mold"])
    sphere_w = wellip(side, ac + du * 0.13 * size, hc + dv * 0.13 * size, 0.012, 0.012, 0.012, M["mold"], "Лепнина бусина")
    return o

def frame_on_wall(side, a0, a1, h0, h1, t=0.07, deco=True):
    """Рамка-молдинг (неоклассика): профиль 70×24 + лепные уголки-акант во всех углах (узел Б)."""
    if WMODE == "insets": wbox(side, a0 + 0.02, a1 - 0.02, 0.0, 0.0025, h0 + 0.02, h1 - 0.02, M["wall2"], name="Вставка")
    swept_frame(side, a0, a1, h0, h1)
    if deco and (a1 - a0) > 0.3 and (h1 - h0) > 0.3:
        e = t + 0.005
        for (ac, hc, du, dv) in ((a0 + e, h1 - e, 1, -1), (a1 - e, h1 - e, -1, -1), (a0 + e, h0 + e, 1, 1), (a1 - e, h0 + e, -1, 1)):
            acanthus(side, ac, hc, du, dv, size=0.22 if (h1 - h0) > 0.9 else 0.15)

def frames_in(side, a0, a1):
    n = max(1, round((a1 - a0) / 1.1)); w = (a1 - a0) / n
    for k in range(n):
        u0, u1 = a0 + k * w + 0.12, a0 + (k + 1) * w - 0.12
        frame_on_wall(side, u0, u1, 0.25, 0.85); frame_on_wall(side, u0, u1, 1.05, H - 0.42)

# ---- готовые текстуры на материалы
if KREM and OPTC.get("tumbatex"):     # шпон с текстурой для встроенной мебели
    for k in ("tumba", "tumba_frame"):
        pbr(M[k], "washed_grey_oak_veneer", 2.0, tint="#" + OPTC.get("tumba", "C9A57A"), use_diff=True, nstr=0.4, rough_mul=0.7)
if GREYW: pbr(M["wall"], "washed_grey_oak_veneer", 1.6, tint="#BDBBB5", use_diff=True, nstr=0.35, rough_mul=0.55)
else: pbr(M["wall"], "white_plaster_02", 1.2, nstr=0.4, rough_mul=1.0)
pbr(M["mold"], "white_plaster_02", 2.0, nstr=0.2)
pbr(M["sofa"], "velour_velvet", 3.0, tint=SOFA or "#7B9C88", use_diff=True, nstr=0.6, rough_mul=0.9)
pbr(M["rug"], "wool_boucle", 2.5, nstr=1.0)
_fb = M["floor"].node_tree.nodes["Principled BSDF"]; _lk = _fb.inputs["Base Color"].links[0].from_socket
pbr(M["floor"], "washed_grey_oak_veneer", 1.5, nstr=0.5, rough_mul=0.8)
_nt = M["floor"].node_tree; _td = _nt.nodes.new("ShaderNodeTexImage"); _td.image = _img(os.path.join(PH, "washed_grey_oak_veneer", "diff.jpg"))
_tc = _nt.nodes.new("ShaderNodeTexCoord"); _mp = _nt.nodes.new("ShaderNodeMapping"); _mp.inputs["Scale"].default_value = (1.2, 4, 1)
_nt.links.new(_tc.outputs["Object"], _mp.inputs["Vector"]); _nt.links.new(_mp.outputs[0], _td.inputs["Vector"])
_bw = _nt.nodes.new("ShaderNodeRGBToBW"); _nt.links.new(_td.outputs["Color"], _bw.inputs[0])
_mm = _nt.nodes.new("ShaderNodeMath"); _mm.operation = "MULTIPLY"; _mm.inputs[1].default_value = 1.7; _nt.links.new(_bw.outputs[0], _mm.inputs[0])
_mx = _nt.nodes.new("ShaderNodeMix"); _mx.data_type = "RGBA"; _mx.blend_type = "MULTIPLY"; _mx.inputs["Factor"].default_value = 0.85
_nt.links.new(_lk, _mx.inputs[6]); _nt.links.new(_mm.outputs[0], _mx.inputs[7]); _nt.links.new(_mx.outputs[2], _fb.inputs["Base Color"])

BK = os.path.join(os.path.dirname(HERE), "03_materialy", "blenderkit")
def import_bk(name, cx, cz, h0=0.0, rot_deg=0.0, target=None, axis="w", hide=()):
    """Модель BlenderKit (.blend): все объекты файла, ставим по центру (cx, cz) на высоту h0.
    target — размер по оси axis ('w' ширина / 'h' высота); None — реальный размер."""
    f = os.path.join(BK, name + ".blend")
    if not os.path.exists(f): return []
    with bpy.data.libraries.load(f, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    objs = [o for o in dst.objects if o is not None]
    for o in objs:
        if o.type in ("LIGHT", "CAMERA") or any(h in o.name.lower() for h in hide): continue
        sc.collection.objects.link(o)
    objs = [o for o in objs if o.name in sc.objects]
    roots = [o for o in objs if o.parent is None or o.parent not in objs]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    if not pts: return objs
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = {"w": max(mx_.x - mn.x, mx_.y - mn.y), "h": mx_.z - mn.z}[axis]
    k = (target / size) if target else 1.0; ctr = (mn + mx_) / 2
    from mathutils import Matrix
    T_ = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T_ @ r.matrix_world
    return objs
def recolor_metal(objs, material):
    for o in objs:
        if o.type != "MESH": continue
        for sl in o.material_slots:
            m = sl.material
            if not m or not m.use_nodes: continue
            b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if not b: continue
            met = (not b.inputs["Metallic"].is_linked and b.inputs["Metallic"].default_value > 0.4) or b.inputs["Metallic"].is_linked
            bc = b.inputs["Base Color"]; dark = (not bc.is_linked) and sum(bc.default_value[:3]) / 3 < 0.12
            if dark or "leg" in m.name.lower() or "frame" in m.name.lower(): sl.material = material

def import_ph(name, cx, cz, target_w, rot_deg=0.0, h0=0.0):
    """Готовая модель Poly Haven (glTF): ставим по центру (cx, cz) плана, масштаб по ширине."""
    f = os.path.join(PH, name, "model.gltf")
    if not os.path.exists(f): return []
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f)
    objs = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in objs if o.parent is None]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    k = target_w / max(1e-6, (mx_.x - mn.x)); ctr = (mn + mx_) / 2
    from mathutils import Matrix
    T_ = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T_ @ r.matrix_world
    return objs

# ---------------------------------------------------------------- коробка комнаты
T = 0.2
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0.0, M["floor"])
box("Стена лев", X0 - T, Z0 - T, X0, Z1 + T, 0, H, M["wall"])
box("Стена прав", X1, Z0 - T, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена низ лев", X0, Z1, DX0, Z1 + T, 0, H, M["wall"]); box("Стена низ прав", DX1, Z1, X1, Z1 + T, 0, H, M["wall"])
box("Над дверью", DX0, Z1, DX1, Z1 + T, DH, H, M["wall"])
box("Окно лев", X0, Z0 - T, WX0, Z0, 0, H, M["wall"]); box("Окно прав", WX1, Z0 - T, X1, Z0, 0, H, M["wall"])
box("Под окном", WX0, Z0 - T, WX1, Z0, 0, WS, M["wall"]); box("Над окном", WX0, Z0 - T, WX1, Z0, WT, H, M["wall"])
# потолок: основная плоскость + ниша 150 у окна (под скрытый карниз штор)
NI = 0.15
box("Потолок", X0, Z0 + NI, X1, Z1, H, H + 0.05, M["ceil"])
box("Ниша карниза", X0, Z0, X1, Z0 + NI, H + 0.10, H + 0.15, M["ceil"])
box("Ниша борт", X0, Z0 + NI - 0.01, X1, Z0 + NI, H, H + 0.10, M["ceil"])
# окно: рама + стекло + подоконник
box("Подоконник", WX0 - 0.03, Z0 - 0.12, WX1 + 0.03, Z0 + 0.04, WS - 0.03, WS, M["frame"], 0.005)
for (a, b) in ((WX0, WX0 + 0.06), (WX1 - 0.06, WX1), ((WX0 + WX1) / 2 - 0.03, (WX0 + WX1) / 2 + 0.03)):
    box("Импост", a, Z0 - 0.12, b, Z0 - 0.06, WS, WT, M["frame"], 0.004)
for (h0, h1) in ((WS, WS + 0.06), (WT - 0.06, WT)):
    box("Рама гор", WX0, Z0 - 0.12, WX1, Z0 - 0.06, h0, h1, M["frame"], 0.004)
box("Стекло", WX0, Z0 - 0.095, WX1, Z0 - 0.085, WS, WT, M["glass"])
# плинтус 120 и карниз со скрытым LED (кроме оконной стены — там ниша)
for (a, b, c, d) in ((X0, Z0, X0 + 0.015, Z1), (X1 - 0.015, Z0, X1, Z1), (X0, Z1 - 0.015, DX0, Z1), (DX1, Z1 - 0.015, X1, Z1)):
    box("Плинтус", a, b, c, d, 0, 0.12, M["mold"], 0.004)
    ex = 0.012 if c - a < 0.05 else 0; ez = 0.012 if d - b < 0.05 else 0
    box("Плинтус валик", a - (ex if a > X0 + 0.5 else -0.0) * 0, b, c + 0, d, 0.105, 0.125, M["mold"], 0.008, 4) if False else None
CH = H - 0.16 if CEIL != 8 else H - 0.10   # при коробе карниз встаёт под короб
for (a, b, c, d, la, lb, lc, ld) in (
        (X0, Z0 + NI, X0 + 0.10, Z1, X0 + 0.02, Z0 + NI, X0 + 0.04, Z1),
        (X1 - 0.10, Z0 + NI, X1, Z1, X1 - 0.04, Z0 + NI, X1 - 0.02, Z1),
        (X0, Z1 - 0.10, X1, Z1, X0, Z1 - 0.04, X1, Z1 - 0.02)):
    box("Карниз-галтель", a, b, c, d, CH - 0.06, CH, M["mold"], 0.02, 5)
    # ступени профиля вниз по стене (классический карниз)
    if c - a < 0.2 and a < X0 + 0.01: box("Карниз ступень", X0, b, X0 + 0.05, d, CH - 0.11, CH - 0.06, M["mold"], 0.012, 4); box("Карниз валик", X0, b, X0 + 0.025, d, CH - 0.15, CH - 0.11, M["mold"], 0.01, 4)
    elif c - a < 0.2: box("Карниз ступень", X1 - 0.05, b, X1, d, CH - 0.11, CH - 0.06, M["mold"], 0.012, 4); box("Карниз валик", X1 - 0.025, b, X1, d, CH - 0.15, CH - 0.11, M["mold"], 0.01, 4)
    else: box("Карниз ступень", a, Z1 - 0.05, c, Z1, CH - 0.11, CH - 0.06, M["mold"], 0.012, 4); box("Карниз валик", a, Z1 - 0.025, c, Z1, CH - 0.15, CH - 0.11, M["mold"], 0.01, 4)
    _o = box("LED карниз", la, lb, lc, ld, CH, CH + 0.005, M["led"])
    if CEIL == 8: _o.hide_render = True          # потолок ровного одного цвета, без светлой полосы у карниза
box("LED в нише", X0, Z0 + 0.02, X1, Z0 + 0.04, H + 0.095, H + 0.10, M["led"])
# световая рамка (линейный профиль заподлицо, опал), 0,6 от стен
FO = 1.05 if CEIL == 8 else FO
fa0, fa1, fb0, fb1, sw = X0 + FO, X1 - FO, Z0 + FO, Z1 - FO, 0.035
def led_rect(a0, a1, b0, b1, w=0.035):
    for (a, b, c, d) in ((a0, b0, a1, b0 + w), (a0, b1 - w, a1, b1), (a0, b0, a0 + w, b1), (a1 - w, b0, a1, b1)):
        box("Световая рамка", a, b, c, d, H - 0.004, H - 0.001, M["frame_led"])
cxr, czr = (X0 + X1) / 2, (Z0 + Z1) / 2
if CEIL == 1:     # два пересекающихся прямоугольника (как на фото заказчика)
    led_rect(X0 + 0.5, X1 - 1.0, Z0 + 0.6, Z1 - 1.6); led_rect(X0 + 1.0, X1 - 0.5, Z0 + 1.6, Z1 - 0.6)
elif CEIL == 2:   # двойная рамка (внешняя + внутренняя)
    led_rect(X0 + 0.5, X1 - 0.5, Z0 + 0.5, Z1 - 0.5); led_rect(X0 + 0.95, X1 - 0.95, Z0 + 0.95, Z1 - 0.95)
elif CEIL == 3:   # рамка, разделённая на 3 квадрата (над столом, диваном, ТВ)
    led_rect(fa0, fa1, fb0, fb1); L3 = (fb1 - fb0) / 3
    for k in (1, 2): box("Световая рамка", fa0, fb0 + k * L3 - 0.0175, fa1, fb0 + k * L3 + 0.0175, H - 0.004, H - 0.001, M["frame_led"])
elif CEIL == 4:   # три отдельных прямоугольника вдоль комнаты
    L3 = (fb1 - fb0 - 0.4) / 3
    for k in range(3): led_rect(fa0, fa1, fb0 + k * (L3 + 0.2), fb0 + k * (L3 + 0.2) + L3)
else:
    led_rect(fa0, fa1, fb0, fb1)
def ceil_frame(a0, a1, b0, b1, w=0.06, dep=0.025):
    """Потолочный молдинг (рамка) — скруглённые планки на потолке."""
    for (x0_, z0_, x1_, z1_) in ((a0, b0, a1, b0 + w), (a0, b1 - w, a1, b1), (a0, b0, a0 + w, b1), (a1 - w, b0, a1, b1)):
        box("Потолок молдинг", x0_, z0_, x1_, z1_, H - dep, H, M["mold"], 0.01, 4)
def ceil_corners(a0, a1, b0, b1, r=0.07):
    for (x_, z_) in ((a0, b0), (a1, b0), (a0, b1), (a1, b1)):
        ellipse_prism("Потолок розетка", x_, z_, r, r, H - 0.02, H, M["mold"], bevel=0.012)
        ellipse_prism("Потолок розетка", x_, z_, r * 0.5, r * 0.5, H - 0.035, H - 0.02, M["mold"], bevel=0.008)
def _ornament_side():
    """Одна «ветвь» барочного уголка вдоль стороны: большой C-завиток, листья, хвостик-завиток."""
    out = []
    out.append((_spiral(0.40, 0.15, 0.11, 0.02, math.radians(250), 1.3, 36), 1.0, 0.4))    # главный C-завиток
    out.append((_arc((0.08, 0.06), (0.40, 0.04), 0.18), 1.0, 0.8))                          # стебель от угла
    out.append((_arc((0.52, 0.10), (0.85, 0.05), 0.12), 0.8, 0.2))                          # хвост
    out.append((_spiral(0.88, 0.09, 0.04, 0.01, math.radians(120), 1.0, 16), 0.5, 0.2))     # малый завиток на конце
    for (a0, a1, b) in (((0.20, 0.10), (0.30, 0.24), 0.35), ((0.27, 0.07), (0.40, 0.27), 0.3), ((0.55, 0.12), (0.66, 0.22), -0.3)):
        out.append((_arc(a0, a1, b), 0.8, 0.15))                                              # листья-аканты
    return out
ORN_C = _ornament_side()
ORN_C = ORN_C + [([(v, u) for (u, v) in pts], r0, r1) for (pts, r0, r1) in ORN_C]            # зеркально по диагонали
ORN_C += [(_arc((0.05, 0.05), (0.22, 0.22), 0.0), 1.1, 0.9), (_spiral(0.10, 0.10, 0.06, 0.01, 0.0, 1.0, 20), 0.9, 0.3)]   # центр угла
def acanthus_ceil(xc, zc, dx, dz, size=0.26, thick=0.014, shape=None):
    """Лепной уголок-акант на потолке (тот же рисунок, что на стенах)."""
    cu = bpy.data.curves.new("акант-потолок", "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = thick; cu.bevel_resolution = 4; cu.use_fill_caps = True
    for (pts, r0, r1) in (shape or ORN_C):
        sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
        for k, (u, v) in enumerate(pts):
            t = k / max(1, len(pts) - 1); pw = W(xc + dx * u * size, zc + dz * v * size, H - thick * 0.55)
            sp.points[k].co = (pw.x, pw.y, pw.z, 1); sp.points[k].radius = r0 + (r1 - r0) * t
    o = bpy.data.objects.new("Лепнина потолок", cu); sc.collection.objects.link(o); o.data.materials.append(M["mold"])
BW, BD = 0.34, 0.10                # короб ГКЛ по периметру 340×100 (как фото 1), у окна — ниша штор
COVE = []
if CEIL == 8:
    zb0 = Z0 + NI                      # у окна короб начинается за нишей штор
    # короб по кругу: внешняя часть (у стен) — во всю высоту; внутри — полка под ленту и бортик по контуру
    ia0, ia1, ib0, ib1 = X0 + BW, X1 - BW, zb0 + BW, Z1 - BW          # внутренний контур короба
    # 12.11: без шва в углах — куски не перекрываются и без фаски на стыках (иначе в углу видна линия)
    for (a0_, b0_, a1_, b1_) in ((X0, zb0, X0 + 0.20, Z1), (X1 - 0.20, zb0, X1, Z1), (X0 + 0.20, Z1 - 0.20, X1 - 0.20, Z1), (X0 + 0.20, zb0, X1 - 0.20, zb0 + 0.20)):
        box("Короб", a0_, b0_, a1_, b1_, H - BD, H, M["ceil"])
    for (a0_, b0_, a1_, b1_) in ((X0 + 0.20, zb0 + 0.20, ia0, Z1 - 0.20), (ia1, zb0 + 0.20, X1 - 0.20, Z1 - 0.20),
                                  (ia0, ib1, ia1, Z1 - 0.20), (ia0, zb0 + 0.20, ia1, ib0)):
        box("Короб полка", a0_, b0_, a1_, b1_, H - BD, H - 0.065, M["ceil"])
    for (a0_, b0_, a1_, b1_) in ((ia0 - 0.02, ib0 - 0.02, ia0, ib1 + 0.02), (ia1, ib0 - 0.02, ia1 + 0.02, ib1 + 0.02),
                                  (ia0, ib1, ia1, ib1 + 0.02), (ia0, ib0 - 0.02, ia1, ib0)):
        box("Короб бортик", a0_, b0_, a1_, b1_, H - 0.065, H - 0.045, M["ceil"])
    # лента — непрерывно по кругу, углы тоже светятся
    COVE = [("L", ia0 - 0.05, (ib0 + ib1) / 2, 0.03, ib1 - ib0 + 0.10), ("R", ia1 + 0.05, (ib0 + ib1) / 2, 0.03, ib1 - ib0 + 0.10),
            ("B", (ia0 + ia1) / 2, ib1 + 0.05, ia1 - ia0 + 0.10, 0.03), ("T", (ia0 + ia1) / 2, ib0 - 0.05, ia1 - ia0 + 0.10, 0.03)]
    ceil_frame(X0 + 0.45, X1 - 0.45, Z0 + NI + 0.45, Z1 - 0.45, w=0.08, dep=0.05)     # по эскизу: одна рамка в двойную линию
    ceil_frame(X0 + 0.54, X1 - 0.54, Z0 + NI + 0.54, Z1 - 0.54, w=0.035, dep=0.03)
    e = 0.58
    for (x_, z_, dx, dz) in ((X0 + e, Z0 + NI + e, 1, 1), (X1 - e, Z0 + NI + e, -1, 1), (X0 + e, Z1 - e, 1, -1), (X1 - e, Z1 - e, -1, -1)):
        acanthus_ceil(x_, z_, dx, dz, size=0.45, thick=0.017)
    for zz in [Z0 + 1.4 + k * (Z1 - Z0 - 2.8) / 2 for k in range(3)]:   # по 3 круглых спота Ø100 с боков
        for xx in (X0 + 0.80, X1 - 0.80):
            ellipse_prism("Спот круглый", xx, zz, 0.05, 0.05, H - 0.006, H - 0.001, M["frame_led"], seg=24)
            lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = 6 if not NIGHT else 14; lt.spot_size = math.radians(70); lt.spot_blend = 0.6
            lt.color = (1.0, 0.9, 0.78); lt.shadow_soft_size = 0.03
            lo = bpy.data.objects.new("Спот", lt); lo.location = W(xx, zz, H - 0.02); sc.collection.objects.link(lo)
if CEIL == 5:     # A: рамка LED + внутри лепная рамка с розетками по углам
    ceil_frame(fa0 + 0.25, fa1 - 0.25, fb0 + 0.25, fb1 - 0.25); ceil_corners(fa0 + 0.28, fa1 - 0.28, fb0 + 0.28, fb1 - 0.28)
elif CEIL == 6:   # B: рамка LED + внутри 3 лепные филёнки (кессоны)
    L3 = (fb1 - fb0 - 0.5 - 0.3) / 3
    for k in range(3):
        z0_ = fb0 + 0.25 + k * (L3 + 0.15); ceil_frame(fa0 + 0.25, fa1 - 0.25, z0_, z0_ + L3)
elif CEIL == 7:   # C: лепная рамка снаружи LED + розетка-медальон в центре (без люстры)
    ceil_frame(fa0 - 0.18, fa1 + 0.18, fb0 - 0.18, fb1 + 0.18, w=0.08)
    for (rr, d0, d1) in ((0.42, 0.0, 0.015), (0.32, 0.015, 0.03), (0.18, 0.03, 0.05), (0.08, 0.05, 0.07)):
        ellipse_prism("Потолок медальон", cxr, czr, rr, rr, H - d1, H - d0, M["mold"], bevel=0.008)

# ---------------------------------------------------------------- стены: молдинги
TVF = F("ТВ-тумба")[0]; tz0, tz1 = TVF["z"], TVF["z"] + TVF["d"]; tm = (tz0 + tz1) / 2
frames_in("L", Z0, tz0); frames_in("L", tz1, Z1)
frame_on_wall("L", tm - 1.12, tm + 1.12, 0.68, 2.00)                       # ТВ в рамке молдинга
frames_in("R", Z0, Z1 - 0.62)
frames_in("T", X0, WX0) if WX0 - X0 > 0.5 else None
frames_in("T", WX1, X1) if X1 - WX1 > 0.5 else None

if WMODE == "lower":
    HL = 0.95
    for (side, a0, a1) in (("L", Z0, Z1), ("R", Z0, Z1), ("T", X0, WX0), ("T", WX1, X1), ("B", X0, DX0 - 0.08), ("B", DX1 + 0.08, X1)):
        wbox(side, a0, a1, 0.0, 0.0025, 0.0, HL, M["wall2"], name="Низ стены")
        mold_strip(side, a0, a1, HL - 0.03, HL + 0.025, True)
    wbox("T", WX0, WX1, 0.0, 0.0025, 0.0, WS - 0.03, M["wall2"], name="Низ стены")
# ---------------------------------------------------------------- мебель
# ТВ-зона: подвесная тумба в цвет стен + ТВ на стене
if KREM:   # встроенная напольная тумба во всю ТВ-зону: рамки-фасады, латунные ручки, каменная столешница
    k0, k1, KD, KH = tm - 1.55, tm + 1.55, 0.45, 0.62
    box("ТВ-тумба корпус", X0, k0, X0 + KD - 0.02, k1, 0.08, KH, M["tumba"])
    box("Цоколь", X0, k0 + 0.02, X0 + KD - 0.06, k1 - 0.02, 0.0, 0.08, M["tumba"])
    box("Столешница", X0, k0 - 0.01, X0 + KD + 0.01, k1 + 0.01, KH, KH + 0.025, M["top"], 0.004)
    nd = 4; dw = (k1 - k0) / nd
    for k in range(nd):
        u0, u1 = k0 + k * dw + 0.003, k0 + (k + 1) * dw - 0.003
        box("Фасад тумбы", X0 + KD - 0.02, u0, X0 + KD, u1, 0.085, KH - 0.005, M["tumba"], 0.002)
        for (p0, p1, q0, q1) in ((u0 + 0.06, u1 - 0.06, KH - 0.085, KH - 0.07), (u0 + 0.06, u1 - 0.06, 0.15, 0.165),
                                 (u0 + 0.06, u0 + 0.075, 0.15, KH - 0.07), (u1 - 0.075, u1 - 0.06, 0.15, KH - 0.07)):
            box("Рамка тумбы", X0 + KD, p0, X0 + KD + 0.008, p1, q0, q1, M["tumba_frame"], 0.002)
        mz = (u0 + u1) / 2
        box("Ручка латунь", X0 + KD + 0.008, mz - 0.11, X0 + KD + 0.022, mz + 0.11, KH - 0.115, KH - 0.103, M["brass"], 0.004)
else:
    box("ТВ-тумба", X0, tz0, X0 + TVF["w"], tz1, 0.25, 0.55, M["tumba"], 0.006)
    for zz in np.linspace(tz0, tz1, 4)[1:-1]:
        box("Шов фасада", X0 + TVF["w"] - 0.001, zz - 0.0015, X0 + TVF["w"] + 0.0005, zz + 0.0015, 0.26, 0.54, M["dark"])
    _tf = X0 + TVF["w"]; _seg = np.linspace(tz0, tz1, 4)
    for k in range(3):                                   # рамки на фасадах тумбы + латунные кнопки
        u0, u1 = _seg[k] + 0.05, _seg[k + 1] - 0.05
        for (p0, p1, q0, q1) in ((u0, u1, 0.49, 0.51), (u0, u1, 0.29, 0.31), (u0, u0 + 0.02, 0.29, 0.51), (u1 - 0.02, u1, 0.29, 0.51)):
            box("Рамка тумбы", _tf, p0, _tf + 0.01, p1, q0, q1, M["tumba_frame"], 0.002)
        sphere("Кнопка латунь", _tf + 0.02, (_seg[k] + _seg[k + 1]) / 2, 0.40, 0.014, M["brass"])
box("ТВ 85\"", X0 + 0.01, tm - 0.95, X0 + 0.045, tm + 0.95, 0.80, 1.87, M["tv"], 0.004)   # ТВ 85" ~1900×1070

# диван — СУЩЕСТВУЮЩИЙ у заказчика: зелёный бархат, спинка с вертикальной стёжкой «каналами» (размер уточнить)
S = F("Диван")[0]; sx0, sz0, sx1, sz1 = S["x"], S["z"], S["x"] + S["w"], S["z"] + S["d"]
box("Диван основание", sx0 + 0.04, sz0 + 0.03, sx1, sz1 - 0.03, 0.10, 0.40, M["sofa"], 0.06, 5)
for (lz0, lz1) in ((sz0 + 0.09, sz0 + 0.13), (sz1 - 0.13, sz1 - 0.09)):        # ножки
    for lx in (sx0 + 0.10, sx1 - 0.10):
        box("Диван ножка", lx - 0.02, lz0, lx + 0.02, lz1, 0.0, 0.10, M["wood"], 0.006)
box("Диван спинка", sx1 - 0.24, sz0 + 0.18, sx1 - 0.02, sz1 - 0.18, 0.38, 0.90, M["sofa"], 0.09, 6)
nch = max(8, round((sz1 - sz0 - 0.4) / 0.17)); cw = (sz1 - sz0 - 0.36) / nch
for k in range(1, nch):                                 # швы-строчки «каналов» на цельной спинке
    zz = sz0 + 0.18 + k * cw
    box("Диван шов", sx1 - 0.245, zz - 0.005, sx1 - 0.23, zz + 0.005, 0.44, 0.86, M["seam"], 0.004, 2)
for (za, zb) in ((sz0 + 0.02, sz0 + 0.20), (sz1 - 0.20, sz1 - 0.02)):          # подлокотники-валики
    box("Диван подлокотник", sx0 + 0.06, za, sx1 - 0.02, zb, 0.38, 0.68, M["sofa"], 0.08, 6)
sm = (sz0 + sz1) / 2
box("Подушка", sx0 + 0.06, sz0 + 0.20, sx1 - 0.25, sm - 0.01, 0.40, 0.52, M["sofa"], 0.06, 5)
box("Подушка", sx0 + 0.06, sm + 0.01, sx1 - 0.25, sz1 - 0.20, 0.40, 0.52, M["sofa"], 0.06, 5)

TB = (F("Журн") or F("Столик"))[0]; tcx, tcz = TB["x"] + TB["w"] / 2, TB["z"] + TB["d"] / 2
if VAR in ("B", "C"):
    M["caramel"] = mat("Подушки карамель", "#A8714A", rough=0.9, sheen=0.4)
    M["olive"] = mat("Подушки олива", "#7D7A5A", rough=0.9, sheen=0.4)
    M["leaf"] = mat("Листва", "#4E5E3A", rough=0.7)
    M["pot"] = mat("Кашпо", "#8C8478", rough=0.8, bump=0.3, bscale=80)
    sm = (sz0 + sz1) / 2
    for (zz, mm) in ((sz0 + 0.42, "caramel"), (sz0 + 0.75, "olive"), (sz1 - 0.75, "olive"), (sz1 - 0.42, "caramel")):
        box("Подушка декор", sx1 - 0.36, zz - 0.2, sx1 - 0.22, zz + 0.2, 0.48, 0.88, M[mm], 0.06, 4)
    box("Плед", sx0 + 0.15, sz1 - 0.6, sx1 - 0.3, sz1 - 0.3, 0.50, 0.53, M["caramel"], 0.02, 3)
    # растение (олива) в углу у окна
    pcx, pcz = X0 + 0.42, Z0 + 0.55
    ellipse_prism("Кашпо", pcx, pcz, 0.24, 0.24, 0.0, 0.5, M["pot"], bevel=0.03)
    box("Ствол", pcx - 0.02, pcz - 0.02, pcx + 0.02, pcz + 0.02, 0.5, 1.5, M["dark"])
    import random as _r; _r.seed(3)
    for _ in range(40):
        sphere("Листва", pcx + _r.uniform(-0.38, 0.38), pcz + _r.uniform(-0.3, 0.3), _r.uniform(1.25, 2.05), _r.uniform(0.08, 0.15), M["leaf"])
    for (k, c) in enumerate(("#2B2B2B", "#B8A88E", "#6F6656")):
        box("Книга", tcx - 0.15, tcz - 0.12 + k * 0.0, tcx + 0.15, tcz + 0.1, 0.35 + k * 0.03, 0.38 + k * 0.03, mat("Книга%d" % k, c, 0.6), 0.003)
# кресла-«ракушки» букле, лицом к столу
def line3d(name, p, q, r, material):
    d = q - p; L = d.length
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r, depth=L)
    rot = d.to_track_quat("Z", "Y").to_matrix()
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=rot)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(p + q) / 2)
    o = obj(name, bm, material)
    for pp in o.data.polygons: pp.use_smooth = True

def tub_chair(cx, cz, face_z):
    """Кресло (каталог №8, правки заказчика): «ушастое» бархатное, верх спинки — трапеция (прямой верх,
    расширяется кверху), подлокотники отогнуты наружу, низ цельный большой (без отдельной подушки),
    стёжка пуговицами, конические ножки."""
    f = 1 if face_z > 0 else -1
    zb = cz - f * 0.36
    def L(x, y, h): return W(cx + x, zb + f * y, h)
    for (x, y) in ((-0.30, 0.10), (0.30, 0.10), (-0.30, 0.66), (0.30, 0.66)):     # конические ножки
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.016, radius2=0.026, depth=0.20)
        bmesh.ops.translate(bm, verts=bm.verts, vec=L(x, y, 0.10)); o = obj("Кресло ножка", bm, M["wood"])
        for pp in o.data.polygons: pp.use_smooth = True
    # цельный большой низ (сиденье = корпус), слегка расширяется кверху
    bm = bmesh.new(); vs = []
    for (h, e) in ((0.20, 0.0), (0.47, 0.03)):
        for (x, y) in ((-0.36 - e, 0.04), (0.36 + e, 0.04), (0.36 + e, 0.74 + e), (-0.36 - e, 0.74 + e)):
            vs.append(bm.verts.new(L(x, y, h)))
    for fc in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[q] for q in fc])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj("Кресло низ", bm, M["chair"], bevel=0.09, seg=8)
    # подлокотники: отогнуты наружу кверху, к переду ниже
    for sx in (-1, 1):
        nu, nv = 16, 10; bm = bmesh.new(); g = []
        for jv in range(nv + 1):
            v = jv / nv; row = []
            for iu in range(nu + 1):
                y = 0.10 + 0.62 * iu / nu
                t_ = min(1, max(0, (y - 0.12) / 0.30)); t_ = t_ * t_ * (3 - 2 * t_); ht = 0.80 * (1 - t_) + 0.64 * t_
                row.append(bm.verts.new(L(sx * (0.33 + 0.12 * v ** 1.6), y, 0.45 + (ht - 0.45) * v)))
            g.append(row)
        for jv in range(nv):
            for iu in range(nu): bm.faces.new((g[jv][iu], g[jv][iu + 1], g[jv + 1][iu + 1], g[jv + 1][iu]))
        o = obj("Кресло подлокотник", bm, M["shell"])
        md = o.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.10; md.offset = 0
        mb = o.modifiers.new("bevel", "BEVEL"); mb.width = 0.045; mb.segments = 8; mb.limit_method = "ANGLE"
        for pp in o.data.polygons: pp.use_smooth = True
    # спинка-трапеция с прямым верхом
    nu, nv = 26, 16; bm = bmesh.new(); g = []
    def B(u, v): return L(u * (0.33 + 0.15 * v ** 1.5), 0.04 + 0.10 * u * u - 0.07 * v, 0.45 + 0.55 * v + v ** 4 * (0.10 * abs(u) ** 3 - 0.02))   # №8: «уши» вверху по краям
    for jv in range(nv + 1): g.append([bm.verts.new(B(-1 + 2 * iu / nu, jv / nv)) for iu in range(nu + 1)])
    for jv in range(nv):
        for iu in range(nu): bm.faces.new((g[jv][iu], g[jv][iu + 1], g[jv + 1][iu + 1], g[jv + 1][iu]))
    o = obj("Кресло спинка", bm, M["shell"])
    md = o.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.13; md.offset = 0
    mb = o.modifiers.new("bevel", "BEVEL"); mb.width = 0.05; mb.segments = 8; mb.limit_method = "ANGLE"
    for pp in o.data.polygons: pp.use_smooth = True
    for (u, v) in ((-0.5, 0.35), (0.0, 0.35), (0.5, 0.35), (-0.25, 0.58), (0.25, 0.58), (-0.5, 0.8), (0.0, 0.8), (0.5, 0.8)):   # стёжка пуговицами
        pnt = B(u, v) + Vector((0, -f * 0.066, 0)); sphere("Кресло пуговица", pnt.x, -pnt.y, pnt.z, 0.012, M["chair"])
    xa, xb = sorted((zb + f * 0.14, zb + f * 0.76))
    box("Кресло подушка", cx - 0.31, xa, cx + 0.31, xb, 0.45, 0.56, M["chair"], 0.06, 6)
TB = (F("Журн") or F("Столик"))[0]; tcx, tcz = TB["x"] + TB["w"] / 2, TB["z"] + TB["d"] / 2
for c in F("Кресло"):
    cx, cz = c["x"] + c["w"] / 2, c["z"] + c["d"] / 2
    if not import_ph("GreenChair_01", cx, cz, 0.75, 0 if cz < tcz else 180):
        tub_chair(cx, cz, +1 if cz < tcz else -1)

# журнальный стол: овал 1200×700, мрамор на тёмном основании
_tbl = import_bk("stol_mramor", tcx, tcz, 0.0, 90, 1.20) if KREM else []
if _tbl:
    recolor_metal(_tbl, M["brass"])
    import_bk("knigi", tcx - 0.05, tcz + 0.25, 0.47, 25)
    import_bk("tyulpany", tcx + 0.05, tcz - 0.2, 0.47, 0, 0.32, "h")
elif not import_ph("gothic_coffee_table", tcx, tcz, 1.10, 90):     # стол в стиле мебели — резное тёмное дерево (готовая модель)
    ellipse_prism("Стол основание", tcx, tcz, TB["w"] / 2 - 0.16, TB["d"] / 2 - 0.22, 0.0, 0.31, M["dark"], bevel=0.01)
    ellipse_prism("Стол мрамор", tcx, tcz, TB["w"] / 2, TB["d"] / 2, 0.31, 0.35, M["marble"], bevel=0.008)

# ковёр 2,3×3,0 молочный
rx0, rx1 = max(X0 + 1.1, sx0 - 1.45), min(X1 - 0.12, sx0 + 0.55)
if not KREM: box("Ковёр", rx0, tcz - 1.5, rx1, tcz + 1.5, 0.0, 0.012, M["rug"], 0.004)   # 12.11: ковры убраны

# шкаф у двери (в цвет стен, фасады с рамками)
for wd in F("Шкаф"):
    a0, a1, b0, b1 = wd["x"], wd["x"] + wd["w"], wd["z"], wd["z"] + wd["d"]
    if KREM: a0, a1 = DX1 + 0.085, X1          # встроенный: от наличника двери до стены
    WH = (H - BD) if CEIL == 8 else wd["h"]          # шкаф до потолка (до короба), без щели сверху
    box("Шкаф", a0, b0, a1, b1, 0, WH, M["tumba"], 0.004)
    n = 4; w = (a1 - a0) / n
    for k in range(n):
        u0, u1 = a0 + k * w + 0.07, a0 + (k + 1) * w - 0.07
        for (p0, p1, q0, q1) in ((u0, u1, WH - 0.2, WH - 0.17), (u0, u1, 0.15, 0.18), (u0, u0 + 0.03, 0.15, WH - 0.17), (u1 - 0.03, u1, 0.15, WH - 0.17)):
            box("Рамка фасада", p0, b0 - 0.012, p1, b0, q0, q1, M["tumba_frame"], 0.003)
        hx = a0 + (k + 1) * w - 0.05 if k % 2 == 0 else a0 + k * w + 0.05        # латунные ручки-скобы у стыка створок
        box("Ручка латунь", hx - 0.008, b0 - 0.035, hx + 0.008, b0 - 0.012, (0.70 if KREM else 0.95), (1.55 if KREM else 1.25), M["brass"], 0.004)
        if k: box("Шов", a0 + k * w - 0.0015, b0 - 0.002, a0 + k * w + 0.0015, b0, 0.02, WH - 0.02, M["tumba_frame"])   # шов между створками, не по краю

# дверь (неоклассика): полотно + филёнки + ручка
box("Дверь", DX0, Z1 + 0.06, DX1, Z1 + 0.10, 0, DH, M["door"], 0.004)
for (h0, h1) in ((0.2, 0.95), (1.15, DH - 0.18)):
    for (p0, p1, q0, q1) in ((DX0 + 0.12, DX1 - 0.12, h1 - 0.025, h1), (DX0 + 0.12, DX1 - 0.12, h0, h0 + 0.025),
                             (DX0 + 0.12, DX0 + 0.145, h0, h1), (DX1 - 0.145, DX1 - 0.12, h0, h1)):
        box("Филёнка", p0, Z1 + 0.05, p1, Z1 + 0.06, q0, q1, M["mold"], 0.003)
box("Ручка", DX1 - 0.12, Z1 + 0.02, DX1 - 0.06, Z1 + 0.05, 1.0, 1.02, M["brass"], 0.004)
for (a, b) in ((DX0 - 0.08, DX0), (DX1, DX1 + 0.08)):
    box("Наличник", a, Z1 - 0.015, b, Z1, 0, DH + 0.08, M["mold"], 0.004)
box("Наличник", DX0 - 0.08, Z1 - 0.015, DX1 + 0.08, Z1, DH, DH + 0.08, M["mold"], 0.004)

# бра-шары у концов дивана, h=1600
M["opal"] = mat("Опаловое стекло", "#FBF7F0", rough=0.25, transm=0.0, sheen=0.0)
_on = M["opal"].node_tree.nodes["Principled BSDF"]
if "Emission Color" in _on.inputs:
    _on.inputs["Emission Color"].default_value = hexlin("#FFE9CC"); _on.inputs["Emission Strength"].default_value = 0.7
if "Subsurface Weight" in _on.inputs: _on.inputs["Subsurface Weight"].default_value = 0.3
def cyl_x(name, x0, x1, cz, h, r, material):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=r, radius2=r, depth=abs(x1 - x0))
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.radians(90), 3, "Y"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=W((x0 + x1) / 2, cz, h))
    o = obj(name, bm, material)
    for pp in o.data.polygons: pp.use_smooth = True
for zz in ():   # бра убраны по решению заказчика
    cyl_x("Бра основание", X1 - 0.018, X1, zz, 1.60, 0.055, M["black"])
    cyl_x("Бра кольцо", X1 - 0.026, X1 - 0.018, zz, 1.60, 0.02, M["brass"])
    cyl_x("Бра кронштейн", X1 - 0.11, X1 - 0.026, zz, 1.60, 0.009, M["black"])
    cyl_x("Бра патрон", X1 - 0.135, X1 - 0.105, zz, 1.60, 0.022, M["brass"])
    sphere("Бра шар", X1 - 0.21, zz, 1.60, 0.085, M["opal"])
    lt = bpy.data.lights.new("Бра", "POINT"); lt.energy = 10; lt.color = (1.0, 0.88, 0.72); lt.shadow_soft_size = 0.08
    lo = bpy.data.objects.new("Бра", lt); lo.location = W(X1 - 0.21, zz, 1.60); sc.collection.objects.link(lo)

if KREM:
    import_bk("rastenie_bolshoe", X1 - 0.45, Z0 + 0.50, 0.0, 0, 1.65, "h")
    import_bk("tyulpany", X0 + 0.25, tm + 1.25, 0.645, 0, 0.38, "h")
else:
    import_ph("potted_plant_01", X0 + 0.40, Z0 + 0.55, 0.55)
_sofa = import_ph("Sofa_01", (sx0 + sx1) / 2, (sz0 + sz1) / 2, 2.30, -90)   # готовая модель дивана в стиле кресел
if _sofa:
    for o in list(sc.objects):
        if o.name.startswith(("Диван", "Подушка")) and o.type == "MESH": bpy.data.objects.remove(o, do_unlink=True)
_pz = (sz0 + sz1) / 2
# шторы: тюль на всю ширину + плотные по бокам, волной, из ниши до пола
def drape(name, a0, a1, zc, amp, waves, material):
    bm = bmesh.new(); nu, nv = max(24, int((a1 - a0) * 60)), 12; grid = []
    for j in range(nv + 1):
        h = 0.01 + (H + 0.09 - 0.01) * j / nv; row = []
        for i in range(nu + 1):
            x = a0 + (a1 - a0) * i / nu; z = zc + amp * math.sin(2 * math.pi * waves * i / nu)
            row.append(bm.verts.new(W(x, z, h)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    o = obj(name, bm, material)
    md = o.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.004
    for p in o.data.polygons: p.use_smooth = True
drape("Тюль", X0 + 0.03, X1 - 0.03, Z0 + 0.05, 0.025, (X1 - X0) / 0.12, M["tulle"])
drape("Штора лев", X0 + 0.02, WX0 + 0.18, Z0 + 0.11, 0.04, 6, M["drape"])
drape("Штора прав", WX1 - 0.18, X1 - 0.02, Z0 + 0.11, 0.04, 6, M["drape"])

# ---------------------------------------------------------------- свет
def area(name, loc, size, energy, rot=(0, 0, 0), color=(1.0, 0.9, 0.78), shape="RECTANGLE", sy=None):
    lt = bpy.data.lights.new(name, "AREA"); lt.energy = energy; lt.color = color; lt.shape = shape
    lt.size = size; lt.size_y = sy or size
    o = bpy.data.objects.new(name, lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
    return o
# дневной свет из окна (сцена «Обычный»: день + рамка 60% + периметр + бра)
area("Окно", W((WX0 + WX1) / 2, Z0 - 0.3, (WS + WT) / 2), WX1 - WX0, 6 if NIGHT else 220, rot=(math.radians(90), 0, 0), color=(1.0, 0.97, 0.94), sy=WT - WS)
# скрытая подсветка из карниза: свет вверх по потолку мягким ореолом (как на референсе)
for (sd, cxl, czl, sx_, sz_) in COVE:            # LED-лента на полке короба (за бортиком) — светит вверх и к центру
    rot = {"L": (math.radians(180), math.radians(35), 0), "R": (math.radians(180), math.radians(-35), 0),
           "B": (math.radians(180 - 35), 0, 0), "T": (math.radians(180 + 35), 0, 0)}[sd]
    area("Лента в коробе", W(cxl, czl, H - 0.062), sx_, 3.0 * max(sx_, sz_), rot=rot, sy=sz_, color=(1.0, 0.82, 0.6))
# световая рамка — дублируем тонкими area-лампами вниз (ровный расчётный свет)
for (cx, cz, sx, sz) in (((fa0 + fa1) / 2, fb0, fa1 - fa0, 0.04), ((fa0 + fa1) / 2, fb1, fa1 - fa0, 0.04),
                         (fa0, (fb0 + fb1) / 2, 0.04, fb1 - fb0), (fa1, (fb0 + fb1) / 2, 0.04, fb1 - fb0)):
    area("Рамка свет", W(cx, cz, H - 0.01), sx, 9 * max(sx, sz), sy=sz, color=(1.0, 0.95, 0.88))
sun = bpy.data.lights.new("Солнце", "SUN"); sun.energy = 0.0 if NIGHT else 2.2; sun.angle = math.radians(1.5); sun.color = (1.0, 0.97, 0.92)
so = bpy.data.objects.new("Солнце", sun); so.rotation_euler = (math.radians(58), 0, math.radians(200)); sc.collection.objects.link(so)
w = sc.world or bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get("Background"); bg.inputs[0].default_value = hexlin("#DCE6EE"); bg.inputs[1].default_value = 0.02 if NIGHT else 0.35

# ---------------------------------------------------------------- камеры (ракурсы)
cx = (X0 + X1) / 2
CAMS = [
    ("1_ot_dveri_k_oknu", W(X0 + 0.35, Z1 - 0.35, 1.45), W(X1 - 0.9, Z0 + 1.3, 1.0), 16),
    ("2_ot_okna_k_dveri", W(cx + 0.35, Z0 + 0.45, 1.45), W(cx - 0.5, Z1 - 0.4, 0.95), 16),
    ("3_divan_i_kresla", W(X0 + 0.35, tcz, 1.25), W(X1, tcz, 1.05), 18),
    ("4_tv_zona", W(sx0 - 0.15, tcz + 0.6, 1.20), W(X0, tm, 1.15), 18),
    ("7_kreslo", W(4.1, 3.75, 1.05), W(3.9, 2.0, 0.6), 30),
    ("6_detal_steny", W(X1 - 2.2, 3.9, 1.6), W(X1, 3.9, 1.75), 32),
    ("5_obshchiy_sverhu", W(X1 - 0.3, Z1 - 0.75, 2.4), W(cx - 0.4, Z0 + 1.8, 0.2), 15),
    ("8_potolok", W(X0 + 0.5, Z1 - 1.3, 1.1), W(X1 - 0.6, Z0 + 1.8, 2.75), 14),
    ("9_ugol_potolka", W(X0 + 1.2, Z1 - 1.6, 1.4), W(X0 + 0.2, Z1 - 0.4, 2.7), 22),
]
cams = []
for (n, loc, tgt, lens) in CAMS:
    cd = bpy.data.cameras.new(n); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02
    co = bpy.data.objects.new(n, cd); co.location = loc
    co.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(co)
    cams.append((n, co))

# ---------------------------------------------------------------- рендер
sc.render.engine = "CYCLES"
cy = sc.cycles
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    for dev in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = dev; pr.get_devices()
            for d in pr.devices: d.use = True
            cy.device = "GPU"; break
        except Exception: continue
except Exception: pass
cy.samples = 48 if QUICK else 128
cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 8; cy.diffuse_bounces = 4
sc.render.resolution_x, sc.render.resolution_y = (960, 540) if QUICK else (1920, 1080)
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 92
try: sc.view_settings.view_transform = "AgX"
except Exception: sc.view_settings.view_transform = "Filmic"
sc.view_settings.exposure = -0.9 if NIGHT else -0.35
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
def set_col(m, hx):
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = hexlin(hx)
def lighter(hx, k=1.03):
    h = hx.lstrip("#"); return "#" + "".join(f"{min(255, int(int(h[i:i+2], 16) * k)):02X}" for i in (0, 2, 4))
if VARIANTS:
    VL = json.load(open(VARIANTS, encoding="utf-8")); vd = os.path.join(OUT, "varianty"); os.makedirs(vd, exist_ok=True)
    sc.camera = cams[0][1]
    for k, v in enumerate(VL, 1):
        FL = v["floor"].split("-"); FLOOR_IMG.user_clear(); bpy.data.images.remove(FLOOR_IMG)
        newm = floor_mat()
        for o in sc.objects:
            if o.name.startswith("Пол") and o.type == "MESH": o.data.materials[0] = newm
        set_col(M["wall"], v["wall"]); set_col(M["mold"], lighter(v["wall"]))
        set_col(M["tumba"], v.get("cab") or lighter(v["wall"], 1.02))
        set_col(M["drape"], v["drape"])
        if v.get("rug"): set_col(M["rug"], v["rug"])
        if v.get("tulle"): set_col(M["tulle"], v["tulle"])
        sc.render.filepath = os.path.join(vd, f"{k:02d}.jpg"); bpy.ops.render.render(write_still=True)
        print("VARIANT", k)
    raise SystemExit
for i, (n, co) in enumerate(cams, 1):
    if SHOTS and i not in SHOTS: continue
    sc.camera = co
    sc.render.filepath = os.path.join(OUT, ("q_" if QUICK else "") + TAG + VAR + ("_" + SOFA[1:] if SOFA else "") + ("_" + CHAIR[1:] if CHAIR else "") + "_" + n + ".jpg")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)
