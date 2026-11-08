# 6 · Running the AI finishing pass on your own PC

This is a free alternative to the Gemini tool: no per-image cost, and nothing leaves your machine. The code-painted renders in `art/png/` lock the composition. A local Stable Diffusion XL model, steered by a ControlNet, repaints them with a hand-painted finish. `tools/local_refine.py` does the work through ComfyUI's local API.

## 6.1 Will my PC run it?

| Your graphics | Works? | Speed (per picture, roughly) |
|---|---|---|
| NVIDIA RTX with 12 GB+ VRAM (3060 12 GB, 4070, 4080, 4090…) | Yes, comfortably | 15–60 s |
| NVIDIA with 8 GB VRAM | Yes (use `--hires 1`, or ComfyUI's low-VRAM mode) | 30–90 s |
| Apple Silicon Mac (M1–M4) with 16 GB+ memory | Yes, slower | 1–3 min |
| AMD Radeon | Possible but fiddly (best on Linux) | varies |
| No dedicated GPU | Not practical | — |

On Windows, check your graphics card under Task Manager → Performance → GPU ("Dedicated GPU memory").

## 6.2 Install (one time, about 30 minutes plus downloads)

1. **ComfyUI.** Install the desktop app from **comfy.org** (Windows/Mac), or the portable build from **github.com/comfyanonymous/ComfyUI**. Start it once so it creates its folders.
2. **Download two models** (about 7 GB in total) into ComfyUI's `models` folder:

   | File | Put it in | From (Hugging Face) | Licence |
   |---|---|---|---|
   | `sd_xl_base_1.0.safetensors` | `models/checkpoints/` | `stabilityai/stable-diffusion-xl-base-1.0` | CreativeML Open RAIL++-M (commercial use allowed, with use restrictions) |
   | `diffusion_pytorch_model.safetensors` (rename it to `controlnet-canny-sdxl-1.0.safetensors`) | `models/controlnet/` | `diffusers/controlnet-canny-sdxl-1.0` | OpenRAIL++ |

3. **This project:** clone the repository, check out this branch, and install the Python libraries:

```bash
git clone https://github.com/Cheezwedge/IllustratedBooks.git
```

```bash
cd IllustratedBooks
```

```bash
git checkout claude/adoring-albattani-y9nc94
```

```bash
pip install pillow numpy scipy weasyprint pymupdf markdown
```

### On a Linux machine

Linux is the best-supported platform for ComfyUI, and the easiest one for AMD cards. ComfyUI's desktop app is Windows/Mac only, so on Linux install it from source.

**1. Check the graphics card.** For NVIDIA, this shows the card, its VRAM and the driver version:

```bash
nvidia-smi
```

For AMD:

```bash
rocminfo | grep -i gfx
```

**2. Install ComfyUI** in a Python virtual environment:

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
```

```bash
cd ComfyUI
```

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

Install PyTorch for your card. pytorch.org ("Get started") gives the exact command for your CUDA or ROCm version. For NVIDIA it looks like this:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

Then ComfyUI's own requirements:

```bash
pip install -r requirements.txt
```

**3. Download the two models** straight into place:

```bash
wget -O models/checkpoints/sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

```bash
wget -O models/controlnet/controlnet-canny-sdxl-1.0.safetensors https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors
```

**4. Start ComfyUI.** Leave it running in its own terminal (or under `tmux`/`screen` on a headless box):

```bash
python main.py
```

It listens on `http://127.0.0.1:8188`, which is what `tools/local_refine.py` expects. Run the project scripts on the same machine. If you run them from another computer, start ComfyUI with `--listen` and pass `--server http://<linux-ip>:8188`. Only do that on a trusted home network.

## 6.3 Use it

With ComfyUI running, check that it can see the models:

```bash
python tools/local_refine.py --list
```

Repaint the frontispiece cutaway, three versions:

```bash
python tools/local_refine.py --id FM-P1 --variants 3
```

Results land in `art/ai/` as `<ID>__localN.png`, already fitted to 300 dpi print size. Everything is logged in `art/ai/log.csv`. To put a chosen one into the book:

```bash
python tools/ai_refine.py --promote art/ai/FM-P1__local2.png
```

```bash
python book/build.py
```

**Tuning:**

| Option | Effect |
|---|---|
| `--denoise 0.35` | Keeps the drawing very close. `0.6` repaints more freely. Start at 0.45–0.5. |
| `--cn-strength 0.8` | Holds the layout harder. `0.4` gives the model more freedom. |
| `--hires 1` | Turns off the second detail pass (for 8 GB cards). |
| `--seed 1234` | Repeats a result you liked. |

## 6.4 Better results

- **Style fine-tunes:** you can swap the SDXL base for a watercolour or storybook fine-tune with `--ckpt <file>`. Read each model's licence for commercial use. **Do not use any model or LoRA trained to imitate a named artist or series** (including anything labelled Brambly Hedge or Jill Barklem). That is the clearest legal and ethical risk in the whole project.
- **Paint-over workflow:** the free **Krita AI Diffusion** plugin (github.com/Acly/krita-ai-diffusion) runs the same models inside a painting app. You can repaint just one region, such as a face or a shelf, and paint by hand in between. This is the best way to reach finished quality.
- **Characters:** design them first (art bible §2.6). Train or use a reference adapter only on *your own* character sheets.
- **Disclosure:** everything here is AI-assisted. Keep `art/ai/log.csv` and your layered files (rights doc §1.7, art bible §2.10).

## 6.5 Letting Claude drive it

This cloud session can't reach your PC. You can instead run Claude Code **on the PC** in the cloned folder, either:

- through the Code tab of the Claude desktop app, or
- by running `claude` in a terminal in that folder.

Then ask it to run `tools/local_refine.py`. It will then be able to start ComfyUI jobs, compare variants and promote the best ones, just as here.

On a headless Linux machine, start Claude Code in the project folder in Remote Control mode. You can then drive that session from the Claude app on your phone or laptop while the work runs on the Linux box's GPU:

```bash
claude remote-control
```
