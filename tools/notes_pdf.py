#!/usr/bin/env python3
"""Compile the planning documents, art gallery and dummy samples into output/production-notes.pdf."""
import glob
import os
import re

import markdown
import pymupdf
from weasyprint import HTML

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "output")
PNG = os.path.join(ROOT, "art", "png")
CACHE = os.path.join(OUT, ".notes-cache")


def f(p):
    return "file://" + p


def page_png(pdf, n, width_px, name):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, name)
    d = pymupdf.open(pdf)
    pg = d[n - 1]
    z = width_px / pg.rect.width
    pg.get_pixmap(matrix=pymupdf.Matrix(z, z)).save(out)
    return out


def md(path):
    text = open(path, encoding="utf-8").read()
    h = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    h = h.replace("[ ]", "☐")
    return h


def main():
    fonts = os.path.join(ROOT, "fonts")
    screen = os.path.join(OUT, "interior-screen.pdf")
    css = f"""
@font-face{{font-family:'Gar';src:url({f(fonts + '/EBGaramond-400.ttf')})}}
@font-face{{font-family:'Gar';font-style:italic;src:url({f(fonts + '/EBGaramond-400i.ttf')})}}
@font-face{{font-family:'Gar';font-weight:600;src:url({f(fonts + '/EBGaramond-600.ttf')})}}
@font-face{{font-family:'Fell';src:url({f(fonts + '/IMFellEnglish-400.ttf')})}}
@font-face{{font-family:'FellSC';src:url({f(fonts + '/IMFellEnglishSC-400.ttf')})}}
@font-face{{font-family:'Canon';src:url({f(fonts + '/IMFellFrenchCanon-400.ttf')})}}
@page {{ size: A4; margin: 20mm 18mm 20mm 18mm; background: #fdf9ef;
  @bottom-center {{ content: counter(page); font: 9pt 'Fell'; color: #6b5240; }}
  @top-right {{ content: string(sec); font: italic 9pt 'Fell'; color: #6b5240; }} }}
@page :first {{ @bottom-center {{ content: none }} @top-right {{ content: none }} }}
body {{ font: 10.5pt/14.5pt 'Gar'; color: #2b2119; }}
h1 {{ font: normal 24pt 'Canon'; color: #3d2b1f; break-before: page; string-set: sec content(); margin: 0 0 8pt;
      border-bottom: 1pt solid #c9a27a; padding-bottom: 4pt; }}
h2 {{ font: normal 15pt 'Fell'; color: #6e3456; margin: 16pt 0 5pt; break-after: avoid; }}
h3 {{ font: normal 12.5pt 'Fell'; color: #3d2b1f; margin: 12pt 0 4pt; break-after: avoid; }}
p {{ margin: 0 0 6pt; }}
a {{ color: #6e3456; text-decoration: none; }}
blockquote {{ margin: 6pt 0; padding: 6pt 10pt; background: #f3e8cf; border-left: 3pt solid #b48a62; font-style: italic; }}
code {{ font-family: 'DejaVu Sans Mono'; font-size: 8.5pt; background: #f1e6cc; padding: 0 2pt; }}
pre {{ background: #f1e6cc; padding: 6pt 8pt; font-size: 8pt; line-height: 10.5pt; white-space: pre-wrap; }}
pre code {{ background: none; }}
table {{ border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 8.6pt; line-height: 11pt; }}
th {{ background: #e9d9b6; font-weight: 600; text-align: left; }}
th, td {{ border: 0.5pt solid #c9b28d; padding: 2.5pt 4pt; vertical-align: top; }}
tr {{ break-inside: avoid; }}
ul, ol {{ margin: 2pt 0 8pt; padding-left: 16pt; }}
li {{ margin-bottom: 2pt; }}
.cover {{ text-align: center; padding-top: 30mm; }}
.cover .t {{ font: 44pt 'Canon'; color: #3d2b1f; }}
.cover .s {{ font: italic 18pt 'Fell'; color: #6e3456; margin: 6pt 0 18pt; }}
.cover img {{ width: 120mm; }}
.cover .meta {{ font: 10pt 'FellSC'; letter-spacing: 0.1em; color: #6b5240; margin-top: 14pt; }}
.gal {{ text-align: center; }}
.gal img {{ margin: 3pt; vertical-align: middle; }}
.gal .cap {{ font: italic 9pt 'Gar'; color: #6b5240; text-align: center; margin-bottom: 8pt; }}
.two img {{ width: 84mm; }}
.pages img {{ width: 55mm; border: 0.5pt solid #bbb; }}
.pairs img {{ width: 84mm; border: 0.5pt solid #bbb; margin: 2pt 0; }}
.note {{ font-size: 9pt; color: #6b5240; }}
"""
    parts = []
    parts.append(f"""<div class="cover"><div class="t">The Hobbit</div>
<div class="s">An illustrated edition: plan, art bible &amp; production notes</div>
<img src="{f(PNG + '/cover_front_art.jpg')}" style="width:80mm"/>
<div class="meta">Working document · build of the dummy interior, cover and style studies</div></div>""")
    readme = md(os.path.join(ROOT, "README.md"))
    readme = re.sub(r"<h1>.*?</h1>", "<h1>Overview</h1>", readme, count=1, flags=re.S)
    readme = re.sub(r'<img[^>]*>', '', readme)
    parts.append(readme)
    for p in sorted(glob.glob(os.path.join(ROOT, "docs", "0*.md"))):
        parts.append(md(p))
    # gallery
    g = ['<h1>Style-study gallery</h1><p>All art below was generated for this project as a style reference: original '
         'settings, objects and decorations only. Characters are deliberately left for your own designs (art bible §2.6).</p>']
    g.append(f'<div class="gal two"><img src="{f(PNG + "/plate_burrow_cutaway.jpg")}"/><img src="{f(PNG + "/plate_cellar_mechanism.jpg")}"/>'
             '<div class="cap">Full-page plates: the hillside burrow-home cutaway (frontispiece) and the barrel-cellar mechanism.</div></div>')
    heads = "".join(f'<img src="{f(p)}" style="width:56mm"/>' for p in sorted(glob.glob(PNG + "/header_*.png")))
    g.append(f'<h2>Chapter openers</h2><div class="gal">{heads}<div class="cap">Nineteen bramble banners with chapter emblems.</div></div>')
    crit = "".join(f'<img src="{f(p)}" style="width:24mm"/>' for p in sorted(glob.glob(PNG + "/critter_*.png")))
    orn = "".join(f'<img src="{f(PNG + "/" + n)}" style="height:{h}"/>' for n, h in
                  (("orn_tailpiece.png", "16mm"), ("orn_section.png", "8mm"), ("orn_corner.png", "26mm")))
    dc = "".join(f'<img src="{f(PNG + "/dropcap_" + c + ".png")}" style="width:17mm"/>' for c in "ABCDEFGHIJKLM")
    g.append(f'<h2>Margin critters, ornaments and drop caps</h2><div class="gal">{crit}<div class="cap">Margin critters (stamped on pages with no other art).</div>'
             f'{orn}<div class="cap">Tailpiece, section break, corner vine.</div>{dc}<div class="cap">Illuminated drop caps (A–Z rendered).</div></div>')
    if os.path.exists(os.path.join(OUT, "cover-guides.pdf")):
        cov = page_png(os.path.join(OUT, "cover-guides.pdf"), 1, 1600, "cover.png")
        g.append(f'<h2>Wraparound cover (with guides)</h2><div class="gal"><img src="{f(cov)}" style="width:170mm"/>'
                 '<div class="cap">Back · spine · front, with trim, safe-zone, spine and barcode guides. The spine width is computed from the page count.</div></div>')
    parts.append("".join(g))
    # dummy page samples
    if os.path.exists(screen):
        d = pymupdf.open(screen)
        n = len(d)
        picks = [(1, "Half-title"), (2, "Frontispiece"), (3, "Title page"), (4, "Copyright page"), (13, "Chapter opener"),
                 (15, "Full-page plate slot"), (17, "Inset spot"), (18, "Cutaway spread, left"), (19, "Cutaway spread, right"),
                 (22, "Half-page at top"), (16, "Margin critter"), (226, "Style-study plate in place")]
        imgs = []
        for pn, cap in picks:
            if pn <= n:
                p = page_png(screen, pn, 520, f"pg{pn}.png")
                imgs.append(f'<span style="display:inline-block;text-align:center;margin:2pt"><img src="{f(p)}"/><br/>'
                            f'<span class="note">p.{pn}: {cap}</span></span>')
        parts.append('<h1>Sample pages from the dummy</h1><p>Rendered from <code>output/interior-screen.pdf</code>. Placeholder boxes '
                     'show each planned illustration\'s ID, size and brief, so the dummy doubles as a storyboard for the illustrator.</p>'
                     f'<div class="gal pages">{"".join(imgs)}</div>')
    rep = os.path.join(OUT, "build-report.md")
    if os.path.exists(rep):
        parts.append(md(rep).replace("<h1>Build report</h1>", "<h1>Build report</h1>"))
    html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(parts)}</body></html>"
    HTML(string=html, base_url=ROOT).write_pdf(os.path.join(OUT, "production-notes.pdf"))
    print("wrote output/production-notes.pdf")


if __name__ == "__main__":
    main()
