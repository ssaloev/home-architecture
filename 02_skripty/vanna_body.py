# ======================= ВАННАЯ — вариант A (12.11.2026), стиль фото 15: чёрный «мрамор» Nero Marquina, керамогранит 600×1200
X0, X1, Z0, Z1 = 3.564, 6.073, 8.018, 9.509
H, HC = 2.70, 2.50
DX0, DX1, DH = 4.255, 5.055, 2.10                       # дверь в верхней стене (z = Z0), открывается внутрь
GRAF = "#" + OPT.get("ward", "2F2F31")

def marble_img(name, nx, ny, tiles_u, tiles_v, seed=3, kind="dark"):
    # 13.11: как в образце (05_ishodniki/obrazec_albom_dizajnera_76m2.pdf, л.46–50): тёмный графитово-коричневый мрамор
    # с густой сеткой белых прожилок + белый мрамор с мягкими серыми прожилками
    def fbm(beta, s):
        r = np.random.default_rng(s); F = np.fft.fftfreq(ny)[:, None]; G = np.fft.rfftfreq(nx)[None, :]
        k = np.sqrt((F * ny / max(nx, ny)) ** 2 + (G * nx / max(nx, ny)) ** 2) + 1e-4
        spec = (r.normal(size=k.shape) + 1j * r.normal(size=k.shape)) * k ** (-beta); spec[0, 0] = 0
        f = np.fft.irfft2(spec, s=(ny, nx)); return (f - f.mean()) / f.std()
    yy, xx = np.mgrid[0:ny, 0:nx] / max(nx, ny)
    F = [fbm(2.0, seed + i) for i in range(6)]
    def vein(dirx, diry, K, w, warp, mask_f, mt):
        g = xx * dirx + yy * diry + warp * F[mask_f] + 0.15 * F[(mask_f + 1) % 6]
        return np.exp(-np.abs(np.sin(g * K)) / w) * np.clip(F[(mask_f + 2) % 6] - mt, 0, 1).clip(0, 1) ** 0.5
    DENSE = (vein(2.4, 1.6, 6.0, 0.030, 0.16, 0, -0.8) + vein(-1.2, 2.6, 8.0, 0.022, 0.14, 1, -0.5) * 0.9
             + vein(1.0, -2.2, 11.0, 0.016, 0.12, 2, -0.2) * 0.8 + vein(2.8, 0.6, 15.0, 0.012, 0.10, 3, 0.0) * 0.7
             + vein(0.4, 3.0, 19.0, 0.010, 0.10, 4, 0.2) * 0.6)
    SOFT = vein(2.0, 1.4, 5.0, 0.018, 0.4, 0, 0.0) * 0.7 + vein(-1.4, 2.2, 9.0, 0.008, 0.3, 1, 0.3) * 0.5
    SPARSE = vein(2.6, 1.7, 4.0, 0.012, 0.2, 0, 0.2) * 0.8 + vein(-1.2, 2.8, 3.5, 0.007, 0.25, 1, 0.5) * 0.5
    KINDS = {  # база (sRGB 0..1), прожилки, рисунок, контраст пятен
        "dark":   ((0.27, 0.245, 0.23), (0.90, 0.88, 0.85), DENSE, 0.10),   # тёмный мрамор образца
        "white":  ((0.91, 0.90, 0.885), (0.55, 0.53, 0.52), SOFT, 0.015),   # белый мрамор
        "grafit": ((0.30, 0.30, 0.31), (0.80, 0.80, 0.80), SPARSE, 0.06),   # графит, редкие прожилки
        "grey":   ((0.50, 0.495, 0.49), (0.90, 0.90, 0.89), DENSE * 0.8, 0.05),  # серый мрамор с белыми прожилками
        "greige": ((0.55, 0.52, 0.48), (0.88, 0.86, 0.82), SPARSE, 0.05),   # тёплый серо-бежевый камень
        "beton":  ((0.40, 0.395, 0.39), (0.40, 0.40, 0.40), SPARSE * 0, 0.12),
        # 13.11 серая гамма (заказчик: «серый, тёмно-серый, чёрно-серый, графитово-серый»), одна плитка на всю ванную
        "g1": ((0.56, 0.56, 0.56), (0.86, 0.86, 0.86), DENSE * 0.55, 0.06),   # серый
        "g2": ((0.42, 0.42, 0.425), (0.84, 0.84, 0.84), DENSE * 0.55, 0.07),  # тёмно-серый
        "g3": ((0.31, 0.31, 0.32), (0.82, 0.82, 0.82), DENSE * 0.55, 0.08),   # графит
        "g4": ((0.20, 0.20, 0.205), (0.80, 0.80, 0.80), DENSE * 0.55, 0.10)}  # чёрно-серый   # микроцемент графит
    bcl, vcl, v, kc = KINDS[kind]
    v = np.clip(v, 0, 1)
    bc = np.array(bcl) * (1 + kc * F[4][..., None]) + 0.01 * F[5][..., None]
    vc = np.array(vcl)
    col = bc * (1 - v[..., None]) + vc * v[..., None]
    col = col + np.random.default_rng(seed + 9).normal(0, 0.008, (ny, nx))[..., None]
    tu, tv = nx / tiles_u, ny / tiles_v
    ax_, ay_ = np.arange(nx), np.arange(ny)
    seam = (np.minimum(ax_ % tu, tu - ax_ % tu)[None, :] < 1.2) | (np.minimum(ay_ % tv, tv - ay_ % tv)[:, None] < 1.2)
    col[seam] = col[seam] * 0.75
    col = np.clip(col, 0, 1) ** 2.2
    img = bpy.data.images.new(name, nx, ny, alpha=False); px = np.ones((ny, nx, 4), np.float32); px[..., :3] = col
    img.pixels.foreach_set(px.ravel()); img.pack(); return img
