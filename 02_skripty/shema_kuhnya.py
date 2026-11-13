# -*- coding: utf-8 -*-
"""Кухня 3855×2291 — вариант 2 (13.11.2026, на согласование) по замечаниям заказчика:
без стульев, П-образная банкетка (больше мест), видимый холодильник side-by-side, плита 4 конфорки 600 + духовка, ТВ."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_kuhnya.png")
NL = chr(10)
fig, ax = plt.subplots(figsize=(16, 11), dpi=130)
X0, X1, Z0, Z1 = 9.145, 13.0, 1.909, 4.2
T = 0.15
ax.add_patch(Rectangle((X0, Z0), X1 - X0, Z1 - Z0, fc="#ECEBE8", ec="none"))
for (a, b, c, d) in ((X0 - T, Z0 - T, X1 + T, Z0), (X0 - T, Z1, X1 + T, Z1 + T), (X0 - T, Z0, X0, Z1), (X1, Z0, X1 + T, Z1)):
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc="#3A3632"))
ax.add_patch(Rectangle((11.036, Z0 - T), 1.6, T, fc="#BFE0F2", ec="#3A3632"))
ax.text(11.836, Z0 - 0.30, "ОКНО 1600, подоконник 900", ha="center", fontsize=9)
ax.add_patch(Rectangle((X0, Z1), 0.80, T, fc="white", ec="#888"))
ax.text(9.545, Z1 + 0.30, "вход из коридора", ha="center", fontsize=9)
def R(x0, z0, x1, z1, fc, t="", fs=9, col="#222", ec="#555", ls="-", lw=1.3):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def dim(x0, z0, x1, z1, t, col="#B03A2E", fs=9):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.0))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=fs, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.25))
GR, KN, TL = "#3A3A3D", "#9A9BA0", "#8E8E8E"
# кухня у правой стены
RX = X1 - 0.60
R(RX, Z0, X1, 2.509, GR, NL.join(["ПЛИТА", "4 конфорки", "600", "+ духовка"]), 9, "white")
for (cx, cz, r) in ((RX + 0.17, Z0 + 0.17, 0.09), (RX + 0.43, Z0 + 0.17, 0.07), (RX + 0.17, 2.34, 0.07), (RX + 0.43, 2.34, 0.10)):
    ax.add_patch(Circle((cx, cz), r, fc="none", ec="white", lw=1))
R(RX, 2.509, X1, 2.959, GR, NL.join(["ПММ", "450"]), 9, "white")
R(RX, 2.959, X1, 3.50, GR, NL.join(["мойка", "540"]), 9, "white")
R(X1 - 0.35, Z0, X1, 3.50, "none", "", ec="#B03A2E", ls="--", lw=1)
ax.text(X1 - 0.03, 3.42, "верх: вытяжка, шкафы, СВЧ встр.", rotation=90, fontsize=7.5, color="#B03A2E", ha="right", va="bottom")
# холодильник side-by-side у нижней стены
R(12.10, 3.50, X1, Z1, "#6E6F73", NL.join(["ХОЛОДИЛЬНИК", "side-by-side", "900×700"]), 9, "white", ec="#111", lw=2)
# П-банкетка
BD = 0.50
R(X0, Z0, X0 + BD, 3.509, KN, NL.join(["банкетка", "3 места"]), 9)
R(X0 + BD, Z0, 11.0, Z0 + 0.48, KN, "банкетка  3 места", 9)
R(11.05, 2.45, 11.50, 3.25, KN, NL.join(["банкетка", "2 места", "(спинкой", "к кухне)"]), 8)
# стол
TCX, TCZ = X0 + 1.2, Z0 + 0.975
R(TCX - 0.65, TCZ - 0.425, TCX + 0.65, TCZ + 0.425, TL, NL.join(["СТОЛ 1300×850", "6–8 человек"]), 11, "white")
# ТВ на нижней стене
R(10.00, Z1 - 0.06, 11.12, Z1, "#111", "", ec="#111")
ax.annotate("ТВ 50\" на стене, h 1000–1650", (10.56, Z1 - 0.06), (10.15, 3.80), fontsize=9, color="#111", arrowprops=dict(arrowstyle="->"))
# К4
ax.text(X0 + 0.05, 2.52, "К4", fontsize=9, color="#2F7FA8", fontweight="bold")
# проходы
dim(11.50, 2.85, RX, 2.85, "900 проход")
dim(11.30, 3.25, 11.30, Z1, "950")
dim(X0, Z1 + 0.55, X1, Z1 + 0.55, "3855")
dim(X1 + 0.35, Z0, X1 + 0.35, Z1, "2291")
ax.set_title("КУХНЯ — вариант 2: без стульев, П-банкетка (8 мест), холодильник side-by-side, плита 600, ТВ", fontsize=13, fontweight="bold")
ax.set_xlim(X0 - 0.5, X1 + 0.6); ax.set_ylim(Z1 + 0.8, Z0 - 0.55); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig(OUT); print(OUT)
