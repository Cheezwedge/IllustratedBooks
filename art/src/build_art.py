"""Paint every piece in the style library with the watercolour engine (art/src/wc.py).

    python3 art/src/build_art.py            # paint everything at 300 dpi (WC_DPI=150 for quick previews)
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
import scene_pantry  # noqa: E402

SVG = os.path.join(ROOT, "art", "png")   # the raster engine writes PNG/JPEG directly
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
    scene_pantry.build(out("half_pantry_vignette.png"))
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
    print(f"painted {len(files)} pieces into art/png/")

if __name__ == "__main__":
    main()
