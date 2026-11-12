# =========================================================== 2. Мебель
s = Sheet("Планировочное решение с расстановкой мебели", 2)
s.furniture(fill="#F3EFE7", col="#6B665C", sw=3); s.walls(); s.numbers(names=True)
def mlabel(x, z, t, size=26):
    s.A(f'<text x="{X(x):.0f}" y="{Y(z):.0f}" text-anchor="middle" font-size="{size}" fill="{INK}">{t}</text>')
for f in FURN:
    if not f["name"]: continue
    cx, cz = f["x"] + f["w"] / 2, f["z"] + f["d"] / 2 + 0.05
    if f["d"] > f["w"] * 1.6:
        s.A(f'<text x="{X(cx):.0f}" y="{Y(cz):.0f}" transform="rotate(-90 {X(cx):.0f} {Y(cz):.0f})" text-anchor="middle" font-size="24" fill="{INK}">{f["name"]}</text>')
    else:
        mlabel(cx, cz, f["name"], 24)
mlabel(0.71, 8.55, "биде", 24); mlabel(1.43, 8.55, "унитаз", 24); mlabel(5.62, 8.43, "гиг. душ*", 22); mlabel(5.62, 9.13, "унитаз", 22); mlabel(11.4, 3.15, "Стол", 24)
s.explication("Экспликация помещений", expl_rows(), colname="м²")
s.notes(["1. Шкафы — до h=2400; фасады —", "    на согласование.", "2. Кухня у стояка Т1, вытяжка", "    в вент. отверстие перекрытия.",
         "3. Биде в обоих с/у, рядом с унитазом:", "    санузел 400/720/400, ванная", "    395/700/395; ванна 1400.", "4. Размеры мебели уточнить", "    у производителя."])
s.save("s2_mebel")

# =========================================================== 3. Розетки
s = Sheet("План размещения розеток", 3)
s.furniture(); s.walls(); s.numbers()
its = []
for (n, room, wall, a, kind, h, what, cnt) in SK:
    syms = [sock_sym(kind)] * min(cnt, 4) + ([lan_sym] if kind == "tv" else [])
    its.append(dict(n=n, room=room, wall=wall, a=a, syms=syms, text=f"h={h}", above=(n == 34)))
place(s, its, None)
xs, zs = 3.455, 8.15
s.A(f'<rect x="{X(xs)-30:.1f}" y="{Y(zs)-34:.1f}" width="26" height="68" fill="{RED}" stroke="{INK}" stroke-width="2"/>')
s.A(f'<line x1="{X(xs)-17:.1f}" y1="{Y(zs)-34:.1f}" x2="{X(xs)+60:.1f}" y2="{Y(7.55):.1f}" stroke="{INK}" stroke-width="2"/><text x="{X(xs)+70:.0f}" y="{Y(7.55)+10:.0f}" font-size="30" fill="{INK}">Эл.щит + слаботочный, h=1500</text>')
tot = {"std": 0, "tv": 0, "wet": 0, "pwr": 0, "ac": 0}
for x in SK: tot[x[4]] += x[7]
s.explication("Экспликация", [("Розетка 220 В, 16 А", bound(sock_sym("std"), s), tot["std"]), ("Розетка за ТВ (в блоке)", bound(sock_sym("tv"), s), tot["tv"]),
    ("Интернет / ТВ (RJ45)", bound(lan_sym, s), 3), ("Розетка IP44 с крышкой", bound(sock_sym("wet"), s), tot["wet"]), ("Силовая 32 А (плита)", bound(sock_sym("pwr"), s), tot["pwr"]),
    ("Кондиционер", bound(sock_sym("ac"), s), tot["ac"]), ("Подрозетник Ø68", lambda cx, cy: s.A(f'<circle cx="{cx}" cy="{cy}" r="15" fill="none" stroke="{INK}" stroke-width="3"/>'), sum(tot.values()) + 3)])
s.notes(["1. h — высота от чистого пола до", "    центра розетки, мм.", "2. Красные размеры — привязка", "    к оси розетки от угла помещения.", "3. Блок: общая рамка, шаг 71 мм.",
         "4. Влажные зоны: IP44, УЗО 30 мА.", "5. Не ближе 600 мм к ванне и душу;", "    не над мойкой и плитой.", "6. Кабель ВВГнг(А)-LS: 3×2,5 —", "    розетки; 3×6 — плита 32 А.", "7. Группы щита — следующий лист."])
s.save("s3_rozetki")

# =========================================================== 4. Выключатели
SW = [  # n, room, wall, a, keys, walk, text
 (1, "Гостиная", "L", 6.35, 2, False, "диммер 2 кан."),
 (2, "Комната", "R", 6.35, 3, False, "h=900 3-кл. (3-я — резерв)"),
 (3, "Спальня 2", "B", 10.25, 3, False, "h=900 3-кл. (3-я — бра)"),
 (4, "Кухня", "L", 4.45, 3, False, "h=900 3-кл. (3-я — подсв. столешницы)"),
 (5, "Коридор", "L", 6.85, 2, False, "h=900  с/у: свет + вент."),
 (6, "Коридор", "B", 5.20, 2, False, "h=900  ванная: свет + вент."),
 (7, "Прихожая", "B", 3.30, 2, True, "h=900 проходной 2-кл.: круглые / LED паз"),
 (8, "Коридор", "R", 7.65, 2, True, "h=900 проходной 2-кл."),
]
s = Sheet("План размещения выключателей", 4)
s.furniture(); s.walls(); s.numbers()
its = [dict(n=n, room=room, wall=wall, a=a, syms=[sw_sym(k, w)], text=t, above=(n == 1)) for (n, room, wall, a, k, w, t) in SW]
place(s, its, None)
s.explication("Экспликация", [("Выключатель 1-клав.", None, 0), ("Диммер 3-канальный (гостиная)", bound(sw_sym(3), s), 1), ("Выключатель 2-клав.", bound(sw_sym(2), s), sum(1 for x in SW if x[4] == 2 and not x[5])), ("Выключатель 3-клав.", bound(sw_sym(3), s), sum(1 for x in SW if x[4] == 3 and not x[5])),
                              ("Переключатель проходной 2-клав.", bound(sw_sym(2, True), s), sum(1 for x in SW if x[5])), ("Подрозетник Ø68", lambda cx, cy: s.A(f'<circle cx="{cx}" cy="{cy}" r="15" fill="none" stroke="{INK}" stroke-width="3"/>'), len(SW))])
