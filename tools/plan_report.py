#!/usr/bin/env python3
"""Regenerate docs/03-illustration-plan.md from plan/*.csv and output/build-report.json."""
import collections
import csv
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NUM = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII",
       "XVIII", "XIX"]
TYPE_NAME = {"opener": "Opener", "plate": "Plate", "spread": "Cutaway spread", "half": "Half-page", "inset": "Inset",
             "vignette": "Tailpiece", "map": "Map"}


def main():
    items = list(csv.DictReader(open(os.path.join(ROOT, "plan", "illustrations.csv"))))
    chapters = list(csv.DictReader(open(os.path.join(ROOT, "plan", "chapters.csv"))))
    rep_path = os.path.join(ROOT, "output", "build-report.json")
    rep = json.load(open(rep_path)) if os.path.exists(rep_path) else {}
    cnt = collections.Counter(i["type"] for i in items)
    pri = collections.Counter(i["priority"] for i in items)
    styl = sum(1 for i in items if i["status"] == "style-study")
    pages = rep.get("pages", "?")
    starts = dict((c, p) for c, p in rep.get("chapter_starts", []))

    L = ["# 3 · Illustration plan", "",
         "The editable source of truth is **`plan/illustrations.csv`**: open it in any spreadsheet. The build reads it directly, "
         "and this page is regenerated from it by `python3 tools/plan_report.py`.", "",
         "## 3.1 How every page turn gets a picture", "",
         "| Layer | Count | What it does |", "|---|---|---|",
         f"| Cutaway spreads (S) | {cnt['spread']} | The showpieces: double-page cross-sections of the key places |",
         f"| Full-page plates (P) | {cnt['plate']} | One to three per chapter, at the big story moments |",
         f"| Half-page pictures (H) | {cnt['half']} | The top of a text page, roughly every 6–8 pages |",
         f"| Inset spots (I) | {cnt['inset']} | Small pictures with text wrapping around them |",
         f"| Chapter openers (O) | {cnt['opener']} | A bramble banner with an emblem roundel, plus an illuminated drop cap (**all drafted**) |",
         f"| Tailpieces (V) | {cnt['vignette']} | A bramble sprig closing each chapter (**drafted**) |",
         "| Margin critters (M) | 13 drafted, aim for about 40 | Stamped automatically on any page that has no other art |",
         "| Blank-page vignettes | automatic | Blank versos before chapter openings show the next chapter's emblem |", "",
         f"In the current dummy ({pages} pages), every page that has no planned art gets a margin critter "
         f"({rep.get('stamped_print', '?')} pages) and every blank page gets a vignette ({rep.get('blanks_print', '?')}). "
         "So **no page is ever without a picture**. To make the critter pages richer, add more insets to the CSV; the layout "
         "absorbs them automatically.", "",
         f"**Totals:** {len(items)} planned pieces (priority A: {pri['A']}, B: {pri['B']}, C: {pri['C']}). "
         f"{styl} are already drafted as style studies in `art/png/`.", "",
         "**Priorities:**", "",
         "- **A** is essential for launch.",
         "- **B** strongly wanted.",
         "- **C** can be phased into a later printing; until then a margin critter takes its place.", "",
         "## 3.2 The big cutaways", "",
         "These are the pages people will buy the book for. Each one gets a full research pass: how the room would really be "
         "built, lit, heated and stocked.", ""]
    for i in items:
        if i["type"] == "spread":
            L.append(f"- **{i['id']}: {i['title']}.** {i['brief']}")
    L += ["", "## 3.3 Chapter by chapter", ""]
    for c in chapters:
        n = c["chapter"]
        ci = [i for i in items if i["chapter"] == n]
        pg = ""
        if starts:
            nxt = starts.get(int(n) + 1, pages if isinstance(pages, int) else None)
            if nxt and int(n) in starts:
                pg = f" · about {nxt - starts[int(n)]} pages in the dummy"
        L += [f"### {NUM[int(n)]}. {c['title']}", "",
              f"*About {int(c['est_words']):,} words{pg} · palette: {c['palette']}*", "",
              "| ID | Type | Where | Title | Brief | Pri | Status |", "|---|---|---|---|---|---|---|"]
        for i in ci:
            where = f"{float(i['position']):.0%}" if i["type"] not in ("opener", "vignette") else ("start" if i["type"] == "opener" else "end")
            L.append(f"| {i['id']} | {TYPE_NAME[i['type']]} | {where} | {i['title']} | {i['brief']} | {i['priority']} | {i['status']} |")
        L.append("")
    L += ["### Front and back matter", "", "| ID | Type | Title | Brief | Pri | Status |", "|---|---|---|---|---|---|"]
    for i in items:
        if i["chapter"] in ("0", "99"):
            L.append(f"| {i['id']} | {TYPE_NAME[i['type']]} | {i['title']} | {i['brief']} | {i['priority']} | {i['status']} |")
    L += ["", "*Word counts are planning estimates (±15%), used only to size the placeholder text. Scene briefs are "
          "summaries written for this plan; they contain no text from the novel.*", ""]
    with open(os.path.join(ROOT, "docs", "03-illustration-plan.md"), "w") as f:
        f.write("\n".join(L))
    print("wrote docs/03-illustration-plan.md")


if __name__ == "__main__":
    main()
