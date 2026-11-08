#!/usr/bin/env python3
"""
Build the illustrated edition's interior PDFs.

    python3 book/build.py                 # full book, print + screen PDFs + report
    python3 book/build.py --chapters 1-3  # quick partial build
    python3 book/build.py --scale 0.3     # shorter placeholder text (fast preview)

Inputs
  plan/chapters.csv        chapter titles and planning word counts
  plan/illustrations.csv   every planned illustration (id, chapter, type, position, ...)
  book/book.json           title page / copyright page details
  book/text/NN.md          YOUR chapter text (optional; placeholder text is used when missing)
  art/final/<ID>.png|jpg   finished art (optional; overrides the 'file' column)

Outputs (output/)
  interior-print.pdf       7x10in + 0.125in bleed, for the printer / KDP / IngramSpark
  interior-screen.pdf      7x10in trim, cream pages, for digital sale & proofing
  build-report.md          page counts, art coverage, spine-width estimates

How page-level art is placed
  Full-page plates, double-page spreads and half-page pictures must start exactly
  on a page boundary, otherwise the page before them is left half-empty.  Each
  chapter is therefore laid out on its own, item by item: render, find the page
  where the item's anchor paragraph falls, split the paragraph at the last whole
  word on that page, insert the art there, re-render.  Spreads are additionally
  forced to begin on a left-hand (verso) page.  Inset spots are floats; if one
  would leave a gap at the foot of a page it is nudged one paragraph later.
  Finally every text page that still has no picture gets a small 'margin
  critter' stamped in its outer bottom corner, and blank pages get a vignette,
  so there is always something to look at on every page turn.
"""
import argparse
import copy
import csv
import html
import io
import json
import os
import random
import re
import sys
import time
import logging

from weasyprint import HTML

logging.getLogger("weasyprint").setLevel(logging.ERROR)
logging.getLogger("fontTools").setLevel(logging.ERROR)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "output")
ART = os.path.join(ROOT, "art")

# ------------------------------------------------------------------ geometry
TRIM_W, TRIM_H, BLEED = 7.0, 10.0, 0.125
TOP, BOTTOM, INNER, OUTER = 0.75, 0.85, 0.875, 0.625     # margins measured from trim
TEXT_W = TRIM_W - INNER - OUTER                          # 5.5in
TEXT_H = TRIM_H - TOP - BOTTOM                            # 8.4in
NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV",
            "XVI", "XVII", "XVIII", "XIX", "XX"]

LOREM = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore "
         "magna aliqua enim ad minim veniam quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo "
         "consequat duis aute irure in reprehenderit voluptate velit esse cillum fugiat nulla pariatur excepteur sint "
         "occaecat cupidatat non proident sunt culpa qui officia deserunt mollit anim id est laborum curabitur "
         "pretium tincidunt lacus nulla gravida orci a odio nullam varius turpis et commodo pharetra est eros "
         "bibendum elit nec luctus magna felis sollicitudin mauris integer in mauris eu nibh euismod gravida").split()
OPENERS = ["Aliquam", "Bibendum", "Curabitur", "Donec", "Etiam", "Fusce", "Gravida", "Hendrerit", "Integer",
           "Justo", "Kalendae", "Lacinia", "Mauris", "Nullam", "Ornare", "Pellentesque", "Quisque", "Rhoncus", "Sed"]


# =================================================================== loading
def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def art_path(item):
    """Final art beats the plan's file column; returns absolute path or None."""
    for ext in (".png", ".jpg", ".jpeg"):
        p = os.path.join(ART, "final", item["id"] + ext)
        if os.path.exists(p):
            return p
    if item.get("file"):
        p = os.path.join(ROOT, item["file"])
        if os.path.exists(p):
            return p
    return None


