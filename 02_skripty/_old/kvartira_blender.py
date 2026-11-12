# -*- coding: utf-8 -*-
"""Квартира 100 м² (Казакон) — сцена и рендеры для Blender 3.6 / 4.x / 5.x.
Запуск: Blender → вкладка Scripting → Open → kvartira.py → Run Script.
Гостиная — неоклассика; комната, спальня, кухня, коридор, прихожая — рифлёные бамбуковые
панели; ванная и санузел — керамогранит. Размеры — из альбома (план, ±1–3 см).
"""
import bpy, bmesh, math, os, random
import numpy as np
from mathutils import Vector, Matrix

# ---------------------------------------------------------------- настройки
QUICK = False            # True — быстрый черновик (маленькое разрешение, мало сэмплов)
SHOTS = "all"            # "all" или список номеров, например [1, 2, 3]
RENDER = True            # False — только собрать сцену
OUT = os.path.join(os.path.expanduser("~"), "Documents", "kvartira_render")
H = 2.7                  # высота потолка

# ---------------------------------------------------------------- геометрия (план, м: x вправо, z вниз)
WALLS = [[1.655, 0.0, 1.018, 0.309], [4.836, 0.0, 1.436, 0.309], [8.436, 0.0, 0.836, 0.309], [10.327, 0.0, 0.436, 0.309], [1.655, 0.309, 0.291, 6.491], [5.545, 0.309, 0.2, 6.364], [8.945, 0.309, 0.2, 0.236], [10.455, 0.309, 0.309, 1.6], [8.945, 1.345, 0.2, 5.327], [10.764, 1.6, 0.273, 0.309], [12.636, 1.6, 0.673, 0.309], [9.145, 1.818, 1.309, 0.091], [13.0, 1.909, 0.309, 2.418], [13.309, 2.018, 1.745, 0.309], [13.309, 2.327, 0.436, 2.0], [14.745, 2.327, 0.309, 0.236], [14.745, 3.327, 0.309, 2.291], [13.745, 3.545, 0.145, 0.091], [14.618, 3.545, 0.127, 0.091], [9.945, 4.2, 3.055, 0.127], [9.945, 4.327, 0.127, 2.273], [9.145, 5.745, 0.009, 0.8], [9.155, 5.755, 0.027, 0.791], [0.0, 6.509, 1.091, 0.291], [1.564, 6.509, 0.091, 0.291], [1.091, 6.545, 0.473, 0.255], [1.945, 6.545, 0.2, 0.127], [2.945, 6.545, 2.6, 0.127], [5.745, 6.545, 2.4, 0.127], [0.0, 6.8, 0.309, 2.527], [1.836, 6.8, 0.109, 0.2], [14.745, 7.182, 0.309, 0.6], [9.945, 7.4, 0.127, 1.218], [10.073, 7.491, 4.673, 0.291], [1.836, 7.8, 0.109, 2.0], [3.455, 7.909, 0.8, 0.109], [5.055, 7.909, 1.309, 0.109], [3.455, 8.018, 0.109, 1.782], [6.073, 8.018, 0.291, 1.782], [6.364, 8.418, 1.836, 0.091], [8.964, 8.418, 0.982, 0.091], [6.364, 8.509, 0.036, 0.109], [9.909, 8.509, 0.036, 0.109], [6.4, 8.527, 1.8, 0.091], [8.964, 8.527, 0.945, 0.091], [0.309, 9.018, 1.527, 0.309], [1.655, 9.327, 0.182, 0.473], [1.945, 9.509, 0.309, 0.291], [3.145, 9.509, 0.309, 0.291], [3.564, 9.509, 2.509, 0.291], [8.1818, 8.4727, 0.7818, 0.2364]]
WINDOWS = [[2.673, 0.018, 2.164, 0.273], [6.273, 0.018, 2.164, 0.273], [9.273, 0.018, 1.055, 0.273], [11.036, 1.618, 1.6, 0.273], [14.764, 2.564, 0.273, 0.764], [14.764, 5.618, 0.273, 1.564]]
ROOMS = {"Гостиная": (1.946, 5.545, 0.309, 6.545), "Комната": (5.745, 8.945, 0.309, 6.545), "Кухня": (9.145, 13.0, 1.909, 4.2),
         "Спальня 2": (10.072, 14.745, 4.327, 7.491), "Коридор": (1.945, 9.945, 6.672, 7.909), "Прихожая": (1.945, 3.455, 7.909, 9.509),
         "Ванная": (3.564, 6.073, 8.018, 9.509), "Санузел": (0.309, 1.836, 6.8, 9.018)}
NEO = ["Гостиная"]
BAMBOO = ["Комната", "Спальня 2", "Коридор", "Прихожая"]
WET = ["Ванная", "Санузел"]
# двери: (x, z, w, d в плане), тип
DOORS = [((2.145, 6.545, 0.8, 0.127), "neo"), ((8.145, 6.545, 0.8, 0.127), "std"), ((1.836, 7.0, 0.109, 0.8), "std"),
         ((4.255, 7.909, 0.8, 0.109), "std"), ((9.945, 6.6, 0.127, 0.8), "std"), ((9.145, 4.2, 0.8, 0.127), "open"),
         ((2.254, 9.509, 0.891, 0.291), "entry"), ((8.945, 0.545, 0.2, 0.8), "glass")]

# ---------------------------------------------------------------- очистка сцены
for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images, bpy.data.curves):
    for b in list(coll):
        try: coll.remove(b)
        except Exception: pass
scene = bpy.context.scene
for c in list(scene.collection.children):
    bpy.data.collections.remove(c)
def mkcoll(n):
    c = bpy.data.collections.new(n); scene.collection.children.link(c); return c
C_ARCH, C_FIN, C_FURN, C_LIGHT, C_CAM, C_CUT = [mkcoll(n) for n in ("Архитектура", "Отделка", "Мебель", "Свет", "Камеры", "Вырезы")]
C_CUT.hide_render = True
random.seed(7)

# ---------------------------------------------------------------- цвета и материалы
def lin(hexc):
    hexc = hexc.lstrip("#"); out = []
    for i in (0, 2, 4):
        u = int(hexc[i:i + 2], 16) / 255
        out.append(u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)

def setin(node, names, val):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = val; return

