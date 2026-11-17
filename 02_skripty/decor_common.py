# -*- coding: utf-8 -*-
"""17.11.2026 (заказчик: «как у SM — картинка сразу дорогая, у нас пусто и дёшево»): ДЕКОР в каждой комнате.
Бесплатные модели BlenderKit (03_materialy/blenderkit): вазы, посуда, картины, растения, полотенца, свечи, коврики, лампы.
Выполняется exec() внутри скрипта комнаты (нужны bpy, Matrix, Vector, math, W(), PROJ/BK, OUTDIR). Отключить: decor=0.
dk(name, cx, cz, h0, rot, size, axis) — поставить модель: центр (cx, cz) в координатах плана, низ на h0, поворот rot° вокруг вертикали,
  масштаб так, чтобы габарит по axis ("w" — ширина, "h" — высота) был size. wall=("R"|"L"|"T"|"B") — повесить на стену (картина/зеркало)."""
import os, math
import bpy
from mathutils import Matrix, Vector

_BKD = os.path.join(PROJ, "03_materialy", "blenderkit")


def _load(name):
    f = os.path.join(_BKD, name + ".blend")
    if not os.path.exists(f): print("DECOR нет файла", name); return []
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [n for n in src.objects]
    objs = [o for o in dst.objects if o is not None and o.type not in ("LIGHT", "CAMERA")]
    for o in objs:
        try: bpy.context.scene.collection.objects.link(o)
        except Exception: pass
    return objs


def _bbox(objs):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    if not pts: return None, None
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def top_at(cx, cz, skip=(), start=2.9):
    """высота верхней поверхности под точкой (луч сверху вниз) — чтобы предмет стоял, а не висел"""
    dg = bpy.context.evaluated_depsgraph_get(); o = W(cx, cz, start); d = Vector((0, 0, -1)); h = 0.0
    for _ in range(6):
        ok, loc, nrm, idx, ob, mt = bpy.context.scene.ray_cast(dg, o, d)
        if not ok: break
        if ob in skip or ob.name.lower().startswith(("потолок", "перекрыт", "спот", "led", "балка", "шнур", "подвес", "torus", "cube")):
            o = loc + d * 0.002; continue
        h = loc.z; break
    return h


def dk(name, cx, cz, h0=0.0, rot=0.0, size=None, axis="w", wall=None):
    if isinstance(h0, str) and h0.startswith("auto"): h0 = top_at(cx, cz, start=float(h0[5:]) if ":" in h0 else 2.9)   # "auto:1.2" — луч ниже навесных шкафов
    objs = _load(name)
    if not objs: return []
    roots = [o for o in objs if o.parent is None or o.parent not in objs]
    mn, mx = _bbox(objs)
    if mn is None: return objs
    d = mx - mn
    if wall and d.z < min(d.x, d.y):                    # картина/зеркало лежит плашмя — поставить на ребро
        for r in roots: r.matrix_world = Matrix.Rotation(math.radians(90), 4, "X") @ r.matrix_world
        mn, mx = _bbox(objs); d = mx - mn
    if wall:                                            # тонкой стороной к стене
        if d.x < d.y:
            for r in roots: r.matrix_world = Matrix.Rotation(math.radians(90), 4, "Z") @ r.matrix_world
            mn, mx = _bbox(objs); d = mx - mn
        rot = {"T": 0, "B": 180, "L": 90, "R": -90}[wall]
    cur = {"w": max(d.x, d.y), "h": d.z}[axis]
    k = (size / cur) if (size and cur > 1e-6) else 1.0
    ctr = (mn + mx) / 2
    T = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot), 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T @ r.matrix_world
    print("DECOR", name, round(k, 3))
    return objs


def curtains_model(cx, cz, width, wall, h_top):
    """17.11 (заказчик: «шторы нормальные найди»): модель «Gray linen curtain» (тюль + плотная штора) вместо процедурных;
    плотная ткань перекрашивается в цвет штор проекта (тёмно-синий), тюль остаётся светлым. Растягивается по ширине окна и до потолка."""
    objs = _load("shtory_len")
    if not objs: return []
    roots = [o for o in objs if o.parent is None or o.parent not in objs]
    mn, mx = _bbox(objs); d = mx - mn
    if d.x < d.y:
        for r in roots: r.matrix_world = Matrix.Rotation(math.radians(90), 4, "Z") @ r.matrix_world
        mn, mx = _bbox(objs); d = mx - mn
    S = Matrix.Diagonal((width / d.x, 1.0, (h_top + 0.05) / d.z, 1.0))   # +5 см: подол лежит на полу, без щели
    ctr = (mn + mx) / 2
    rot = {"T": 0, "B": 180, "L": 90, "R": -90}[wall]
    T = Matrix.Translation(W(cx, cz, -0.02)) @ Matrix.Rotation(math.radians(rot), 4, "Z") @ S @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    for r in roots: r.matrix_world = T @ r.matrix_world
    for o in objs:
        if o.type != "MESH": continue
        for sl in o.material_slots:
            m = sl.material
            b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (m and m.use_nodes) else None
            col = b.inputs["Base Color"].default_value if b is not None else (1, 1, 1, 1)
            lum = 0.3 * col[0] + 0.59 * col[1] + 0.11 * col[2]
            if b is not None and (b.inputs["Base Color"].is_linked or lum < 0.6) and "tul" not in m.name.lower() and "sheer" not in m.name.lower():
                sl.material = M["curt"]
    for o in list(bpy.context.scene.objects):          # убрать процедурные шторы и тюль (кроме рулонной)
        n = o.name.lower()
        if (n.startswith("штора") or n.startswith("тюль")) and "рулон" not in n: o.hide_render = True; o.hide_viewport = True
    print("DECOR шторы-модель", round(width, 2))
    return objs


