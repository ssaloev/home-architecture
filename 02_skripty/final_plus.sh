#!/bin/bash
# 14.11.2026: финал альбома в «супер-реализме» (real + real_plus.py: IES, порталы окон, шторы, потёртости). Кадры *_plus.jpg (гостиная 1 — _smA_*).
cd "$(dirname "$0")/.." ; B="D:/ProgramFiles/blender.exe"; S=02_skripty; R="real samples=500 tag=_plus"; T="timeout 2400"
run() { $T "$B" -b --factory-startup -P "$@" 2>&1 | grep -i "Traceback\|Error:"; }
for n in 1 2 3 4 5 6 7 8 9; do $T "$B" -b --factory-startup -P $S/gostinaya_blender.py -- krem greywalls stroitel smceil floor=5B5B59-555553 plank=0.6x0.09 ceil=8 shots=$n tag=_sm real samples=500 dexp=-0.4 2>&1 | grep -i "Traceback\|Error:"; echo "gost $n $(date +%H:%M)"; done
run $S/komnata_blender.py -- $R shots=3; echo "komnata $(date +%H:%M)"
for n in 1 2 3 4; do run $S/spalnya_blender.py -- $R shots=$n; done; echo "spalnya $(date +%H:%M)"
for n in 1 2 3 4; do run $S/koridor_blender.py -- $R shots=$n; done; echo "koridor $(date +%H:%M)"
for a in "1 0" "2 0" "3 0" "1 1"; do set -- $a; run $S/sanuzel_blender.py -- $R iesk=0.03 shots=$1 open=$2 exp=1.0; done; echo "sanuzel $(date +%H:%M)"
for a in "1 0" "2 0" "3 0" "5 0" "2 1" "5 1"; do set -- $a; run $S/vanna_blender.py -- $R iesk=0.03 shots=$1 open=$2 exp=1.0; done; echo "vanna $(date +%H:%M)"
for n in 1 2 3 4 5; do run $S/kuhnya_blender.py -- $R iesk=0.03 shots=$n exp=1.1; done; echo "kuhnya $(date +%H:%M)"
echo ALL DONE
