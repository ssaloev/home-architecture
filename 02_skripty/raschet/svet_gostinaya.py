"""Светотехнический расчёт гостиной (приближённый): точечный метод для прямого света
трековых спотов + метод «интегрирующей сферы» для отражённого света и LED-карниза.
Комната берётся из data/kvartira.json. Запуск: python raschet/svet_gostinaya.py"""
import json, math, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "kvartira.json"), encoding="utf-8"))
r = next(x for x in D["rooms"] if x["name"] == "Гостиная")
x0, x1, z0, z1 = r["rects"][0]; A_ = x1 - x0; B_ = z1 - z0          # ширина 3,6 × длина 6,24
H = D["meta"]["ceiling_h"]; HW = 0.8; h = H - HW                     # рабочая плоскость 0,8 м
AREA = A_ * B_; PER = 2 * (A_ + B_)
RHO = 0.55                     # средний коэф. отражения: светлые стены/потолок, средний пол
S_ROOM = 2 * AREA + PER * H
NORM = 150                     # лк, жилая комната (СП 52.13330)

def spot_grid(lines, per_line, wall_off, end_off=0.6):
    xs = [x0 + wall_off + (A_ - 2 * wall_off) * k / (lines - 1) for k in range(lines)] if lines > 1 else [x0 + A_ / 2]
    zs = [z0 + end_off + (B_ - 2 * end_off) * (j + 0.5) / per_line for j in range(per_line)]
    return [(x, z) for x in xs for z in zs], xs

def frame_pts(off, step=0.1):
    """Световая рамка (линейный профиль заподлицо) в off м от стен -> цепочка точечных источников."""
    fx0, fx1, fz0, fz1 = x0 + off, x1 - off, z0 + off, z1 - off; pts = []
    nx = int((fx1 - fx0) / step); nz = int((fz1 - fz0) / step)
    for i in range(nx): t = fx0 + (i + .5) * (fx1 - fx0) / nx; pts += [(t, fz0), (t, fz1)]
    for j in range(nz): t = fz0 + (j + .5) * (fz1 - fz0) / nz; pts += [(fx0, t), (fx1, t)]
    return pts, 2 * ((fx1 - fx0) + (fz1 - fz0))

def calc(spots, lm, beam=60, led_lm=0.0, dim=1.0, extra_lm=0.0, n=60):
    half = math.radians(beam / 2); m = math.log(0.5) / math.log(math.cos(half))
    I0 = lm * dim * (m + 1) / (2 * math.pi)
    gx = np.linspace(x0 + 0.25, x1 - 0.25, n); gz = np.linspace(z0 + 0.25, z1 - 0.25, int(n * B_ / A_))
    X, Z = np.meshgrid(gx, gz); E = np.zeros_like(X)
    for (sx, sz) in spots:
        d2 = (X - sx) ** 2 + (Z - sz) ** 2 + h * h; c = h / np.sqrt(d2)
        E += I0 * c ** m * c / d2
    # LED-карниз светит в потолок (КПД ниши ~0,3), бра — частично (~0,4); всё это — равномерная добавка
    useful = lm * dim * len(spots) + led_lm * 0.3 + extra_lm * 0.4
    E_ind = useful * RHO / (S_ROOM * (1 - RHO))          # многократные отражения
    E_soft = (led_lm * 0.3 + extra_lm * 0.4) / AREA * 0.6  # первая «подсветка» с потолка/стен
    E = E + E_ind + E_soft
    return E, gx, gz

SCH = {
 "A": dict(name="2 линии, 0,9 от стен", lines=2, per=5, off=0.9, lm=550, w=7),
 "B": dict(name="3 линии, 0,6 от стен", lines=3, per=4, off=0.6, lm=450, w=6),
 "C": dict(name="1 линия по центру", lines=1, per=6, off=0.0, lm=900, w=10),
}
LED_LM = PER * 0.85 * 600     # LED в карнизе: ~600 лм/м (9,6 Вт/м), по периметру минус проёмы
BRA_LM = 0            # бра убраны (решение заказчика 11.2026)
res = {}
for k, s in SCH.items():
    spots, xs = spot_grid(s["lines"], s["per"], s["off"])
    E, gx, gz = calc(spots, s["lm"])
    res[k] = dict(s, spots=spots, xs=xs, E=E, gx=gx, gz=gz, avg=E.mean(), mn=E.min(), U=E.min() / E.mean(), n=len(spots), lm_tot=len(spots) * s["lm"], W_tot=len(spots) * s["w"])
# СОГЛАСОВАНО (11.2026): белая световая рамка в 0,6 м от стен, 500 лм/м, + скрытый LED по периметру + бра
FR_OFF, FR_LPM = 0.6, 500
fp, FR_LEN = frame_pts(FR_OFF); E, gx, gz = calc(fp, FR_LPM * FR_LEN / len(fp), beam=120)
res["R"] = dict(name=f"световая рамка {FR_OFF} от стен", spots=fp, xs=[], E=E, gx=gx, gz=gz, avg=E.mean(), mn=E.min(), U=E.min() / E.mean(),
                n=round(FR_LEN, 2), lm=FR_LPM, lm_tot=FR_LEN * FR_LPM, W_tot=round(FR_LEN * 5))
SC = []
for nm, dim, led, bra in (("Ночь / кино", 0.0, 0.3, 0.0), ("Вечер, уют", 0.2, 1.0, 0.0), ("Обычный", 0.6, 1.0, 0.0), ("Максимум (уборка, гости)", 1.0, 1.0, 0.0)):
    E, _, _ = calc(fp, FR_LPM * FR_LEN / len(fp), beam=120, led_lm=LED_LM * led, dim=dim, extra_lm=BRA_LM * bra)
    SC.append((nm, dim, led, bra, E.mean()))
if __name__ == "__main__":
    print(f"Комната {A_:.2f}×{B_:.2f} = {AREA:.1f} м², h={H}; норма {NORM} лк")
    for k, v in res.items():
        print(k, v["name"], f"спотов {v['n']}×{v['lm']} лм ({v['W_tot']} Вт): Eср={v['avg']:.0f} лк, Emin={v['mn']:.0f}, U={v['U']:.2f}")
    for s in SC: print("сцена", s[0], f"рамка {s[1]*100:.0f}% LED {s[2]*100:.0f}% бра {s[3]*100:.0f}% → ≈{s[4]:.0f} лк")
