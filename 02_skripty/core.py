"""Ядро альбома: данные квартиры (из data/kvartira.json) + класс листа Sheet + общие условные знаки.
Все листы исполняются в ОДНОМ пространстве имён (build.py), поэтому могут менять S/OX/OY/FS для крупных фрагментов."""
import json, os, math
ROOT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "data", "kvartira.json"), encoding="utf-8"))
META = D["meta"]; HCEIL = META["ceiling_h"]

# ---------- геометрия в «старом» формате, который понимают листы
G = {"walls": D["walls"], "windows": [w["rect"] for w in D["windows"]]}
ROOMS = D["rooms"]; RBY = {r["name"]: r for r in ROOMS}
rooms = {r["name"]: tuple(r["rects"][0]) for r in ROOMS}          # главный прямоугольник: x0, x1, z0, z1
SK = [tuple(x) for x in D["sockets"]]
FURN = D["furniture"]
furn = [(f["x"], f["z"], f["w"], f["d"]) for f in FURN]
DOORS = D["doors"]; WINDOWS = D["windows"]

def room_area(r):            # площадь в чистоте по прямоугольникам, м²
    return sum((x1 - x0) * (z1 - z0) for x0, x1, z0, z1 in r["rects"])
def room_perim(r):           # периметр главного прямоугольника + ниш (приближённо)
    x0, x1, z0, z1 = r["rects"][0]; p = 2 * ((x1 - x0) + (z1 - z0))
    for (a0, a1, b0, b1) in r["rects"][1:]: p += 2 * max(a1 - a0, b1 - b0)
    return p
def f2(v): return f"{v:.2f}".replace(".", ",")
def mm(v): return f"{round(v * 1000 / 5) * 5:,}".replace(",", " ")
AREA = [(r["name"], f2(room_area(r)), r["num"]) for r in ROOMS]
AREA_TOTAL = sum(room_area(r) for r in ROOMS)
NUM = {r["name"]: r["num"] for r in ROOMS}
NPOS = {r["name"]: tuple(r["label"]) for r in ROOMS}
CHECK = {r["name"] for r in ROOMS if r.get("status") == "check"}
def expl_rows():
    return [(a, None, b, n) for a, b, n in AREA] + [("ИТОГО в чистоте", None, f2(AREA_TOTAL), ""), (f"по застройщику (со стенами)", None, f2(META["area_developer"]), "")]

