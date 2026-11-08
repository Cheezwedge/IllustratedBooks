#!/usr/bin/env python3
"""
Local AI finishing pass: the same job as tools/ai_refine.py, but on your own PC with ComfyUI.

The code-painted render is the composition guide.  A local Stable Diffusion XL model repaints it
image-to-image while a ControlNet (edge map of the render) holds every room, shelf and root in
place; an optional second "hires" pass adds detail at a larger size.  The result is fitted to exact
print size at 300 dpi and logged in art/ai/log.csv, exactly like the Gemini tool.

Set-up is in docs/06-local-ai.md.  With ComfyUI running (default http://127.0.0.1:8188):

    python tools/local_refine.py --list                       # checkpoints / controlnets ComfyUI can see
    python tools/local_refine.py --id FM-P1 --ckpt sd_xl_base_1.0.safetensors \
        --controlnet controlnet-canny-sdxl-1.0.safetensors --variants 3
    python tools/local_refine.py --id half-pantry --guide art/png/half_pantry_vignette.png --type half \
        --brief "Close-up of a cosy pantry ..." --ckpt sd_xl_base_1.0.safetensors
    python tools/local_refine.py --id FM-P1 --dry-run         # print the workflow without sending it

Tuning: --denoise (0.35 keeps the drawing closely, 0.6 repaints more freely), --cn-strength (how hard the
layout is held), --steps, --cfg, --seed.  Promote a chosen result with:  python tools/ai_refine.py --promote <file>
"""
import argparse
import csv
import datetime
import io
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
import uuid

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ai_refine as AR  # noqa: E402  (shared plan loading, style language, sizes, print fitting)

NEG = ("photo, photorealistic, 3d render, cgi, glossy digital painting, airbrushed, heavy black outlines, anime, "
       "manga, comic, text, letters, watermark, signature, frame, border, blurry, jpeg artifacts, deformed, "
       "extra limbs, scary, gore, dark horror")
# SDXL-native generation sizes (about one megapixel) by aspect
GEN = {"2:3": (832, 1216), "3:4": (896, 1152), "4:5": (896, 1088), "1:1": (1024, 1024), "4:3": (1152, 896),
       "5:4": (1088, 896), "3:2": (1216, 832), "16:9": (1344, 768), "9:16": (768, 1344), "21:9": (1536, 640)}


