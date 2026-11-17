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


def mute(objs, sat=0.12):
    """17.11 (проверка «палитра»): приглушить цвет текстур картины/ковра до почти серого"""
    for o in objs:
        if o.type != "MESH": continue
        for sl in o.material_slots:
            m = sl.material
            if not (m and m.use_nodes) or m.get("_muted"): continue
            nt = m.node_tree; b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if b is None: continue
            inp = b.inputs["Base Color"]
            hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = sat
            if inp.is_linked: nt.links.new(inp.links[0].from_socket, hs.inputs["Color"])
            else: hs.inputs["Color"].default_value = inp.default_value
            nt.links.new(hs.outputs["Color"], inp); m["_muted"] = 1


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
    # 17.11 (заказчик: «что это такое» — тюль перекрасился в синий и штора была с одной стороны):
    # тюль (sheer) оставляем белым полупрозрачным на всю ширину; плотную штору сужаем до ~0,6 м у края окна и зеркально ставим вторую
    dr = [o for o in objs if o.type == "MESH" and "sheer" not in o.name.lower()]
    bpy.context.view_layer.update()
    _tm = bpy.data.materials.new("Тюль плотный белый"); _tm.use_nodes = True                      # 17.11 («а это?»): тюль серыми «трубами» и
    _tb = next(n for n in _tm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")                   # сквозь него видна рама — делаем плотнее и белее
    _tb.inputs["Base Color"].default_value = (0.93, 0.93, 0.92, 1); _tb.inputs["Roughness"].default_value = 0.85
    for _k, _v in (("Transmission Weight", 0.15), ("Alpha", 0.92), ("Subsurface Weight", 0.25)):
        if _k in _tb.inputs: _tb.inputs[_k].default_value = _v
    for o in [o for o in objs if o.type == "MESH" and "sheer" in o.name.lower()]: o.data.materials.clear(); o.data.materials.append(_tm)
    for o in [o for o in objs if o.type == "MESH" and "sheer" in o.name.lower()]:      # тюль — на всю ширину окна
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]; ax = 0 if wall in "TB" else 1
        a0 = min(p[ax] for p in pts); a1 = max(p[ax] for p in pts); c_ = W(cx, cz, 0)[ax]
        k = (width - 0.3) / max(0.01, a1 - a0); Sv = [1.0, 1.0, 1.0]; Sv[ax] = k
        o.matrix_world = Matrix.Diagonal((Sv[0], Sv[1], Sv[2], 1.0)) @ o.matrix_world
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]; mid = (min(p[ax] for p in pts) + max(p[ax] for p in pts)) / 2
        t = Vector((0, 0, 0)); t[ax] = c_ - mid; o.matrix_world = Matrix.Translation(t) @ o.matrix_world
    for o in dr:
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn_ = Vector([min(p[i] for p in pts) for i in range(3)]); mx_ = Vector([max(p[i] for p in pts) for i in range(3)])
        ax = 0 if wall in "TB" else 1
        wnd_c = W(cx, cz, 0)[ax]
        far = mx_[ax] if abs(mx_[ax] - wnd_c) > abs(mn_[ax] - wnd_c) else mn_[ax]
        k = min(1.0, 0.62 / max(0.01, mx_[ax] - mn_[ax]))
        Sv = [1.0, 1.0, 1.0]; Sv[ax] = k
        piv = Vector((0, 0, 0)); piv[ax] = far
        o.matrix_world = Matrix.Translation(piv) @ Matrix.Diagonal((Sv[0], Sv[1], Sv[2], 1.0)) @ Matrix.Translation(-piv) @ o.matrix_world
        c2 = o.copy(); bpy.context.scene.collection.objects.link(c2); objs.append(c2)
        Mv = [1.0, 1.0, 1.0]; Mv[ax] = -1.0; cvec = Vector((0, 0, 0)); cvec[ax] = wnd_c
        c2.matrix_world = Matrix.Translation(cvec) @ Matrix.Diagonal((Mv[0], Mv[1], Mv[2], 1.0)) @ Matrix.Translation(-cvec) @ o.matrix_world
    for o in objs:
        if o.type != "MESH" or "sheer" in o.name.lower(): continue
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
    # 17.11 (заказчик: «настрой скрипт, чтобы такое просто не могло быть»): ЗАЩИТА — шторы не могут проходить сквозь
    # подоконник, раму, стекло, стену: отодвигаем от стены, пока зазор до самого выступающего элемента окна < 2 см
    bpy.context.view_layer.update()
    ax = 1 if wall in "TB" else 0                          # ось «от стены» в координатах Blender
    sgn = {"T": -1, "B": 1, "L": 1, "R": -1}[wall]         # куда «в комнату» по этой оси (W: z плана → -y)
    hard = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_render and o not in objs
            and o.name.lower().startswith(("подоконник", "рама", "импост", "стекло", "откос", "стена", "под окном", "над окном", "простен"))]
    def _ext(obs):
        P = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
        return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])
    cmn, cmx = _ext([o for o in objs if o.type == "MESH"])
    shift = 0.0
    for h in hard:
        hmn, hmx = _ext([h])
        if all(min(cmx[i], hmx[i]) - max(cmn[i], hmn[i]) > 0 for i in range(3) if i != ax) or True:
            ov_other = all(min(cmx[i], hmx[i]) - max(cmn[i], hmn[i]) > 0.01 for i in range(3) if i != ax)
            if not ov_other: continue
            cc = (cmn[ax] + cmx[ax]) / 2; hc = (hmn[ax] + hmx[ax]) / 2
            if (hc - cc) * sgn > 0: continue                # препятствие со стороны комнаты (противоположная стена) — не наше
            face = hmx[ax] if sgn > 0 else hmn[ax]          # грань препятствия, обращённая в комнату
            back = cmn[ax] if sgn > 0 else cmx[ax]          # задняя (к стене) грань штор
            need = (face + 0.02 - back) if sgn > 0 else (back - (face - 0.02))
            shift = max(shift, need)
    if shift > 0:
        t = Vector((0, 0, 0)); t[ax] = sgn * shift
        for o in objs:
            if o.parent is None or o.parent not in objs: o.matrix_world = Matrix.Translation(t) @ o.matrix_world
        print("DECOR шторы отодвинуты от окна на", round(shift * 1000), "мм")
    print("DECOR шторы-модель", round(width, 2))
    return objs


