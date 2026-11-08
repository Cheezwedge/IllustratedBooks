# The Hobbit: an illustrated edition (production kit)

A complete plan and working production pipeline for a **new illustrated edition of *The Hobbit, or There and Back Again***, intended for sale only where the text is in the public domain (New Zealand first). The art direction is cosy and intricate: pen-and-watercolour hedgerow detail, **cutaway views** of burrows, halls, cellars and mechanisms, and **a picture on every page turn**.

> ⚖️ Read **`docs/01-rights-and-territories.md`** before anything else. The book is still in copyright in the US, UK, EU, Australia, Canada and most other places. Trademarks and film designs are separate issues, and *where copies are printed* matters.

## What's here

| | |
|---|---|
| `output/interior-print.pdf` | **Print-ready interior dummy**: 7 × 10 in + 0.125 in bleed, about 407 pages, front and back matter, contents, plates list, every illustration slot laid out |
| `output/interior-screen.pdf` | The same at trim size with cream pages, for proofing and digital sale |
| `output/cover-paperback.pdf` | Wraparound cover (back, spine, front) with the spine sized from the page count; `cover-guides.pdf` shows the guides |
| `output/cover-ebook-front.jpg` | Ebook store cover |
| `output/production-notes.pdf` | **All the planning in one PDF**: rights, art bible, illustration plan, production, text preparation, gallery, sample pages |
| `docs/` | The same planning documents as Markdown |
| `plan/illustrations.csv` | **The illustration plan**: 176 pieces, each with ID, chapter, type, position, brief, priority and status. Edit it in any spreadsheet. |
| `art/png/` | Style-study art at 300 ppi: 2 full-page cutaways, 19 chapter openers and emblems, 13 margin critters, 26 drop caps, ornaments, cover art |
| `art/src/` | The generators for that art (Python to SVG, rendered with Chromium) |
| `book/build.py` | The layout engine (WeasyPrint): places plates and spreads on exact page boundaries, half-pages at page tops, insets with text wrap, critters on any art-less page |
| `book/cover.py` | Cover builder |
| `book/book.json` | Title-page and copyright-page details (imprint, ISBNs, territories, dedication) |

## Two things deliberately left for you

1. **The text of the novel is not included.** You supply it from a legitimate public-domain source in your territory (`docs/05-text-preparation.md`). Until then the dummy uses placeholder Latin, sized to each chapter's length.
2. **The characters are not drawn.** The hobbit, the wizard, the dwarves, the dragon and the rest should be your own designs, and that is also where the risk of resembling the films concentrates. The art bible (§2.6) gives book-based design notes. The style studies cover settings, cutaways, objects and decorations.

## Quick start

Install the Python dependencies:

```bash
pip install weasyprint pymupdf pillow markdown
```

Build the interior (about 2 minutes):

```bash
python3 book/build.py
```

Build the cover (run after the interior, which sets the page count):

```bash
python3 book/cover.py
```

Regenerate the illustration-plan document from the CSV:

```bash
python3 tools/plan_report.py
```

Compile the production-notes PDF:

```bash
python3 tools/notes_pdf.py
```

Re-render the style-study art (needs Node with Playwright and Chromium):

```bash
python3 art/src/build_art.py
```

**Adding finished art:** save it as `art/final/<ID>.png` or `.jpg` (e.g. `art/final/P-05-01.jpg`) at the size given in the art bible §2.8 and rebuild. It replaces the labelled placeholder automatically.

**Adding the text:** save `book/text/01.md` to `book/text/19.md` and rebuild. Every illustration re-flows to its scene.

## Next steps

1. Get an NZ IP lawyer's sign-off and do a trademark search (rights doc §1.4–1.5).
2. Transcribe and proofread the text, then rebuild to get the real page count and cost.
3. Design the characters and lock the colour script.
4. Produce the A-priority art: 35 plates and cutaway spreads.
5. Proof copy from an NZ printer, then launch.
