#!/usr/bin/env python3
"""
Set correctly spelled labels into the blank placards of an AI-generated picture.

Image models misspell words, so the style library asks them for EMPTY label boxes. This tool
finds those boxes and types the real words in, so the spelling is always right and can be changed.

    # 1. find the blank placards and write an editable label file (numbered boxes + preview)
    python3 tools/label_placards.py detect art/anchors/U2_three_panel_blank_labels.jpg

    # 2. edit the "text" of each box in the .labels.json file ("|" = line break; "" = leave blank)

    # 3. render the labelled picture (x2 resolution so the type is crisp)
    python3 tools/label_placards.py apply art/anchors/U2_three_panel_blank_labels.jpg

Boxes with "role": "title" use the book's serif (IM Fell English); "label" boxes use a clean
sans-serif (Inter SemiBold) in capitals.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "output", "labelled")
INK = (61, 43, 31)


def detect(path):
    im = np.asarray(Image.open(path).convert("RGB")).astype(float) / 255
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    lum = im.mean(2)
    std = np.sqrt(np.maximum(ndi.uniform_filter(lum ** 2, 5) - ndi.uniform_filter(lum, 5) ** 2, 0))
    cand = ndi.binary_opening((R > 0.91) & (G > 0.85) & (B > 0.70) & (std < 0.035), iterations=2)
    lab, _ = ndi.label(cand)
    H, W = lum.shape
    boxes = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        fill = (lab[sl] == i).sum() / (h * w)
        if 0.035 * W <= w <= 0.4 * W and 0.008 * H <= h <= 0.07 * H and fill > 0.8 and w / h > 1.6:
            boxes.append({"x": int(xs.start), "y": int(ys.start), "w": int(w), "h": int(h)})
    # reading order: by column (thirds of the width), then top to bottom
    boxes.sort(key=lambda b: (int(b["x"] / (W / 3)), b["y"]))
    for k, b in enumerate(boxes):
        b["id"] = k
        b["role"] = "title" if b["w"] > 0.2 * W and b["y"] < 0.1 * H else "label"
        b["text"] = ""
    return boxes


def fit_font(draw, lines, fontfile, box_w, box_h, upper):
    for size in range(int(box_h * 0.8), 5, -1):
        f = ImageFont.truetype(fontfile, size)
        widths = [draw.textlength(l.upper() if upper else l, font=f) for l in lines]
        line_h = size * 1.12
        if max(widths) <= box_w * 0.88 and line_h * len(lines) <= box_h * 0.82:
            return f, size
    return ImageFont.truetype(fontfile, 6), 6


def apply(path, boxes, scale=2):
    im = Image.open(path).convert("RGB")
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for b in boxes:
        text = b.get("text", "").strip()
        if not text:
            continue
        lines = text.split("|")
        x, y, w, h = (b[k] * scale for k in ("x", "y", "w", "h"))
        title = b.get("role") == "title"
        fontfile = os.path.join(FONTS, "IMFellEnglish-400.ttf" if title else "Inter-SemiBold.otf")
        f, size = fit_font(d, lines, fontfile, w, h, upper=not title)
        line_h = size * 1.12
        y0 = y + (h - line_h * len(lines)) / 2 + size * 0.05
        for i, line in enumerate(lines):
            s = line if title else line.upper()
            tw = d.textlength(s, font=f)
            d.text((x + (w - tw) / 2, y0 + i * line_h), s, font=f, fill=INK)
    return im


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("detect", "apply"):
        print(__doc__)
        return
    cmd, path = sys.argv[1], sys.argv[2]
    labels_path = os.path.splitext(path)[0] + ".labels.json"
    os.makedirs(OUT, exist_ok=True)
    if cmd == "detect":
        boxes = detect(path)
        if os.path.exists(labels_path):
            old = {b["id"]: b for b in json.load(open(labels_path))}
            for b in boxes:
                if b["id"] in old:
                    b["text"], b["role"] = old[b["id"]].get("text", ""), old[b["id"]].get("role", b["role"])
        json.dump(boxes, open(labels_path, "w"), indent=1)
        prev = Image.open(path).convert("RGB")
        d = ImageDraw.Draw(prev)
        for b in boxes:
            d.rectangle([b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]], outline="red", width=2)
            d.text((b["x"] + 3, b["y"] + 1), str(b["id"]), fill="red")
        pp = os.path.join(OUT, os.path.basename(os.path.splitext(path)[0]) + "_boxes.png")
        prev.save(pp)
        print(f"{len(boxes)} placards -> {labels_path}\npreview with numbered boxes -> {pp}")
    else:
        boxes = json.load(open(labels_path))
        out = os.path.join(OUT, os.path.basename(os.path.splitext(path)[0]).replace("_blank_labels", "") + "_labelled.png")
        apply(path, boxes).save(out)
        print(f"labelled -> {out}")


if __name__ == "__main__":
    main()
