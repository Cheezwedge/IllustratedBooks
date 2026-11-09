#!/usr/bin/env python3
"""Build the portable style kit for other AI image generators.

    python3 tools/style_kit.py

Outputs
  output/style-anchors/A0..A5_*.jpg   anchor images resized for uploading (max 2048 px, cream background)
  output/style-anchors.zip            the same, zipped
  output/style-prompt-library.pdf     docs/07-style-prompt-library.md with the anchors embedded
"""
import glob
import os
import re
import zipfile

import markdown
from PIL import Image, ImageDraw, ImageFont
from weasyprint import HTML

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PNG = os.path.join(ROOT, "art", "png")
OUT = os.path.join(ROOT, "output")
ANC = os.path.join(OUT, "style-anchors")
CREAM = (251, 247, 238)


def flat(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", im.size, CREAM)
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def fit(im, max_side=2048):
    im = im.copy()
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    return im


def grid(paths, cols, cell, pad=30, label_font=None):
    ims = [flat(p) for p in paths]
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell + pad * 2, rows * cell + pad * 2), CREAM)
    for i, im in enumerate(ims):
        t = im.copy()
        t.thumbnail((cell - 20, cell - 20), Image.LANCZOS)
        x = pad + (i % cols) * cell + (cell - t.width) // 2
        y = pad + (i // cols) * cell + (cell - t.height) // 2
        sheet.paste(t, (x, y))
    return sheet


def decoration_sheet():
    """Two chapter-opener banners stacked, with a tailpiece and a drop cap beneath."""
    h1, h2 = flat(os.path.join(PNG, "header_07.png")), flat(os.path.join(PNG, "header_11.png"))
    tail, dc = flat(os.path.join(PNG, "orn_tailpiece.png")), flat(os.path.join(PNG, "dropcap_B.png"))
    W = h1.width + 60
    H = h1.height + h2.height + max(tail.height, dc.height) + 120
    sheet = Image.new("RGB", (W, H), CREAM)
    sheet.paste(h1, (30, 30))
    sheet.paste(h2, (30, 60 + h1.height))
    y = 90 + h1.height + h2.height
    sheet.paste(tail, (W // 2 - tail.width - 60, y + (dc.height - tail.height) // 2))
    sheet.paste(dc, (W // 2 + 60, y))
    return fit(sheet)


def build_anchors():
    os.makedirs(ANC, exist_ok=True)
    for f in glob.glob(os.path.join(ANC, "*.jpg")):
        os.remove(f)
    a = {
        "A1_composition_burrow_cutaway.jpg": fit(flat(os.path.join(PNG, "plate_burrow_cutaway.jpg"))),
        "A2_mechanism_cellar.jpg": fit(flat(os.path.join(PNG, "plate_cellar_mechanism.jpg"))),
        "A3_medium_pantry_closeup.jpg": fit(flat(os.path.join(PNG, "half_pantry_vignette.png"))),
        "A4_nature_studies_sheet.jpg": grid(sorted(glob.glob(os.path.join(PNG, "critter_*.png"))), 6, 300),
        "A5_decoration_opener.jpg": decoration_sheet(),
    }
    for name, im in a.items():
        im.save(os.path.join(ANC, name), quality=90)
    # your own reference images (art/anchors/*.jpg|png), copied in as U-anchors
    for p in sorted(glob.glob(os.path.join(ROOT, "art", "anchors", "*"))):
        if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            base = os.path.splitext(os.path.basename(p))[0]
            fit(flat(p)).save(os.path.join(ANC, base + ".jpg"), quality=92)
    # A0: everything on one sheet with captions
    font_path = os.path.join(ROOT, "fonts", "IMFellEnglish-400i.ttf")
    f = ImageFont.truetype(font_path, 34)
    tiles = [("A1 composition", a["A1_composition_burrow_cutaway.jpg"]), ("A2 mechanism", a["A2_mechanism_cellar.jpg"]),
             ("A3 medium & clutter", a["A3_medium_pantry_closeup.jpg"]), ("A4 nature studies", a["A4_nature_studies_sheet.jpg"]),
             ("A5 decoration", a["A5_decoration_opener.jpg"])]
    W, H = 2400, 1760
    sheet = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(sheet)
    boxes = [(30, 30, 650, 1000), (680, 30, 1300, 1000), (1330, 30, 2370, 1000), (30, 1040, 1190, 1740), (1220, 1040, 2370, 1740)]
    for (cap, im), (x0, y0, x1, y1) in zip(tiles, boxes):
        t = im.copy()
        t.thumbnail((x1 - x0, y1 - y0 - 50), Image.LANCZOS)
        sheet.paste(t, (x0 + (x1 - x0 - t.width) // 2, y0 + 50))
        d.text((x0, y0), cap, font=f, fill=(61, 43, 31))
    sheet.save(os.path.join(ANC, "A0_anchor_sheet.jpg"), quality=90)
    with zipfile.ZipFile(os.path.join(OUT, "style-anchors.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(glob.glob(os.path.join(ANC, "*.jpg"))):
            z.write(p, os.path.join("style-anchors", os.path.basename(p)))
    return sorted(glob.glob(os.path.join(ANC, "*.jpg")))


def build_pdf(anchors):
    src = open(os.path.join(ROOT, "docs", "07-style-prompt-library.md"), encoding="utf-8").read()
    body = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists"])
    body = body.replace('src="../', f'src="file://{ROOT}/')
    gallery = "".join(f'<div class="anc"><img src="file://{p}"/><div class="cap">{os.path.basename(p)}</div></div>' for p in anchors)
    fonts = os.path.join(ROOT, "fonts")
    css = f"""
@font-face{{font-family:'Gar';src:url(file://{fonts}/EBGaramond-400.ttf)}}
@font-face{{font-family:'Gar';font-style:italic;src:url(file://{fonts}/EBGaramond-400i.ttf)}}
@font-face{{font-family:'Gar';font-weight:600;src:url(file://{fonts}/EBGaramond-600.ttf)}}
@font-face{{font-family:'Fell';src:url(file://{fonts}/IMFellEnglish-400.ttf)}}
@font-face{{font-family:'Canon';src:url(file://{fonts}/IMFellFrenchCanon-400.ttf)}}
@page {{ size: A4; margin: 18mm 17mm; background: #fdf9ef; @bottom-center {{ content: counter(page); font: 9pt 'Fell'; color: #6b5240; }} }}
body {{ font: 10.5pt/14.2pt 'Gar'; color: #2b2119; }}
h1 {{ font: normal 24pt/28pt 'Canon'; color: #3d2b1f; margin: 0 0 8pt; border-bottom: 1pt solid #c9a27a; padding-bottom: 4pt; }}
h2 {{ font: normal 15pt 'Fell'; color: #6e3456; margin: 16pt 0 5pt; break-after: avoid; }}
p {{ margin: 0 0 6pt; }}
pre {{ background: #f1e6cc; border-left: 3pt solid #b48a62; padding: 6pt 8pt; font: 8.6pt/11.4pt 'DejaVu Sans Mono';
       white-space: pre-wrap; break-inside: avoid; }}
code {{ font-family: 'DejaVu Sans Mono'; font-size: 8.5pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.8pt; line-height: 11.2pt; margin: 4pt 0 10pt; }}
th {{ background: #e9d9b6; text-align: left; }} th, td {{ border: 0.5pt solid #c9b28d; padding: 2.5pt 4pt; vertical-align: top; }}
img {{ max-width: 100%; }}
p img {{ display: block; max-height: 150mm; margin: 6pt auto; }}
hr {{ border: 0; border-top: 0.6pt solid #c9a27a; }}
.gal {{ break-before: page; }}
.anc {{ text-align: center; margin: 6pt 0 12pt; break-inside: avoid; }}
.anc img {{ max-height: 120mm; }}
.cap {{ font: italic 9pt 'Gar'; color: #6b5240; }}
"""
    html = (f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}"
            f"<div class='gal'><h2>Anchor images (attach these as style references)</h2>{gallery}</div></body></html>")
    HTML(string=html, base_url=ROOT).write_pdf(os.path.join(OUT, "style-prompt-library.pdf"))


if __name__ == "__main__":
    anchors = build_anchors()
    build_pdf(anchors)
    print("anchors:", ", ".join(os.path.basename(a) for a in anchors))
    print("wrote output/style-anchors.zip and output/style-prompt-library.pdf")