def mat(name, color, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = lin(color) if isinstance(color, str) else color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat: setin(b, ["Coat Weight", "Clearcoat"], coat)
    m.diffuse_color = lin(color) if isinstance(color, str) else color
    return m

def emit_mat(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = lin(color); e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o.inputs["Surface"]); return m

def glass_mat(name, tint="#EEF4F6", transp=0.88):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    t = nt.nodes.new("ShaderNodeBsdfTransparent"); t.inputs["Color"].default_value = lin(tint)
    g = nt.nodes.new("ShaderNodeBsdfGlossy"); g.inputs["Roughness"].default_value = 0.02
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 1 - transp
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(g.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o.inputs["Surface"])
    try: m.blend_method = "BLEND"
    except Exception: pass
    return m

# ---------------------------------------------------------------- процедурные текстуры (numpy)
def h2(a, b, salt=0):
    v = (a.astype(np.int64) * 73856093) ^ (b.astype(np.int64) * 19349663) ^ (salt * 83492791)
    return (v % 10007) / 10007.0

def np_image(name, arr):
    hgt, wid, _ = arr.shape
    img = bpy.data.images.new(name, wid, hgt, alpha=False)
    rgba = np.ones((hgt, wid, 4), np.float32); rgba[:, :, :3] = np.clip(arr, 0, 1)
    img.pixels.foreach_set(rgba.ravel())
    try: img.pack()
    except Exception: pass
    return img

def grid(wpx, hpx, mw, mh):
    xs = (np.arange(wpx) + 0.5) / wpx * mw; ys = (np.arange(hpx) + 0.5) / hpx * mh
    return np.meshgrid(xs, ys)

def tex_herringbone(size=1536, meters=1.6, W=0.4, Pp=0.16):
    X, Y = grid(size, size, meters, meters)
    c = np.floor(X / W).astype(np.int64); xl = X - c * W; d = np.where(c % 2 == 0, 1.0, -1.0)
    t = (Y + d * xl) / Pp; pid = np.floor(t).astype(np.int64); fr = t - pid
    nc = int(round(meters / W)); npid = int(round(meters / Pp))
    h = h2(c % nc, pid % npid)
    base = np.array([0.68, 0.52, 0.37])
    tone = 0.86 + 0.26 * h
    along = (X * 0.7071 - d * Y * 0.7071)
    grain = 0.035 * np.sin(2 * np.pi * (fr * 11 + h * 7 + 0.25 * np.sin(along * 9 + h * 20)))
    knot = 0.05 * np.exp(-((fr - 0.5) ** 2) / 0.02) * (h > 0.85)
    arr = base[None, None, :] * (tone + grain - knot)[..., None]
    seam = (fr < 0.014) | (fr > 0.986) | (xl < 0.0025) | (xl > W - 0.0025)
    arr[seam] *= 0.55
    return arr

def tex_planks(size=1536, meters=2.4, L=1.2, Wd=0.2, base=(0.66, 0.50, 0.36)):
    X, Y = grid(size, size, meters, meters)
    row = np.floor(Y / Wd).astype(np.int64); off = ((row * 0.37) % 1.0) * L
    col = np.floor((X + off) / L).astype(np.int64)
    h = h2(col % int(round(meters / L)), row % int(round(meters / Wd)))
    fy = Y / Wd - row; fx = (X + off) / L - col
    tone = 0.88 + 0.22 * h
    grain = 0.04 * np.sin(2 * np.pi * (fy * 9 + h * 7 + 0.3 * np.sin(X * 2.6 + h * 10)))
    arr = np.array(base)[None, None, :] * (tone + grain)[..., None]
    seam = (fy < 0.01) | (fy > 0.99) | (fx < 0.0025) | (fx > 0.9975)
    arr[seam] *= 0.6
    return arr

def tex_stone(size=1536, meters=1.2, T=0.6, TL=1.2, base=(0.93, 0.915, 0.89), joints=True):
    """Итальянский керамогранит под мрамор (тёплый калакатта), 600×1200, ректифицированный шов 1,5 мм."""
    X, Y = grid(size, size, meters, meters)
    rng = np.random.default_rng(7)
    def fbm(Xs, Ys, oct=5):
        v = np.zeros_like(Xs)
        for o in range(oct):
            f = 2 ** o
            for _ in range(2):
                kx, ky = rng.integers(-2, 3, 2) * f + rng.integers(1, 3) * f
                v += np.sin(2 * np.pi * (kx * Xs + ky * Ys) / meters + rng.random() * 6.28) / (f * 1.6)
        return v
    w = fbm(X, Y, 2) * 0.5
    t1 = (X * 0.55 + Y * 0.85) / meters * 2.0 + w * 0.35
    t2 = (X * 0.9 - Y * 0.3) / meters * 1.3 + fbm(X, Y, 2) * 0.25
    vein1 = np.exp(-np.abs(np.sin(np.pi * t1)) * 70) + 0.35 * np.exp(-np.abs(np.sin(np.pi * t1 * 3.1 + 0.7)) * 120)
    vein2 = 0.6 * np.exp(-np.abs(np.sin(np.pi * t2)) * 90)
    cloud = 0.02 * fbm(X, Y, 2)
    tint = np.array([0.66, 0.63, 0.60])
    v = np.clip(vein1 + vein2, 0, 1)
    arr = np.array(base)[None, None, :] * (1 + cloud)[..., None]
    arr = arr * (1 - 0.5 * v[..., None]) + tint[None, None, :] * (0.5 * v)[..., None]
    if joints:
        fxm = X % T; fym = Y % TL
        joint = (fxm < 0.0012) | (fxm > T - 0.0012) | (fym < 0.0012) | (fym > TL - 0.0012)
        arr[joint] = np.array([0.80, 0.79, 0.77])
    return arr

def tex_travertine_slab(size=1536, meters=1.2):
    return tex_stone(size, meters, joints=False)

def tex_bamboo(wpx=720, hpx=3072, mw=0.6, mh=2.56):
    """Ламель: молочно-серый, тонкие продольные волокна, лёгкая разница тона (текстура на каждую ламель по UV)."""
    X, Y = grid(wpx, hpx, mw, mh)
    rng = np.random.default_rng(5)
    base = np.array([0.86, 0.84, 0.80])
    fib = 0.018 * np.sin(2 * np.pi * (X * 140 + 0.6 * np.sin(Y * 2.3))) + 0.012 * np.sin(2 * np.pi * (X * 410 + Y * 0.9))
    lowf = 0.02 * np.sin(2 * np.pi * (Y / mh * 3 + X * 4))
    noise = rng.normal(0, 0.008, X.shape)
    return base[None, None, :] * (0.97 + fib + lowf + noise)[..., None]

# ---------------------------------------------------------------- материалы со «знанием» зон
def node(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items(): setattr(n, k, v)
    return n

def region_factor(nt, pos_sep, rects, pad=0.035):
    """1 внутри любого прямоугольника плана (x0,x1,z0,z1), иначе 0. Блендер y = -z плана."""
    acc = None
    for (x0, x1, z0, z1) in rects:
        parts = []
        for (comp, op, val) in ((0, "GREATER_THAN", x0 - pad), (0, "LESS_THAN", x1 + pad), (1, "LESS_THAN", -(z0 - pad)), (1, "GREATER_THAN", -(z1 + pad))):
            m = node(nt, "ShaderNodeMath", operation=op); nt.links.new(pos_sep.outputs[comp], m.inputs[0]); m.inputs[1].default_value = val; parts.append(m)
        prod = parts[0]
        for q in parts[1:]:
            mm = node(nt, "ShaderNodeMath", operation="MULTIPLY"); nt.links.new(prod.outputs[0], mm.inputs[0]); nt.links.new(q.outputs[0], mm.inputs[1]); prod = mm
        if acc is None: acc = prod
        else:
            mx = node(nt, "ShaderNodeMath", operation="MAXIMUM"); nt.links.new(acc.outputs[0], mx.inputs[0]); nt.links.new(prod.outputs[0], mx.inputs[1]); acc = mx
    return acc

def img_bsdf(nt, img, vec_socket, scale, rough, bump=0.0, coat=0.0):
    mp = node(nt, "ShaderNodeMapping"); nt.links.new(vec_socket, mp.inputs["Vector"]); mp.inputs["Scale"].default_value = scale
    tx = node(nt, "ShaderNodeTexImage"); tx.image = img; tx.extension = "REPEAT"; nt.links.new(mp.outputs[0], tx.inputs["Vector"])
    b = node(nt, "ShaderNodeBsdfPrincipled"); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    if coat: setin(b, ["Coat Weight", "Clearcoat"], coat)
    if bump:
        bp = node(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.002
        nt.links.new(tx.outputs["Color"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    return b

def plain_bsdf(nt, color, rough):
    b = node(nt, "ShaderNodeBsdfPrincipled"); b.inputs["Base Color"].default_value = lin(color); b.inputs["Roughness"].default_value = rough; return b

def fresh(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    tc = node(nt, "ShaderNodeTexCoord"); sp = node(nt, "ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    out = node(nt, "ShaderNodeOutputMaterial")
    return m, nt, tc, sp, out

IMG_HB = np_image("herringbone", tex_herringbone())
IMG_PL = np_image("planks", tex_planks())
IMG_ST = np_image("stone", tex_stone())
IMG_BB = np_image("bamboo", tex_bamboo())
IMG_TR = np_image("travertine", tex_travertine_slab())

R_NEO = [ROOMS[r] for r in NEO]; R_WET = [ROOMS[r] for r in WET]

def wall_material():
    m, nt, tc, sp, out = fresh("Стены")
    paint_neo = plain_bsdf(nt, "#EEE5D6", 0.85)
    paint_oth = plain_bsdf(nt, "#EDE3D3", 0.85)
    # плитка на вертикальных гранях: u = x + y, v = z
    ad = node(nt, "ShaderNodeMath", operation="ADD"); nt.links.new(sp.outputs[0], ad.inputs[0]); nt.links.new(sp.outputs[1], ad.inputs[1])
    cb = node(nt, "ShaderNodeCombineXYZ"); nt.links.new(ad.outputs[0], cb.inputs[0]); nt.links.new(sp.outputs[2], cb.inputs[1])
    tile = img_bsdf(nt, IMG_ST, cb.outputs[0], (1 / 1.2, 1 / 1.2, 1), 0.18, bump=0.15, coat=0.3)
    f_neo = region_factor(nt, sp, R_NEO); f_wet = region_factor(nt, sp, R_WET, pad=0.03)
    m1 = node(nt, "ShaderNodeMixShader"); nt.links.new(f_neo.outputs[0], m1.inputs[0]); nt.links.new(paint_oth.outputs[0], m1.inputs[1]); nt.links.new(paint_neo.outputs[0], m1.inputs[2])
    m2 = node(nt, "ShaderNodeMixShader"); nt.links.new(f_wet.outputs[0], m2.inputs[0]); nt.links.new(m1.outputs[0], m2.inputs[1]); nt.links.new(tile.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"]); m.diffuse_color = lin("#E4DACB"); return m

def floor_material():
    m, nt, tc, sp, out = fresh("Пол")
    hb = img_bsdf(nt, IMG_HB, tc.outputs["Object"], (1 / 1.6, 1 / 1.6, 1), 0.38, bump=0.25, coat=0.15)
    pl = img_bsdf(nt, IMG_PL, tc.outputs["Object"], (1 / 2.4, 1 / 2.4, 1), 0.42, bump=0.25)
    st = img_bsdf(nt, IMG_ST, tc.outputs["Object"], (1 / 1.2, 1 / 1.2, 1), 0.22, bump=0.15, coat=0.2)
    f_neo = region_factor(nt, sp, R_NEO, pad=0.0); f_wet = region_factor(nt, sp, R_WET, pad=0.0)
    m1 = node(nt, "ShaderNodeMixShader"); nt.links.new(f_neo.outputs[0], m1.inputs[0]); nt.links.new(pl.outputs[0], m1.inputs[1]); nt.links.new(hb.outputs[0], m1.inputs[2])
    m2 = node(nt, "ShaderNodeMixShader"); nt.links.new(f_wet.outputs[0], m2.inputs[0]); nt.links.new(m1.outputs[0], m2.inputs[1]); nt.links.new(st.outputs[0], m2.inputs[2])
    nt.links.new(m2.outputs[0], out.inputs["Surface"]); return m

def travertine_material():
    m, nt, tc, sp, out = fresh("Керамогранит слэб")
    ad = node(nt, "ShaderNodeMath", operation="ADD"); nt.links.new(sp.outputs[0], ad.inputs[0]); nt.links.new(sp.outputs[1], ad.inputs[1])
    cb = node(nt, "ShaderNodeCombineXYZ"); nt.links.new(ad.outputs[0], cb.inputs[0]); nt.links.new(sp.outputs[2], cb.inputs[1])
    b = img_bsdf(nt, IMG_TR, cb.outputs[0], (1 / 1.2, 1 / 1.2, 1), 0.3, bump=0.2, coat=0.2)
    nt.links.new(b.outputs[0], out.inputs["Surface"]); m.diffuse_color = lin("#DCCFBA"); return m

def bamboo_material():
    m = bpy.data.materials.new("Бамбуковые ламели"); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    uv = node(nt, "ShaderNodeUVMap")
    tx = node(nt, "ShaderNodeTexImage"); tx.image = IMG_BB; nt.links.new(uv.outputs[0], tx.inputs["Vector"])
    b = node(nt, "ShaderNodeBsdfPrincipled"); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.45
    setin(b, ["Coat Weight", "Clearcoat"], 0.12)
    bp = node(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; bp.inputs["Distance"].default_value = 0.0008
    nt.links.new(tx.outputs["Color"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    o = node(nt, "ShaderNodeOutputMaterial"); nt.links.new(b.outputs[0], o.inputs["Surface"]); m.diffuse_color = lin("#DAD5CC"); return m

M = {
    "wall": wall_material(), "floor": floor_material(), "bamboo": bamboo_material(), "felt": mat("Подложка", "#3E3B37", 0.95), "travertine": travertine_material(),
    "ceil": mat("Потолок", "#F6F3EE", 0.9), "trim": mat("Белый молдинг", "#F7F4EE", 0.45),
    "base_b": mat("Плинтус", "#D6D0C6", 0.5), "front": mat("Фасады", "#EAE2D5", 0.5), "front_low": mat("Фасады мокко", "#6E5646", 0.45),
    "front_neo": mat("Фасады неоклассика", "#F1ECE3", 0.4), "oak": mat("Дуб", "#A98B6C", 0.5),
    "black": mat("Чёрный матовый", "#1E1D1A", 0.45), "steel": mat("Сталь", "#8E8A86", 0.3, 0.9),
    "brass": mat("Латунь", "#B08D57", 0.28, 1.0), "ceramic": mat("Керамика", "#F7F7F5", 0.08, coat=0.6),
    "fab_cream": mat("Ткань крем", "#E7DCCB", 0.95), "fab_sand": mat("Ткань песок", "#CBB8A0", 0.95), "fab_main": mat("Ткань карамель", "#A47A57", 0.95), "fab_accent": mat("Ткань олива", "#77744A", 0.95),
    "fab_grey": mat("Ткань серо-беж", "#B9AFA3", 0.95), "rug": mat("Ковёр", "#DED3C2", 1.0),
    "marble": mat("Мрамор стол", "#ECE8E2", 0.15, coat=0.5), "plastic": mat("Пластик белый", "#F2F1EE", 0.35),
    "tv": mat("Экран", "#0C0C0E", 0.08), "pvc": mat("Рама окна", "#F4F4F2", 0.4),
    "mirror": mat("Зеркало", "#FFFFFF", 0.0, 1.0), "glass": glass_mat("Стекло окна"),
    "glass_sh": glass_mat("Стекло душа", "#F2F7F7", 0.93), "tulle": glass_mat("Тюль", "#FFFDF8", 0.55),
    "door": mat("Двери", "#E8DFD2", 0.5), "entry": mat("Входная дверь", "#3A3530", 0.5),
    "bulb": emit_mat("Лампа", "#FFE6C4", 25.0), "opal": emit_mat("Опал", "#FFF1DE", 4.0), "led": emit_mat("LED подсветка", "#FFE2BE", 5.0),
    "washer_door": mat("Дверца стиралки", "#2B2E31", 0.1),
}

# ---------------------------------------------------------------- построители мешей (вершины в мировых координатах)
def W(x, z, h): return Vector((x, -z, h))

def to_obj(name, bm, material, coll, smooth=False, bevel=0.0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    if bevel:
        md = ob.modifiers.new("Фаска", "BEVEL"); md.width = bevel; md.segments = 2
        try: md.limit_method = "ANGLE"
        except Exception: pass
    return ob

def box(name, x, z, w, d, h0, hh, material, coll=None, bevel=0.0):
    coll = coll or C_FURN
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = W(x + (v.co.x + 0.5) * w, z + (v.co.y + 0.5) * d, h0 + (v.co.z + 0.5) * hh)
    return to_obj(name, bm, material, coll, bevel=bevel)

def cyl(name, cx, cz, r, h0, hh, material, coll=None, seg=40, axis="Z", rz=None, smooth=True):
    coll = coll or C_FURN
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if rz is None else rz, depth=hh)
    if axis == "X": bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
    if axis == "Y": bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=W(cx, cz, h0 + (hh / 2 if axis == "Z" else 0)))
    return to_obj(name, bm, material, coll, smooth=smooth)

def ellipsoid(name, cx, cz, h, rx, rz, rh, material, coll=None):
    coll = coll or C_FURN
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0)
    for v in bm.verts: v.co = Vector((cx + v.co.x * rx, -(cz + v.co.y * rz), h + v.co.z * rh))
    return to_obj(name, bm, material, coll, smooth=True)

def plane_h(name, x0, x1, z0, z1, h, material, coll, down=False):
    bm = bmesh.new()
    vs = [bm.verts.new(W(x, z, h)) for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))]
    f = bm.faces.new(vs if down else vs[::-1]); return to_obj(name, bm, material, coll)

def cut(target, cutter):
    md = target.modifiers.new("Вырез", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cutter
    for c in list(cutter.users_collection): c.objects.unlink(cutter)
    C_CUT.objects.link(cutter); cutter.hide_render = True; cutter.display_type = "WIRE"

# ---------------------------------------------------------------- стены, окна, двери, пол, потолок
for i, (x, z, w, d) in enumerate(WALLS):
    box(f"Стена {i}", x, z, w, d, 0, H, M["wall"], C_ARCH)
for i, (x, z, w, d) in enumerate(WINDOWS):
    box(f"Подоконная часть {i}", x, z, w, d, 0, 0.9, M["wall"], C_ARCH)
    box(f"Надоконная часть {i}", x, z, w, d, 2.4, H - 2.4, M["wall"], C_ARCH)
    horiz = w > d; fr = 0.065
    if horiz:
        gz = z + d * 0.45; gd = 0.07
        box(f"Стекло {i}", x, gz, w, 0.02, 0.9, 1.5, M["glass"], C_ARCH)
        for (a, b) in ((x, x + fr), (x + w - fr, x + w), (x + w / 2 - fr / 2, x + w / 2 + fr / 2)):
            box(f"Рама {i}", a, gz - 0.025, b - a, gd, 0.9, 1.5, M["pvc"], C_ARCH)
        for hh in (0.9, 2.4 - fr):
            box(f"Рама {i}", x, gz - 0.025, w, gd, hh, fr, M["pvc"], C_ARCH)
        box(f"Подоконник {i}", x - 0.03, z + d - 0.01, w + 0.06, 0.06 + 0.01, 0.88, 0.03, M["pvc"], C_ARCH, bevel=0.004)
    else:
        gx = x + w * 0.45
        box(f"Стекло {i}", gx, z, 0.02, d, 0.9, 1.5, M["glass"], C_ARCH)
        for (a, b) in ((z, z + fr), (z + d - fr, z + d)):
            box(f"Рама {i}", gx - 0.025, a, 0.07, b - a, 0.9, 1.5, M["pvc"], C_ARCH)
        for hh in (0.9, 2.4 - fr):
            box(f"Рама {i}", gx - 0.025, z, 0.07, d, hh, fr, M["pvc"], C_ARCH)
        box(f"Подоконник {i}", x - 0.07, z - 0.03, 0.08, d + 0.06, 0.88, 0.03, M["pvc"], C_ARCH, bevel=0.004)

for (x, z, w, d), kind in DOORS:
    hd = 2.1
    box("Перемычка", x, z, w, d, hd, H - hd, M["wall"], C_ARCH)
    along_x = w > d
    if kind in ("std", "neo", "entry"):
        th = 0.04
        if along_x: lx, lz, lw, ld = x + 0.01, z + d / 2 - th / 2, w - 0.02, th
        else: lx, lz, lw, ld = x + w / 2 - th / 2, z + 0.01, th, d - 0.02
        mdoor = M["entry"] if kind == "entry" else (M["trim"] if kind == "neo" else M["door"])
        box("Дверное полотно", lx, lz, lw, ld, 0.01, hd - 0.02, mdoor, C_ARCH, bevel=0.003)
        # ручка
        if along_x:
            for s in (-1, 1):
                box("Ручка", x + w - 0.12, z + d / 2 + s * 0.035 - 0.01, 0.1, 0.02, 1.0, 0.02, M["brass"] if kind == "neo" else M["black"], C_FURN)
        else:
            for s in (-1, 1):
                box("Ручка", x + w / 2 + s * 0.035 - 0.01, z + d - 0.12, 0.02, 0.1, 1.0, 0.02, M["black"], C_FURN)
        if kind == "neo":   # филёнки на полотне (обе стороны)
            for s in (-1, 1):
                fz = z + d / 2 + s * (th / 2 + 0.004) - 0.004
                for (h0, hh) in ((0.15, 0.75), (1.05, 0.85)):
                    for (a, b, hb, hbh) in ((x + 0.12, x + 0.14, h0, hh), (x + w - 0.14, x + w - 0.12, h0, hh)):
                        box("Филёнка", a, fz, b - a, 0.008, hb, hbh, M["trim"], C_FIN)
                    for hb in (h0, h0 + hh - 0.02):
                        box("Филёнка", x + 0.12, fz, w - 0.24, 0.008, hb, 0.02, M["trim"], C_FIN)
    elif kind == "glass":
        box("Стеклянная дверь", x + w * 0.45, z, 0.02, d, 0.0, hd, M["glass"], C_ARCH)
        box("Рама двери", x + w * 0.45 - 0.025, z, 0.07, 0.06, 0.0, hd, M["pvc"], C_ARCH)
        box("Рама двери", x + w * 0.45 - 0.025, z + d - 0.06, 0.07, 0.06, 0.0, hd, M["pvc"], C_ARCH)

EXTRA = [(6.0, 9.945, 7.909, 8.418), (9.145, 10.073, 4.2, 6.672), (13.745, 14.745, 3.545, 4.327)]
FL = list(ROOMS.values()) + EXTRA + [(x, x + w, z, z + d) for (x, z, w, d), k in DOORS if k != "glass"]
for i, (x0, x1, z0, z1) in enumerate(FL):
    plane_h(f"Пол {i}", x0, x1, z0, z1, 0.0, M["floor"], C_ARCH, down=False)
    plane_h(f"Потолок {i}", x0, x1, z0, z1, H, M["ceil"], C_ARCH, down=True)
plane_h("Пол ниши", 8.945, 10.455, 0.309, 1.818, 0.0, M["floor"], C_ARCH)

# ---------------------------------------------------------------- анализ стен по периметру комнаты
def in_rect(px, pz, r):
    x, z, w, d = r; return x <= px <= x + w and z <= pz <= z + d

def classify(px, pz):
    for r in WINDOWS:
        if in_rect(px, pz, r): return "win"
    for (r, k) in DOORS:
        if in_rect(px, pz, r): return "door"
    for r in WALLS:
        if in_rect(px, pz, r): return "wall"
    return "gap"

SIDES = {"T": ((1, 0), (0, 1)), "B": ((1, 0), (0, -1)), "L": ((0, 1), (1, 0)), "R": ((0, 1), (-1, 0))}

def side_base(room, side):
    x0, x1, z0, z1 = ROOMS[room]
    return {"T": ((x0, z0), (x0, x1)), "B": ((x0, z1), (x0, x1)), "L": ((x0, z0), (z0, z1)), "R": ((x1, z0), (z0, z1))}[side]

def segments(room, side, off=0.03, step=0.01):
    (bx, bz), (a0, a1) = side_base(room, side); (ax, az), (nx, nz) = SIDES[side]
    segs = []; a = a0 + step / 2
    while a < a1:
        px = (a if ax else bx) - nx * off; pz = (a if az else bz) - nz * off
        k = classify(px, pz)
        if segs and segs[-1][0] == k: segs[-1][2] = a + step / 2
        else: segs.append([k, a - step / 2, a + step / 2])
        a += step
    if segs: segs[0][1] = a0; segs[-1][2] = a1
    return segs

def on_wall(room, side, a0, a1, n0, n1, h0, h1, material, coll, name="Деталь", bevel=0.0):
    """Брусок вдоль стороны комнаты: по длине a0..a1, от стены n0..n1 внутрь, по высоте h0..h1."""
    (bx, bz), _ = side_base(room, side); (ax, az), (nx, nz) = SIDES[side]
    if ax:   # вдоль x
        z_a = bz + nz * n0; z_b = bz + nz * n1
        return box(name, a0, min(z_a, z_b), a1 - a0, abs(z_b - z_a), h0, h1 - h0, material, coll, bevel)
    x_a = bx + nx * n0; x_b = bx + nx * n1
    return box(name, min(x_a, x_b), a0, abs(x_b - x_a), a1 - a0, h0, h1 - h0, material, coll, bevel)

SEG = {r: {s: segments(r, s) for s in "TBLR"} for r in ROOMS}

# ---------------------------------------------------------------- неоклассика (гостиная)
def neo_room(room):
    x0, x1, z0, z1 = ROOMS[room]
    for side in "TBLR":
        for (k, a0, a1) in SEG[room][side]:
            if k in ("wall",):
                on_wall(room, side, a0, a1, 0, 0.016, 0, 0.12, M["trim"], C_FIN, "Плинтус", 0.003)
                on_wall(room, side, a0, a1, 0, 0.022, 0.12, 0.135, M["trim"], C_FIN, "Плинтус профиль", 0.003)
            if k in ("wall", "win", "door"):
                on_wall(room, side, a0, a1, 0, 0.07, H - 0.08, H, M["trim"], C_FIN, "Карниз", 0.004)
                on_wall(room, side, a0, a1, 0, 0.035, H - 0.13, H - 0.08, M["trim"], C_FIN, "Карниз ступень", 0.003)
                on_wall(room, side, a0, a1, 0, 0.012, H - 0.30, H - 0.27, M["trim"], C_FIN, "Фриз", 0.002)
            if k == "wall":
                L = a1 - a0 - 0.30
                if L < 0.45: continue
                n = max(1, round(L / 1.15)); gap = 0.18
                fw = (a1 - a0 - gap * (n + 1)) / n
                for i in range(n):
                    s0 = a0 + gap + i * (fw + gap); s1 = s0 + fw
                    for (hb, ht) in ((0.32, 0.92), (1.08, 2.28)):
                        p = 0.035
                        on_wall(room, side, s0, s1, 0, 0.014, hb, hb + p, M["trim"], C_FIN, "Молдинг", 0.004)
                        on_wall(room, side, s0, s1, 0, 0.014, ht - p, ht, M["trim"], C_FIN, "Молдинг", 0.004)
                        on_wall(room, side, s0, s0 + p, 0, 0.014, hb, ht, M["trim"], C_FIN, "Молдинг", 0.004)
                        on_wall(room, side, s1 - p, s1, 0, 0.014, hb, ht, M["trim"], C_FIN, "Молдинг", 0.004)
    # потолочная рамка и розетка
    inset = 0.45
    for (a, b, c, d) in ((x0 + inset, x1 - inset, z0 + inset, z0 + inset + 0.05), (x0 + inset, x1 - inset, z1 - inset - 0.05, z1 - inset),
                         (x0 + inset, x0 + inset + 0.05, z0 + inset, z1 - inset), (x1 - inset - 0.05, x1 - inset, z0 + inset, z1 - inset)):
        box("Потолочный молдинг", a, c, b - a, d - c, H - 0.02, 0.02, M["trim"], C_FIN)
    cx, cz = (x0 + x1) / 2, 3.45
    cyl("Розетка потолка", cx, cz, 0.32, H - 0.03, 0.03, M["trim"], C_FIN)
    cyl("Розетка потолка 2", cx, cz, 0.22, H - 0.05, 0.02, M["trim"], C_FIN)
    chandelier(cx, cz)

def chandelier(cx, cz):
    cyl("Люстра штанга", cx, cz, 0.012, 1.95, H - 1.95, M["brass"])
    ellipsoid("Люстра центр", cx, cz, 1.92, 0.07, 0.07, 0.09, M["brass"])
    for i in range(8):
        a = i / 8 * 2 * math.pi; r = 0.38
        px, pz = cx + r * math.cos(a), cz + r * math.sin(a)
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.008, radius2=0.008, depth=r)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-a, 3, "Z"))
        bmesh.ops.translate(bm, verts=bm.verts, vec=W(cx + r / 2 * math.cos(a), cz + r / 2 * math.sin(a), 1.88))
        to_obj("Люстра рожок", bm, M["brass"], C_FURN, smooth=True)
        cyl("Чашка", px, pz, 0.035, 1.87, 0.03, M["brass"])
        cyl("Свеча", px, pz, 0.014, 1.90, 0.11, M["fab_cream"])
        ellipsoid("Лампочка", px, pz, 2.04, 0.018, 0.018, 0.03, M["bulb"])
    L = bpy.data.lights.new("Люстра свет", "POINT"); L.energy = 120; L.color = (1.0, 0.82, 0.62); L.shadow_soft_size = 0.35
    o = bpy.data.objects.new("Люстра свет", L); o.location = W(cx, cz, 1.98); C_LIGHT.objects.link(o)

# ---------------------------------------------------------------- бамбуковые ламели
def bamboo_room(room, h0=0.08, h1=2.64, sides="TBLR", sw=0.032, gap=0.012, depth=0.014):
    """Прямоугольные ламели 32×14 мм с шагом 44 мм на тёмной подложке, молочно-серые."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    for side in sides:
        (bx, bz), _ = side_base(room, side); (ax, az), (nx, nz) = SIDES[side]
        for (k, a0, a1) in SEG[room][side]:
            if k != "wall" or a1 - a0 < 0.06: continue
            def P3(a, n, h):
                px = (a if ax else bx) + nx * n; pz = (a if az else bz) + nz * n
                return W(px, pz, h)
            pitch = sw + gap; n = int((a1 - a0 + gap) / pitch); st = a0 + ((a1 - a0) - (n * pitch - gap)) / 2
            on_wall(room, side, a0, a1, 0, 0.004, h0, h1, M["felt"], C_FIN, "Подложка")
            for i in range(n):
                s0 = st + i * pitch; s1 = s0 + sw; u = random.random() * 0.8
                vb = [P3(s0, 0.004, h0), P3(s1, 0.004, h0), P3(s1, 0.004 + depth, h0), P3(s0, 0.004 + depth, h0)]
                vt = [P3(s0, 0.004, h1), P3(s1, 0.004, h1), P3(s1, 0.004 + depth, h1), P3(s0, 0.004 + depth, h1)]
                B = [bm.verts.new(v) for v in vb]; T = [bm.verts.new(v) for v in vt]
                for j in range(4):
                    f = bm.faces.new([B[j], B[(j + 1) % 4], T[(j + 1) % 4], T[j]])
                    for lp, uv in zip(f.loops, ((u, 0), (u + 0.05, 0), (u + 0.05, 1), (u, 1))): lp[uvl].uv = uv
                bm.faces.new(T[::-1]); bm.faces.new(B)
            on_wall(room, side, a0, a1, 0, 0.03, 0, h0, M["base_b"], C_FIN, "Плинтус", 0.003)
            on_wall(room, side, a0 + 0.02, a1 - 0.02, 0.002, 0.01, h1 + 0.015, h1 + 0.025, M["led"], C_FIN, "LED")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = to_obj(f"Ламели {room}", bm, M["bamboo"], C_FIN)
    md = ob.modifiers.new("Фаска", "BEVEL"); md.width = 0.0015; md.segments = 1
    return ob

for r in NEO: neo_room(r)
for r in BAMBOO: bamboo_room(r, sides="T" if r == "Кухня" else "TBLR")

# ---------------------------------------------------------------- мебель
def px(v): return v / 55.0

def sofa(x0, z0, w, d, back, mat_body, mat_cush, neo=False):
    """back: сторона спинки 'R','L','T','B'. Размеры в метрах плана."""
    sh = 0.42; bh = 0.82 if neo else 0.78; bd = 0.2; arm = 0.16
    box("Диван основание", x0 + 0.02, z0 + 0.02, w - 0.04, d - 0.04, 0.08, sh - 0.12, mat_body, bevel=0.03)
    if back in "RL":
        bx = x0 + w - bd if back == "R" else x0
        box("Диван спинка", bx, z0, bd, d, 0.08, bh - 0.08, mat_body, bevel=0.04)
        for zz in (z0, z0 + d - arm):
            box("Подлокотник", x0, zz, w, arm, 0.08, 0.55, mat_body, bevel=0.06)
        n = 3; cw = (d - 2 * arm) / n
        for i in range(n):
            box("Подушка", x0 + (0 if back == "R" else bd), z0 + arm + i * cw + 0.005, w - bd, cw - 0.01, sh - 0.04, 0.13, mat_cush, bevel=0.05)
            box("Подушка спинки", bx + (-0.14 if back == "R" else bd), z0 + arm + i * cw + 0.01, 0.14, cw - 0.02, sh + 0.08, 0.36, mat_cush, bevel=0.06)
    else:
        bz = z0 if back == "T" else z0 + d - bd
        box("Спинка", x0, bz, w, bd, 0.08, bh - 0.08, mat_body, bevel=0.04)
        for xx in (x0, x0 + w - arm):
            box("Подлокотник", xx, z0, arm, d, 0.08, 0.55, mat_body, bevel=0.06)
        n = 3; cw = (w - 2 * arm) / n
        for i in range(n):
            box("Подушка", x0 + arm + i * cw + 0.005, z0 + (bd if back == "T" else 0), cw - 0.01, d - bd, sh - 0.04, 0.13, mat_cush, bevel=0.05)
    for (lx, lz) in ((x0 + 0.06, z0 + 0.06), (x0 + w - 0.1, z0 + 0.06), (x0 + 0.06, z0 + d - 0.1), (x0 + w - 0.1, z0 + d - 0.1)):
        cyl("Ножка", lx + 0.02, lz + 0.02, 0.018, 0, 0.08, M["brass"] if neo else M["black"])

def armchair(x0, z0, s, back, neo=False):
    body = M["fab_sand"] if neo else M["fab_grey"]
    box("Кресло сиденье", x0 + 0.05, z0 + 0.05, s - 0.1, s - 0.1, 0.2, 0.22, body, bevel=0.04)
    if back == "T": box("Кресло спинка", x0 + 0.05, z0, s - 0.1, 0.12, 0.2, 0.62, body, bevel=0.05)
    else: box("Кресло спинка", x0 + 0.05, z0 + s - 0.12, s - 0.1, 0.12, 0.2, 0.62, body, bevel=0.05)
    for xx in (x0 + 0.02, x0 + s - 0.12):
        box("Кресло подлокотник", xx, z0 + 0.05, 0.1, s - 0.1, 0.2, 0.42, body, bevel=0.04)
    box("Кресло подушка", x0 + 0.13, z0 + (0.16 if back == "T" else 0.08), s - 0.26, s - 0.26, 0.42, 0.08, M["fab_cream"], bevel=0.035)
    for (lx, lz) in ((x0 + 0.1, z0 + 0.1), (x0 + s - 0.1, z0 + 0.1), (x0 + 0.1, z0 + s - 0.1), (x0 + s - 0.1, z0 + s - 0.1)):
        cyl("Ножка", lx, lz, 0.015, 0, 0.2, M["brass"] if neo else M["black"], rz=0.01)

def wardrobe(x0, z0, w, d, h, material, neo=False, facing="B"):
    box("Шкаф", x0, z0, w, d, 0, h, material, bevel=0.004)
    if not neo: return
    # филёнки на фасаде (сторона facing)
    n = max(2, round((w if facing in "TB" else d) / 0.5))
    span = w if facing in "TB" else d; dw = span / n
    for i in range(n):
        a0 = (x0 if facing in "TB" else z0) + i * dw
        for (h0, hh) in ((0.1, 0.55), (0.75, h - 0.85)):
            fr = [(a0 + 0.07, a0 + dw - 0.07, h0, h0 + 0.025), (a0 + 0.07, a0 + dw - 0.07, h0 + hh - 0.025, h0 + hh),
                  (a0 + 0.07, a0 + 0.095, h0, h0 + hh), (a0 + dw - 0.095, a0 + dw - 0.07, h0, h0 + hh)]
            for (p0, p1, q0, q1) in fr:
                if facing == "B": box("Филёнка", p0, z0 + d, p1 - p0, 0.01, q0, q1 - q0, M["trim"], C_FIN, 0.002)
                elif facing == "T": box("Филёнка", p0, z0 - 0.01, p1 - p0, 0.01, q0, q1 - q0, M["trim"], C_FIN, 0.002)
        if facing == "T": hz = z0 - 0.03
        else: hz = z0 + d + 0.01
        box("Ручка", a0 + dw - 0.04 if i % 2 == 0 else a0 + 0.03, hz, 0.012, 0.02, 1.0, 0.18, M["brass"])
    box("Шкаф карниз", x0 - 0.02, z0 - 0.02 if facing == "T" else z0, w + 0.04, d + 0.02, h, 0.06, M["trim"], C_FIN, 0.004)

def tv(x, z, w, d, h0, hh): box("ТВ", x, z, w, d, h0, hh, M["tv"], bevel=0.003)

def round_table(cx, cz, r, h, top_mat, leg_mat):
    cyl("Стол столешница", cx, cz, r, h - 0.03, 0.03, top_mat)
    cyl("Стол опора", cx, cz, 0.03, 0.03, h - 0.06, leg_mat)
    cyl("Стол база", cx, cz, r * 0.55, 0, 0.03, leg_mat)

def curtains(x0, x1, z):
    box("Карниз штанга", x0 - 0.25, z + 0.06, x1 - x0 + 0.5, 0.02, 2.55, 0.02, M["brass"])
    for (a, b) in ((x0 - 0.25, x0 + 0.15), (x1 - 0.15, x1 + 0.25)):
        n = 7; wv = (b - a) / n
        for i in range(n):
            cyl("Штора", a + (i + 0.5) * wv, z + 0.12, wv * 0.62, 0.02, 2.5, M["fab_cream"], seg=16, rz=wv * 0.62)
    box("Тюль", x0 + 0.1, z + 0.09, x1 - x0 - 0.2, 0.004, 0.03, 2.5, M["tulle"])

# --- Гостиная (неоклассика)
neo = True
box("Ковёр", 2.85, 2.25, 2.5, 2.4, 0, 0.012, M["rug"])
box("Ковёр кайма", 2.75, 2.15, 2.7, 2.6, 0, 0.008, M["fab_sand"])
sofa(px(255) - 0.05, px(129), px(50) + 0.05, px(121), "R", M["fab_sand"], M["fab_cream"], neo=True)
armchair(px(193), px(116) + 0.05, px(44), "T", neo=True)
armchair(px(193), px(218) - 0.05, px(44), "B", neo=True)
round_table(px(215) + 0.2, px(189), 0.42, 0.45, M["marble"], M["brass"])
tv(1.95, px(156), 0.04, px(66), 1.05, 0.72)
box("ТВ-консоль", 1.95, px(150), 0.45, px(78), 0.18, 0.42, M["front_neo"], bevel=0.006)
box("ТВ-консоль столешница", 1.94, px(150) - 0.01, 0.47, px(78) + 0.02, 0.6, 0.025, M["marble"], bevel=0.003)
for zz in (px(150) + 0.05, px(150) + px(78) - 0.08):
    for xx in (1.99, 2.33):
        cyl("Ножка консоли", xx, zz, 0.012, 0, 0.18, M["brass"])
wardrobe(px(166), px(327), px(136), px(33), 2.4, M["front_neo"], neo=True, facing="T")
curtains(WINDOWS[0][0], WINDOWS[0][0] + WINDOWS[0][2], 0.309)
box("Кондиционер", 5.545 - 0.22, 0.55, 0.22, 0.85, 2.3, 0.3, M["plastic"], bevel=0.02)

# --- Комната
sofa(px(442) - 0.05, px(129), px(50) + 0.05, px(121), "R", M["fab_grey"], M["fab_cream"])
armchair(px(356), px(142), px(44), "T"); armchair(px(356), px(244) - 0.05, px(44), "B")
round_table(px(378), px(215), 0.38, 0.45, M["oak"], M["black"])
tv(5.745, px(156), 0.04, px(66), 1.05, 0.72)
box("ТВ-тумба", 5.745, px(150), 0.4, px(78), 0.15, 0.4, M["front"], bevel=0.006)
wardrobe(px(316), px(327), px(128), px(33), 2.4, M["front"])
box("Ковёр комната", 6.5, 2.3, 2.0, 2.2, 0, 0.012, M["rug"])
box("Кондиционер", 5.745, 0.6, 0.22, 0.85, 2.3, 0.3, M["plastic"], bevel=0.02)

# --- Кухня v5: рабочая линия справа (холодильник у входа → мойка → плита у окна), духовка под плитой,
#     колонна СВЧ+кладовая, угловая банкетка у окна, проход 0,9–1,2 м
KX0, KX1, KZ0, KZ1 = ROOMS["Кухня"]
RX0 = KX1 - 0.6
FZ0 = KZ1 - 0.6                      # холодильник и колонна — в правом нижнем углу (у входа)
# холодильник встроенный (правая стена, у входа)
box("Колонна холодильник", RX0, FZ0, 0.6, 0.6, 0, H - 0.01, M["front"], bevel=0.003)
box("Ручка холодильника", RX0 - 0.012, FZ0 + 0.03, 0.012, 0.02, 0.9, 0.6, M["brass"])
# колонна СВЧ + кладовая (нижняя стена, рядом с холодильником)
box("Колонна СВЧ кладовая", RX0 - 0.6, FZ0, 0.6, 0.6, 0, H - 0.01, M["front"], bevel=0.003)
box("СВЧ", RX0 - 0.55, FZ0 - 0.006, 0.5, 0.006, 1.35, 0.38, M["tv"], bevel=0.002)
box("Ручка", RX0 - 0.1, FZ0 - 0.012, 0.02, 0.012, 0.85, 0.4, M["brass"])
box("Шов", RX0 - 0.003, FZ0 - 0.004, 0.006, 0.008, 0, H, M["black"])
# нижняя линия: плита+духовка (у окна), посудомойка, мойка
LZ1 = FZ0
box("Нижние модули", RX0 + 0.02, KZ0, 0.58, LZ1 - KZ0, 0.1, 0.76, M["oak"], bevel=0.003)
_fl = bmesh.new()
for _i in range(int((LZ1 - KZ0) / 0.025)):
    _z0 = KZ0 + _i * 0.025
    if _z0 + 0.025 <= KZ0 + 0.6 and True: pass
    _bm = bmesh.new()
    bmesh.ops.create_cone(_bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.0115, radius2=0.0115, depth=0.74)
    for _v in _bm.verts: _v.co = W(RX0 + 0.02 + _v.co.x * 0.45, _z0 + 0.0125 + _v.co.y, 0.48 + _v.co.z)
    _me = bpy.data.meshes.new("t"); _bm.to_mesh(_me); _bm.free(); _fl.from_mesh(_me); bpy.data.meshes.remove(_me)
to_obj("Рифлёные фасады", _fl, M["oak"], C_FURN, smooth=True)
box("Духовой шкаф", RX0 - 0.004, KZ0 + 0.03, 0.01, 0.54, 0.12, 0.6, M["tv"], bevel=0.003)
box("Ручка духовки", RX0 - 0.03, KZ0 + 0.08, 0.02, 0.44, 0.66, 0.018, M["steel"], bevel=0.004)
box("Цоколь", RX0 + 0.06, KZ0, 0.54, LZ1 - KZ0, 0, 0.1, M["black"])
box("Гола-профиль", RX0 + 0.004, KZ0 + 0.6, 0.02, LZ1 - KZ0 - 0.6, 0.8, 0.03, M["brass"])
box("Столешница", RX0 - 0.01, KZ0, 0.62, LZ1 - KZ0, 0.86, 0.04, M["travertine"], bevel=0.004)
box("Фартук", KX1 - 0.02, KZ0, 0.02, LZ1 - KZ0, 0.9, 0.65, M["travertine"])
box("Варочная индукция", RX0 + 0.06, KZ0 + 0.04, 0.5, 0.52, 0.9, 0.006, M["tv"], bevel=0.003)
for (cx, cz, r) in ((RX0 + 0.19, KZ0 + 0.17, 0.08), (RX0 + 0.43, KZ0 + 0.17, 0.07), (RX0 + 0.19, KZ0 + 0.42, 0.07), (RX0 + 0.43, KZ0 + 0.42, 0.09)):
    cyl("Зона нагрева", cx, cz, r, 0.906, 0.0005, M["steel"], seg=48)
SZ = KZ0 + 1.06                       # мойка
sink = box("Мойка", RX0 + 0.08, SZ, 0.44, 0.5, 0.86, 0.04, M["travertine"])
c = box("вырез мойки", RX0 + 0.12, SZ + 0.04, 0.36, 0.42, 0.7, 0.3, M["steel"]); cut(sink, c)
box("Чаша мойки", RX0 + 0.12, SZ + 0.04, 0.36, 0.42, 0.7, 0.005, M["steel"])
cyl("Смеситель", KX1 - 0.07, SZ + 0.25, 0.013, 0.9, 0.36, M["black"])
cyl("Излив", KX1 - 0.07 - 0.11, SZ + 0.25, 0.011, 1.25, 0.22, M["black"], axis="X")
# верхние шкафы с полками до потолка над всей линией; над плитой — шкаф со встроенной вытяжкой
box("Верхние шкафы", KX1 - 0.36, KZ0, 0.35, LZ1 - KZ0, 1.55, H - 1.56, M["front"], bevel=0.003)
_n = round((LZ1 - KZ0) / 0.6)
for _i in range(1, _n + 1):
    _zc = min(KZ0 + _i * (LZ1 - KZ0) / _n, LZ1 - 0.002)
    box("Шов", KX1 - 0.365, _zc - 0.002, 0.008, 0.004, 1.55, H - 1.56, M["black"])
box("Шов гориз", KX1 - 0.365, KZ0, 0.008, LZ1 - KZ0, 2.12, 0.004, M["black"])
box("Вытяжка встроенная", KX1 - 0.36, KZ0 + 0.02, 0.35, 0.56, 1.52, 0.03, M["black"], bevel=0.002)
box("LED под шкафами", KX1 - 0.33, KZ0 + 0.65, 0.025, LZ1 - KZ0 - 0.7, 1.545, 0.005, M["led"])
box("Рулонная штора", 11.036 + 0.05, KZ0 - 0.06, 1.5, 0.01, 1.95, 0.42, M["fab_cream"])
# угловая банкетка у окна: вдоль левой стены и под окном (до откоса)
BL1 = KZ0 + 1.6; BW1 = 11.0
box("Банкетка левая", KX0, KZ0, 0.5, BL1 - KZ0, 0.0, 0.38, M["oak"], bevel=0.008)
box("Банкетка окно", KX0 + 0.5, KZ0, BW1 - KX0 - 0.5, 0.48, 0.0, 0.38, M["oak"], bevel=0.008)
box("Сиденье левое", KX0 + 0.01, KZ0 + 0.01, 0.48, BL1 - KZ0 - 0.02, 0.38, 0.09, M["fab_accent"], bevel=0.035)
box("Сиденье окно", KX0 + 0.5, KZ0 + 0.01, BW1 - KX0 - 0.51, 0.46, 0.38, 0.09, M["fab_accent"], bevel=0.035)
for zz in (KZ0 + 0.5, KZ0 + 1.05):
    box("Спинка", KX0, zz, 0.12, 0.53, 0.47, 0.42, M["fab_accent"], bevel=0.05)
for xx in (KX0 + 0.02, KX0 + 0.62, KX0 + 1.22):
    box("Спинка", xx, KZ0, min(0.58, BW1 - xx - 0.02), 0.12, 0.47, 0.42, M["fab_accent"], bevel=0.05)
ellipsoid("Подушка", KX0 + 0.2, KZ0 + 0.25, 0.68, 0.18, 0.18, 0.18, M["fab_cream"])
ellipsoid("Подушка", KX0 + 0.13, KZ0 + 1.2, 0.68, 0.06, 0.2, 0.18, M["fab_main"])
# стол 1300×850 со скруглёнными углами, на опоре
_tcx, _tcz = KX0 + 0.55 + 0.65, KZ0 + 0.55 + 0.425
_t = cyl("Стол", _tcx, _tcz, 1.0, 0.715, 0.045, M["oak"], seg=96)
for _v in _t.data.vertices:
    _v.co.x = _tcx + (_v.co.x - _tcx) * 0.65; _v.co.y = -_tcz + (_v.co.y + _tcz) * 0.425
_p = cyl("Опора стола", _tcx, _tcz, 0.12, 0.03, 0.69, M["oak"], seg=48, rz=0.07)
cyl("Опора база", _tcx, _tcz, 0.28, 0.0, 0.03, M["oak"], seg=48)
# 2 стула со стороны прохода + детский стульчик у торца
def chair_k(cx, cz, face="L"):
    box("Стул сиденье", cx - 0.22, cz - 0.22, 0.44, 0.44, 0.44, 0.06, M["fab_cream"], bevel=0.025)
    box("Стул спинка", cx + (0.17 if face == "L" else -0.22), cz - 0.22, 0.05, 0.44, 0.5, 0.38, M["fab_cream"], bevel=0.025)
    for (dx, dz) in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)):
        cyl("Ножка стула", cx + dx, cz + dz, 0.015, 0, 0.44, M["oak"], rz=0.011)
for zc in (_tcz - 0.24, _tcz + 0.24):
    chair_k(_tcx + 0.65 + 0.22, zc, "L")
hx, hz = _tcx - 0.2, _tcz + 0.425 + 0.24
box("Детский стул", hx - 0.2, hz - 0.2, 0.4, 0.4, 0.72, 0.05, M["oak"], bevel=0.02)
box("Детский стул спинка", hx - 0.2, hz + 0.15, 0.4, 0.05, 0.77, 0.32, M["oak"], bevel=0.02)
for (dx, dz) in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)):
    cyl("Ножка", hx + dx, hz + dz, 0.016, 0, 0.72, M["oak"])
for i, xc in enumerate((_tcx - 0.35, _tcx + 0.35)):
    cyl("Подвес", xc, _tcz, 0.003, 1.72, H - 1.72, M["black"])
    cyl("Чашка", xc, _tcz, 0.04, 1.71, 0.03, M["brass"])
    ellipsoid("Шар опал", xc, _tcz, 1.58, 0.13, 0.13, 0.13, M["opal"])
    Lp = bpy.data.lights.new("Подвес свет", "POINT"); Lp.energy = 14; Lp.color = (1.0, 0.88, 0.75); Lp.shadow_soft_size = 0.13
    op = bpy.data.objects.new("Подвес свет", Lp); op.location = W(xc, _tcz, 1.40); C_LIGHT.objects.link(op)
cyl("Ваза", _tcx, _tcz, 0.06, 0.76, 0.22, M["ceramic"], rz=0.045)

# --- Спальня 2
box("Кровать", px(640), px(239) + 0.12, px(121), px(50) - 0.12, 0.08, 0.32, M["fab_grey"], bevel=0.03)
box("Матрас", px(640) + 0.02, px(239) + 0.14, px(121) - 0.04, px(50) - 0.16, 0.4, 0.2, M["fab_cream"], bevel=0.05)
box("Изголовье", px(640), px(239), px(121), 0.12, 0.08, 1.05, M["fab_sand"], bevel=0.04)
box("Плед", px(640) + 1.2, px(239) + 0.13, px(121) - 1.25, px(50) - 0.14, 0.58, 0.04, M["fab_sand"], bevel=0.02)
for i in range(2):
    box("Подушка", px(640) + 0.15 + i * 0.75, px(239) + 0.16, 0.6, 0.35, 0.6, 0.14, M["fab_cream"], bevel=0.06)
wardrobe(px(554), px(238), px(33), px(120), 2.4, M["front"])
tv(px(668), 7.491 - 0.04, px(66), 0.04, 1.05, 0.72)
box("ТВ-тумба", px(662), 7.491 - 0.4, px(78), 0.4, 0.15, 0.4, M["front"], bevel=0.006)
box("Кондиционер", 14.745 - 0.22, 4.55, 0.22, 0.85, 2.3, 0.3, M["plastic"], bevel=0.02)

# --- Коридор и прихожая
box("Шкаф-купе", px(350), px(436), px(197), px(26), 0, 2.4, M["front"], bevel=0.004)
for i in range(1, 4):
    box("Шов купе", px(350) + i * px(197) / 4 - 0.004, px(436) - 0.003, 0.008, 0.004, 0, 2.4, M["black"])
box("Шкаф прихожей", px(160), px(462), px(30), px(58), 0, 2.4, M["front"], bevel=0.004)
box("Обувница", px(107), px(460), px(16), px(60), 0.15, 0.85, M["front"], bevel=0.004)
box("Зеркало", 1.946, px(460) + 0.05, 0.01, px(60) - 0.1, 1.15, 0.95, M["mirror"])

# --- Ванная
box("Ванна", 3.564, 8.959, 1.40, 0.55, 0, 0.55, M["ceramic"], bevel=0.02)
c = box("вырез ванны", 3.62, 9.015, 1.29, 0.44, 0.15, 0.5, M["ceramic"], bevel=0.0)
cut(bpy.data.objects["Ванна"], c)
box("Смеситель ванны", 4.2, 9.509 - 0.06, 0.18, 0.06, 0.78, 0.04, M["black"], bevel=0.005)
box("Стиральная машина", 3.618, 8.218, 0.6, 0.6, 0, 0.85, M["plastic"], bevel=0.02)
cyl("Люк стиралки", 4.22, 8.518, 0.17, 0.42, 0.0, M["washer_door"], axis="X")
cyl("Люк стиралки", 4.225, 8.518, 0.17, 0.42, 0.012, M["washer_door"], axis="X")
cyl("Бойлер Б1", 3.79, 8.52, 0.225, 1.5, 0.8, M["plastic"])
ellipsoid("Бойлер Б1 низ", 3.79, 8.52, 1.5, 0.225, 0.225, 0.06, M["plastic"])
ellipsoid("Бойлер Б1 верх", 3.79, 8.52, 2.3, 0.225, 0.225, 0.06, M["plastic"])
box("Инсталляция короб", 6.073 - 0.16, 8.018, 0.16, 1.491, 0, 1.12, M["wall"], C_ARCH)
box("Полка короба", 6.073 - 0.18, 8.018, 0.18, 1.491, 1.12, 0.02, M["ceramic"], C_ARCH)

def wall_hung(cx, cz, along_x, wall_n, bidet=False):
    """Подвесной унитаз/биде. along_x — ось прибора вдоль x (стена по z); wall_n — координата стены короба."""
    rx, rz = (0.18, 0.27) if not along_x else (0.27, 0.18)
    ell = ellipsoid("Биде" if bidet else "Унитаз", cx, cz, 0.3, rx, rz, 0.13, M["ceramic"])
    if not bidet:
        ellipsoid("Сиденье", cx, cz, 0.41, rx * 0.98, rz * 0.98, 0.02, M["ceramic"])
    else:
        cyl("Смеситель биде", cx + (0.0 if not along_x else 0.0), cz, 0.012, 0.42, 0.06, M["black"])

def flush(x, z, w, d):
    box("Кнопка смыва", x, z, w, d, 0.92, 0.15, M["black"], bevel=0.004)

wall_hung(5.913 - 0.25, 9.115, True, 5.913); flush(5.913 - 0.006, 9.115 - 0.11, 0.006, 0.22)
wall_hung(5.913 - 0.25, 8.415, True, 5.913, bidet=True)

# --- Санузел
box("Инсталляция короб", 0.309, 9.018 - 0.16, 1.527, 0.16, 0, 1.12, M["wall"], C_ARCH)
box("Полка короба", 0.309, 9.018 - 0.18, 1.527, 0.18, 1.12, 0.02, M["ceramic"], C_ARCH)
wall_hung(1.43, 8.858 - 0.25, False, 8.858); flush(1.43 - 0.11, 8.858 - 0.006, 0.22, 0.006)
wall_hung(0.71, 8.858 - 0.25, False, 8.858, bidet=True)
cyl("Бойлер Б2", 0.90, 8.79, 0.225, 2.125, 1.0, M["plastic"], axis="X")
box("Поддон душа", 0.327, 6.818, 0.69, 0.89, 0, 0.03, M["ceramic"], bevel=0.01)
box("Трап", 0.4, 7.55, 0.5, 0.05, 0.031, 0.002, M["steel"])
box("Стекло душа", 1.0, 6.82, 0.01, 0.89, 0.03, 2.0, M["glass_sh"])
box("Профиль душа", 0.327, 6.82, 0.69, 0.02, 2.02, 0.02, M["black"])
box("Тропический душ", 0.55, 6.83, 0.25, 0.25, 2.08, 0.015, M["black"], bevel=0.003)
cyl("Штанга душа", 0.67, 6.83, 0.01, 2.09, 0.1, M["black"])
box("Смеситель душа", 0.33, 7.2, 0.05, 0.16, 1.05, 0.08, M["black"], bevel=0.005)
box("Бак 200 л", 1.03, 6.81, 0.6, 0.4, 0, 0.9, M["plastic"], bevel=0.03)
box("Насос", 1.18, 6.85, 0.3, 0.25, 0.9, 0.22, M["steel"], bevel=0.01)
box("Раковина", 0.309, 7.85, 0.36, 0.45, 0.72, 0.14, M["ceramic"], bevel=0.02)
c = box("вырез раковины", 0.36, 7.9, 0.27, 0.35, 0.78, 0.2, M["ceramic"])
cut(bpy.data.objects["Раковина"], c)
cyl("Смеситель", 0.34, 8.075, 0.014, 0.86, 0.18, M["black"])
box("Зеркало", 0.309, 7.86, 0.012, 0.43, 1.05, 0.75, M["mirror"])
box("Подсветка зеркала", 0.309, 7.84, 0.004, 0.47, 1.03, 0.79, M["led"])

# ---------------------------------------------------------------- свет
def area(name, cx, cz, size, watts, color=(1.0, 0.92, 0.84), h=H - 0.02):
    L = bpy.data.lights.new(name, "AREA"); L.energy = watts; L.color = color; L.size = size
    o = bpy.data.objects.new(name, L); o.location = W(cx, cz, h); C_LIGHT.objects.link(o)
for rn, (x0, x1, z0, z1) in ROOMS.items():
    a = (x1 - x0) * (z1 - z0)
    if rn in NEO: continue
    area(f"Свет {rn}", (x0 + x1) / 2, (z0 + z1) / 2, min(x1 - x0, z1 - z0) * 0.5, 9 * a)
area("Свет гостиная заполняющий", 3.75, 3.4, 2.0, 90)
sun = bpy.data.lights.new("Солнце", "SUN"); sun.energy = 3.2; sun.angle = math.radians(1.2); sun.color = (1.0, 0.95, 0.88)
so = bpy.data.objects.new("Солнце", sun); C_LIGHT.objects.link(so)
so.rotation_euler = Vector((0.35, -0.75, -0.55)).to_track_quat("-Z", "Y").to_euler()
world = scene.world or bpy.data.worlds.new("Мир"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.62, 0.74, 0.92, 1); bg.inputs["Strength"].default_value = 1.6

# ---------------------------------------------------------------- камеры
CAMS = [
    ("01_gostinaya_okno", (3.75, 5.85, 1.40), (3.75, 0.3, 1.25), 17),
    ("02_gostinaya_shkaf", (3.55, 0.75, 1.40), (3.45, 6.5, 1.15), 17),
    ("03_gostinaya_tv", (5.15, 5.65, 1.45), (1.95, 3.0, 1.15), 16),
    ("04_gostinaya_divan", (2.35, 5.25, 1.30), (5.5, 2.9, 1.15), 20),
    ("05_komnata_okno", (7.35, 5.85, 1.40), (7.35, 0.3, 1.25), 17),
    ("06_komnata_shkaf", (7.2, 0.75, 1.40), (7.05, 6.5, 1.15), 17),
    ("07_spalnya_okno", (10.85, 6.95, 1.40), (14.7, 6.3, 1.2), 17),
    ("08_spalnya_shkaf", (14.35, 6.1, 1.40), (10.1, 5.4, 1.2), 17),
    ("09_koridor_vhod", (9.6, 7.3, 1.50), (2.0, 7.9, 1.2), 18),
    ("10_koridor_spalnya", (2.3, 7.25, 1.50), (9.9, 7.05, 1.2), 18),
    ("11_kuhnya", (9.6, 4.05, 1.5), (12.4, 2.4, 1.0), 18),
    ("11b_kuhnya_stol", (12.2, 3.35, 1.5), (9.6, 2.3, 0.95), 18),
    ("11c_kuhnya_okno", (10.4, 4.0, 1.55), (12.0, 1.9, 1.1), 18),
    ("12_vannaya_dver", (4.65, 8.12, 1.55), (4.55, 9.5, 0.7), 12),
    ("13_vannaya_ugol", (3.8, 9.35, 1.55), (5.9, 8.25, 0.9), 12),
    ("14_sanuzel_dver", (1.74, 7.4, 1.55), (0.45, 8.65, 0.8), 12),
    ("15_sanuzel_dush", (1.72, 8.62, 1.55), (0.5, 7.15, 1.1), 12),
]
cam_objs = []
for (n, p, t, lens) in CAMS:
    cd = bpy.data.cameras.new(n); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.03
    o = bpy.data.objects.new(n, cd); C_CAM.objects.link(o)
    o.location = W(*p); d = W(*t) - W(*p); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam_objs.append(o)
scene.camera = cam_objs[0]

# ---------------------------------------------------------------- рендер
scene.render.engine = "CYCLES"
gpu = False
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = t
            (getattr(prefs, "refresh_devices", None) or prefs.get_devices)()
            devs = [d for d in prefs.devices if d.type == t]
            if devs:
                for d in prefs.devices: d.use = (d.type == t)
                gpu = True; break
        except Exception:
            continue
except Exception:
    pass
scene.cycles.device = "GPU" if gpu else "CPU"
scene.cycles.samples = (48 if gpu else 16) if QUICK else (512 if gpu else 128)
try: scene.cycles.use_adaptive_sampling = True
except Exception: pass
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8; scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
scene.render.resolution_x, scene.render.resolution_y = (960, 540) if QUICK else (1920, 1080)
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for vt in ("AgX", "Filmic"):
    try: scene.view_settings.view_transform = vt; break
    except Exception: continue
for lk in ("AgX - Medium High Contrast", "Medium High Contrast", "None"):
    try: scene.view_settings.look = lk; break
    except Exception: continue
scene.view_settings.exposure = -0.6

os.makedirs(OUT, exist_ok=True)
try: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "kvartira.blend"), copy=True)
except Exception as e: print("save blend:", e)
print("GPU:", gpu, "| объектов:", len(bpy.data.objects))

if RENDER:
    for i, o in enumerate(cam_objs, 1):
        if SHOTS != "all" and i not in SHOTS: continue
        scene.camera = o
        scene.render.filepath = os.path.join(OUT, o.name + ".png")
        bpy.ops.render.render(write_still=True)
        print("готово:", scene.render.filepath)
