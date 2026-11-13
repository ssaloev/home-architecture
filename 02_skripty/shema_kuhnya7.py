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
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_kuhnya7.png")
NL = chr(10)
fig, ax = plt.subplots(figsize=(16, 11), dpi=130)
X0, X1, Z0, Z1 = 9.145, 13.0, 1.909, 4.2
T = 0.15
ax.add_patch(Rectangle((X0, Z0), X1 - X0, Z1 - Z0, fc="#ECEBE8", ec="none"))
for (a, b, c, d) in ((X0 - T, Z0 - T, X1 + T, Z0), (X0 - T, Z1, X1 + T, Z1 + T), (X0 - T, Z0, X0, Z1), (X1, Z0, X1 + T, Z1)):
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc="#3A3632"))
ax.add_patch(Rectangle((11.036, Z0 - T), 1.6, T, fc="#BFE0F2", ec="#3A3632"))
ax.text(11.836, Z0 - 0.30, "ОКНО 1600 — открыто, ничего не мешает", ha="center", fontsize=9)
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
# 13.11 вариант 5: ОКНО СВОБОДНО — перед окном ничего нет (створка открывается полностью), только подоконник
ax.add_patch(Rectangle((11.036, Z0), 1.6, 0.25, fc="#DFF0E6", ec="#2E7D4F", ls="--", lw=1.3))
ax.text(11.836, Z0 + 0.42, NL.join(["перед окном свободно", "створка открывается полностью"]), ha="center", fontsize=9, color="#2E7D4F", fontweight="bold")
# правая стена — весь кухонный ряд до угла: плита у окна → ПММ 450 → мойка 600 → угловой низ
RX = X1 - D
# 13.11 (по заказчику): мойка и плита поменяны местами — мойка у окна, ПММ рядом с мойкой, плита дальше
R(RX, Z0, X1, Z0 + 0.60, GR, NL.join(["МОЙКА", "600"]), 9, "white")
ax.add_patch(Rectangle((RX + 0.10, Z0 + 0.08), 0.40, 0.44, fc="#222", ec="white", lw=1))
R(RX, Z0 + 0.60, X1, Z0 + 1.05, GR, NL.join(["ПММ", "450"]), 9, "white")
R(RX, Z0 + 1.05, X1, Z0 + 1.65, GR, NL.join(["ПЛИТА", "4 зоны 600", "+ духовка"]), 9, "white")
for (cx, cz, r) in ((RX + 0.17, Z0 + 1.22, 0.08), (RX + 0.43, Z0 + 1.22, 0.07), (RX + 0.17, Z0 + 1.48, 0.07), (RX + 0.43, Z0 + 1.48, 0.09)):
    ax.add_patch(Circle((cx, cz), r, fc="none", ec="white", lw=1))
R(RX, Z0 + 1.65, X1, Z1, GR, NL.join(["угловой", "низ", "(карусель)"]), 8.5, "white")
R(X1 - 0.35, Z0, X1, Z1, "none", "", ec="#B03A2E", ls="--", lw=1)
ax.text(X1 - 0.03, Z0 + 0.65, "верх: шкафы до потолка, вытяжка над плитой", rotation=90, fontsize=7.5, color="#B03A2E", ha="right", va="bottom")
# нижняя стена — сразу у входа холодильник side-by-side (по эскизу заказчика), за ним колонны до потолка
R(9.96, Z1 - 0.70, 10.88, Z1, "#B9BBBD", NL.join(["ХОЛОДИЛЬНИК", "side-by-side", "900×700"]), 9, ec="#111", lw=2.5)
R(10.88, Z1 - 0.60, 11.48, Z1, "#5A5A5E", NL.join(["колонна", "кладовая"]), 8.5, "white")
R(11.48, Z1 - 0.60, 12.08, Z1, "#5A5A5E", NL.join(["колонна", "СВЧ +", "кофемаш."]), 8.5, "white")
R(12.08, Z1 - 0.60, RX, Z1, GR, NL.join(["бутыл.", "320"]), 7.5, "white")
# левая стена: буфет + ТВ над ним; верхняя стена слева от окна — шкаф до потолка
# 13.11 (по заказчику): место на 2 человека — стол 1000×600 у левой стены (вместо буфета), 2 стула, ТВ над столом
R(X0, 2.40, X0 + 0.60, 3.40, "#8E8E8E", NL.join(["СТОЛ", "1000×600", "на 2"]), 9, "white")
R(X0, 2.45, X0 + 0.05, 3.35, "#111", "", ec="#111")
for zc in (2.65, 3.15):
    R(X0 + 0.62, zc - 0.21, X0 + 1.04, zc + 0.21, "#C9CBCD", "стул", 8, ec="#333")
dim(X0 + 0.05, 3.40, X0 + 0.05, Z1, "800 проход")
ax.annotate("ТВ 50\" над столом", (X0 + 0.05, 2.55), (10.25, 2.50), fontsize=9, color="#111", arrowprops=dict(arrowstyle="->"))
R(X0, Z0, 11.0, Z0 + 0.45, "#5A5A5E", "шкаф до потолка 1855×450 (посуда, техника, запасы)", 8.5, "white")
ax.text(X0 + 0.05, 2.38, "К4", fontsize=8.5, color="#2F7FA8", fontweight="bold", va="bottom")
# свободный центр
ax.text(11.2, 2.75, NL.join(["СВОБОДНО"]), ha="center", va="center", fontsize=11, color="#2E7D4F", fontweight="bold")
dim(11.6, Z0 + 0.45, 11.6, Z1 - 0.60, "%d" % round((Z1 - 0.60 - Z0 - 0.45) * 1000))
dim(X0 + 1.04, 3.0, RX, 3.0, "%d" % round((RX - X0 - 1.04) * 1000))
dim(X0, Z1 + 0.55, X1, Z1 + 0.55, "3855")
dim(X1 + 0.35, Z0, X1 + 0.35, Z1, "2291")
ax.set_title("КУХНЯ — вариант 7: мойка у окна, плита дальше; холодильник у входа; стол на 2 у левой стены; окно свободно", fontsize=12.5, fontweight="bold")
ax.set_xlim(X0 - 0.5, X1 + 0.6); ax.set_ylim(Z1 + 0.8, Z0 - 0.55); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig(OUT); print(OUT)
