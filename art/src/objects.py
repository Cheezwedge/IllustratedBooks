"""Reusable hand-drawn objects. Every function draws onto a kit.Doc."""
import math
from kit import (PAL, INK, INK_SOFT, smooth, poly, ellipse_pts, blob, rect_pts, arch_pts,
                 line_pts, inside, bez_pts, transform_pts, lerp)


# ===================================================================== nature
def pebbles(d, polygon, n, rmin=3, rmax=9, colors=None):
    colors = colors or [PAL["stone"], PAL["stone2"], PAL["clay"], "#cfc2ad"]
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    placed = 0
    tries = 0
    while placed < n and tries < n * 30:
        tries += 1
        x, y = d.u(min(xs), max(xs)), d.u(min(ys), max(ys))
        if not inside((x, y), polygon):
            continue
        r = d.u(rmin, rmax)
        pts = blob(x, y, r, r * d.u(0.55, 0.85), d.rng, 0.18, 9, rot=d.r(0.6))
        d.shape(pts, d.choice(colors), 0.8, w=0.8, ink_color=INK_SOFT)
        if r > 5:
            d.ink(ellipse_pts(x - r * 0.25, y - r * 0.25, r * 0.4, r * 0.2, 6, a0=3.4, a1=4.6), 0.5, PAL["white"], op=0.7)
        placed += 1


def soil_texture(d, polygon, n=120, color=None):
    color = color or PAL["earthdk"]
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    for _ in range(n):
        x, y = d.u(min(xs), max(xs)), d.u(min(ys), max(ys))
        if inside((x, y), polygon):
            if d.chance(0.6):
                L = d.u(2, 6)
                a = d.r(0.5)
                d.ink([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], 0.5, color, op=0.55, smooth_=False)
            else:
                d.dot(x, y, d.u(0.5, 1.1), color, 0.5)


def mottle(d, polygon, colors, n=14, rmin=20, rmax=60, op=0.25):
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    for _ in range(n):
        x, y = d.u(min(xs), max(xs)), d.u(min(ys), max(ys))
        if inside((x, y), polygon):
            r = d.u(rmin, rmax)
            d.wash(blob(x, y, r, r * 0.6, d.rng, 0.25, 10), d.choice(colors), op, soft=True)


def root(d, x, y, ang, length, w, depth=3, color=None, avoid=None, ymin=None):
    """Recursive organic root. ang in radians (pi/2 = straight down)."""
    color = color or PAL["root"]
    pts = [(x, y)]
    cx, cy, a = x, y, ang
    seg = length / 8
    for i in range(8):
        a += d.r(0.35)
        cx += seg * math.cos(a)
        cy += seg * math.sin(a)
        if avoid and any(inside((cx, cy), poly_) for poly_ in avoid):
            a += 0.9 * (1 if d.chance(0.5) else -1)
            cx += seg * math.cos(a) * 0.3
            cy += seg * math.sin(a) * 0.3
        if ymin and cy < ymin(cx) + 6:
            cy = ymin(cx) + 6
            a = math.pi / 2 + d.r(0.6)
        pts.append((cx, cy))
    # tapered: draw as wash band + ink edges
    if w > 2.2:
        left, right = [], []
        for i, (px, py) in enumerate(pts):
            t = i / (len(pts) - 1)
            ww = w * (1 - t * 0.8) / 2
            if i < len(pts) - 1:
                nx, ny = pts[i + 1][0] - px, pts[i + 1][1] - py
            else:
                nx, ny = px - pts[i - 1][0], py - pts[i - 1][1]
            L = math.hypot(nx, ny) or 1
            ox, oy = -ny / L * ww, nx / L * ww
            left.append((px + ox, py + oy))
            right.append((px - ox, py - oy))
        band = left + right[::-1]
        d.wash(band, color, 0.85, jitter=0.4)
        d.ink(left, 0.7, INK, op=0.85)
        d.ink(right, 0.7, INK, op=0.85)
    else:
        d.ink(pts, max(0.5, w * 0.6), color, op=0.9)
        d.ink(pts, max(0.4, w * 0.25), INK, op=0.6)
    if depth > 0:
        for i in (2, 4, 6):
            if d.chance(0.75):
                bx, by = pts[i]
                root(d, bx, by, a + d.choice([-1, 1]) * d.u(0.4, 1.0), length * d.u(0.35, 0.6),
                     w * 0.5, depth - 1, color, avoid, ymin)
    # root hairs
    if depth == 0:
        for _ in range(3):
            i = d.rng.randrange(1, len(pts))
            px, py = pts[i]
            aa = a + d.r(1.4)
            d.ink([(px, py), (px + 5 * math.cos(aa), py + 5 * math.sin(aa))], 0.4, INK_SOFT, op=0.6, smooth_=False)


def grass_band(d, surface, depth=24, color=None):
    """Green turf band hanging below a surface polyline (list of (x,y) left->right)."""
    color = color or PAL["grass"]
    lower = [(x + d.r(2), y + depth + d.r(4)) for x, y in surface[::-1]]
    d.wash(surface + lower, color, 0.85, jitter=1)


def tufts(d, surface, every=6, h=10, color=None, flowers=0.0):
    color = color or PAL["grass2"]
    for i in range(len(surface) - 1):
        (x1, y1), (x2, y2) = surface[i], surface[i + 1]
        L = math.hypot(x2 - x1, y2 - y1)
        k = max(1, int(L / every))
        for j in range(k):
            t = j / k
            x, y = lerp(x1, x2, t), lerp(y1, y2, t)
            hh = h * d.u(0.5, 1.3)
            a = -math.pi / 2 + d.r(0.45)
            tip = (x + hh * math.cos(a), y + hh * math.sin(a))
            mid = (x + hh * 0.5 * math.cos(a) + d.r(1.5), y + hh * 0.5 * math.sin(a))
            d.ink([(x, y + 1), mid, tip], d.u(0.5, 0.9), d.choice([color, PAL["leafdk"], PAL["grass"]]), op=0.9)
            if flowers and d.chance(flowers):
                flower(d, tip[0], tip[1], d.u(2.2, 3.6))


def flower(d, x, y, r, kind=None):
    kind = kind or d.choice(["daisy", "daisy", "butter", "blue", "pink", "clover"])
    if kind == "daisy":
        for k in range(7):
            a = k * 2 * math.pi / 7 + d.r(0.2)
            d.shape(blob(x + r * 0.9 * math.cos(a), y + r * 0.9 * math.sin(a), r * 0.55, r * 0.3, d.rng, 0.1, 8, rot=a),
                    PAL["white"], 0.95, w=0.4, ink_color=INK_SOFT)
        d.shape(blob(x, y, r * 0.45, r * 0.45, d.rng, 0.1, 8), PAL["gold"], 1, w=0.4)
    elif kind == "butter":
        for k in range(5):
            a = k * 2 * math.pi / 5
            d.shape(blob(x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a), r * 0.55, r * 0.5, d.rng, 0.1, 8),
                    "#efcf45", 0.95, w=0.4, ink_color=INK_SOFT)
    elif kind == "blue":
        for k in range(5):
            a = k * 2 * math.pi / 5
            d.wash(blob(x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a), r * 0.45, r * 0.45, d.rng, 0.1, 8),
                   PAL["blue"], 0.95)
        d.dot(x, y, r * 0.25, PAL["gold"])
    elif kind == "pink":
        d.shape(blob(x, y, r * 0.8, r * 0.8, d.rng, 0.2, 10), PAL["rose"], 0.9, w=0.4, ink_color=INK_SOFT)
        d.dot(x, y, r * 0.25, PAL["berry"])
    else:
        d.shape(blob(x, y, r * 0.7, r * 0.9, d.rng, 0.2, 10), PAL["pink"], 0.95, w=0.4, ink_color=INK_SOFT)


