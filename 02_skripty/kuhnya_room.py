# ======================= КУХНЯ (13.11.2026) — по листу 11 «План кухни»: линейная кухня у правой стены
# (плита+духовка у окна → ПММ 450 → мойка → холодильник-колонна), колонна СВЧ+кладовая у нижней стены,
# угловая банкетка (левая + верхняя стена) + стол 1300×850 + 2 стула; К4 над банкеткой.
# Стиль квартиры: серые бамбуковые панели, мебель графит #2F2F31 без ручек (гола-профиль), столешница и фартук —
# серый керамогранит (как в ванной), пол — тот же керамогранит 1200×600.
X0, X1, Z0, Z1 = 9.145, 13.0, 1.909, 4.2
H, HC = 2.70, 2.65
WX0, WX1, WS, WT = 11.036, 12.636, 0.90, 2.40       # окно в верхней стене
DX0, DX1, DH = 9.145, 9.945, 2.10                   # проём из коридора (нижняя стена), без двери
OUTDIR = "kuhnya"
#==COMMON==
WALLC = "#BDBBB5"
M["wall"] = tex(mat("Бамбуковые панели серые", WALLC, 0.38), "washed_grey_oak_veneer", 1.6, WALLC, 1.55, 0.7)
M["seam"] = mat("Шов панелей", "#2E2C2A", 0.6)
M["knit"] = mat("Ткань банкетки", "#8A8B8F", 0.95)
M["bglass"] = mat("Чёрное стекло", "#0B0B0C", 0.06)
M["wframe"] = mat("Рама окна", "#F2F1EE", 0.4)
M["blind"] = mat("Рулонная штора", "#D9D7D2", 0.9, transm=0.25)
M["shade"] = emis("Плафон", "#FFE2B8", 8)

# ---------------- коробка: пол, стены (бамбук, листы 1220 со швами), окно, проём
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["tilef"])
box("Стена L", X0 - T, Z0 - T, X0, Z1 + T, 0, H, M["wall"])
box("Стена R", X1, Z0 - T, X1 + T, Z1 + T, 0, H, M["wall"])
box("Стена T1", X0 - T, Z0 - T, WX0, Z0, 0, H, M["wall"]); box("Стена T2", WX1, Z0 - T, X1 + T, Z0, 0, H, M["wall"])
box("Под окном", WX0, Z0 - T, WX1, Z0, 0, WS, M["wall"]); box("Над окном", WX0, Z0 - T, WX1, Z0, WT, H, M["wall"])
box("Стена B1", DX1, Z1, X1 + T, Z1 + T, 0, H, M["wall"]); box("Над проёмом", DX0 - T, Z1, DX1, Z1 + T, DH, H, M["wall"])
box("Потолок", X0 - T, Z0 - T, X1 + T, Z1 + T, HC, HC + 0.05, M["ceil"])
for x in (X0 + 1.22, X0 + 2.44):
    box("Шов", x - 0.008, Z1 - 0.004, x + 0.008, Z1, 0, HC, M["seam"])
for z in (Z0 + 1.22,):
    box("Шов", X0, z - 0.008, X0 + 0.004, z + 0.008, 0, HC, M["seam"])
# окно: рама, стекло, подоконник (= столешница), рулонная штора
box("Подоконник", WX0, Z0 - 0.10, WX1, Z0 + 0.02, WS - 0.03, WS, M["tile"])
for (a, b) in ((WX0, WX0 + 0.06), (WX1 - 0.06, WX1), ((WX0 + WX1) / 2 - 0.03, (WX0 + WX1) / 2 + 0.03)):
    box("Рама", a, Z0 - 0.10, b, Z0 - 0.04, WS, WT, M["wframe"])
for (h0, h1) in ((WS, WS + 0.06), (WT - 0.06, WT)): box("Рама", WX0, Z0 - 0.10, WX1, Z0 - 0.04, h0, h1, M["wframe"])
box("Стекло", WX0, Z0 - 0.075, WX1, Z0 - 0.065, WS, WT, M["glass"])
M["sky"] = emis("Вид за окном", "#DCE4EC", 1.6)
box("Небо", WX0 - 1.0, Z0 - 1.6, WX1 + 1.0, Z0 - 1.55, 0.0, 3.6, M["sky"])
box("Штора рулонная", WX0 + 0.02, Z0 - 0.035, WX1 - 0.02, Z0 - 0.03, WT - 0.55, WT - 0.02, M["blind"])
box("Короб шторы", WX0, Z0 - 0.06, WX1, Z0, WT - 0.02, WT + 0.06, M["ward"])
lt = bpy.data.lights.new("Окно", "AREA"); lt.size = 1.6; lt.size_y = 1.5; lt.energy = 260; lt.color = (1, 0.97, 0.92)
o = bpy.data.objects.new("Окно", lt); o.location = W((WX0 + WX1) / 2, Z0 - 0.4, (WS + WT) / 2); o.rotation_euler = (math.radians(90), 0, 0); sc.collection.objects.link(o)

