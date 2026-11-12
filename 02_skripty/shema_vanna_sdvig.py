# -*- coding: utf-8 -*-
"""Ванная: проверка предложения заказчика (13.11) — ванна сдвинута к унитазу, стиралка в ванной слева от раковины."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_vanna_sdvig.png")
NL = chr(10)
X0, X1, Z0, Z1 = 3.564, 6.073, 8.018, 9.509
fig, axs = plt.subplots(1, 2, figsize=(18, 8.2), dpi=120)
def panel(ax, BL, title):
    def R(x0, z0, x1, z1, fc, t="", fs=9, col="#222", ec="#555", ls="-", lw=1.3):
        ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls))
        if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
    def dim(x0, z0, x1, z1, t, col="#B03A2E"):
        ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.2))
        ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=10, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.25))
    ax.add_patch(Rectangle((X0 - 0.12, Z0 - 0.12), X1 - X0 + 0.24, Z1 - Z0 + 0.24, fc="#3A3632"))
    R(X0, Z0, X1, Z1, "#E9E9E9", ec="none")
    ax.add_patch(Rectangle((4.255, Z0 - 0.12), 0.8, 0.12, fc="white", ec="#888"))
    ax.add_patch(Arc((4.255, Z0), 1.6, 1.6, theta1=0, theta2=90, color="#999", lw=1, ls="--"))
    BX0 = X1 - BL
    R(BX0, Z1 - 0.70, X1, Z1, "white", "ванна %d×700" % round(BL * 1000), 11)
    R(X0, 8.06, X0 + 0.48, 8.66, "#8E8E8E", NL.join(["раковина", "600"]), 8.5, col="white")
    R(X0 + 0.05, 8.86, X0 + 0.65, 9.46, "white", NL.join(["стиралка", "10 кг"]), 8.5, ec="#333")
    gap = BX0 - (X0 + 0.65)
    ok = gap >= 0.55
    R(X0 + 0.65, 8.86, BX0, 9.46, ("#DFF0E6" if ok else "#F6D5D0"), "", ec=("#2E7D4F" if ok else "#B03A2E"), ls="--")
    dim(X0 + 0.65, 9.62, BX0, 9.62, "%d" % round(gap * 1000))
    ax.text(X0 + 0.65 + gap / 2, 9.16, NL.join(["место перед", "стиралкой"]), ha="center", fontsize=8, color=("#2E7D4F" if ok else "#B03A2E"))
    R(X1 - 0.20, 8.08, X1, 8.76, "#BDBDBD", "", ls="--"); R(X1 - 0.75, 8.235, X1 - 0.20, 8.595, "white", "унитаз", 8)
    dim(X0, 9.82, X1, 9.82, "2509")
    ax.set_xlim(3.3, 6.35); ax.set_ylim(10.0, 7.6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", color=("#2E7D4F" if ok else "#B03A2E"))
panel(axs[0], 1.70, NL.join(["Как вы предлагаете: ванна 1700 к унитазу,", "стиралка слева от раковины → дверцу НЕ открыть (160 мм)"]))
panel(axs[1], 1.30, NL.join(["Чтобы работало: ванна 1300×700 (короткая)", "→ перед стиралкой 559 мм; бак 200 л — места нет"]))
fig.suptitle("Ванная 2509 мм: ванна + стиралка 650 (со шлангами) + место перед ней ≥ 550 = нужно ≥ 2900", fontsize=13, fontweight="bold", x=0.02, ha="left")
plt.tight_layout(rect=(0, 0, 1, 0.93)); plt.savefig(OUT, facecolor="white"); print(OUT)
