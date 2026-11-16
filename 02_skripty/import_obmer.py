"""Перенос обмерного плана из онлайн-редактора в kvartira.json.

Редактор: https://claude.ai/artifact/EgvxEz6DFfjMhEu2cAvwct (исходник страницы — obmer/plan_editor.html).
Снимок его данных лежит в data/obmer_plan.json (координаты в метрах, как в kvartira.json).

    python import_obmer.py            # data/obmer_plan.json -> data/kvartira.json
    python import_obmer.py снимок.json

Переносится геометрия: стены, окна, двери, полы помещений (rects/label/status), бетон
(балки, вентшахты, трубы — ключ "concrete"), замеры А–П ("zamer"), стояки, высота потолка.
Мебель, розетки, свет и стиль помещений остаются как были.
"""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data", "obmer_plan.json")
dst = os.path.join(HERE, "data", "kvartira.json")
P = json.load(open(src, encoding="utf-8"))
K = json.load(open(dst, encoding="utf-8"))
r4 = lambda v: round(v, 4)

K["walls"] = [[r4(w["x"]), r4(w["z"]), r4(w["w"]), r4(w["h"])] for w in P["walls"] if w["w"] > 0 and w["h"] > 0]
K["wall_materials"] = {f'{r4(w["x"])},{r4(w["z"])}': w["mat"] for w in P["walls"] if w.get("mat")}
K["windows"] = [{"rect": [r4(o["x"]), r4(o["z"]), r4(o["w"]), r4(o["h"])], "sill": o.get("sill", 0.8), "top": o.get("top", 2.4)}
                | ({"real_mm": o["real"]} if o.get("real") else {}) for o in P["windows"]]
K["doors"] = [{"rect": [r4(o["x"]), r4(o["z"]), r4(o["w"]), r4(o["h"])], "type": o.get("type", "std"), "h": o.get("hh", 2.1), "name": o.get("name", "")}
              | ({"real_mm": o["real"]} if o.get("real") else {}) for o in P["doors"]]

old = {r["name"]: r for r in K["rooms"]}
default = {"style": "modern", "floor": "parquet", "lights": {"main": "spots", "spots": 1, "led": None}}
rooms = []
for r in sorted(P["rooms"], key=lambda r: r["num"]):
    base = dict(old.get(r["name"], {**default, "name": r["name"]}))
    base.update(name=r["name"], num=r["num"], rects=[[r4(v) for v in q] for q in r["rects"]],
                label=r.get("label") or base.get("label"), status=r.get("status", "check"))
    if r.get("note"): base["note"] = r["note"]
    rooms.append(base)
K["rooms"] = rooms

K["concrete"] = [{"kind": b["kind"], "rect": [r4(b["x"]), r4(b["z"]), r4(b["w"]), r4(b["h"])],
                  **({"drop_mm": b["drop"]} if b.get("drop") else {}), **({"note": b["note"]} if b.get("note") else {})}
                 for b in P.get("beams", [])]
K["zamer"] = [{"L": m["L"], "room": m.get("room", ""), "note": m.get("note", ""),
               "plan_line": {"o": m["o"], "c": m["c"], "m": m["m"], "a0": m.get("a0"), "a1": m.get("a1"), "auto": m.get("auto", True)},
               "real_mm": m.get("real"), **({"comment": m["comment"]} if m.get("comment") else {})} for m in P["meas"]]
if P.get("risers"):
    BB = {b["id"]: b for b in P.get("beams", [])}
    K["risers"] = [{"name": rs["name"], "room": rs.get("room", ""),
                    "x": r4(BB[rs["in"]]["x"] + BB[rs["in"]]["w"] / 2), "z": r4(BB[rs["in"]]["z"] + 0.15)}
                   for rs in P["risers"] if rs.get("in") in BB]
if P.get("ceiling", {}).get("real"):
    K["meta"]["ceiling_h"] = P["ceiling"]["real"] / 1000; K["meta"]["ceiling_status"] = "ok"
if P.get("notes"): K["obmer_notes"] = P["notes"]
K["meta"]["status_note"] = "ЧЕРНОВИК — геометрия по обмеру (частично), спальня 2 ещё уточняется"

json.dump(K, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"kvartira.json: стен {len(K['walls'])}, окон {len(K['windows'])}, дверей {len(K['doors'])}, помещений {len(rooms)}, бетон {len(K['concrete'])}")