s.notes(["1. Все выключатели h=900 от пола", "    до центра, 100–150 мм от", "    откоса со стороны ручки двери.", "2. Гостиная: диммер 2 канала +", "    4 сценария (лист света).", "    Комнаты, кухня: клавиша 1 —", "    основной свет, клавиша 2 —",
         "    LED-подсветка потолка.", "3. Ванная и санузел — выключатели", "    снаружи, в коридоре; 2-я", "    клавиша — вытяжной вентилятор.", "4. Коридор + прихожая: проходные", "    2-клав. у входной двери и у", "    спальни 2 (кл.1 — круглые Ø240,", "    кл.2 — LED в пазу потолка).",
         "5. Кабель ВВГнг(А)-LS 3×1,5,", "    группы освещения C10.", "6. ЗАПАС: в подрозетник выключателя", "    заводить 5-жильный кабель (3 линии", "    + N + PE) — можно добавить свет", "    без штробления."])
s.save("s4_vykl")

# =========================================================== 5. Сантехника
def dot(col, t):
    def f(cx, cy, s):
        s.A(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{16*FS:.0f}" fill="{col}" stroke="{INK}" stroke-width="2"/><text x="{cx:.1f}" y="{cy+7*FS:.1f}" text-anchor="middle" font-size="{18*FS:.0f}" font-weight="bold" fill="#FFFFFF">{t}</text>')
    return f
CW, HW, KN = dot(BLUE, "Х"), dot(RED, "Г"), dot(BROWN, "К")
PL = [  # n, room, wall, a, syms, text   (13.11.2026: по согласованной расстановке shema_vanna.png и кухне s11)
 (1, "Кухня", "R", 3.28, [CW, HW, KN], "мойка: Х/Г h=550, К h=500"),
 (2, "Кухня", "R", 2.73, [CW, KN], "ПММ: h=450"),
 (3, "Санузел", "L", 7.25, [CW, HW], "душ: смеситель h=1100"),
 (4, "Санузел", "T", 1.31, [CW, HW, KN], "раковина (верхняя стена): Х/Г h=550, К h=500"),
 (5, "Санузел", "B", 0.71, [CW, HW, KN], "биде: Х/Г h=250, К Ø50 h=200"),
 (6, "Санузел", "B", 1.43, [CW, KN], "унитаз: Х h=1000*, К Ø110 h=230"),
 (7, "Ванная", "L", 8.78, [CW, KN], "стиралка 10 кг: Х h=600, К h=600 (сбоку от машины)"),
 (8, "Ванная", "B", 5.55, [CW, HW], "ванна 1300: смеситель h=800"),
 (9, "Ванная", "R", 8.415, [CW, KN], "унитаз: Х h=1000*, К Ø110 h=230"),
 (10, "Ванная", "R", 8.69, [CW, HW], "гиг. душ у унитаза: Х/Г h=700"),
 (11, "Ванная", "R", 8.42, [CW, HW, KN], "бойлер Б1 80 л (над унитазом): Х/Г h=1750, К (клапан)"),
 (12, "Санузел", "B", 1.43, [CW, HW, KN], "бойлер Б2 80 л (над унитазом): Х/Г h=1750, К (клапан)"),
 (13, "Санузел", "L", 8.00, [CW, KN], "бак 200 л под заказ + насос: Х h=300, перелив в трап"),
 (14, "Ванная", "L", 8.36, [CW, HW, KN], "раковина: Х/Г h=550, К h=500"),
]
s = Sheet("План сантехнического оборудования", 5)
s.furniture(); s.walls(); s.numbers()
its = [dict(n=n, room=room, wall=wall, a=a, syms=sy, text="", above=(room == "Санузел" and wall == "B")) for (n, room, wall, a, sy, t) in PL]
place(s, its, None)
# drains: shower and bath
for (x, z, t) in ((0.67, 7.26, "трап душа"), (4.95, 9.16, "слив ванны")):
    s.A(f'<rect x="{X(x)-14:.1f}" y="{Y(z)-14:.1f}" width="28" height="28" fill="none" stroke="{BROWN}" stroke-width="4"/><line x1="{X(x)-14:.1f}" y1="{Y(z):.1f}" x2="{X(x)+14:.1f}" y2="{Y(z):.1f}" stroke="{BROWN}" stroke-width="3"/>')
cnt = lambda sym: sum(x[4].count(sym) for x in PL)
s.explication("Выводы воды и канализации", [(t[0].upper() + t[1:], None, "", n) for (n, room, wall, a, sy, t) in PL], colname="")
s.notes(["Х — холодная, Г — горячая, К — канал.", "1. h — от чистого пола до оси", "    вывода, мм.", "2. * Унитазы — подвесные; биде —", "    в санузле; в ванной — гиг. душ", "    у унитаза.",
         "3. Канализация: уклон ≥2% к", "    стояку; Ø50 — приборы, Ø110 —", "    унитазы.", "4. Стояки Т1–Т3 — по плану", "    застройщика, не переносить.",
         "5. Душ: трап с гидрозатвором,", "    гидроизоляция пола + 200 мм", "    на стены (в душе — 2000).", "6. Б1, Б2 — пунктир: над унитазами", "    в шкафах 550, h 1700–2650.", "7. Бак 200 л — узкий под заказ", "    520×220×2000, на полу, санузел."])
s.save("s5_santeh")

# =========================================================== 6. Кондиционеры
s = Sheet("План кондиционеров", 6)
s.furniture(); s.walls(); s.numbers()
units = [  # (x,z,w,d) indoor unit rect in metres, label, label pos, socket ref
 ((5.545 - 0.22, 0.45, 0.22, 0.80), "К1 гостиная", (4.4, 1.7)),
 ((5.745, 0.50, 0.22, 0.80), "К2 комната", (7.1, 1.7)),
 ((14.745 - 0.22, 4.60, 0.22, 0.80), "К3 спальня 2", (13.7, 5.05)),
 ((9.145, 1.95, 0.22, 0.80), "К4 кухня", (10.3, 2.75)),
]
for (x, z, w, d), t, (lx, lz) in units:
    s.A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#DFF0E6" stroke="{GREEN}" stroke-width="5"/>')
    s.A(f'<text x="{X(lx):.0f}" y="{Y(lz):.0f}" text-anchor="middle" font-size="30" font-weight="bold" fill="{GREEN}">{t}</text>')
    s.A(f'<text x="{X(lx):.0f}" y="{Y(lz)+38:.0f}" text-anchor="middle" font-size="26" fill="{INK}">верх блока h=2500</text>')
# outdoor units in niches
for (x, z, w, d), t in (((515/P, 40/P, 45/P, 28/P), "Н1, Н2"), ((785/P, 160/P, 36/P, 26/P), "Н3")):
    s.A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#FFFFFF" stroke="{GREEN}" stroke-width="5"/>')
    s.A(f'<text x="{X(x+w/2):.0f}" y="{Y(z+d)+40:.0f}" text-anchor="middle" font-size="28" font-weight="bold" fill="{GREEN}">{t}</text>')
# routes (dashed, under the ceiling)
routes = [[(5.43, 0.55), (5.43, 0.40), (9.6, 0.40), (9.6, 0.97)],
          [(5.86, 0.60), (5.86, 0.45), (9.7, 0.45), (9.7, 0.97)],
          [(14.64, 4.65), (14.64, 3.40), (14.58, 3.40)],
          [(9.30, 2.00), (9.30, 1.40)]]
for pts in routes:
    d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(z):.1f}" for i, (x, z) in enumerate(pts))
    s.A(f'<path d="{d}" fill="none" stroke="{GREEN}" stroke-width="4" stroke-dasharray="16 10" marker-end="url(#arr)"/>')
