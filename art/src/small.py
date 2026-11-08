"""Chapter emblems + bramble header banners, margin critters, drop caps and ornaments.

All transparent-background so they sit directly on the page.
"""
import math
from kit import PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, arch_pts, line_pts, transform_pts
from wc import Canvas as Doc
import objects as O


# ===================================================================== emblems
# Each draws into a 160x160 box centred on (cx, cy).
def em_teapot(d, cx, cy):
    O.table(d, cx, cy + 46, 120, 8, cloth=PAL["white"])
    O.teapot(d, cx - 18, cy + 30, 2.0, PAL["navy"])
    O.cup(d, cx + 34, cy + 30, 1.5)
    O.cake(d, cx + 18, cy + 4 + 26 - 26, 0.0001) if False else None
    O.cake(d, cx + 44, cy + 2, 0.9)
    O.steam(d, cx + 22, cy - 12, 26)


def em_campfire(d, cx, cy):
    d.glow(cx, cy + 20, 70, PAL["fire"], 0.45)
    for a, b in (((cx - 46, cy + 50), (cx + 4, cy - 46)), ((cx + 46, cy + 50), (cx - 4, cy - 46)), ((cx, cy + 54), (cx, cy - 50))):
        d.ink([a, b], 3, PAL["wooddk"])
    d.ink([(cx, cy - 40), (cx, cy - 8)], 1, INK)
    d.shape([(cx - 20, cy - 8), (cx - 22, cy + 10), (cx - 12, cy + 18), (cx + 12, cy + 18), (cx + 22, cy + 10), (cx + 20, cy - 8)], "#3d3d3d", 0.92, w=1.1)
    d.ink(ellipse_pts(cx, cy - 8, 20, 4, 16), 1, INK, closed=True)
    for k in range(5):
        fx = cx + (k - 2) * 8
        h = d.u(18, 28)
        d.shape([(fx - 6, cy + 46), (fx - 3, cy + 46 - h * 0.6), (fx, cy + 46 - h), (fx + 3, cy + 46 - h * 0.5), (fx + 6, cy + 46)],
                d.choice([PAL["fire"], PAL["fire2"], PAL["flame"]]), 0.92, w=0.6, ink_color=PAL["rust"])
    for lx, a in ((-14, 0.25), (14, -0.25)):
        pts = transform_pts(rect_pts(-24, -4, 48, 8, 10), cx + lx, cy + 52, 1, a)
        d.shape(pts, PAL["wooddk"], 0.95, w=0.8, smooth_=False)
    O.smoke(d, cx + 4, cy - 30, 40, 7)


def em_book(d, cx, cy):
    d.ink(ellipse_pts(cx + 40, cy - 46, 12, 12, 16, a0=0.9, a1=5.4), 1.4, PAL["gold"])
    d.wash(ellipse_pts(cx + 40, cy - 46, 12, 12, 16), "#f6e3a0", 0.6)
    d.wash(ellipse_pts(cx + 46, cy - 48, 10, 11, 16), "#ffffff", 0.0)
    for s in (-1, 1):
        page = [(cx, cy + 30), (cx + s * 56, cy + 24), (cx + s * 58, cy - 20), (cx + s * 4, cy - 14)]
        d.shape(page, "#f7eedb", 0.95, w=1.0)
        for k in range(6):
            y = cy - 10 + k * 6
            d.line(cx + s * 8, y + 2, cx + s * 48, y - 1, 0.5, INK_SOFT, 0.3, op=0.6)
    d.wash([(cx - 58, cy + 26), (cx, cy + 34), (cx + 58, cy + 26), (cx + 56, cy + 32), (cx, cy + 40), (cx - 56, cy + 32)], PAL["red"], 0.9)
    # faint glowing runes on the right page
    for k in range(4):
        d.ink([(cx + 18 + k * 8, cy - 6), (cx + 22 + k * 8, cy + 2), (cx + 18 + k * 8, cy + 6)], 0.8, "#9fc6d6", op=0.9)
    O.candle(d, cx - 44, cy - 20, 22)


def em_lantern_cave(d, cx, cy):
    arch = arch_pts(cx - 56, cy - 56, 112, 112, 40, 16)
    d.wash(arch, "#3e3a3a", 0.85)
    for k in range(13):
        a = math.pi + math.pi * k / 12
        x, y = cx + 64 * math.cos(a), cy - 16 + 50 * math.sin(a)
        d.shape(blob(x, y, 9, 7, d.rng, 0.12, 9, rot=a), d.choice([PAL["stone"], PAL["stone2"]]), 0.9, w=0.8)
    for side in (-1, 1):
        for k in range(4):
            d.shape(blob(cx + side * 62, cy - 4 + k * 16, 8, 7, d.rng, 0.1, 9), d.choice([PAL["stone"], PAL["stone2"]]), 0.9, w=0.8)
    O.lantern(d, cx, cy - 34, 1.8, lit=True, hang=10)
    for k in range(3):
        O.mushroom(d, cx - 30 + k * 10, cy + 56, 0.5, cap="#d7c98a")


def em_ring(d, cx, cy):
    d.wash(ellipse_pts(cx, cy + 20, 64, 22, 24), PAL["waterdk"], 0.7)
    d.shape(blob(cx, cy + 22, 36, 16, d.rng, 0.12, 12), PAL["stone2"], 0.95, w=1.0)
    d.glow(cx, cy + 2, 40, PAL["gold"], 0.5)
    d.shape(ellipse_pts(cx, cy + 4, 16, 9, 24), PAL["gold"], 0.95, w=1.0)
    d.wash(ellipse_pts(cx, cy + 4, 10.5, 5, 20), "#8a8580", 0.95)
    d.ink(ellipse_pts(cx, cy + 4, 10.5, 5, 20), 0.9, INK, closed=True)
    d.ink(ellipse_pts(cx - 4, cy + 0, 9, 5, 10, a0=3.4, a1=4.6), 1.2, "#fff3c0")
    for a in (0.3, 1.4, 2.5, 4.0, 5.2):
        d.line(cx + 26 * math.cos(a), cy + 2 + 20 * math.sin(a), cx + 34 * math.cos(a), cy + 2 + 26 * math.sin(a), 0.8, PAL["gold"], 0)


def em_feather(d, cx, cy):
    spine = [(cx - 40, cy + 50), (cx - 10, cy + 10), (cx + 20, cy - 30), (cx + 44, cy - 56)]
    left, right = [], []
    for k in range(1, 15):
        t = k / 15
        x = cx - 40 + 84 * t
        y = cy + 50 - 106 * t
        w = 18 * math.sin(math.pi * min(1, t * 1.05))
        left.append((x - w * 0.8, y - w * 0.5))
        right.append((x + w * 0.8, y + w * 0.5))
    d.shape([spine[0]] + left + [spine[-1]] + right[::-1], "#8a6a4a", 0.9, w=1.0)
    for k in range(2, 14):
        t = k / 15
        x = cx - 40 + 84 * t
        y = cy + 50 - 106 * t
        d.line(x, y, x - 14, y - 4, 0.5, INK_SOFT, 0.2)
        d.line(x, y, x + 6, y + 13, 0.5, INK_SOFT, 0.2)
    d.ink(spine, 1.4, "#f2e6cc")
    for px, py in ((cx + 30, cy + 36), (cx + 52, cy + 24)):
        d.shape(ellipse_pts(px, py, 11, 16, 18), "#9a6a3a", 0.92, w=1.0)
        for r in range(4):
            for k in range(3):
                d.ink([(px - 8 + k * 7, py - 10 + r * 6), (px - 5 + k * 7, py - 7 + r * 6)], 0.7, INK)


