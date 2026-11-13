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
ALL = OPT.get("all", "g1")      # 13.11: заказчик выбрал плитку №1 — серый, одна на всё помещение
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
def wb(n, w, a0, a1, d0, d1, h0, h1, m, bev=0.0):
    """коробка у стены w (L/R/T/B): a — вдоль стены, d — отступ от стены в комнату"""
    if w == "L": return box(n, X0 + d0, a0, X0 + d1, a1, h0, h1, m, bev)
    if w == "R": return box(n, X1 - d1, a0, X1 - d0, a1, h0, h1, m, bev)
    if w == "T": return box(n, a0, Z0 + d0, a1, Z0 + d1, h0, h1, m, bev)
    return box(n, a0, Z1 - d1, a1, Z1 - d0, h0, h1, m, bev)
def pt(w, a, d):
    return {"L": (X0 + d, a), "R": (X1 - d, a), "T": (a, Z0 + d), "B": (a, Z1 - d)}[w]
def room_box(doorwall, da0, da1):
    box("Пол", X0 - T, Z0 - T, X1 + T, Z1 + T, -0.05, 0, M["tilef"])
    for (w, x0_, z0_, x1_, z1_) in (("L", X0 - T, Z0 - T, X0, Z1 + T), ("R", X1, Z0 - T, X1 + T, Z1 + T),
                                   ("T", X0 - T, Z0 - T, X1 + T, Z0), ("B", X0 - T, Z1, X1 + T, Z1 + T)):
        if w != doorwall: box("Стена " + w, x0_, z0_, x1_, z1_, 0, H, M["tile"]); continue
        if w in ("T", "B"):
            box("Стена", x0_, z0_, da0, z1_, 0, H, M["tile"]); box("Стена", da1, z0_, x1_, z1_, 0, H, M["tile"]); box("Над дверью", da0, z0_, da1, z1_, DH, H, M["tile"])
        else:
            box("Стена", x0_, z0_, x1_, da0, 0, H, M["tile"]); box("Стена", x0_, da1, x1_, z1_, 0, H, M["tile"]); box("Над дверью", x0_, da0, x1_, da1, DH, H, M["tile"])
    # дверное полотно (крем) в проёме + чёрный наличник + ручка
    sgn = {"T": -1, "B": 1, "L": -1, "R": 1}[doorwall]
    wb("Дверь", doorwall, da0 + 0.005, da1 - 0.005, -0.07, -0.03, 0.005, DH - 0.005, M["door"])
    for (a, b_) in ((da0, da0 + 0.012), (da1 - 0.012, da1)): wb("Наличник", doorwall, a, b_, -0.03, 0.003, 0, DH, M["black"])
    wb("Наличник верх", doorwall, da0, da1, -0.03, 0.003, DH - 0.012, DH, M["black"])
    wb("Ручка", doorwall, da1 - 0.20, da1 - 0.07, 0.025, 0.04, 1.0, 1.02, M["black"]); wb("Ручка ножка", doorwall, da1 - 0.09, da1 - 0.07, -0.03, 0.04, 1.0, 1.02, M["black"])
    box("Потолок", X0 - T, Z0 - T, X1 + T, Z1 + T, HC, HC + 0.05, M["ceil"])
