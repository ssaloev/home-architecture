# -*- coding: utf-8 -*-
"""17.11.2026 (заказчик: «квадраты — тупо, сделай реалистично, чтобы рабочим было понятно»):
условные знаки мебели и сантехники ВИД СВЕРХУ, как в архитектурных альбомах — кровать с подушками и одеялом,
диван со спинкой и подлокотниками, ванна с чашей и сливом, унитаз, раковина со смесителем, плита с конфорками,
мойка, стиралка с барабаном, холодильник, шкаф с дверцами и штангой, стол со стульями, ТВ на тумбе.
Ориентация: «спина» предмета — к ближайшей стене его комнаты (кровать — изголовьем, диван — спинкой, унитаз — бачком)."""
import math

WHITE, TEXT, WOOD, DARK, STEEL, GLASS = "#FFFFFF", "#F2F0EC", "#E9DFCF", "#3A3833", "#D7D9DB", "#E3F0F6"


def _back(f, rooms_rects):
    x, z, w, d = f["x"], f["z"], f["w"], f["d"]
    cx, cz = x + w / 2, z + d / 2
    best = None
    for rects in rooms_rects:
        for (x0, x1, z0, z1) in rects:
            if x0 - 0.05 <= cx <= x1 + 0.05 and z0 - 0.05 <= cz <= z1 + 0.05:
                best = (x0, x1, z0, z1); break
        if best: break
    if not best: return "T" if w >= d else "L"
    x0, x1, z0, z1 = best
    gaps = {"T": z - z0, "B": z1 - (z + d), "L": x - x0, "R": x1 - (x + w)}
    m = min(gaps.values()); near = [k_ for k_, g in gaps.items() if g <= m + 0.05]
    if len(near) > 1:                                   # в углу: спиной к стене вдоль длинной стороны предмета
        par = [k_ for k_ in near if (k_ in "TB") == (w >= d)]
        if par: return par[0]
    return min(gaps, key=gaps.get)


