# -*- coding: utf-8 -*-
"""Гостиная (13.11.2026): рамки на стенах по системе SM (лист 53): одна большая рамка на всю высоту, двойной профиль
(внешний 90 + внутренняя линия), отступы 100 сверху/снизу, картина 800×1050 в главной рамке. Наша высота под коробом 2490."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_gostinaya_ramki_sm.png")
NL = chr(10)
Z0, Z1, H, HB = 0.309, 6.545, 2.70, 2.49
SK, KC = 0.10, 0.13                 # плинтус 100, карниз под коробом 130 (как у SM)
TOP = HB - KC - 0.08; BOT = SK + 0.08   # отступы 80 (у SM 100, у нас ниже потолок)
PR = 0.09                           # профиль рамки 90
AC0, AC1 = 0.309, 1.45              # кондиционер у окна (верх 2250)
SOFA0, SOFA1 = 2.24, 4.64
WARD = Z1 - 0.62
fig, ax = plt.subplots(figsize=(19, 9.5), dpi=105)
def R(x0, y0, x1, y1, fc, ec="#555", lw=1.0, t="", fs=9, col="#222"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw))
    if t: ax.text((x0 + x1) / 2, (y0 + y1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def frame(a0, a1, label, pic=False):
    R(a0, BOT, a1, TOP, "none", "#6E6A64", 2.6)                       # внешний профиль 90
    R(a0 + PR, BOT + PR, a1 - PR, TOP - PR, "none", "#9A958D", 1.2)  # внутренняя кромка профиля
    R(a0 + PR + 0.03, BOT + PR + 0.03, a1 - PR - 0.03, TOP - PR - 0.03, "none", "#B5B0A8", 0.8)   # тонкая внутренняя линия
    for (cx, cy, sx, sy) in ():   # 13.11: уголки убрали
        ax.plot([cx, cx + sx * 0.17], [cy + sy * 0.02, cy + sy * 0.02], color="#8F8A82", lw=3.5); ax.plot([cx + sx * 0.02, cx + sx * 0.02], [cy, cy + sy * 0.17], color="#8F8A82", lw=3.5)
        ax.plot([cx + sx * 0.06], [cy + sy * 0.06], marker="*", ms=11, color="#8F8A82")
    ax.text((a0 + a1) / 2, TOP + 0.03, label, ha="center", fontsize=9.5, color="#B03A2E", fontweight="bold")
    if pic:
        pc = (a0 + a1) / 2; pb = 1.10          # низ картины выше спинки дивана
        R(pc - 0.35, pb, pc + 0.35, pb + 0.90, "#3C4E63", "#B8925A", 2, "картина" + NL + "700×900", 9, "white")
        ax.annotate("", (pc - 0.35, pb - 0.08), (a0 + PR, pb - 0.08), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E"))
        ax.text((a0 + PR + pc - 0.35) / 2, pb - 0.15, f"{round((pc - 0.35 - a0 - PR) * 1000)}", ha="center", fontsize=8.5, color="#B03A2E")
        ax.annotate("", (pc + 0.25, pb + 0.90), (pc + 0.25, TOP - PR), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E"))
        ax.text(pc + 0.28, (pb + 0.90 + TOP - PR) / 2, f"{round((TOP - PR - pb - 0.90) * 1000)}", fontsize=8.5, color="#B03A2E", va="center")
        ax.annotate("", (pc + 0.25, BOT + PR), (pc + 0.25, pb), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E"))
        ax.text(pc + 0.28, (BOT + PR + pb) / 2, f"{round((pb - BOT - PR) * 1000)}", fontsize=8.5, color="#B03A2E", va="center")
# стена, короб, карниз, плинтус
R(Z0, 0, WARD, HB, "#EDE8DF", "#888"); R(Z0, HB, WARD, H, "#A9F5D2", "#2E8B57", t="короб 280, низ 2490", fs=8.5)
R(Z0, HB - KC, WARD, HB, "#DCD6CC", "#888", t="карниз 130", fs=8); R(Z0, 0, WARD, SK, "#DCD6CC", "#888", t="плинтус 100", fs=7.5)
R(WARD, 0, Z1, H, "#4A4A4C", "#222", t="шкаф", fs=9, col="white")
# 13.11 согласовано (вариант Б): три равные большие рамки на всю стену, кондиционер внутри первой; без уголков и картины
AC0, AC1 = Z0 + 0.30, Z0 + 1.40
R(AC0, 1.95, AC1, 2.25, "#F4F4F4", "#999", t="кондиционер, 300 от угла" + NL + "верх 2250", fs=8.5)
e0, e1 = Z0 + 0.10, WARD - 0.12; wm = (e1 - e0 - 0.20) / 3
for k in range(3):
    frame(e0 + k * (wm + 0.10), e0 + k * (wm + 0.10) + wm, f"{round(wm*1000)}")
ax.add_patch(Rectangle((SOFA0, 0), SOFA1 - SOFA0, 0.95, fc="#4F6B57", ec="#2F4536", alpha=0.35)); ax.text((SOFA0 + SOFA1) / 2, 0.45, "ваш диван", ha="center", fontsize=10)
for (y0, y1, t) in ((0, SK, "100"), (SK, BOT, "80"), (BOT, TOP, f"{round((TOP-BOT)*1000)}"), (TOP, HB - KC, "80"), (HB - KC, HB, "130")):
    ax.annotate("", (Z0 - 0.15, y0), (Z0 - 0.15, y1), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E")); ax.text(Z0 - 0.19, (y0 + y1) / 2, t, fontsize=8.5, color="#B03A2E", va="center", ha="right")
ax.text(Z0, H + 0.12, "РАЗВЁРТКА: стена с диваном — три рамки (система SM, вариант Б)", fontsize=13, fontweight="bold")
ax.text(Z0, -0.22, "← окно", fontsize=9); ax.text(Z1, -0.22, "вход/шкаф →", fontsize=9, ha="right")
ax.set_xlim(Z0 - 0.5, Z1 + 0.1); ax.set_ylim(-0.6, H + 0.3); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.02, 0.03, NL.join([
    "Три равные рамки на всю стену (от окна до шкафа), кондиционер — внутри первой рамки, 300 от угла со шторой, верх 2250.",
    "Профиль рамки 90 (классический) + зазор 45 + вторая рамка 30 (как у SM, лист 53); без лепных уголков. Отступы: 80 от карниза 130 и над плинтусом 100."]), fontsize=11, color="#7A3B1E", fontweight="bold")
plt.subplots_adjust(left=0.02, right=0.99, top=0.95, bottom=0.14); plt.savefig(OUT); print(OUT)
