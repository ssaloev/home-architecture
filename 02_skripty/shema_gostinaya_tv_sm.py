# -*- coding: utf-8 -*-
"""Гостиная (13.11.2026): ТВ-стена по системе SM (лист 53, ТВ-стена со стеллажами) — под ТВ низкая рифлёная тумба 300 (шпон орех),
по бокам стеллажи 550 с подсветкой, за ТВ рифлёная вставка 500 с LED, рамка-молдинг. Строитель: «под телевизором — шпон»."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_gostinaya_tv_sm.png")
NL = chr(10)
Z0, Z1, H, HB = 0.309, 6.545, 2.70, 2.49
TOP = HB - 0.13 - 0.08                  # 80 под карнизом 130
tm = 3.44                               # центр ТВ-зоны (как сейчас)
SH = 0.55; UH = 0.30                    # стеллаж 550, тумба 300
C0, C1 = tm - 1.55, tm + 1.55           # центральная зона 3100 (как прежняя тумба)
S0 = (C0 - SH, C0); S1 = (C1, C1 + SH)
fig, ax = plt.subplots(figsize=(19, 9.5), dpi=105)
def R(x0, y0, x1, y1, fc, ec="#555", lw=1.0, t="", fs=9, col="#222"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw))
    if t: ax.text((x0 + x1) / 2, (y0 + y1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def dim(p, q, y, t, vert=False):
    if vert:
        ax.annotate("", (y, p), (y, q), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E")); ax.text(y + 0.04, (p + q) / 2, t, fontsize=8.5, color="#B03A2E", va="center")
    else:
        ax.annotate("", (p, y), (q, y), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#B03A2E")); ax.text((p + q) / 2, y + 0.03, t, fontsize=8.5, color="#B03A2E", ha="center")
R(Z0, 0, Z1, HB, "#EDE8DF", "#888"); R(Z0, HB, Z1, H, "#A9F5D2", "#2E8B57", t="короб, низ 2490", fs=8.5); R(Z0, HB - 0.13, Z1, HB, "#DCD6CC", "#888", t="карниз 130", fs=8)
# тумба 300, рифлёная, орех
R(S0[0], 0, S1[1], UH, "#5C4636", "#3A2A20", 1.4)
z = S0[0] + 0.02
while z < S1[1] - 0.02:
    ax.plot([z, z], [0.03, UH - 0.03], color="#47362A", lw=0.9); z += 0.025
ax.text((S0[0] + S1[1]) / 2, UH / 2, "ТУМБА 300 — рифлёный шпон ОРЕХА, 6 дверец, латунные ручки", ha="center", va="center", fontsize=10, color="white", fontweight="bold")
# стеллажи
for (a, b) in (S0, S1):
    R(a, UH, b, TOP, "#7A5E48", "#E9E1D3", 2.5)
    for hh in (0.75, 1.20, 1.65, 2.05):
        R(a + 0.03, hh, b - 0.03, hh + 0.02, "#E9E1D3", "none"); R(a + 0.03, hh - 0.012, b - 0.03, hh, "#FFD27A", "none")
    ax.text((a + b) / 2, 1.0, "стеллаж" + NL + "550" + NL + "LED", ha="center", fontsize=8.5, color="white")
# центр: рамка-молдинг + рифлёная вставка 500 с LED + ТВ
R(C0 + 0.10, UH + 0.10, C1 - 0.10, TOP, "none", "#8E8A84", 2.2)
R(C0 + 0.13, UH + 0.13, C1 - 0.13, TOP - 0.03, "none", "#B5B0A8", 0.8)
FL0, FL1 = 0, 0   # 13.11: рифлёную вставку убрали (заказчик)
ax.add_patch(Rectangle((tm - 0.95, 0.85), 1.90, 1.07, fc="#111", ec="#333", zorder=5)); ax.text(tm, 1.38, "ТВ 85″", ha="center", va="center", fontsize=11, color="white", zorder=6)
dim(C0, C1, TOP + 0.04, "3100 центральная зона"); dim(S0[0], S0[1], TOP + 0.04, "550"); dim(S1[0], S1[1], TOP + 0.04, "550")
dim(0, UH, S1[1] + 0.12, "300", vert=True); dim(UH, TOP, S1[1] + 0.12, f"{round((TOP-UH)*1000)}", vert=True)
ax.text(Z0, H + 0.12, "ТВ-СТЕНА по системе SM (лист 53): «под телевизором — шпон» (строитель)", fontsize=13, fontweight="bold")
ax.text(Z0, -0.2, "← окно", fontsize=9); ax.text(Z1, -0.2, "шкаф/вход →", fontsize=9, ha="right")
ax.text(Z0 + 0.4, 1.2, "рамки" + NL + "(система SM)", fontsize=9, color="#777"); ax.text(Z1 - 0.7, 0.6, "рамки" + NL + "(система SM)", fontsize=9, color="#777")
ax.set_xlim(Z0 - 0.2, Z1 + 0.5); ax.set_ylim(-0.5, H + 0.3); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.02, 0.03, NL.join([
    "Как у SM: вместо высокой графитовой тумбы — НИЗКАЯ тумба 300 во всю зону 4200, фасады — рифлёный шпон ореха (строитель: «под телевизором — шпон»).",
    "По бокам — открытые стеллажи 550 с подсветкой полок (внутри орех, рамка крем); ТВ — на стене в рамке-молдинге (профиль 90 + вторая рамка 30).",
    "Фон стены — крем, как остальные стены. Шкаф у входа — тоже рифлёный шпон ореха, латунные ручки."]), fontsize=11, color="#7A3B1E", fontweight="bold")
plt.subplots_adjust(left=0.02, right=0.99, top=0.95, bottom=0.14); plt.savefig(OUT); print(OUT)
