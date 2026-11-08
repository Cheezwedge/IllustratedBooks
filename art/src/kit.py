"""
Hand-drawn watercolour drawing kit.

Every illustration in this project is built from these helpers so the whole
book shares one consistent look: wobbly sepia ink lines laid over soft,
granulating watercolour washes on warm paper.

Units: 100 user units = 1 inch.  Rendered at 300 dpi -> 3 px per unit.
"""
import math
import random

INK = "#3d2b1f"      # sepia ink
INK_SOFT = "#6b5240"  # lighter ink for fine detail

PAL = {
    "paper": "#f6eedb", "cream": "#fbf4e2",
    "sky": "#b9d2dc", "sky2": "#e3ece6", "cloud": "#fbf8ef",
    "hill_far": "#a9b9c4", "mount": "#9aa6bd", "mount2": "#c3c7d6",
    "grass": "#93b062", "grass2": "#6e9446", "grass3": "#b6c77d",
    "leaf": "#7f9c4d", "leafdk": "#58773a", "leaflt": "#a9bf6b", "moss": "#9fb168",
    "earth": "#c09668", "earth2": "#a77d52", "earthdk": "#80593a", "clay": "#d2a878",
    "root": "#7a5534",
    "stone": "#c2b7a4", "stone2": "#a99d8a", "stonedk": "#8b8070",
    "wood": "#b07a43", "wooddk": "#82552d", "woodlt": "#d1a26a",
    "plaster": "#f1dfb8", "plaster2": "#e6cc9b", "ochre": "#dba94f",
    "gold": "#dcae3e", "brass": "#cfa23c", "copper": "#c27a4a",
    "red": "#b9553d", "rust": "#a4472f", "berry": "#6e3456", "rose": "#dc8e7c", "pink": "#e9b3a5",
    "blue": "#7393b1", "navy": "#4c6385", "teal": "#5f8d87", "lav": "#a99bbf",
    "door": "#4e7d47", "door2": "#3f6a3b",
    "fire": "#f2a63c", "fire2": "#e46b2d", "flame": "#fbd96e",
    "water": "#86adbf", "water2": "#5d8597", "waterdk": "#45697a",
    "shadow": "#5d4c66", "white": "#fffdf6", "cheese": "#efc85a", "jam": "#a83a3f",
    "honey": "#e2a13a", "apple": "#c4513a", "apple2": "#9eb04a",
}


