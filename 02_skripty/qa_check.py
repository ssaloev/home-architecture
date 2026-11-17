# -*- coding: utf-8 -*-
"""17.11.2026 — ИНСТРУМЕНТ ПРОВЕРКИ КВАРТИРЫ (заказчик: «сделай инструмент проверки и по нему решаем, что делать»).
Четыре проверки по каждой комнате:
 1. ПЛАН ЕСТЬ        — комната есть в data/kvartira.json, у неё есть стены/контур и мебель с размерами.
 2. ТОЧНО ПО ПЛАНУ   — каждый предмет плана найден в 3D на своём месте (совпадение габарита сверху ≥ 50 %);
                       и наоборот — крупные предметы 3D, которых нет на плане.
 3. РЕАЛИСТИЧНОСТЬ   — сколько видимой мебели собрано из «коробок» (≤ 24 вершин, без фаски) против настоящих моделей.
 4. РАСПОЛОЖЕНИЕ     — предметы висят в воздухе, уходят в стену, пересекаются друг с другом.
Запуск:  python qa_check.py            — читает 08_vizualizacii/<комната>/qa_scene.json (сделать: blender ... -- qa shots=0)
         python qa_check.py --dump     — сначала выгрузить сцены всех комнат через Blender (≈1–2 мин)
Отчёт: 06_albom/proverka_kvartiry.md + .json (баллы 0–100 по каждой проверке)."""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
D = json.load(open(os.path.join(HERE, "data", "kvartira.json"), encoding="utf-8"))
ROOMS = {  # комната плана -> (скрипт, папка сцены)
    "Гостиная": ("gostinaya_blender.py", "gostinaya", ["krem", "greywalls", "stroitel", "smceil"]),
    "Комната": ("komnata_blender.py", "komnata", []),
    "Спальня 2": ("spalnya_blender.py", "spalnya2", []),
    "Кухня": ("kuhnya_blender.py", "kuhnya", []),
    "Ванная": ("vanna_blender.py", "vannaya", []),
    "Санузел": ("sanuzel_blender.py", "sanuzel", []),
    "Коридор": ("koridor_blender.py", "koridor", []),
}
STRUCT = ("стена", "пол", "потолок", "плинтус", "шов", "над двер", "над окн", "под окн", "простен", "откос", "рама", "стекло", "перекрыт",
          "небо", "короб", "выемка", "балка", "шахта", "вентшахта", "led", "подсвет", "трап", "порожек", "профиль", "карниз", "вырез",
          "фартук", "цоколь", "гола", "наличник", "полотно", "дверь", "ручк", "розетк", "spot", "спот", "lamp", "лента", "ниша", "тамбур", "лоджия",
          "кондиционер", "наружный", "рулон", "штора", "тюль", "держатель", "шнур", "импост", "подоконник")
FURN_NAMES = ("шкаф", "тумб", "кровать", "подиум", "матрас", "покрывало", "изголов", "диван", "кресл", "стол", "колонн", "холодил", "мойк",
              "столешн", "корпус", "ванна", "раковин", "унитаз", "стирал", "полка", "фасад", "антресол", "бойлер", "бак", "консоль", "скамья", "обувниц",
              "стеллаж", "пуф", "зеркало")


