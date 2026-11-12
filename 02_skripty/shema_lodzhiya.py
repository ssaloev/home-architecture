# -*- coding: utf-8 -*-
"""Схема лоджии с наружными блоками кондиционеров (вид сверху) — для согласования 12.11.2026."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_lodzhiya_kond.png")
fig, ax = plt.subplots(figsize=(15, 10), dpi=140)
WALL = "#3A3632"
for w in D["walls"]:
    x, z, ww, dd = w
    ax.add_patch(Rectangle((x, z), ww, dd, fc=WALL, ec=WALL))
for wn in D["windows"]:
    x, z, ww, dd = wn["rect"]
    ax.add_patch(Rectangle((x, z), ww, dd, fc="#DCEBF2", ec="#5B8FA8", lw=1.5))
def T(x, z, s, fs=11, **kw): ax.text(x, z, s, ha="center", va="center", fontsize=fs, **kw)
def dim(x0, z0, x1, z1, t, col="#B03A2E"):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.2))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=11, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.5))
# помещения
for (x0, z0, x1, z1, t) in ((1.946, 0.309, 5.545, 6.545, "ГОСТИНАЯ"), (5.745, 0.309, 8.945, 6.545, "ВТОРАЯ\nГОСТИНАЯ"), (9.145, 1.909, 13.0, 4.2, "КУХНЯ"),
                            (10.072, 4.327, 14.745, 7.491, "СПАЛЬНЯ 2"), (1.945, 6.672, 9.945, 7.909, "")):
    if t: T((x0 + x1) / 2, (z0 + z1) / 2 + 0.6, t, 13, fontweight="bold", color="#666")
for (x0, z0, w, d, t) in ((9.145, 0.309, 1.31, 1.509, "ЛОДЖИЯ А"), (13.745, 2.327, 1.0, 1.218, "ЛОДЖИЯ Б")):
    ax.add_patch(Rectangle((x0, z0), w, d, fc="#FFF4D6", ec="#C27A12", lw=2.5, zorder=0.5))
    T(x0 + w / 2, z0 + 0.18, t, 11, fontweight="bold", color="#8A5A0B")
ax.add_patch(Rectangle((13.745, 3.545), 1.0, 0.782, fc="#FFF9EA", ec="none", zorder=0.4)); T(14.25, 3.95, "тамбур\nиз спальни", 8.5, color="#8A5A0B")
# двери в ниши
ax.plot([9.045, 9.045], [0.545, 1.345], color="#2F7FA8", lw=6); T(8.45, 0.95, "стекл.\nдверь 800", 9, color="#2F7FA8")
ax.plot([13.89, 14.618], [3.59, 3.59], color="#2F7FA8", lw=6); T(14.25, 3.37, "стекл. дверь", 8.5, color="#2F7FA8")
# наружные блоки
def unit(x, z, w, d, t):
    ax.add_patch(Rectangle((x, z), w, d, fc="#FFFFFF", ec="#2E7D4F", lw=2.5, hatch="///")); T(x + w / 2, z + d / 2, t, 9, fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
unit(10.155, 0.55, 0.30, 0.80, "Н1\nН2")
unit(13.85, 2.75, 0.80, 0.30, "Н3 + Н4")
unit(13.85, 3.12, 0.80, 0.30, "Н4") if False else None
T(10.0, 1.62, "Н1, Н2 — кронштейны\nдруг над другом", 8.5, color="#2E7D4F")
T(14.25, 3.18, "Н3, Н4 — друг над другом", 8, color="#2E7D4F")
# внутренние блоки и трассы
for (x, z, w, d, t) in ((5.32, 0.45, 0.22, 0.8, "К1"), (5.75, 0.50, 0.22, 0.8, "К2"), (14.52, 4.60, 0.22, 0.8, "К3"), (9.15, 1.95, 0.8, 0.22, "К4")):
    ax.add_patch(Rectangle((x, z), w, d, fc="#DFF0E6", ec="#2E7D4F", lw=2)); T(x + w / 2 + (0 if w > d else 0.3), z + d / 2 + (0.3 if w > d else 0), t, 11, fontweight="bold", color="#2E7D4F")
def route(pts, col="#2E7D4F"):
    xs, zs = zip(*pts); ax.plot(xs, zs, color=col, lw=2.2, ls="--")
    ax.annotate("", pts[-1], pts[-2], arrowprops=dict(arrowstyle="->", color=col, lw=2))
route([(5.43, 0.55), (5.43, 0.40), (8.8, 0.40), (10.15, 0.70)])
route([(5.86, 0.62), (5.86, 0.47), (8.8, 0.47), (10.15, 1.05)])
route([(14.63, 4.60), (14.63, 3.30)])
route([(9.95, 2.17), (12.9, 2.17), (13.9, 2.9)])
T(11.4, 2.42, "трасса К4 под потолком кухни", 9, color="#2E7D4F")
T(7.2, 0.18, "трассы К1, К2 под потолком", 9, color="#2E7D4F")
dim(9.145, 2.0 - 0.15, 10.455, 2.0 - 0.15, "1310") if False else None
ax.set_xlim(1.4, 15.6); ax.set_ylim(9.0, -0.5); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Кондиционеры: 2 ниши для наружных блоков — вид сверху (на согласование)", fontsize=15, fontweight="bold", loc="left")
T(8.5, 8.75, "Лоджия А (из второй гостиной): Н1 — гостиная, Н2 — вторая гостиная.   Лоджия Б (из спальни 2): Н3 — спальня 2, Н4 — кухня.   Размеры — проверить на замере.", 10.5, color="#444")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
