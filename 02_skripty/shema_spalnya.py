# -*- coding: utf-8 -*-
"""Спальня 2 — вид сверху по плану: двери, окно, проход в лоджию Б, расстановка (вариант на согласование)."""
import os, json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
VAR = sys.argv[1] if len(sys.argv) > 1 else "A"
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", f"shema_spalnya_{VAR}.png")
X0, X1, Z0, Z1 = 10.072, 14.745, 4.327, 7.491
BC = 12.43            # кровать по центру глухой части верхней стены (между шкафом и проходом в лоджию)
fig, ax = plt.subplots(figsize=(13, 11), dpi=130)
ax.add_patch(Rectangle((X0, Z0), X1 - X0, Z1 - Z0, fc="#FAF9F6", ec="none"))
ax.add_patch(Rectangle((13.745, 2.327), 1.0, 2.0, fc="#FFF4D6", ec="none"))
for w in D["walls"]:
    ax.add_patch(Rectangle((w[0], w[1]), w[2], w[3], fc="#3A3632", ec="#3A3632"))
for wn in D["windows"]:
    x, z, ww, dd = wn["rect"]; ax.add_patch(Rectangle((x, z), ww, dd, fc="#DCEBF2", ec="#5B8FA8", lw=1.5))
def R(x0, z0, x1, z1, fc, t="", fs=10, rot=0, ec="#555", col="#222", **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=1.4, **kw))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, rotation=rot, color=col)
def dim(x0, z0, x1, z1, t, col="#B03A2E"):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.1))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=10, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.4))
# двери
ax.plot([10.02, 10.02], [6.6, 7.4], color="#1C1B1A", lw=6)
ax.text(9.55, 7.0, "ВХОД\nиз коридора", ha="center", fontsize=10, fontweight="bold")
ax.plot([13.89, 14.618], [3.59, 3.59], color="#2F7FA8", lw=6); ax.text(14.25, 3.35, "стекл. дверь", ha="center", fontsize=9, color="#2F7FA8")
ax.text(14.25, 2.75, "ЛОДЖИЯ Б\nН3 (спальня)", ha="center", fontsize=10, fontweight="bold", color="#8A5A0B")
ax.text(14.25, 3.95, "проход\nв лоджию", ha="center", fontsize=9, color="#8A5A0B")
# мебель (предложение)
G = "#4A4A4C"
R(X0, Z0, X0 + 0.6, 6.509, G, "ШКАФ 600×2180", 10, rot=90, col="white")
if VAR == "A":
    R(BC - 0.75, Z0 + 0.02, BC + 0.75, Z0 + 2.15, "#D8D2C8", "КРОВАТЬ 1400×2000\n(под заказ)", 11)
    R(BC - 0.80, Z0, BC + 0.80, Z0 + 0.13, "#5E5E62", "")
    for xx in (BC - 1.025, BC + 1.025): R(xx - 0.175, Z0 + 0.0, xx + 0.175, Z0 + 0.38, "#4A4A4C", "тумб.\n350", 8, col="white")
    R(BC - 0.8, Z1 - 0.40, BC + 0.8, Z1, G, "ТВ-тумба + ТВ 55\"", 9, col="white")
    # дуги открывания: дверь входа (петли у шкафа) и створки шкафа
    ax.add_patch(Arc((10.07, 6.6), 1.6, 1.6, theta1=0, theta2=90, color="#B03A2E", lw=1.3, ls="--"))
    for k in range(4):
        zc = Z0 + k * (6.509 - Z0) / 4 + ((6.509 - Z0) / 4 if k % 2 == 0 else 0)
        ax.add_patch(Arc((X0 + 0.6, zc), 1.09, 1.09, theta1=(270 if k % 2 == 0 else 0), theta2=(360 if k % 2 == 0 else 90), color="#2F7FA8", lw=1, ls=":"))
else:
    BB = 12.35
    R(BB - 0.875, Z1 - 2.15, BB + 0.875, Z1 - 0.05, "#D8D2C8", "КРОВАТЬ 1600×2000", 11)
    R(BB - 0.925, Z1 - 0.10, BB + 0.925, Z1, "#8C8580", "")
    for xx in (BB - 1.17, BB + 1.17): R(xx - 0.25, Z1 - 0.44, xx + 0.25, Z1 - 0.02, "#E8E4DC", "тумб.", 8)
    R(BC - 0.8, Z0, BC + 0.8, Z0 + 0.40, G, "ТВ-тумба + ТВ 55\"", 9, col="white")
R(13.75, Z1 - 0.40, 14.55, Z1, "#E8E4DC", "столик+зеркало", 8) if VAR == "A" else R(X1 - 0.40, 6.0, X1, 6.75, "#E8E4DC", "столик", 8, rot=90)
R(X1 - 0.22, 4.45, X1, 5.55, "#DFF0E6", "К3", 9, ec="#2E7D4F", rot=90)
ax.add_patch(Circle((14.15, Z1 - 0.65) if VAR == "A" else (X1 - 0.65, 6.4), 0.2, fc="#CFC9C2", ec="#555")); ax.text(*((14.15, Z1 - 0.65) if VAR == "A" else (X1 - 0.65, 6.4)), "пуф", ha="center", va="center", fontsize=8)
# размеры
dim(X0 + 0.6, Z0 - 0.12, 13.745, Z0 - 0.12, "глухая часть стены 3070")
dim(13.745, 4.45, 14.745, 4.45, "проход 1000"); dim(BC + 1.20, Z0 + 0.6, 13.745, Z0 + 0.6, "%d" % round((13.745 - BC - 1.20) * 1000)) if VAR == "A" else None; dim(X0 + 0.6, Z0 + 0.6, BC - 1.20, Z0 + 0.6, "%d" % round((BC - 1.20 - X0 - 0.6) * 1000)) if VAR == "A" else None
dim(BC, Z0 + 2.15, BC, Z1 - 0.40, "до ТВ 720") if VAR == "A" else dim(12.35, Z0 + 0.40, 12.35, Z1 - 2.15, "до ТВ 720")
dim(X0, 7.65, X1, 7.65, "4670")
dim(9.75, Z0, 9.75, Z1, "3160")
ax.set_xlim(9.2, 15.3); ax.set_ylim(8.0, 2.1); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(("Спальня 2 — кровать 1400, тумбочки 350, дуги открывания дверей" if VAR == "A" else "Вариант Б — изголовье у нижней стены, проход в лоджию у ног"), fontsize=15, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
