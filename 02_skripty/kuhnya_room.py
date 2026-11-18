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

# ================= 18.11.2026: ВАРИАНТ 2в (по рисунку заказчика; схема 01_chertezhi/shema_kuhnya_2v.png)
# правая стена: шкаф 220 + полки перед шахтой → ПЛИТА П2 (вытяжка В3 над ней) → ящик 300 → МОЙКА М2 → ящик → УГОЛ (волшебный уголок)
# нижняя стена: от входа ХОЛОДИЛЬНИК 800 → колонна духовка Д3 + СВЧ №1 (вровень, 720) → ПММ 450 → ящик → угол
# левая стена — БЕЗ мебели (проход и место у стола); стол 1100×700 в левом верхнем углу у окна, 3 стула
RX = X1 - 0.60; CT = 0.90; KZ0 = 2.409; SH = 12.506
BZ = Z1 - 0.60; CZ = Z1 - 0.60
HZ0, HZ1 = 2.41, 3.01; MZ0, MZ1 = 3.31, 3.91                  # плита, мойка (правая стена)
TD = 0.72                                                        # глубина холодильника и колонны (вровень)
FX0, FX1 = 10.166, 10.966                                        # ниша холодильника 800
OX0, OX1 = 10.966, 11.566                                        # колонна духовка + СВЧ
PX0, PX1 = 11.566, 12.016                                        # ПММ 450
BX0 = PX0
# -- шкаф 220 перед шахтой и трубой
box("Шкаф у шахты корпус", RX + 0.02, Z0, SH, KZ0, 0.10, CT - 0.04, M["ward"])
box("Цоколь у шахты", RX + 0.05, Z0, SH, KZ0, 0, 0.10, M["black"])
for (a, b) in ((Z0, 1.86), (1.86, KZ0)):
    box("Фасад у шахты", RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, CT - 0.042, M["ward"], 0.002)
box("Столешница у шахты", RX - 0.02, Z0, SH, KZ0, CT - 0.04, CT, M["tile"])
for hh in (1.25, 1.62, 1.99, 2.36):
    box("Полка у шахты", RX + 0.02, Z0, SH, KZ0, hh, hh + 0.025, M["ward"])
    box("LED полки", RX + 0.04, Z0 + 0.03, RX + 0.06, KZ0 - 0.03, hh - 0.004, hh, M["led"])
for (a, b) in ((Z0, Z0 + 0.018), (KZ0 - 0.018, KZ0)): box("Боковина полок", RX + 0.02, a, SH, b, CT, HC, M["ward"])
# -- низ правой стены
box("Цоколь", RX + 0.05, KZ0, X1, Z1, 0, 0.10, M["black"])
box("Корпус низ правый", RX + 0.02, KZ0, X1, Z1, 0.10, CT - 0.04, M["ward"])
for (a, b) in ((HZ0, HZ1), (HZ1, MZ0), (MZ1, CZ)):
    for (h0, h1) in ((0.10, 0.37), (0.37, 0.63), (0.63, CT - 0.042)):
        box("Ящик", RX, a + 0.002, RX + 0.02, b - 0.002, h0 + 0.002, h1 - 0.002, M["ward"], 0.002)
box("Фасад мойка", RX, MZ0 + 0.002, RX + 0.02, MZ1 - 0.002, 0.10, CT - 0.042, M["ward"], 0.002)
box("Фасад угла (волшебный уголок)", RX, CZ + 0.002, RX + 0.02, Z1 - 0.002, 0.10, CT - 0.042, M["ward"], 0.002)
# -- низ нижней стены: ПММ + ящик до угла
box("Цоколь низ", BX0, BZ + 0.05, RX, Z1, 0, 0.10, M["black"])
box("Корпус низ нижний", BX0, BZ + 0.02, RX, Z1, 0.10, CT - 0.04, M["ward"])
box("Фасад ПММ", PX0 + 0.002, BZ, PX1 - 0.002, BZ + 0.02, 0.10, CT - 0.042, M["ward"], 0.002)
for (h0, h1) in ((0.10, 0.37), (0.37, 0.63), (0.63, CT - 0.042)):
    box("Ящик", PX1 + 0.002, BZ, RX - 0.002, BZ + 0.02, h0 + 0.002, h1 - 0.002, M["ward"], 0.002)
