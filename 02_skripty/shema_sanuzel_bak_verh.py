# -*- coding: utf-8 -*-
"""Санузел (13.11.2026, по эскизу заказчика): бак 200 л — НАВЕРХУ, в шкафу до потолка над биде; боковой пенал убран.
Слева — фасад стены с инсталляцией, справа — вид сверху."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_sanuzel_bak_verh.png")
NL = chr(10)
X0, X1, Z0, Z1, HC = 0.309, 1.836, 6.8, 9.018, 2.65
SX1, SZ1 = 1.018, 7.709
TX1 = 0.95                       # шкаф бака: X0..TX1 (640), бойлер TX1..X1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 10), dpi=110, gridspec_kw=dict(width_ratios=[1.1, 1]))
def R(ax, x0, y0, x1, y1, fc, t="", fs=10, col="#222", ec="#555", lw=1.5, ls="-"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (y0 + y1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
# ---------- фасад (смотрим на стену с инсталляцией)
a = a1
R(a, X0 - 0.06, -0.05, X1 + 0.06, 0, "#3A3632"); R(a, X0 - 0.06, HC, X1 + 0.06, HC + 0.05, "#3A3632")
R(a, X0, 0, X1, 1.12, "#BDBDBD", "короб инсталляций h 1120", 9)
R(a, X0, 1.40, TX1, HC, "#2F2F31", "", ec="#B03A2E", lw=3)
R(a, X0 + 0.03, 1.45, TX1 - 0.03, HC - 0.06, "#F2F2F2", NL.join(["БАК 200 л", "под заказ", "580 × 300", "h 1150"]), 12, "#B03A2E")
R(a, X0 + 0.03, HC - 0.05, TX1 - 0.03, HC - 0.01, "#666")
a.text((X0 + TX1) / 2, 1.30, "низ шкафа 1400 — над головой сидящего", ha="center", fontsize=8.5, color="#B03A2E")
R(a, TX1, 1.12, X1, 1.80, "#4A4A4C", "полки 200", 9, "white")
R(a, TX1, 1.80, X1, HC, "#2F2F31", "", ec="#2F7FA8", lw=2)
a.add_patch(Ellipse((1.43, 2.22), 0.45, 0.72, fc="#E8E8E8", ec="#2F7FA8")); a.text(1.43, 2.22, NL.join(["бойлер", "Б2"]), ha="center", va="center", fontsize=10)
a.add_patch(Ellipse((0.71, 0.33), 0.36, 0.16, fc="white", ec="#555")); a.text(0.71, 0.33, "биде", ha="center", va="center", fontsize=10)
a.add_patch(Ellipse((1.43, 0.33), 0.36, 0.16, fc="white", ec="#555")); a.text(1.43, 0.33, "унитаз", ha="center", va="center", fontsize=10)
a.text(X0 - 0.03, HC + 0.12, "ФАСАД: стена с инсталляцией — шкаф до потолка", fontsize=13, fontweight="bold")
a.set_xlim(X0 - 0.25, X1 + 0.15); a.set_ylim(-0.15, HC + 0.25); a.set_aspect("equal"); a.axis("off")
for y in (1.12, 1.40, 1.80, HC): a.text(X1 + 0.03, y, f"{int(round(y * 1000))}", fontsize=9, va="center")
# ---------- вид сверху
a = a2; T = 0.12
R(a, X0, Z0, X1, Z1, "#E6E6E6", ec="none")
for (x0, z0, x1, z1) in ((X0 - T, Z0 - T, X1 + T, Z0), (X0 - T, Z1, X1 + T, Z1 + T), (X0 - T, Z0, X0, Z1), (X1, Z0, X1 + T, 7.0), (X1, 7.8, X1 + T, Z1)):
    R(a, x0, z0, x1, z1, "#3A3632", ec="none")
R(a, X1, 7.0, X1 + T, 7.8, "white", ec="#888"); a.text(X1 + 0.15, 7.4, NL.join(["вход"]), fontsize=10, va="center")
R(a, X0, Z0, SX1, SZ1, "#CFE3EC", NL.join(["ДУШ", "700×900"]), 12, ec="#2F7FA8")
R(a, 1.10, Z0, 1.60, Z0 + 0.40, "#8E8E8E", "раковина", 9, "white")
R(a, X0, Z1 - 0.20, X1, Z1, "#BDBDBD", "", ec="#555")
R(a, X0, Z1 - 0.30, TX1, Z1, "none", "", ec="#B03A2E", lw=3, ls="--"); a.text(X0 + 0.02, Z1 - 0.33, "бак 200 л над биде (h 1400–2650)", fontsize=8.5, color="#B03A2E")
R(a, TX1, Z1 - 0.55, X1, Z1, "none", "", ec="#2F7FA8", lw=2, ls=":"); a.text(X1 - 0.02, Z1 - 0.58, "бойлер (h 1800+)", fontsize=8.5, color="#2F7FA8", ha="right")
R(a, 0.53, Z1 - 0.70, 0.89, Z1 - 0.20, "white", NL.join(["биде", "360×500"]), 10)
R(a, 1.25, Z1 - 0.75, 1.61, Z1 - 0.20, "white", "унитаз", 10)
a.annotate("", (0.71, SZ1), (0.71, Z1 - 0.70), arrowprops=dict(arrowstyle="<->", color="#2E7D4F", lw=2)); a.text(0.75, SZ1 + 0.30, "610 мм", fontsize=11, color="#2E7D4F", fontweight="bold")
a.text(X0 + 0.02, 7.95, NL.join(["боковой пенал", "УБРАН — стена", "свободна"]), fontsize=9, color="#2E7D4F")
a.text(X0 - 0.1, Z0 - 0.25, "ВИД СВЕРХУ", fontsize=13, fontweight="bold")
a.set_xlim(X0 - 0.2, X1 + 0.45); a.set_ylim(Z1 + 0.2, Z0 - 0.35); a.set_aspect("equal"); a.axis("off")
fig.text(0.03, 0.03, NL.join([
    "БАК 200 л — наверху, в графитовом шкафу до потолка над биде: плоский, под заказ 580 × 300 × 1150 (= 200 л), на стальной раме, крепится к стене и инсталляции; насос — рядом в шкафу.",
    "Справа — бойлер Б2 над унитазом, под ним полки. Вся стена с инсталляцией — один шкаф до потолка. Боковой пенал у биде убран."]), fontsize=11.5, color="#B03A2E", fontweight="bold")
plt.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.12); plt.savefig(OUT); print(OUT)