s.explication("Экспликация", [("Внутренний блок 2,5–3,5 кВт", lambda cx, cy: s.A(f'<rect x="{cx-26}" y="{cy-10}" width="52" height="20" fill="#DFF0E6" stroke="{GREEN}" stroke-width="4"/>'), 4),
                              ("Наружный блок в нише", lambda cx, cy: s.A(f'<rect x="{cx-20}" y="{cy-14}" width="40" height="28" fill="#FFFFFF" stroke="{GREEN}" stroke-width="4"/>'), 4),
                              ("Трасса фреон + дренаж", lambda cx, cy: s.A(f'<line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{GREEN}" stroke-width="4" stroke-dasharray="12 8"/>'), "4"),
                              ("Розетка h=2200 (лист 3)", bound(sock_sym("ac"), s), 4)])
s.notes(["1. Блок на стене, верх h=2500,", "    150–200 мм до потолка.", "2. Трассы скрыто, в штробе / за", "    потолком; уклон дренажа ≥1%", "    к наружному блоку.",
         "3. Не вешать над кроватью и", "    рабочим местом — поток вдоль", "    комнаты.", "4. Ниши Н1/Н2 у комнаты, Н3 —", "    у спальни 2 (по плану застр.).",
         "5. Розетки №6, 13, 26, 49 — сбоку", "    от блока, лист 3.", "6. К4 кухня: наружный блок Н4 — в", "    нише Н1/Н2 (проверить место на", "    замере) или на фасаде у окна кухни."])
s.save("s6_kond")

# =========================================================== 7. Тёплый пол
s = Sheet("План тёплого пола", 7)
zones = {"Ванная": [(3.62, 8.22, 0.60, 0.60), (3.64, 8.89, 1.40, 0.55), (5.52, 8.235, 0.55, 0.36), (5.52, 8.935, 0.55, 0.36)],
         "Санузел": [(0.53, 8.47, 0.40, 0.55), (1.25, 8.47, 0.36, 0.55), (1.03, 6.81, 0.60, 0.40)]}
for room, excl in zones.items():
    x0, x1, z0, z1 = rooms[room][:4]
    s.A(f'<rect x="{X(x0)+8:.1f}" y="{Y(z0)+8:.1f}" width="{(x1-x0)*S-16:.1f}" height="{(z1-z0)*S-16:.1f}" fill="url(#heat)" stroke="{RED}" stroke-width="4"/>')
    for (x, z, w, d) in excl:
        s.A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#FFFFFF" stroke="{RED}" stroke-width="2" stroke-dasharray="8 6"/>')
s.o[1] = s.o[1].replace('</defs>', f'<pattern id="heat" width="24" height="24" patternUnits="userSpaceOnUse"><rect width="24" height="24" fill="#FBE3DF"/><path d="M0,12 Q6,4 12,12 T24,12" fill="none" stroke="{RED}" stroke-width="2"/></pattern></defs>')
s.furniture(); s.walls(); s.numbers()
# sensors (in corrugated tube, between heating lines)
for (x, z) in ((4.6, 8.45), (1.05, 8.0)):
    s.A(f'<circle cx="{X(x):.1f}" cy="{Y(z):.1f}" r="14" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/><text x="{X(x)+22:.1f}" y="{Y(z)+10:.1f}" font-size="26" fill="{INK}">датчик</text>')
def thermo(cx, cy, s):
    s.A(f'<rect x="{cx-17:.1f}" y="{cy-17:.1f}" width="34" height="34" fill="#F4D03F" stroke="{INK}" stroke-width="2"/><text x="{cx:.1f}" y="{cy+8:.1f}" text-anchor="middle" font-size="20" font-weight="bold" fill="{INK}">t°</text>')
its = [dict(n="Т1", room="Коридор", wall="B", a=5.50, syms=[thermo], text="h=900 ванная"),
       dict(n="Т2", room="Коридор", wall="L", a=7.85, syms=[thermo], text="h=900 санузел")]
place(s, its, None)
for (cx, cz, t) in ((4.75, 9.3, "≈2,0 м²"), (0.9, 7.35, "≈2,5 м²")):
    s.A(f'<text x="{X(cx):.0f}" y="{Y(cz):.0f}" text-anchor="middle" font-size="30" font-weight="bold" fill="{RED}">{t}</text>')
s.explication("Экспликация", [("Нагревательный мат под плитку", lambda cx, cy: s.A(f'<rect x="{cx-22}" y="{cy-14}" width="44" height="28" fill="url(#heat)" stroke="{RED}" stroke-width="3"/>'), "2"),
    ("Терморегулятор, h=900", bound(thermo, s), 2), ("Датчик пола в гофре Ø16", lambda cx, cy: s.A(f'<circle cx="{cx}" cy="{cy}" r="13" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>'), 2),
    ("Без подогрева (под прибором)", lambda cx, cy: s.A(f'<rect x="{cx-22}" y="{cy-14}" width="44" height="28" fill="#FFFFFF" stroke="{RED}" stroke-width="2" stroke-dasharray="6 4"/>'), "")])
s.notes(["1. Тёплый пол — только ванная", "    и санузел. В комнатах, кухне,", "    коридоре — нет (есть отопление).", "2. Электрический мат 150 Вт/м²", "    под плитку, в клей.",
         "3. Не греть под ванной, унитазом,", "    биде, стиральной машиной.", "4. Терморегуляторы — снаружи,", "    в коридоре, h=900.", "5. Питание: отдельная группа", "    C16 + УЗО 30 мА, 3×2,5.",
         "6. Датчик — в гофре, чтобы", "    менять без вскрытия плитки."])
s.save("s7_pol")
print("done")