def leaf(d, x, y, L, ang, color=None, wdt=0.42, vein=True, ink_w=0.7):
    color = color or d.choice([PAL["leaf"], PAL["leafdk"], PAL["leaflt"]])
    pts = []
    n = 8
    for i in range(n + 1):
        t = i / n
        pts.append((t * L, math.sin(math.pi * t) * L * wdt / 2))
    for i in range(n - 1, 0, -1):
        t = i / n
        pts.append((t * L, -math.sin(math.pi * t) * L * wdt / 2))
    pts = transform_pts(pts, x, y, 1, ang, 0, 0)
    d.shape(pts, color, 0.9, w=ink_w)
    if vein:
        d.ink(transform_pts([(L * 0.05, 0), (L * 0.5, 0.5), (L * 0.9, 0)], x, y, 1, ang, 0, 0), 0.45, INK_SOFT, op=0.8)


def oak_leaf(d, x, y, L, ang, color=None):
    color = color or d.choice([PAL["leaf"], PAL["leafdk"], PAL["leaflt"], "#b9a14b"])
    pts = []
    lobes = 5
    for i in range(0, 41):
        t = i / 40
        wv = math.sin(math.pi * t) * (0.62 + 0.38 * abs(math.sin(t * lobes * math.pi)))
        pts.append((t * L, wv * L * 0.24))
    for i in range(39, 0, -1):
        t = i / 40
        wv = math.sin(math.pi * t) * (0.62 + 0.38 * abs(math.sin(t * lobes * math.pi + 0.3)))
        pts.append((t * L, -wv * L * 0.24))
    pts = transform_pts(pts, x, y, 1, ang)
    d.shape(pts, color, 0.9, w=0.7)
    d.ink(transform_pts([(-L * 0.12, 0), (L * 0.9, 0)], x, y, 1, ang), 0.5, INK_SOFT)


def acorn(d, x, y, s=1.0, ang=0.0):
    nut = transform_pts(ellipse_pts(0, 6 * s, 7 * s, 10 * s, 18), x, y, 1, ang)
    d.shape(nut, "#b98a3e", 0.95, w=0.9)
    d.ink(transform_pts(ellipse_pts(-2.5 * s, 7 * s, 2 * s, 5 * s, 8, a0=2.2, a1=4.2), x, y, 1, ang), 0.5, PAL["white"], op=0.8)
    cup = transform_pts([(-8.5 * s, 1 * s), (-8 * s, -4 * s), (-4 * s, -7.5 * s), (0, -8 * s), (4 * s, -7.5 * s),
                         (8 * s, -4 * s), (8.5 * s, 1 * s), (0, 3 * s)], x, y, 1, ang)
    d.shape(cup, "#8a6a3e", 0.95, w=0.9)
    for i in range(5):
        for j in range(2):
            cx, cy = -6 * s + i * 3 * s, -4.5 * s + j * 3.5 * s
            px, py = transform_pts([(cx, cy)], x, y, 1, ang)[0]
            d.ink(ellipse_pts(px, py, 1.1 * s, 0.8 * s, 6, a0=0, a1=math.pi), 0.4, INK)
    d.ink(transform_pts([(0, -8 * s), (1 * s, -12 * s), (3 * s, -14 * s)], x, y, 1, ang), 1.1, INK)


def mushroom(d, x, y, s=1.0, cap=None, spots=True, lean=0.0):
    cap = cap or d.choice([PAL["red"], "#c8894a", "#d7b77c"])
    stem = [(x - 3.5 * s, y), (x - 3 * s + lean * 4, y - 10 * s), (x - 2.5 * s + lean * 8, y - 17 * s),
            (x + 2.5 * s + lean * 8, y - 17 * s), (x + 3 * s + lean * 4, y - 10 * s), (x + 4 * s, y)]
    d.shape(stem, "#f2e6cd", 0.95, w=0.8, smooth_=True)
    cx, cy = x + lean * 8, y - 17 * s
    capp = [(cx - 12 * s, cy + 1 * s)] + ellipse_pts(cx, cy, 12 * s, 9 * s, 14, a0=math.pi, a1=2 * math.pi)[1:-1] + [
        (cx + 12 * s, cy + 1 * s), (cx, cy + 2.5 * s)]
    d.shape(capp, cap, 0.92, w=0.9)
    # gills
    for k in range(-4, 5):
        d.ink([(cx + k * 2.2 * s, cy + 1.6 * s), (cx + k * 1.2 * s, cy + 0.3 * s)], 0.35, INK_SOFT, op=0.6, smooth_=False)
    if spots and cap == PAL["red"]:
        for _ in range(5):
            a = d.u(math.pi * 1.1, math.pi * 1.9)
            rr = d.u(0.3, 0.8)
            d.shape(blob(cx + 12 * s * rr * math.cos(a), cy + 9 * s * rr * math.sin(a), 1.6 * s, 1.2 * s, d.rng, 0.2, 7),
                    PAL["white"], 1, w=0.3, ink_color=INK_SOFT)


def foliage_cluster(d, cx, cy, rx, ry, n=16, colors=None, leaves=60, ink_op=0.8):
    colors = colors or [PAL["leaf"], PAL["leafdk"], PAL["moss"], PAL["leaflt"]]
    blobs = []
    for i in range(n):
        a = d.u(0, 2 * math.pi)
        rr = math.sqrt(d.u(0, 1))
        bx, by = cx + rx * 0.75 * rr * math.cos(a), cy + ry * 0.75 * rr * math.sin(a)
        br = d.u(0.28, 0.45) * min(rx, ry)
        blobs.append((by, bx, br))
    blobs.sort()
    # back to front: darker at bottom
    for by, bx, br in blobs:
        t = (by - (cy - ry)) / (2 * ry)
        col = PAL["leafdk"] if t > 0.6 and d.chance(0.6) else d.choice(colors)
        pts = scallop(bx, by, br, br * 0.85, d)
        d.wash(pts, col, 0.88)
        d.ink(pts[: int(len(pts) * 0.7)], 0.7, INK, op=ink_op)
    for _ in range(leaves):
        a = d.u(0, 2 * math.pi)
        rr = math.sqrt(d.u(0, 1))
        x, y = cx + rx * 0.62 * rr * math.cos(a), cy + ry * 0.62 * rr * math.sin(a)
        L = d.u(3, 6)
        aa = d.u(0, 2 * math.pi)
        d.ink([(x, y), (x + L * math.cos(aa), y + L * math.sin(aa)), (x + L * 1.2 * math.cos(aa + 0.8), y + L * 1.2 * math.sin(aa + 0.8))],
              0.5, PAL["leafdk"] if d.chance(0.7) else INK, op=0.7)


