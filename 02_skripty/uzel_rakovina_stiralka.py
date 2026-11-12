# -*- coding: utf-8 -*-
"""Узел: раковина «кувшинка» над стиральной машиной 10 кг (ванная) — разрез сбоку и вид спереди, размеры. 13.11.2026"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "uzel_rakovina_stiralka.png")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 9), dpi=130)
def dim(ax, x0, y0, x1, y1, t, col="#B03A2E"):
    ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", color=col, lw=1))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, t, color=col, fontsize=10, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
# ---------------- разрез сбоку (стена слева)
ax = a1
ax.add_patch(Rectangle((-120, -40), 120, 2340, fc="#8E8E8E")); ax.text(-60, 2150, "стена", ha="center", fontsize=9, color="white", rotation=90)
ax.add_patch(Rectangle((0, -40), 1000, 40, fc="#8E8E8E"))
ax.add_patch(Rectangle((100, 0), 600, 850, fc="white", ec="#333", lw=1.5))
ax.text(400, 450, "стиральная\nмашина 10 кг\n600 × 600 × 850", ha="center", va="center", fontsize=11)
ax.add_patch(Rectangle((700, 300), 18, 280, fc="#555"))
ax.add_patch(Rectangle((15, 120), 70, 700, fc="#E6F0F5", ec="#2F7FA8", ls=":"))
ax.text(50, 470, "шланги\nкран\nслив", fontsize=8, ha="center", va="center", color="#2F7FA8")
ax.add_patch(Rectangle((0, 880), 720, 40, fc="#7A7A7A", ec="#333"))
ax.text(360, 860, "рама/столешница 40 мм, плитка", fontsize=8.5, ha="center", va="top")
ax.add_patch(FancyBboxPatch((120, 920), 600, 110, boxstyle="round,pad=0,rounding_size=25", fc="#F4F4F2", ec="#333", lw=1.5))
ax.text(420, 975, "раковина «кувшинка» 600×600", fontsize=9.5, ha="center")
ax.add_patch(Rectangle((0, 930), 280, 24, fc="#111"))
ax.annotate("плоский сифон — лежит СВЕРХУ,\nуходит НАЗАД в стену (не вниз!)", (150, 945), (160, 1260), fontsize=9.5, ha="left",
            arrowprops=dict(arrowstyle="->", color="#111"), fontweight="bold")
ax.add_patch(Rectangle((0, 1150), 60, 40, fc="#222")); ax.add_patch(Rectangle((60, 1165), 200, 14, fc="#222")); ax.text(270, 1110, "смеситель из стены", fontsize=9)
ax.add_patch(Rectangle((0, 1450), 30, 800, fc="#C9D3D6", ec="#222")); ax.text(60, 1850, "зеркало с LED", fontsize=9, rotation=90, va="center")
ax.add_patch(Rectangle((-10, 300), 10, 50, fc="#B03A2E")); ax.text(-140, 325, "розетка стиралки\nIP44, сбоку", fontsize=8, ha="right", color="#B03A2E")
dim(ax, 820, 0, 820, 850, "850"); dim(ax, 920, 0, 920, 1030, "1030")
ax.text(760, 865, "зазор 30", fontsize=8, va="center", color="#B03A2E")
dim(ax, 0, -150, 100, -150, "100"); dim(ax, 100, -150, 700, -150, "600"); dim(ax, 0, -270, 720, -270, "720 от стены")
ax.set_xlim(-520, 1050); ax.set_ylim(-340, 2300); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Разрез сбоку", fontsize=13, fontweight="bold", loc="left")
# ---------------- вид спереди
ax = a2
ax.add_patch(Rectangle((0, -40), 780, 40, fc="#8E8E8E"))
ax.add_patch(Rectangle((90, 0), 600, 850, fc="white", ec="#333", lw=1.5))
ax.add_patch(Circle((390, 430), 190, fc="#2B2D2F", ec="#111", lw=6))
ax.add_patch(Rectangle((0, 880), 780, 40, fc="#7A7A7A", ec="#333"))
ax.add_patch(FancyBboxPatch((90, 920), 600, 110, boxstyle="round,pad=0,rounding_size=25", fc="#F4F4F2", ec="#333", lw=1.5))
ax.add_patch(Rectangle((370, 1150), 40, 60, fc="#222")); ax.add_patch(Rectangle((380, 1080), 20, 80, fc="#222"))
ax.add_patch(Rectangle((40, 1450), 700, 800, fc="#C9D3D6", ec="#111", lw=3)); ax.text(390, 1850, "зеркало 700×800\nподсветка за зеркалом", ha="center", fontsize=10)
dim(ax, 0, -150, 780, -150, "780 — ниша от двери до ванны")
ax.text(390, -360, "Как это работает: обычная раковина сливает ВНИЗ — туда, где стоит машина, поэтому так нельзя.\n"
        "«Кувшинка» — плоская раковина со сливом НАЗАД: сифон лежит над машиной и уходит в стену.\n"
        "Так делают в маленьких ванных; раковины продаются готовыми комплектами с плоским сифоном.",
        ha="center", fontsize=10)
ax.set_xlim(-60, 840); ax.set_ylim(-520, 2300); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Вид спереди", fontsize=13, fontweight="bold", loc="left")
fig.suptitle("Ванная — раковина «кувшинка» над стиральной машиной 10 кг", fontsize=15, fontweight="bold", x=0.02, ha="left")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
