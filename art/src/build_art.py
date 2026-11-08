"""Generate every SVG in the style library and render them to 300 dpi PNGs.

    python3 art/src/build_art.py            # SVG + PNG (300 dpi)
    python3 art/src/build_art.py --svg-only
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import small  # noqa: E402
import scene_burrow  # noqa: E402
import scene_cellar  # noqa: E402
import scene_cover  # noqa: E402

SVG = os.path.join(ROOT, "art", "svg")
NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI",
            "XVII", "XVIII", "XIX"]


def main():
    os.makedirs(SVG, exist_ok=True)
    files = []

    def out(name):
        p = os.path.join(SVG, name)
        files.append(p)
        return p

    scene_burrow.build(out("plate_burrow_cutaway.svg"))
    scene_cellar.build(out("plate_cellar_mechanism.svg"))
    scene_cover.build_front(out("cover_front_art.svg"))
    scene_cover.build_back(out("cover_back_art.svg"))
    for i, num in enumerate(NUMERALS):
        small.chapter_header(out(f"header_{i + 1:02d}.svg"), i, num)
        small.emblem(out(f"emblem_{i + 1:02d}.svg"), i)
    for i in range(len(small.CRITTERS)):
        small.critter(out(f"critter_{i + 1:02d}.svg"), i)
    small.tailpiece(out("orn_tailpiece.svg"))
    small.section_break(out("orn_section.svg"))
    small.corner_vine(out("orn_corner.svg"))
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        small.dropcap(out(f"dropcap_{ch}.svg"), ch, i)
    print(f"wrote {len(files)} SVGs")
    if "--svg-only" not in sys.argv:
        dpi = "300"
        for a in sys.argv:
            if a.startswith("--dpi="):
                dpi = a.split("=")[1]
        subprocess.run(["node", os.path.join(ROOT, "tools", "render.cjs"), "--dpi", dpi] + files, check=True)
        # opaque full-page art -> high-quality JPEG (PNG of watercolour grain is 4-5x larger)
        from PIL import Image
        png_dir = os.path.join(ROOT, "art", "png")
        for name in os.listdir(png_dir):
            if name.startswith(("plate_", "cover_")) and name.endswith(".png"):
                p = os.path.join(png_dir, name)
                Image.open(p).convert("RGB").save(p[:-4] + ".jpg", quality=92, dpi=(int(dpi), int(dpi)), subsampling=0)
                os.remove(p)
                print("jpeg:", name[:-4] + ".jpg")


if __name__ == "__main__":
    main()
