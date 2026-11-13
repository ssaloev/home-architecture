# -*- coding: utf-8 -*-
"""Гостиная (13.11.2026): переделка по примеру студии SM — дастархан в центре, люстра, ТВ-стена-акцент.
Слева — вид сверху, справа — развёртка ТВ-стены. На согласование."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_gostinaya_dastarhan.png")
NL = chr(10)
X0, X1, Z0, Z1, H = 1.946, 5.545, 0.309, 6.545, 2.70
WX0, WX1 = 2.673, 4.837
DX0, DX1 = 2.145, 2.945
TV0, TV1, TVD = 1.89, 4.99, 0.40            # ТВ-тумба вдоль левой стены, глубина 400
ST = ((1.04, 1.84), (5.04, 5.84))            # стеллажи с подсветкой по бокам, глубина 350
TX0, TX1, TZ0, TZ1 = 3.70, 4.60, 3.35, 5.35  # дастархан 2000×900, h 400 (13.11: сдвинут к шкафу — диван в углу у окна)
K = 0.60                                     # курпача
SZ0, SZ1 = Z0 + 0.02, Z0 + 2.42              # 13.11: диван в УГЛУ у окна — вдоль правой стены, лицом к ТВ
SX0, SX1 = X1 - 0.95, X1 - 0.02
WZ0 = 5.945                                  # встроенный шкаф
fig, (a1, a2) = plt.subplots(1, 2, figsize=(18, 11), dpi=110, gridspec_kw=dict(width_ratios=[1, 1.15]))
def R(ax, x0, y0, x1, y1, fc, t="", fs=10, col="#222", ec="#555", lw=1.2, ls="-", rot=0):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (y0 + y1) / 2, t, ha="center", va="center", fontsize=fs, color=col, rotation=rot)
def dim(ax, p, q, t, off=(0, 0), col="#2E7D4F"):
    ax.annotate("", p, q, arrowprops=dict(arrowstyle="<->", color=col, lw=1.6))
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], t, fontsize=10, color=col, fontweight="bold", ha="center", va="center")
# ================= вид сверху
a = a1; T = 0.14
R(a, X0, Z0, X1, Z1, "#EFE9DF", ec="none")
for (x0, z0, x1, z1) in ((X0 - T, Z0 - T, WX0, Z0), (WX1, Z0 - T, X1 + T, Z0), (X0 - T, Z0, X0, Z1 + T), (X1, Z0, X1 + T, Z1 + T),
                         (X0, Z1, DX0, Z1 + T), (DX1, Z1, X1, Z1 + T)):
    R(a, x0, z0, x1, z1, "#3A3632", ec="none")
R(a, WX0, Z0 - T, WX1, Z0, "#BFDCEB", ec="#2F7FA8"); a.text((WX0 + WX1) / 2, Z0 - 0.25, "окно 2160", ha="center", fontsize=10, color="#2F7FA8")
R(a, DX0, Z1, DX1, Z1 + T, "white", ec="#888"); a.text((DX0 + DX1) / 2, Z1 + 0.30, "вход", ha="center", fontsize=10)
# шкаф
R(a, 3.03, WZ0, X1, Z1, "#E3D9C8", "встроенный шкаф (остаётся)", 9)
# ТВ-стена
R(a, X0, TV0, X0 + TVD, TV1, "#4A4A4C", NL.join(["ТВ-тумба", "3100×400"]), 9, "white", rot=90)
for (s0, s1) in ST: R(a, X0, s0, X0 + 0.35, s1, "#57575A", "стеллаж", 8, "white", rot=90)
R(a, X0 - 0.02, 2.49, X0 + 0.03, 4.39, "#111")
# дастархан + курпачи
for (x0, z0, x1, z1) in ((TX0 - K, TZ0, TX0, TZ1), (TX1, TZ0, TX1 + K, TZ1), (TX0, TZ0 - K, TX1, TZ0)):
    a.add_patch(FancyBboxPatch((x0 + 0.02, z0 + 0.02), x1 - x0 - 0.04, z1 - z0 - 0.04, boxstyle="round,pad=0,rounding_size=0.06", fc="#E9E2D3", ec="#4F6B57", lw=1.2))
R(a, TX0, TZ0, TX1, TZ1, "#6B4A33", NL.join(["ДАСТАРХАН", "2000×900", "h 400", "на 8–10", "гостей"]), 10, "white", ec="#3A2618", lw=2)
a.text(TX0 - K / 2, (TZ0 + TZ1) / 2, "курпачи", rotation=90, ha="center", va="center", fontsize=9, color="#6B5030")
a.text(TX1 + K / 2, (TZ0 + TZ1) / 2, "курпачи", rotation=90, ha="center", va="center", fontsize=8.5, color="#6B5030")
# люстра
a.add_patch(Circle(((TX0 + TX1) / 2, (TZ0 + TZ1) / 2), 0.55, fc="none", ec="#C08A2E", lw=2.2, ls="--"))
a.text(TX0 - K, TZ0 - K - 0.10, "пунктир — люстра над столом", fontsize=9, color="#C08A2E", ha="left")
# диван у окна
a.add_patch(FancyBboxPatch((SX0, SZ0), SX1 - SX0, SZ1 - SZ0, boxstyle="round,pad=0,rounding_size=0.12", fc="#4F6B57", ec="#2F4536", lw=1.5))
a.text((SX0 + SX1) / 2, (SZ0 + SZ1) / 2, NL.join(["ВАШ ДИВАН", "зелёный", "в углу у окна,", "лицом к ТВ"]), ha="center", va="center", fontsize=9.5, color="white")
# 13.11: два ваших кресла + столик у окна (как в примере SM)
for cx in (2.95, 3.95):
    a.add_patch(FancyBboxPatch((cx - 0.40, Z0 + 0.15), 0.80, 0.80, boxstyle="round,pad=0,rounding_size=0.15", fc="#4F6B57", ec="#2F4536"))
    a.text(cx, Z0 + 0.55, "кресло", ha="center", va="center", fontsize=8.5, color="white")
a.add_patch(Circle((3.45, Z0 + 0.35), 0.17, fc="#E8E8E8", ec="#777"))
# проходы
dim(a, (X0 + TVD, 4.3), (TX0 - K, 4.3), "755", (0, -0.12))
a.text((X0 + TVD + TX0 - K) / 2, 4.65, NL.join(["проход", "от двери"]), ha="center", fontsize=8.5, color="#2E7D4F")
dim(a, (4.15, TZ1), (4.15, WZ0), "595", (0.25, 0))
dim(a, (TX1 + K, 5.0), (X1, 5.0), "345", (0, -0.12))
dim(a, (X0, Z0 - 0.45), (X1, Z0 - 0.45), "3600", (0, -0.12), "#555")
dim(a, (X1 + 0.30, Z0), (X1 + 0.30, Z1), "6236", (0.18, 0), "#555")
a.text(X0 - 0.1, Z0 - 0.75, "ВИД СВЕРХУ", fontsize=14, fontweight="bold")
a.set_xlim(X0 - 0.3, X1 + 0.65); a.set_ylim(Z1 + 0.5, Z0 - 0.9); a.set_aspect("equal"); a.axis("off")
# ================= развёртка ТВ-стены (смотрим на левую стену; слева — окно, справа — вход)
a = a2
R(a, Z0, -0.05, Z1, 0, "#3A3632"); R(a, Z0, H, Z1, H + 0.05, "#3A3632")
R(a, Z0, 0, Z1, H, "#F4EFE6", ec="#888")
R(a, Z0, H - 0.30, Z1, H, "#ECE6DA", ec="#bbb"); a.text((Z0 + Z1) / 2, H - 0.15, "потолок: короб ГКЛ + LED, ОДНА большая рамка, чёрные треки (по строителю)", ha="center", fontsize=8.5, color="#777")
for (s0, s1) in ST:
    R(a, s0, 0, s1, H - 0.30, "#57575A", ec="#3A3A3C")
    for hh in (0.55, 1.05, 1.55, 2.0):
        R(a, s0 + 0.03, hh, s1 - 0.03, hh + 0.025, "#3A3A3C", ec="none")
        R(a, s0 + 0.03, hh - 0.012, s1 - 0.03, hh, "#FFE7A8", ec="none")
    R(a, s0 + 0.03, 0, s1 - 0.03, 0.50, "#4A4A4C", "закрыто", 8, "white")
    a.text((s0 + s1) / 2, 1.3, NL.join(["стеллаж", "с LED", "350"]), ha="center", fontsize=8.5, color="white")
R(a, TV0, 0.75, TV1, H - 0.30, "#7A5A40", ec="#5A3F2C")                 # крем-панель с лепной рамкой (наш стиль)
for k in range(1, 6): a.plot([TV0 + k * 0.517] * 2, [0.75, H - 0.30], color="#5A3F2C", lw=0.8)
R(a, TV0, 0.08, TV1, 0.65, "#4A4A4C", ec="#2A2A2C")
for k in range(1, 4): a.plot([TV0 + k * 0.775] * 2, [0.1, 0.63], color="#5A4632", lw=1)
R(a, TV0, 0.65, TV1, 0.68, "#E9E4DA", ec="#999"); a.text((TV0 + TV1) / 2, 0.36, "тумба 3100 графит, латунь, камень", ha="center", fontsize=8.5, color="white")
R(a, 2.49, 0.95, 4.39, 2.02, "#111", "ТВ 85″", 11, "white")
for zz in (TV0 + 0.25, TV1 - 0.25):
    R(a, zz - 0.02, 1.05, zz + 0.02, 1.85, "#FFE7A8", ec="#C08A2E")
a.text(TV0 + 0.25, 0.85, "бра", ha="center", fontsize=8); a.text(TV1 - 0.25, 0.85, "бра", ha="center", fontsize=8)
a.text(TV0 + 0.05, H - 0.38, "ШПОН ореха (по строителю), LED по краю", fontsize=8.5, color="white", va="top")
a.text(Z0 + 0.02, -0.25, "← окно", fontsize=10); a.text(Z1 - 0.02, -0.25, "к шкафу/входу →", fontsize=10, ha="right")
a.text(Z0, H + 0.18, "ТВ-СТЕНА (левая стена) — стеллажи по примеру SM, цвета наши", fontsize=14, fontweight="bold")
a.set_xlim(Z0 - 0.15, Z1 + 0.15); a.set_ylim(-0.45, H + 0.35); a.set_aspect("equal"); a.axis("off")
fig.text(0.02, 0.025, NL.join([
    "ЦВЕТА ОСТАЮТСЯ НАШИ (по заказчику): стены крем с лепниной, графитовые тумба и стеллажи, зелёные шторы, ВАШ зелёный диван.",
    "Меняется расстановка по примеру SM: в центре ДАСТАРХАН 2000×900 (h 400) с курпачами на 8–10 человек, над ним люстра;",
    "по строителю: за ТВ — шпон ореха, рамки на стенах крупнее, на потолке одна большая рамка и треки; по бокам ТВ — графитовые стеллажи с подсветкой.",
    "Диван — в углу у окна, лицом к ТВ; у окна — 2 ваших кресла и столик. Проход вдоль ТВ — 755 мм. Курпачи можно убрать в шкаф — тогда зал свободный."]), fontsize=11.5, color="#7A3B1E", fontweight="bold")
plt.subplots_adjust(left=0.02, right=0.99, top=0.97, bottom=0.14); plt.savefig(OUT); print(OUT)
