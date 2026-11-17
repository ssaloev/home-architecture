#!/bin/bash
# 17.11: перерендер мокрых зон с плиткой A (темнее) и исправленным декором — после основной очереди
cd "$(dirname "$0")/.." ; B="D:/ProgramFiles/blender.exe"; S=02_skripty; R="real samples=500 tag=_plus"
run() { timeout 2400 "$B" -b --factory-startup -P "$@" 2>&1 | grep -i "Traceback\|Error:" | grep -v HIP; }
for a in "1 0" "2 0" "3 0" "1 1"; do set -- $a; run $S/sanuzel_blender.py -- $R iesk=0.03 shots=$1 open=$2 exp=1.0; done; echo "sanuzel $(date +%H:%M)"
for a in "1 0" "2 0" "3 0" "5 0" "2 1" "5 1"; do set -- $a; run $S/vanna_blender.py -- $R iesk=0.03 shots=$1 open=$2 exp=1.0; done; echo "vanna $(date +%H:%M)"
for n in 1 2 3 4 5; do run $S/kuhnya_blender.py -- $R iesk=0.03 shots=$n exp=1.1; done; echo "kuhnya $(date +%H:%M)"
for n in 1 2 3; do run $S/komnata_blender.py -- $R shots=$n; done; echo "komnata $(date +%H:%M)"
for n in 1 2 3 4; do run $S/spalnya_blender.py -- $R shots=$n; done; echo "spalnya $(date +%H:%M)"
for n in 1 2 3 4; do run $S/koridor_blender.py -- $R shots=$n; done; echo "koridor $(date +%H:%M)"
for n in 1 2 3 4 5 6 7 8 9; do timeout 2400 "$B" -b --factory-startup -P $S/gostinaya_blender.py -- krem greywalls stroitel smceil floor=5B5B59-555553 plank=0.6x0.09 ceil=8 shots=$n tag=_sm real samples=500 dexp=-0.4 2>&1 | grep -i "Traceback\|Error:" | grep -v HIP; done; echo "gost $(date +%H:%M)"
for r in sanuzel_blender vanna_blender kuhnya_blender komnata_blender spalnya_blender; do run $S/$r.py -- elev shots=0 esamples=96 iesk=0.03; done; echo "WET DONE $(date +%H:%M)"
