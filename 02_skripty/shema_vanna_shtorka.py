# -*- coding: utf-8 -*-
"""Ванная — вид сверху (13.11.2026): ванна без стекла, тканевая шторка на Г-карнизе; сплошная столешница; шкафы до потолка."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_vanna_shtorka.png")
NL = chr(10)
X0, X1, Z0, Z1 = 3.564, 6.073, 8.018, 9.509
DX0, DX1 = 4.255, 5.055
SZ0, SZ1, CD = 8.06, 8.66, 0.62
WZ0, WZ1 = 8.84, 9.44
BX0, BZ0 = X1 - 1.30, Z1 - 0.70
fig, ax = plt.subplots(figsize=(13, 10), dpi=120)
T = 0.12
ax.add_patch(Rectangle((X0, Z0), X1 - X0, Z1 - Z0, fc="#E6E6E6"))
for (a, b, c, d) in ((X0 - T, Z1, X1 + T, Z1 + T), (X0 - T, Z0, X0, Z1), (X1, Z0, X1 + T, Z1), (X0 - T, Z0 - T, DX0, Z0), (DX1, Z0 - T, X1 + T, Z0)):
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc="#3A3632"))
ax.add_patch(Rectangle((DX0, Z0 - T), DX1 - DX0, T, fc="white", ec="#888")); ax.text((DX0 + DX1) / 2, Z0 - 0.20, "вход в ванную", ha="center", fontsize=11)
def R(x0, z0, x1, z1, fc, t="", fs=11, col="#222", ec="#555", lw=1.5):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def num(x, z, n):
    ax.text(x, z, n, ha="center", va="center", fontsize=16, color="white", fontweight="bold", bbox=dict(boxstyle="circle", fc="#B03A2E", ec="none"))
# левая стена: сплошная столешница h900 от раковины до угла, стиралка под ней, шкаф над ней до потолка
R(X0, SZ0, X0 + CD, Z1, "#D8D2C6", "", ec="#555")
ax.add_patch(Circle((X0 + 0.30, (SZ0 + SZ1) / 2), 0.20, fc="white", ec="#555")); ax.text(X0 + 0.30, (SZ0 + SZ1) / 2, "раковина", ha="center", va="center", fontsize=10)
R(X0 + 0.02, WZ0, X0 + 0.60, WZ1, "white", NL.join(["стиралка", "под столешницей"]), 9.5)
ax.add_patch(Rectangle((X0, SZ1 + 0.02), 0.35, Z1 - SZ1 - 0.03, fc="none", ec="#2F2F31", ls="--", lw=2))
ax.text(X0 + CD + 0.05, 9.0, NL.join(["шкаф над стиралкой", "до потолка"]), fontsize=9, color="#2F2F31")
num(X0 + CD + 0.25, SZ0 + 0.15, "2")
# ванна + Г-карниз + шторка
R(BX0, BZ0, X1, Z1, "#CFE3EC", NL.join(["ВАННА", "1300×700"]), 13, ec="#2F7FA8")
ax.plot([X1, BX0, BX0], [BZ0, BZ0, Z1], color="#111", lw=2.5)
xx = np.linspace(X1 - 0.30, X1 - 0.02, 20); ax.plot(xx, BZ0 + 0.03 + 0.025 * np.sin(xx * 90), color="#7A4B22", lw=3)
zz = np.linspace(BZ0 + 0.03, Z1 - 0.02, 25); ax.plot(BX0 + 0.03 + 0.02 * np.sin(zz * 70), zz, color="#7A4B22", lw=2.5)
ax.text(X1 - 0.16, BZ0 - 0.07, "шторка собрана", ha="center", fontsize=9, color="#7A4B22")
ax.text(BX0 - 0.03, BZ0 - 0.07, "Г-карниз под потолком", ha="right", fontsize=9, color="#7A4B22")
num(BX0 + 0.35, BZ0 + 0.20, "1")
# правая стена: унитаз, шкаф с бойлером над ним
R(X1 - 0.20, 8.06, X1, 8.78, "#BDBDBD", "", 9)
R(X1 - 0.75, 8.415 - 0.18, X1 - 0.20, 8.415 + 0.18, "white", "унитаз", 10)
ax.add_patch(Rectangle((X1 - 0.55, 8.06), 0.55, 0.72, fc="none", ec="#2F7FA8", ls=":", lw=2))
ax.text(X1 - 0.85, 8.10, NL.join(["бойлер Б1 в шкафу", "над унитазом"]), fontsize=9, color="#2F7FA8", ha="right", va="top")
ax.text(X0 - 0.15, Z1 + 0.30, NL.join([
    "1 — ВАННА БЕЗ СТЕКЛА: тканевая шторка на Г-карнизе под потолком (вдоль ванны и у торца).",
    "     Собирается к стене; снять и постирать — легко. Душ: лейка на штанге + ручная лейка со шлангом.",
    "2 — Одна сплошная столешница h 900 от раковины до угла, стиралка под ней,",
    "     над стиралкой шкаф до потолка (порошки, полотенца)."]), fontsize=12, color="#B03A2E", fontweight="bold", va="top")
ax.set_title("ВАННАЯ: шторка на Г-карнизе вместо стекла", fontsize=15, fontweight="bold")
ax.set_xlim(X0 - 0.3, X1 + 0.3); ax.set_ylim(Z1 + 0.85, Z0 - 0.35); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig(OUT); print(OUT)
