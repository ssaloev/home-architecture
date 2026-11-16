# -*- coding: utf-8 -*-
"""16.11.2026: страница «Обмер квартиры» (Artifact, db): заказчик вписывает размеры на объекте с телефона,
значения сохраняются в базе артефакта — Claude читает их и правит чертежи. План — из data/kvartira.json."""
import os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "obmer.html")
S = 60
xs = [q[i] for r in D["rooms"] for q in r["rects"] for i in (0, 1)]; zs = [q[i] for r in D["rooms"] for q in r["rects"] for i in (2, 3)]
X0, Z0 = min(xs) - 0.25, min(zs) - 0.25; VW, VH = (max(xs) - X0 + 0.25) * S, (max(zs) - Z0 + 0.35) * S
p = lambda v, o: round((v - o) * S, 1)
svg = [f'<svg viewBox="0 0 {VW:.0f} {VH:.0f}" role="img" aria-label="План квартиры с номерами комнат, дверей и окон">']
for r in D["rooms"]:
    for (x0, x1, z0, z1) in r["rects"]: svg.append(f'<rect class="rm" x="{p(x0,X0)}" y="{p(z0,Z0)}" width="{p(x1,x0)}" height="{p(z1,z0)}"/>')
for (x, z, w, d) in D["walls"]: svg.append(f'<rect class="wl" x="{p(x,X0)}" y="{p(z,Z0)}" width="{w*S:.1f}" height="{d*S:.1f}"/>')
def tag(cls, key, cx, cy):
    return f'<a href="#{key}" class="tg {cls}" data-k="{key}"><rect x="{cx-17}" y="{cy-11}" width="34" height="22" rx="5"/><text x="{cx}" y="{cy+5}">{key}</text></a>'
for k, wn in enumerate(D["windows"], 1):
    x, z, w, d = wn["rect"]; svg.append(f'<rect class="wn" x="{p(x,X0)}" y="{p(z,Z0)}" width="{w*S:.1f}" height="{d*S:.1f}"/>')
for k, dr in enumerate(D["doors"], 1):
    x, z, w, d = dr["rect"]; svg.append(f'<rect class="dr" x="{p(x,X0)}" y="{p(z,Z0)}" width="{w*S:.1f}" height="{d*S:.1f}"/>')
for k, r in enumerate(D["rooms"], 1):
    x0, x1, z0, z1 = max(r["rects"], key=lambda q: (q[1] - q[0]) * (q[3] - q[2]))
    cx, cy = p((x0 + x1) / 2, X0), p((z0 + z1) / 2, Z0)
    svg.append(f'<text class="rn" x="{cx}" y="{cy-18}">{r["name"]}</text>' + tag("t-p", f"П{k}", cx, cy + 4))
for k, wn in enumerate(D["windows"], 1):
    x, z, w, d = wn["rect"]; svg.append(tag("t-o", f"О{k}", p(x + w / 2, X0), p(z + d / 2, Z0)))
for k, dr in enumerate(D["doors"], 1):
    x, z, w, d = dr["rect"]; svg.append(tag("t-d", f"Д{k}", p(x + w / 2, X0), p(z + d / 2, Z0)))
svg.append("</svg>")
rooms = [r["name"] for r in D["rooms"]]
GROUPS = [
  {"id": "rooms", "title": "Комнаты", "hint": "Длина и ширина — по полу, от стены до стены. Высоту меряйте в середине комнаты.",
   "items": [{"k": f"П{k}", "name": r["name"]} for k, r in enumerate(D["rooms"], 1)],
   "fields": [["len", "Длина"], ["wid", "Ширина"], ["h", "Высота до потолка"]]},
  {"id": "doors", "title": "Двери и проёмы", "hint": "Проём в стене без коробки: ширина, высота от пола, толщина стены.",
   "items": [{"k": f"Д{k}", "name": d["name"]} for k, d in enumerate(D["doors"], 1)],
   "fields": [["w", "Ширина проёма"], ["h", "Высота проёма"], ["t", "Толщина стены"]]},
  {"id": "windows", "title": "Окна", "hint": "Ширина по проёму; высоты — от чистого пола.",
   "items": [{"k": f"О{k}", "name": next((r for r in rooms), "")} for k, _ in enumerate(D["windows"], 1)],
   "fields": [["w", "Ширина"], ["sill", "Подоконник от пола"], ["top", "Верх от пола"], ["depth", "Глубина откоса"]]},
  {"id": "risers", "title": "Стояки, трубы, щиты", "hint": "Вода, канализация, отопление, газ, электрощит. Расстояния — от двух ближайших стен до центра.",
   "items": [{"k": f"Т{k}", "name": ""} for k in range(1, 7)], "room": True, "what": "ХВС, ГВС, канализация, отопление, газ, щит…",
   "fields": [["x", "От стены 1"], ["y", "От стены 2"], ["d", "Диаметр / размер"]]},
  {"id": "ceiling", "title": "Потолок: вентиляция, трубы, балки", "hint": "Всё, что на потолке или ниже 2600: вытяжки, решётки, трубы, балки, короба.",
   "items": [{"k": f"{c}{k}", "name": n} for c, n, m in (("В", "вентканал / вытяжка", 6), ("ПТ", "труба на потолке", 4), ("Б", "балка / короб", 4)) for k in range(1, m + 1)],
   "room": True, "fields": [["x", "От стены 1"], ["y", "От стены 2"], ["size", "Размер Ш×Г или Ø"], ["low", "Низ от пола"]]},
]
for k, wn in enumerate(D["windows"], 1):     # окно → комната
    x, z, w, d = wn["rect"]; cx, cz = x + w / 2, z + d / 2
    best = min(D["rooms"], key=lambda r: min(abs(cx - (q[0] + q[1]) / 2) + abs(cz - (q[2] + q[3]) / 2) for q in r["rects"]))
    GROUPS[2]["items"][k - 1]["name"] = best["name"]
html = open(os.path.join(HERE, "obmer_template.html"), encoding="utf-8").read()
html = html.replace("/*SVG*/", "\n".join(svg)).replace("/*GROUPS*/", json.dumps(GROUPS, ensure_ascii=False)).replace("/*ROOMS*/", json.dumps(rooms, ensure_ascii=False))
open(OUT, "w", encoding="utf-8").write(html); print(OUT)