def smart_quotes(s):
    s = re.sub(r'(^|[\s(\[{—–-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(^|[\s(\[{—–-])'", "\\1\u2018", s)
    s = s.replace("'", "\u2019")
    s = s.replace("---", "\u2014").replace("--", "\u2013")
    return s


def parse_text(md):
    """Very small markdown subset -> list of blocks.

    # Title            chapter title (optional, overrides chapters.csv)
    blank line         paragraph separator
    > line             verse (consecutive lines form one verse block)
    ***                section break
    {{art:ID}}         pin an illustration here
    *italic*           italics
    """
    title = None
    blocks = []
    paras = re.split(r"\n\s*\n", md.strip("\n"))
    for chunk in paras:
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("# "):
            title = chunk[2:].strip()
            continue
        if re.fullmatch(r"(\*\s*){3,}|-{3,}", chunk):
            blocks.append({"t": "break"})
            continue
        m = re.fullmatch(r"\{\{art:([A-Za-z0-9-]+)\}\}", chunk)
        if m:
            blocks.append({"t": "pin", "id": m.group(1)})
            continue
        lines = chunk.split("\n")
        if all(l.startswith(">") for l in lines):
            blocks.append({"t": "verse", "lines": [smart_quotes(l.lstrip(">").strip()) for l in lines]})
            continue
        text = smart_quotes(" ".join(l.strip() for l in lines))
        blocks.append({"t": "para", "tokens": text.split()})
    return title, blocks


def placeholder_text(ch, words, rng):
    blocks = []
    total = 0
    first = True
    while total < words:
        r = rng.random()
        if r < 0.25:
            n = rng.randint(14, 40)        # dialogue-ish
        elif r < 0.85:
            n = rng.randint(60, 120)
        else:
            n = rng.randint(130, 190)
        toks = [rng.choice(LOREM) for _ in range(n)]
        # sentences
        out = []
        cap = True
        for i, t in enumerate(toks):
            w = t.capitalize() if cap else t
            cap = False
            if i < n - 1 and rng.random() < 0.08:
                w += rng.choice([".", ".", ",", ";", "!", "?"])
                cap = w.endswith((".", "!", "?"))
            elif rng.random() < 0.06:
                w += ","
            out.append(w)
        out[-1] = out[-1].rstrip(",;") + "."
        if r < 0.25:
            out[0] = "\u201c" + out[0]
            out[-1] = out[-1] + "\u201d"
        if first:
            out[0] = OPENERS[(ch - 1) % len(OPENERS)]
            first = False
        blocks.append({"t": "para", "tokens": out})
        total += n
        if rng.random() < 0.03 and total < words * 0.9:
            blocks.append({"t": "verse", "lines": [" ".join(rng.choice(LOREM) for _ in range(rng.randint(4, 7))).capitalize()
                                                   for _ in range(rng.choice([4, 6, 8]))]})
        if rng.random() < 0.012:
            blocks.append({"t": "break"})
    blocks.insert(1, {"t": "note"})
    return blocks


# ============================================================ HTML snippets
def inline_html(tokens, italic=False):
    """Render tokens with *italic* markers; returns (html, italic_state_at_end)."""
    out = []
    for t in tokens:
        s = html.escape(t)
        res = ""
        if italic:
            res += "<em>"
        i = 0
        buf = ""
        while i < len(s):
            if s[i] == "*":
                if italic:
                    buf += "</em>"
                else:
                    buf += "<em>"
                italic = not italic
            else:
                buf += s[i]
            i += 1
        res += buf
        if italic:
            res += "</em>"
        # collapse redundant tags
        res = res.replace("<em></em>", "")
        out.append(res)
    return " ".join(out), italic


def file_url(p):
    return "file://" + p


def img_or_proxy(path, w, h, cls="", proxy=False, alt=""):
    if proxy or not path:
        return f'<div class="proxy {cls}" style="width:{w}in;height:{h}in"></div>'
    return f'<img class="{cls}" src="{file_url(path)}" style="width:{w}in;height:{h}in" alt="{html.escape(alt)}"/>'


def placeholder_box(item, w, h, kind, show_brief=True, emblem=None):
    brief = html.escape(item["brief"]) if show_brief else ""
    em = f'<img class="ph-emblem" src="{file_url(emblem)}"/>' if emblem else ""
    labels = {"plate": "Full-page plate · full bleed", "spread": "Cutaway spread · two pages",
              "half": "Half-page illustration", "inset": "Inset spot · text wraps", "map": "Map spread"}
    return (f'<div class="ph ph-{kind}" style="width:{w}in;height:{h}in">{em}'
            f'<div class="ph-id">{html.escape(item["id"])}</div>'
            f'<div class="ph-title">{html.escape(item["title"])}</div>'
            f'<div class="ph-kind">{labels.get(kind, kind)}</div>'
            f'<div class="ph-brief">{brief}</div></div>')


# ===================================================================== CSS
def font_css():
    f = os.path.join(ROOT, "fonts")
    faces = [("EB Garamond", "EBGaramond-400.ttf", 400, "normal"), ("EB Garamond", "EBGaramond-400i.ttf", 400, "italic"),
             ("EB Garamond", "EBGaramond-600.ttf", 600, "normal"), ("EB Garamond", "EBGaramond-600i.ttf", 600, "italic"),
             ("IM Fell English", "IMFellEnglish-400.ttf", 400, "normal"), ("IM Fell English", "IMFellEnglish-400i.ttf", 400, "italic"),
             ("IM Fell English SC", "IMFellEnglishSC-400.ttf", 400, "normal"),
             ("IM Fell French Canon", "IMFellFrenchCanon-400.ttf", 400, "normal"),
             ("IM Fell French Canon", "IMFellFrenchCanon-400i.ttf", 400, "italic")]
    return "\n".join(f"@font-face{{font-family:'{n}';src:url({file_url(os.path.join(f, fn))});font-weight:{w};font-style:{s}}}"
                     for n, fn, w, s in faces)


def page_css(mode, plates, cfg):
    """mode: 'print' (bleed) or 'screen' (trim)."""
    b = BLEED if mode == "print" else 0.0
    pw, ph = TRIM_W + b, TRIM_H + 2 * b
    paper = "#fdf8ec" if mode == "screen" else "white"
    title_sc = html.escape(cfg["title"])
    css = f"""
@page {{
  size: {pw}in {ph}in;
  margin: {TOP + b}in {OUTER + b}in {BOTTOM + b}in {INNER}in;
  background: {paper};
  @top-center {{ content: string(chaptitle, first-except); font: italic 10.5pt 'IM Fell English'; color: #6b5240;
                 vertical-align: bottom; padding-bottom: 0.2in; }}
  @bottom-center {{ content: counter(page); font: 11pt 'IM Fell English'; color: #6b5240; vertical-align: top; padding-top: 0.22in; }}
}}
@page :left  {{ margin-left: {OUTER + b}in; margin-right: {INNER}in;
               @top-center {{ content: "{title_sc}"; font: 10pt 'IM Fell English SC'; letter-spacing: 0.12em; color: #6b5240; }} }}
@page :right {{ margin-left: {INNER}in; margin-right: {OUTER + b}in; }}
@page :blank {{ @top-center {{ content: none }} @bottom-center {{ content: none }} }}
@page front {{ @top-center {{ content: none }} @bottom-center {{ content: none }} }}
@page body:nth(1 of body) {{ counter-reset: page 1 }}
@page front:left {{ @top-center {{ content: none }} }}
@page back {{ @top-center {{ content: none }} }}
@page back:left {{ @top-center {{ content: none }} }}
@page plate {{ margin: 0; @top-center {{ content: none }} @bottom-center {{ content: none }} }}
@page plate:left {{ margin: 0; @top-center {{ content: none }} }}
@page plate:right {{ margin: 0; }}
"""
    # per-plate named pages with the art as page background (handles bleed & left/right crop exactly)
    for name, path, kind in plates:
        url = file_url(path)
        if kind == "plate":
            size = f"{TRIM_W + BLEED}in {TRIM_H + 2 * BLEED}in"
            if mode == "print":
                pos_l, pos_r = "0 0", "0 0"
            else:
                pos_l, pos_r = f"-{BLEED}in -{BLEED}in", f"0 -{BLEED}in"
        else:  # spread halves
            size = f"{2 * TRIM_W + 2 * BLEED}in {TRIM_H + 2 * BLEED}in"
            if kind == "spreadL":
                pos_l = "0 0" if mode == "print" else f"-{BLEED}in -{BLEED}in"
                pos_r = pos_l
            else:
                pos_l = f"-{TRIM_W + BLEED}in 0" if mode == "print" else f"-{TRIM_W + BLEED}in -{BLEED}in"
                pos_r = pos_l
        for side, pos in ((":left", pos_l), (":right", pos_r)):
            css += (f"@page {name}{side} {{ margin: 0; background: {paper} url({url}) no-repeat; background-size: {size}; "
                    f"background-position: {pos}; @top-center {{ content: none }} @bottom-center {{ content: none }} }}\n")
    return css


BODY_CSS = """
html { font-family: 'EB Garamond'; font-size: 13pt; line-height: 18.5pt; color: #2b2119; }
body { margin: 0; }
p { margin: 0; text-indent: 1.3em; text-align: justify; hyphens: auto; orphans: 2; widows: 2; }
p.first, p.cont, p.after { text-indent: 0; }
p.split { text-align-last: justify; }
em { font-style: italic; }
.sc { font-variant: small-caps; letter-spacing: 0.04em; }
.note { font: italic 9.5pt/12pt 'EB Garamond'; color: #8a5a3a; border: 0.6pt dashed #c9a27a; padding: 4pt 7pt; margin: 6pt 0 8pt;
        text-align: center; text-indent: 0; }
.verse { margin: 9pt 0 9pt 1.4in; font-style: italic; }
.verse p { text-indent: 0; text-align: left; }
.sbreak { text-align: center; margin: 6pt 0; height: 0.32in; }
.sbreak img { width: 1.1in; height: 0.32in; }

.bodymatter { page: body; }
section.chapter { break-before: right; }
.opener { text-align: center; margin-top: 0.1in; margin-bottom: 0.18in; }
.opener .hdr { width: 5.5in; height: 2.0in; display: block; margin: 0 auto; }
.chapnum { font: 12pt 'IM Fell English SC'; letter-spacing: 0.25em; color: #7a2f2a; margin-top: 0.04in; }
h1 { font: normal 25pt/28pt 'IM Fell English'; margin: 0.04in 0 0; color: #3d2b1f; string-set: chaptitle content(); }
img.dropcap, div.dropcap { float: left; width: 0.86in; height: 0.86in; margin: 0.03in 0.1in 0 0; }

figure { margin: 0; }
figure.half { break-before: page; width: 5.5in; margin: 0 0 0.16in 0; text-align: center; }
figure.half img, figure.half .ph, figure.half .proxy { display: block; }
figure.inset { width: 2.45in; margin-bottom: 0.08in; }
figure.inset.right { float: right; margin-left: 0.16in; }
figure.inset.left { float: left; margin-right: 0.16in; }
figcaption { font: italic 9pt 'EB Garamond'; color: #6b5240; text-align: center; margin-top: 2pt; }
.tail { text-align: center; margin-top: 0.2in; break-before: avoid; }
.tail img { width: 2.4in; height: 0.7in; }

.plate { page: plate; width: 100%; height: 1in; margin: 0; }
.plate.ph-page { height: auto; }
.ph { box-sizing: border-box; border: 1.2pt dashed #b48a62; background: #fbf3e0; border-radius: 8pt; position: relative;
      padding: 10pt 12pt; text-align: center; overflow: hidden; color: #5a4636; }
.ph-emblem { position: absolute; width: 1.7in; height: 1.7in; left: 50%; top: 50%; margin-left: -0.85in; margin-top: -0.85in; opacity: 0.18; }
.ph-id { font: 9pt 'IM Fell English SC'; letter-spacing: 0.15em; color: #9a6a4a; }
.ph-title { font: italic 14pt/16pt 'IM Fell English'; margin: 3pt 0; color: #3d2b1f; }
.ph-kind { font: 8pt 'EB Garamond'; text-transform: uppercase; letter-spacing: 0.12em; color: #9a6a4a; }
.ph-brief { font: italic 9pt/11.5pt 'EB Garamond'; margin-top: 5pt; text-align: center; }
figure.inset .ph { padding: 6pt; }
figure.inset .ph-title { font-size: 10.5pt; line-height: 12pt; }
figure.inset .ph-brief { font-size: 8pt; line-height: 9.5pt; }
.platebox { box-sizing: border-box; width: 100%; height: 100%; padding: 0.7in 0.75in; }
.platebox .ph { width: 100% !important; height: 100% !important; padding-top: 2.6in; }
.platebox .ph-title { font-size: 22pt; line-height: 26pt; }
.platebox .ph-brief { font-size: 12pt; line-height: 16pt; margin: 10pt 0.3in 0; }
.platebox .ph-emblem { width: 3in; height: 3in; margin-left: -1.5in; margin-top: -2.9in; opacity: 0.22; }

/* front & back matter */
section.front { page: front; }
section.back { page: back; break-before: right; }
.fm { break-after: page; text-align: center; }
.halftitle { padding-top: 2.6in; }
.halftitle .t { font: 30pt 'IM Fell French Canon'; color: #3d2b1f; }
.halftitle img { width: 1.6in; height: 1.6in; margin-top: 0.5in; }
.titlepage { padding-top: 0.6in; }
.titlepage .t { font: 54pt/58pt 'IM Fell French Canon'; color: #3d2b1f; }
.titlepage .st { font: italic 19pt 'IM Fell French Canon'; color: #7a2f2a; margin-top: 0.08in; }
.titlepage .au { font: 16pt 'IM Fell English SC'; letter-spacing: 0.12em; margin-top: 0.35in; }
.titlepage img { width: 2.2in; height: 2.2in; margin: 0.35in 0 0.2in; }
.titlepage .il { font: italic 13pt 'IM Fell English'; }
.titlepage .pub { font: 11pt 'IM Fell English SC'; letter-spacing: 0.15em; margin-top: 0.9in; color: #6b5240; }
.copyright { text-align: left; font: 8.6pt/11.4pt 'EB Garamond'; padding-top: 2.2in; color: #3d3027; }
.copyright p { text-indent: 0; text-align: left; margin-bottom: 5pt; hyphens: manual; }
.copyright img { width: 0.9in; height: 0.7in; display: block; margin: 0 0 8pt; }
.dedication { padding-top: 2.8in; font: italic 14pt/20pt 'IM Fell English'; white-space: pre-line; }
.dedication img { width: 1.2in; height: 0.35in; margin-top: 0.3in; }
.listpage h2 { font: normal 22pt 'IM Fell English'; margin: 0.1in 0 0.25in; string-set: none; }
.listpage .orn { width: 2.4in; height: 0.7in; }
.toc { text-align: left; }
.toc a { display: block; color: #2b2119; text-decoration: none; font: 12pt/22pt 'EB Garamond'; }
.toc a .n { display: inline-block; width: 0.55in; font: 11pt 'IM Fell English SC'; color: #7a2f2a; }
.toc a::after { content: leader('.') target-counter(attr(href), page); }
.loi a { font: 10.5pt/17pt 'EB Garamond'; }
.loi a .n { width: 0.75in; font: 9pt 'IM Fell English SC'; }
.prose { text-align: left; }
.prose p { margin-bottom: 7pt; text-indent: 0; }
.prose h2 { font: normal 20pt 'IM Fell English'; text-align: center; margin: 0.2in 0 0.2in; }
.end { text-align: center; padding-top: 3in; font: italic 16pt 'IM Fell English'; }
"""


# ============================================================= chapter model
class Chapter:
    def __init__(self, num, title, blocks, items, rng, cfg, proxy_art=True):
        self.num = num
        self.title = title
        self.blocks = []
        self.cfg = cfg
        self.rng = rng
        self.items = items
        self._n = 0
        for b in blocks:
            self.add(b)
        self.place_items()

    def add(self, b, at=None):
        self._n += 1
        b = dict(b)
        b["bid"] = f"b{self.num}_{self._n}"
        if at is None:
            self.blocks.append(b)
        else:
            self.blocks.insert(at, b)
        return b

    def place_items(self):
        pinned = {b["id"] for b in self.blocks if b["t"] == "pin"}
        paras = [i for i, b in enumerate(self.blocks) if b["t"] == "para"]
        side = 0
        self.pending = []   # page-level items: (item, anchor_bid)
        # replace pins
        for i, b in enumerate(list(self.blocks)):
            if b["t"] == "pin":
                it = next((x for x in self.items if x["id"] == b["id"]), None)
                if it is None:
                    b["t"] = "skip"
                    continue
                self._attach(it, self.blocks.index(b), side)
                side += 1
        for it in self.items:
            if it["id"] in pinned or it["type"] in ("opener", "vignette"):
                continue
            pos = float(it["position"] or 0.5)
            k = paras[min(len(paras) - 1, max(1, int(round(pos * (len(paras) - 1)))))]
            self._attach(it, self.blocks.index(next(b for b in self.blocks if b is self.blocks[k])), side)
            side += 1
            paras = [i for i, b in enumerate(self.blocks) if b["t"] == "para"]

    def _attach(self, it, idx, side):
        t = it["type"]
        if t == "inset":
            self.add({"t": "inset", "item": it, "side": "right" if side % 2 == 0 else "left"}, at=idx)
        elif t in ("plate", "spread", "half", "map"):
            # anchor = the paragraph at idx (or next para)
            j = idx
            while j < len(self.blocks) and self.blocks[j]["t"] != "para":
                j += 1
            j = min(j, len(self.blocks) - 1)
            if self.blocks[idx]["t"] == "pin":
                self.blocks[idx]["t"] = "skip"
            self.pending.append((it, self.blocks[j]["bid"]))

    # ------------------------------------------------------------ rendering
    def html(self, proxy=True):
        cfg = self.cfg
        out = [f'<section class="chapter" id="ch{self.num}">']
        hdr = os.path.join(ART, "png", f"header_{self.num:02d}.png")
        out.append('<div class="opener">' + img_or_proxy(hdr if os.path.exists(hdr) else None, 5.5, 2.0, "hdr", proxy)
                   + f'<div class="chapnum">Chapter {NUMERALS[self.num - 1]}</div><h1>{html.escape(self.title)}</h1></div>')
        first_para_done = False
        italic = False
        tail = (f'<div class="tail" id="b{self.num}_tail">' +
                img_or_proxy(os.path.join(ART, "png", "orn_tailpiece.png"), 2.4, 0.7, "", proxy) + "</div>")
        tail_done = False
        for b in self.blocks:
            t = b["t"]
            bid = b["bid"]
            if b.get("after_tail") and not tail_done:
                out.append(tail)
                tail_done = True
            if t == "para":
                toks = b["tokens"]
                cls = b.get("cls", "")
                if not first_para_done and not b.get("cont"):
                    first_para_done = True
                    word = toks[0].lstrip("\u201c\u2018\"'")
                    letter = word[0].upper() if word else "A"
                    rest = word[1:]
                    dc = os.path.join(ART, "png", f"dropcap_{letter}.png")
                    dch = img_or_proxy(dc if os.path.exists(dc) else None, 0.86, 0.86, "dropcap", proxy, letter)
                    if proxy:
                        dch = '<div class="dropcap proxy"></div>'
                    first_html, italic = inline_html([rest] + toks[1:3], italic)
                    rest_html, italic = inline_html(toks[3:], italic)
                    out.append(f'<p id="{bid}" class="first {cls}">{dch}<span class="sc">{first_html}</span> {rest_html}</p>')
                    continue
                if b.get("cont"):
                    cls += " cont"
                h, italic = inline_html(toks, b.get("italic_in", False))
                italic = False
                out.append(f'<p id="{bid}" class="{cls.strip()}">{h}</p>')
            elif t == "verse":
                lines = "".join(f"<p>{html.escape(l)}</p>" for l in b["lines"])
                out.append(f'<div class="verse" id="{bid}">{lines}</div>')
            elif t == "break":
                orn = os.path.join(ART, "png", "orn_section.png")
                out.append(f'<div class="sbreak" id="{bid}">{img_or_proxy(orn, 1.1, 0.32, "", proxy)}</div>')
            elif t == "note":
                out.append(f'<p class="note" id="{bid}">Placeholder text. Replace with the chapter text from your public-domain '
                           f'source edition (see docs/05-text-preparation.md) and rebuild; illustrations re-flow automatically.</p>')
            elif t == "inset":
                it = b["item"]
                p = art_path(it)
                inner = (img_or_proxy(p, 2.45, 2.45, "", proxy) if p else
                         placeholder_box(it, 2.45, 2.45, "inset", cfg.get("show_placeholder_briefs", True)))
                out.append(f'<figure class="inset {b["side"]}" id="{bid}">{inner}</figure>')
            elif t == "half":
                it = b["item"]
                p = art_path(it)
                emblem = os.path.join(ART, "png", f"emblem_{self.num:02d}.png")
                inner = (img_or_proxy(p, 5.5, 4.0, "", proxy) if p else
                         placeholder_box(it, 5.5, 3.9, "half", cfg.get("show_placeholder_briefs", True), emblem))
                out.append(f'<figure class="half" id="{bid}">{inner}</figure>')
            elif t in ("plate", "spreadL", "spreadR"):
                out.append(plate_html(b, self.num, proxy, cfg))
        if not tail_done:
            out.append(tail)
        out.append("</section>")
        return "\n".join(out)

    def plate_names(self):
        res = []
        for b in self.blocks:
            if b["t"] in ("plate", "spreadL", "spreadR") and b.get("path"):
                kind = "plate" if b["t"] == "plate" else b["t"]
                res.append((b["page_name"], b["path"], kind))
        return res


def plate_html(b, chnum, proxy, cfg):
    it = b["item"]
    name = b["page_name"]
    if b.get("path"):
        return f'<div class="plate" id="{b["bid"]}" style="page:{name};height:{TEXT_H}in"></div>'
    emblem = os.path.join(ART, "png", f"emblem_{chnum:02d}.png") if chnum else None
    side = {"plate": "", "spreadL": " — left page", "spreadR": " — right page"}[b["t"]]
    kind = "plate" if b["t"] == "plate" else ("map" if it["type"] == "map" else "spread")
    ph = placeholder_box(dict(it, title=it["title"] + side), 5.5, 8.4, kind, cfg.get("show_placeholder_briefs", True),
                         emblem if os.path.exists(emblem or "") else None)
    return f'<div class="plate ph-page" id="{b["bid"]}" style="page:plate"><div class="platebox" style="height:{TRIM_H}in">{ph}</div></div>'


def page_level_blocks(ch, it):
    """Blocks that represent a page-level item."""
    p = art_path(it)
    base = re.sub(r"[^A-Za-z0-9]", "_", it["id"])
    if it["type"] in ("plate",):
        return [{"t": "plate", "item": it, "path": p, "page_name": f"pl_{base}"}]
    if it["type"] in ("spread", "map"):
        if p:
            from PIL import Image
            with Image.open(p) as im:
                landscape = im.width > im.height
        else:
            landscape = False
        if p and landscape:
            return [{"t": "spreadL", "item": it, "path": p, "page_name": f"sl_{base}"},
                    {"t": "spreadR", "item": it, "path": p, "page_name": f"sr_{base}"}]
        if p:   # portrait style study standing in for a spread: show it left, placeholder right
            return [{"t": "plate", "item": it, "path": p, "page_name": f"pl_{base}"},
                    {"t": "spreadR", "item": it, "path": None, "page_name": f"sr_{base}"}]
        return [{"t": "spreadL", "item": it, "path": None, "page_name": f"sl_{base}"},
                {"t": "spreadR", "item": it, "path": None, "page_name": f"sr_{base}"}]
    if it["type"] == "half":
        return [{"t": "half", "item": it}]
    raise ValueError(it["type"])


# ======================================================= layout inspection
def walk(box, out):
    out.append(box)
    for c in getattr(box, "children", None) or []:
        walk(c, out)
    return out


def page_blocks(doc):
    """For each page: ordered list of (bid, box) for our top-level blocks."""
    res = []
    for pg in doc.pages:
        seen = []
        for bx in walk(pg._page_box, []):
            el = getattr(bx, "element", None)
            if el is None or type(bx).__name__ in ("TextBox", "LineBox", "InlineBox"):
                continue
            i = el.get("id") or ""
            if i.startswith("b") and "_" in i and (not seen or seen[-1][0] != i):
                if i not in [s[0] for s in seen]:
                    seen.append((i, bx))
        res.append(seen)
    return res


def words_on_page(block_box):
    """Count whole words of a paragraph box on one page; also whether the last one is hyphen-split."""
    lines = []
    for ln in block_box.children:
        if type(ln).__name__ != "LineBox":
            continue
        parts = []
        for b in walk(ln, []):
            if type(b).__name__ == "TextBox":
                el = b.element
                if el is not None and "dropcap" in (el.get("class") or ""):
                    continue
                parts.append(b.text)
        lines.append("".join(parts))
    text = ""
    for i, l in enumerate(lines):
        l2 = l.rstrip()
        if l2.endswith("\u2010") or (l2.endswith("-") and not l2.endswith("--") and i < len(lines) - 1 and False):
            text += l2[:-1]
        else:
            text += l2 + " "
    words = text.split()
    partial = bool(lines) and lines[-1].rstrip().endswith("\u2010")
    return len(words) - (1 if partial else 0)


def render_doc(body, css, base=ROOT):
    return HTML(string=f"<html lang='en'><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>",
                base_url=base).render()


def layout_chapter(ch, css_fn, log):
    """Insert page-level items at page boundaries, then fix inset gaps."""
    for it, anchor in ch.pending:
        kind = it["type"]
        for attempt in range(4):
            doc = render_doc(ch.html(proxy=True), css_fn([]))
            pb = page_blocks(doc)
            L = len(pb) - 1
            page_of = {}
            for pi, blist in enumerate(pb):
                for bid, _ in blist:
                    page_of.setdefault(bid, pi)
            t = page_of.get(anchor, 0) + attempt
            if kind in ("spread", "map"):
                if t % 2 == 1:
                    t += 1
                if t > L:
                    t = L if L % 2 == 0 else L - 1
            elif kind == "half":
                t = min(t, max(0, L - 1))
            else:
                t = min(t, L)
            t = max(0, t)
            blist = pb[t]
            if not blist:
                continue
            last_bid, last_box = blist[-1]
            if last_bid.endswith("_tail"):
                for nb in page_level_blocks(ch, it):
                    nb["after_tail"] = True
                    ch.add(nb, at=len(ch.blocks))
                break
            continues = t + 1 <= L and any(b == last_bid for b, _ in pb[t + 1])
            idx = next(i for i, b in enumerate(ch.blocks) if b["bid"] == last_bid)
            blk = ch.blocks[idx]
            if not continues:
                ins = idx + 1
            elif blk["t"] == "para":
                k = words_on_page(last_box)
                toks = blk["tokens"]
                if k <= 0 or k >= len(toks):
                    ins = idx + (1 if k >= len(toks) else 0)
                else:
                    a = dict(blk, tokens=toks[:k], cls=(blk.get("cls", "") + " split").strip())
                    bb = dict(blk, tokens=toks[k:], cont=True, cls="")
                    bb["italic_in"] = inline_html(toks[:k])[1]
                    ch.blocks[idx] = a
                    ch.add(bb, at=idx + 1)
                    ins = idx + 1
            else:
                continue  # verse/figure straddles the page: try the next page
            for k2, nb in enumerate(page_level_blocks(ch, it)):
                ch.add(nb, at=ins + k2)
            break
        else:
            log(f"  ! could not place {it['id']} cleanly; appended at chapter end")
            for nb in page_level_blocks(ch, it):
                nb["after_tail"] = True
                ch.add(nb, at=len(ch.blocks))
    # inset gap fixing: an inset that does not fit pushes itself and the following text to the next page
    for _ in range(8):
        doc = render_doc(ch.html(proxy=True), css_fn([]))
        pb = page_blocks(doc)
        moved = False
        for pi in range(1, len(pb)):
            if not pb[pi]:
                continue
            first_bid = pb[pi][0][0]
            blk = next((b for b in ch.blocks if b["bid"] == first_bid), None)
            if blk is None or blk["t"] != "inset":
                continue
            # previous page: how far down does content go?
            prev = pb[pi - 1]
            if not prev:
                continue
            bottom = max(bx.position_y + bx.height for _, bx in prev)
            page_h = doc.pages[pi - 1]._page_box.margin_height()
            if page_h - bottom > (BOTTOM + 0.6) * 96:
                i = ch.blocks.index(blk)
                # move it after the next paragraph
                j = i + 1
                while j < len(ch.blocks) and ch.blocks[j]["t"] != "para":
                    j += 1
                if j < len(ch.blocks):
                    ch.blocks.insert(j, ch.blocks.pop(i))
                    moved = True
                    break
        if not moved:
            break
    return ch


# ============================================================ front & back
def front_matter(cfg, chapters, plates_list, proxy):
    a = lambda n: os.path.join(ART, "png", n)  # noqa: E731
    t = html.escape
    out = ['<section class="front">']
    out.append(f'<div class="fm halftitle"><div class="t">{t(cfg["title"])}</div>'
               f'<img src="{file_url(a("orn_corner.png"))}"/></div>')
    out.append("FRONTISPIECE")
    out.append(f'<div class="fm titlepage"><div class="t">{t(cfg["title"])}</div><div class="st">{t(cfg["subtitle"])}</div>'
               f'<div class="au">by {t(cfg["author"])}</div><img src="{file_url(a("emblem_19.png"))}"/>'
               f'<div class="il">with illustrations by {t(cfg["illustrator"])}</div>'
               f'<div class="pub">{t(cfg["publisher"])} · {t(cfg["city"])}</div></div>')
    isbns = "<br/>".join(f"ISBN {v} ({k})" for k, v in cfg["isbn"].items())
    out.append(f'''<div class="fm copyright"><img src="{file_url(a("critter_01.png"))}"/>
<p><em>{t(cfg["title"])}, {t(cfg["subtitle"])}</em> by {t(cfg["author"])} was first published in 1937. The text of this
edition follows {t(cfg["text_source"])}. It is in the public domain in {t(cfg["territories"])} and in other countries where the
term of copyright is the author's life plus fifty years. It remains in copyright in many other countries.</p>
<p><strong>For sale only in {t(cfg["territories"])}.</strong> Not for export.</p>
<p>Illustrations, decorations, cover, book design and all new editorial material © {t(cfg["year"])} {t(cfg["illustrator"])}.
All rights reserved. No part of the new material may be reproduced without written permission.</p>
<p>This illustrated edition is independent. It is not authorised, sponsored or endorsed by the Tolkien Estate,
HarperCollins, Middle-earth Enterprises, or the makers of any film or other adaptation.</p>
<p>First published in {t(cfg["year"])} by {t(cfg["publisher"])}, {t(cfg["city"])}.</p>
<p>{isbns}</p>
<p>A catalogue record for this book is available from the National Library of New Zealand.</p>
<p>Typeset in EB Garamond and IM Fell (SIL Open Font Licence). Printed by {t(cfg["printer"])}.</p></div>''')
    out.append(f'<div class="fm dedication">{t(cfg["dedication"])}<br/><img src="{file_url(a("orn_section.png"))}"/></div>')
    # contents
    toc = "".join(f'<a href="#ch{c.num}"><span class="n">{NUMERALS[c.num - 1]}</span>{t(c.title)}</a>' for c in chapters)
    out.append(f'<div class="fm listpage"><img class="orn" src="{file_url(a("orn_tailpiece.png"))}"/><h2>Contents</h2>'
               f'<div class="toc">{toc}</div></div>')
    loi = "".join(f'<a href="#{bid}"><span class="n">{t(iid)}</span>{t(title)}</a>' for iid, title, bid in plates_list)
    out.append(f'<div class="fm listpage loi"><img class="orn" src="{file_url(a("orn_tailpiece.png"))}"/>'
               f'<h2>Plates &amp; Cutaways</h2><div class="toc">{loi}</div></div>')
    out.append(f'''<div class="fm prose"><h2>A Note on this Edition</h2>
<p>[Write a short note here: which printing you transcribed, any silent corrections you made, and why you wanted to
illustrate the story this way. Keep it in your own words; do not reproduce forewords or notes from other editions.]</p>
<p>[An optional paragraph for young readers: there is a small brown snail hidden in every big picture. Can you find them all?
The answers are at the back of the book.]</p>
<p style="text-align:center;margin-top:0.25in"><img src="{file_url(a("half_pantry_vignette.png"))}" style="width:5.5in;height:4in"/></p></div>''')
    out.append("MAPSPREAD")
    out.append("</section>")
    return "\n".join(out)


def back_matter(cfg, items, proxy):
    a = lambda n: os.path.join(ART, "png", n)  # noqa: E731
    out = ['<section class="back">']
    snail = next((i for i in items if i["id"] == "BM-P1"), None)
    if snail:
        out.append(f'<div class="fm prose"><h2>Did you find the snail?</h2>'
                   + placeholder_box(snail, 5.5, 6.6, "plate", True, a("critter_01.png")) + "</div>")
    out.append(f'''<div class="fm prose"><h2>About the Illustrator</h2>
<p>[A short biography, your working method (pen and watercolour on cotton paper, for example) and where readers can
find more of your work.]</p><p style="text-align:center"><img src="{file_url(a("critter_06.png"))}" style="width:0.9in;height:0.7in"/></p></div>''')
    out.append(f'<div class="fm end">The End<br/><img src="{file_url(a("orn_tailpiece.png"))}" style="width:2.4in;height:0.7in"/></div>')
    out.append("</section>")
    return "\n".join(out)


# ================================================================== stamping
def stamp_pages(pdf_path, mode, n_front, critters, emblems, report, starts=()):
    """Give every art-less page something to look at."""
    import pymupdf
    doc = pymupdf.open(pdf_path)
    b = BLEED if mode == "print" else 0.0
    rng = random.Random(7)
    last = None
    stamped = blanks = 0
    for i, page in enumerate(doc):
        imgs = page.get_image_info()
        text = page.get_text().strip()
        pw = page.rect.width
        ph = page.rect.height
        is_left = (i % 2 == 1)  # page index 0 is a right-hand page
        if not imgs and not text:
            # blank page -> centred vignette
            nxt = [c for c, pi in starts if pi > i]
            prv = [c for c, pi in starts if pi <= i]
            chn = nxt[0] if nxt else (prv[-1] if prv else 19)
            em = os.path.join(ART, "png", f"emblem_{chn:02d}.png")
            if not os.path.exists(em):
                em = emblems[i % len(emblems)]
            s = 1.6 * 72
            r = pymupdf.Rect(pw / 2 - s / 2, ph / 2 - s / 2, pw / 2 + s / 2, ph / 2 + s / 2)
            page.insert_image(r, filename=em)
            blanks += 1
            continue
        has_art = any((im["bbox"][2] - im["bbox"][0]) > 72 * 1.2 for im in imgs) or "inset spot" in text.lower()
        if i < n_front or has_art:
            continue
        choices = [c for c in critters if c != last]
        c = rng.choice(choices)
        last = c
        w, h = 0.8 * 72, 0.62 * 72
        y1 = ph - (b + 0.18) * 72
        if is_left:
            x0 = (b + OUTER - 0.35) * 72
        else:
            x0 = pw - (b + OUTER - 0.35) * 72 - w
        page.insert_image(pymupdf.Rect(x0, y1 - h, x0 + w, y1), filename=c)
        stamped += 1
    doc.save(pdf_path + ".tmp", garbage=3, deflate=True)
    doc.close()
    os.replace(pdf_path + ".tmp", pdf_path)
    report["stamped_" + mode] = stamped
    report["blanks_" + mode] = blanks


# ===================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="1-19")
    ap.add_argument("--scale", type=float, default=None, help="placeholder text length factor")
    ap.add_argument("--only", choices=["print", "screen"], default=None)
    args = ap.parse_args()
    t0 = time.time()
    log = print
    cfg = json.load(open(os.path.join(ROOT, "book", "book.json")))
    scale = args.scale if args.scale is not None else cfg.get("placeholder_scale", 1.0)
    chapters_meta = load_csv(os.path.join(ROOT, "plan", "chapters.csv"))
    items = load_csv(os.path.join(ROOT, "plan", "illustrations.csv"))
    lo, hi = (int(x) for x in args.chapters.split("-")) if "-" in args.chapters else (int(args.chapters),) * 2
    os.makedirs(OUT, exist_ok=True)

    base_css = font_css() + BODY_CSS
    chapters = []
    text_status = {}
    for meta in chapters_meta:
        n = int(meta["chapter"])
        if not lo <= n <= hi:
            continue
        rng = random.Random(1000 + n)
        path = os.path.join(ROOT, "book", "text", f"{n:02d}.md")
        if os.path.exists(path):
            title, blocks = parse_text(open(path, encoding="utf-8").read())
            title = title or meta["title"]
            text_status[n] = "your text"
        else:
            title = meta["title"]
            blocks = placeholder_text(n, int(int(meta["est_words"]) * scale), rng)
            text_status[n] = "placeholder"
        ch_items = [i for i in items if i["chapter"] == str(n)]
        ch = Chapter(n, title, blocks, ch_items, rng, cfg)
        log(f"chapter {n:2d}: {len(ch.pending)} page-level items, laying out ...")
        layout_chapter(ch, lambda pl: page_css("screen", pl, cfg) + base_css, log)
        chapters.append(ch)

    # front matter plates: frontispiece, map spread
    fm_items = {i["id"]: i for i in items if i["chapter"] == "0"}
    front_blocks = []
    fp = fm_items.get("FM-P1")
    mp = fm_items.get("FM-M1")
    n_plate = 0

    def mk(it, kind_blocks, prefix):
        out = []
        for k, b in enumerate(kind_blocks):
            b = dict(b)
            b["bid"] = f"bfm_{prefix}{k}"
            out.append(b)
        return out

    fp_blocks = mk(fp, page_level_blocks(None, fp), "fp") if fp else []
    map_blocks = mk(mp, page_level_blocks(None, mp), "map") if mp else []

    # list of plates & spreads
    plates_list = []
    for b in fp_blocks[:1]:
        plates_list.append((fp["id"], fp["title"], b["bid"]))
    for ch in chapters:
        seen = set()
        for b in ch.blocks:
            if b["t"] in ("plate", "spreadL") and b["item"]["id"] not in seen:
                seen.add(b["item"]["id"])
                plates_list.append((b["item"]["id"], b["item"]["title"], b["bid"]))

    def assemble(mode, proxy=False):
        fm = front_matter(cfg, chapters, plates_list, proxy)
        fm = fm.replace("FRONTISPIECE", "".join(plate_html(b, 1, proxy, cfg) for b in fp_blocks))
        # the map spread must open on a left page: pad with a blank page if needed (handled by break-before:left)
        mp_html = "".join(plate_html(b, 0, proxy, cfg) for b in map_blocks)
        mp_html = mp_html.replace('class="plate', 'style="break-before:left" class="plate', 1)
        fm = fm.replace("MAPSPREAD", mp_html)
        body = (fm + '<div class="bodymatter">' + "".join(c.html(proxy) for c in chapters) + "</div>"
                + back_matter(cfg, items, proxy))
        plates = []
        for b in fp_blocks + map_blocks:
            if b.get("path"):
                plates.append((b["page_name"], b["path"], "plate" if b["t"] == "plate" else b["t"]))
        for c in chapters:
            plates += c.plate_names()
        css = page_css(mode, plates, cfg) + base_css
        return body, css

    report = {"chapters": [], "text": text_status}
    modes = [args.only] if args.only else ["print", "screen"]
    for mode in modes:
        body, css = assemble(mode)
        log(f"rendering {mode} PDF ...")
        doc = render_doc(body, css)
        path = os.path.join(OUT, f"interior-{mode}.pdf")
        doc.write_pdf(path)
        report["pages_" + mode] = len(doc.pages)
        # front matter page count = pages before chapter 1
        n_front = 0
        for pi, pg in enumerate(doc.pages):
            ids = [bx.element.get("id") for bx in walk(pg._page_box, []) if getattr(bx, "element", None) is not None]
            if f"ch{chapters[0].num}" in ids:
                n_front = pi
                break
        report["front_pages"] = n_front
        # chapter page ranges (printed folios)
        starts = []
        for c in chapters:
            for pi, pg in enumerate(doc.pages):
                ids = {bx.element.get("id") for bx in walk(pg._page_box, []) if getattr(bx, "element", None) is not None}
                if f"ch{c.num}" in ids:
                    starts.append((c.num, pi))
                    break
        report["chapter_starts"] = starts
        critters = sorted(os.path.join(ART, "png", f) for f in os.listdir(os.path.join(ART, "png")) if f.startswith("critter_"))
        emblems = sorted(os.path.join(ART, "png", f) for f in os.listdir(os.path.join(ART, "png")) if f.startswith("emblem_"))
        stamp_pages(path, mode, n_front, critters, emblems, report, starts)
        log(f"  {path}: {len(doc.pages)} pages")
    write_report(report, chapters, items, cfg, time.time() - t0)
    log(f"done in {time.time() - t0:.0f}s")


def write_report(rep, chapters, items, cfg, secs):
    n = rep.get("pages_print") or rep.get("pages_screen")
    lines = ["# Build report", "", f"Built {time.strftime('%Y-%m-%d %H:%M')} in {secs:.0f}s.", "",
             f"- **Total pages (print interior): {n}**",
             f"- Front-matter pages (roman): {rep.get('front_pages')}",
             f"- Pages given a margin critter (no other art): {rep.get('stamped_print', rep.get('stamped_screen'))}",
             f"- Blank pages given a vignette: {rep.get('blanks_print', rep.get('blanks_screen'))}", ""]
    placeholder = [k for k, v in rep["text"].items() if v == "placeholder"]
    if placeholder:
        lines += [f"> Chapters {', '.join(map(str, placeholder))} use **placeholder text** sized from planning word counts, "
                  "so page counts are estimates until your text is in `book/text/`.", ""]
    lines += ["## Chapters", "", "| Ch | Title | Starts on PDF page | Text | Plates | Spreads | Half | Inset |",
              "|---|---|---|---|---|---|---|---|"]
    starts = dict(rep.get("chapter_starts", []))
    for c in chapters:
        ci = [i for i in items if i["chapter"] == str(c.num)]
        cnt = lambda t: sum(1 for i in ci if i["type"] == t)  # noqa: E731
        lines.append(f"| {NUMERALS[c.num - 1]} | {c.title} | {starts.get(c.num, 0) + 1} | {rep['text'][c.num]} | "
                     f"{cnt('plate')} | {cnt('spread')} | {cnt('half')} | {cnt('inset')} |")
    done = sum(1 for i in items if art_path(i) and i["status"] != "planned")
    finals = sum(1 for i in items if os.path.exists(os.path.join(ART, "final", i["id"] + ".png")))
    lines += ["", "## Art status", "", f"- Planned illustrations in `plan/illustrations.csv`: {len(items)}",
              f"- With style-study art: {done}", f"- With final art in `art/final/`: {finals}", "",
              "## Spine width estimates", "",
              "Use the printer's own calculator before you send files. These are rules of thumb for white paper.", "",
              "| Printer / paper | inch per page | Spine (in) |", "|---|---|---|"]
    for name, k in (("KDP premium colour", 0.002347), ("KDP standard colour", 0.002252), ("IngramSpark colour 70lb (approx.)", 0.0025)):
        lines.append(f"| {name} | {k} | {n * k:.3f} |")
    with open(os.path.join(OUT, "build-report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(OUT, "build-report.json"), "w") as f:
        json.dump({"pages": n, **{k: v for k, v in rep.items() if k != "text"}}, f, indent=1)


if __name__ == "__main__":
    main()
