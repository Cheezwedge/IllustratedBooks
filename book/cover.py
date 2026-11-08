#!/usr/bin/env python3
"""
Build a wraparound paperback cover (back + spine + front) sized from the interior page count.

    python3 book/cover.py                       # uses output/build-report.json, KDP premium colour paper
    python3 book/cover.py --pages 412 --paper ingram

Outputs (output/)
  cover-paperback.pdf     upload/print file (no guides)
  cover-guides.pdf        same with trim, spine, safe-zone and barcode guides (for checking only)
  cover-ebook-front.jpg   front panel for ebook stores (7:10)

ALWAYS check the final spine width against your printer's own cover calculator or template:
paper thickness differs between printers and paper stocks. Hardcover (case-laminate) covers need
the printer's hardcover template (extra wrap and hinge), not this file.
"""
import argparse
import html
import json
import os

from weasyprint import HTML

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "output")
PNG = os.path.join(ROOT, "art", "png")
TRIM_W, TRIM_H, BLEED = 7.0, 10.0, 0.125
PAPER = {  # inches per page (white paper, colour interiors) - rules of thumb only
    "kdp": 0.002347,          # KDP premium colour
    "kdp-standard": 0.002252,  # KDP standard colour
    "ingram": 0.0025,         # IngramSpark 70lb colour (approx.)
}


def f(p):
    return "file://" + p


