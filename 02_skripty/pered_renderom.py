# -*- coding: utf-8 -*-
"""17.11.2026 (заказчик: «до рендера всё должно быть проверено, после рендера — никаких правок по расположению»).
ШЛАГБАУМ перед рендером: выгружает 3D всех комнат и проверяет пп. 1, 2, 4, 5 (план, точно по плану, расположение, палитра).
Если хоть одна комната ниже порога — рендер НЕ запускается (код выхода 1), печатается список косяков.
Использование: python pered_renderom.py && bash final_....sh"""
import subprocess, sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
PORog = {1: 100, 2: 75, 4: 95, 5: 90}     # 2: 75 — душ без поддона санузла не имеет «тела» на плане (известное исключение)
r = subprocess.run([sys.executable, os.path.join(HERE, "qa_check.py"), "--dump"], cwd=HERE, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
R = json.load(open(os.path.join(PROJ, "06_albom", "proverka_kvartiry.json"), encoding="utf-8"))
bad = []
for room in R:
    for k, p in PORog.items():
        sc = room["score"].get(str(k), room["score"].get(k, 0))
        if sc < p:
            bad.append(f"{room['room']}: п.{k} = {sc} < {p}")
            for t in room["issues"].get(str(k), room["issues"].get(k, []))[:6]: bad.append("    - " + t)
if bad:
    print("РЕНДЕР ОСТАНОВЛЕН — сначала исправить:"); print("\n".join(bad)); sys.exit(1)
print("ПРОВЕРКА ПРОЙДЕНА — можно рендерить")
