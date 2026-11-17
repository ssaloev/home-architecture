# ======================= САНУЗЕЛ — ВАРИАНТ И (утв. 17.11.2026, схема 01_chertezhi/shema_sanuzel_obmer_i.png), по ОБМЕРУ 900×1820
# шахта 385 по всей левой стене (X0 = её грань), стояк Т1 в верхнем конце; выемка 640 в шахте у Т1 — в ней инсталляция + бак 200 л;
# унитаз лицом к стене с дверью; дверь 700 ПЕРЕНЕСЕНА напротив унитаза; душ 900×820 без поддона в дальнем торце за стеклом;
# раковина 450×200, над ней плоский бойлер Б2 в шкафу; насос/фильтры — под раковиной. Прежний вариант — sanuzel_room_v13_11.py
X0, X1, Z0, Z1 = 0.694, 1.836, 6.8, 9.018           # по зафиксированному обмеру (редактор): от грани шахты
H, HC = 2.70, 2.65
DZ0, DZ1, DH = 7.04, 7.74, 2.10                         # дверь 700 в правой стене (x = X1), наружу
OUTDIR = "sanuzel"
#==COMMON==
room_box("R", DZ0, DZ1)
RZ0, RZ1, RD = 7.00, 7.64, 0.385                        # выемка в шахте

# ---- выемка: вырез в левой стене + стенки ниши (плитка)
_cut = box("Вырез выемки", X0 - 0.20, RZ0, X0 + 0.01, RZ1, -0.05, HC, M["tile"])
_wl = bpy.data.objects.get("Стена L")
if _wl and _cut:
    _bm = _wl.modifiers.new("vyemka", "BOOLEAN"); _bm.object = _cut; _bm.operation = "DIFFERENCE"
    bpy.context.view_layer.objects.active = _wl; bpy.ops.object.modifier_apply(modifier="vyemka")
    bpy.data.objects.remove(_cut, do_unlink=True)
box("Выемка задник", X0 - RD - 0.05, RZ0 - 0.05, X0 - RD, RZ1 + 0.05, 0, H, M["tile"])
box("Выемка бок", X0 - RD, RZ0 - 0.05, X0 - 0.002, RZ0, 0, H, M["tile"]); box("Выемка бок", X0 - RD, RZ1, X0 - 0.002, RZ1 + 0.05, 0, H, M["tile"])   # 17.11: не доходят до лица стены — иначе наложение с плиткой (тёмные полосы у шкафа)
box("Выемка пол", X0 - RD, RZ0, X0, RZ1, -0.05, 0, M["tilef"]); box("Выемка потолок", X0 - RD, RZ0, X0, RZ1, HC, HC + 0.05, M["ceil"])

# ---- инсталляция (короб в выемке до 1120) + унитаз лицом к двери
box("Короб инсталляции", X0 - RD, RZ0, X0, RZ1, 0, 1.12, M["tile"])          # 17.11 (заказчик: «унитаз уходит в мебель — выдвинуть»): короб на всю глубину выемки
hung("Унитаз", "L", (RZ0 + RZ1) / 2, "wc", d0=0.0)                       # унитаз висит на коробе заподлицо со стеной шахты, не в выемке
# ---- 17.11 (заказчик): бак 200 л — в БОЛЬШОЙ ванной (шкаф над стиралкой); в выемке над унитазом — БОЙЛЕР Б2,
#      закрыт фасадом В ЦВЕТ ПЛИТКИ (без белого шкафа, стена цельная), 2 створки, скрытые ручки-профиль
M["fasad_pl"] = M["tile"]
# 17.11 (заказчик: «двери распашные — верно; внизу маленький шкафчик под туалетную бумагу»):
#   выемка над коробом инсталляции: ВЕРХНИЙ шкаф — бойлер (HB0..потолок), НИЖНИЙ маленький шкафчик — бумага (1,125..HB0);
#   фасады накладные (перекрывают края выемки), распашные по 2 створки, цвет шкафов квартиры, ручки чёрные стандартные
HB0 = 1.43
# 17.11 (заказчик: «шкаф кажется белый, а не серый, как у нас в мебели»): фасады санузла — серо-белые, как мебель квартиры на кадрах
M["ward"] = mat("Фасады серо-белые", "#C9C9C5", 0.5)
box("Полка-разделитель", X0 - RD, RZ0, X0, RZ1, HB0 - 0.018, HB0, M["ward"], 0.002)
# кнопка смыва — на коробе инсталляции над унитазом, чёрная (вся фурнитура чёрная)
box("Кнопка смыва", X0, (RZ0 + RZ1) / 2 - 0.12, X0 + 0.008, (RZ0 + RZ1) / 2 + 0.12, 0.90, 1.06, M["black"], 0.003)
for _zz in ((RZ0 + RZ1) / 2 - 0.055, (RZ0 + RZ1) / 2 + 0.055): box("Клавиша смыва", X0 + 0.008, _zz - 0.05, X0 + 0.011, _zz + 0.05, 0.93, 1.03, M["black"], 0.002)
_ZM = (RZ0 + RZ1) / 2
_SECT = ((1.125, HC - 0.003, "бойлер и бумага"),)   # 17.11 (заказчик): всего 2 распашные двери на всю высоту; внутри — полка, снизу секция под бумагу
if OPENC:
    wb("Бойлер плоский", "L", _ZM - 0.235, _ZM + 0.235, -RD + 0.02, -RD + 0.305, 1.47, 2.325, M["boilerg"], 0.06)
    for _k in range(2):   # рулоны бумаги в нижнем шкафчике
        for _j in range(3):
            _o = _cyl(X0 - RD + 0.08 + _k * 0.13, RZ0 + 0.10 + _j * 0.15, 0.055, 1.125, 1.225, M["white"], 32); _o.name = "Рулон бумаги"
    for (h0_, h1_, _n) in _SECT:
        for k, (p0, p1) in enumerate(((RZ0 + 0.003, _ZM - 0.0015), (_ZM + 0.0015, RZ1 - 0.003))):
            _door_open("L", p0, p1, 0.0, h0_, h1_, k == 0)
