# -*- coding: utf-8 -*-
"""Гостиная (13.11.2026): потолок и стены ПО СИСТЕМЕ SM (лист 52 «Узел-1», листы 49–50), адаптация под нашу высоту 2700.
1) план потолка с привязками; 2) узел-1: их (3070) и наш (2700); 3) развёртка стены с диваном — рамки по их системе."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_gostinaya_potolok_sm.png")
NL = chr(10)
X0, X1, Z0, Z1, H = 1.946, 5.545, 0.309, 6.545, 2.70
NI = 0.15                     # ниша штор у окна
# ширины по чертежу SM (мм): короб 280 | 2-й уровень 215 + трек 35 + 150 | поле
W1, W2a, WT, W2b = 0.280, 0.215, 0.035, 0.150
# высоты: SM 3070 → наш 2700 (×0.6): поле −30, подъём 120 (карниз 100×105), ступень 60 (карниз 60×65)
HF, H2, H1 = 2.67, 2.55, 2.49
fig = plt.figure(figsize=(20, 12), dpi=100)
a1 = fig.add_axes([0.01, 0.12, 0.30, 0.82]); a2 = fig.add_axes([0.33, 0.52, 0.32, 0.42]); a2b = fig.add_axes([0.33, 0.12, 0.32, 0.36]); a3 = fig.add_axes([0.67, 0.12, 0.32, 0.82])
def R(ax, x0, y0, x1, y1, fc, t="", fs=9, col="#222", ec="#555", lw=1.0, ls="-"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (y0 + y1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def ring(ax, o0, o1, fc, zb0):
    for (x0, z0, x1, z1) in ((X0 + o0, zb0 + o0, X0 + o1, Z1 - o0), (X1 - o1, zb0 + o0, X1 - o0, Z1 - o0), (X0 + o1, zb0 + o0, X1 - o1, zb0 + o1), (X0 + o1, Z1 - o1, X1 - o1, Z1 - o0)):
        R(ax, x0, z0, x1, z1, fc, ec="none")
# ---------- 1. план потолка
a = a1; zb0 = Z0 + NI
R(a, X0 - 0.12, Z0 - 0.12, X1 + 0.12, Z1 + 0.12, "#3A3632", ec="none"); R(a, X0, Z0, X1, Z1, "white", ec="none")
R(a, X0, Z0, X1, zb0, "#BFDCEB", "ниша штор 150", 7)
ring(a, 0, W1, "#6FC7B5", zb0); ring(a, W1, W1 + W2a + WT + W2b, "#B7E5DA", zb0)
o = W1 + W2a; ring(a, o, o + WT, "#222", zb0)
o2 = W1 + W2a + WT + W2b
R(a, X0 + o2, zb0 + o2, X1 - o2, Z1 - o2, "white", NL.join(["ПОЛЕ", f"h {int(HF*1000)}", "подсветка", "из-за карниза"]), 10, ec="#C08A2E", lw=2)
for (o_, c_) in ((W1, "#888"), (o2, "#C08A2E")):
    R(a, X0 + o_, zb0 + o_, X1 - o_, Z1 - o_, "none", ec=c_, lw=1.6)
y = (zb0 + Z1) / 2
xs = [X0, X0 + W1, X0 + W1 + W2a, X0 + W1 + W2a + WT, X0 + o2]
for (p, q, t) in zip(xs[:-1], xs[1:], ("280", "215", "35", "150")):
    a.annotate("", (p, y), (q, y), arrowprops=dict(arrowstyle="<->", lw=0.9, color="#B03A2E")); a.text((p + q) / 2, y - 0.07, t, ha="center", fontsize=8, color="#B03A2E", rotation=90)
a.text(X0 + 0.14, zb0 + 1.5, f"короб h {int(H1*1000)}", rotation=90, fontsize=8, va="center"); a.text(X0 + W1 + 0.2, zb0 + 1.5, f"2-й уровень h {int(H2*1000)}", rotation=90, fontsize=8, va="center")
a.text(X1 - W1 - W2a - 0.05, zb0 + 2.4, "магнитный трек 35 по кругу", rotation=90, fontsize=8, va="center", color="#222")
a.text(X0, Z0 - 0.3, "ПЛАН ПОТОЛКА (как SM, лист 49)", fontsize=12, fontweight="bold")
a.text((X0 + X1) / 2, Z1 + 0.32, "← ТВ-стена слева | стена с диваном справа →", ha="center", fontsize=8.5)
a.set_xlim(X0 - 0.3, X1 + 0.3); a.set_ylim(Z1 + 0.5, Z0 - 0.45); a.set_aspect("equal"); a.axis("off")
# ---------- 2. узлы
def node(ax, slab, f, l2, l1, k1, k2, title, col):
    s = 1.0
    ax.add_patch(Rectangle((-0.05, slab), 1.30, 0.06, fc="#9A9A9A", ec="#555")); ax.add_patch(Rectangle((-0.05, 0), 0.05, slab, fc="#CCC", ec="#555"))
    ax.add_patch(Polygon([(0, slab), (1.25, slab), (1.25, f), (0.69, f), (0.69, l2), (0.28 + 0.41 * 0, l2), (0.28, l2), (0.28, l1), (0, l1)], fc="#A9F5D2", ec="#2E8B57"))
    ax.plot([0.69, 1.25], [f, f], color="#2E8B57")
    # карниз ступени
    ax.add_patch(Polygon([(0.28, l2), (0.28 + k1[1], l2), (0.28 + k1[1] * 0.3, l2 - k1[0] * 0.6), (0.28, l1 + 0.005)], fc="#DDD", ec="#555"))
    # трек
    ax.add_patch(Rectangle((0.495, l2), 0.035, 0.05, fc="#222")); ax.plot([0.512, 0.53], [l2, l2 - 0.06], color="#222", lw=4)
    # карниз у поля + подсветка
    ax.add_patch(Polygon([(0.69, l2 + 0.01), (0.69, f - 0.05), (0.69 + k2[1], f - 0.05), (0.69 + k2[1] * 0.4, l2 + k2[0] * 0.3)], fc="#DDD", ec="#555"))
    ax.plot([0.69 + 0.05], [f - 0.04], "o", color="#F0A030", ms=7)
    for (y0, y1, t) in ((l1, l2, f"{round((l2-l1)*1000)}"), (l2, f, f"{round((f-l2)*1000)}"), (f, slab, f"{round((slab-f)*1000)}")):
        ax.annotate("", (1.32, y0), (1.32, y1), arrowprops=dict(arrowstyle="<->", lw=0.9, color="#B03A2E")); ax.text(1.35, (y0 + y1) / 2, t, fontsize=9, va="center", color="#B03A2E")
    for (x0, x1_, t) in ((0, 0.28, "280"), (0.28, 0.495, "215"), (0.495, 0.53, "35"), (0.53, 0.69, "150")):
        ax.annotate("", (x0, l1 - 0.05), (x1_, l1 - 0.05), arrowprops=dict(arrowstyle="<->", lw=0.8)); ax.text((x0 + x1_) / 2, l1 - 0.10, t, ha="center", fontsize=8)
    ax.text(0.02, l1 + 0.01, f"низ короба {round(l1*1000)}", fontsize=8.5, va="bottom")
    ax.text(0.30 + k1[1], l2 - 0.03, f"карниз {int(k1[0]*1000)}×{int(k1[1]*1000)}", fontsize=8.5)
    ax.text(0.69 + k2[1] + 0.02, f - 0.08, f"карниз {int(k2[0]*1000)}×{int(k2[1]*1000)}" + NL + "+ LED подсветка", fontsize=8.5)
    ax.text(0.56, l2 - 0.10, "трек 35", fontsize=8.5)
    ax.set_title(title, fontsize=12, fontweight="bold", color=col, loc="left")
    ax.set_xlim(-0.1, 1.55); ax.set_ylim(l1 - 0.16, slab + 0.09); ax.set_aspect("equal"); ax.axis("off")
node(a2, 3.07, 3.02, 2.82, 2.72, (0.10, 0.065), (0.15, 0.155), "УЗЕЛ-1 у SM (потолок 3070)", "#555")
node(a2b, 2.70, HF, H2, H1, (0.06, 0.065), (0.10, 0.105), "НАШ УЗЕЛ (потолок 2700): те же ширины, высоты ×0,6", "#B03A2E")
# ---------- 3. развёртка стены с диваном (правая), рамки по системе SM
a = a3; L0, L1 = Z0, Z1 - 0.62       # до встроенного шкафа
R(a, L0, 0, L1, H1, "#EDE8DF", ec="#888"); R(a, L0, H1, L1, H, "#A9F5D2", ec="#2E8B57"); a.text((L0 + L1) / 2, (H1 + H) / 2, f"короб 280, низ {int(H1*1000)}", ha="center", va="center", fontsize=8)
# система SM: зазор сверху 80, профиль 80, верхняя рамка, зазор 90, нижняя рамка, 100 до пола
g_top, pr, gap, flo, low = 0.08, 0.08, 0.09, 0.10, 0.43
up = H1 - g_top - pr * 4 - gap - low - flo
_m = (L0 + L1) / 2
cols = [(L0 + 0.12, L0 + 1.12), (L0 + 1.26, _m - 0.07), (_m + 0.07, L1 - 1.26), (L1 - 1.12, L1 - 0.12)]
for (c0, c1) in cols:
    for (h0, h1) in ((flo + pr, flo + pr + low), (flo + 2 * pr + low + gap + pr, flo + 3 * pr + low + gap + up)):
        R(a, c0, h0 - pr, c1, h1 + pr, "none", ec="#777", lw=2.2); R(a, c0 + 0.015, h0 - pr + 0.015, c1 - 0.015, h1 + pr - 0.015, "none", ec="#AAA", lw=0.8)
        for (cx, cy) in ((c0 + 0.1, h1 - 0.02), (c1 - 0.1, h1 - 0.02), (c0 + 0.1, h0 + 0.02), (c1 - 0.1, h0 + 0.02)):
            a.plot([cx], [cy], marker=(5, 1), ms=9, color="#999")
    a.text((c0 + c1) / 2, flo + 2 * pr + low + gap + up / 2 + 0.3, f"{int(round((c1 - c0 - 0.16) * 1000))}", ha="center", fontsize=8.5, color="#B03A2E")
dims = [(0, flo, "100"), (flo + pr, flo + pr + low, f"{int(low*1000)}"), (flo + 2 * pr + low, flo + 2 * pr + low + gap, "90"), (flo + 3 * pr + low + gap, flo + 3 * pr + low + gap + up, f"{int(round(up*1000))}"), (H1 - g_top, H1, "80")]
for (y0, y1, t) in dims:
    a.annotate("", (L1 + 0.12, y0), (L1 + 0.12, y1), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E")); a.text(L1 + 0.16, (y0 + y1) / 2, t, fontsize=8.5, va="center", color="#B03A2E")
a.add_patch(Rectangle((2.24, 0), 2.40, 0.85, fc="#4F6B57", ec="#2F4536", alpha=0.35)); a.text(3.44, 0.5, "диван (ваш)", ha="center", fontsize=9)
a.text(L0, H + 0.12, "РАЗВЁРТКА: стена с диваном — рамки по системе SM", fontsize=12, fontweight="bold")
a.text(L0, -0.18, "← окно", fontsize=9); a.text(L1, -0.18, "шкаф →", fontsize=9, ha="right")
a.set_xlim(L0 - 0.1, L1 + 0.5); a.set_ylim(-0.3, H + 0.25); a.set_aspect("equal"); a.axis("off")
fig.text(0.01, 0.015, NL.join([
    "ПОТОЛОК КАК У SM (лист 52, Узел-1): короб 280 у стен → ступень с карнизом → 2-й уровень 215 + встроенный магнитный трек 35 + 150 → подъём к полю с карнизом и LED-подсветкой на поле.",
    "Ширины — точно как у SM.",
    f"Высоты: у SM потолок 3070 и короб опущен на 350 — у нас 2700, поэтому ×0,6: поле {int(HF*1000)}, 2-й уровень {int(H2*1000)}, низ короба {int(H1*1000)}. Карнизы: 60×65 и 100×105 (у SM 100×65 и 150×155). ",
    "Стены — 2 рамки по высоте с лепными уголками (как у SM)."]),
    fontsize=11, color="#7A3B1E", fontweight="bold")
plt.savefig(OUT); print(OUT)
