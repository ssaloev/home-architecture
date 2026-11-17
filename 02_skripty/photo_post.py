# -*- coding: utf-8 -*-
"""17.11.2026 (заказчик: «как будто сделал ИИ, дёшево — у студий как фото»): фотографическая подача в режиме real.
1) СОЛНЦЕ через окно (тёплое, мягкие тени) — только в комнатах с окном; 2) тон AgX с контрастом «как фото»;
3) постобработка компоновщиком: мягкое свечение светлых мест (glare), лёгкая виньетка, плёночное зерно.
Отключить: photo=0 (всё), sun=0 (солнце), post=0 (компоновщик)."""
import math, bpy
from mathutils import Euler

if OPT.get("photo", "1") == "1":
    _sc = bpy.context.scene
    # ---- 1. солнце из окна
    if OPT.get("sun", "1") == "1":
        _dir = None
        if "WX0" in globals() and "WZ0" not in globals(): _dir = "T"       # окно в верхней стене (z = Z0): свет идёт в +z плана
        elif "WZ0" in globals(): _dir = "R"                                  # окно в правой стене (x = X1): свет идёт в -x
        if _dir:
            sd = bpy.data.lights.new("Солнце", "SUN"); sd.energy = float(OPT.get("sunE", "2.2")); sd.angle = math.radians(1.2)
            sd.color = (1.0, 0.93, 0.82)
            so = bpy.data.objects.new("Солнце", sd); _sc.collection.objects.link(so)
            el = math.radians(float(OPT.get("sunEl", "32")))                # высота солнца
            az = math.radians(float(OPT.get("sunAz", "25")))                # отклонение от нормали окна
            # камера/свет в Blender: направление луча = -Z объекта. План: x → X, z → -Y.
            if _dir == "T": so.rotation_euler = Euler((math.pi / 2 - el, 0, math.pi + az), "XYZ")
            else: so.rotation_euler = Euler((math.pi / 2 - el, 0, math.pi / 2 + az), "XYZ")
            print("PHOTO солнце", _dir)
    # ---- 2. тон
    try:
        _sc.view_settings.view_transform = "AgX"
        for lk in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Base Contrast"):
            try: _sc.view_settings.look = lk; break
            except Exception: continue
    except Exception as e: print("PHOTO look", e)
    # ---- 3. компоновщик: glare + виньетка + зерно
    if OPT.get("post", "1") == "1":
        try:
            if hasattr(_sc, "compositing_node_group"):                     # Blender 4.4+/5.x
                nt = bpy.data.node_groups.new("Фото-пост", "CompositorNodeTree"); _sc.compositing_node_group = nt
                gi = nt.nodes.new("NodeGroupInput"); go = nt.nodes.new("NodeGroupOutput")
                nt.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
                rl = nt.nodes.new("CompositorNodeRLayers"); src = rl.outputs["Image"]
                def out(sock): nt.links.new(sock, go.inputs[0])
            else:
                _sc.use_nodes = True; nt = _sc.node_tree
                for n in list(nt.nodes): nt.nodes.remove(n)
                rl = nt.nodes.new("CompositorNodeRLayers"); src = rl.outputs["Image"]
                co = nt.nodes.new("CompositorNodeComposite")
                def out(sock): nt.links.new(sock, co.inputs[0])
            gl = nt.nodes.new("CompositorNodeGlare")
            for k_, v_ in (("glare_type", "FOG_GLOW"), ("quality", "HIGH"), ("threshold", 0.95), ("mix", -0.8), ("size", 7)):
                try: setattr(gl, k_, v_)
                except Exception: pass
            for k_, v_ in (("Threshold", 0.95), ("Strength", 0.12), ("Size", 0.5)):
                if k_ in gl.inputs:
                    try: gl.inputs[k_].default_value = v_
                    except Exception: pass
            nt.links.new(src, gl.inputs[0]); cur = gl.outputs[0]
            em = nt.nodes.new("CompositorNodeEllipseMask")
            for k_, v_ in (("width", 1.25), ("height", 1.25)):
                try: setattr(em, k_, v_)
                except Exception: pass
            for k_, v_ in (("Size", (1.25, 1.25)),):
                if k_ in em.inputs:
                    try: em.inputs[k_].default_value = v_
                    except Exception: pass
            bl = nt.nodes.new("CompositorNodeBlur")
            for k_, v_ in (("size_x", 400), ("size_y", 400), ("use_relative", False)):
                try: setattr(bl, k_, v_)
                except Exception: pass
            if "Size" in bl.inputs:
                try: bl.inputs["Size"].default_value = (400, 400)
                except Exception: pass
            nt.links.new(em.outputs[0], bl.inputs[0])
            mx = nt.nodes.new("CompositorNodeMixRGB") if hasattr(bpy.types, "CompositorNodeMixRGB") else nt.nodes.new("ShaderNodeMix")
            try: mx.blend_type = "MULTIPLY"
            except Exception: pass
            if mx.bl_idname == "ShaderNodeMix":
                mx.data_type = "RGBA"; mx.inputs[0].default_value = 0.22; nt.links.new(cur, mx.inputs[6]); nt.links.new(bl.outputs[0], mx.inputs[7]); cur = mx.outputs[2]
            else:
                mx.inputs[0].default_value = 0.22; nt.links.new(cur, mx.inputs[1]); nt.links.new(bl.outputs[0], mx.inputs[2]); cur = mx.outputs[0]
            out(cur)
            print("PHOTO компоновщик ok")
        except Exception as e:
            print("PHOTO компоновщик пропущен:", e)