def hung(n, w, a, kind="wc", d0=0.20, depth=None):
    """подвесной унитаз / биде — реальные модели BlenderKit (13.11), на коробе инсталляции, верх чаши h=400"""
    f = os.path.join(BK, ("unitaz_podv" if kind == "wc" else "bide_podv") + ".blend")
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [o for o in src.objects]
    objs = [o for o in dst.objects if o is not None and o.type == "MESH"]
    ytop = -0.126 if kind == "wc" else 0.071                # верх чаши в координатах модели
    x, z = pt(w, a, d0); rz = {"T": 0, "B": 180, "L": 90, "R": -90}[w]
    Tm = Matrix.Translation(W(x, z, 0.40 - ytop)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
    for o in objs:
        sc.collection.objects.link(o); o.matrix_world = Tm @ o.matrix_world
        for i, ms in enumerate(o.data.materials):
            if ms and any(k in ms.name.lower() for k in ("chrome", "metal", "steel")): o.data.materials[i] = M["black"]
    if depth:   # 13.11: компактная модель — глубина от короба depth (м), масштаб только вдоль нормали к стене
        bpy.context.view_layer.update()
        nx_, nz_ = {"T": (0, 1), "B": (0, -1), "L": (1, 0), "R": (-1, 0)}[w]; nv = W(nx_, nz_, 0) - W(0, 0, 0)
        p0 = W(x, z, 0); cur = max((o.matrix_world @ Vector(c) - p0).dot(nv) for o in objs for c in o.bound_box)
        k = depth / cur; S = Matrix.Identity(4)
        for i in range(3):
            for j in range(3): S[i][j] += (k - 1) * nv[i] * nv[j]
        A = Matrix.Translation(p0) @ S @ Matrix.Translation(-p0)
        for o in objs:
            if o.parent not in objs: o.matrix_world = A @ o.matrix_world
        print("HUNG depth", n, round(cur, 3), "->", depth)
    return objs
def vessel(w, a, d, top, r=0.20, k=0.78):
    x, z = pt(w, a, d)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r, depth=0.13, location=W(x, z, top + 0.065))
    s_ = bpy.context.active_object; s_.scale = ((k, 1, 1) if w in ("L", "R") else (1, k, 1)); s_.data.materials.append(M["white"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r - 0.02, depth=0.2, location=W(x, z, top + 0.16))
    c_ = bpy.context.active_object; c_.scale = s_.scale; c_.hide_render = True; c_.display_type = "WIRE"
    md = s_.modifiers.new("cav", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = c_
    bv = s_.modifiers.new("bv", "BEVEL"); bv.width = 0.008; bv.segments = 3
    wb("Смеситель настенный", w, a - 0.04, a + 0.04, 0, 0.03, top + 0.24, top + 0.32, M["black"], 0.005)
    wb("Излив", w, a - 0.015, a + 0.015, 0.03, d - 0.02, top + 0.26, top + 0.285, M["black"], 0.005)
def mirror_led(w, a0, a1, h0, h1):
    wb("Зеркало", w, a0, a1, 0.035, 0.045, h0, h1, M["mirror"], 0.002)
    for (p0, p1, q0, q1) in ((a0, a1, h0, h0 + 0.012), (a0, a1, h1 - 0.012, h1), (a0, a0 + 0.012, h0, h1), (a1 - 0.012, a1, h0, h1)):
        wb("Рамка зеркала", w, p0, p1, 0.035, 0.05, q0, q1, M["black"])
    wb("Подложка зеркала", w, a0 + 0.06, a1 - 0.06, 0.004, 0.035, h0 + 0.06, h1 - 0.06, M["black"])
    for (p0, p1, q0, q1) in ((a0 + 0.04, a1 - 0.04, h0 + 0.04, h0 + 0.05), (a0 + 0.04, a1 - 0.04, h1 - 0.05, h1 - 0.04),
                             (a0 + 0.04, a0 + 0.05, h0 + 0.04, h1 - 0.04), (a1 - 0.05, a1 - 0.04, h0 + 0.04, h1 - 0.04)):
        wb("LED за зеркалом", w, p0, p1, 0.030, 0.034, q0, q1, M["ledm"])
OPENC = OPT.get("open", "0") == "1"      # open=1 — рендер с ОТКРЫТЫМИ дверцами шкафов: видно бойлер / бак / химию
M["boiler"] = mat("Бойлер белый", "#EDEDEB", 0.25)
M["inner"] = mat("Шкаф внутри", "#4A4A4D", 0.6)
M["boilerg"] = mat("Бойлер серый металлик", "#8C8E91", 0.35)
def _cyl(x, z, r, h0, h1, m, v=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h1 - h0, location=W(x, z, (h0 + h1) / 2)); o = bpy.context.active_object; o.data.materials.append(m); return o
def cab_content(kind, w, a0, a1, d, h0, h1):
    kind, ac = kind if isinstance(kind, tuple) else (kind, (a0 + a1) / 2)
    if kind == "boiler":                # Ariston Lydos Eco 80 V ≈ Ø450×760, трубы и кабель вниз
        x, z = pt(w, ac, 0.25); top = h1 - 0.06
        o = _cyl(x, z, 0.225, top - 0.76, top, M["boiler"], 64); bv = o.modifiers.new("b", "BEVEL"); bv.width = 0.03; bv.segments = 4
        _cyl(x, z, 0.06, top - 0.79, top - 0.76, M["black"])
        x2, z2 = pt(w, ac, 0.47); box("Дисплей бойлера", x2 - 0.04, z2 - 0.04, x2 + 0.04, z2 + 0.04, top - 0.33, top - 0.25, M["black"])
        for da in (-0.07, 0.07):
            xp, zp = pt(w, ac + da, 0.25); _cyl(xp, zp, 0.011, h0 + 0.02, top - 0.76, M["white"], 16)
    elif kind == "flatboiler":          # 13.11 (по фото заказчика): плоский бойлер 470×875×285, серый, сверху; насос бака — внизу отсека
        top = h1 - 0.05; bot = top - 0.875
        wb("Бойлер плоский", w, ac - 0.235, ac + 0.235, 0.01, 0.295, bot, top, M["boilerg"], 0.06)
        wb("Панель бойлера", w, ac - 0.06, ac + 0.06, 0.294, 0.298, bot + 0.06, bot + 0.20, M["black"])
        for da in (-0.07, 0.07):
            xp, zp = pt(w, ac + da, 0.12); _cyl(xp, zp, 0.011, h0 + 0.02, bot, M["white"], 16)
        x, z = pt(w, a0 + 0.12, 0.13); _cyl(x, z, 0.07, h0 + 0.02, h0 + 0.20, M["ward"], 32)
    elif kind == "tank":                # узкий бак 200 л 500×200×1800 + насос сверху
        wb("Бак 200 л", w, a0 + 0.02, a1 - 0.02, 0.01, d - 0.03, 0.05, 1.85, M["boiler"], 0.02)
        x, z = pt(w, ac, (d - 0.02) / 2); _cyl(x, z, 0.07, 1.90, 2.15, M["ward"], 32); _cyl(x, z, 0.012, 2.15, h1, M["white"], 16)
        wb("Указатель уровня", w, ac - 0.01, ac + 0.01, d - 0.031, d - 0.029, 0.15, 1.75, M["glass"])
    elif kind == "tank_top":            # 13.11: плоский бак 200 л 580×300×1150 в шкафу над биде (на раме), уровень сбоку
        wb("Бак 200 л", w, a0 + 0.025, a1 - 0.025, 0.01, d - 0.03, h0 + 0.03, h1 - 0.04, M["boiler"], 0.02)
        wb("Указатель уровня", w, ac - 0.01, ac + 0.01, d - 0.031, d - 0.029, h0 + 0.10, h1 - 0.12, M["glass"])
        x, z = pt(w, a1 - 0.08, (d - 0.02) / 2); _cyl(x, z, 0.015, h1 - 0.04, h1, M["white"], 16)
    elif kind == "store":               # нижний отсек под бойлером: туалетная бумага, запасы, бытовая мелочь
        hb = h0 + 0.018
        for hs in ((h0 + h1) / 2,):
            wb("Полка отсека", w, a0 + 0.02, a1 - 0.02, 0.01, d - 0.03, hs, hs + 0.018, M["ward"])
        for i in range(4):
            x, z = pt(w, a0 + 0.08 + i * 0.115, d * 0.45); _cyl(x, z, 0.055, hb, hb + 0.10, M["white"], 32)
            _cyl(x, z, 0.055, hb + 0.10, hb + 0.20, M["white"], 32)
        wb("Коробка", w, a1 - 0.22, a1 - 0.04, 0.03, d - 0.06, hb, hb + 0.18, M["towel"], 0.01)
    elif kind == "laundry":             # полки: порошки, гели, сухие полотенца
        SH_ = (h0 + 0.02, (h0 + h1) / 2) if h1 - h0 < 1.2 else (h0 + 0.02, h0 + 0.42, h0 + 0.86)
        for hh in SH_:
            wb("Полка шкафа", w, a0 + 0.02, a1 - 0.02, 0.01, d - 0.03, hh, hh + 0.018, M["ward"])
        if len(SH_) == 3:               # верхняя полка — корзины с запасами
            for j in range(3):
                wb("Корзина", w, a0 + 0.04 + j * ((a1 - a0 - 0.08) / 3), a0 + 0.02 + (j + 1) * ((a1 - a0 - 0.08) / 3), 0.03, d - 0.05, SH_[2] + 0.018, SH_[2] + 0.22, M["black"], 0.015)
        hb = h0 + 0.038
        for i, c in enumerate(("white", "black", "white", "white")):
            x, z = pt(w, a0 + 0.07 + i * 0.075, d * 0.45)
            box("Бытовая химия", x - 0.03, z - 0.03, x + 0.03, z + 0.03, hb, hb + (0.24 if i % 2 else 0.20), M[c], 0.008)
        wb("Коробка порошка", w, a1 - 0.24, a1 - 0.04, 0.03, d - 0.06, hb, hb + 0.28, M["white"], 0.01)
        hm = SH_[1] + 0.018
        for k in range(3):
            for j in range(2):
                wb("Сухое полотенце", w, a0 + 0.04 + j * 0.27, a0 + 0.29 + j * 0.27, 0.03, d - 0.06, hm + k * 0.075, hm + (k + 1) * 0.075 - 0.004, M["towel" if k % 2 else "white"], 0.02)
def _door_open(w, p0, p1, d, h0, h1, hinge_lo):
    """фасад, повёрнутый на 100° вокруг петли (открыт)"""
    hx, hz = pt(w, p0 if hinge_lo else p1, d)
    fx, fz = pt(w, p1 if hinge_lo else p0, d); nx, nz = pt(w, p0, d + 1.0)
    bx, bz = pt(w, p0, d)
    u = Vector((fx - hx, fz - hz)); nrm = Vector((nx - bx, nz - bz))
    ang = math.atan2(u.x * nrm.y - u.y * nrm.x, u.dot(nrm))      # в плоскости (x,z) — поворот u к нормали
    ang = math.copysign(math.radians(100), ang)
    piv = bpy.data.objects.new("Петля фасада", None); piv.location = W(hx, hz, 0); sc.collection.objects.link(piv)
    parts = [wb("Фасад", w, p0, p1, d - 0.02, d, h0 + 0.002, h1 - 0.002, M["ward"], 0.002)]
    ah = p1 - 0.05 if hinge_lo else p0 + 0.05
    parts.append(wb("Ручка", w, ah - 0.006, ah + 0.006, d, d + 0.016, h0 + 0.03, h0 + 0.33, M["black"], 0.002))
    for o_ in parts: o_.parent = piv; o_.matrix_parent_inverse = Matrix.Translation(piv.location).inverted()
    piv.rotation_euler = (0, 0, -ang)        # ось z мира; (x,z)-план → (x,-y): знак меняется
def cabinet(n, w, a0, a1, d, h0, h1, doors=2, content=None, led=True):
    """графитовый навесной шкаф (прячет бойлер / бак / химию), гладкие фасады, чёрные ручки, LED снизу"""
    if OPENC and content:
        for (q0, q1, e0, e1) in ((a0, a1, 0, d - 0.02), ):
            wb(n + " зад", w, q0, q1, 0, 0.01, h0, h1, M["inner"])
            wb(n + " бок", w, q0, q0 + 0.018, 0, d - 0.02, h0, h1, M["ward"]); wb(n + " бок", w, q1 - 0.018, q1, 0, d - 0.02, h0, h1, M["ward"])
            wb(n + " дно", w, q0, q1, 0, d - 0.02, h0, h0 + 0.018, M["ward"]); wb(n + " верх", w, q0, q1, 0, d - 0.02, h1 - 0.018, h1, M["ward"])
        cab_content(content, w, a0, a1, d, h0, h1)
    else:
        wb(n, w, a0, a1, 0, d - 0.02, h0, h1, M["ward"])
    step = (a1 - a0) / doors
    for k in range(doors):
        p0, p1 = a0 + k * step + 0.002, a0 + (k + 1) * step - 0.002
        if OPENC and content: _door_open(w, p0, p1, d, h0, h1, k % 2 == 0); continue
        wb("Фасад", w, p0, p1, d - 0.02, d, h0 + 0.002, h1 - 0.002, M["ward"], 0.002)
        ah = p1 - 0.05 if k % 2 == 0 else p0 + 0.05
        wb("Ручка", w, ah - 0.006, ah + 0.006, d, d + 0.016, h0 + 0.03, h0 + 0.33, M["black"], 0.002)
    if led: wb("LED под шкафом", w, a0 + 0.03, a1 - 0.03, 0.05, d - 0.05, h0 - 0.005, h0, M["led"])
def spots(P, e=None):
    for (xx, zz) in P:
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.04, depth=0.004, location=W(xx, zz, HC - 0.002)); bpy.context.active_object.data.materials.append(M["spot"])
        lt = bpy.data.lights.new("Спот", "SPOT"); lt.energy = float(OPT.get("spot", "110")); lt.spot_size = math.radians(80); lt.spot_blend = 0.7; lt.color = (1, 0.92, 0.82)   # 13.11: светлее (по заказчику)
        o = bpy.data.objects.new("Спот", lt); o.location = W(xx, zz, HC - 0.02); sc.collection.objects.link(o)
    w_ = sc.world or bpy.data.worlds.new("W"); sc.world = w_; w_.use_nodes = True; w_.node_tree.nodes["Background"].inputs[1].default_value = 0.6
def towel_rail(w, a0, a1):
    for aa in (a0, a1): wb("Сушитель стойка", w, aa - 0.01, aa + 0.01, 0.04, 0.06, 0.85, 1.65, M["black"])
    for k in range(6): wb("Сушитель перекладина", w, a0, a1, 0.045, 0.06, 0.90 + k * 0.145, 0.915 + k * 0.145, M["black"])
    wb("Полотенце", w, a0 + 0.03, a1 - 0.03, 0.06, 0.09, 1.10, 1.57, M["towel"], 0.02)
def bottles(w, a, d, h, cols=("white", "black", "white")):
    for i, c in enumerate(cols):
        x, z = pt(w, a + i * 0.07, d)
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.028, depth=0.16, location=W(x, z, h + 0.08)); bpy.context.active_object.data.materials.append(M[c])
def bk_load(fname, Tm, recolor=None, keep=()):
    """загрузить модель BlenderKit и поставить матрицей Tm; recolor — материал для всех слотов, кроме имён из keep"""
    f = os.path.join(BK, fname + ".blend")
    if not os.path.exists(f): print("NO MODEL", fname); return []
    with bpy.data.libraries.load(f, link=False) as (src, dst): dst.objects = [o for o in src.objects]
    allo = [o for o in dst.objects if o is not None and o.type not in ("LIGHT", "CAMERA")]
    for o in allo: sc.collection.objects.link(o)
    bpy.context.view_layer.update()
    roots = [o for o in allo if o.parent is None or o.parent not in allo]
    for o in roots: o.matrix_world = Tm @ o.matrix_world
    objs = [o for o in allo if o.type == "MESH"]
    if recolor is not None:
        for o in objs:
            for i, ms in enumerate(o.data.materials):
                if not ms or not any(k in ms.name.lower() for k in keep): o.data.materials[i] = recolor
    return objs
