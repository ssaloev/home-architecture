
# ================= СПАЛЬНЯ 2 — вариант 3 (12.11.2026)
T = 0.2
BC = 12.43                                   # ось кровати: центр глухой части верхней стены (вариант А, 12.11)
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["floor"])
LZ0, LZ1, LX0, LX1 = 2.327, 3.545, 13.745, 14.745     # лоджия Б и тамбур (план)
box("Стена верх", X0 - T, Z0 - T, LX0, Z0, 0, H, M["wall"])
box("Тамбур стена лев", LX0 - 0.15, LZ0 - 0.2, LX0, Z0, 0, H, M["wall"]); box("Тамбур стена прав", LX1, LZ0 - 0.2, LX1 + T, Z0, 0, H, M["wall"])
box("Тамбур потолок", LX0 - 0.15, LZ0 - 0.2, LX1 + T, Z0 + SL + 0.01, HC, H + 0.05, M["ceil"])
M["log"] = mat("Лоджия штукатурка", "#D9D6D0", 0.9)
box("Лоджия пол", LX0, LZ0, LX1, Z0, -0.05, 0, M["floor"]); box("Лоджия стена верх", LX0 - 0.15, LZ0 - 0.2, LX1 + T, LZ0, 0, H, M["log"])
for (a0, a1) in ((LX0, 13.89), (14.618, LX1)): box("Простенок двери", a0, LZ1, a1, LZ1 + 0.09, 0, H, M["wall"])
box("Над дверью лоджии", 13.89, LZ1, 14.618, LZ1 + 0.09, 2.10, H, M["wall"])
for (a0, a1) in ((13.89, 13.95), (14.558, 14.618)): box("Рама двери", a0, LZ1 + 0.02, a1, LZ1 + 0.07, 0, 2.10, M["wframe"], 0.003)
box("Рама двери", 13.89, LZ1 + 0.02, 14.618, LZ1 + 0.07, 2.04, 2.10, M["wframe"], 0.003); box("Импост", 13.89, LZ1 + 0.02, 14.618, LZ1 + 0.07, 0.85, 0.91, M["wframe"], 0.003)
box("Стекло двери лоджии", 13.95, LZ1 + 0.04, 14.558, LZ1 + 0.05, 0.0, 2.04, M["glass"])
M["acw2"] = mat("Наружный блок", "#EDEDEA", 0.4)
box("Наружный блок Н3", 13.85, LZ0 + 0.05, 14.65, LZ0 + 0.35, 0.02, 0.57, M["acw2"], 0.01)
box("Стена низ", X0 - T, Z1, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена лев", X0 - T, Z0, X0, DZ0, 0, H, M["wall"]); box("Стена лев2", X0 - T, DZ1, X0, Z1, 0, H, M["wall"]); box("Над дверью", X0 - T, DZ0, X0, DZ1, DH, H, M["wall"])
box("Стена прав", X1, Z0, X1 + T, WZ0, 0, H, M["wall"]); box("Стена прав2", X1, WZ1, X1 + T, Z1, 0, H, M["wall"])
box("Под окном", X1, WZ0, X1 + T, WZ1, 0, WS, M["wall"]); box("Над окном", X1, WZ0, X1 + T, WZ1, WT, H, M["wall"])
box("Перекрытие", X0 - T, Z0 - T, X1 + T, Z1 + T, H, H + 0.05, M["ceil"])
NI = 0.16
box("Потолок", X0 + SL, Z0 + SL, X1 - NI - SL, Z1 - SL, HC, H, M["ceil"]); box("Потолок у прохода", LX0 - 0.15, Z0 - 0.01, X1 - NI - SL, Z0 + SL, HC, H, M["ceil"])
for (a0, b0, a1, b1) in ((X0 + 0.01, Z0, X0 + 0.03, Z1), (X1 - NI - 0.03, Z0, X1 - NI - 0.01, Z1), (X0, Z0 + 0.01, X1 - NI, Z0 + 0.03), (X0, Z1 - 0.03, X1 - NI, Z1 - 0.01)):
    box("LED паз", a0, b0, a1, b1, HC + 0.03, HC + 0.035, M["led"])
for xx in (11.25, 14.15):                     # 2 линейных светильника вдоль комнаты
    box("Линия света", xx - 0.02, Z0 + 0.35, xx + 0.02, Z1 - 0.35, HC - 0.004, HC, M["spot"])
# окно (правая стена)
box("Подоконник", X1 - 0.04, WZ0 - 0.03, X1 + 0.12, WZ1 + 0.03, WS - 0.03, WS, M["wframe"], 0.005)
for a in np.linspace(WZ0, WZ1, 3): box("Импост", X1 + 0.06, a - 0.03, X1 + 0.12, a + 0.03, WS, WT, M["wframe"], 0.004)
for (h0, h1) in ((WS, WS + 0.06), (WT - 0.06, WT)): box("Рама", X1 + 0.06, WZ0, X1 + 0.12, WZ1, h0, h1, M["wframe"], 0.004)
box("Стекло", X1 + 0.085, WZ0, X1 + 0.095, WZ1, WS, WT, M["glass"])
def seam_x(fixed, n_, xs):
    for p in xs: box("Шов", p - 0.008, fixed, p + 0.008, fixed + n_ * 0.0008, 0.08, HC, M["seam"])
def seam_z(fixed, n_, zs):
    for p in zs: box("Шов", fixed, p - 0.008, fixed + n_ * 0.0008, p + 0.008, 0.08, HC, M["seam"])
seam_x(Z1, -1, [x for x in (BC - 0.8 - 1.22, BC - 0.8, BC + 0.8, BC + 0.8 + 1.22) if X0 + 0.15 < x < X1 - 0.15])   # стена ТВ: швы по краям тумбы, за ТВ цельный лист
seam_x(Z0, +1, [x for x in (BC - 1.83, BC - 0.61, BC + 0.61, BC + 1.83) if X0 + 0.65 < x < LX0 - 0.1])   # стена за кроватью: листы 1220 симметрично кровати
seam_z(X1, -1, [])
# 13.11 (по заказчику): стены прохода в лоджию — тоже бамбуковые панели: швы листов + шов в углах
_pm = (LZ1 + 0.09 + Z0) / 2
seam_z(LX0, +1, [_pm, Z0 - 0.008]); seam_z(LX1, -1, [_pm, Z0 - 0.008])
seam_x(LZ1 + 0.09, +1, [LX0 + 0.075, LX1 - 0.07])
for (a, b, c, d) in ((X0 + 0.6, Z0, LX0, Z0 + 0.015), (X0, Z1 - 0.015, X1, Z1), (X1 - 0.015, LZ1 + 0.09, X1, Z1), (X0, 6.509, X0 + 0.015, 6.60), (X0, 7.40, X0 + 0.015, Z1), (LX0, LZ1 + 0.09, LX0 + 0.015, Z0)):   # плинтус до углов (12.11)
    box("Плинтус", a, b, c, d, 0, 0.08, M["wall"], 0.002)

# ---------------- стена за кроватью: мягкие вертикальные панели + рамка орех + подсветка
M["soft"] = mat("Мягкие панели серо-бежевые", "#" + OPT.get("soft", "8C8580"), 0.95)
M["walnut"] = tex(mat("Орех", "#5A3E2B", 0.45), "washed_grey_oak_veneer", 2.0, "#6B4A33", 1.4)
HW0, HW1, HH = BC - 1.45, BC + 1.45, 1.30
# (убрано 12.11: мягкие панели на стене) box("Рамка орех", HW0 - 0.04, Z0, HW1 + 0.04, Z0 + 0.03, 0.0, HH + 0.04, M["walnut"], 0.004)
# (убрано 12.11: мягкие панели на стене) npn = 10; pw = (HW1 - HW0) / npn
# (убрано 12.11: мягкие панели на стене) for i in range(npn):
# (убрано 12.11: мягкие панели на стене) a = HW0 + i * pw
# (убрано 12.11: мягкие панели на стене) box("Мягкая панель", a + 0.004, Z0 + 0.03, a + pw - 0.004, Z0 + 0.075, 0.12, HH, M["soft"], 0.02)
# (убрано 12.11: мягкие панели на стене) box("LED над изголовьем", HW0, Z0 + 0.02, HW1, Z0 + 0.03, HH + 0.045, HH + 0.05, M["led"])

# ---------------- кровать 1600 + тумбочки + подвесы
# кровать под заказ (12.11): подиум графит «парящий» с подсветкой, мягкое изголовье со стёжкой, подвесные тумбочки
CUSTOM = OPT.get("bed", "custom") == "custom"
M["hbf"] = mat("Изголовье ткань графит-серая", "#" + OPT.get("hb", "5E5E62"), 0.95)
M["linen"] = mat("Бельё белое", "#F2F0EC", 0.9); M["duvet"] = mat("Покрывало серое", "#" + OPT.get("duv", "B4B5B3"), 0.95); M["plaid"] = mat("Плед графит", "#3C3C3F", 0.95)
zh = Z0 + 0.005
if CUSTOM:
    box("Подиум", BC - 0.76, zh + 0.02, BC + 0.76, zh + 2.12, 0.10, 0.34, M["ward"], 0.012)
    box("Цоколь", BC - 0.64, zh + 0.12, BC + 0.64, zh + 2.0, 0.0, 0.10, M["black"])
    for (a0, b0, a1, b1) in ((BC - 0.66, zh + 2.0, BC + 0.66, zh + 2.01), (BC - 0.66, zh + 0.12, BC - 0.65, zh + 2.0), (BC + 0.65, zh + 0.12, BC + 0.66, zh + 2.0)):
        box("LED подиума", a0, b0, a1, b1, 0.085, 0.095, M["led"])
    box("Матрас", BC - 0.70, zh + 0.14, BC + 0.70, zh + 2.08, 0.34, 0.56, M["linen"], 0.05)
    box("Покрывало", BC - 0.76, zh + 0.72, BC + 0.76, zh + 2.12, 0.40, 0.60, M["duvet"], 0.05)
    # 13.11 (по заказчику): плед — мягкая ткань: перегиб через край кровати, свес по бокам, складки (сетка + solidify + subsurf)
    def drape(name, cx, z0_, z1_, top, half, drop, m, r=0.045, nu=90, nv=24, amp=0.012):
        Lh = half + math.pi * r / 2 + drop
        bm = bmesh.new(); rows = []
        for j in range(nv + 1):
            zz = z0_ + (z1_ - z0_) * j / nv; row = []
            for i in range(nu + 1):
                u = -Lh + 2 * Lh * i / nu; s = 1 if u >= 0 else -1; a = abs(u)
                if a <= half: x, h = a, top
                elif a <= half + math.pi * r / 2:
                    t = (a - half) / r; x, h = half + r * math.sin(t), top - r + r * math.cos(t)
                else: x, h = half + r + 0.01 * (a - half - math.pi * r / 2) / drop, top - r - (a - half - math.pi * r / 2)
                w_ = amp * (math.sin(zz * 41 + u * 7) * 0.6 + math.sin(zz * 17 - u * 13) * 0.4)
                if a > half: x += w_ * 0.8
                else: h += w_ * 0.35
                row.append(bm.verts.new(W(cx + s * x, zz, h)))
            rows.append(row)
        for j in range(nv):
            for i in range(nu): bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
        sd = o.modifiers.new("t", "SOLIDIFY"); sd.thickness = 0.006
        ss = o.modifiers.new("s", "SUBSURF"); ss.levels = 1; ss.render_levels = 2
        for p in o.data.polygons: p.use_smooth = True
        return o
    drape("Плед", BC, zh + 1.60, zh + 2.02, 0.606, 0.762, 0.24, M["plaid"])
    def _pillow(fn, cx, cz, h0, w, tilt, mm, rot=0.0):
        objs = import_bk(fn, cx, cz, h0, rot, w)
        p = W(cx, cz, h0)
        R_ = Matrix.Translation(p) @ Matrix.Rotation(math.radians(tilt), 4, "X") @ Matrix.Translation(-p)
        for o_ in objs:
            if o_.parent is None or o_.parent not in objs: o_.matrix_world = R_ @ o_.matrix_world
            if o_.type == "MESH":
                for i_ in range(len(o_.data.materials)): o_.data.materials[i_] = mm
                if not o_.data.materials: o_.data.materials.append(mm)
    for xx in (BC - 0.36, BC + 0.36):            # спальные 50×70, наклонены к изголовью
        _pillow("podushka_spalnaya", xx, zh + 0.36, 0.50, 0.70, -28, M["linen"])
    for xx in (BC - 0.24, BC + 0.24):            # декоративные 45×45, серые
        _pillow("podushka_dekor", xx, zh + 0.58, 0.55, 0.48, -18, M["plaid"])
    nch = 8; cw = 1.60 / nch
    for i in range(nch):
        a = BC - 0.80 + i * cw
        # 13.11 (по заказчику): мягкие «пухлые» каналы — овальное сечение, скруглённый верх, глубокие швы между ними
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=cw / 2 - 0.003, depth=0.95, location=W(a + cw / 2, zh + 0.075, 0.775))
        ch = bpy.context.active_object; ch.name = "Изголовье канал"; ch.scale = (1, 0.055 / (cw / 2 - 0.003), 1); ch.data.materials.append(M["hbf"])
        bv = ch.modifiers.new("b", "BEVEL"); bv.width = 0.045; bv.segments = 8; bv.limit_method = "ANGLE"
        ch.modifiers.new("s", "SUBSURF").levels = 1
        for pp in ch.data.polygons: pp.use_smooth = True
    box("Изголовье основа", BC - 0.80, zh, BC + 0.80, zh + 0.07, 0.30, 1.24, M["hbf"], 0.01)
    box("LED за изголовьем", BC - 0.78, zh, BC + 0.78, zh + 0.01, 1.255, 1.26, M["led"])
    for xx in (BC - 1.025, BC + 1.025):          # подвесные тумбочки графит 350
        box("Тумбочка подвесная", xx - 0.175, Z0 + 0.005, xx + 0.175, Z0 + 0.40, 0.40, 0.62, M["ward"], 0.006)
        box("Шов ящика", xx - 0.175, Z0 + 0.399, xx + 0.175, Z0 + 0.402, 0.508, 0.512, M["black"])
        box("Ручка", xx - 0.07, Z0 + 0.40, xx + 0.07, Z0 + 0.415, 0.555, 0.565, M["black"], 0.003)
        box("LED под тумбочкой", xx - 0.15, Z0 + 0.03, xx + 0.15, Z0 + 0.37, 0.394, 0.398, M["led"])