# ---------- нумерация листов задаётся в build.py (SHEETS); здесь значения по умолчанию
SHEET_NO = {}; LISTOV = 1; DONE = []
OUT_SVG = os.path.join(ROOT, "out", "svg")
P = 55.0; S = 168.0; OX, OY = 230, 300
X = lambda m: OX + m * S
Y = lambda m: OY + m * S
INK = "#1E1D1A"; FURN_C = "#9C968C"; RED = "#D0312D"; BLUE = "#1F5FA8"; GREEN = "#2E7D4F"; ORANGE = "#C27A12"
FURNC = FURN_C
PURP = "#6C4BB0"; BROWN = "#7A4B22"; W, H = 3840, 2160; SX = 3020
FS = 1.0
FONT = "PT Sans, DejaVu Sans, Arial, sans-serif"
INW = {"L": (1, 0), "R": (-1, 0), "T": (0, 1), "B": (0, -1)}
class Sheet:
    def __init__(s, title, no):
        s.o = []; s.title = title; s.no = no
        A = s.A
        A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
        A('<defs><pattern id="hatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="14" height="14" fill="#6E6A63"/><line x1="0" y1="0" x2="0" y2="14" stroke="#3C3A36" stroke-width="4"/></pattern>'
          f'<marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker></defs>')
        A(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
        A(f'<rect x="120" y="40" width="{W-160}" height="{H-80}" fill="none" stroke="{INK}" stroke-width="5"/>')
        A(f'<line x1="{SX}" y1="40" x2="{SX}" y2="{H-40}" stroke="{INK}" stroke-width="4"/>')
        A(f'<text x="{(120+SX)/2:.0f}" y="180" text-anchor="middle" font-size="76" fill="{INK}">{title}</text>')
    def A(s, t): s.o.append(t)
    # ---------- base layers
    def furniture(s, fill="none", col=FURNC, sw=2.5):
        A = s.A
        for (x, z, w, d) in furn:
            A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
        s.toilet(1.43, 9.018, col=col); s.toilet(0.71, 9.018, col=ORANGE, sw=5)
        s.toilet_r(8.415, 6.073, col=col)          # 13.11: в ванной один унитаз (+ гиг. душ)
        s.highitems()
        A(f'<rect x="{X(1.058):.1f}" y="{Y(6.80):.1f}" width="{0.50*S:.1f}" height="{0.42*S:.1f}" rx="10" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')   # раковина санузла (верхняя стена)
        A(f'<rect x="{X(3.564):.1f}" y="{Y(8.06):.1f}" width="{0.48*S:.1f}" height="{0.60*S:.1f}" rx="10" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')  # раковина ванной
        A(f'<rect x="{X(686/P):.1f}" y="{Y(112/P):.1f}" width="{25/P*S:.1f}" height="{32/P*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        for cy in (122, 136):
            A(f'<circle cx="{X(698.5/P):.1f}" cy="{Y(cy/P):.1f}" r="15" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        A(f'<rect x="{X(686/P):.1f}" y="{Y(180/P):.1f}" width="{25/P*S:.1f}" height="{30/P*S:.1f}" rx="10" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        A(f'<circle cx="{X(215.5/P):.1f}" cy="{Y(468.5/P):.1f}" r="36" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    def toilet(s, ax, wallz, col=FURNC, sw=2.5, w=0.36, d=0.55):
        x0 = ax - w / 2
        s.A(f'<rect x="{X(x0):.1f}" y="{Y(wallz-0.16):.1f}" width="{w*S:.1f}" height="{0.16*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        s.A(f'<ellipse cx="{X(ax):.1f}" cy="{Y(wallz-0.16-(d-0.16)/2):.1f}" rx="{w/2*S:.1f}" ry="{(d-0.16)/2*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    def highitems(s):
        A = s.A; C = "#B03A2E"
        # 13.11: бойлеры Ø450 над унитазами (пунктир — висят высоко), бак 200 л под заказ — пенал у левой стены санузла
        for (bx, bz, t) in ((6.073 - 0.275, 8.42, "Б1"), (1.43, 9.018 - 0.275, "Б2")):
            A(f'<circle cx="{X(bx):.1f}" cy="{Y(bz):.1f}" r="{0.225*S:.1f}" fill="none" stroke="{C}" stroke-width="5" stroke-dasharray="14 8"/>')
            A(f'<text x="{X(bx):.0f}" y="{Y(bz)+8:.0f}" text-anchor="middle" font-size="22" font-weight="bold" fill="{C}">{t}</text>')
        A(f'<rect x="{X(0.309):.1f}" y="{Y(7.74):.1f}" width="{0.24*S:.1f}" height="{0.52*S:.1f}" fill="#E3EEF8" stroke="{BLUE}" stroke-width="5"/>')
        if S < 300: A(f'<text x="{X(0.43):.0f}" y="{Y(8.00)+9:.0f}" text-anchor="middle" font-size="20" font-weight="bold" fill="{BLUE}">бак</text>')
    def toilet_r(s, az, wallx, col=FURNC, sw=2.5, w=0.36, d=0.55):
        z0 = az - w / 2
        s.A(f'<rect x="{X(wallx-0.16):.1f}" y="{Y(z0):.1f}" width="{0.16*S:.1f}" height="{w*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        s.A(f'<ellipse cx="{X(wallx-0.16-(d-0.16)/2):.1f}" cy="{Y(az):.1f}" rx="{(d-0.16)/2*S:.1f}" ry="{w/2*S:.1f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    def walls(s):
        A = s.A
        for (x, z, w, d) in G["windows"]:
            A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>')
            if w > d: A(f'<line x1="{X(x):.1f}" y1="{Y(z+d/2):.1f}" x2="{X(x+w):.1f}" y2="{Y(z+d/2):.1f}" stroke="{INK}" stroke-width="2"/>')
            else: A(f'<line x1="{X(x+w/2):.1f}" y1="{Y(z):.1f}" x2="{X(x+w/2):.1f}" y2="{Y(z+d):.1f}" stroke="{INK}" stroke-width="2"/>')
        for (x, z, w, d) in G["walls"]:
            A(f'<rect x="{X(x):.1f}" y="{Y(z):.1f}" width="{w*S:.1f}" height="{d*S:.1f}" fill="url(#hatch)" stroke="{INK}" stroke-width="1.5"/>')
    def numbers(s, names=False):
        for n, (cx, cy) in NPOS.items():
            s.A(f'<circle cx="{X(cx):.0f}" cy="{Y(cy):.0f}" r="34" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/><text x="{X(cx):.0f}" y="{Y(cy)+14:.0f}" text-anchor="middle" font-size="38" fill="{INK}">{NUM[n]}</text>')
            if names:
                yy = Y(cy) - 50 if n in ("Санузел", "Прихожая") else Y(cy) + 80
                s.A(f'<text x="{X(cx):.0f}" y="{yy:.0f}" text-anchor="middle" font-size="32" fill="#6B665C">{n}</text>')
    # ---------- helpers
    def wp(s, room, wall, a):
        x0, x1, z0, z1 = rooms[room][:4]
        return {"L": (X(x0), Y(a)), "R": (X(x1), Y(a)), "T": (X(a), Y(z0)), "B": (X(a), Y(z1))}[wall]
    def tick(s, x, y):
        s.A(f'<line x1="{x-12:.1f}" y1="{y+12:.1f}" x2="{x+12:.1f}" y2="{y-12:.1f}" stroke="{BLUE}" stroke-width="3"/>')
    def dtext(s, x, y, t, vertical):
        if vertical: s.A(f'<text x="{x:.0f}" y="{y:.0f}" transform="rotate(-90 {x:.0f} {y:.0f})" text-anchor="middle" font-size="{27*FS:.0f}" fill="{RED}">{t}</text>')
        else: s.A(f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="middle" font-size="{27*FS:.0f}" fill="{RED}">{t}</text>')
    def chain(s, room, wall, pts, inset=26):
        x0, x1, z0, z1 = rooms[room][:4]
        seq = [z0 if wall in "LR" else x0] + sorted(pts)
        if wall in "LR":
            lx = X(x0) + inset if wall == "L" else X(x1) - inset
            s.A(f'<line x1="{lx:.1f}" y1="{Y(seq[0]):.1f}" x2="{lx:.1f}" y2="{Y(seq[-1]):.1f}" stroke="{RED}" stroke-width="2.5"/>')
            for v in seq: s.tick(lx, Y(v))
            for a_, b_ in zip(seq, seq[1:]):
                mm = round((b_ - a_) * 1000 / 5) * 5
                if mm > 0: s.dtext(lx - 12 if wall == "L" else lx + 32, (Y(a_) + Y(b_)) / 2, f"{mm:,}".replace(",", " "), True)
        else:
            ly = Y(z0) + inset if wall == "T" else Y(z1) - inset
            s.A(f'<line x1="{X(seq[0]):.1f}" y1="{ly:.1f}" x2="{X(seq[-1]):.1f}" y2="{ly:.1f}" stroke="{RED}" stroke-width="2.5"/>')
            for v in seq: s.tick(X(v), ly)
            for a_, b_ in zip(seq, seq[1:]):
                mm = round((b_ - a_) * 1000 / 5) * 5
                if mm > 0: s.dtext((X(a_) + X(b_)) / 2, ly - 10 if wall == "B" else ly + 34, f"{mm:,}".replace(",", " "), False)
    def box(s, wx, wy, dx):
        s.A(f'<rect x="{wx-9-(0 if dx else 9):.1f}" y="{wy-9-(9 if dx else 0):.1f}" width="{18 if dx else 36}" height="{36 if dx else 18}" fill="#F2C230" stroke="{INK}" stroke-width="1.5"/>')
    def label(s, x, y, num, text, anchor="middle"):
        n = f'<tspan font-weight="bold" font-size="{26*FS:.0f}" fill="{RED}">{num} </tspan>' if num != "" else ""
        s.A(f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="{32*FS:.0f}" fill="{INK}">{n}{text}</text>')
    # ---------- right column
    def explication(s, head, rows, colname="шт"):
        A = s.A; cx0, cx1 = SX, W - 40
        hl = lambda y: A(f'<line x1="{cx0}" y1="{y}" x2="{cx1}" y2="{y}" stroke="{INK}" stroke-width="2"/>')
        A(f'<text x="{(cx0+cx1)/2:.0f}" y="130" text-anchor="middle" font-size="40" fill="{INK}">{head}</text>')
        cols = [cx0 + 10, cx0 + 80, cx0 + 540, cx0 + 650]
        ty = 170; hl(ty)
        A(f'<text x="{cols[0]+20}" y="{ty+40}" font-size="26" fill="{INK}">№</text><text x="{cols[1]}" y="{ty+40}" font-size="26" fill="{INK}">Наименование</text><text x="{cols[3]+50}" y="{ty+40}" text-anchor="middle" font-size="26" fill="{INK}">{colname}</text>')
        ty += 60; hl(ty)
        for i, row in enumerate(rows):
            t, sym, q = row[:3]; no = row[3] if len(row) > 3 else i + 1
            yy = ty + 46
            A(f'<text x="{cols[0]+8}" y="{yy}" font-size="26" fill="{INK}">{no}</text><text x="{cols[1]}" y="{yy}" font-size="26" fill="{INK}">{t}</text>')
            if sym: sym(cols[2] + 40, yy - 9)
            A(f'<text x="{cols[3]+50}" y="{yy}" text-anchor="middle" font-size="28" font-weight="bold" fill="{INK}">{q}</text>')
            ty += 64; hl(ty)
        for c in cols[1:]:
            A(f'<line x1="{c-14}" y1="170" x2="{c-14}" y2="{ty}" stroke="{INK}" stroke-width="2"/>')
        s.ty = ty
    def notes(s, lines):
        A = s.A; ty = s.ty + 70
        A(f'<text x="{(SX+W-40)/2:.0f}" y="{ty}" text-anchor="middle" font-size="36" font-weight="bold" fill="{INK}">Примечания</text>')
        for i, t in enumerate(lines):
            A(f'<text x="{SX+30}" y="{ty+56+i*46}" font-size="28" fill="{INK}">{t}</text>')
    def stamp(s):
        A = s.A; cx0, cx1 = SX, W - 40; tb = H - 420
        hl = lambda y: A(f'<line x1="{cx0}" y1="{y}" x2="{cx1}" y2="{y}" stroke="{INK}" stroke-width="2"/>')
        hl(tb)
        A(f'<text x="{(cx0+cx1)/2:.0f}" y="{tb+60}" text-anchor="middle" font-size="{34 if len(s.title) < 32 else 26}" fill="{INK}">{s.title}</text>')
        hl(tb + 90); w3 = (cx1 - cx0) / 3
        for i, t in enumerate(["Дата", "Лист", "Листов"]):
            A(f'<text x="{cx0+w3*i+w3/2:.0f}" y="{tb+128}" text-anchor="middle" font-size="28" fill="{INK}">{t}</text>')
        hl(tb + 145)
        s.no = SHEET_NO.get(s.fname, s.no) if hasattr(s, "fname") else s.no
        for i, t in enumerate([META["date"], str(s.no), str(LISTOV)]):
            A(f'<text x="{cx0+w3*i+w3/2:.0f}" y="{tb+215}" text-anchor="middle" font-size="40" fill="{INK}">{t}</text>')
        for i in (1, 2):
            A(f'<line x1="{cx0+w3*i:.0f}" y1="{tb+90}" x2="{cx0+w3*i:.0f}" y2="{tb+260}" stroke="{INK}" stroke-width="2"/>')
        hl(tb + 260)
        for i, t in enumerate(["Дизайнер", "Про-щик", "Раз-тал"]):
            A(f'<text x="{cx0+20}" y="{tb+300+i*36}" font-size="24" fill="{INK}">{t}</text>')
        A(f'<text x="{cx0+220}" y="{tb+300}" font-size="24" font-style="italic" fill="{INK}">{META["designer"]}</text>')
        if META.get("status_note"):
            A(f'<text x="{(120+SX)/2:.0f}" y="{H-70}" text-anchor="middle" font-size="30" font-weight="bold" fill="{ORANGE}" opacity="0.85">{META["status_note"]}</text>')
        A(f'<text x="{(cx0+cx1)/2:.0f}" y="{H-58}" text-anchor="middle" font-size="28" fill="{INK}">{META["city_year"]}</text>')
    def save(s, name):
        s.fname = name
        s.stamp(); s.A('</svg>')
        os.makedirs(OUT_SVG, exist_ok=True)
        open(os.path.join(OUT_SVG, name + ".svg"), "w", encoding="utf-8").write("\n".join(s.o))
        DONE.append(name)

# ---------- symbols
def sq(col, inner=""):
    def f(cx, cy, s):
        s.A(f'<rect x="{cx-17:.1f}" y="{cy-17:.1f}" width="34" height="34" fill="{col}" stroke="{INK}" stroke-width="2"/>{inner.format(cx=cx, cy=cy)}')
    return f
SOCK_IN = '<circle cx="{cx}" cy="{cy}" r="10" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
KC = {"std": "#E07B1F", "tv": PURP, "pwr": RED, "ac": GREEN, "wet": BLUE}
def sock_sym(kind): return sq(KC[kind], SOCK_IN)
def lan_sym(cx, cy, s):
    s.A(f'<rect x="{cx-17:.1f}" y="{cy-17:.1f}" width="34" height="34" fill="#FFFFFF" stroke="{BLUE}" stroke-width="4"/><text x="{cx:.1f}" y="{cy+8:.1f}" text-anchor="middle" font-size="18" font-weight="bold" fill="{BLUE}">LAN</text>')
def sw_sym(keys, walk=False):
    def f(cx, cy, s):
        s.A(f'<rect x="{cx-17:.1f}" y="{cy-17:.1f}" width="34" height="34" fill="{"#2F7FA8" if walk else PURP}" stroke="{INK}" stroke-width="2"/>')
        for i in range(keys):
            xx = cx - 17 + 34 * (i + 1) / (keys + 1)
            s.A(f'<line x1="{xx:.1f}" y1="{cy-11:.1f}" x2="{xx:.1f}" y2="{cy+11:.1f}" stroke="#FFFFFF" stroke-width="4"/>')
    return f
def bound(fn, s): return lambda cx, cy: fn(cx, cy, s)

def place(s, items, kindf, extra_label=None):
    """items: list of dict(n, room, wall, a, syms:[fn], text). Stagger close points on the same wall."""
    byw = {}
    for it in items: byw.setdefault((it["room"], it["wall"]), []).append(round(it["a"], 2))
    stag = {}
    for k, v in byw.items():
        v = sorted(set(v)); prev = None; flag = False
        for a in v:
            flag = (k[1] in 'TB' and prev is not None and a - prev < 0.75 and not flag); stag[(k[0], k[1], a)] = flag; prev = a
    grp = {}
    for it in items: grp.setdefault((it["room"], it["wall"], round(it["a"], 2)), []).append(it)
    for (room, wall, a), its in grp.items():
        wx, wy = s.wp(room, wall, a); dx, dy = INW[wall]
        s.box(wx, wy, dx)
        ex = 120 if stag.get((room, wall, a)) else 0
        bx, by = wx + dx * (70 + ex) * FS, wy + dy * (70 + ex) * FS
        for j, it in enumerate(its):
            syms = it["syms"]; k = len(syms)
            oy = (j * 92 * FS) * (1 if dy >= 0 else -1) if dx == 0 else j * 92 * FS
            st = 38 * FS; rw = k * st
            sx0 = bx - rw / 2 + st / 2 if dx == 0 else (bx + 2 if dx > 0 else bx - rw + st - 2)
            for i, fn in enumerate(syms): fn(sx0 + i * st, by + oy, s)
            if dx == 0: ty = by + oy + (52 if dy > 0 else -30) * FS; tx = bx
            else: ty = by + oy + (50 if not it.get("above") else -30) * FS; tx = sx0 + rw / 2 - st / 2
            s.label(tx, ty, it.get("n", ""), it["text"])
    ch = {}
    for it in items: ch.setdefault((it["room"], it["wall"]), set()).add(round(it["a"], 3))
    for (room, wall), pts in ch.items(): s.chain(room, wall, pts)
