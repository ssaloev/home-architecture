#!/bin/bash
# 17.11.2026: полный рендер с ДЕКОРОМ + ортогональные виды стен для разверток (как у SM)
cd "$(dirname "$0")/.." ; B="D:/ProgramFiles/blender.exe"; S=02_skripty
bash $S/final_plus.sh
run() { timeout 1200 "$B" -b --factory-startup -P "$@" 2>&1 | grep -i "Traceback\|Error:" | grep -v HIP; }
for r in komnata_blender spalnya_blender kuhnya_blender vanna_blender sanuzel_blender; do run $S/$r.py -- elev shots=0 esamples=96 iesk=0.03; echo "elev $r $(date +%H:%M)"; done
echo ELEV DONE
