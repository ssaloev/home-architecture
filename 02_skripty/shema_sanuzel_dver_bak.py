# -*- coding: utf-8 -*-
"""Санузел — вид сверху: как открывается дверь душа (раздвижная, «купе») и где стоит бак 200 л (13.11.2026)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_sanuzel_dver_bak.png")
NL = chr(10)
X0, X1, Z0, Z1 = 0.309, 1.836, 6.8, 9.018
SX1, SZ1 = 1.018, 7.709
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
# душ
R(X0, Z0, SX1, SZ1, "#CFE3EC", NL.join(["ДУШ", "700×900"]), 13, ec="#2F7FA8")
ax.plot([SX1, SX1], [Z0, SZ1], color="#2F7FA8", lw=4); ax.text(SX1 + 0.03, 7.0, NL.join(["глухое", "стекло"]), fontsize=10, color="#2F7FA8")
ax.add_patch(Rectangle((X0 + 0.10, Z0 + 0.0), 0.50, 0.12, fc="#999", ec="#555")); ax.text(X0 + 0.35, Z0 + 0.20, "ниша 3 полки", ha="center", fontsize=9)
# раздвижная дверь: закрыта (пунктир) и открыта (сплошная) + рельс
ax.plot([X0 + 0.02, X0 + 1.44], [SZ1 + 0.02, SZ1 + 0.02], color="#111", lw=2); ax.text(X0 + 1.44, SZ1 - 0.02, " рельс", fontsize=10, va="bottom")
ax.plot([X0 + 0.02, X0 + 0.72], [SZ1 + 0.035, SZ1 + 0.035], color="#B03A2E", lw=3, ls="--")
ax.plot([X0 + 0.72, X0 + 1.42], [SZ1 + 0.055, SZ1 + 0.055], color="#B03A2E", lw=5)
ax.add_patch(FancyArrowPatch((X0 + 0.25, SZ1 + 0.16), (X0 + 0.95, SZ1 + 0.16), arrowstyle="-|>", mutation_scale=30, color="#B03A2E", lw=2.5))
ax.text(X0 + 1.10, SZ1 + 0.16, "1", ha="center", va="center", fontsize=16, color="white", fontweight="bold", bbox=dict(boxstyle="circle", fc="#B03A2E", ec="none"))
ax.text(X0 + 0.37, SZ1 - 0.06, "закрыта", ha="center", fontsize=9, color="#B03A2E")
ax.text(X0 + 1.07, SZ1 - 0.06, "открыта", ha="center", fontsize=9, color="#B03A2E")
# раковина
R(1.058, Z0, 1.558, Z0 + 0.40, "#8E8E8E", NL.join(["раковина", "+ тумба"]), 10, "white")
# бак
R(X0, 7.74, X0 + 0.24, 8.26, "#2F2F31", "", ec="#B03A2E", lw=3)
ax.add_patch(Rectangle((X0 + 0.01, 7.76), 0.20, 0.48, fc="white", ec="#555"))
ax.text(X0 + 0.45, 8.0, "2", ha="center", va="center", fontsize=16, color="white", fontweight="bold", bbox=dict(boxstyle="circle", fc="#B03A2E", ec="none"))
ax.text(X0 - 0.2, Z1 + 0.25, NL.join(["1 — ДВЕРЬ ДУША: раздвижная «купе», стекло 700 едет ВПРАВО по рельсу вдоль душа;", "     в комнату не открывается, раковине и биде не мешает.",
        "2 — БАК 200 л ЗДЕСЬ: узкий, под заказ 520 × 220 × высота 2000, стоит у стены", "     между душем и биде в графитовом пенале до потолка, насос сверху."]), fontsize=12, color="#B03A2E", fontweight="bold", va="top")
# инсталляции, биде, унитаз, бойлер
R(X0, Z1 - 0.20, X1, Z1, "#BDBDBD", "короб инсталляций + шкаф до потолка", 9)
R(0.53, Z1 - 0.75, 0.89, Z1 - 0.20, "white", "биде", 11)
R(1.25, Z1 - 0.75, 1.61, Z1 - 0.20, "white", "унитаз", 11)
ax.add_patch(Circle((1.43, Z1 - 0.435), 0.225, fc="none", ec="#2F7FA8", ls=":", lw=2))
ax.text(1.43, Z1 - 0.88, "бойлер Б2 — над унитазом", ha="center", fontsize=10, color="#2F7FA8")
ax.set_title("САНУЗЕЛ — вид сверху: дверь душа и бак 200 л", fontsize=15, fontweight="bold")
ax.set_xlim(X0 - 0.3, X1 + 0.6); ax.set_ylim(Z1 + 0.85, Z0 - 0.35); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig(OUT); print(OUT)