def marble_mat(name, img, S, rough=0.12):
    m = mat(name, "#1A1A1C", rough); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.projection = "BOX"; t.projection_blend = 0.0; t.interpolation = "Cubic"
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = S
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], t.inputs["Vector"]); nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m
ALL = OPT.get("all", "")
IMG_W = marble_img("мрамор тёмный стены", 1024, 2048, 2, 2, 3, ALL or "dark")     # плитка 600×1200 вертикально
IMG_L = marble_img("мрамор белый стены", 1024, 2048, 2, 2, 21, ALL or "white")
IMG_F = marble_img("мрамор тёмный пол", 2048, 1024, 2, 2, 11, ALL or "dark")      # пол 1200×600
M = dict(tile=marble_mat("Керамогранит тёмный", IMG_W, (1 / 1.2, 1 / 1.2, 1 / 2.4), 0.15),
         tilew=marble_mat("Керамогранит белый", IMG_L, (1 / 1.2, 1 / 1.2, 1 / 2.4), 0.15),
         tilef=marble_mat("Керамогранит пол", IMG_F, (1 / 2.4, 1 / 1.2, 1.0), 0.18),
         ceil=mat("Потолок", "#EEECE7", 0.9), white=mat("Сантехника белая", "#F4F4F2", 0.08),
         acryl=mat("Ванна акрил", "#F6F6F4", 0.12), black=mat("Чёрный матовый", "#151516", 0.35, 0.6),
         ward=mat("Графит матовый", GRAF, 0.45), door=mat("Двери", "#E2E0DB", 0.45),
         mirror=mat("Зеркало", "#E3E7E8", 0.02, 1.0), glass=mat("Стекло", "#FFFFFF", 0.0, transm=1.0),
         dglass=mat("Стекло дверцы", "#202426", 0.05), towel=mat("Полотенце", "#8A8B8F", 1.0),
         led=emis("LED", "#FFE6C8", 6), ledm=emis("LED за зеркалом", "#FFE6C8", 40), spot=emis("Спот", "#FFF4E2", 12))
