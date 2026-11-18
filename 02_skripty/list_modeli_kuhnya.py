# 18.11.2026: лист моделей кухни с номерами (вертикально, для телефона) — заказчик выбирает номер в каждом разделе
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
PROJ = r"D:/PROJECT/sadi_architertura"; TH = PROJ + "/03_materialy/blenderkit/_thumbs/"
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", s)
def crop_int():
    im = Image.open(PROJ + "/08_vizualizacii/vannaya/v9_rakovina_polotenca_print.jpg"); return im.crop((520, 1500, 1330, 2150))
OUT = "_sogl_kuhnya_modeli.jpg"
SEC = [("МОЙКА (тумба 600)", [(crop_int, "камень, чаша\nв столешнице, как в ванной"),
                              ("91a0d345-fcd0-4276-9bbe-d72c029ab2ea", "сталь 500×500")]),
       ("КРАН (смеситель)", [("d72e6594-4d2a-4211-96c8-787f4b2e13bb", "С2 — как в ванной\nи санузле (утв.)"), ("3a39bc99-05de-4be9-8eeb-b7c5b92572a3", "высокий тёмный"),
                             ("742d1d1e-4104-4b2c-8771-940fd6931aed", "высокий тонкий"), ("a9c9c33b-d7b9-4528-b804-fc572049d458", "Delta, гусак"),
                             ("2e20ef22-6890-4dc9-92f7-8e9ab3702251", "выдвижной излив"), ("7434539d-5ad3-431c-9226-3f9f5dba5e77", "низкий L-образный")]),
       ("ВАРОЧНАЯ ПАНЕЛЬ 600", [("4a960e36-3d38-44f1-a1b6-8cde22b1d549", "Bosch индукция 600"), ("ebd637c5-7820-47fa-8a7f-0b4a1da27ac5", "индукция 590"),
                                ("da045b04-b9c1-451a-b8e2-436ea8939439", "индукция 600"), ("d6c15e4b-e621-408b-98a6-65498d25daea", "Whirlpool 590"),
                                ("a576faae-b802-41a1-9c99-de1afe0ed3b1", "стеклокерамика 590")]),
       ("ДУХОВКА + СВЧ (в колонне)", [("5b7e1627-5c7b-40dc-9e74-4a0ea5653f41", "духовка 600"), ("11f652c3-351e-4da9-ad5e-979a01cdf356", "компактная 455\n(духовка+СВЧ)"),
                                      ("662647e4-f9d4-4b28-ba67-e02f90c16522", "духовка 600")]),
       ("ВЫТЯЖКА", [("edfb7c9b-cfb4-45e9-823e-b59c82c4ba02", "встроенная 600\n(в навесном шкафу)"), ("977f0bf9-00cf-4cd7-8bb3-2414fbffbb89", "наклонная 514"),
                    ("b5ca85cf-94d8-4c25-b8d5-b7f35a081261", "плоская 760")])]
import sys as _s
if len(_s.argv) > 1 and _s.argv[1] == "svch":
    OUT = "_sogl_kuhnya_svch.jpg"
    SEC = [("МИКРОВОЛНОВКА (над плитой, в шкафу над вытяжкой)", [("78612930-1e80-4761-b7fc-dc256043e3d6", "чёрная 456"), ("098a05b6-d1bb-480b-a6a4-ee3b12419af8", "477×289"),
           ("64f0b320-19ee-4657-bdfb-ca5dadcba28e", "503×316"), ("53fe30e5-8dd2-4e55-8dba-4a0250569d09", "Brastemp 539"), ("ace4ab37-7b63-42d1-985e-3c6bafc0ae9f", "550×330"),
           ("ab51cfe4-5fa6-4fdc-830b-87daa5d4265c", "компактная 450")])]
W, C, TW = 1080, 3, 330
rows = sum(1 + (len(it) + C - 1) // C for _, it in SEC)
H = 170 + sum(80 + ((len(it) + C - 1) // C) * (TW + 90) for _, it in SEC)
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
d.text((30, 25), "Кухня — модели: напиши номер" + (" в каждом разделе" if len(SEC) > 1 else ""), font=F(40, True), fill="#222")
d.text((30, 85), "все бесплатные, под наши размеры; например «мойка 1, кран 1, панель 1…»", font=F(26), fill="#555")
y = 170
for title, items in SEC:
    d.rectangle([20, y, W - 20, y + 60], fill="#2F2F31"); d.text((40, y + 12), title, font=F(32, True), fill="white"); y += 80
    for i, (src, cap) in enumerate(items):
        r, c = divmod(i, C); x = 30 + c * (TW + 25); yy = y + r * (TW + 90)
        try: t = src() if callable(src) else Image.open(TH + src + ".jpg")
        except Exception: t = Image.new("RGB", (TW, TW), "#EEE")
        t = ImageOps.pad(t.convert("RGB"), (TW, TW), color="white"); im.paste(t, (x, yy)); d.rectangle([x, yy, x + TW, yy + TW], outline="#999", width=2)
        d.ellipse([x + 8, yy + 8, x + 62, yy + 62], fill="#D35400"); n = str(i + 1); d.text((x + 35 - d.textlength(n, font=F(32, True)) / 2, yy + 16), n, font=F(32, True), fill="white")
        for k, ln in enumerate(cap.split("\n")): d.text((x + 4, yy + TW + 8 + k * 30), ln, font=F(25, k == 0), fill="#222")
    y += ((len(items) + C - 1) // C) * (TW + 90)
im.save(PROJ + "/08_vizualizacii/" + OUT, quality=90); print("ok", H)
