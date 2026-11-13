# -*- coding: utf-8 -*-
"""Санузел — вид сверху (13.11.2026, вар. 2 по заказчику): вход в душ СО СТОРОНЫ РАКОВИНЫ, маятниковая дверь
(открывается в обе стороны); стенка к биде — глухое стекло; бак 200 л."""
import os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_sanuzel_dver2.png")
NL = chr(10)
X0, X1, Z0, Z1 = 0.309, 1.836, 6.8, 9.018
SX1, SZ1 = 1.018, 7.709
HZ = 7.18; LW = SZ1 - HZ                     # ось двери (у глухой части), полотно ≈530
fig, ax = plt.subplots(figsize=(11, 14), dpi=120)
T = 0.12
ax.add_patch(Rectangle((X0, Z0), X1 - X0, Z1 - Z0, fc="#E6E6E6"))
for (a, b, c, d) in ((X0 - T, Z0 - T, X1 + T, Z0), (X0 - T, Z1, X1 + T, Z1 + T), (X0 - T, Z0, X0, Z1)):
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc="#3A3632"))
ax.add_patch(Rectangle((X1, Z0 - T), T, 7.0 - Z0 + T, fc="#3A3632")); ax.add_patch(Rectangle((X1, 7.8), T, Z1 + T - 7.8, fc="#3A3632"))
ax.add_patch(Rectangle((X1, 7.0), T, 0.8, fc="white", ec="#888")); ax.text(X1 + 0.20, 7.4, NL.join(["вход", "в санузел"]), fontsize=11, va="center")
def R(x0, z0, x1, z1, fc, t="", fs=11, col="#222", ec="#555", lw=1.5):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def num(x, z, n):
    ax.text(x, z, n, ha="center", va="center", fontsize=16, color="white", fontweight="bold", bbox=dict(boxstyle="circle", fc="#B03A2E", ec="none"))
# душ
R(X0, Z0, SX1, SZ1, "#CFE3EC", NL.join(["ДУШ", "700×900"]), 13, ec="#2F7FA8")
ax.add_patch(Rectangle((X0 + 0.10, Z0), 0.50, 0.12, fc="#999", ec="#555")); ax.text(X0 + 0.35, Z0 + 0.20, "ниша 3 полки", ha="center", fontsize=9)
# 13.11 вар. 3 (по заказчику): БЕЗ СТЕКЛА — тканевая шторка на Г-образном потолочном карнизе (легко снять и постирать)
import numpy as np
ax.plot([X0, SX1, SX1], [SZ1, SZ1, Z0], color="#111", lw=2.5)                       # Г-карниз под потолком
zz = np.linspace(Z0 + 0.05, SZ1 - 0.02, 40); ax.plot(SX1 - 0.03 + 0.02 * np.sin(zz * 70), zz, color="#7A4B22", lw=2.5)   # шторка задёрнута (сторона раковины)
xx = np.linspace(X0 + 0.02, SX1 - 0.03, 30); ax.plot(xx, SZ1 - 0.03 + 0.02 * np.sin(xx * 70), color="#7A4B22", lw=2.5)   # шторка задёрнута (сторона биде)
ax.add_patch(Rectangle((X0 + 0.01, SZ1 - 0.12), 0.10, 0.10, fc="#C9A27A", ec="#7A4B22")); ax.text(X0 + 0.13, SZ1 - 0.17, "шторка собрана у стены", fontsize=8.5, color="#7A4B22")
ax.text(SX1 + 0.05, 7.30, NL.join(["Г-карниз", "под потолком,", "шторка", "ткань"]), fontsize=9, color="#7A4B22", va="center")
ax.text(X0 + 0.35, SZ1 + 0.09, "вход в душ — с любой стороны", ha="center", fontsize=9.5, color="#2E7D4F")
num(SX1 + 0.40, 7.55, "1")
# раковина (глубина уменьшена до 350, чтобы дверь её не задевала)
R(1.10, Z0, 1.60, Z0 + 0.40, "#8E8E8E", NL.join(["раковина", "500×400"]), 10, "white")
# бак
R(X0, 7.74, X0 + 0.24, 8.26, "#2F2F31", "", ec="#B03A2E", lw=3)
ax.add_patch(Rectangle((X0 + 0.01, 7.76), 0.20, 0.48, fc="white", ec="#555"))
num(X0 + 0.45, 8.0, "2")
# инсталляции, биде, унитаз, бойлер
R(X0, Z1 - 0.20, X1, Z1, "#BDBDBD", "короб инсталляций + шкаф до потолка", 9)
R(0.53, Z1 - 0.70, 0.89, Z1 - 0.20, "white", NL.join(["биде", "360×500"]), 11)
ax.annotate("", (0.71, SZ1), (0.71, Z1 - 0.70), arrowprops=dict(arrowstyle="<->", color="#2E7D4F", lw=2)); ax.text(0.74, SZ1 + 0.17, "610 мм", fontsize=12, color="#2E7D4F", fontweight="bold", va="center")
R(1.25, Z1 - 0.75, 1.61, Z1 - 0.20, "white", "унитаз", 11)
ax.add_patch(Circle((1.43, Z1 - 0.435), 0.225, fc="none", ec="#2F7FA8", ls=":", lw=2))
ax.text(1.43, Z1 - 0.88, "бойлер Б2 — над унитазом", ha="center", fontsize=10, color="#2F7FA8")
ax.text(X0 - 0.2, Z1 + 0.25, NL.join([
    "1 — ДУШ БЕЗ СТЕКЛА: тканевая шторка на Г-карнизе под потолком.",
    "     Отодвигается в любую сторону, вход шириной во весь душ; шторку легко снять и постирать.",
    "     Поддон/трап с уклоном к стене, чтобы вода не выходила в санузел.",
    "2 — БАК 200 л ЗДЕСЬ: узкий, под заказ 520 × 220 × высота 2000, у стены между душем и биде,",
    "     в графитовом пенале до потолка, насос сверху.",
    "Биде подвесное компактное 360 × 500: спереди 610 мм свободно (норма 600)."]), fontsize=12, color="#B03A2E", fontweight="bold", va="top")
ax.set_title("САНУЗЕЛ: душ без стекла — шторка на Г-карнизе; бак 200 л", fontsize=15, fontweight="bold")
ax.set_xlim(X0 - 0.3, X1 + 0.6); ax.set_ylim(Z1 + 0.85, Z0 - 0.35); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig(OUT); print(OUT)
