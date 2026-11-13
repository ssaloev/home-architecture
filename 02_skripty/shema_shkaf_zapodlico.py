# -*- coding: utf-8 -*-
"""13.11.2026: шкаф над инсталляцией без выступа — варианты заподлицо с коробом (санузел и ванная)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_shkaf_zapodlico.png")
NL = chr(10); HC = 2.65
fig, axs = plt.subplots(1, 3, figsize=(19, 9), dpi=100)
def sc(ax, title, box_d, cab_d, front, col, note):
    R = lambda x0, y0, x1, y1, fc, ec="#555": ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec))
    R(-0.1, 0, 0, HC, "#3A3632"); R(0, 0, box_d, 1.12, "#BDBDBD"); R(0, 1.12, cab_d, HC, "#5C4636")
    ax.text(box_d / 2, 0.55, f"короб{NL}{int(box_d*1000)}", ha="center", fontsize=10)
    ax.text(cab_d / 2, 1.9, f"шкаф{NL}{int(cab_d*1000)}", ha="center", color="white", fontsize=10)
    ax.add_patch(Ellipse((box_d + 0.25, 0.40), 0.50, 0.14, fc="white", ec="#555"))
    ax.annotate("", (box_d + 0.50, 0.25), (box_d + 0.50 + front, 0.25), arrowprops=dict(arrowstyle="<->", color=col, lw=2))
    ax.text(box_d + 0.50 + front / 2, 0.12, f"перед биде {int(front*1000)}", ha="center", color=col, fontsize=11, fontweight="bold")
    if cab_d > box_d: ax.annotate("выступ " + str(int((cab_d - box_d) * 1000)), (cab_d, 1.15), (cab_d + 0.25, 1.35), color="#B03A2E", fontsize=11, arrowprops=dict(arrowstyle="->", color="#B03A2E"))
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left"); ax.text(0, -0.25, note, fontsize=10, va="top")
    ax.set_xlim(-0.2, 1.75); ax.set_ylim(-0.75, HC + 0.1); ax.set_aspect("equal"); ax.axis("off")
F0 = 0.61          # сейчас: перед биде 610 при коробе 200
sc(axs[0], "СЕЙЧАС: шкаф 320 над коробом 200", 0.20, 0.32, F0, "#2E7D4F", "шкаф выступает на 120 над коробом")
sc(axs[1], "ВАР. 1: короб тоже 320 (заподлицо)", 0.32, 0.32, F0 - 0.12, "#B03A2E", "ровная стена от пола до потолка," + NL + "но перед биде 490 (норма ≥600)")
sc(axs[2], "ВАР. 2: шкаф 200 (заподлицо с коробом)", 0.20, 0.20, F0, "#2E7D4F", "ровная стена, перед биде 610;" + NL + "бак плоский 200 мм (под заказ ~1000×200×1100 = 200 л)," + NL + "бойлер — плоский тонкий ~190 мм (есть 50–80 л)")
plt.subplots_adjust(left=0.02, right=0.99, top=0.93, bottom=0.05); plt.savefig(OUT); print(OUT)
