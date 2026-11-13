# -*- coding: utf-8 -*-
"""Кухня 3855×2291 — вариант 3 (13.11.2026, на согласование): стол и стулья убраны (по заказчику).
Угловая кухня: мойка под окном, плита на правой стене; у нижней стены — холодильник side-by-side + 2 колонны;
у левой стены — буфет с ТВ над ним. Центр свободен."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_kuhnya4.png")
NL = chr(10)
fig, ax = plt.subplots(figsize=(16, 11), dpi=130)
X0, X1, Z0, Z1 = 9.145, 13.0, 1.909, 4.2
T = 0.15
ax.add_patch(Rectangle((X0, Z0), X1 - X0, Z1 - Z0, fc="#ECEBE8", ec="none"))
for (a, b, c, d) in ((X0 - T, Z0 - T, X1 + T, Z0), (X0 - T, Z1, X1 + T, Z1 + T), (X0 - T, Z0, X0, Z1), (X1, Z0, X1 + T, Z1)):
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc="#3A3632"))
ax.add_patch(Rectangle((11.036, Z0 - T), 1.6, T, fc="#BFE0F2", ec="#3A3632"))
ax.text(11.836, Z0 - 0.30, "ОКНО 1600, подоконник 900 = столешница", ha="center", fontsize=9)
ax.add_patch(Rectangle((X0, Z1), 0.80, T, fc="white", ec="#888"))
ax.text(9.545, Z1 + 0.30, "вход из коридора", ha="center", fontsize=9)
def R(x0, z0, x1, z1, fc, t="", fs=9, col="#222", ec="#555", ls="-", lw=1.3):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def dim(x0, z0, x1, z1, t, col="#B03A2E", fs=9):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.0))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=fs, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.25))
GR, TL = "#3A3A3D", "#8E8E8E"
D = 0.60
# верхняя стена (под окном): ящики · ПММ 600 · мойка под окном
R(10.30, Z0, 10.94, Z0 + D, GR, NL.join(["ящики", "640"]), 9, "white")
R(10.94, Z0, 11.54, Z0 + D, GR, NL.join(["ПММ", "600"]), 9, "white")
R(11.54, Z0, 12.14, Z0 + D, GR, NL.join(["МОЙКА", "под окном"]), 9, "white")
ax.add_patch(Rectangle((11.62, Z0 + 0.10), 0.44, 0.38, fc="#222", ec="white", lw=1))
R(12.14, Z0, X1, Z0 + D, GR, NL.join(["угловой", "шкаф"]), 8, "white")
# правая стена: плита 600 + духовка, ящики
RX = X1 - D
R(RX, Z0 + D, X1, Z0 + D + 0.60, GR, NL.join(["ПЛИТА", "4 зоны 600", "+ духовка"]), 9, "white")
for (cx, cz, r) in ((RX + 0.17, Z0 + D + 0.17, 0.08), (RX + 0.43, Z0 + D + 0.17, 0.07), (RX + 0.17, Z0 + D + 0.43, 0.07), (RX + 0.43, Z0 + D + 0.43, 0.09)):
    ax.add_patch(Circle((cx, cz), r, fc="none", ec="white", lw=1))
R(RX, Z0 + D + 0.60, X1, Z1 - 0.60, GR, NL.join(["ящики", "%d" % round((Z1 - 0.60 - Z0 - D - 0.60) * 1000)]), 9, "white")
R(X1 - 0.35, Z0, X1, Z1 - 0.60, "none", "", ec="#B03A2E", ls="--", lw=1)
R(10.30, Z0, 11.0, Z0 + 0.35, "none", "", ec="#B03A2E", ls="--", lw=1)
R(12.66, Z0, X1, Z0 + 0.35, "none", "", ec="#B03A2E", ls="--", lw=1)
ax.text(10.0, Z0 + 0.72, "пунктир — верхние шкафы до потолка; над окном шкафов нет; вытяжка над плитой", fontsize=7.5, color="#B03A2E")
# левая стена: холодильник side-by-side — отдельно, на открытом месте, виден от входа
R(X0, 2.55, X0 + 0.70, 3.47, "#B9BBBD", NL.join(["ХОЛОДИЛЬ-", "НИК", "side-by-", "side", "900×700"]), 9, ec="#111", lw=2.5)
ax.annotate("двери открываются в кухню", (X0 + 0.72, 3.0), (9.95, 2.35), fontsize=8.5, color="#2E7D4F", arrowprops=dict(arrowstyle="->", color="#2E7D4F"))
# нижняя стена: буфет + ТВ над ним; справа 2 колонны до потолка
R(10.05, Z1 - 0.45, 11.75, Z1, "#6E6F73", NL.join(["БУФЕТ 1700×450", "посуда"]), 9, "white")
R(10.30, Z1 - 0.05, 11.50, Z1, "#111", "", ec="#111")
ax.text(10.90, Z1 - 0.55, "ТВ 50\" над буфетом", ha="center", fontsize=9)
R(11.80, Z1 - 0.60, 12.40, Z1, "#5A5A5E", NL.join(["колонна", "СВЧ +", "кофемашина"]), 8.5, "white")
R(12.40, Z1 - 0.60, X1, Z1, "#5A5A5E", NL.join(["колонна", "кладовая"]), 8.5, "white")
ax.text(X0 + 0.05, 2.45, "К4", fontsize=8.5, color="#2F7FA8", fontweight="bold")
# свободный центр
ax.text(11.1, 3.35, NL.join(["СВОБОДНО", "(стола и стульев нет)"]), ha="center", va="center", fontsize=11, color="#2E7D4F", fontweight="bold")
# размеры проходов
dim(11.30, Z0 + D, 11.30, Z1 - 0.45, "%d" % round((Z1 - 0.45 - Z0 - D) * 1000))
dim(X0 + 0.70, 3.0, RX, 3.0, "%d" % round((RX - X0 - 0.70) * 1000))
dim(X0, Z1 + 0.55, X1, Z1 + 0.55, "3855")
dim(X1 + 0.35, Z0, X1 + 0.35, Z1, "2291")
ax.set_title("КУХНЯ — вариант 4: холодильник отдельно у левой стены (виден от входа), мойка под окном, плита справа, буфет с ТВ", fontsize=12.5, fontweight="bold")
ax.set_xlim(X0 - 0.5, X1 + 0.6); ax.set_ylim(Z1 + 0.8, Z0 - 0.55); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig(OUT); print(OUT)
