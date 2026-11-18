# ======================= ВАННАЯ по ОБМЕРУ 2350×2420 (утв. 17.11.2026, схема 01_chertezhi/shema_obmer_vanna.png)
# шахта на правой стене (X1 = её грань), стояк Т2 внизу (в коробе труб) → унитаз внизу правой стены, бойлер Б1 над ним;
# ванна 1700×700 вдоль левой стены (шторка на Г-карнизе); раковина 600×480 с открытой полкой и стиралка 10 кг — на правой стене у двери;
# дверь 900 в верхней стене, петли у ванны. Прежний вариант (2509×1491) — vannaya_room_v13_11.py
X0, X1, Z0, Z1 = 3.564, 5.914, 7.434, 9.854
H, HC = 2.70, 2.65
DX0, DX1, DH = 3.749, 4.649, 2.10                       # дверь в верхней стене (z = Z0)
OUTDIR = "vannaya"
#==COMMON==
room_box("T", DX0, DX1)

# ---- правая стена у двери: раковина 600×480; зеркало с LED
# 18.11 (заказчик: «поставь нормальную раковину, которую мы выбрали; утверждённую модель — везде»):
#   как в санузле — ИНТЕГРИРОВАННАЯ раковина в столешнице из белого искусственного камня (600×480×120, чаша 420×300 гл. 95, R35),
#   смеситель С2 на столешнице за чашей; под ней шкафчик (сифон, краны) серо-белый, ниже открытая полка с полотенцами
CT = 0.90; SZ0, SZ1 = 7.55, 8.15; CD = 0.48
M["kamen"] = mat("Искусственный камень белый", "#E9E7E2", 0.28)
_SC = (SZ0 + SZ1) / 2
_slab = wb("Столешница с раковиной", "R", SZ0, SZ1, 0, CD, CT - 0.12, CT, M["kamen"])
_bx, _bz = pt("R", _SC, 0.28)                              # центр чаши (сзади 130 — под смеситель)
bpy.ops.mesh.primitive_cube_add(location=W(_bx, _bz, CT + 0.005)); _cut = bpy.context.active_object
_cut.scale = (0.15, 0.21, 0.10); bpy.ops.object.transform_apply(scale=True)
_cb = _cut.modifiers.new("r", "BEVEL"); _cb.width = 0.035; _cb.segments = 10
bpy.context.view_layer.objects.active = _cut; bpy.ops.object.modifier_apply(modifier="r")
_bo = _slab.modifiers.new("chasha", "BOOLEAN"); _bo.object = _cut; _bo.operation = "DIFFERENCE"
bpy.context.view_layer.objects.active = _slab; bpy.ops.object.modifier_apply(modifier="chasha")
bpy.data.objects.remove(_cut, do_unlink=True)
_eb = _slab.modifiers.new("kromka", "BEVEL"); _eb.width = 0.004; _eb.segments = 3; _eb.limit_method = "ANGLE"
for _p in _slab.data.polygons: _p.use_smooth = True
_cyl(_bx, _bz, 0.019, CT - 0.096, CT - 0.093, M["black"], 32).name = "Донный клапан"
_fo = bk_fit("smesitel_c2", 0, 0, 0, 0)                   # смеситель С2 (утв. 17.11 в санузле)
_fm = [o for o in _fo if o.type == "MESH"]
if _fm:
    bpy.context.view_layer.update()
    _V = [o.matrix_world @ v.co for o in _fm for v in o.data.vertices]
    _zmin = min(v.z for v in _V); _base = [v for v in _V if v.z < _zmin + 0.02]
    _sx = sum(v.x for v in _base) / len(_base); _sy = sum(v.y for v in _base) / len(_base)
    _cx = (min(v.x for v in _V) + max(v.x for v in _V)) / 2; _cy = (min(v.y for v in _V) + max(v.y for v in _V)) / 2
    _ang = math.atan2(_cy - _sy, _cx - _sx)
    _rt = {o for o in _fo if o.parent is None or o.parent not in _fo}
    _R = Matrix.Rotation(math.pi - _ang, 4, "Z")              # излив → -X (от правой стены в чашу)
    _mx, _mz = pt("R", _SC, 0.065)
    _tgt = W(_mx, _mz, CT)
    for o in _rt: o.matrix_world = Matrix.Translation(_tgt) @ _R @ Matrix.Translation(Vector((-_sx, -_sy, -_zmin))) @ o.matrix_world
    for o in _fm:
        for i_ in range(len(o.data.materials)): o.data.materials[i_] = M["black"]
