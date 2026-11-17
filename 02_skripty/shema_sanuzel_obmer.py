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


# ======================= В (17.11, заказчик: «душевую в 1 м»): туалет + душ 1000 БЕЗ поддона — мокрая зона перед унитазом
fig = plt.figure(figsize=(10.8, 12), dpi=130)
fig.text(0.03, 0.985, "САНУЗЕЛ 900 × 1820 — вариант В: унитаз + душ 1000", fontsize=17, fontweight="bold", va="top")
fig.text(0.03, 0.962, "Душ без поддона: пол в плитке с уклоном к трапу, шторка. Зона душа = место для ног у унитаза.", fontsize=10.5, va="top")
c = fig.add_axes([0.10, 0.36, 0.80, 0.58]); room(c, "")
box(c, 0, 0, W, 0.20, "#BDBDBD", "инсталляция 200", 8, ls="--")
box(c, 0.27, 0.20, 0.63, 0.75, "white", "унитаз" + NL + "+ гиг. душ", 9)
c.add_patch(Rectangle((0.02, 0.0), W - 0.04, 0.32, fc="none", ec="#B03A2E", ls=":", lw=1.6))
c.text(W / 2, -0.12, "над унитазом: шкаф 320 — бак 200 л + бойлер Б2", ha="center", fontsize=8, color="#B03A2E")
c.add_patch(Rectangle((0, 0.78), W, 1.0, fc="#CFE3EC", ec="#2F7FA8", lw=1.4))
c.text(W / 2, 1.18, "душ 900×1000" + NL + "без поддона" + NL + "(он же — место для ног)", ha="center", va="center", fontsize=9.5, color="#1F4E79")
c.plot([0.06, 0.84], [1.62, 1.62], color="#2F7FA8", lw=3); c.text(W / 2, 1.70, "трап-лоток 700", ha="center", fontsize=8, color="#1F4E79")
c.plot([0.02, W - 0.02], [0.78, 0.78], color="#555", lw=2.2, ls=(0, (4, 2))); c.text(W - 0.03, 0.73, "шторка", ha="right", fontsize=8, color="#555")
c.add_patch(Circle((0.10, 1.05), 0.05, fc="#333")); c.text(0.18, 1.05, "лейка", fontsize=8, va="center")
fig.text(0.03, 0.335, NL.join([
    "• Всё помещается: унитаз у стояка Т1 (750) + душ 1000 → 1750 из 1820.",
    "• Душ без поддона: пол поднимаем ~60–80 мм, гидроизоляция, уклон к трапу-лотку у дальней стены.",
    "• Шторка на потолочном карнизе отделяет душ от унитаза; когда не моетесь — это место для ног.",
    "• Бак 200 л + бойлер Б2 — в шкафу над унитазом, как согласовано 13.11.",
    "• Раковины здесь нет (руки — в ванной рядом). Можно мини-раковину 350×200 на стену у двери над трапом.",
    "• Дверь 800 — наружу, с порогом 20 мм (вода не выйдет)."]), fontsize=10.5, va="top", linespacing=1.6)
OUT_V = OUT.replace(".png", "_v.png"); fig.savefig(OUT_V, facecolor="white"); print(OUT_V)


# ======================= Г (17.11, заказчик): с порога — в дальнем правом углу у Т1 унитаз (в небольшой выемке у стояка),
#                         справа рядом с ним (та же торцевая стена) — раковина для рук; ближний левый угол — душ без поддона
fig = plt.figure(figsize=(10.8, 12), dpi=130)
fig.text(0.03, 0.985, "САНУЗЕЛ 900 × 1820 — вариант Г (как вы описали)", fontsize=17, fontweight="bold", va="top")
fig.text(0.03, 0.962, "Вид от двери: дальний правый угол у Т1 — унитаз, рядом справа — раковина, угол слева — душ.", fontsize=10.5, va="top")
g = fig.add_axes([0.10, 0.36, 0.80, 0.58]); room(g, "")
UX = 0.33                                                   # ось унитаза от грани шахты (+ выемка у стояка — уточнить)
box(g, 0.0, 0.0, 0.52, 0.20, "#BDBDBD", "инстал.", 7.5, ls="--")
box(g, UX - 0.18, 0.20, UX + 0.18, 0.75, "white", "унитаз" + NL + "+ гиг." + NL + "душ", 8.5)
g.add_patch(Rectangle((-0.10, 0.0), 0.10, 0.45, fc="#F7E6C4", ec="#B07A1E", ls="--", lw=1.4))
g.annotate("выемка у стояка —" + NL + "размер уточнить", (-0.05, 0.22), (-0.95, 0.55), fontsize=8.5, color="#B07A1E",
           arrowprops=dict(arrowstyle="->", color="#B07A1E"))