def build(pages, paper, guides, cfg):
    spine = round(pages * PAPER[paper], 4)
    W = 2 * TRIM_W + spine + 2 * BLEED
    H = TRIM_H + 2 * BLEED
    back_x = 0
    spine_x = BLEED + TRIM_W
    front_x = spine_x + spine
    t = html.escape
    spine_text = spine >= 0.3
    fonts = os.path.join(ROOT, "fonts")
    css = f"""
@font-face{{font-family:'Fell';src:url({f(os.path.join(fonts,'IMFellFrenchCanon-400.ttf'))})}}
@font-face{{font-family:'Fell';font-style:italic;src:url({f(os.path.join(fonts,'IMFellFrenchCanon-400i.ttf'))})}}
@font-face{{font-family:'FellSC';src:url({f(os.path.join(fonts,'IMFellEnglishSC-400.ttf'))})}}
@font-face{{font-family:'Gar';src:url({f(os.path.join(fonts,'EBGaramond-400.ttf'))})}}
@font-face{{font-family:'Gar';font-style:italic;src:url({f(os.path.join(fonts,'EBGaramond-400i.ttf'))})}}
@page {{ size: {W}in {H}in; margin: 0; }}
body {{ margin: 0; width: {W}in; height: {H}in; position: relative; overflow: hidden; }}
.abs {{ position: absolute; }}
.panel {{ top: 0; width: {TRIM_W + BLEED}in; height: {H}in; }}
.panel img {{ width: {TRIM_W + BLEED}in; height: {H}in; }}
.spine {{ left: {spine_x}in; top: 0; width: {spine}in; height: {H}in; background: #3f5f3a; }}
.spine .txt {{ position: absolute; left: {spine / 2}in; top: {H / 2}in; width: {TRIM_H - 1.4}in; margin-left: -{(TRIM_H - 1.4) / 2}in;
   transform: rotate(90deg); text-align: center; color: #f6eedb; font: {min(16, spine * 72 * 0.5):.1f}pt 'Fell'; white-space: nowrap; }}
.spine .txt span {{ font: {min(10, spine * 72 * 0.32):.1f}pt 'FellSC'; letter-spacing: 0.12em; margin-left: 0.25in; }}
.cart {{ left: {front_x + 0.75}in; top: {BLEED + 0.55}in; width: {TRIM_W - 1.5}in; text-align: center;
   background: rgba(251,244,226,0.86); border: 1.5pt solid #6e3456; border-radius: 10pt; padding: 0.22in 0.2in 0.2in; box-sizing: border-box; }}
.cart .t {{ font: 60pt/62pt 'Fell'; color: #3d2b1f; }}
.cart .st {{ font: italic 18pt 'Fell'; color: #7a2f2a; margin-top: 2pt; }}
.cart .au {{ font: 15pt 'FellSC'; letter-spacing: 0.14em; color: #3d2b1f; margin-top: 10pt; }}
.cart .by {{ font: italic 11.5pt 'Gar'; color: #5a4636; margin-top: 4pt; }}
.ribbon {{ left: {front_x + 2.2}in; top: {BLEED + 3.2}in; width: 2.6in; text-align: center; background: #6e3456; color: #fbf4e2;
   font: italic 12pt 'Gar'; padding: 3pt 0; border-radius: 3pt; }}
.ill {{ left: {front_x + 0.6}in; top: {BLEED + TRIM_H - 0.8}in; width: {TRIM_W - 1.2}in; text-align: center; color: #fbf4e2;
   font: italic 13pt 'Gar'; text-shadow: 0 0 4pt #3d2b1f; }}
.blurb {{ left: {BLEED + 0.7}in; top: {BLEED + 1.2}in; width: {TRIM_W - 1.4}in; background: rgba(251,244,226,0.9); border-radius: 8pt;
   padding: 0.3in 0.35in; box-sizing: border-box; font: 11.5pt/15.5pt 'Gar'; color: #2b2119; border: 1pt solid #b48a62; }}
.blurb h2 {{ font: normal 20pt 'Fell'; text-align: center; margin: 0 0 8pt; color: #3d2b1f; }}
.blurb p {{ margin: 0 0 7pt; }}
.blurb .terr {{ font: 9.5pt 'FellSC'; letter-spacing: 0.08em; text-align: center; margin-top: 10pt; color: #6e3456; }}
.barcode {{ left: {BLEED + TRIM_W - 0.25 - 2.0}in; top: {BLEED + TRIM_H - 0.25 - 1.2}in; width: 2.0in; height: 1.2in; background: white; }}
.imprint {{ left: {BLEED + 0.5}in; top: {BLEED + TRIM_H - 0.85}in; font: 10pt 'FellSC'; letter-spacing: 0.12em; color: #fbf4e2;
   text-shadow: 0 0 3pt #3d2b1f; }}
.g {{ position: absolute; border: 0.5pt dashed red; box-sizing: border-box; }}
.gl {{ position: absolute; font: 7pt sans-serif; color: red; }}
"""
    body = [
        f'<div class="abs panel" style="left:{back_x}in"><img src="{f(os.path.join(PNG, "cover_back_art.jpg"))}"/></div>',
        f'<div class="abs panel" style="left:{front_x}in"><img src="{f(os.path.join(PNG, "cover_front_art.jpg"))}"/></div>',
        f'<div class="abs spine">' + (f'<div class="txt">{t(cfg["title"])}<span>{t(cfg["author"])}</span></div>' if spine_text else "") + "</div>",
        f'<div class="abs cart"><div class="t">{t(cfg["title"])}</div><div class="st">{t(cfg["subtitle"])}</div>'
        f'<div class="au">{t(cfg["author"])}</div><div class="by">with watercolour illustrations by {t(cfg["illustrator"])}</div></div>',
        f'<div class="abs ribbon">The Illustrated Edition</div>',
        f'''<div class="abs blurb"><h2>{t(cfg["title"])}</h2>
<p>[Your blurb, in your own words. For example: a comfortable hobbit who wants nothing more than his armchair and a
well-stocked pantry is swept off on an adventure by a wizard and thirteen dwarves, over mountains, through forests and
under the earth, to a dragon's hoard and home again.]</p>
<p>[What makes this edition special: cutaway views of burrows, halls, cellars and mountain workings, a picture on every
page turn, and a little snail hidden in every big illustration for young readers to find.]</p>
<p class="terr">For sale only in {t(cfg["territories"])}</p></div>''',
        f'<div class="abs barcode"></div>',
        f'<div class="abs imprint">{t(cfg["publisher"])}</div>',
    ]
    if guides:
        b = BLEED
        body += [
            f'<div class="g" style="left:{b}in;top:{b}in;width:{W - 2 * b}in;height:{TRIM_H}in;border-color:#c00"></div>',
            f'<div class="g" style="left:{spine_x}in;top:0;width:{spine}in;height:{H}in;border-color:#00a"></div>',
            f'<div class="g" style="left:{b + 0.25}in;top:{b + 0.25}in;width:{TRIM_W - 0.5}in;height:{TRIM_H - 0.5}in;border-color:#0a0"></div>',
            f'<div class="g" style="left:{front_x + 0.25}in;top:{b + 0.25}in;width:{TRIM_W - 0.5}in;height:{TRIM_H - 0.5}in;border-color:#0a0"></div>',
            f'<div class="gl" style="left:{spine_x + 0.02}in;top:{b + 0.05}in">spine {spine:.3f}in ({pages}pp, {paper})</div>',
            f'<div class="gl" style="left:{b + TRIM_W - 2.2}in;top:{b + TRIM_H - 1.65}in">barcode area 2.0 x 1.2in</div>',
            f'<div class="gl" style="left:{b + 0.3}in;top:{b + 0.05}in">red = trim · green = 0.25in safe zone · blue = spine</div>',
        ]
    doc = HTML(string=f"<html><head><style>{css}</style></head><body>{''.join(body)}</body></html>").render()
    return doc, spine, W, H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int)
    ap.add_argument("--paper", choices=list(PAPER), default="kdp")
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(ROOT, "book", "book.json")))
    pages = a.pages
    if not pages:
        rep = json.load(open(os.path.join(OUT, "build-report.json")))
        pages = rep["pages"]
    for guides, name in ((False, "cover-paperback.pdf"), (True, "cover-guides.pdf")):
        doc, spine, W, H = build(pages, a.paper, guides, cfg)
        doc.write_pdf(os.path.join(OUT, name))
    # ebook front cover
    import pymupdf
    d = pymupdf.open(os.path.join(OUT, "cover-paperback.pdf"))
    pg = d[0]
    x0 = (BLEED + TRIM_W + spine) * 72
    clip = pymupdf.Rect(x0, BLEED * 72, x0 + TRIM_W * 72, (BLEED + TRIM_H) * 72)
    zoom = 1800 / (TRIM_W * 72)
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    pix.save(os.path.join(OUT, "cover-ebook-front.jpg"), jpg_quality=92)
    print(f"cover: {pages} pages, paper={a.paper}, spine={spine:.3f}in, sheet={W:.3f} x {H:.3f}in")


if __name__ == "__main__":
    main()