else:
  _bed = import_bk("krovat_myagkaya", BC, Z0 + 0.08 + 1.05, 0.0, 0, 1.80)
  for (xx, rot) in ((BC - 1.20, 180), (BC + 1.20, 180)):
    for _o in import_bk("tumbochka_noir", xx, Z0 + 0.26, 0.0, 0, 0.55):
        if _o.type != "MESH": continue
        for _sl in _o.material_slots:
            _m = _sl.material; _b = next((n for n in _m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if (_m and _m.use_nodes) else None
            if _b is not None and not _b.inputs["Metallic"].is_linked and _b.inputs["Metallic"].default_value > 0.5: _sl.material = M["black"]; continue
            _sl.material = M["ward"]
for (xx, rot) in ((BC - 1.025, 0), (BC + 1.025, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.003, depth=H - 1.32, location=W(xx, Z0 + 0.27, (H + 1.32) / 2)); bpy.context.active_object.data.materials.append(M["black"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.06, depth=0.24, location=W(xx, Z0 + 0.27, 1.20)); o_ = bpy.context.active_object; o_.data.materials.append(M["brass"]); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.05, depth=0.004, location=W(xx, Z0 + 0.27, 1.079)); bpy.context.active_object.data.materials.append(M["spot"])
    lt = bpy.data.lights.new("Подвес", "POINT"); lt.energy = 6; lt.color = (1, 0.85, 0.65); lt.shadow_soft_size = 0.05
    o = bpy.data.objects.new("Подвес", lt); o.location = W(xx, Z0 + 0.27, 1.05); sc.collection.objects.link(o)

# ---------------- встроенный шкаф графит (левая стена, до потолка)
b0, b1, wx = Z0, 6.509, X0 + 0.60
box("Шкаф", X0, b0, wx, b1, 0, HC, M["ward"])
n = 4; w = (b1 - b0) / n
for k in range(n):
    u0, u1 = b0 + k * w + 0.07, b0 + (k + 1) * w - 0.07
    if k: box("Шов", wx, b0 + k * w - 0.0015, wx + 0.002, b0 + k * w + 0.0015, 0.02, HC - 0.02, M["black"])
    hz = b0 + (k + 1) * w - 0.05 if k % 2 == 0 else b0 + k * w + 0.05
    box("Ручка чёрная", wx + 0.012, hz - 0.008, wx + 0.035, hz + 0.008, 0.70, 1.55, M["black"], 0.004)

# ---------------- дверь (левая стена)
xf = X0 - 0.05
box("Полотно", xf - 0.02, DZ0 + 0.03, xf + 0.02, DZ1 - 0.03, 0, DH - 0.03, M["door"], 0.003)
for (a, b) in ((DZ0, DZ0 + 0.03), (DZ1 - 0.03, DZ1)): box("Рамка", xf - 0.03, a, xf + 0.03, b, 0, DH, M["black"], 0.002)
box("Рамка", xf - 0.03, DZ0, xf + 0.03, DZ1, DH - 0.03, DH, M["black"], 0.002)
box("Ручка", xf + 0.02, DZ1 - 0.10, xf + 0.07, DZ1 - 0.09, 1.0, 1.02, M["black"]); box("Ручка", xf + 0.055, DZ1 - 0.22, xf + 0.07, DZ1 - 0.09, 1.0, 1.02, M["black"])   # петли у шкафа, ручка у угла — дверь открывается к ТВ-стене

# ---------------- ТВ напротив кровати: подвесная тумба графит + ТВ 55"
t0, t1 = BC - 0.8, BC + 0.8
box("ТВ-тумба", t0, Z1 - 0.40, t1, Z1, 0.30, 0.62, M["ward"]); box("Столешница", t0 - 0.01, Z1 - 0.41, t1 + 0.01, Z1, 0.62, 0.645, M["top"], 0.003)
for k in range(2):
    u0, u1 = t0 + k * 0.8 + 0.003, t0 + (k + 1) * 0.8 - 0.003
    box("Фасад", u0, Z1 - 0.42, u1, Z1 - 0.40, 0.305, 0.615, M["ward"], 0.002)
    box("Ручка", (u0 + u1) / 2 - 0.1, Z1 - 0.435, (u0 + u1) / 2 + 0.1, Z1 - 0.42, 0.55, 0.562, M["black"], 0.003)
box("ТВ 55", BC - 0.62, Z1 - 0.045, BC + 0.62, Z1 - 0.01, 1.0, 1.70, M["tv"], 0.004)

# ---------------- туалетный столик с зеркалом (угол у окна) + пуф + растение
box("Столик", 13.75, Z1 - 0.40, 14.55, Z1, 0.72, 0.75, M["ward"], 0.004)
box("Ящик столика", 13.77, Z1 - 0.40, 14.53, Z1, 0.58, 0.72, M["ward"], 0.003)
box("Зеркало подсв.", 13.80, Z1 - 0.025, 14.50, Z1 - 0.02, 1.0, 1.85, M["led"])
box("Зеркало", 13.82, Z1 - 0.03, 14.48, Z1 - 0.025, 1.02, 1.83, mat("Зеркало", "#E3E7E8", 0.02, 1.0))
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.2, depth=0.44, location=W(14.15, Z1 - 0.65, 0.22)); bpy.context.active_object.data.materials.append(M["soft"])
# растение убрано 12.11 по просьбе заказчика
# большое зеркало в пол с LED-подсветкой (правая стена под кондиционером), 800×1850
def rmirror(name, z0, z1, h0, h1, x, r, m, dep):
    bpy.ops.mesh.primitive_plane_add(size=1); o = bpy.context.active_object; o.name = name
    o.scale = (z1 - z0, h1 - h0, 1); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new("b", "BEVEL"); md.affect = "VERTICES"; md.width = r; md.segments = 12
    o.modifiers.new("s", "SOLIDIFY").thickness = dep
    o.rotation_euler = (math.radians(90), 0, math.radians(90)); o.location = W(x, (z0 + z1) / 2, (h0 + h1) / 2)
    o.data.materials.append(m); return o
MZ0, MZ1 = 4.55, 5.35
rmirror("Подсветка зеркала", MZ0 - 0.015, MZ1 + 0.015, 0.115, 2.015, X1 - 0.02, 0.003, M["led"], 0.004)
rmirror("Зеркало в пол", MZ0, MZ1, 0.13, 2.0, X1 - 0.03, 0.002, mat("Зеркало", "#E3E7E8", 0.02, 1.0), 0.01)
area(W(X1 - 0.05, (MZ0 + MZ1) / 2, 1.07), 0.02, 12, rot=(0, math.radians(-90), 0), sy=1.8) if False else None

# ---------------- кондиционер К3 (план: правая стена, z 4.60–5.40, верх h=2500) + розетка h=2200
ACZ0, ACZ1 = 4.60, 5.40
M["acw"] = mat("Кондиционер белый", "#F3F3F1", 0.35)
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
ac_unit(("R", X1), (ACZ0 + ACZ1) / 2, 2.54, flip="acflip" in ARGS)
# ---------------- шторы на правой стене
def drape_z(name, a0, a1, xc, amp, waves, m):
    bm = bmesh.new(); nu = int((a1 - a0) / 0.02); rows = []
    for h in (0.0, H - 0.02):
        rows.append([bm.verts.new(W(xc + amp * math.sin(2 * math.pi * waves * i / nu), a0 + (a1 - a0) * i / nu, h)) for i in range(nu + 1)])
    for i in range(nu): bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(m)
    o.modifiers.new("s", "SOLIDIFY").thickness = 0.006
    for p in o.data.polygons: p.use_smooth = True
drape_z("Тюль", ACZ1 + 0.05, Z1 - 0.03, X1 - 0.05, 0.025, (Z1 - WZ0) / 0.12, M["tulle"])
drape_z("Штора 1", ACZ1 + 0.05, WZ0 + 0.20, X1 - 0.11, 0.04, 6, M["curt"])
drape_z("Штора 2", WZ1 - 0.20, Z1 - 0.02, X1 - 0.11, 0.04, 4, M["curt"])

# ---------------- свет
def area(loc, size, energy, rot=(0, 0, 0), color=(1, 0.95, 0.88), sy=None, spread=None):
    lt = bpy.data.lights.new("A", "AREA"); lt.energy = energy; lt.color = color; lt.shape = "RECTANGLE"; lt.size = size; lt.size_y = sy or size
    if spread: lt.spread = math.radians(spread)
    o = bpy.data.objects.new("A", lt); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    try: o.visible_camera = False
    except Exception: pass
area(W(X1 + 0.5, (WZ0 + WZ1) / 2, 1.6), WZ1 - WZ0, 350, rot=(0, math.radians(-90), 0), sy=WT - WS, color=(0.95, 0.97, 1.0))
for (x0_, z0_, x1_, z1_) in ((X0 + 0.04, Z0, X0 + 0.04, Z1), (X1 - NI - 0.04, Z0, X1 - NI - 0.04, Z1), (X0, Z0 + 0.04, X1, Z0 + 0.04), (X0, Z1 - 0.04, X1, Z1 - 0.04)):
    L = max(abs(x1_ - x0_), abs(z1_ - z0_)); hz = abs(x1_ - x0_) > abs(z1_ - z0_)
    area(W((x0_ + x1_) / 2, (z0_ + z1_) / 2, HC + 0.02), L if hz else 0.03, 30 * L, sy=0.03 if hz else L, spread=80)
for xx in (11.25, 14.15):
    area(W(xx, (Z0 + Z1) / 2, HC - 0.01), 0.04, 60, sy=Z1 - Z0 - 0.7)
# (убрано 12.11: мягкие панели на стене) area(W(BC, Z0 + 0.06, HH + 0.06), HW1 - HW0, 15, sy=0.02, color=(1, 0.86, 0.66))
for xx in (11.515, 13.30):                    # 4 круглых спота (план света: 2×2)
    for zz in (5.393, 6.425):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.045, depth=0.004, location=W(xx, zz, HC - 0.002)); bpy.context.active_object.data.materials.append(M["spot"])
        bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.006, location=W(xx, zz, HC - 0.003)); bpy.context.active_object.data.materials.append(M["black"])
        lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = 10; lt.spot_size = math.radians(70); lt.spot_blend = 0.6; lt.color = (1, 0.92, 0.82)
        o = bpy.data.objects.new("Спот", lt); o.location = W(xx, zz, HC - 0.02); sc.collection.objects.link(o)
area(W((LX0 + LX1) / 2, (LZ1 + Z0) / 2, HC - 0.05), 0.6, 25, sy=0.5)          # свет в тамбуре
area(W((LX0 + LX1) / 2, (LZ0 + LZ1) / 2, H - 0.1), 0.6, 30, sy=0.6)           # свет в лоджии
box("Торец стены у прохода", LX0 - 0.15, Z0 - 0.2, LX0 + 0.01, Z0 + 0.01, 0, HC, M["wall"])
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.3

# ---------------- камеры
CAMS = {"1": ("1_ot_dveri_k_krovati", W(10.95, 7.25, 1.50), W(13.4, 4.4, 1.0), 15),
        "2": ("2_ot_okna_k_shkafu", W(14.35, 4.75, 1.50), W(10.5, 7.1, 1.05), 15),
        "3": ("3_krovat_pryamo", W(BC, 7.35, 1.45), W(BC, Z0, 1.0), 16),
        "4": ("4_prohod_v_lodzhiyu", W(12.9, 7.2, 1.5), W(14.25, 3.0, 1.1), 18)}
