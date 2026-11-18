# 18.11.2026: кухня по обмеру 3300×3400 — 2 варианта на выбор (вертикально, для телефона)
from PIL import Image, ImageDraw, ImageFont
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", s)
X0, X1, Z0, Z1 = 9.586, 12.886, 1.309, 4.709
S = 270; PW, PH = 1080, 1220
im = Image.new("RGB", (PW, 150 + 2 * PH), "white"); d = ImageDraw.Draw(im)
d.text((40, 30), "Кухня по обмеру 3300×3400 — 2 варианта", font=F(44, True), fill="#222")
d.text((40, 92), "фасады серо-белые, ручки чёрные; размеры в мм", font=F(28), fill="#555")
WALL, CAB, COL, TECH, GREEN = "#4A4740", "#C9C9C5", "#9C9A95", "#FFFFFF", "#2E8B57"

def panel(k, title, sub, items, extra=None):
    oy = 150 + k * PH
    P = lambda x, z: (int(150 + (x - X0) * S), int(oy + 170 + (z - Z0) * S))
    d.rectangle([20, oy, PW - 20, oy + PH - 30], outline="#888", width=4)
    d.text((40, oy + 18), title, font=F(40, True), fill="#222")
    for i, t in enumerate(sub): d.text((40, oy + 70 + i * 34), t, font=F(26), fill="#444")
    T = 0.12
    for (a, b, c, e) in ((X0 - T, Z0 - T, X1 + T, Z0), (X0 - T, Z0, X0, Z1 + T), (X1, Z0 - T, X1 + T, Z1 + T), (10.105, Z1, X1 + T, Z1 + T)):
        d.rectangle([*P(a, b), *P(c, e)], fill=WALL)
    d.rectangle([*P(11.036, Z0 - T), *P(12.506, Z0)], fill="#BFD9EF"); d.text(P(11.40, Z0 - 0.105), "окно 1600", font=F(22, True), fill="#1F4E8C")
    d.rectangle([*P(12.506, Z0), *P(X1, 2.109)], fill="#8A8780"); d.text(P(12.52, 1.55), "вент", font=F(22, True), fill="white")
    d.rectangle([*P(12.506, 2.109), *P(X1, 2.409)], fill="#D6D3CC", outline="#555", width=2); d.text(P(12.52, 2.19), "труба", font=F(20), fill="#333")
    d.text(P(9.62, 4.80), "вход 519", font=F(24, True), fill="#8A5A00")
    for (a, b, c, e, t, col) in items:
        d.rectangle([*P(a, b), *P(c, e)], fill=col, outline="#333", width=3)
        bx0, by0 = P(a, b); bx1, by1 = P(c, e); lines = t.split("\n"); fs = 22
        for i, ln in enumerate(lines):
            w = d.textlength(ln, font=F(fs, True))
            d.text(((bx0 + bx1) / 2 - w / 2, (by0 + by1) / 2 - len(lines) * 13 + i * 27), ln, font=F(fs, True), fill="#222")
    if extra: extra(P)
    # размеры
    y = P(0, Z1)[1] + 70; d.line([P(X0, 0)[0], y, P(X1, 0)[0], y], fill="#B03A2E", width=3)
    d.text(((P(X0, 0)[0] + P(X1, 0)[0]) / 2 - 30, y - 34), "3300", font=F(28, True), fill="#B03A2E")
    x = P(X0, 0)[0] - 70; d.line([x, P(0, Z0)[1], x, P(0, Z1)[1]], fill="#B03A2E", width=3)
    d.text((x - 52, (P(0, Z0)[1] + P(0, Z1)[1]) / 2), "3400", font=F(24, True), fill="#B03A2E")

def chairs(P, pts):
    for (x, z) in pts:
        c = P(x, z); d.ellipse([c[0] - 30, c[1] - 30, c[0] + 30, c[1] + 30], fill="#DDD", outline="#555", width=2)

RX = X1 - 0.60
A = [(X0, 1.50, X0 + 0.60, 2.10, "колонна\nкладовая", CAB), (X0, 2.10, X0 + 0.60, 2.70, "колонна\nдуховка\n+СВЧ", CAB),   # 18.11: холодильник первым от входа
     (X0, 2.70, X0 + 0.75, 3.60, "холодильник\nside-by-side\n900", COL),
     (RX, 2.41, X1, 3.01, "мойка\n600", TECH), (RX, 3.01, X1, 3.46, "ПММ\n450", CAB), (RX, 3.46, X1, 4.11, "стол-\nешница", CAB),
     (RX, 4.11, X1, 4.709, "плита\n600", TECH), (10.55, Z0 + 0.10, 11.75, Z0 + 0.80, "стол 1200×700", "#F3F0EA")]
panel(0, "1. ПРЯМАЯ (по правой стене)", ["мойка у трубы → ПММ → столешница → плита;", "слева от входа: холодильник первым, дальше 2 колонны; стол у окна"],
      A, lambda P: chairs(P, [(10.85, 2.40), (11.45, 2.40), (12.05, 1.65)]))
B = [(X0, 2.10, X0 + 0.60, 2.70, "колонна\nдуховка\n+СВЧ", CAB), (X0, 2.70, X0 + 0.75, 3.60, "холодильник\nside-by-side\n900", COL),
     (RX, 2.41, X1, 3.01, "мойка\n600", TECH), (RX, 3.01, X1, 3.46, "ПММ\n450", CAB), (RX, 3.46, X1, 4.709, "столешница\nугол", CAB),
     (11.686, Z1 - 0.60, RX, Z1, "плита\n600", TECH), (10.50, Z1 - 0.60, 11.686, Z1, "столешница\n(рабочая)", CAB),
     (10.55, Z0 + 0.10, 11.75, Z0 + 0.80, "стол 1200×700", "#F3F0EA")]
panel(1, "2. УГЛОВАЯ (Г-образная)", ["мойка у трубы → ПММ → угол → плита на нижней стене;", "больше столешницы; слева от входа холодильник, за ним колонна"],
      B, lambda P: chairs(P, [(10.85, 2.40), (11.45, 2.40), (12.05, 1.65)]))
im.save("D:/PROJECT/sadi_architertura/01_chertezhi/shema_kuhnya_ugol.png"); print("ok")
