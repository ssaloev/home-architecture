# -*- coding: utf-8 -*-
"""16.11.2026: схема для заказчика — вся мебель с номерами и реальными размерами (из data/kvartira.json),
предложение цвета (мебель серая, встроенное — белый корпус + серые полки, ручки чёрные) и пустая графа «ЕСТЬ?»
— заказчик отмечает, что уже есть (переиспользуем), и правит размеры. Вертикально под телефон."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_mebel_spisok.png")

def room_of(cx, cz):
    for r in D["rooms"]:
        for (x0, x1, z0, z1) in r["rects"]:
            if x0 - 0.05 <= cx <= x1 + 0.05 and z0 - 0.05 <= cz <= z1 + 0.05: return r["name"]
    return "—"
BUILT = {"wardrobe", "tall", "shelf", "low"}
TECH = {"washer", "bath", "shower", "fridge"}
def colour(f):
    k = f["kind"]
    if k in TECH: return "техника", "#BBBBBB"
    if k in BUILT: return "белая встроенная", "#F4F4F2"
    if k == "tv": return "серая? (сейчас орех)", "#9A9A9A"
    return "серая", "#9A9A9A"
names = {"chair": "Стул"}
items = []
for f in D["furniture"]:
    nm = f["name"] or names.get(f["kind"], f["kind"])
    cx, cz = f["x"] + f["w"] / 2, f["z"] + f["d"] / 2
    a, b = sorted((f["w"], f["d"]), reverse=True)
    items.append(dict(f, nm=nm, room=room_of(cx, cz), size=f"{int(round(a*1000))}×{int(round(b*1000))}×{int(round(f['h']*1000))}"))
order = [r["name"] for r in D["rooms"]]
items.sort(key=lambda i: (order.index(i["room"]) if i["room"] in order else 99, i["x"], i["z"]))

fig = plt.figure(figsize=(10.8, 20), dpi=150)
ax = fig.add_axes([0.03, 0.66, 0.94, 0.29])
for r in D["rooms"]:
    for (x0, x1, z0, z1) in r["rects"]:
        ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc="#FBFAF7", ec="#333", lw=1.6))
    x0, x1, z0, z1 = r["rects"][0]
    ax.text((x0 + x1) / 2, z0 + 0.18, r["name"], ha="center", va="top", fontsize=8, color="#666", style="italic")
for n, it in enumerate(items, 1):
    _, fc = colour(it)
    ax.add_patch(Rectangle((it["x"], it["z"]), it["w"], it["d"], fc=fc, ec="#111", lw=0.8, alpha=0.95))
    ax.text(it["x"] + it["w"] / 2, it["z"] + it["d"] / 2, str(n), ha="center", va="center", fontsize=8, fontweight="bold",
            color="white" if fc == "#9A9A9A" else "#B03A2E")
xs = [x for r in D["rooms"] for q in r["rects"] for x in q[:2]]; zs = [z for r in D["rooms"] for q in r["rects"] for z in q[2:]]
ax.set_xlim(min(xs) - 0.2, max(xs) + 0.2); ax.set_ylim(max(zs) + 0.2, min(zs) - 0.2); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.03, 0.982, "МЕБЕЛЬ — что есть, что новое (реальные размеры, мм)", fontsize=17, fontweight="bold")
fig.text(0.03, 0.968, "Отметьте в графе «ЕСТЬ?» то, что уже есть (переиспользуем), и исправьте размеры, если не так.", fontsize=11)
fig.text(0.03, 0.645, "Цвета:  ■ серая — отдельная мебель   □ белая — встроенная: корпус белый, полки серые, ручки чёрные",
         fontsize=10)

ta = fig.add_axes([0.03, 0.01, 0.94, 0.62]); ta.axis("off")
cols = ["№", "Помещение", "Предмет", "Ш×Г×В, мм", "Цвет (предложение)", "ЕСТЬ?"]
rows = [[str(n), it["room"], it["nm"][:52], it["size"], colour(it)[0], ""] for n, it in enumerate(items, 1)]
t = ta.table(cellText=rows, colLabels=cols, loc="upper center", cellLoc="left",
             colWidths=[0.05, 0.13, 0.44, 0.15, 0.15, 0.08])
t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 2.1)
for (r, c), cell in t.get_celld().items():
    if r == 0: cell.set_facecolor("#333"); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
    elif c == 5: cell.set_facecolor("#FFF6D5")
plt.savefig(OUT); print(OUT, len(items))