# =========================================================== 5а. Узлы санузла и ванной крупно
SHORT = {13: "бак 200 л", 3: "душ", 4: "раковина", 5: "биде", 6: "унитаз", 12: "бойлер Б2", 7: "стиралка", 8: "ванна", 9: "унитаз", 10: "гиг. душ", 11: "бойлер Б1", 14: "раковина"}
s = Sheet("Санузел и ванная — узлы сантехники", "5а"); FS = 1.6
regions = [("Санузел", 8, 0.20, 6.70, 1.95, 9.12, 600, 260, 360), ("Ванная", 7, 3.45, 7.92, 6.18, 9.62, 560, 1350, 520)]
for idx, (room, num, rx0, rz0, rx1, rz1, sc, px0, py0) in enumerate(regions):
    S = sc; OX = px0 - rx0 * sc; OY = py0 - rz0 * sc
    s.A(f'<clipPath id="cl{idx}"><rect x="{X(rx0):.0f}" y="{Y(rz0):.0f}" width="{(rx1-rx0)*S:.0f}" height="{(rz1-rz0)*S:.0f}"/></clipPath>')
    s.A(f'<g clip-path="url(#cl{idx})">'); s.furniture(); s.walls(); s.A('</g>')
    s.A(f'<rect x="{X(rx0):.0f}" y="{Y(rz0):.0f}" width="{(rx1-rx0)*S:.0f}" height="{(rz1-rz0)*S:.0f}" fill="none" stroke="#B8B2A8" stroke-width="2" stroke-dasharray="10 8"/>')
    s.A(f'<text x="{X(rx0):.0f}" y="{Y(rz0)-24:.0f}" font-size="44" font-weight="bold" fill="{INK}">{room} ({num})</text>')
    its = [dict(n=n, room=r_, wall=w_, a=a_, syms=sy, text=SHORT[n]) for (n, r_, w_, a_, sy, t) in PL if r_ == room]
    place(s, its, None)
    for (x, z, t) in ((0.67, 7.26, "трап"), (4.95, 9.16, "слив")):
        if rx0 <= x <= rx1 and rz0 <= z <= rz1:
            s.A(f'<rect x="{X(x)-18:.1f}" y="{Y(z)-18:.1f}" width="36" height="36" fill="#FFFFFF" stroke="{BROWN}" stroke-width="5"/><line x1="{X(x)-18:.1f}" y1="{Y(z):.1f}" x2="{X(x)+18:.1f}" y2="{Y(z):.1f}" stroke="{BROWN}" stroke-width="4"/><text x="{X(x)+28:.1f}" y="{Y(z)+10:.1f}" font-size="28" fill="{BROWN}">{t}</text>')
S, OX, OY = 168.0, 230, 300; FS = 1.0
s.explication("Выводы: высота от пола, мм", [(t[0].upper() + t[1:], None, "", n) for (n, room, wall, a, sy, t) in PL if room in ("Санузел", "Ванная")], colname="")
s.notes(["Х — холодная, Г — горячая,", "К — канализация.", "Красные размеры — от угла", "помещения до оси вывода.", "Пунктир — бойлеры (висят высоко).",
         "Унитазы и биде — подвесные,", "на инсталляции."])
s.save("s5a_uzly")
print("5a done")

# =========================================================== Развертки стен
PH = {1: [(CW, 550), (HW, 550), (KN, 500)], 2: [(CW, 450), (KN, 450)], 3: [(CW, 1100), (HW, 1100)], 4: [(CW, 550), (HW, 550), (KN, 500)],
      5: [(CW, 250), (HW, 250), (KN, 200)], 6: [(CW, 1000), (KN, 230)], 7: [(CW, 600), (KN, 600)], 8: [(CW, 800), (HW, 800)],
      9: [(CW, 1000), (KN, 230)], 10: [(CW, 700), (HW, 700)], 11: [(CW, 1750), (HW, 1750), (KN, 1700)],
      12: [(CW, 1750), (HW, 1750), (KN, 1700)], 13: [(CW, 300), (KN, 100)], 14: [(CW, 550), (HW, 550), (KN, 500)]}
FIX = {   # 13.11.2026: по согласованной расстановке
 ("Санузел", "B"): [(0.309, 1.836, 0, 1.12, "", "inst"), (0.53, 0.89, 0.30, 0.42, "биде", "wc"), (1.25, 1.61, 0.30, 0.42, "унитаз", "wc"), (0.40, 1.75, 1.70, 2.65, "шкаф: бойлер Б2 80 л", "boiler")],
 ("Санузел", "L"): [(6.82, 7.71, 0, 2.0, "душ", "glass"), (7.74, 8.26, 0, 2.65, "бак 200 л (заказ)", "tank")],
 ("Санузел", "T"): [(0.33, 1.02, 0, 2.0, "душ", "glass"), (1.058, 1.558, 0.80, 0.85, "раковина", "fix"), (1.08, 1.54, 1.20, 2.05, "зеркало", "mirror")],
 ("Санузел", "R"): [(7.0, 7.8, 0, 2.1, "дверь (наружу)", "door"), (7.84, 8.24, 0.85, 1.65, "сушитель", "fix")],
 ("Ванная", "T"): [(4.255, 5.055, 0, 2.1, "дверь", "door"), (5.10, 5.50, 0.85, 1.65, "сушитель", "fix")],
 ("Ванная", "L"): [(8.06, 8.66, 0.80, 0.85, "раковина", "fix"), (8.08, 8.64, 1.25, 2.10, "зеркало", "mirror"), (8.86, 9.46, 0, 0.85, "стиралка 10 кг", "fix")],
 ("Ванная", "B"): [(4.773, 6.073, 0, 0.58, "ванна 1300", "fix"), (4.89, 5.41, 1.10, 1.40, "ниша", "fix")],
 ("Ванная", "R"): [(8.08, 8.78, 0, 1.12, "", "inst"), (8.235, 8.595, 0.30, 0.42, "унитаз", "wc"), (8.06, 8.78, 1.70, 2.65, "шкаф: бойлер Б1", "boiler"), (8.809, 9.509, 0, 0.58, "ванна", "fix")],
 ("Кухня", "R"): [(1.909, 3.6, 0.9, 1.5, "фартук", "splash"), (1.909, 3.6, 0, 0.9, "плита · ПММ · мойка", "fix"), (1.96, 2.46, 0.9, 0.94, "", "fix"), (3.03, 3.53, 0.86, 0.9, "", "fix"), (1.909, 3.6, 1.5, 2.65, "верхние шкафы, вытяжка", "fix"), (3.6, 4.2, 0, 2.65, "холодильник", "fix")],
 ("Кухня", "B"): [(11.8, 12.4, 0, 2.65, "колонна СВЧ", "fix"), (12.4, 13.0, 0, 2.65, "холод.", "fix")],
 ("Кухня", "T"): [(9.145, 11.0, 0, 0.45, "банкетка", "fix"), (11.036, 12.636, 0.9, 2.4, "окно", "window"), (12.4, 13.0, 0, 0.9, "плита", "fix")],
 ("Кухня", "L"): [(1.909, 3.509, 0, 0.45, "банкетка", "fix"), (1.95, 3.05, 2.24, 2.54, "К4", "fix")],
}

WALLNAME = {"T": "верхняя", "B": "нижняя", "L": "левая", "R": "правая"}
ORN = ("M0,0.16 C0.28,0.04 0.5,0.22 0.38,0.38 C0.3,0.48 0.16,0.38 0.24,0.3 "
       "M0.16,0 C0.04,0.28 0.22,0.5 0.38,0.38 "
       "M0.38,0.38 Q0.62,0.3 0.86,0.1 Q0.7,0.28 0.6,0.3 "
       "M0.38,0.38 Q0.3,0.62 0.1,0.86 Q0.28,0.7 0.3,0.6 "
       "M0.5,0.18 Q0.6,0.12 0.66,0.04 M0.18,0.5 Q0.12,0.6 0.04,0.66")
