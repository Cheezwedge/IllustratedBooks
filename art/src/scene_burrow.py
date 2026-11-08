"""Full-page plate: cutaway of a hillside burrow-home (style study).

Composition: exterior hill face with round door on the left; the rest of the
hill and the ground beneath are 'cut away' to reveal three levels of rooms,
storerooms and cellars, threaded with tree roots.  Sized for a 7x10in page
with 0.125in bleed (7.125 x 10.25in).
"""
import math
from kit import Doc, PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, arch_pts, line_pts, lerp, smooth
import objects as O


def room(d, x, top, w, floor, archh, wall=None, wainscot=True, label=None):
    wall = wall or PAL["plaster"]
    pts = arch_pts(x, top, w, floor - top, archh)
    # dark cavity edge (the cut earth around the room)
    d.wash([(px + (px - (x + w / 2)) * 0.035, py + (py - (top + floor) / 2) * 0.05) for px, py in pts], PAL["earthdk"], 0.8)
    d.wash(pts, wall, 0.95)
    # soft lamplight
    d.wash(ellipse_pts(x + w / 2, (top + floor) / 2, w * 0.45, (floor - top) * 0.4, 18), "#fbe7b5", 0.5, soft=True)
    if wainscot:
        wy = floor - (floor - top) * 0.32
        O.planks(d, x + 2, wy, w - 4, floor - wy - 8, max(3, int(w / 16)), vertical=True, color=PAL["woodlt"], grain=False, nails=False)
        O.beam(d, x + 1, wy - 3, w - 2, 4, PAL["wood"])
    O.floor_tiles(d, x + 1, floor - 8, w - 2, 8)
    # ceiling beams following arch
    d.ink(arch_pts(x + 4, top + 4, w - 8, floor - top - 4, archh - 3)[1:-2], 2.2, PAL["wooddk"], op=0.8)
    d.ink(pts, 1.5, INK, closed=True)
    if label:
        d.text(x + w / 2, top + archh * 0.5 + 12, label, size=13, color=INK, italic=True, family="IM Fell English")
    return pts


