# -*- coding: utf-8 -*-
"""17.11.2026: САНУЗЕЛ по обмеру — свободно 900 (Е) × 1820 (Ж) от грани шахты; шахта 385 заполнена по всей стене,
стояк Т1 в самом конце (угол у прихожей), дверь 800 наружу — в прихожую. 2 варианта на выбор, вертикально под телефон.
Местные координаты: x — поперёк (0 = грань шахты), z — вдоль (0 = торец со стояком)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_chertezhi", "shema_sanuzel_obmer.png")
NL = chr(10); W, L, SH, T = 0.90, 1.82, 0.385, 0.12
DZ0, DZ1 = L - 0.85, L - 0.05                               # дверь 800 на длинной стене, у дальнего конца
TILE = "#8E8E8E"


def room(ax, title):
    ax.add_patch(Rectangle((-SH - T, -T), SH + W + 2 * T, L + 2 * T, fc="#3A3632"))
    ax.add_patch(Rectangle((0, 0), W, L, fc="#E9E9E7"))
    ax.add_patch(Rectangle((-SH, -T), SH, L + T, fc="white", ec="#B03A2E", hatch="//"))
    ax.add_patch(Circle((-SH + 0.12, 0.10), 0.055, fc="#B03A2E")); ax.text(-SH + 0.12, 0.26, "Т1", ha="center", fontsize=9, color="#B03A2E", fontweight="bold")
    ax.text(-SH / 2, L / 2, "шахта 385" + NL + "(заполнена)", ha="center", va="center", fontsize=8, color="#B03A2E", rotation=90)
    ax.add_patch(Rectangle((W, DZ0), T, DZ1 - DZ0, fc="#F3D9A4", ec="#8A5A00"))
    ax.add_patch(Arc((W + T, DZ1), 1.6, 1.6, theta1=270, theta2=360, color="#B03A2E", lw=1, ls="--"))
    ax.text(W + T + 0.45, DZ1 - 0.25, "дверь 800" + NL + "наружу", fontsize=8.5, color="#B03A2E")
    ax.text(W + T + 0.1, 0.4, "прихожая", fontsize=9, color="#777", rotation=90, va="center")
    ax.annotate("", (0, L + 0.25), (W, L + 0.25), arrowprops=dict(arrowstyle="<->", color="#B03A2E"))
    ax.text(W / 2, L + 0.33, "900 (Е)", ha="center", fontsize=10, color="#B03A2E", fontweight="bold")
    ax.annotate("", (-SH - 0.25, 0), (-SH - 0.25, L), arrowprops=dict(arrowstyle="<->", color="#B03A2E"))
    ax.text(-SH - 0.33, L / 2, "1820 (Ж)", rotation=90, va="center", ha="center", fontsize=10, color="#B03A2E", fontweight="bold")
    ax.set_title(title, fontsize=12.5, fontweight="bold", loc="left")
    ax.set_xlim(-SH - 0.5, W + 1.05); ax.set_ylim(L + 0.45, -0.3); ax.set_aspect("equal"); ax.axis("off")


def box(ax, x0, z0, x1, z1, fc, t, fs=9, col="#222", ec="#444", ls="-"):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, ls=ls, lw=1.2))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=fs, color=col)


def legs(ax, x0, z0, x1, z1, t):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc="#DFF0E6", ec="#2E7D4F", ls="--"))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, t, ha="center", va="center", fontsize=8.5, color="#2E7D4F", fontweight="bold")


fig = plt.figure(figsize=(10.8, 11), dpi=130)
fig.text(0.03, 0.985, "САНУЗЕЛ по обмеру: 900 × 1820 — 2 варианта", fontsize=17, fontweight="bold", va="top")
fig.text(0.03, 0.967, "Шахта заполнена по всей стене, стояк Т1 в самом конце. Душ + биде + унитаз в ряд (как было) — НЕ влезают.", fontsize=10.5, va="top")

# ---- A: унитаз + гиг. душ у стояка, бак/бойлер над ним, мини-раковина; мыться — в ванной
a = fig.add_axes([0.02, 0.37, 0.47, 0.56]); room(a, "А — туалет (рекомендую)")
box(a, 0, 0, W, 0.20, "#BDBDBD", "инсталляция 200", 8, ls="--")
box(a, 0.27, 0.20, 0.63, 0.75, "white", "унитаз" + NL + "+ гиг." + NL + "душ", 9)
a.add_patch(Rectangle((0.02, 0.0), W - 0.04, 0.32, fc="none", ec="#B03A2E", ls=":", lw=1.6))
a.text(W / 2, -0.12, "над унитазом: шкаф 320 — бак 200 л + бойлер Б2", ha="center", fontsize=7.5, color="#B03A2E")
legs(a, 0.0, 0.76, W, 1.40, "ноги 650")
box(a, 0.0, 1.42, 0.30, 1.82, TILE, "мини-" + NL + "рак." + NL + "400×" + NL + "300", 7.5, col="white")
a.text(0.6, 1.62, "проход" + NL + "600", ha="center", fontsize=8.5, color="#2E7D4F", fontweight="bold")

# ---- Б: душ 900×900 + раковина; унитаз — только в ванной
b = fig.add_axes([0.51, 0.37, 0.47, 0.56]); room(b, "Б — душевая")
box(b, 0, 0, W, 0.90, "#CFE3EC", "душ" + NL + "900×900" + NL + "трап у стояка" + NL + "(шторка)", 9, ec="#2F7FA8")
box(b, 0.0, 1.0, 0.42, 1.55, TILE, "рак." + NL + "500×" + NL + "420", 8, col="white")
b.text(W / 2, -0.12, "бак 200 л и бойлер Б2 — в коридор/кладовку", ha="center", fontsize=7.5, color="#B03A2E")
legs(b, 0.43, 0.92, W, 1.80, "проход" + NL + "470")

fig.text(0.03, 0.34, NL.join([
    "А — туалет: унитаз с гигиеническим душем у стояка Т1 (короткая канализация), над ним шкаф 320:",
    "    бак 200 л + бойлер Б2 (как согласовано 13.11). Ноги 650 — норма. Мини-раковина 400×300 у двери.",
    "    Душа нет — мыться в ванной (там ванна 1700 со шторкой). Биде заменяет гигиенический душ.",
    "",
    "Б — душевая: душ 900×900 (трап у стояка) + раковина; унитаз — только в ванной.",
    "    Бак 200 л и бойлер Б2 сюда не встают — нужно искать место в коридоре или кладовке.",
    "",
    "В обоих вариантах дверь 800 открывается НАРУЖУ (в прихожую), иначе её некуда открыть.",
    "Размеры 900 и 1820 — свободное место от грани шахты. Если 900 мерили вместе с шахтой — скажите, пересчитаю."]),
    fontsize=10.5, va="top", linespacing=1.55)
fig.savefig(OUT, facecolor="white"); print(OUT)
