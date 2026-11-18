# 18.11.2026: лист моделей спальни 2 с номерами (вертикально, для телефона) — заказчик выбирает номер в каждом разделе
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
PROJ = r"D:/PROJECT/sadi_architertura"; TH = PROJ + "/03_materialy/blenderkit/_thumbs/"
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", s)
SP = PROJ + "/08_vizualizacii/spalnya2/"
cur = lambda f, box: (lambda: Image.open(SP + f).crop(box))
OUT = "_sogl_spalnya2_modeli.jpg"
SEC = [("КРОВАТЬ 1400×2000", [(cur("3_krovat_pryamo_plus.jpg", (560, 780, 1360, 1080)), "сейчас: мягкая|кремовая"),
                             ("a3c4d119-4447-4b78-a1ca-d6f57309c9d0", "серая мягкая|на ножках"), ("8bf9e517-a0f8-4969-a2a2-49639eed73a1", "серая|бокс-спринг"),
                             ("4c22d080-5dfc-4b4b-a691-6241c6c4a566", "мягкая, светлая,|высокое изголовье"), ("2fc41ff0-a7d2-4381-931d-eaa01261f754", "тёмное изголовье,|серое бельё")]),
       ("ТУМБОЧКИ (место 450 с каждой стороны)", [("cf1171ff-5999-40db-bc09-9628342a35ab", "белая с ящиками|(сейчас)"), ("341b04e0-697d-4adb-9fef-45b69b5cae8f", "белая, ящик|+ полка, 450"),
                             ("f13d8196-1d50-4882-a10b-ec1d00b7638c", "белая|скруглённая"), ("e1126ded-5cbe-44b5-b207-92a9fbda8491", "подвесная|(парит над полом)")]),
       ("СВЕТИЛЬНИКИ НАД ТУМБОЧКАМИ", [(cur("3_krovat_pryamo_plus.jpg", (440, 380, 660, 720)), "сейчас:|абажур"), ("f40f1b2c-0305-4672-b3be-4453f6cce7e4", "чёрный купол"),
                             ("581347ca-0607-45f9-9504-7cd9fafce845", "чёрный цилиндр,|минимализм"), ("245ad359-51b9-4ab0-8676-d6034e5ae8fe", "стекло + латунь"),
                             ("2c266e2b-e5aa-4468-8e6f-3f91010feae5", "чёрный с золотом,|тонкий")]),
       ("ТУАЛЕТНЫЙ СТОЛИК (угол у окна, 800)", [((lambda: Image.open(PROJ + "/08_vizualizacii/koridor/v4_obuvnica_zerkalo_print.jpg").crop((150, 250, 1500, 1750))), "белый, ящики|+ зеркало LED (как|в прихожей)"),
                             ("af442b28-3e6b-49d5-b106-bbdad223bb9b", "орех, круглое|зеркало с LED"), ("678b2327-0c3d-4d2e-adac-d9af9c01cb86", "столик с|откидным зеркалом")]),
       ("ПУФ К СТОЛИКУ", [("58d879b6-ba9b-4fa5-a475-424d2fdc7700", "серый, ткань"), ("c64209e3-bb12-4058-b30f-fba70cfdc8dd", "мех, светлый"),
                         ("7e8fcbb3-a8cf-40f0-8e41-949de8b6570c", "серый|двойной"), ("36ffe0af-d826-44e3-8cc9-56d6ad162758", "кожа, чёрный")])]
W, C, TW = 1080, 3, 330
H = 170 + sum(80 + ((len(it) + C - 1) // C) * (TW + 90) for _, it in SEC)
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
d.text((30, 25), "Спальня 2 — модели: напиши номер в каждом разделе", font=F(36, True), fill="#222")
d.text((30, 85), "все бесплатные, под наши размеры; например «кровать 2, тумбочки 1, свет 3…»", font=F(26), fill="#555")
y = 170
for title, items in SEC:
    d.rectangle([20, y, W - 20, y + 60], fill="#2F2F31"); d.text((40, y + 12), title, font=F(32, True), fill="white"); y += 80
    for i, (src, cap) in enumerate(items):
        r, c = divmod(i, C); x = 30 + c * (TW + 25); yy = y + r * (TW + 90)
        try: t = src() if callable(src) else Image.open(TH + src + ".jpg")
        except Exception: t = Image.new("RGB", (TW, TW), "#EEE")
        t = ImageOps.pad(t.convert("RGB"), (TW, TW), color="white"); im.paste(t, (x, yy)); d.rectangle([x, yy, x + TW, yy + TW], outline="#999", width=2)
        d.ellipse([x + 8, yy + 8, x + 62, yy + 62], fill="#D35400"); n = str(i + 1); d.text((x + 35 - d.textlength(n, font=F(32, True)) / 2, yy + 16), n, font=F(32, True), fill="white")
        for k, ln in enumerate(cap.split("|")): d.text((x + 4, yy + TW + 8 + k * 30), ln, font=F(25, k == 0), fill="#222")
    y += ((len(items) + C - 1) // C) * (TW + 90)
im.save(PROJ + "/08_vizualizacii/" + OUT, quality=90); print("ok", H)
