"""Full-page plate: a vaulted barrel-cellar over an underground river (style study).

Shows the 'inner workings' the art bible asks for: winch, gears, pulley,
counterweighted trapdoor lever, barrel chute and a portcullis water-gate,
all in cross-section.  7.125 x 10.25in (7x10 page + bleed).
"""
import math
from kit import PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, arch_pts, line_pts, inside
from wc import Canvas as Doc
import objects as O


def build(path):
    W, H = 712.5, 1025
    d = Doc(7.125, 10.25, seed=21)

    # ------------------------------------------------ forest floor at top
    d.wash_gradient([(-10, -10), (W + 10, -10), (W + 10, 140), (-10, 140)], [(0, "#dfe6d6"), (1, "#c9d7c0")], 0, 0, 0, 140, op=0.8, soft=True)
    for tx, tw in ((70, 46), (250, 60), (520, 52), (660, 40)):
        O.tree_trunk(d, tx, 112, -20, tw)
        d.wash([(tx - tw * 0.4, 0), (tx + tw * 0.4, 0), (tx + tw * 0.3, 100), (tx - tw * 0.3, 100)], "#9a9a8a", 0.35)
    for fx in (150, 380, 440, 600):
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.45
            pts = [(fx, 118), (fx + 18 * math.cos(a), 118 + 18 * math.sin(a)), (fx + 30 * math.cos(a + 0.2), 118 + 30 * math.sin(a + 0.2))]
            d.ink(pts, 2.2, PAL["leafdk"])
            for t in range(1, 6):
                px = fx + 30 * math.cos(a) * t / 6
                py = 118 + 30 * math.sin(a) * t / 6
                O.leaf(d, px, py, 6, a - 1.2, ink_w=0.4, vein=False)
                O.leaf(d, px, py, 6, a + 1.2, ink_w=0.4, vein=False)
    surface = [(x, 118 + 4 * math.sin(x / 40)) for x in range(-20, 760, 30)]

    # ------------------------------------------------------- rock body
    rock = surface + [(740, 1040), (-20, 1040)]
    d.wash(rock, "#a99b84", 0.95, jitter=0)
    O.mottle(d, rock, ["#94866f", "#c2b59c", "#857762", "#b7a88c"], n=60, rmin=30, rmax=90, op=0.45)
    O.grass_band(d, surface, 14, PAL["moss"])
    O.tufts(d, surface, every=8, h=8, flowers=0.05)
    for sy in (150, 190, 548, 562, 940, 960):
        pts = [(x, sy + 10 * math.sin(x / 90 + sy) + d.r(3)) for x in range(-10, 740, 40)]
        d.ink(pts, 0.7, "#6f6252", op=0.5)
    O.pebbles(d, [(-20, 130), (740, 130), (740, 168), (-20, 168)], 40, 3, 9, ["#9c8d77", "#c2b49c", "#857866"])
    O.pebbles(d, [(-20, 520), (740, 520), (740, 590), (-20, 590)], 40, 3, 9, ["#9c8d77", "#c2b49c", "#857866"])
    O.soil_texture(d, rock, 300, "#6f6252")

    # roots dropping down from the trees
    for tx in (70, 250, 520, 660):
        for a in (1.35, 1.75):
            O.root(d, tx + d.r(8), 124, a, 50, 2.2, 1)

    # ----------------------------------------------------- vaulted cellar
    cx0, cx1 = 34, 680
    ctop, cfloor = 168, 520
    vault = arch_pts(cx0, ctop, cx1 - cx0, cfloor - ctop, 110, 24)
    d.wash([(x + (x - 357) * 0.025, y + (y - 344) * 0.04) for x, y in vault], "#5e5243", 0.9)
    d.push_clip(vault)
    O.stone_wall(d, cx0 - 10, ctop - 10, cx1 - cx0 + 20, cfloor - ctop + 10, course=22,
                 colors=["#d9ccb4", "#cbbd9f", "#e2d6bf", "#c4b496"], mortar="#efe3c8", ink_op=0.45)
    d.wash(ellipse_pts(357, 380, 330, 170, 24), "#fbe7b5", 0.4, soft=True)
    d.wash([(cx0, ctop + 60), (cx0 + 60, ctop + 40), (cx0 + 40, cfloor), (cx0, cfloor)], PAL["shadow"], 0.25, soft=True)
    d.wash([(cx1, ctop + 60), (cx1 - 60, ctop + 40), (cx1 - 40, cfloor), (cx1, cfloor)], PAL["shadow"], 0.25, soft=True)
    d.pop_clip()
    d.ink(vault, 1.8, INK, closed=True)
    # vault ribs
    # floor
    floor = [(cx0, cfloor), (cx1, cfloor), (cx1, cfloor + 34), (cx0, cfloor + 34)]
    O.stone_wall(d, cx0, cfloor, cx1 - cx0, 34, course=17, colors=["#a99a83", "#b5a68e", "#9c8d77"], mortar="#7d705f")

    # trapdoor opening in the floor
    tx0, tx1 = 300, 410
    d.wash(rect_pts(tx0, cfloor - 1, tx1 - tx0, 36), "#2c3a40", 0.95, smooth_=False)
    # open trapdoor flap hanging down into the river cave
    flap = [(tx0, cfloor + 34), (tx0 + 6, cfloor + 34), (tx0 + 22, cfloor + 140), (tx0 + 14, cfloor + 142)]
    O.planks(d, tx0 - 2, cfloor + 34, 8, 4, 1)
    d.shape(flap, PAL["wood"], 0.95, w=1.1, smooth_=False)
    d.ink([(tx0 + 4, cfloor + 60), (tx0 + 13, cfloor + 60)], 1.2, "#3a3a3a")
    d.ink([(tx0 + 8, cfloor + 110), (tx0 + 17, cfloor + 110)], 1.2, "#3a3a3a")

    # barrel chute (wooden ramp) towards the trapdoor
    O.planks(d, 180, cfloor - 30, 120, 6, 1, vertical=False, color=PAL["woodlt"])
    d.ink([(180, cfloor - 30), (300, cfloor - 2)], 1.2, INK)
    for lx in (190, 230, 270):
        d.line(lx, cfloor - 28 + (lx - 180) * 0.23, lx, cfloor, 1.4, PAL["wooddk"], 0)
    O.barrel_side(d, 262, cfloor - 22, 26, 34)

    # stacked barrel pyramid on the left
    for row, n in enumerate((5, 4, 3, 2)):
        for i in range(n):
            O.barrel_end(d, 58 + 26 * i + row * 13, cfloor - 22 - row * 41, 20, tap=(row == 0 and i == 1))
    O.beam(d, 36, cfloor - 4, 140, 4)

    # winch frame with gears above the trapdoor
    fx = 355
    d.shape(rect_pts(fx - 70, 248, 6, cfloor - 248), PAL["wooddk"], 0.9, w=1.0, smooth_=False)
    d.shape(rect_pts(fx + 64, 248, 6, cfloor - 248), PAL["wooddk"], 0.9, w=1.0, smooth_=False)
    O.beam(d, fx - 76, 240, 152, 10)
    O.gear(d, fx - 30, 300, 26, 12, PAL["woodlt"], rot=0.2)
    O.gear(d, fx + 8, 286, 15, 8, PAL["wood"], rot=0.5)
    O.gear(d, fx + 40, 300, 20, 10, PAL["brass"], rot=0.1)
    # crank handle
    d.ink([(fx - 30, 300), (fx - 60, 330), (fx - 64, 342)], 3, PAL["wooddk"])
    d.shape(ellipse_pts(fx - 64, 345, 5, 5, 10), PAL["woodlt"], 0.95, w=0.8)
    # drum with rope wound round
    d.shape(rect_pts(fx - 10, 326, 46, 22, 10), PAL["wood"], 0.9, w=0.9, smooth_=False)
    for k in range(8):
        d.ink([(fx - 8 + k * 5.6, 327), (fx - 6 + k * 5.6, 347)], 1.1, "#b8955a")
    # pulley on the beam and rope down to a barrel being lowered
    O.gear(d, fx + 30, 252, 9, 6, "#8a8a8a")
    O.rope(d, [(fx + 30, 262), (fx + 30, 330), (fx + 31, 400), (fx + 30, 448)])
    d.ink([(fx + 18, 452), (fx + 30, 448), (fx + 42, 452)], 1.2, "#b8955a")
    O.barrel_side(d, fx + 30, 500, 34, 46)
    # counterweighted lever by the trapdoor
    d.shape(ellipse_pts(450, cfloor - 12, 8, 8, 12), PAL["wooddk"], 0.95, w=0.9)
    d.ink([(420, cfloor - 2), (450, cfloor - 12), (520, cfloor - 64)], 4.5, PAL["wood"])
    d.ink([(420, cfloor - 2), (450, cfloor - 12), (520, cfloor - 64)], 0.9, INK)
    d.shape(blob(523, cfloor - 70, 14, 11, d.rng, 0.15, 10), "#8d8a84", 0.95, w=1.0)
    d.ink([(520, cfloor - 64), (523, cfloor - 80)], 1.2, "#555")

    # right side: second winch for the water-gate, chain going down through the floor
    O.gear(d, 610, 330, 30, 14, PAL["woodlt"], rot=0.3)
    O.gear(d, 650, 300, 14, 8, PAL["brass"])
    d.ink([(610, 330), (580, 360), (576, 372)], 3, PAL["wooddk"])
    d.shape(rect_pts(600, 320, 6, cfloor - 320), PAL["wooddk"], 0.9, w=0.9, smooth_=False)
    chain = [(640, 360 + k * 9) for k in range(int((cfloor + 34 - 360) / 9))]
    for (x, y) in chain:
        d.ink(ellipse_pts(x, y, 2.4, 4.8, 8), 0.9, "#555555", closed=True)

    # wall lanterns, key ring, flagons, wine rack, sacks
    O.lantern(d, 150, 230, 1.0, hang=10)
    O.lantern(d, 560, 230, 1.0, hang=10)
    d.ink(ellipse_pts(470, 300, 10, 10, 14), 1.4, PAL["brass"], closed=True)
    for k in range(5):
        a = math.pi * (0.3 + k * 0.1)
        kx, ky = 470 + 10 * math.cos(a), 300 + 10 * math.sin(a)
        d.ink([(kx, ky), (kx + 2 * math.cos(a), ky + 18)], 1.6, PAL["brass"])
        d.ink([(kx + 2 * math.cos(a), ky + 16), (kx + 2 * math.cos(a) + 4, ky + 16)], 1.6, PAL["brass"])
    d.line(470, 280, 470, 290, 1.0, INK, 0)
    O.wine_rack(d, 560, cfloor - 4, 34, 90, 5)
    O.table(d, 470, cfloor - 4, 40, 28, cloth="#e8d8b6")
    for k, cx in enumerate((458, 472, 486)):
        d.shape([(cx - 4, cfloor - 34), (cx - 5, cfloor - 46), (cx + 5, cfloor - 46), (cx + 4, cfloor - 34)],
                d.choice(["#8a6a8a", PAL["copper"], "#7c9a6a"]), 0.95, w=0.7, smooth_=False)
    O.sack(d, 630, cfloor - 4, 26, 28)
    O.sack(d, 656, cfloor - 4, 22, 22, color="#d8c394")

    # --------------------------------------------- underground river cave
    cave = [(-20, 600), (60, 572), (160, 566), (260, 580), (360, 576), (460, 584), (560, 570), (640, 590), (740, 580),
            (740, 900), (640, 920), (520, 915), (400, 930), (280, 920), (160, 928), (60, 915), (-20, 925)]
    d.wash_gradient(cave, [(0, "#4f5b5d"), (0.6, "#6f7d79"), (1, "#a7b8a6")], 0, 0, W, 0, op=0.9, smooth_=True)
    O.mottle(d, cave, ["#3f4a4c", "#7f8c86"], n=18, rmin=30, rmax=70, op=0.3)
    d.ink(cave[:9], 1.6, INK)
    d.ink(cave[9:], 1.6, INK)
    # water-gate arch on the right, daylight beyond
    gate = arch_pts(560, 640, 150, 280, 60, 16)
    d.wash(gate, "#d8e7d6", 0.95)
    d.wash(ellipse_pts(640, 800, 120, 140, 20), "#fbf1c8", 0.6, soft=True)
    for k in range(5):
        O.tree_trunk(d, 590 + k * 30, 800, 650, 8)
    O.foliage_cluster(d, 640, 690, 80, 40, n=10, leaves=30)
    O.stone_wall(d, 548, 620, 14, 300, course=16)
    O.stone_wall(d, 702, 620, 14, 300, course=16)
    d.ink(gate, 1.4, INK)
    # raised portcullis
    for k in range(7):
        gx = 568 + k * 20
        d.line(gx, 640, gx, 700, 2.2, "#4a4a4a", 0)
        d.ink([(gx - 1, 700), (gx, 708), (gx + 1, 700)], 1.6, "#4a4a4a")
    for gy in (650, 676, 698):
        d.line(562, gy, 702, gy, 1.8, "#4a4a4a", 0)
    # water
    water_top = 728
    water = [(-20, water_top)] + [(x, water_top + 3 * math.sin(x / 25)) for x in range(0, 740, 20)] + [(740, 905), (-20, 915)]
    d.wash_gradient(water, [(0, "#4f7d8c"), (0.7, "#6f9fae"), (1, "#a9cbc9")], 0, 0, W, 0, op=0.85, smooth_=True)
    d.wash([(x, y + 30) for x, y in water], PAL["waterdk"], 0.35)
    d.wash([(570, water_top + 4), (700, water_top + 4), (690, 820), (580, 820)], "#cfe3df", 0.35, soft=True)
    # stone ledge with a moored boat and a lamp post on the left
    ledge = [(-20, 700), (40, 690), (130, 694), (150, 715), (140, 735), (-20, 740)]
    d.shape(ledge, "#8f826e", 0.95, w=1.2)
    O.stone_wall(d, -10, 700, 140, 34, course=12, colors=["#a99a83", "#9c8d77"], mortar="#6f6252", ink_op=0.6)
    d.shape(rect_pts(110, 650, 5, 46), PAL["wooddk"], 0.95, w=0.8, smooth_=False)
    O.lantern(d, 112, 640, 0.9)
    boat = [(150, water_top + 2), (165, water_top + 16), (230, water_top + 18), (250, water_top - 2), (240, water_top + 1), (160, water_top + 4)]
    d.shape(boat, PAL["wood"], 0.95, w=1.1)
    d.ink([(160, water_top + 8), (240, water_top + 9)], 0.6, INK_SOFT)
    O.rope(d, [(112, 690), (130, water_top - 10), (152, water_top + 4)], 1.1)
    # glowing cave mushrooms on the ledge
    for mx in (20, 48, 74):
        d.glow(mx, 686, 16, "#d9f0b0", 0.6)
        O.mushroom(d, mx, 692, 0.7, cap="#d7c98a")
    for k in range(40):
        wx, wy = d.u(0, 700), d.u(water_top + 8, 890)
        d.ink([(wx, wy), (wx + 7, wy - 1.5), (wx + 14, wy)], 0.6, PAL["white"], op=0.5)
    # floating barrels drifting out of the gate
    for bx, by, r in ((300, water_top + 4, 22), (420, water_top + 2, 20), (520, water_top + 6, 18), (640, water_top + 3, 16)):
        O.barrel_end(d, bx, by, r)
        d.ink([(bx - r - 6, by + r * 0.6), (bx - r - 18, by + r * 0.6 + 2)], 0.7, PAL["white"], op=0.7)
    # a barrel splashing down from the trapdoor
    O.barrel_side(d, 355, 676, 30, 40)
    for k in range(6):
        a = math.pi * (1.1 + k * 0.16)
        d.ink([(355 + 22 * math.cos(a), water_top - 4 + 10 * math.sin(a)), (355 + 34 * math.cos(a), water_top - 10 + 18 * math.sin(a))], 1.0, PAL["white"])
    d.ink([(330, 620), (334, 640)], 0.6, INK_SOFT, op=0.6)
    d.ink([(380, 620), (376, 640)], 0.6, INK_SOFT, op=0.6)
    # fish & stalactites
    for fx, fy in ((120, 850), (300, 870), (470, 845)):
        d.shape([(fx - 10, fy), (fx, fy - 4), (fx + 8, fy), (fx, fy + 4)], "#c9a25a", 0.9, w=0.6)
        d.shape([(fx - 10, fy), (fx - 16, fy - 4), (fx - 16, fy + 4)], "#c9a25a", 0.9, w=0.6, smooth_=False)
        d.dot(fx + 4, fy - 1, 0.8)
    for sx in range(30, 540, 46):
        L = d.u(12, 30)
        d.shape([(sx - 6, 574), (sx + 6, 574), (sx + d.r(1), 574 + L)], "#8f826e", 0.9, w=0.7)
    # river-bed stones
    O.pebbles(d, [(-20, 905), (740, 895), (740, 1040), (-20, 1040)], 90, 4, 14, ["#9c8d77", "#b5a68e", "#857866", "#c2b49c"])
    O.soil_texture(d, [(-20, 930), (740, 920), (740, 1040), (-20, 1040)], 150, "#6f6252")
    O.pebbles(d, [(-20, 140), (740, 140), (740, 165), (-20, 165)], 25, 3, 8)

    # labels
    for x, y, s in ((150, 262, "the Barrel Store"), (355, 230, "the Great Winch"), (300, 625, "the Under-river"), (635, 615, "the Water-gate")):
        d.text(x, y, s, size=13, italic=True)

    d.save(path)


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else "../svg/plate_cellar_mechanism.svg")
