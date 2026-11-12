# -*- coding: utf-8 -*-
"""Вся квартира сверху: мебель как в 3D + кондиционеры (внутр./наруж. блоки, 2 лоджии), трассы фреона и питание от щита."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_vse_kond.png")
fig, ax = plt.subplots(figsize=(20, 14), dpi=120)
for r in D["rooms"]:
    for (x0, x1, z0, z1) in r["rects"]:
        ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc="#FAF9F6", ec="none", zorder=0))
    cx, cz = r["label"]
    ax.text(cx, cz, r["name"].upper(), ha="center", va="center", fontsize=12, fontweight="bold", color="#9A958C", zorder=1)
for w in D["walls"]:
    ax.add_patch(Rectangle((w[0], w[1]), w[2], w[3], fc="#3A3632", ec="#3A3632", zorder=3))
for wn in D["windows"]:
    x, z, ww, dd = wn["rect"]; ax.add_patch(Rectangle((x, z), ww, dd, fc="#DCEBF2", ec="#5B8FA8", lw=1.2, zorder=3))
KC = {"wardrobe": "#4A4A4C", "tv": "#4A4A4C", "sofa": "#B9BBC0", "chair": "#C9CBD0", "table": "#ECEBE8", "bed": "#D8D2C8", "low": "#9A9084"}
for f in D["furniture"]:
    c = KC.get(f.get("kind"), "#E4E0D8")
    ax.add_patch(Rectangle((f["x"], f["z"]), f["w"], f["d"], fc=c, ec="#555", lw=0.8, zorder=2))
    big = max(f["w"], f["d"]) > 0.9
    if big:
        ax.text(f["x"] + f["w"] / 2, f["z"] + f["d"] / 2, f["name"].split(" (")[0][:26], ha="center", va="center", fontsize=7,
                rotation=90 if f["d"] > f["w"] * 1.4 else 0, color="white" if c == "#4A4A4C" else "#222", zorder=2.5)
# лоджии
for (x0, z0, w, d, t) in ((9.145, 0.309, 1.31, 1.509, "ЛОДЖИЯ А"), (13.745, 2.327, 1.0, 1.218, "ЛОДЖИЯ Б")):
    ax.add_patch(Rectangle((x0, z0), w, d, fc="#FFF4D6", ec="#C27A12", lw=2, zorder=1.5)); ax.text(x0 + w / 2, z0 + 0.2, t, ha="center", fontsize=10, fontweight="bold", color="#8A5A0B", zorder=4)
ax.plot([9.045, 9.045], [0.545, 1.345], color="#2F7FA8", lw=6, zorder=4); ax.plot([13.89, 14.618], [3.59, 3.59], color="#2F7FA8", lw=6, zorder=4)
def unit(x, z, w, d, t):
    ax.add_patch(Rectangle((x, z), w, d, fc="#FFFFFF", ec="#2E7D4F", lw=2.2, hatch="///", zorder=5)); ax.text(x + w / 2, z + d / 2, t, ha="center", va="center", fontsize=8, fontweight="bold", zorder=6, bbox=dict(fc="white", ec="none", pad=0.2))
unit(10.155, 0.55, 0.30, 0.80, "Н1\nН2"); unit(9.25, 1.50, 0.80, 0.30, "Н4 кухня"); unit(13.85, 2.75, 0.80, 0.30, "Н3")
IND = [("К1 гостиная", 5.545 - 0.22, 0.45, 0.22, 1.1), ("К2 вторая гостиная", 5.745, 0.35, 0.22, 1.1), ("К3 спальня 2", 14.745 - 0.22, 4.45, 0.22, 1.1), ("К4 кухня", 9.145, 1.95, 0.22, 1.1)]
for (t, x, z, w, d) in IND:
    ax.add_patch(Rectangle((x, z), w, d, fc="#DFF0E6", ec="#2E7D4F", lw=2, zorder=5))
    ax.text(x + w / 2 + (0.35 if x > 9 and x < 13 else (-0.35 if x < 5.6 else 0.35)), z + d / 2, t.split()[0], ha="center", va="center", fontsize=10, fontweight="bold", color="#2E7D4F", zorder=6)
def line(pts, col, ls, lw=2.2, z=4.5):
    xs, zs = zip(*pts); ax.plot(xs, zs, color=col, ls=ls, lw=lw, zorder=z)
G = "#2E7D4F"
line([(5.43, 0.5), (5.43, 0.38), (8.9, 0.38), (10.1, 0.65)], G, "--")          # К1 → Н1
line([(5.86, 0.42), (8.9, 0.44), (10.1, 1.05)], G, "--")                      # К2 → Н2
line([(14.63, 4.5), (14.63, 3.35)], G, "--")                                  # К3 → Н3
line([(9.3, 2.0), (9.3, 1.85), (9.6, 1.80)], G, "--")                           # К4 → Н4 (через стену в лоджию А)
# питание кондиционеров от щита (группы 19–22, кабель 3×2,5)
SH = (3.43, 8.15)
ax.add_patch(Rectangle((SH[0] - 0.06, SH[1] - 0.2), 0.12, 0.4, fc="#D0312D", ec="#111", zorder=6)); ax.text(SH[0] + 0.15, SH[1] + 0.35, "ЭЛ.ЩИТ", fontsize=9, color="#D0312D", fontweight="bold", zorder=6)
RED = "#D0312D"
line([SH, (3.43, 7.7), (5.45, 7.7), (5.45, 1.3)], RED, ":", 2.4)               # гр.19 → К1
line([SH, (3.43, 7.75), (5.84, 7.75), (5.84, 1.45)], RED, ":", 2.4)            # гр.20 → К2
line([SH, (3.43, 7.8), (9.8, 7.8), (9.8, 6.75), (10.2, 6.75), (14.62, 6.75), (14.62, 5.55)], RED, ":", 2.4)   # гр.21 → К3
line([SH, (3.43, 7.85), (9.75, 7.85), (9.75, 5.2), (9.2, 5.2), (9.2, 3.05)], RED, ":", 2.4)                   # гр.22 → К4
for (x, z) in ((5.45, 1.3), (5.84, 1.45), (14.62, 5.55), (9.2, 3.05)):
    ax.add_patch(Rectangle((x - 0.06, z - 0.06), 0.12, 0.12, fc="#2E7D4F", ec="#111", zorder=7))
# легенда
L = [("#DFF0E6", G, "-", "Внутренний блок К (на стене, верх h=2500)"), ("#FFFFFF", G, "-", "Наружный блок Н (в лоджии, кронштейны друг над другом)"),
     (None, G, "--", "Трасса фреон + дренаж (под потолком, в коробе/штробе)"), (None, RED, ":", "Питание кондиционера от щита: группы 19–22, C16, 3×2,5"),
     ("#2E7D4F", "#111", "-", "Розетка кондиционера h=2200 (рядом с блоком)"), (None, "#2F7FA8", "-", "Стеклянная дверь в лоджию")]
for i, (fc, ec, ls, t) in enumerate(L):
    y = 10.0 + i * 0.3
    if fc: ax.add_patch(Rectangle((0.3, y - 0.1), 0.4, 0.2, fc=fc, ec=ec, lw=2, zorder=6))
    else: ax.plot([0.3, 0.7], [y, y], color=ec, ls=ls, lw=3 if ec != "#2F7FA8" else 6, zorder=6)
    ax.text(0.85, y, t, va="center", fontsize=11, zorder=6)
ax.text(8.5, 11.9, "Лоджия А: Н1 — гостиная, Н2 — вторая гостиная, Н4 — кухня.  Лоджия Б: Н3 — спальня 2.  Размеры — проверить на замере.", fontsize=11, color="#444", ha="center")
ax.set_xlim(-0.2, 15.4); ax.set_ylim(12.2, -0.4); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Квартира сверху: мебель, кондиционеры, трассы и питание", fontsize=17, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
