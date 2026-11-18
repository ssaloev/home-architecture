# 18.11.2026: схема для заказчика — 3 варианта двери ванной (вид сверху), вертикально для телефона
import math
from PIL import Image, ImageDraw, ImageFont
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", s)
S = 320; XA, ZA = 3.30, 6.50; PW, PH = 1080, 760
W_ = 1080; H_ = 140 + 3 * (PH + 40)
im = Image.new("RGB", (W_, H_), "white"); d = ImageDraw.Draw(im)
d.text((40, 30), "Дверь в ванную — 3 варианта (вид сверху)", font=F(44, True), fill="#222")
d.text((40, 90), "проём 900, коридор 653 мм", font=F(30), fill="#555")
GREY, WALL, BLUE, RED, GREEN = "#EEE", "#555", "#2F6DB5", "#C0392B", "#2E8B57"

def panel(k, title, verdict, ok, draw_door):
    oy = 140 + k * (PH + 40)
    P = lambda x, z: (40 + (x - XA) * S, oy + 110 + (z - ZA) * S)
    d.rectangle([20, oy, W_ - 20, oy + PH], outline=GREEN if ok == 1 else (RED if ok == 0 else "#D68910"), width=6)
    d.text((40, oy + 15), title, font=F(38, True), fill="#222")
    d.text((40, oy + 62), verdict, font=F(28), fill=GREEN if ok == 1 else (RED if ok == 0 else "#B9770E"))
    # стены
    for (x0, z0, x1, z1) in ((3.30, 6.55, 6.35, 6.672), (3.30, 7.325, 3.749, 7.434), (4.649, 7.325, 6.35, 7.434), (3.455, 7.434, 3.564, 8.45), (5.914, 7.434, 6.35, 8.45)):
        d.rectangle([*P(x0, z0), *P(x1, z1)], fill=WALL)
    d.rectangle([*P(3.564, 7.434), *P(5.914, 8.45)], fill="#F7F7F5")
    d.text(P(4.75, 6.80), "КОРИДОР  653", font=F(30, True), fill="#333")
    d.text(P(4.95, 7.70), "ВАННАЯ", font=F(30, True), fill="#333")
    d.rectangle([*P(3.564, 8.154), *P(4.264, 8.45)], fill="#DDE8F3", outline="#557", width=3); d.text(P(3.62, 8.22), "ванна", font=F(26), fill="#333")
    d.rectangle([*P(5.434, 7.55), *P(5.914, 8.15)], fill="#FFFFFF", outline="#557", width=3); d.text(P(5.45, 7.80), "раковина", font=F(22), fill="#333")
    draw_door(P, oy)

def arc(P, hx, hz, r, a0, a1, col):
    c = P(hx, hz); R = r * S
    d.arc([c[0] - R, c[1] - R, c[0] + R, c[1] + R], a0, a1, fill=col, width=4)

def v1(P, oy):   # откатная: полотно 950 едет вправо по стене коридора
    d.rectangle([*P(4.649, 7.28), *P(5.60, 7.325)], fill=BLUE)
    d.rectangle([*P(3.749, 7.30), *P(4.70, 7.325)], outline=BLUE, width=3)
    a = P(4.0, 7.18); b = P(4.95, 7.18); d.line([a, b], fill=BLUE, width=5); d.polygon([(b[0], b[1]), (b[0] - 22, b[1] - 12), (b[0] - 22, b[1] + 12)], fill=BLUE)
    d.text(P(3.56, 6.69), "полотно едет вправо по стене", font=F(24), fill=BLUE)
def v2(P, oy):   # внутрь 700, петли справа
    d.rectangle([*P(3.749, 7.325), *P(3.949, 7.434)], fill=WALL)        # проём сужен до 700
    d.line([P(4.649, 7.434), P(4.649, 8.134)], fill=BLUE, width=8)
    arc(P, 4.649, 7.434, 0.70, 90, 180, BLUE)
    d.text(P(3.98, 7.48), "700", font=F(26, True), fill=BLUE)
    arc(P, 4.649, 7.434, 0.90, 90, 180, RED); d.text(P(4.30, 8.30), "900 упрётся в ванну", font=F(22), fill=RED)
def v3(P, oy):   # наружу 600
    d.rectangle([*P(4.349, 7.325), *P(4.649, 7.434)], fill=WALL)        # проём сужен до 600
    d.line([P(3.749, 7.325), P(3.749, 6.725)], fill=BLUE, width=8)
    arc(P, 3.749, 7.325, 0.60, 270, 360, BLUE)
    d.text(P(4.42, 7.05), "открыта — коридор перекрыт", font=F(24), fill=RED)

panel(0, "1. ОТКАТНАЯ 900 (советую)", "ширина 900 сохраняется, ничему не мешает; полотно по стене коридора", 1, v1)
panel(1, "2. РАСПАШНАЯ ВНУТРЬ 700", "дверь 900 внутрь бьёт в ванну — только 700, петли справа", 2, v2)
panel(2, "3. НАРУЖУ 600", "узкая; открытая — перегораживает коридор", 0, v3)
im.save("D:/PROJECT/sadi_architertura/01_chertezhi/shema_dver_vannoy.png")
print("ok")
