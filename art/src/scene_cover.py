"""Cover art panels (no text: the title is set in the cover layout).

Front: an evening landscape — a lamplit round-doored hill-home in the
foreground, a winding road leading away over green hills to a far blue
mountain (the 'there and back again' journey), framed by a bramble-hung tree.
Back: the same evening meadow continuing, quiet enough to carry the blurb.
Each panel is 7.125 x 10.25in (7x10 trim + bleed on three sides).
"""
import math
from kit import Doc, PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, line_pts
import objects as O
import small


def sky(d, W, H):
    g = d.linear([(0, "#9fbcd0", 1), (0.45, "#e9e2c8", 1), (0.62, "#f6dca8", 1), (1, "#f6dca8", 1)])
    d.add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#{g})"/>')
    d.add(f'<rect x="0" y="0" width="{W}" height="{H}" filter="url(#paperf2)" opacity="0.35"/>')


def hills(d, W, base, layers):
    for i, (y, amp, col, op) in enumerate(layers):
        pts = [(-20, 1045)] + [(x, y + amp * math.sin(x / (120 + i * 30) + i * 1.7) + d.r(2)) for x in range(-20, int(W) + 40, 30)] + [(W + 20, 1045)]
        d.wash(pts, col, op)
        d.ink(pts[1:-1], 0.7, INK_SOFT, op=0.5)


def build_front(path):
    W, H = 712.5, 1025
    d = Doc(7.125, 10.25, seed=33)
    sky(d, W, H)
    O.cloud(d, 520, 120, 150, 36)
    O.cloud(d, 160, 80, 120, 28)
    # far mountain
    mt = [(260, 560), (340, 500), (400, 455), (430, 440), (470, 452), (540, 505), (620, 560)]
    d.wash(mt, PAL["mount"], 0.8)
    d.wash([(400, 455), (430, 440), (470, 452), (455, 470), (430, 462), (412, 472)], "#e9eef4", 0.9)
    d.ink(mt[1:-1], 0.8, INK_SOFT, op=0.6)
    hills(d, W, 760, [(540, 12, "#b7c4a6", 0.85), (585, 16, "#a3b97e", 0.9), (640, 18, PAL["grass3"], 0.92), (700, 14, PAL["grass"], 0.95)])
    # the winding road from foreground into the distance
    road = [(330, 1040), (420, 940), (520, 860), (480, 790), (360, 740), (420, 690), (500, 650), (470, 610), (430, 585)]
    left = [(x - (16 - i * 1.7), y) for i, (x, y) in enumerate(road)]
    right = [(x + (16 - i * 1.7) + (40 if i == 0 else 30 if i == 1 else 0), y) for i, (x, y) in enumerate(road)]
    d.wash(left + right[::-1], "#e8d2a2", 0.95)
    d.ink(left, 0.8, INK_SOFT)
    d.ink(right, 0.8, INK_SOFT)
    # hedgerows & small trees along the hills
    for x, y, r in ((150, 600, 30), (620, 620, 26), (560, 680, 34), (90, 660, 22), (640, 560, 18)):
        O.foliage_cluster(d, x, y, r * 1.4, r, n=8, leaves=20)
    # the hill-home, lower left
    hill = [(-20, 1040), (-20, 760), (40, 730), (140, 712), (240, 724), (320, 770), (360, 840), (350, 1040)]
    d.shape(hill, PAL["grass"], 0.95, w=1.2)
    O.mottle(d, hill, [PAL["grass2"], PAL["grass3"]], n=14, rmin=20, rmax=50, op=0.3)
    O.round_door(d, 165, 850, 56)
    O.round_window(d, 285, 830, 20)
    O.round_window(d, 52, 818, 18, curtain=PAL["blue"])
    d.glow(165, 850, 120, PAL["flame"], 0.25)
    O.lantern(d, 240, 780, 1.1)
    d.ink([(232, 774), (252, 774)], 1.4, INK)
    O.steps(d, 120, 906, 1, 92, 9)
    O.steps(d, 112, 915, 1, 108, 10)
    d.shape(rect_pts(240, 930, 70, 7), PAL["woodlt"], 0.9, w=0.9, smooth_=False)
    for lx in (246, 302):
        d.line(lx, 937, lx, 958, 1.6, PAL["wooddk"], 0)
    O.tufts(d, hill[1:7], every=6, h=10, flowers=0.2)
    # chimney with smoke on top of the hill
    d.shape(rect_pts(196, 690, 22, 30, 10), "#b9704e", 0.95, w=1.0, smooth_=False)
    O.smoke(d, 207, 680, 120, 10)
    # garden flowers & gate in the foreground
    O.fence(d, -10, 980, 100, 975, 34, 5)
    for k in range(40):
        x = d.u(-10, 330)
        y = d.u(950, 1020)
        O.flower(d, x, y, d.u(3, 6))
    O.tufts(d, [(-20, 1000), (360, 990)], every=4, h=16, flowers=0.2)
    # framing tree on the right with brambles
    O.tree_trunk(d, 668, 1040, 400, 92, lean=-12)
    d.ink([(650, 520), (590, 440), (530, 400)], 6, PAL["wooddk"])
    O.foliage_cluster(d, 620, 330, 160, 120, n=22, leaves=160)
    O.foliage_cluster(d, 520, 410, 70, 40, n=8, leaves=30)
    small.bramble_branch(d, 700, 760, 560, 900, -1)
    small.bramble_branch(d, 690, 900, 520, 1000, -1)
    # foreground mushrooms & snail
    O.mushroom(d, 470, 1000, 1.6, PAL["red"])
    O.mushroom(d, 492, 1004, 1.1, "#c8894a", lean=0.3)
    d.save(path)


def build_back(path):
    W, H = 712.5, 1025
    d = Doc(7.125, 10.25, seed=34)
    sky(d, W, H)
    O.cloud(d, 240, 140, 160, 36)
    hills(d, W, 760, [(600, 14, "#b7c4a6", 0.85), (660, 16, "#a3b97e", 0.9), (740, 18, PAL["grass3"], 0.92), (820, 14, PAL["grass"], 0.95)])
    for x, y, r in ((560, 640, 30), (380, 700, 24), (120, 680, 18)):
        O.foliage_cluster(d, x, y, r * 1.4, r, n=8, leaves=20)
    O.tree_trunk(d, 30, 1040, 500, 84, lean=12)
    O.foliage_cluster(d, 70, 430, 140, 110, n=20, leaves=140)
    for k in range(50):
        O.flower(d, d.u(0, W), d.u(940, 1020), d.u(3, 6))
    O.tufts(d, [(-20, 960), (W + 20, 950)], every=4, h=18, flowers=0.2)
    small.bramble_branch(d, 20, 1000, 300, 960, 1)
    for x in (600, 630):
        O.mushroom(d, x, 1000, 1.2)
    d.save(path)