# -- столешница Г + фартук
box("Столешница правая", RX - 0.02, KZ0, X1, Z1, CT - 0.04, CT, M["tile"])
box("Столешница нижняя", BX0, BZ - 0.02, RX - 0.02, Z1, CT - 0.04, CT, M["tile"])
box("Фартук правый", X1 - 0.01, KZ0, X1, Z1, CT, 1.50, M["tile"])
box("Фартук нижний", BX0, Z1 - 0.01, X1, Z1, CT, 1.50, M["tile"])
# -- плита П2 у шахты + вытяжка В3
HCZ = (HZ0 + HZ1) / 2
bk_fit("panel_p2", RX + 0.30, HCZ, CT - 0.004, 90, 0.59)
bk_fit("vytyazhka_v3", X1 - 0.25, HCZ, 1.62, -90, 0.76)
# -- мойка М2 + кран 4 (рядом с плитой, через ящик 300)
SC = (MZ0 + MZ1) / 2
bk_fit("moyka_m2", RX + 0.30, SC, CT - 0.489, 90, 0.50)
_kr = bk_fit("kran_kuhnya_4", X1 - 0.19, SC, CT, -90, 0.40, "h")
for o in _kr:
    for i_ in range(len(o.data.materials)): o.data.materials[i_] = M["black"]
# -- верхние шкафы до потолка
UD = 0.35; UX = X1 - UD; UZ = Z1 - UD
for (a, b, h0) in ((KZ0, HZ1 + 0.08, 1.75), (HZ1 + 0.08, MZ0 + 0.30, 1.50), (MZ0 + 0.30, 4.06, 1.50), (4.06, UZ, 1.50)):
    box("Верх правый корпус", UX + 0.02, a, X1, b, h0, HC, M["ward"])
    box("Фасад верх", UX, a + 0.002, UX + 0.02, b - 0.002, h0, HC - 0.002, M["ward"], 0.002)