def towel_rail_bk(w, a, hc=1.25):
    """полотенцесушитель (модель BlenderKit, перекрашен в чёрный, полотенца — серые)"""
    x, z = pt(w, a, 0.0); rz = {"T": 0, "B": 180, "L": 90, "R": -90}[w]
    Tm = Matrix.Translation(W(x, z, hc)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
    objs = bk_load("polotencesushitel", Tm)
    for o in objs:
        for i, ms in enumerate(o.data.materials):
            o.data.materials[i] = M["towel"] if (ms and "towel" in ms.name.lower()) else M["black"]
    return objs
def washer_bk(w, a0, a1, d0=0.05):
    """стиральная машина Samsung WD11 (600×586×849) спиной к стене w, дверцей в комнату"""
    if w != "L": raise ValueError("только L")
    Tm = Matrix.Translation(Vector((X0 + d0 + 0.586, -a1, 0.0))) @ Matrix.Rotation(math.radians(90), 4, "Z")
    return bk_load("stiralka_samsung", Tm)
def bath_bk(x0, x1, z0, z1, h=0.56):
    """ванна (модель BlenderKit 1476×742×515) масштабом в прямоугольник плана"""
    Tm = Matrix.Translation(W((x0 + x1) / 2, (z0 + z1) / 2, 0)) @ Matrix.Diagonal(((x1 - x0) / 1.476, (z1 - z0) / 0.742, h / 0.515, 1.0))
    return bk_load("vanna_akril", Tm, M["acryl"], keep=("metal", "black"))
def bk_fit(fname, cx, cz, h0, rot=0.0, target=None, axis="w", recolor=None, keep=()):
    """модель BlenderKit: центр габарита в (cx, cz), низ на h0, поворот rot° вокруг вертикали, масштаб по ширине target"""
    objs = bk_load(fname, Matrix.Identity(4), recolor, keep)
    allo = [o for o in bpy.data.objects if o in objs or (o.parent in objs)]
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    if not pts: return objs
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    size = {"w": max(mx_.x - mn.x, mx_.y - mn.y), "h": mx_.z - mn.z}[axis]
    k = (target / size) if target else 1.0; ctr = (mn + mx_) / 2
    T_ = Matrix.Translation(W(cx, cz, h0)) @ Matrix.Rotation(math.radians(rot), 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-ctr.x, -ctr.y, -mn.z)))
    roots = set()
    for o in objs:
        r = o
        while r.parent is not None: r = r.parent
        roots.add(r)
    print("BKFIT", fname, tuple(round(v,3) for v in mn), tuple(round(v,3) for v in mx_), round(k,3), len(objs), len(roots))
    for r in roots: r.matrix_world = T_ @ r.matrix_world
    return objs