def orn_corner(A, x, y, dx, dy, size, col, sw=1.6):
    """Лепной уголок-акант (условно): завиток + листья, внутрь рамки."""
    A(f'<g transform="translate({x:.1f},{y:.1f}) scale({dx*size:.2f},{dy*size:.2f})"><path d="{ORN}" fill="none" stroke="{col}" stroke-width="{sw}" vector-effect="non-scaling-stroke"/>'
      f'<circle cx="0.13" cy="0.13" r="0.06" fill="none" stroke="{col}" stroke-width="{sw}" vector-effect="non-scaling-stroke"/></g>')

def elevation(s, room, wall, px0, py0, sc, title, wet):
    x0, x1, z0, z1 = rooms[room][:4]
    Lw = (x1 - x0) if wall in "TB" else (z1 - z0)
    U = {"T": lambda a: a - x0, "B": lambda a: x1 - a, "L": lambda a: z1 - a, "R": lambda a: a - z0}[wall]
    PX = lambda u: px0 + u * sc; PY = lambda h: py0 + (2.7 - h) * sc
    A = s.A
    A(f'<rect x="{PX(0):.1f}" y="{PY(2.7):.1f}" width="{Lw*sc:.1f}" height="{2.7*sc:.1f}" fill="{"url(#tile)" if wet is True else (wet or "#FFFFFF")}" stroke="{INK}" stroke-width="4"/>')
    A(f'<line x1="{PX(0)-20:.1f}" y1="{PY(0):.1f}" x2="{PX(Lw)+20:.1f}" y2="{PY(0):.1f}" stroke="{INK}" stroke-width="7"/>')
    st = {"inst": ("none", "#8A8478", "10 6"), "wc": ("#FFFFFF", INK, ""), "boiler": ("#FBE3DF", "#B03A2E", "14 8"), "glass": ("#E7F1F6", "#5C8AA8", ""),
          "fix": ("#F3EFE7", "#6B665C", ""), "mirror": ("#EEF3F5", "#8AA0AA", ""), "tank": ("#E3EEF8", BLUE, ""), "door": ("#FFFFFF", INK, ""),
          "window": ("#FFFFFF", INK, ""), "splash": ("#E8DDD0", "#B8AA9C", ""),
          "molding": ("none", "#A08C68", ""), "wood": ("#9C7B5C", "#6E5440", ""), "low": ("#F3EFE7", "#6B665C", ""), "cornice": ("#F7F4EE", "#A08C68", ""), "tv": ("#2B2A27", INK, "")}
    for (a0, a1, h0, h1, lab, kind) in FIX.get((room, wall), []):
        u0, u1 = sorted((U(a0), U(a1)))
        f, c, d = st[kind]
        A(f'<rect x="{PX(u0):.1f}" y="{PY(h1):.1f}" width="{(u1-u0)*sc:.1f}" height="{(h1-h0)*sc:.1f}" fill="{f}" stroke="{c}" stroke-width="3"{f" stroke-dasharray={chr(34)}{d}{chr(34)}" if d else ""}/>')
        if kind == "molding" and (u1 - u0) > 0.3 and (h1 - h0) > 0.3:   # профиль (2-я линия) + лепные уголки во всех углах
            q = 0.03
            A(f'<rect x="{PX(u0+q):.1f}" y="{PY(h1-q):.1f}" width="{(u1-u0-2*q)*sc:.1f}" height="{(h1-h0-2*q)*sc:.1f}" fill="none" stroke="{c}" stroke-width="1.5"/>')
            for (cu, ch, dx, dy) in ((u0, h1, 1, 1), (u1, h1, -1, 1), (u0, h0, 1, -1), (u1, h0, -1, -1)):
                orn_corner(A, PX(cu), PY(ch), dx, dy, 0.15 * sc, c)
        if kind == "door":
            A(f'<line x1="{PX(u0):.1f}" y1="{PY(h1):.1f}" x2="{PX(u1):.1f}" y2="{PY(h0):.1f}" stroke="{INK}" stroke-width="2"/><line x1="{PX(u1):.1f}" y1="{PY(h1):.1f}" x2="{PX(u0):.1f}" y2="{PY(h0):.1f}" stroke="{INK}" stroke-width="2"/>')
        if lab:
            A(f'<text x="{PX((u0+u1)/2):.0f}" y="{PY((h0+h1)/2)+10:.0f}" text-anchor="middle" font-size="26" fill="{c if kind not in ("fix","splash") else INK}">{lab}</text>')
    pts = []   # (u, [(h, syms)], label)
    for (n, r_, w_, a, kind, h, what, cnt) in SK:
        if r_ == room and w_ == wall:
            pts.append((U(a), [(h, [sock_sym(kind)] * min(cnt, 2))], f"{n} — {what[0].lower() + what[1:]}, h={h}"))
    for (n, r_, w_, a, sy, t) in PL:
        if r_ == room and w_ == wall:
            byh = {}
            for sym, h in PH[n]: byh.setdefault(h, []).append(sym)
            pts.append((U(a), sorted(byh.items(), reverse=True), f"{n} — {t}"))
    us = set(); calls = []
    for (u, hs, lab) in pts:
        top = None
        for h, syms in hs:
            k = len(syms); w = 36
            for i, fn in enumerate(syms): fn(PX(u) - (k - 1) * w / 2 + i * w, PY(h / 1000), s)
            if top is None: top = (PX(u) + (k - 1) * w / 2 + 18, PY(h / 1000))
        calls.append((top[1], top[0], lab)); us.add(round(u, 3))
    calls.sort()
    cx = PX(Lw) + 70; slot = PY(2.6)
    for (y, x, lab) in calls:
        ty = max(slot, y)
        A(f'<polyline points="{x:.0f},{y:.0f} {cx-14:.0f},{ty:.0f}" fill="none" stroke="#8A8478" stroke-width="2"/>')
        A(f'<text x="{cx:.0f}" y="{ty+9:.0f}" font-size="25" fill="{INK}">{lab}</text>')
        slot = ty + 40
    # chain under the floor
    seq = [0.0] + sorted(us) + [Lw]
    yy = PY(0) + 50
    A(f'<line x1="{PX(0):.1f}" y1="{yy:.1f}" x2="{PX(Lw):.1f}" y2="{yy:.1f}" stroke="{RED}" stroke-width="2.5"/>')
    for v in seq: s.tick(PX(v), yy)
    for a_, b_ in zip(seq, seq[1:]):
        mm = round((b_ - a_) * 1000 / 5) * 5
        if mm > 0: s.dtext((PX(a_) + PX(b_)) / 2, yy - 10, f"{mm:,}".replace(",", " "), False)
    yy2 = yy + 56
    A(f'<line x1="{PX(0):.1f}" y1="{yy2:.1f}" x2="{PX(Lw):.1f}" y2="{yy2:.1f}" stroke="{RED}" stroke-width="2.5"/>'); s.tick(PX(0), yy2); s.tick(PX(Lw), yy2)
    s.dtext((PX(0) + PX(Lw)) / 2, yy2 - 10, f"{round(Lw*1000/5)*5:,}".replace(",", " "), False)
    lx = PX(0) - 40
    A(f'<line x1="{lx:.1f}" y1="{PY(0):.1f}" x2="{lx:.1f}" y2="{PY(2.7):.1f}" stroke="{RED}" stroke-width="2.5"/>'); s.tick(lx, PY(0)); s.tick(lx, PY(2.7))
    s.dtext(lx - 12, (PY(0) + PY(2.7)) / 2, "2 700", True)
    A(f'<text x="{PX(0):.0f}" y="{PY(2.7)-26:.0f}" font-size="34" font-weight="bold" fill="{INK}">{title}</text>')

