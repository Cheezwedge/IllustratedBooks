"""
wc.py - a raster watercolour-and-pen engine.

Drop-in replacement for kit.Doc (same drawing API), but instead of emitting SVG it paints
directly into a 300 dpi pixel canvas using a simple physical model of transparent watercolour:

  * every wash is a GLAZE: it multiplies the paint already on the paper (colours mix and darken
    like real transparent pigment), optionally after LIFTING what is underneath (so objects can be
    painted 'over' a background, as an illustrator would by reserving the area);
  * the wash edge wanders slightly (low-frequency displacement) and pigment POOLS at the edge as
    the wash dries (edge darkening);
  * pigment GRANULATES into the hollows of a cold-press paper surface;
  * washes are MOTTLED (uneven density) and MODELLED - darker away from a light source at the
    upper left - so every object has volume rather than a flat fill;
  * pen lines are fine, tapered, slightly broken, with occasional faint pencil under-drawing;
  * optional fine HATCHING on the shadow side of objects;
  * whites are reserved paper (painting a near-white 'lifts' the paint back to paper).

Units are the same as kit.Doc: 100 units = 1 inch.  DPI comes from WC_DPI (default 300).
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from kit import PAL, INK, INK_SOFT  # noqa: F401  (re-exported for scene modules)

DPI = int(os.environ.get("WC_DPI", "300"))
INK_SCALE = 0.5          # pen lines are finer than the old SVG strokes
HATCH = True
PENCIL = True
FONT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fonts"))
FONTS = {("IM Fell English", False): "IMFellEnglish-400.ttf", ("IM Fell English", True): "IMFellEnglish-400i.ttf",
         ("IM Fell English SC", False): "IMFellEnglishSC-400.ttf", ("IM Fell French Canon", False): "IMFellFrenchCanon-400.ttf",
         ("IM Fell French Canon", True): "IMFellFrenchCanon-400i.ttf", ("EB Garamond", False): "EBGaramond-400.ttf",
         ("EB Garamond", True): "EBGaramond-400i.ttf"}
PAPER_RGB = (0.985, 0.968, 0.93)


SOFTEN = 0.14   # pull wash colours gently towards a natural, delicate palette


def soften(rgb, k=None):
    k = SOFTEN if k is None else k
    grey = float(rgb @ np.array([0.3, 0.55, 0.15], np.float32))
    out = rgb * (1 - k) + grey * k          # desaturate a little
    return out * (1 - k * 0.5) + np.float32(1.0) * k * 0.5   # and lighten a little


def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


def value_noise(h, w, cell, rng, order=3):
    """Smooth noise in [0,1] with features about `cell` pixels across."""
    gh, gw = max(2, int(h / cell) + 3), max(2, int(w / cell) + 3)
    g = rng.random((gh, gw)).astype(np.float32)
    z = ndi.zoom(g, (h / (gh - 2), w / (gw - 2)), order=order, mode="reflect")
    z = z[:h, :w]
    if z.shape != (h, w):
        z = np.pad(z, ((0, h - z.shape[0]), (0, w - z.shape[1])), mode="edge")
    z -= z.min()
    m = z.max()
    return z / m if m > 0 else z


def flatten(pts, closed, smooth_, step_px=2.0):
    """Catmull-Rom (same tension as kit.smooth) -> dense polyline."""
    n = len(pts)
    if not smooth_ or n < 3:
        out = list(pts)
        if closed and n > 1:
            out = out + [out[0]]
        return out
    t = 0.5
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        L = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        k = max(2, int(L / step_px))
        for j in range(k):
            s = j / k
            ms = 1 - s
            x = ms ** 3 * p1[0] + 3 * ms * ms * s * c1[0] + 3 * ms * s * s * c2[0] + s ** 3 * p2[0]
            y = ms ** 3 * p1[1] + 3 * ms * ms * s * c1[1] + 3 * ms * s * s * c2[1] + s ** 3 * p2[1]
            out.append((x, y))
    out.append(pts[0] if closed else pts[-1])
    return out


class Canvas:
    """Raster watercolour canvas with the kit.Doc drawing API."""

    def __init__(self, w_in, h_in, seed=1, paper=True, paper_color=None, grain=True, dpi=None):
        self.dpi = dpi or DPI
        self.k = self.dpi / 100.0          # pixels per unit
        self.ks = self.dpi / 300.0         # effect scale relative to 300 dpi
        self.w, self.h = w_in * 100, h_in * 100
        self.w_in, self.h_in = w_in, h_in
        self.W, self.H = int(round(w_in * self.dpi)), int(round(h_in * self.dpi))
        self.rng = random.Random(seed)
        self.seed = seed
        self.paper = paper
        self.paper_rgb = np.array(PAPER_RGB, np.float32)
        if paper_color:
            self.paper_rgb = hex2rgb(paper_color) * 0.35 + self.paper_rgb * 0.65
        self.T = np.ones((self.H, self.W, 3), np.float32)
        nr = np.random.default_rng(seed)
        H, W, s = self.H, self.W, self.ks
        # cold-press paper height map
        self.tex = (0.45 * value_noise(H, W, 5 * s, nr) + 0.35 * value_noise(H, W, 13 * s, nr)
                    + 0.2 * value_noise(H, W, 38 * s, nr)).astype(np.float32)
        self.tex = (self.tex - self.tex.min()) / (self.tex.max() - self.tex.min() + 1e-6)
        self.dx = (value_noise(H, W, 70 * s, nr) * 2 - 1).astype(np.float32)
        self.dy = (value_noise(H, W, 70 * s, nr) * 2 - 1).astype(np.float32)
        self.fx = (value_noise(H, W, 22 * s, nr) * 2 - 1).astype(np.float32)
        self.fy = (value_noise(H, W, 22 * s, nr) * 2 - 1).astype(np.float32)
        self.mot = value_noise(H, W, 110 * s, nr).astype(np.float32)
        self.mot2 = value_noise(H, W, 35 * s, nr).astype(np.float32)
        self.clip_stack = []
        self.tf = [(0.0, 0.0, 1.0)]
        self.vig = None
        self.layers = []   # compatibility with code that resets layers

    # ------------------------------------------------------------- helpers
    def r(self, a=1.0):
        return self.rng.uniform(-a, a)

    def u(self, lo, hi):
        return self.rng.uniform(lo, hi)

    def chance(self, p):
        return self.rng.random() < p

    def choice(self, seq):
        return self.rng.choice(seq)

    def push_transform(self, dx, dy, s):
        ox, oy, os_ = self.tf[-1]
        self.tf.append((ox + dx * os_, oy + dy * os_, os_ * s))

    def pop_transform(self):
        self.tf.pop()

    def _px(self, pts):
        ox, oy, s = self.tf[-1]
        k = self.k
        return [((ox + x * s) * k, (oy + y * s) * k) for x, y in pts]

    def _scale(self):
        return self.tf[-1][2]

    def push_clip(self, pts, smooth_=True):
        poly = flatten(self._px(pts), True, smooth_)
        m = self._poly_mask_full(poly)
        if self.clip_stack:
            m = m * self.clip_stack[-1]
        self.clip_stack.append(m)

    def pop_clip(self):
        self.clip_stack.pop()

    def set_vignette(self, pts, soft=40):
        """Fade the whole picture out to bare paper outside an irregular shape (spot illustrations)."""
        poly = flatten(self._px(pts), True, True)
        m = self._poly_mask_full(poly)
        amp = 18 * self.ks
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        m = ndi.map_coordinates(m, [yy + amp * self.dy * 2, xx + amp * self.dx * 2], order=1, mode="constant")
        m = ndi.gaussian_filter(m, soft * self.ks)
        m = np.clip(m * (0.85 + 0.3 * self.mot2), 0, 1)
        self.vig = m

    def _poly_mask_full(self, poly):
        img = Image.new("L", (self.W * 2, self.H * 2), 0)
        ImageDraw.Draw(img).polygon([(x * 2, y * 2) for x, y in poly], fill=255)
        return np.asarray(img.resize((self.W, self.H), Image.BOX), np.float32) / 255.0

    def _bbox(self, poly, margin):
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0 = max(0, int(min(xs) - margin))
        y0 = max(0, int(min(ys) - margin))
        x1 = min(self.W, int(max(xs) + margin) + 1)
        y1 = min(self.H, int(max(ys) + margin) + 1)
        if x1 <= x0 or y1 <= y0:
            return None
        return x0, y0, x1, y1

    def _raster(self, poly, box, ss=2):
        x0, y0, x1, y1 = box
        img = Image.new("L", ((x1 - x0) * ss, (y1 - y0) * ss), 0)
        ImageDraw.Draw(img).polygon([((x - x0) * ss, (y - y0) * ss) for x, y in poly], fill=255)
        if ss > 1:
            img = img.resize((x1 - x0, y1 - y0), Image.BOX)
        return np.asarray(img, np.float32) / 255.0

    def _clip(self, box, a):
        if self.clip_stack:
            x0, y0, x1, y1 = box
            a = a * self.clip_stack[-1][y0:y1, x0:x1]
        return a

    # ------------------------------------------------------- core painting
    def _paint(self, poly, rgb, op, soft=False, shade=None, gran=None, edge=None, cover=None, grad=None, hatch=True):
        s = self.ks
        amp = (7.0 if soft else 2.6) * s
        blur = 7.0 * s * self._scale() ** 0.5 if soft else 0
        box = self._bbox(poly, amp * 2 + blur * 3 + 4)
        if box is None:
            return
        x0, y0, x1, y1 = box
        m = self._raster(poly, box)
        if m.max() <= 0:
            return
        h, w = m.shape
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = self.dx[y0:y1, x0:x1]
        dy = self.dy[y0:y1, x0:x1]
        fx = self.fx[y0:y1, x0:x1]
        fy = self.fy[y0:y1, x0:x1]
        m = ndi.map_coordinates(m, [yy + amp * dy + 0.5 * amp * fy, xx + amp * dx + 0.5 * amp * fx], order=1, mode="constant")
        if soft:
            m = ndi.gaussian_filter(m, blur)
        tex = self.tex[y0:y1, x0:x1]
        mot = self.mot[y0:y1, x0:x1]
        mot2 = self.mot2[y0:y1, x0:x1]
        lum = float(rgb @ np.array([0.3, 0.55, 0.15], np.float32))
        # whites: reserve paper (lift paint) instead of glazing
        if lum > 0.94:
            a = self._clip(box, m * min(1.0, op * 1.05))
            T = self.T[y0:y1, x0:x1]
            tint = 1 - (1 - rgb) * 0.6
            self.T[y0:y1, x0:x1] = T * (1 - a[..., None]) + tint * a[..., None]
            return
        if cover is None:
            cover = float(np.clip((op - 0.55) / 0.3, 0, 1)) * 0.9
        if shade is None:
            shade = 0.0 if soft else 0.42
        if gran is None:
            gran = 0.35 if lum < 0.75 else 0.22
        if edge is None:
            edge = 0.0 if soft else 0.65
        dens = m * op
        dens = dens * (0.8 + 0.32 * mot + 0.12 * (mot2 - 0.5))
        if shade > 0:
            pxs = [p[0] for p in poly]
            pys = [p[1] for p in poly]
            bx0, bx1, by0, by1 = min(pxs), max(pxs), min(pys), max(pys)
            tx = (xx + x0 - bx0) / max(1.0, bx1 - bx0)
            ty = (yy + y0 - by0) / max(1.0, by1 - by0)
            t = np.clip(0.45 * tx + 0.55 * ty, 0, 1)
            dens = dens * (1 - shade * 0.55 + shade * 1.1 * t ** 1.3)
        if edge > 0:
            hard = m > 0.5
            if hard.any():
                dist = ndi.distance_transform_edt(hard)
                dens = dens * (1 + edge * np.exp(-dist / (2.4 * s)) * hard + 0.0)
        if gran > 0:
            dens = dens * (1 - gran + gran * 2 * tex)
        dens = self._clip(box, np.clip(dens, 0, 1.6))
        T = self.T[y0:y1, x0:x1]
        if cover > 0:
            lift = self._clip(box, np.clip(m, 0, 1) * cover)
            T = T * (1 - lift[..., None]) + lift[..., None]
        col = rgb if grad is None else grad(xx + x0, yy + y0)
        absorb = (1 - col) if grad is None else (1 - col)
        self.T[y0:y1, x0:x1] = np.clip(T * (1 - np.clip(dens[..., None] * absorb, 0, 0.97)), 0, 1)
        if HATCH and hatch and not soft and shade > 0.2 and op > 0.6 and (x1 - x0) * (y1 - y0) > (40 * s) ** 2 and lum < 0.88:
            self._hatch(m, box, poly, 0.22 + 0.25 * (1 - lum))

    def _hatch(self, m, box, poly, strength):
        """Fine diagonal pen hatching on the shadow side (lower right) of a shape."""
        x0, y0, x1, y1 = box
        h, w = m.shape
        s = self.ks
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        spacing = 5.2 * s
        wob = 2.0 * s * self.fx[y0:y1, x0:x1]
        ph = ((xx + x0) * 0.62 + (yy + y0) * 0.78 + wob) / spacing
        lines = np.clip(1.0 - np.abs((ph - np.round(ph))) * spacing / (0.75 * s + 0.3), 0, 1)
        pxs = [p[0] for p in poly]
        pys = [p[1] for p in poly]
        bx0, bx1, by0, by1 = min(pxs), max(pxs), min(pys), max(pys)
        t = np.clip(0.5 * (xx + x0 - bx0) / max(1, bx1 - bx0) + 0.5 * (yy + y0 - by0) / max(1, by1 - by0), 0, 1)
        region = np.clip((t - 0.58) / 0.25, 0, 1) * np.clip(m * 1.4 - 0.4, 0, 1)
        brk = np.clip(self.mot2[y0:y1, x0:x1] * 1.6 - 0.2, 0, 1)
        a = self._clip(box, lines * region * brk * strength)
        ink = hex2rgb(INK)
        self.T[y0:y1, x0:x1] *= 1 - a[..., None] * (1 - ink)

    def _stroke(self, poly, width, rgb, op, taper=True, closed=False, broken=0.25):
        if len(poly) < 2:
            return
        s = self.ks
        n = len(poly)
        # cumulative length
        L = [0.0]
        for i in range(1, n):
            L.append(L[-1] + math.hypot(poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]))
        tot = L[-1] or 1.0
        left, right = [], []
        for i in range(n):
            if i == 0:
                vx, vy = poly[1][0] - poly[0][0], poly[1][1] - poly[0][1]
            elif i == n - 1:
                vx, vy = poly[-1][0] - poly[-2][0], poly[-1][1] - poly[-2][1]
            else:
                vx, vy = poly[i + 1][0] - poly[i - 1][0], poly[i + 1][1] - poly[i - 1][1]
            l = math.hypot(vx, vy) or 1.0
            nx, ny = -vy / l, vx / l
            t = L[i] / tot
            if taper and not closed:
                k = min(1.0, 0.25 + t * 4) * min(1.0, 0.35 + (1 - t) * 3.2)
            else:
                k = 1.0
            k *= 1 + 0.18 * math.sin(L[i] / (9 * s) + self.seed)
            hw = max(0.32, width * k / 2)
            left.append((poly[i][0] + nx * hw, poly[i][1] + ny * hw))
            right.append((poly[i][0] - nx * hw, poly[i][1] - ny * hw))
        outline = left + right[::-1]
        box = self._bbox(outline, 3)
        if box is None:
            return
        x0, y0, x1, y1 = box
        a = self._raster(outline, box, ss=3)
        if broken:
            a = a * (1 - broken + broken * np.clip(self.mot2[y0:y1, x0:x1] * 1.7, 0, 1))
            a = a * (0.82 + 0.18 * self.tex[y0:y1, x0:x1])
        a = self._clip(box, np.clip(a * op, 0, 1))
        self.T[y0:y1, x0:x1] *= 1 - a[..., None] * (1 - rgb)

    # ------------------------------------------------------------- the API
    def wash(self, pts, color, op=0.85, closed=True, soft=False, jitter=1.2, smooth_=True, extra="",
             shade=None, gran=None, edge=None, cover=None, hatch=True):
        p = [(x + self.r(jitter), y + self.r(jitter)) for x, y in pts]
        poly = flatten(self._px(p), True, smooth_)
        self._paint(poly, soften(hex2rgb(color)), op, soft, shade, gran, edge, cover, hatch=hatch)

    def wash_gradient(self, pts, stops, x1, y1, x2, y2, op=0.9, soft=False, smooth_=False, shade=0.0, cover=0.9):
        """A wash whose colour changes along (x1,y1)->(x2,y2) (units). stops: [(t, '#hex'), ...]."""
        P = self._px([(x1, y1), (x2, y2)])
        (ax, ay), (bx, by) = P
        vx, vy = bx - ax, by - ay
        L2 = vx * vx + vy * vy or 1.0
        ts = np.array([t for t, _ in stops], np.float32)
        cs = np.stack([soften(hex2rgb(c)) for _, c in stops])

        def grad(X, Y):
            t = np.clip(((X - ax) * vx + (Y - ay) * vy) / L2, 0, 1)
            out = np.empty(t.shape + (3,), np.float32)
            for ch in range(3):
                out[..., ch] = np.interp(t, ts, cs[:, ch])
            return out
        poly = flatten(self._px(pts), True, smooth_)
        self._paint(poly, cs[0], op, soft, shade, 0.2, 0.0 if soft else 0.3, cover, grad=grad)

    def ink(self, pts, w=1.3, color=INK, closed=False, op=1.0, smooth_=True, jitter=0.6, dash=None):
        p = [(x + self.r(jitter), y + self.r(jitter)) for x, y in pts]
        poly = flatten(self._px(p), closed, smooth_, step_px=1.5)
        width = max(0.55, w * INK_SCALE * self.k * self._scale())
        rgb = hex2rgb(color)
        if dash:
            seg_on, seg_off = (float(v) * self.k * self._scale() for v in dash.split()[:2])
            acc, cur, on = 0.0, [poly[0]], True
            for a, b in zip(poly, poly[1:]):
                acc += math.hypot(b[0] - a[0], b[1] - a[1])
                cur.append(b)
                if acc >= (seg_on if on else seg_off):
                    if on and len(cur) > 1:
                        self._stroke(cur, width, rgb, op * 0.9, taper=False)
                    cur, acc, on = [b], 0.0, not on
            if on and len(cur) > 1:
                self._stroke(cur, width, rgb, op * 0.9, taper=False)
            return
        self._stroke(poly, width, rgb, op * 0.9, taper=True, closed=closed)
        if PENCIL and len(poly) > 6 and self.chance(0.3) and color in (INK, INK_SOFT):
            off = self.u(0.6, 1.6) * self.ks
            pp = [(x + off * self.fx[min(self.H - 1, int(y)), min(self.W - 1, int(x))] * 2,
                   y + off) for x, y in poly]
            self._stroke(pp, 0.7 * self.ks, hex2rgb("#77706a"), 0.16, taper=True, broken=0.5)

    def shape(self, pts, color, op=0.85, w=1.3, ink_color=INK, smooth_=True, ink_op=1.0, soft=False, shade=None):
        self.wash(pts, color, op, True, soft=soft, smooth_=smooth_, shade=shade)
        if w > 0:
            self.ink(pts, w, ink_color, True, op=ink_op * 0.92, smooth_=smooth_)

    def line(self, x1, y1, x2, y2, w=1.2, color=INK, bow=0.8, op=1.0):
        from kit import line_pts
        self.ink(line_pts(x1, y1, x2, y2, bow, self.rng), w, color, op=op)

    def dot(self, x, y, r=1.2, color=INK, op=1):
        (cx, cy), = self._px([(x, y)])
        rr = max(0.6, r * self.k * self._scale() * 0.8)
        box = self._bbox([(cx - rr, cy - rr), (cx + rr, cy + rr)], 2)
        if box is None:
            return
        x0, y0, x1, y1 = box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        a = np.clip(rr + 0.5 - np.hypot(xx - cx, yy - cy), 0, 1) * op * 0.9
        rgb = hex2rgb(color)
        a = self._clip(box, a)
        if rgb.mean() > 0.94:
            T = self.T[y0:y1, x0:x1]
            self.T[y0:y1, x0:x1] = T * (1 - a[..., None]) + a[..., None]
        else:
            self.T[y0:y1, x0:x1] *= 1 - a[..., None] * (1 - rgb)

    def glow(self, x, y, r, color=PAL["flame"], op=0.7):
        (cx, cy), = self._px([(x, y)])
        R = r * self.k * self._scale()
        box = self._bbox([(cx - R, cy - R), (cx + R, cy + R)], 2)
        if box is None:
            return
        x0, y0, x1, y1 = box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d2 = ((xx - cx) ** 2 + ((yy - cy) / 0.9) ** 2) / (R * R)
        g = np.exp(-d2 * 2.6)
        lift = self._clip(box, np.clip(g * op * 0.55, 0, 1))
        T = self.T[y0:y1, x0:x1]
        T = T * (1 - lift[..., None]) + lift[..., None]
        warm = self._clip(box, g * op * 0.38)
        self.T[y0:y1, x0:x1] = T * (1 - warm[..., None] * (1 - hex2rgb(color)))

    def text(self, x, y, s, size=14, color=INK, family="IM Fell English", anchor="middle", italic=False, extra=""):
        fn = FONTS.get((family, italic)) or FONTS.get((family, False)) or "IMFellEnglish-400.ttf"
        px = max(6, int(size * self.k * self._scale()))
        font = ImageFont.truetype(os.path.join(FONT_DIR, fn), px)
        (cx, cy), = self._px([(x, y)])
        bb = font.getbbox(s)
        tw = bb[2] - bb[0]
        ax = cx - tw / 2 if anchor == "middle" else (cx - tw if anchor == "end" else cx)
        box = self._bbox([(ax - 4, cy - px * 1.1), (ax + tw + 4, cy + px * 0.4)], 2)
        if box is None:
            return
        x0, y0, x1, y1 = box
        img = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(img).text((ax - x0, cy - y0), s, font=font, fill=255, anchor="ls")
        a = np.asarray(img, np.float32) / 255.0 * 0.92
        a = self._clip(box, a * (0.85 + 0.15 * self.tex[y0:y1, x0:x1]))
        self.T[y0:y1, x0:x1] *= 1 - a[..., None] * (1 - hex2rgb(color))

    # ---------------------------------------------------------------- output
    def image(self):
        T = self.T
        if self.vig is not None:
            T = 1 - (1 - T) * self.vig[..., None]
        if self.paper:
            shading = 1 - 0.07 * (1 - self.tex[..., None])
            rgb = np.clip(self.paper_rgb * shading * T, 0, 1)
            return Image.fromarray((rgb * 255 + 0.5).astype(np.uint8), "RGB")
        # transparent: convert the multiply layer to straight alpha (exact over white)
        a = np.clip(1 - T.min(axis=2), 0, 1)
        col = 1 - (1 - T) / np.maximum(a[..., None], 1e-4)
        col = np.clip(col, 0, 1)
        rgba = np.dstack([col, a])
        return Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA")

    def save(self, path):
        im = self.image()
        base, ext = os.path.splitext(path)
        if ext.lower() == ".svg":
            path = base + (".jpg" if self.paper else ".png")
            ext = os.path.splitext(path)[1]
        if ext.lower() in (".jpg", ".jpeg"):
            im.convert("RGB").save(path, quality=93, dpi=(self.dpi, self.dpi), subsampling=0)
        else:
            im.save(path, dpi=(self.dpi, self.dpi), optimize=False, compress_level=6)
        return path


Doc = Canvas