def scallop(cx, cy, rx, ry, d, bumps=None):
    bumps = bumps or d.rng.randint(7, 11)
    pts = []
    for i in range(bumps * 4):
        a = 2 * math.pi * i / (bumps * 4)
        k = 1 + 0.09 * abs(math.sin(a * bumps / 2 * 2)) + d.r(0.03)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def cloud(d, cx, cy, w, h):
    for i in range(6):
        x = cx + d.u(-w / 2, w / 2)
        y = cy + d.u(-h / 3, h / 4)
        r = d.u(h * 0.4, h * 0.7)
        d.wash(blob(x, y, r * 1.3, r, d.rng, 0.15, 12), PAL["cloud"], 0.85, soft=True)
    d.ink(ellipse_pts(cx, cy + h * 0.15, w * 0.55, h * 0.35, 20, a0=math.pi * 1.05, a1=math.pi * 1.95), 0.5, INK_SOFT, op=0.35)


def tree_trunk(d, x, ybase, ytop, w, lean=0.0):
    pts = [(x - w * 0.9, ybase + 4), (x - w * 0.55, ybase - 12), (x - w * 0.5 + lean * 0.3, lerp(ybase, ytop, 0.5)),
           (x - w * 0.42 + lean, ytop), (x + w * 0.42 + lean, ytop), (x + w * 0.5 + lean * 0.3, lerp(ybase, ytop, 0.5)),
           (x + w * 0.55, ybase - 12), (x + w * 0.95, ybase + 4)]
    d.wash(pts, PAL["paper"], 1.0, jitter=0)
    d.shape(pts, PAL["wooddk"], 0.9, w=1.2)
    # bark lines
    for i in range(int(w / 3)):
        bx = x - w * 0.4 + i * 3 + d.r(1)
        y0 = d.u(ytop + 5, ybase - 30)
        y1 = y0 + d.u(15, 50)
        if y1 < ybase:
            d.ink([(bx, y0), (bx + d.r(1.5), (y0 + y1) / 2), (bx + d.r(1.5), y1)], 0.5, INK, op=0.6)
    d.wash([(x + w * 0.1, ybase - 10), (x + w * 0.45, ybase - 12), (x + w * 0.4 + lean, ytop + 10), (x + w * 0.12 + lean, ytop + 10)],
           PAL["shadow"], 0.25)


# =================================================================== building
def stone_wall(d, x, y, w, h, course=16, colors=None, mortar=PAL["plaster2"], ink_op=0.8):
    colors = colors or [PAL["stone"], PAL["stone2"], "#cbbfa9", "#b3a68f"]
    d.wash(rect_pts(x, y, w, h), mortar, 0.7, smooth_=False)
    rows = max(1, int(h / course))
    for r in range(rows):
        yy = y + r * h / rows
        hh = h / rows
        cx = x - d.u(0, course)
        while cx < x + w:
            sw = d.u(course * 1.1, course * 2.2)
            x0, x1 = max(x, cx + 1), min(x + w, cx + sw - 1)
            if x1 - x0 > 4:
                pts = blob((x0 + x1) / 2, yy + hh / 2, (x1 - x0) / 2, hh / 2 - 1, d.rng, 0.08, 12)
                d.shape(pts, d.choice(colors), 0.85, w=0.7, ink_op=ink_op)
            cx += sw


def planks(d, x, y, w, h, n, vertical=True, color=None, grain=True, nails=True):
    color = color or PAL["wood"]
    for i in range(n):
        if vertical:
            px, py, pw, ph = x + i * w / n, y, w / n, h
        else:
            px, py, pw, ph = x, y + i * h / n, w, h / n
        tint = d.choice([color, PAL["woodlt"], color])
        d.shape(rect_pts(px, py, pw, ph), tint, 0.85, w=0.8, smooth_=False)
        if grain:
            for g in range(2):
                if vertical:
                    gx = px + pw * d.u(0.25, 0.75)
                    d.ink(line_pts(gx, py + d.u(2, ph * 0.3), gx + d.r(1), py + ph * d.u(0.6, 0.95), 0.8, d.rng), 0.4, INK_SOFT, op=0.6)
                else:
                    gy = py + ph * d.u(0.25, 0.75)
                    d.ink(line_pts(px + d.u(2, pw * 0.3), gy, px + pw * d.u(0.6, 0.95), gy + d.r(1), 0.8, d.rng), 0.4, INK_SOFT, op=0.6)
        if nails:
            if vertical:
                d.dot(px + pw / 2, py + 4, 0.8)
                d.dot(px + pw / 2, py + ph - 4, 0.8)
            else:
                d.dot(px + 4, py + ph / 2, 0.8)
                d.dot(px + pw - 4, py + ph / 2, 0.8)


def beam(d, x, y, w, h, color=None):
    color = color or PAL["wooddk"]
    d.shape(rect_pts(x, y, w, h, 30), color, 0.85, w=1.0, smooth_=False)
    for _ in range(max(1, int(w / 40))):
        gx = d.u(x + 4, x + w - 20)
        d.ink(line_pts(gx, y + h * d.u(0.3, 0.7), gx + d.u(8, 25), y + h * d.u(0.3, 0.7), 0.5, d.rng), 0.4, INK_SOFT, op=0.7)


def floor_tiles(d, x, y, w, h, size=10, c1=None, c2=None):
    c1 = c1 or PAL["rust"]
    c2 = c2 or PAL["clay"]
    d.wash(rect_pts(x, y, w, h), c2, 0.8, smooth_=False)
    nx = int(w / size)
    for i in range(nx):
        if i % 2 == 0:
            d.wash(rect_pts(x + i * size, y, size, h), c1, 0.55, smooth_=False)
        d.line(x + i * size, y, x + i * size, y + h, 0.5, INK_SOFT, 0.2)
    d.line(x, y, x + w, y, 0.8, INK, 0.3)


def rug(d, cx, y, w, h, c1=None, c2=None):
    c1 = c1 or PAL["red"]
    c2 = c2 or PAL["ochre"]
    pts = rect_pts(cx - w / 2, y - h, w, h, 12)
    d.shape(pts, c1, 0.85, w=0.8, smooth_=False)
    d.wash(rect_pts(cx - w / 2 + 3, y - h + 1, w - 6, h - 2, 12), c2, 0.5, smooth_=False)
    for i in range(int(w / 5)):
        fx = cx - w / 2 + i * 5 + 2
        d.line(fx, y, fx + d.r(1), y + 3, 0.4, INK_SOFT, 0.3)


# ================================================================ furnishings
def barrel_side(d, x, y, w, h, color=None, hoops=PAL["stonedk"], label=False):
    """Upright barrel, (x,y) = bottom-centre."""
    color = color or PAL["wood"]
    bulge = w * 0.14
    pts = [(x - w / 2, y), (x - w / 2 - bulge * 0.7, y - h * 0.25), (x - w / 2 - bulge, y - h / 2), (x - w / 2 - bulge * 0.7, y - h * 0.75),
           (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2 + bulge * 0.7, y - h * 0.75), (x + w / 2 + bulge, y - h / 2),
           (x + w / 2 + bulge * 0.7, y - h * 0.25), (x + w / 2, y)]
    d.shape(pts, color, 0.88, w=1.1)
    # staves
    for k in range(1, 5):
        t = k / 5
        sx = lerp(x - w / 2, x + w / 2, t)
        b = (t - 0.5) * 2 * bulge
        d.ink([(sx, y - 1), (sx + b, y - h / 2), (sx, y - h + 1)], 0.5, INK_SOFT, op=0.7)
    for hy in (0.12, 0.3, 0.7, 0.88):
        yy = y - h * hy
        bb = bulge * math.sin(math.pi * hy)
        d.ink([(x - w / 2 - bb, yy), (x, yy + 2), (x + w / 2 + bb, yy)], 2.6, "#5f5a54", op=0.95)
    d.wash([(x + w * 0.15, y - 3), (x + w / 2 + bulge * 0.8, y - h / 2), (x + w * 0.2, y - h + 3)], PAL["shadow"], 0.25)
    d.shape(ellipse_pts(x, y - h, w / 2, w * 0.1, 18), "#c99a62", 0.9, w=0.6)
    d.ink(ellipse_pts(x, y - h, w / 2 * 0.8, w * 0.07, 16), 0.4, INK_SOFT, True, op=0.7)