T = 0.12
# ---------------- коробка
box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["tilef"])
box("Стена лев", X0 - T, Z0 - T, X0, Z1 + T, 0, H, M["tile"])
box("Стена прав", X1, Z0 - T, X1 + T, Z1 + T, 0, H, M["tilew"])
box("Стена низ", X0 - T, Z1, X1 + T, Z1 + T, 0, H, M["tilew"])
box("Стена верх 1", X0 - T, Z0 - T, DX0, Z0, 0, H, M["tile"])
box("Стена верх 2", DX1, Z0 - T, X1 + T, Z0, 0, H, M["tile"])
box("Над дверью", DX0, Z0 - T, DX1, Z0, DH, H, M["tile"])
box("Дверь", DX0 + 0.005, Z0 - 0.07, DX1 - 0.005, Z0 - 0.03, 0.005, DH - 0.005, M["door"])
for (a, b_) in ((DX0, DX0 + 0.012), (DX1 - 0.012, DX1)): box("Наличник", a, Z0 - 0.03, b_, Z0 + 0.003, 0, DH, M["black"])
box("Наличник верх", DX0, Z0 - 0.03, DX1, Z0 + 0.003, DH - 0.012, DH, M["black"])
box("Ручка двери", DX1 - 0.09, Z0 - 0.03, DX1 - 0.07, Z0 + 0.04, 1.0, 1.02, M["black"]); box("Ручка двери2", DX1 - 0.20, Z0 + 0.025, DX1 - 0.07, Z0 + 0.04, 1.0, 1.02, M["black"])
box("Потолок", X0 - T, Z0 - T, X1 + T, Z1 + T, HC, HC + 0.05, M["ceil"])

# ---------------- стиральная машина (левая стена у двери) + графитовый шкаф над ней (бойлер Б1 внутри)
WX = 4.218
box("Стиралка", X0 + 0.06, 8.218, WX, 8.818, 0.0, 0.85, M["white"], 0.012)
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.165, depth=0.03, location=W(WX + 0.005, 8.518, 0.46), rotation=(0, math.radians(90), 0)); bpy.context.active_object.data.materials.append(M["dglass"])
bpy.ops.mesh.primitive_torus_add(major_radius=0.175, minor_radius=0.014, location=W(WX + 0.01, 8.518, 0.46), rotation=(0, math.radians(90), 0)); bpy.context.active_object.data.materials.append(M["black"])
box("Панель стиралки", WX, 8.25, WX + 0.003, 8.62, 0.76, 0.82, M["black"])
box("Шкаф над стиралкой", X0, Z0, X0 + 0.42, 8.86, 1.50, HC, M["ward"])
for (a, b_) in ((Z0 + 0.002, 8.438), (8.442, 8.858)):
    box("Фасад шкафа", X0 + 0.42, a, X0 + 0.44, b_, 1.50, HC - 0.003, M["ward"], 0.002)
for zz in (8.40, 8.48):
    box("Ручка шкафа", X0 + 0.44, zz - 0.006, X0 + 0.456, zz + 0.006, 1.52, 1.82, M["black"], 0.002)
box("LED под шкафом", X0 + 0.05, Z0 + 0.03, X0 + 0.38, 8.83, 1.495, 1.50, M["led"])

# ---------------- ванна 1400×550 у нижней стены + бортик-полка из керамогранита + стеклянная шторка
BX0, BX1, BZ0 = 3.60, 5.04, 8.89
box("Бортик лев", X0, BZ0 - 0.02, BX0, Z1, 0, 0.58, M["tile"])
box("Полка-бортик", BX1, BZ0 - 0.04, BX1 + 0.10, Z1, 0, 0.60, M["tile"])
tub = box("Ванна", BX0, BZ0, BX1, Z1 - 0.005, 0, 0.58, M["acryl"], 0.015)
cav = box("Чаша", BX0 + 0.06, BZ0 + 0.06, BX1 - 0.07, Z1 - 0.065, 0.16, 0.9, M["acryl"], 0.0)
md = tub.modifiers.new("cav", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cav
cav.hide_render = True; cav.display_type = "WIRE"
box("Шторка стекло", BX1 - 0.012, BZ0, BX1 - 0.004, Z1 - 0.01, 0.58, 2.00, M["glass"])
box("Профиль шторки", BX1 - 0.016, Z1 - 0.025, BX1, Z1, 0.58, 2.00, M["black"])
box("Смеситель", 4.25, Z1 - 0.05, 4.45, Z1, 0.82, 0.90, M["black"], 0.006)
box("Излив", 4.33, Z1 - 0.20, 4.37, Z1 - 0.05, 0.70, 0.73, M["black"], 0.006)
box("Штанга душа", 4.70, Z1 - 0.03, 4.72, Z1, 1.00, 1.90, M["black"])
box("Лейка", 4.66, Z1 - 0.07, 4.76, Z1 - 0.03, 1.55, 1.75, M["black"], 0.01)
box("Ниша LED", 3.85, Z1 - 0.10, 4.55, Z1 - 0.095, 1.385, 1.39, M["led"])
box("Полочка ниши", 3.85, Z1 - 0.10, 4.55, Z1, 1.10, 1.12, M["tile"])
box("Ниша бок1", 3.84, Z1 - 0.10, 3.85, Z1, 1.10, 1.40, M["tile"]); box("Ниша бок2", 4.55, Z1 - 0.10, 4.56, Z1, 1.10, 1.40, M["tile"])
box("Ниша верх", 3.84, Z1 - 0.10, 4.56, Z1, 1.39, 1.40, M["tile"])
for (xx, c) in ((3.95, "white"), (4.05, "black"), (4.40, "white")):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.03, depth=0.17, location=W(xx, Z1 - 0.05, 1.205)); bpy.context.active_object.data.materials.append(M[c])

