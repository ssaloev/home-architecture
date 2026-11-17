#!/bin/bash
# 17.11.2026: ЕДИНСТВЕННЫЙ вход для рендера альбома. Сначала шлагбаум проверки (pered_renderom.py) — при косяках рендер НЕ стартует.
cd "$(dirname "$0")"
PYTHONIOENCODING=utf-8 python pered_renderom.py || { echo "РЕНДЕР НЕ ЗАПУЩЕН: исправить по отчёту 06_albom/proverka_kvartiry.md"; exit 1; }
bash final_wet.sh
