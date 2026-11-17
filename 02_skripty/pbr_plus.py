# -*- coding: utf-8 -*-
"""17.11.2026 (заказчик: «не реалистично — текстуры и мебель как коробки»): ФОТО-ФАКТУРЫ ambientCG (CC0) вместо гладких цветов.
Выполняется в режиме real (из real_plus.py), когда сцена уже собрана. По имени материала:
  керамогранит (мокрые зоны) → Marble012 + швы плитки 600×1200;  пол (ламинат/SPC) → WoodFloor051, обесцвечен и затемнён до тёмно-серого;
  стены/обои/панели → рельеф PaintedPlaster017;  фасады/мебель → лёгкий рельеф Concrete034 (матовая краска);
  ткани (диван, кровать, шторы, ковёр) → Fabric061 (рельеф ткани).
Цвет каждого материала сохраняется (кроме плитки и пола). Отключить: pbr=0."""
import os, bpy

_AC = os.path.join(globals().get("PROJ") or os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03_materialy", "ambientcg")


def _img(asset, kind, non_color=False):
    f = os.path.join(_AC, asset, f"{asset}_2K-JPG_{kind}.jpg")
    if not os.path.exists(f): return None
    im = bpy.data.images.load(f, check_existing=True)
    if non_color: im.colorspace_settings.name = "Non-Color"
    return im


def _setup(m, asset, scale, color=True, nstr=0.6, rough=True, tint=None, gray=False, grout=None):
    if not m.use_nodes: m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    b = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if b is None: return
    base = tuple(b.inputs["Base Color"].default_value)
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / scale,) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def tex(img):
        t = N.new("ShaderNodeTexImage"); t.image = img; t.projection = "BOX"; t.projection_blend = 0.25
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    if color:
        ci = _img(asset, "Color")
        if ci:
            t = tex(ci); out = t.outputs["Color"]
            if gray or tint:
                hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 0.0 if gray else 1.0
                L.new(out, hs.inputs["Color"]); out = hs.outputs["Color"]
            if tint:
                mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
                L.new(out, mx.inputs[6]); mx.inputs[7].default_value = tint; out = mx.outputs[2]
            if grout:                                   # швы плитки: Brick Texture (раскладка вразбежку 0)
                br = N.new("ShaderNodeTexBrick"); br.offset = 0.0; br.squash = 1.0
                br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = 0.0025
                br.inputs["Brick Width"].default_value = grout[0]; br.inputs["Row Height"].default_value = grout[1]
                br.inputs["Color1"].default_value = (1, 1, 1, 1); br.inputs["Color2"].default_value = (1, 1, 1, 1)
                br.inputs["Mortar"].default_value = (0.55, 0.55, 0.55, 1)
                L.new(tc.outputs["Object"], br.inputs["Vector"])
                mx2 = N.new("ShaderNodeMix"); mx2.data_type = "RGBA"; mx2.blend_type = "MULTIPLY"; mx2.inputs["Factor"].default_value = 1.0
                L.new(out, mx2.inputs[6]); L.new(br.outputs["Color"], mx2.inputs[7]); out = mx2.outputs[2]
            L.new(out, b.inputs["Base Color"])
    if rough:
        ri = _img(asset, "Roughness", True)
        if ri:
            t = tex(ri); mr = N.new("ShaderNodeMapRange")
            mr.inputs["To Min"].default_value = max(0.05, b.inputs["Roughness"].default_value - 0.15)
            mr.inputs["To Max"].default_value = min(1.0, b.inputs["Roughness"].default_value + 0.15)
            L.new(t.outputs["Color"], mr.inputs["Value"]); L.new(mr.outputs["Result"], b.inputs["Roughness"])
    ni = _img(asset, "NormalGL", True)
    if ni:
        t = tex(ni); nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nstr
        L.new(t.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])