def draw(A, X, Y, S, f, rooms_rects, fill="#F3EFE7", col="#6B665C", sw=2.5, back=None, tables=()):
    x, z, w, d = f["x"], f["z"], f["w"], f["d"]
    k, nm = f.get("kind", ""), (f.get("name") or "").lower()
    b = back or f.get("back") or _back(f, rooms_rects)
    if f.get("kind") == "chair" and min(w, d) < 0.6 and tables:      # стул: спинкой ОТ стола
        tx, tz = min(((t["x"] + t["w"] / 2, t["z"] + t["d"] / 2) for t in tables), key=lambda p: (p[0] - x - w / 2) ** 2 + (p[1] - z - d / 2) ** 2)
        dx, dz = (x + w / 2) - tx, (z + d / 2) - tz
        b = ("R" if dx > 0 else "L") if abs(dx) > abs(dz) else ("B" if dz > 0 else "T")
    Lu, Lv = (w, d) if b in "TB" else (d, w)

    def P(u, v):
        if b == "T": return x + u, z + v
        if b == "B": return x + Lu - u, z + d - v
        if b == "L": return x + v, z + Lu - u
        return x + w - v, z + u                       # R

    def R(u0, v0, u1, v1, fc=fill, st=col, s_=sw, r=0.0, dash=""):
        (ax, az), (bx, bz) = P(u0, v0), P(u1, v1)
        x0_, x1_, z0_, z1_ = min(ax, bx), max(ax, bx), min(az, bz), max(az, bz)
        A(f'<rect x="{X(x0_):.1f}" y="{Y(z0_):.1f}" width="{(x1_-x0_)*S:.1f}" height="{(z1_-z0_)*S:.1f}" rx="{r*S:.1f}" fill="{fc}" stroke="{st}" stroke-width="{s_}"'
          + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")

    def E(uc, vc, ru, rv, fc=WHITE, st=col, s_=sw):
        cx, cz = P(uc, vc); rx, rz = (ru, rv) if b in "TB" else (rv, ru)
        A(f'<ellipse cx="{X(cx):.1f}" cy="{Y(cz):.1f}" rx="{rx*S:.1f}" ry="{rz*S:.1f}" fill="{fc}" stroke="{st}" stroke-width="{s_}"/>')

    def C(uc, vc, r, fc=WHITE, st=col, s_=sw):
        cx, cz = P(uc, vc); A(f'<circle cx="{X(cx):.1f}" cy="{Y(cz):.1f}" r="{r*S:.1f}" fill="{fc}" stroke="{st}" stroke-width="{s_}"/>')

    def Ln(pts, st=col, s_=sw, dash=""):
        q = " ".join(f"{X(P(u, v)[0]):.1f},{Y(P(u, v)[1]):.1f}" for u, v in pts)
        A(f'<polyline points="{q}" fill="none" stroke="{st}" stroke-width="{s_}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")

    def Pg(pts, fc, st=col, s_=sw):
        q = " ".join(f"{X(P(u, v)[0]):.1f},{Y(P(u, v)[1]):.1f}" for u, v in pts)
        A(f'<polygon points="{q}" fill="{fc}" stroke="{st}" stroke-width="{s_}"/>')

    thin = sw * 0.6
    if k == "bed":                                      # изголовье, 2 подушки, одеяло с отвёрнутым краем
        R(0, 0, Lu, Lv, fill, r=0.03)
        R(0, 0, Lu, 0.08, WOOD, r=0.02)
        n = 2 if Lu > 1.1 else 1; pw = (Lu - 0.12 - 0.06 * (n - 1)) / n
        for i in range(n): R(0.06 + i * (pw + 0.06), 0.13, 0.06 + i * (pw + 0.06) + pw, 0.50, WHITE, r=0.07)
        R(0.02, 0.62, Lu - 0.02, Lv - 0.02, TEXT, r=0.04)
        Ln([(0.02, 0.80), (Lu - 0.02, 0.80)], s_=thin)
        Pg([(Lu - 0.02, Lv - 0.45), (Lu - 0.02, Lv - 0.02), (Lu - 0.45, Lv - 0.02)], WHITE, s_=thin)
    elif k == "sofa":                                   # спинка, подлокотники, подушки сиденья
        R(0, 0, Lu, Lv, fill, r=0.06)
        R(0.02, 0.02, Lu - 0.02, 0.22, WOOD, r=0.05)
        R(0.02, 0.02, 0.17, Lv - 0.02, WOOD, r=0.05); R(Lu - 0.17, 0.02, Lu - 0.02, Lv - 0.02, WOOD, r=0.05)
        n = max(2, round((Lu - 0.34) / 0.65)); cw = (Lu - 0.34) / n
        for i in range(n): R(0.17 + i * cw + 0.01, 0.24, 0.17 + (i + 1) * cw - 0.01, Lv - 0.04, TEXT, r=0.05)
    elif k == "chair" and Lu >= 0.6:                    # кресло
        R(0, 0, Lu, Lv, fill, r=0.08)
        R(0.03, 0.03, Lu - 0.03, 0.20, WOOD, r=0.06)
        R(0.03, 0.03, 0.16, Lv - 0.04, WOOD, r=0.05); R(Lu - 0.16, 0.03, Lu - 0.03, Lv - 0.04, WOOD, r=0.05)
        R(0.18, 0.22, Lu - 0.18, Lv - 0.06, TEXT, r=0.06)
    elif k == "chair":                                  # стул: сиденье + спинка
        R(0.02, 0.06, Lu - 0.02, Lv - 0.01, fill, r=0.05)
        R(0.02, 0.0, Lu - 0.02, 0.06, DARK, r=0.02)
    elif k == "table":
        if "кругл" in nm:
            C(Lu / 2, Lv / 2, min(Lu, Lv) / 2 - 0.02, WOOD); C(Lu / 2, Lv / 2, min(Lu, Lv) / 2 - 0.09, WOOD, s_=thin)
        elif "туалетн" in nm:
            R(0, 0, Lu, Lv, WOOD, r=0.02); R(0.10, 0.0, Lu - 0.10, 0.03, GLASS); C(Lu / 2, Lv + 0.25, 0.18, TEXT)
        else:
            R(0, 0, Lu, Lv, WOOD, r=0.03); R(0.04, 0.04, Lu - 0.04, Lv - 0.04, "none", s_=thin)
    elif k == "wardrobe":                               # корпус, дверцы (ряд у фасада), штанга с плечиками
        R(0, 0, Lu, Lv, fill)
        R(0, Lv - 0.03, Lu, Lv, WHITE)
        n = max(1, round(Lu / 0.55))
        for i in range(1, n): Ln([(i * Lu / n, Lv - 0.03), (i * Lu / n, Lv)])
        Ln([(0.05, Lv * 0.45), (Lu - 0.05, Lv * 0.45)], s_=sw * 1.2)
        t = 0.12
        while t < Lu - 0.08:
            Ln([(t - 0.02, Lv * 0.45 - 0.17), (t + 0.02, Lv * 0.45 + 0.17)], s_=thin); t += 0.10
    elif k == "tv":                                     # тумба + телевизор
        R(0, 0, Lu, Lv, WOOD); n = max(2, round(Lu / 0.6))
        for i in range(1, n): Ln([(i * Lu / n, Lv - 0.02), (i * Lu / n, Lv)], s_=thin)
        tw = min(Lu - 0.1, 1.45)
        R(Lu / 2 - tw / 2, 0.04, Lu / 2 + tw / 2, 0.08, DARK, st=DARK)
    elif k == "shelf":
        R(0, 0, Lu, Lv, WOOD); [Ln([(0.03, v), (Lu - 0.03, v)], s_=thin) for v in (Lv * 0.33, Lv * 0.66)]
    elif k == "fridge":                                 # side-by-side: две двери, ручки
        R(0, 0, Lu, Lv, STEEL); Ln([(Lu / 2, 0.05), (Lu / 2, Lv)])
        for du in (-0.04, 0.04): Ln([(Lu / 2 + du, Lv - 0.01), (Lu / 2 + du, Lv + 0.03)], s_=sw * 1.5)
        R(0.06, Lv - 0.10, Lu - 0.06, Lv - 0.06, "none", s_=thin, dash="6 4")
    elif k == "tall":                                   # колонны: встроенная техника — тёмные стёкла
        R(0, 0, Lu, Lv, fill); n = max(1, round(Lu / 0.6))
        for i in range(1, n): Ln([(i * Lu / n, 0), (i * Lu / n, Lv)])
        R(0.05, Lv - 0.06, Lu / n - 0.05, Lv - 0.02, DARK, st=DARK)
    elif k == "low" and ("мойка" in nm or "плита" in nm):   # кухонный ряд: столешница, мойка, варочная панель
        R(0, 0, Lu, Lv, WOOD); Ln([(0, Lv - 0.04), (Lu, Lv - 0.04)], s_=thin)
        R(0.08, 0.10, 0.52, Lv - 0.10, WHITE, r=0.05); R(0.13, 0.15, 0.47, Lv - 0.15, STEEL, r=0.05, s_=thin)
        C(0.30, 0.06, 0.025, DARK); C(0.30, Lv / 2, 0.02, DARK, s_=thin)
        h0 = Lu - 0.64
        R(h0, 0.04, h0 + 0.58, Lv - 0.04, DARK, st=DARK, r=0.02)
        for (du, dv, rr) in ((0.15, 0.17, 0.09), (0.43, 0.17, 0.07), (0.15, Lv - 0.21, 0.07), (0.43, Lv - 0.21, 0.09)):
            C(h0 + du, dv, rr, "none", st="#9A9A9A", s_=thin)
        R(0.60, Lv - 0.06, 1.04, Lv - 0.03, "none", s_=thin, dash="5 4")
    elif k == "low":                                    # тумбочка / обувница: ящик + лампа
        R(0, 0, Lu, Lv, WOOD, r=0.02)
        if "тумбоч" in nm: C(Lu / 2, Lv / 2, min(Lu, Lv) * 0.25, WHITE, s_=thin)
    elif k == "bath":                                   # ванна: борт, чаша, слив, смеситель
        R(0, 0, Lu, Lv, WHITE, r=0.04)
        R(0.07, 0.07, Lu - 0.07, Lv - 0.07, "#F6FAFC", r=min(Lu, Lv) * 0.28)
        long_u = Lu >= Lv
        if long_u: C(Lu - 0.20, Lv / 2, 0.025, "none"); R(Lu - 0.06, Lv / 2 - 0.06, Lu, Lv / 2 + 0.06, DARK, st=DARK)
        else: C(Lu / 2, Lv - 0.20, 0.025, "none"); R(Lu / 2 - 0.06, Lv - 0.06, Lu / 2 + 0.06, Lv, DARK, st=DARK)
    elif k == "sink":                                   # раковина: столешница + овальная чаша + смеситель
        R(0, 0, Lu, Lv, WHITE if Lv < 0.3 else WOOD, r=0.03)
        E(Lu / 2, Lv * 0.55, min(Lu * 0.36, 0.22), min(Lv * 0.32, 0.16), WHITE)
        C(Lu / 2, 0.05, 0.022, DARK, st=DARK); C(Lu / 2, Lv * 0.55, 0.015, "none", s_=thin)
    elif k == "washer":                                 # стиралка: корпус, люк, барабан, панель
        R(0, 0, Lu, Lv, WHITE, r=0.03); R(0.03, 0.03, Lu - 0.03, 0.12, "#ECECEC", s_=thin)
        C(Lu / 2, Lv / 2 + 0.05, min(Lu, Lv) * 0.33, "#F5F7F8"); C(Lu / 2, Lv / 2 + 0.05, min(Lu, Lv) * 0.22, GLASS, s_=thin)
    elif k == "wc":                                     # подвесной унитаз: короб/клавиша, чаша, сиденье
        R(0, 0, Lu, 0.05, "#DDDDDD", s_=thin)
        E(Lu / 2, 0.05 + (Lv - 0.05) / 2, Lu / 2, (Lv - 0.05) / 2, WHITE)
        E(Lu / 2, 0.05 + (Lv - 0.05) * 0.56, Lu * 0.30, (Lv - 0.05) * 0.32, "#F6FAFC", s_=thin)
    elif k == "inst":                                   # инсталляция / короб — штриховка
        R(0, 0, Lu, Lv, "#EDEAE4", dash="8 5")
        Ln([(0, 0), (Lu, Lv)], s_=thin, dash="6 6"); Ln([(Lu, 0), (0, Lv)], s_=thin, dash="6 6")
    elif k == "shower":                                 # душ без поддона: плитка с уклоном, трап-лоток, лейка
        R(0, 0, Lu, Lv, GLASS)
        for (u_, v_) in ((0, Lv), (Lu, Lv)): Ln([(u_, v_), (Lu / 2, 0.08)], s_=thin, dash="8 6")
        R(0.06, 0.06, Lu - 0.06, 0.10, DARK, st=DARK)              # трап-лоток у дальней стены
        Ln([(0, Lv), (Lu, Lv)], st="#5C8AA8", s_=sw * 2.2)          # стекло со стороны комнаты
        C(0.12, Lv * 0.5, 0.035, WHITE)
    else:
        R(0, 0, Lu, Lv, fill)