def em_honey(d, cx, cy):
    pot = [(cx - 34, cy + 50), (cx - 44, cy + 10), (cx - 34, cy - 24), (cx + 34, cy - 24), (cx + 44, cy + 10), (cx + 34, cy + 50)]
    d.shape(pot, "#d8b07a", 0.92, w=1.2)
    d.wash([(cx - 40, cy - 22), (cx + 40, cy - 22), (cx + 36, cy - 8), (cx + 10, cy - 2), (cx + 6, cy + 14), (cx - 2, cy - 2), (cx - 38, cy - 8)], PAL["honey"], 0.95)
    d.shape(ellipse_pts(cx, cy - 26, 36, 7, 20), "#e8dcc0", 0.95, w=1.0)
    d.shape(rect_pts(cx - 20, cy + 8, 40, 22, 10), PAL["white"], 0.95, w=0.7, smooth_=False)
    d.text(cx, cy + 25, "HONEY", size=11, family="IM Fell English SC", color=PAL["red"])
    d.ink([(cx + 12, cy - 30), (cx + 34, cy - 62)], 2.2, PAL["woodlt"])
    for bx, by in ((cx - 46, cy - 50), (cx - 18, cy - 62), (cx + 52, cy - 30)):
        bee(d, bx, by, 1.1)
    d.ink([(cx - 60, cy - 40), (cx - 50, cy - 46), (cx - 56, cy - 56), (cx - 46, cy - 50)], 0.5, INK_SOFT, op=0.7, dash="2 2")


def bee(d, x, y, s=1.0):
    d.shape(ellipse_pts(x, y, 7 * s, 5 * s, 14), "#e3b43a", 0.95, w=0.8)
    for k in (-2, 2):
        d.line(x + k * s, y - 4.5 * s, x + k * s, y + 4.5 * s, 1.4 * s, INK, 0)
    for k in (-1, 1):
        d.shape(ellipse_pts(x - 1 * s + k * 3 * s, y - 7 * s, 3 * s, 4.5 * s, 10, rot=k * 0.4), "#eef4f6", 0.85, w=0.5, ink_color=INK_SOFT)
    d.dot(x + 7 * s, y - 1 * s, 1.0 * s)


def em_web(d, cx, cy):
    d.ink([(cx - 64, cy - 64), (cx - 40, cy - 10), (cx - 54, cy + 60)], 2.0, PAL["wooddk"])
    d.ink([(cx + 62, cy - 60), (cx + 50, cy + 10), (cx + 60, cy + 62)], 2.0, PAL["wooddk"])
    O.leaf(d, cx - 48, cy - 34, 16, -2.4)
    O.leaf(d, cx + 52, cy + 30, 16, 0.4)
    anchors = [(cx - 44, cy - 30), (cx - 8, cy - 62), (cx + 52, cy - 40), (cx + 52, cy + 24), (cx + 10, cy + 60), (cx - 46, cy + 34)]
    for a in anchors:
        d.line(cx, cy, a[0], a[1], 0.6, INK_SOFT, 0.5)
    for r in range(1, 6):
        ring = []
        for a in anchors:
            t = r / 6
            ring.append((cx + (a[0] - cx) * t, cy + (a[1] - cy) * t + 1.5))
        d.ink(ring, 0.5, INK_SOFT, closed=True, op=0.9)
    for k in range(9):
        a = anchors[k % 6]
        t = d.u(0.3, 0.9)
        d.shape(ellipse_pts(cx + (a[0] - cx) * t, cy + (a[1] - cy) * t, 2.2, 2.2, 8), "#d9eef6", 0.95, w=0.4, ink_color=PAL["blue"])
    d.shape(ellipse_pts(cx + 4, cy + 4, 5, 6, 10), "#3a3a3a", 0.95, w=0.5)
    d.shape(ellipse_pts(cx + 4, cy - 3, 3, 3, 8), "#3a3a3a", 0.95, w=0.5)
    for k in range(4):
        for s in (-1, 1):
            d.ink([(cx + 4, cy + 2 + k * 2), (cx + 4 + s * 7, cy - 2 + k * 3), (cx + 4 + s * 9, cy + 4 + k * 3)], 0.6, INK)


def em_barrel(d, cx, cy):
    O.barrel_side(d, cx, cy + 46, 58, 80)
    for k in range(4):
        d.shape(blob(cx - 52 + k * 9 + d.r(2), cy + 42 - (k % 2) * 6, 6, 6, d.rng, 0.08, 10), d.choice([PAL["apple"], PAL["apple2"]]), 0.95, w=0.8)
    d.ink([(cx + 50, cy + 50), (cx + 60, cy + 30), (cx + 70, cy + 40)], 0.8, PAL["white"])


def em_boat(d, cx, cy):
    d.wash([(cx - 72, cy + 30), (cx + 72, cy + 30), (cx + 70, cy + 56), (cx - 70, cy + 56)], PAL["water"], 0.8)
    for k in range(5):
        x = cx - 60 + k * 28
        d.ink([(x, cy + 40), (x + 8, cy + 38), (x + 16, cy + 40)], 0.7, PAL["white"])
    hull = [(cx - 54, cy + 14), (cx - 40, cy + 34), (cx + 36, cy + 34), (cx + 58, cy + 10), (cx + 46, cy + 16), (cx - 44, cy + 18)]
    d.shape(hull, PAL["wood"], 0.95, w=1.2)
    d.ink([(cx - 46, cy + 24), (cx + 46, cy + 24)], 0.7, INK_SOFT)
    d.ink([(cx - 6, cy + 18), (cx - 40, cy - 10)], 2.2, PAL["woodlt"])
    d.shape([(cx - 40, cy - 10), (cx - 46, cy - 18), (cx - 48, cy - 14)], PAL["woodlt"], 0.95, w=0.8)
    for k in range(6):
        x = cx + 36 + k * 6
        d.ink([(x, cy + 34), (x + d.r(3), cy - 30 + k * 4)], 1.1, PAL["leafdk"])
        if k % 2 == 0:
            d.shape(ellipse_pts(x + 1, cy - 30 + k * 4, 2.5, 7, 10), "#7a5534", 0.95, w=0.6)
    # stilt house far off
    d.wash([(cx - 74, cy - 36), (cx - 50, cy - 52), (cx - 28, cy - 36)], "#a99bbf", 0.6)
    d.wash(rect_pts(cx - 70, cy - 36, 38, 22), "#c3c7d6", 0.6, smooth_=False)
    for k in range(4):
        d.line(cx - 68 + k * 11, cy - 14, cx - 68 + k * 11, cy + 30, 0.8, INK_SOFT, 0)


