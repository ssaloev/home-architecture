import os
os.chdir(r"D:\PROJECT\sadi_architertura\02_skripty")
src = open('komnata_blender.py', encoding='utf-8').read().split('\n')
head = '\n'.join(src[5:117])
head = head.replace('"08_vizualizacii", "komnata"', '"08_vizualizacii", "spalnya2"')
head = head.replace('X0, X1, Z0, Z1 = 5.745, 8.945, 0.309, 6.545', 'X0, X1, Z0, Z1 = 10.072, 14.745, 4.327, 7.491')
head = head.replace('WX0, WX1, WS, WT = 6.273, 8.437, 0.80, 2.40', 'WZ0, WZ1, WS, WT = 5.618, 7.182, 0.80, 2.40      # окно на правой стене (x = X1)')
head = head.replace('DX0, DX1, DH = 8.145, 8.945, 2.10', 'DZ0, DZ1, DH = 6.60, 7.40, 2.10                   # дверь на левой стене (x = X0)')
tail_i = next(i for i, l in enumerate(src) if l.startswith('sc.render.engine = "CYCLES"'))
tail = '\n'.join(src[tail_i:])
body = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spalnya_body.py"), encoding='utf-8').read()
doc = '# -*- coding: utf-8 -*-\n"""Спальня 2 — вариант 3: серые панели, мягкое изголовье-стена, линейный свет.\nЗапуск: blender -b --factory-startup -P spalnya_blender.py -- [quick] [shots=1,2,3]"""\n'
open('spalnya_blender.py', 'w', encoding='utf-8').write(doc + head + '\n' + body + '\n' + tail)
print('ok')