M["curtain"] = mat("Шторка ткань светло-серая", "#C9C8C4", 0.95, transm=0.15)
def curtain_strip(n, a, b, h0, h1, amp=0.025, waves=None, m=None):
    """тканевая шторка (волнами) между точками плана a=(x,z) и b=(x,z), по высоте h0..h1"""
    ax_, az_ = a; bx_, bz_ = b
    L = math.hypot(bx_ - ax_, bz_ - az_); ux, uz = (bx_ - ax_) / L, (bz_ - az_) / L; nx, nz = -uz, ux
    nw = waves or max(2, int(L / 0.09)); nu = nw * 8
    bm = bmesh.new(); rows = []
    for j, h in enumerate((h0, (h0 + h1) / 2, h1)):
        row = []
        for i in range(nu + 1):
            t = i / nu; off = amp * math.sin(t * nw * 2 * math.pi)
            row.append(bm.verts.new(W(ax_ + ux * L * t + nx * off, az_ + uz * L * t + nz * off, h)))
        rows.append(row)
    for j in range(2):
        for i in range(nu): bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    me = bpy.data.meshes.new(n); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(n, me); sc.collection.objects.link(o)
    o.data.materials.append(m or M["curtain"]); sd = o.modifiers.new("t", "SOLIDIFY"); sd.thickness = 0.003
    for p in o.data.polygons: p.use_smooth = True
    return o
def curtain_rail(pts, h=2.00):
    """Г-образный карниз (чёрная труба Ø20) по точкам плана + кольца"""
    for (p, q) in zip(pts[:-1], pts[1:]):
        box("Карниз шторки", min(p[0], q[0]) - 0.01, min(p[1], q[1]) - 0.01, max(p[0], q[0]) + 0.01, max(p[1], q[1]) + 0.01, h - 0.01, h + 0.01, M["black"], 0.004)
