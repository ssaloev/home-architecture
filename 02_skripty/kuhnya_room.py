# ======================= КУХНЯ ПО ОБМЕРУ 3300×3400 (утв. 17.11.2026, схема 01_chertezhi/shema_obmer_kuhnya.png):
# состав вар. 7 сохранён: левая стена — холодильник side-by-side + 2 колонны (кофе+СВЧ, кладовая); правая стена (ниже вентшахты) —
# мойка → ПММ → столешница → плита; стол 1200×700 у окна + 3 стула; вход 519 в левом нижнем углу. Прежний вариант — kuhnya_room_v13_11.py
# --- ниже — описание вар. 7 (13.11) для истории:
# окно свободно; правая стена от окна: мойка 600 → ПММ 450 → плита 600 + духовка → угловой низ; у нижней стены сразу у входа
# холодильник side-by-side, колонны (кладовая, СВЧ+кофемашина), бутылочница 320; слева от окна стол 1200×600 + 2 стула;
# левая стена свободна (стол, буфет, ТВ убраны); К4 на левой стене.
# Стиль квартиры: серые бамбуковые панели, мебель графит #2F2F31 без ручек (гола-профиль), столешница и фартук —
# серый керамогранит (как в ванной), пол — тот же керамогранит 1200×600.
X0, X1, Z0, Z1 = 9.586, 12.886, 1.309, 4.709
H, HC = 2.70, 2.65
WX0, WX1, WS, WT = 11.036, 12.636, 0.90, 2.40       # окно в верхней стене
DX0, DX1, DH = 9.586, 10.105, 2.10                  # проём 519 из коридора (нижняя стена, левый угол), без двери
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
M["kfloor"] = tex(mat("Пол тёмно-серый (влагостойкий SPC)", "#5B5B59", 0.45), "laminate_floor_02", 0.6, "#5B5B59", 1.3)   # 14.11: пол как во всей квартире
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["kfloor"])
for _o in [o for o in sc.objects if o.name.startswith("Пол") and o.type == "MESH"]:   # общий короб комнаты кладёт плитку — заменить на пол квартиры
    _o.data.materials.clear(); _o.data.materials.append(M["kfloor"])
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

# 17.11 обмер: вентшахта 800×380 в правом верхнем углу + труба под ней (до z 2.409)
box("Вентшахта", 12.506, Z0, X1, 2.109, 0, H, M["wall"]); box("Короб трубы", 12.506, 2.109, X1, 2.409, 0, H, M["wall"])

# ---------------- правая стена: мойка у окна → ПММ → плита → угловой низ; столешница до угла; фартук; верхние шкафы
RX = X1 - 0.60; CT = 0.90; KZ0 = 2.409                   # 17.11: ряд начинается ниже вентшахты
S0, S1, P0, P1, H0, H1 = 2.45, 3.05, 3.05, 3.50, 4.05, 4.65
box("Цоколь", RX + 0.05, KZ0, X1, Z1, 0, 0.10, M["black"])
box("Корпус низ", RX + 0.02, KZ0, X1, Z1, 0.10, CT - 0.04, M["ward"])
box("Гола-профиль", RX, KZ0, RX + 0.025, Z1, CT - 0.10, CT - 0.07, M["black"])
for (a, b, t) in ((S0, S1, "мойка"), (P0, P1, "ПММ"), (P1, H0, "столешн.")):
    box("Фасад " + t, RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, CT - 0.11, M["ward"], 0.002)