def elev_sheet(title, no, room, walls, wet, fname, notes):
    s = Sheet(title, no)
    s.o[1] = s.o[1].replace('</defs>', '<pattern id="tile" width="30" height="30" patternUnits="userSpaceOnUse"><rect width="30" height="30" fill="#F6F2EC"/><path d="M30,0 V30 H0" fill="none" stroke="#DDD5CA" stroke-width="2"/></pattern></defs>')
    cells = [(260, 330), (1640, 330), (260, 1210), (1640, 1210)]
    rows = []
    for i, (wall, name) in enumerate(walls):
        x0, x1, z0, z1 = rooms[room][:4]
        Lw = (x1 - x0) if wall in "TB" else (z1 - z0)
        sc = min(250, 800 / Lw)
        elevation(s, room, wall, cells[i][0], cells[i][1], sc, f"Вид {i+1} — {name}", wet)
        rows.append((f"Вид {i+1}: {WALLNAME[wall]} стена по плану", None, "", i + 1))
    s.explication("Развертки", rows, colname="")
    s.notes(notes)
    s.save(fname)

WETN = ["1. Вид — стоя в помещении лицом", "    к стене; слева — левый угол.", "2. Красные размеры: снизу — от", "    левого угла до оси точки, мм;", "    h — от чистого пола.",
        "3. Плитка — на всю высоту 2700.", "4. Пунктир серый — рама", "    инсталляции 1120 мм.", "5. Пунктир красный — бойлер.", "6. Размеры ±1–3 см, уточнить", "    по замеру."]
elev_sheet("Развертки стен санузла", "8", "Санузел", [("L", "душ, бак 200 л"), ("B", "биде, унитаз, бойлер"), ("T", "душ, раковина"), ("R", "дверь, сушитель")], True, "s8_razv_su", WETN)
elev_sheet("Развертки стен ванной", "9", "Ванная", [("T", "дверь, сушитель"), ("L", "раковина, стиралка"), ("B", "ванна 1300"), ("R", "унитаз, бойлер")], True, "s9_razv_van", WETN)
elev_sheet("Развертки стен кухни", "10", "Кухня", [("R", "плита, ПММ, мойка, холодильник"), ("B", "колонна СВЧ"), ("T", "банкетка, окно"), ("L", "банкетка, кондиционер")], False,
           "s10_razv_kuh", ["1. Вид — лицом к стене; слева —", "    левый угол.", "2. Столешница h=900, фартук", "    900–1500, верхние до 2200.", "3. Розетки над столешницей h=1100,", "    не над мойкой и плитой.",
                            "4. Вытяжка — в вент. отверстие", "    перекрытия.", "5. Размеры ±1–3 см, уточнить", "    по замеру."])
print("razv done")

# =========================================================== 11. Кухня: оборудование
KX0, KX1, KZ0, KZ1 = rooms["Кухня"][:4]
s = Sheet("План кухни — мебель и техника", 11)
S = 300.0; OX = 380 - KX0 * S; OY = 320 - KZ0 * S
s.A(f'<clipPath id="ck"><rect x="{X(KX0-0.3):.0f}" y="{Y(KZ0-0.3):.0f}" width="{(KX1-KX0+0.6)*S:.0f}" height="{(KZ1-KZ0+0.45)*S:.0f}"/></clipPath>')
s.A('<g clip-path="url(#ck)">'); s.walls(); s.A('</g>')
FILL = {"col": "#EFE8DC", "low": "#CDBBA8", "up": "none", "bench": "#D8C2A6", "tab": "#E3D3BE", "ch": "#F1EADF"}
RX0 = KX1 - 0.6; FZ0 = KZ1 - 0.6; LZ1 = FZ0
TCX, TCZ = KX0 + 1.2, KZ0 + 0.975
ITEMS = [
 (1, RX0, FZ0, 0.6, 0.6, "col", "Холодильник встроенный 600"),
 (2, RX0 - 0.6, FZ0, 0.6, 0.6, "col", "Колонна: СВЧ + кладовая"),
 (3, RX0, KZ0, 0.6, 0.6, "low", "Плита-индукция + духовка под ней"),
 (4, RX0, KZ0 + 0.6, 0.6, 0.45, "low", "Посудомойка 450"),
 (5, RX0, KZ0 + 1.05, 0.6, LZ1 - KZ0 - 1.05, "low", "Мойка + шкаф под ней"),
 (6, KX1 - 0.35, KZ0, 0.35, LZ1 - KZ0, "up", "Верхние шкафы с полками"),
 (7, KX1 - 0.35, KZ0, 0.35, 0.6, "up", "Вытяжка в шкафу"),
 (8, KX0, KZ0, 0.5, 1.6, "bench", "Угловая банкетка с ящиками"),
 (9, TCX - 0.65, TCZ - 0.425, 1.3, 0.85, "tab", "Стол 1300×850 на опоре"),
 (10, TCX + 0.65 + 0.01, TCZ - 0.46, 0.44, 0.92, "ch", "Стулья — 2 шт."),
 (11, TCX - 0.4, TCZ + 0.445, 0.4, 0.4, "ch", "Детский стульчик"),
]
MPOS = {3: (RX0 + 0.12, KZ0 + 0.3), 7: (KX1 - 0.17, KZ0 + 0.3), 6: (KX1 - 0.17, KZ0 + 1.1), 4: (RX0 + 0.12, KZ0 + 0.82), 5: (RX0 + 0.12, KZ0 + 1.3)}
s.A(f'<rect x="{X(KX0+0.5):.1f}" y="{Y(KZ0):.1f}" width="{(11.0-KX0-0.5)*S:.1f}" height="{0.48*S:.1f}" fill="{FILL["bench"]}" stroke="{INK}" stroke-width="3"/>')
for (n, x, z, w, d, k, t) in ITEMS:
    dash = k == "up"
    s.A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="{FILL[k]}" stroke="{INK}" stroke-width="{4 if dash else 3}"{" stroke-dasharray=" + chr(34) + "16 10" + chr(34) if dash else ""}/>')
