"""Собирает vanna_blender.py (ванная) и sanuzel_blender.py (санузел): шапка komnata_blender + wet_common + *_room + рендер-хвост."""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('komnata_blender.py', encoding='utf-8').read().split('\n')
end = next(i for i, l in enumerate(src) if l.startswith('WALLC ='))
tail_i = next(i for i, l in enumerate(src) if l.startswith('sc.render.engine = "CYCLES"'))
tail = '\n'.join(src[tail_i:])
common = open('wet_common.py', encoding='utf-8').read()
a0 = next(i for i, l in enumerate(src) if l.startswith('def ac_unit('))
a1 = next(i for i in range(a0 + 1, len(src)) if src[i] and not src[i].startswith((' ', '\t')))
acdef = '\n'.join(src[a0:a1])                     # функция кондиционера из komnata_blender.py
for room, out in (('vannaya_room.py', 'vanna_blender.py'), ('sanuzel_room.py', 'sanuzel_blender.py'), ('kuhnya_room.py', 'kuhnya_blender.py')):
    body = open(room, encoding='utf-8').read().replace('#==AC==', acdef)
    folder = [l for l in body.split('\n') if l.startswith('OUTDIR')][0].split('"')[1]
    head = '\n'.join(src[5:end]).replace('"08_vizualizacii", "komnata"', '"08_vizualizacii", "%s"' % folder)
    head = head.replace('OPT.get("shots", "1,2,3")', 'OPT.get("shots", "1,2,3,4")')
    body = body.replace('#==COMMON==', common)
    doc = '# -*- coding: utf-8 -*-\n"""%s — СГЕНЕРИРОВАН gen_vanna.py из %s + wet_common.py. Не править вручную.\nЗапуск: blender -b --factory-startup -P %s -- [quick] [shots=1,2,3,4] [all=g1]"""\n' % (folder, room, out)
    open(out, 'w', encoding='utf-8').write(doc + head + '\n' + body + '\n' + tail)
    print('ok', out)
