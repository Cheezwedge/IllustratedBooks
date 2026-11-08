# 4 · Production and publishing

## 4.1 Formats

| Format | Spec | File | Notes |
|---|---|---|---|
| **Paperback** | 7 × 10 in, premium colour interior, white paper, matte cover | `output/interior-print.pdf` + `output/cover-paperback.pdf` | The most affordable print edition. |
| **Hardcover** | 7 × 10 in, case-laminate (printed boards), optional dust jacket | `output/interior-print.pdf` + the printer's hardcover template | The gift edition. The cover needs the printer's own template: wrap and hinge allowances differ from a paperback. |
| **PDF ebook** | 7 × 10 in, cream page tint, no bleed | `output/interior-screen.pdf` | Sell direct (your own shop, geo-restricted) or through PDF-friendly stores. |
| **EPUB ebook** | Reflowable EPUB 3 with images | (next step) | Best for Kindle, Kobo and Apple Books. Text re-flows; plates become full-screen images and insets sit inline. Build this once the text is final. |

## 4.2 Interior specifications (already set in `book/build.py`)

- **Trim:** 7 × 10 in. **Bleed:** 0.125 in on the outside, top and bottom, so the page size with bleed is 7.125 × 10.25 in.
- **Margins from trim:** top 0.75 in; bottom 0.85 in; inside (gutter) 0.875 in; outside 0.625 in.
  - The text block is 5.5 × 8.4 in.
  - The gutter is above KDP's minimum (0.625 in for 301–500 pages, 0.75 in for 501–700).
- **Type:**
  - Body: EB Garamond 13/18.5 pt, justified and hyphenated. A comfortable read-aloud size for ages 7 and up.
  - Display: IM Fell English, IM Fell French Canon and IM Fell English SC.
  - Both are SIL Open Font Licence, embedded and commercially usable. Licences are in `fonts/`.
- **Images:** 300 ppi at final size, RGB. The printer converts to CMYK.
  - Before final upload, ask your printer for their ICC profile and do a soft-proof.
  - Keep total ink below about 300%.
  - Bright greens and violets can shift, so print a proof copy.
- **PDF:** fonts embedded, no crop marks (KDP and IngramSpark both want none). If your printer asks for PDF/X-1a or PDF/X-4, convert the file in Acrobat Pro or with Ghostscript.
- **Front matter** (roman folios, no running heads):
  - half-title
  - frontispiece
  - title page
  - copyright page
  - dedication
  - contents
  - plates and cutaways list
  - note on the edition
  - map spread
- **Back matter:** "Did you find the snail?", about the illustrator, finis.

## 4.3 Page count and cost

The dummy built today is **407 pages** with placeholder text at estimated chapter lengths, a spine of about 0.95 in. Expect ±10% once your real text is in.

Four hundred colour pages printed on demand make an **expensive** book. Get a quote from your printer's calculator before setting a price. Options if it is too dear:

1. **Two volumes:** Part One (Chapters I–IX, about 220 pp) and Part Two (X–XIX, about 190 pp). Each is a comfortable bedtime-reading length.
2. **A short offset run with an NZ printer** (500–1,500 copies). The unit cost drops sharply and it solves the "where is it printed" problem (rights doc §1.5).
3. **Reduce pages:** 12/17 pt body text saves about 8%. Reducing plate count saves pages too, but don't cut the cutaways: they are the book's selling point.

## 4.4 ISBNs and metadata

- Use a separate ISBN for each format (hardback, paperback, EPUB, PDF). NZ ISBNs are free from the National Library of New Zealand. Put them in `book/book.json`; they print on the copyright page.
- **Title field:** *The Hobbit, or There and Back Again (Illustrated)*. Some platforms, KDP included, *require* the "(Illustrated)" tag for a differentiated public-domain edition.
- **Contributors:** J. R. R. Tolkien (author); you (illustrator).
- **Categories:**
  - BISAC JUV037000 (Juvenile Fiction / Fantasy & Magic)
  - JUV001000 (Action & Adventure)
  - FIC009000 (Fiction / Fantasy) for adult collectors
- **Age range:** 7–12 for reading aloud, 9+ for independent reading.
- **Keywords:** illustrated classic, watercolour illustrations, cutaway illustrations, gift edition, read-aloud classic. Avoid "Brambly Hedge", film titles, other illustrators' names and trademarked terms you do not need.
- **Territories:** New Zealand only, plus any other countries your lawyer clears.

## 4.5 Platform notes

| Platform | Territory control | Notes |
|---|---|---|
| **IngramSpark** | Per-market rights and pricing | Reaches NZ booksellers and libraries. Check *where* NZ orders are printed (rights doc §1.5). |
| **Amazon KDP** | Per-country rights | Public-domain policy: illustrated differentiation, "(Illustrated)" in the title, may ask for proof. AI-content disclosure is required. Expect manual review. |
| **Kobo Writing Life** | Per-country | Strong in NZ through retailer partners. |
| **Apple Books** | Per-country | EPUB only. |
| **Your own shop** | You control it | Geo-block downloads and shipping. Sell signed hardcovers here. |
| **Local NZ printer** | — | Best for the physical edition: printing happens in a public-domain territory. |

## 4.6 Production schedule (a realistic outline)

| Phase | What | Rough length |
|---|---|---|
| 0 | IP lawyer review (NZ), trademark search, decide territories | 2–4 weeks |
| 1 | Transcribe and proofread the text, then build the real page count | 3–6 weeks |
| 2 | Character design sheets and colour script, signed off | 4–6 weeks |
| 3 | Art production, priority **A** first (35 plates and spreads; the 19 openers are already drafted) | 6–12 months |
| 4 | Priority **B** and **C** halves and insets (or phase them into a second printing) | runs alongside phase 3 |
| 5 | Layout pass with final art, proofreading in layout, cover final | 3–4 weeks |
| 6 | Printed proof copies, colour check, corrections | 2–4 weeks |
| 7 | Launch: NZ legal deposit, store listings, review copies | — |

## 4.7 Pre-flight checklist

- [ ] Lawyer has confirmed public-domain status and the extension position for every sales territory.
- [ ] Trademark searches done (IPONZ, CIPC). The title treatment is your own lettering, with no film or estate marks.
- [ ] Text comes from a pre-1974 printing, proofread twice, with no modern editorial material.
- [ ] Every illustration is original and checked for resemblance to films and published illustrations. Contracts assign or license worldwide rights.
- [ ] `output/build-report.md` shows no placeholder chapters, and every A-priority item has final art.
- [ ] Copyright page completed: territories, ISBNs, printer, disclaimer.
- [ ] Spine width checked against the printer's calculator, and `book/cover.py --pages N` re-run.
- [ ] Proof copy approved: colour, gutter, plates on the correct sides, nothing important in the gutter of spreads.
- [ ] Platform territories restricted. "For sale only in …" appears on the copyright page and back cover.
- [ ] Legal deposit copies sent to the National Library of New Zealand.
