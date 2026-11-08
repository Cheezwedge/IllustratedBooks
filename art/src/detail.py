"""High-detail painterly objects for the watercolour engine (wc.Canvas).

These are deliberately small-scale and dense: the look depends on many tiny, carefully
shaded things (leaves, blades, crockery, jars, grain) rather than a few big shapes.
"""
import math
from kit import PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, arch_pts, line_pts, lerp, transform_pts, inside
import objects as O

LEAF_LIGHT = ["#b7c77a", "#a6bd6a", "#c4cf86"]
LEAF_MID = ["#86a557", "#7d9d50", "#90ab5e", "#7a9a4f"]
LEAF_DARK = ["#5e7e3e", "#56743a", "#4d6a36", "#647f42"]


# =============================================================== foliage
def leaf_shape(x, y, L, ang, wdt=0.42, n=6):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((t * L, math.sin(math.pi * t) ** 0.8 * L * wdt / 2))
    for i in range(n - 1, 0, -1):
        t = i / n
        pts.append((t * L, -math.sin(math.pi * t) ** 0.8 * L * wdt / 2))
    return transform_pts(pts, x, y, 1, ang)


def leafy_mass(d, cx, cy, rx, ry, clumps=14, leaves=500, leaf_len=(4, 7), ink_frac=0.16, palette=None):
    """A tree crown or hedge built the way a watercolourist builds one: rounded clumps lit from the
    upper left, dark pockets beneath them, and the silhouettes formed by hundreds of individual leaves."""
    light, mid, dark = palette or (LEAF_LIGHT, LEAF_MID, LEAF_DARK)
    cl = []
    for _ in range(clumps):
        a = d.u(0, 2 * math.pi)
        r = math.sqrt(d.u(0.02, 1)) * 0.74
        x, y = cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)
        rr = d.u(0.22, 0.36) * min(rx, ry) * (1.15 if y < cy else 1.0)
        cl.append((y, x, rr))
    cl.sort(key=lambda c: (c[0], -c[1]))      # paint back clumps (higher) first
    avg_r = sum(c[2] for c in cl) / len(cl)
    for y, x, rr in cl:                      # pass 1: clump washes
        t = (y - (cy - ry)) / (2 * ry)
        base = d.choice(dark) if t > 0.7 else d.choice(mid)
        d.wash(blob(x, y, rr * 0.86, rr * 0.76, d.rng, 0.16, 16), base, 0.5, shade=0.85, edge=0.3, hatch=False)
        d.wash(blob(x + rr * 0.3, y + rr * 0.4, rr * 0.65, rr * 0.36, d.rng, 0.2, 12), d.choice(dark), 0.4, hatch=False, edge=0.1, shade=0.3)
    for y, x, rr in cl:                      # pass 2: leaves on top
        per = max(6, int(leaves / max(1, clumps) * (rr / avg_r) ** 1.6))
        for i in range(per):
            rim = d.chance(0.62)
            a = d.u(0, 2 * math.pi)
            k = d.u(0.72, 1.06) if rim else math.sqrt(d.u(0, 0.7))
            lx, ly = x + rr * k * math.cos(a), y + rr * 0.88 * k * math.sin(a)
            loc = (math.cos(a) + math.sin(a)) * k * 0.7 + ((lx - cx) / rx + (ly - cy) / ry) * 0.35
            if loc < -0.45:
                col = d.choice(light)
            elif loc > 0.45:
                col = d.choice(dark)
            else:
                col = d.choice(mid)
            L = d.u(*leaf_len)
            ang = a + d.r(1.2) if rim else d.u(0, 2 * math.pi)
            pts = leaf_shape(lx, ly, L, ang, d.u(0.4, 0.55))
            d.wash(pts, col, 0.85, jitter=0.1, shade=0.35, gran=0.12, edge=0.55, hatch=False)
            if d.chance(ink_frac):
                d.ink(pts, 0.45, INK_SOFT, True, op=0.7, jitter=0.08)
    for _ in range(int(clumps / 3)):
        x, y = cx + d.r(rx * 0.5), cy + d.r(ry * 0.4)
        d.ink([(x, y), (x + d.r(8), y + d.u(4, 10)), (x + d.r(12), y + d.u(10, 18))], 0.8, "#6e5238", op=0.7)


def oak_tree(d, x, ybase, h, w, crown_rx, crown_ry, lean=0, leaves=900):
    """Trunk with bark texture, branching limbs and a painterly crown."""
    top = ybase - h
    trunk = [(x - w * 1.0, ybase + 4), (x - w * 0.6, ybase - 10), (x - w * 0.48, ybase - h * 0.45), (x - w * 0.4 + lean, top),
             (x + w * 0.4 + lean, top), (x + w * 0.5, ybase - h * 0.45), (x + w * 0.62, ybase - 10), (x + w * 1.05, ybase + 4)]
    d.shape(trunk, "#8a6a4c", 0.9, w=1.1, shade=0.8)
    for i in range(int(w * 0.9)):
        bx = x - w * 0.45 + i * (w * 0.9) / (w * 0.9) * 1.1 + d.r(1)
        y0 = d.u(top + 4, ybase - 20)
        L = d.u(10, 34)
        d.ink([(bx, y0), (bx + d.r(1.2), y0 + L * 0.5), (bx + d.r(1.5), y0 + L)], 0.55, INK_SOFT, op=0.7)
    # moss on the shady side
    d.wash([(x + w * 0.15, ybase - 6), (x + w * 0.55, ybase - 8), (x + w * 0.45, ybase - h * 0.5), (x + w * 0.2, ybase - h * 0.45)],
           "#8ea05c", 0.35, soft=True)
    # limbs
    for (dx, dy, ex, ey, ww) in ((-0.1, 0.0, -0.75, -0.35, 7), (0.1, 0.05, 0.7, -0.4, 7), (0, 0, -0.25, -0.75, 5), (0, 0, 0.3, -0.7, 5)):
        sx, sy = x + lean + dx * w, top + 8 + dy * h
        exx, eyy = x + ex * crown_rx * 0.7, top + ey * crown_ry * 0.8 + 20
        d.ink([(sx, sy), ((sx + exx) / 2 + d.r(6), (sy + eyy) / 2 - 6), (exx, eyy)], ww, "#7a5b40", op=0.95)
        d.ink([(sx, sy), ((sx + exx) / 2 + d.r(6), (sy + eyy) / 2 - 6), (exx, eyy)], 0.7, INK, op=0.7)
    leafy_mass(d, x + lean, top - crown_ry * 0.45, crown_rx, crown_ry, clumps=30, leaves=leaves, leaf_len=(5, 9))


