"""Section C (Verse 2, the precision platformer, V2a-V2n): prompt blocks, keyframe runner, sheets.
Helpers adapted from tools/sectionA/common.py (copied, not imported, so the sections stay independent).

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/sectionC/kf.py list
    $PY tools/sectionC/kf.py run V2a1 V2b ...     # ids or prefixes; writes media/shots/<clip>/kf_<n>.png + a sheet
"""
import concurrent.futures as cfut
import os
import sys
import traceback

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
import cf  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

SHOTS = os.path.join(ROOT, "media/shots")
REFDIR = os.path.join(ROOT, "media/shots/_C_refs")
SHEETS = os.path.join(ROOT, "media/shots/_C_sheets")

JADE_SHEET = "media/design/jade_canon_turnaround.png"
JADE_ACTION = "media/design/takes/jade_action_flare_t2.png"
AGENT_SHEET = "media/design/takes/agent_turn_nano_t2_styleref.jpg"

STYLE = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, dense "
         "precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no color anywhere "
         "except the girl. The girl is a full-color anime character (clean cel shading) exactly matching the reference "
         "sheet. Full bleed, edge to edge, no border, no margin, no paper edge, no frame, 16:9. No text, no letters, no "
         "numbers, no signs with writing, no signature, no watermark.")

STYLE_NOGIRL = ("Rendered as an M.C. Escher wood engraving / lithograph: crisp black ink lines on warm off-white paper, "
                "dense precise parallel hatching and cross-hatching that follows form, high contrast, no gray wash, no "
                "color anywhere. Full bleed, edge to edge, no border, no margin, no paper edge, no frame, 16:9. No text, "
                "no letters, no numbers, no license plates, no signs with writing, no signature, no watermark.")

NIGHT = ("It is night, drawn as an M.C. Escher wood engraving: the dark sky and shadows carved from dense black ink with "
         "fine white engraved lines, every light (headlights, streetlamps, siren strobes) a crisp white engraved starburst "
         "of radiating lines, warm off-white paper showing only in the lit areas, no gray wash, no airbrush, no "
         "photographic shading. ")

DAY = ("Bright day, drawn as an M.C. Escher wood engraving: mostly warm off-white paper with crisp black ink line work "
       "and dense hatching in the shadows, no gray wash. ")

JADE = ("The girl is EXACTLY the anime girl from the attached character turnaround sheet: same face, same anime drawing "
        "style and cel shading, and exactly her outfit: white cropped bomber jacket with an orange band across the chest "
        "and around both sleeves, small pale-blue dot patch on her left chest, round black-and-white '1420 MHz' roundel "
        "patch on her LEFT upper sleeve, black crop top, navy-blue wide-leg cargo pants with hanging orange straps, chunky "
        "white sneakers, orange over-ear headphones resting around her neck, long black hair worn up in a loose bun with a "
        "yellow wooden pencil stuck through the bun; ALL of her long hair is gathered up into the bun, only a few short "
        "strands frame her face, no long hair hanging down her back. The orange headphones always rest around her NECK, "
        "never on her head. The '1420 MHz' patch is only on her LEFT sleeve; her right sleeve has no patch. ")

AGENTS = ("The agents are EXACTLY the men of the attached engraved agent reference sheet: identical plain black narrow "
          "suits, white shirts, thin black ties, opaque black sunglasses, nearly blank mannequin-like engraved faces with "
          "no expression, short slicked hair carved as tight parallel lines, a coiled earpiece wire behind the ear. They "
          "are drawn in the same black-and-white engraving as the world. ")

CAR = ("a white 2001 Acura TL four-door sedan (sleek late-1990s/early-2000s Japanese sedan, smooth rounded body, slim "
       "headlights, five-spoke alloy wheels), its white paint drawn as bare paper with only fine contour lines so it "
       "reads clearly as the one white car")

SEDANS = ("identical black 1990s government sedans drawn in solid black ink with thin white engraved highlight lines, "
          "each with a roof light bar blazing as a crisp WHITE engraved starburst of radiating lines (no color at all)")

SIDE = ("Exact side view, the camera perpendicular to the road like a 2D side-scrolling video game, horizon level, "
        "everything moving left to right. ")