def build(path):
    W, H = 712.5, 1025
    d = Doc(7.125, 10.25, seed=7)

    # ------------------------------------------------------------------ sky
    sky = d.linear([(0, PAL["sky"], 1), (0.55, PAL["sky2"], 1), (1, PAL["cream"], 1)])
    d.add(f'<rect x="0" y="0" width="{W}" height="520" fill="url(#{sky})" opacity="0.9" filter="url(#washsoft)"/>')
    O.cloud(d, 110, 120, 140, 40)
    O.cloud(d, 640, 190, 110, 30)
    O.cloud(d, 300, 40, 90, 22)
    # distant hills, left
    far = [(-20, 400), (-20, 330), (40, 300), (120, 290), (190, 300), (250, 320), (260, 400)]
    d.wash(far, PAL["hill_far"], 0.7, soft=True)
    far2 = [(-20, 400), (-20, 350), (60, 335), (150, 330), (240, 345), (250, 400)]
    d.wash(far2, "#b3c49a", 0.75)
    # birds
    for bx, by in ((80, 200), (100, 190), (125, 205)):
        d.ink([(bx - 5, by), (bx - 2, by - 3), (bx, by), (bx + 2, by - 3), (bx + 5, by)], 0.8, INK_SOFT)

    # ------------------------------------------------------------ the hill
    surface = [(-15, 445), (60, 410), (140, 372), (220, 338), (300, 304), (380, 280), (460, 263), (540, 257),
               (620, 266), (690, 283), (730, 293)]
    earth = surface + [(730, 1040), (-15, 1040)]
    d.wash(earth, PAL["earth"], 0.95, jitter=0)
    O.mottle(d, earth, [PAL["earth2"], PAL["clay"], PAL["earthdk"]], n=40, rmin=25, rmax=70, op=0.28)
    # strata lines
    for sy in (520, 650, 840, 1000):
        pts = [(x, sy + 10 * math.sin(x / 70 + sy) + d.r(3)) for x in range(-10, 740, 40)]
        d.ink(pts, 0.6, PAL["earthdk"], op=0.35)

    # rooms (polygons kept for root avoidance)
    cut_x = 252
    main_top, main_floor = 452, 615
    low_top, low_floor = 676, 806
    cel_top, cel_floor = 866, 975
    rooms = []

    # chimney shaft through the earth (drawn before rooms so the fireplace sits on top)
    O.stone_wall(d, 612, 262, 26, main_top - 262 + 30, course=11, colors=["#c98f6a", "#b67a58", "#d7a27c"], mortar="#9b7a5c")
    # roots from the tree, avoiding rooms
    avoid = [rect_pts(cut_x - 6, main_top - 18, 440, main_floor - main_top + 30),
             rect_pts(260, low_top - 12, 430, low_floor - low_top + 25),
             rect_pts(50, cel_top - 12, 640, cel_floor - cel_top + 25),
             rect_pts(606, 250, 38, 220)]
    def surf_y(x):
        for (x1, y1), (x2, y2) in zip(surface, surface[1:]):
            if x1 <= x <= x2:
                return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        return surface[0][1] if x < surface[0][0] else surface[-1][1]
    for ang, L, w in ((1.9, 190, 9), (1.2, 210, 9), (2.3, 160, 6), (0.8, 200, 6), (1.55, 140, 7), (2.55, 120, 4), (0.55, 150, 4)):
        O.root(d, 430 + d.r(10), 274, ang, L, w, depth=3, avoid=avoid, ymin=surf_y)
    # long roots creeping down the sides
    O.root(d, 690, 300, 1.75, 300, 5, 3, avoid=avoid, ymin=surf_y)
    O.root(d, 300, 330, 1.95, 140, 4, 2, avoid=avoid, ymin=surf_y)

    O.pebbles(d, [(255, 300), (730, 270), (730, 1040), (-15, 1040), (-15, 660), (255, 660)], 110, 2.5, 10)
    O.soil_texture(d, [(255, 300), (730, 270), (730, 1040), (-15, 1040), (-15, 660), (255, 660)], 420)

    # ----- main level: hall + parlour
    hall = room(d, cut_x, main_top + 14, 156, main_floor, 34, label="the Hall")
    parlour = room(d, 418, main_top, 266, main_floor, 52, label="the Parlour")
    # doorway between hall and parlour
    d.shape(rect_pts(404, 520, 18, main_floor - 520), PAL["plaster2"], 0.95, w=0)
    d.shape(arch_pts(402, 512, 22, main_floor - 512, 11), PAL["wood"], 0.9, w=1.0)
    d.shape(arch_pts(406, 518, 14, main_floor - 520, 7), "#f3dcae", 0.95, w=0.8)

    # hall furnishings
    O.hat_pegs(d, cut_x + 14, 528, 120)
    O.lantern(d, 374, main_top + 26, 0.9, hang=8)
    O.rug(d, 330, main_floor - 8, 90, 4, PAL["navy"], PAL["ochre"])
    # umbrella stand + boots
    d.shape([(262, main_floor - 8), (264, main_floor - 34), (276, main_floor - 34), (278, main_floor - 8)], "#8a8f7a", 0.9, w=0.9)
    d.ink([(268, main_floor - 34), (266, main_floor - 52)], 1.4, PAL["wooddk"])
    d.ink(ellipse_pts(263, main_floor - 52, 3.5, 3.5, 8, a0=math.pi * 1.9, a1=math.pi * 3.0), 1.4, PAL["wooddk"])
    for bx in (360, 374):
        d.shape([(bx, main_floor - 8), (bx, main_floor - 24), (bx + 7, main_floor - 24), (bx + 7, main_floor - 12),
                 (bx + 12, main_floor - 10), (bx + 12, main_floor - 8)], "#5a3e2a", 0.92, w=0.8, smooth_=False)
    # small chest with a map scroll on it
    d.shape(rect_pts(296, main_floor - 26, 34, 18), PAL["wood"], 0.9, w=0.9, smooth_=False)
    d.line(296, main_floor - 20, 330, main_floor - 20, 0.8, PAL["brass"], 0)
    d.shape(rect_pts(302, main_floor - 31, 22, 5, 6), "#f0e2c0", 0.95, w=0.6, smooth_=False)

    # parlour furnishings
    O.bookcase(d, 428, main_floor - 8, 36, 112, shelves=4)
    O.table(d, 492, main_floor - 8, 38, 30)
    O.teapot(d, 486, main_floor - 46, 0.7)
    O.cup(d, 502, main_floor - 39, 0.8)
    O.cake(d, 476, main_floor - 39, 0.55)
    O.rug(d, 560, main_floor - 8, 110, 4)
    O.armchair(d, 552, main_floor - 8, 1.25, PAL["red"])
    # footstool
    d.shape(blob(585, main_floor - 15, 9, 5, d.rng, 0.1, 10), PAL["ochre"], 0.9, w=0.8)
    O.fireplace(d, 640, main_floor - 8, 60, 78, fire=True)
    # framed picture and round mirror
    d.shape(rect_pts(476, 506, 34, 26, 10), PAL["gold"], 0.9, w=0.9, smooth_=False)
    d.shape(rect_pts(480, 510, 26, 18, 10), PAL["sky"], 0.9, w=0.6, smooth_=False)
    d.wash([(480, 528), (490, 518), (498, 522), (506, 515), (506, 528)], PAL["grass"], 0.9)
    d.shape(ellipse_pts(532, 526, 12, 12, 22), PAL["brass"], 0.9, w=0.9)
    d.shape(ellipse_pts(532, 526, 9, 9, 20), "#dbe6e6", 0.9, w=0.6)
    d.ink(ellipse_pts(529, 522, 4, 2.5, 8, a0=3.4, a1=4.6), 1, PAL["white"], op=0.9)
    O.lantern(d, 600, main_top + 16, 0.8, hang=14)
    # chimney pot and smoke on the hill top
    d.shape(rect_pts(611, 230, 28, 36, 10), "#b9704e", 0.92, w=1.1, smooth_=False)
    d.shape(rect_pts(607, 224, 36, 8, 10), "#a35f42", 0.95, w=1.0, smooth_=False)
    O.smoke(d, 625, 214, 150, 12)

    # ----- stair passage hall -> kitchen
    stair = [(cut_x + 4, main_floor - 2), (cut_x + 46, main_floor - 2), (300, low_floor), (cut_x + 4, low_floor)]
    d.wash(stair, PAL["earthdk"], 0.85)
    d.wash([(cut_x + 8, main_floor), (cut_x + 42, main_floor), (296, low_floor - 2), (cut_x + 8, low_floor - 2)], "#e8cf9f", 0.95)
    for i in range(10):
        sy = main_floor + 4 + i * 18.5
        sx = cut_x + 8
        d.shape(rect_pts(sx, sy, 40 - i * 0.6, 6, 10), PAL["stone"], 0.9, w=0.7, smooth_=False)
    d.ink(stair, 1.3, INK, closed=True, smooth_=False)

    # ----- lower level: kitchen + pantry
    kitchen = room(d, 300, low_top, 186, low_floor, 30, label="the Kitchen")
    pantry = room(d, 500, low_top, 186, low_floor, 30, label="the Pantry", wainscot=False)
    d.shape(arch_pts(484, 712, 20, low_floor - 712, 10), PAL["wood"], 0.9, w=1.0)
    d.shape(arch_pts(488, 718, 12, low_floor - 720, 6), "#f3dcae", 0.95, w=0.8)

    O.range_stove(d, 342, low_floor - 8, 56, 44)
    O.pots_rail(d, 308, 716, 72)
    O.dresser(d, 392, low_floor - 8, 44, 84)
    O.table(d, 460, low_floor - 8, 30, 26, cloth="#f2e8d0")
    d.shape(blob(456, low_floor - 40, 9, 5, d.rng, 0.1, 10), "#d39a55", 0.92, w=0.8)  # loaf
    d.ink([(450, low_floor - 41), (453, low_floor - 44)], 0.5, INK_SOFT)
    d.ink([(456, low_floor - 41), (459, low_floor - 44)], 0.5, INK_SOFT)
    O.basket(d, 470, low_floor - 8, 16, 10, PAL["apple2"])
    O.onion_string(d, 468, low_top + 30, 5, 0.9)

    # pantry: shelves of jars, cheeses, hams, sacks
    for i, sy in enumerate((742, 770, 798 - 20)):
        pass
    O.shelf_of_jars(d, 508, 734, 100, 15)
    O.shelf_of_jars(d, 508, 760, 100, 13)
    O.shelf(d, 508, 784, 100)
    for cx in (522, 546, 572):
        O.cheese(d, cx, 784, 9)
    O.ham(d, 628, low_top + 14, 1.0)
    O.ham(d, 652, low_top + 18, 0.85)
    O.onion_string(d, 672, low_top + 22, 4, 0.8)
    O.sack(d, 625, low_floor - 8, 26, 30, label="FLOUR")
    O.sack(d, 655, low_floor - 8, 22, 24, color="#d8c394", label="OATS")
    O.basket(d, 596, low_floor - 8, 20, 10)
    O.jar(d, 680, low_floor - 8, 14, kind="crock")

    # ----- steps pantry -> cellar
    st2 = [(640, low_floor - 2), (684, low_floor - 2), (684, cel_floor), (600, cel_floor)]
    d.wash(st2, PAL["earthdk"], 0.85)
    d.wash([(644, low_floor), (680, low_floor), (680, cel_floor - 2), (606, cel_floor - 2)], "#e3c995", 0.95)
    for i in range(9):
        sy = low_floor + 6 + i * 18.5
        sx = 644 - i * 4.4
        d.shape(rect_pts(sx, sy, 36, 6, 10), PAL["stone"], 0.9, w=0.7, smooth_=False)
    d.ink(st2, 1.3, INK, closed=True, smooth_=False)

    # ----- cellar
    cellar = room(d, 48, cel_top, 556, cel_floor, 36, wall="#e6cf9f", wainscot=False, label="the Cellar")
    O.stone_wall(d, 50, cel_floor - 46, 30, 38, course=9)
    # barrel racks
    O.beam(d, 92, cel_floor - 12, 150, 5)
    for i in range(5):
        O.barrel_end(d, 106 + i * 30, cel_floor - 27, 14, tap=(i == 2))
    for i in range(4):
        O.barrel_end(d, 121 + i * 30, cel_floor - 55, 14)
    O.wine_rack(d, 262, cel_floor - 8, 52, 70, 5.2)
    # apple racks
    for k, sy in enumerate((cel_floor - 70, cel_floor - 45, cel_floor - 20)):
        O.shelf(d, 330, sy, 72, brackets=False)
        for i in range(9):
            d.shape(blob(336 + i * 7.6, sy - 3.4, 3.6, 3.4, d.rng, 0.1, 8), d.choice([PAL["apple"], PAL["apple2"], "#d9b44a"]), 0.95, w=0.5)
    d.line(331, cel_floor - 74, 331, cel_floor - 8, 1.2, PAL["wooddk"], 0)
    d.line(401, cel_floor - 74, 401, cel_floor - 8, 1.2, PAL["wooddk"], 0)
    for bx in (436, 466, 496):
        O.barrel_side(d, bx, cel_floor - 8, 26, 38)
    O.candle(d, 466, cel_floor - 46, 10)
    O.sack(d, 530, cel_floor - 8, 26, 28, label="POTATOES" if False else "")
    O.basket(d, 562, cel_floor - 8, 22, 12, "#c9a25a")
    # firewood stack
    for r_ in range(3):
        for c_ in range(4 - r_):
            O.barrel_end  # placeholder to keep lints quiet
            cx, cy = 572 + c_ * 9 + r_ * 4.5, cel_floor - 13 - r_ * 8
            d.shape(ellipse_pts(cx, cy, 4.6, 4.2, 10), "#c79a5f", 0.95, w=0.6)
            d.ink(ellipse_pts(cx, cy, 2, 1.8, 8), 0.4, INK_SOFT, closed=True)
    # cobweb in the cellar corner
    wx, wy = 70, cel_top + 40
    for k in range(6):
        a = math.pi * (1.5 + k / 10)
        d.line(wx, wy - 10, wx + 40 * math.cos(a + math.pi / 2), wy - 10 + 40 * math.sin(a + math.pi / 2), 0.35, INK_SOFT, 0.2, op=0.6)

    # ----------------------------------------- exterior hill face (left)
    cut = [(250, 322), (244, 380), (253, 432), (246, 486), (256, 534), (249, 584), (258, 632), (266, 658)]
    face = [p for p in surface if p[0] <= 250] + cut + [(-15, 658)]
    d.wash(face, PAL["grass"], 0.95, jitter=0)
    O.mottle(d, face, [PAL["grass2"], PAL["grass3"], PAL["moss"]], n=22, rmin=15, rmax=45, op=0.35)
    for _ in range(140):
        x, y = d.u(-10, 245), d.u(330, 650)
        from kit import inside
        if inside((x, y), face):
            L = d.u(3, 7)
            d.ink([(x, y), (x + d.r(1.5), y - L)], 0.5, d.choice([PAL["grass2"], PAL["leafdk"]]), op=0.7, smooth_=False)
    # cut edge: dark earth lip + hanging grass roots
    d.ink(cut, 2.2, PAL["earthdk"], op=0.9)
    d.ink(cut, 1.0, INK)
    for (x1, y1) in cut[:-1]:
        for k in range(3):
            d.ink([(x1 + 2, y1 + k * 12), (x1 + 8 + d.r(3), y1 + k * 12 + 6), (x1 + 11, y1 + k * 12 + 13)], 0.4, INK_SOFT, op=0.6)
    # the round door, window, doorstep
    O.round_door(d, 132, 556, 52)
    # roses around door frame
    for k in range(16):
        a = math.pi * (1.05 + k * 0.06)
        x, y = 132 + 64 * math.cos(a), 556 + 64 * math.sin(a)
        O.leaf(d, x, y, 7, a + 1.6, ink_w=0.5)
        if k % 3 == 0:
            O.flower(d, x + 2, y - 2, 3.2, "pink")
    O.round_window(d, 52, 470, 22)
    O.steps(d, 98, 612, 1, 70, 8)
    O.steps(d, 92, 620, 1, 82, 9)
    # bench + lantern + flower pots
    O.lantern(d, 200, 505, 0.85, lit=True, hang=6)
    d.ink([(196, 499), (210, 499)], 1.2, INK)
    d.shape(rect_pts(186, 618, 46, 6), PAL["woodlt"], 0.9, w=0.8, smooth_=False)
    for lx in (190, 226):
        d.line(lx, 624, lx, 640, 1.4, PAL["wooddk"], 0)
    for px, col in ((64, PAL["red"]), (76, PAL["rose"])):
        d.shape([(px - 6, 640), (px - 7, 628), (px + 7, 628), (px + 6, 640)], "#c4774a", 0.92, w=0.8, smooth_=False)
        for k in range(4):
            O.flower(d, px - 5 + k * 3.3, 624 - d.u(0, 5), 2.6, d.choice(["pink", "daisy", "butter"]))
    O.tufts(d, [p for p in surface if p[0] <= 250], every=7, h=9, flowers=0.12)

    # garden strip & fence
    garden_top = [(-15, 642), (60, 640), (140, 641), (200, 643), (266, 650)]
    d.wash(garden_top + [(266, 668), (-15, 668)], PAL["grass2"], 0.9)
    O.tufts(d, garden_top, every=4, h=12, flowers=0.18)
    O.fence(d, -10, 646, 38, 643, 26, 3)
    for sx in (110, 140, 168):
        d.shape(blob(sx, 646, 11, 3.5, d.rng, 0.1, 10), PAL["stone"], 0.9, w=0.7)
    # flower roots in the garden soil
    for fx in range(10, 250, 22):
        O.root(d, fx, 668, 1.57 + d.r(0.4), d.u(25, 55), 1.8, 1)
    # turf on the cut hill top
    top_cut = [p for p in surface if p[0] >= 250]
    O.grass_band(d, [(250, 322)] + top_cut, 16)
    O.tufts(d, [(250, 322)] + top_cut, every=6, h=10, flowers=0.08)

    # ------------------------------------------------------------- tree
    O.tree_trunk(d, 430, 268, 140, 38, lean=-6)
    d.ink([(420, 170), (380, 140), (350, 130)], 4, PAL["wooddk"])
    d.ink([(440, 160), (490, 130), (520, 118)], 4, PAL["wooddk"])
    O.foliage_cluster(d, 430, 122, 180, 96, n=26, leaves=200)
    O.foliage_cluster(d, 300, 158, 66, 46, n=8, leaves=30)
    O.foliage_cluster(d, 560, 150, 66, 50, n=8, leaves=30)
    # a swing hanging from the branch
    d.line(492, 150, 488, 236, 0.7, "#b8955a", 0)
    d.line(512, 142, 510, 236, 0.7, "#b8955a", 0)
    d.shape(rect_pts(484, 236, 30, 4), PAL["woodlt"], 0.95, w=0.7, smooth_=False)

    # ---------------------------------------------- small creatures/details
    # worm in the soil
    wp = [(150 + i * 5, 760 + 4 * math.sin(i)) for i in range(9)]
    d.ink(wp, 3.2, "#d48c86")
    d.ink(wp, 0.6, INK, op=0.7)
    # snail on the hill
    d.shape(ellipse_pts(170, 410, 7, 6, 16), "#c98f4f", 0.95, w=0.8)
    d.ink([(170, 410), (172, 408), (171, 405), (167, 407), (166, 412), (172, 414), (176, 410)], 0.5, INK)
    d.shape([(161, 416), (182, 416), (186, 410), (183, 412), (175, 415)], "#c7b9a0", 0.95, w=0.6)
    # beetle
    d.shape(ellipse_pts(700 - 30, 720, 5, 7, 12), "#3d5a4a", 0.95, w=0.6)
    d.line(670, 713, 670, 727, 0.5, INK, 0)
    # buried old key (an easter egg for sharp-eyed children)
    kx, ky = 120, 820
    d.shape(ellipse_pts(kx, ky, 6, 6, 12), PAL["brass"], 0.9, w=0.8)
    d.ink(ellipse_pts(kx, ky, 2.5, 2.5, 8), 0.6, INK, closed=True)
    d.shape(rect_pts(kx + 5, ky - 1.6, 22, 3.2), PAL["brass"], 0.9, w=0.6, smooth_=False)
    d.shape(rect_pts(kx + 20, ky + 1.6, 3, 5), PAL["brass"], 0.9, w=0.5, smooth_=False)
    d.shape(rect_pts(kx + 24, ky + 1.6, 2.4, 3.5), PAL["brass"], 0.9, w=0.5, smooth_=False)
    # fossil shell
    d.ink([(330 + 6 * t / 10 * math.cos(t * 0.9), 1000 + 6 * t / 10 * math.sin(t * 0.9)) for t in range(0, 22)], 0.8, INK_SOFT)
    # butterflies
    for bx, by, c in ((210, 600, PAL["gold"]), (40, 600, PAL["blue"])):
        for s in (-1, 1):
            d.shape(blob(bx + s * 4, by - 2, 4, 3, d.rng, 0.1, 8, rot=s * 0.5), c, 0.95, w=0.5)
        d.line(bx, by - 4, bx, by + 2, 0.7, INK, 0)

    d.save(path)


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else "../svg/plate_burrow_cutaway.svg")
