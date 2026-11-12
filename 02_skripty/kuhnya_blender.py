# -*- coding: utf-8 -*-
"""kuhnya — СГЕНЕРИРОВАН gen_vanna.py из kuhnya_room.py + wet_common.py. Не править вручную.
Запуск: blender -b --factory-startup -P kuhnya_blender.py -- [quick] [shots=1,2,3,4] [all=g1]"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "quick" in ARGS
OPT = dict(a.split("=", 1) for a in ARGS if "=" in a)
SHOTS = OPT.get("shots", "1,2,3,4").split(",")
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, "08_vizualizacii", "kuhnya"); os.makedirs(OUT, exist_ok=True)
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

# ======================= КУХНЯ (13.11.2026) — по листу 11 «План кухни»: линейная кухня у правой стены
# (плита+духовка у окна → ПММ 450 → мойка → холодильник-колонна), колонна СВЧ+кладовая у нижней стены,
# угловая банкетка (левая + верхняя стена) + стол 1300×850 + 2 стула; К4 над банкеткой.
# Стиль квартиры: серые бамбуковые панели, мебель графит #2F2F31 без ручек (гола-профиль), столешница и фартук —
# серый керамогранит (как в ванной), пол — тот же керамогранит 1200×600.
X0, X1, Z0, Z1 = 9.145, 13.0, 1.909, 4.2
H, HC = 2.70, 2.65
WX0, WX1, WS, WT = 11.036, 12.636, 0.90, 2.40       # окно в верхней стене
DX0, DX1, DH = 9.145, 9.945, 2.10                   # проём из коридора (нижняя стена), без двери
OUTDIR = "kuhnya"
GRAF = "#" + OPT.get("ward", "2F2F31")

def marble_img(name, nx, ny, tiles_u, tiles_v, seed=3, kind="dark"):
    # 13.11: как в образце (05_ishodniki/obrazec_albom_dizajnera_76m2.pdf, л.46–50): тёмный графитово-коричневый мрамор
    # с густой сеткой белых прожилок + белый мрамор с мягкими серыми прожилками
    def fbm(beta, s):
        r = np.random.default_rng(s); F = np.fft.fftfreq(ny)[:, None]; G = np.fft.rfftfreq(nx)[None, :]
        k = np.sqrt((F * ny / max(nx, ny)) ** 2 + (G * nx / max(nx, ny)) ** 2) + 1e-4
        spec = (r.normal(size=k.shape) + 1j * r.normal(size=k.shape)) * k ** (-beta); spec[0, 0] = 0
        f = np.fft.irfft2(spec, s=(ny, nx)); return (f - f.mean()) / f.std()
    yy, xx = np.mgrid[0:ny, 0:nx] / max(nx, ny)
    F = [fbm(2.0, seed + i) for i in range(6)]
    def vein(dirx, diry, K, w, warp, mask_f, mt):
        g = xx * dirx + yy * diry + warp * F[mask_f] + 0.15 * F[(mask_f + 1) % 6]
        return np.exp(-np.abs(np.sin(g * K)) / w) * np.clip(F[(mask_f + 2) % 6] - mt, 0, 1).clip(0, 1) ** 0.5
    DENSE = (vein(2.4, 1.6, 6.0, 0.030, 0.16, 0, -0.8) + vein(-1.2, 2.6, 8.0, 0.022, 0.14, 1, -0.5) * 0.9
             + vein(1.0, -2.2, 11.0, 0.016, 0.12, 2, -0.2) * 0.8 + vein(2.8, 0.6, 15.0, 0.012, 0.10, 3, 0.0) * 0.7
             + vein(0.4, 3.0, 19.0, 0.010, 0.10, 4, 0.2) * 0.6)
    SOFT = vein(2.0, 1.4, 5.0, 0.018, 0.4, 0, 0.0) * 0.7 + vein(-1.4, 2.2, 9.0, 0.008, 0.3, 1, 0.3) * 0.5
    SPARSE = vein(2.6, 1.7, 4.0, 0.012, 0.2, 0, 0.2) * 0.8 + vein(-1.2, 2.8, 3.5, 0.007, 0.25, 1, 0.5) * 0.5
    KINDS = {  # база (sRGB 0..1), прожилки, рисунок, контраст пятен
        "dark":   ((0.27, 0.245, 0.23), (0.90, 0.88, 0.85), DENSE, 0.10),   # тёмный мрамор образца
        "white":  ((0.91, 0.90, 0.885), (0.55, 0.53, 0.52), SOFT, 0.015),   # белый мрамор
        "grafit": ((0.30, 0.30, 0.31), (0.80, 0.80, 0.80), SPARSE, 0.06),   # графит, редкие прожилки
        "grey":   ((0.50, 0.495, 0.49), (0.90, 0.90, 0.89), DENSE * 0.8, 0.05),  # серый мрамор с белыми прожилками
        "greige": ((0.55, 0.52, 0.48), (0.88, 0.86, 0.82), SPARSE, 0.05),   # тёплый серо-бежевый камень
        "beton":  ((0.40, 0.395, 0.39), (0.40, 0.40, 0.40), SPARSE * 0, 0.12),
        # 13.11 серая гамма (заказчик: «серый, тёмно-серый, чёрно-серый, графитово-серый»), одна плитка на всю ванную
        "g1": ((0.56, 0.56, 0.56), (0.86, 0.86, 0.86), DENSE * 0.55, 0.06),   # серый
        "g2": ((0.42, 0.42, 0.425), (0.84, 0.84, 0.84), DENSE * 0.55, 0.07),  # тёмно-серый
        "g3": ((0.31, 0.31, 0.32), (0.82, 0.82, 0.82), DENSE * 0.55, 0.08),   # графит
        "g4": ((0.20, 0.20, 0.205), (0.80, 0.80, 0.80), DENSE * 0.55, 0.10)}  # чёрно-серый   # микроцемент графит
    bcl, vcl, v, kc = KINDS[kind]
    v = np.clip(v, 0, 1)
    bc = np.array(bcl) * (1 + kc * F[4][..., None]) + 0.01 * F[5][..., None]
    vc = np.array(vcl)
    col = bc * (1 - v[..., None]) + vc * v[..., None]
    col = col + np.random.default_rng(seed + 9).normal(0, 0.008, (ny, nx))[..., None]
    tu, tv = nx / tiles_u, ny / tiles_v
    ax_, ay_ = np.arange(nx), np.arange(ny)
    seam = (np.minimum(ax_ % tu, tu - ax_ % tu)[None, :] < 1.2) | (np.minimum(ay_ % tv, tv - ay_ % tv)[:, None] < 1.2)
    col[seam] = col[seam] * 0.75
    col = np.clip(col, 0, 1) ** 2.2
    img = bpy.data.images.new(name, nx, ny, alpha=False); px = np.ones((ny, nx, 4), np.float32); px[..., :3] = col
    img.pixels.foreach_set(px.ravel()); img.pack(); return img
def marble_mat(name, img, S, rough=0.12):
    m = mat(name, "#1A1A1C", rough); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.projection = "BOX"; t.projection_blend = 0.0; t.interpolation = "Cubic"
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = S
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], t.inputs["Vector"]); nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m
ALL = OPT.get("all", "g1")      # 13.11: заказчик выбрал плитку №1 — серый, одна на всё помещение
IMG_W = marble_img("мрамор тёмный стены", 1024, 2048, 2, 2, 3, ALL or "dark")     # плитка 600×1200 вертикально
IMG_L = marble_img("мрамор белый стены", 1024, 2048, 2, 2, 21, ALL or "white")
IMG_F = marble_img("мрамор тёмный пол", 2048, 1024, 2, 2, 11, ALL or "dark")      # пол 1200×600
M = dict(tile=marble_mat("Керамогранит тёмный", IMG_W, (1 / 1.2, 1 / 1.2, 1 / 2.4), 0.15),
         tilew=marble_mat("Керамогранит белый", IMG_L, (1 / 1.2, 1 / 1.2, 1 / 2.4), 0.15),
         tilef=marble_mat("Керамогранит пол", IMG_F, (1 / 2.4, 1 / 1.2, 1.0), 0.18),
         ceil=mat("Потолок", "#EEECE7", 0.9), white=mat("Сантехника белая", "#F4F4F2", 0.08),
         acryl=mat("Ванна акрил", "#F6F6F4", 0.12), black=mat("Чёрный матовый", "#151516", 0.35, 0.6),
         ward=mat("Графит матовый", GRAF, 0.45), door=mat("Двери", "#E2E0DB", 0.45),
         mirror=mat("Зеркало", "#E3E7E8", 0.02, 1.0), glass=mat("Стекло", "#FFFFFF", 0.0, transm=1.0),
         dglass=mat("Стекло дверцы", "#202426", 0.05), towel=mat("Полотенце", "#8A8B8F", 1.0),
         led=emis("LED", "#FFE6C8", 6), ledm=emis("LED за зеркалом", "#FFE6C8", 40), spot=emis("Спот", "#FFF4E2", 12))
T = 0.12
def wb(n, w, a0, a1, d0, d1, h0, h1, m, bev=0.0):
    """коробка у стены w (L/R/T/B): a — вдоль стены, d — отступ от стены в комнату"""
    if w == "L": return box(n, X0 + d0, a0, X0 + d1, a1, h0, h1, m, bev)
    if w == "R": return box(n, X1 - d1, a0, X1 - d0, a1, h0, h1, m, bev)
    if w == "T": return box(n, a0, Z0 + d0, a1, Z0 + d1, h0, h1, m, bev)
    return box(n, a0, Z1 - d1, a1, Z1 - d0, h0, h1, m, bev)
def pt(w, a, d):
    return {"L": (X0 + d, a), "R": (X1 - d, a), "T": (a, Z0 + d), "B": (a, Z1 - d)}[w]
def room_box(doorwall, da0, da1):
    box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["tilef"])
    for (w, x0_, z0_, x1_, z1_) in (("L", X0 - T, Z0 - T, X0, Z1 + T), ("R", X1, Z0 - T, X1 + T, Z1 + T),
                                   ("T", X0 - T, Z0 - T, X1 + T, Z0), ("B", X0 - T, Z1, X1 + T, Z1 + T)):
        if w != doorwall: box("Стена " + w, x0_, z0_, x1_, z1_, 0, H, M["tile"]); continue
        if w in ("T", "B"):
            box("Стена", x0_, z0_, da0, z1_, 0, H, M["tile"]); box("Стена", da1, z0_, x1_, z1_, 0, H, M["tile"]); box("Над дверью", da0, z0_, da1, z1_, DH, H, M["tile"])
        else:
            box("Стена", x0_, z0_, x1_, da0, 0, H, M["tile"]); box("Стена", x0_, da1, x1_, z1_, 0, H, M["tile"]); box("Над дверью", x0_, da0, x1_, da1, DH, H, M["tile"])
    # дверное полотно (крем) в проёме + чёрный наличник + ручка
    sgn = {"T": -1, "B": 1, "L": -1, "R": 1}[doorwall]
    wb("Дверь", doorwall, da0 + 0.005, da1 - 0.005, -0.07, -0.03, 0.005, DH - 0.005, M["door"])
    for (a, b_) in ((da0, da0 + 0.012), (da1 - 0.012, da1)): wb("Наличник", doorwall, a, b_, -0.03, 0.003, 0, DH, M["black"])
    wb("Наличник верх", doorwall, da0, da1, -0.03, 0.003, DH - 0.012, DH, M["black"])
    wb("Ручка", doorwall, da1 - 0.20, da1 - 0.07, 0.025, 0.04, 1.0, 1.02, M["black"]); wb("Ручка ножка", doorwall, da1 - 0.09, da1 - 0.07, -0.03, 0.04, 1.0, 1.02, M["black"])
    box("Потолок", X0 - T, Z0 - T, X1 + T, Z1 + T, HC, HC + 0.05, M["ceil"])
def hung(n, w, a, kind="wc", d0=0.20):
    """подвесной унитаз / биде — реальные модели BlenderKit (13.11), на коробе инсталляции, верх чаши h=400"""
    f = os.path.join(BK, ("unitaz_podv" if kind == "wc" else "bide_podv") + ".blend")
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [o for o in src.objects]
    objs = [o for o in dst.objects if o is not None and o.type == "MESH"]
    ytop = -0.126 if kind == "wc" else 0.071                # верх чаши в координатах модели
    x, z = pt(w, a, d0); rz = {"T": 0, "B": 180, "L": 90, "R": -90}[w]
    Tm = Matrix.Translation(W(x, z, 0.40 - ytop)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
    for o in objs:
        sc.collection.objects.link(o); o.matrix_world = Tm @ o.matrix_world
        for i, ms in enumerate(o.data.materials):
            if ms and any(k in ms.name.lower() for k in ("chrome", "metal", "steel")): o.data.materials[i] = M["black"]
    return objs
def vessel(w, a, d, top, r=0.20, k=0.78):
    x, z = pt(w, a, d)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r, depth=0.13, location=W(x, z, top + 0.065))
    s_ = bpy.context.active_object; s_.scale = ((k, 1, 1) if w in ("L", "R") else (1, k, 1)); s_.data.materials.append(M["white"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r - 0.02, depth=0.2, location=W(x, z, top + 0.16))
    c_ = bpy.context.active_object; c_.scale = s_.scale; c_.hide_render = True; c_.display_type = "WIRE"
    md = s_.modifiers.new("cav", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = c_
    bv = s_.modifiers.new("bv", "BEVEL"); bv.width = 0.008; bv.segments = 3
    wb("Смеситель настенный", w, a - 0.04, a + 0.04, 0, 0.03, top + 0.24, top + 0.32, M["black"], 0.005)
    wb("Излив", w, a - 0.015, a + 0.015, 0.03, d - 0.02, top + 0.26, top + 0.285, M["black"], 0.005)
def mirror_led(w, a0, a1, h0, h1):
    wb("Зеркало", w, a0, a1, 0.035, 0.045, h0, h1, M["mirror"], 0.002)
    for (p0, p1, q0, q1) in ((a0, a1, h0, h0 + 0.012), (a0, a1, h1 - 0.012, h1), (a0, a0 + 0.012, h0, h1), (a1 - 0.012, a1, h0, h1)):
        wb("Рамка зеркала", w, p0, p1, 0.035, 0.05, q0, q1, M["black"])
    wb("Подложка зеркала", w, a0 + 0.06, a1 - 0.06, 0.004, 0.035, h0 + 0.06, h1 - 0.06, M["black"])
    for (p0, p1, q0, q1) in ((a0 + 0.04, a1 - 0.04, h0 + 0.04, h0 + 0.05), (a0 + 0.04, a1 - 0.04, h1 - 0.05, h1 - 0.04),
                             (a0 + 0.04, a0 + 0.05, h0 + 0.04, h1 - 0.04), (a1 - 0.05, a1 - 0.04, h0 + 0.04, h1 - 0.04)):
        wb("LED за зеркалом", w, p0, p1, 0.030, 0.034, q0, q1, M["ledm"])
def cabinet(n, w, a0, a1, d, h0, h1, doors=2):
    """графитовый навесной шкаф (прячет бойлер / бак), гладкие фасады, чёрные ручки, LED снизу"""
    wb(n, w, a0, a1, 0, d - 0.02, h0, h1, M["ward"])
    step = (a1 - a0) / doors
    for k in range(doors):
        p0, p1 = a0 + k * step + 0.002, a0 + (k + 1) * step - 0.002
        wb("Фасад", w, p0, p1, d - 0.02, d, h0 + 0.002, h1 - 0.002, M["ward"], 0.002)
        ah = p1 - 0.05 if k % 2 == 0 else p0 + 0.05
        wb("Ручка", w, ah - 0.006, ah + 0.006, d, d + 0.016, h0 + 0.03, h0 + 0.33, M["black"], 0.002)
    wb("LED под шкафом", w, a0 + 0.03, a1 - 0.03, 0.05, d - 0.05, h0 - 0.005, h0, M["led"])
def spots(P, e=None):
    for (xx, zz) in P:
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.04, depth=0.004, location=W(xx, zz, HC - 0.002)); bpy.context.active_object.data.materials.append(M["spot"])
        lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = float(OPT.get("spot", "60")); lt.spot_size = math.radians(80); lt.spot_blend = 0.7; lt.color = (1, 0.92, 0.82)
        o = bpy.data.objects.new("Спот", lt); o.location = W(xx, zz, HC - 0.02); sc.collection.objects.link(o)
    w_ = sc.world or bpy.data.worlds.new("W"); sc.world = w_; w_.use_nodes = True; w_.node_tree.nodes["Background"].inputs[1].default_value = 0.6
def towel_rail(w, a0, a1):
    for aa in (a0, a1): wb("Сушитель стойка", w, aa - 0.01, aa + 0.01, 0.04, 0.06, 0.85, 1.65, M["black"])
    for k in range(6): wb("Сушитель перекладина", w, a0, a1, 0.045, 0.06, 0.90 + k * 0.145, 0.915 + k * 0.145, M["black"])
    wb("Полотенце", w, a0 + 0.03, a1 - 0.03, 0.06, 0.09, 1.10, 1.57, M["towel"], 0.02)
def bottles(w, a, d, h, cols=("white", "black", "white")):
    for i, c in enumerate(cols):
        x, z = pt(w, a + i * 0.07, d)
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.028, depth=0.16, location=W(x, z, h + 0.08)); bpy.context.active_object.data.materials.append(M[c])
def bk_load(fname, Tm, recolor=None, keep=()):
    """загрузить модель BlenderKit и поставить матрицей Tm; recolor — материал для всех слотов, кроме имён из keep"""
    f = os.path.join(BK, fname + ".blend")
    if not os.path.exists(f): print("NO MODEL", fname); return []
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [o for o in src.objects]
    allo = [o for o in dst.objects if o is not None and o.type not in ("LIGHT", "CAMERA")]
    for o in allo: sc.collection.objects.link(o)
    bpy.context.view_layer.update()
    roots = [o for o in allo if o.parent is None or o.parent not in allo]
    for o in roots: o.matrix_world = Tm @ o.matrix_world
    objs = [o for o in allo if o.type == "MESH"]
    if recolor is not None:
        for o in objs:
            for i, ms in enumerate(o.data.materials):
                if not ms or not any(k in ms.name.lower() for k in keep): o.data.materials[i] = recolor
    return objs
def towel_rail_bk(w, a, hc=1.25):
    """полотенцесушитель (модель BlenderKit, перекрашен в чёрный, полотенца — серые)"""
    x, z = pt(w, a, 0.0); rz = {"T": 0, "B": 180, "L": 90, "R": -90}[w]
    Tm = Matrix.Translation(W(x, z, hc)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
    objs = bk_load("polotencesushitel", Tm)
    for o in objs:
        for i, ms in enumerate(o.data.materials):
            o.data.materials[i] = M["towel"] if (ms and "towel" in ms.name.lower()) else M["black"]
    return objs
def washer_bk(w, a0, a1, d0=0.05):
    """стиральная машина Samsung WD11 (600×586×849) спиной к стене w, дверцей в комнату"""
    if w != "L": raise ValueError("только L")
    Tm = Matrix.Translation(Vector((X0 + d0 + 0.586, -a1, 0.0))) @ Matrix.Rotation(math.radians(90), 4, "Z")
    return bk_load("stiralka_samsung", Tm)
def bath_bk(x0, x1, z0, z1, h=0.56):
    """ванна (модель BlenderKit 1476×742×515) масштабом в прямоугольник плана"""
    Tm = Matrix.Translation(W((x0 + x1) / 2, (z0 + z1) / 2, 0)) @ Matrix.Diagonal(((x1 - x0) / 1.476, (z1 - z0) / 0.742, h / 0.515, 1.0))
    return bk_load("vanna_akril", Tm, M["acryl"], keep=("metal", "black"))

WALLC = "#BDBBB5"
M["wall"] = tex(mat("Бамбуковые панели серые", WALLC, 0.38), "washed_grey_oak_veneer", 1.6, WALLC, 1.55, 0.7)
M["seam"] = mat("Шов панелей", "#2E2C2A", 0.6)
M["knit"] = mat("Ткань банкетки", "#8A8B8F", 0.95)
M["bglass"] = mat("Чёрное стекло", "#0B0B0C", 0.06)
M["wframe"] = mat("Рама окна", "#F2F1EE", 0.4)
M["blind"] = mat("Рулонная штора", "#D9D7D2", 0.9, transm=0.25)
M["shade"] = emis("Плафон", "#FFE2B8", 8)

# ---------------- коробка: пол, стены (бамбук, листы 1220 со швами), окно, проём
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["tilef"])
box("Стена L", X0 - T, Z0 - T, X0, Z1 + T, 0, H, M["wall"])
box("Стена R", X1, Z0 - T, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена T1", X0 - T, Z0 - T, WX0, Z0, 0, H, M["wall"]); box("Стена T2", WX1, Z0 - T, X1 + T, Z0, 0, H, M["wall"])
box("Под окном", WX0, Z0 - T, WX1, Z0, 0, WS, M["wall"]); box("Над окном", WX0, Z0 - T, WX1, Z0, WT, H, M["wall"])
box("Стена B1", DX1, Z1, X1 + T, Z1 + T, 0, H, M["wall"]); box("Над проёмом", DX0 - T, Z1, DX1, Z1 + T, DH, H, M["wall"])
box("Потолок", X0 - T, Z0 - T, X1 + T, Z1 + T, HC, HC + 0.05, M["ceil"])
for x in (X0 + 1.22, X0 + 2.44):
    box("Шов", x - 0.008, Z1 - 0.004, x + 0.008, Z1, 0, HC, M["seam"])
for z in (Z0 + 1.22,):
    box("Шов", X0, z - 0.008, X0 + 0.004, z + 0.008, 0, HC, M["seam"])
# окно: рама, стекло, подоконник (= столешница), рулонная штора
box("Подоконник", WX0, Z0 - 0.10, WX1, Z0 + 0.02, WS - 0.03, WS, M["tile"])
for (a, b) in ((WX0, WX0 + 0.06), (WX1 - 0.06, WX1), ((WX0 + WX1) / 2 - 0.03, (WX0 + WX1) / 2 + 0.03)):
    box("Рама", a, Z0 - 0.10, b, Z0 - 0.04, WS, WT, M["wframe"])
for (h0, h1) in ((WS, WS + 0.06), (WT - 0.06, WT)): box("Рама", WX0, Z0 - 0.10, WX1, Z0 - 0.04, h0, h1, M["wframe"])
box("Стекло", WX0, Z0 - 0.075, WX1, Z0 - 0.065, WS, WT, M["glass"])
M["sky"] = emis("Вид за окном", "#DCE4EC", 1.6)
box("Небо", WX0 - 1.0, Z0 - 1.6, WX1 + 1.0, Z0 - 1.55, 0.0, 3.6, M["sky"])
box("Штора рулонная", WX0 + 0.02, Z0 - 0.035, WX1 - 0.02, Z0 - 0.03, WT - 0.55, WT - 0.02, M["blind"])
box("Короб шторы", WX0, Z0 - 0.06, WX1, Z0, WT - 0.02, WT + 0.06, M["ward"])
lt = bpy.data.lights.new("Окно", "AREA"); lt.size = 1.6; lt.size_y = 1.5; lt.energy = 260; lt.color = (1, 0.97, 0.92)
o = bpy.data.objects.new("Окно", lt); o.location = W((WX0 + WX1) / 2, Z0 - 0.4, (WS + WT) / 2); o.rotation_euler = (math.radians(90), 0, 0); sc.collection.objects.link(o)

# ---------------- правая стена: нижние модули (плита+духовка, ПММ 450, мойка), столешница, фартук, верхние шкафы
RX = X1 - 0.60; RZ1 = 3.60; CT = 0.90
box("Цоколь", RX + 0.05, Z0, X1, RZ1, 0, 0.10, M["black"])
box("Корпус низ", RX + 0.02, Z0, X1, RZ1, 0.10, CT - 0.04, M["ward"])
box("Гола-профиль", RX, Z0, RX + 0.025, RZ1, CT - 0.10, CT - 0.07, M["black"])
MODS = [(Z0, 2.509, "плита"), (2.509, 2.959, "ПММ"), (2.959, RZ1, "мойка")]
for (a, b, t) in MODS:
    if t == "плита":
        box("Духовка", RX - 0.002, a + 0.03, RX + 0.02, b - 0.03, 0.14, 0.72, M["bglass"], 0.004)
        box("Ящик под духовкой", RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, 0.13, M["ward"], 0.002)
        box("Ящик над духовкой", RX, a + 0.002, RX + 0.02, b - 0.002, 0.73, CT - 0.11, M["ward"], 0.002)
    else:
        box("Фасад " + t, RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, CT - 0.11, M["ward"], 0.002)
box("Столешница", RX - 0.02, Z0, X1, RZ1, CT - 0.04, CT, M["tile"])
box("Варочная индукция", RX + 0.05, Z0 + 0.04, X1 - 0.03, 2.50 - 0.05, CT, CT + 0.006, M["bglass"], 0.003)
for (cx, cz, r) in ((RX + 0.17, Z0 + 0.17, 0.09), (RX + 0.42, Z0 + 0.17, 0.08), (RX + 0.17, 2.30, 0.08), (RX + 0.42, 2.30, 0.10)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.002, location=W(cx, cz, CT + 0.007)); bpy.context.active_object.data.materials.append(M["seam"])
box("Мойка (врезная, графит)", RX + 0.08, 3.03, X1 - 0.10, 3.53, CT - 0.002, CT + 0.001, M["black"])
box("Смеситель стойка", X1 - 0.075, 3.26, X1 - 0.045, 3.30, CT, CT + 0.32, M["black"], 0.008)
box("Смеситель излив", X1 - 0.30, 3.265, X1 - 0.045, 3.295, CT + 0.29, CT + 0.32, M["black"], 0.008)
box("Фартук", X1 - 0.01, Z0, X1, RZ1, CT, 1.50, M["tile"])
UX = X1 - 0.35
box("Верхние шкафы корпус", UX + 0.02, Z0, X1, RZ1, 1.50, HC, M["ward"])
for (a, b) in ((Z0, 2.509), (2.509, 3.06), (3.06, RZ1)):
    box("Фасад верх", UX, a + 0.002, UX + 0.02, b - 0.002, 1.50, HC - 0.002, M["ward"], 0.002)
box("Вытяжка (встроенная)", UX + 0.03, Z0 + 0.03, X1 - 0.02, 2.48, 1.49, 1.50, M["black"])
box("LED под шкафами", UX + 0.04, 2.52, UX + 0.07, RZ1 - 0.02, 1.495, 1.50, M["led"])
lt = bpy.data.lights.new("Рабочая зона", "AREA"); lt.size = 1.0; lt.size_y = 0.06; lt.energy = 22; lt.color = (1, 0.9, 0.78)
o = bpy.data.objects.new("Рабочая зона", lt); o.location = W(X1 - 0.30, (2.52 + RZ1) / 2, 1.48); o.rotation_euler = (0, 0, math.radians(90)); sc.collection.objects.link(o)
for (z_, c) in ((2.62, "white"), (2.69, "black")):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.035, depth=0.20, location=W(X1 - 0.12, z_, CT + 0.10)); bpy.context.active_object.data.materials.append(M[c])
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.09, depth=0.20, location=W(X1 - 0.20, 2.80, CT + 0.10)); bpy.context.active_object.data.materials.append(M["black"])   # чайник

# ---------------- холодильник-колонна (низ-право) и колонна СВЧ + кладовая (нижняя стена)
box("Колонна холодильника", RX + 0.02, RZ1, X1, Z1, 0.10, HC, M["ward"])
box("Цоколь колонн", 11.85, RZ1 + 0.05, X1, Z1, 0, 0.10, M["black"])
box("Фасад холодильника", RX, RZ1 + 0.002, RX + 0.02, Z1 - 0.002, 0.10, 1.95, M["ward"], 0.002)
box("Фасад антресоли", RX, RZ1 + 0.002, RX + 0.02, Z1 - 0.002, 1.96, HC - 0.002, M["ward"], 0.002)
box("Колонна СВЧ", 11.80, RZ1 + 0.02, 12.40, Z1, 0.10, HC, M["ward"])
box("СВЧ", 11.84, RZ1, 12.36, RZ1 + 0.02, 1.35, 1.73, M["bglass"], 0.004)
for (h0, h1) in ((0.10, 1.33), (1.75, HC - 0.002)):
    box("Фасад колонны", 11.802, RZ1, 12.398, RZ1 + 0.02, h0, h1, M["ward"], 0.002)
box("Гола верт.", RX - 0.004, RZ1 - 0.01, RX + 0.02, RZ1 + 0.01, 0.10, HC, M["black"])

# ---------------- угловая банкетка (левая стена + верхняя стена до окна): база графит с ящиками, мягкое сиденье и спинка
BD = 0.50
for (x0, z0, x1, z1) in ((X0, Z0, X0 + BD, 3.509), (X0 + BD, Z0, 11.0, Z0 + 0.48)):
    box("Банкетка база", x0, z0, x1, z1, 0.06, 0.40, M["ward"], 0.004)
    box("Банкетка цоколь", x0 + 0.03, z0 + 0.03, x1 - 0.03, z1 - 0.03, 0, 0.06, M["black"])
    box("Сиденье", x0, z0, x1, z1, 0.40, 0.47, M["knit"], 0.03)
box("Спинка L", X0, Z0 + 0.10, X0 + 0.10, 3.509, 0.47, 0.92, M["knit"], 0.035)
box("Спинка T", X0 + 0.10, Z0, 11.0, Z0 + 0.10, 0.47, 0.92, M["knit"], 0.035)
for (x0, z0, x1, z1) in ((X0 + 0.10, 2.70, X0 + 0.22, 3.05), (10.20, Z0 + 0.10, 10.55, Z0 + 0.22)):
    box("Подушка", x0, z0, x1, z1, 0.47, 0.82, M["towel"], 0.05)

# ---------------- стол 1300×850 (столешница керамогранит, опора чёрная) + 2 стула + подвесы
TCX, TCZ = X0 + 1.2, Z0 + 0.975
box("Стол столешница", TCX - 0.65, TCZ - 0.425, TCX + 0.65, TCZ + 0.425, 0.72, 0.75, M["tile"], 0.006)
box("Стол опора", TCX - 0.30, TCZ - 0.05, TCX + 0.30, TCZ + 0.05, 0.03, 0.72, M["black"])
box("Стол основание", TCX - 0.35, TCZ - 0.25, TCX + 0.35, TCZ + 0.25, 0.0, 0.03, M["black"])
for (cz,) in ((TCZ - 0.24,), (TCZ + 0.24,)):
    Tm = Matrix.Translation(W(TCX + 0.65 + 0.28, cz, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")
    for o_ in bk_load("stul_minimal", Tm):
        for i_, ms in enumerate(o_.data.materials):
            o_.data.materials[i_] = M["knit"] if (ms and "cuir" in ms.name.lower()) else M["black"]
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.12, depth=0.012, location=W(TCX - 0.15, TCZ, 0.756)); bpy.context.active_object.data.materials.append(M["white"])  # блюдо
for dx in (-0.33, 0.33):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.09, depth=0.26, location=W(TCX + dx, TCZ, 1.70)); bpy.context.active_object.data.materials.append(M["black"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.082, depth=0.004, location=W(TCX + dx, TCZ, 1.568)); bpy.context.active_object.data.materials.append(M["shade"])
    box("Шнур", TCX + dx - 0.003, TCZ - 0.003, TCX + dx + 0.003, TCZ + 0.003, 1.83, HC, M["black"])
    lt = bpy.data.lights.new("Подвес", "SPOT"); lt.energy = 18; lt.spot_size = math.radians(70); lt.spot_blend = 0.5; lt.color = (1, 0.88, 0.72)
    o = bpy.data.objects.new("Подвес", lt); o.location = W(TCX + dx, TCZ, 1.56); sc.collection.objects.link(o)

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
ac_unit(("L", X0), 2.50, 2.54)        # К4 над банкеткой

# ---------------- потолок: споты + LED по периметру
spots([(11.6, 2.45), (11.6, 3.40), (12.55, 2.45), (12.55, 3.40)], 30)
for (x0, z0, x1, z1) in ((X0, Z0, X1, Z0 + 0.02), (X0, Z1 - 0.02, X1, Z1), (X0, Z0, X0 + 0.02, Z1), (X1 - 0.02, Z0, X1, Z1)):
    box("LED периметр", x0, z0, x1, z1, HC - 0.012, HC - 0.008, M["led"])

CAMS = {"1": ("1_ot_vhoda", W(9.70, 4.05, 1.60), W(12.60, 2.30, 1.00), 15),
        "2": ("2_rabochaya_zona", W(10.60, 3.55, 1.60), W(12.90, 2.70, 1.05), 16),
        "3": ("3_stolovaya", W(12.20, 3.45, 1.60), W(9.40, 2.25, 0.80), 15),
        "4": ("4_ot_okna", W(11.70, 2.05, 1.70), W(10.80, 4.15, 0.95), 15)}

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