box("Угловой шкаф корпус", UX + 0.02, UZ + 0.02, X1, Z1, 1.50, HC, M["ward"])
box("Угловой фасад-гармошка", UX, UZ, UX + 0.02, Z1, 1.50, HC - 0.002, M["ward"], 0.002)
box("Верх нижний корпус", BX0, UZ + 0.02, UX, Z1, 1.50, HC, M["ward"])
box("Фасад верх", BX0 + 0.002, UZ, UX - 0.002, UZ + 0.02, 1.50, HC - 0.002, M["ward"], 0.002)
box("LED под шкафами", UX + 0.04, HZ1 + 0.10, UX + 0.07, UZ - 0.03, 1.495, 1.50, M["led"])
box("LED под шкафами", BX0 + 0.03, UZ + 0.04, UX - 0.03, UZ + 0.07, 1.495, 1.50, M["led"])
lt = bpy.data.lights.new("Рабочая зона", "AREA"); lt.size = 2.0; lt.size_y = 0.06; lt.energy = 30; lt.color = (1, 0.9, 0.78)
o = bpy.data.objects.new("Рабочая зона", lt); o.location = W(X1 - 0.30, (KZ0 + Z1) / 2, 1.48); o.rotation_euler = (0, 0, math.radians(90)); sc.collection.objects.link(o)
# -- колонна духовка + СВЧ (нижняя стена, вровень с холодильником 720)
CF = Z1 - TD                                                   # фронт колонны и холодильника
box("Колонна корпус", OX0, CF + 0.02, OX1, Z1, 0.10, HC, M["ward"])
box("Цоколь колонны", OX0, CF + 0.05, OX1, Z1, 0, 0.10, M["black"])
box("Фасад колонны низ", OX0 + 0.002, CF, OX1 - 0.002, CF + 0.02, 0.10, 0.70, M["ward"], 0.002)
OCX = (OX0 + OX1) / 2
M["steelh"] = mat("Сталь ручек техники", "#C8CACC", 0.22, 1.0)
M["okno_t"] = mat("Окно дверцы техники", "#3B3D40", 0.08)
M["disp"] = emis("Дисплей техники", "#7FD7FF", 3)
bk_fit("duhovka_d3", OCX, CF + 0.30, 0.72, 0, 0.594, recolor=M["bglass"], keep=("display", "screen", "led"))
bk_fit("svch_m1", OCX, CF + 0.29, 1.36, 0, 0.595, recolor=M["bglass"])
F0 = CF - 0.003
box("Окно духовки", OX0 + 0.07, F0, OX1 - 0.07, F0 + 0.004, 0.80, 1.13, M["okno_t"], 0.004)
box("Панель духовки", OX0 + 0.01, F0 - 0.002, OX1 - 0.01, F0 + 0.004, 1.235, 1.31, M["black"])
box("Дисплей духовки", OCX - 0.05, F0 - 0.003, OCX + 0.05, F0 - 0.002, 1.262, 1.285, M["disp"])
box("Ручка духовки", OX0 + 0.07, F0 - 0.032, OX1 - 0.07, F0 - 0.018, 1.185, 1.20, M["steelh"], 0.003)
for _xk in (OX0 + 0.09, OX1 - 0.09): box("Держатель ручки", _xk - 0.006, F0 - 0.02, _xk + 0.006, F0, 1.187, 1.198, M["steelh"])
box("Окно СВЧ", OX0 + 0.04, F0, OX1 - 0.17, F0 + 0.004, 1.40, 1.775, M["okno_t"], 0.004)
box("Панель СВЧ", OX1 - 0.15, F0 - 0.002, OX1 - 0.03, F0 + 0.004, 1.39, 1.785, M["black"])
box("Дисплей СВЧ", OX1 - 0.13, F0 - 0.003, OX1 - 0.05, F0 - 0.002, 1.735, 1.758, M["disp"])
for _k in range(4): box("Кнопка СВЧ", OX1 - 0.12, F0 - 0.006, OX1 - 0.06, F0 - 0.002, 1.66 - _k * 0.045, 1.685 - _k * 0.045, M["steelh"], 0.002)
box("Фасад колонны верх", OX0 + 0.002, CF, OX1 - 0.002, CF + 0.02, 1.84, HC - 0.002, M["ward"], 0.002)
# -- холодильник 800 у входа (модель — выбор заказчика), над ним антресоль, боковина к входу
FRM = OPT.get("holod", "holodilnik_800")   # 18.11: выбор заказчика №6
bk_fit(FRM, (FX0 + FX1) / 2, Z1 - 0.36, 0.0, 180, 0.72)   # холодильник №6 (Consul 624×725×1835): глубина 720 — вровень с колонной
box("Антресоль над холодильником", FX0, CF + 0.02, FX1, Z1, 1.88, HC, M["ward"])
box("Фасад антресоли", FX0 + 0.002, CF, FX1 - 0.002, CF + 0.02, 1.882, HC - 0.002, M["ward"], 0.002)
box("Боковина у холодильника", FX0 - 0.018, CF, FX0, Z1, 0, HC, M["ward"])

# ---------------- стол 1200×700 у окна + 3 стула; подвес над столом
TX0, TX1, TZ0, TZ1 = 9.90, 11.00, 1.50, 2.20                  # 18.11 вар. 2в: стол 1100×700 в левом верхнем углу
box("Стол столешница", TX0, TZ0, TX1, TZ1, 0.72, 0.75, M["tile"], 0.006)
for xl in (TX0 + 0.06, TX1 - 0.10):
    for zl in (TZ0 + 0.06, TZ1 - 0.10): box("Ножка стола", xl, zl, xl + 0.04, zl + 0.04, 0.0, 0.72, M["black"])
