import json, math
G = {"walls": [[1.655, 0.0, 1.018, 0.309], [4.836, 0.0, 1.436, 0.309], [8.436, 0.0, 0.836, 0.309], [10.327, 0.0, 0.436, 0.309], [1.655, 0.309, 0.291, 6.491], [5.545, 0.309, 0.2, 6.364], [8.945, 0.309, 0.2, 0.236], [10.455, 0.309, 0.309, 1.6], [8.945, 1.345, 0.2, 5.327], [10.764, 1.6, 0.273, 0.309], [12.636, 1.6, 0.673, 0.309], [9.145, 1.818, 1.309, 0.091], [13.0, 1.909, 0.309, 2.418], [13.309, 2.018, 1.745, 0.309], [13.309, 2.327, 0.436, 2.0], [14.745, 2.327, 0.309, 0.236], [14.745, 3.327, 0.309, 2.291], [13.745, 3.545, 0.145, 0.091], [14.618, 3.545, 0.127, 0.091], [9.945, 4.2, 3.055, 0.127], [9.945, 4.327, 0.127, 2.273], [9.145, 5.745, 0.009, 0.8], [9.155, 5.755, 0.027, 0.791], [0.0, 6.509, 1.091, 0.291], [1.564, 6.509, 0.091, 0.291], [1.091, 6.545, 0.473, 0.255], [1.945, 6.545, 0.2, 0.127], [2.945, 6.545, 2.6, 0.127], [5.745, 6.545, 2.4, 0.127], [0.0, 6.8, 0.309, 2.527], [1.836, 6.8, 0.109, 0.2], [14.745, 7.182, 0.309, 0.6], [9.945, 7.4, 0.127, 1.218], [10.073, 7.491, 4.673, 0.291], [1.836, 7.8, 0.109, 2.0], [3.455, 7.909, 0.8, 0.109], [5.055, 7.909, 1.309, 0.109], [3.455, 8.018, 0.109, 1.782], [6.073, 8.018, 0.291, 1.782], [6.364, 8.418, 1.836, 0.091], [8.964, 8.418, 0.982, 0.091], [6.364, 8.509, 0.036, 0.109], [9.909, 8.509, 0.036, 0.109], [6.4, 8.527, 1.8, 0.091], [8.964, 8.527, 0.945, 0.091], [0.309, 9.018, 1.527, 0.309], [1.655, 9.327, 0.182, 0.473], [1.945, 9.509, 0.309, 0.291], [3.145, 9.509, 0.309, 0.291], [3.564, 9.509, 2.509, 0.291], [8.1818, 8.4727, 0.7818, 0.2364]],
     "windows": [[2.673, 0.018, 2.164, 0.273], [6.273, 0.018, 2.164, 0.273], [9.273, 0.018, 1.055, 0.273], [11.036, 1.618, 1.6, 0.273], [14.764, 2.564, 0.273, 0.764], [14.764, 5.618, 0.273, 1.564]]}
P = 55.0
S = 172.0          # px per metre
OX, OY = 150, 330  # plan origin on canvas
X = lambda m: OX + m * S
Y = lambda m: OY + m * S
def r(l, t, w, d):  # plan-px rect -> metres
    return (l / P, t / P, w / P, d / P)

INK = "#1E1D1A"; MUTED = "#8A8478"; FURN = "#B9B1A4"; BG = "#F3F0E8"
RED = "#C0392B"; BLUE = "#1F5FA8"; GREEN = "#2E7D4F"; ORANGE = "#C27A12"
out = []
A = out.append
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2160" viewBox="0 0 3840 2160" font-family="DejaVu Sans">')
A(f'<rect width="3840" height="2160" fill="{BG}"/>')

# furniture (thin outlines) — taken from the 3D model
furn = [
 r(166,327,136,33), r(316,327,128,33), r(554,238,33,120), r(160,462,30,58), r(350,436,197,26), r(107,460,16,60),  # wardrobes, shoe
 r(503,105,34,34), r(537,105,80,33), r(552,198,33,33), r(585,198,97,33), r(682,105,33,126),                   # kitchen
 r(255,129,50,121), r(442,129,50,121), r(640,239,121,50),                                                          # sofas / bed
 r(109,150,14,78), r(318,150,14,78), r(662,398,78,14),                                                             # TV consoles
 r(199,452,33,33), r(200,489,83,30), r(288,496,18,24),                                                             # bath room
 r(18,375,38,49),                                                                                                  # shower
]
for (x, z, w, d) in furn:
    A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="none" stroke="{FURN}" stroke-width="3"/>')
