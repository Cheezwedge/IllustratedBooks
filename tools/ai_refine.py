#!/usr/bin/env python3
"""
AI finishing pass: repaint a style-study render with an image model, keeping its composition.

The code-painted pieces in art/png/ fix the layout (every room, shelf and root where the plan wants
it).  An image model is then asked to repaint that exact composition as a finished pen-and-watercolour
illustration.  Composition from code + finish from the model, then a human paint-over (art bible §2.10).

Provider: Google Gemini API (generativelanguage.googleapis.com), the image-capable Gemini models.
The API key is never stored in this repository: in a Claude Code cloud session it is held by the
environment's network proxy, which injects it into requests; locally, set GEMINI_API_KEY.

    python3 tools/ai_refine.py --list-models
    python3 tools/ai_refine.py --id FM-P1                     # uses the item's style-study render as the guide
    python3 tools/ai_refine.py --id P-05-01 --guide sketch.png --ref chars/hobbit_sheet.png --variants 3
    python3 tools/ai_refine.py --id FM-P1 --dry-run           # show the request without sending it
    python3 tools/ai_refine.py --promote art/ai/FM-P1__v1.png # copy a chosen result into art/final/

Every generation is logged in art/ai/log.csv (model, prompt, guide, time) for AI-content disclosure.
"""
import argparse
import base64
import csv
import datetime
import io
import json
import os
import shutil
import sys
import urllib.error
import urllib.request

from PIL import Image, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
API = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
AI_DIR = os.path.join(ROOT, "art", "ai")

# Style language from docs/02-art-bible.md §2.2 - descriptive only, never an artist's or a series' name.
STYLE = ("fine sepia pen line, soft transparent watercolour washes on warm cream paper, gentle granulation, "
         "colours occasionally escaping the lines, warm natural daylight or golden lamplight, botanically accurate "
         "English hedgerow plants (bramble, dog-rose, honeysuckle, hawthorn, oak, beech, ferns, mushrooms), rounded "
         "cosy architecture, intricate cross-section cutaway where shown, abundant tiny domestic details "
         "(crockery, preserves, baskets, herbs, wood grain), storybook warmth, classic children's book illustration")
AVOID = ("Do not imitate any specific living or dead artist, book series or film. No photorealism, no digital gloss, "
         "no heavy black outlines, no added text, lettering, signatures or watermarks (keep only small labels already "
         "present in the reference). Nothing frightening or gory.")

# final print sizes (inches) by plan type - art bible §2.8
SIZES = {"plate": (7.125, 10.25), "spread": (14.25, 10.25), "map": (14.25, 10.25), "half": (5.5, 4.0),
         "inset": (2.6, 2.6), "opener": (5.5, 2.0), "vignette": (2.4, 0.7)}
RATIOS = {"1:1": 1.0, "2:3": 2 / 3, "3:2": 1.5, "3:4": 0.75, "4:3": 4 / 3, "4:5": 0.8, "5:4": 1.25, "9:16": 9 / 16,
          "16:9": 16 / 9, "21:9": 21 / 9}


def key_header():
    # In a cloud session the proxy replaces this value with the stored credential.
    return os.environ.get("GEMINI_API_KEY", "injected-by-proxy")


def call(path, body=None, method="POST"):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"x-goog-api-key": key_header(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:800]
        raise SystemExit(f"Gemini API error {e.code}: {msg}")


def list_models():
    res = call("/models?pageSize=200", method="GET")
    for m in res.get("models", []):
        name = m["name"].split("/")[-1]
        methods = m.get("supportedGenerationMethods", [])
        if "image" in name or "imagen" in name:
            print(f"{name:45s} {', '.join(methods)}  {m.get('displayName', '')}")


def load_plan():
    with open(os.path.join(ROOT, "plan", "illustrations.csv"), newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def nearest_ratio(w, h):
    r = w / h
    return min(RATIOS, key=lambda k: abs(RATIOS[k] - r))


def png_part(path, max_side=2048):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", im.size, (251, 247, 238))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    im = im.convert("RGB")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(buf.getvalue()).decode()}}


def clean_brief(text):
    """Drop production notes (e.g. 'STYLE STUDY made ...') that are for us, not for the model."""
    import re
    sents = re.split(r"(?<=[.!?])\s+|\s*\(", text)
    keep = [x.strip().rstrip(")") for x in sents if x.strip() and "style study" not in x.lower() and "replace or refine" not in x.lower()]
    return " ".join(keep)


def build_prompt(item, has_guide, n_refs, extra):
    lines = []
    if has_guide:
        lines.append("Repaint the FIRST reference image as a finished illustration for a classic illustrated children's "
                     "book. Keep its composition, viewpoint, layout and the position of every room and object exactly; "
                     "refine, enrich and add small believable details, but do not move or remove anything.")
    else:
        lines.append("Paint a finished illustration for a classic illustrated children's book.")
    if n_refs:
        lines.append(f"The other {n_refs} reference image(s) are character or prop design sheets: keep those designs "
                     "exactly (faces, proportions, clothing colours).")
    title = item["title"].split(":")[-1].strip() if item["title"].lower().startswith(("frontispiece", "cutaway")) else item["title"]
    lines.append(f"Scene: {title}. {clean_brief(item['brief'])}")
    lines.append(f"Style: {STYLE}.")
    lines.append("Include a tiny brown snail hidden somewhere in the picture." if item.get("type") in ("plate", "spread") else "")
    lines.append(AVOID)
    if extra:
        lines.append(extra)
    return " ".join(l for l in lines if l)


def fit_to_print(img, w_in, h_in, dpi=300):
    """Cover-crop to the exact print aspect and resample to 300 dpi (upscaling if the model returned less)."""
    W, H = int(round(w_in * dpi)), int(round(h_in * dpi))
    r = W / H
    iw, ih = img.size
    if iw / ih > r:
        nw = int(ih * r)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / r)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    up = W / img.size[0]
    img = img.resize((W, H), Image.LANCZOS)
    if up > 1.3:
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    return img, up


