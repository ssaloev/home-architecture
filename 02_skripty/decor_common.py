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


def dk(name, cx, cz, h0=0.0, rot=0.0, size=None, axis="w", wall=None):
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


if OPT.get("decor", "1") == "1":
    R_ = globals().get("OUTDIR") or os.path.basename(globals().get("OUT", ""))
    if R_ == "komnata":
        _sw = globals().get("SWAP", True)                # SWAP: ТВ у правой стены (X1), диван у левой (X0)
        dk("kartina_2", (X0 + 0.03) if _sw else (X1 - 0.03), tm, 1.05, size=0.80, wall=("L" if _sw else "R"))
        dk("vazy_3", (X1 - 0.22) if _sw else (X0 + 0.22), tm - 1.05, 0.32, 90, 0.55)
        dk("svechi", 7.05, tm + 0.20, 0.47, 0, 0.18)
        dk("vaza_frukty", 7.25, tm - 0.25, 0.47, 0, 0.30)
        dk("sansevieriya", (X1 - 0.30) if _sw else (X0 + 0.30), Z0 + 0.45, 0.0, 0, 0.75, "h")
    elif R_ == "spalnya2":
        for xx in (BC - 1.025, BC + 1.025): dk("lampa_nastol", xx, Z0 + 0.22, 0.45, 0, 0.42, "h")
        dk("podushki_dekor", BC, Z0 + 0.55, 0.56, 0, 0.90)
        dk("kartina_2", 14.15, Z1 - 0.03, 1.35, size=0.55, wall="B")
        dk("sansevieriya", X1 - 0.30, Z1 - 0.30, 0.0, 0, 0.80, "h")
        dk("svechi", 14.35, Z1 - 0.22, 0.75, 0, 0.15)
    elif R_ == "kuhnya":
        dk("posuda_4", 11.45, Z0 + 0.36, 0.75, 0, 0.42)
        dk("vaza_frukty", 11.75, Z0 + 0.30, 0.75, 0, 0.28)
        dk("doska_razdel", X1 - 0.30, 3.75, 0.90, 90, 0.36)
        dk("vazy_3", X1 - 0.18, 3.25, 1.52, 90, 0.30) if False else None
        dk("sansevieriya", X0 + 0.30, 4.40, 0.0, 0, 0.70, "h")
    elif R_ == "vannaya":
        dk("vanna_aksessuary", X1 - 0.16, SZ0 + 0.10, CT, -90, 0.22)
        dk("polotenca_stopka", X1 - 0.30, 8.55, 0.86, -90, 0.30)
        dk("kovrik_seryi", X0 + 1.15, 9.05, 0.0, 90, 0.95)
        dk("svechi", X0 + 0.12, BZ0 + 0.12, 0.58, 0, 0.14)
        dk("sansevieriya", X0 + 0.95, Z0 + 0.25, 0.0, 0, 0.65, "h")
    elif R_ == "sanuzel":
        dk("vanna_aksessuary", X1 - 0.12, Z0 + 0.10, CT, 0, 0.22)
        dk("polotence_visit", X1 - 0.03, 7.90, 0.85, size=0.45, wall="R")
        dk("kovrik_seryi", (X0 + X1) / 2, 7.45, 0.0, 90, 0.60)
        dk("svechi", X1 - 0.33, Z0 + 0.10, CT, 0, 0.12)
