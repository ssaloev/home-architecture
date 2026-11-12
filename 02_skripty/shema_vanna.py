# -*- coding: utf-8 -*-
"""Ванная + санузел + стиралка в шкафу коридора — вид сверху по РЕАЛЬНЫМ размерам (13.11.2026, на согласование).
Стиралка 10 кг 600×600×850; бойлер Ariston Lydos Eco 80 V ≈ Ø450×760 (только вертикально);
бак 200 л 580×580×1000 + насос; ванна 1700×700; душ 700×900; подвесные унитаз/биде 360×550 + инсталляция 200."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_vanna.png")
fig, ax = plt.subplots(figsize=(20, 9.5), dpi=130)
TILE, GR = "#8E8E8E", "#3A3A3D"
for r in D["rooms"]:
    if r["name"] in ("Ванная", "Санузел", "Коридор", "Прихожая"):
        for (x0, x1, z0, z1) in r["rects"]:
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=("#E4E4E4" if r["name"] in ("Ванная", "Санузел") else "#FAF9F6"), ec="none"))
for w in D["walls"]:
    ax.add_patch(Rectangle((w[0], w[1]), w[2], w[3], fc="#3A3632", ec="#3A3632"))
for d in D["doors"]:
    x, z, ww, dd = d["rect"]; ax.add_patch(Rectangle((x, z), ww, dd, fc="white", ec="#888", lw=0.8))
def R(x0, z0, x1, z1, fc, t="", fs=9, col="#222", ec="#555", ls="-", lw=1.3):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)
def dim(x0, z0, x1, z1, t, col="#B03A2E", fs=9):
    ax.annotate("", (x0, z0), (x1, z1), arrowprops=dict(arrowstyle="<->", color=col, lw=1.0))
    if t: ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, color=col, fontsize=fs, ha="center", va="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.25))
def legs(x0, z0, x1, z1, t):
    R(x0, z0, x1, z1, "#DFF0E6", "", ec="#2E7D4F", ls="--"); ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=8, color="#2E7D4F", fontweight="bold")
NL = chr(10)

# ======================= САНУЗЕЛ 1527×2218: душ, раковина, биде + унитаз, бойлер Б2
X0, X1, Z0, Z1 = 0.309, 1.836, 6.8, 9.018
R(X0, Z0, 1.018, 7.709, "#CFE3EC", NL.join(["душ", "700×900", "трап"]), 8.5, ec="#2F7FA8")
R(1.058, Z0, 1.558, Z0 + 0.42, TILE, NL.join(["раковина", "500×420"]), 8, col="white")
R(X0, Z1 - 0.20, X1, Z1, "#BDBDBD", "инсталляции 200", 7, ls="--")
R(0.53, Z1 - 0.75, 0.89, Z1 - 0.20, "white", NL.join(["биде", "360×550"]), 8)
R(1.25, Z1 - 0.75, 1.61, Z1 - 0.20, "white", NL.join(["унитаз", "360×550"]), 8)
R(X0, 7.74, X0 + 0.22, 8.26, "#3A3A3D", "", ec="#B03A2E", lw=2)
ax.text(X0 + 0.11, 8.00, NL.join(["бак", "200 л", "под", "заказ"]), ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")
ax.annotate(NL.join(["узкий бак под заказ 520×220×2000 (200 л)", "в графитовом пенале, насос сверху"]), (X0 + 0.05, 8.00), (-0.25, 9.55),
            fontsize=8, color="#B03A2E", arrowprops=dict(arrowstyle="->", color="#B03A2E"))
ax.add_patch(Circle((1.43, Z1 - 0.435), 0.225, fc="none", ec="#B03A2E", ls=":", lw=1.6))
ax.text(1.07, Z1 + 0.06, "Б2 Ø450 над унитазом, h 1700–2650", ha="center", fontsize=7.5, color="#B03A2E")
legs(0.53, 7.72, 0.89, Z1 - 0.76, NL.join(["ноги", "%d" % round((Z1 - 0.75 - 7.709) * 1000)]))
legs(1.25, 7.25, 1.61, Z1 - 0.76, NL.join(["ноги", "%d" % round((Z1 - 0.75 - 7.24) * 1000)]))
ax.add_patch(Arc((1.945, 7.0), 1.6, 1.6, theta1=0, theta2=90, color="#B03A2E", lw=1, ls="--")); ax.text(2.25, 7.45, NL.join(["дверь", "наружу"]), fontsize=8, color="#B03A2E")
ax.text(1.07, 6.60, "САНУЗЕЛ 1527×2218", ha="center", fontsize=12, fontweight="bold")
dim(X0, 9.30, X1, 9.30, "1527"); dim(0.10, Z0, 0.10, Z1, "2218")

# ======================= ВАННАЯ 2509×1491: ванна 1700, раковина с открытой полкой, унитаз + гиг. душ,
#                         тех. колонна в углу у ванны: бак 200 л + насос внизу, бойлер Б1 сверху
X0, X1, Z0, Z1 = 3.564, 6.073, 8.018, 9.509
BZ = Z1 - 0.70
BX0 = X1 - 1.30                                   # 13.11: ванна 1300×700 сдвинута к унитазу (по заказчику)
R(BX0, BZ, X1, Z1, "white", "ванна 1300×700", 11)
R(X0, 8.06, X0 + 0.48, 8.66, TILE, NL.join(["раковина", "600×480", "снизу —", "открытая", "полка"]), 7.5, col="white")
ax.text(X0 + 0.02, 8.04, "зеркало над раковиной", fontsize=7, color="#555")
R(X0 + 0.05, 8.86, X0 + 0.65, 9.46, "white", NL.join(["стиралка", "10 кг", "600×600"]), 8, ec="#333")
legs(X0 + 0.66, 8.86, BX0 - 0.01, 9.46, NL.join(["загрузка", "%d" % round((BX0 - X0 - 0.65) * 1000)]))
R(X1 - 0.20, 8.08, X1, BZ, "#BDBDBD", "", ls="--")
R(X1 - 0.75, 8.235, X1 - 0.20, 8.595, "white", NL.join(["унитаз", "+ гиг. душ"]), 8)
ax.add_patch(Circle((X1 - 0.28, 8.42), 0.225, fc="none", ec="#B03A2E", ls=":", lw=1.6))
ax.text(X1 - 0.05, 7.96, "бойлер Б1 Ø450 над унитазом, h 1700–2650", ha="right", fontsize=7.5, color="#B03A2E")
legs(X0 + 0.50, 8.235, X1 - 0.76, 8.595, "ноги %d" % round((X1 - 0.75 - (X0 + 0.48)) * 1000))
ax.add_patch(Arc((4.255, 7.98), 1.6, 1.6, theta1=0, theta2=90, color="#B03A2E", lw=1, ls="--"))
ax.text(4.20, 7.80, "ВАННАЯ 2509×1491", ha="center", fontsize=12, fontweight="bold")
dim(X0, 9.75, BX0, 9.75, "%d" % round((BX0 - X0) * 1000)); dim(BX0, 9.75, X1, 9.75, "1300")
dim(6.25, BZ, 6.25, Z1, "700")

# ======================= КОРИДОР: первая секция встроенного шкафа (у угла ванной) — стиральная машина за дверцами
ax.text(3.6, 10.15, NL.join(["Ванная: раковина с открытой полкой, слева от неё стиралка 10 кг, ванна 1300 к унитазу, бойлер Б1 над унитазом. Санузел: узкий бак 200 л под заказ в пенале сбоку от биде.",
        "Бойлеры Ariston Lydos Eco 80 V ≈ Ø450×760 (только вертикально) — в шкафах 550 над унитазами. Шкафы коридора — без изменений. Зелёным — место для ног (норма ≥ 600)."]),
        ha="center", fontsize=9.5)
ax.set_xlim(-0.4, 6.7); ax.set_ylim(10.35, 6.45); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Санузел и ванная — расстановка по реальным размерам (13.11.2026)", fontsize=14, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(OUT, facecolor="white"); print(OUT)
