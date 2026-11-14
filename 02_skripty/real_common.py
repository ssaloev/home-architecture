# -*- coding: utf-8 -*-
"""14.11.2026: блок «real» для скриптов без своего (гостиная 1, коридор) — как в komnata_blender.py:
фаски на мебели, небо HDRI в окне, долгий расчёт, затем real_plus.py (IES, порталы, шторы, потёртости).
Камеру не трогаем (ракурсы гостиной и коридора уже согласованы)."""
import os, bpy
PROJ = globals().get("PROJ", r"D:\PROJECT\sadi_architertura")
OPT = globals().get("OPT") or dict(a.split("=", 1) for a in ARGS if "=" in a)
for _o in [o for o in sc.objects if o.type == "MESH" and len(o.data.vertices) <= 24 and not o.name.startswith(("Пол", "Стена", "Потолок", "Окно", "Над", "Под", "Стекло"))]:
    _ds = [x for x in _o.dimensions if x > 0]
    if not _ds or max(_ds) < 0.01: continue
    _b = _o.modifiers.new("fаска", "BEVEL"); _b.width = min(0.004, min(_ds) * 0.3); _b.segments = 2; _b.limit_method = "ANGLE"
_hd = os.path.join(PROJ, "03_materialy", "hdri", "sky.hdr")
if os.path.exists(_hd) and OPT.get("hdri", "1") == "1":
    _w = sc.world or bpy.data.worlds.new("W"); sc.world = _w
    try: _w.use_nodes = True
    except Exception: pass
    _nt = _w.node_tree
    _bg = _nt.nodes.get("Background") or _nt.nodes.new("ShaderNodeBackground"); _env = _nt.nodes.new("ShaderNodeTexEnvironment")
    _env.image = bpy.data.images.load(_hd, check_existing=True); _nt.links.new(_env.outputs["Color"], _bg.inputs["Color"])
    _bg.inputs["Strength"].default_value = float(OPT.get("sky", "1.0"))
    _ou = next((n for n in _nt.nodes if n.type == "OUTPUT_WORLD"), None) or _nt.nodes.new("ShaderNodeOutputWorld")
    _nt.links.new(_bg.outputs[0], _ou.inputs["Surface"])
sc.cycles.samples = int(OPT.get("samples", "500")); sc.cycles.adaptive_threshold = 0.01
sc.cycles.max_bounces = 12; sc.cycles.diffuse_bounces = 6; sc.cycles.glossy_bounces = 6; sc.cycles.sample_clamp_indirect = 8
sc.view_settings.exposure += float(OPT.get("dexp", "0"))
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
if OPT.get("plus", "1") == "1":
    exec(open(os.path.join(PROJ, "02_skripty", "real_plus.py"), encoding="utf-8").read())