# ---------------- унитаз подвесной + гигиенический душ (правая стена, у нижнего угла)
IX = X1 - 0.20
box("Короб инсталляции", IX, 8.865, X1, Z1, 0, 1.12, M["tile"])
box("Унитаз", IX - 0.55, 9.115 - 0.18, IX, 9.115 + 0.18, 0.30, 0.42, M["white"], 0.06)
box("Сиденье", IX - 0.54, 9.115 - 0.175, IX - 0.02, 9.115 + 0.175, 0.42, 0.44, M["white"], 0.03)
box("Кнопка смыва", IX - 0.006, 9.115 - 0.12, IX, 9.115 + 0.12, 0.92, 1.08, M["black"], 0.004)
box("Гиг. душ", IX - 0.03, 8.90, IX, 8.94, 0.62, 0.72, M["black"], 0.005)
box("Лейка гиг.", IX - 0.07, 8.895, IX - 0.03, 8.945, 0.64, 0.70, M["black"], 0.008)

# ---------------- столешница из керамогранита с накладной раковиной (правая стена, у двери) + зеркало с LED
VX = X1 - 0.48; VZ0, VZ1 = Z0, 8.818
box("Столешница", VX, VZ0, X1, VZ1, 0.80, 0.85, M["tile"])
box("Бок столешницы", VX, VZ1 - 0.05, X1, VZ1, 0.10, 0.80, M["tile"])
box("Задник ниши", X1 - 0.02, VZ0, X1, VZ1, 0.10, 0.80, M["tile"])
box("Полка ниши", VX + 0.02, VZ0, X1, VZ1 - 0.05, 0.38, 0.40, M["tile"])
box("Цоколь ниши", VX + 0.05, VZ0, X1, VZ1 - 0.05, 0.0, 0.10, M["black"])
box("LED под столешницей", VX + 0.03, VZ0 + 0.01, VX + 0.06, VZ1 - 0.06, 0.795, 0.80, M["led"])
for k in range(3):
    box("Полотенце", X1 - 0.40, VZ0 + 0.06 + k * 0.23, X1 - 0.08, VZ0 + 0.26 + k * 0.23, 0.40, 0.52, M["towel"], 0.03)
for k in range(2):
    box("Корзина", X1 - 0.38, VZ0 + 0.10 + k * 0.33, X1 - 0.10, VZ0 + 0.38 + k * 0.33, 0.10, 0.30, M["black"], 0.02)