class Doc:
    """A single SVG illustration."""

    def __init__(self, w_in, h_in, seed=1, paper=True, paper_color=None, grain=True):
        self.w = w_in * 100
        self.h = h_in * 100
        self.w_in, self.h_in = w_in, h_in
        self.rng = random.Random(seed)
        self.seed = seed
        self.layers = []
        self.defs = []
        self.paper = paper
        self.paper_color = paper_color or PAL["paper"]
        self.grain = grain
        self._gid = 0
        self._add_filters()

    # ----------------------------------------------------------- utilities
    def uid(self, p="g"):
        self._gid += 1
        return f"{p}{self._gid}"

    def r(self, a=1.0):
        return self.rng.uniform(-a, a)

    def u(self, lo, hi):
        return self.rng.uniform(lo, hi)

    def chance(self, p):
        return self.rng.random() < p

    def choice(self, seq):
        return self.rng.choice(seq)

    def add(self, s):
        self.layers.append(s)

    def _add_filters(self):
        s = self.seed
        self.defs.append(f"""
<filter id="wash" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="{s}" result="n1"/>
  <feDisplacementMap in="SourceGraphic" in2="n1" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.45" numOctaves="3" seed="{s+7}" result="n2"/>
  <feColorMatrix in="n2" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.65" result="grain"/>
  <feComposite in="d" in2="grain" operator="in" result="g"/>
  <feMorphology in="d" operator="erode" radius="1.6" result="er"/>
  <feComposite in="d" in2="er" operator="out" result="edge"/>
  <feColorMatrix in="edge" type="matrix" values="0.55 0 0 0 0  0 0.55 0 0 0  0 0 0.55 0 0  0 0 0 0.45 0" result="edk"/>
  <feGaussianBlur in="edk" stdDeviation="0.5" result="edkb"/>
  <feMerge><feMergeNode in="g"/><feMergeNode in="edkb"/></feMerge>
</filter>
<filter id="washsoft" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="{s+3}" result="n1"/>
  <feDisplacementMap in="SourceGraphic" in2="n1" scale="12" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="2.2" result="b"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.35" numOctaves="3" seed="{s+9}" result="n2"/>
  <feColorMatrix in="n2" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.8 1.8" result="grain"/>
  <feComposite in="b" in2="grain" operator="in"/>
</filter>
<filter id="inkf" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="1" seed="{s+1}" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="glowf" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="paperf" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="4" seed="{s+5}" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.42  0 0 0 0 0.33  0 0 0 0 0.22  0 0 0 -1.3 0.78"/>
</filter>
<filter id="paperf2" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="{s+6}" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.55  0 0 0 0 0.42  0 0 0 0 0.25  0 0 0 -0.9 0.5"/>
</filter>
""")

    def radial(self, color, op=0.8):
        gid = self.uid("rg")
        self.defs.append(
            f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        return gid

    def linear(self, stops, x1=0, y1=0, x2=0, y2=1):
        gid = self.uid("lg")
        st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')
        return gid

    def clip(self, pts):
        cid = self.uid("cp")
        self.defs.append(f'<clipPath id="{cid}"><path d="{smooth(pts, True)}"/></clipPath>')
        return cid

    def clip_poly(self, pts):
        cid = self.uid("cp")
        self.defs.append(f'<clipPath id="{cid}"><path d="{poly(pts, True)}"/></clipPath>')
        return cid

    # ------------------------------------------------------------ drawing
    def wash(self, pts, color, op=0.85, closed=True, soft=False, jitter=1.2, smooth_=True, extra=""):
        p = [(x + self.r(jitter), y + self.r(jitter)) for x, y in pts]
        d = smooth(p, closed) if smooth_ else poly(p, closed)
        f = "washsoft" if soft else "wash"
        self.add(f'<path d="{d}" fill="{color}" fill-opacity="{op}" filter="url(#{f})" {extra}/>')

    def wash_d(self, d, color, op=0.85, soft=False, extra=""):
        f = "washsoft" if soft else "wash"
        self.add(f'<path d="{d}" fill="{color}" fill-opacity="{op}" filter="url(#{f})" {extra}/>')

    def ink(self, pts, w=1.3, color=INK, closed=False, op=1.0, smooth_=True, jitter=0.6, dash=None):
        p = [(x + self.r(jitter), y + self.r(jitter)) for x, y in pts]
        d = smooth(p, closed) if smooth_ else poly(p, closed)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-opacity="{op}" '
                 f'stroke-linecap="round" stroke-linejoin="round" filter="url(#inkf)"{da}/>')

    def ink_d(self, d, w=1.3, color=INK, op=1.0):
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-opacity="{op}" '
                 f'stroke-linecap="round" stroke-linejoin="round" filter="url(#inkf)"/>')

    def shape(self, pts, color, op=0.85, w=1.3, ink_color=INK, smooth_=True, ink_op=1.0, soft=False):
        """Watercolour wash plus ink outline of a closed shape."""
        self.wash(pts, color, op, True, soft=soft, smooth_=smooth_)
        if w > 0:
            self.ink(pts, w, ink_color, True, op=ink_op, smooth_=smooth_)

    def line(self, x1, y1, x2, y2, w=1.2, color=INK, bow=0.8, op=1.0):
        self.ink(line_pts(x1, y1, x2, y2, bow, self.rng), w, color, op=op)

    def dot(self, x, y, r=1.2, color=INK, op=1):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" fill-opacity="{op}"/>')

    def glow(self, x, y, r, color=PAL["flame"], op=0.7):
        g = self.radial(color, op)
        self.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r*0.9:.1f}" fill="url(#{g})"/>')

    def group(self, inner, extra=""):
        self.add(f"<g {extra}>{''.join(inner)}</g>")

    def begin(self, extra=""):
        """Start capturing layers into a group (e.g. for clipping)."""
        self.layers.append(("BEGIN", extra))

    def end(self):
        # collapse back to last BEGIN
        for i in range(len(self.layers) - 1, -1, -1):
            if isinstance(self.layers[i], tuple) and self.layers[i][0] == "BEGIN":
                extra = self.layers[i][1]
                inner = self.layers[i + 1:]
                del self.layers[i:]
                self.layers.append(f"<g {extra}>{''.join(inner)}</g>")
                return
        raise RuntimeError("end() without begin()")

    def text(self, x, y, s, size=14, color=INK, family="IM Fell English", anchor="middle", italic=False, extra=""):
        st = "italic" if italic else "normal"
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-style="{st}" '
                 f'fill="{color}" text-anchor="{anchor}" {extra}>{s}</text>')

    # -------------------------------------------------------------- output
    def svg(self):
        bg = ""
        if self.paper:
            bg = (f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="{self.paper_color}"/>'
                  f'<rect x="0" y="0" width="{self.w}" height="{self.h}" filter="url(#paperf2)" opacity="0.5"/>')
        grain = ""
        if self.grain:
            grain = (f'<rect x="0" y="0" width="{self.w}" height="{self.h}" filter="url(#paperf)" '
                     f'opacity="0.22" style="mix-blend-mode:multiply"/>')
            if not self.paper:
                # grain only where there is paint
                grain = ""
        body = "".join(x for x in self.layers if isinstance(x, str))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w_in}in" height="{self.h_in}in" '
                f'viewBox="0 0 {self.w:.0f} {self.h:.0f}"><defs>{"".join(self.defs)}</defs>'
                f'{bg}<g>{body}</g>{grain}</svg>')

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.svg())