for (cx, cz, r) in ((RX0 + 0.3, KZ0 + 0.15, 0.08), (RX0 + 0.5, KZ0 + 0.15, 0.07), (RX0 + 0.3, KZ0 + 0.43, 0.07), (RX0 + 0.5, KZ0 + 0.43, 0.08)):
    s.A(f'<circle cx="{X(cx):.0f}" cy="{Y(cz):.0f}" r="{r*S:.0f}" fill="none" stroke="#6B665C" stroke-width="3"/>')
s.A(f'<rect x="{X(RX0+0.2):.0f}" y="{Y(KZ0+1.1):.0f}" width="{0.34*S:.0f}" height="{0.46*S:.0f}" rx="18" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>')
for (n, x, z, w, d, k, t) in ITEMS:
    cx, cz = MPOS.get(n, (x + w / 2, z + d / 2))
    s.A(f'<circle cx="{X(cx):.0f}" cy="{Y(cz):.0f}" r="28" fill="#FFFFFF" stroke="{RED}" stroke-width="4"/><text x="{X(cx):.0f}" y="{Y(cz)+11:.0f}" text-anchor="middle" font-size="30" font-weight="bold" fill="{RED}">{n}</text>')
# проход
s.A(f'<line x1="{X(TCX+0.65+0.45):.0f}" y1="{Y(KZ0+1.2):.0f}" x2="{X(RX0):.0f}" y2="{Y(KZ0+1.2):.0f}" stroke="{GREEN}" stroke-width="3" marker-end="url(#arr)"/>')
s.A(f'<text x="{(X(TCX+1.1)+X(RX0))/2:.0f}" y="{Y(KZ0+1.2)-14:.0f}" text-anchor="middle" font-size="26" fill="{GREEN}">проход ≥900</text>')
def hd(x0, x1, y, t):
    s.A(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{RED}" stroke-width="2.5"/>'); s.tick(x0, y); s.tick(x1, y)
    s.dtext((x0 + x1) / 2, y - 12, t, False)
def vd(y0, y1, x, t):
    s.A(f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="{RED}" stroke-width="2.5"/>'); s.tick(x, y0); s.tick(x, y1)
    s.dtext(x - 14, (y0 + y1) / 2, t, True)
mm = lambda v: f"{round(v*1000):,}".replace(",", " ")
yb = Y(KZ1) + 120
hd(X(KX0), X(RX0 - 0.6), yb, mm(RX0 - 0.6 - KX0)); hd(X(RX0 - 0.6), X(RX0), yb, "600"); hd(X(RX0), X(KX1), yb, "600")
hd(X(KX0), X(KX1), yb + 60, mm(KX1 - KX0))
xr = X(KX1) + 150
for (a_, b_) in ((0, 0.6), (0.6, 1.05), (1.05, LZ1 - KZ0), (LZ1 - KZ0, KZ1 - KZ0)):
    vd(Y(KZ0 + a_), Y(KZ0 + b_), xr, mm(b_ - a_))
vd(Y(KZ0), Y(KZ1), xr + 60, mm(KZ1 - KZ0))
s.A(f'<text x="{X(KX0+0.4):.0f}" y="{Y(KZ1)+70:.0f}" text-anchor="middle" font-size="30" fill="{INK}">вход</text>')
E = 250.0
def elev(x0, ybase, length, title):
    s.A(f'<rect x="{x0:.0f}" y="{ybase-2.7*E:.0f}" width="{length*E:.0f}" height="{2.7*E:.0f}" fill="none" stroke="{INK}" stroke-width="4"/>')
    s.A(f'<line x1="{x0-20:.0f}" y1="{ybase:.0f}" x2="{x0+length*E+20:.0f}" y2="{ybase:.0f}" stroke="{INK}" stroke-width="7"/>')
    s.A(f'<text x="{x0:.0f}" y="{ybase-2.7*E-24:.0f}" font-size="34" font-weight="bold" fill="{INK}">{title}</text>')
def er(x0, ybase, u0, u1, h0, h1, fill, label=None, num=None, fs=24, tcol=INK):
    s.A(f'<rect x="{x0+u0*E:.1f}" y="{ybase-h1*E:.1f}" width="{(u1-u0)*E:.1f}" height="{(h1-h0)*E:.1f}" fill="{fill}" stroke="{INK}" stroke-width="3"/>')
    cx, cy = x0 + (u0 + u1) / 2 * E, ybase - (h0 + h1) / 2 * E
    if label: s.A(f'<text x="{cx:.0f}" y="{cy+9:.0f}" text-anchor="middle" font-size="{fs}" fill="{tcol}">{label}</text>')
    if num: s.A(f'<circle cx="{cx:.0f}" cy="{cy-(34 if label else 0):.0f}" r="24" fill="#FFFFFF" stroke="{RED}" stroke-width="4"/><text x="{cx:.0f}" y="{cy-(34 if label else 0)+10:.0f}" text-anchor="middle" font-size="26" font-weight="bold" fill="{RED}">{num}</text>')
L = KZ1 - KZ0; Lr = LZ1 - KZ0
xa, yb2 = 300, 2040
elev(xa, yb2, L, "Вид А — правая стена")
er(xa, yb2, 0, Lr, 0.9, 1.55, "#E8DDCF", "фартук керамогранит", fs=22)
for (a_, b_, n) in ((0, 0.6, 3), (0.6, 1.05, 4), (1.05, Lr, 5)):
    er(xa, yb2, a_, b_, 0.1, 0.86, "#CDBBA8", None, n)
er(xa, yb2, 0.03, 0.57, 0.12, 0.72, "#3A3833", "духовка", None, tcol="#FFFFFF", fs=20)
er(xa, yb2, 0, Lr, 0.0, 0.1, "#3A3833"); er(xa, yb2, 0, Lr, 0.86, 0.9, "#D8C8B2")
for (a_, b_, n) in ((0, 0.6, 7), (0.6, 1.15, 6), (1.15, Lr, None)):
    er(xa, yb2, a_, b_, 1.55, 2.7, "#EFE8DC", None, n)
er(xa, yb2, Lr, L, 0, 2.7, "#EFE8DC", "холодил.", 1, fs=20)
for (h, t) in ((0.86, "860"), (1.55, "1550"), (2.7, "2700")):
    s.A(f'<text x="{xa+L*E+18:.0f}" y="{yb2-h*E+9:.0f}" font-size="24" fill="{RED}">{t}</text>')
Lb = KX1 - KX0
xb = 300 + L * E + 520
elev(xb, yb2 - 0, 1.2 + 0.4, "Вид Б — колонны (у входа)")
er(xb, yb2, 0.0, 0.6, 0, 2.7, "#EFE8DC", "холодил.", 1, fs=20)
er(xb, yb2, 0.6, 1.2, 0, 2.7, "#EFE8DC", None, 2)
er(xb, yb2, 0.65, 1.15, 1.35, 1.73, "#3A3833", "СВЧ", None, tcol="#FFFFFF", fs=20)
for h in (0.4, 0.8, 2.1, 2.4):
    s.A(f'<line x1="{xb+0.62*E:.0f}" y1="{yb2-h*E:.0f}" x2="{xb+1.18*E:.0f}" y2="{yb2-h*E:.0f}" stroke="#8A8478" stroke-width="2" stroke-dasharray="10 6"/>')
for (h, t) in ((1.35, "1350"), (1.73, "1730"), (2.7, "2700")):
    s.A(f'<text x="{xb+1.6*E+18:.0f}" y="{yb2-h*E+9:.0f}" font-size="24" fill="{RED}">{t}</text>')
S, OX, OY = 168.0, 230, 300
s.explication("Мебель и техника", [(t, None, "", n) for (n, x, z, w, d, k, t) in ITEMS], colname="")
s.notes(["Порядок работы: холодильник →", "мойка → плита (у окна).", "Духовка под плитой, СВЧ в колонне.", "Проход перед кухней ≥ 900 мм.",
         "Верхние шкафы и колонны —", "до потолка 2700.", "Фасады без ручек (гола-профиль).", "Размеры ±1–3 см, уточнить", "по замеру."])
s.save("s11_kuhnya")
print("kitchen sheet done")

# =========================================================== Замерный лист
s = Sheet("Замерный лист — что проверить рулеткой", "—")
s.walls(); s.numbers(names=True)
MEAS = [  # буква, комната, ориентация, координата линии, a0, a1, примечание
 ("А", "Кухня", "h", 2.10, 9.145, 13.0, "ширина кухни вдоль окна (эскиз 3860 / застр. 4200)"),
 ("Б", "Кухня", "v", 9.40, 1.909, 4.2, "глубина кухни: окно → стена спальни (2290 / 2930)"),
 ("В", "Спальня 2", "h", 6.95, 10.072, 14.745, "ширина спальни 2 (4670 / 4790)"),
 ("Г", "Спальня 2", "v", 14.45, 4.327, 7.491, "глубина спальни 2 (3160 / 3400)"),
 ("Д", "Спальня 2", "v", 10.30, 4.327, 6.6, "левая стена спальни: угол → дверь (под шкаф)"),
 ("Е", "Санузел", "h", 7.15, 0.309, 1.836, "ширина санузла"),
 ("Ж", "Санузел", "v", 0.55, 6.8, 9.018, "длина санузла"),
 ("З", "Ванная", "h", 8.75, 3.564, 6.073, "длина ванной"),
 ("И", "Ванная", "v", 5.30, 8.018, 9.509, "ширина ванной"),
 ("К", "Коридор", "h", 7.25, 1.945, 9.945, "длина коридора"),
 ("Л", "Коридор", "v", 6.10, 6.672, 7.909, "ширина коридора"),
 ("М", "Прихожая", "h", 9.0, 1.945, 3.455, "ширина прихожей"),
 ("Н", "Гостиная", "h", 1.0, 1.946, 5.545, "ширина гостиной (3600)"),
 ("О", "Гостиная", "v", 2.3, 0.309, 6.545, "длина гостиной (6250)"),
 ("П", "Комната", "h", 1.0, 5.745, 8.945, "ширина комнаты (3190)"),
]
for (L, room, o, c, a0, a1, note) in MEAS:
    if o == "h":
        y = Y(c)
        s.A(f'<line x1="{X(a0):.1f}" y1="{y:.1f}" x2="{X(a1):.1f}" y2="{y:.1f}" stroke="{BLUE}" stroke-width="4"/>'); s.tick(X(a0), y); s.tick(X(a1), y)
        fr = {"К": 0.22, "З": 0.28, "В": 0.7}.get(L, 0.5)
        cx, cy = X(a0) + (X(a1) - X(a0)) * fr, y
    else:
        x = X(c)
        s.A(f'<line x1="{x:.1f}" y1="{Y(a0):.1f}" x2="{x:.1f}" y2="{Y(a1):.1f}" stroke="{BLUE}" stroke-width="4"/>'); s.tick(x, Y(a0)); s.tick(x, Y(a1))
        cx, cy = x, (Y(a0) + Y(a1)) / 2
    s.A(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="30" fill="{BLUE}"/><text x="{cx:.0f}" y="{cy+12:.0f}" text-anchor="middle" font-size="34" font-weight="bold" fill="#FFFFFF">{L}</text>')
# таблица справа
cx0, cx1 = SX, W - 40
s.A(f'<text x="{(cx0+cx1)/2:.0f}" y="{130}" text-anchor="middle" font-size="40" fill="{INK}">Размеры, мм</text>')
ty = 170
s.A(f'<line x1="{cx0}" y1="{ty}" x2="{cx1}" y2="{ty}" stroke="{INK}" stroke-width="2"/>')
s.A(f'<text x="{cx0+20}" y="{ty+40}" font-size="26" fill="{INK}">Букв.</text><text x="{cx0+130}" y="{ty+40}" font-size="26" fill="{INK}">чертёж</text><text x="{cx0+290}" y="{ty+40}" font-size="26" fill="{INK}">замер</text>')
ty += 60
for (L, room, o, c, a0, a1, note) in MEAS:
    s.A(f'<line x1="{cx0}" y1="{ty}" x2="{cx1}" y2="{ty}" stroke="{INK}" stroke-width="2"/>')
    s.A(f'<text x="{cx0+40}" y="{ty+46}" text-anchor="middle" font-size="30" font-weight="bold" fill="{BLUE}">{L}</text>')
    s.A(f'<text x="{cx0+130}" y="{ty+46}" font-size="28" fill="{INK}">{round((a1-a0)*1000):,}</text>'.replace(",", " "))
    s.A(f'<rect x="{cx0+280}" y="{ty+12}" width="180" height="46" fill="#FFFFFF" stroke="#8A8478" stroke-width="2"/>')
    ty += 70
s.A(f'<line x1="{cx0}" y1="{ty}" x2="{cx1}" y2="{ty}" stroke="{INK}" stroke-width="2"/>')
for xx in (cx0 + 100, cx0 + 270):
    s.A(f'<line x1="{xx}" y1="170" x2="{xx}" y2="{ty}" stroke="{INK}" stroke-width="2"/>')
ty += 50
for i, t in enumerate(["Мерить по полу, от стены до стены,", "в двух местах; писать меньшее.", "Ещё: высота потолка, ширина", "каждой двери, где стояки Т1–Т3.", "Д — главное для шкафа в спальне 2.", "А и Б — для кухни (8,8 или 14 м²?)."]):
    s.A(f'<text x="{cx0+20}" y="{ty+i*44}" font-size="27" fill="{INK}">{t}</text>')
s.save("sZ_zamer")
print("zamer done")