def _bk_imgs(name):
    """картинки (цвет, шероховатость, нормаль) из материала BlenderKit 03_materialy/blenderkit/<name>.blend"""
    f = os.path.join(os.path.dirname(_AC), "blenderkit", name + ".blend")
    if not os.path.exists(f): return None
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.materials = list(src.materials)
    out = {}
    for mm in dst.materials:
        if not mm or not mm.use_nodes: continue
        for nd in mm.node_tree.nodes:
            if nd.type == "TEX_IMAGE" and nd.image:
                k = nd.image.name.lower()
                if "rough" in k: out["r"] = nd.image
                elif "norm" in k or "nrm" in k: out["n"] = nd.image
                elif nd.image.colorspace_settings.name.lower().startswith("srgb") and "c" not in out: out["c"] = nd.image
    return out or None


def _wall_bk(m, I, rep):
    if not m.use_nodes: m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    b = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if b is None: return
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / rep,) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def tx(img, nc=False):
        t = N.new("ShaderNodeTexImage"); t.image = img; t.projection = "BOX"; t.projection_blend = 0.1
        if nc: img.colorspace_settings.name = "Non-Color"
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    if "c" in I:
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
        k_ = float(OPT.get("oboi_tint", "0.58")); mx.inputs[7].default_value = (k_, k_, k_ * 0.99, 1)   # 17.11: серые, темнее (заказчик)
        L.new(tx(I["c"]).outputs["Color"], mx.inputs[6]); L.new(mx.outputs[2], b.inputs["Base Color"])
    if "r" in I: L.new(tx(I["r"], True).outputs["Color"], b.inputs["Roughness"])
    if "n" in I:
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.5
        L.new(tx(I["n"], True).outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])


_OB = _bk_imgs(OPT.get("oboi_bk", "oboi_11_mandala")) if OPT.get("oboi_bk", "oboi_11_mandala") not in ("0", "") else None
if OPT.get("pbr", "1") == "1":
    _done = 0
    for m in list(bpy.data.materials):
        n = m.name.lower()
        try:
            if n.startswith("керамогранит"):
                _T = {"terr": ("Tiles043", 0.9, True, (0.30, 0.30, 0.30, 1), None),                 # тёмно-серое терраццо (17.11 — «отвратительно»)
                      "A": ("Concrete034", 1.2, True, (0.26, 0.26, 0.26, 1), (0.6, 1.2)),          # почти чёрный графит, матовый 600×1200 (17.11 заказчик: ещё темнее — чтобы серо-белые изделия выделялись)
                      "B": ("Marble003", 1.2, True, (1.0, 1.0, 1.0, 1), (0.6, 1.2)),               # светлый мрамор, лёгкие прожилки
                      "C": ("Concrete046", 1.2, True, (0.55, 0.55, 0.55, 1), (0.6, 1.2)),          # тёмно-серый матовый, 600×1200
                      "D": ("Marble012", 1.2, False, (0.92, 0.92, 0.92, 1), (0.6, 1.2))}[OPT.get("tile", "A")]
                _setup(m, _T[0], _T[1], gray=_T[2], tint=_T[3], grout=_T[4], nstr=0.06)   # 17.11: рельеф плитки едва заметный (было «мокрая штукатурка»)
            elif n.startswith("пол") and not n.startswith(("полот", "полк", "полир", "полос")) and "керамогранит" not in n:   # 17.11: «Полотенце» получало текстуру пола
                _setup(m, "WoodFloor051", 1.6, gray=True, tint=(0.36, 0.36, 0.355, 1), nstr=0.5)   # 17.11: пол ТЁМНО-серый (было светлее нужного)
            elif n.startswith("обои"):
                if _OB: _wall_bk(m, _OB, float(OPT.get("oboi_rep", "0.53")))   # 17.11 заказчик: обои №11 из каталога (Mandala)
                else: continue
            elif any(k in n for k in ("стены", "бамбуков", "штукатурка", "панели")):
                _setup(m, "PaintedPlaster017", 3.0, color=False, nstr=0.10)
            elif any(k in n for k in ("фасад", "шкаф", "мебель серая", "рамки", "графит матовый", "двери")):
                _setup(m, "Concrete034", 1.5, color=False, nstr=0.12)
            elif any(k in n for k in ("ткань", "букле", "покрывало", "изголовье", "плед", "шторы", "ковёр", "подушк", "бельё", "полотенце")):
                _setup(m, "Fabric061", 0.25, color=False, nstr=0.8)
            else:
                continue
            _done += 1
        except Exception as e:
            print("PBR skip", m.name, e)
    print("PBR материалов:", _done)