box("Духовка", RX - 0.002, H0 + 0.03, RX + 0.02, H1 - 0.03, 0.14, 0.72, M["bglass"], 0.004)
box("Ящик под духовкой", RX, H0 + 0.002, RX + 0.02, H1 - 0.002, 0.10, 0.13, M["ward"], 0.002)
box("Ящик над духовкой", RX, H0 + 0.002, RX + 0.02, H1 - 0.002, 0.73, CT - 0.11, M["ward"], 0.002)
box("Столешница", RX - 0.02, KZ0, X1, Z1, CT - 0.04, CT, M["tile"])
bk_fit("plita_bosch600", RX + 0.31, (H0 + H1) / 2, CT, 90, 0.59)      # индукция Bosch 600, 4 зоны
box("Мойка (врезная, графит)", RX + 0.08, S0 + 0.10, X1 - 0.10, S1 - 0.08, CT - 0.002, CT + 0.001, M["black"])
SC = (S0 + 0.10 + S1 - 0.08) / 2
box("Смеситель стойка", X1 - 0.075, SC - 0.02, X1 - 0.045, SC + 0.02, CT, CT + 0.32, M["black"], 0.008)
box("Смеситель излив", X1 - 0.30, SC - 0.015, X1 - 0.045, SC + 0.015, CT + 0.29, CT + 0.32, M["black"], 0.008)
box("Фартук", X1 - 0.01, KZ0, X1, Z1, CT, 1.50, M["tile"])
UX = X1 - 0.35
box("Верхние шкафы корпус", UX + 0.02, KZ0, X1, Z1, 1.50, HC, M["ward"])
for (a, b) in ((KZ0, S1), (S1, H0), (H0, H1), (H1, Z1)):
    box("Фасад верх", UX, a + 0.002, UX + 0.02, b - 0.002, 1.50, HC - 0.002, M["ward"], 0.002)
box("Вытяжка (встроенная)", UX + 0.03, H0 + 0.03, X1 - 0.02, H1 - 0.03, 1.49, 1.50, M["black"])
box("LED под шкафами", UX + 0.04, KZ0 + 0.03, UX + 0.07, Z1 - 0.03, 1.495, 1.50, M["led"])
lt = bpy.data.lights.new("Рабочая зона", "AREA"); lt.size = 2.0; lt.size_y = 0.06; lt.energy = 30; lt.color = (1, 0.9, 0.78)
o = bpy.data.objects.new("Рабочая зона", lt); o.location = W(X1 - 0.30, (KZ0 + Z1) / 2, 1.48); o.rotation_euler = (0, 0, math.radians(90)); sc.collection.objects.link(o)
for (z_, c) in ((P0 + 0.10, "white"), (P0 + 0.17, "black")):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.035, depth=0.20, location=W(X1 - 0.12, z_, CT + 0.10)); bpy.context.active_object.data.materials.append(M[c])
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.09, depth=0.20, location=W(X1 - 0.20, 3.75, CT + 0.10)); bpy.context.active_object.data.materials.append(M["black"])   # чайник

# ---------------- левая стена (17.11 по обмеру): холодильник side-by-side у окна, колонны кофе+СВЧ и кладовая; у входа свободно
M["steel"] = mat("Нержавейка холодильника", "#B9BBBD", 0.28, 1.0)
FZ0, FZ1, FD = 1.40, 2.30, 0.70
bk_fit("holodilnik_sbs", X0 + FD / 2, (FZ0 + FZ1) / 2, 0.0, -90, 0.88, recolor=M["steel"], keep=("badge",))
FS = (FZ0 + FZ1) / 2
for zh in (FS - 0.015, FS + 0.055):
    box("Ручка холодильника", X0 + FD + 0.02, zh - 0.012, X0 + FD + 0.035, zh, 0.70, 1.60, M["steel"], 0.004)
box("Антресоль над холодильником", X0, FZ0, X0 + FD - 0.02, FZ1, 1.84, HC, M["ward"])
box("Фасад антресоли", X0 + FD - 0.02, FZ0 + 0.002, X0 + FD, FZ1 - 0.002, 1.842, HC - 0.002, M["ward"], 0.002)
CD = 0.65; CX = X0 + CD
box("Колонны корпус", X0, FZ1, CX - 0.02, 3.50, 0.10, HC, M["ward"])
box("Цоколь колонн", X0, FZ1, CX - 0.05, 3.50, 0, 0.10, M["black"])
box("Фасад колонны", CX - 0.02, FZ1 + 0.002, CX, 2.90 - 0.002, 0.10, 0.90, M["ward"], 0.002)
box("Кофемашина (встр.)", CX - 0.02, 2.32, CX + 0.002, 2.88, 0.92, 1.36, M["bglass"], 0.004)
box("СВЧ (встр.)", CX - 0.02, 2.32, CX + 0.002, 2.88, 1.38, 1.76, M["bglass"], 0.004)
box("СВЧ дисплей", CX + 0.002, 2.76, CX + 0.004, 2.85, 1.66, 1.70, M["led"])
box("Фасад колонны верх", CX - 0.02, FZ1 + 0.002, CX, 2.90 - 0.002, 1.78, HC - 0.002, M["ward"], 0.002)
box("Фасад кладовой", CX - 0.02, 2.90 + 0.002, CX, 3.50 - 0.002, 0.10, HC - 0.002, M["ward"], 0.002)
box("Гола верт.", CX - 0.02, 2.896, CX + 0.002, 2.904, 0.10, HC, M["black"])

