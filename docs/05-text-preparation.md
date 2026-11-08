# 5 · Preparing the text

The repository has **no text of the novel** in it. The dummy PDFs use placeholder Latin sized to each chapter's approximate length. You supply the real text from a legitimate public-domain source in your territory (see `01-rights-and-territories.md` §1.3), and the build re-flows every illustration around it automatically.

## 5.1 Source

1. **Choose your edition.** For an "original" edition, use the **1937 first edition** text. If you prefer the familiar wording, use the 1966 third edition. Do not mix them.
2. **Get a pre-1974 printing** you can work from: your own copy, a library copy, or scans you are entitled to use in your territory.
3. **Transcribe or OCR it yourself, then proofread twice** against the printed page, the second time reading aloud. Classic OCR errors to check:
   - "rn" read as "m"
   - "tbe" for "the"
   - lost italics
   - broken hyphenation at line ends
   - dropped song lines
4. **Leave out** anything not in the source printing, and anything written by others: forewords, notes, appendices, modern maps.

## 5.2 File format

Make one file per chapter: `book/text/01.md` to `book/text/19.md`. UTF-8 plain text.

```text
# An Unexpected Party

First paragraph of the chapter. The opening letter becomes the
illuminated drop cap automatically, and the first few words are set
in small caps.

Second paragraph. Use *asterisks* for italics. Straight "quotes" and
'apostrophes' are converted to curly ones; -- becomes an en dash and
--- an em dash.

> A line of a song or poem
> each line starting with ">"
> forms one verse block.

***

The paragraph after a section break.

{{art:H-01-03}}

A line like the one above pins an illustration to that exact spot.
Without pins, illustrations are placed from the 'position' column in
plan/illustrations.csv (0 = chapter start, 1 = chapter end).
```

- Paragraphs are separated by a blank line. Single line breaks inside a paragraph are ignored.
- A `# Title` line overrides the chapter title in `plan/chapters.csv`.
- A chapter without a file keeps using placeholder text, so you can work chapter by chapter.

## 5.3 Rebuild and check

```bash
python3 book/build.py --chapters 1-1
```

```bash
python3 book/build.py
```

```bash
python3 book/cover.py
```

Then:

- Open `output/interior-screen.pdf` and check each plate sits near its scene. If one drifts too far, either adjust `position` in the CSV or add a `{{art:ID}}` pin.
- Re-run `book/cover.py` whenever the page count changes, because the spine width depends on it.
- Read `output/build-report.md` for page counts, art coverage and spine estimates.
