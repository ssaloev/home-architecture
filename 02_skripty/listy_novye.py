# Новые листы альбома (по образцу профессионального альбома). Исполняется в пространстве имён build.py
# после core.py и listy_osnovnye.py — поэтому доступны Sheet, X, Y, rooms, FURN, elevation, FIX, SK, PL и т. д.
import base64, io, math
S, OX, OY, FS = 168.0, 230, 300, 1.0

STYLE = D["styles"]; FLOORS = D["floors"]
CEIL_H = {"neo": 2.70, "modern": 2.65, "wet": 2.50, "hall": 2.65}
CEIL_OVR = {"Коридор": 2.50, "Прихожая": 2.50}          # короба под вентиляцию/трассы
def ceil_h(r): return r.get("ceiling_h", CEIL_OVR.get(r["name"], CEIL_H[r["style"]]))
VIEW_ORDER = {"Санузел": "LBTR", "Ванная": "TLBR", "Кухня": "RBTL"}   # как на старых листах разверток
def view_order(name): return VIEW_ORDER.get(name, "TRBL")
WALLRU = {"T": "верхняя", "B": "нижняя", "L": "левая", "R": "правая"}
CHK = ORANGE                                                         # цвет «размер под вопросом»

# ------------------------------------------------------------------ общие помощники
def dcol(room): return CHK if room in CHECK else RED
def tick_c(x, y, col):
    return f'<line x1="{x-11:.1f}" y1="{y+11:.1f}" x2="{x+11:.1f}" y2="{y-11:.1f}" stroke="{col}" stroke-width="3"/>'
def chain(s, vals, at, horizontal, col=RED, side=-1, fs=25, total=False):
    """Размерная цепочка в метрах. vals — точки вдоль оси, at — положение линии (м) по другой оси.
    side=-1: текст над/слева от линии, +1: под/справа."""
    vals = sorted(set(round(v, 4) for v in vals))
    if len(vals) < 2: return
    if horizontal:
        y = Y(at); s.A(f'<line x1="{X(vals[0]):.1f}" y1="{y:.1f}" x2="{X(vals[-1]):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.2"/>')
        for v in vals: s.A(tick_c(X(v), y, col))
        for i, (a, b) in enumerate(zip(vals, vals[1:])):
            if b - a < 0.04: continue
            w = (b - a) * S; ty = y - 9 if side < 0 else y + 30
            if w < 70: ty += (-26 if side < 0 else 26) * (i % 2)
            s.A(f'<text x="{(X(a)+X(b))/2:.0f}" y="{ty:.0f}" text-anchor="middle" font-size="{fs if w > 70 else fs-5}" fill="{col}">{mm(b-a)}</text>')
    else:
        x = X(at); s.A(f'<line x1="{x:.1f}" y1="{Y(vals[0]):.1f}" x2="{x:.1f}" y2="{Y(vals[-1]):.1f}" stroke="{col}" stroke-width="2.2"/>')
        for v in vals: s.A(tick_c(x, Y(v), col))
        for i, (a, b) in enumerate(zip(vals, vals[1:])):
            if b - a < 0.04: continue
            h = (b - a) * S; tx = x - 9 if side < 0 else x + 30
            if h < 70: tx += (-26 if side < 0 else 26) * (i % 2)
            cy = (Y(a) + Y(b)) / 2
            s.A(f'<text x="{tx:.0f}" y="{cy:.0f}" transform="rotate(-90 {tx:.0f} {cy:.0f})" text-anchor="middle" font-size="{fs if h > 70 else fs-5}" fill="{col}">{mm(b-a)}</text>')

def openings(rect, side):
    """Окна и двери в стене side ('T','B','L','R') прямоугольника помещения: [(a0, a1, kind, obj)]."""
    x0, x1, z0, z1 = rect; res = []
    for kind, ob in [("win", w) for w in WINDOWS] + [("door", d) for d in DOORS]:
        ox, oz, ow, od = ob["rect"]
        if side in "TB":
            if ow < od: continue
            zl = z0 if side == "T" else z1
            lo, hi = (zl - 0.45, zl + 0.01) if side == "T" else (zl - 0.01, zl + 0.45)
            if oz < hi and oz + od > lo:
                a0, a1 = max(ox, x0), min(ox + ow, x1)
                if a1 - a0 > 0.1: res.append((a0, a1, kind, ob))
        else:
            if od < ow: continue
            xl = x0 if side == "L" else x1
            lo, hi = (xl - 0.45, xl + 0.01) if side == "L" else (xl - 0.01, xl + 0.45)
            if ox < hi and ox + ow > lo:
                a0, a1 = max(oz, z0), min(oz + od, z1)
                if a1 - a0 > 0.1: res.append((a0, a1, kind, ob))
    return sorted(res, key=lambda t: t[0])

def wall_len(rect, side): x0, x1, z0, z1 = rect; return (x1 - x0) if side in "TB" else (z1 - z0)
def room_of(x, z):
    for r in ROOMS:
        for (x0, x1, z0, z1) in r["rects"]:
            if x0 - 0.01 <= x <= x1 + 0.01 and z0 - 0.01 <= z <= z1 + 0.01: return r
    return None
def room_num(s, r, area=True, name=True, col=INK):
    cx, cz = r["label"]
    s.A(f'<circle cx="{X(cx):.0f}" cy="{Y(cz):.0f}" r="34" fill="#FFFFFF" stroke="{col}" stroke-width="3"/><text x="{X(cx):.0f}" y="{Y(cz)+14:.0f}" text-anchor="middle" font-size="38" fill="{col}">{r["num"]}</text>')
    if area:
        q = " ?" if r["name"] in CHECK else ""
        s.A(f'<text x="{X(cx):.0f}" y="{Y(cz)+76:.0f}" text-anchor="middle" font-size="28" font-weight="bold" fill="{CHK if q else INK}">{f2(room_area(r))} м²{q}</text>')