def barrel_end(d, cx, cy, r, color=None, tap=False):
    """Barrel lying down, seen end-on."""
    color = color or PAL["wood"]
    d.shape(ellipse_pts(cx, cy, r, r, 24), PAL["wooddk"], 0.9, w=1.1)
    d.shape(ellipse_pts(cx, cy, r * 0.82, r * 0.82, 22), color, 0.85, w=0.8)
    for k in (-0.45, 0, 0.45):
        d.line(cx + k * r - r * 0.1, cy - r * 0.78, cx + k * r - r * 0.1, cy + r * 0.78, 0.4, INK_SOFT, 0.3)
    d.ink(ellipse_pts(cx, cy, r * 0.93, r * 0.93, 24), 1.0, PAL["stonedk"], closed=True, op=0.8)
    if tap:
        d.shape(rect_pts(cx - 2, cy + r * 0.3, 4, 8), PAL["brass"], 1, w=0.6)
        d.shape(rect_pts(cx - 5, cy + r * 0.3 + 6, 10, 3), PAL["brass"], 1, w=0.6)
    else:
        d.dot(cx + r * 0.25, cy + r * 0.35, 1.6, INK)


def jar(d, x, y, h, color=None, lid=None, label=True, kind=None):
    """Jar standing on a shelf at (x,y)=bottom-centre."""
    kind = kind or d.choice(["jar", "jar", "crock", "bottle"])
    color = color or d.choice([PAL["jam"], PAL["honey"], PAL["apple2"], PAL["rose"], PAL["berry"], PAL["ochre"]])
    w = h * d.u(0.55, 0.8)
    if kind == "bottle":
        w = h * 0.38
        pts = [(x - w / 2, y), (x - w / 2, y - h * 0.6), (x - w * 0.18, y - h * 0.82), (x - w * 0.18, y - h),
               (x + w * 0.18, y - h), (x + w * 0.18, y - h * 0.82), (x + w / 2, y - h * 0.6), (x + w / 2, y)]
        d.shape(pts, d.choice(["#7c9a6a", "#8a5a3a", "#6e7f9a"]), 0.8, w=0.8, smooth_=False)
        d.shape(rect_pts(x - w * 0.2, y - h - 3, w * 0.4, 3.5), PAL["woodlt"], 1, w=0.5, smooth_=False)
    elif kind == "crock":
        pts = [(x - w * 0.4, y), (x - w / 2, y - h * 0.5), (x - w * 0.38, y - h), (x + w * 0.38, y - h),
               (x + w / 2, y - h * 0.5), (x + w * 0.4, y)]
        d.shape(pts, d.choice(["#c9b58f", "#b98f61", "#d8c9a8"]), 0.9, w=0.8)
        d.ink([(x - w * 0.45, y - h * 0.35), (x + w * 0.45, y - h * 0.35)], 0.6, PAL["navy"], op=0.7)
    else:
        pts = rect_pts(x - w / 2, y - h * 0.85, w, h * 0.85, 6)
        d.wash(pts, color, 0.85, smooth_=False)
        d.ink(pts, 0.8, INK, True, smooth_=False)
        cloth = lid or d.choice(["#e9dcc0", "#d7a0a0", "#a9c0d8", "#e9dcc0"])
        cp = [(x - w / 2 - 2, y - h * 0.8), (x - w / 2 + 1, y - h), (x + w / 2 - 1, y - h), (x + w / 2 + 2, y - h * 0.8),
              (x, y - h * 0.76)]
        d.shape(cp, cloth, 0.95, w=0.6)
        d.ink([(x - w / 2, y - h * 0.83), (x + w / 2, y - h * 0.83)], 0.6, PAL["red"], op=0.8)
        if label and h > 9:
            d.shape(rect_pts(x - w * 0.3, y - h * 0.5, w * 0.6, h * 0.22, 5), PAL["white"], 0.95, w=0.4, smooth_=False)
            d.line(x - w * 0.2, y - h * 0.4, x + w * 0.2, y - h * 0.4, 0.3, INK_SOFT, 0.2)
        d.ink([(x - w * 0.3, y - h * 0.7), (x - w * 0.3, y - h * 0.2)], 0.8, PAL["white"], op=0.6)


def shelf(d, x, y, w, depth=5, brackets=True):
    d.shape(rect_pts(x, y, w, depth, 20), PAL["woodlt"], 0.9, w=0.8, smooth_=False)
    if brackets:
        for bx in (x + 6, x + w - 6):
            d.ink([(bx, y + depth), (bx, y + depth + 7), (bx + (4 if bx < x + w / 2 else -4), y + depth)], 0.8, INK)


def shelf_of_jars(d, x, y, w, h=16, n=None):
    shelf(d, x, y, w)
    n = n or int(w / (h * 0.9))
    gap = w / n
    for i in range(n):
        jx = x + gap * (i + 0.5) + d.r(1.5)
        jar(d, jx, y, h * d.u(0.75, 1.1))


def cheese(d, x, y, r):
    d.shape([(x - r, y), (x - r, y - r * 0.7), (x + r, y - r * 0.7), (x + r, y)], PAL["cheese"], 0.9, w=0.8, smooth_=False)
    d.shape(ellipse_pts(x, y - r * 0.7, r, r * 0.25, 16), "#f5da7c", 0.95, w=0.7)
    d.ink(ellipse_pts(x, y, r, r * 0.25, 16, a0=0, a1=math.pi), 0.8, INK)
    # wedge cut
    d.shape([(x, y - r * 0.7), (x + r * 0.7, y - r * 0.85), (x + r * 0.95, y - r * 0.68)], "#fbe9a6", 1, w=0.6, smooth_=False)


def ham(d, x, y, s=1.0):
    """Hanging ham; (x,y) = hook point."""
    d.line(x, y, x, y + 8 * s, 0.6, INK)
    pts = [(x, y + 8 * s), (x - 7 * s, y + 18 * s), (x - 9 * s, y + 32 * s), (x, y + 38 * s), (x + 9 * s, y + 32 * s),
           (x + 7 * s, y + 18 * s)]
    d.shape(pts, "#c46b4e", 0.9, w=0.9)
    d.wash(blob(x + 2 * s, y + 30 * s, 5 * s, 4 * s, d.rng, 0.2, 8), "#efc9a8", 0.8)
    d.ink([(x - 6 * s, y + 20 * s), (x + 6 * s, y + 20 * s)], 0.6, INK_SOFT, op=0.8)
    d.ink([(x - 7 * s, y + 26 * s), (x + 7 * s, y + 26 * s)], 0.6, INK_SOFT, op=0.8)


