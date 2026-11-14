# -*- coding: utf-8 -*-
"""14.11.2026: «супер-реализм» на бесплатном — выполняется внутри блока real (exec, общие глобалы bpy/sc/PROJ).
1) свет IES — споты становятся точечными с паспортом светораспределения даунлайта (пятна-«арки» на стенах);
2) порталы в окнах — Cycles точнее берёт небо HDRI через окно (меньше шума, правильный дневной свет);
3) шторы — складки глубже книзу, неровные, ткань с рельефом (ambientCG Fabric062, CC0);
4) потёртости — карта ambientCG SurfaceImperfections003 (CC0) в шероховатость глянцевых материалов (пятна/разводы на бликах).
Отключить по пунктам: noies=1 noportal=1 nocurt=1 noimp=1."""
import bpy, bmesh, math, os, random
from mathutils import Vector
_P = os.path.join(PROJ, "03_materialy")
_O = OPT if "OPT" in globals() else {}
random.seed(7)

# ---- 1. IES
def _ies_file():
    fn = os.path.join(_P, "ies", "downlight_60.ies")
    if os.path.exists(fn): return fn
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    ang = list(range(0, 91, 2))
    cd = []
    for a in ang:      # плато ~0–22°, резкий край ~30–38°, слабая засветка до 60°
        c = 1000.0 * math.exp(-(a / 31.0) ** 6) + 45.0 * max(0.0, 1 - a / 62.0)
        if 24 <= a <= 32: c *= 1.06            # светлое кольцо на краю пятна (отражатель)
        cd.append(round(c, 1))
    txt = ["IESNA:LM-63-2002", "[MANUFAC] generated: generic downlight 60 deg", "TILT=NONE",
           f"1 800 1 {len(ang)} 1 1 2 0.08 0.08 0", "1.0 1.0 9",
           " ".join(str(a) for a in ang), "0", " ".join(str(c) for c in cd)]
    open(fn, "w").write("\n".join(txt) + "\n")
    return fn

if _O.get("noies") != "1":
    _f = _ies_file(); _n = 0
    for _o in [o for o in sc.objects if o.type == "LIGHT" and o.data.type == "SPOT"]:
        _l = _o.data; _e = _l.energy; _col = tuple(_l.color)
        _l.type = "POINT"; _l = _o.data; _l.energy = _e * float(_O.get("iesk", "1.15")); _l.color = _col; _l.shadow_soft_size = 0.025
        try: _l.use_nodes = True
        except Exception: pass
        _nt = _l.node_tree
        if _nt is None: continue
        _em = next((n for n in _nt.nodes if n.type == "EMISSION"), None)
        if _em is None:
            _em = _nt.nodes.new("ShaderNodeEmission"); _ou = next((n for n in _nt.nodes if n.type == "OUTPUT_LIGHT"), None) or _nt.nodes.new("ShaderNodeOutputLight")
            _nt.links.new(_em.outputs[0], _ou.inputs[0])
        _ie = _nt.nodes.new("ShaderNodeTexIES"); _ie.mode = "EXTERNAL"; _ie.filepath = _f
        _nt.links.new(_ie.outputs["Fac"], _em.inputs["Strength"]); _n += 1
    print("REAL+ IES:", _n, flush=True)

# ---- 2. порталы окон
if _O.get("noportal") != "1":
    _ctr = Vector((0, 0, 0)); _fl = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("Пол")]
    if _fl:
        _pts = [o.matrix_world @ Vector(c) for o in _fl for c in o.bound_box]; _ctr = sum(_pts, Vector()) / len(_pts)
    for _g in [o for o in sc.objects if o.type == "MESH" and (o.name == "Стекло" or o.name.startswith(("Стекло.", "Стекло двери лоджии")))]:
        _pts = [_g.matrix_world @ Vector(c) for c in _g.bound_box]
        _mn = Vector([min(p[i] for p in _pts) for i in range(3)]); _mx = Vector([max(p[i] for p in _pts) for i in range(3)]); _c = (_mn + _mx) / 2
        _thin = 0 if (_mx.x - _mn.x) < (_mx.y - _mn.y) else 1
        _lt = bpy.data.lights.new("Портал", "AREA"); _lt.shape = "RECTANGLE"
        try: _lt.cycles.is_portal = True
        except Exception:
            try: _lt.is_portal = True
            except Exception: pass
        _w = (_mx.y - _mn.y) if _thin == 0 else (_mx.x - _mn.x); _lt.size = _w; _lt.size_y = _mx.z - _mn.z
        _po = bpy.data.objects.new("Портал", _lt); sc.collection.objects.link(_po)
        _dir = Vector((1, 0, 0)) if _thin == 0 else Vector((0, 1, 0))
        if (_ctr - _c).dot(_dir) < 0: _dir = -_dir
        _po.location = _c + _dir * 0.02
        _po.rotation_euler = _dir.to_track_quat("-Z", "Y").to_euler()   # -Z света смотрит в комнату
        print("REAL+ портал", _g.name, round(_w, 2), round(_mx.z - _mn.z, 2), flush=True)

