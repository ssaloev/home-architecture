# -*- coding: utf-8 -*-
"""17.11.2026: ОБЩАЯ СХЕМА квартиры по обмеру (PR #1): стены/двери/окна/бетон из kvartira.json, размеры комнат,
замеры А–С (красным — где план ещё не совпадает с замером), мебель — текущая расстановка + новые схемы спальни/ванной/кухни.
План повёрнут на 90° — вертикально под телефон (окна гостиных справа)."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = os.path.join(os.path.dirname(HERE), "01_chertezhi", "shema_obshaya_obmer.png")
NL = chr(10)
ZM = 10.3                                            # поворот: u = ZM - z (вправо), v = x (вниз)
GR, WH = "#8C8B88", "#F4F4F2"

fig = plt.figure(figsize=(10.8, 17.5), dpi=130)
fig.text(0.03, 0.985, "ОБЩАЯ СХЕМА — квартира по обмеру 16–17.11", fontsize=18, fontweight="bold", va="top")
fig.text(0.03, 0.968, "Размеры в мм. 18.11: план = зафиксированный обмер из онлайн-редактора. Окна гостиных — справа.", fontsize=10.5, va="top")
ax = fig.add_axes([0.02, 0.11, 0.96, 0.85])


def RR(x0, z0, x1, z1, fc, t="", fs=7.5, col="#222", ec="#555", lw=1.0, ls="-", hatch=None, zo=1):
    u0, u1 = ZM - z1, ZM - z0
    ax.add_patch(Rectangle((u0, x0), u1 - u0, x1 - x0, fc=fc, ec=ec, lw=lw, ls=ls, hatch=hatch, zorder=zo))
    if t: ax.text((u0 + u1) / 2, (x0 + x1) / 2, t, ha="center", va="center", fontsize=fs, color=col)


def T(x, z, t, **k): ax.text(ZM - z, x, t, ha="center", va="center", **k)


def rect4(r): x, z, w, d = r; return x, z, x + w, z + d


for r in D["rooms"]:
    for (x0, x1, z0, z1) in r["rects"]: RR(x0, z0, x1, z1, "#FBFAF7", ec="none")
for w in D["walls"]: RR(*rect4(w), "#3A3632", ec="#3A3632")
for wn in D["windows"]: RR(*rect4(wn["rect"]), "#BFE0F2", ec="#2C6E91")
for dr in D["doors"]:
    x0, z0, x1, z1 = rect4(dr["rect"]); RR(x0, z0, x1, z1, "#F3D9A4", ec="#8A5A00")
    wmm = dr.get("real_mm") or round(max(dr["rect"][2], dr["rect"][3]) * 1000)
    if dr["type"] != "entry": T((x0 + x1) / 2, (z0 + z1) / 2, str(wmm), fontsize=6.5, color="#8A5A00", fontweight="bold")
for c in D["concrete"]:
    RR(*rect4(c["rect"]), "none", ec="#B03A2E", hatch="//", ls="--" if c["kind"] == "beam" else "-", zo=5)
for r in D["risers"]: ax.add_patch(Circle((ZM - r["z"], r["x"]), 0.06, fc="#B03A2E", zorder=6)); T(r["x"] + 0.15, r["z"], r["name"], fontsize=7, color="#B03A2E", zorder=6)

# ---- мебель: гостиная, коридор, прихожая, санузел — как в проекте; гостиная 2 — как в 3D после обмера; 3 комнаты — новые схемы
def room_of(x, z):
    for r in D["rooms"]:
        for q in r["rects"]:
            if q[0] <= x <= q[1] and q[2] <= z <= q[3]: return r["name"]
for f in D["furniture"]:
    if room_of(f["x"] + f["w"] / 2, f["z"] + f["d"] / 2) in ("Гостиная", "Коридор", "Прихожая"):
        if f["kind"] == "shower": f = dict(f, x=0.694 + 0.02, w=0.70)    # 17.11: шахта санузла по всей стене — душ от её грани
        RR(f["x"], f["z"], f["x"] + f["w"], f["z"] + f["d"], WH if f["kind"] == "wardrobe" else "#DCDBD8", ec="#666", lw=0.8)
# гостиная 2 (Комната): 5.786–9.386 × 0.309–6.545, дверь слева — шкаф справа от двери, ТВ у левой стены, диван у правой
RR(5.786, 1.75, 6.186, 4.85, GR, "ТВ 3100", 7, col="white"); RR(8.436, 2.17, 9.386, 4.43, "#DCDBD8", "диван 2260", 7)
RR(6.775, 5.945, 9.386, 6.545, WH, "шкаф 2611×600", 7, ec="#333")
for (a, b) in ((1.45, 2.4), (4.2, 5.15)): RR(7.4, a, 8.35, b, "#DCDBD8", "кресло", 6.5)
# спальня 2
RR(11.90, 4.836, 13.30, 6.936, WH, "кровать" + NL + "1400×2000", 7.5, ec="#333"); RR(10.232, 4.836, 10.832, 5.936, WH, "шкаф" + NL + "1100", 6.5, ec="#333")
RR(11.45, 4.836, 11.90, 5.236, GR); RR(13.30, 4.836, 13.75, 5.236, GR); RR(11.90, 7.216, 13.30, 7.516, GR, "ТВ", 6.5, col="white")
RR(13.75, 7.116, 14.55, 7.516, GR)
# ванная (Т2 внизу — унитаз у него, ванна вдоль левой стены)
RR(3.564, 8.154, 4.264, 9.854, "white", "ванна 1700", 7, ec="#333"); RR(5.434, 7.55, 5.914, 8.15, "#8E8E8E", "рак.", 6.5, col="white")
RR(5.294, 8.25, 5.894, 8.85, "white", "стир.", 6.5, ec="#333"); RR(5.164, 9.27, 5.714, 9.63, "white", "унит.", 6.5, ec="#333")
# санузел (утв. 17.11, вар. И): унитаз у Т1 в выемке, дверь напротив, душ в дальнем торце
RR(0.309, 7.07, 0.509, 7.57, "#BDBDBD"); RR(0.509, 7.14, 1.059, 7.50, "white", "унит.", 6.5, ec="#333")
RR(1.144, 6.8, 1.594, 7.0, "#8E8E8E", "рак.", 6, col="white"); RR(0.694, 7.8, 1.594, 8.62, "#CFE3EC", "душ", 7, ec="#2F7FA8")
# кухня
RR(12.286, 2.409, 12.886, 4.709, "#D9D8D4", "мойка · ПММ · плита", 6.5, ec="#333")
RR(9.586, 1.40, 10.286, 2.30, GR, "холод.", 6.5, col="white"); RR(9.586, 2.30, 10.236, 3.50, GR, "колонны", 6.5, col="white")
RR(10.85, 1.309, 12.05, 2.009, WH, "стол", 7, ec="#333")

# ---- названия и размеры комнат (по плану) + буквы замеров
for r in D["rooms"]:
    x0, x1, z0, z1 = max(r["rects"], key=lambda q: (q[1] - q[0]) * (q[3] - q[2]))
    big = (x1 - x0) * (z1 - z0) > 3 and r["name"] != "Коридор"
    T((x0 + x1) / 2 + (0.0 if big else 0.0), (z0 + z1) / 2, r["name"] + (NL + "%d×%d" % (round((z1 - z0) * 1000), round((x1 - x0) * 1000)) if big else ""),
      fontsize=10 if big else 7.5, fontweight="bold", color="#333", bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.3))
z_ok = {"А": 3300, "Б": 3400, "В": 4680, "Г": 2680, "Д": 1100, "Е": 900, "Ж": 1820, "З": 2350, "И": 2420, "К": 8160, "Л": 1600, "М": 2010, "Н": 3640, "П": 3600, "С": 1575}
lines = []
for z in D["zamer"]:
    L, real = z["L"], z.get("real_mm")
    if real is None: lines.append("%s %s — не замерено" % (L, z["room"] or "")); continue
    ok = abs(z_ok.get(L, real) - real) <= 30
    lines.append("%s  %-10s %5d %s" % (L, z["room"] or "проход", real, "" if ok else "  ← на плане %d, подогнать" % z_ok.get(L, 0)))
fig.text(0.03, 0.10, "ЗАМЕРЫ (мм):" + NL + NL.join(lines[:9]), fontsize=9.5, va="top", family="monospace")
fig.text(0.52, 0.10, NL + NL.join(lines[9:]) + NL + NL + "Мебель в спальне 2, ванной, кухне —" + NL + "новые схемы (на согласовании).", fontsize=9.5, va="top", family="monospace")
ax.set_xlim(-0.2, ZM + 0.25); ax.set_ylim(15.5, -0.2); ax.set_aspect("equal"); ax.axis("off")
fig.savefig(OUT, facecolor="white"); print(OUT)
