# -*- coding: utf-8 -*-
"""Схема коридора и прихожей с мебелью и размерами (по koridor_blender.py)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_chertezhi", "shema_koridor_mebel.png")
CX0, CX1, CZ0, CZ1 = 1.945, 9.945, 6.672, 7.909
PX0, PX1, PZ1 = 1.945, 3.455, 9.509
KX0, KZ1 = 6.0, 8.418
fig, ax = plt.subplots(figsize=(16, 7.5), dpi=150)
WALL = "#3A3632"
def R(x0, z0, x1, z1, fc, ec="#555", lw=1, **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=fc, edgecolor=ec, lw=lw, **kw))
def T(x, z, s, fs=9, **kw): ax.text(x, z, s, ha="center", va="center", fontsize=fs, **kw)
def dim(x0, z0, x1, z1, txt, off=0.0, col="#B03A2E", fs=9):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.2, shrinkA=0, shrinkB=0))
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    ax.text(xm + (off if x0 == x1 else 0), zm + (off if z0 == z1 else 0), txt, color=col, fontsize=fs, ha="center", va="center",
            fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.6))
# пол
R(CX0, CZ0, CX1, CZ1, "#F3ECE2", ec="none"); R(PX0, CZ1, PX1, PZ1, "#F3ECE2", ec="none"); R(KX0, CZ1, CX1, KZ1, "#F3ECE2", ec="none")
# стены
t = 0.12
for (x0, z0, x1, z1) in [(CX0 - t, CZ0 - t, 2.145, CZ0), (2.945, CZ0 - t, 8.145, CZ0), (8.945, CZ0 - t, 9.145, CZ0),
                         (PX1, CZ1, 4.255, CZ1 + t), (5.055, CZ1, KX0, CZ1 + t), (KX0 - t, CZ1 + t, KX0, KZ1 + t), (KX0, KZ1, CX1, KZ1 + t),
                         (CX1, CZ0 - t, CX1 + t, 6.75), (CX1, 7.55, CX1 + t, KZ1 + t),
                         (CX0 - t, CZ0, CX0, 7.0), (CX0 - t, 7.8, CX0, PZ1 + t), (PX1, CZ1, PX1 + t, PZ1 + t),
                         (PX0 - t, PZ1, 2.254, PZ1 + t), (3.145, PZ1, PX1 + t, PZ1 + t)]:
    R(x0, z0, x1, z1, WALL, ec=WALL)
# двери (проёмы)
for (x0, x1, z, lab, up) in [(2.145, 2.945, CZ0, "в гостиную", -1), (8.145, 8.945, CZ0, "в комнату", -1), (4.255, 5.055, CZ1, "в ванную", 1),
                             (2.254, 3.145, PZ1, "ВХОДНАЯ ДВЕРЬ 890", 1)]:
    ax.plot([x0, x1], [z, z], color="#1C1B1A", lw=3); T((x0 + x1) / 2, z + up * 0.2, lab, 8, color="#555")
for (z0, z1, x, lab, s) in [(7.0, 7.8, CX0, "санузел", -1), (6.75, 7.55, CX1, "спальня 2", 1)]:
    ax.plot([x, x], [z0, z1], color="#1C1B1A", lw=3); T(x + s * 0.32, (z0 + z1) / 2, lab, 8, color="#555", rotation=90)
ax.plot([9.145, 9.945], [CZ0, CZ0], color="#999", lw=1, ls="--"); T(9.55, CZ0 - 0.2, "к кухне", 8, color="#555")
# мебель
CW = "#E3D8C8"; OAK = "#D9B68A"
R(KX0, CZ1 + 0.0, CX1, KZ1, CW, lw=1.2); T((KX0 + CX1) / 2, (CZ1 + KZ1) / 2, "ШКАФЫ ВСТРОЕННЫЕ до потолка, 6 дверей", 9, fontweight="bold")
R(PX0, 7.95, PX0 + 0.40, 8.70, CW, lw=1.2); T(PX0 + 0.2, 8.32, "ШКАФ\nхозяев", 8, fontweight="bold")
R(PX0, 8.72, PX0 + 0.40, 9.30, OAK, lw=1.2); T(PX0 + 0.2, 9.01, "ГОСТИ\nштанга,\nскамья", 7.5, fontweight="bold")
R(PX1 - 0.24, 8.05, PX1, 9.25, CW, lw=1.2); T(PX1 - 0.12, 8.65, "ОБУВНИЦА 240 откидная + зеркало", 7.5, rotation=90, fontweight="bold")
R(3.7, 6.98, 9.4, 7.62, "none", ec="#B5A894", ls=":"); T(8.7, 7.30, "дорожка", 7, color="#8A7D6A")
for x in (2.75, 3.95, 5.15, 6.35, 7.55, 8.75):
    ax.add_patch(Circle((x, (CZ0 + CZ1) / 2), 0.12, fc="#FFF6D8", ec="#C9A227", lw=1))
for z in (8.55, 9.15): ax.add_patch(Circle(((PX0 + PX1) / 2 + 0.05, z), 0.12, fc="#FFF6D8", ec="#C9A227", lw=1))
# размеры
dim(9.75, CZ0, 9.75, CZ1, "1240", off=0.0)
dim(7.6, CZ0, 7.6, CZ1, "проход 1240")
dim(CX0, 6.25, CX1, 6.25, "коридор 8000")
dim(KX0, 8.75, CX1, 8.75, "шкафы 3945 × глуб. 510")
dim(PX0, 9.95, PX1, 9.95, "прихожая 1510")
dim(PX0 + 0.40, 8.85, PX1 - 0.24, 8.85, "проход 870")
dim(PX0, 7.75, PX0 + 0.40, 7.75, "400", fs=8)
dim(PX1 - 0.24, 7.75 + 0.0, PX1, 7.75, "240", fs=8)
dim(1.4, CZ1, 1.4, PZ1, "1600")
dim(PX0 + 0.20, 9.30, PX0 + 0.20, PZ1, "210", col="#2E7D32", fs=8)
T(7.9, 9.45, "Размеры прихожей предварительные — проверить на замере.\nЦифры в мм. Жёлтые круги — светильники Ø240, по периметру потолка и в плинтусах — LED-подсветка.", 9, color="#444")
ax.set_xlim(1.0, 10.5); ax.set_ylim(10.2, 5.9); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Коридор и прихожая — расстановка мебели и проходы", fontsize=15, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