box("Царга", TX0 + 0.06, TZ0 + 0.06, TX1 - 0.06, TZ1 - 0.06, 0.66, 0.72, M["black"])
for (xc, zc, rz) in ((10.20, TZ1 + 0.04, 180), (10.70, TZ1 + 0.04, 180), (TX1 + 0.22, (TZ0 + TZ1) / 2, -90)):
    Tm = Matrix.Translation(W(xc, zc, 0)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
    for o_ in bk_load("stul_minimal", Tm):
        for i_, ms in enumerate(o_.data.materials):
            o_.data.materials[i_] = M["knit"] if (ms and "cuir" in ms.name.lower()) else M["black"]
TCX = (TX0 + TX1) / 2
pz = (TZ0 + TZ1) / 2
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.09, depth=0.26, location=W(TCX, pz, 1.85)); bpy.context.active_object.data.materials.append(M["black"])
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.082, depth=0.004, location=W(TCX, pz, 1.718)); bpy.context.active_object.data.materials.append(M["shade"])
box("Шнур", TCX - 0.003, pz - 0.003, TCX + 0.003, pz + 0.003, 1.98, HC, M["black"])
lt = bpy.data.lights.new("Подвес", "SPOT"); lt.energy = 18; lt.spot_size = math.radians(70); lt.spot_blend = 0.5; lt.color = (1, 0.88, 0.72)
o = bpy.data.objects.new("Подвес", lt); o.location = W(TCX, pz, 1.71); sc.collection.objects.link(o)


#==AC==
# 18.11 (заказчик): кондиционера на кухне НЕ будет (К4 убран)

# ---------------- потолок: споты + LED по периметру
spots([(10.9, 2.80), (10.9, 3.70), (11.7, 2.80), (11.7, 3.70), (11.0, 1.70)], 60)
for (x0, z0, x1, z1) in ((X0, Z0, X1, Z0 + 0.02), (X0, Z1 - 0.02, X1, Z1), (X0, Z0, X0 + 0.02, Z1), (X1 - 0.02, Z0, X1, Z1)):
    box("LED периметр", x0, z0, x1, z1, HC - 0.012, HC - 0.008, M["led"])