# ================================================================ meadow
def blades(d, surface, every=2.2, h=(5, 13), colors=None, lean=0.35, op=0.9):
    colors = colors or ["#7d9d50", "#90ab5e", "#6b8c45", "#a6b86a", "#b9b06a"]
    for (x1, y1), (x2, y2) in zip(surface, surface[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        for j in range(max(1, int(L / every))):
            t = j / max(1, int(L / every))
            x, y = lerp(x1, x2, t) + d.r(1), lerp(y1, y2, t) + d.u(0, 2)
            hh = d.u(*h)
            a = -math.pi / 2 + d.r(lean)
            bend = d.r(2.5)
            tip = (x + hh * math.cos(a) + bend, y + hh * math.sin(a))
            mid = (x + hh * 0.5 * math.cos(a) + bend * 0.3, y + hh * 0.5 * math.sin(a))
            d.ink([(x, y), mid, tip], d.u(0.7, 1.2), d.choice(colors), op=op, jitter=0.2)


def wildflower(d, x, y, kind=None, s=1.0):
    kind = kind or d.choice(["daisy", "daisy", "buttercup", "clover", "forgetmenot", "poppy", "harebell", "campion"])
    stem_h = {"daisy": 9, "buttercup": 12, "clover": 6, "forgetmenot": 8, "poppy": 15, "harebell": 13, "campion": 14}[kind] * s * d.u(0.7, 1.2)
    top = (x + d.r(2), y - stem_h)
    d.ink([(x, y), ((x + top[0]) / 2 + d.r(1), (y + top[1]) / 2), top], 0.6, "#6b8c45", op=0.9, jitter=0.1)
    fx, fy = top
    if kind == "daisy":
        for k in range(9):
            a = k * 2 * math.pi / 9
            d.wash(leaf_shape(fx, fy, 2.6 * s, a, 0.5, 4), "#fffdf6", 1.0, jitter=0.05)
            d.ink(leaf_shape(fx, fy, 2.6 * s, a, 0.5, 4), 0.3, "#9a8f7a", True, op=0.5, jitter=0.05)
        d.wash(ellipse_pts(fx, fy, 1.0 * s, 1.0 * s, 8), "#e3b43a", 0.95, jitter=0.05)
    elif kind == "buttercup":
        for k in range(5):
            a = k * 2 * math.pi / 5 - math.pi / 2
            d.wash(ellipse_pts(fx + 1.3 * s * math.cos(a), fy + 1.3 * s * math.sin(a), 1.4 * s, 1.3 * s, 8), "#f0c53a", 0.95, jitter=0.05)
        d.dot(fx, fy, 0.5 * s, "#a07a20")
    elif kind == "clover":
        d.wash(ellipse_pts(fx, fy, 2.0 * s, 2.3 * s, 10), "#e2a6b6", 0.9, jitter=0.1, shade=0.6)
        for k in range(6):
            d.dot(fx + d.r(1.4 * s), fy + d.r(1.6 * s), 0.35 * s, "#b9607e")
        for k in (-1, 1):
            d.wash(ellipse_pts(x + k * 2.5 * s, y - 2 * s, 1.8 * s, 1.3 * s, 8), "#7d9d50", 0.85, jitter=0.05)
    elif kind == "forgetmenot":
        for c in range(3):
            ox, oy = fx + d.r(2.5 * s), fy + d.r(2 * s)
            for k in range(5):
                a = k * 2 * math.pi / 5
                d.wash(ellipse_pts(ox + 0.8 * s * math.cos(a), oy + 0.8 * s * math.sin(a), 0.75 * s, 0.75 * s, 6), "#7fa2d4", 0.95, jitter=0.03)
            d.dot(ox, oy, 0.3 * s, "#e3c43a")
    elif kind == "poppy":
        d.wash(blob(fx, fy, 3.2 * s, 2.6 * s, d.rng, 0.15, 10), "#d6533a", 0.92, jitter=0.1, shade=0.6)
        d.dot(fx, fy - 0.3 * s, 0.8 * s, "#2f2a2a")
    elif kind == "harebell":
        d.ink([(fx, fy), (fx + 2 * s, fy + 1 * s)], 0.5, "#6b8c45")
        bell = [(fx + 1 * s, fy + 0.5 * s), (fx + 0.2 * s, fy + 4 * s), (fx + 1.5 * s, fy + 5.2 * s), (fx + 2.8 * s, fy + 5.4 * s),
                (fx + 4 * s, fy + 4.4 * s), (fx + 3 * s, fy + 0.8 * s)]
        d.shape(bell, "#8f95cf", 0.92, w=0.35, ink_color=INK_SOFT)
    else:  # red campion
        for k in range(5):
            a = k * 2 * math.pi / 5 - math.pi / 2
            d.wash(ellipse_pts(fx + 1.5 * s * math.cos(a), fy + 1.5 * s * math.sin(a), 1.2 * s, 1.0 * s, 8), "#d77aa0", 0.92, jitter=0.05)


def meadow(d, surface, density=0.6, flowers=0.18, h=(5, 13)):
    """Grass blades along a surface with scattered wildflowers."""
    blades(d, surface, every=2.6 / density, h=h)
    for (x1, y1), (x2, y2) in zip(surface, surface[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        for j in range(int(L * flowers / 6)):
            t = d.u(0, 1)
            wildflower(d, lerp(x1, x2, t), lerp(y1, y2, t) + d.u(0, 1.5), s=d.u(0.8, 1.15))


def foxglove(d, x, y, h=48):
    d.ink([(x, y), (x + 1, y - h * 0.5), (x + 2, y - h)], 1.0, "#6b8c45")
    for k in range(9):
        t = 0.35 + k * 0.07
        bx, by = x + 1 + t * 1.5, y - h * t
        side = 1 if k % 2 else -1
        bell = transform_pts([(0, -1.5), (5, -2.3), (6.5, 0), (5, 2.3), (0, 1.5)], bx, by, 1 - t * 0.4, math.pi / 2 + side * 0.9)
        d.shape(bell, "#c97fb0", 0.9, w=0.35, ink_color=INK_SOFT)
    for k in (-1, 1):
        O.leaf(d, x, y - 2, 13, -math.pi / 2 + k * 1.1, "#7d9d50", wdt=0.35, ink_w=0.4)


def bramble_spray(d, x, y, L, ang, berries=True):
    import small
    small.bramble_branch(d, x, y, x + L * math.cos(ang), y + L * math.sin(ang), 1 if math.cos(ang) >= 0 else -1)


# ============================================================ earth & stone
def stratum(d, pts_top, depth, color, op=0.35):
    lower = [(x + d.r(3), y + depth + d.r(depth * 0.25)) for x, y in pts_top[::-1]]
    d.wash(pts_top + lower, color, op, soft=True)


def fine_roots(d, x, y, ang, length, w, depth=3, avoid=None, ymin=None):
    """Lighter, finer roots with root-hairs (wraps objects.root)."""
    O.root(d, x, y, ang, length, w, depth, color="#9a7552", avoid=avoid, ymin=ymin)


def shaded_pebbles(d, polygon, n, rmin=2, rmax=7):
    O.pebbles(d, polygon, n, rmin, rmax, ["#cdbfa6", "#b9aa90", "#d8c7a6", "#a99a82", "#c9a882"])


# ================================================================ wood
def planked_wall(d, x, y, w, h, n, color="#c8a06e", grain=True):
    for i in range(n):
        px = x + i * w / n
        pw = w / n
        tint = d.choice([color, "#c09363", "#d0a876", color])
        d.wash(rect_pts(px, y, pw, h, 12), tint, 0.85, smooth_=False, shade=0.25)
        d.line(px, y, px, y + h, 0.5, INK, 0.3, op=0.8)
        if grain:
            for g in range(3):
                gx = px + pw * d.u(0.2, 0.8)
                pts = [(gx + 0.8 * math.sin(k * 0.9 + g), y + h * k / 8) for k in range(9)]
                d.ink(pts, 0.35, "#8a6440", op=0.5, jitter=0.2)
            if d.chance(0.35):
                kx, ky = px + pw * d.u(0.3, 0.7), y + h * d.u(0.2, 0.8)
                d.ink(ellipse_pts(kx, ky, 1.2, 2.2, 8), 0.4, "#6e4e30", True, op=0.7)


def beam_grain(d, x, y, w, h, color="#9a7048"):
    d.shape(rect_pts(x, y, w, h, 24), color, 0.9, w=0.8, smooth_=False, shade=0.6)
    for k in range(max(1, int(h / 2.2))):
        yy = y + (k + 0.5) * h / max(1, int(h / 2.2))
        pts = [(x + w * t / 10, yy + 0.5 * math.sin(t * 1.3 + k)) for t in range(11)]
        d.ink(pts, 0.3, "#6e4e30", op=0.45, jitter=0.15)


# ============================================================= interiors
def plaster_room(d, x, top, w, floor, archh, wall="#f0dfba", label=None, panel=True, floor_kind="flags"):
    pts = arch_pts(x, top, w, floor - top, archh, 20)
    # dug-earth rim
    d.wash([(px + (px - (x + w / 2)) * 0.03, py + (py - (top + floor) / 2) * 0.045) for px, py in pts], "#8f6a46", 0.75, shade=0.2)
    d.wash(pts, wall, 0.95, shade=0.25, cover=0.95)
    # lamp-warmth and soft corner shadow
    d.wash(ellipse_pts(x + w / 2, (top + floor) / 2 + 6, w * 0.4, (floor - top) * 0.36, 20), "#f7dfa4", 0.35, soft=True)
    d.wash(pts[:6], "#b39274", 0.25, soft=True)
    # faint plaster texture
    for _ in range(int(w * (floor - top) / 900)):
        px, py = x + d.u(6, w - 6), top + archh * 0.6 + d.u(0, floor - top - archh * 0.6 - 10)
        d.ink([(px, py), (px + d.u(2, 5), py + d.r(1))], 0.3, "#b59b78", op=0.4, jitter=0.2)
    if panel:
        wy = floor - (floor - top) * 0.3
        planked_wall(d, x + 2, wy, w - 4, floor - wy - 8, max(4, int(w / 11)))
        beam_grain(d, x + 1, wy - 3.5, w - 2, 4)
    if floor_kind == "flags":
        flags(d, x + 1, floor - 8, w - 2, 8)
    else:
        boards(d, x + 1, floor - 8, w - 2, 8)
    # arched ceiling ribs
    d.ink(arch_pts(x + 4, top + 4, w - 8, floor - top - 4, archh - 3, 20)[1:-2], 3.2, "#9a7048", op=0.9)
    d.ink(arch_pts(x + 4, top + 4, w - 8, floor - top - 4, archh - 3, 20)[1:-2], 0.6, INK, op=0.6)
    d.ink(pts, 1.1, INK, closed=True)
    if label:
        d.text(x + w / 2, top + archh * 0.5 + 11, label, size=11.5, italic=True)
    return pts


def flags(d, x, y, w, h):
    cx = x
    while cx < x + w - 2:
        fw = d.u(9, 15)
        d.wash(rect_pts(cx, y, min(fw, x + w - cx), h, 6), d.choice(["#c9b79a", "#b9a68a", "#d3c3a4"]), 0.9, smooth_=False, shade=0.5)
        d.ink(rect_pts(cx, y, min(fw, x + w - cx), h, 6), 0.4, INK_SOFT, True, op=0.6, smooth_=False)
        cx += fw


def boards(d, x, y, w, h):
    d.wash(rect_pts(x, y, w, h, 10), "#b98a5a", 0.9, smooth_=False, shade=0.4)
    cx = x
    while cx < x + w:
        cx += d.u(14, 26)
        d.line(cx, y, cx, y + h, 0.4, INK_SOFT, 0.1, op=0.7)


def rag_rug(d, cx, y, w, h=5):
    cols = ["#c2674e", "#d9a65a", "#7f9cb5", "#9cb07a", "#c99ab0"]
    d.wash(ellipse_pts(cx, y - h / 2, w / 2, h / 2 + 1, 24), "#b8946a", 0.9, shade=0.3)
    for k in range(6):
        rr = (k + 1) / 7
        d.ink(ellipse_pts(cx, y - h / 2, w / 2 * rr, (h / 2 + 1) * rr, 24), 1.1, cols[k % len(cols)], True, op=0.9, jitter=0.1)


def gingham(d, pts_rect, color="#c96a5a"):
    x, y, w, h = pts_rect
    d.wash(rect_pts(x, y, w, h, 8), "#fbf3e3", 0.95, smooth_=False)
    for i in range(int(w / 3)):
        d.line(x + i * 3 + 1.5, y, x + i * 3 + 1.5, y + h, 0.9, color, 0, op=0.45)
    for j in range(int(h / 3)):
        d.line(x, y + j * 3 + 1.5, x + w, y + j * 3 + 1.5, 0.9, color, 0, op=0.45)


def tea_table(d, x, floor, w=40, h=27):
    for lx in (x - w / 2 + 4, x + w / 2 - 6):
        leg = [(lx, floor), (lx - 0.5, floor - h * 0.4), (lx + 0.8, floor - h * 0.6), (lx, floor - h), (lx + 2.5, floor - h),
               (lx + 1.8, floor - h * 0.6), (lx + 3, floor - h * 0.4), (lx + 2.5, floor)]
        d.shape(leg, "#8a5f3a", 0.95, w=0.6)
    cloth = [(x - w / 2 - 3, floor - h), (x - w / 2 - 4, floor - h + 10), (x + w / 2 + 4, floor - h + 10), (x + w / 2 + 3, floor - h)]
    gingham(d, (x - w / 2 - 4, floor - h, w + 8, 10))
    d.ink(cloth, 0.7, INK, True, op=0.8, smooth_=False)
    for i in range(int((w + 8) / 2.4)):
        cx = x - w / 2 - 4 + i * 2.4
        d.ink([(cx, floor - h + 10), (cx + 0.3, floor - h + 12)], 0.5, "#c96a5a", op=0.7)
    ty = floor - h
    teapot_fine(d, x - 8, ty, 0.62)
    cup_saucer(d, x + 7, ty, 0.62)
    cup_saucer(d, x + 15, ty, 0.55)
    O.cake(d, x - 22 + 3, ty - 0.5, 0.42)
    jam_pot(d, x + 1, ty, 0.5)


def teapot_fine(d, x, y, s=1.0):
    body = ellipse_pts(x, y - 9 * s, 11 * s, 9 * s, 28)
    d.shape(body, "#e9eef2", 0.95, w=0.8)
    d.wash(ellipse_pts(x + 3 * s, y - 7 * s, 8 * s, 6 * s, 16), "#a9b6c6", 0.35, soft=True)
    for k in range(7):
        a = k * 2 * math.pi / 7
        fx, fy = x + 7 * s * math.cos(a) * 0.9, y - 9 * s + 5 * s * math.sin(a) * 0.8
        d.dot(fx, fy, 1.1 * s, "#5d7fb0")
        d.dot(fx + 1.2 * s, fy + 0.6 * s, 0.6 * s, "#7f9c4d")
    spout = [(x + 9 * s, y - 10 * s), (x + 15 * s, y - 13 * s), (x + 19 * s, y - 19 * s), (x + 20.5 * s, y - 18.5 * s),
             (x + 17 * s, y - 11 * s), (x + 9 * s, y - 5 * s)]
    d.shape(spout, "#e9eef2", 0.95, w=0.7)
    d.ink(ellipse_pts(x - 13 * s, y - 10 * s, 5 * s, 5.5 * s, 14, a0=math.pi * 0.4, a1=math.pi * 1.6), 1.6 * s, "#5d7fb0")
    d.shape(ellipse_pts(x, y - 18 * s, 6 * s, 2 * s, 14), "#e9eef2", 0.95, w=0.6)
    d.shape(ellipse_pts(x, y - 20.5 * s, 1.8 * s, 1.8 * s, 8), "#5d7fb0", 0.9, w=0.5)
    O.steam(d, x + 21 * s, y - 21 * s, 14 * s, 0.5)


def cup_saucer(d, x, y, s=1.0):
    d.shape(ellipse_pts(x, y - 0.5 * s, 7 * s, 1.6 * s, 14), "#f3f1ea", 0.95, w=0.5)
    cup = [(x - 4.5 * s, y - 7 * s), (x - 3.8 * s, y - 2 * s), (x - 2 * s, y - 0.8 * s), (x + 2 * s, y - 0.8 * s), (x + 3.8 * s, y - 2 * s),
           (x + 4.5 * s, y - 7 * s)]
    d.shape(cup, "#f3f1ea", 0.95, w=0.6)
    d.line(x - 4.2 * s, y - 5.5 * s, x + 4.2 * s, y - 5.5 * s, 0.8, "#5d7fb0", 0, op=0.8)
    d.ink(ellipse_pts(x + 5.3 * s, y - 4.5 * s, 1.8 * s, 1.8 * s, 8, a0=-1.5, a1=1.5), 0.6, INK)


def jam_pot(d, x, y, s=1.0):
    d.shape(rect_pts(x - 4 * s, y - 9 * s, 8 * s, 9 * s, 4), "#b33d45", 0.9, w=0.6, smooth_=False)
    d.shape([(x - 5 * s, y - 8 * s), (x - 4 * s, y - 10.5 * s), (x + 4 * s, y - 10.5 * s), (x + 5 * s, y - 8 * s), (x, y - 7.5 * s)],
            "#f1e6cf", 0.95, w=0.5)
    d.dot(x - 1.5 * s, y - 9.5 * s, 0.5 * s, "#c96a5a")
    d.dot(x + 1.5 * s, y - 9.2 * s, 0.5 * s, "#c96a5a")


def wing_chair(d, x, floor, s=1.0, fabric="#b8574a"):
    back = [(x - 15 * s, floor - 15 * s), (x - 17 * s, floor - 34 * s), (x - 12 * s, floor - 44 * s), (x - 2 * s, floor - 46 * s),
            (x + 8 * s, floor - 45 * s), (x + 15 * s, floor - 39 * s), (x + 16 * s, floor - 15 * s)]
    d.shape(back, fabric, 0.9, w=0.9, shade=0.7)
    # tiny flower print
    for _ in range(int(30 * s)):
        px, py = x + d.u(-14, 14) * s, floor - d.u(17, 42) * s
        if inside((px, py), back):
            d.dot(px, py, 0.55 * s, "#f0d9a8", 0.9)
            d.dot(px + 0.6 * s, py + 0.5 * s, 0.35 * s, "#7f9c4d", 0.9)
    seat = rect_pts(x - 17 * s, floor - 17 * s, 34 * s, 8 * s, 8)
    d.shape(seat, fabric, 0.92, w=0.8, shade=0.6)
    for sx in (-1, 1):
        arm = [(x + sx * 14 * s, floor - 7 * s), (x + sx * 14 * s, floor - 22 * s), (x + sx * 20 * s, floor - 26 * s), (x + sx * 23.5 * s, floor - 22 * s),
               (x + sx * 21 * s, floor - 18 * s), (x + sx * 20 * s, floor - 7 * s)]
        d.shape(arm, fabric, 0.92, w=0.8, shade=0.7)
    # patchwork cushion
    cush = rect_pts(x - 8 * s, floor - 27 * s, 16 * s, 10 * s, 6)
    d.shape(cush, "#e8d2a0", 0.95, w=0.6)
    for i in range(3):
        for j in range(2):
            col = d.choice(["#7f9cb5", "#c99ab0", "#9cb07a", "#d9a65a"])
            d.wash(rect_pts(x - 8 * s + i * 5.3 * s, floor - 27 * s + j * 5 * s, 5.3 * s, 5 * s, 4), col, 0.7, smooth_=False, shade=0.2)
    d.ink([(x - 8 * s, floor - 22 * s), (x + 8 * s, floor - 22 * s)], 0.4, INK, dash="1 1")
    # lace antimacassar
    lace = [(x - 7 * s, floor - 44 * s), (x + 7 * s, floor - 44 * s), (x + 6 * s, floor - 36 * s), (x - 6 * s, floor - 36 * s)]
    d.shape(lace, "#fffdf6", 0.95, w=0.4, ink_color=INK_SOFT)
    for k in range(7):
        d.dot(x - 6 * s + k * 2 * s, floor - 35.5 * s, 0.5 * s, INK_SOFT)
    for lx in (-15, 15):
        d.shape([(x + lx * s - 1.5 * s, floor - 7 * s), (x + lx * s - 1 * s, floor), (x + lx * s + 1 * s, floor), (x + lx * s + 1.5 * s, floor - 7 * s)],
                "#6e4a2c", 0.95, w=0.5)


def inglenook(d, x, floor, w=66, h=82):
    """Stone fireplace with logs, fire, kettle on a crane, bellows, fire irons, log basket and a crowded mantel."""
    O.stone_wall(d, x - w / 2, floor - h, w, h, course=h / 7, colors=["#cbbfa9", "#bcae95", "#d6cab3", "#b2a48b"], mortar="#e9dcc0", ink_op=0.6)
    beam_grain(d, x - w / 2 - 7, floor - h - 7, w + 14, 7, "#8a6440")
    ow, oh = w * 0.62, h * 0.62
    op = arch_pts(x - ow / 2, floor - oh, ow, oh, oh * 0.3, 16)
    d.shape(op, "#4a3a30", 0.92, w=0.9, shade=0.3)
    d.glow(x, floor - oh * 0.28, w * 1.05, "#f2a63c", 0.75)
    # logs
    for lx, a in ((-0.16, 0.08), (0.14, -0.1)):
        lg = transform_pts(rect_pts(-11, -2.5, 22, 5, 8), x + lx * ow, floor - 6, 1, a)
        d.shape(lg, "#7a5534", 0.95, w=0.6)
        d.wash(ellipse_pts(x + lx * ow + 10 * math.cos(a), floor - 6 + 10 * math.sin(a), 1.6, 2.6, 8), "#e6c79a", 0.9)
    # layered flames: soft red base, orange, yellow tongues
    for col, sc, n in (("#d9502e", 1.0, 5), ("#f08a32", 0.8, 6), ("#f8cf5a", 0.55, 5)):
        for k in range(n):
            fx = x + d.r(ow * 0.28)
            fh = oh * d.u(0.32, 0.6) * sc
            fl = [(fx - 5 * sc, floor - 7), (fx - 3 * sc, floor - 7 - fh * 0.5), (fx + d.r(2), floor - 7 - fh),
                  (fx + 3 * sc, floor - 7 - fh * 0.45), (fx + 5 * sc, floor - 7)]
            d.wash(fl, col, 0.85, shade=0.0, gran=0.05, edge=0.25)
    # kettle on a crane
    kx = x + ow * 0.12
    d.line(x - ow * 0.4, floor - oh * 0.88, kx, floor - oh * 0.88, 1.2, "#3a3a3a", 0)
    d.line(kx, floor - oh * 0.88, kx, floor - oh * 0.8, 0.8, "#3a3a3a", 0)
    pot = [(kx - 6, floor - oh * 0.78), (kx - 7, floor - oh * 0.7), (kx - 5, floor - oh * 0.6), (kx + 5, floor - oh * 0.6),
           (kx + 7, floor - oh * 0.7), (kx + 6, floor - oh * 0.78)]
    d.shape(pot, "#3d3d3d", 0.92, w=0.6, shade=0.6)
    d.ink(ellipse_pts(kx, floor - oh * 0.8, 7, 3.5, 10, a0=math.pi, a1=2 * math.pi), 0.6, "#3a3a3a")
    # fire irons and bellows
    for k, ix in enumerate((x + w / 2 + 4, x + w / 2 + 7)):
        d.ink([(ix, floor), (ix + 0.5, floor - 26 + k * 3)], 1.0, "#4a4a4a")
        d.dot(ix + 0.5, floor - 27 + k * 3, 1.3, "#c9a03a")
    bell = [(x - w / 2 - 12, floor - 22), (x - w / 2 - 6, floor - 30), (x - w / 2 - 1, floor - 22), (x - w / 2 - 6, floor - 14)]
    d.shape(bell, "#9a6a3a", 0.92, w=0.6)
    d.ink([(x - w / 2 - 6, floor - 14), (x - w / 2 - 6, floor - 9)], 0.9, "#4a4a4a")
    # log basket
    O.basket(d, x + w / 2 + 16, floor, 18, 9, "#8a6440")
    # mantel crowd
    my = floor - h - 7
    O.candle(d, x - w * 0.4, my, 10)
    O.candle(d, x + w * 0.42, my, 8)
    d.shape(ellipse_pts(x - 6, my - 9, 7, 7, 20), "#c9a03a", 0.92, w=0.7)
    d.shape(ellipse_pts(x - 6, my - 9, 5, 5, 16), "#fbf6ea", 0.95, w=0.4)
    d.line(x - 6, my - 9, x - 6, my - 12.5, 0.5, INK, 0)
    d.line(x - 6, my - 9, x - 3.5, my - 8, 0.5, INK, 0)
    for k, jx in enumerate((x + 6, x + 12, x + 18)):
        O.jar(d, jx, my, 7 + k, kind=["crock", "bottle", "jar"][k])
    # dried herbs hanging from the beam
    for hx in (x - w * 0.25, x - w * 0.08, x + w * 0.1, x + w * 0.27):
        herb_bunch(d, hx, floor - h)


def herb_bunch(d, x, y, s=1.0):
    d.line(x, y, x, y + 4 * s, 0.4, "#9a7a4a", 0)
    for k in range(9):
        a = math.pi / 2 + (k - 4) * 0.12
        L = d.u(9, 14) * s
        ex, ey = x + L * math.cos(a), y + 4 * s + L * math.sin(a)
        d.ink([(x, y + 4 * s), (ex, ey)], 0.45, "#7a8a4a", op=0.9)
        for t in (0.4, 0.6, 0.8):
            O.leaf(d, x + (ex - x) * t, y + 4 * s + (ey - y - 4 * s) * t, 2.6 * s, a + d.choice([-0.8, 0.8]),
                   d.choice(["#8c9a5a", "#a3a865", "#9b8a5a"]), wdt=0.5, vein=False, ink_w=0)
    d.wash(rect_pts(x - 1.5 * s, y + 3 * s, 3 * s, 2 * s, 3), "#c96a5a", 0.9, smooth_=False)


def preserves_shelf(d, x, y, w, h=14):
    O.shelf(d, x, y, w)
    cx = x + 3
    while cx < x + w - 6:
        jw = d.u(6, 9)
        jh = h * d.u(0.75, 1.1)
        kind = d.choice(["jar", "jar", "jar", "crock", "bottle", "honey"])
        if kind == "honey":
            d.shape([(cx, y), (cx - 1, y - jh * 0.6), (cx + 1, y - jh), (cx + jw - 1, y - jh), (cx + jw + 1, y - jh * 0.6), (cx + jw, y)],
                    "#e2a13a", 0.85, w=0.6)
            d.wash(rect_pts(cx + 1, y - jh * 0.55, jw - 2, jh * 0.3, 4), "#f6e6c0", 0.95, smooth_=False)
            for k in range(3):
                d.line(cx + 2, y - jh * 0.5 + k * 1.6, cx + jw - 2, y - jh * 0.5 + k * 1.6, 0.25, INK_SOFT, 0, op=0.7)
        else:
            O.jar(d, cx + jw / 2, y, jh, kind=kind)
        cx += jw + d.u(1, 2.5)


def hanging_pans(d, x, y, w):
    d.line(x, y, x + w, y, 1.1, "#4a4a4a", 0)
    n = int(w / 13)
    for i in range(n):
        px = x + 6 + i * 13
        d.line(px, y, px, y + 3, 0.5, INK, 0)
        kind = i % 4
        if kind in (0, 2):
            d.ink([(px, y + 3), (px, y + 11)], 1.6, "#a8633a")
            d.shape(ellipse_pts(px, y + 17, 6, 6, 20), "#c27a4a", 0.9, w=0.7, shade=0.7)
            d.ink(ellipse_pts(px - 2, y + 15, 2.5, 2, 8, a0=3.4, a1=4.6), 0.8, "#fff4dc", op=0.9)
        elif kind == 1:
            d.ink([(px, y + 3), (px, y + 17)], 0.8, "#6a6a6a")
            d.shape(ellipse_pts(px, y + 20, 3.6, 2.6, 12), "#9a9a9a", 0.9, w=0.5)
        else:
            d.ink([(px, y + 3), (px, y + 9)], 0.7, "#6a6a6a")
            d.shape([(px - 4, y + 9), (px + 4, y + 9), (px + 3, y + 22), (px - 3, y + 22)], "#d8cfc0", 0.9, w=0.5, smooth_=False)


def plate_dresser(d, x, floor, w, h):
    base_h = h * 0.42
    d.shape(rect_pts(x, floor - base_h, w, base_h, 12), "#a8784a", 0.9, w=0.8, smooth_=False, shade=0.5)
    for k in range(2):
        dx = x + 3 + k * (w - 6) / 2
        d.shape(rect_pts(dx, floor - base_h + 7, (w - 6) / 2 - 2, base_h - 10, 10), "#b98a5a", 0.85, w=0.5, smooth_=False)
        d.dot(dx + (w - 6) / 4 - 1, floor - base_h * 0.5, 1.0, "#c9a03a")
    d.line(x + 3, floor - base_h + 4, x + w - 3, floor - base_h + 4, 0.5, INK, 0)
    d.shape(rect_pts(x + 2, floor - h, w - 4, h - base_h, 12), "#8a5f3a", 0.9, w=0.8, smooth_=False, shade=0.5)
    d.wash(rect_pts(x + 4, floor - h + 3, w - 8, h - base_h - 3, 12), "#6e4a2c", 0.5, smooth_=False)
    rows = 3
    for r in range(rows):
        sy = floor - base_h - r * (h - base_h) / rows
        d.line(x + 2, sy - 1, x + w - 2, sy - 1, 1.0, "#5a3c22", 0)
        n = int((w - 6) / 8.5)
        for i in range(n):
            px = x + 6 + i * ((w - 10) / n)
            if (r + i) % 3 == 2 and r < 2:
                jug(d, px, sy - 1.5, 0.55)
                continue
            rr = (h - base_h) / rows * 0.36
            d.shape(ellipse_pts(px, sy - rr - 1.5, rr, rr, 20), "#f5f2ea", 0.95, w=0.45)
            d.ink(ellipse_pts(px, sy - rr - 1.5, rr * 0.72, rr * 0.72, 18), 0.5, d.choice(["#5d7fb0", "#c96a5a", "#7f9c4d"]), True, op=0.85)
            for k in range(8):
                a = k * math.pi / 4
                d.dot(px + rr * 0.86 * math.cos(a), sy - rr - 1.5 + rr * 0.86 * math.sin(a), 0.35, "#5d7fb0")
    # cups on hooks
    for i in range(int((w - 6) / 7)):
        hx = x + 5 + i * 7
        d.line(hx, floor - base_h - 1, hx, floor - base_h + 1.5, 0.4, INK, 0)
        cup_saucer(d, hx, floor - base_h + 6, 0.38)


def jug(d, x, y, s=1.0):
    j = [(x - 5 * s, y), (x - 6 * s, y - 7 * s), (x - 4 * s, y - 13 * s), (x - 5 * s, y - 15 * s), (x + 4 * s, y - 15 * s),
         (x + 6 * s, y - 16 * s), (x + 4 * s, y - 12 * s), (x + 6 * s, y - 7 * s), (x + 5 * s, y)]
    d.shape(j, "#d9c9a8", 0.92, w=0.5)
    d.line(x - 5 * s, y - 6 * s, x + 5.5 * s, y - 6 * s, 0.7, "#5d7fb0", 0)
    d.ink(ellipse_pts(x - 7 * s, y - 9 * s, 2.5 * s, 3.5 * s, 8, a0=1.6, a1=4.7), 0.7, INK)


def kitchen_range(d, x, floor, w=58, h=44):
    d.shape(rect_pts(x - w / 2, floor - h, w, h, 14), "#4c4643", 0.94, w=0.9, smooth_=False, shade=0.5)
    d.shape(rect_pts(x - w / 2 + 4, floor - h * 0.64, w * 0.42, h * 0.5, 8), "#342f2c", 0.95, w=0.6, smooth_=False)
    d.glow(x - w / 2 + 4 + w * 0.21, floor - h * 0.38, 22, "#f2a63c", 0.8)
    for k in range(5):
        d.line(x - w / 2 + 7 + k * w * 0.08, floor - h * 0.6, x - w / 2 + 7 + k * w * 0.08, floor - h * 0.2, 0.7, "#d9702e", 0)
    d.shape(rect_pts(x + w * 0.04, floor - h * 0.64, w * 0.4, h * 0.5, 8), "#3e3936", 0.95, w=0.6, smooth_=False)
    d.dot(x + w * 0.1, floor - h * 0.4, 1.3, "#c9a03a")
    # brass rail with a tea towel
    d.line(x - w / 2 - 1, floor - h * 0.72, x + w / 2 + 1, floor - h * 0.72, 1.4, "#c9a03a", 0)
    gingham(d, (x + w * 0.12, floor - h * 0.72, 9, 13), "#5d7fb0")
    d.line(x - w / 2 - 3, floor - h, x + w / 2 + 3, floor - h, 1.6, "#2f2a28", 0)
    kx = x - w * 0.22
    d.shape([(kx - 9, floor - h), (kx - 8, floor - h - 9), (kx - 4, floor - h - 12), (kx + 4, floor - h - 12), (kx + 8, floor - h - 9), (kx + 9, floor - h)],
            "#c27a4a", 0.92, w=0.8, shade=0.7)
    d.ink([(kx + 8, floor - h - 6), (kx + 14, floor - h - 10), (kx + 16, floor - h - 14)], 1.4, "#c27a4a")
    d.ink(ellipse_pts(kx, floor - h - 13, 6, 5, 10, a0=math.pi, a1=2 * math.pi), 0.9, INK)
    O.steam(d, kx + 16, floor - h - 16, 18)
    px = x + w * 0.22
    d.shape([(px - 10, floor - h), (px - 10, floor - h - 11), (px + 10, floor - h - 11), (px + 10, floor - h)], "#5a5a5a", 0.92, w=0.8, smooth_=False, shade=0.6)
    d.ink([(px - 13, floor - h - 9), (px - 10, floor - h - 9)], 1.0, INK)
    d.ink([(px + 10, floor - h - 9), (px + 13, floor - h - 9)], 1.0, INK)
    d.shape(rect_pts(x + w * 0.3, floor - h - 46, 7, 46, 12), "#4c4643", 0.92, w=0.7, smooth_=False)


def coat_pegs(d, x, y, w):
    beam_grain(d, x, y, w, 4, "#a8784a")
    n = int(w / 16)
    for i in range(n):
        px = x + 8 + i * 16
        d.line(px, y + 4, px, y + 8, 1.2, "#5a3c22", 0)
        kind = i % 5
        if kind in (0, 3):
            col = d.choice(["#5d7a4a", "#8f5a4a", "#6a6f8f", "#a07a4a"])
            cloak = [(px - 2, y + 7), (px - 8, y + 18), (px - 10, y + 40), (px - 4, y + 42), (px + 4, y + 41), (px + 10, y + 40),
                     (px + 8, y + 18), (px + 2, y + 7)]
            d.shape(cloak, col, 0.88, w=0.7, shade=0.7)
            for k in (-4, 0, 4):
                d.ink([(px + k * 0.5, y + 12), (px + k, y + 39)], 0.35, INK_SOFT, op=0.7)
        elif kind == 1:
            hat = [(px - 9, y + 13), (px - 5, y + 12), (px - 4, y + 4), (px + 4, y + 4), (px + 5, y + 12), (px + 9, y + 13)]
            d.shape(hat, "#7a6a4a", 0.9, w=0.7, shade=0.6)
            d.line(px - 4.5, y + 10, px + 4.5, y + 10, 1.2, "#b8574a", 0)
            O.flower(d, px + 3, y + 9.5, 1.6, "pink")
        elif kind == 2:
            d.shape([(px - 2, y + 7), (px - 3.5, y + 30), (px, y + 32), (px + 3.5, y + 30), (px + 2, y + 7)], "#d99a7a", 0.9, w=0.5)
            for k in range(5):
                d.line(px - 3, y + 11 + k * 4, px + 3, y + 11 + k * 4, 0.6, "#b8574a", 0)
        else:
            basket = [(px - 6, y + 14), (px - 5, y + 24), (px + 5, y + 24), (px + 6, y + 14)]
            d.shape(basket, "#c79a5a", 0.9, w=0.6, smooth_=False)
            d.ink(ellipse_pts(px, y + 14, 6, 8, 12, a0=math.pi, a1=2 * math.pi), 0.8, "#a07a40")
            for k in range(3):
                d.line(px - 5, y + 16 + k * 3, px + 5, y + 16 + k * 3, 0.3, INK_SOFT, 0)
            for k in range(3):
                d.dot(px - 3 + k * 3, y + 13, 1.6, d.choice(["#c4513a", "#9eb04a"]))


def barrel_stack(d, x, floor, cols=5, rows=2, r=13):
    O.beam(d, x - r - 4, floor - 5, cols * 2 * r + 8, 5, "#7d5229")
    for row in range(rows):
        for i in range(cols - row):
            cx = x + i * 2 * r + row * r
            cy = floor - 5 - r - row * (2 * r - 3)
            d.shape(ellipse_pts(cx, cy, r, r, 30), "#7a5332", 0.92, w=0.9, shade=0.6)
            d.shape(ellipse_pts(cx, cy, r * 0.8, r * 0.8, 28), "#b07a43", 0.88, w=0.6, shade=0.5)
            for k in (-0.45, 0, 0.45):
                d.line(cx + k * r * 0.8, cy - r * 0.76, cx + k * r * 0.8, cy + r * 0.76, 0.35, INK_SOFT, 0.1, op=0.8)
            d.ink(ellipse_pts(cx, cy, r * 0.92, r * 0.92, 28), 1.0, "#6a6560", True, op=0.85)
            if row == 0 and i == 1:
                d.shape(rect_pts(cx - 1.5, cy + r * 0.3, 3, 6), "#c9a03a", 1, w=0.5, smooth_=False)
            else:
                d.dot(cx + r * 0.25, cy + r * 0.35, 1.2, INK)
            d.text(cx, cy + 2, d.choice(["Ale", "Cider", "Mead", "Elder", "Perry", "Plum"]), size=4.2, italic=True, color="#4a3426")


def apple_rack(d, x, floor, w=70, rows=3):
    gap = 22
    d.line(x, floor - rows * gap - 4, x, floor, 1.4, "#6e4a2c", 0)
    d.line(x + w, floor - rows * gap - 4, x + w, floor, 1.4, "#6e4a2c", 0)
    for r in range(rows):
        sy = floor - 6 - r * gap
        for k in range(3):
            d.line(x, sy + k * 1.6, x + w, sy + k * 1.6, 0.6, "#8a6440", 0)
        for i in range(int(w / 6.6)):
            col = d.choice(["#c4513a", "#9eb04a", "#d9b44a", "#b8574a", "#a8b85a"])
            ax = x + 4 + i * 6.6 + d.r(0.6)
            d.shape(ellipse_pts(ax, sy - 3, 3.2, 3.0, 12), col, 0.92, w=0.4, shade=0.6)
            d.dot(ax - 0.8, sy - 4.2, 0.6, "#fff4dc", 0.8)


def potato_sack(d, x, floor, w=24, h=26, label="POTATOES", fill="#c9a87a"):
    O.sack(d, x, floor, w, h, color="#e2cfa3")
    for k in range(4):
        d.shape(ellipse_pts(x - 6 + k * 4 + d.r(1), floor - h * 0.98 + d.r(1), 2.6, 2.1, 10), fill, 0.9, w=0.4)
    d.text(x, floor - h * 0.38, label, size=3.6, family="IM Fell English SC", color="#9a3a2a")


def lantern_lit(d, x, y, s=1.0, hang=8):
    O.lantern(d, x, y, s, lit=True, hang=hang)


def snail(d, x, y, s=1.0, flip=False):
    k = -1 if flip else 1
    d.shape(ellipse_pts(x, y, 5 * s, 4.4 * s, 18), "#c38a52", 0.95, w=0.6, shade=0.6)
    sp = [(x + k * (t / 6) * s * math.cos(t * 0.9), y + (t / 6) * s * math.sin(t * 0.9)) for t in range(1, 28)]
    d.ink(sp, 0.5, INK)
    body = [(x - k * 6 * s, y + 4.6 * s), (x + k * 8 * s, y + 4.6 * s), (x + k * 11 * s, y + 0.5 * s), (x + k * 9 * s, y + 2 * s), (x + k * 4 * s, y + 3.6 * s)]
    d.shape(body, "#c7b9a0", 0.95, w=0.5)
    d.ink([(x + k * 9.6 * s, y + 0.8 * s), (x + k * 11 * s, y - 4 * s)], 0.45, INK)
    d.ink([(x + k * 10.6 * s, y + 1.2 * s), (x + k * 13.5 * s, y - 3 * s)], 0.45, INK)