if OPT.get("decor", "1") == "1":
    R_ = globals().get("OUTDIR") or os.path.basename(globals().get("OUT", ""))
    if R_ == "komnata":
        if OPT.get("curt2", "1") == "1" and "WX0" in globals(): curtains_model((WX0 + WX1) / 2, Z0 + 0.10, (WX1 - WX0) + 0.70, "T", globals().get("HC", 2.62) - 0.04)
        _sw = globals().get("SWAP", True)                # SWAP: ТВ у правой стены (X1), диван у левой (X0)
        _tx = (2 * (X0 + X1) / 2 - 7.15) if _sw else 7.15   # центр столика (после поворота группы)
        dk("kartina_2", (X0 + 0.03) if _sw else (X1 - 0.03), tm, 1.05, size=0.80, wall=("L" if _sw else "R"))
        dk("vazy_3", (X1 - 0.22) if _sw else (X0 + 0.22), tm - 1.05, 0.32, 90, 0.55)
        dk("svechi", _tx - 0.10, tm + 0.20, "auto", 0, 0.18)
        dk("vaza_frukty", _tx + 0.10, tm - 0.25, "auto", 0, 0.30)
        dk("sansevieriya", (X1 - 0.30) if _sw else (X0 + 0.30), Z0 + 0.45, 0.0, 0, 0.75, "h")
    elif R_ == "spalnya2":
        _g = mat("Текстиль серый (акцент)", "#8E8E8C", 0.95) if "mat" in globals() else None
        for _o in list(bpy.context.scene.objects):          # 17.11: персиковые подушки/плед модели кровати → серые (палитра)
            if _o.type != "MESH" or _g is None: continue
            for _sl in _o.material_slots:
                _m = _sl.material; _b = next((n for n in _m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (_m and _m.use_nodes) else None
                if _b is None or _b.inputs["Base Color"].is_linked: continue
                _c = _b.inputs["Base Color"].default_value
                if _c[0] - _c[2] > 0.18 and _c[0] > 0.35: _sl.material = _g
        if OPT.get("curt2", "1") == "1" and "WZ0" in globals(): curtains_model(X1 - 0.12, (WZ0 + WZ1) / 2, (WZ1 - WZ0) + 0.60, "R", globals().get("HC", 2.62) - 0.04)
        for xx in (BC - 1.03, BC + 1.03): dk("lampa_nastol", xx, Z0 + 0.22, "auto", 0, 0.42, "h")
        dk("kartina_2", 14.15, Z1 - 0.03, 1.35, size=0.55, wall="B")
        dk("sansevieriya", X1 - 0.30, Z1 - 0.30, 0.0, 0, 0.80, "h")
        dk("svechi", 14.35, Z1 - 0.22, "auto", 0, 0.15)
    elif R_ == "kuhnya":
        dk("posuda_4", 11.45, Z0 + 0.36, "auto", 0, 0.42)
        dk("vaza_frukty", 11.75, Z0 + 0.30, "auto", 0, 0.28)
        dk("doska_razdel", X1 - 0.30, 3.75, "auto:1.3", 90, 0.36)
        dk("vazy_3", X1 - 0.18, 3.25, 1.52, 90, 0.30) if False else None
        dk("sansevieriya", X0 + 0.30, 4.40, 0.0, 0, 0.70, "h")
    elif R_ == "vannaya":
        dk("vanna_aksessuary", X1 - 0.16, SZ0 + 0.10, "auto:1.15", -90, 0.22)
        for _o in dk("polotenca_stopka", X1 - 0.30, 8.55, "auto:1.15", -90, 0.30):   # 17.11: полотенца в палитре (белые/серые), не радужные
            if _o.type == "MESH":
                for _i, _sl in enumerate(_o.material_slots): _sl.material = M["white"] if _i % 2 == 0 else M.get("towel", M["white"])
        dk("kovrik_seryi", X0 + 1.15, 9.05, 0.0, 90, 0.95)
        dk("svechi", X0 + 0.12, BZ0 + 0.12, 0.58, 0, 0.14)
        dk("sansevieriya", X0 + 0.95, Z0 + 0.25, 0.0, 0, 0.65, "h")
    elif R_ == "sanuzel":
        dk("vanna_aksessuary", X1 - 0.12, Z0 + 0.10, "auto:1.3", 0, 0.22)
        dk("polotence_visit", X1 - 0.03, 7.90, 0.85, size=0.45, wall="R")
        dk("kovrik_seryi", (X0 + X1) / 2, 7.45, 0.0, 90, 0.60)
        dk("svechi", X1 - 0.33, Z0 + 0.10, "auto:1.3", 0, 0.12)