# 18.11 (заказчик: «кухня не похожа на мебель — коробки»): как во всей квартире — чёрные ручки на каждом фасаде и ящике,
# тёмные швы 3 мм между фасадами (тень за фасадом), ручки на холодильнике
M["shov"] = mat("Шов фасадов (тень)", "#2A2A2C", 0.8)
_rc = Vector(((X0 + X1) / 2, -(Z0 + Z1) / 2))
bpy.context.view_layer.update()
for _o in [o for o in sc.objects if o.type == "MESH" and (o.name.startswith("Фасад") or o.name.startswith("Ящик"))]:
    _P = [_o.matrix_world @ Vector(c) for c in _o.bound_box]
    x0_, x1_ = min(p.x for p in _P), max(p.x for p in _P); y0_, y1_ = min(p.y for p in _P), max(p.y for p in _P); z0_, z1_ = min(p.z for p in _P), max(p.z for p in _P)
    thin_x = (x1_ - x0_) < (y1_ - y0_)
    if thin_x:
        fx = x0_ if abs(_rc.x - x0_) < abs(_rc.x - x1_) else x1_; sg = -1 if fx == x0_ else 1
        a0_, a1_ = y0_, y1_
    else:
        fy = y0_ if abs(_rc.y - y0_) < abs(_rc.y - y1_) else y1_; sg = -1 if fy == y0_ else 1
        a0_, a1_ = x0_, x1_
    # тень-шов: тёмная пластина 6 мм за фасадом, шире на 3 мм
    if thin_x:
        bx = fx - sg * 0.024
        bpy.ops.mesh.primitive_cube_add(location=(bx, (a0_ + a1_) / 2, (z0_ + z1_) / 2)); sh_ = bpy.context.active_object; sh_.scale = (0.003, (a1_ - a0_) / 2 + 0.003, (z1_ - z0_) / 2 + 0.003)
    else:
        by = fy - sg * 0.024
        bpy.ops.mesh.primitive_cube_add(location=((a0_ + a1_) / 2, by, (z0_ + z1_) / 2)); sh_ = bpy.context.active_object; sh_.scale = ((a1_ - a0_) / 2 + 0.003, 0.003, (z1_ - z0_) / 2 + 0.003)
    sh_.name = "Шов"; sh_.data.materials.append(M["shov"])
    W_, Hh = a1_ - a0_, z1_ - z0_
    if "угла" in _o.name or "антресоли" in _o.name: pass
    if Hh < 0.45 and W_ > Hh:                      # ящик: горизонтальная ручка у верхней кромки
        L = min(0.40, W_ * 0.6); c = (a0_ + a1_) / 2; ha, hb, hz0, hz1 = c - L / 2, c + L / 2, z1_ - 0.055, z1_ - 0.043
    else:                                           # дверца: вертикальная ручка у края, ближе к центру комнаты
        ea = a1_ - 0.045 if abs((_rc.y if thin_x else _rc.x) - a1_) < abs((_rc.y if thin_x else _rc.x) - a0_) else a0_ + 0.045
        ha, hb = ea - 0.006, ea + 0.006
        if z0_ > 1.3: hz0, hz1 = z0_ + 0.04, z0_ + 0.34             # навесной — внизу
        elif z1_ < 1.0: hz0, hz1 = z1_ - 0.30, z1_ - 0.04           # нижний — вверху
        else: hz0, hz1 = 0.95, 1.30                                  # колонна — на уровне руки
    if thin_x:
        hx0, hx1 = (fx - 0.026, fx) if sg < 0 else (fx, fx + 0.026)
        bpy.ops.mesh.primitive_cube_add(location=((hx0 + hx1) / 2, (ha + hb) / 2, (hz0 + hz1) / 2)); h_ = bpy.context.active_object; h_.scale = ((hx1 - hx0) / 2, (hb - ha) / 2, (hz1 - hz0) / 2)
    else:
        hy0, hy1 = (fy - 0.026, fy) if sg < 0 else (fy, fy + 0.026)
        bpy.ops.mesh.primitive_cube_add(location=((ha + hb) / 2, (hy0 + hy1) / 2, (hz0 + hz1) / 2)); h_ = bpy.context.active_object; h_.scale = ((hb - ha) / 2, (hy1 - hy0) / 2, (hz1 - hz0) / 2)
    h_.name = "Ручка"; h_.data.materials.append(M["black"])
    bv = h_.modifiers.new("b", "BEVEL"); bv.width = 0.003; bv.segments = 2
exec(open(os.path.join(PROJ, "02_skripty", "decor_common.py"), encoding="utf-8").read())   # 17.11: декор (decor=0 — без него)
CAMS = {"v1": ("v1_pravaya_plita_moyka", W(10.20, 3.10, 1.3), W(X1, 3.10, 1.3), 0),
        "v2": ("v2_nizhnyaya_holodilnik", W(11.20, 2.30, 1.3), W(11.20, Z1, 1.3), 0),
        "v3": ("v3_levaya_svobodno", W(12.20, 3.00, 1.3), W(X0, 3.00, 1.3), 0),
        "v4": ("v4_okno_stol", W(11.10, 3.85, 1.3), W(11.10, Z0, 1.3), 0),
        "v5": ("v5_ot_vhoda", W(9.85, 3.85, 1.3), W(X1, Z0, 1.3), 0),
        "v6": ("v6_ot_shahty_k_vhodu", W(12.20, 2.50, 1.3), W(X0, Z1, 1.3), 0),
        "v7": ("v7_ugol_iz_za_stola", W(9.75, 2.45, 1.3), W(X1, Z1, 1.3), 0),
        "v8": ("v8_ot_ugla_k_oknu", W(12.15, 4.00, 1.3), W(X0, Z0, 1.3), 0),
        "v9": ("v9_ugol_moyka", W(11.10, 3.10, 1.3), W(X1, Z1, 1.3), 0)}
if OPENC: CAMS = {k: ("open_" + v[0],) + v[1:] for k, v in CAMS.items()}