# ---------------- правая стена: нижние модули (плита+духовка, ПММ 450, мойка), столешница, фартук, верхние шкафы
RX = X1 - 0.60; RZ1 = 3.60; CT = 0.90
box("Цоколь", RX + 0.05, Z0, X1, RZ1, 0, 0.10, M["black"])
box("Корпус низ", RX + 0.02, Z0, X1, RZ1, 0.10, CT - 0.04, M["ward"])
box("Гола-профиль", RX, Z0, RX + 0.025, RZ1, CT - 0.10, CT - 0.07, M["black"])
MODS = [(Z0, 2.509, "плита"), (2.509, 2.959, "ПММ"), (2.959, RZ1, "мойка")]
for (a, b, t) in MODS:
    if t == "плита":
        box("Духовка", RX - 0.002, a + 0.03, RX + 0.02, b - 0.03, 0.14, 0.72, M["bglass"], 0.004)
        box("Ящик под духовкой", RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, 0.13, M["ward"], 0.002)
        box("Ящик над духовкой", RX, a + 0.002, RX + 0.02, b - 0.002, 0.73, CT - 0.11, M["ward"], 0.002)
    else:
        box("Фасад " + t, RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, CT - 0.11, M["ward"], 0.002)
box("Столешница", RX - 0.02, Z0, X1, RZ1, CT - 0.04, CT, M["tile"])
box("Варочная индукция", RX + 0.05, Z0 + 0.04, X1 - 0.03, 2.50 - 0.05, CT, CT + 0.006, M["bglass"], 0.003)
for (cx, cz, r) in ((RX + 0.17, Z0 + 0.17, 0.09), (RX + 0.42, Z0 + 0.17, 0.08), (RX + 0.17, 2.30, 0.08), (RX + 0.42, 2.30, 0.10)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.002, location=W(cx, cz, CT + 0.007)); bpy.context.active_object.data.materials.append(M["seam"])
box("Мойка (врезная, графит)", RX + 0.08, 3.03, X1 - 0.10, 3.53, CT - 0.002, CT + 0.001, M["black"])
box("Смеситель стойка", X1 - 0.075, 3.26, X1 - 0.045, 3.30, CT, CT + 0.32, M["black"], 0.008)
box("Смеситель излив", X1 - 0.30, 3.265, X1 - 0.045, 3.295, CT + 0.29, CT + 0.32, M["black"], 0.008)
box("Фартук", X1 - 0.01, Z0, X1, RZ1, CT, 1.50, M["tile"])
UX = X1 - 0.35
box("Верхние шкафы корпус", UX + 0.02, Z0, X1, RZ1, 1.50, HC, M["ward"])
for (a, b) in ((Z0, 2.509), (2.509, 3.06), (3.06, RZ1)):
    box("Фасад верх", UX, a + 0.002, UX + 0.02, b - 0.002, 1.50, HC - 0.002, M["ward"], 0.002)
box("Вытяжка (встроенная)", UX + 0.03, Z0 + 0.03, X1 - 0.02, 2.48, 1.49, 1.50, M["black"])
box("LED под шкафами", UX + 0.04, 2.52, UX + 0.07, RZ1 - 0.02, 1.495, 1.50, M["led"])
lt = bpy.data.lights.new("Рабочая зона", "AREA"); lt.size = 1.0; lt.size_y = 0.06; lt.energy = 22; lt.color = (1, 0.9, 0.78)
o = bpy.data.objects.new("Рабочая зона", lt); o.location = W(X1 - 0.30, (2.52 + RZ1) / 2, 1.48); o.rotation_euler = (0, 0, math.radians(90)); sc.collection.objects.link(o)
for (z_, c) in ((2.62, "white"), (2.69, "black")):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.035, depth=0.20, location=W(X1 - 0.12, z_, CT + 0.10)); bpy.context.active_object.data.materials.append(M[c])
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.09, depth=0.20, location=W(X1 - 0.20, 2.80, CT + 0.10)); bpy.context.active_object.data.materials.append(M["black"])   # чайник

# ---------------- холодильник-колонна (низ-право) и колонна СВЧ + кладовая (нижняя стена)
box("Колонна холодильника", RX + 0.02, RZ1, X1, Z1, 0.10, HC, M["ward"])
box("Цоколь колонн", 11.85, RZ1 + 0.05, X1, Z1, 0, 0.10, M["black"])
box("Фасад холодильника", RX, RZ1 + 0.002, RX + 0.02, Z1 - 0.002, 0.10, 1.95, M["ward"], 0.002)
box("Фасад антресоли", RX, RZ1 + 0.002, RX + 0.02, Z1 - 0.002, 1.96, HC - 0.002, M["ward"], 0.002)
box("Колонна СВЧ", 11.80, RZ1 + 0.02, 12.40, Z1, 0.10, HC, M["ward"])
box("СВЧ", 11.84, RZ1, 12.36, RZ1 + 0.02, 1.35, 1.73, M["bglass"], 0.004)
for (h0, h1) in ((0.10, 1.33), (1.75, HC - 0.002)):
    box("Фасад колонны", 11.802, RZ1, 12.398, RZ1 + 0.02, h0, h1, M["ward"], 0.002)