box(g, 0.55, 0.0, W, 0.28, TILE, "раков." + NL + "350×280", 7.5, col="white")
g.add_patch(Rectangle((0.02, 0.0), 0.50, 0.32, fc="none", ec="#B03A2E", ls=":", lw=1.6))
g.text(W / 2, -0.12, "над унитазом: шкаф — бак 200 л + бойлер Б2", ha="center", fontsize=8, color="#B03A2E")
legs(g, 0.0, 0.76, W, 0.98, "ноги")
g.add_patch(Rectangle((0, 0.98), W, 0.84, fc="#CFE3EC", ec="#2F7FA8", lw=1.4))
g.text(W / 2, 1.33, "душ 900×840" + NL + "без поддона", ha="center", va="center", fontsize=9.5, color="#1F4E79")
g.plot([0.06, 0.84], [1.72, 1.72], color="#2F7FA8", lw=3); g.text(W / 2, 1.79, "трап-лоток", ha="center", fontsize=8, color="#1F4E79")
g.plot([0.02, W - 0.02], [0.98, 0.98], color="#555", lw=2.2, ls=(0, (4, 2))); g.text(W - 0.03, 0.94, "шторка", ha="right", fontsize=8, color="#555")
g.add_patch(Circle((0.10, 1.25), 0.05, fc="#333")); g.text(0.18, 1.25, "лейка", fontsize=8, va="center")
g.annotate("", (0, 0.88), (0.76 - 0.76, 0.88), arrowprops=dict(arrowstyle="-"))
g.annotate("", (W + 0.2, 0.0), (W + 0.2, 0.98), arrowprops=dict(arrowstyle="<->", color="#B03A2E"))
g.text(W + 0.24, 0.49, "980", fontsize=9, color="#B03A2E", fontweight="bold", va="center")
g.annotate("", (W + 0.2, 0.98), (W + 0.2, L), arrowprops=dict(arrowstyle="<->", color="#2F7FA8"))
g.text(W + 0.24, 1.40, "840", fontsize=9, color="#2F7FA8", fontweight="bold", va="center")
g.text(UX, 0.84, "ось %d" % round(UX * 1000), ha="center", fontsize=8, color="#555")
fig.text(0.03, 0.335, NL.join([
    "• Унитаз — в дальнем углу у стояка Т1, вплотную к шахте; выемку у стояка используем под инсталляцию/унитаз",
    "  (пришлите её ширину и глубину — сдвину унитаз в неё и раковину сделаю шире).",
    "• Раковина 350×280 — на той же стене справа от унитаза, руки мыть сразу у унитаза.",
    "• Душ — в ближнем углу у двери, 900×840, без поддона: уклон к трапу, шторка. Шторка открыта — это место для ног.",
    "• Перед унитазом сухо 230 мм + зона душа — вместе ~1070 для ног (норма 600).",
    "• Бак 200 л + бойлер Б2 — в шкафу над унитазом. Дверь 800 — наружу, порог 20 мм."]), fontsize=10.5, va="top", linespacing=1.6)
OUT_G = OUT.replace(".png", "_g.png"); fig.savefig(OUT_G, facecolor="white"); print(OUT_G)


# ======================= Д (17.11, эскиз заказчика): у торцевой стены в ряд — унитаз (у шахты) + раковина, в правом углу короб с трубой;
#                         дверь посередине длинной стены (наружу); душ внизу у шахты, не до стены с дверью
fig = plt.figure(figsize=(10.8, 12), dpi=130)
fig.text(0.03, 0.985, "САНУЗЕЛ 900 × 1820 — вариант Д: унитаз в выемке", fontsize=17, fontweight="bold", va="top")
fig.text(0.03, 0.962, "Унитаз в выемке шахты у Т1. Дверь — на своём месте. Раковина в углу. Душ у двери во всю ширину.", fontsize=10.5, va="top")
DZ0, DZ1 = L - 0.85, L - 0.05                          # дверь НЕ переносим (заказчик 17.11) — как по плану                                       # дверь — посередине длинной стены (по эскизу)
d = fig.add_axes([0.10, 0.36, 0.80, 0.58]); room(d, "")
for p in list(d.patches):                                   # убрать дверь/дугу из room() — у этого варианта дверь в другом месте
    if isinstance(p, Arc) or (isinstance(p, Rectangle) and p.get_x() == W and abs(p.get_width() - T) < 1e-6): p.remove()