else:
    for (h0_, h1_, _n) in _SECT:
        for k, (p0, p1) in enumerate(((RZ0 + 0.003, _ZM - 0.0015), (_ZM + 0.0015, RZ1 - 0.003))):
            q0 = p0 - (0.018 if k == 0 else 0.0); q1 = p1 + (0.018 if k == 1 else 0.0)
            box("Фасад шкафа " + _n, X0, q0, X0 + 0.018, q1, h0_, h1_, M["ward"], 0.002)
            ah = q1 - 0.05 if k == 0 else q0 + 0.05
            _hh = (h0_ + 0.05, h0_ + 0.45)   # ручки внизу двери — удобно с пола
            box("Ручка", X0 + 0.018, ah - 0.006, X0 + 0.034, ah + 0.006, _hh[0], _hh[1], M["black"], 0.002)
# ---- раковина 450×200 в углу у двери (верхняя стена); под ней шкафчик (фильтры) и полка с полотенцами; над ней зеркало
CT = 0.85; SA0, SA1 = X1 - 0.45, X1 - 0.005
# 17.11 (заказчик: «все модели раковин не те — под наши размеры»): ИНТЕГРИРОВАННАЯ раковина в столешнице из белого
#   искусственного камня 450×200×120, чаша 300×130 гл. 95 со скруглениями R35 (смещена влево); смеситель С2 на столешнице справа
M["kamen"] = mat("Искусственный камень белый", "#E9E7E2", 0.28)
_SX = (SA0 + SA1) / 2
_slab = wb("Столешница с раковиной", "T", SA0, SA1, 0, 0.20, CT - 0.12, CT, M["kamen"])
_BX = SA0 + 0.03 + 0.15                                  # центр чаши (чаша 300, слева бортик 30, справа 115 — под смеситель)
bpy.ops.mesh.primitive_cube_add(location=W(_BX, Z0 + 0.105, CT + 0.005)); _cut = bpy.context.active_object
_cut.scale = (0.15, 0.065, 0.10); bpy.ops.object.transform_apply(scale=True)
_cb = _cut.modifiers.new("r", "BEVEL"); _cb.width = 0.035; _cb.segments = 10
bpy.context.view_layer.objects.active = _cut; bpy.ops.object.modifier_apply(modifier="r")
_bo = _slab.modifiers.new("chasha", "BOOLEAN"); _bo.object = _cut; _bo.operation = "DIFFERENCE"
bpy.context.view_layer.objects.active = _slab; bpy.ops.object.modifier_apply(modifier="chasha")
bpy.data.objects.remove(_cut, do_unlink=True)
_eb = _slab.modifiers.new("kromka", "BEVEL"); _eb.width = 0.004; _eb.segments = 3; _eb.limit_method = "ANGLE"
for _p in _slab.data.polygons: _p.use_smooth = True
_cyl(_BX, Z0 + 0.105, 0.019, CT - 0.096, CT - 0.093, M["black"], 32).name = "Донный клапан"
# смеситель С2 (выбор заказчика 17.11): высокий чёрный, стоит на столешнице СПРАВА от чаши, излив повёрнут вдоль стены в чашу
_fo = bk_fit("smesitel_c2", 0, 0, 0, 0)
_fm = [o for o in _fo if o.type == "MESH"]
if _fm:
    bpy.context.view_layer.update()
    _V = [o.matrix_world @ v.co for o in _fm for v in o.data.vertices]
    _zmin = min(v.z for v in _V); _base = [v for v in _V if v.z < _zmin + 0.02]
    _sx = sum(v.x for v in _base) / len(_base); _sy = sum(v.y for v in _base) / len(_base)
    _cx = (min(v.x for v in _V) + max(v.x for v in _V)) / 2; _cy = (min(v.y for v in _V) + max(v.y for v in _V)) / 2
    _ang = math.atan2(_cy - _sy, _cx - _sx)                  # направление излива от стойки
    _rt = {o for o in _fo if o.parent is None or o.parent not in _fo}
    _R = Matrix.Rotation(math.pi - _ang, 4, "Z")              # излив → -X (влево вдоль верхней стены, к чаше)
    _tgt = W(SA1 - 0.055, Z0 + 0.10, CT)
    for o in _rt: o.matrix_world = Matrix.Translation(_tgt) @ _R @ Matrix.Translation(Vector((-_sx, -_sy, -_zmin))) @ o.matrix_world
    for o in _fm:
        for i_ in range(len(o.data.materials)): o.data.materials[i_] = M["black"]
