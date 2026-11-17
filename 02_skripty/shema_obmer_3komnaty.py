# -*- coding: utf-8 -*-
"""17.11.2026: новые расстановки по ОБМЕРУ (PR #1) — спальня 2, ванная, кухня. На согласование, вертикально под телефон.
Геометрия стен/дверей/окон/бетона — из data/kvartira.json; мебель — по согласованным 13.11 составам, переставлена под новые стены."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUTD = os.path.join(os.path.dirname(HERE), "01_chertezhi")
NL = chr(10)
GR, WH, GY, TILE = "#8C8B88", "#F4F4F2", "#BDBDBD", "#8E8E8E"


def base(ax, names, box):
    for r in D["rooms"]:
        for (x0, x1, z0, z1) in r["rects"]:
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc="#FBFAF7" if r["name"] in names else "#EEEDEA", ec="none"))
    for w in D["walls"]: ax.add_patch(Rectangle((w[0], w[1]), w[2], w[3], fc="#3A3632", ec="#3A3632"))
    for wn in D["windows"]:
        x, z, w, d = wn["rect"]; ax.add_patch(Rectangle((x, z), w, d, fc="#BFE0F2", ec="#2C6E91", lw=1))
    for dr in D["doors"]:
        x, z, w, d = dr["rect"]; ax.add_patch(Rectangle((x, z), w, d, fc="#F3D9A4", ec="#8A5A00", lw=1))
    for c in D["concrete"]:
        x, z, w, d = c["rect"]
        ax.add_patch(Rectangle((x, z), w, d, fc="none", ec="#B03A2E", hatch="//", lw=1, ls="--" if c["kind"] == "beam" else "-"))
    for r in D["risers"]: ax.add_patch(Circle((r["x"], r["z"]), 0.055, fc="#B03A2E"))
    x0, x1, z0, z1 = box
    ax.set_xlim(x0, x1); ax.set_ylim(z1, z0); ax.set_aspect("equal"); ax.axis("off")


def R(ax, x0, z0, x1, z1, fc, t="", fs=9, col="#222", ec="#555", ls="-", lw=1.3):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)


def dim(ax, x0, z0, x1, z1, t, col="#B03A2E", fs=9):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.0))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=fs, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.2))


def legs(ax, x0, z0, x1, z1, t):
    R(ax, x0, z0, x1, z1, "#DFF0E6", "", ec="#2E7D4F", ls="--")
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=8, color="#2E7D4F", fontweight="bold")


def mm(v): return "%d" % round(v * 1000)


def sheet(fn, title, notes, draw, box, names, h=13.5):
    fig = plt.figure(figsize=(10.8, h), dpi=130)
    fig.text(0.03, 0.975, title, fontsize=17, fontweight="bold", va="top")
    ax = fig.add_axes([0.03, 0.20, 0.94, 0.72]); base(ax, names, box); draw(ax)
    for c in D["concrete"]:   # бетон поверх мебели — видно, над чем проходит
        x, z, w, d = c["rect"]; ax.add_patch(Rectangle((x, z), w, d, fc="none", ec="#B03A2E", hatch="//", lw=1.4, ls="--" if c["kind"] == "beam" else "-", zorder=5))
    fig.text(0.03, 0.17, NL.join(notes), fontsize=10.5, va="top", linespacing=1.5)
    p = os.path.join(OUTD, fn); fig.savefig(p, facecolor="white"); plt.close(fig); print(p); return p


# ======================= СПАЛЬНЯ 2: 4680×2680, дверь на левой стене (угол → дверь 1100), балка по линии Г, ниша к лоджии Б
def spalnya(ax):
    X0, X1, Z0, Z1 = 10.232, 14.913, 4.836, 7.516
    BX0, BX1 = 11.90, 13.30                                   # кровать 1400×2000 + изголовье 100
    R(ax, BX0, Z0, BX1, Z0 + 0.10, GR, "", ec="#333")
    R(ax, BX0, Z0 + 0.10, BX1, Z0 + 2.10, WH, NL.join(["кровать", "1400×2000"]), 11)
    R(ax, BX0 - 0.45, Z0, BX0, Z0 + 0.40, GR, "тумба", 7.5, col="white")
    R(ax, BX1, Z0, BX1 + 0.45, Z0 + 0.40, GR, "тумба", 7.5, col="white")
    R(ax, X0, 6.416, X0 + 0.60, Z1, WH, NL.join(["шкаф", "встроенный", "1100×600", "белый"]), 8.5, ec="#333")
    R(ax, BX0, Z1 - 0.30, BX1, Z1, GR, "ТВ 55\" + подвесная тумба 300", 7.5, col="white")
    R(ax, 13.75, Z1 - 0.40, 14.55, Z1, GR, NL.join(["туалетный", "столик"]), 7.5, col="white")
    legs(ax, BX0, Z0 + 2.10, BX1, Z1 - 0.30, "проход " + mm(Z1 - 0.30 - Z0 - 2.10) + " (тумба подвесная — по полу " + mm(Z1 - Z0 - 2.10) + ")")
    legs(ax, X0, Z0, BX0 - 0.45, 5.60, NL.join(["проход", mm(BX0 - 0.45 - X0)]))
    ax.add_patch(Arc((X0, 5.616), 1.6, 1.6, theta1=0, theta2=90, color="#B03A2E", lw=1, ls="--"))
    ax.text(12.93, 4.72, "балка", fontsize=8, color="#B03A2E", ha="center")
    ax.text(14.25, 4.2, NL.join(["ниша", "к лоджии Б"]), fontsize=8.5, ha="center", color="#555")
    dim(ax, X0, 7.75, X1, 7.75, "4680 (В 4700)"); dim(ax, 15.15, Z0, 15.15, Z1, "2680")
    dim(ax, 10.05, 6.416, 10.05, Z1, "1100"); dim(ax, 10.05, Z0, 10.05, 5.616, "780"); dim(ax, BX0, 7.95, BX1, 7.95, "1400")
    dim(ax, X0, 8.15, BX0, 8.15, mm(BX0 - X0))
    dim(ax, X0, 7.08, 12.752, 7.08, "2520 до балки")


sp = sheet("shema_obmer_spalnya2.png", "СПАЛЬНЯ 2 по обмеру — расстановка (на согласование)",
           ["• Комната 4680×2680 (было 4670×3160) — на 0,5 м уже, поэтому:",
            "• кровать 1400×2000 изголовьем к верхней стене; ТВ на стене напротив, тумба ПОДВЕСНАЯ (под ней пол свободен);",
            "• до стены от изножья 476 — мало (норма 600). Если тесно — кровать 1400×1900 (+100) или 1600×2000 не ставить.",
            "• дверь выше: сверху 780, дверь 800, шкаф 1100×600 у нижнего угла (замер Д).",
            "• балка — 2520 от стены с дверью, проходит над правой частью кровати.",
            "• Цвета: шкаф белый, тумбы и ТВ-тумба серые, ручки чёрные."], spalnya, (9.6, 15.5, 3.4, 8.35), ("Спальня 2", "Лоджия Б"), h=11.5)


# ======================= ВАННАЯ: 2350×2420 до шахты (вентшахта + стояк Т2 на правой стене), дверь 900 сверху слева
def vanna(ax):
    X0, X1, Z0, Z1 = 3.564, 5.914, 7.434, 9.854             # X1 — грань шахты; стояк Т2 — внизу, в коробе труб (заказчик 17.11)
    R(ax, X0, Z1 - 1.70, X0 + 0.70, Z1, "white", NL.join(["ванна", "1700×700", "", "шторка", "на Г-карнизе"]), 9.5, ec="#333")
    R(ax, X1 - 0.48, 7.55, X1, 8.15, TILE, NL.join(["раковина", "600×480", "откр. полка"]), 7.5, col="white")
    R(ax, X1 - 0.62, 8.25, X1 - 0.02, 8.85, "white", NL.join(["стиралка", "10 кг", "600×600"]), 8, ec="#333")
    R(ax, X1 - 0.20, 9.10, X1, 9.80, GY, "", ls="--")
    R(ax, X1 - 0.75, 9.27, X1 - 0.20, 9.63, "white", NL.join(["унитаз", "+ гиг. душ"]), 8)
    ax.add_patch(Circle((X1 - 0.28, 9.45), 0.225, fc="none", ec="#B03A2E", ls=":", lw=1.6))
    ax.text(X1 - 0.05, 10.0, "бойлер Б1 над унитазом", ha="right", fontsize=8, color="#B03A2E")
    legs(ax, X0 + 0.72, 8.25, X1 - 0.64, 9.85, NL.join(["проход", mm(X1 - 0.64 - X0 - 0.72)]))
    legs(ax, X0 + 0.72, 9.27, X1 - 0.76, 9.63, "ноги у унитаза " + mm(X1 - 0.76 - X0 - 0.72))
    ax.add_patch(Arc((3.749, 7.434), 1.8, 1.8, theta1=0, theta2=90, color="#B03A2E", lw=1, ls="--"))
    ax.text(6.10, 8.4, NL.join(["шахта"]), fontsize=8, ha="center", color="#B03A2E")
    ax.text(6.10, 9.55, NL.join(["Т2"]), fontsize=8, ha="center", color="#B03A2E", fontweight="bold")
    dim(ax, X0, 10.40, X1, 10.40, "2350 (З)"); dim(ax, 3.3, Z0, 3.3, Z1, "2420 (И)")
    dim(ax, X0, 10.15, X0 + 0.70, 10.15, "700")


va = sheet("shema_obmer_vanna.png", "ВАННАЯ по обмеру — расстановка (на согласование)",
           ["• Ванная 2350×2420 до шахты (было 2509×1491) — стала почти квадратной и больше.",
            "• Состав тот же, что согласован 13.11: раковина с открытой полкой, стиралка 10 кг отдельно, унитаз + гиг. душ,",
            "  бойлер Б1 над унитазом.",
            "• Стояк Т2 — внизу, в коробе труб → унитаз у него, бойлер Б1 над унитазом.",
            "• Ванна ПОЛНАЯ 1700×700 (было 1300) — вдоль левой стены; раковина и стиралка — на правой, у двери.",
            "• Дверь 900 — петли слева (у ванны), полотно открывается к раковине; по дуге ничего не стоит."], vanna, (3.0, 6.6, 7.0, 10.6), ("Ванная",), h=12)


# ======================= КУХНЯ: 3300×3400, окно сверху, вентшахта 800×380 + труба в правом верхнем углу, проём 519 снизу слева
def kuhnya(ax):
    X0, X1, Z0, Z1 = 9.586, 12.886, 1.309, 4.709
    C = 0.60
    R(ax, X1 - C, 2.409, X1, Z1, "#D9D8D4", "", ec="#333")
    for (a, b, t) in ((2.45, 3.05, "мойка 600"), (3.05, 3.50, "ПММ 450"), (3.50, 4.05, "столешн."), (4.05, 4.65, "плита 600")):
        R(ax, X1 - C + 0.02, a, X1 - 0.02, b, "white" if "мойка" in t or "плита" in t else "#ECEBE8", t, 8)
    R(ax, X0, 1.40, X0 + 0.70, 2.30, GR, NL.join(["холодильник", "side-by-side", "900"]), 8, col="white")
    R(ax, X0, 2.30, X0 + 0.65, 2.90, GR, NL.join(["колонна", "кофе+СВЧ"]), 7.5, col="white")
    R(ax, X0, 2.90, X0 + 0.65, 3.50, GR, NL.join(["колонна", "кладовая"]), 7.5, col="white")
    R(ax, 10.85, Z0, 12.05, Z0 + 0.70, WH, NL.join(["стол", "1200×700"]), 9, ec="#333")
    for (cx, cz) in ((11.15, 2.25), (11.75, 2.25), (10.60, 1.66)): ax.add_patch(Circle((cx, cz), 0.21, fc="#CFCFCF", ec="#555"))
    legs(ax, X0 + 0.70, 2.55, X1 - C, Z1 - 0.10, NL.join(["рабочий проход", mm(X1 - C - X0 - 0.70)]))
    ax.text(9.85, 4.25, NL.join(["вход", "519"]), fontsize=8.5, ha="center", color="#8A5A00", fontweight="bold")
    ax.text(12.70, 1.15, "вентшахта 800×380 + труба", fontsize=8, ha="center", color="#B03A2E")
    dim(ax, X0, 5.0, X1, 5.0, "3300 (А)"); dim(ax, 13.2, Z0, 13.2, Z1, "3400 (Б)")
    dim(ax, X1 - C, 4.85, X1, 4.85, "600")


ku = sheet("shema_obmer_kuhnya.png", "КУХНЯ по обмеру — расстановка (на согласование)",
           ["• Кухня 3300×3400 (было 3855×2291) — другая форма, вход узкий 519 в левом нижнем углу.",
            "• Состав вар. 7 сохранён: холодильник side-by-side, 2 колонны (кофе+СВЧ, кладовая) — на левой стене;",
            "  мойка → ПММ → плита — вдоль правой стены (2300), начинаются ниже вентшахты.",
            "• Стол 1200×700 у окна, 3 стула; подоконник 900 — окно свободно, свет на стол.",
            "• Проход между холодильником и столешницей ~2 м — свободно, «треугольник» короткий.",
            "• Фасады серые, ручки чёрные; столешница/фартук — серый керамогранит."], kuhnya, (9.2, 13.6, 0.85, 5.25), ("Кухня",), h=12.5)

from PIL import Image
ims = [Image.open(p) for p in (sp, va, ku)]
W_ = 1080; ims = [im.resize((W_, round(im.height * W_ / im.width))) for im in ims]
c = Image.new("RGB", (W_, sum(im.height for im in ims)), "white"); y = 0
for im in ims: c.paste(im, (0, y)); y += im.height
P = os.path.join(OUTD, "shema_obmer_3komnaty.jpg"); c.save(P, quality=88); print(P)