for t in list(d.texts):
    if t.get_text().startswith("дверь"): t.remove()
d.add_patch(Rectangle((W, DZ0), T, DZ1 - DZ0, fc="#F3D9A4", ec="#8A5A00"))
d.add_patch(Arc((W + T, DZ1), 1.6, 1.6, theta1=270, theta2=360, color="#B03A2E", lw=1, ls="--"))
d.text(W + T + 0.45, DZ1 - 0.25, "дверь 800" + NL + "наружу", fontsize=8.5, color="#B03A2E")
d.plot([-SH, 0], [0.38, 0.38], color="#B03A2E", lw=1.5)                              # линия на шахте — как на эскизе
RC = SH                                                   # выемка в шахте у Т1 (глубина — уточнить), в ней инсталляция
d.add_patch(Rectangle((-RC, 0.20), RC, 0.64, fc="#F7E6C4", ec="#B07A1E", ls="--", lw=1.4, zorder=3))
d.text(-RC / 2, 0.92, "выемка 640", ha="center", fontsize=7.5, color="#B07A1E")
box(d, -RC, 0.27, -RC + 0.20, 0.77, "#BDBDBD", "", ls="--"); d.patches[-1].set_zorder(4)
box(d, -RC + 0.20, 0.34, -RC + 0.75, 0.70, "white", "", 8.5); d.patches[-1].set_zorder(4); d.text(-RC + 0.47, 0.52, "унитаз" + NL + "+ гиг. душ", ha="center", va="center", fontsize=8.5, zorder=6)
d.annotate("", (-RC + 0.75, 0.52), (0.80, 0.52), arrowprops=dict(arrowstyle="<-", color="#2E7D4F", lw=1.5))
legs(d, -RC + 0.76, 0.34, W, 0.70, "ноги" + NL + NL + "%d" % round((W + RC - 0.76) * 1000))
box(d, 0.50, 0.0, W, 0.22, TILE, "раковина 400×220", 7.5, col="white")
d.text(0.1, -0.12, "над унитазом: шкаф — бак 200 л + бойлер Б2", ha="center", fontsize=8, color="#B03A2E")
d.add_patch(Rectangle((0, 1.0), W, L - 1.0, fc="#CFE3EC", ec="#2F7FA8", lw=1.4))
d.text(0.45, 1.35, "душ" + NL + "900×820", ha="center", va="center", fontsize=9.5, color="#1F4E79")
d.add_patch(Circle((0.45, 1.70), 0.04, fc="#2F7FA8")); d.text(0.45, 1.78, "трап", ha="center", fontsize=7.5, color="#1F4E79")
d.plot([0.0, W], [1.0, 1.0], color="#555", lw=2, ls=(0, (4, 2)))
fig.text(0.03, 0.335, NL.join([
    "• Выемка 640 — вдоль стены, глубиной в шахту (до 385), за стены не выходит. Инсталляция и часть унитаза — в ней.",
    "• Унитаз смотрит на стену напротив; для ног %d (норма 600 — чуть меньше, но удобно, т.к. дальше свободно)." % round((W + RC - 0.76) * 1000),
    "• Дверь — где есть сейчас, не переносим. Открывается наружу.",
    "• Раковина 400×220 для рук — в углу у унитаза. Душ 900×820 у двери, без поддона, трап, шторка.",
    "• Глубину выемки нарисовал на всю шахту (385). Если мельче — ноги уменьшатся на столько же.",
    "• Бак 200 л + бойлер Б2 — в шкафу над унитазом."]), fontsize=10.5, va="top", linespacing=1.6)
OUT_D = OUT.replace(".png", "_d.png"); fig.savefig(OUT_D, facecolor="white"); print(OUT_D)