# ---- 3. шторы
def _fabric_mat(m):
    d = os.path.join(_P, "ambientcg", "Fabric062")
    if m is None or m.node_tree is None or not os.path.isdir(d) or m.get("_fab"): return
    nt = m.node_tree; bs = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bs is None: return
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (6, 6, 6)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nm = nt.nodes.new("ShaderNodeTexImage"); nm.image = bpy.data.images.load(os.path.join(d, "Fabric062_1K-JPG_NormalGL.jpg"), check_existing=True)
    nm.image.colorspace_settings.name = "Non-Color"; nm.projection = "BOX"; nm.projection_blend = 0.3
    nt.links.new(mp.outputs["Vector"], nm.inputs["Vector"])
    nmap = nt.nodes.new("ShaderNodeNormalMap"); nmap.inputs["Strength"].default_value = 0.6
    nt.links.new(nm.outputs["Color"], nmap.inputs["Color"]); nt.links.new(nmap.outputs["Normal"], bs.inputs["Normal"])
    try: bs.inputs["Sheen Weight"].default_value = 0.35
    except Exception: pass
    m["_fab"] = 1

if _O.get("nocurt") != "1":
    for _o in [o for o in sc.objects if o.type == "MESH" and o.name.startswith(("Штора", "Тюль"))]:
        if "рулон" in _o.name: continue
        me = _o.data; vs = me.vertices
        if len(vs) < 8 or len(vs) > 4000: continue
        xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
        z0, z1 = min(zs), max(zs)
        if z1 - z0 < 1.0: continue
        along = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1; nrm = 1 - along
        base = sum(v.co[nrm] for v in vs) / len(vs)
        tops = sorted([v for v in vs if v.co.z > (z0 + z1) / 2], key=lambda v: v.co[along])
        cols = [(v.co[along], v.co[nrm] - base) for v in tops]
        if len(cols) < 3: continue
        tulle = _o.name.startswith("Тюль"); NV = 40
        bm = bmesh.new(); grid = []
        ph = [2.3 * a + 1.4 * math.sin(4.1 * a + 0.7) for a, _ in cols]   # плавно вдоль шторы (без «дождя» из полос)
        for j in range(NV + 1):
            t = j / NV; h = z0 + (z1 - z0) * t; down = 1 - t; row = []
            for i, (a, d) in enumerate(cols):
                k = 1.0 + (0.55 if tulle else 0.85) * down ** 1.5                       # складка глубже книзу
                sway = (0.004 if tulle else 0.007) * down ** 2 * math.sin(ph[i] + 9 * t) # неровность ткани
                hem = (0.006 if not tulle else 0.0) * max(0.0, 1 - t / 0.02)             # подгиб низа
                co = [0.0, 0.0, h]; co[along] = a; co[nrm] = base + d * k + sway + (hem if d > 0 else -hem)
                row.append(bm.verts.new(co))
            grid.append(row)
        for j in range(NV):
            for i in range(len(cols) - 1): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        mats = list(me.materials); nme = bpy.data.meshes.new(me.name + "_r"); bm.to_mesh(nme); bm.free()
        for m in mats: nme.materials.append(m)
        for p in nme.polygons: p.use_smooth = True
        _o.data = nme
        if not tulle and mats: _fabric_mat(mats[0])
    print("REAL+ шторы ok", flush=True)

# ---- 4. потёртости на бликах
if _O.get("noimp") != "1":
    _im = os.path.join(_P, "ambientcg", "SurfaceImperfections003", "SurfaceImperfections003_1K-JPG_Color.jpg")
    if os.path.exists(_im):
        _img = bpy.data.images.load(_im, check_existing=True); _img.colorspace_settings.name = "Non-Color"; _k = 0
        for m in bpy.data.materials:
            if m.node_tree is None or m.get("_imp"): continue
            nt = m.node_tree; bs = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bs is None: continue
            ri = bs.inputs["Roughness"]
            if not ri.is_linked and ri.default_value > 0.55: continue           # матовые не трогаем
            tr = bs.inputs.get("Transmission Weight")
            if tr is not None and not tr.is_linked and tr.default_value > 0.5: continue   # стекло
            tc = nt.nodes.new("ShaderNodeTexCoord"); tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = _img
            tx.projection = "BOX"; tx.projection_blend = 0.4; nt.links.new(tc.outputs["Object"], tx.inputs["Vector"])
            mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.0; mr.inputs["To Max"].default_value = 0.18
            nt.links.new(tx.outputs["Color"], mr.inputs["Value"])
            ad = nt.nodes.new("ShaderNodeMath"); ad.operation = "ADD"; ad.use_clamp = True
            if ri.is_linked: nt.links.new(ri.links[0].from_socket, ad.inputs[0])
            else: ad.inputs[0].default_value = ri.default_value
            nt.links.new(mr.outputs["Result"], ad.inputs[1]); nt.links.new(ad.outputs["Value"], ri)
            m["_imp"] = 1; _k += 1
        print("REAL+ потёртости:", _k, flush=True)