def em_key(d, cx, cy):
    d.shape(blob(cx + 10, cy + 40, 66, 22, d.rng, 0.12, 14), PAL["stone2"], 0.9, w=1.0)
    d.shape(ellipse_pts(cx - 36, cy - 10, 22, 22, 24), PAL["brass"], 0.95, w=1.2)
    d.wash(ellipse_pts(cx - 36, cy - 10, 11, 11, 18), "#00000000", 0)
    d.ink(ellipse_pts(cx - 36, cy - 10, 11, 11, 18), 1.0, INK, closed=True)
    for a in range(4):
        aa = a * math.pi / 2 + math.pi / 4
        d.ink(ellipse_pts(cx - 36 + 16 * math.cos(aa), cy - 10 + 16 * math.sin(aa), 3, 3, 8), 0.7, INK, closed=True)
    shaft = rect_pts(cx - 14, cy - 15, 74, 10, 10)
    d.shape(shaft, PAL["brass"], 0.95, w=1.1, smooth_=False)
    d.shape(rect_pts(cx + 40, cy - 6, 8, 18, 6), PAL["brass"], 0.95, w=1.0, smooth_=False)
    d.shape(rect_pts(cx + 52, cy - 6, 6, 12, 6), PAL["brass"], 0.95, w=1.0, smooth_=False)
    d.ink([(cx - 8, cy - 13), (cx + 50, cy - 13)], 1.0, "#fff1b8")
    # snail on the stone
    sx, sy = cx + 40, cy + 28
    d.shape(ellipse_pts(sx, sy, 10, 9, 16), "#c98f4f", 0.95, w=0.9)
    d.ink([(sx, sy), (sx + 3, sy - 2), (sx + 1, sy - 6), (sx - 5, sy - 3), (sx - 5, sy + 4), (sx + 4, sy + 6), (sx + 9, sy)], 0.6, INK)
    d.shape([(sx - 14, sy + 9), (sx + 16, sy + 9), (sx + 22, sy), (sx + 18, sy + 3), (sx + 10, sy + 7)], "#c7b9a0", 0.95, w=0.7)
    d.ink([(sx + 19, sy + 1), (sx + 22, sy - 8)], 0.6, INK)
    d.ink([(sx + 21, sy + 1), (sx + 26, sy - 6)], 0.6, INK)


def em_treasure(d, cx, cy):
    for k in range(18):
        x = cx + d.u(-60, 60)
        y = cy + 44 - abs(x - cx) * 0.25 + d.u(-10, 6)
        d.shape(ellipse_pts(x, y, 8, 4, 14, rot=d.r(0.3)), PAL["gold"], 0.95, w=0.7)
    goblet = [(cx - 18, cy - 50), (cx - 16, cy - 30), (cx - 6, cy - 16), (cx - 4, cy + 10), (cx - 16, cy + 20), (cx + 16, cy + 20),
              (cx + 4, cy + 10), (cx + 6, cy - 16), (cx + 16, cy - 30), (cx + 18, cy - 50)]
    d.shape(goblet, PAL["gold"], 0.95, w=1.2)
    d.ink(ellipse_pts(cx, cy - 50, 18, 4, 16), 1.0, INK, closed=True)
    for gx, gy, c in ((cx - 9, cy - 34, PAL["red"]), (cx + 8, cy - 36, PAL["teal"]), (cx, cy - 26, PAL["blue"])):
        d.shape(ellipse_pts(gx, gy, 3.2, 3.2, 8), c, 0.95, w=0.5)
    for gx, gy, c in ((cx - 40, cy + 34, PAL["red"]), (cx + 36, cy + 30, PAL["teal"]), (cx + 52, cy + 40, PAL["lav"])):
        d.shape([(gx, gy - 6), (gx + 6, gy), (gx, gy + 6), (gx - 6, gy)], c, 0.95, w=0.7, smooth_=False)
    d.ink([(cx - 12, cy - 46), (cx - 10, cy - 34)], 1.2, "#fff1b8")
    for a in (0.6, 2.4):
        d.line(cx + 30 * math.cos(a) * 1.6, cy - 50 + 10 * math.sin(a), cx + 38 * math.cos(a) * 1.6, cy - 56 + 10 * math.sin(a), 0.8, PAL["gold"], 0)


def em_candle(d, cx, cy):
    d.wash(ellipse_pts(cx + 30, cy + 46, 50, 8, 18), PAL["shadow"], 0.3)
    O.candle(d, cx - 6, cy + 46, 46)
    d.ink(ellipse_pts(cx + 30, cy - 30, 20, 20, 18, a0=-1.2, a1=1.6), 0.8, INK_SOFT, op=0.5)
    for k in range(3):
        d.line(cx + 34 + k * 9, cy - 46 + k * 5, cx + 38 + k * 9, cy - 40 + k * 5, 0.8, INK_SOFT, 0)


def em_arrow(d, cx, cy):
    d.wash(ellipse_pts(cx - 30, cy - 34, 13, 13, 16), "#f6e3a0", 0.8)
    d.ink(ellipse_pts(cx - 30, cy - 34, 13, 13, 16, a0=0.9, a1=5.4), 1.2, PAL["gold"])
    for sx, sy in ((cx + 20, cy - 56), (cx - 54, cy + 4), (cx + 44, cy + 6), (cx - 6, cy - 60), (cx + 56, cy - 30)):
        for a in range(4):
            aa = a * math.pi / 2
            d.line(sx, sy, sx + 4 * math.cos(aa), sy + 4 * math.sin(aa), 0.8, PAL["gold"], 0)
    d.wash([(cx - 70, cy + 40), (cx - 20, cy + 30), (cx + 30, cy + 42), (cx + 70, cy + 34), (cx + 70, cy + 70), (cx - 70, cy + 70)], "#5d7a8a", 0.7)
    a = -0.7
    x1, y1, x2, y2 = cx - 58, cy + 48, cx + 50, cy - 40
    d.ink([(x1, y1), (x2, y2)], 2.4, PAL["wooddk"])
    d.shape(transform_pts([(0, -6), (16, 0), (0, 6), (3, 0)], x2, y2, 1, a), "#3a3a3a", 0.95, w=0.8, smooth_=False)
    for k in range(3):
        px, py = x1 + 6 + k * 5, y1 - 5 - k * 4
        d.shape(transform_pts([(0, 0), (-12, -8), (-4, 0), (-12, 8)], px, py, 1, a), "#2f2f2f", 0.95, w=0.6, smooth_=False)