def img_b64(path, maxw=1600, q=82):
    from PIL import Image
    im = Image.open(path).convert("RGB"); im.thumbnail((maxw, maxw))
    b = io.BytesIO(); im.save(b, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode(), im.size
def add_defs(s, xml): s.o[1] = s.o[1].replace("</defs>", xml + "</defs>")
def legend(s, y0, items, title="Условные обозначения"):
    """items: [(svg_fn(cx, cy), text)] — в правой колонке начиная с y0."""
    s.A(f'<text x="{(SX+W-40)/2:.0f}" y="{y0}" text-anchor="middle" font-size="34" font-weight="bold" fill="{INK}">{title}</text>')
    y = y0 + 60
    for fn, t in items:
        fn(SX + 70, y - 9); s.A(f'<text x="{SX+130}" y="{y}" font-size="26" fill="{INK}">{t}</text>'); y += 54
    s.ty = y - 40
    return y
def hatch_item(cx, cy, s=None): pass

# ================================================================== Титульный лист
# ================================================================== Обложка (по образцу проф. альбома: без рамки, фото в шевроне)
def cover():
    o = []; A = o.append
    BG, IK, AC = "#F1F1F2", "#24242B", "#8C9A7C"
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Bahnschrift, {FONT}">')
    hero = os.path.join(PROJ, "08_vizualizacii", "gostinaya", "_kremA_3_divan_i_kresla.jpg")
    if not os.path.exists(hero): hero = os.path.join(PROJ, "08_vizualizacii", "gostinaya", "_kremA_1_ot_dveri_k_oknu.jpg")
    href = ""
    if os.path.exists(hero):
        from PIL import Image as _I
        im = _I.open(hero).convert("RGB"); im.thumbnail((2000, 2000)); bf = io.BytesIO(); im.save(bf, "JPEG", quality=86)
        href = "data:image/jpeg;base64," + base64.b64encode(bf.getvalue()).decode()
    # шеврон: две параллельные «стрелки» вправо-влево, фото между ними
    P = "1880,40 2420,40 2060,1080 2420,2120 1880,2120 1520,1080"
    Q = "2420,40 3800,40 3800,2120 2420,2120 2060,1080"
    A(f'<defs><clipPath id="cv"><polygon points="2160,40 3200,40 2840,1080 3200,2120 2160,2120 2520,1080"/></clipPath></defs>')
    A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    A(f'<rect x="40" y="40" width="{W-80}" height="{H-80}" fill="none" stroke="#D6D6DA" stroke-width="3"/>')
    if href: A(f'<image x="1700" y="40" width="1900" height="2080" preserveAspectRatio="xMidYMid slice" href="{href}" clip-path="url(#cv)"/>')
    for (dx, sw, col) in ((-70, 34, "#FFFFFF"), (-110, 8, IK)):
        A(f'<polyline points="{2160+dx},40 {2520+dx},1080 {2160+dx},2120" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    for (dx, sw, col) in ((60, 30, "#FFFFFF"), (95, 8, IK)):
        A(f'<polyline points="{3200+dx},40 {2840+dx},1080 {3200+dx},2120" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    A(f'<rect x="{3200+120}" y="40" width="{W-40-3320}" height="{H-80}" fill="{BG}"/>')
    A(f'<polygon points="{3200+110},40 {W-40},40 {W-40},{H-40} {3200+110},{H-40} {2840+110},1080" fill="{BG}"/>')
    # геометрия: тонкий круг, акцентный круг, линия, крестики, уголок
    A(f'<circle cx="2050" cy="1300" r="360" fill="none" stroke="#9A9AA2" stroke-width="2.5"/>')
    A(f'<circle cx="2250" cy="1240" r="95" fill="{AC}"/>')
    A(f'<line x1="2230" y1="1270" x2="1180" y2="2120" stroke="{IK}" stroke-width="2.5"/>')
    for (cx, cy) in ((1160, 540), (3560, 760)):
        A(f'<path d="M{cx-45},{cy} H{cx+45} M{cx},{cy-45} V{cy+45}" stroke="#6E6E78" stroke-width="3"/>')
    A(f'<path d="M1430,670 H1500 V740" fill="none" stroke="{IK}" stroke-width="4"/>')
    # логотип-монограмма
    A(f'<g transform="translate(330,190)"><path d="M0,90 L38,0 L76,90 M14,58 H62" fill="none" stroke="{IK}" stroke-width="10"/>'
      f'<circle cx="38" cy="-14" r="9" fill="{IK}"/><text x="110" y="40" font-size="54" font-weight="bold" fill="{IK}">SALOEV</text>'
      f'<text x="110" y="92" font-size="44" fill="{IK}">DESIGN</text></g>')
    # заголовок
    A(f'<text x="330" y="880" font-size="190" font-weight="bold" letter-spacing="14" fill="{IK}" font-stretch="condensed">ДИЗАЙН-ПРОЕКТ</text>')
    A(f'<rect x="330" y="960" width="1060" height="150" fill="{IK}"/>')
    A(f'<text x="370" y="1060" font-size="66" letter-spacing="10" fill="#FFFFFF">КВАРТИРА 100,58 м²</text>')
    A(f'<text x="330" y="1220" font-size="52" letter-spacing="4" fill="#5A5A64">НЕОКЛАССИКА · {META["address"].upper()}</text>')
    # нижний блок
    A(f'<rect x="330" y="1560" width="270" height="16" fill="{IK}"/>')
    A(f'<text x="330" y="1700" font-size="64" fill="{IK}">ДИЗАЙНЕР</text>')
    A(f'<text x="330" y="1790" font-size="46" fill="{IK}">{META["designer"]}</text>')
    A(f'<text x="330" y="1870" font-size="40" fill="#6E6E78">{META["date"]} · альбом {LISTOV} листов</text>')
    A('</svg>')
    os.makedirs(OUT_SVG, exist_ok=True)
    open(os.path.join(OUT_SVG, "t0_titul.svg"), "w", encoding="utf-8").write(chr(10).join(o)); DONE.append("t0_titul")
cover()

# ================================================================== Ведомость чертежей
s = Sheet("Ведомость чертежей", 0)
half = (len(SHEETS) + 1) // 2; RH = min(54, int(1740 / (half + 1))); y = 290
for c, (x0t, x1t) in enumerate(((180, 1560), (1620, 3000))):
    part = SHEETS[c * half:(c + 1) * half]
    s.A(f'<rect x="{x0t}" y="{y}" width="{x1t-x0t}" height="{(len(part)+1)*RH}" fill="none" stroke="{INK}" stroke-width="3"/>')
    s.A(f'<text x="{x0t+50}" y="{y+38}" text-anchor="middle" font-size="26" font-weight="bold" fill="{INK}">Лист</text><text x="{x0t+120}" y="{y+38}" font-size="26" font-weight="bold" fill="{INK}">Наименование</text><text x="{x1t-150}" y="{y+38}" font-size="26" font-weight="bold" fill="{INK}">Статус</text>')
    for i, (f, name) in enumerate(part):
        yy = y + RH * (i + 1); n = c * half + i + 1
        nm = name if len(name) <= 52 else name[:50] + "…"
        s.A(f'<line x1="{x0t}" y1="{yy}" x2="{x1t}" y2="{yy}" stroke="{INK}" stroke-width="1.5"/>')
        s.A(f'<text x="{x0t+50}" y="{yy+37}" text-anchor="middle" font-size="25" fill="{INK}">{n}</text><text x="{x0t+120}" y="{yy+37}" font-size="25" fill="{INK}">{nm}</text><text x="{x1t-150}" y="{yy+37}" font-size="22" fill="#8A8478">черновик</text>')
    for xx in (x0t + 100, x1t - 170):
        s.A(f'<line x1="{xx}" y1="{y}" x2="{xx}" y2="{y+(len(part)+1)*RH}" stroke="{INK}" stroke-width="1.5"/>')
s.ty = 130
s.notes(["Вне нумерации:", "  Замерный лист (что мерить).", "", "Все листы строятся из одного", "файла data/kvartira.json:", "  python build.py", "", "После замера правится только", "этот файл — листы, площади и", "ведомости пересчитываются сами."])
s.save("t1_vedomost")

# ================================================================== Исходные требования
s = Sheet("Исходные требования и стиль", 0)
y = 300
s.A(f'<text x="200" y="{y}" font-size="48" font-weight="bold" fill="{INK}">Что важно заказчику</text>')
for i, t in enumerate(D["requirements"]):
    s.A(f'<circle cx="222" cy="{y+70+i*72-10}" r="9" fill="{ORANGE}"/><text x="250" y="{y+70+i*72}" font-size="34" fill="{INK}">{t}</text>')
y += 70 + len(D["requirements"]) * 72 + 80
s.A(f'<text x="200" y="{y}" font-size="48" font-weight="bold" fill="{INK}">Стиль и отделка по помещениям</text>')
cols = [200, 300, 620, 1060, 1720, 2400]; y += 40
heads = ["№", "Помещение", "Стиль", "Пол", "Стены", "Потолок"]
s.A(f'<line x1="200" y1="{y}" x2="2950" y2="{y}" stroke="{INK}" stroke-width="2"/>')
for c, h in zip(cols, heads): s.A(f'<text x="{c+10}" y="{y+40}" font-size="28" font-weight="bold" fill="{INK}">{h}</text>')
y += 60
for r in ROOMS:
    st = STYLE[r["style"]]
    walls_t = st["walls"].split(" / ")[0] if r["name"] != "Кухня" else "Фартук — керамогранит; стены — на согласование"
    cells = [str(r["num"]), r["name"], st["name"], FLOORS[r["floor"]]["name"], walls_t, st["ceiling"].split(";")[0] + f", h={int(ceil_h(r)*1000)}"]
    s.A(f'<line x1="200" y1="{y}" x2="2950" y2="{y}" stroke="#CFC9BE" stroke-width="1.5"/>')
    for c, t in zip(cols, cells):
        lines = [t[i:i+34] for i in range(0, len(t), 34)] if len(t) > 36 else [t]
        for k, ln in enumerate(lines[:2]): s.A(f'<text x="{c+10}" y="{y+40+k*30}" font-size="{26 if len(lines) > 1 else 28}" fill="{INK}">{ln}</text>')
    y += 80
s.explication("Стиль", [("Неоклассика — гостиная", None, "1"), ("Остальные — НЕ выбран", None, "7")], colname="")
s.notes(["Решено: гостиная — неоклассика.", "Стиль остальных — подобрать", "референсы в интернете и", "согласовать с заказчиком.", "Дети: скруглённые углы,", "моющиеся покрытия."])
s.save("t2_trebovaniya")

# ================================================================== Обмерный план (детальный)
s = Sheet("Обмерный план", 1)
OY = 360
s.walls()
for r in ROOMS: room_num(s, r)
for r in ROOMS:
    col = dcol(r["name"])
    for k, rect in enumerate(r["rects"]):
        x0, x1, z0, z1 = rect
        main = (k == 0)
        # верх/низ: цепочка с проёмами
        for side in ("T", "B") if main else ("T",):
            op = openings(rect, side)
            if side == "B" and not op and main: continue
            pts = [x0, x1] + [v for (a0, a1, *_r) in op for v in (a0, a1)]
            at = z0 + 0.17 if side == "T" else z1 - 0.17
            chain(s, pts, at, True, col, side=+1 if side == "T" else -1)
        for side in ("L", "R") if main else ("L",):
            op = openings(rect, side)
            if side == "R" and not op and main: continue
            pts = [z0, z1] + [v for (a0, a1, *_r) in op for v in (a0, a1)]
            at = x0 + 0.17 if side == "L" else x1 - 0.17
            chain(s, pts, at, False, col, side=+1 if side == "L" else -1)
# толщины перегородок между соседними помещениями
allr = [(r["name"], rc) for r in ROOMS for rc in r["rects"]]
seen_t = set()
for (na, A_) in allr:
    for (nb, B_) in allr:
        if na == nb: continue
        g = B_[0] - A_[1]; ov0, ov1 = max(A_[2], B_[2]), min(A_[3], B_[3])
        if 0.05 < g < 0.5 and ov1 - ov0 > 0.3:
            zc = (ov0 + ov1) / 2; key = (round(A_[1], 2), round(zc, 1))
            if key in seen_t: continue
            seen_t.add(key)
            s.A(f'<rect x="{X((A_[1]+B_[0])/2)-15:.0f}" y="{Y(zc)-62:.0f}" width="30" height="64" fill="#FFFFFF"/>')
            s.A(f'<text x="{X((A_[1]+B_[0])/2)+7:.0f}" y="{Y(zc)-30:.0f}" transform="rotate(-90 {X((A_[1]+B_[0])/2)+7:.0f} {Y(zc)-30:.0f})" text-anchor="middle" font-size="20" font-weight="bold" fill="{BLUE}">{mm(g)}</text>')
        g = B_[2] - A_[3]; ov0, ov1 = max(A_[0], B_[0]), min(A_[1], B_[1])
        if 0.05 < g < 0.5 and ov1 - ov0 > 0.3:
            xc = (ov0 + ov1) / 2; key = (round(xc, 1), round(A_[3], 2))
            if key in seen_t: continue
            seen_t.add(key)
            s.A(f'<rect x="{X(xc)-32:.0f}" y="{Y((A_[3]+B_[2])/2)-13:.0f}" width="64" height="26" fill="#FFFFFF"/>')
            s.A(f'<text x="{X(xc):.0f}" y="{Y((A_[3]+B_[2])/2)+8:.0f}" text-anchor="middle" font-size="20" font-weight="bold" fill="{BLUE}">{mm(g)}</text>')
# габаритная цепочка по фасаду (верх) — по окнам и простенкам
top = sorted({v for (x, z, w, d) in G["walls"] if z < 0.02 for v in (x, x + w)} | {v for wd in WINDOWS for v in (wd["rect"][0], wd["rect"][0] + wd["rect"][2]) if wd["rect"][1] < 0.1})
chain(s, top, -0.22, True, INK, side=-1, fs=24)
chain(s, [top[0], top[-1]], -0.48, True, INK, side=-1, fs=26)
# стояки (если внесены)
for rs in D.get("risers", []):
    s.A(f'<circle cx="{X(rs["x"]):.0f}" cy="{Y(rs["z"]):.0f}" r="18" fill="#FFFFFF" stroke="{RED}" stroke-width="5"/><text x="{X(rs["x"])+26:.0f}" y="{Y(rs["z"])+9:.0f}" font-size="26" font-weight="bold" fill="{RED}">{rs["name"]}</text>')
s.A(f'<text x="{X(9.8):.0f}" y="{Y(1.0):.0f}" text-anchor="middle" font-size="26" fill="{INK}">ниша конд.</text>')
s.explication("Экспликация помещений", expl_rows(), colname="м²")
legend(s, s.ty + 80, [
    (lambda cx, cy: s.A(f'<rect x="{cx-30}" y="{cy-14}" width="60" height="28" fill="url(#hatch)" stroke="{INK}"/>'), "Существующие стены"),
    (lambda cx, cy: s.A(f'<line x1="{cx-30}" y1="{cy}" x2="{cx+30}" y2="{cy}" stroke="{RED}" stroke-width="3"/>'), "Размер в чистоте, мм"),
    (lambda cx, cy: s.A(f'<line x1="{cx-30}" y1="{cy}" x2="{cx+30}" y2="{cy}" stroke="{CHK}" stroke-width="3"/>'), "Размер ПОД ВОПРОСОМ (замер)"),
    (lambda cx, cy: s.A(f'<text x="{cx}" y="{cy+9}" text-anchor="middle" font-size="22" font-weight="bold" fill="{BLUE}">120</text>'), "Толщина перегородки, мм"),
    (lambda cx, cy: s.A(f'<circle cx="{cx}" cy="{cy}" r="14" fill="#FFF" stroke="{RED}" stroke-width="4"/>'), "Стояк (внести после замера)"),
])
s.notes([f"1. Потолок {int(HCEIL*1000)} — проверить в 3 местах.", "2. Окна: подоконник ~800, верх", "    ~2400 — уточнить по замеру.", "3. Допуск ±20 мм; изменения —", "    по согласованию с заказчиком."])
s.save("s1_obmer")
OY = 300

# ================================================================== Демонтаж / монтаж
s = Sheet("План демонтажа и монтажа перегородок", 0)
s.furniture(col="#C9C3B8"); s.walls()
for r in ROOMS: room_num(s, r, area=False)
NEW = [((0.309, 8.818, 1.527, 0.20), "короб инсталляций h=1200"),     # санузел, стена биде/унитаза
       ((5.873, 8.08, 0.20, 0.70), "короб инсталляций h=1200"),       # ванная, правая стена (13.11: один унитаз)
       ((0.309, 7.74, 0.24, 0.52), "")]                                # 13.11: пенал бака 200 л под заказ (санузел, левая стена)
for (x, z, w, d), t in NEW:
    s.A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#9FD3A8" stroke="{GREEN}" stroke-width="3"/>')
s.A(f'<text x="{X(1.07):.0f}" y="{Y(9.018)+60:.0f}" text-anchor="middle" font-size="24" fill="{GREEN}">короб инсталляций (ГКЛВ) h=1200</text>')
s.A(f'<text x="{X(6.3):.0f}" y="{Y(8.75):.0f}" font-size="24" fill="{GREEN}">короб инсталл.</text>')
s.explication("Экспликация помещений", expl_rows(), colname="м²")
legend(s, s.ty + 80, [
    (lambda cx, cy: s.A(f'<rect x="{cx-30}" y="{cy-14}" width="60" height="28" fill="url(#hatch)" stroke="{INK}"/>'), "Существующие стены — сохраняются"),
    (lambda cx, cy: s.A(f'<rect x="{cx-30}" y="{cy-14}" width="60" height="28" fill="#FFFFFF" stroke="{RED}" stroke-width="3" stroke-dasharray="8 5"/>'), "Демонтируемые (нет)"),
    (lambda cx, cy: s.A(f'<rect x="{cx-30}" y="{cy-14}" width="60" height="28" fill="#9FD3A8" stroke="{GREEN}" stroke-width="3"/>'), "Монтируемые: ГКЛВ на профиле"),
])
s.notes(["1. Перенос перегородок НЕ", "    предусмотрен (черновик).", "2. Демонтаж: старая сантехника,", "    покрытия пола, отделка стен.", "3. Монтаж: короба инсталляций", "    в с/у, ниша бака 200 л.", "4. Несущие стены — не трогать;", "    отметить после замера."])
s.save("s1b_demontazh")

# ================================================================== Мебель с размерами
s = Sheet("Планировочное решение с размерами", 0)
s.furniture(fill="#F3EFE7", col="#6B665C", sw=3); s.walls()
for r in ROOMS: room_num(s, r, area=False)
for f in FURN:
    cx, cz = f["x"] + f["w"] / 2, f["z"] + f["d"] / 2
    r = room_of(cx, cz)
    if not r: continue
    x0, x1, z0, z1 = next(rc for rc in r["rects"] if rc[0] - 0.01 <= cx <= rc[1] + 0.01 and rc[2] - 0.01 <= cz <= rc[3] + 0.01)
    col = dcol(r["name"])
    gl, gr = f["x"] - x0, x1 - (f["x"] + f["w"]); gt, gb = f["z"] - z0, z1 - (f["z"] + f["d"])
    # привязка к ближайшей стене по каждой оси (если не вплотную)
    if min(gl, gr) > 0.04:
        if gl <= gr: chain(s, [x0, f["x"]], cz, True, col, fs=21)
        else: chain(s, [f["x"] + f["w"], x1], cz, True, col, fs=21)
    if min(gt, gb) > 0.04:
        if gt <= gb: chain(s, [z0, f["z"]], cx, False, col, fs=21)
        else: chain(s, [f["z"] + f["d"], z1], cx, False, col, fs=21)
    # габарит предмета
    lab = f'{mm(f["w"])}×{mm(f["d"])}'.replace(" ", "")
    vert = f["d"] > f["w"] * 1.6
    if vert:
        s.A(f'<text x="{X(cx)+8:.0f}" y="{Y(cz):.0f}" transform="rotate(-90 {X(cx)+8:.0f} {Y(cz):.0f})" text-anchor="middle" font-size="21" fill="{INK}">{(f["name"].split(" ")[0] + " ") if f["name"] else ""}{lab}</text>')
    else:
        s.A(f'<text x="{X(cx):.0f}" y="{Y(cz)+8:.0f}" text-anchor="middle" font-size="21" fill="{INK}">{(f["name"].split(" ")[0] + " ") if f["name"] else ""}{lab}</text>')
# проходы (минимальные)
s.A(f'<text x="{X(3.75):.0f}" y="{Y(5.5):.0f}" text-anchor="middle" font-size="22" fill="{GREEN}">проход ≥ 700</text>')
s.explication("Экспликация помещений", expl_rows(), colname="м²")
s.notes(["1. Размеры мебели — габаритные, мм;", "    привязка — от стены в чистоте.", "2. Оранжевым — помещения, где", "    размеры под вопросом (замер).", "3. Шкафы до h=2400, фасады", "    без ручек (push-to-open).",
         "4. Проходы: ≥700 мм, у кровати", "    ≥600 мм.", "5. Детская безопасность: мебель", "    крепить к стене, углы R≥10."])
s.save("s2b_mebel_razm")

# ================================================================== План покрытий пола
s = Sheet("План покрытий пола", 0)
add_defs(s, '''<pattern id="fl_parquet" width="480" height="160" patternUnits="userSpaceOnUse"><rect x="-240" y="0" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="0" y="0" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="240" y="0" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="480" y="0" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="-80" y="20" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="160" y="20" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="400" y="20" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="640" y="20" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="-160" y="40" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="80" y="40" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="320" y="40" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="560" y="40" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="-40" y="60" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="200" y="60" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="440" y="60" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="680" y="60" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="-200" y="80" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="40" y="80" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="280" y="80" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="520" y="80" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="-120" y="100" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="120" y="100" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="360" y="100" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="600" y="100" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="-20" y="120" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="220" y="120" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="460" y="120" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="700" y="120" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="-140" y="140" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="100" y="140" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/><rect x="340" y="140" width="240" height="20" fill="#ECE7DE" stroke="#9C968C" stroke-width="1.2"/><rect x="580" y="140" width="240" height="20" fill="#DCD4C5" stroke="#9C968C" stroke-width="1.2"/></pattern>
<pattern id="fl_porcelain" width="101" height="202" patternUnits="userSpaceOnUse"><rect width="101" height="202" fill="#FFFFFF"/><path d="M0,0 H101 M0,0 V202" fill="none" stroke="#9C968C" stroke-width="1.5"/></pattern>
<pattern id="fl_tbd" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="#FFFFFF"/><circle cx="30" cy="30" r="2.5" fill="#C9C3B8"/></pattern>''')
for r in ROOMS:
    for (x0, x1, z0, z1) in r["rects"]:
        s.A(f'<rect x="{X(x0):.1f}" y="{Y(z0):.1f}" width="{(x1-x0)*S:.1f}" height="{(z1-z0)*S:.1f}" fill="url(#fl_{r["floor"]})" stroke="none"/>')
s.walls()
for r in ROOMS:
    cx, cz = r["label"]
    s.A(f'<rect x="{X(cx)-120:.0f}" y="{Y(cz)-42:.0f}" width="240" height="150" rx="10" fill="#FFFFFF" opacity="0.88"/>')
    room_num(s, r)
# стыки покрытий у дверей
for d in DOORS:
    ox, oz, ow, od = d["rect"]
    if ow >= od: pa, pb = (ox + ow / 2, oz - 0.12), (ox + ow / 2, oz + od + 0.12)
    else: pa, pb = (ox - 0.12, oz + od / 2), (ox + ow + 0.12, oz + od / 2)
    ra, rb = room_of(*pa), room_of(*pb)
    if ra and rb and ra["floor"] != rb["floor"]:
        if ow >= od: s.A(f'<line x1="{X(ox):.1f}" y1="{Y(oz+od/2):.1f}" x2="{X(ox+ow):.1f}" y2="{Y(oz+od/2):.1f}" stroke="{RED}" stroke-width="7"/>')
        else: s.A(f'<line x1="{X(ox+ow/2):.1f}" y1="{Y(oz):.1f}" x2="{X(ox+ow/2):.1f}" y2="{Y(oz+od):.1f}" stroke="{RED}" stroke-width="7"/>')
tot = {}
for r in ROOMS: tot[r["floor"]] = tot.get(r["floor"], 0) + room_area(r)
s.explication("Покрытия пола", [(FLOORS[k]["name"], (lambda k: (lambda cx, cy: s.A(f'<rect x="{cx-28}" y="{cy-16}" width="56" height="32" fill="url(#fl_{k})" stroke="{INK}"/>')))(k), f2(v)) for k, v in tot.items()]
              + [("Стык покрытий (профиль)", lambda cx, cy: s.A(f'<line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{RED}" stroke-width="7"/>'), "")], colname="м²")
s.notes(["1. Площади — в чистоте, без запаса;", "    закупка: керамогранит +10%,", "    доска палубная +7%.", "2. Доска — один пол на всю", "    квартиру, кроме кухни и мокрых зон.", "3. Стыки в дверных проёмах —", "    под полотном двери, без порогов.",
          "5. Гидроизоляция: ванная, санузел,", "    кухня у мойки."])
s.save("s12_poly")

# ================================================================== План потолка
def light_frame(s, a0, a1, b0, b1, sw=1.0):
    """Световая линия (профиль заподлицо, белый опал): контур + светлая полоса."""
    for st, c in ((14 * sw, INK), (8 * sw, "#FFE9A8")):
        s.A(f'<rect x="{X(a0):.1f}" y="{Y(b0):.1f}" width="{(a1-a0)*S:.1f}" height="{(b1-b0)*S:.1f}" fill="none" stroke="{c}" stroke-width="{st}"/>')

s = Sheet("План потолка", 0)
CFILL = {"neo": "#FBF8F1", "modern": "#F4F6F7", "wet": "#EAF2F6", "hall": "#F4F6F7"}
for r in ROOMS:
    for (x0, x1, z0, z1) in r["rects"]:
        s.A(f'<rect x="{X(x0):.1f}" y="{Y(z0):.1f}" width="{(x1-x0)*S:.1f}" height="{(z1-z0)*S:.1f}" fill="{CFILL[r["style"]]}"/>')
    x0, x1, z0, z1 = r["rects"][0]
    led = r["lights"].get("led")
    if led in ("cornice", "niche") and r["style"] != "neo":
        i = 0.12
        s.A(f'<rect x="{X(x0+i):.1f}" y="{Y(z0+i):.1f}" width="{(x1-x0-2*i)*S:.1f}" height="{(z1-z0-2*i)*S:.1f}" fill="none" stroke="{ORANGE}" stroke-width="4" stroke-dasharray="18 10"/>')
    if r["lights"].get("main") == "frame":
        fo = r["lights"].get("frame_off", 0.6); light_frame(s, x0 + fo, x1 - fo, z0 + fo, z1 - fo)
        # скрытая ниша под карниз штор (2 ряда: тюль + шторы) вдоль окна
        s.A(f'<rect x="{X(x0):.1f}" y="{Y(z0):.1f}" width="{(x1-x0)*S:.1f}" height="{0.15*S:.1f}" fill="#E8E2D6" stroke="{INK}" stroke-width="2" stroke-dasharray="10 6"/>')
        s.A(f'<text x="{X((x0+x1)/2):.0f}" y="{Y(z0+0.15)+28:.0f}" text-anchor="middle" font-size="20" fill="{INK}">ниша 150 под карниз штор</text>')
    if r["style"] == "neo":     # СОГЛАСОВАНО (образцы 1+5): лепные рамки с узорами, розетка, подсветка карниза, круглые споты
        GC = "#A08C68"         # по эскизу заказчика: одна лепная рамка (двойная линия) у стен + узоры в 4 углах
        bz0 = z0 + 0.15        # короб ГКЛ 340×100 по 3 стенам (у окна — ниша штор), внутри — LED за бортиком
        s.A(f'<rect x="{X(x0+0.34):.1f}" y="{Y(bz0+0.34):.1f}" width="{(x1-x0-0.68)*S:.1f}" height="{(z1-bz0-0.68)*S:.1f}" fill="none" stroke="{INK}" stroke-width="3"/>')
        s.A(f'<rect x="{X(x0+0.30):.1f}" y="{Y(bz0+0.30):.1f}" width="{(x1-x0-0.60)*S:.1f}" height="{(z1-bz0-0.60)*S:.1f}" fill="none" stroke="{ORANGE}" stroke-width="4" stroke-dasharray="14 8"/>')
        s.A(f'<text x="{X((x0+x1)/2):.0f}" y="{Y(z1-0.12):.0f}" text-anchor="middle" font-size="19" fill="{INK}">короб 340×100, низ +2600</text>')
        for (i, sw_) in ((0.45, 5), (0.54, 2.5)):
            s.A(f'<rect x="{X(x0+i):.1f}" y="{Y(bz0+i-0.05):.1f}" width="{(x1-x0-2*i)*S:.1f}" height="{(z1-bz0-2*i+0.05)*S:.1f}" fill="none" stroke="{GC}" stroke-width="{sw_}"/>')
        q = 0.58
        for (ux, uz, dx, dz) in ((x0+q, z0+q, 1, 1), (x1-q, z0+q, -1, 1), (x0+q, z1-q, 1, -1), (x1-q, z1-q, -1, -1)):
            orn_corner(s.A, X(ux), Y(uz), dx, dz, 0.45 * S, GC)
        ns = r["lights"].get("round_spots", 0)
        for k in range(ns // 2):
            zz = z0 + 1.4 + k * (z1 - z0 - 2.8) / max(1, ns // 2 - 1)
            for xx in (x0 + 0.80, x1 - 0.80):
                s.A(f'<circle cx="{X(xx):.1f}" cy="{Y(zz):.1f}" r="14" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><circle cx="{X(xx):.1f}" cy="{Y(zz):.1f}" r="5" fill="{INK}"/>')
s.walls()
for r in ROOMS:
    cx, cz = r["label"]; h = int(ceil_h(r) * 1000)
    room_num(s, r, area=False)
    s.A(f'<rect x="{X(cx)-70:.0f}" y="{Y(cz)+46:.0f}" width="140" height="46" rx="23" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/><text x="{X(cx):.0f}" y="{Y(cz)+79:.0f}" text-anchor="middle" font-size="27" font-weight="bold" fill="{INK}">+{h}</text>')
s.explication("Типы потолка", [("Гостиная: ГКЛ, окраска, карниз", lambda cx, cy: s.A(f'<rect x="{cx-28}" y="{cy-16}" width="56" height="32" fill="{CFILL["neo"]}" stroke="#A08C68" stroke-width="3"/>'), "1"),
    ("ГКЛ, окраска, теневой профиль", lambda cx, cy: s.A(f'<rect x="{cx-28}" y="{cy-16}" width="56" height="32" fill="{CFILL["modern"]}" stroke="{INK}"/>'), "5"),
    ("Влагостойкий ГКЛВ / натяжной", lambda cx, cy: s.A(f'<rect x="{cx-28}" y="{cy-16}" width="56" height="32" fill="{CFILL["wet"]}" stroke="{INK}"/>'), "2"),
    ("Световая линия заподлицо, белая", lambda cx, cy: s.A(f'<line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{INK}" stroke-width="14"/><line x1="{cx-27}" y1="{cy}" x2="{cx+27}" y2="{cy}" stroke="#FFE9A8" stroke-width="8"/>'), "1"),
    ("LED-лента в нише / карнизе", lambda cx, cy: s.A(f'<line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{ORANGE}" stroke-width="4" stroke-dasharray="12 6"/>'), ""),
    ("Отметка потолка от чистого пола", lambda cx, cy: s.A(f'<rect x="{cx-30}" y="{cy-14}" width="60" height="28" rx="14" fill="#FFF" stroke="{INK}" stroke-width="2"/>'), "")], colname="шт")
s.notes([f"1. Плита перекрытия {int(HCEIL*1000)} (проверить).", "2. Коридор, прихожая 2500 — короб", "    под вентиляцию и трассы.", "3. Мокрые зоны 2500 — над", "    бойлерами доступ (люк).",
         "4. Гостиная: короб ГКЛ 340×100 по", "    кругу (у окна — до ниши штор), LED", "    на потолок +2700 (как фото 1);", "    лепная рамка с узорами в углах,", "    LED-рамка, по 3 спота с боков;", "    у окна ниша 150 под 2-рядный", "    скрытый карниз (тюль + шторы).", "5. Комнаты: теневой профиль", "    + LED-ниша по периметру."])
s.save("s13_potolok")

# ================================================================== План привязки светильников
s = Sheet("План привязки осветительных приборов", 0)
s.furniture(col="#D2CCC2"); s.walls()
SYM = {}
def l_chand(cx, cy, s=s): s.A(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="30" fill="#FFF8E6" stroke="{INK}" stroke-width="4"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="{ORANGE}"/><path d="M{cx-30:.1f},{cy:.1f} H{cx+30:.1f} M{cx:.1f},{cy-30:.1f} V{cy+30:.1f}" stroke="{INK}" stroke-width="2"/>')
def l_pend(cx, cy, s=s): s.A(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="#FFF8E6" stroke="{INK}" stroke-width="4"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="{INK}"/>')
def l_spot(cx, cy, s=s): s.A(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><path d="M{cx-8:.1f},{cy-8:.1f} L{cx+8:.1f},{cy+8:.1f} M{cx+8:.1f},{cy-8:.1f} L{cx-8:.1f},{cy+8:.1f}" stroke="{INK}" stroke-width="2"/>')
def l_sconce(cx, cy, s=s): s.A(f'<path d="M{cx-18:.1f},{cy:.1f} A18,18 0 0 1 {cx+18:.1f},{cy:.1f} Z" fill="{ORANGE}" stroke="{INK}" stroke-width="2"/>')
count = {"chand": 0, "pend": 0, "spot": 0, "sconce": 0}
for r in ROOMS:
    x0, x1, z0, z1 = r["rects"][0]; L = r["lights"]; pts = []
    W_, H_ = x1 - x0, z1 - z0; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if L["main"] == "chandelier": l_chand(X(cx), Y(cz)); pts.append((cx, cz)); count["chand"] += 1
    if L["main"] == "pendant": l_pend(X(cx), Y(cz)); pts.append((cx, cz)); count["pend"] += 1
    if L["main"] == "pendants2":
        tx, tz = x0 + 1.2, z0 + 0.975
        for dx in (-0.3, 0.3): l_pend(X(tx + dx), Y(tz)); pts.append((tx + dx, tz)); count["pend"] += 1
    n = L.get("spots", 0)
    if n:
        if L["main"] == "spots_line":
            if W_ >= H_: sp = [(x0 + (i + 0.5) * W_ / n, cz) for i in range(n)]
            else: sp = [(cx, z0 + (i + 0.5) * H_ / n) for i in range(n)]
        else:
            m = 0.55 if W_ > 2 and H_ > 2 else 0.4
            ar = W_ / H_
            cols, rows = min(((c, n // c) for c in range(1, n + 1) if n % c == 0), key=lambda cr: abs(math.log((cr[0] / cr[1]) / ar)))
            sp = [(x0 + m + (W_ - 2 * m) * (i + 0.5) / cols, z0 + m + (H_ - 2 * m) * (j + 0.5) / rows) for j in range(rows) for i in range(cols)][:n]
        for (px, pz) in sp: l_spot(X(px), Y(pz)); pts.append((px, pz)); count["spot"] += 1
    if L.get("led") == "worktop":
        s.A(f'<line x1="{X(10.64):.1f}" y1="{Y(z1-0.32):.1f}" x2="{X(12.4):.1f}" y2="{Y(z1-0.32):.1f}" stroke="{ORANGE}" stroke-width="5" stroke-dasharray="16 8"/>')
    if L.get("led") == "mirror":
        s.A(f'<text x="{X(cx):.0f}" y="{Y(z1)-20:.0f}" text-anchor="middle" font-size="20" fill="{ORANGE}">подсв. зеркала</text>')
    if L.get("led") in ("cornice", "niche"):
        s.A(f'<rect x="{X(x0+0.12):.1f}" y="{Y(z0+0.12):.1f}" width="{(W_-0.24)*S:.1f}" height="{(H_-0.24)*S:.1f}" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="16 10"/>')
    if L.get("sconces"):
        if r["name"] == "Гостиная":
            for zz in (2.2, 4.7): l_sconce(X(x1) - 0, Y(zz)); count["sconce"] += 1
            s.A(f'<text x="{X(x1)-30:.0f}" y="{Y(3.45):.0f}" text-anchor="end" font-size="22" fill="{ORANGE}">бра h=1600</text>')
        elif r["name"] == "Спальня 2":
            for xx in (11.45, 14.0): l_sconce(X(xx), Y(z0) + 18); count["sconce"] += 1
            s.A(f'<text x="{X(12.75):.0f}" y="{Y(z0)+44:.0f}" text-anchor="middle" font-size="22" fill="{ORANGE}">бра h=1400</text>')
    if L["main"] == "frame":
        fo = L.get("frame_off", 0.6); fa0, fa1, fb0, fb1 = x0 + fo, x1 - fo, z0 + fo, z1 - fo
        light_frame(s, fa0, fa1, fb0, fb1, 0.8)
        pts += [(fa0, fb0), (fa1, fb1)]
        ns = L.get("round_spots", 0)
        for k in range(ns // 2):
            zz = z0 + 1.4 + k * (z1 - z0 - 2.8) / max(1, ns // 2 - 1)
            for xx in (x0 + 0.80, x1 - 0.80): l_spot(X(xx), Y(zz)); count["spot"] += 1
        if ns: pts += [(x0 + 0.75, z0 + 1.4)]
        count["frame"] = count.get("frame", 0) + 2 * ((fa1 - fa0) + (fb1 - fb0))
        s.A(f'<text x="{X(cx)-40:.0f}" y="{Y(cz)-60:.0f}" text-anchor="middle" font-size="22" fill="{ORANGE}">световая рамка {(fa1-fa0)*1000:.0f}×{(fb1-fb0)*1000:.0f}</text>')
        s.A(f'<text x="{X(cx)-40:.0f}" y="{Y(cz)-32:.0f}" text-anchor="middle" font-size="22" fill="{ORANGE}">{L.get("frame_lm_m",500)} лм/м, 3000 K — 4 сценария</text>')
    if pts:
        col = dcol(r["name"])
        chain(s, [x0, x1] + [p[0] for p in pts], z0 + 0.12 if r["name"] not in ("Коридор",) else z1 - 0.12, True, col, side=+1, fs=21)
        if H_ > 1.4: chain(s, [z0, z1] + [p[1] for p in pts], x0 + 0.12, False, col, side=+1, fs=21)
# ---- коридор и прихожая (согласовано 12.11): круглые Ø240, LED в пазу, зеркало (LED в плинтусах убран 12.11)
def l_disc(cx, cy, s=s): s.A(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="21" fill="#FFF8E6" stroke="{INK}" stroke-width="4"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="none" stroke="{INK}" stroke-width="2"/>')
def l_plinth(x0_, z0_, x1_, z1_, s=s): s.A(f'<line x1="{X(x0_):.1f}" y1="{Y(z0_):.1f}" x2="{X(x1_):.1f}" y2="{Y(z1_):.1f}" stroke="#2E9E6B" stroke-width="7" stroke-dasharray="5 7"/>')
DISCS = [(x, 7.29) for x in (2.75, 3.95, 5.15, 6.35, 7.55, 8.75)] + [(2.70, 8.55), (2.70, 9.15)]
for (px, pz) in DISCS: l_disc(X(px), Y(pz)); count["spot_disc"] = count.get("spot_disc", 0) + 1
chain(s, [1.945, 9.945] + [p[0] for p in DISCS[:6]], 6.672 + 0.12, True, dcol("Коридор"), side=+1, fs=21)
chain(s, [7.909, 9.509, 8.55, 9.15], 1.945 + 0.12, False, dcol("Прихожая"), side=+1, fs=21)
s.A(f'<rect x="{X(1.945+0.05):.1f}" y="{Y(7.909+0.05):.1f}" width="{(3.455-1.945-0.1)*S:.1f}" height="{(9.509-7.909-0.1)*S:.1f}" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="16 10"/>')
s.A(f'<rect x="{X(3.455)-16:.1f}" y="{Y(8.45):.1f}" width="10" height="{0.8*S:.1f}" fill="{ORANGE}"/><text x="{X(3.455)-24:.0f}" y="{Y(8.85):.0f}" text-anchor="end" font-size="20" fill="{ORANGE}">зеркало с подсв., h=1700</text>')
s.A(f'<text x="{X(5.5):.0f}" y="{Y(6.672)+150:.0f}" text-anchor="middle" font-size="21" fill="{ORANGE}">БП LED 24 В — в шкафу коридора у щита (доступ)</text>')
s.A(f'<rect x="{X(13.75):.1f}" y="{Y(7.491)-16:.1f}" width="{0.8*S:.1f}" height="10" fill="{ORANGE}"/><text x="{X(14.15):.0f}" y="{Y(7.491)-26:.0f}" text-anchor="middle" font-size="20" fill="{ORANGE}">зеркало с подсв., h=1800</text>')
for r in ROOMS: room_num(s, r, area=False)
s.explication("Светильники", [("Люстра (крюк, розетка Ø600)", lambda cx, cy: l_chand(cx, cy), count["chand"]), ("Подвесной светильник", lambda cx, cy: l_pend(cx, cy), count["pend"]),
    ("Точечный встраиваемый Ø80", lambda cx, cy: l_spot(cx, cy), count["spot"]), ("Круглый светильник Ø240", lambda cx, cy: l_disc(cx, cy), count.get("spot_disc", 0)), ("Бра настенное", lambda cx, cy: l_sconce(cx, cy + 8), count["sconce"]),
    ("Световая линия заподлицо, м", lambda cx, cy: s.A(f'<line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{INK}" stroke-width="12"/><line x1="{cx-27}" y1="{cy}" x2="{cx+27}" y2="{cy}" stroke="#FFE9A8" stroke-width="7"/>'), f'{count["frame"]:.1f}'.replace(".", ",") if count.get("frame") else ""),
    ("LED-лента 24 В", lambda cx, cy: s.A(f'<line x1="{cx-28}" y1="{cy}" x2="{cx+28}" y2="{cy}" stroke="{ORANGE}" stroke-width="4" stroke-dasharray="12 6"/>'), "")], colname="шт")
s.notes(["1. Привязка — от стены в чистоте", "    до оси светильника, мм.", "2. Мокрые зоны — споты IP44,", "    LED у зеркала IP44.", "3. LED-лента: блок питания в", "    доступном месте (люк/ниша).",
         "4. Кухня: 2 подвеса над столом,", "    подсветка рабочей зоны.", "5. Группы: C10, кабель 3×1,5;", "    выключатели — лист 12.", "6. Гостиная — 2 канала диммера", "    (рамка / периметр), без бра;", "    РЕЗЕРВ: 2 вывода под бра h=1600", "    и вывод в центр потолка (под", "    люстру) — в коробке, заглушены.", "    В каждой комнате — резервный", "    вывод в центр потолка 3×1,5.", "    4 сценария: ночь ~35 лк,", "    вечер ~170, обычный ~270,", "    максимум ~370 (норма 150)."])
s.save("s14_svet")

# ================================================================== План для развертки стен
s = Sheet("План для развертки стен", 0)
s.furniture(col="#D2CCC2"); s.walls()
for r in ROOMS:
    x0, x1, z0, z1 = r["rects"][0]; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    for i, side in enumerate(view_order(r["name"])):
        # маркер вида: кружок у стены, стрелка — к стене
        if side == "T": px, pz, ang = cx, z0 + 0.38, -90
        if side == "B": px, pz, ang = cx, z1 - 0.38, 90
        if side == "L": px, pz, ang = x0 + 0.38, cz, 180
        if side == "R": px, pz, ang = x1 - 0.38, cz, 0
        rad = 26 if min(x1 - x0, z1 - z0) < 1.8 else 34
        s.A(f'<g transform="translate({X(px):.1f},{Y(pz):.1f})"><path d="M{rad},0 L{rad+16},0" stroke="{BLUE}" stroke-width="4" transform="rotate({ang})"/><path d="M{rad+16},-9 L{rad+30},0 L{rad+16},9 Z" fill="{BLUE}" transform="rotate({ang})"/>'
            f'<circle r="{rad}" fill="#FFFFFF" stroke="{BLUE}" stroke-width="3"/><text y="{9 if rad < 30 else 11}" text-anchor="middle" font-size="{22 if rad < 30 else 27}" font-weight="bold" fill="{BLUE}">{r["num"]}.{i+1}</text></g>')
    s.A(f'<text x="{X(cx):.0f}" y="{Y(cz)+10:.0f}" text-anchor="middle" font-size="30" fill="#6B665C">{r["name"]}</text>')
s.explication("Развертки", [(f'{r["name"]}: виды {r["num"]}.1–{r["num"]}.4', None, "") for r in ROOMS], colname="")
s.notes(["1. Номер вида = № помещения.№ стены.", "2. Стрелка — направление взгляда.", "3. Смотреть вместе с листами", "    разверток."])
s.save("s15_razv_plan")

# ================================================================== Развертки жилых помещений
def auto_fix(rname, rect, side):
    """Окна, двери и мебель у стены -> элементы развертки (a0, a1, h0, h1, подпись, вид)."""
    out = []
    for (a0, a1, kind, ob) in openings(rect, side):
        if kind == "win": out.append((a0, a1, ob["sill"], ob["top"], "окно", "window"))
        else: out.append((a0, a1, 0, ob["h"], "проём" if ob["type"] == "open" else "дверь", "door"))
    x0, x1, z0, z1 = rect
    for f in FURN:
        fx0, fx1, fz0, fz1 = f["x"], f["x"] + f["w"], f["z"], f["z"] + f["d"]
        touch = {"T": abs(fz0 - z0) < 0.06, "B": abs(fz1 - z1) < 0.06, "L": abs(fx0 - x0) < 0.06, "R": abs(fx1 - x1) < 0.06}[side]
        inside = x0 - 0.05 <= fx0 and fx1 <= x1 + 0.05 and z0 - 0.05 <= fz0 and fz1 <= z1 + 0.05
        if touch and inside and f["kind"] not in ("sofa", "bed"):
            a0, a1 = (fx0, fx1) if side in "TB" else (fz0, fz1)
            nm = f["name"].split(" ")[0] if f["name"] else ""
            h0 = 0.25 if "подвесн" in f["name"] else 0          # подвесная тумба — от 250 над полом
            out.append((a0, a1, h0, f["h"] if not h0 else h0 + 0.3, nm, "low" if h0 else ("tv" if f["kind"] == "tv" else ("low" if f["h"] < 1.2 else "fix"))))
            if f["kind"] == "tv":   # ТВ на стене над тумбой
                m = (a0 + a1) / 2; out.append((m - 0.95, m + 0.95, 0.80, 1.87, "ТВ 85\"", "tv"))
                if next((r["style"] for r in ROOMS if r["name"] == rname), "") == "neo":   # ТВ в рамке молдинга
                    out.append((m - 1.12, m + 1.12, 0.68, 2.0, "", "molding"))
    return out
def neo_moldings(items, Lmin, Lmax, a_of):
    """Рамки-молдинги в свободных участках стены (неоклассика) + карниз."""
    busy = sorted([(min(a, b), max(a, b)) for (a, b, *_r) in items])
    free = []; cur = Lmin
    for (a, b) in busy:
        if a - cur > 0.7: free.append((cur, a))
        cur = max(cur, b)
    if Lmax - cur > 0.7: free.append((cur, Lmax))
    out = [(Lmin, Lmax, HCEIL - 0.12, HCEIL, "", "cornice")]
    for (a, b) in free:
        n = max(1, round((b - a) / 1.1))
        w = (b - a) / n
        for k in range(n):
            u0, u1 = a + k * w + 0.12, a + (k + 1) * w - 0.12
            out.append((u0, u1, 0.25, 0.85, "", "molding"))
            out.append((u0, u1, 1.05, HCEIL - 0.3, "", "molding"))
    return out
PATS = '''<pattern id="tile" width="30" height="30" patternUnits="userSpaceOnUse"><rect width="30" height="30" fill="#F6F2EC"/><path d="M30,0 V30 H0" fill="none" stroke="#DDD5CA" stroke-width="2"/></pattern>
<pattern id="bamboo" width="22" height="60" patternUnits="userSpaceOnUse"><rect width="22" height="60" fill="#EFE3CC"/><path d="M0,0 V60" stroke="#D9C7A6" stroke-width="2"/><path d="M4,30 H18" stroke="#E2D2B4" stroke-width="1.5"/></pattern>
<pattern id="paint_neo" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#F4EBDD"/></pattern>'''
def room_elev_sheet(fname, title, rname, notes):
    r = RBY[rname]; rect = tuple(r["rects"][0])
    global FIX
    s = Sheet(title, 0); add_defs(s, PATS)
    cells = [(260, 330), (1640, 330), (260, 1210), (1640, 1210)]
    rows = []
    for i, side in enumerate(view_order(rname)):
        items = auto_fix(rname, rect, side)
        if rname == "Прихожая" and side == "R":     # консоль + зеркало на светлой панели
            items = items + [(8.55, 8.95, 1.15, 1.85, "зеркало", "mirror")]
        if rname == "Прихожая" and side == "L":     # как в альбоме-образце: рейки под орех за скамьёй + крючки
            items = [(8.25, 9.35, 0.0, 2.65, "", "wood")] + items
        if r["style"] == "neo": items = items + neo_moldings(items, *( (rect[0], rect[1]) if side in "TB" else (rect[2], rect[3]) ), None)
        FIX[(rname, side)] = items
        Lw = wall_len(rect, side); sc = min(250, 800 / Lw)
        fill = "#F3F0EA" if r["style"] == "hall" else "#FFFFFF"   # прихожая: светлые гладкие панели (согласовано)
        elevation(s, rname, side, cells[i][0], cells[i][1], sc, f"Вид {r['num']}.{i+1} — {WALLRU[side]} стена", fill)
        rows.append((f"Вид {r['num']}.{i+1}: {WALLRU[side]} стена по плану", None, "", i + 1))
    if rname in CHECK:
        s.A(f'<text x="{(120+SX)/2:.0f}" y="245" text-anchor="middle" font-size="30" font-weight="bold" fill="{CHK}">Размеры помещения — под вопросом, уточнить после замера</text>')
    s.explication("Развертки", rows, colname="")
    s.notes(notes)
    if r["style"] == "neo": neo_details(s)
    s.save(fname)
def neo_details(s):
    """Узлы: А — профиль молдинга 70×24 (М 2:1), Б — лепной уголок ≈150×150."""
    ox, oy, k = 3120, 1250, 4200
    s.A(f'<text x="{ox-20}" y="{oy-150}" font-size="28" font-weight="bold" fill="{INK}">Узел А — профиль молдинга</text>')
    PRF = [(-0.035, 0), (-0.035, 0.005), (-0.030, 0.006), (-0.026, 0.008), (-0.022, 0.013), (-0.016, 0.018), (-0.010, 0.021), (-0.004, 0.022), (0.002, 0.020),
           (0.006, 0.015), (0.010, 0.012), (0.014, 0.013), (0.018, 0.016), (0.022, 0.016), (0.026, 0.012), (0.029, 0.008), (0.032, 0.006), (0.035, 0.004), (0.035, 0)]
    pts = " ".join(f"{ox + 160 + x*k:.0f},{oy - y*k:.0f}" for x, y in PRF)
    s.A(f'<polygon points="{pts}" fill="#F3EFE7" stroke="{INK}" stroke-width="3"/>')
    s.A(f'<line x1="{ox}" y1="{oy}" x2="{ox+320}" y2="{oy}" stroke="{INK}" stroke-width="3"/><text x="{ox+330}" y="{oy+8}" font-size="22" fill="#6B665C">стена</text>')
    s.A(f'<line x1="{ox+160-0.035*k:.0f}" y1="{oy+35}" x2="{ox+160+0.035*k:.0f}" y2="{oy+35}" stroke="{RED}" stroke-width="2"/><text x="{ox+160}" y="{oy+65}" text-anchor="middle" font-size="24" fill="{RED}">70</text>')
    s.A(f'<text x="{ox+160+0.035*k+14:.0f}" y="{oy-40}" font-size="24" fill="{RED}">24</text>')
    s.A(f'<text x="{ox-20}" y="{oy+110}" font-size="22" fill="#6B665C">полиуретан под покраску, в цвет стен</text>')
    bx, by = 3120, 1420
    s.A(f'<text x="{bx-20}" y="{by}" font-size="28" font-weight="bold" fill="{INK}">Узел Б — лепной уголок</text>')
    s.A(f'<path d="M{bx},{by+40} H{bx+260} M{bx},{by+40} V{by+300}" stroke="#A08C68" stroke-width="10" fill="none"/>')
    orn_corner(s.A, bx + 12, by + 52, 1, 1, 200, "#A08C68", 2.5)
    s.A(f'<text x="{bx+290}" y="{by+150}" font-size="22" fill="#6B665C">≈150×150,</text><text x="{bx+290}" y="{by+180}" font-size="22" fill="#6B665C">акант, во всех</text><text x="{bx+290}" y="{by+210}" font-size="22" fill="#6B665C">углах рамок</text>')
NEO_N = ["1. Стены — NCS S 1500-N (светло-", "    серый), моющаяся; молдинги в тон.", "2. Рамки: низ 250–850, верх", "    1050 — до карниза; профиль", "    70×24 (узел А), уголки-акант", "    во всех углах (узел Б).", "3. Карниз-галтель 120 мм, плинтус", "    высокий 120 мм.", "4. h розеток — от чистого пола.", "5. Шкаф — до h=2400."]
MOD_N = ["1. Стены: бамбуковые панели —", "    декор НЕ выбран.", "2. Плинтус — на согласование.", "3. h розеток — от чистого пола.", "4. Шкафы — до h=2400.", "5. ТВ на кронштейне h низа ~950."]
room_elev_sheet("s16_razv_gost", "Развертка стен гостиной", "Гостиная", NEO_N)
room_elev_sheet("s17_razv_komn", "Развертка стен комнаты", "Комната", MOD_N)
room_elev_sheet("s18_razv_sp2", "Развертка стен спальни 2", "Спальня 2", MOD_N)
room_elev_sheet("s19_razv_kor", "Развертка стен коридора", "Коридор", MOD_N)
HALL_N = ["1. Стены — бамбуковые панели", "    Dekorchi, светло-серые гладкие;", "    без молдингов и лепнины.", "2. За скамьёй — рифлёные рейки", "    под орех 1100, до потолка,", "    крючки h=1700 (как в образце).", "3. Скамья-обувница — тёмная.", "4. Консоль + зеркало напротив.", "5. h розеток — от чистого пола."]
room_elev_sheet("s20_razv_prih", "Развертка стен прихожей", "Прихожая", HALL_N)

# ================================================================== Ведомость отделки
s = Sheet("Ведомость отделки помещений", 0)
cols = [150, 230, 480, 980, 1180, 1900, 2120, 2700, 2880]
heads = ["№", "Помещение", "Пол", "м²", "Стены", "м²", "Потолок", "м²", ""]
y = 300
s.A(f'<rect x="150" y="{y}" width="2830" height="{70 + len(ROOMS)*120}" fill="none" stroke="{INK}" stroke-width="3"/>')
for c, h in zip(cols, heads): s.A(f'<text x="{c+12}" y="{y+45}" font-size="28" font-weight="bold" fill="{INK}">{h}</text>')
for c in cols[1:-1]: s.A(f'<line x1="{c}" y1="{y}" x2="{c}" y2="{y+70+len(ROOMS)*120}" stroke="{INK}" stroke-width="1.5"/>')
y += 70; T = {"floor": 0, "wall": 0, "ceil": 0}
for r in ROOMS:
    rect = r["rects"][0]; hc = ceil_h(r)
    per = room_perim(r); af = room_area(r)
    op = sum((a1 - a0) * ((ob["top"] - ob["sill"]) if k == "win" else ob["h"]) for sd in "TBLR" for (a0, a1, k, ob) in openings(rect, sd))
    aw = per * hc - op
    st = STYLE[r["style"]]
    wt = "Фартук — керамогранит; стены — на согласование" if r["name"] == "Кухня" else st["walls"]
    ct = st["ceiling"].split(";")[0] + f", h={int(hc*1000)}"
    T["floor"] += af; T["wall"] += aw; T["ceil"] += af
    s.A(f'<line x1="150" y1="{y}" x2="2980" y2="{y}" stroke="{INK}" stroke-width="1.5"/>')
    def wrap(t, n):
        out, cur = [], ""
        for w_ in t.split(" "):
            if len(cur) + len(w_) + 1 > n: out.append(cur); cur = w_
            else: cur = (cur + " " + w_).strip()
        return out + [cur]
    q = " ?" if r["name"] in CHECK else ""
    for c, t, n in ((cols[0], str(r["num"]), 5), (cols[1], r["name"], 14), (cols[2], FLOORS[r["floor"]]["name"], 28), (cols[3], f2(af) + q, 10),
                    (cols[4], wt, 40), (cols[5], f2(aw) + q, 10), (cols[6], ct, 32), (cols[7], f2(af) + q, 10)):
        for k, ln in enumerate(wrap(t, n)[:3]):
            s.A(f'<text x="{c+12}" y="{y+40+k*32}" font-size="25" fill="{CHK if (q and "?" in t) else INK}">{ln}</text>')
    y += 120
s.A(f'<text x="{cols[2]+12}" y="{y+50}" font-size="28" font-weight="bold" fill="{INK}">ИТОГО</text><text x="{cols[3]+12}" y="{y+50}" font-size="28" font-weight="bold" fill="{INK}">{f2(T["floor"])}</text><text x="{cols[5]+12}" y="{y+50}" font-size="28" font-weight="bold" fill="{INK}">{f2(T["wall"])}</text><text x="{cols[7]+12}" y="{y+50}" font-size="28" font-weight="bold" fill="{INK}">{f2(T["ceil"])}</text>')
s.ty = 130
s.notes(["1. Площади — в чистоте, расчётные", "    по геометрии проекта; стены —", "    за вычетом окон и дверей.", "2. «?» — до контрольного замера.", "3. Закупка с запасом: плитка +10%,", "    краска — 2 слоя, панели +5%.",
         "4. Мокрые зоны: керамогранит", "    до потолка, гидроизоляция", "    пола + 200 мм на стены,", "    в душе — 2000.", "5. Кухня: фартук 900–1500", "    керамогранит 60×120."])
s.save("s21_otdelka")

# ================================================================== Материалы: что согласовано
s = Sheet("Материалы и палитра", 0)
DEC = [("Пол — вся квартира, кроме кухни и мокрых зон", "Доска палубная, беленый дуб 2 тона через раз («почти как стены»)", "согласовано, образцы — подобрать в магазине"), ("Гостиная — стиль", "Неоклассика, вариант 2 «бакинская»", "согласовано"), ("Гостиная — цвет стен", "NCS S 1500-N (светло-серый, ПЕРЕСОГЛАСОВАНО 11.2026 под зелёную мебель; было NCS S 1002-Y), моющаяся краска; молдинги в тон", "согласовано; перед покупкой — выкрас"),
       ("Кухня, ванная, санузел", "Только итальянский керамогранит 60×120 под мрамор", "согласовано, коллекция не выбрана"),
       ("Травертин", "Исключён везде", "исключён"),
       ("Комната, спальня 2, коридор, прихожая — стены", "Бамбуковые панели (Dekorchi)", "декор НЕ выбран"),
       ("Гостиная — мебель", "Диван — существующий заказчика (зелёный бархат, стёжка «каналы»), 2 «ушастых» кресла в том же бархате (каталог №8), «буквой П»; стол овал 1200×700, мрамор; ТВ-тумба подвесная 1800, в цвет стен, ТВ в рамке молдинга; шторы: тюль + плотные тёмно-зелёные, потолок–пол; ковёр молочный однотонный; без бра", "согласовано, модели — подобрать"),
       ("Потолки", "—", "НЕ согласовано"), ("Цвета стен, фасадов, тканей", "—", "НЕ согласовано"), ("Сантехника, смесители, фурнитура", "—", "НЕ согласовано")]
y = 300; cols = [200, 1150, 2250]
for c, h in zip(cols, ["Позиция", "Решение", "Статус"]): s.A(f'<text x="{c}" y="{y}" font-size="32" font-weight="bold" fill="{INK}">{h}</text>')
for i, (a, b, c_) in enumerate(DEC):
    yy = y + 40 + i * 90
    s.A(f'<line x1="200" y1="{yy}" x2="2950" y2="{yy}" stroke="#CFC9BE" stroke-width="2"/>')
    col = GREEN if c_.startswith("согласовано") else (RED if c_ == "исключён" else ORANGE)
    s.A(f'<text x="{cols[0]}" y="{yy+55}" font-size="30" fill="{INK}">{a}</text><text x="{cols[1]}" y="{yy+55}" font-size="30" fill="{INK}">{b}</text><text x="{cols[2]}" y="{yy+55}" font-size="30" font-weight="bold" fill="{col}">{c_}</text>')
s.ty = 130
s.notes(["Текстуры и цвета на листах", "НЕ показаны, пока не согласованы.", "", "Нужно от заказчика:", "  — декор бамбуковых панелей", "    (скрины Dekorchi);", "  — пол в комнатах и коридоре;", "  — коллекция керамогранита;", "  — примеры стиля гостиной."])
s.save("s22_materialy")

# ================================================================== Визуализации
import base64 as _b64, io as _io
VZ = os.path.join(PROJ, "08_vizualizacii")
SH = [("gostinaya/_kremA_1_ot_dveri_k_oknu", "Гостиная", "от двери к окну"), ("gostinaya/_kremA_2_ot_okna_k_dveri", "Гостиная", "от окна к двери"),
      ("gostinaya/_kremA_3_divan_i_kresla", "Гостиная", "диван и кресла"), ("gostinaya/_kremA_4_tv_zona", "Гостиная", "ТВ-зона"),
      ("gostinaya/_kremA_5_obshchiy_sverhu", "Гостиная", "общий вид"),
      ("gostinaya/_kremA_7_kreslo", "Гостиная", "кресло и столик"), ("gostinaya/_kremA_6_detal_steny", "Гостиная", "деталь стены"),
      ("gostinaya/_kremA_8_potolok", "Гостиная", "потолок"), ("gostinaya/_kremA_9_ugol_potolka", "Гостиная", "угол потолка"),
      ("komnata/1_ot_dveri_k_oknu", "Вторая гостиная", "от двери к окну"), ("komnata/2_ot_okna_k_shkafu", "Вторая гостиная", "от окна к шкафу"),
      ("komnata/3_tv_zona", "Вторая гостиная", "ТВ-зона"),
      ("spalnya2/1_ot_dveri_k_krovati", "Спальня 2", "от двери к кровати"), ("spalnya2/3_krovat_pryamo", "Спальня 2", "кровать и изголовье"),
      ("spalnya2/2_ot_okna_k_shkafu", "Спальня 2", "от окна к шкафу и ТВ"),
      ("spalnya2/4_prohod_v_lodzhiyu", "Спальня 2", "проход в лоджию Б"),
      ("koridor/1_koridor_k_prihozhey", "Коридор", "вид к прихожей"), ("koridor/2_vhodnaya_dver", "Прихожая", "входная дверь, обувница"),
      ("koridor/4_prihozhaya_gosti", "Прихожая", "шкаф и место для гостей"), ("koridor/3_prihozhaya_zerkalo", "Прихожая", "обувница и зеркало"),
      ("vannaya/1_ot_dveri", "Ванная", "от двери: унитаз, ванна"), ("vannaya/2_rakovina_stiralka", "Ванная", "раковина и стиральная машина"),
      ("vannaya/3_vanna", "Ванная", "ванна 1300"), ("vannaya/4_k_dveri", "Ванная", "вид к двери"),
      ("sanuzel/1_ot_dveri", "Санузел", "от двери: биде и унитаз"), ("sanuzel/2_dush_rakovina", "Санузел", "душ и раковина"),
      ("sanuzel/3_bak_bide", "Санузел", "пенал бака 200 л и биде"), ("sanuzel/4_iz_dusha", "Санузел", "вид из душа"),
      ("kuhnya/1_ot_vhoda", "Кухня", "от входа"), ("kuhnya/2_rabochaya_zona", "Кухня", "рабочая зона"),
      ("kuhnya/3_stolovaya", "Кухня", "банкетка и стол"), ("kuhnya/4_ot_okna", "Кухня", "от окна к входу")]
for k, (fn, room, cap) in enumerate(SH, 1):        # как в образце: один ракурс — один лист, картинка на весь лист
    s = Sheet("", 0)
    f = os.path.join(VZ, fn + ".jpg")
    if os.path.exists(f):
        from PIL import Image as _I
        im = _I.open(f).convert("RGB"); im.thumbnail((2600, 2600)); bf = _io.BytesIO(); im.save(bf, "JPEG", quality=88)
        s.A(f'<image x="125" y="45" width="{SX-130}" height="{H-90}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{_b64.b64encode(bf.getvalue()).decode()}"/>')
    s.A(f'<rect x="{SX}" y="40" width="{W-40-SX}" height="{H-80}" fill="#FFFFFF"/>')
    s.A(f'<text x="{(SX+W-40)/2:.0f}" y="200" text-anchor="middle" font-size="40" fill="{INK}">{room}</text>')
    s.A(f'<text x="{(SX+W-40)/2:.0f}" y="260" text-anchor="middle" font-size="32" fill="#6B665C">{cap}</text>')
    s.title = f"Визуализация — {room.lower()}, {cap}"
    s.save(f"s23_vizual_{k}")

# ================================================================== Прихожая: варианты планировки (на выбор заказчика)
s = Sheet("Прихожая — варианты планировки", 0)
PR = RBY["Прихожая"]["rects"][0]; px0_, px1_, pz0_, pz1_ = PR
ENT = next(d for d in DOORS if d["type"] == "entry")["rect"]
SHIT_Z = 8.15
VAR = [
 ("А", "Как сейчас", [((1.945, 8.364, 0.291, 1.091), "обувница", "low"), ((2.909, 8.400, 0.546, 1.055), "шкаф", "tall")],
  ["Проход между мебелью ~670 —", "уже входной двери (890).", "Двоим не разойтись,", "детей не обуть сидя."]),
 ("Б", "Шкаф на правую стену", [((3.005, 7.909, 0.450, 1.290), "шкаф до потолка 450×1290", "tall"), ((1.945, 8.70, 0.35, 0.55), "банкетка откидная", "fold")],
  ["Максимум хранения у входа.", "Щит — внутри шкафа", "(отдельная дверца, доступ).", "Проход ~1030, с открытой", "банкеткой ~710."]),
 ("В", "ВЫБРАН — открытая прихожая", [((1.945, 8.35, 0.35, 0.90), "скамья-обувница + крючки", "low"), ((3.205, 8.40, 0.25, 0.70), "консоль + зеркало", "low")],
  ["Самый широкий проход ~910.", "Верхняя одежда — в шкаф-купе", "коридора (3580 уже есть).", "Детские крючки на h=1000.", "Консоль ниже щита — щит", "свободен; до двери 260."]),
]
FC = {"low": "#F3EFE7", "tall": "#E6E1D8", "fold": "none", "mirror": "#DDE6EA"}
sc = 420.0; rx0, rz0, rx1, rz1 = px0_ - 0.25, pz0_ - 0.35, px1_ + 0.25, pz1_ + 0.30
for k, (letter, name, items, pros) in enumerate(VAR):
    S = sc; OX = 200 + k * 940 - rx0 * sc; OY = 400 - rz0 * sc
    s.A(f'<clipPath id="pv{k}"><rect x="{X(rx0):.0f}" y="{Y(rz0):.0f}" width="{(rx1-rx0)*S:.0f}" height="{(rz1-rz0)*S:.0f}"/></clipPath>')
    s.A(f'<g clip-path="url(#pv{k})">'); s.walls(); s.A('</g>')
    chosen = name.startswith("ВЫБРАН")
    s.A(f'<text x="{X(rx0):.0f}" y="{Y(rz0)-30:.0f}" font-size="46" font-weight="bold" fill="{GREEN if chosen else INK}">Вариант {letter}</text><text x="{X(rx0)+250:.0f}" y="{Y(rz0)-30:.0f}" font-size="32" font-weight="{"bold" if chosen else "normal"}" fill="{GREEN if chosen else "#6B665C"}">{name}</text>')
    if chosen: s.A(f'<rect x="{X(rx0)-24:.0f}" y="{Y(rz0)-90:.0f}" width="{(rx1-rx0)*S+48:.0f}" height="{(rz1-rz0)*S+560:.0f}" rx="16" fill="none" stroke="{GREEN}" stroke-width="5"/>')
    for (x, z, w, d), lab, kind in items:
        dash = ' stroke-dasharray="12 8"' if kind == "fold" else ""
        s.A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="{FC[kind]}" stroke="#6B665C" stroke-width="3"{dash}/>')
        cx, cz = x + w / 2, z + d / 2
        rot = f' transform="rotate(-90 {X(cx):.0f} {Y(cz):.0f})"' if d > w else ""
        s.A(f'<text x="{X(cx):.0f}" y="{Y(cz)+8:.0f}" text-anchor="middle" font-size="22" fill="{INK}"{rot}>{lab}</text>')
    # проход: между самыми выступающими предметами слева и справа
    left = max([x + w for (x, z, w, d), _, kd in items if x < 2.4 and kd != "mirror"] + [px0_])
    right = min([x for (x, z, w, d), _, kd in items if x > 2.4] + [px1_])
    ok = (right - left) >= 0.8
    chain(s, [px0_, left, right, px1_], 8.95, True, GREEN if ok else RED, side=-1, fs=24)
    s.A(f'<text x="{X((left+right)/2):.0f}" y="{Y(8.95)+42:.0f}" text-anchor="middle" font-size="24" font-weight="bold" fill="{GREEN if ok else RED}">проход</text>')
    # щит и входная дверь
    s.A(f'<rect x="{X(px1_)-14:.1f}" y="{Y(SHIT_Z)-30:.1f}" width="14" height="60" fill="{INK}"/><text x="{X(px1_)+10:.0f}" y="{Y(SHIT_Z)+8:.0f}" font-size="22" fill="{INK}">щит</text>')
    s.A(f'<text x="{X(ENT[0]+ENT[2]/2):.0f}" y="{Y(ENT[1]+ENT[3])+40:.0f}" text-anchor="middle" font-size="24" fill="{INK}">вход</text>')
    chain(s, [pz0_, pz1_], px0_ - 0.15, False, CHK, side=-1, fs=24)
    for i, ln in enumerate(pros):
        s.A(f'<text x="{X(rx0):.0f}" y="{Y(rz1)+110+i*44:.0f}" font-size="30" fill="{INK}">{ln}</text>')
S, OX, OY = 168.0, 230, 300
s.explication("Нужно решить заказчику", [("Вариант планировки: В — ВЫБРАН", None, "✓"), ("Сколько пар обуви хранить у входа", None, ""),
    ("Пол прихожей: как в коридоре или отдельный", None, ""), ("Отделка стен и фасадов", None, ""), ("Нужна ли банкетка (обувать детей)", None, "")], colname="")
s.notes(["Только планировка — без текстур", "и цветов (их выбирает заказчик).", "Размеры прихожей 1510×1600 —", "под вопросом до замера.", "Зелёный проход ≥800 — удобно;", "красный — тесно.",
         "Щит h=1500 — доступ обязателен.", "", "Мебель не заходит в проём", "входной двери 890."])
s.save("s24_prih_var")
print("новые листы готовы")

# ================================================================== Схема щита (12.11.2026)
s = Sheet("Схема щита — группы, автоматы, кабели", 0)
G = [  # гр, назначение, аппарат, кабель, кВт
 ("ВВОД", "Вводной автомат 2P + реле напряжения", "C40 2P + РН 50 А", "по ТУ ввода", "≈11 расч."),
 ("УЗО-1", "Розетки сухих комнат (гр. 4–7)", "УЗО 40 А / 30 мА", "—", ""),
 ("1", "Свет: гостиная, комната, коридор, прихожая", "C10", "ВВГнг(А)-LS 3×1,5", "0,5"),
 ("2", "Свет: кухня, спальня 2, ванная, санузел", "C10", "3×1,5", "0,4"),
 ("3", "LED 24 В: паз коридора/прихожей, гостиная (БП)", "C10", "3×1,5", "0,3"),
 ("4", "Розетки: гостиная + коридор", "C16 (через УЗО-1)", "3×2,5", "2,0"),
 ("5", "Розетки: комната", "C16 (через УЗО-1)", "3×2,5", "2,0"),
 ("6", "Розетки: спальня 2", "C16 (через УЗО-1)", "3×2,5", "2,0"),
 ("7", "Розетки: прихожая (зеркало, сушилка, пылесос)", "C16 (через УЗО-1)", "3×2,5", "1,0"),
 ("8", "Кухня: розетки над столешницей (3 блока)", "Дифавт. C16 / 30 мА", "3×2,5", "3,0"),
 ("9", "Кухня: холодильник + микроволновка", "Дифавт. C16 / 30 мА", "3×2,5", "1,5"),
 ("10", "Кухня: посудомоечная машина", "Дифавт. C16 / 30 мА", "3×2,5", "2,0"),
 ("11", "Кухня: духовой шкаф", "Дифавт. C16 / 30 мА", "3×2,5", "3,0"),
 ("12", "Кухня: индукционная варочная панель", "Дифавт. C32 / 30 мА", "3×6", "7,0"),
 ("13", "Стиральная машина (ванная)", "Дифавт. C16 / 30 мА", "3×2,5", "2,2"),
 ("14", "Бойлер 80 л — ванная", "Дифавт. C16 / 30 мА", "3×2,5", "2,0"),
 ("15", "Бойлер 80 л — санузел + насосная станция бака", "Дифавт. C16 / 30 мА", "3×2,5", "2,5"),
 ("16", "Ванная + санузел: фен, полотенцесушители", "Дифавт. C16 / 30 мА", "3×2,5", "1,5"),
 ("17", "Тёплый пол — ванная (мат ≈2,0 м²)", "Дифавт. C16 / 30 мА", "3×2,5", "0,3"),
 ("18", "Тёплый пол — санузел (мат ≈2,5 м²)", "Дифавт. C16 / 30 мА", "3×2,5", "0,4"),
 ("19", "Кондиционер — гостиная", "C16", "3×2,5", "1,5"),
 ("20", "Кондиционер — комната", "C16", "3×2,5", "1,5"),
 ("21", "Кондиционер — спальня 2", "C16", "3×2,5", "1,2"),
 ("22", "Кондиционер — кухня", "C16", "3×2,5", "1,2"),
 ("23–24", "РЕЗЕРВ (2 места в щите)", "C16", "—", ""),
]
cx = [170, 380, 1500, 2150, 2700]; y0 = 280; rh = 64
s.A(f'<rect x="150" y="{y0}" width="2820" height="{rh}" fill="#EEE9E0" stroke="{INK}" stroke-width="2"/>')
for x, t in zip(cx, ["Группа", "Назначение", "Аппарат защиты", "Кабель", "кВт"]):
    s.A(f'<text x="{x}" y="{y0+43}" font-size="30" font-weight="bold" fill="{INK}">{t}</text>')
for i, row in enumerate(G):
    y = y0 + rh * (i + 1)
    bg = "#FFF6E6" if row[0] in ("ВВОД", "УЗО-1") else ("#F7F9FB" if i % 2 else "#FFFFFF")
    s.A(f'<rect x="150" y="{y}" width="2820" height="{rh}" fill="{bg}" stroke="#CFC9BF" stroke-width="1.5"/>')
    for x, t in zip(cx, row):
        s.A(f'<text x="{x}" y="{y+43}" font-size="28" fill="{INK}">{t}</text>')
s.explication("Щит", [("Модулей в щите (с резервом 20%)", None, "≈48"), ("Дифавтоматов 30 мА", None, 11), ("Автоматов C10", None, 3), ("Автоматов C16", None, 9), ("Автомат C32", None, 1), ("УЗО 40 А / 30 мА", None, 1)], colname="шт")
s.notes(["1. Щит в прихожей, h=1500 (низ", "    1300), рядом слаботочный.", "2. Вся медь, ВВГнг(А)-LS; свет 3×1,5,", "    розетки 3×2,5, плита 3×6.", "3. Мокрые зоны, кухня, тёплый пол —", "    только через дифавтомат 30 мА.",
         "4. Тёплый пол: электрический мат", "    150 Вт/м², терморегулятор h=900", "    снаружи, датчик в гофре.", "5. Слаботочка: от слаботочного щита", "    UTP cat.6 к каждому ТВ (3) + роутер", "    (центр коридора, h=2200), RG-6 к ТВ,",
         "    кабель домофона к входной двери.", "6. Мощности плиты/духовки уточнить", "    по моделям — при >7 кВт плита", "    3×10, автомат C40.", "7. Кабели не в одной штробе с", "    слаботочкой (≥100 мм)."])
s.save("s3b_shchit")


# ================================================================== Схема кондиционеров: вся квартира (12.11.2026)
s = Sheet("", 0)
_f = os.path.join(PROJ, "01_chertezhi", "shema_vse_kond.png")
if os.path.exists(_f):
    from PIL import Image as _I
    import base64 as _b64b, io as _iob
    _im = _I.open(_f).convert("RGB"); _im.thumbnail((2900, 2900)); _bf = _iob.BytesIO(); _im.save(_bf, "JPEG", quality=90)
    s.A(f'<image x="130" y="50" width="{SX-140}" height="{H-100}" preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,{_b64b.b64encode(_bf.getvalue()).decode()}"/>')
s.ty = 130
s.notes(["Наружные блоки:", "  лоджия А (из второй гостиной):", "  Н1 гостиная, Н2 вторая гостиная,", "  Н4 кухня;", "  лоджия Б (из спальни 2):", "  Н3 спальня 2.",
         "", "Питание: группы 19–22 щита,", "  C16, кабель 3×2,5, розетка", "  h=2200 сбоку от блока.", "Трассы фреон + дренаж под", "  потолком, уклон дренажа ≥1%."])
s.title = "Кондиционеры — схема квартиры"
s.save("s6b_kond_shema")


# ================================================================== Ванная и санузел: расстановка по реальным размерам (13.11.2026)
s = Sheet("", 0)
_f = os.path.join(PROJ, "01_chertezhi", "shema_vanna.png")
if os.path.exists(_f):
    from PIL import Image as _I
    import base64 as _b64b, io as _iob
    _im = _I.open(_f).convert("RGB"); _im.thumbnail((2900, 2900)); _bf = _iob.BytesIO(); _im.save(_bf, "JPEG", quality=90)
    s.A(f'<image x="130" y="50" width="{SX-140}" height="{H-100}" preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,{_b64b.b64encode(_bf.getvalue()).decode()}"/>')
s.ty = 130
s.notes(["Ванная: раковина 600 с открытой", "  полкой, стиралка 10 кг слева,", "  ванна 1300×700, унитаз + гиг. душ,", "  бойлер Б1 в шкафу над унитазом.",
         "Санузел: душ 700×900, раковина", "  на верхней стене, биде, унитаз,", "  бойлер Б2 над унитазом,", "  бак 200 л — узкий под заказ", "  520×220×2000 в пенале.",
         "", "Места для ног ≥ 600 (кроме", "  биде — 559). Двери мокрых зон", "  лучше наружу.", "Бойлеры Ariston Lydos Eco 80 V", "  (≈Ø450×760) — сверить паспорт."])
s.title = "Ванная и санузел — расстановка"
s.save("s5b_vanna_shema")