# ---------------------------------------------------------------- geometry
def smooth(pts, closed=False, t=0.5):
    """Catmull-Rom spline through points -> cubic Bezier path."""
    n = len(pts)
    if n < 2:
        return ""
    if n == 2:
        return f"M{pts[0][0]:.1f},{pts[0][1]:.1f} L{pts[1][0]:.1f},{pts[1][1]:.1f}"
    P = list(pts)
    d = f"M{P[0][0]:.1f},{P[0][1]:.1f}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    if closed:
        d += " Z"
    return d


def poly(pts, closed=False):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + (" Z" if closed else "")


def ellipse_pts(cx, cy, rx, ry, n=28, rng=None, irr=0.0, a0=0.0, a1=2 * math.pi, rot=0.0):
    out = []
    full = abs((a1 - a0) - 2 * math.pi) < 1e-6
    m = n if full else n + 1
    for i in range(m):
        a = a0 + (a1 - a0) * i / n
        k = 1 + (rng.uniform(-irr, irr) if (rng and irr) else 0)
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        xr = x * math.cos(rot) - y * math.sin(rot)
        yr = x * math.sin(rot) + y * math.cos(rot)
        out.append((cx + xr, cy + yr))
    return out


def blob(cx, cy, rx, ry, rng, irr=0.12, n=14, rot=0.0):
    return ellipse_pts(cx, cy, rx, ry, n, rng, irr, rot=rot)


def rect_pts(x, y, w, h, step=18):
    pts = []
    nx = max(1, int(w / step))
    ny = max(1, int(h / step))
    for i in range(nx):
        pts.append((x + w * i / nx, y))
    for i in range(ny):
        pts.append((x + w, y + h * i / ny))
    for i in range(nx):
        pts.append((x + w - w * i / nx, y + h))
    for i in range(ny):
        pts.append((x, y + h - h * i / ny))
    return pts


def arch_pts(x, y, w, h, archh, n=16):
    """Room shape: flat floor, straight walls, elliptical arched ceiling. (x,y) = top-left."""
    pts = [(x, y + h), (x, y + archh)]
    for i in range(1, n):
        a = math.pi + math.pi * i / n
        pts.append((x + w / 2 + w / 2 * math.cos(a), y + archh + archh * math.sin(a)))
    pts += [(x + w, y + archh), (x + w, y + h)]
    pts += [(x + w * 0.5, y + h)]
    return pts


def line_pts(x1, y1, x2, y2, bow=0.8, rng=None, n=None):
    L = math.hypot(x2 - x1, y2 - y1)
    n = n or max(2, int(L / 22) + 1)
    nx, ny = (-(y2 - y1) / (L or 1), (x2 - x1) / (L or 1))
    b = rng.uniform(-bow, bow) if rng else 0
    pts = []
    for i in range(n + 1):
        t = i / n
        off = b * math.sin(math.pi * t) * min(1, L / 60)
        pts.append((x1 + (x2 - x1) * t + nx * off, y1 + (y2 - y1) * t + ny * off))
    return pts


def lerp(a, b, t):
    return a + (b - a) * t


def inside(pt, polygon):
    x, y = pt
    c = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi):
            c = not c
        j = i
    return c


def bez_pts(p0, p1, p2, p3, n=12):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


def transform_pts(pts, dx=0, dy=0, s=1.0, rot=0.0, cx=0, cy=0):
    out = []
    for x, y in pts:
        x0, y0 = (x - cx) * s, (y - cy) * s
        xr = x0 * math.cos(rot) - y0 * math.sin(rot)
        yr = x0 * math.sin(rot) + y0 * math.cos(rot)
        out.append((xr + cx + dx, yr + cy + dy))
    return out