box("Гола верт.", RX - 0.004, RZ1 - 0.01, RX + 0.02, RZ1 + 0.01, 0.10, HC, M["black"])

# ---------------- угловая банкетка (левая стена + верхняя стена до окна): база графит с ящиками, мягкое сиденье и спинка
BD = 0.50
for (x0, z0, x1, z1) in ((X0, Z0, X0 + BD, 3.509), (X0 + BD, Z0, 11.0, Z0 + 0.48)):
    box("Банкетка база", x0, z0, x1, z1, 0.06, 0.40, M["ward"], 0.004)
    box("Банкетка цоколь", x0 + 0.03, z0 + 0.03, x1 - 0.03, z1 - 0.03, 0, 0.06, M["black"])
    box("Сиденье", x0, z0, x1, z1, 0.40, 0.47, M["knit"], 0.03)
box("Спинка L", X0, Z0 + 0.10, X0 + 0.10, 3.509, 0.47, 0.92, M["knit"], 0.035)
box("Спинка T", X0 + 0.10, Z0, 11.0, Z0 + 0.10, 0.47, 0.92, M["knit"], 0.035)
for (x0, z0, x1, z1) in ((X0 + 0.10, 2.70, X0 + 0.22, 3.05), (10.20, Z0 + 0.10, 10.55, Z0 + 0.22)):
    box("Подушка", x0, z0, x1, z1, 0.47, 0.82, M["towel"], 0.05)

# ---------------- стол 1300×850 (столешница керамогранит, опора чёрная) + 2 стула + подвесы
TCX, TCZ = X0 + 1.2, Z0 + 0.975
box("Стол столешница", TCX - 0.65, TCZ - 0.425, TCX + 0.65, TCZ + 0.425, 0.72, 0.75, M["tile"], 0.006)
box("Стол опора", TCX - 0.30, TCZ - 0.05, TCX + 0.30, TCZ + 0.05, 0.03, 0.72, M["black"])
box("Стол основание", TCX - 0.35, TCZ - 0.25, TCX + 0.35, TCZ + 0.25, 0.0, 0.03, M["black"])
for (cz,) in ((TCZ - 0.24,), (TCZ + 0.24,)):
    Tm = Matrix.Translation(W(TCX + 0.65 + 0.28, cz, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")
    for o_ in bk_load("stul_minimal", Tm):
        for i_, ms in enumerate(o_.data.materials):
            o_.data.materials[i_] = M["knit"] if (ms and "cuir" in ms.name.lower()) else M["black"]
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.12, depth=0.012, location=W(TCX - 0.15, TCZ, 0.756)); bpy.context.active_object.data.materials.append(M["white"])  # блюдо
for dx in (-0.33, 0.33):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.09, depth=0.26, location=W(TCX + dx, TCZ, 1.70)); bpy.context.active_object.data.materials.append(M["black"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.082, depth=0.004, location=W(TCX + dx, TCZ, 1.568)); bpy.context.active_object.data.materials.append(M["shade"])
    box("Шнур", TCX + dx - 0.003, TCZ - 0.003, TCX + dx + 0.003, TCZ + 0.003, 1.83, HC, M["black"])
    lt = bpy.data.lights.new("Подвес", "SPOT"); lt.energy = 18; lt.spot_size = math.radians(70); lt.spot_blend = 0.5; lt.color = (1, 0.88, 0.72)
    o = bpy.data.objects.new("Подвес", lt); o.location = W(TCX + dx, TCZ, 1.56); sc.collection.objects.link(o)

#==AC==
ac_unit(("L", X0), 2.50, 2.54)        # К4 над банкеткой

# ---------------- потолок: споты + LED по периметру
spots([(11.6, 2.45), (11.6, 3.40), (12.55, 2.45), (12.55, 3.40)], 30)
for (x0, z0, x1, z1) in ((X0, Z0, X1, Z0 + 0.02), (X0, Z1 - 0.02, X1, Z1), (X0, Z0, X0 + 0.02, Z1), (X1 - 0.02, Z0, X1, Z1)):
    box("LED периметр", x0, z0, x1, z1, HC - 0.012, HC - 0.008, M["led"])

CAMS = {"1": ("1_ot_vhoda", W(9.70, 4.05, 1.60), W(12.60, 2.30, 1.00), 15),
        "2": ("2_rabochaya_zona", W(10.60, 3.55, 1.60), W(12.90, 2.70, 1.05), 16),
        "3": ("3_stolovaya", W(12.20, 3.45, 1.60), W(9.40, 2.25, 0.80), 15),
        "4": ("4_ot_okna", W(11.70, 2.05, 1.70), W(10.80, 4.15, 0.95), 15)}
