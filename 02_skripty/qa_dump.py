# -*- coding: utf-8 -*-
"""17.11.2026: ИНСТРУМЕНТ ПРОВЕРКИ — выгрузка собранной 3D-сцены комнаты (без рендера) для qa_check.py.
Запуск: blender -b --factory-startup -P <комната>_blender.py -- qa shots=0
Пишет 08_vizualizacii/<комната>/qa_scene.json: каждый меш — имя, материалы, число вершин, габарит в координатах ПЛАНА
(x, z — как в kvartira.json; h — высота от пола), признак «модель BlenderKit» (подгружена из .blend)."""
import os, json, bpy
from mathutils import Vector

if "qa" in ARGS:
    bpy.context.view_layer.update()
    out = []
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or o.hide_render: continue
        try:
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        except Exception:
            continue
        xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
        me = o.data
        nv = len(me.vertices) if hasattr(me, "vertices") else 0
        mods = [m.type for m in o.modifiers]
        out.append(dict(name=o.name, mats=[(s.material.name if s.material else "") for s in o.material_slots][:4], verts=nv, mods=mods,
                        lib=bool(o.get("_bk")) or (o.library is not None) or nv > 400,
                        x0=round(min(xs), 3), x1=round(max(xs), 3), z0=round(-max(ys), 3), z1=round(-min(ys), 3), h0=round(min(zs), 3), h1=round(max(zs), 3)))
    room = dict(X0=globals().get("X0"), X1=globals().get("X1"), Z0=globals().get("Z0"), Z1=globals().get("Z1"), H=globals().get("HC", globals().get("H", 2.65)))
    d = globals().get("OUT") or os.path.join(PROJ, "08_vizualizacii", globals().get("OUTDIR", "_"))
    os.makedirs(d, exist_ok=True)
    json.dump(dict(room=room, objects=out), open(os.path.join(d, "qa_scene.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("QA выгружено:", len(out), "объектов ->", os.path.join(d, "qa_scene.json"))
