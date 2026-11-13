#!/bin/bash
# 14.11.2026: финальные рендеры для альбома (вариант 2: слоновая кость + орех ТВ, серый лён, пол дымчатый дуб везде, плитка грейж)
cd "$(dirname "$0")/.." ; B="D:/ProgramFiles/blender.exe"; S=02_skripty; R="real samples=500"
for n in 1 2 3 4 5 6 7 8 9; do "$B" -b --factory-startup -P $S/gostinaya_blender.py -- krem greywalls stroitel smceil floor=7E6A58-776350 plank=0.6x0.09 ceil=8 shots=$n tag=_sm 2>&1 | grep -i "Traceback\|Error:"; echo "gost $n $(date +%H:%M)"; done
"$B" -b --factory-startup -P $S/komnata_blender.py -- $R shots=1,2,3 tag= 2>&1 | grep -i "Traceback\|Error:"; echo "komnata $(date +%H:%M)"
"$B" -b --factory-startup -P $S/spalnya_blender.py -- $R shots=1,2,3,4 tag= 2>&1 | grep -i "Traceback\|Error:"; echo "spalnya $(date +%H:%M)"
"$B" -b --factory-startup -P $S/koridor_blender.py -- shots=1,2,3,4 2>&1 | grep -i "Traceback\|Error:"; echo "koridor $(date +%H:%M)"
for a in "1 0" "2 0" "3 0" "4 0" "6 0" "5 1"; do set -- $a; "$B" -b --factory-startup -P $S/sanuzel_blender.py -- $R shots=$1 open=$2 exp=1.0 tag= 2>&1 | grep -i "Traceback\|Error:"; done; echo "sanuzel $(date +%H:%M)"
for a in "1 0" "2 0" "3 0" "5 0" "2 1" "5 1"; do set -- $a; "$B" -b --factory-startup -P $S/vanna_blender.py -- $R shots=$1 open=$2 exp=1.0 tag= 2>&1 | grep -i "Traceback\|Error:"; done; echo "vanna $(date +%H:%M)"
for n in 1 2 3 4 5; do "$B" -b --factory-startup -P $S/kuhnya_blender.py -- $R shots=$n exp=1.1 tag= 2>&1 | grep -i "Traceback\|Error:"; done; echo "kuhnya $(date +%H:%M)"
echo ALL DONE
