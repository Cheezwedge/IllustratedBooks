"""Full-page plate: hillside burrow-home cutaway, second study.

What is new compared with scene_burrow.py:
  * every room is a little stage set in one-point perspective (back wall, side walls, vaulted
    ceiling, a floor that recedes), so furniture stands at different depths and overlaps;
  * furniture is built from boxes and cylinders with visible tops and sides;
  * pen hatching is placed deliberately (vaults, shaded walls, shafts) instead of automatically;
  * room names sit on small placards, and there are more small stories: a washing line, a bee
    skep, carrots in the soil, a rabbit warren, a hedgehog asleep under the oak, a cat on the rug.
Same paper, paint engine (wc.py) and page size as the first study. No characters.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc  # noqa: E402
from wc import Canvas, hex2rgb, flatten  # noqa: E402
from kit import ellipse_pts, blob, rect_pts, arch_pts, inside  # noqa: E402
import objects as O  # noqa: E402
import detail as D  # noqa: E402

INKC = "#3a281c"
WOOD, WOODDK, WOODLT, STONE = "#b98a58", "#8a6038", "#d1a674", "#c9bca6"
JAM = ["#a8323a", "#c9772e", "#7a2f52", "#d6a531", "#8f9a3a", "#b8493f", "#5d3a5a"]


def tint(h, k):
    c = hex2rgb(h)
    c = c + (1 - c) * k if k > 0 else c * (1 + k)
    return "#%02x%02x%02x" % tuple(int(max(0.0, min(1.0, float(v))) * 255) for v in c)


class Paper(Canvas):
    def hatch(self, pts, ang=0.8, gap=3.0, w=0.6, op=0.4, color=INKC, fade=None):
        """Pen hatching clipped to a polygon. ang = direction across the lines; fade=(x1,y1,x2,y2) ramps 0 -> 1."""
        poly = flatten(self._px(pts), True, False)
        box = self._bbox(poly, 2)
        if box is None:
            return
        x0, y0, x1, y1 = box
        m = self._raster(poly, box)
        hh, ww = m.shape
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        X, Y = xx + x0, yy + y0
        g = max(2.5, gap * self.k * self._scale())
        ph = (X * math.cos(ang) + Y * math.sin(ang) + 1.8 * self.ks * self.fx[y0:y1, x0:x1]) / g
        dist = np.abs(ph - np.round(ph)) * g
        lw = max(0.9, w * wc.INK_SCALE * self.k * self._scale())
        a = np.clip(lw / 2 + 0.5 - dist, 0, 1) * m * op
        if fade:
            (ax, ay), (bx, by) = self._px([fade[:2], fade[2:]])
            vx, vy = bx - ax, by - ay
            a = a * np.clip(((X - ax) * vx + (Y - ay) * vy) / ((vx * vx + vy * vy) or 1.0), 0, 1)
        a = self._clip(box, a * np.clip(self.mot2[y0:y1, x0:x1] * 1.4, 0.4, 1))
        self.T[y0:y1, x0:x1] *= 1 - a[..., None] * (1 - hex2rgb(color))


def face(d, pts, col, op=0.92, w=0.7, shade=0.3, jit=0.3, cover=None):
    d.wash(pts, col, op, jitter=jit, smooth_=False, shade=shade, hatch=False, cover=cover)
    if w:
        d.ink(pts, w, INKC, True, smooth_=False, jitter=jit * 0.6)


def hi(d, pts):
    """A highlight: lift the paint back to bare paper."""
    d.wash(pts, "#ffffff", 0.85, jitter=0.05, hatch=False)


def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# ============================================================ the stage-set room
class Room:
    """A room seen through its cut-away front in one-point perspective.

    Coordinates are 'front-plane' units: (x, y) as if on the cut plane, plus a depth z from 0 (back wall)
    to 1 (cut plane). Everything shrinks towards the vanishing point (vx, vy) as z goes to 0.
    """

    def __init__(s, d, x, top, w, floor, arch, sb=0.75, eye=0.42):
        s.d, s.x, s.top, s.w, s.floor, s.arch, s.sb = d, x, top, w, floor, arch, sb
        s.vx, s.vy = x + w / 2, top + (floor - top) * eye
        s.F = arch_pts(x, top, w, floor - top, arch, 22)[:-1]     # BL, left spring, arc..., right spring, BR

    def k(s, z):
        return s.sb + (1 - s.sb) * z

    def P(s, x, y, z):
        k = s.k(z)
        return (s.vx + (x - s.vx) * k, s.vy + (y - s.vy) * k)

    def Q(s, pts, z):
        return [s.P(x, y, z) for x, y in pts]

    def push(s, z):
        k = s.k(z)
        s.d.push_transform(s.vx * (1 - k), s.vy * (1 - k), k)

    def pop(s):
        s.d.pop_transform()

    def ceil(s, x):
        t = (x - s.vx) / (s.w / 2)
        return s.top + s.arch * (1 - math.sqrt(max(0.0, 1 - t * t)))

    def shell(s, wall="#f2e2bd", floor="boards", panel=True, stone_back=False):
        d, F, fl = s.d, s.F, s.floor
        B = s.Q(F, 0)
        cx, cy = s.vx, (s.top + fl) / 2
        d.wash([(px + (px - cx) * 0.035, py + (py - cy) * 0.06) for px, py in F], "#7a5838", 0.8, shade=0.2, hatch=False, smooth_=False, jitter=0.6)
        d.wash(F, wall, 0.97, cover=1.0, shade=0.0, jitter=0.3, hatch=False, smooth_=False)
        arcF, arcB = F[1:-1], B[1:-1]
        vault = arcF + arcB[::-1]
        d.wash(vault, tint(wall, -0.17), 0.9, jitter=0.3, smooth_=False, shade=0.0, hatch=False)
        d.hatch(vault, ang=0.55, gap=2.5, op=0.3)
        Lw, Rw = [F[0], F[1], B[1], B[0]], [F[-1], F[-2], B[-2], B[-1]]
        d.wash(Lw, tint(wall, -0.06), 0.9, jitter=0.3, smooth_=False, shade=0.0, hatch=False)
        d.wash(Rw, tint(wall, -0.2), 0.9, jitter=0.3, smooth_=False, shade=0.0, hatch=False)
        d.hatch(Rw, ang=2.45, gap=2.7, op=0.28)
        d.wash(B, wall, 0.95, jitter=0.3, smooth_=False, shade=0.2, cover=1.0, hatch=False)
        if stone_back:
            d.push_clip(B, smooth_=False)
            s.push(0)
            O.stone_wall(d, s.x, s.top, s.w, fl - s.top, course=11, colors=["#d6cab2", "#c8bb9f", "#ded3bd", "#bfb196"],
                         mortar="#eadfc6", ink_op=0.5)
            s.pop()
            d.pop_clip()
        d.wash(ellipse_pts(s.vx, s.vy + 4, s.w * 0.27, (fl - s.top) * 0.25, 18), "#f8dc98", 0.4, soft=True)
        if floor == "boards":
            nb = max(6, int(s.w / 14))
            for i in range(nb):
                xa, xb = s.x + s.w * i / nb, s.x + s.w * (i + 1) / nb
                q = [s.P(xa, fl, 1), s.P(xb, fl, 1), s.P(xb, fl, 0), s.P(xa, fl, 0)]
                face(d, q, d.choice(["#c79a66", "#b98a58", "#d1a674"]), w=0.45, shade=0.15, jit=0.2, cover=1.0)
        else:
            zs = [0, 0.28, 0.54, 0.78, 1]
            for j in range(4):
                nb = max(4, int(s.w / 24))
                off = 0.5 * (j % 2)
                for i in range(-1, nb + 1):
                    xa = s.x + s.w * max(0.0, min(1.0, (i + off) / nb))
                    xb = s.x + s.w * max(0.0, min(1.0, (i + 1 + off) / nb))
                    if xb - xa < 1:
                        continue
                    q = [s.P(xa, fl, zs[j + 1]), s.P(xb, fl, zs[j + 1]), s.P(xb, fl, zs[j]), s.P(xa, fl, zs[j])]
                    face(d, q, d.choice(["#cfc1a8", "#bfb096", "#d8cab0", "#c6b79c"]), w=0.45, shade=0.1, jit=0.2, cover=1.0)
        if panel:
            wy = fl - (fl - s.top) * 0.3
            s.push(0)
            D.planked_wall(d, s.x + 0.5, wy, s.w - 1, fl - wy, max(5, int(s.w / 10)))
            D.beam_grain(d, s.x, wy - 3, s.w, 3.5)
            s.pop()
            for xw, tk in ((s.x, -0.05), (s.x + s.w, -0.24)):
                q = [s.P(xw, fl, 0), s.P(xw, fl, 1), s.P(xw, wy, 1), s.P(xw, wy, 0)]
                d.wash(q, tint("#c8a06e", tk), 0.92, jitter=0.2, smooth_=False, shade=0.0, hatch=False, cover=1.0)
                for z in (0.25, 0.5, 0.75):
                    d.ink([s.P(xw, fl, z), s.P(xw, wy, z)], 0.45, INKC, op=0.6, jitter=0.1, smooth_=False)
                d.ink([s.P(xw, wy, 0), s.P(xw, wy, 1)], 1.3, WOODDK, jitter=0.1, smooth_=False)
        for z in (0.34, 0.67):                                   # vault ribs
            arc = s.Q(arcF, z)
            d.ink(arc, 2.6, "#9a7048", op=0.95, jitter=0.15, smooth_=False)
            d.ink(arc, 0.5, INKC, op=0.6, jitter=0.15, smooth_=False)
        d.ink(B, 0.7, INKC, True, op=0.85, jitter=0.15, smooth_=False)
        for a, b in ((F[0], B[0]), (F[-1], B[-1]), (F[1], B[1]), (F[-2], B[-2])):
            d.ink([a, b], 0.7, INKC, op=0.85, jitter=0.1, smooth_=False)

    def close(s):
        s.d.ink(s.F, 1.7, INKC, True, jitter=0.3, smooth_=False)

    def doorway(s, right, z0=0.32, z1=0.78, h=64):
        """An arched opening in a side wall, seen at a slant."""
        xw, fl = (s.x + s.w if right else s.x), s.floor
        arch = [s.P(xw, fl - h * (0.74 + 0.26 * math.sin(math.pi * t / 10)), z0 + (z1 - z0) * t / 10) for t in range(11)]
        q = [s.P(xw, fl, z0)] + arch + [s.P(xw, fl, z1)]
        face(s.d, q, "#6f553c", w=0, shade=0.0, cover=1.0)
        s.d.hatch(q, ang=1.3, gap=2.2, op=0.35)
        s.d.ink(q, 2.2, WOODDK, True, jitter=0.1, smooth_=False)
        s.d.ink(q, 0.6, INKC, True, jitter=0.1, smooth_=False)


def box(R, x0, x1, y0, y1, z0, z1, col, w=0.7):
    """A box from depth z0 (far) to z1 (near): paints whichever of top, underside and sides can be seen."""
    d = R.d
    if y0 > R.vy:
        face(d, [R.P(x0, y0, z1), R.P(x1, y0, z1), R.P(x1, y0, z0), R.P(x0, y0, z0)], tint(col, 0.22), w=w * 0.8, shade=0.1, cover=1.0)
    if y1 < R.vy:
        face(d, [R.P(x0, y1, z1), R.P(x1, y1, z1), R.P(x1, y1, z0), R.P(x0, y1, z0)], tint(col, -0.32), w=w * 0.8, shade=0.1, cover=1.0)
    if x1 < R.vx:
        face(d, [R.P(x1, y0, z1), R.P(x1, y0, z0), R.P(x1, y1, z0), R.P(x1, y1, z1)], tint(col, -0.2), w=w * 0.8, shade=0.2, cover=1.0)
    if x0 > R.vx:
        face(d, [R.P(x0, y0, z1), R.P(x0, y0, z0), R.P(x0, y1, z0), R.P(x0, y1, z1)], tint(col, -0.1), w=w * 0.8, shade=0.2, cover=1.0)
    face(d, [R.P(x0, y0, z1), R.P(x1, y0, z1), R.P(x1, y1, z1), R.P(x0, y1, z1)], col, w=w, shade=0.35, cover=1.0)


def cyl(R, cx, r, h, z, col, ybase=None, bulge=0.0, hoops=(), topc=None):
    """An upright cylinder (tub, churn, barrel); the lower it sits below eye level, the rounder its top."""
    d = R.d
    R.push(z)
    y = R.floor if ybase is None else ybase
    e = lambda yy: r * max(0.07, min(0.36, (yy - R.vy) / 280.0))   # noqa: E731
    b = r * bulge
    body = ([(cx - r, y - h), (cx - r - b * 0.8, y - h * 0.75), (cx - r - b, y - h * 0.5), (cx - r - b * 0.8, y - h * 0.25)]
            + ellipse_pts(cx, y, r, e(y), 10, a0=math.pi, a1=0)
            + [(cx + r + b * 0.8, y - h * 0.25), (cx + r + b, y - h * 0.5), (cx + r + b * 0.8, y - h * 0.75), (cx + r, y - h)])
    d.wash(body, col, 0.93, jitter=0.2, shade=0.55, cover=1.0, hatch=False)
    d.ink(body, 0.8, INKC, True, jitter=0.15)
    d.hatch([(cx + r * 0.35, y - h), (cx + r + b, y - h), (cx + r + b, y + e(y)), (cx + r * 0.35, y + e(y))], ang=0.2, gap=2.0, op=0.3)
    for t in hoops:
        yy, bb = y - h * t, b * math.sin(math.pi * t)
        d.ink(ellipse_pts(cx, yy, r + bb, e(yy), 10, a0=math.pi, a1=0), 1.7, "#5f5a54", op=0.9, jitter=0.1)
    top = ellipse_pts(cx, y - h, r, e(y - h), 18)
    d.wash(top, topc or tint(col, 0.25), 0.95, jitter=0.15, shade=0.12, cover=1.0, hatch=False)
    d.ink(top, 0.7, INKC, True, jitter=0.1)
    R.pop()
    return y - h


def barrel_lying(R, cx, cy, r, z0, z1, log=False):
    """A barrel (or a log) lying with its end towards us and its body running back into the room."""
    d = R.d
    c1, c0 = R.P(cx, cy, z1), R.P(cx, cy, z0)
    r1, r0 = r * R.k(z1), r * R.k(z0)
    body = hull(ellipse_pts(c1[0], c1[1], r1, r1, 20) + ellipse_pts(c0[0], c0[1], r0, r0, 20))
    d.wash(body, "#7d5a38" if log else "#8a5f3a", 0.93, jitter=0.2, smooth_=False, shade=0.4, cover=1.0, hatch=False)
    d.ink(body, 0.8, INKC, True, jitter=0.15, smooth_=False)
    if not log:
        for t in (0.3, 0.68):
            z = z0 + (z1 - z0) * t
            c = R.P(cx, cy, z)
            d.ink(ellipse_pts(c[0], c[1], r * R.k(z) * 1.03, r * R.k(z) * 1.03, 20), 1.2, "#5f5a54", True, op=0.85, jitter=0.1)
    head = ellipse_pts(c1[0], c1[1], r1, r1, 24)
    d.wash(head, "#d9b98a" if log else "#7a5332", 0.95, jitter=0.15, shade=0.3, cover=1.0, hatch=False)
    d.ink(head, 0.8, INKC, True, jitter=0.12)
    if log:
        for q in (0.65, 0.35):
            d.ink(ellipse_pts(c1[0], c1[1], r1 * q, r1 * q, 12), 0.35, "#8a6038", True, op=0.8, jitter=0.1)
        return
    d.wash(ellipse_pts(c1[0], c1[1], r1 * 0.8, r1 * 0.8, 22), "#bd8a54", 0.92, jitter=0.12, shade=0.45, hatch=False)
    for q in (-0.42, 0.0, 0.42):
        hh = r1 * 0.8 * math.sqrt(1 - q * q)
        d.ink([(c1[0] + q * r1 * 0.8, c1[1] - hh), (c1[0] + q * r1 * 0.8, c1[1] + hh)], 0.4, INKC, op=0.6, jitter=0.1, smooth_=False)
    d.ink(ellipse_pts(c1[0], c1[1], r1 * 0.9, r1 * 0.9, 22), 1.1, "#5f5a54", True, op=0.85, jitter=0.1)
    d.dot(c1[0] + r1 * 0.22, c1[1] + r1 * 0.38, 1.1, INKC)


def table(R, x0, x1, ytop, z0, z1, col=WOODLT, th=3.5):
    d, fl = R.d, R.floor
    d.wash([R.P(x0, fl, z0), R.P(x1, fl, z0), R.P(x1 + 4, fl, z1), R.P(x0 + 4, fl, z1)], "#5d4c66", 0.25, soft=True)
    for z in (z0 + 0.03, z1 - 0.03):
        R.push(z)
        for lx in (x0 + 2, x1 - 5):
            face(d, [(lx, ytop + th), (lx + 3, ytop + th), (lx + 2.5, fl), (lx + 0.5, fl)], tint(col, -0.28), w=0.5, shade=0.2, cover=1.0)
        R.pop()
    box(R, x0, x1, ytop, ytop + th, z0, z1, col)


def wall_shelf(R, x0, x1, y, zf, fill, col=WOODLT):
    """A shelf on the back wall; fill(d, y) draws what stands on it."""
    above = y < R.vy
    if not above:
        box(R, x0, x1, y, y + 3, 0, zf, col)
    R.push(zf * 0.55)
    fill(R.d, y)
    R.pop()
    if above:
        box(R, x0, x1, y, y + 3, 0, zf, col)


def jar_row(d, x0, x1, y, hmax, kinds="jjjhcb", gap=1.3):
    x = x0
    while x < x1 - 4:
        k = d.choice(kinds)
        h = hmax * d.u(0.72, 1.0)
        w = h * (0.34 if k == "b" else d.u(0.6, 0.8))
        if x + w > x1:
            break
        cx = x + w / 2
        if k == "j":                                              # jam jar: cloth cap, string, label
            body = [(x, y), (x, y - h * 0.8), (x + w, y - h * 0.8), (x + w, y)]
            face(d, body, d.choice(JAM), op=0.9, w=0.5, shade=0.5, jit=0.12)
            cap = [(x - 0.8, y - h * 0.74), (x + 0.3, y - h), (x + w - 0.3, y - h), (x + w + 0.8, y - h * 0.74), (cx, y - h * 0.7)]
            d.wash(cap, d.choice(["#f3ead6", "#e9b7b0", "#b9cde0", "#f3ead6"]), 0.95, jitter=0.1, shade=0.1, hatch=False)
            d.ink(cap, 0.45, INKC, True, jitter=0.08)
            d.ink([(x, y - h * 0.78), (x + w, y - h * 0.78)], 0.5, "#b8493f", jitter=0.05, smooth_=False)
            d.wash(rect_pts(x + w * 0.2, y - h * 0.55, w * 0.6, h * 0.26, 4), "#fbf4e2", 1.0, jitter=0.05, smooth_=False, hatch=False)
            hi(d, [(x + 0.6, y - h * 0.7), (x + 1.3, y - h * 0.7), (x + 1.3, y - h * 0.62), (x + 0.6, y - h * 0.62)])
        elif k == "h":                                            # honey pot
            pot = [(x + w * 0.12, y), (x, y - h * 0.45), (x + w * 0.15, y - h * 0.8), (x + w * 0.85, y - h * 0.8), (x + w, y - h * 0.45), (x + w * 0.88, y)]
            d.wash(pot, "#e0a23a", 0.9, jitter=0.12, shade=0.55, hatch=False)
            d.ink(pot, 0.5, INKC, True, jitter=0.1)
            face(d, ellipse_pts(cx, y - h * 0.82, w * 0.4, h * 0.07, 10), "#c98a2e", w=0.4, shade=0.1, jit=0.05)
            d.dot(cx, y - h * 0.9, 0.9, "#8a5a1e")
            d.wash(rect_pts(x + w * 0.22, y - h * 0.5, w * 0.56, h * 0.22, 4), "#fbf4e2", 1.0, jitter=0.05, smooth_=False, hatch=False)
        else:
            O.jar(d, cx, y, h, kind="crock" if k == "c" else "bottle")
        x += w + gap


def placard(d, cx, cy, s, size=8.0):
    w, h = len(s) * size * 0.6 + 12, size + 6
    p = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2 + 4, cy), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2 - 4, cy)]
    d.wash(p, "#f6ecd2", 0.97, cover=1.0, jitter=0.3, smooth_=False, shade=0.1, hatch=False)
    d.ink(p, 0.8, INKC, True, jitter=0.25, smooth_=False)
    d.text(cx, cy + size * 0.33, s, size=size, family="IM Fell English SC", color=INKC)


def floor_oval(R, cx, zc, rx, rz, cols):
    for i, c in enumerate(cols):
        k = 1 - i / len(cols)
        pts = [R.P(cx + rx * k * math.cos(2 * math.pi * j / 24), R.floor, zc + rz * k * math.sin(2 * math.pi * j / 24)) for j in range(24)]
        R.d.wash(pts, c, 0.9, jitter=0.15, shade=0.1, hatch=False, cover=1.0)
        R.d.ink(pts, 0.45, INKC, True, op=0.6, jitter=0.1)


def cat(d, x, y, s=1.0, col="#cf8a40"):
    tail = [(x + 8 * s, y - 3 * s), (x + 7 * s, y + 0.8 * s), (x - 1 * s, y + 1.2 * s), (x - 6 * s, y + 0.2 * s)]
    d.ink(tail, 4.2 * s, col, jitter=0.1)
    body = ellipse_pts(x, y - 4 * s, 9 * s, 4.8 * s, 16)
    d.wash(body, col, 0.94, jitter=0.15, shade=0.5, hatch=False, cover=1.0)
    d.ink(body, 0.6, INKC, True, jitter=0.1)
    for k in range(4):
        d.ink([(x - 3 * s + k * 3 * s, y - 8.3 * s), (x - 2.4 * s + k * 3 * s, y - 5.5 * s)], 1.0, "#9a5a22", op=0.8, jitter=0.1)
    head = ellipse_pts(x - 7.2 * s, y - 3.6 * s, 3.7 * s, 3.2 * s, 12)
    for ex in (-9.6, -5.8):
        ear = [(x + ex * s, y - 5.6 * s), (x + (ex + 0.9) * s, y - 9 * s), (x + (ex + 2.2) * s, y - 5.9 * s)]
        d.wash(ear, col, 0.95, jitter=0.05, smooth_=False, hatch=False)
        d.ink(ear, 0.5, INKC, True, jitter=0.05, smooth_=False)
    d.wash(head, col, 0.95, jitter=0.1, cover=1.0, hatch=False)
    d.ink(head, 0.55, INKC, True, jitter=0.1)
    for ex in (-8.6, -6.0):
        d.ink([(x + ex * s, y - 3.8 * s), (x + (ex + 0.7) * s, y - 3.3 * s), (x + (ex + 1.4) * s, y - 3.8 * s)], 0.4, INKC, jitter=0.03)


def armchair(R, cx, z, fab="#b5564a"):
    d, fl = R.d, R.floor
    zb, zf = z - 0.13, z + 0.13
    d.wash([R.P(cx - 20, fl, zb), R.P(cx + 26, fl, zb), R.P(cx + 26, fl, zf + 0.05), R.P(cx - 20, fl, zf + 0.05)], "#5d4c66", 0.28, soft=True)
    R.push(zb)
    back = [(cx - 15, fl - 14), (cx - 17, fl - 36), (cx - 12, fl - 47), (cx, fl - 50), (cx + 12, fl - 47), (cx + 17, fl - 36), (cx + 15, fl - 14)]
    d.wash(back, fab, 0.93, jitter=0.3, shade=0.6, cover=1.0)
    d.ink(back, 0.9, INKC, True, jitter=0.2)
    for _ in range(34):
        px, py = cx + d.r(15), fl - d.u(17, 47)
        if inside((px, py), back):
            d.dot(px, py, 0.55, "#f1dcae", 0.9)
    lace = [(cx - 7, fl - 48.5), (cx + 7, fl - 48.5), (cx + 6, fl - 39), (cx - 6, fl - 39)]
    hi(d, lace)
    d.ink(lace, 0.4, INKC, True, op=0.6, jitter=0.1)
    R.pop()
    box(R, cx - 15, cx + 15, fl - 17, fl - 5, zb, zf, fab)
    box(R, cx - 21, cx - 15, fl - 27, fl - 5, zb, zf, tint(fab, -0.08))
    box(R, cx + 15, cx + 21, fl - 27, fl - 5, zb, zf, tint(fab, -0.08))
    R.push(zf)
    for lx in (-20, 17.5):
        d.shape(rect_pts(cx + lx, fl - 5, 2.5, 5, 4), "#6e4a2c", 0.95, w=0.4, smooth_=False)
    R.pop()
    R.push(z)
    for i in range(3):
        for j in range(2):
            face(d, rect_pts(cx - 8 + i * 5.3, fl - 28 + j * 5, 5.3, 5, 4), d.choice(["#7f9cb5", "#c99ab0", "#9cb07a", "#d9a65a", "#e8d2a0"]), w=0.35, shade=0.2, jit=0.1, cover=1.0)
    R.pop()


def scaled(R, cx, z, k):
    """Scale whatever is drawn next about the point where (cx, floor, z) meets the floor. Undo with R.pop()."""
    p = R.P(cx, R.floor, z)
    R.d.push_transform(p[0] * (1 - k), p[1] * (1 - k), k)


def round_door(d, cx, cy, r):
    n = 18
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n + 0.03, 2 * math.pi * (k + 1) / n - 0.03
        st = [(cx + r * 1.05 * math.cos(a0), cy + r * 1.05 * math.sin(a0)), (cx + r * 1.25 * math.cos(a0), cy + r * 1.25 * math.sin(a0)),
              (cx + r * 1.25 * math.cos(a1), cy + r * 1.25 * math.sin(a1)), (cx + r * 1.05 * math.cos(a1), cy + r * 1.05 * math.sin(a1))]
        face(d, st, d.choice(["#cdbfa6", "#bcae95", "#d8c9ad", "#c4b59a"]), w=0.6, shade=0.3, jit=0.4, cover=1.0)
    d.wash(ellipse_pts(cx, cy, r * 1.05, r * 1.05, 40), "#4a3a28", 0.92, jitter=0.2, cover=1.0, hatch=False)
    disc = ellipse_pts(cx + r * 0.025, cy + r * 0.03, r * 0.985, r * 0.985, 40)
    d.wash(disc, "#4f8048", 0.94, jitter=0.2, shade=0.5, cover=1.0, hatch=False)
    d.hatch(disc, ang=0.75, gap=2.6, op=0.3, fade=(cx - r * 0.1, cy - r * 0.1, cx + r * 0.8, cy + r * 0.8))
    d.ink(disc, 1.1, INKC, True, jitter=0.2)
    for k in range(-3, 4):
        xx = cx + k * r / 3.6
        hh = math.sqrt(max(0.0, (r * 0.97) ** 2 - (xx - cx) ** 2))
        d.ink([(xx, cy - hh), (xx + 0.4, cy), (xx, cy + hh)], 0.5, INKC, op=0.65, jitter=0.2)
    for hy in (-0.45, 0.45):                                     # iron strap hinges with curled ends
        y = cy + r * hy
        x0 = cx - math.sqrt(r * r - (r * hy) ** 2) * 0.97
        d.ink([(x0, y), (x0 + r * 0.75, y)], 2.6, "#33302d", jitter=0.1, smooth_=False)
        d.ink([(x0 + r * 0.75, y), (x0 + r * 0.86, y - 3), (x0 + r * 0.8, y - 5)], 1.2, "#33302d", jitter=0.05)
        d.ink([(x0 + r * 0.75, y), (x0 + r * 0.86, y + 3), (x0 + r * 0.8, y + 5)], 1.2, "#33302d", jitter=0.05)
        for q in (0.12, 0.4, 0.66):
            d.dot(x0 + r * q, y, 0.7, "#8a8782")
    win = ellipse_pts(cx, cy - r * 0.55, r * 0.15, r * 0.15, 14)   # little glass roundel
    d.wash(win, "#f7e08e", 0.95, jitter=0.05, cover=1.0, hatch=False)
    d.ink(win, 0.9, "#3a2a1c", True, jitter=0.05)
    d.ink([(cx - r * 0.15, cy - r * 0.55), (cx + r * 0.15, cy - r * 0.55)], 0.5, "#3a2a1c", jitter=0.03, smooth_=False)
    d.ink([(cx, cy - r * 0.7), (cx, cy - r * 0.4)], 0.5, "#3a2a1c", jitter=0.03, smooth_=False)
    face(d, ellipse_pts(cx, cy, r * 0.085, r * 0.085, 14), "#d2a53a", w=0.7, shade=0.5, jit=0.05, cover=1.0)   # knob in the middle
    d.dot(cx - r * 0.03, cy - r * 0.03, r * 0.022, "#ffffff")
    d.dot(cx, cy + r * 0.2, 0.9, INKC)


# ======================================================================== the plate
def build(path, dpi=None):
    wc.SOFTEN, wc.INK_SCALE = 0.10, 0.56
    W = 712.5
    d = Paper(7.125, 10.25, seed=52, dpi=dpi)

    # ---------------------------------------------------------------- sky and far country
    d.wash_gradient([(-10, -10), (W + 10, -10), (W + 10, 480), (-10, 480)], [(0, "#9dbdd0"), (0.55, "#d3e2df"), (1, "#f4ecd6")],
                    0, 0, 0, 470, op=0.75, soft=True)
    for cx, cy, cw, ch in ((130, 112, 150, 30), (616, 150, 120, 24), (300, 46, 90, 18)):
        for _ in range(7):
            d.wash(blob(cx + d.r(cw / 2), cy + d.r(ch / 3), d.u(ch, ch * 1.5), d.u(ch * 0.5, ch * 0.85), d.rng, 0.15, 14), "#fffdf6", 0.85, soft=True)
        d.wash(ellipse_pts(cx, cy + ch * 0.45, cw * 0.5, ch * 0.2, 18), "#aebbc6", 0.22, soft=True)
    d.wash([(-20, 440), (-20, 330), (40, 306), (110, 296), (190, 306), (255, 326), (262, 440)], "#9fb2c0", 0.6, soft=True)
    d.wash([(-20, 440), (-20, 356), (50, 338), (130, 332), (210, 342), (262, 362), (262, 440)], "#b9c89c", 0.85, shade=0.2, hatch=False)
    for fx, fy, fw, col in ((14, 352, 46, "#d6cf8c"), (78, 344, 42, "#a8bf7c"), (146, 348, 52, "#c9c680"), (36, 378, 60, "#9db872"), (124, 380, 58, "#d9d498")):
        q = [(fx, fy + 6), (fx + fw * 0.2, fy - 6), (fx + fw, fy - 4), (fx + fw * 0.9, fy + 14), (fx + fw * 0.1, fy + 16)]
        d.wash(q, col, 0.75, jitter=0.5, shade=0.1, hatch=False)
        for i in range(8):
            d.dot(fx + fw * (0.2 + 0.8 * i / 8) + d.r(1), fy - 5.5 + d.r(1.2), d.u(1.2, 2.2), "#5e7e3e", 0.85)
    for bx, by in ((74, 214), (93, 204), (117, 218)):
        d.ink([(bx - 5, by), (bx - 2, by - 3), (bx, by), (bx + 2, by - 3), (bx + 5, by)], 0.7, "#6b5240")

    # ---------------------------------------------------------------- the earth
    surface = [(-15, 440), (60, 405), (140, 368), (220, 332), (300, 300), (380, 276), (460, 260), (540, 254), (620, 262), (690, 280), (730, 292)]

    def sy(x):
        for (x1, y1), (x2, y2) in zip(surface, surface[1:]):
            if x1 <= x <= x2:
                return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        return surface[0][1] if x < surface[0][0] else surface[-1][1]

    earth = surface + [(730, 1040), (-15, 1040)]
    d.wash(earth, "#d2ad7a", 0.92, jitter=0, shade=0.12, cover=1.0, hatch=False)
    d.wash(surface + [(x, y + 30 + d.r(4)) for x, y in surface[::-1]], "#8a6642", 0.5, jitter=0.5, shade=0.0, hatch=False)
    for k, yy in enumerate((400, 520, 640, 760, 860, 960)):
        D.stratum(d, [(x, yy + 14 * math.sin(x / 90 + k * 1.3) + d.r(3)) for x in range(-20, 760, 40)], d.u(30, 55),
                  d.choice(["#c1986a", "#dcc08f", "#b58a5c", "#cfa676"]), 0.32)
    O.mottle(d, earth, ["#b88d5e", "#e2c898", "#a67c52"], n=46, rmin=18, rmax=55, op=0.16)

    hall = Room(d, 250, 438, 146, 600, 34)
    parl = Room(d, 406, 420, 284, 600, 50, sb=0.74)
    kit = Room(d, 300, 656, 206, 815, 30)
    pan = Room(d, 516, 656, 174, 815, 30)
    cel = Room(d, 40, 866, 560, 986, 34, sb=0.8, eye=0.4)
    fire_cx = 630
    flue_x = parl.P(fire_cx, 0, 0.05)[0]
    O.stone_wall(d, flue_x - 12, sy(flue_x) + 2, 24, parl.top - sy(flue_x) + 34, course=10, colors=["#c98f6a", "#b67a58", "#d7a27c"], mortar="#9b7a5c")

    avoid = [rect_pts(244, 424, 452, 190), rect_pts(292, 644, 404, 184), rect_pts(34, 852, 662, 150),
             rect_pts(flue_x - 16, 250, 32, 200), rect_pts(248, 596, 50, 226), rect_pts(300, 350, 80, 46), rect_pts(505, 330, 50, 40)]
    for ang, L, wd in ((1.9, 185, 8), (1.2, 205, 8), (2.3, 150, 5), (0.8, 195, 5), (1.55, 140, 6), (2.6, 115, 3.5), (0.5, 150, 3.5), (1.75, 115, 3)):
        O.root(d, 440 + d.r(12), 272, ang, L, wd, 3, color="#9a7552", avoid=avoid, ymin=sy)
    for x in range(250, 730, 7):
        O.root(d, x + d.r(2), sy(x) + 12, 1.57 + d.r(0.35), d.u(9, 24), 1.0, 1, color="#a7865e", ymin=sy)
    region = [(248, 300), (730, 270), (730, 1040), (-15, 1040), (-15, 664), (248, 664)]
    D.shaded_pebbles(d, region, 190, 1.8, 7)
    O.soil_texture(d, region, 800, "#8f6a46")

    # a hedgehog asleep in a nest of leaves under the oak
    nest = blob(340, 372, 30, 17, d.rng, 0.1, 16)
    d.wash(nest, "#5e4630", 0.85, jitter=0.3, shade=0.2, cover=1.0, hatch=False)
    for _ in range(26):
        a = d.u(0, 2 * math.pi)
        lx, ly = 340 + 24 * math.cos(a), 374 + 12 * math.sin(a)
        d.wash(D.leaf_shape(lx, ly, d.u(6, 9), d.u(0, 6.3), 0.5), d.choice(["#c9a14b", "#b9803a", "#a8743f", "#d6b25e"]), 0.9, jitter=0.1, hatch=False)
    hog = [(322, 380)] + ellipse_pts(340, 380, 17, 13, 14, a0=math.pi, a1=2 * math.pi)[1:] + [(358, 380)]
    d.wash(hog, "#7a5c3e", 0.95, jitter=0.15, shade=0.4, cover=1.0, hatch=False)
    for _ in range(90):
        a = d.u(math.pi * 1.02, math.pi * 1.98)
        rr = d.u(0.35, 1.0)
        px, py = 340 + 16 * rr * math.cos(a), 380 + 12.5 * rr * math.sin(a)
        d.ink([(px, py), (px + 3.2 * math.cos(a - 0.3), py + 3.2 * math.sin(a - 0.3))], 0.45, d.choice(["#3a281c", "#e6d2ac"]), op=0.85, jitter=0.05, smooth_=False)
    snout = [(322, 380), (318, 376), (313, 378.5), (318, 381)]
    d.wash(snout, "#d9b98a", 0.95, jitter=0.05, cover=1.0, hatch=False)
    d.ink(snout, 0.5, INKC, True, jitter=0.05)
    d.dot(312.6, 378.4, 0.9, INKC)
    d.ink([(318, 377.4), (319.5, 378.2), (321, 377.4)], 0.4, INKC, jitter=0.03)
    # a squirrel's forgotten store of acorns
    d.wash(blob(530, 350, 20, 12, d.rng, 0.12, 14), "#5e4630", 0.8, jitter=0.3, cover=1.0, hatch=False)
    for ax, ay, aa in ((520, 349, 0.4), (529, 352, -0.3), (537, 348, 0.9), (526, 344, 1.4), (541, 353, -0.8)):
        O.acorn(d, ax, ay, 0.62, aa)
    # a rabbit warren under the garden
    tun = [(26, 668), (30, 700), (54, 732), (90, 748)]
    d.ink(tun, 16, "#5e4630", op=0.85, jitter=0.2)
    den = blob(120, 754, 40, 23, d.rng, 0.1, 16)
    d.wash(den, "#5e4630", 0.88, jitter=0.3, cover=1.0, hatch=False)
    for _ in range(30):
        px, py = 120 + d.r(34), 770 + d.r(5)
        d.ink([(px, py), (px + d.r(5), py - d.u(1, 4))], 0.5, "#d9c07a", op=0.9, jitter=0.05, smooth_=False)
    for rx, ry, col, flip in ((106, 762, "#b09a82", 1), (134, 764, "#8f7a66", -1)):
        bd = ellipse_pts(rx, ry - 6, 12, 8, 14)
        d.wash(bd, col, 0.95, jitter=0.15, shade=0.5, cover=1.0, hatch=False)
        d.ink(bd, 0.6, INKC, True, jitter=0.1)
        hx = rx - flip * 9
        for e in (0, 2.6):
            ear = [(hx + flip * e, ry - 10), (hx + flip * (e + 3.5), ry - 23), (hx + flip * (e + 5), ry - 10)]
            d.wash(ear, col, 0.95, jitter=0.08, hatch=False)
            d.ink(ear, 0.5, INKC, True, jitter=0.06)
        hd = ellipse_pts(hx, ry - 7, 5.2, 4.6, 12)
        d.wash(hd, col, 0.96, jitter=0.1, cover=1.0, hatch=False)
        d.ink(hd, 0.55, INKC, True, jitter=0.08)
        d.ink([(hx - flip * 2.6, ry - 7.8), (hx - flip * 1.4, ry - 7.2), (hx - flip * 0.2, ry - 7.8)], 0.4, INKC, jitter=0.03)
        d.dot(rx + flip * 11, ry - 4, 2.2, "#f6efe2")
    # old things in the ground
    wp = [(52 + i * 5, 812 + 3.5 * math.sin(i * 1.1)) for i in range(9)]
    d.ink(wp, 2.8, "#d9968e", jitter=0.1)
    d.ink(wp, 0.45, INKC, op=0.6, jitter=0.1)
    face(d, ellipse_pts(196, 834, 6, 6, 14), "#c9a03a", w=0.6, shade=0.4, jit=0.1)
    d.wash(ellipse_pts(196, 834, 2.6, 2.6, 8), "#d2ad7a", 0.95, jitter=0.05, cover=1.0, hatch=False)
    face(d, rect_pts(201, 832.4, 22, 3.2, 8), "#c9a03a", w=0.5, shade=0.2, jit=0.1)
    face(d, rect_pts(216, 835.6, 3, 5, 4), "#c9a03a", w=0.4, shade=0.2, jit=0.1)
    d.ink([(650 + 6 * t / 10 * math.cos(t * 0.9), 1004 + 6 * t / 10 * math.sin(t * 0.9)) for t in range(0, 22)], 0.6, "#6b5240", jitter=0.1)

    # ---------------------------------------------------------------- stairs
    shaft = [(254, 596), (292, 596), (292, 818), (254, 818)]
    d.wash([(250, 592), (296, 592), (296, 822), (250, 822)], "#7a5838", 0.8, hatch=False, smooth_=False, jitter=0.5)
    d.wash(shaft, "#ead6aa", 0.96, cover=1.0, jitter=0.3, smooth_=False, shade=0.25, hatch=False)
    d.hatch(shaft, ang=2.5, gap=2.6, op=0.3, fade=(254, 700, 300, 700))
    for i in range(12):                                          # winding stone stair round a wooden newel
        yy, left = 606 + i * 17.3, i % 2 == 0
        xw, xn = (256, 271) if left else (290, 275)
        face(d, [(xw, yy), (xn, yy + 1.5), (xn, yy + 5), (xw, yy + 8)], "#d9ccb4" if left else "#c4b69c", w=0.5, shade=0.2, jit=0.15, cover=1.0)
    face(d, rect_pts(271, 598, 4, 218, 30), "#a8784a", w=0.6, shade=0.3, jit=0.15, cover=1.0)
    d.ink(shaft, 1.2, INKC, True, jitter=0.3, smooth_=False)
    O.lantern(d, 283, 690, 0.5, True, 0)
    cst = [(612, 812), (690, 812), (690, 990), (606, 990)]
    d.wash([(608, 808), (694, 808), (694, 994), (600, 994)], "#7a5838", 0.8, hatch=False, smooth_=False, jitter=0.5)
    d.wash(cst, "#e8d2a4", 0.96, cover=1.0, jitter=0.3, smooth_=False, shade=0.25, hatch=False)
    d.hatch(cst, ang=0.7, gap=2.6, op=0.3, fade=(606, 820, 660, 960))
    steps = [(690, 826)]
    for i in range(9):
        x0 = 690 - 9 * (i + 1)
        steps += [(x0, 826 + 18 * i), (x0, 826 + 18 * (i + 1))]
    steps += [(606, 988), (690, 988)]
    d.wash(steps, "#c4b69c", 0.95, jitter=0.15, smooth_=False, shade=0.35, cover=1.0, hatch=False)
    d.ink(steps, 0.8, INKC, True, jitter=0.15, smooth_=False)
    d.hatch(steps, ang=0.0, gap=2.4, op=0.22)
    d.ink([(684, 812), (614, 968)], 1.3, "#b8955a", jitter=0.3)     # rope handrail
    d.ink(cst, 1.2, INKC, True, jitter=0.3, smooth_=False)

    # ---------------------------------------------------------------- the hall
    R, fl = hall, hall.floor
    R.shell(floor="flags")
    R.doorway(False)
    R.doorway(True)
    R.push(0)
    D.coat_pegs(d, R.x + 10, fl - 114, R.w - 20)
    bx_ = R.x + 30
    face(d, ellipse_pts(bx_, fl - 132, 7, 7, 16), WOOD, w=0.6, jit=0.1)
    hi(d, ellipse_pts(bx_, fl - 132, 5, 5, 14))
    d.ink([(bx_, fl - 132), (bx_ + 3, fl - 135)], 0.5, INKC, jitter=0.05, smooth_=False)
    face(d, rect_pts(R.x + R.w - 44, fl - 142, 20, 16, 8), "#c9a03a", w=0.6, jit=0.12)
    d.wash(rect_pts(R.x + R.w - 41.5, fl - 139.5, 15, 11, 8), "#e9ddc0", 0.95, jitter=0.08, smooth_=False, cover=1.0, hatch=False)
    R.pop()
    box(R, 270, 352, fl - 26, fl, 0, 0.16, WOOD)                   # settle
    R.push(0.16)
    for k in range(3):
        d.ink(rect_pts(274 + k * 26, fl - 22, 22, 18, 8), 0.5, INKC, True, op=0.7, jitter=0.15, smooth_=False)
    R.pop()
    R.push(0.08)
    face(d, rect_pts(276, fl - 31, 26, 5, 6), "#7f9cb5", w=0.5, shade=0.3, jit=0.2, cover=1.0)
    face(d, rect_pts(306, fl - 33, 16, 7, 6), "#d9a65a", w=0.5, shade=0.3, jit=0.2, cover=1.0)
    O.basket(d, 338, fl - 26, 14, 8, "#c4513a")
    R.pop()
    rug = [R.P(296, fl, 0.24), R.P(350, fl, 0.24), R.P(350, fl, 0.94), R.P(296, fl, 0.94)]
    face(d, rug, "#a8473c", w=0.6, shade=0.1, cover=1.0)
    for z in (0.34, 0.48, 0.62, 0.76, 0.88):
        d.ink([R.P(298, fl, z), R.P(348, fl, z)], 1.3, d.choice(["#e3c070", "#f1e3c2", "#7f9cb5"]), op=0.9, jitter=0.1, smooth_=False)
    top = cyl(R, 374, 6.5, 26, 0.3, "#8f9a7e")
    R.push(0.3)
    for k, c in enumerate(("#6e4a2c", "#3d3d3d", "#8a5f3a")):
        d.ink([(371 + k * 3, top + 1), (370 + k * 3.6, top - 24 - k * 4)], 1.4, c, jitter=0.1)
    d.ink(ellipse_pts(367.4, top - 24, 3, 3, 8, a0=0, a1=-math.pi), 1.4, "#6e4a2c", jitter=0.05)
    R.pop()
    R.push(0.6)
    for bx in (362, 373):                                        # boots by the door
        bt = [(bx, fl), (bx, fl - 14), (bx + 6, fl - 14), (bx + 6.4, fl - 4), (bx + 11, fl - 2.6), (bx + 11, fl)]
        face(d, bt, "#6a4a32", w=0.6, shade=0.5, jit=0.15, cover=1.0)
    R.pop()
    R.push(0.5)
    O.lantern(d, R.vx, R.ceil(R.vx) + 9, 0.8, True, 9)
    R.pop()
    R.close()

    # ---------------------------------------------------------------- the parlour
    R, fl = parl, parl.floor
    R.shell(floor="boards")
    R.doorway(False)
    R.push(0)                                                      # things hung on the back wall
    face(d, rect_pts(496, fl - 134, 34, 24, 10), "#c9a03a", w=0.7, jit=0.15)
    d.wash(rect_pts(499.5, fl - 130.5, 27, 17, 10), "#bcd3dc", 0.95, jitter=0.1, smooth_=False, cover=1.0, hatch=False)
    d.wash([(499.5, fl - 113.5), (508, fl - 122), (515, fl - 118), (526.5, fl - 125), (526.5, fl - 113.5)], "#93b062", 0.9, jitter=0.1, hatch=False)
    face(d, ellipse_pts(552, fl - 122, 10.5, 10.5, 22), "#c9a03a", w=0.7, jit=0.1)
    d.wash(ellipse_pts(552, fl - 122, 7.8, 7.8, 18), "#dbe6e6", 0.95, jitter=0.08, cover=1.0, hatch=False)
    hi(d, ellipse_pts(549, fl - 125, 3.2, 1.6, 8, rot=-0.6))
    d.ink([(494, fl - 80), (584, fl - 80)], 1.6, WOODDK, jitter=0.1, smooth_=False)    # plate rail
    for k, px in enumerate((504, 522, 540, 558, 575)):
        face(d, ellipse_pts(px, fl - 88, 7, 7, 18), "#f5f2ea", w=0.5, shade=0.15, jit=0.08, cover=1.0)
        d.ink(ellipse_pts(px, fl - 88, 4.8, 4.8, 14), 0.6, ("#5d7fb0", "#c96a5a", "#7f9c4d")[k % 3], True, jitter=0.06)
        d.dot(px, fl - 88, 1.1, ("#5d7fb0", "#c96a5a", "#7f9c4d")[k % 3])
    R.pop()
    box(R, 416, 458, fl - 132, fl, 0, 0.1, WOODDK)                 # bookcase
    R.push(0.1)
    d.wash(rect_pts(419, fl - 129, 36, 126, 12), "#4a3322", 0.8, jitter=0.2, smooth_=False, hatch=False)
    for k in range(5):
        yy = fl - 4 - k * 25
        O.books_row(d, 420, yy, 34, 19)
        d.ink([(418, yy + 0.6), (456, yy + 0.6)], 1.3, WOOD, jitter=0.1, smooth_=False)
    R.pop()
    box(R, 468, 484, fl - 124, fl, 0, 0.07, "#9a6a3e")             # long-case clock
    R.push(0.07)
    face(d, ellipse_pts(476, fl - 113, 6, 6, 16), "#fbf4e2", w=0.6, shade=0.1, jit=0.08, cover=1.0)
    d.ink([(476, fl - 113), (476, fl - 117.5)], 0.6, INKC, jitter=0.03, smooth_=False)
    d.ink([(476, fl - 113), (479, fl - 111.5)], 0.6, INKC, jitter=0.03, smooth_=False)
    d.ink(rect_pts(471.5, fl - 100, 9, 60, 10), 0.5, INKC, True, op=0.7, jitter=0.1, smooth_=False)
    d.ink([(476, fl - 98), (477, fl - 62)], 0.6, "#c9a03a", jitter=0.05)
    face(d, ellipse_pts(477, fl - 60, 2.6, 2.6, 10), "#c9a03a", w=0.4, jit=0.05)
    R.pop()
    cx, bw = fire_cx, 76                                           # chimney breast, hearth and mantel
    top = R.ceil(cx) + 3
    box(R, cx - bw / 2, cx + bw / 2, top, fl, 0, 0.1, STONE)
    R.push(0.1)
    O.stone_wall(d, cx - bw / 2 + 1, top + 1, bw - 2, fl - top - 2, course=9.5, colors=["#cdbfa6", "#bcae95", "#d8cab3", "#b3a58c"], mortar="#e8dbc0", ink_op=0.6)
    opn = arch_pts(cx - 23, fl - 56, 46, 56, 18, 14)
    d.wash(opn, "#3f3028", 0.94, jitter=0.2, shade=0.2, cover=1.0, hatch=False)
    d.ink(opn, 0.9, INKC, True, jitter=0.15)
    d.glow(cx, fl - 20, 62, "#f2a63c", 0.8)
    for lx, tl in ((-16, 1.5), (-3, -1.5)):
        face(d, [(cx + lx, fl - 7 + tl), (cx + lx + 22, fl - 7 - tl), (cx + lx + 22, fl - 2.5 - tl), (cx + lx, fl - 2.5 + tl)], "#7a5534", w=0.5, jit=0.15)
    for col, sc, n in (("#d9502e", 1.0, 5), ("#f08a32", 0.78, 6), ("#f8cf5a", 0.5, 5)):
        for _ in range(n):
            fx, fh = cx + d.r(13), d.u(18, 32) * sc
            d.wash([(fx - 5 * sc, fl - 7), (fx - 2.5 * sc, fl - 7 - fh * 0.5), (fx + d.r(2), fl - 7 - fh), (fx + 3 * sc, fl - 7 - fh * 0.45), (fx + 5 * sc, fl - 7)],
                   col, 0.88, jitter=0.2, shade=0.0, gran=0.05, edge=0.25, hatch=False)
    d.ink([(cx - 22, fl - 50), (cx + 6, fl - 50), (cx + 6, fl - 44)], 1.1, "#2f2a28", jitter=0.1, smooth_=False)
    pot = [(cx + 0.5, fl - 44), (cx - 1, fl - 38), (cx + 1, fl - 33), (cx + 11, fl - 33), (cx + 13, fl - 38), (cx + 11.5, fl - 44)]
    face(d, pot, "#3a3634", w=0.6, shade=0.5, jit=0.15, cover=1.0)
    R.pop()
    box(R, cx - bw / 2 - 5, cx + bw / 2 + 5, fl - 66, fl - 60, 0.1, 0.18, WOODDK)
    R.push(0.14)
    O.candle(d, cx - 34, fl - 66, 10)
    O.candle(d, cx + 35, fl - 66, 8)
    face(d, ellipse_pts(cx - 8, fl - 74, 7, 7, 18), "#c9a03a", w=0.6, jit=0.08, cover=1.0)
    hi(d, ellipse_pts(cx - 8, fl - 74, 5, 5, 14))
    d.ink([(cx - 8, fl - 74), (cx - 8, fl - 77.5)], 0.5, INKC, jitter=0.03, smooth_=False)
    d.ink([(cx - 8, fl - 74), (cx - 5.6, fl - 73)], 0.5, INKC, jitter=0.03, smooth_=False)
    for k, jx in enumerate((cx + 6, cx + 14, cx + 22)):
        O.jar(d, jx, fl - 66, 7 + k, kind=("crock", "bottle", "jar")[k])
    R.pop()
    R.push(0.18)
    for hx in (-26, 24):
        D.herb_bunch(d, cx + hx, fl - 60, 0.75)
    R.pop()
    box(R, cx - bw / 2 - 4, cx + bw / 2 + 4, fl - 3, fl, 0.1, 0.4, "#bfb29a")
    R.push(0.3)
    for k, ix in enumerate((cx + 41, cx + 44.5)):                  # fire irons and the log basket
        d.ink([(ix, fl), (ix + 0.5, fl - 28 + k * 3)], 1.0, "#4a4a4a", jitter=0.1)
        d.dot(ix + 0.5, fl - 29 + k * 3, 1.3, "#c9a03a")
    R.pop()
    floor_oval(R, 520, 0.6, 76, 0.3, ["#a8473c", "#d9a65a", "#7f9cb5", "#c99ab0", "#9cb07a", "#e8d2a0"])
    R.push(0.5)
    O.lantern(d, 520, R.ceil(520) + 12, 0.85, True, 12)
    R.pop()
    scaled(R, 548, 0.52, 1.3)
    armchair(R, 548, 0.52)
    R.pop()
    top = cyl(R, 470, 3, 26, 0.64, WOODDK)                         # round tea table on a pedestal
    cyl(R, 470, 22, 8, 0.64, "#f6eedd", ybase=top + 7, topc="#fffaf0")
    R.push(0.64)
    for k in range(-6, 7):
        d.ink([(470 + k * 3.3, top + 2), (470 + k * 3.4, top + 7.5)], 0.7, "#c96a5a", op=0.5, jitter=0.05, smooth_=False)
    yt = top - 1
    D.teapot_fine(d, 462, yt + 1.5, 0.55)
    O.cake(d, 478, yt - 2.5, 0.42)
    D.cup_saucer(d, 471, yt + 4, 0.5)
    D.cup_saucer(d, 484, yt + 2.5, 0.5)
    D.jam_pot(d, 455, yt + 4, 0.42)
    R.pop()
    R.push(0.72)
    cat(d, 500, fl - 1, 1.05)
    R.pop()
    R.push(0.78)
    O.basket(d, 634, fl, 17, 9, "#7f9cb5")                         # knitting
    d.ink([(630, fl - 9), (624, fl - 21)], 0.6, "#c9b28d", jitter=0.05)
    d.ink([(635, fl - 9), (641, fl - 20)], 0.6, "#c9b28d", jitter=0.05)
    R.pop()
    cyl(R, 592, 8, 7, 0.74, "#d9a65a")                             # footstool
    R.close()

    # ---------------------------------------------------------------- the kitchen
    R, fl = kit, kit.floor
    R.shell(floor="flags", panel=False)
    R.doorway(True)
    R.push(0)
    for i in range(6):                                             # blue-and-white tiles behind the range
        for j in range(4):
            face(d, rect_pts(432 + i * 10, fl - 82 + j * 9, 10, 9, 5), "#f3f1ea", w=0.35, shade=0.05, jit=0.08, cover=1.0)
            d.dot(437 + i * 10, fl - 77.5 + j * 9, 1.3, "#5d7fb0")
    D.hanging_pans(d, 378, fl - 112, 50)
    R.pop()
    box(R, 312, 372, fl - 42, fl, 0, 0.16, "#b08455")              # dresser: cupboard below, plate rack above
    R.push(0.16)
    for k in range(2):
        d.ink(rect_pts(315 + k * 28, fl - 38, 26, 34, 8), 0.5, INKC, True, op=0.75, jitter=0.15, smooth_=False)
        d.dot(338 + k * 6, fl - 22, 1.1, "#c9a03a")
    R.pop()
    box(R, 314, 370, fl - 128, fl - 42, 0, 0.07, WOODDK)
    R.push(0.07)
    d.wash(rect_pts(317, fl - 125, 50, 81, 10), "#4a3322", 0.75, jitter=0.2, smooth_=False, hatch=False)
    for row in range(3):
        yy = fl - 44 - row * 27
        for i in range(5):
            px = 322 + i * 10.2
            if (row + i) % 4 == 3:
                D.jug(d, px, yy - 1, 0.55)
                continue
            face(d, ellipse_pts(px, yy - 8, 6.2, 6.2, 18), "#f5f2ea", w=0.45, shade=0.15, jit=0.06, cover=1.0)
            d.ink(ellipse_pts(px, yy - 8, 4.2, 4.2, 14), 0.55, ("#5d7fb0", "#c96a5a", "#7f9c4d")[(row + i) % 3], True, jitter=0.05)
        d.ink([(316, yy), (368, yy)], 1.3, WOOD, jitter=0.1, smooth_=False)
    R.pop()
    R.push(0.1)
    O.jar(d, 324, fl - 42, 11, kind="crock")
    face(d, [(338, fl - 42), (336, fl - 49), (354, fl - 49), (352, fl - 42)], "#e8dcc0", w=0.5, shade=0.4, jit=0.1, cover=1.0)
    d.ink([(346, fl - 49), (357, fl - 58)], 1.0, "#a07a4a", jitter=0.1)
    R.pop()
    wall_shelf(R, 432, 480, fl - 93, 0.08, lambda dd, y: jar_row(dd, 434, 478, y, 10, "cch"))
    box(R, 384, 424, fl - 30, fl, 0, 0.15, STONE)                  # stone sink with a hand pump
    face(d, [R.P(388, fl - 30, 0.13), R.P(420, fl - 30, 0.13), R.P(420, fl - 30, 0.03), R.P(388, fl - 30, 0.03)], "#7f8d94", w=0.5, shade=0.1, cover=1.0)
    R.push(0.04)
    face(d, rect_pts(388.5, fl - 68, 6, 38, 8), "#55665e", w=0.6, shade=0.5, jit=0.1, cover=1.0)      # pump body
    face(d, [(394.5, fl - 60), (402, fl - 60), (404, fl - 53), (400.5, fl - 53), (399.5, fl - 56.5), (394.5, fl - 56.5)], "#55665e", w=0.5, shade=0.3, jit=0.08, cover=1.0)
    face(d, ellipse_pts(391.5, fl - 70, 4, 2.6, 10), "#3f4d46", w=0.5, jit=0.05, cover=1.0)
    d.ink([(391.5, fl - 70), (378, fl - 86)], 2.6, "#3f4d46", jitter=0.08, smooth_=False)
    d.dot(377.6, fl - 86.4, 1.9, "#c9a03a")
    d.ink([(402.2, fl - 52), (402.2, fl - 42)], 0.6, "#8fb9cc", jitter=0.1, dash="1.2 1")
    R.pop()
    R.push(0.1)
    face(d, [(396, fl - 30), (395, fl - 40), (408, fl - 40), (407, fl - 30)], "#a8784a", w=0.5, shade=0.5, jit=0.1, cover=1.0)   # bucket
    d.ink(ellipse_pts(401.5, fl - 40, 6.5, 7, 8, a0=math.pi, a1=2 * math.pi), 0.6, "#4a4a4a", jitter=0.05)
    R.pop()
    box(R, 432, 492, fl - 46, fl, 0, 0.2, "#4a4441")               # cast-iron range
    R.push(0.2)
    face(d, rect_pts(436, fl - 34, 24, 26, 8), "#2f2a27", w=0.6, shade=0.1, jit=0.1, cover=1.0)
    d.glow(448, fl - 20, 20, "#f2a63c", 0.85)
    for k in range(5):
        d.ink([(439 + k * 4.5, fl - 31), (439 + k * 4.5, fl - 11)], 0.8, "#d9702e", jitter=0.05, smooth_=False)
    face(d, rect_pts(464, fl - 34, 24, 26, 8), "#3a3532", w=0.6, shade=0.2, jit=0.1, cover=1.0)
    d.dot(468, fl - 21, 1.3, "#c9a03a")
    d.ink([(431, fl - 39), (493, fl - 39)], 1.5, "#c9a03a", jitter=0.08, smooth_=False)
    D.gingham(d, (476, fl - 39, 8, 12), "#5d7fb0")
    R.pop()
    R.push(0.1)
    ky = fl - 46
    kb = [(440, ky), (441, ky - 9), (445, ky - 12), (453, ky - 12), (457, ky - 9), (458, ky)]
    face(d, kb, "#c27a4a", w=0.7, shade=0.6, jit=0.12, cover=1.0)
    d.ink([(457, ky - 6), (463, ky - 10), (465, ky - 14)], 1.5, "#c27a4a", jitter=0.05)
    d.ink(ellipse_pts(449, ky - 13, 6, 5, 10, a0=math.pi, a1=2 * math.pi), 0.9, INKC, jitter=0.05)
    hi(d, ellipse_pts(445, ky - 8, 2.2, 1.2, 8, rot=-0.5))
    O.steam(d, 465, ky - 16, 18)
    face(d, [(470, ky), (470, ky - 11), (488, ky - 11), (488, ky)], "#5a5a5a", w=0.7, shade=0.5, jit=0.12, cover=1.0)
    d.ink([(468, ky - 12), (490, ky - 12)], 1.4, "#3a3a3a", jitter=0.05, smooth_=False)
    d.dot(479, ky - 13.5, 1.2, "#3a3a3a")
    O.steam(d, 479, ky - 15, 14, 0.4)
    R.pop()
    R.push(0.04)
    face(d, rect_pts(483, R.ceil(485) + 2, 5, fl - 46 - R.ceil(485) - 2, 12), "#5a5450", w=0.5, shade=0.3, jit=0.12, cover=1.0)
    R.pop()
    R.push(0.34)
    for hx in (332, 352, 462):
        D.herb_bunch(d, hx, R.ceil(hx) + 1, 0.95)
    R.pop()
    R.push(0.67)
    O.onion_string(d, 340, R.ceil(340) + 1, 5, 0.9)
    D.herb_bunch(d, 440, R.ceil(440) + 1, 0.9)
    R.pop()
    table(R, 318, 392, fl - 36, 0.5, 0.84)
    R.push(0.64)
    ty = fl - 36
    face(d, [(324, ty), (324, ty - 1.6), (348, ty - 1.6), (348, ty)], "#b98a58", w=0.4, jit=0.08, cover=1.0)       # bread board
    loaf = blob(336, ty - 5.5, 9, 4.6, d.rng, 0.08, 12)
    d.wash(loaf, "#d39a55", 0.94, jitter=0.1, shade=0.6, cover=1.0, hatch=False)
    d.ink(loaf, 0.55, INKC, True, jitter=0.08)
    for k in range(3):
        d.ink([(331 + k * 4, ty - 6), (333 + k * 4, ty - 9)], 0.4, "#8a5a2a", jitter=0.05)
    bowl = [(356, ty - 8), (358, ty - 1.5), (361, ty), (371, ty), (374, ty - 1.5), (376, ty - 8)]
    face(d, bowl, "#e8dcc0", w=0.55, shade=0.45, jit=0.1, cover=1.0)
    d.ink([(357, ty - 5), (375, ty - 5)], 0.7, "#5d7fb0", jitter=0.05, smooth_=False)
    d.ink([(368, ty - 8), (379, ty - 17)], 1.1, "#a07a4a", jitter=0.08)
    D.jug(d, 384, ty, 0.6)
    for k in range(4):
        D.wildflower(d, 382 + k * 1.4, ty - 9, d.choice(["daisy", "forgetmenot", "campion", "buttercup"]), 0.6)
    R.pop()
    R.push(0.74)
    for k in range(5):                                             # eggs in a dish, and a rolling pin
        face(d, ellipse_pts(328 + k * 3.3, ty - 2.6 - (k % 2) * 1.6, 1.9, 2.4, 10), "#f1e6cf", w=0.35, shade=0.3, jit=0.05, cover=1.0)
    face(d, [(324, ty), (325.5, ty - 3), (344, ty - 3), (345.5, ty)], "#c9b58f", w=0.5, shade=0.3, jit=0.08, cover=1.0)
    face(d, rect_pts(358, ty - 3.4, 24, 3.4, 8), "#d9b98a", w=0.45, shade=0.4, jit=0.08, cover=1.0)
    d.ink([(354, ty - 1.7), (358, ty - 1.7)], 1.2, WOODDK, jitter=0.03, smooth_=False)
    d.ink([(382, ty - 1.7), (386, ty - 1.7)], 1.2, WOODDK, jitter=0.03, smooth_=False)
    R.pop()
    cyl(R, 470, 7.5, 16, 0.8, WOOD)                                # three-legged stool
    R.push(0.88)
    O.basket(d, 416, fl, 20, 10, "#9eb04a")
    d.ink([(308, fl), (305, fl - 62)], 1.2, "#a07a4a", jitter=0.15)         # besom broom
    for k in range(8):
        d.ink([(307.6, fl - 16), (302 + k * 1.6, fl)], 0.5, "#c9a86a", jitter=0.05, smooth_=False)
    R.pop()
    R.push(0.5)
    O.lantern(d, 400, R.ceil(400) + 8, 0.75, True, 8)
    R.pop()
    R.close()

    # ---------------------------------------------------------------- the pantry
    R, fl = pan, pan.floor
    R.shell(floor="flags", panel=False)
    R.doorway(False)
    wall_shelf(R, R.x + 6, R.x + R.w - 6, fl - 114, 0.16, lambda dd, y: jar_row(dd, R.x + 10, R.x + R.w - 10, y, 13, "jjjjh"))
    wall_shelf(R, R.x + 6, R.x + R.w - 6, fl - 82, 0.16, lambda dd, y: jar_row(dd, R.x + 10, R.x + R.w - 10, y, 14, "hhjcbcb"))

    def larder(dd, y):
        for cx in (R.x + 22, R.x + 46, R.x + 70):
            O.cheese(dd, cx, y, 9.5)
        O.cake(dd, R.x + 98, y - 0.5, 0.6)
        face(dd, [(R.x + 116, y), (R.x + 114.5, y - 6), (R.x + 138, y - 6), (R.x + 136.5, y)], "#c9b58f", w=0.5, shade=0.4, jit=0.1, cover=1.0)
        for k in range(6):
            face(dd, ellipse_pts(R.x + 118.5 + k * 3.2, y - 7.4 - (k % 2) * 1.8, 2.0, 2.6, 10), "#f1e6cf", w=0.35, shade=0.3, jit=0.05, cover=1.0)
        O.jar(dd, R.x + 152, y, 13, kind="crock")
    wall_shelf(R, R.x + 6, R.x + R.w - 6, fl - 48, 0.18, larder)
    box(R, R.x + 10, R.x + 52, fl - 24, fl, 0, 0.2, "#b08455")      # flour bin
    R.push(0.2)
    d.text(R.x + 31, fl - 9, "FLOUR", size=5.5, family="IM Fell English SC", color="#7a2f2a")
    R.pop()
    for hx, z, sc in ((R.x + 40, 0.3, 0.95), (R.x + 78, 0.52, 1.0), (R.x + 116, 0.34, 0.85), (R.x + 140, 0.6, 1.0)):
        R.push(z)
        O.ham(d, hx, R.ceil(hx) + 1, sc)
        R.pop()
    R.push(0.45)
    O.onion_string(d, R.x + 100, R.ceil(R.x + 100) + 1, 5, 0.85)
    D.herb_bunch(d, R.x + 60, R.ceil(R.x + 60) + 1, 0.9)
    R.pop()
    top = cyl(R, R.x + 132, 14, 34, 0.5, "#b07a43", bulge=0.14, hoops=(0.14, 0.3, 0.7, 0.86))     # apple barrel
    R.push(0.5)
    for k in range(9):
        face(d, ellipse_pts(R.x + 122 + (k % 5) * 5 + d.r(0.8), top - 2 - (k // 5) * 3.6, 3.2, 3.0, 12), d.choice(["#c4513a", "#9eb04a", "#d9b44a"]), w=0.4, shade=0.5, jit=0.06, cover=1.0)
    R.pop()
    R.push(0.62)
    D.potato_sack(d, R.x + 74, fl, 25, 28, "OATS", "#d8c394")
    R.pop()
    R.push(0.8)
    D.potato_sack(d, R.x + 44, fl, 27, 31, "FLOUR", "#f3ead6")
    R.pop()
    cyl(R, R.x + 100, 8, 24, 0.86, "#b9c0c2", hoops=(0.25, 0.75))   # milk churn
    trap = [R.P(R.x + 124, fl, 0.62), R.P(R.x + 166, fl, 0.62), R.P(R.x + 166, fl, 0.97), R.P(R.x + 124, fl, 0.97)]
    face(d, trap, "#5a4632", w=0.8, shade=0.0, cover=1.0)            # trapdoor down to the cellar
    d.hatch(trap, ang=0.4, gap=2.2, op=0.4)
    box(R, R.x + 166, R.x + 169, fl - 30, fl, 0.62, 0.97, WOOD)
    R.push(0.8)
    d.ink([(R.x + 130, fl + 2), (R.x + 130, fl - 16)], 1.6, WOODDK, jitter=0.1, smooth_=False)
    d.ink([(R.x + 142, fl + 2), (R.x + 142, fl - 16)], 1.6, WOODDK, jitter=0.1, smooth_=False)
    for k in range(3):
        d.ink([(R.x + 130, fl - 3 - k * 5.5), (R.x + 142, fl - 3 - k * 5.5)], 1.2, WOODDK, jitter=0.05, smooth_=False)
    R.pop()
    R.push(0.5)
    O.lantern(d, R.vx - 26, R.ceil(R.vx - 26) + 8, 0.7, True, 8)
    R.pop()
    R.close()

    # ---------------------------------------------------------------- the cellar
    R, fl = cel, cel.floor
    R.shell(wall="#e9d6ac", floor="flags", panel=False, stone_back=True)
    R.doorway(True, z0=0.3, z1=0.8, h=70)
    box(R, 110, 274, fl - 3, fl, 0.03, 0.3, WOODDK)
    for cx in (128, 160, 192, 224, 256):
        barrel_lying(R, cx, fl - 19, 15, 0.03, 0.3)
    for cx in (144, 176, 208, 240):
        barrel_lying(R, cx, fl - 46.5, 15, 0.03, 0.3)
    R.push(0.3)
    D.snail(d, 208, fl - 66, 0.7)
    for cx, nm in ((128, "Ale"), (160, "Cider"), (192, "Mead"), (224, "Perry"), (256, "Plum")):
        d.text(cx, fl - 22, nm, size=4.6, italic=True, color="#3a281c")
    R.pop()
    box(R, 290, 350, fl - 74, fl, 0, 0.12, "#4a3524")
    R.push(0.12)
    O.wine_rack(d, 290, fl, 60, 74, 5.2)
    R.pop()
    R.push(0.1)
    D.apple_rack(d, 364, fl, 66, 3)
    R.pop()
    R.push(0.5)                                                    # cider press
    px = 62
    for x0 in (px, px + 34):
        face(d, rect_pts(x0, fl - 62, 5, 62, 12), WOODDK, w=0.6, shade=0.3, jit=0.12, cover=1.0)
    face(d, rect_pts(px - 4, fl - 66, 47, 7, 12), WOOD, w=0.6, shade=0.3, jit=0.12, cover=1.0)
    face(d, rect_pts(px + 17, fl - 59, 5, 26, 8), "#c9a86a", w=0.5, shade=0.3, jit=0.08, cover=1.0)
    for k in range(7):
        d.ink([(px + 17, fl - 57 + k * 3.4), (px + 22, fl - 55.4 + k * 3.4)], 0.5, INKC, op=0.8, jitter=0.03, smooth_=False)
    d.ink([(px + 6, fl - 52), (px + 33, fl - 54)], 1.6, WOODDK, jitter=0.08, smooth_=False)
    face(d, rect_pts(px + 7, fl - 33, 25, 3.5, 8), WOOD, w=0.5, jit=0.08, cover=1.0)
    tub = [(px + 8, fl - 8), (px + 7, fl - 29), (px + 32, fl - 29), (px + 31, fl - 8)]
    face(d, tub, "#b07a43", w=0.6, shade=0.5, jit=0.1, cover=1.0)
    for k in range(1, 6):
        d.ink([(px + 7 + k * 4.2, fl - 29), (px + 7.6 + k * 4.1, fl - 8)], 0.4, INKC, op=0.6, jitter=0.03, smooth_=False)
    for yy in (fl - 25, fl - 12):
        d.ink([(px + 7, yy), (px + 32, yy)], 1.3, "#5f5a54", jitter=0.05, smooth_=False)
    face(d, rect_pts(px + 4, fl - 8, 32, 3.5, 8), WOODDK, w=0.5, jit=0.08, cover=1.0)
    d.ink([(px + 36, fl - 6), (px + 42, fl - 4)], 1.2, WOODDK, jitter=0.05, smooth_=False)
    face(d, [(px + 40, fl), (px + 39, fl - 9), (px + 50, fl - 9), (px + 49, fl)], "#a8784a", w=0.5, shade=0.5, jit=0.1, cover=1.0)
    R.pop()
    top = cyl(R, 462, 13, 36, 0.4, "#b07a43", bulge=0.14, hoops=(0.14, 0.3, 0.7, 0.86))
    cyl(R, 494, 13, 36, 0.46, "#a8743f", bulge=0.14, hoops=(0.14, 0.3, 0.7, 0.86))
    R.push(0.4)
    O.candle(d, 462, top, 10)
    R.pop()
    cyl(R, 516, 14, 38, 0.84, "#b98a58", bulge=0.14, hoops=(0.14, 0.3, 0.7, 0.86))
    for row, n in enumerate((4, 3, 2)):                            # firewood
        for i in range(n):
            barrel_lying(R, 548 + i * 9.6 + row * 4.8, fl - 5 - row * 8.2, 4.8, 0.2, 0.42, log=True)
    R.push(0.72)
    D.potato_sack(d, 426, fl, 27, 29, "POTATOES")
    O.basket(d, 392, fl, 22, 11, "#c9a25a")
    R.pop()
    R.push(0)                                                      # cobweb in the far corner
    wx, wy = R.x + 6, R.top + 40
    for k in range(7):
        a = math.pi * k / 12
        d.ink([(wx, wy), (wx + 40 * math.cos(a), wy + 40 * math.sin(a))], 0.35, "#6b5240", op=0.7, jitter=0.1, smooth_=False)
    for rr in (12, 23, 34):
        d.ink([(wx + rr * math.cos(math.pi * k / 12), wy + rr * math.sin(math.pi * k / 12) + 1.5) for k in range(7)], 0.35, "#6b5240", op=0.7, jitter=0.1)
    R.pop()
    R.push(0.5)
    O.lantern(d, 330, R.ceil(330) + 8, 0.8, True, 8)
    R.pop()
    R.close()

    placard(d, hall.vx + 12, hall.floor + 4, "The Hall")
    placard(d, parl.vx, parl.floor + 4, "The Parlour")
    placard(d, kit.vx, kit.floor + 4, "The Kitchen")
    placard(d, pan.vx - 22, pan.floor + 4, "The Pantry")
    placard(d, 300, cel.top + 1, "The Cellar")

    # ---------------------------------------------------------------- the hill face and the garden
    cut = [(248, 322), (242, 380), (251, 432), (244, 486), (254, 534), (247, 584), (256, 632), (264, 660)]
    facep = [p for p in surface if p[0] <= 248] + cut + [(-15, 660)]
    d.wash(facep, "#9cb56a", 0.92, jitter=0, shade=0.25, cover=1.0, hatch=False)
    O.mottle(d, facep, ["#7d9d50", "#b7c77a", "#8ea05c"], n=26, rmin=12, rmax=40, op=0.3)
    for _ in range(520):
        x, y = d.u(-10, 246), d.u(330, 652)
        if inside((x, y), facep):
            L = d.u(3, 7)
            d.ink([(x, y), (x + d.r(1.2), y - L)], 0.55, d.choice(["#6b8c45", "#86a557", "#a6b86a"]), op=0.75, jitter=0.1, smooth_=False)
    d.hatch([(200, 340), (248, 322)] + cut[1:] + [(214, 660)], ang=0.15, gap=2.8, op=0.22, color="#4d6a36", fade=(205, 500, 252, 500))
    d.ink(cut, 2.2, "#7a5838", op=0.9, jitter=0.4)
    d.ink(cut, 0.8, INKC, jitter=0.4)
    dcx, dcy, dr = 122, 556, 50
    round_door(d, dcx, dcy, dr)
    for side in (-1, 1):                                           # a climbing rose over the door
        stem = [(dcx + side * dr * 1.36 * math.cos(a), dcy - dr * 1.36 * math.sin(a)) for a in [-0.5 + 2.1 * i / 12 for i in range(13)]]
        d.ink(stem, 1.2, "#6e5238", jitter=0.8)
        for i, (sx, sy_) in enumerate(stem):
            for _ in range(3):
                d.wash(D.leaf_shape(sx + d.r(3), sy_ + d.r(3), d.u(5, 7.5), d.u(0, 6.3), 0.5), d.choice(D.LEAF_MID + D.LEAF_DARK), 0.88, jitter=0.1, hatch=False)
            if i % 2 == 0:
                rx, ry = sx + d.r(3), sy_ + d.r(3)
                for j in range(5):
                    d.wash(ellipse_pts(rx + 1.6 * math.cos(j * 1.257), ry + 1.6 * math.sin(j * 1.257), 1.8, 1.6, 8), "#e9a0ac", 0.92, jitter=0.05, hatch=False)
                d.dot(rx, ry, 0.7, "#c9607e")
    O.round_window(d, 44, 474, 21)
    for (x0, x1, y0, y1, y2) in ((dcx - 38, dcx + 38, 610, 616, 626), (dcx - 50, dcx + 50, 626, 633, 644)):       # two stone steps
        face(d, [(x0 + 5, y0), (x1 - 5, y0), (x1, y1), (x0, y1)], "#d8cdb6", w=0.6, shade=0.1, cover=1.0)
        face(d, [(x0, y1), (x1, y1), (x1, y2), (x0, y2)], "#b9ac94", w=0.7, shade=0.3, cover=1.0)
        d.hatch([(x0, y1), (x1, y1), (x1, y2), (x0, y2)], ang=1.57, gap=2.2, op=0.25)
    for bx in (dcx + 14, dcx + 26):                                # muddy boots left on the step
        bt = [(bx, 626), (bx, 611), (bx + 6, 611), (bx + 6.4, 621.5), (bx + 11.5, 623.5), (bx + 11.5, 626)]
        face(d, bt, "#6a4a32", w=0.6, shade=0.5, jit=0.15, cover=1.0)
    d.ink([(dcx - 44, 626), (dcx - 50, 566)], 1.5, "#8a5f3a", jitter=0.2)      # walking stick against the wall
    d.ink(ellipse_pts(dcx - 46.6, 566, 3.4, 3.4, 8, a0=math.pi, a1=2 * math.pi), 1.5, "#8a5f3a", jitter=0.05)
    O.lantern(d, 196, 496, 0.8, True, 6)
    d.ink([(190, 490), (204, 490)], 1.1, INKC, jitter=0.1, smooth_=False)
    face(d, [(186, 612), (232, 612), (236, 617.5), (182, 617.5)], WOODLT, w=0.6, shade=0.1, cover=1.0)             # bench
    face(d, [(182, 617.5), (236, 617.5), (236, 621), (182, 621)], WOOD, w=0.6, shade=0.3, cover=1.0)
    for lx in (187, 229):
        d.ink([(lx, 621), (lx, 642)], 1.5, WOODDK, jitter=0.1, smooth_=False)
    O.basket(d, 218, 612, 13, 7, "#c4513a")
    face(d, [(190, 612), (189, 602), (200, 602), (199, 612)], "#b9c0c2", w=0.5, shade=0.5, jit=0.1, cover=1.0)     # watering can
    d.ink([(200, 606), (207, 601)], 1.2, "#8f979a", jitter=0.05)
    d.ink(ellipse_pts(194.5, 601, 4.5, 4.5, 8, a0=math.pi, a1=2 * math.pi), 0.8, "#8f979a", jitter=0.05)
    O.barrel_side(d, 14, 644, 24, 34)                              # rain butt
    for px_, col in ((62, "#c4774a"), (76, "#b8684a")):
        face(d, [(px_ - 6, 644), (px_ - 7, 632), (px_ + 7, 632), (px_ + 6, 644)], col, w=0.6, shade=0.5, jit=0.12, cover=1.0)
        for k in range(5):
            D.wildflower(d, px_ - 5.5 + k * 2.8, 632, d.choice(["campion", "daisy", "buttercup", "poppy"]), 0.7)
    for fx, fh in ((240, 52), (30, 40), (166, 36)):
        D.foxglove(d, fx, 646, fh)
    D.meadow(d, [p for p in surface if p[0] <= 248], density=0.7, flowers=0.25, h=(4, 10))
    D.snail(d, 172, 414, 0.8)
    garden = [(-15, 646), (60, 644), (140, 645), (200, 647), (264, 654)]
    d.wash(garden + [(264, 672), (-15, 672)], "#86a557", 0.9, shade=0.2, cover=1.0, hatch=False)
    for sx in (92, 122, 152):
        face(d, blob(sx, 652, 11, 3.4, d.rng, 0.1, 12), "#c9bfa9", w=0.6, shade=0.3, jit=0.1, cover=1.0)
    D.meadow(d, garden, density=0.9, flowers=0.35, h=(6, 14))
    O.fence(d, 34, 650, 72, 648, 22, 3)
    for fx in range(8, 250, 12):
        O.root(d, fx, 672, 1.57 + d.r(0.4), d.u(16, 40), 1.2, 1, color="#a7865e")

    # ---------------------------------------------------------------- on top of the hill
    top_cut = [(248, 322)] + [p for p in surface if p[0] >= 248]
    O.grass_band(d, [p for p in top_cut if p[0] < 498] + [(498, sy(498))], 14, "#93b062")
    O.grass_band(d, [(592, sy(592))] + [p for p in top_cut if p[0] > 592], 14, "#93b062")
    d.ink([(498, sy(498) + 1), (545, sy(545) + 0.5), (592, sy(592) + 1)], 1.6, "#6e5238", jitter=0.5)       # bare soil of the bed
    # vegetables growing down into the soil
    for cx in range(526, 590, 9):
        y0, L = sy(cx) + 4, d.u(15, 24)
        c = [(cx - 2.8, y0), (cx + 2.8, y0), (cx + 1.6, y0 + L * 0.55), (cx + d.r(0.8), y0 + L), (cx - 1.6, y0 + L * 0.55)]
        d.wash(c, "#e08a3a", 0.95, jitter=0.15, shade=0.4, cover=1.0, hatch=False)
        d.ink(c, 0.5, INKC, True, jitter=0.1)
        for t in (0.25, 0.45, 0.65):
            d.ink([(cx - 2 * (1 - t), y0 + L * t), (cx + 1.4 * (1 - t), y0 + L * t + 0.6)], 0.3, "#a85a20", op=0.8, jitter=0.05, smooth_=False)
    for cx in (506, 516):
        bt = ellipse_pts(cx, sy(cx) + 10, 5.2, 6.4, 12)
        d.wash(bt, "#8a2f52", 0.95, jitter=0.12, shade=0.5, cover=1.0, hatch=False)
        d.ink(bt, 0.5, INKC, True, jitter=0.1)
        d.ink([(cx, sy(cx) + 16), (cx + 1, sy(cx) + 24)], 0.5, "#6e2a44", jitter=0.1)
    for cx in list(range(526, 590, 9)) + [506, 516]:               # carrot and beetroot tops
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.35
            d.ink([(cx, sy(cx) + 2), (cx + 6 * math.cos(a), sy(cx) + 2 + 6 * math.sin(a)), (cx + 10 * math.cos(a + 0.2), sy(cx) + 2 + 10 * math.sin(a + 0.2))],
                  0.8, "#6b8c45" if cx > 520 else "#7a4a5a", jitter=0.1)
    d.ink([(596, sy(596) + 4), (592, sy(596) - 26)], 1.4, "#8a5f3a", jitter=0.1)            # spade left in the bed
    face(d, [(593, sy(596) - 2), (599, sy(596) - 1), (598, sy(596) + 9), (594, sy(596) + 8)], "#8f979a", w=0.5, jit=0.08)
    D.meadow(d, [p for p in top_cut if p[0] < 500], density=0.8, flowers=0.22, h=(4, 11))
    D.meadow(d, [(600, sy(600)), (690, 280), (730, 292)], density=0.8, flowers=0.22, h=(4, 11))
    D.foxglove(d, 268, 314, 40)
    D.foxglove(d, 704, 286, 40)
    # washing line from a post to the oak
    px0, py0 = 292, sy(292)
    d.ink([(px0, py0 + 2), (px0 - 1, py0 - 56)], 2.0, "#8a6038", jitter=0.2)
    line = [(px0 - 1, py0 - 54), (330, py0 - 44), (375, py0 - 49), (424, 210)]
    d.ink(line, 0.6, "#6b5240", jitter=0.3)
    shirt = [(318, 254), (314, 258), (317, 262), (320, 260), (320, 276), (334, 277), (334, 261), (337, 263), (340, 259), (336, 255), (330, 256), (324, 256)]
    hi(d, shirt)
    d.ink(shirt, 0.5, INKC, True, jitter=0.15)
    for k in range(4):
        d.ink([(321, 262 + k * 3.6), (333, 262.4 + k * 3.6)], 0.5, "#7f9cb5", op=0.7, jitter=0.05, smooth_=False)
    for sx, col in ((348, "#c96a5a"), (357, "#d9a65a")):           # a pair of odd socks
        sock = [(sx, 254), (sx + 5, 254), (sx + 5, 265), (sx + 9, 268), (sx + 8, 271), (sx, 270)]
        face(d, sock, col, w=0.45, shade=0.3, jit=0.1, cover=1.0)
    sheet = [(374, 251), (402, 236), (403, 262), (398, 268), (376, 276)]
    hi(d, sheet)
    d.ink(sheet, 0.5, INKC, True, jitter=0.2)
    d.ink([(384, 250), (385, 271)], 0.35, "#9aa3aa", op=0.7, jitter=0.2)
    d.ink([(394, 244), (395, 268)], 0.35, "#9aa3aa", op=0.7, jitter=0.2)
    # a straw bee skep on a stool
    kx, ky = 660, sy(660)
    face(d, [(kx - 12, ky - 6), (kx + 12, ky - 6), (kx + 13, ky - 3.5), (kx - 13, ky - 3.5)], WOOD, w=0.5, jit=0.1, cover=1.0)
    for lx in (-10, 10):
        d.ink([(kx + lx, ky - 3.5), (kx + lx * 1.15, ky + 3)], 1.4, WOODDK, jitter=0.05, smooth_=False)
    skep = [(kx - 10, ky - 6), (kx - 10.5, ky - 14), (kx - 7, ky - 21), (kx, ky - 24), (kx + 7, ky - 21), (kx + 10.5, ky - 14), (kx + 10, ky - 6)]
    d.wash(skep, "#dcb866", 0.95, jitter=0.15, shade=0.5, cover=1.0, hatch=False)
    d.ink(skep, 0.7, INKC, True, jitter=0.12)
    for k in range(1, 6):
        yy = ky - 6 - k * 3.1
        hw = 10.4 * math.sqrt(max(0.05, 1 - (k * 3.1 / 18.5) ** 2))
        d.ink([(kx - hw, yy), (kx, yy + 0.8), (kx + hw, yy)], 0.5, "#8a6a2e", op=0.85, jitter=0.08)
    d.wash(ellipse_pts(kx, ky - 8.4, 2.4, 1.8, 8), "#3a281c", 0.95, jitter=0.05, hatch=False)
    for bx, by in ((kx - 18, ky - 22), (kx + 15, ky - 27), (kx + 22, ky - 14), (kx - 6, ky - 33)):
        face(d, ellipse_pts(bx, by, 1.9, 1.3, 8), "#e3b43a", w=0.35, shade=0.0, jit=0.03, cover=1.0)
        d.ink([(bx, by - 1.3), (bx, by + 1.3)], 0.5, INKC, jitter=0.02, smooth_=False)
        hi(d, ellipse_pts(bx - 0.4, by - 2.1, 1.5, 0.9, 6))
    # chimney
    cy0 = sy(flue_x)
    face(d, rect_pts(flue_x - 13, cy0 - 34, 26, 38, 10), "#b9704e", w=0.9, shade=0.5, cover=1.0)
    for j in range(5):
        d.ink([(flue_x - 13, cy0 - 28 + j * 7), (flue_x + 13, cy0 - 28 + j * 7)], 0.4, "#7a4630", op=0.7, jitter=0.1, smooth_=False)
        for i in range(3):
            xx = flue_x - 13 + (i + 0.5 * (j % 2)) * 9.5 + 3
            d.ink([(xx, cy0 - 35 + j * 7), (xx, cy0 - 28 + j * 7)], 0.4, "#7a4630", op=0.7, jitter=0.05, smooth_=False)
    face(d, rect_pts(flue_x - 16, cy0 - 40, 32, 7, 10), "#a35f42", w=0.8, shade=0.3, cover=1.0)
    face(d, [(flue_x - 7, cy0 - 40), (flue_x - 5.5, cy0 - 54), (flue_x + 5.5, cy0 - 54), (flue_x + 7, cy0 - 40)], "#c98a5e", w=0.7, shade=0.5, cover=1.0)
    d.hatch(rect_pts(flue_x + 3, cy0 - 34, 10, 38, 10), ang=0.3, gap=2.2, op=0.3)
    O.smoke(d, flue_x, cy0 - 60, 140, 11)

    # ---------------------------------------------------------------- the oak
    D.oak_tree(d, 440, 270, 120, 34, 188, 102, lean=-6, leaves=2700)
    d.hatch([(446, 160), (460, 160), (470, 268), (444, 268)], ang=0.25, gap=2.3, op=0.3)
    d.ink([(500, 164), (497, 232)], 0.6, "#b8955a", jitter=0.15)
    d.ink([(520, 156), (518, 232)], 0.6, "#b8955a", jitter=0.15)
    face(d, [(492, 232), (523, 232), (524, 236), (491, 236)], WOODLT, w=0.6, jit=0.1, cover=1.0)
    for bx, by, c in ((214, 598, "#e3b43a"), (36, 590, "#7f9cb5"), (310, 232, "#f0e6c8"), (668, 236, "#e9a0ac")):
        for s_ in (-1, 1):
            d.wash(blob(bx + s_ * 3.6, by - 2, 3.8, 2.9, d.rng, 0.1, 8, rot=s_ * 0.5), c, 0.92, jitter=0.05, hatch=False)
        d.ink([(bx, by - 4), (bx, by + 2)], 0.6, INKC, jitter=0.03, smooth_=False)
    return d.save(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "compare", "plate_burrow_cutaway_v2.jpg")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    print(build(out, int(sys.argv[2]) if len(sys.argv) > 2 else None))