def em_thrush(d, cx, cy):
    d.ink([(cx - 70, cy + 40), (cx - 20, cy + 30), (cx + 40, cy + 34), (cx + 70, cy + 24)], 3, PAL["wooddk"])
    for lx, a in ((cx - 50, -2.4), (cx + 50, -0.9), (cx + 10, 2.3)):
        O.leaf(d, lx, cy + 34, 16, a)
    body = [(cx - 30, cy + 10), (cx - 10, cy - 12), (cx + 16, cy - 16), (cx + 30, cy - 4), (cx + 26, cy + 22), (cx + 4, cy + 30), (cx - 20, cy + 24)]
    d.shape(body, "#9a7a58", 0.92, w=1.1)
    d.wash([(cx - 6, cy + 4), (cx + 22, cy - 2), (cx + 24, cy + 20), (cx + 2, cy + 28)], "#efe0c0", 0.95)
    for k in range(8):
        d.dot(cx + 4 + (k % 3) * 6 + d.r(1), cy + 6 + (k // 3) * 6, 1.4, "#5a4030")
    d.shape([(cx + 14, cy - 16), (cx + 28, cy - 26), (cx + 38, cy - 16), (cx + 32, cy - 6), (cx + 22, cy - 8)], "#9a7a58", 0.95, w=1.0)
    d.dot(cx + 30, cy - 18, 1.6)
    d.shape([(cx + 37, cy - 18), (cx + 46, cy - 16), (cx + 37, cy - 14)], "#d9a94e", 0.95, w=0.6, smooth_=False)
    d.shape([(cx - 28, cy + 10), (cx - 58, cy + 2), (cx - 56, cy + 12), (cx - 24, cy + 20)], "#7a5a3a", 0.92, w=0.9)
    d.ink([(cx - 4, cy - 4), (cx - 22, cy + 4), (cx - 30, cy + 12)], 0.6, INK)
    for fx in (cx - 2, cx + 8):
        d.ink([(fx, cy + 28), (fx, cy + 34)], 1.0, INK)


def em_gem(d, cx, cy):
    d.glow(cx, cy, 70, "#e8f2ff", 0.9)
    for k in range(12):
        a = k * math.pi / 6
        d.line(cx + 36 * math.cos(a), cy + 36 * math.sin(a), cx + 62 * math.cos(a), cy + 62 * math.sin(a), 0.8, PAL["gold"], 0, op=0.7)
    outline = [(cx - 30, cy - 12), (cx - 16, cy - 30), (cx + 16, cy - 30), (cx + 30, cy - 12), (cx, cy + 36)]
    d.shape(outline, "#f4f7fb", 0.95, w=1.2, smooth_=False)
    for a, b in (((cx - 30, cy - 12), (cx + 30, cy - 12)), ((cx - 16, cy - 30), (cx - 8, cy - 12)), ((cx + 16, cy - 30), (cx + 8, cy - 12)),
                 ((cx - 8, cy - 12), (cx, cy + 36)), ((cx + 8, cy - 12), (cx, cy + 36)), ((cx, cy - 30), (cx - 8, cy - 12)), ((cx, cy - 30), (cx + 8, cy - 12))):
        d.line(a[0], a[1], b[0], b[1], 0.7, INK_SOFT, 0)
    d.wash([(cx - 26, cy - 12), (cx - 8, cy - 12), (cx, cy + 30)], "#c6d8ee", 0.7)
    d.wash([(cx + 8, cy - 12), (cx + 28, cy - 12), (cx + 2, cy + 30)], "#e7d6f0", 0.6)


def em_shield(d, cx, cy):
    for a in (-0.6, 0.6):
        x2, y2 = cx + 70 * math.sin(a), cy - 70 * math.cos(a)
        d.ink([(cx - (x2 - cx) * 0.9, cy + (cy - y2) * 0.9), (x2, y2)], 2.2, PAL["wooddk"])
        d.shape(transform_pts([(-5, 0), (0, -14), (5, 0)], x2, y2, 1, a), "#9aa0a6", 0.95, w=0.8, smooth_=False)
    d.shape(ellipse_pts(cx, cy, 46, 46, 30), PAL["wood"], 0.95, w=1.3)
    d.ink(ellipse_pts(cx, cy, 40, 40, 28), 2.4, "#8a8f94", closed=True)
    for k in range(-3, 4):
        h = math.sqrt(max(0, 40 * 40 - (k * 11) ** 2))
        d.line(cx + k * 11, cy - h + 2, cx + k * 11, cy + h - 2, 0.5, INK_SOFT, 0.3)
    d.shape(ellipse_pts(cx, cy, 10, 10, 14), "#b0b5ba", 0.95, w=1.0)
    d.ink(ellipse_pts(cx - 3, cy - 3, 4, 3, 8, a0=3.4, a1=4.6), 1.0, PAL["white"])
    O.cloud(d, cx + 40, cy - 56, 40, 14)


def em_pack(d, cx, cy):
    d.ink([(cx + 40, cy - 66), (cx + 30, cy + 60)], 3.2, PAL["wooddk"])
    d.ink(ellipse_pts(cx + 46, cy - 62, 7, 7, 10, a0=math.pi, a1=2.2 * math.pi), 3.2, PAL["wooddk"])
    pack = [(cx - 40, cy + 54), (cx - 46, cy - 6), (cx - 30, cy - 34), (cx + 14, cy - 36), (cx + 26, cy - 6), (cx + 22, cy + 54)]
    d.shape(pack, "#9a7a4a", 0.92, w=1.2)
    d.shape([(cx - 40, cy - 22), (cx - 34, cy - 40), (cx + 18, cy - 40), (cx + 24, cy - 22), (cx - 8, cy - 4)], "#7d5f38", 0.95, w=1.1)
    d.shape(rect_pts(cx - 12, cy - 12, 8, 12), PAL["brass"], 0.95, w=0.7, smooth_=False)
    d.ink([(cx - 30, cy + 10), (cx + 14, cy + 10)], 1.6, "#5a3e22")
    O.ham(d, cx - 46, cy - 10, 0.0001) if False else None
    d.shape(blob(cx - 6, cy + 64, 54, 6, d.rng, 0.1, 12), PAL["grass"], 0.8, w=0)
    # bedroll on top
    d.shape(rect_pts(cx - 40, cy - 54, 60, 16, 10), PAL["red"], 0.92, w=1.0)
    d.ink(ellipse_pts(cx + 20, cy - 46, 4, 8, 10), 0.8, INK, closed=True)
    O.tufts(d, [(cx - 60, cy + 64), (cx + 50, cy + 64)], every=6, h=8, flowers=0.2)


def em_door(d, cx, cy):
    hill = [(cx - 76, cy + 60), (cx - 70, cy - 10), (cx - 40, cy - 52), (cx, cy - 64), (cx + 40, cy - 52), (cx + 70, cy - 10), (cx + 76, cy + 60)]
    d.shape(hill, PAL["grass"], 0.92, w=1.1)
    O.round_door(d, cx, cy + 6, 38)
    O.tufts(d, hill[1:6], every=6, h=7, flowers=0.25)
    d.shape(rect_pts(cx - 30, cy + 48, 60, 8), PAL["stone"], 0.9, w=0.8, smooth_=False)
    O.lantern(d, cx + 52, cy - 22, 0.9)
    O.smoke(d, cx + 30, cy - 70, 20, 5)
    d.shape(rect_pts(cx + 24, cy - 76, 12, 14), "#b9704e", 0.95, w=0.9, smooth_=False)


EMBLEMS = [em_teapot, em_campfire, em_book, em_lantern_cave, em_ring, em_feather, em_honey, em_web, em_barrel,
           em_boat, em_key, em_treasure, em_candle, em_arrow, em_thrush, em_gem, em_shield, em_pack, em_door]


# ================================================================= banner
def bramble_branch(d, x0, y0, x1, y1, direction, seed_shift=0):
    """A curving bramble stem with leaves, flowers and berries."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + math.sin(t * math.pi * 2.2) * 10
        pts.append((x, y))
    d.ink(pts, 2.4, "#7a4a3a")
    d.ink(pts, 0.8, INK)
    for i in range(1, n):
        x, y = pts[i]
        if i % 2 == 0:
            for k in range(2):
                d.line(x + k * 3, y - 1, x + k * 3 + 1.5 * direction, y - 4, 0.6, INK, 0)
        side = -1 if i % 2 else 1
        a = (-math.pi / 2 if side < 0 else math.pi / 2) + d.r(0.5) + (0.3 * direction)
        if d.chance(0.8):
            leaf_cluster(d, x, y, a)
        if i % 4 == 1:
            berry_cluster(d, x + 6 * direction, y + 10)
        elif i % 4 == 3:
            O.flower(d, x + 4 * direction, y - 10, 5, "pink")


def leaf_cluster(d, x, y, a):
    for k in (-0.5, 0, 0.5):
        L = 16 if k == 0 else 12
        aa = a + k
        O.leaf(d, x + 4 * math.cos(aa), y + 4 * math.sin(aa), L, aa, wdt=0.55, ink_w=0.6)


def berry_cluster(d, x, y, s=1.0):
    for k in range(5):
        bx = x + (k % 3 - 1) * 4.4 * s + d.r(1)
        by = y + (k // 3) * 4.4 * s + d.r(1)
        col = d.choice([PAL["berry"], "#2f2238", PAL["berry"], PAL["red"]])
        d.shape(ellipse_pts(bx, by, 3 * s, 3 * s, 8), col, 0.95, w=0.5)
        d.dot(bx - 0.9 * s, by - 0.9 * s, 0.7 * s, PAL["white"], 0.8)


def chapter_header(path, chapter_idx, numeral):
    d = Doc(5.5, 2.0, seed=100 + chapter_idx, paper=False)
    W, H = 550, 200
    cx, cy = W / 2, 94
    bramble_branch(d, cx - 70, cy + 10, 30, cy - 4, -1)
    bramble_branch(d, cx + 70, cy + 10, W - 30, cy - 4, 1)
    # roundel
    d.shape(ellipse_pts(cx, cy, 82, 82, 40), "#fbf4e2", 0.98, w=1.6)
    d.ink(ellipse_pts(cx, cy, 76, 76, 40), 0.8, INK_SOFT, closed=True)
    for k in range(24):
        a = 2 * math.pi * k / 24
        d.dot(cx + 79 * math.cos(a), cy + 79 * math.sin(a), 1.0, PAL["berry"])
    # emblem drawn into the roundel, clipped
    s = 0.9
    d.push_clip(ellipse_pts(cx, cy, 75, 75, 40))
    d.push_transform(cx - 80 * s, cy - 80 * s, s)
    EMBLEMS[chapter_idx](d, 80, 80)
    d.pop_transform()
    d.pop_clip()
    # numeral ribbon
    rib = [(cx - 34, cy + 70), (cx + 34, cy + 70), (cx + 40, cy + 82), (cx + 34, cy + 94), (cx - 34, cy + 94), (cx - 40, cy + 82)]
    d.shape(rib, "#efe2c2", 0.98, w=1.0, smooth_=False)
    d.text(cx, cy + 88, numeral, size=15, family="IM Fell English SC")
    d.save(path)


def emblem(path, idx):
    d = Doc(1.6, 1.6, seed=300 + idx, paper=False)
    EMBLEMS[idx](d, 80, 80)
    d.save(path)


# ================================================================ critters
# Small natural-history studies: drawn as a naturalist would, not as cartoons.
import detail as D  # noqa: E402


def _leaf_veined(d, x, y, L, ang, col=None, wdt=0.5, serr=True):
    col = col or d.choice(D.LEAF_MID)
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        w = math.sin(math.pi * t) ** 0.85 * L * wdt / 2 * (1 + (0.06 if serr and i % 2 else 0))
        pts.append((t * L, w))
    for i in range(n - 1, 0, -1):
        t = i / n
        w = math.sin(math.pi * t) ** 0.85 * L * wdt / 2 * (1 + (0.06 if serr and i % 2 else 0))
        pts.append((t * L, -w))
    P = transform_pts(pts, x, y, 1, ang)
    d.shape(P, col, 0.88, w=0.5, shade=0.6)
    d.ink(transform_pts([(0, 0), (L * 0.5, 0.4), (L * 0.95, 0)], x, y, 1, ang), 0.4, INK_SOFT, op=0.8)
    for k in range(1, 6):
        t = k / 6.5
        for sgn in (-1, 1):
            d.ink(transform_pts([(L * t, 0), (L * (t + 0.12), sgn * L * wdt * 0.32 * math.sin(math.pi * t))], x, y, 1, ang), 0.3, INK_SOFT, op=0.6)


def cr_snail(d):
    x, y = 40, 34
    d.shape(ellipse_pts(x, y, 15, 13.5, 30), "#d8b27a", 0.92, w=0.8, shade=0.8)
    for band, col in ((0.85, "#7a4a2a"), (0.55, "#9a6a3a"), (0.3, "#7a4a2a")):
        d.ink([(x + 15 * band * (1 - t / 40) * math.cos(t * 0.33), y + 13.5 * band * (1 - t / 40) * math.sin(t * 0.33)) for t in range(0, 30)],
              1.6, col, op=0.7)
    d.ink([(x + (t / 3.2) * math.cos(t * 0.75), y + (t / 3.6) * math.sin(t * 0.75)) for t in range(1, 44)], 0.6, INK)
    d.ink(ellipse_pts(x - 5, y - 6, 4, 2.5, 8, a0=3.3, a1=4.8), 1.0, "#fff4dc", op=0.8)
    body = [(18, 48), (30, 47), (56, 48), (68, 45), (78, 36), (75, 40), (64, 44)]
    d.shape(body + [(40, 50), (20, 50)], "#cdbb9c", 0.92, w=0.6, shade=0.6)
    for k in range(12):
        d.dot(26 + k * 4, 48 + d.r(1), 0.35, INK_SOFT, 0.7)
    for ex, ey, tx, ty in ((74, 38, 77, 24), (77, 39, 84, 27)):
        d.ink([(ex, ey), ((ex + tx) / 2 + 1, (ey + ty) / 2), (tx, ty)], 0.6, "#8a7a62")
        d.dot(tx, ty, 1.1, "#4a3a2a")
    d.ink([(4, 51), (20, 50.5)], 0.6, "#c7d6dc", op=0.8)


def cr_ladybird(d):
    _leaf_veined(d, 6, 46, 74, -0.32, "#86a557", 0.42)
    x, y = 46, 31
    d.shape(ellipse_pts(x, y, 11, 9, 24), "#c8382c", 0.95, w=0.7, shade=0.8)
    d.line(x, y - 9, x + 1, y + 9, 0.6, INK, 0)
    for sx, sy, r in ((-5, -3, 2.0), (5, -2, 2.0), (-4, 4, 1.6), (6, 4, 1.6), (0, -6, 1.3)):
        d.wash(ellipse_pts(x + sx, y + sy, r, r, 10), "#2a2220", 0.92)
    d.shape(ellipse_pts(x + 11, y + 1, 4.2, 4.8, 12), "#2a2220", 0.95, w=0.5)
    d.dot(x + 12, y - 1.5, 0.9, "#f3efe6")
    d.ink(ellipse_pts(x - 4, y - 5, 4, 2, 8, a0=3.4, a1=4.7), 1.0, "#ffffff", op=0.85)
    for k in range(3):
        d.ink([(x - 4 + k * 4, y + 8), (x - 6 + k * 4, y + 12)], 0.45, INK)


def cr_bee(d):
    x, y = 46, 36
    for k, (col, w_) in enumerate((("#2a2420", 9), ("#e3b43a", 10), ("#2a2420", 10), ("#e3b43a", 9), ("#f1e8d8", 7))):
        cx = x - 14 + k * 6.5
        d.wash(ellipse_pts(cx, y, 5, w_, 14), col, 0.9, shade=0.6, hatch=False)
        for _ in range(28):
            a = d.u(0, 2 * math.pi)
            r0 = d.u(0.3, 0.95)
            px, py = cx + 4 * r0 * math.cos(a), y + w_ * r0 * math.sin(a)
            d.ink([(px, py), (px + 2.2 * math.cos(a), py + 2.2 * math.sin(a))], 0.35, col if col != "#f1e8d8" else "#b9ab90", op=0.85, jitter=0.1)
    d.shape(ellipse_pts(x - 20, y + 1, 5, 6, 12), "#2a2420", 0.95, w=0.5)
    d.dot(x - 22, y - 1, 0.8, "#f3efe6")
    for k in (-1, 1):
        d.ink([(x - 23, y - 3), (x - 28, y - 9 - k), (x - 31, y - 8 - k * 2)], 0.45, INK)
    for k, (wx, wy, rot) in enumerate(((x - 4, y - 14, -0.5), (x + 4, y - 13, -0.15))):
        wing = ellipse_pts(wx, wy, 11, 5, 18, rot=rot)
        d.wash(wing, "#e6eef2", 0.55, hatch=False, edge=0.8)
        d.ink(wing, 0.35, INK_SOFT, True, op=0.7)
        d.ink([(wx - 8 * math.cos(rot), wy - 8 * math.sin(rot)), (wx + 6 * math.cos(rot), wy + 6 * math.sin(rot) + 2)], 0.25, INK_SOFT, op=0.6)
    for k in range(3):
        d.ink([(x - 10 + k * 6, y + 9), (x - 12 + k * 6, y + 15), (x - 14 + k * 6, y + 17)], 0.45, INK)


def cr_butterfly(d):
    cx, cy = 45, 34
    for sgn in (-1, 1):
        fw = transform_pts([(0, 0), (8, -12), (20, -20), (26, -14), (22, -2), (6, 2)], cx, cy - 2, 1, 0) if sgn > 0 else \
            transform_pts([(0, 0), (-8, -12), (-20, -20), (-26, -14), (-22, -2), (-6, 2)], cx, cy - 2, 1, 0)
        hw = [(cx, cy), (cx + sgn * 6, cy + 2), (cx + sgn * 16, cy + 6), (cx + sgn * 15, cy + 15), (cx + sgn * 8, cy + 16), (cx + sgn * 2, cy + 8)]
        d.shape(fw, "#c75a32", 0.9, w=0.6, shade=0.5)
        d.shape(hw, "#b8503a", 0.9, w=0.6, shade=0.5)
        # eye-spots and dark margins like a peacock butterfly
        ex, ey = cx + sgn * 18, cy - 13
        d.wash(ellipse_pts(ex, ey, 4.4, 3.6, 14), "#2f2a3a", 0.9)
        d.wash(ellipse_pts(ex, ey, 2.8, 2.2, 12), "#6f86b8", 0.9)
        d.dot(ex, ey, 0.9, "#f3efe6")
        hx, hy = cx + sgn * 11, cy + 10
        d.wash(ellipse_pts(hx, hy, 3.6, 3.0, 12), "#2f2a3a", 0.85)
        d.wash(ellipse_pts(hx, hy, 2.0, 1.6, 10), "#7f94c8", 0.85)
        for k in range(4):
            d.ink([(cx + sgn * 2, cy - 1), (cx + sgn * (10 + k * 4), cy - 8 - k * 3)], 0.3, INK_SOFT, op=0.6)
        d.ink(fw[2:5], 1.4, "#3a2a26", op=0.6)
    d.shape(ellipse_pts(cx, cy + 3, 1.8, 9, 12), "#3a2e28", 0.95, w=0.4)
    for sgn in (-1, 1):
        d.ink([(cx, cy - 5), (cx + sgn * 5, cy - 15), (cx + sgn * 7, cy - 19)], 0.4, INK)
        d.dot(cx + sgn * 7, cy - 19, 0.8)


def cr_beetle(d):
    cx, cy = 45, 36
    for k in range(3):
        for sgn in (-1, 1):
            d.ink([(cx + sgn * 6, cy - 3 + k * 6), (cx + sgn * 13, cy - 6 + k * 7), (cx + sgn * 17, cy + k * 8)], 0.6, INK)
    d.shape(ellipse_pts(cx, cy + 4, 10, 14, 26), "#3f6150", 0.94, w=0.7, shade=0.9)
    d.line(cx, cy - 9, cx, cy + 18, 0.6, INK, 0)
    for k in range(4):
        d.ink([(cx - 6 + k * 1.2, cy - 6), (cx - 6.5 + k * 1.2, cy + 14)], 0.3, "#9fc0aa", op=0.6)
        d.ink([(cx + 2.5 + k * 1.2, cy - 6), (cx + 2 + k * 1.2, cy + 14)], 0.3, "#9fc0aa", op=0.6)
    d.shape(ellipse_pts(cx, cy - 12, 6, 4.6, 14), "#2f4a3c", 0.95, w=0.6)
    d.shape(ellipse_pts(cx, cy - 17.5, 3.5, 2.8, 10), "#2a3a32", 0.95, w=0.5)
    for sgn in (-1, 1):
        d.ink([(cx + sgn * 2, cy - 19), (cx + sgn * 5, cy - 25), (cx + sgn * 8, cy - 27)], 0.4, INK)
    d.ink(ellipse_pts(cx - 4, cy - 2, 3, 6, 10, a0=3.4, a1=4.8), 1.2, "#d6ecd8", op=0.7)


def cr_acorns(d):
    d.ink([(12, 14), (34, 20), (58, 17)], 1.4, "#7a5534")
    O.oak_leaf(d, 52, 16, 30, 0.25, "#93a85a")
    O.oak_leaf(d, 20, 16, 22, -2.6, "#b9a14b")
    O.acorn(d, 30, 29, 1.3, 0.2)
    O.acorn(d, 46, 33, 1.2, -0.3)


def cr_mushrooms(d):
    O.mushroom(d, 34, 58, 1.6, PAL["red"])
    O.mushroom(d, 58, 58, 1.0, "#c8894a", lean=0.3)
    d.shape(blob(48, 59, 30, 2.5, d.rng, 0.1, 12), "#9a8a5a", 0.6, w=0)
    D.blades(d, [(14, 59), (80, 59)], every=2.0, h=(3, 8))


def cr_berries(d):
    d.ink([(8, 18), (30, 24), (52, 20), (80, 28)], 1.6, "#8a4a4a")
    for k in range(6):
        d.ink([(12 + k * 11, 21 + (k % 2)), (13 + k * 11, 19)], 0.5, "#8a4a4a")
    _leaf_veined(d, 24, 23, 22, -1.9, d.choice(D.LEAF_MID), 0.55)
    _leaf_veined(d, 58, 22, 20, -1.0, d.choice(D.LEAF_DARK), 0.55)
    for bx, by, ripe in ((36, 36, 1.0), (50, 34, 1.0), (68, 40, 0.5), (22, 36, 0.0)):
        d.ink([(bx, by - 8), (bx, by - 3)], 0.5, "#6b8c45")
        for k in range(10):
            a = k * 2 * math.pi / 7
            r_ = 2.4 if k < 7 else 0
            px, py = bx + r_ * math.cos(a) + d.r(0.4), by + r_ * math.sin(a) * 1.15 + (k - 7) * 1.6 * (k >= 7)
            col = "#3a2238" if ripe > 0.8 else ("#a8334a" if ripe > 0.3 else "#b9c46a")
            d.shape(ellipse_pts(px, py, 1.9, 1.9, 10), col, 0.95, w=0.3, shade=0.8)
            d.dot(px - 0.6, py - 0.7, 0.45, "#ffffff", 0.85)
    O.flower(d, 76, 18, 5, "pink")


def cr_daisies(d):
    for x, y, h in ((26, 20, 40), (46, 28, 32), (64, 18, 42)):
        d.ink([(x, y), (x + d.r(3), y + h * 0.5), (x + d.r(2), 60)], 0.9, "#6b8c45")
        D.wildflower(d, x, y + 0.5, "daisy", 2.3) if False else None
        for k in range(13):
            a = k * 2 * math.pi / 13
            p = D.leaf_shape(x, y, 7, a, 0.36, 5)
            d.wash(p, "#fffdf6", 1.0, jitter=0.05)
            d.ink(p, 0.3, "#9a8f7a", True, op=0.6, jitter=0.05)
            if k % 3 == 0:
                d.ink([(x + 2 * math.cos(a), y + 2 * math.sin(a)), (x + 6 * math.cos(a), y + 6 * math.sin(a))], 0.4, "#e9a8b0", op=0.6)
        d.shape(ellipse_pts(x, y, 2.4, 2.4, 12), "#e3b43a", 0.95, w=0.4, shade=0.8)
    _leaf_veined(d, 40, 58, 14, -2.6, None, 0.4)
    _leaf_veined(d, 50, 58, 14, -0.5, None, 0.4)


def cr_bluebells(d):
    stem = [(30, 62), (34, 34), (44, 16), (58, 12)]
    d.ink(stem, 1.0, "#6b8c45")
    for k, (x, y) in enumerate(((40, 22), (46, 18), (52, 15), (36, 30), (34, 40))):
        d.ink([(x, y), (x + 3, y + 6)], 0.5, "#6b8c45")
        bell = [(x - 1, y + 5), (x - 2, y + 13), (x + 0.5, y + 15.5), (x + 3, y + 13.5), (x + 5.5, y + 15.5), (x + 8, y + 12), (x + 6, y + 5)]
        d.shape(bell, "#6f86c8", 0.9, w=0.5, shade=0.8)
        d.ink([(x + 2, y + 7), (x + 2.5, y + 13)], 0.3, "#3a4a7a", op=0.6)
    O.leaf(d, 30, 62, 34, -1.3, "#7d9d50", wdt=0.2)
    O.leaf(d, 32, 62, 30, -1.9, "#5e7e3e", wdt=0.2)


def cr_fern(d):
    spine = [(14, 60), (30, 40), (50, 24), (76, 14)]
    d.ink(spine, 1.0, "#6b8c45")
    for k in range(1, 12):
        t = k / 12
        x = 14 + 62 * t
        y = 60 - 46 * t + 4 * math.sin(t * 3)
        L = 15 * (1 - t * 0.7)
        for sgn, base in ((-1, -2.2), (1, 0.4)):
            a = base
            for j in range(4):
                tt = (j + 1) / 5
                px, py = x + L * tt * math.cos(a), y + L * tt * math.sin(a)
                d.wash(D.leaf_shape(px, py, L * 0.28, a + sgn * 1.2, 0.6, 4), d.choice(D.LEAF_MID + D.LEAF_LIGHT), 0.88, jitter=0.05)
            d.ink([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], 0.35, "#6b8c45", op=0.9)


def cr_oakleaf(d):
    O.oak_leaf(d, 14, 40, 56, -0.4, "#c9a14b")
    d.wash(ellipse_pts(36, 34, 8, 5, 12), "#a8743f", 0.35, soft=True)
    O.acorn(d, 66, 46, 1.1, 0.4)


def cr_feather(d):
    spine = lambda t: (12 + 64 * t, 60 - 50 * t + 4 * math.sin(t * 3))  # noqa: E731
    left, right = [], []
    for k in range(0, 31):
        t = k / 30
        x, y = spine(t)
        w = 10 * math.sin(math.pi * min(1, t * 1.08)) + 0.5
        left.append((x - w * 0.55, y - w * 0.85))
        right.append((x + w * 0.62, y + w * 0.7))
    d.shape([spine(0)] + left + [spine(1)] + right[::-1], "#a07a52", 0.9, w=0.6, shade=0.7)
    for k in range(3, 29, 4):       # darker bars across the vane
        t = k / 30
        x, y = spine(t)
        w = 10 * math.sin(math.pi * min(1, t * 1.08))
        d.wash([(x - w * 0.55, y - w * 0.85), (x - w * 0.4 + 2.5, y - w * 0.85 - 1.5), (x + w * 0.62 + 2.5, y + w * 0.7 - 1.5),
                (x + w * 0.62, y + w * 0.7)], "#5a4030", 0.55, jitter=0.2, hatch=False)
    for k in range(1, 30):
        t = k / 30
        x, y = spine(t)
        w = 10 * math.sin(math.pi * min(1, t * 1.08))
        d.ink([(x, y), (x - w * 0.55, y - w * 0.85)], 0.3, "#4a3426", op=0.5, jitter=0.05)
        d.ink([(x, y), (x + w * 0.62, y + w * 0.7)], 0.3, "#4a3426", op=0.5, jitter=0.05)
    for k in range(6):
        d.ink([(13 + k, 58 - k * 1.2), (10 + k * 1.5, 52 - k)], 0.4, "#c9b9a0", op=0.8)
    d.ink([spine(t / 20) for t in range(21)], 0.9, "#efe4cc")


def cr_strawberries(d):
    d.ink([(10, 60), (24, 40), (40, 28)], 0.8, "#6b8c45")
    for k, (lx, ly, a) in enumerate(((40, 28, -1.2), (40, 28, -0.4), (40, 28, 0.4))):
        _leaf_veined(d, lx, ly, 18, a, None, 0.62)
    for bx, by in ((22, 44), (34, 50), (14, 52)):
        d.ink([(24, 40), (bx, by - 6)], 0.5, "#6b8c45")
        berry = [(bx - 4, by - 5), (bx + 4, by - 5), (bx + 3.5, by + 1), (bx, by + 6), (bx - 3.5, by + 1)]
        d.shape(berry, "#d23c35", 0.95, w=0.5, shade=0.8)
        for k in range(10):
            d.dot(bx + d.r(3), by + d.u(-4, 3), 0.35, "#f6e7a6", 0.95)
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.6
            d.ink([(bx, by - 5), (bx + 4 * math.cos(a + math.pi), by - 5 + 2.5 * math.sin(a + math.pi))], 0.6, "#5e7e3e")
    d.dot(28, 37, 1.6, "#ffffff")
    for k in range(5):
        a = k * 2 * math.pi / 5
        d.wash(ellipse_pts(54 + 2.4 * math.cos(a), 46 + 2.4 * math.sin(a), 2.2, 2.2, 8), "#fffdf6", 1.0, jitter=0.05)
    d.dot(54, 46, 0.9, "#e3c43a")


def cr_rosehips(d):
    d.ink([(8, 52), (34, 34), (60, 26), (82, 20)], 1.4, "#7a4a3a")
    for k in range(5):
        x = 16 + k * 14
        d.ink([(x, 47 - k * 5.5), (x - 1, 44 - k * 5.5)], 0.5, "#7a4a3a")
    for (hx, hy) in ((30, 46), (52, 38), (70, 32)):
        d.ink([(hx, hy - 9), (hx - 1, hy - 4)], 0.5, "#6b5a3a")
        d.shape(ellipse_pts(hx, hy, 4, 6, 16), "#d0472f", 0.95, w=0.5, shade=0.8)
        d.dot(hx - 1.2, hy - 2, 0.8, "#ffffff", 0.85)
        for k in range(4):
            d.ink([(hx, hy + 6), (hx - 3 + k * 2, hy + 9)], 0.4, "#3a2a20")
    _leaf_veined(d, 40, 30, 14, -1.3, None, 0.55)
    _leaf_veined(d, 64, 25, 12, -2.0, None, 0.55)


def cr_hazelnuts(d):
    for (hx, hy, a) in ((32, 38, -0.3), (52, 42, 0.4)):
        husk = transform_pts([(-9, -4), (-6, -11), (0, -14), (6, -11), (9, -4), (5, -6), (0, -9), (-5, -6)], hx, hy, 1, a)
        nut = ellipse_pts(hx, hy + 2, 7.5, 8.5, 22, rot=a)
        d.shape(nut, "#a8743f", 0.94, w=0.6, shade=0.8)
        d.wash(ellipse_pts(hx + 1, hy + 7, 4.5, 2.5, 12, rot=a), "#d8c39a", 0.9)
        for k in range(4):
            d.ink([(hx - 4 + k * 2.5, hy - 3), (hx - 3.5 + k * 2.5, hy + 7)], 0.3, "#6e4a2c", op=0.6)
        d.shape(husk, "#9db06a", 0.9, w=0.6, shade=0.5)
    _leaf_veined(d, 20, 22, 28, -0.3, None, 0.75)


def cr_dragonfly(d):
    cx, cy = 34, 30
    for k in range(9):
        d.shape(ellipse_pts(cx + 6 + k * 4.4, cy + 2 + k * 0.5, 2.2, 1.6, 10), "#3f7f9a" if k % 2 else "#4f9ab0", 0.92, w=0.35)
    d.shape(ellipse_pts(cx, cy, 4, 3.2, 12), "#3f7f9a", 0.95, w=0.5, shade=0.7)
    d.shape(ellipse_pts(cx - 5, cy - 0.5, 2.8, 2.8, 10), "#2f6a80", 0.95, w=0.5)
    d.dot(cx - 6, cy - 1.5, 0.7, "#ffffff")
    for (dx, dy, L, a) in ((0, -1, 26, -1.9), (0, -1, 24, -1.35), (2, 1, 24, 1.95), (2, 1, 22, 1.4)):
        wing = D.leaf_shape(cx + dx, cy + dy, L, a, 0.26, 8)
        d.wash(wing, "#e3eef0", 0.5, hatch=False, edge=0.9)
        d.ink(wing, 0.3, INK_SOFT, True, op=0.7)
        for k in range(1, 6):
            t = k / 6
            px, py = cx + dx + L * t * math.cos(a), cy + dy + L * t * math.sin(a)
            d.ink([(px - 2 * math.cos(a + 1.57), py - 2 * math.sin(a + 1.57)), (px + 2 * math.cos(a + 1.57), py + 2 * math.sin(a + 1.57))], 0.2, INK_SOFT, op=0.5)


CRITTERS = [cr_snail, cr_ladybird, cr_bee, cr_butterfly, cr_beetle, cr_acorns, cr_mushrooms, cr_berries, cr_daisies,
            cr_bluebells, cr_fern, cr_oakleaf, cr_feather, cr_strawberries, cr_rosehips, cr_hazelnuts, cr_dragonfly]


def critter(path, idx):
    d = Doc(0.9, 0.7, seed=400 + idx, paper=False)
    d.push_transform(0, 0, 1.0)
    CRITTERS[idx](d)
    d.save(path)


# ============================================================== ornaments
def tailpiece(path):
    d = Doc(2.4, 0.7, seed=501, paper=False)
    bramble_branch(d, 120, 36, 20, 32, -1)
    bramble_branch(d, 120, 36, 220, 32, 1)
    berry_cluster(d, 120, 40, 1.4)
    d.save(path)


def section_break(path):
    d = Doc(1.4, 0.4, seed=502, paper=False)
    for x in (40, 70, 100):
        O.acorn(d, x, 18, 0.9, d.r(0.3))
    d.save(path)


def dropcap(path, letter, idx=0):
    d = Doc(1.0, 1.0, seed=600 + idx, paper=False)
    frame = rect_pts(6, 6, 88, 88, 10)
    d.shape(frame, "#efe2c2", 0.95, w=1.4, smooth_=False)
    d.ink(rect_pts(11, 11, 78, 78, 10), 0.7, INK_SOFT, closed=True, smooth_=False)
    # vine creeping along the left and bottom edges only (keeps the letter clear)
    edge = [(8, 20), (6, 50), (9, 80), (20, 93), (50, 95), (82, 92)]
    d.ink(edge, 1.6, "#7a4a3a", op=0.8)
    for k, (x, y) in enumerate(edge[1:-1]):
        O.leaf(d, x, y, 10, (2.6 if k < 2 else 1.2) + d.r(0.3), wdt=0.5, ink_w=0.5)
    berry_cluster(d, 14, 84, 0.8)
    berry_cluster(d, 86, 14, 0.7)
    d.text(50, 78, letter, size=72, color="#7a2f2a", family="IM Fell French Canon")
    d.save(path)


def corner_vine(path):
    d = Doc(1.2, 1.2, seed=503, paper=False)
    pts = [(4, 116), (10, 70), (30, 34), (70, 10), (116, 4)]
    d.ink(pts, 1.8, "#7a4a3a")
    for i, (x, y) in enumerate(pts[1:-1]):
        leaf_cluster(d, x, y, -0.4 + i * 0.5)
    berry_cluster(d, 40, 40, 1.0)
    O.flower(d, 16, 96, 5, "pink")
    d.save(path)