def ref(path, max_side=1536):
    src = os.path.join(ROOT, path)
    os.makedirs(REFDIR, exist_ok=True)
    out = os.path.join(REFDIR, os.path.splitext(os.path.basename(path))[0] + f"_{max_side}.jpg")
    if not os.path.exists(out):
        im = Image.open(src)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (244, 242, 236))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side), Image.LANCZOS)
        im.save(out, quality=92)
    return os.path.relpath(out, ROOT)


def inp_for(model, prompt, refs=()):
    refs = ["file:" + ref(r) for r in refs]
    if model.startswith("openai/gpt-image"):
        d = {"prompt": prompt, "size": "1536x1024", "quality": "high", "output_format": "png"}
        if refs:
            d["images"] = refs
        return d
    if model == "google/nano-banana-pro":
        d = {"prompt": prompt, "aspect_ratio": "16:9", "image_size": "2K", "output_format": "png"}
        if refs:
            d["image_input"] = refs[:3]
        return d
    if model == "bytedance/seedream-5-pro":
        d = {"prompt": prompt, "size": "2560x1440", "watermark": False}
        if refs:
            d["image"] = refs if len(refs) > 1 else refs[0]
        return d
    raise ValueError(model)


def trim_margins(path, thresh=18):
    """Trim a uniform paper/border margin if the model drew one; then force 16:9 by center crop. In place."""
    import numpy as np
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape

    def busy(line):
        return (np.abs(line - np.median(line, axis=0)).sum(axis=1) > 60).mean() > 0.02

    t, b, l, r = 0, h, 0, w
    while t < h // 6 and not busy(a[t]):
        t += 1
    while b > h - h // 6 and not busy(a[b - 1]):
        b -= 1
    while l < w // 6 and not busy(a[:, l]):
        l += 1
    while r > w - w // 6 and not busy(a[:, r - 1]):
        r -= 1
    box = [l, t, r, b]
    if sum(m > thresh for m in (t, h - b, l, w - r)) >= 3:
        box = [l + 4, t + 4, r - 4, b - 4]
    else:
        box = [0, 0, w, h]
    cw, ch = box[2] - box[0], box[3] - box[1]
    if cw / ch > 16 / 9:
        nw = round(ch * 16 / 9); box[0] += (cw - nw) // 2; box[2] = box[0] + nw
    else:
        nh = round(cw * 9 / 16); box[1] += (ch - nh) // 2; box[3] = box[1] + nh
    if tuple(box) != (0, 0, w, h):
        base, ext = os.path.splitext(path)
        raw = base + "_raw" + ext
        if not os.path.exists(raw):
            im.save(raw)
        im.crop(box).save(path)
    return path


def run_jobs(jobs, workers=int(os.environ.get("C_WORKERS", 8))):
    def one(j):
        try:
            os.makedirs(os.path.dirname(j["out"]), exist_ok=True)
            p = cf.generate(j["model"], inp_for(j["model"], j["prompt"], j.get("refs", ())), j["out"],
                            tag=j.get("tag", "C_" + j["id"]), timeout=600)[0]
            trim_margins(p)
            return j["id"], p
        except Exception as e:  # noqa: BLE001
            print(f"FAILED {j['id']} {j['model']}: {e}", file=sys.stderr)
            traceback.print_exc()
            return j["id"], None
    res = {}
    with cfut.ThreadPoolExecutor(workers) as ex:
        for k, p in ex.map(one, jobs):
            res[k] = p
    return res


def sheet(tiles, out, title="", cols=2, width=2400):
    pad, head, lab = 12, 50, 34
    tw = (width - pad * (cols + 1)) // cols
    th = round(tw * 9 / 16)
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new("RGB", (width, head + rows * (th + lab + pad) + pad), (24, 24, 24))
    d = ImageDraw.Draw(S)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except OSError:
        f = ImageFont.load_default()
    d.text((pad, 10), title, fill=(255, 255, 255), font=f)
    for i, (p, label) in enumerate(tiles):
        x = pad + (i % cols) * (tw + pad)
        y = head + (i // cols) * (th + lab + pad)
        d.text((x, y + 2), label, fill=(255, 200, 80), font=f)
        if p and os.path.exists(p):
            im = Image.open(p).convert("RGB")
            im.thumbnail((tw, th), Image.LANCZOS)
            S.paste(im, (x, y + lab))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    S.save(out, quality=88)
    return out
