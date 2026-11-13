# ======================= КУХНЯ — ВАРИАНТ 7 (13.11.2026, согласован по схеме 01_chertezhi/shema_kuhnya7.png):
# окно свободно; правая стена от окна: мойка 600 → ПММ 450 → плита 600 + духовка → угловой низ; у нижней стены сразу у входа
# холодильник side-by-side, колонны (кладовая, СВЧ+кофемашина), бутылочница 320; слева от окна стол 1200×600 + 2 стула;
# левая стена свободна (стол, буфет, ТВ убраны); К4 на левой стене.
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

# ---------------- правая стена: мойка у окна → ПММ → плита → угловой низ; столешница до угла; фартук; верхние шкафы
RX = X1 - 0.60; CT = 0.90
S0, S1, P0, P1, H0, H1 = Z0, 2.509, 2.509, 2.959, 2.959, 3.559
box("Цоколь", RX + 0.05, Z0, X1, Z1, 0, 0.10, M["black"])
box("Корпус низ", RX + 0.02, Z0, X1, Z1, 0.10, CT - 0.04, M["ward"])
box("Гола-профиль", RX, Z0, RX + 0.025, Z1, CT - 0.10, CT - 0.07, M["black"])
for (a, b, t) in ((S0, S1, "мойка"), (P0, P1, "ПММ"), (H1, Z1, "угол")):
    box("Фасад " + t, RX, a + 0.002, RX + 0.02, b - 0.002, 0.10, CT - 0.11, M["ward"], 0.002)
box("Духовка", RX - 0.002, H0 + 0.03, RX + 0.02, H1 - 0.03, 0.14, 0.72, M["bglass"], 0.004)
box("Ящик под духовкой", RX, H0 + 0.002, RX + 0.02, H1 - 0.002, 0.10, 0.13, M["ward"], 0.002)
box("Ящик над духовкой", RX, H0 + 0.002, RX + 0.02, H1 - 0.002, 0.73, CT - 0.11, M["ward"], 0.002)
box("Столешница", RX - 0.02, Z0, X1, Z1, CT - 0.04, CT, M["tile"])
bk_fit("plita_bosch600", RX + 0.31, (H0 + H1) / 2, CT, 90, 0.59)      # индукция Bosch 600, 4 зоны
box("Мойка (врезная, графит)", RX + 0.08, S0 + 0.10, X1 - 0.10, S1 - 0.08, CT - 0.002, CT + 0.001, M["black"])
SC = (S0 + 0.10 + S1 - 0.08) / 2
box("Смеситель стойка", X1 - 0.075, SC - 0.02, X1 - 0.045, SC + 0.02, CT, CT + 0.32, M["black"], 0.008)
box("Смеситель излив", X1 - 0.30, SC - 0.015, X1 - 0.045, SC + 0.015, CT + 0.29, CT + 0.32, M["black"], 0.008)
box("Фартук", X1 - 0.01, Z0, X1, Z1, CT, 1.50, M["tile"])
UX = X1 - 0.35
box("Верхние шкафы корпус", UX + 0.02, Z0, X1, Z1, 1.50, HC, M["ward"])
for (a, b) in ((Z0, S1), (S1, H0), (H0, H1), (H1, Z1)):
    box("Фасад верх", UX, a + 0.002, UX + 0.02, b - 0.002, 1.50, HC - 0.002, M["ward"], 0.002)
box("Вытяжка (встроенная)", UX + 0.03, H0 + 0.03, X1 - 0.02, H1 - 0.03, 1.49, 1.50, M["black"])
box("LED под шкафами", UX + 0.04, Z0 + 0.03, UX + 0.07, Z1 - 0.03, 1.495, 1.50, M["led"])
lt = bpy.data.lights.new("Рабочая зона", "AREA"); lt.size = 2.0; lt.size_y = 0.06; lt.energy = 30; lt.color = (1, 0.9, 0.78)
o = bpy.data.objects.new("Рабочая зона", lt); o.location = W(X1 - 0.30, (Z0 + Z1) / 2, 1.48); o.rotation_euler = (0, 0, math.radians(90)); sc.collection.objects.link(o)
for (z_, c) in ((P0 + 0.10, "white"), (P0 + 0.17, "black")):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.035, depth=0.20, location=W(X1 - 0.12, z_, CT + 0.10)); bpy.context.active_object.data.materials.append(M[c])
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.09, depth=0.20, location=W(X1 - 0.20, 3.85, CT + 0.10)); bpy.context.active_object.data.materials.append(M["black"])   # чайник

# ---------------- нижняя стена: холодильник side-by-side сразу у входа (по эскизу заказчика), колонны до потолка, бутылочница
M["steel"] = mat("Нержавейка холодильника", "#B9BBBD", 0.28, 1.0)
FX0, FX1, FZ = 9.96, 10.88, Z1 - 0.70
bk_fit("holodilnik_sbs", (FX0 + FX1) / 2, (FZ + Z1) / 2, 0.0, 180, 0.88, recolor=M["steel"], keep=("badge",))
FS = (FX0 + FX1) / 2
for xh in (FS + 0.015, FS - 0.055):
    box("Ручка холодильника", xh, FZ - 0.035, xh + 0.012, FZ - 0.02, 0.70, 1.60, M["steel"], 0.004)
    for hh in (0.74, 1.56): box("Стойка ручки", xh, FZ - 0.035, xh + 0.012, FZ + 0.01, hh - 0.01, hh + 0.01, M["steel"])