def onion_string(d, x, y, n=5, s=1.0):
    d.line(x, y, x, y + n * 7 * s + 6, 0.6, "#b9955a")
    for i in range(n):
        ox = x + (4 if i % 2 else -4) * s
        oy = y + 8 * s + i * 7 * s
        d.shape(blob(ox, oy, 4 * s, 4.4 * s, d.rng, 0.08, 10), d.choice(["#d7a35a", "#c98a4a", "#b86f5a"]), 0.9, w=0.6)


def sack(d, x, y, w, h, color="#e2cfa3", label=None):
    pts = [(x - w / 2, y), (x - w * 0.55, y - h * 0.5), (x - w * 0.35, y - h * 0.9), (x - w * 0.15, y - h),
           (x, y - h * 1.08), (x + w * 0.15, y - h), (x + w * 0.35, y - h * 0.9), (x + w * 0.55, y - h * 0.5), (x + w / 2, y)]
    d.shape(pts, color, 0.9, w=0.9)
    d.ink([(x - w * 0.3, y - h * 0.86), (x, y - h * 0.82), (x + w * 0.3, y - h * 0.86)], 0.8, "#8a6a3e")
    d.ink([(x - w * 0.3, y - h * 0.3), (x - w * 0.25, y - h * 0.6)], 0.4, INK_SOFT, op=0.6)
    if label:
        d.text(x, y - h * 0.4, label, size=h * 0.22, color=PAL["red"], family="IM Fell English SC")


def basket(d, x, y, w, h, fruit=None):
    fruit = fruit or PAL["apple"]
    for i in range(int(w / 6)):
        fx = x - w / 2 + 4 + i * 6
        d.shape(blob(fx + d.r(1), y - h - d.u(0, 3), 4.2, 4.0, d.rng, 0.1, 10), d.choice([fruit, PAL["apple2"], fruit]), 0.95, w=0.6)
    pts = [(x - w / 2, y - h), (x - w * 0.42, y), (x + w * 0.42, y), (x + w / 2, y - h)]
    d.shape(pts, "#c79a5a", 0.9, w=0.9, smooth_=False)
    for k in range(1, 4):
        yy = y - h * k / 4
        d.line(x - w * 0.47, yy, x + w * 0.47, yy, 0.4, INK_SOFT, 0.3)
    for k in range(1, 6):
        xx = x - w / 2 + w * k / 6
        d.line(xx, y - h, xx + (x - xx) * 0.1, y, 0.4, INK_SOFT, 0.2)


def books_row(d, x, y, w, hmax=18):
    cx = x
    while cx < x + w - 3:
        bw = d.u(3, 6)
        bh = hmax * d.u(0.7, 1.0)
        lean = 0
        col = d.choice([PAL["red"], PAL["navy"], PAL["door"], PAL["ochre"], PAL["berry"], "#7b5a3a", PAL["teal"]])
        d.shape([(cx, y), (cx + lean, y - bh), (cx + bw + lean, y - bh), (cx + bw, y)], col, 0.9, w=0.6, smooth_=False)
        d.line(cx + 0.8, y - bh * 0.8, cx + bw - 0.8, y - bh * 0.8, 0.4, PAL["gold"], 0.2)
        d.line(cx + 0.8, y - bh * 0.2, cx + bw - 0.8, y - bh * 0.2, 0.4, PAL["gold"], 0.2)
        cx += bw + 0.3


def bookcase(d, x, y, w, h, shelves=4):
    d.shape(rect_pts(x, y - h, w, h, 20), PAL["wooddk"], 0.9, w=1.0, smooth_=False)
    for i in range(shelves):
        sy = y - h + 4 + (i + 1) * (h - 8) / shelves
        d.wash(rect_pts(x + 3, sy - (h - 8) / shelves + 2, w - 6, (h - 8) / shelves - 2), "#5a3c22", 0.6, smooth_=False)
        books_row(d, x + 4, sy - 1, w - 8, (h - 8) / shelves - 4)
        d.line(x + 2, sy, x + w - 2, sy, 1.0, INK, 0.2)


def armchair(d, x, y, s=1.0, color=None):
    color = color or PAL["red"]
    # back
    back = [(x - 16 * s, y - 14 * s), (x - 17 * s, y - 34 * s), (x - 10 * s, y - 42 * s), (x + 10 * s, y - 42 * s),
            (x + 17 * s, y - 34 * s), (x + 16 * s, y - 14 * s)]
    d.shape(back, color, 0.88, w=1.0)
    # seat
    d.shape(rect_pts(x - 17 * s, y - 16 * s, 34 * s, 8 * s, 10), color, 0.9, w=0.9)
    # arms
    for sx in (-1, 1):
        arm = [(x + sx * 15 * s, y - 6 * s), (x + sx * 15 * s, y - 22 * s), (x + sx * 22 * s, y - 25 * s),
               (x + sx * 23 * s, y - 20 * s), (x + sx * 20 * s, y - 6 * s)]
        d.shape(arm, color, 0.92, w=0.9)
    d.wash(back[2:5] + [(x + 8 * s, y - 20 * s)], PAL["shadow"], 0.2)
    # legs
    for lx in (-17, 17):
        d.shape(rect_pts(x + lx * s - 1.5 * s, y - 6 * s, 3 * s, 6 * s), PAL["wooddk"], 0.95, w=0.6, smooth_=False)
    # cushion & antimacassar
    d.shape(blob(x, y - 36 * s, 7 * s, 3 * s, d.rng, 0.1, 10), PAL["white"], 0.9, w=0.5, ink_color=INK_SOFT)
    # button tufts
    for bx in (-6, 0, 6):
        d.dot(x + bx * s, y - 26 * s, 0.7 * s)


def table(d, x, y, w, h, cloth=None):
    cloth = cloth or PAL["white"]
    for lx in (x - w / 2 + 4, x + w / 2 - 6):
        d.shape(rect_pts(lx, y - h, 2.5, h), PAL["wooddk"], 0.95, w=0.6, smooth_=False)
    d.shape([(x - w / 2 - 3, y - h), (x - w / 2 - 4, y - h + 9), (x + w / 2 + 4, y - h + 9), (x + w / 2 + 3, y - h),
             (x + w / 2 - 2, y - h - 2), (x - w / 2 + 2, y - h - 2)], cloth, 0.9, w=0.8)
    for i in range(int(w / 7)):
        cx = x - w / 2 + i * 7 + 2
        d.ink([(cx, y - h + 8.5), (cx + 3.5, y - h + 10.5), (cx + 7, y - h + 8.5)], 0.5, PAL["red"], op=0.6)