SC = (VZ0 + VZ1) / 2
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.22, depth=0.13, location=W(X1 - 0.25, SC, 0.85 + 0.065))
sink = bpy.context.active_object; sink.scale = (0.78, 1.0, 1.0); sink.data.materials.append(M["white"])
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.20, depth=0.2, location=W(X1 - 0.25, SC, 0.85 + 0.13 + 0.03))
sc_ = bpy.context.active_object; sc_.scale = (0.76, 0.98, 1.0); sc_.hide_render = True; sc_.display_type = "WIRE"
md = sink.modifiers.new("cav", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = sc_
bv = sink.modifiers.new("bv", "BEVEL"); bv.width = 0.008; bv.segments = 3
box("Смеситель настенный", X1 - 0.03, SC - 0.04, X1, SC + 0.04, 1.08, 1.16, M["black"], 0.005)
box("Излив раковины", X1 - 0.20, SC - 0.015, X1 - 0.03, SC + 0.015, 1.10, 1.125, M["black"], 0.005)
MZ0, MZ1, MH0, MH1 = VZ0 + 0.06, VZ1 - 0.06, 1.25, 2.10
box("Зеркало", X1 - 0.045, MZ0, X1 - 0.035, MZ1, MH0, MH1, M["mirror"], 0.002)
for (a0, a1, b0, b1) in ((MZ0, MZ1, MH0, MH0 + 0.012), (MZ0, MZ1, MH1 - 0.012, MH1), (MZ0, MZ0 + 0.012, MH0, MH1), (MZ1 - 0.012, MZ1, MH0, MH1)):
    box("Рамка зеркала", X1 - 0.05, a0, X1 - 0.035, a1, b0, b1, M["black"])
box("Подложка зеркала", X1 - 0.035, MZ0 + 0.06, X1 - 0.004, MZ1 - 0.06, MH0 + 0.06, MH1 - 0.06, M["black"])
for (a0, a1, b0, b1) in ((MZ0 + 0.04, MZ1 - 0.04, MH0 + 0.04, MH0 + 0.05), (MZ0 + 0.04, MZ1 - 0.04, MH1 - 0.05, MH1 - 0.04),
                         (MZ0 + 0.04, MZ0 + 0.05, MH0 + 0.04, MH1 - 0.04), (MZ1 - 0.05, MZ1 - 0.04, MH0 + 0.04, MH1 - 0.04)):
    box("LED за зеркалом", X1 - 0.034, a0, X1 - 0.030, a1, b0, b1, M["ledm"])
# подвес-кольца у зеркала (как на фото 15)
for (hh, r) in ((1.62, 0.07), (1.50, 0.06)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.008, location=W(X1 - 0.25, VZ1 + 0.02, hh), rotation=(math.radians(90), 0, math.radians(90)))
    bpy.context.active_object.data.materials.append(M["led"])
box("Подвес шнур", X1 - 0.252, VZ1 + 0.018, X1 - 0.248, VZ1 + 0.022, 1.69, HC, M["black"])
for (xx, c) in ((X1 - 0.42, "white"), (X1 - 0.36, "black")):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.03, depth=0.16, location=W(xx, VZ0 + 0.10, 0.93)); bpy.context.active_object.data.materials.append(M[c])

# ---------------- полотенцесушитель чёрный (верхняя стена, между дверью и столешницей)
TX0, TX1 = DX1 + 0.08, VX - 0.06
for xx in (TX0, TX1): box("Сушитель стойка", xx - 0.01, Z0 + 0.04, xx + 0.01, Z0 + 0.06, 0.85, 1.65, M["black"])
for k in range(6): box("Сушитель перекладина", TX0, Z0 + 0.045, TX1, Z0 + 0.06, 0.90 + k * 0.145, 0.915 + k * 0.145, M["black"])
box("Полотенце висит", TX0 + 0.03, Z0 + 0.06, TX1 - 0.03, Z0 + 0.09, 1.10, 1.57, M["towel"], 0.02)

# ---------------- свет: 4 точечных + LED
for xx in (4.15, 5.35):
    for zz in (8.50, 9.10):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.04, depth=0.004, location=W(xx, zz, HC - 0.002)); bpy.context.active_object.data.materials.append(M["spot"])
        lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = float(OPT.get("spot", "35")); lt.spot_size = math.radians(80); lt.spot_blend = 0.7; lt.color = (1, 0.92, 0.82)
        o = bpy.data.objects.new("Спот", lt); o.location = W(xx, zz, HC - 0.02); sc.collection.objects.link(o)
lt = bpy.data.lights.new("Зеркало", "AREA"); lt.shape = "RECTANGLE"; lt.size = 0.6; lt.size_y = 0.6; lt.energy = 12; lt.color = (1, 0.9, 0.78)
o = bpy.data.objects.new("Зеркало", lt); o.location = W(X1 - 0.30, SC, 1.70); o.rotation_euler = (0, math.radians(-90), 0); sc.collection.objects.link(o)
try: o.visible_camera = False; o.visible_glossy = False
except Exception: pass
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[1].default_value = 0.6

CAMS = {"1": ("1_ot_dveri", W(4.55, 8.20, 1.60), W(5.7, 9.35, 0.95), 13),
        "2": ("2_stoleshnica_zerkalo", W(4.35, 8.80, 1.55), W(X1, 8.40, 1.25), 15),
        "3": ("3_vanna", W(5.75, 8.25, 1.65), W(3.7, 9.40, 0.85), 13),
        "4": ("4_k_dveri", W(5.35, 9.30, 1.60), W(3.9, 8.05, 1.15), 13)}