# 18.11 (заказчик: «полка висит непонятно где — соедини со шкафом, чтобы было одно; дверца без ручек — нажал, открылась»):
#   ОДНА тумба под столешницей: боковины 18 мм от дна до камня, сверху шкафчик с одной дверцей push-to-open (без ручки),
#   снизу открытая ниша с полотенцами (задняя стенка, LED сверху ниши)
_TB0, _TH = 0.10, CT - 0.12                                 # низ тумбы, верх (под камнем)
_CH0 = 0.42                                                 # низ шкафчика = верх ниши
for (q0, q1) in ((SZ0, SZ0 + 0.018), (SZ1 - 0.018, SZ1)): wb("Тумба боковина", "R", q0, q1, 0, CD, _TB0, _TH, M["ward"], 0.002)
wb("Тумба дно (полка для полотенец)", "R", SZ0 + 0.018, SZ1 - 0.018, 0, CD, _TB0, _TB0 + 0.025, M["ward"], 0.002)
wb("Тумба задняя стенка ниши", "R", SZ0 + 0.018, SZ1 - 0.018, 0, 0.01, _TB0, _CH0, M["ward"])
wb("Шкафчик под раковиной (сифон, краны)", "R", SZ0 + 0.018, SZ1 - 0.018, 0, CD - 0.02, _CH0, _TH, M["ward"])
wb("Фасад push-to-open", "R", SZ0 + 0.020, SZ1 - 0.020, CD - 0.02, CD, _CH0 + 0.002, _TH - 0.003, M["ward"], 0.002)
wb("LED ниши", "R", SZ0 + 0.04, SZ1 - 0.04, 0.05, CD - 0.05, _CH0 - 0.005, _CH0, M["led"])
if OPT.get("decor", "1") == "0":   # 18.11: с декором — две стопки полотенец моделью (decor_common), «как в отеле»
    for k in range(2): wb("Полотенца", "R", SZ0 + 0.06 + k * 0.26, SZ0 + 0.28 + k * 0.26, 0.08, 0.40, 0.125, 0.27, M["towel"], 0.03)
bottles("R", SZ0 + 0.04, 0.08, CT)
mirror_led("R", SZ0 + 0.02, SZ1 - 0.02, 1.25, 2.10)

# ---- стиралка 10 кг 600×600×850 рядом с раковиной, над ней шкаф до потолка (химия, полотенца)
washer_bk("R", 8.25, 8.85)
# 18.11 (заказчик: «над унитазом бак и бойлер — один слева, другой справа, ничего не выпирает, всё в один уровень»):
#   ряд шкафов на правой стене — фасады в одной плоскости (глубина 320, как короб инсталляции), низ на одной высоте 1120
cabinet("Шкаф над стиралкой: порошки, полотенца", "R", 8.22, 8.84, 0.32, 1.12, HC, 2, "laundry")

# ---- ванна 1700×700 вдоль левой стены, к нижней стене; шторка на Г-карнизе; смеситель и лейка на левой стене
BZ0, BX1 = Z1 - 1.70, X0 + 0.70
if OPT.get("tub2", "1") == "1" and os.path.exists(os.path.join(BK, "vanna_pryam.blend")):   # 17.11 (проверка: ванна была коробкой) — модель 1720×726
    bk_fit("vanna_pryam", (X0 + BX1) / 2, (BZ0 + Z1) / 2, 0.0, 90, 1.70)
