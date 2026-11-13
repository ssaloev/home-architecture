# -*- coding: utf-8 -*-
"""13.11.2026: запас над головой сидящего на унитазе/биде под шкафом (санузел и ванная). Разрез: стена — короб — шкаф — человек."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse, Polygon
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_sanuzel_golova.png")
NL = chr(10)
HC = 2.65
fig, axs = plt.subplots(1, 2, figsize=(17, 9.5), dpi=105)
def scene(ax, title, low_d, low_top, ok):
    R = lambda x0, y0, x1, y1, fc, ec="#555", lw=1.0: ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw))
    R(-0.12, 0, 0, HC + 0.05, "#3A3632")                      # стена
    R(0, 0, 0.20, 1.12, "#BDBDBD"); ax.text(0.10, 0.6, "короб" + NL + "инстал." + NL + "200", ha="center", fontsize=9)
    R(0, 1.12, low_d, low_top, "#2F2F31"); ax.text(low_d / 2, (1.12 + low_top) / 2, f"{int(low_d*1000)}", ha="center", va="center", color="white", fontsize=9)
    R(0, low_top, 0.32, HC, "#2F2F31"); ax.text(0.16, (low_top + HC) / 2, "шкаф 320" + NL + "бак / бойлер", ha="center", va="center", color="white", fontsize=9)
    ax.add_patch(Ellipse((0.47, 0.40), 0.56, 0.16, fc="white", ec="#555"))   # унитаз
    R(0.20, 0.30, 0.30, 0.42, "white")
    # сидящий человек (рост 1,85): таз 0.45, плечи 1.00, голова центр ~1.22, макушка ~1.34
    ax.add_patch(Polygon([(0.30, 0.42), (0.62, 0.42), (0.55, 1.02), (0.30, 1.02)], fc="#E8D3BC", ec="#9C7E62"))
    ax.add_patch(Circle((0.40, 1.22), 0.11, fc="#E8D3BC", ec="#9C7E62"))
    ax.plot([0.25, 0.75], [1.34, 1.34], ls="--", color="#B03A2E"); ax.text(0.77, 1.34, "макушка сидящего 1340" + NL + "(рост 1,85)", fontsize=9, color="#B03A2E", va="center")
    ax.annotate("", (0.32, 1.40), (0.32, low_top), arrowprops=dict(arrowstyle="<->", color="#2E7D4F" if ok else "#B03A2E", lw=2))
    ax.text(0.34, (1.34 + low_top) / 2 + 0.03, f"запас {int(round((low_top - 1.34) * 1000))}", fontsize=10, color="#2E7D4F" if ok else "#B03A2E", fontweight="bold")
    ax.annotate("", (0.20, 1.06), (0.29, 1.06), arrowprops=dict(arrowstyle="<->", color="#555")); ax.text(0.245, 0.99, "голова ~400 от стены", fontsize=8, ha="center")
    for y in (1.12, low_top, HC): ax.text(-0.15, y, f"{int(round(y*1000))}", fontsize=9, ha="right", va="center")
    ax.set_title(title, fontsize=12, fontweight="bold", color="#2E7D4F" if ok else "#B03A2E", loc="left")
    ax.set_xlim(-0.35, 1.25); ax.set_ylim(-0.05, HC + 0.12); ax.set_aspect("equal"); ax.axis("off")
scene(axs[0], "БЫЛО: шкаф 320 с высоты 1120 — над головой", 0.32, 1.12, False)
scene(axs[1], "СТАЛО: низ 200 до 1550, выше 320", 0.20, 1.55, True)
fig.text(0.02, 0.03, NL.join([
    "Над унитазом и биде (санузел) и над унитазом (ванная): нижняя часть шкафа 1120–1550 — мелкая 200,",
    "заподлицо с коробом инсталляции — над головой ничего не нависает;",
    "глубокая часть 320 — с 1550 до потолка (запас над макушкой сидящего ростом 1,85 м ≈ 210 мм). Фасад единый, двери в одну линию.",
    "Бак 200 л — плоский прямоугольный 850×300×800 (слева, 1600–2400); бойлеры — плоские 470×875×285. Ничего не выпирает."]), fontsize=11.5, color="#7A3B1E", fontweight="bold")
plt.subplots_adjust(left=0.02, right=0.99, top=0.94, bottom=0.14); plt.savefig(OUT); print(OUT)
