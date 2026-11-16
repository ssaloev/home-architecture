# -*- coding: utf-8 -*-
"""16.11.2026: обмерные листы для заказчика (на объекте, с телефона) — пустые графы для реальных размеров.
1) план: стены, двери Д1…, окна О1…, комнаты — длина/ширина/высота ___; стояки и трубы — вписать;
2) потолок: вентиляция/вытяжки В1…, трубы, балки, короба — нарисовать и вписать размеры от стен.
Вертикально под телефон (ширина 1080 px × 1.5)."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUTD = os.path.join(os.path.dirname(HERE), "01_chertezhi")
xs = [q[0] for r in D["rooms"] for q in r["rects"]] + [q[1] for r in D["rooms"] for q in r["rects"]]
zs = [q[2] for r in D["rooms"] for q in r["rects"]] + [q[3] for r in D["rooms"] for q in r["rects"]]
BL = "______"

def base(ax, doors=True):
    for r in D["rooms"]:
        for (x0, x1, z0, z1) in r["rects"]: ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc="#FBFAF7", ec="none"))
    for (x, z, w, d) in D["walls"]: ax.add_patch(Rectangle((x, z), w, d, fc="#3A3632", ec="#3A3632"))
    for k, wn in enumerate(D["windows"], 1):
        x, z, w, d = wn["rect"]; ax.add_patch(Rectangle((x, z), w, d, fc="#BFE0F2", ec="#2C6E91", lw=1))
        if doors: ax.text(x + w / 2, z + d / 2, f"О{k}", ha="center", va="center", fontsize=9, fontweight="bold", color="#1F4E79",
                          bbox=dict(fc="white", ec="#1F4E79", boxstyle="round,pad=0.15"))
    for k, dr in enumerate(D["doors"], 1):
        x, z, w, d = dr["rect"]; ax.add_patch(Rectangle((x, z), w, d, fc="#F3D9A4", ec="#8A5A00", lw=1))
        if doors: ax.text(x + w / 2, z + d / 2, f"Д{k}", ha="center", va="center", fontsize=9, fontweight="bold", color="#8A5A00",
                          bbox=dict(fc="white", ec="#8A5A00", boxstyle="round,pad=0.15"))
    ax.set_xlim(min(xs) - 0.3, max(xs) + 0.3); ax.set_ylim(max(zs) + 0.4, min(zs) - 0.3); ax.set_aspect("equal"); ax.axis("off")

def table(ax, cols, rows, widths, fs=9.5, sc=2.0):
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=cols, loc="upper center", cellLoc="left", colWidths=widths)
    t.auto_set_font_size(False); t.set_fontsize(fs); t.scale(1, sc)
    for (r, c), cell in t.get_celld().items():
        if r == 0: cell.set_facecolor("#333"); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        elif cell.get_text().get_text().startswith("_"): cell.set_facecolor("#FFF6D5")

# ============ 1. ПЛАН: стены, двери, окна, комнаты, стояки
fig = plt.figure(figsize=(10.8, 24), dpi=150)
fig.text(0.03, 0.985, "ОБМЕР 1 — комнаты, двери, окна, стояки", fontsize=18, fontweight="bold")
fig.text(0.03, 0.976, "Рулеткой, в мм. Жёлтые клетки — вписать. Стояки/трубы/щиты — отметить точкой на плане и вписать внизу.", fontsize=10.5)
ax = fig.add_axes([0.03, 0.75, 0.94, 0.22]); base(ax)
for k, r in enumerate(D["rooms"], 1):
    x0, x1, z0, z1 = max(r["rects"], key=lambda q: (q[1] - q[0]) * (q[3] - q[2]))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, f"П{k}\n{r['name']}", ha="center", va="center", fontsize=9, color="#555")
rows = [[f"П{k}", r["name"], BL, BL, BL] for k, r in enumerate(D["rooms"], 1)]
table(fig.add_axes([0.03, 0.555, 0.94, 0.18]), ["№", "Комната", "Длина", "Ширина", "Высота до потолка"], rows, [0.07, 0.30, 0.20, 0.20, 0.23])
rows = [[f"Д{k}", dr["name"], BL, BL, BL] for k, dr in enumerate(D["doors"], 1)]
table(fig.add_axes([0.03, 0.375, 0.94, 0.17]), ["№", "Дверь / проём", "Ширина проёма", "Высота проёма", "Толщина стены"], rows, [0.07, 0.30, 0.21, 0.21, 0.21])
rows = [[f"О{k}", BL, BL, BL, BL] for k, _ in enumerate(D["windows"], 1)]
table(fig.add_axes([0.03, 0.245, 0.94, 0.125]), ["№", "Ширина окна", "Подоконник от пола", "Верх окна от пола", "Глубина откоса"], rows, [0.07, 0.22, 0.24, 0.24, 0.23])
rows = [[f"Т{k}", BL, BL, BL, BL] for k in range(1, 7)]
table(fig.add_axes([0.03, 0.04, 0.94, 0.195]), ["№", "Что (ХВС/ГВС/канализ./отопл./газ/щит)", "Комната", "От стен: X / Y", "Диаметр / размер"], rows, [0.07, 0.33, 0.18, 0.21, 0.21])
fig.text(0.03, 0.02, "Пример: «Т1 — канализация Ø110, санузел, 250 от левой стены / 180 от задней».", fontsize=10, color="#555")
f1 = os.path.join(OUTD, "obmer_1_plan.png"); plt.savefig(f1); plt.close(fig); print(f1)

# ============ 2. ПОТОЛОК: вентиляция, вытяжки, трубы, балки
fig = plt.figure(figsize=(10.8, 15), dpi=150)
fig.text(0.03, 0.98, "ОБМЕР 2 — потолок: вентиляция, трубы, балки", fontsize=18, fontweight="bold")
fig.text(0.03, 0.966, "Нарисуйте на плане значком и впишите размеры от двух стен. Высоту потолка — в 2–3 точках комнаты.", fontsize=10.5)
ax = fig.add_axes([0.03, 0.60, 0.94, 0.35]); base(ax, doors=False)
for k, r in enumerate(D["rooms"], 1):
    x0, x1, z0, z1 = max(r["rects"], key=lambda q: (q[1] - q[0]) * (q[3] - q[2]))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, f"{r['name']}\nh = ____", ha="center", va="center", fontsize=9, color="#555")
lg = fig.add_axes([0.03, 0.55, 0.94, 0.045]); lg.axis("off"); lg.set_xlim(0, 10); lg.set_ylim(0, 1)
lg.add_patch(Rectangle((0.1, 0.25), 0.45, 0.5, fc="white", ec="#1F4E79", lw=2)); lg.plot([0.1, 0.55], [0.25, 0.75], c="#1F4E79"); lg.plot([0.1, 0.55], [0.75, 0.25], c="#1F4E79")
lg.text(0.7, 0.5, "В — вентканал / вытяжка", va="center", fontsize=10)
lg.add_patch(Circle((3.9, 0.5), 0.2, fc="#B03A2E")); lg.text(4.2, 0.5, "Т — труба / стояк", va="center", fontsize=10)
lg.add_patch(Rectangle((6.6, 0.3), 0.7, 0.4, fc="#BBBBBB", ec="#555", hatch="//")); lg.text(7.45, 0.5, "Б — балка / короб", va="center", fontsize=10)
rows = [[f"{c}{k}", BL, BL, BL, BL] for c, n in (("В", 6), ("Т", 4), ("Б", 4)) for k in range(1, n + 1)]
table(fig.add_axes([0.03, 0.04, 0.94, 0.50]), ["№", "Комната", "От стен: X / Y", "Размер (Ш×Г или Ø)", "Низ от пола / выступ"], rows, [0.07, 0.22, 0.23, 0.24, 0.24], sc=2.3)
fig.text(0.03, 0.015, "Важно для потолка: всё, что ниже 2600 от пола, и решётки вытяжек в санузле, ванной, кухне.", fontsize=10, color="#555")
f2 = os.path.join(OUTD, "obmer_2_potolok.png"); plt.savefig(f2); plt.close(fig); print(f2)