# hob & sink symbols
A(f'<rect x="{X(686/P):.1f}" y="{Y(112/P):.1f}" width="{25/P*S:.1f}" height="{32/P*S:.1f}" fill="none" stroke="{FURN}" stroke-width="3"/>')
for cy in (122, 136):
    A(f'<circle cx="{X(698.5/P):.1f}" cy="{Y(cy/P):.1f}" r="16" fill="none" stroke="{FURN}" stroke-width="3"/>')
A(f'<rect x="{X(686/P):.1f}" y="{Y(180/P):.1f}" width="{25/P*S:.1f}" height="{30/P*S:.1f}" rx="10" fill="none" stroke="{FURN}" stroke-width="3"/>')
# washer circle
A(f'<circle cx="{X(215.5/P):.1f}" cy="{Y(468.5/P):.1f}" r="38" fill="none" stroke="{FURN}" stroke-width="3"/>')
# --- санузел: new layout, bidet + toilet on the bottom wall, compact sink on the left wall
def toilet(ax, wallz, w=0.36, d=0.55, col=FURN, sw=3):
    x0 = ax - w / 2
    A(f'<rect x="{X(x0):.1f}" y="{Y(wallz-0.16):.1f}" width="{w*S:.1f}" height="{0.16*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    A(f'<ellipse cx="{X(ax):.1f}" cy="{Y(wallz-0.16-(d-0.16)/2):.1f}" rx="{w/2*S:.1f}" ry="{(d-0.16)/2*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
toilet(1.43, 9.018)
toilet(0.71, 9.018, col=ORANGE, sw=5)  # bidet
A(f'<ellipse cx="{X(0.71):.1f}" cy="{Y(9.018-0.16-0.195):.1f}" rx="10" ry="10" fill="{ORANGE}"/>')
A(f'<rect x="{X(0.309):.1f}" y="{Y(7.85):.1f}" width="{0.32*S:.1f}" height="{0.45*S:.1f}" rx="10" fill="none" stroke="{FURN}" stroke-width="3"/>')  # sink
toilet(5.40, 9.509)  # ванная WC kept

# windows
for (x, z, w, d) in G["windows"]:
    A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>')
    if w > d:
        A(f'<line x1="{X(x):.1f}" y1="{Y(z+d/2):.1f}" x2="{X(x+w):.1f}" y2="{Y(z+d/2):.1f}" stroke="{INK}" stroke-width="2"/>')
    else:
        A(f'<line x1="{X(x+w/2):.1f}" y1="{Y(z):.1f}" x2="{X(x+w/2):.1f}" y2="{Y(z+d):.1f}" stroke="{INK}" stroke-width="2"/>')
# walls
for (x, z, w, d) in G["walls"]:
    A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#3A3833"/>')

# rooms
rooms = {
 "Гостиная":  (1.946, 5.545, 0.309, 6.545, "22,5 м²", 3.75, 1.2),
 "Комната":   (5.745, 8.945, 0.309, 6.545, "19,9 м²", 7.35, 1.2),
 "Кухня":     (9.145, 13.0, 1.909, 4.2,  "14,0 м²", 10.6, 3.1),
 "Спальня 2": (10.072, 14.745, 4.327, 7.491, "16,3 м²", 12.3, 6.3),
 "Коридор":   (1.945, 9.945, 6.672, 7.909, "", 6.6, 7.35),
 "Прихожая":  (1.945, 3.455, 7.909, 9.509, "", 2.55, 8.15),
 "Ванная":    (3.564, 6.073, 8.018, 9.509, "3,7 м²", 5.0, 8.55),
 "Санузел":   (0.309, 1.836, 6.8, 9.018, "3,1 м²", 1.1, 7.95),
}
for n, (x0, x1, z0, z1, a, cx, cy) in rooms.items():
    A(f'<text x="{X(cx):.0f}" y="{Y(cy):.0f}" text-anchor="middle" font-size="40" font-weight="bold" fill="{MUTED}">{n}</text>')
    if a:
        A(f'<text x="{X(cx):.0f}" y="{Y(cy)+44:.0f}" text-anchor="middle" font-size="32" fill="{MUTED}">{a}</text>')

# sockets: n, room, wall(L/R/T/B), along (m), kind, h(mm), what, count
SK = [
 (1,"Гостиная","L",3.44,"tv",1100,"За ТВ: 4 розетки + LAN + ТВ-антенна",4),
 (2,"Гостиная","L",3.44,"std",300,"Тумба ТВ, блок",2),
 (3,"Гостиная","R",2.20,"std",300,"У дивана",1),
 (4,"Гостиная","R",4.70,"std",300,"У дивана",1),
 (5,"Гостиная","T",2.30,"std",300,"У окна (торшер, обогрев)",1),
 (6,"Гостиная","R",1.40,"ac",2200,"Кондиционер",1),
 (7,"Гостиная","L",5.80,"std",300,"Пылесос",1),
 (8,"Комната","L",3.44,"tv",1100,"За ТВ: 4 розетки + LAN + ТВ-антенна",4),
 (9,"Комната","L",3.44,"std",300,"Тумба ТВ, блок",2),
 (10,"Комната","R",2.20,"std",300,"У дивана",1),
 (11,"Комната","R",4.70,"std",300,"У дивана",1),
 (12,"Комната","T",6.00,"std",300,"У окна",1),
 (13,"Комната","L",1.45,"ac",2200,"Кондиционер",1),
 (14,"Комната","L",5.80,"std",300,"Пылесос",1),
 (15,"Кухня","B",10.85,"std",1100,"Над столешницей, блок",2),
 (16,"Кухня","B",11.90,"std",1100,"Над столешницей, блок",2),
 (17,"Кухня","R",2.85,"pwr",300,"Индукционная плита 32 А (в соседнем модуле)",1),
 (18,"Кухня","R",2.33,"std",2100,"Вытяжка (в коробе над корпусом)",1),
 (19,"Кухня","L",2.70,"std",300,"Холодильник (сбоку)",1),
 (20,"Кухня","R",4.00,"std",300,"Посудомойка (в соседнем модуле)",1),
 (21,"Кухня","T",10.50,"std",300,"Духовой шкаф (в колонне ниже духовки)",1),
 (22,"Спальня 2","T",11.45,"std",700,"У спального места, блок",2),
 (23,"Спальня 2","T",13.60,"std",700,"У спального места, блок",2),
 (24,"Спальня 2","B",12.75,"tv",1100,"За ТВ: 4 розетки + LAN + ТВ-антенна",4),
 (25,"Спальня 2","B",12.75,"std",300,"Тумба ТВ, блок",2),
 (26,"Спальня 2","R",4.45,"ac",2200,"Кондиционер",1),
 (27,"Спальня 2","R",5.45,"std",300,"У окна",1),
 (28,"Коридор","T",4.00,"std",300,"Пылесос",1),
 (29,"Коридор","T",7.00,"std",300,"Пылесос",1),
 (30,"Прихожая","L",8.10,"std",300,"Пылесос",1),
 (31,"Прихожая","L",8.90,"std",1100,"Над обувницей (зарядка, зеркало)",1),
 (32,"Ванная","T",3.90,"wet",1000,"Стиральная машина, IP44",1),
 (33,"Ванная","T",5.75,"wet",1100,"Фен, IP44",1),
 (34,"Санузел","L",8.45,"wet",1100,"У зеркала (фен, бритва), IP44",1),
 (35,"Ванная","T",3.90,"wet",2000,"Бойлер 80 л, IP44",1),
 (36,"Санузел","R",8.70,"wet",2000,"Бойлер 80 л, IP44",1),
 (37,"Санузел","T",1.72,"wet",1300,"Насосная станция бака, IP44",1),
]
COL = {"std": INK, "tv": INK, "pwr": RED, "ac": GREEN, "wet": BLUE}
seen = {}
def sock(n, room, wall, a, kind, h):
    x0, x1, z0, z1 = rooms[room][:4]
    if wall == "L": px_, py_, ang = X(x0), Y(a), 0
    if wall == "R": px_, py_, ang = X(x1), Y(a), 180
    if wall == "T": px_, py_, ang = X(a), Y(z0), 90
    if wall == "B": px_, py_, ang = X(a), Y(z1), 270
    key = (round(px_), round(py_))
    stack = seen.get(key, 0); seen[key] = stack + 1
    c = COL[kind]
    R = 24
    g = f'<g transform="translate({px_:.1f},{py_:.1f}) rotate({ang})">'
    # semicircle, flat side on the wall; bar = ground contact (ГОСТ 21.608)
    fill = c if kind in ("pwr",) else "#FFFFFF"
    g += f'<path d="M0,{-R} A{R},{R} 0 0 1 0,{R} Z" fill="{fill}" stroke="{c}" stroke-width="5"/>'
    g += f'<line x1="{R}" y1="{-R*0.9}" x2="{R}" y2="{R*0.9}" stroke="{c}" stroke-width="5"/>'
    if kind == "tv":
        g += f'<rect x="{R+8}" y="-14" width="28" height="28" fill="none" stroke="{BLUE}" stroke-width="5"/>'
    g += '</g>'
    A(g)
    # label pushed into the room
    off = 78 + stack * 0
    dx = {0: 1, 180: -1, 90: 0, 270: 0}[ang]; dy = {0: 0, 180: 0, 90: 1, 270: -1}[ang]
    lx, ly = px_ + dx * off, py_ + dy * off
    if stack:
        lx += (0 if dx else 0); ly += 0
    return (lx, ly, c, dx, dy)

labels = {}
for (n, room, wall, a, kind, h, what, cnt) in SK:
    lx, ly, c, dx, dy = sock(n, room, wall, a, kind, h)
    labels.setdefault((round(lx), round(ly)), []).append((n, h, c, dx, dy))
for (lx, ly), items in labels.items():
    for i, (n, h, c, dx, dy) in enumerate(items):
        yy = ly + i * 62 - (len(items) - 1) * 31
        anchor = "start" if dx > 0 else ("end" if dx < 0 else "middle")
        if dx == 0:
            yy = ly + (i * 62 if dy > 0 else -i * 62) + (14 if dy > 0 else 0)
        A(f'<text x="{lx:.0f}" y="{yy+14:.0f}" text-anchor="{anchor}" font-size="34" font-weight="bold" fill="{c}">{n}<tspan font-weight="normal" font-size="28" fill="{INK}"> h{h}</tspan></text>')

# ЩК в прихожей
x_sh, z_sh = 3.455, 8.15
A(f'<rect x="{X(x_sh)-30:.1f}" y="{Y(z_sh)-36:.1f}" width="30" height="72" fill="{INK}"/>')
A(f'<text x="{X(x_sh)-44:.0f}" y="{Y(z_sh)+12:.0f}" text-anchor="end" font-size="32" font-weight="bold" fill="{INK}">ЩК + ЩС</text>')

# bidet callout
A(f'<text x="{X(0.71):.0f}" y="{Y(9.018)+70:.0f}" text-anchor="middle" font-size="32" font-weight="bold" fill="{ORANGE}">БИДЕ</text>')
A(f'<text x="{X(1.43):.0f}" y="{Y(9.018)+70:.0f}" text-anchor="middle" font-size="32" fill="{MUTED}">унитаз</text>')
# dimension bidet-toilet axes
yd = Y(9.018) + 110
A(f'<line x1="{X(0.309):.1f}" y1="{yd}" x2="{X(1.836):.1f}" y2="{yd}" stroke="{ORANGE}" stroke-width="3"/>')
for xm in (0.309, 0.71, 1.43, 1.836):
    A(f'<line x1="{X(xm):.1f}" y1="{yd-14}" x2="{X(xm):.1f}" y2="{yd+14}" stroke="{ORANGE}" stroke-width="3"/>')
for (a, b, t) in ((0.309, 0.71, "400"), (0.71, 1.43, "720"), (1.43, 1.836, "400")):
    A(f'<text x="{(X(a)+X(b))/2:.0f}" y="{yd+44}" text-anchor="middle" font-size="28" fill="{ORANGE}">{t}</text>')

# title block
A(f'<text x="150" y="150" font-size="72" font-weight="bold" fill="{INK}">ЭОМ. План расположения розеток</text>')
A(f'<text x="150" y="225" font-size="38" fill="{MUTED}">Квартира 100,58 м² · потолок 2700 · h — высота центра розетки от чистого пола, мм · ГОСТ 21.210, ГОСТ 21.608, СП 256.1325800.2016</text>')

# legend
LX = 2880; ly = 420
A(f'<text x="{LX}" y="{ly}" font-size="44" font-weight="bold" fill="{INK}">Условные обозначения</text>')
leg = [("std", "Розетка 2P+PE 16 А, скрытая"), ("tv", "То же + интернет RJ45 / ТВ"), ("wet", "Розетка IP44 с крышкой"), ("pwr", "Силовая 32 А (плита)"), ("ac", "Кондиционер, h2200")]
for i, (k, t) in enumerate(leg):
    yy = ly + 90 + i * 90
    c = COL[k]; R = 24
    g = f'<g transform="translate({LX+10},{yy})">'
    fill = c if k == "pwr" else "#FFFFFF"
    g += f'<path d="M0,{-R} A{R},{R} 0 0 1 0,{R} Z" fill="{fill}" stroke="{c}" stroke-width="5"/><line x1="{R}" y1="{-R*0.9}" x2="{R}" y2="{R*0.9}" stroke="{c}" stroke-width="5"/>'
    if k == "tv":
        g += f'<rect x="{R+8}" y="-14" width="28" height="28" fill="none" stroke="{BLUE}" stroke-width="5"/>'
    g += '</g>'
    A(g)
    A(f'<text x="{LX+100}" y="{yy+12}" font-size="34" fill="{INK}">{t}</text>')
yy = ly + 90 + 5 * 90
A(f'<rect x="{LX}" y="{yy-36}" width="30" height="72" fill="{INK}"/><text x="{LX+100}" y="{yy+12}" font-size="34" fill="{INK}">Щит квартирный + слаботочный</text>')
yy += 90
A(f'<ellipse cx="{LX+18}" cy="{yy}" rx="20" ry="26" fill="none" stroke="{ORANGE}" stroke-width="5"/><text x="{LX+100}" y="{yy+12}" font-size="34" fill="{INK}">Биде подвесное (новое)</text>')
yy += 110
notes = ["1. Цифра у знака — № розетки,", "    h — высота центра от чистого пола.", "2. Привязка к стенам — лист «Ведомость».",
         "3. Розетки в блоке — общая рамка,", "    шаг 71 мм, по горизонтали.", "4. Влажные зоны: IP44, УЗО 30 мА.",
         "5. Не ставить над мойкой и плитой;", "    ≥600 мм от ванны и душа.", "6. Кабель ВВГнг(А)-LS: розетки 3×2,5;", "    плита 3×6. Скрытая прокладка.",
         "7. Санузел перепланирован: унитаз", "    и биде на одной стене, раковина", "    перенесена на левую стену."]
for i, t in enumerate(notes):
    A(f'<text x="{LX}" y="{yy + i*50}" font-size="31" fill="{INK}">{t}</text>')
A(f'<text x="3720" y="2100" text-anchor="end" font-size="34" font-style="italic" fill="{INK}">created by Saloev S.A.</text>')
A('</svg>')
open("plan.svg", "w").write("\n".join(out))

# schedule data for the table slides
rows = []
for (n, room, wall, a, kind, h, what, cnt) in SK:
    x0, x1, z0, z1 = rooms[room][:4]
    if wall in "LR":
        d = round((a - z0) * 1000 / 10) * 10; ref = f"{d} от верхнего угла по плану"
        wn = "левая" if wall == "L" else "правая"
    else:
        d = round((a - x0) * 1000 / 10) * 10; ref = f"{d} от левого угла по плану"
        wn = "верхняя" if wall == "T" else "нижняя"
    rows.append(dict(n=n, room=room, wall=wn, ref=ref, h=h, what=what, cnt=cnt, kind=kind))
json.dump(rows, open("rows.json", "w"), ensure_ascii=False, indent=1)
print(len(rows), sum(r["cnt"] for r in rows))