else:
    tub = box("Ванна", X0, BZ0, BX1, Z1 - 0.003, 0, 0.58, M["acryl"], 0.015)
    cav = box("Чаша", X0 + 0.07, BZ0 + 0.07, BX1 - 0.07, Z1 - 0.07, 0.16, 0.9, M["acryl"])
    md = tub.modifiers.new("cav", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cav; cav.hide_render = True; cav.display_type = "WIRE"
# 18.11 (заказчик: «шторки отвратительные»): вместо штор — СТЕКЛЯННАЯ ШТОРКА на ванну (как перегородка санузла):
#   неподвижное стекло 850×1420 на борту ванны у душа, чёрный профиль, без карниза
GS0 = Z1 - 0.85
box("Стекло на ванну", BX1 - 0.03, GS0, BX1 - 0.022, Z1 - 0.003, 0.58, 2.00, M["glass"])
box("Профиль стекла (стена)", BX1 - 0.034, Z1 - 0.02, BX1 - 0.018, Z1, 0.58, 2.00, M["black"])
box("Профиль стекла (верх)", BX1 - 0.034, GS0, BX1 - 0.018, Z1, 1.99, 2.00, M["black"])
box("Профиль стекла (край)", BX1 - 0.034, GS0, BX1 - 0.018, GS0 + 0.012, 0.58, 2.00, M["black"])
MZ = Z1 - 0.85
box("Смеситель", X0, MZ - 0.10, X0 + 0.05, MZ + 0.10, 0.82, 0.90, M["black"], 0.006)
box("Излив", X0 + 0.05, MZ - 0.02, X0 + 0.20, MZ + 0.02, 0.70, 0.73, M["black"], 0.006)
box("Штанга душа", X0, Z1 - 0.32, X0 + 0.03, Z1 - 0.30, 1.00, 1.90, M["black"])
box("Лейка", X0 + 0.03, Z1 - 0.36, X0 + 0.07, Z1 - 0.26, 1.55, 1.75, M["black"], 0.01)
box("Полочка ниши", X0, BZ0 + 0.25, X0 + 0.10, BZ0 + 0.75, 1.10, 1.12, M["tile"])
box("Ниша LED", X0, BZ0 + 0.25, X0 + 0.005, BZ0 + 0.75, 1.385, 1.39, M["led"])
bottles("L", BZ0 + 0.30, 0.05, 1.12)

# ---- правая стена внизу (у стояка Т2): короб инсталляции, подвесной унитаз + гиг. душ; плоский бойлер Б1 в шкафу над ним
UZ = 9.45
wb("Короб инсталляции", "R", UZ - 0.36, Z1, 0, 0.32, 0, 1.12, M["tile"])
hung("Унитаз", "R", UZ, "wc", d0=0.32)
wb("Гиг. душ смеситель", "R", UZ - 0.30, UZ - 0.24, 0.32, 0.35, 0.66, 0.74, M["black"], 0.005)
wb("Гиг. душ лейка", "R", UZ - 0.295, UZ - 0.245, 0.35, 0.39, 0.80, 0.95, M["black"], 0.01)
# 18.11 (правило «утверждённые модели — везде»): держатель Д1 и ведро М3 как в санузле — на нижней стене сбоку от унитаза, крышкой к унитазу
_HX = X1 - 0.60
_dh = bk_fit("derzhatel_d1", _HX, Z1 - 0.07, 0.66, 0)
for o in _dh:
    if o.type == "MESH":
        for i_ in range(len(o.data.materials)): o.data.materials[i_] = M["black"]
if _dh:
    def _top(o):
        while o.parent is not None: o = o.parent
        return o
    _rt = {_top(o) for o in _dh}
    bpy.context.view_layer.update()
    _P = [o.matrix_world @ Vector(c) for o in _dh if o.type == "MESH" for c in o.bound_box]
    _pv = Vector(tuple((min(p_[i] for p_ in _P) + max(p_[i] for p_ in _P)) / 2 for i in range(3)))
    _R = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Diagonal((1, -1, 1, 1)) @ Matrix.Rotation(math.radians(90), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
    for o in _rt: o.matrix_world = Matrix.Translation(_pv) @ _R @ Matrix.Translation(-_pv) @ o.matrix_world
    bpy.context.view_layer.update()
    _P = [o.matrix_world @ Vector(c) for o in _dh if o.type == "MESH" for c in o.bound_box]
    _d = Vector((_HX - (min(p_.x for p_ in _P) + max(p_.x for p_ in _P)) / 2, (-Z1) - min(p_.y for p_ in _P), 0.70 - (min(p_.z for p_ in _P) + max(p_.z for p_ in _P)) / 2))
    for o in _rt: o.location += _d
_mu = bk_fit("musorka_m3", X1 - 1.00, Z1 - 0.16, 0.0, 0, 0.29, "h")
for o in _mu:
    if o.type == "MESH":
        for i_ in range(len(o.data.materials)): o.data.materials[i_] = M["black"]
cabinet("Шкаф над унитазом слева: бак 200 л + насос", "R", 8.86, 9.355, 0.32, 1.12, HC, 1, "tank_top", led=False)   # плоский бак ~200 л 460×280×1470 (под заказ)
cabinet("Шкаф над унитазом справа: бойлер Б1", "R", 9.36, Z1 - 0.005, 0.32, 1.12, HC, 1, ("flatboiler", (9.36 + Z1) / 2), led=False)

# 18.11 (заказчик: «места для полотенец не вижу»): сушитель 450 + рядом 2 крючка с полотенцами (как в санузле); под раковиной — стопки полотенец
_tr = [o for o in towel_rail_bk("T", 4.93, hc=1.25) if o.type == "MESH"]
if _tr:
    bpy.context.view_layer.update()
    _P = [o.matrix_world @ Vector(c) for o in _tr for c in o.bound_box]
    _k = 0.45 / (max(p_.x for p_ in _P) - min(p_.x for p_ in _P))
    _piv = Vector(((max(p_.x for p_ in _P) + min(p_.x for p_ in _P)) / 2, max(p_.y for p_ in _P), min(p_.z for p_ in _P)))
    _rt = {o for o in _tr if o.parent is None or o.parent not in _tr}
    for o in _rt: o.matrix_world = Matrix.Translation(Vector((_piv.x, _piv.y, 0.95))) @ Matrix.Scale(_k, 4) @ Matrix.Translation(-_piv) @ o.matrix_world
for xx in (5.26, 5.35): wb("Крючок полотенца", "T", xx - 0.008, xx + 0.008, 0, 0.05, 1.69, 1.71, M["black"], 0.003)
spots([(4.25, 7.95), (5.30, 7.95), (4.00, 9.20), (5.20, 9.20)])

exec(open(os.path.join(PROJ, "02_skripty", "decor_common.py"), encoding="utf-8").read())   # 17.11: декор (decor=0 — без него)
CAMS = {"1": ("1_ot_dveri", W(4.20, 7.52, 1.60), W(5.40, 9.60, 0.80), 13),
        "2": ("2_rakovina_stiralka", W(4.30, 8.90, 1.60), W(X1, 8.20, 1.05), 14),
        "3": ("3_vanna", W(5.30, 8.10, 1.60), W(X0 + 0.35, 9.30, 0.70), 13),
        "4": ("4_k_dveri", W(5.10, 9.70, 1.65), W(4.10, 7.44, 1.10), 13)}
CAMS["5"] = ("5_bojler_shkaf", W(4.40, 8.90, 1.60), W(X1, UZ, 1.75), 13)
# 18.11: вертикальные «как с телефона» — каждая стена целиком (пол–потолок) + 4 угла (см. правило kadry-polnye-vertikalnye)
CAMS.update({"v1": ("v1_ot_dveri_na_unitaz", W(4.20, Z0 + 0.06, 1.3), W(4.70, Z1, 1.3), 0),
             "v2": ("v2_shkafy_bak_bojler", W(X0 + 0.75, 9.10, 1.3), W(X1, 9.10, 1.3), 0),
             "v3": ("v3_vanna", W(X1 - 0.70, 8.90, 1.3), W(X0, 8.90, 1.3), 0),
             "v4": ("v4_k_dveri", W(4.70, Z1 - 0.06, 1.3), W(4.20, Z0, 1.3), 0),
             "v5": ("v5_ugol_dver_rakovina", W(X0 + 0.06, Z0 + 0.06, 1.3), W(X1, Z1, 1.3), 0),
             "v6": ("v6_ugol_rakovina", W(X1 - 0.30, Z0 + 0.06, 1.3), W(X0, Z1, 1.3), 0),
             "v7": ("v7_ugol_vanna", W(X0 + 0.80, Z1 - 0.06, 1.3), W(X1, Z0, 1.3), 0),
             "v8": ("v8_ugol_unitaz", W(X1 - 0.80, Z1 - 0.06, 1.3), W(X0, Z0, 1.3), 0),
             "v9": ("v9_rakovina_polotenca", W(X0 + 0.80, 7.75, 1.3), W(X1, 7.75, 1.3), 0),
             "v10": ("v10_unitaz_derzhatel", W(X0 + 0.75, Z0 + 0.70, 1.3), W(X1 - 0.45, Z1, 1.3), 0)})   # 18.11: унитаз, держатель Д1, ведро М3   # 18.11: раковина, полотенца под ней, крючки и сушитель
if OPENC: CAMS = {k: ("open_" + v[0],) + v[1:] for k, v in CAMS.items()}
