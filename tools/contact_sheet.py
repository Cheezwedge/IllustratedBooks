"""Make a quick review grid of rendered art. Usage: contact_sheet.py out.png cols cell_w pattern..."""
import sys, glob
from PIL import Image, ImageDraw
out, cols, cell = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
files = []
for p in sys.argv[4:]:
    files += sorted(glob.glob(p))
thumbs = []
for f in files:
    im = Image.open(f).convert("RGBA")
    im.thumbnail((cell, cell))
    thumbs.append((f.split('/')[-1], im))
rows = (len(thumbs) + cols - 1) // cols
H = max(t[1].height for t in thumbs) + 18
sheet = Image.new("RGB", (cols * cell, rows * H), "#fdf8ec")
dr = ImageDraw.Draw(sheet)
for i, (name, im) in enumerate(thumbs):
    x, y = (i % cols) * cell, (i // cols) * H
    sheet.paste(im, (x + (cell - im.width) // 2, y), im)
    dr.text((x + 4, y + H - 15), name, fill="#555")
sheet.save(out)
print(out, sheet.size)
