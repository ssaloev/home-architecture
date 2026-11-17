# -*- coding: utf-8 -*-
"""17.11.2026 (проверка: «мебель — коробки»): детали встроенной мебели в режиме real.
Фасады (объекты «Фасад…», «Ящик…», «Дверца…») уменьшаются на 1,5 мм с каждой стороны в плоскости фасада —
между дверцами появляются настоящие тёмные зазоры 3 мм, как у реальной мебели; плюс фаска 1,5 мм. Отключить: fdet=0."""
import bpy
from mathutils import Vector
if OPT.get("fdet", "1") == "1":
    _n = 0
    for o in list(bpy.context.scene.objects):
        if o.type != "MESH": continue
        nm = o.name.lower()
        if not nm.startswith(("фасад", "ящик", "дверца")): continue
        me = o.data
        if len(me.vertices) > 64: continue
        vs = [v.co.copy() for v in me.vertices]
        mn = Vector([min(v[i] for v in vs) for i in range(3)]); mx = Vector([max(v[i] for v in vs) for i in range(3)])
        dims = mx - mn; thin = min(range(3), key=lambda i: dims[i])
        g = 0.0015
        for v in me.vertices:
            for i in range(3):
                if i == thin or dims[i] < 4 * g: continue
                c = (mn[i] + mx[i]) / 2
                v.co[i] = v.co[i] - g if v.co[i] > c else v.co[i] + g
        if not any(m.type == "BEVEL" for m in o.modifiers):
            b = o.modifiers.new("fdet_bevel", "BEVEL"); b.width = 0.0015; b.segments = 2; b.limit_method = "ANGLE"
        _n += 1
    print("Детали фасадов:", _n)