def generate(args):
    plan = load_plan()
    if args.id in plan:
        item = dict(plan[args.id])
    elif args.guide and args.brief:
        item = {"id": args.id, "type": args.type, "title": args.title or args.id, "brief": args.brief, "file": ""}
    else:
        raise SystemExit(f"unknown id {args.id}; use a plan ID, or give --guide, --brief (and --type/--title) for an ad-hoc piece")
    guide = args.guide or (os.path.join(ROOT, item["file"]) if item.get("file") else None)
    if guide and not os.path.exists(guide):
        guide = None
    w_in, h_in = SIZES.get(item["type"], (7.125, 10.25))
    if guide:
        gw, gh = Image.open(guide).size
        if abs((gw / gh) / (w_in / h_in) - 1) > 0.25:
            print(f"note: the guide is {gw}x{gh} but a {item['type']} is {w_in} x {h_in} in; "
                  f"using the guide's shape (pass --aspect to override)")
            w_in, h_in = (7.125, 10.25) if gh > gw else (14.25, 10.25)
    ratio = args.aspect or nearest_ratio(w_in, h_in)
    prompt = build_prompt(item, bool(guide), len(args.ref), args.extra)
    parts = ([png_part(guide)] if guide else []) + [png_part(p, 1024) for p in args.ref] + [{"text": prompt}]
    gen_cfg = {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": ratio}}
    if args.size:
        gen_cfg["imageConfig"]["imageSize"] = args.size
    body = {"contents": [{"role": "user", "parts": parts}], "generationConfig": gen_cfg}
    print(f"model   {args.model}\nitem    {args.id} ({item['type']}, print {w_in} x {h_in} in, aspect {ratio})\n"
          f"guide   {guide or '(none: text only)'}\nrefs    {args.ref or '-'}\nprompt  {prompt}\n")
    if args.dry_run:
        return
    os.makedirs(AI_DIR, exist_ok=True)
    logp = os.path.join(AI_DIR, "log.csv")
    new_log = not os.path.exists(logp)
    for v in range(1, args.variants + 1):
        res = call(f"/models/{args.model}:generateContent", body)
        imgs = []
        for c in res.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                data = p.get("inlineData") or p.get("inline_data")
                if data:
                    imgs.append(base64.b64decode(data["data"]))
                elif p.get("text"):
                    print("model says:", p["text"][:300])
        if not imgs:
            print(f"variant {v}: no image returned ({json.dumps(res)[:400]})")
            continue
        raw = Image.open(io.BytesIO(imgs[0])).convert("RGB")
        out_raw = os.path.join(AI_DIR, f"{args.id}__v{v}_raw.png")
        raw.save(out_raw)
        fitted, up = fit_to_print(raw, w_in, h_in)
        out = os.path.join(AI_DIR, f"{args.id}__v{v}.png")
        fitted.save(out, dpi=(300, 300))
        print(f"variant {v}: model returned {raw.size[0]}x{raw.size[1]} -> {out} (x{up:.2f} to 300 dpi"
              f"{'; consider a larger --size or an upscaler' if up > 1.6 else ''})")
        with open(logp, "a", newline="") as f:
            w = csv.writer(f)
            if new_log:
                w.writerow(["time", "id", "variant", "model", "guide", "refs", "aspect", "returned_px", "file", "prompt"])
                new_log = False
            w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), args.id, v, args.model, guide or "",
                        ";".join(args.ref), ratio, f"{raw.size[0]}x{raw.size[1]}", os.path.relpath(out, ROOT), prompt])


def promote(path):
    name = os.path.basename(path)
    iid = name.split("__")[0]
    os.makedirs(os.path.join(ROOT, "art", "final"), exist_ok=True)
    dst = os.path.join(ROOT, "art", "final", iid + os.path.splitext(name)[1])
    shutil.copyfile(path, dst)
    print(f"{path} -> {dst}  (rebuild with: python3 book/build.py)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--id", help="illustration ID from plan/illustrations.csv")
    ap.add_argument("--guide", help="composition image (defaults to the item's style-study render)")
    ap.add_argument("--ref", action="append", default=[], help="character/prop reference sheet (repeatable)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--aspect", choices=list(RATIOS), help="override the aspect ratio sent to the model")
    ap.add_argument("--size", help="imageSize for models that support it, e.g. 2K or 4K")
    ap.add_argument("--variants", type=int, default=1)
    ap.add_argument("--extra", default="", help="extra instructions appended to the prompt")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="test that the API key works")
    ap.add_argument("--type", default="half", choices=list(SIZES), help="ad-hoc piece: size class")
    ap.add_argument("--title", help="ad-hoc piece: title")
    ap.add_argument("--brief", help="ad-hoc piece: scene description")
    ap.add_argument("--promote", help="copy a chosen art/ai/<ID>__vN.png into art/final/")
    a = ap.parse_args()
    if a.check:
        res = call("/models?pageSize=200", method="GET")
        img = [m["name"].split("/")[-1] for m in res.get("models", []) if "image" in m["name"]]
        print(f"API key OK: {len(res.get('models', []))} models visible; image-capable: {', '.join(img) or 'none listed'}")
    elif a.list_models:
        list_models()
    elif a.promote:
        promote(a.promote)
    elif a.id:
        generate(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