def teapot(d, x, y, s=1.0, color=None):
    color = color or PAL["navy"]
    body = ellipse_pts(x, y - 9 * s, 11 * s, 9 * s, 22)
    d.shape(body, color, 0.9, w=1.0)
    spout = [(x + 9 * s, y - 10 * s), (x + 15 * s, y - 13 * s), (x + 19 * s, y - 19 * s), (x + 20 * s, y - 18 * s),
             (x + 17 * s, y - 11 * s), (x + 9 * s, y - 5 * s)]
    d.shape(spout, color, 0.9, w=0.9)
    d.ink(ellipse_pts(x - 13 * s, y - 10 * s, 5 * s, 5.5 * s, 14, a0=math.pi * 0.4, a1=math.pi * 1.6), 1.6 * s, INK)
    d.shape(ellipse_pts(x, y - 18 * s, 6 * s, 2 * s, 12), color, 0.95, w=0.8)
    d.shape(ellipse_pts(x, y - 21 * s, 2 * s, 2 * s, 8), PAL["white"], 0.95, w=0.6)
    d.ink(ellipse_pts(x - 4 * s, y - 11 * s, 4 * s, 3 * s, 10, a0=3.3, a1=4.6), 1.0 * s, PAL["white"], op=0.85)
    # little flowers painted on
    for fx, fy in ((-3, -7), (4, -6)):
        d.dot(x + fx * s, y + fy * s, 1.3 * s, PAL["white"], 0.9)


def cup(d, x, y, s=1.0, color=None):
    color = color or PAL["white"]
    d.shape([(x - 5 * s, y - 7 * s), (x - 4 * s, y - 1 * s), (x - 2 * s, y), (x + 2 * s, y), (x + 4 * s, y - 1 * s), (x + 5 * s, y - 7 * s)],
            color, 0.95, w=0.7)
    d.ink(ellipse_pts(x + 6 * s, y - 4.5 * s, 2 * s, 2 * s, 8, a0=-1.4, a1=1.4), 0.7, INK)
    d.ink(ellipse_pts(x, y + 0.5 * s, 7 * s, 1.5 * s, 12, a0=0, a1=math.pi), 0.6, INK)
    d.line(x - 4.5 * s, y - 5 * s, x + 4.5 * s, y - 5 * s, 0.6, PAL["navy"], 0.3)


def cake(d, x, y, s=1.0):
    d.shape(ellipse_pts(x, y, 14 * s, 3 * s, 16), PAL["white"], 0.95, w=0.6)
    d.shape([(x - 10 * s, y - 1 * s), (x - 10 * s, y - 10 * s), (x + 10 * s, y - 10 * s), (x + 10 * s, y - 1 * s)],
            "#d9a865", 0.92, w=0.8, smooth_=False)
    d.shape(ellipse_pts(x, y - 10 * s, 10 * s, 2.5 * s, 16), "#f4e3c2", 0.95, w=0.7)
    for _ in range(8):
        d.dot(x + d.r(8 * s), y - 10 * s + d.r(1.5 * s), 0.6 * s, "#5a3a22")
    d.line(x - 10 * s, y - 5 * s, x + 10 * s, y - 5 * s, 0.5, "#a8743f", 0.2)


def candle(d, x, y, h=14, holder=True, lit=True):
    if lit:
        d.glow(x, y - h - 5, 22, PAL["flame"], 0.55)
    if holder:
        d.shape(ellipse_pts(x, y, 8, 2.4, 14), PAL["brass"], 0.95, w=0.7)
        d.ink(ellipse_pts(x + 9, y - 1, 3, 3, 8, a0=-1.6, a1=1.6), 0.8, INK)
    d.shape(rect_pts(x - 2.4, y - h, 4.8, h, 6), "#f6efd9", 0.95, w=0.7, smooth_=False)
    d.ink([(x - 2.4, y - h + 1), (x - 2.6, y - h + 5)], 0.6, "#f6efd9")
    if lit:
        d.line(x, y - h, x, y - h - 2, 0.6, INK, 0)
        d.shape([(x, y - h - 1), (x - 2.4, y - h - 5), (x, y - h - 11), (x + 2.4, y - h - 5)], PAL["flame"], 1, w=0.5, ink_color=PAL["fire2"])


def lantern(d, x, y, s=1.0, lit=True, hang=0):
    """Hanging lantern; (x,y) = top ring."""
    if hang:
        d.line(x, y - hang, x, y, 0.7, INK)
    if lit:
        d.glow(x, y + 16 * s, 34 * s, PAL["flame"], 0.5)
    d.ink(ellipse_pts(x, y + 1 * s, 2.5 * s, 2.5 * s, 8), 0.8, INK, closed=True)
    d.shape([(x - 6 * s, y + 8 * s), (x, y + 3 * s), (x + 6 * s, y + 8 * s)], PAL["wooddk"], 0.95, w=0.8, smooth_=False)
    d.shape(rect_pts(x - 6 * s, y + 8 * s, 12 * s, 16 * s, 5), "#fbe7a1" if lit else "#cfd8d6", 0.85, w=0.9, smooth_=False)
    if lit:
        d.shape([(x, y + 12 * s), (x - 2.5 * s, y + 17 * s), (x, y + 21 * s), (x + 2.5 * s, y + 17 * s)], PAL["fire"], 1, w=0.4, ink_color=PAL["fire2"])
    for lx in (x - 6 * s, x, x + 6 * s):
        d.line(lx, y + 8 * s, lx, y + 24 * s, 0.7, INK, 0.1)
    d.shape(rect_pts(x - 7 * s, y + 24 * s, 14 * s, 3 * s), PAL["wooddk"], 0.95, w=0.7, smooth_=False)


def fireplace(d, x, y, w, h, fire=True, kettle=False):
    """Stone fireplace; (x,y) = floor centre."""
    stone_wall(d, x - w / 2, y - h, w, h, course=h / 6)
    # mantel
    beam(d, x - w / 2 - 6, y - h - 6, w + 12, 7, PAL["wooddk"])
    # opening
    ow, oh = w * 0.6, h * 0.62
    op = arch_pts(x - ow / 2, y - oh, ow, oh, oh * 0.35, 14)
    d.shape(op, "#3a2a22", 0.95, w=1.1)
    if fire:
        d.glow(x, y - oh * 0.3, w * 0.9, PAL["fire"], 0.55)
        for k in range(6):
            fx = x + d.r(ow * 0.3)
            fh = oh * d.u(0.3, 0.6)
            d.shape([(fx - 5, y - 4), (fx - 3, y - fh * 0.6), (fx + d.r(2), y - fh), (fx + 3, y - fh * 0.5), (fx + 5, y - 4)],
                    d.choice([PAL["fire"], PAL["fire2"], PAL["flame"]]), 0.9, w=0.5, ink_color=PAL["rust"])
        for lx in (-0.18, 0.12):
            d.shape(rect_pts(x + lx * ow - 8, y - 6, 18, 4.5, 6), PAL["wooddk"], 0.95, w=0.6, smooth_=False)
    if kettle:
        kx, ky = x + ow * 0.05, y - oh * 0.42
        d.line(kx, y - oh * 0.95, kx, ky - 12, 0.8, INK)
        d.shape(ellipse_pts(kx, ky, 9, 7, 16), "#3b3b3b", 0.9, w=0.8)
    # items on mantel
    candle(d, x - w * 0.38, y - h - 6, 10)
    d.shape(ellipse_pts(x, y - h - 15, 8, 8, 18), PAL["brass"], 0.9, w=0.8)  # clock
    d.shape(ellipse_pts(x, y - h - 15, 5.6, 5.6, 16), PAL["white"], 0.95, w=0.5)
    d.line(x, y - h - 15, x, y - h - 19, 0.6, INK, 0)
    d.line(x, y - h - 15, x + 3, y - h - 14, 0.6, INK, 0)
    d.shape(rect_pts(x - 5, y - h - 8, 10, 2), PAL["brass"], 0.9, w=0.5, smooth_=False)
    jar(d, x + w * 0.36, y - h - 6, 9, kind="crock")


