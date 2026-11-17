#!/bin/bash
# 14.11.2026: БЫСТРЫЙ ПРОСМОТР всей квартиры (EEVEE, ~1–2 мин): bash 02_skripty/prosmotr.sh [доп. аргументы, напр. oboi=hessian_230:C9BCA8]
# результат: 08_vizualizacii/_prosmotr.jpg (все комнаты на одном листе). Финальные рендеры (Cycles) — без "fast".
cd "$(dirname "$0")/.." ; B="D:/ProgramFiles/blender.exe"; S=02_skripty; X="$@"; t0=$(date +%s)
"$B" -b --factory-startup -P $S/gostinaya_blender.py -- fast krem greywalls stroitel smceil floor=5B5B59-555553 plank=0.6x0.09 ceil=8 shots=3,4 tag=_sm $X >/dev/null 2>&1
"$B" -b --factory-startup -P $S/komnata_blender.py -- fast shots=2,3 $X >/dev/null 2>&1
"$B" -b --factory-startup -P $S/spalnya_blender.py -- fast shots=1,2 $X >/dev/null 2>&1
"$B" -b --factory-startup -P $S/koridor_blender.py -- fast shots=1,4 $X >/dev/null 2>&1
"$B" -b --factory-startup -P $S/sanuzel_blender.py -- fast shots=1 exp=1.0 $X >/dev/null 2>&1
"$B" -b --factory-startup -P $S/vanna_blender.py -- fast shots=1 exp=1.0 $X >/dev/null 2>&1
"$B" -b --factory-startup -P $S/kuhnya_blender.py -- fast shots=2 exp=1.1 $X >/dev/null 2>&1
python -X utf8 - <<'PY'
from PIL import Image, ImageDraw, ImageFont
import os
V="08_vizualizacii"; f=ImageFont.truetype("arial.ttf",26)
fs=[("gostinaya/q__smA_3_divan_i_kresla","Гостиная 1"),("gostinaya/q__smA_4_tv_zona","Гостиная 1 — ТВ"),("komnata/q_2_ot_okna_k_shkafu","Гостиная 2"),("komnata/q_3_tv_zona","Гостиная 2 — ТВ"),
    ("spalnya2/q_1_ot_dveri_k_krovati","Спальня"),("spalnya2/q_2_ot_okna_k_shkafu","Спальня — шкаф"),("koridor/q_1_koridor_k_prihozhey","Коридор"),("koridor/q_4_prihozhaya_gosti","Прихожая"),
    ("sanuzel/q_1_ot_dveri","Санузел"),("vannaya/q_1_ot_dveri","Ванная"),("kuhnya/q_2_rabochaya_zona","Кухня")]
c=Image.new("RGB",(1080,len(fs)*658),"white"); d=ImageDraw.Draw(c); fb=ImageFont.truetype("arialbd.ttf",34)   # вертикально под телефон
for i,(p,t) in enumerate(fs):
    q=os.path.join(V,p+".jpg"); y=i*658
    d.text((20,y+8),t,fill="black",font=fb)
    if os.path.exists(q): c.paste(Image.open(q).resize((1080,608)),(0,y+50))
c.save(os.path.join(V,"_prosmotr.jpg"),quality=86); print("OK", os.path.join(V,"_prosmotr.jpg"))
PY
echo "время: $(( $(date +%s) - t0 )) с"