# ---------------- стол 1200×700 у окна (верхняя стена) + 3 стула; подвес над столом
TX0, TX1, TD = 10.85, 12.05, 0.70
box("Стол столешница", TX0, Z0, TX1, Z0 + TD, 0.72, 0.75, M["tile"], 0.006)
for xl in (TX0 + 0.06, TX1 - 0.10):
    box("Ножка стола", xl, Z0 + TD - 0.10, xl + 0.04, Z0 + TD - 0.06, 0.0, 0.72, M["black"])
box("Царга", TX0 + 0.06, Z0 + 0.02, TX1 - 0.06, Z0 + TD - 0.06, 0.66, 0.72, M["black"])
for (xc, zc, rz) in ((11.15, Z0 + TD + 0.04, 180), (11.75, Z0 + TD + 0.04, 180), (TX0 - 0.20, Z0 + 0.35, 90)):
    Tm = Matrix.Translation(W(xc, zc, 0)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
    for o_ in bk_load("stul_minimal", Tm):
        for i_, ms in enumerate(o_.data.materials):
            o_.data.materials[i_] = M["knit"] if (ms and "cuir" in ms.name.lower()) else M["black"]
TCX = (TX0 + TX1) / 2
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.12, depth=0.012, location=W(TCX, Z0 + 0.35, 0.756)); bpy.context.active_object.data.materials.append(M["white"])
pz = Z0 + 0.38
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.09, depth=0.26, location=W(TCX, pz, 1.85)); bpy.context.active_object.data.materials.append(M["black"])
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.082, depth=0.004, location=W(TCX, pz, 1.718)); bpy.context.active_object.data.materials.append(M["shade"])
box("Шнур", TCX - 0.003, pz - 0.003, TCX + 0.003, pz + 0.003, 1.98, HC, M["black"])
lt = bpy.data.lights.new("Подвес", "SPOT"); lt.energy = 18; lt.spot_size = math.radians(70); lt.spot_blend = 0.5; lt.color = (1, 0.88, 0.72)
o = bpy.data.objects.new("Подвес", lt); o.location = W(TCX, pz, 1.71); sc.collection.objects.link(o)


#==AC==
ac_unit(("L", X0), 4.05, 2.58)        # К4 (17.11: над свободной частью левой стены у входа)

# ---------------- потолок: споты + LED по периметру
spots([(10.9, 2.80), (10.9, 3.90), (11.7, 2.80), (11.7, 3.90), (12.55, 2.80), (12.55, 3.90)], 60)   # 13.11: светлее (по заказчику)
for (x0, z0, x1, z1) in ((X0, Z0, X1, Z0 + 0.02), (X0, Z1 - 0.02, X1, Z1), (X0, Z0, X0 + 0.02, Z1), (X1 - 0.02, Z0, X1, Z1)):
    box("LED периметр", x0, z0, x1, z1, HC - 0.012, HC - 0.008, M["led"])

CAMS = {"1": ("1_ot_vhoda", W(9.85, 4.55, 1.60), W(12.60, 2.20, 1.00), 15),
        "2": ("2_rabochaya_zona", W(10.60, 3.60, 1.60), W(12.88, 3.30, 1.05), 16),
        "3": ("3_stol", W(11.90, 4.30, 1.60), W(11.20, 1.31, 0.85), 15),
        "4": ("4_ot_okna", W(12.20, 2.20, 1.65), W(9.70, 4.20, 0.95), 15),
        "9": ("9_sverhu_stol", W(TCX, 2.40, 2.60), W(TCX, 1.70, 0.0), 15),
        "5": ("5_holodilnik", W(12.10, 3.80, 1.55), W(9.60, 2.10, 1.00), 16)}