def range_stove(d, x, y, w, h):
    """Kitchen range; (x,y) = floor centre."""
    d.shape(rect_pts(x - w / 2, y - h, w, h, 14), "#4a4440", 0.92, w=1.1, smooth_=False)
    d.shape(rect_pts(x - w / 2 + 4, y - h * 0.62, w * 0.45, h * 0.45, 8), "#2f2a27", 0.95, w=0.8, smooth_=False)
    d.glow(x - w / 2 + 4 + w * 0.22, y - h * 0.4, 18, PAL["fire"], 0.6)
    for k in range(4):
        d.line(x - w / 2 + 6 + k * w * 0.1, y - h * 0.58, x - w / 2 + 6 + k * w * 0.1, y - h * 0.2, 0.7, PAL["fire2"], 0)
    d.shape(rect_pts(x + w * 0.05, y - h * 0.62, w * 0.38, h * 0.45, 8), "#3a3532", 0.95, w=0.8, smooth_=False)
    d.dot(x + w * 0.1, y - h * 0.4, 1.4, PAL["brass"])
    d.line(x - w / 2 - 2, y - h, x + w / 2 + 2, y - h, 1.6, INK, 0)
    # kettle and pot on top
    kx = x - w * 0.22
    d.shape([(kx - 9, y - h), (kx - 8, y - h - 9), (kx - 4, y - h - 12), (kx + 4, y - h - 12), (kx + 8, y - h - 9), (kx + 9, y - h)],
            PAL["copper"], 0.92, w=0.9)
    d.ink([(kx + 8, y - h - 6), (kx + 14, y - h - 10), (kx + 16, y - h - 14)], 1.6, PAL["copper"])
    d.ink(ellipse_pts(kx, y - h - 13, 6, 5, 10, a0=math.pi, a1=2 * math.pi), 0.9, INK)
    steam(d, kx + 16, y - h - 16, 18)
    px = x + w * 0.22
    d.shape(rect_pts(px - 9, y - h - 10, 18, 10, 6), "#5b5b5b", 0.92, w=0.9, smooth_=False)
    d.line(px - 12, y - h - 8, px - 9, y - h - 8, 1, INK, 0)
    d.line(px + 9, y - h - 8, px + 12, y - h - 8, 1, INK, 0)
    # flue pipe
    d.shape(rect_pts(x + w * 0.3, y - h - 40, 7, 40, 10), "#4a4440", 0.9, w=0.8, smooth_=False)


def steam(d, x, y, h, op=0.6):
    pts = []
    for i in range(7):
        t = i / 6
        pts.append((x + math.sin(t * 6 + d.u(0, 1)) * 3, y - t * h))
    d.ink(pts, 0.7, "#9fa7ad", op=op)


def smoke(d, x, y, h, w=10):
    for k in range(5):
        t = k / 4
        d.wash(blob(x + math.sin(t * 4) * w, y - t * h, w * (0.6 + t), w * (0.5 + t * 0.8), d.rng, 0.2, 10),
               "#c9ccc9", 0.5 - t * 0.35, soft=True)
    pts = [(x + math.sin(i / 8 * 5) * w * 0.8, y - i / 8 * h * 0.45) for i in range(9)]
    d.ink(pts, 0.4, INK_SOFT, op=0.15)


def pots_rail(d, x, y, w):
    d.line(x, y, x + w, y, 1.2, INK)
    n = int(w / 16)
    for i in range(n):
        px = x + 8 + i * 16
        d.line(px, y, px, y + 4, 0.6, INK, 0)
        kind = i % 3
        if kind == 0:  # frying pan
            d.ink([(px, y + 4), (px, y + 14)], 1.4, INK)
            d.shape(ellipse_pts(px, y + 20, 7, 7, 14), "#3d3d3d", 0.92, w=0.8)
        elif kind == 1:  # copper pan
            d.ink([(px, y + 4), (px, y + 12)], 1.4, PAL["copper"])
            d.shape(ellipse_pts(px, y + 18, 6.5, 6.5, 14), PAL["copper"], 0.92, w=0.8)
            d.ink(ellipse_pts(px - 2, y + 16, 3, 2, 8, a0=3.3, a1=4.6), 0.7, PAL["white"], op=0.8)
        else:  # ladle
            d.ink([(px, y + 4), (px, y + 18)], 0.9, INK)
            d.shape(ellipse_pts(px, y + 21, 4, 3, 10), "#9a9a9a", 0.92, w=0.6)


def dresser(d, x, y, w, h):
    """Kitchen dresser with plates; (x,y) bottom-left."""
    d.shape(rect_pts(x, y - h * 0.42, w, h * 0.42, 12), PAL["wood"], 0.9, w=1.0, smooth_=False)
    for k in range(2):
        d.shape(rect_pts(x + 3 + k * (w - 6) / 2, y - h * 0.4 + 3, (w - 6) / 2 - 2, h * 0.36 - 4, 10), PAL["woodlt"], 0.8, w=0.6, smooth_=False)
        d.dot(x + 3 + k * (w - 6) / 2 + (w - 6) / 4, y - h * 0.22, 1.1)
    d.shape(rect_pts(x + 2, y - h, w - 4, h * 0.58, 12), PAL["wooddk"], 0.85, w=0.9, smooth_=False)
    for row in range(2):
        sy = y - h * 0.42 - row * h * 0.27
        d.line(x + 2, sy - 1, x + w - 2, sy - 1, 1, INK, 0)
        n = int((w - 6) / 12)
        for i in range(n):
            px = x + 9 + i * ((w - 12) / n)
            d.shape(ellipse_pts(px, sy - h * 0.12, 5.5, 5.5, 14), PAL["white"], 0.95, w=0.6)
            d.ink(ellipse_pts(px, sy - h * 0.12, 3.6, 3.6, 12), 0.6, PAL["navy"], closed=True, op=0.8)


def hat_pegs(d, x, y, w):
    beam(d, x, y, w, 4, PAL["wood"])
    n = int(w / 18)
    for i in range(n):
        px = x + 9 + i * 18
        d.line(px, y + 4, px, y + 8, 1.2, INK, 0)
        kind = i % 4
        if kind == 0:  # cloak
            d.shape([(px - 2, y + 7), (px - 8, y + 20), (px - 10, y + 44), (px + 10, y + 44), (px + 8, y + 20), (px + 2, y + 7)],
                    d.choice([PAL["door2"], PAL["red"], "#8a6a8a"]), 0.88, w=0.9)
            d.ink([(px - 3, y + 15), (px - 4, y + 40)], 0.5, INK_SOFT, op=0.6)
            d.ink([(px + 3, y + 15), (px + 4, y + 40)], 0.5, INK_SOFT, op=0.6)
        elif kind == 1:  # hooded coat
            d.shape([(px - 2, y + 7), (px - 7, y + 16), (px - 8, y + 34), (px + 8, y + 34), (px + 7, y + 16), (px + 2, y + 7)],
                    d.choice([PAL["blue"], PAL["ochre"], PAL["teal"]]), 0.88, w=0.9)
        elif kind == 2:  # scarf
            d.shape([(px - 2, y + 7), (px - 4, y + 30), (px, y + 32), (px + 4, y + 30), (px + 2, y + 7)], PAL["rose"], 0.9, w=0.7)
            for k in range(3):
                d.line(px - 3.5, y + 14 + k * 6, px + 3.5, y + 14 + k * 6, 0.5, PAL["red"], 0)
        else:  # walking stick and umbrella
            d.ink([(px, y + 8), (px - 1, y + 46)], 1.4, PAL["wooddk"])
            d.ink(ellipse_pts(px + 3, y + 9, 3, 3, 8, a0=math.pi, a1=2 * math.pi), 1.4, PAL["wooddk"])