if OPT.get("decor", "1") == "1":
    R_ = globals().get("OUTDIR") or os.path.basename(globals().get("OUT", ""))
    if R_ == "komnata":
        _gf = mat("Мебель мягкая серая", "#5C5C5A", 0.9)        # 17.11 заказчик: «мебель серая» — диван и кресла серые
        _roots = set(list(globals().get("_sofa") or []) + list(globals().get("_ch") or []))
        def _anc(o):
            while o is not None:
                if o in _roots: return True
                o = o.parent
            return False
        for _o in [o for o in bpy.context.scene.objects if _anc(o)]:
            if _o.type != "MESH": continue
            for _sl in _o.material_slots:
                _m = _sl.material; _b = next((n for n in _m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (_m and _m.use_nodes) else None
                if _b is not None and (_b.inputs["Metallic"].is_linked or _b.inputs["Metallic"].default_value > 0.5): continue
                _sl.material = _gf
        if OPT.get("curt2", "1") == "1" and "WX0" in globals(): curtains_model((WX0 + WX1) / 2, Z0 + 0.10, (WX1 - WX0) + 0.70, "T", globals().get("HC", 2.62) - 0.04)
        _sw = globals().get("SWAP", True)                # SWAP: ТВ у правой стены (X1), диван у левой (X0)
        _tx = (2 * (X0 + X1) / 2 - 7.15) if _sw else 7.15   # центр столика (после поворота группы)
        mute(dk("kartina_2", (X0 + 0.03) if _sw else (X1 - 0.03), tm, 1.05, size=0.80, wall=("L" if _sw else "R")))
        mute([o for o in bpy.context.scene.objects if o.type == "MESH" and any(sl.material and "kover" in sl.material.name.lower() or (sl.material and "rug" in sl.material.name.lower()) or (sl.material and "carpet" in sl.material.name.lower()) for sl in o.material_slots)], 0.0)
        mute([o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.lower().startswith(("ковер", "ковёр", "rug", "carpet"))], 0.0)
        mute(dk("vazy_3", (X1 - 0.22) if _sw else (X0 + 0.22), tm - 1.05, 0.32, 90, 0.55), 0.05)
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
        mute(dk("kartina_2", 14.15, Z1 - 0.03, 1.35, size=0.55, wall="B"))
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
        # 18.11: растение убрано — декор ванной согласуется с заказчиком отдельно (палитра: без зелёного)
    elif R_ == "sanuzel":
        _st = dk("polotenca_stopka", X1 - 0.225, Z0 + 0.10, "auto:0.33", 0, 0.30)   # 17.11: полка под шкафчиком — стопка полотенец «как в отеле»
        _twc = [(0.86, 0.85, 0.82, 1), (0.55, 0.55, 0.54, 1)]   # в модели цветные — перекрасить: белые / серые по очереди
        for _i, o in enumerate([o for o in (_st or []) if o.type == "MESH"]):
            _m = bpy.data.materials.new("Полотенце стопка %d" % _i); _m.use_nodes = True
            _b = next(n_ for n_ in _m.node_tree.nodes if n_.type == "BSDF_PRINCIPLED"); _b.inputs["Base Color"].default_value = _twc[_i % 2]; _b.inputs["Roughness"].default_value = 1.0
            for i_ in range(len(o.data.materials)): o.data.materials[i_] = _m
        def _one_towel(_tw, col):   # в модели несколько полотенец — оставить одно (самое большое), перекрасить
            if not _tw: return
            _big = max(_tw, key=lambda o: len(o.data.vertices) if o.type == "MESH" else 0)
            _gm = bpy.data.materials.new("Полотенце крючок"); _gm.use_nodes = True
            _gb = next(n_ for n_ in _gm.node_tree.nodes if n_.type == "BSDF_PRINCIPLED"); _gb.inputs["Base Color"].default_value = col; _gb.inputs["Roughness"].default_value = 1.0
            for o in _tw:
                if o.type != "MESH": continue
                if o is not _big: o.hide_render = True; continue
                for i_ in range(len(o.data.materials)): o.data.materials[i_] = _gm
        for _xx, _c in ((1.24, (0.86, 0.85, 0.82, 1)), (1.33, (0.50, 0.50, 0.49, 1))):   # 17.11: полотенца на крючках рядом с сушителем
            _one_towel(dk("polotence_visit", _xx, Z0 + 0.03, 1.22, size=0.30, wall="T"), _c)
        _tw = None   # крючки у двери — для одежды (полотенца теперь у сушителя)
        if False:
            _big = max(_tw, key=lambda o: len(o.data.vertices) if o.type == "MESH" else 0)
            _gm = bpy.data.materials.new("Полотенце серое"); _gm.use_nodes = True
            _gb = next(n_ for n_ in _gm.node_tree.nodes if n_.type == "BSDF_PRINCIPLED"); _gb.inputs["Base Color"].default_value = (0.42, 0.42, 0.41, 1); _gb.inputs["Roughness"].default_value = 1.0
            for o in _tw:
                if o.type != "MESH": continue
                if o is not _big: o.hide_render = True; continue
                for i_ in range(len(o.data.materials)): o.data.materials[i_] = _gm
        dk("kovrik_seryi", (X0 + X1) / 2, 7.45, 0.0, 90, 0.60)
