"""Render PDF pages as a contact sheet: pdf_thumbs.py in.pdf out.png first last [cols] [width_px]"""
import sys, pymupdf
from PIL import Image, ImageDraw
pdf, out, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 6
W = int(sys.argv[6]) if len(sys.argv) > 6 else 260
doc = pymupdf.open(pdf)
ims = []
for i in range(a - 1, min(b, len(doc))):
    pg = doc[i]
    zoom = W / pg.rect.width
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    ims.append((i + 1, Image.frombytes("RGB", (pix.width, pix.height), pix.samples)))
h = max(im.height for _, im in ims) + 16
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 8), rows * h), "#777")
d = ImageDraw.Draw(sheet)
for k, (n, im) in enumerate(ims):
    x, y = (k % cols) * (W + 8), (k // cols) * h
    sheet.paste(im, (x, y))
    d.text((x + 4, y + im.height + 2), f"p{n}", fill="white")
sheet.save(out)
print(out, sheet.size)