def http(server, path, data=None, headers=None, method=None):
    req = urllib.request.Request(server + path, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def upload(server, path):
    """Multipart upload of the guide image to ComfyUI's input folder."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", im.size, (251, 247, 238))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "PNG")
    name = "guide_" + uuid.uuid4().hex[:8] + ".png"
    b = "----illbooks" + uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + buf.getvalue() + \
        f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    res = json.loads(http(server, "/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={b}"}))
    return res["name"]


def workflow(a, image_name, pos, neg, gw, gh, seed):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": a.ckpt}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "5": {"class_type": "ImageScale", "inputs": {"image": ["4", 0], "upscale_method": "lanczos",
                                                     "width": gw, "height": gh, "crop": "center"}},
        "6": {"class_type": "VAEEncode", "inputs": {"pixels": ["5", 0], "vae": ["1", 2]}},
    }
    pos_ref, neg_ref = ["2", 0], ["3", 0]
    if a.controlnet:
        wf["7"] = {"class_type": "ControlNetLoader", "inputs": {"control_net_name": a.controlnet}}
        wf["8"] = {"class_type": "Canny", "inputs": {"image": ["5", 0], "low_threshold": 0.15, "high_threshold": 0.45}}
        wf["9"] = {"class_type": "ControlNetApplyAdvanced",
                   "inputs": {"positive": pos_ref, "negative": neg_ref, "control_net": ["7", 0], "image": ["8", 0],
                              "strength": a.cn_strength, "start_percent": 0.0, "end_percent": 0.85}}
        pos_ref, neg_ref = ["9", 0], ["9", 1]
    wf["10"] = {"class_type": "KSampler",
                "inputs": {"model": ["1", 0], "seed": seed, "steps": a.steps, "cfg": a.cfg, "sampler_name": "dpmpp_2m",
                           "scheduler": "karras", "positive": pos_ref, "negative": neg_ref, "latent_image": ["6", 0],
                           "denoise": a.denoise}}
    last = ["10", 0]
    if a.hires > 1.0:
        wf["11"] = {"class_type": "LatentUpscaleBy", "inputs": {"samples": last, "upscale_method": "bicubic", "scale_by": a.hires}}
        wf["12"] = {"class_type": "KSampler",
                    "inputs": {"model": ["1", 0], "seed": seed + 1, "steps": max(12, a.steps // 2), "cfg": a.cfg,
                               "sampler_name": "dpmpp_2m", "scheduler": "karras", "positive": pos_ref, "negative": neg_ref,
                               "latent_image": ["11", 0], "denoise": 0.35}}
        last = ["12", 0]
    wf["20"] = {"class_type": "VAEDecode", "inputs": {"samples": last, "vae": ["1", 2]}}
    wf["21"] = {"class_type": "SaveImage", "inputs": {"images": ["20", 0], "filename_prefix": "illustratedbooks"}}
    return wf


def run(a):
    plan = AR.load_plan()
    if a.id in plan:
        item = dict(plan[a.id])
    elif a.guide and a.brief:
        item = {"id": a.id, "type": a.type, "title": a.title or a.id, "brief": a.brief, "file": ""}
    else:
        raise SystemExit("unknown id: use a plan ID, or give --guide and --brief for an ad-hoc piece")
    guide = a.guide or (os.path.join(AR.ROOT, item["file"]) if item.get("file") else None)
    if not guide or not os.path.exists(guide):
        raise SystemExit("this tool needs a composition guide image (--guide or a style-study render in the plan)")
    w_in, h_in = AR.SIZES.get(item["type"], (7.125, 10.25))
    gw0, gh0 = Image.open(guide).size
    if abs((gw0 / gh0) / (w_in / h_in) - 1) > 0.25:
        w_in, h_in = (7.125, 10.25) if gh0 > gw0 else (14.25, 10.25)
    ratio = AR.nearest_ratio(w_in, h_in)
    gw, gh = GEN[ratio]
    pos = (f"{item['title']}. {AR.clean_brief(item['brief'])} {AR.STYLE}, intricate detail, "
           f"masterpiece children's book illustration. {a.extra}").strip()
    print(f"server  {a.server}\nitem    {a.id} ({item['type']}, print {w_in} x {h_in} in, generate {gw}x{gh}"
          f"{f' then x{a.hires}' if a.hires > 1 else ''})\nguide   {guide}\nmodel   {a.ckpt}  controlnet: {a.controlnet or '-'}\n")
    if a.dry_run:
        print(json.dumps(workflow(a, "guide.png", pos, NEG, gw, gh, 1), indent=1))
        return
    name = upload(a.server, guide)
    os.makedirs(AR.AI_DIR, exist_ok=True)
    logp = os.path.join(AR.AI_DIR, "log.csv")
    new_log = not os.path.exists(logp)
    for v in range(1, a.variants + 1):
        seed = (a.seed if a.seed is not None else random.randint(1, 2 ** 31)) + v
        cid = uuid.uuid4().hex
        res = json.loads(http(a.server, "/prompt", json.dumps({"prompt": workflow(a, name, pos, NEG, gw, gh, seed),
                                                               "client_id": cid}).encode(),
                              {"Content-Type": "application/json"}))
        pid = res["prompt_id"]
        t0 = time.time()
        while True:
            hist = json.loads(http(a.server, f"/history/{pid}"))
            if pid in hist and hist[pid].get("outputs"):
                break
            if pid in hist and hist[pid].get("status", {}).get("status_str") == "error":
                raise SystemExit(f"ComfyUI reported an error: {json.dumps(hist[pid]['status'])[:600]}")
            if time.time() - t0 > a.timeout:
                raise SystemExit("timed out waiting for ComfyUI")
            time.sleep(2)
        imgs = [i for o in hist[pid]["outputs"].values() for i in o.get("images", [])]
        q = urllib.parse.urlencode({"filename": imgs[0]["filename"], "subfolder": imgs[0].get("subfolder", ""),
                                    "type": imgs[0].get("type", "output")})
        raw = Image.open(io.BytesIO(http(a.server, "/view?" + q))).convert("RGB")
        out_raw = os.path.join(AR.AI_DIR, f"{a.id}__local{v}_raw.png")
        raw.save(out_raw)
        fitted, up = AR.fit_to_print(raw, w_in, h_in)
        out = os.path.join(AR.AI_DIR, f"{a.id}__local{v}.png")
        fitted.save(out, dpi=(300, 300))
        print(f"variant {v} (seed {seed}, {time.time() - t0:.0f}s): {raw.size[0]}x{raw.size[1]} -> {out} (x{up:.2f})")
        with open(logp, "a", newline="") as f:
            w = csv.writer(f)
            if new_log:
                w.writerow(["time", "id", "variant", "model", "guide", "refs", "aspect", "returned_px", "file", "prompt"])
                new_log = False
            w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), a.id, f"local{v}",
                        f"{a.ckpt} + {a.controlnet or 'no controlnet'} (denoise {a.denoise}, seed {seed})", guide, "",
                        ratio, f"{raw.size[0]}x{raw.size[1]}", os.path.relpath(out, AR.ROOT), pos])


def list_models(server):
    for node, key in (("CheckpointLoaderSimple", "ckpt_name"), ("ControlNetLoader", "control_net_name")):
        info = json.loads(http(server, f"/object_info/{node}"))
        names = info[node]["input"]["required"][key][0]
        print(f"{node}: " + (", ".join(names) if names else "(none found - see docs/06-local-ai.md)"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188"))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--id")
    ap.add_argument("--guide")
    ap.add_argument("--type", default="half", choices=list(AR.SIZES))
    ap.add_argument("--title")
    ap.add_argument("--brief")
    ap.add_argument("--extra", default="")
    ap.add_argument("--ckpt", default="sd_xl_base_1.0.safetensors")
    ap.add_argument("--controlnet", default="controlnet-canny-sdxl-1.0.safetensors",
                    help="ControlNet file name, or '' to run plain image-to-image")
    ap.add_argument("--denoise", type=float, default=0.5)
    ap.add_argument("--cn-strength", type=float, default=0.6)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=6.0)
    ap.add_argument("--hires", type=float, default=1.6, help="second detail pass scale (1 to disable)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--variants", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.list:
        list_models(a.server)
    elif a.id:
        run(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
