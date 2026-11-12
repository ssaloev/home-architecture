# -*- coding: utf-8 -*-
"""Вторая гостиная — расстановка как в 3D (komnata_blender.py), вид сверху, на согласование."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_komnata_rasstanovka.png")
X0, X1, Z0, Z1 = 5.745, 8.945, 0.309, 6.545
tm = 3.436
fig, ax = plt.subplots(figsize=(11, 14), dpi=130)
for w in D["walls"]:
    ax.add_patch(Rectangle((w[0], w[1]), w[2], w[3], fc="#3A3632", ec="#3A3632"))
for wn in D["windows"]:
    x, z, ww, dd = wn["rect"]; ax.add_patch(Rectangle((x, z), ww, dd, fc="#DCEBF2", ec="#5B8FA8", lw=1.5))
def R(x0, z0, x1, z1, fc, t="", fs=10, ec="#555", rot=0, lw=1.5, **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, **kw))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, rotation=rot)
def dim(x0, z0, x1, z1, t, col="#B03A2E"):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.1))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=10, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.4))
GR = "#4A4A4C"
# лоджия А
R(9.145, 0.309, 10.455, 1.818, "#FFF4D6", "ЛОДЖИЯ А", 10, ec="#C27A12", lw=2)
R(10.155, 0.55, 10.455, 1.35, "#FFFFFF", "Н1+Н2", 8, ec="#2E7D4F", rot=90, hatch="///")
ax.plot([9.045, 9.045], [0.545, 1.345], color="#2F7FA8", lw=6)
ax.text(9.6, 1.55, "стеклянная\nдверь 800", fontsize=9, color="#2F7FA8", ha="center")
# входная дверь
ax.plot([8.145, 8.945], [6.61, 6.61], color="#1C1B1A", lw=5); ax.text(8.55, 6.85, "вход из коридора", fontsize=9, ha="center")
# мебель как в 3D
R(X0, 5.945, 8.115, Z1, GR, "ШКАФ встроенный 2370×600", 10, ec="#222", **{})
ax.texts[-1].set_color("white")
R(X1 - 0.45, tm - 1.55, X1, tm + 1.55, GR, "ТВ-тумба 3100×450\n+ рейки, ТВ 85\"", 9, ec="#222", rot=90); ax.texts[-1].set_color("white")
R(X0, tm - 1.13, X0 + 0.95, tm + 1.13, "#B9BBC0", "ДИВАН Peru 2260", 10, rot=90)
R(7.84 - 0.50, 5.02 - 0.48, 7.84 + 0.50, 5.02 + 0.48, "#C9CBD0", "кресло", 9)
R(7.84 - 0.50, 1.87 - 0.48, 7.84 + 0.50, 1.87 + 0.48, "#C9CBD0", "кресло", 9)
ax.add_patch(Circle((7.54, tm), 0.55, fc="#ECEBE8", ec="#555")); ax.text(7.54, tm, "столик\nØ1100", ha="center", va="center", fontsize=9)
ax.add_patch(Circle((X0 + 0.32, 1.95), 0.22, fc="#CFE5CF", ec="#4E7A4E")); ax.text(X0 + 0.32, 1.95, "раст.", ha="center", va="center", fontsize=8)
R(X0, 0.55, X0 + 0.25, 1.25, "#FFFFFF", "К2", 9, ec="#2E7D4F", lw=2)
R(5.745, 0.309, 8.945, 0.47, "#E7E3DC", "шторы + тюль", 8, ec="none")
# размеры
dim(X0 + 0.95, 4.1, X1 - 0.45, 4.1, "проход 1800")
dim(X1 + 0.05, 1.345, X1 + 0.05, tm - 1.55, "540")
ax.text(9.5, 2.85, "от двери в лоджию\nдо ТВ-тумбы 540", fontsize=9, color="#B03A2E")
ax.set_xlim(5.2, 10.9); ax.set_ylim(7.2, -0.3); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Вторая гостиная — расстановка (вид сверху)", fontsize=15, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
