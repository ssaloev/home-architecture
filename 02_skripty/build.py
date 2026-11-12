"""Собрать весь альбом одной командой:
    python build.py            — все листы: SVG -> PNG (01_chertezhi) + PDF-альбом (06_albom)
    python build.py --fast     — только SVG, без рендера (проверить, что всё строится)
Данные правятся только в data/kvartira.json."""
import os, sys, time
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
os.chdir(ROOT)

# Порядок листов = ведомость чертежей (как в профессиональном альбоме). Имя файла -> название.
SHEETS = [
    ("t0_titul", "Титульный лист"),
    ("t1_vedomost", "Ведомость чертежей"),
    ("t2_trebovaniya", "Исходные требования и стиль"),
    ("s1_obmer", "Обмерный план"),
    ("s1b_demontazh", "План демонтажа и монтажа перегородок"),
    ("s2_mebel", "Планировочное решение с расстановкой мебели"),
    ("s2b_mebel_razm", "Планировочное решение с размерами"),
    ("s12_poly", "План покрытий пола"),
    ("s7_pol", "План тёплого пола"),
    ("s13_potolok", "План потолка"),
    ("s14_svet", "План привязки осветительных приборов"),
    ("s4_vykl", "План размещения выключателей"),
    ("s3_rozetki", "План размещения розеток"),
    ("s3b_shchit", "Схема щита — группы, автоматы, кабели"),
    ("s6_kond", "План кондиционеров"),
    ("s5_santeh", "План сантехнического оборудования"),
    ("s5a_uzly", "Санузел и ванная — узлы сантехники"),
    ("s11_kuhnya", "План кухни — мебель и техника"),
    ("s15_razv_plan", "План для развертки стен"),
    ("s16_razv_gost", "Развертка стен гостиной"),
    ("s17_razv_komn", "Развертка стен комнаты"),
    ("s18_razv_sp2", "Развертка стен спальни 2"),
    ("s19_razv_kor", "Развертка стен коридора"),
    ("s20_razv_prih", "Развертка стен прихожей"),
    ("s24_prih_var", "Прихожая — варианты планировки"),
    ("s10_razv_kuh", "Развертка стен кухни"),
    ("s8_razv_su", "Развертка стен санузла"),
    ("s9_razv_van", "Развертка стен ванной"),
    ("s21_otdelka", "Ведомость отделки помещений"),
    ("s22_materialy", "Материалы и палитра"),
    ("s23_vizual_1", "Визуализация гостиной — от двери к окну"),
    ("s23_vizual_2", "Визуализация гостиной — от окна к двери"),
    ("s23_vizual_3", "Визуализация гостиной — диван и кресла"),
    ("s23_vizual_4", "Визуализация гостиной — ТВ-зона"),
    ("s23_vizual_5", "Визуализация гостиной — общий вид"),
    ("s23_vizual_6", "Визуализация гостиной — кресло и столик"),
    ("s23_vizual_7", "Визуализация гостиной — деталь стены"),
    ("s23_vizual_8", "Визуализация гостиной — потолок"),
    ("s23_vizual_9", "Визуализация гостиной — угол потолка"),
    ("s23_vizual_10", "Визуализация второй гостиной — от двери к окну"),
    ("s23_vizual_11", "Визуализация второй гостиной — от окна к шкафу"),
    ("s23_vizual_12", "Визуализация второй гостиной — ТВ-зона"),
    ("s23_vizual_13", "Визуализация коридора — вид к прихожей"),
    ("s23_vizual_14", "Визуализация прихожей — входная дверь"),
    ("s23_vizual_15", "Визуализация прихожей — шкаф и место для гостей"),
    ("s23_vizual_16", "Визуализация прихожей — обувница и зеркало"),
]
EXTRA = [("sZ_zamer", "Замерный лист — что проверить рулеткой")]   # вне нумерации

ns = {"__name__": "album", "__file__": os.path.join(ROOT, "core.py")}
exec(open("core.py", encoding="utf-8").read(), ns)
ns["SHEET_NO"] = {f: i + 1 for i, (f, _) in enumerate(SHEETS)}
ns["SHEET_NO"]["sZ_zamer"] = "—"
ns["LISTOV"] = len(SHEETS)
ns["SHEETS"] = SHEETS; ns["PROJ"] = PROJ
for f in ("listy_osnovnye.py", "listy_novye.py"):
    if os.path.exists(f):
        exec(open(f, encoding="utf-8").read(), ns)

done = set(ns["DONE"])
missing = [f for f, _ in SHEETS if f not in done]
print(f"SVG: {len(done)} листов" + (f"; НЕ ПОСТРОЕНЫ: {', '.join(missing)}" if missing else ""))
if "--fast" in sys.argv: sys.exit()

import render, pymupdf
svgdir = ns["OUT_SVG"]; pngdir = os.path.join(PROJ, "01_chertezhi"); pdfdir = os.path.join(ROOT, "out", "pdf")
albdir = os.path.join(PROJ, "06_albom")
for d in (pngdir, pdfdir, albdir): os.makedirs(d, exist_ok=True)
t0 = time.time()
order = [f for f, _ in SHEETS if f in done] + [f for f, _ in EXTRA if f in done]
for f in order:
    svg = os.path.join(svgdir, f + ".svg")
    render.png(svg, os.path.join(pngdir, f + ".png"))
    render.pdf(svg, os.path.join(pdfdir, f + ".pdf"))
    print("  ", f)
alb = pymupdf.open()
for f in order:
    with pymupdf.open(os.path.join(pdfdir, f + ".pdf")) as one:
        alb.insert_pdf(one, from_page=0, to_page=0)
toc = [[1, f"{ns['SHEET_NO'].get(f, '—')}. {dict(SHEETS + EXTRA)[f]}", i + 1] for i, f in enumerate(order)]
alb.set_toc(toc)
out = os.path.join(albdir, "albom_chernovik.pdf")
alb.save(out, garbage=3, deflate=True)
print(f"Готово за {time.time()-t0:.0f} с: {out}  ({len(order)} стр.)")