box("Антресоль над холодильником", FX0, FZ + 0.02, FX1, Z1, 1.84, HC, M["ward"])
box("Фасад антресоли", FX0 + 0.002, FZ, FX1 - 0.002, FZ + 0.02, 1.842, HC - 0.002, M["ward"], 0.002)
CZ = Z1 - 0.60
box("Колонны корпус", FX1, CZ + 0.02, RX, Z1, 0.10, HC, M["ward"])
box("Цоколь колонн", FX1, CZ + 0.05, RX, Z1, 0, 0.10, M["black"])
box("Фасад кладовой", FX1 + 0.002, CZ, 11.48 - 0.002, CZ + 0.02, 0.10, HC - 0.002, M["ward"], 0.002)
box("Фасад колонны", 11.48 + 0.002, CZ, 12.08 - 0.002, CZ + 0.02, 0.10, 0.90, M["ward"], 0.002)
box("Кофемашина (встр.)", 11.50, CZ - 0.002, 12.06, CZ + 0.02, 0.92, 1.36, M["bglass"], 0.004)
box("СВЧ (встр.)", 11.50, CZ - 0.002, 12.06, CZ + 0.02, 1.38, 1.76, M["bglass"], 0.004)
box("СВЧ дисплей", 11.94, CZ - 0.004, 12.03, CZ - 0.003, 1.66, 1.70, M["led"])
box("Фасад колонны верх", 11.48 + 0.002, CZ, 12.08 - 0.002, CZ + 0.02, 1.78, HC - 0.002, M["ward"], 0.002)
box("Бутылочница", 12.08 + 0.002, CZ, RX - 0.002, CZ + 0.02, 0.10, CT - 0.04, M["ward"], 0.002)
box("Столешница у бутылочницы", 12.08, CZ, RX, Z1, CT - 0.04, CT, M["tile"])
box("Шкаф над бутылочницей", 12.08 + 0.002, CZ + 0.25, RX - 0.002, Z1, 1.50, HC, M["ward"], 0.002)
for xg in (11.48, 12.08):
    box("Гола верт.", xg - 0.004, CZ - 0.002, xg + 0.004, CZ + 0.02, 0.10, HC, M["black"])

# ---------------- верхняя стена слева от окна (13.11, по заказчику): шкаф убран — стол 1200×600 у стены + 3 стула (задвинуты)
TX0, TX1, TD = 9.83, 11.03, 0.60          # вариант Б: стол придвинут вплотную к откосу окна
box("Стол столешница", TX0, Z0, TX1, Z0 + TD, 0.72, 0.75, M["tile"], 0.006)
for xl in (TX0 + 0.06, TX1 - 0.10):
    box("Ножка стола", xl, Z0 + TD - 0.10, xl + 0.04, Z0 + TD - 0.06, 0.0, 0.72, M["black"])
box("Царга", TX0 + 0.06, Z0 + 0.02, TX1 - 0.06, Z0 + TD - 0.06, 0.66, 0.72, M["black"])
for (xc, zc, rz) in ((10.13, Z0 + TD + 0.04, 180), (10.73, Z0 + TD + 0.04, 180), (TX1 + 0.20, Z0 + 0.30, -90)):   # по эскизу: 2 стула с длинной стороны, 1 — с торца у окна
    Tm = Matrix.Translation(W(xc, zc, 0)) @ Matrix.Rotation(math.radians(rz), 4, "Z")
    for o_ in bk_load("stul_minimal", Tm):
        for i_, ms in enumerate(o_.data.materials):
            o_.data.materials[i_] = M["knit"] if (ms and "cuir" in ms.name.lower()) else M["black"]
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.12, depth=0.012, location=W(10.43, Z0 + 0.30, 0.756)); bpy.context.active_object.data.materials.append(M["white"])
pz = Z0 + 0.32
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.09, depth=0.26, location=W(10.43, pz, 1.85)); bpy.context.active_object.data.materials.append(M["black"])
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.082, depth=0.004, location=W(10.43, pz, 1.718)); bpy.context.active_object.data.materials.append(M["shade"])
box("Шнур", 10.427, pz - 0.003, 10.433, pz + 0.003, 1.98, HC, M["black"])
lt = bpy.data.lights.new("Подвес", "SPOT"); lt.energy = 18; lt.spot_size = math.radians(70); lt.spot_blend = 0.5; lt.color = (1, 0.88, 0.72)
o = bpy.data.objects.new("Подвес", lt); o.location = W(10.43, pz, 1.71); sc.collection.objects.link(o)

# ---------------- левая стена свободна (13.11: стол, буфет и ТВ убраны по заказчику)

#==AC==
ac_unit(("L", X0), 2.90, 2.58)        # К4

# ---------------- потолок: споты + LED по периметру
spots([(11.0, 2.70), (11.0, 3.40), (11.8, 2.70), (11.8, 3.40), (12.55, 2.40), (12.55, 3.40)], 30)
for (x0, z0, x1, z1) in ((X0, Z0, X1, Z0 + 0.02), (X0, Z1 - 0.02, X1, Z1), (X0, Z0, X0 + 0.02, Z1), (X1 - 0.02, Z0, X1, Z1)):
    box("LED периметр", x0, z0, x1, z1, HC - 0.012, HC - 0.008, M["led"])

CAMS = {"1": ("1_ot_vhoda", W(9.85, 3.45, 1.60), W(12.70, 2.30, 1.00), 15),
        "2": ("2_rabochaya_zona", W(10.40, 3.20, 1.60), W(12.90, 2.60, 1.05), 16),
        "3": ("3_stol", W(11.70, 3.30, 1.60), W(9.60, 1.95, 0.85), 15),
        "4": ("4_ot_okna", W(11.80, 2.20, 1.65), W(10.40, 4.15, 0.95), 15),
        "9": ("9_sverhu_stol", W(10.43, 2.75, 2.60), W(10.43, 2.30, 0.0), 15),
        "5": ("5_holodilnik", W(11.60, 2.50, 1.55), W(10.40, 4.15, 0.95), 16)}