# 17.11 (заказчик: «шкафчик внизу, где оборудование, и ниже полотенца как в отелях»):
#   под столешницей — закрытый шкафчик 1 дверца (за ним фильтры/насос/краны), ниже — открытая полка со скрученными полотенцами
M["towel_w"] = mat("Полотенце белое", "#E9E7E2", 1.0)
cabinet("Шкафчик под раковиной (фильтры, насос)", "T", SA0 + 0.005, SA1, 0.20, 0.36, CT - 0.125, doors=1, content=None, led=True)
wb("Полка для полотенец", "T", SA0 + 0.005, SA1, 0, 0.20, 0.10, 0.125, M["ward"], 0.002)
def _roll(a, h, r=0.052, L=0.17):
    x, z = pt("T", a, 0.015 + L / 2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=L, location=W(x, z, h + r), rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object; o.name = "Полотенце рулон"; o.data.materials.append(M["towel_w"])
    bv = o.modifiers.new("bev", "BEVEL"); bv.width = 0.012; bv.segments = 3
if OPT.get("decor", "1") == "0":   # без декора — простые рулоны; с декором — модель стопки полотенец (decor_common)
    for k in range(3): _roll(SA0 + 0.075 + k * 0.11, 0.125)
# полотенцесушитель — верхняя стена левее раковины (над унитазом не мешает: унитаз на левой стене), розетка №48 рядом скрытая
_tr = [o for o in towel_rail_bk("T", 0.94, hc=1.25) if o.type == "MESH"]   # 17.11 (заказчик: «уменьши»): привести к 450 шириной, низ на 800
if _tr:
    bpy.context.view_layer.update()
    _P = [o.matrix_world @ Vector(c) for o in _tr for c in o.bound_box]
    _w = max(p_.x for p_ in _P) - min(p_.x for p_ in _P); _k = 0.45 / _w
    _piv = Vector(((max(p_.x for p_ in _P) + min(p_.x for p_ in _P)) / 2, max(p_.y for p_ in _P), min(p_.z for p_ in _P)))
    _rt = {o for o in _tr if o.parent is None or o.parent not in _tr}
    for o in _rt: o.matrix_world = Matrix.Translation(Vector((_piv.x, _piv.y, 1.05))) @ Matrix.Scale(_k, 4) @ Matrix.Translation(-_piv) @ o.matrix_world   # 17.11 («сушитель и полотенца слишком близко к унитазу»): низ 1050
    print("Сушитель: было", round(_w, 3), "м, масштаб", round(_k, 3))
# 17.11 (заказчик: «сушитель и вешалка для полотенец — в одном месте рядом»): справа от сушителя 2 крючка для полотенец, h 1550
for xx in (1.24, 1.33): wb("Крючок полотенца", "T", xx - 0.008, xx + 0.008, 0, 0.05, 1.74, 1.76, M["black"], 0.003)   # 17.11: выше, полотенца над уровнем унитаза
# 17.11 (выбор заказчика Д1, место — по разметке заказчика): на стене шахты справа от выемки, h ≈ 700; чёрный. Поворачиваем ТОЛЬКО верхних предков иерархии (иначе части крутились дважды — «криво»)
_HX = 1.02                                                # 17.11 (рисунок заказчика): боковая (верхняя) стена рядом с унитазом, над ведром, крышка сверху
_dh = bk_fit("derzhatel_d1", _HX, Z0 + 0.07, 0.66, 0)
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
    _pv = Vector(((min(p_.x for p_ in _P) + max(p_.x for p_ in _P)) / 2, (min(p_.y for p_ in _P) + max(p_.y for p_ in _P)) / 2, (min(p_.z for p_ in _P) + max(p_.z for p_ in _P)) / 2))
    _R = Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Diagonal((1, -1, 1, 1)) @ Matrix.Rotation(math.radians(90), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")   # 17.11 (заказчик: «-90 обратно — крышкой в сторону унитаза»)
    for o in _rt: o.matrix_world = Matrix.Translation(_pv) @ _R @ Matrix.Translation(-_pv) @ o.matrix_world
    bpy.context.view_layer.update()
    _P = [o.matrix_world @ Vector(c) for o in _dh if o.type == "MESH" for c in o.bound_box]
    _d = Vector((_HX - (min(p_.x for p_ in _P) + max(p_.x for p_ in _P)) / 2, (-Z0) - max(p_.y for p_ in _P), 0.70 - (min(p_.z for p_ in _P) + max(p_.z for p_ in _P)) / 2))
    for o in _rt: o.location += _d
    print("Держатель габарит", [round(max(p_[i] for p_ in _P) - min(p_[i] for p_ in _P), 3) for i in range(3)])
# 17.11 (выбор заказчика М3): мусорное ведро с педалью, чёрное матовое, на полу справа от унитаза под полотенцесушителем
_mu = bk_fit("musorka_m3", 0.90, Z0 + 0.15, 0.0, 0, 0.29, "h")
for o in _mu:
    if o.type == "MESH":
        for i_, ms in enumerate(o.data.materials): o.data.materials[i_] = M["black"]
# крючки для одежды — правая стена между углом и дверью (24 см), 2 шт., h 1650
for zz in (6.87, 6.97): wb("Крючок", "R", zz - 0.008, zz + 0.008, 0, 0.05, 1.64, 1.66, M["black"], 0.003)
mirror_led("T", SA0 + 0.03, SA1 - 0.03, 1.20, 1.90)   # 17.11: бойлер Б2 перенесён в выемку над унитазом — над раковиной зеркало

# ---- душ 900×820 в дальнем торце: стекло (неподвижное 450 + дверь 450), трап-лоток вдоль левой стены под лейкой, душевой комплект на стене шахты
GZ = 7.80
box("Порожек душа", X0, GZ - 0.01, X1, GZ + 0.01, 0, 0.012, M["tile"])
box("Стекло душа", X0, GZ - 0.004, X0 + 0.45, GZ + 0.004, 0.012, 2.00, M["glass"])
box("Дверь душа", X0 + 0.46, GZ - 0.004, X1 - 0.01, GZ + 0.004, 0.012, 2.00, M["glass"])
for xx in (X0 + 0.45, X1 - 0.01): box("Профиль", xx - 0.006, GZ - 0.012, xx + 0.006, GZ + 0.012, 0.012, 2.00, M["black"])
box("Профиль верх", X0, GZ - 0.012, X1, GZ + 0.012, 1.99, 2.01, M["black"])
box("Трап-лоток", X0 + 0.06, GZ + 0.12, X0 + 0.10, Z1 - 0.08, 0.0, 0.003, M["black"])   # 17.11 (разметка заказчика на виде сверху): трап вдоль ЛЕВОЙ стены под лейкой, у нижней — нет
bk_load("dush_komplekt_cherny", Matrix.Translation(W(X0, Z1 - 0.40, 0.95)) @ Matrix.Rotation(math.radians(90), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X"))
spots([((X0 + X1) / 2, 7.30), ((X0 + X1) / 2, Z1 - 0.40)])
# ---- 17.11 (эскиз заказчика): 3 ниши под шампунь НАПРОТИВ лейки — в правой стене душа (не под струёй), 400×250, глубина 100;
#      стена 109 → задник ниши выступает ~5 см в шкаф хозяев прихожей (сзади, снаружи не видно); LED сверху
NZ0, NZ1, ND = 8.20, 8.60, 0.10
NICHES = [(0.95, 1.20), (1.30, 1.55), (1.65, 1.90)]
for n0, n1 in NICHES:
    _c = box("Вырез ниши душа", X1 - 0.01, NZ0, X1 + ND, NZ1, n0, n1, M["tile"])
    for _wl in [o for o in bpy.data.objects if o.name.startswith("Стена") and o.type == "MESH"]:
        _bb = [_wl.matrix_world @ Vector(c_) for c_ in _wl.bound_box]
        if min(v.x for v in _bb) > X1 - 0.02 and max(-v.y for v in _bb) > NZ0 and min(-v.y for v in _bb) < NZ1 and max(v.z for v in _bb) > n1:
            _bm = _wl.modifiers.new("nisha", "BOOLEAN"); _bm.object = _c; _bm.operation = "DIFFERENCE"
            bpy.context.view_layer.objects.active = _wl; bpy.ops.object.modifier_apply(modifier="nisha")
    bpy.data.objects.remove(_c, do_unlink=True)
    box("Ниша задник", X1 + ND, NZ0, X1 + ND + 0.02, NZ1, n0, n1, M["tile"])
    box("Ниша дно", X1, NZ0, X1 + ND, NZ1, n0 - 0.02, n0, M["tile"]); box("Ниша верх", X1, NZ0, X1 + ND, NZ1, n1, n1 + 0.02, M["tile"])
    box("Ниша бок", X1, NZ0 - 0.02, X1 + ND, NZ0, n0, n1, M["tile"]); box("Ниша бок", X1, NZ1, X1 + ND, NZ1 + 0.02, n0, n1, M["tile"])
    box("LED ниши", X1 + 0.01, NZ0 + 0.02, X1 + ND - 0.01, NZ1 - 0.02, n1 - 0.004, n1, M["led"])

exec(open(os.path.join(PROJ, "02_skripty", "decor_common.py"), encoding="utf-8").read())   # 17.11: декор (decor=0 — без него)
CAMS = {"1": ("1_ot_dveri", W(X1 - 0.10, Z1 - 0.10, 1.55), W(X0 + 0.05, 7.25, 0.75), 15),
        "2": ("2_k_dushu", W(X1 - 0.15, 7.30, 1.65), W(X0 + 0.30, Z1 - 0.10, 0.95), 13),
        "3": ("3_iz_dusha", W(X0 + 0.55, Z1 - 0.08, 1.60), W(X1 - 0.20, 6.90, 1.20), 13),
        "4": ("4_rakovina", W(X0 + 0.22, 7.76, 1.25), W(X1 - 0.25, Z0, 0.55), 17),
        "5": ("5_sushitel_rakovina", W((X0 + X1) / 2, 7.76, 1.30), W(1.10, Z0, 1.00), 17),
        # 17.11: вертикальные «как с телефона» — каждая стена целиком, пол и потолок
        "v1": ("v1_dush", W((X0 + X1) / 2, Z0 + 0.06, 1.3), W((X0 + X1) / 2, Z1, 1.3), 24),
        "v2": ("v2_rakovina_sushitel", W((X0 + X1) / 2, Z1 - 0.06, 1.3), W((X0 + X1) / 2, Z0, 1.3), 24),
        "v3": ("v3_unitaz", W(X1 - 0.03, 7.32, 1.3), W(X0, 7.32, 1.3), 14),
        "v4": ("v4_nishi", W(X0 + 0.06, 8.40, 1.3), W(X1, 8.40, 1.3), 14),
        # 17.11 (заказчик: «со всех сторон и углов»): диагонали из 4 углов, пол–потолок
        "v5": ("v5_ugol_dver", W(X1 - 0.06, Z0 + 0.06, 1.3), W(X0, Z1, 1.3), 14),
        "v6": ("v6_ugol_dush_dver", W(X1 - 0.06, Z1 - 0.06, 1.3), W(X0, Z0, 1.3), 14),
        "v7": ("v7_ugol_shahta", W(X0 + 0.06, Z1 - 0.06, 1.3), W(X1, Z0, 1.3), 14),
        "v8": ("v8_ugol_sushitel", W(X0 + 0.40, Z0 + 0.06, 1.3), W(X1, Z1, 1.3), 14)}   # 17.11: сушитель + крючки + раковина   # 17.11: раковина, шкафчик, полотенца, сушитель, крючки
if OPENC: CAMS = {k: ("open_" + v[0],) + v[1:] for k, v in CAMS.items()}
