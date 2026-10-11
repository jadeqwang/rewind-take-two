"""Section F (final drop + outro) helpers: prompts, refs, parallel image calls, 16:9 crops, contact sheets."""
import concurrent.futures as cfut
import os
import sys
import traceback

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
sys.path.insert(0, os.path.join(ROOT, "media/style_tests/scripts"))
import cf  # noqa: E402
import st  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

SHOTS = os.path.join(ROOT, "media/shots")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NANO = "google/nano-banana-pro"
FLARE = "openai/gpt-image-2.5-flare"
SEEDREAM = "bytedance/seedream-5-pro"

# refs (repo-relative JPEGs; png_ref flattens RGBA onto paper)
REF_CANON = None
REF_HAIRDOWN = None
REF_WORLD = "media/style_tests/world/3_loop_L_tracks_seedream-5-pro.jpg"


def refs():
    global REF_CANON, REF_HAIRDOWN
    if REF_CANON is None:
        REF_CANON = st.png_ref(os.path.join(ROOT, "media/design/jade_canon_turnaround.png"))
        REF_HAIRDOWN = st.png_ref(os.path.join(ROOT, "media/design/takes/jade_pencil_flare_t2.png"))
    return REF_HAIRDOWN, REF_CANON, REF_WORLD


JADE_DOWN = ("The girl is a full-color anime character with clean cel shading, exactly matching the reference sheets: "
             "white cropped bomber jacket with an orange band across chest and arms, pale-blue dot patch on the left chest, "
             "round '1420 MHz' patch on the left sleeve, black crop top, navy wide cargo pants with orange straps, chunky "
             "white sneakers, orange headphones around her neck. Her long black hair is DOWN and loose (no bun), "
             "and she holds a yellow pencil in her hand.")

COLOR_WORLD = ("The world is the same M.C. Escher wood engraving as the third reference (crisp black ink line work, dense "
               "precise parallel hatching and cross-hatching that follows form), but now hand-colored: vivid colored-pencil "
               "color laid over the engraving in visible pencil strokes on warm off-white paper tooth - cobalt and "
               "ultramarine blue, vermilion, magenta, emerald, warm orange, sky blue - with the black hatching still showing "
               "through the color everywhere. Gustav Klimt gold-leaf accents (flat burnished gold with spiral and small "
               "square mosaic ornament) on select surfaces. Kandinsky shapes float in the sky: concentric circles, "
               "triangles, arcs and checkerboards in colored pencil. Hand-drawn, not a painting, no watercolor wash, "
               "no airbrush, no digital gradients, not photographic, not 3D.")

FINISH = "Full bleed, edge to edge, no border, no margin, no paper edge, 16:9. No text, no letters, no numbers, no signature."


def run_parallel(jobs, workers=6):
    """jobs: list of (model, prompt, refs, out_path, tag). Returns {out: path|exception}."""
    res = {}

    def one(j):
        model, prompt, rf, out, tag = j
        os.makedirs(os.path.dirname(out), exist_ok=True)
        inp = st.inp_for(model, prompt, rf)
        p = cf.generate(model, inp, out, tag=tag)
        return p[0] if isinstance(p, list) else p

    with cfut.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(one, j): j[3] for j in jobs}
        for f in cfut.as_completed(futs):
            out = futs[f]
            try:
                res[out] = f.result()
                print("ok", res[out], flush=True)
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                res[out] = e
    return res


def to169(path, out=None, pad_top=True):
    """Crop to 16:9 (3:2 gpt output: keep the top, trim the bottom, to protect heads)."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if abs(w / h - 16 / 9) > 0.01:
        if w / h < 16 / 9:
            nh = round(w * 9 / 16)
            y0 = int((h - nh) * (0.35 if pad_top else 0.5))
            im = im.crop((0, y0, w, y0 + nh))
        else:
            nw = round(h * 16 / 9)
            x0 = (w - nw) // 2
            im = im.crop((x0, 0, x0 + nw, h))
    out = out or path
    im.save(out, quality=94) if out.lower().endswith(".jpg") else im.save(out)
    return out


def sheet(items, out, cols=2, cell_w=960, title=""):
    """items: list of (path, label)."""
    ims = []
    for p, lab in items:
        try:
            im = Image.open(p).convert("RGB")
        except Exception:  # noqa: BLE001
            im = Image.new("RGB", (cell_w, cell_w * 9 // 16), (60, 0, 0))
        im = im.resize((cell_w, round(cell_w * im.height / im.width)))
        ims.append((im, lab))
    rows = (len(ims) + cols - 1) // cols
    ch = max(i.height for i, _ in ims) + 28
    top = 40 if title else 0
    S = Image.new("RGB", (cols * cell_w + (cols + 1) * 8, top + rows * (ch + 8) + 8), (26, 26, 26))
    d = ImageDraw.Draw(S)
    f = ImageFont.truetype(FONT, 20)
    if title:
        d.text((10, 8), title, fill=(240, 240, 240), font=f)
    for k, (im, lab) in enumerate(ims):
        r, c = divmod(k, cols)
        x, y = 8 + c * (cell_w + 8), top + 8 + r * (ch + 8)
        d.text((x, y), lab, fill=(245, 190, 80), font=ImageFont.truetype(FONT, 16))
        S.paste(im, (x, y + 24))
    S.save(out, quality=88)
    return out