def wine_rack(d, x, y, w, h, r=5.5):
    d.shape(rect_pts(x, y - h, w, h, 14), "#4a3524", 0.9, w=1.0, smooth_=False)
    cols = int(w / (r * 2 + 2))
    rows = int(h / (r * 2 + 2))
    for i in range(cols):
        for j in range(rows):
            cx = x + r + 2 + i * (r * 2 + 2)
            cy = y - h + r + 2 + j * (r * 2 + 2)
            d.shape(ellipse_pts(cx, cy, r, r, 10), d.choice(["#2f4a3a", "#5a2a2a", "#3a4a2a"]), 0.95, w=0.5)
            d.dot(cx - r * 0.3, cy - r * 0.3, 0.9, PAL["white"], 0.7)


def ladder(d, x1, y1, x2, y2, wdt=12, rungs=None):
    L = math.hypot(x2 - x1, y2 - y1)
    rungs = rungs or int(L / 10)
    nx, ny = (y2 - y1) / L * wdt / 2, -(x2 - x1) / L * wdt / 2
    for s in (-1, 1):
        d.ink(line_pts(x1 + nx * s, y1 + ny * s, x2 + nx * s, y2 + ny * s, 0.5, d.rng), 1.6, PAL["wooddk"])
    for i in range(1, rungs):
        t = i / rungs
        cx, cy = lerp(x1, x2, t), lerp(y1, y2, t)
        d.line(cx - nx, cy - ny, cx + nx, cy + ny, 1.2, PAL["wooddk"], 0.2)


def steps(d, x, y, n, sw=10, sh=7, direction=1, color=None):
    """Stone steps going down; (x,y) top of first step."""
    color = color or PAL["stone"]
    for i in range(n):
        sx = x + i * sw * direction
        sy = y + i * sh
        px = sx if direction > 0 else sx - sw
        d.shape(rect_pts(px, sy, sw + 2, sh, 6), color, 0.85, w=0.8, smooth_=False)


def round_door(d, cx, cy, r, color=None, open_=False):
    color = color or PAL["door"]
    # frame
    d.shape(ellipse_pts(cx, cy, r * 1.14, r * 1.14, 36), PAL["woodlt"], 0.9, w=1.2)
    for k in range(18):
        a = k * 2 * math.pi / 18
        d.line(cx + r * 1.0 * math.cos(a), cy + r * 1.0 * math.sin(a), cx + r * 1.14 * math.cos(a), cy + r * 1.14 * math.sin(a), 0.6, INK, 0)
    d.shape(ellipse_pts(cx, cy, r, r, 36), color, 0.92, w=1.1)
    # planks
    for k in range(-3, 4):
        xx = cx + k * r / 4
        hh = math.sqrt(max(0, r * r - (k * r / 4) ** 2))
        if k > -4:
            d.line(xx, cy - hh + 2, xx, cy + hh - 2, 0.55, INK, 0.3)
    # shading & highlight
    d.wash(ellipse_pts(cx + r * 0.25, cy + r * 0.2, r * 0.7, r * 0.75, 20), PAL["door2"], 0.4)
    d.ink(ellipse_pts(cx, cy, r * 0.88, r * 0.88, 24, a0=3.4, a1=4.6), 1.2, "#9cc08f", op=0.6)
    # brass knob in the middle
    d.shape(ellipse_pts(cx, cy, r * 0.09, r * 0.09, 12), PAL["brass"], 1, w=0.8)
    d.dot(cx - r * 0.025, cy - r * 0.03, r * 0.025, PAL["white"])
    # hinges
    for hy in (-0.45, 0.45):
        d.shape(rect_pts(cx - r * 0.95, cy + r * hy - 2, r * 0.5, 4), "#3a3a3a", 0.9, w=0.5, smooth_=False)


def round_window(d, cx, cy, r, curtain=None, glow=True):
    curtain = curtain or PAL["rose"]
    d.shape(ellipse_pts(cx, cy, r * 1.15, r * 1.15, 28), PAL["woodlt"], 0.9, w=1.0)
    d.shape(ellipse_pts(cx, cy, r, r, 28), "#fbe39a" if glow else PAL["sky"], 0.9, w=0.9)
    d.line(cx - r, cy, cx + r, cy, 1.2, PAL["wooddk"], 0)
    d.line(cx, cy - r, cx, cy + r, 1.2, PAL["wooddk"], 0)
    for s in (-1, 1):
        d.shape([(cx + s * r * 0.95, cy - r * 0.35), (cx + s * r * 0.45, cy - r * 0.6), (cx + s * r * 0.55, cy + r * 0.3),
                 (cx + s * r * 0.9, cy + r * 0.4)], curtain, 0.85, w=0.6)
    # window box with flowers
    d.shape(rect_pts(cx - r * 1.1, cy + r * 1.05, r * 2.2, r * 0.32, 10), PAL["wood"], 0.9, w=0.8, smooth_=False)
    for k in range(7):
        flower(d, cx - r * 0.95 + k * r * 0.32, cy + r * 1.0 + d.r(1.5), r * 0.12)


def fence(d, x1, y1, x2, y2, h=18, n=8):
    for i in range(n + 1):
        t = i / n
        px, py = lerp(x1, x2, t), lerp(y1, y2, t)
        d.shape([(px - 2, py + 2), (px - 2, py - h), (px, py - h - 3), (px + 2, py - h), (px + 2, py + 2)], PAL["woodlt"], 0.9, w=0.7, smooth_=False)
    for k in (0.35, 0.75):
        d.ink(line_pts(x1, y1 - h * k, x2, y2 - h * k, 0.8, d.rng), 1.3, PAL["wooddk"])


def gear(d, cx, cy, r, teeth=10, color=None, rot=0.0):
    color = color or PAL["wood"]
    pts = []
    for i in range(teeth * 4):
        a = rot + 2 * math.pi * i / (teeth * 4)
        k = r * 1.0 if (i % 4) in (0, 1) else r * 0.82
        pts.append((cx + k * math.cos(a), cy + k * math.sin(a)))
    d.shape(pts, color, 0.9, w=1.0, smooth_=False)
    d.shape(ellipse_pts(cx, cy, r * 0.25, r * 0.25, 12), PAL["wooddk"], 0.95, w=0.8)
    for k in range(4):
        a = rot + k * math.pi / 2 + math.pi / 4
        d.line(cx + r * 0.25 * math.cos(a), cy + r * 0.25 * math.sin(a), cx + r * 0.7 * math.cos(a), cy + r * 0.7 * math.sin(a), 1.4, PAL["wooddk"], 0)
    d.ink(ellipse_pts(cx, cy, r * 0.72, r * 0.72, 20), 0.8, INK, closed=True, op=0.8)


def rope(d, pts, w=1.6):
    d.ink(pts, w, "#b8955a")
    d.ink(pts, w * 0.35, INK_SOFT, op=0.6, dash="2 3")
