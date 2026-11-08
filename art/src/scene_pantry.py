"""Half-page spot illustration: a corner of the pantry, close up, fading softly into the page.

Shows the edition's finish at the scale where small domestic detail lives (5.5 x 4.0in,
transparent background, vignetted edge).  No characters - except the hidden snail.
"""
import math
from kit import PAL, INK, INK_SOFT, ellipse_pts, blob, rect_pts, arch_pts
from wc import Canvas
import objects as O
import detail as D


def netted_ham(d, x, y, s=1.0):
    O.ham(d, x, y, s)
    for k in range(-3, 4):
        d.ink([(x + k * 2.4 * s - 3 * s, y + 12 * s), (x + k * 2.4 * s + 4 * s, y + 35 * s)], 0.6, "#5a3c22", op=0.55)
        d.ink([(x + k * 2.4 * s + 3 * s, y + 12 * s), (x + k * 2.4 * s - 4 * s, y + 35 * s)], 0.6, "#5a3c22", op=0.55)
    d.ink(ellipse_pts(x - 3 * s, y + 22 * s, 2.5 * s, 5 * s, 8, a0=3.3, a1=4.6), 0.9, "#ffe8d0", op=0.8)


def build(path):
    d = Canvas(5.5, 4.0, seed=41, paper=False)
    d.push_transform(0, 0, 2.0)        # internal drawing space 275 x 200 units
    # back wall, a little lamplight, the deep-set round window throwing daylight in
    d.wash(rect_pts(-5, -5, 290, 215, 30), "#efdcb4", 0.9, smooth_=False, shade=0.35, hatch=False)
    for _ in range(80):
        px, py = d.u(5, 270), d.u(20, 150)
        d.ink([(px, py), (px + d.u(2, 5), py + d.r(1))], 0.3, "#b59b78", op=0.35, jitter=0.2)
    wx, wy, wr = 214, 64, 25
    d.wash([(wx - 30, wy + 12), (wx + 30, wy + 12), (wx + 70, 150), (wx - 40, 150)], "#fbf0c8", 0.5, soft=True)
    d.shape(ellipse_pts(wx, wy, wr + 6, wr + 6, 36), "#c9b28d", 0.9, w=0.7, shade=0.7)
    d.shape(ellipse_pts(wx, wy, wr, wr, 36), "#cfe0e6", 0.9, w=0.6, shade=0.1)
    d.wash([(wx - wr, wy + 8), (wx - 12, wy - 2), (wx + 2, wy + 4), (wx + 14, wy - 4), (wx + wr, wy + 6), (wx + wr, wy + 20), (wx - wr, wy + 20)],
           "#a6bd6a", 0.8, shade=0.3)
    D.leafy_mass(d, wx + 12, wy + 2, 14, 9, clumps=4, leaves=50, leaf_len=(2.5, 4))
    d.line(wx - wr, wy, wx + wr, wy, 1.4, "#8a6440", 0)
    d.line(wx, wy - wr, wx, wy + wr, 1.4, "#8a6440", 0)
    d.shape(rect_pts(wx - wr - 6, wy + wr + 4, 2 * wr + 12, 5, 12), "#b98a5a", 0.9, w=0.6, smooth_=False, shade=0.5)
    O.jar(d, wx - 12, wy + wr + 4, 10, kind="crock")
    d.shape([(wx + 2, wy + wr + 4), (wx + 1, wy + wr - 6), (wx + 11, wy + wr - 6), (wx + 10, wy + wr + 4)], "#c4774a", 0.92, w=0.5)
    for k in range(4):
        D.wildflower(d, wx + 4 + k * 1.8, wy + wr - 6, d.choice(["daisy", "forgetmenot", "buttercup"]), 0.7)
    O.stone_wall(d, -5, 166, 290, 22, course=8, colors=["#cdbfa6", "#bcae95", "#d8c9ad"], mortar="#e9dcc0", ink_op=0.6)
    D.flags(d, -5, 186, 290, 16)
    D.beam_grain(d, -5, 4, 290, 9, "#9a7048")
    for hx in (8, 60, 112, 164, 266):
        d.ink([(hx, 13), (hx, 17)], 0.9, "#4a4a4a")
    # from the beam: hams in their nets, herbs and onions
    netted_ham(d, 152, 15, 1.15)
    netted_ham(d, 176, 16, 0.95)
    for hx in (124, 138, 258):
        D.herb_bunch(d, hx, 14, 1.1)
    O.onion_string(d, 268, 14, 6, 1.0)
    # three shelves on the left
    D.preserves_shelf(d, 8, 58, 106, 16)
    D.preserves_shelf(d, 8, 92, 106, 15)
    O.shelf(d, 8, 126, 106)
    for cx in (20, 44, 68):
        O.cheese(d, cx, 126, 10)
    O.cake(d, 96, 125, 0.7)
    D.snail(d, 100, 41, 0.75)       # the hidden snail, on the top shelf
    # the bench under the window
    bx0, bx1, by = 150, 268, 132
    D.beam_grain(d, bx0, by, bx1 - bx0, 6, "#b98a5a")
    for lx in (bx0 + 6, bx1 - 9):
        d.shape(rect_pts(lx, by + 6, 4, 50, 8), "#8a5f3a", 0.92, w=0.5, smooth_=False, shade=0.5)
    d.line(bx0 + 8, by + 40, bx1 - 7, by + 40, 1.4, "#8a5f3a", 0)
    D.jug(d, 166, by, 1.2)
    d.shape([(178, by), (176, by - 15), (198, by - 15), (196, by)], "#d8c9a8", 0.92, w=0.6, shade=0.6)     # bread crock
    d.text(187, by - 6, "BREAD", size=3.4, family="IM Fell English SC", color="#5d7fb0")
    d.shape(ellipse_pts(187, by - 15.5, 11.5, 2.4, 14), "#c9b58f", 0.92, w=0.5)
    pie = [(204, by), (203, by - 4), (209, by - 9), (223, by - 9), (229, by - 4), (228, by)]
    d.shape(ellipse_pts(216, by, 15, 2.6, 16), "#f3f1ea", 0.95, w=0.5)
    d.shape(pie, "#d9a25a", 0.92, w=0.6, shade=0.7)
    for k in range(5):
        d.ink([(207 + k * 4.5, by - 8), (209 + k * 4.5, by - 3)], 0.4, "#9a6a3a", op=0.8)
    D.jam_pot(d, 238, by, 1.1)
    d.shape([(246, by), (246, by - 12), (258, by - 12), (258, by)], "#e2a13a", 0.88, w=0.5, smooth_=False, shade=0.6)   # honey + dipper
    d.ink([(252, by - 12), (256, by - 22)], 1.0, "#a07a4a")
    d.shape(ellipse_pts(256.5, by - 23, 2, 2.4, 8), "#c9a25a", 0.9, w=0.4)
    for k in range(5):
        d.shape(ellipse_pts(232 + k * 3.4, by + 34 - (k % 2) * 2.4, 2.1, 2.7, 10), "#f1e6cf", 0.95, w=0.35)
    d.shape([(228, by + 38), (227, by + 33), (250, by + 33), (249, by + 38)], "#c9b58f", 0.92, w=0.5)
    O.barrel_side(d, 176, by + 58, 30, 38, color="#b07a43")
    for k in range(8):
        d.shape(ellipse_pts(166 + (k % 4) * 6.5 + d.r(1), by + 18 - (k // 4) * 4, 3.4, 3.1, 12),
                d.choice(["#c4513a", "#9eb04a", "#d9b44a"]), 0.92, w=0.4, shade=0.6)
    D.potato_sack(d, 212, by + 58, 26, 30, "OATS", "#d8c394")
    # floor: flour sack with scoop, basket of potatoes, a broom
    D.potato_sack(d, 96, 196, 30, 34, "FLOUR", "#f3ead6")
    d.ink([(86, 164), (78, 154)], 1.4, "#a07a4a")
    d.shape(ellipse_pts(88, 166, 4, 3, 10), "#cfc6b8", 0.9, w=0.5)
    O.basket(d, 46, 196, 28, 12, "#c9a87a")
    d.ink([(134, 182), (130, 128)], 1.6, "#8a5f3a")
    d.shape([(131, 178), (136, 178), (142, 196), (124, 196)], "#d9b874", 0.9, w=0.6, smooth_=False, shade=0.6)
    for k in range(8):
        d.ink([(132 + k * 0.6, 180), (125 + k * 2.2, 196)], 0.45, "#9a7a3a", op=0.8)
    d.line(130, 183, 138, 183, 1.0, "#c96a5a", 0)
    d.pop_transform()
    d.set_vignette(blob(275, 195, 262, 188, d.rng, 0.07, 24), soft=22)
    return d.save(path)


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else "../png/half_pantry_vignette.png")
