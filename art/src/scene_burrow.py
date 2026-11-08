"""Full-page plate: cutaway of a hillside burrow-home (style study, high-detail version).

Exterior hill face with the round door on the left; the rest of the hill and the ground
beneath cut away to show three levels of rooms, stores and cellars threaded with roots.
7.125 x 10.25in (7x10 page + bleed).  Painted with the watercolour engine (wc.py).
"""
import math
from kit import PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, arch_pts, line_pts, lerp, inside
from wc import Canvas as Doc
import objects as O
import detail as D


def build(path):
    W, H = 712.5, 1025
    d = Doc(7.125, 10.25, seed=7)

    # ------------------------------------------------------------- sky & distance
    d.wash_gradient([(-10, -10), (W + 10, -10), (W + 10, 520), (-10, 520)],
                    [(0, "#a9c6d6"), (0.5, "#d6e3e0"), (1, "#f3ead2")], 0, 0, 0, 520, op=0.7, soft=True)
    for cx, cy, w_, h_ in ((120, 120, 150, 34), (620, 200, 110, 26), (330, 50, 90, 20)):
        for k in range(7):
            d.wash(blob(cx + d.r(w_ / 2), cy + d.r(h_ / 3), d.u(h_ * 0.6, h_ * 1.0) * 1.4, d.u(h_ * 0.45, h_ * 0.8), d.rng, 0.15, 14),
                   "#fffdf6", 0.8, soft=True)
        d.wash(ellipse_pts(cx, cy + h_ * 0.35, w_ * 0.5, h_ * 0.22, 20), "#b9c4cc", 0.25, soft=True)
    far = [(-20, 420), (-20, 318), (50, 296), (120, 288), (200, 300), (260, 318), (270, 420)]
    d.wash(far, "#a9b8c3", 0.55, soft=True)
    far2 = [(-20, 420), (-20, 345), (60, 332), (150, 328), (240, 342), (260, 420)]
    d.wash(far2, "#b5c49b", 0.7, shade=0.2)
    for tx in range(10, 250, 18):
        D.leafy_mass(d, tx, 334 - 4 * math.sin(tx / 30), 9, 6, clumps=3, leaves=10, leaf_len=(2, 3), ink_frac=0.0)
    for bx, by in ((80, 200), (98, 190), (122, 204)):
        d.ink([(bx - 5, by), (bx - 2, by - 3), (bx, by), (bx + 2, by - 3), (bx + 5, by)], 0.7, INK_SOFT)

    # ------------------------------------------------------------------ the hill
    surface = [(-15, 445), (60, 410), (140, 372), (220, 338), (300, 304), (380, 280), (460, 263), (540, 257),
               (620, 266), (690, 283), (730, 293)]

    def surf_y(x):
        for (x1, y1), (x2, y2) in zip(surface, surface[1:]):
            if x1 <= x <= x2:
                return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        return surface[0][1] if x < surface[0][0] else surface[-1][1]

    earth = surface + [(730, 1040), (-15, 1040)]
    d.wash(earth, "#d3b07e", 0.9, jitter=0, shade=0.15, cover=0.95)
    for k, sy in enumerate((330, 420, 560, 700, 830, 960)):
        top = [(x, sy + 12 * math.sin(x / 80 + k) + d.r(3)) for x in range(-20, 760, 40)]
        D.stratum(d, top, d.u(30, 60), d.choice(["#c49a68", "#d9bb8a", "#b88d5e", "#cfa676"]), 0.3)
    O.mottle(d, earth, ["#b88d5e", "#e0c597", "#a87f55"], n=50, rmin=20, rmax=60, op=0.18)

    cut_x = 252
    main_top, main_floor = 452, 615
    low_top, low_floor = 676, 806
    cel_top, cel_floor = 866, 975

    # chimney flue through the earth
    O.stone_wall(d, 612, 262, 26, main_top - 262 + 30, course=10, colors=["#c98f6a", "#b67a58", "#d7a27c"], mortar="#9b7a5c")
    avoid = [rect_pts(cut_x - 6, main_top - 18, 440, main_floor - main_top + 30),
             rect_pts(260, low_top - 12, 430, low_floor - low_top + 25),
             rect_pts(40, cel_top - 12, 650, cel_floor - cel_top + 25),
             rect_pts(606, 250, 38, 220)]
    for ang, L, w in ((1.9, 190, 8), (1.2, 210, 8), (2.3, 160, 5), (0.8, 200, 5), (1.55, 150, 6), (2.55, 120, 3.5),
                      (0.55, 150, 3.5), (1.7, 120, 3), (1.35, 110, 3)):
        O.root(d, 440 + d.r(12), 276, ang, L, w, depth=3, color="#9a7552", avoid=avoid, ymin=surf_y)
    O.root(d, 690, 300, 1.75, 300, 4, 3, color="#9a7552", avoid=avoid, ymin=surf_y)
    O.root(d, 300, 330, 1.95, 140, 3, 2, color="#9a7552", avoid=avoid, ymin=surf_y)
    # grass roots all along the cut surface
    for x in range(256, 730, 7):
        O.root(d, x + d.r(2), surf_y(x) + 14, 1.57 + d.r(0.35), d.u(10, 26), 1.0, 1, color="#a7865e", ymin=surf_y)

    region = [(255, 300), (730, 270), (730, 1040), (-15, 1040), (-15, 660), (255, 660)]
    D.shaded_pebbles(d, region, 170, 1.8, 7)
    O.soil_texture(d, region, 700, "#8f6a46")

    # ================================================= main level: hall + parlour
    D.plaster_room(d, cut_x, main_top + 14, 156, main_floor, 34, label="the Hall", floor_kind="flags")
    D.plaster_room(d, 418, main_top, 266, main_floor, 52, label="the Parlour", floor_kind="boards")
    d.wash(rect_pts(404, 520, 18, main_floor - 520), "#e9d4a8", 0.95, cover=0.95)
    d.shape(arch_pts(401, 511, 24, main_floor - 511, 12), "#a8784a", 0.9, w=0.8)
    d.shape(arch_pts(405, 517, 16, main_floor - 520, 8), "#f1dfba", 0.95, w=0.6)

    # hall
    D.coat_pegs(d, cut_x + 12, 526, 126)
    D.lantern_lit(d, 372, main_top + 24, 0.85)
    D.rag_rug(d, 330, main_floor - 8, 92, 4)
    stand = [(261, main_floor - 8), (262, main_floor - 34), (276, main_floor - 34), (277, main_floor - 8)]
    d.shape(stand, "#8f9a7e", 0.9, w=0.7, shade=0.6)
    for k, (sx, top_) in enumerate(((265, 58), (270, 64), (274, 52))):
        d.ink([(sx, main_floor - 34), (sx - 1 + k, main_floor - top_)], 1.3, d.choice(["#6e4a2c", "#3d3d3d", "#8a5f3a"]))
    d.ink(ellipse_pts(267.5, main_floor - 64, 3.2, 3.2, 8, a0=math.pi * 1.9, a1=math.pi * 3.0), 1.3, "#6e4a2c")
    for bx in (358, 371):
        d.shape([(bx, main_floor - 8), (bx, main_floor - 23), (bx + 7, main_floor - 23), (bx + 7, main_floor - 12),
                 (bx + 12, main_floor - 10), (bx + 12, main_floor - 8)], "#6a4a32", 0.92, w=0.6, smooth_=False, shade=0.6)
    chest = rect_pts(294, main_floor - 26, 36, 18)
    d.shape(chest, "#a8784a", 0.9, w=0.8, smooth_=False, shade=0.6)
    d.line(294, main_floor - 19, 330, main_floor - 19, 0.9, "#c9a03a", 0)
    d.dot(312, main_floor - 15, 1.2, "#c9a03a")
    d.shape(rect_pts(300, main_floor - 31, 24, 5, 6), "#f1e3c2", 0.95, w=0.5, smooth_=False)
    d.ink([(303, main_floor - 29), (320, main_floor - 29)], 0.35, "#9a6a4a", op=0.8)
    # barometer
    d.shape(ellipse_pts(355, 496, 7, 7, 18), "#a8784a", 0.92, w=0.6)
    d.shape(ellipse_pts(355, 496, 5, 5, 16), "#fbf4e2", 0.95, w=0.4)
    d.line(355, 496, 358, 493, 0.5, INK, 0)

    # parlour
    O.bookcase(d, 428, main_floor - 8, 36, 112, shelves=5)
    D.tea_table(d, 488, main_floor - 8, 38, 26)
    D.rag_rug(d, 560, main_floor - 8, 112, 5)
    D.wing_chair(d, 553, main_floor - 8, 1.22)
    # knitting basket and footstool
    O.basket(d, 585, main_floor - 8, 14, 8, "#7f9cb5")
    d.ink([(583, main_floor - 17), (590, main_floor - 28)], 0.6, "#c9b28d")
    d.ink([(586, main_floor - 17), (580, main_floor - 27)], 0.6, "#c9b28d")
    D.inglenook(d, 645, main_floor - 8, 62, 80)
    # pictures, mirror, sampler, clock
    d.shape(rect_pts(472, 500, 34, 26, 10), "#c9a03a", 0.9, w=0.7, smooth_=False)
    d.wash(rect_pts(476, 504, 26, 18, 10), "#bcd3dc", 0.9, smooth_=False)
    d.wash([(476, 522), (484, 514), (492, 518), (502, 510), (502, 522)], "#93b062", 0.9)
    d.dot(496, 509, 1.2, "#f0c53a")
    d.shape(ellipse_pts(530, 520, 11, 11, 24), "#c9a03a", 0.9, w=0.7)
    d.shape(ellipse_pts(530, 520, 8.2, 8.2, 22), "#dbe6e6", 0.9, w=0.4)
    d.ink(ellipse_pts(527, 516, 3.6, 2.2, 8, a0=3.4, a1=4.6), 0.9, "#ffffff", op=0.9)
    sam = rect_pts(572, 506, 22, 18, 8)
    d.shape(sam, "#f3ead6", 0.95, w=0.6, smooth_=False)
    d.ink(rect_pts(574, 508, 18, 14, 8), 0.4, "#8a5f3a", True, smooth_=False)
    for k in range(3):
        d.ink([(577, 511 + k * 4), (589, 511 + k * 4)], 0.5, d.choice(["#c96a5a", "#5d7fb0", "#7f9c4d"]), dash="1 0.8")
    D.lantern_lit(d, 610, main_top + 14, 0.75, hang=12)
    # chimney pot & smoke
    d.shape(rect_pts(611, 230, 28, 36, 10), "#b9704e", 0.92, w=0.9, smooth_=False, shade=0.6)
    d.shape(rect_pts(607, 224, 36, 8, 10), "#a35f42", 0.95, w=0.8, smooth_=False)
    O.smoke(d, 625, 214, 150, 12)

    # stair passage hall -> kitchen
    stair = [(cut_x + 4, main_floor - 2), (cut_x + 46, main_floor - 2), (300, low_floor), (cut_x + 4, low_floor)]
    d.wash(stair, "#8f6a46", 0.8)
    d.wash([(cut_x + 8, main_floor), (cut_x + 42, main_floor), (296, low_floor - 2), (cut_x + 8, low_floor - 2)], "#ead3a6", 0.95, cover=0.95)
    for i in range(10):
        sy = main_floor + 4 + i * 18.5
        d.shape(rect_pts(cut_x + 8, sy, 40 - i * 0.6, 6, 10), "#c9b79a", 0.9, w=0.6, smooth_=False, shade=0.5)
    d.ink(stair, 1.0, INK, closed=True, smooth_=False)
    D.lantern_lit(d, cut_x + 30, main_floor + 70, 0.6, hang=0)

    # ================================================= lower level: kitchen + pantry
    D.plaster_room(d, 300, low_top, 186, low_floor, 30, label="the Kitchen", floor_kind="flags")
    D.plaster_room(d, 500, low_top, 186, low_floor, 30, label="the Pantry", panel=False, floor_kind="flags")
    d.shape(arch_pts(484, 712, 20, low_floor - 712, 10), "#a8784a", 0.9, w=0.8)
    d.shape(arch_pts(488, 718, 12, low_floor - 720, 6), "#f1dfba", 0.95, w=0.6)
    D.kitchen_range(d, 340, low_floor - 8, 54, 42)
    D.hanging_pans(d, 306, 714, 74)
    D.plate_dresser(d, 388, low_floor - 8, 48, 86)
    # kitchen table with bread, bowl and a jug of flowers
    d.shape(rect_pts(446, low_floor - 34, 34, 4, 10), "#b98a5a", 0.92, w=0.6, smooth_=False, shade=0.5)
    for lx in (449, 475):
        d.shape(rect_pts(lx, low_floor - 30, 2.4, 22), "#8a5f3a", 0.92, w=0.4, smooth_=False)
    d.shape(blob(455, low_floor - 38, 8, 4.5, d.rng, 0.1, 12), "#d39a55", 0.92, w=0.6, shade=0.7)
    for k in range(3):
        d.ink([(450 + k * 4, low_floor - 39), (452 + k * 4, low_floor - 42)], 0.4, INK_SOFT)
    d.shape([(466, low_floor - 34), (465, low_floor - 40), (477, low_floor - 40), (476, low_floor - 34)], "#e8dcc0", 0.92, w=0.5)
    D.jug(d, 474, low_floor - 34, 0.5)
    for k in range(4):
        D.wildflower(d, 473 + k * 1.2, low_floor - 41, d.choice(["daisy", "forgetmenot", "campion"]), 0.6)
    D.herb_bunch(d, 452, low_top + 18)
    D.herb_bunch(d, 466, low_top + 22)
    O.onion_string(d, 438, low_top + 26, 5, 0.85)
    O.basket(d, 432, low_floor - 8, 16, 9, "#9eb04a")
    d.ink([(482, low_floor - 8), (480, low_floor - 50)], 1.1, "#a07a4a")
    for k in range(7):
        d.ink([(480, low_floor - 18), (476 + k * 1.5, low_floor - 8)], 0.5, "#c9a86a")

    # pantry
    D.preserves_shelf(d, 508, 728, 104, 14)
    D.preserves_shelf(d, 508, 752, 104, 12)
    O.shelf(d, 508, 778, 104)
    for cx in (520, 542, 566):
        O.cheese(d, cx, 778, 8.5)
    for k in range(5):
        d.shape(ellipse_pts(588 + k * 3.6, 774 - (k % 2) * 3, 2.2, 2.8, 10), "#f1e6cf", 0.95, w=0.4)
    d.shape([(584, 778), (583, 772), (606, 772), (605, 778)], "#8a6440", 0.9, w=0.5, smooth_=False)
    O.ham(d, 630, low_top + 14, 0.95)
    O.ham(d, 652, low_top + 18, 0.8)
    O.onion_string(d, 672, low_top + 20, 4, 0.8)
    D.herb_bunch(d, 616, low_top + 16, 0.9)
    D.potato_sack(d, 622, low_floor - 8, 25, 28, "FLOUR", "#f3ead6")
    D.potato_sack(d, 650, low_floor - 8, 22, 23, "OATS", "#d8c394")
    O.basket(d, 596, low_floor - 8, 20, 10)
    O.jar(d, 678, low_floor - 8, 14, kind="crock")

    # steps pantry -> cellar
    st2 = [(640, low_floor - 2), (684, low_floor - 2), (684, cel_floor), (600, cel_floor)]
    d.wash(st2, "#8f6a46", 0.8)
    d.wash([(644, low_floor), (680, low_floor), (680, cel_floor - 2), (606, cel_floor - 2)], "#e6cd9c", 0.95, cover=0.95)
    for i in range(9):
        sy = low_floor + 6 + i * 18.5
        d.shape(rect_pts(644 - i * 4.4, sy, 36, 6, 10), "#c9b79a", 0.9, w=0.6, smooth_=False, shade=0.5)
    d.ink(st2, 1.0, INK, closed=True, smooth_=False)

    # ================================================= cellar
    D.plaster_room(d, 48, cel_top, 556, cel_floor, 36, wall="#e8d3a6", panel=False, label="the Cellar", floor_kind="flags")
    O.stone_wall(d, 50, cel_floor - 46, 30, 38, course=9)
    D.barrel_stack(d, 106, cel_floor - 8, cols=5, rows=2, r=13)
    O.wine_rack(d, 252, cel_floor - 8, 52, 70, 5.0)
    D.apple_rack(d, 322, cel_floor - 8, 72, 3)
    for bx in (436, 465, 494):
        O.barrel_side(d, bx, cel_floor - 8, 25, 37)
    O.candle(d, 465, cel_floor - 45, 10)
    D.potato_sack(d, 528, cel_floor - 8, 25, 27, "POTATOES")
    O.basket(d, 556, cel_floor - 8, 20, 11, "#c9a25a")
    for r_ in range(3):
        for c_ in range(4 - r_):
            cx, cy = 572 + c_ * 9 + r_ * 4.5, cel_floor - 13 - r_ * 8
            d.shape(ellipse_pts(cx, cy, 4.5, 4.1, 12), "#c79a5f", 0.95, w=0.5, shade=0.5)
            d.ink(ellipse_pts(cx, cy, 2, 1.8, 8), 0.35, INK_SOFT, True)
    # cobweb in the corner, and the hidden snail on a barrel
    wx, wy = 62, cel_top + 30
    for k in range(7):
        a = math.pi * (0.0 + k / 12)
        d.line(wx, wy, wx + 38 * math.cos(a), wy + 38 * math.sin(a), 0.3, INK_SOFT, 0.2, op=0.6)
    for r_ in (12, 22, 32):
        d.ink([(wx + r_ * math.cos(math.pi * k / 12), wy + r_ * math.sin(math.pi * k / 12) + 1.5) for k in range(7)], 0.3, INK_SOFT, op=0.6)
    D.snail(d, 497, cel_floor - 49, 0.7)

    # ================================================= exterior hill face (left)
    cut = [(250, 322), (244, 380), (253, 432), (246, 486), (256, 534), (249, 584), (258, 632), (266, 658)]
    face = [p for p in surface if p[0] <= 250] + cut + [(-15, 658)]
    d.wash(face, "#9cb56a", 0.9, jitter=0, shade=0.25, cover=0.95)
    O.mottle(d, face, ["#7d9d50", "#b7c77a", "#8ea05c"], n=26, rmin=12, rmax=40, op=0.3)
    for _ in range(420):
        x, y = d.u(-10, 245), d.u(330, 650)
        if inside((x, y), face):
            L = d.u(3, 7)
            d.ink([(x, y), (x + d.r(1.2), y - L)], 0.55, d.choice(["#6b8c45", "#86a557", "#a6b86a"]), op=0.75, jitter=0.1)
    d.ink(cut, 2.0, "#8f6a46", op=0.9)
    d.ink(cut, 0.8, INK)
    # the round door with climbing roses
    O.round_door(d, 132, 556, 52)
    for k in range(26):
        a = math.pi * (1.02 + k * 0.038)
        x, y = 132 + 64 * math.cos(a) + d.r(2), 556 + 64 * math.sin(a) + d.r(2)
        D.leaf_shape  # noqa
        d.wash(D.leaf_shape(x, y, 6, a + 1.6 + d.r(0.6), 0.5), d.choice(D.LEAF_MID + D.LEAF_DARK), 0.85, jitter=0.1)
        if k % 3 == 0:
            for j in range(5):
                aa = j * 2 * math.pi / 5
                d.wash(ellipse_pts(x + 1.4 * math.cos(aa), y - 1 + 1.4 * math.sin(aa), 1.6, 1.4, 8), "#e9a8b0", 0.9, jitter=0.05)
            d.dot(x, y - 1, 0.6, "#c9607e")
    O.round_window(d, 52, 470, 22)
    O.steps(d, 98, 612, 1, 70, 8)
    O.steps(d, 92, 620, 1, 82, 9)
    D.lantern_lit(d, 200, 505, 0.8, hang=6)
    d.ink([(196, 499), (210, 499)], 1.0, INK)
    d.shape(rect_pts(186, 618, 46, 5), "#c99a62", 0.9, w=0.7, smooth_=False, shade=0.5)
    for lx in (190, 226):
        d.line(lx, 623, lx, 640, 1.3, "#7d5229", 0)
    O.basket(d, 220, 618, 12, 7, "#c4513a")
    for px, col in ((64, "#c4774a"), (78, "#b8684a")):
        d.shape([(px - 6, 640), (px - 7, 628), (px + 7, 628), (px + 6, 640)], col, 0.92, w=0.6, smooth_=False, shade=0.6)
        for k in range(4):
            D.wildflower(d, px - 5 + k * 3.3, 628, d.choice(["campion", "daisy", "buttercup"]), 0.7)
    D.foxglove(d, 238, 640, 52)
    D.foxglove(d, 22, 640, 44)
    D.meadow(d, [p for p in surface if p[0] <= 250], density=0.7, flowers=0.25, h=(4, 10))
    D.snail(d, 168, 412, 0.8)
    # garden strip, fence and stepping stones
    garden_top = [(-15, 642), (60, 640), (140, 641), (200, 643), (266, 650)]
    d.wash(garden_top + [(266, 668), (-15, 668)], "#86a557", 0.88, shade=0.2)
    D.meadow(d, garden_top, density=0.9, flowers=0.35, h=(6, 14))
    O.fence(d, -10, 646, 38, 643, 26, 3)
    for sx in (110, 140, 168):
        d.shape(blob(sx, 646, 11, 3.5, d.rng, 0.1, 12), "#c9bfa9", 0.9, w=0.6, shade=0.6)
    for fx in range(10, 250, 12):
        O.root(d, fx, 668, 1.57 + d.r(0.4), d.u(18, 45), 1.2, 1, color="#a7865e")
    # turf and meadow along the cut hill top
    top_cut = [(250, 322)] + [p for p in surface if p[0] >= 250]
    O.grass_band(d, top_cut, 15, "#93b062")
    D.meadow(d, top_cut, density=0.8, flowers=0.2, h=(4, 11))
    D.foxglove(d, 330, 298, 40)
    D.foxglove(d, 560, 262, 46)

    # ================================================= the oak on top
    D.oak_tree(d, 440, 270, 120, 34, 190, 105, lean=-6, leaves=2600)
    d.line(500, 160, 496, 236, 0.6, "#b8955a", 0)
    d.line(520, 152, 518, 236, 0.6, "#b8955a", 0)
    d.shape(rect_pts(492, 236, 30, 4), "#c99a62", 0.95, w=0.6, smooth_=False)

    # ================================================= small creatures & finds
    wp = [(150 + i * 5, 760 + 4 * math.sin(i)) for i in range(9)]
    d.ink(wp, 2.6, "#d9968e")
    d.ink(wp, 0.5, INK, op=0.6)
    kx, ky = 120, 820
    d.shape(ellipse_pts(kx, ky, 6, 6, 14), "#c9a03a", 0.9, w=0.6)
    d.ink(ellipse_pts(kx, ky, 2.5, 2.5, 8), 0.5, INK, closed=True)
    d.shape(rect_pts(kx + 5, ky - 1.6, 22, 3.2), "#c9a03a", 0.9, w=0.5, smooth_=False)
    d.shape(rect_pts(kx + 20, ky + 1.6, 3, 5), "#c9a03a", 0.9, w=0.4, smooth_=False)
    d.ink([(330 + 6 * t / 10 * math.cos(t * 0.9), 1000 + 6 * t / 10 * math.sin(t * 0.9)) for t in range(0, 22)], 0.6, INK_SOFT)
    for bx, by, c in ((210, 600, "#e3b43a"), (40, 600, "#7f9cb5"), (300, 260, "#f0e6c8")):
        for s_ in (-1, 1):
            d.wash(blob(bx + s_ * 4, by - 2, 4, 3, d.rng, 0.1, 8, rot=s_ * 0.5), c, 0.92)
        d.line(bx, by - 4, bx, by + 2, 0.6, INK, 0)
    return d.save(path)


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else "../png/plate_burrow_cutaway.jpg")