def dump_all():
    B = "D:/ProgramFiles/blender.exe"
    for room, (scr, d, extra) in ROOMS.items():
        cmd = [B, "-b", "--factory-startup", "-P", os.path.join(HERE, scr), "--", "qa", "shots=0"] + extra
        print("выгрузка", room, "...", flush=True)
        try: subprocess.run(cmd, cwd=PROJ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
        except Exception as e: print("  ошибка", e)


def rect_of(r): return r["rects"]


def in_room(x, z, rects, pad=0.02):
    return any(x0 - pad <= x <= x1 + pad and z0 - pad <= z <= z1 + pad for (x0, x1, z0, z1) in rects)


def overlap2(a, b):   # площадь пересечения прямоугольников (x0, x1, z0, z1)
    w = min(a[1], b[1]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[2], b[2])
    return max(0, w) * max(0, h)


def area(a): return max(1e-6, (a[1] - a[0]) * (a[3] - a[2]))


def touch(a, b, g=0.025):   # габариты касаются/перекрываются по всем трём осям (зазор ≤ g)
    return all(min(a[k1], b[k1]) - max(a[k0], b[k0]) > -g for (k0, k1) in (("x0", "x1"), ("z0", "z1"), ("h0", "h1")))


def check_room(room):
    scr, d, _ = ROOMS[room]
    R = next((r for r in D["rooms"] if r["name"] == room), None)
    res = dict(room=room, issues={1: [], 2: [], 3: [], 4: []}, score={})
    # ---------- 1. план есть
    if not R: res["issues"][1].append("комнаты нет в плане"); res["score"][1] = 0
    rects = rect_of(R) if R else []
    furn = [f for f in D["furniture"] if R and in_room(f["x"] + f["w"] / 2, f["z"] + f["d"] / 2, rects)]
    if R:
        if not furn: res["issues"][1].append("на плане нет мебели/сантехники для этой комнаты")
        noname = [f for f in furn if not f.get("name")]
        if noname: res["issues"][1].append(f"{len(noname)} предмет(ов) плана без названия")
        res["score"][1] = 100 if furn and not noname else (60 if furn else 30)
    f_scene = os.path.join(PROJ, "08_vizualizacii", d, "qa_scene.json")
    if not os.path.exists(f_scene):
        for k in (2, 3, 4): res["issues"][k].append("нет выгрузки 3D-сцены (запустить qa_check.py --dump)"); res["score"][k] = 0
        return res
    S = json.load(open(f_scene, encoding="utf-8")); objs = S["objects"]
    def is_struct(o): n = o["name"].lower(); return any(k in n for k in STRUCT)
    def fp(o): return (o["x0"], o["x1"], o["z0"], o["z1"])
    vis = [o for o in objs if not is_struct(o) and (o["x1"] - o["x0"]) < 6 and (o["z1"] - o["z0"]) < 6]
    # ---------- 2. точно по плану
    found = 0
    for f in furn:
        fr = (f["x"], f["x"] + f["w"], f["z"], f["z"] + f["d"])
        best = max((overlap2(fr, fp(o)) for o in vis), default=0)
        cov = sum(overlap2(fr, fp(o)) for o in vis if overlap2(fr, fp(o)) > 0.05 * area(fr))
        r_ = min(1.0, max(best, 0.6 * cov) / area(fr))
        if r_ >= 0.5: found += 1
        else: res["issues"][2].append(f"«{f['name'] or f['kind']}» ({round(f['w']*1000)}×{round(f['d']*1000)}) — в 3D на этом месте {'ничего нет' if r_ < 0.1 else f'совпадает только {round(r_*100)} %'}")
    big = [o for o in vis if area(fp(o)) > 0.25 and o["h1"] - o["h0"] > 0.3 and in_room((o["x0"] + o["x1"]) / 2, (o["z0"] + o["z1"]) / 2, rects)]
    for o in big:
        if not any(overlap2(fp(o), (f["x"], f["x"] + f["w"], f["z"], f["z"] + f["d"])) > 0.3 * area(fp(o)) for f in furn):
            if any(k in o["name"].lower() for k in FURN_NAMES):
                res["issues"][2].append(f"в 3D есть «{o['name']}» ({round((o['x1']-o['x0'])*1000)}×{round((o['z1']-o['z0'])*1000)}), а на плане его нет")
    res["score"][2] = round(100 * found / max(1, len(furn)))
    # ---------- 3. реалистичность: коробки против моделей
    furn_objs = [o for o in vis if any(k in o["name"].lower() for k in FURN_NAMES) or o["lib"]]
    boxes = [o for o in furn_objs if o["verts"] <= 24 and not o["lib"] and (o["h1"] - o["h0"]) > 0.05 and area(fp(o)) > 0.02]
    nobevel = [o for o in boxes if "BEVEL" not in o["mods"]]
    vol = lambda o: max(1e-6, area(fp(o)) * max(0.01, o["h1"] - o["h0"]))
    vb = sum(vol(o) for o in boxes); vt = sum(vol(o) for o in furn_objs) or 1
    res["score"][3] = round(100 * (1 - vb / vt) * (0.7 + 0.3 * (1 - len(nobevel) / max(1, len(boxes)))))
    names = {}
    for o in sorted(boxes, key=vol, reverse=True):
        k = o["name"].split(".")[0]; names[k] = names.get(k, 0) + 1
    for k, n in list(names.items())[:12]:
        res["issues"][3].append(f"«{k}» — коробка{' ×' + str(n) if n > 1 else ''}: заменить моделью или добавить детали (кромки, зазоры, фурнитура)")
    if nobevel: res["issues"][3].append(f"{len(nobevel)} коробок без фаски — острые «компьютерные» углы")
    # ---------- 4. расположение
    X0, X1, Z0, Z1 = (S["room"].get(k) for k in ("X0", "X1", "Z0", "Z1"))
    floaters, inwall, cross = [], [], []
    for o in furn_objs:
        if o["h0"] > 0.05:
            touch_wall = X0 is not None and (abs(o["x0"] - X0) < 0.05 or abs(o["x1"] - X1) < 0.05 or abs(o["z0"] - Z0) < 0.05 or abs(o["z1"] - Z1) < 0.05)
            under = any(p is not o and touch(o, p) and p["h0"] <= o["h0"] + 0.005 for p in objs) or o["h1"] >= (S["room"].get("H") or 2.65) - 0.08   # держится за соседний предмет / подвешен к потолку   # держится за соседний предмет (фасад на корпусе, деталь модели, предмет на столе)
            if not touch_wall and not under: floaters.append(o)
        if X0 is not None and (o["x0"] < X0 - 0.06 or o["x1"] > X1 + 0.06 or o["z0"] < Z0 - 0.06 or o["z1"] > Z1 + 0.06):
            if not in_room((o["x0"] + o["x1"]) / 2, (o["z0"] + o["z1"]) / 2, rects, 0.0) or area(fp(o)) > 0.05:
                inwall.append(o)
    big_f = [o for o in furn_objs if vol(o) > 0.02]
    for i, a in enumerate(big_f):
        for b in big_f[i + 1:]:
            ov = overlap2(fp(a), fp(b)); hz = min(a["h1"], b["h1"]) - max(a["h0"], b["h0"])
            if a["lib"] and b["lib"]: continue          # детали одной готовой модели (простыня на матрасе, рама и картина) — это норма
            if ov > 0.25 * min(area(fp(a)), area(fp(b))) and hz > 0.10:
                an, bn = a["name"].split(".")[0], b["name"].split(".")[0]
                if an != bn and not (an.lower()[:5] == bn.lower()[:5]): cross.append((an, bn))
    for o in floaters[:8]: res["issues"][4].append(f"«{o['name'].split('.')[0]}» висит в воздухе (низ {round(o['h0']*1000)} мм, не у стены и не на опоре)")
    for o in inwall[:8]: res["issues"][4].append(f"«{o['name'].split('.')[0]}» выходит за стены комнаты")
    seen = set()
    for (a, b) in cross:
        if (a, b) in seen or len(seen) >= 8: continue
        seen.add((a, b)); res["issues"][4].append(f"«{a}» пересекается с «{b}»")
    res["score"][4] = max(0, 100 - 8 * (len(floaters) + len(inwall)) - 5 * len(seen))
    return res


def main():
    if "--dump" in sys.argv: dump_all()
    allr = [check_room(r) for r in ROOMS]
    T = {1: "1. План есть", 2: "2. Точно по плану", 3: "3. Реалистичность (не коробки)", 4: "4. Расположение"}
    L = ["# Проверка квартиры", "", "| Комната | " + " | ".join(T[k] for k in T) + " |", "|---|" + "---|" * 4]
    for r in allr: L.append(f"| {r['room']} | " + " | ".join(f"{r['score'].get(k, 0)}" for k in T) + " |")
    for r in allr:
        L += ["", f"## {r['room']}"]
        for k in T:
            if r["issues"][k]: L += [f"**{T[k]}** — {r['score'].get(k, 0)}/100"] + [f"- {t}" for t in r["issues"][k]]
    out = os.path.join(PROJ, "06_albom", "proverka_kvartiry.md")
    open(out, "w", encoding="utf-8").write("\n".join(L))
    json.dump(allr, open(out.replace(".md", ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("\n".join(L[:12])); print("Отчёт:", out)


if __name__ == "__main__":
    main()
