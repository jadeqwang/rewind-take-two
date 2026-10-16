#!/usr/bin/env python3
"""Style test stills of Jade for Rewind: is she painted in gongbi (工笔) or in a soft "Braid-like" impressionist
style? Look-test only, wired into nothing. Two styles x two reference photos x two image models = 8 stills, each
matted (BiRefNet) and laid over the film's engraved plates in the framing of media/sing/first/v4_S1_first.jpg.

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python             # cf.py (spend log + cap)
    EPY=tools/engrave/.venv/bin/python                                      # torch + BiRefNet
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python   # OpenCV + MediaPipe
    $PY  tools/sing/style_stills.py gen [KEY ...] [--dry-run] [--soft]    -> media/sing/style/<key>.png + .json
    $EPY tools/sing/style_stills.py matte                                 -> media/sing/style/_matte/<key>.png
    $MPY tools/sing/style_stills.py comp                                  -> media/sing/style/<key>_comp.jpg
    $MPY tools/sing/style_stills.py sheet                                 -> media/sing/style/contact_sheet.jpg

Keys are <style>_<photo>__<model>_<n>  (style gongbi|braid, photo pencils|long, model nbp|gpt).
Sources (inputs/jade_ref_image*.png) are never modified; padded copies the models can take go to _in/.
Calls are logged and capped by tools/gen/cf.py (tags style_still_<style>). --soft = the gentler retry prompt."""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "media/sing/style")
PHOTOS = {
    "pencils": ("inputs/jade_ref_image2_music_video_pencils.png", "media/sing/plates/plate_close_1.jpg"),
    "long": ("inputs/jade_ref_image_music_video_long_hair.png", "media/sing/plates/plate_truth_1.jpg"),
}
FRAME = "media/sing/first/v4_S1_first.jpg"           # target framing (plate cropped by crop.json box)
CROP = json.load(open(os.path.join(ROOT, "media/sing/first/crop.json")))["box"]

# model -> (catalog name, {photo: (aspect W, H) the model is sent / returns}, request builder)
MODELS = {
    "nbp": ("google/nano-banana-pro", {"pencils": (4, 3), "long": (3, 4)},
            lambda p, f, ar: {"prompt": p, "aspect_ratio": f"{ar[0]}:{ar[1]}", "image_size": "2K",
                              "output_format": "png", "image_input": [f]}),
    "gpt": ("openai/gpt-image-2.5-flare", {"pencils": (3, 2), "long": (2, 3)},
            lambda p, f, ar: {"prompt": p, "size": "1536x1024" if ar[0] > ar[1] else "1024x1536", "quality": "high",
                              "output_format": "png", "images": [f]}),
}

# ------------------------------------------------------------------------------------------------- prompts
STYLE = {
    "gongbi": (
        "Repaint this whole photograph as a gongbi (工笔) painting: meticulous Chinese fine-line painting in mineral "
        "colours on silk. Every contour is drawn with a crisp, even, unbroken fine ink line of uniform weight "
        "(iron-wire line, 铁线描): the outline of her face, her eyes and eyelids, brows, nose and lips, every lock and "
        "strand of hair, the glasses frame, the jacket seams, collar, snaps and zip. Inside the lines the colour is laid "
        "in flat, transparent, layered washes of mineral pigment, built up and gently graded (渲染) for form: lead-white "
        "and pale pearl for the jacket, cinnabar-orange for its bands, azurite blue for the disc on her chest, ink black "
        "for her top and hair, warm ochre and soft rose for her skin. No Western light-and-shadow modelling, no "
        "photographic lighting, no gloss, no blur, no texture of oil paint. "),
    "braid": (
        "Repaint this whole photograph as a soft impressionist painting in oil and gouache, like the hand-painted "
        "backgrounds of a dreamy storybook video game: loose, visible brush strokes, dappled painterly texture, warm "
        "glowing golden light falling across her from one side, rich deep blues and warm golds in the shadows and "
        "highlights, soft edges and a faint luminous haze. The brushwork is free everywhere except in her face, which "
        "is painted with care so that every feature stays clear and true. Painted by hand: not a photo, not anime, not "
        "3D, not a cartoon. "),
}
GROUND = {
    "gongbi": "Replace the whole background with a plain, empty ground of aged warm cream silk with its fine weave "
              "showing: nothing else behind her, no landscape, no flowers, no seals or writing. ",
    "braid": "Replace the whole background with a plain, soft painted ground, a quiet wash of muted blue warming to "
             "gold: nothing else behind her, no scenery, no landscape, no clouds, no objects, no architecture. ",
}
LIKENESS = (
    "This is a portrait of a specific real woman and she must stay instantly recognisable as herself. Keep her exact "
    "likeness and proportions from the photo: the same wide heart-shaped face with full cheeks, the same high forehead "
    "and hairline, the same two slightly different eyebrows (each keeps its own shape and height), her own eye shape "
    "and size (do not narrow them into almond eyes, do not enlarge them), the same nose, the same mouth at its real "
    "width and fullness (do not make it smaller), her real warm skin tone and freckles. Her thin dark metal glasses keep "
    "exactly the same frame shape and size, with both lenses. Do not beautify, slim, idealise, age, or whiten her "
    "skin; no makeup; do not make her look like a classical court lady or a generic model. Her expression is calm and "
    "serious: lips closed and relaxed, not smiling. "
)
OUTFIT = {
    "pencils": "Keep her hair up in the loose bun with the same wisps, with the two yellow pencils pushed crossways "
               "through the bun like hairpins: one with a pale-blue eraser on the left, one with a pink eraser on the "
               "right; both pencils and both erasers stay visible. ",
    "long": "Keep her long dark hair down, centre-parted, falling over her shoulders and jacket exactly as in the photo. ",
}
JACKET = (
    "Keep her clothes exactly: the white jacket with its horizontal orange bands, the snap studs on the collar and "
    "shoulders, the silver zip, the pale-blue circle on the chest, and the round black-rimmed sleeve patch whose text "
    "reads exactly \"1420\" over \"MHz\"; the black turtleneck. Keep her pose, the tilt of her head and the framing of "
    "the photo: do not crop, zoom or move her. "
)
SOFT = ("Please make an artistic painted portrait of the person in this photo. ")


def prompt_for(style, photo, soft=False):
    return (SOFT if soft else "") + STYLE[style] + LIKENESS + OUTFIT[photo] + JACKET + GROUND[style]


JOBS = [(s, p, m) for s in STYLE for p in PHOTOS for m in MODELS]


def input_for(photo, short):
    """The source photo padded (never cropped) to the aspect the model returns; pad = edge colour, blurred."""
    from PIL import Image, ImageFilter
    aw, ah = MODELS[short][1][photo]
    p = os.path.join(OUT, "_in", f"{photo}_{aw}x{ah}.png")
    if os.path.exists(p):
        return p
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im = Image.open(os.path.join(ROOT, PHOTOS[photo][0])).convert("RGB")
    w, h = im.size
    if abs(w / h - aw / ah) < 1e-3:
        im.save(p)
        return p
    W, H = (round(h * aw / ah), h) if w / h < aw / ah else (w, round(w * ah / aw))
    import numpy as np
    a = np.asarray(im)
    px, py = (W - w) // 2, (H - h) // 2
    b = np.pad(a, ((py, H - h - py), (px, W - w - px), (0, 0)), mode="edge")
    big = Image.fromarray(b).filter(ImageFilter.GaussianBlur(25))
    big.paste(im, (px, py))
    big.save(p)
    return p


def gen_one(style, photo, short, dry, soft):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    model, aspects, mk = MODELS[short]
    i = 1
    while os.path.exists(os.path.join(OUT, f"{style}_{photo}__{short}_{i}.json")):
        i += 1
    key = f"{style}_{photo}__{short}_{i}"
    prompt = prompt_for(style, photo, soft)
    src = input_for(photo, short)
    inp = mk(prompt, "file:" + os.path.relpath(src, ROOT), aspects[photo])
    tag = f"style_still_{style}"
    try:
        est, why = cf.estimate(model, inp)
        paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
    except BaseException as e:  # one model failing (or refusing) must not lose the rest of the batch
        print(f"[fail] {key}: {str(e)[:400]}", file=sys.stderr)
        return key, None
    if dry:
        return key, est
    json.dump({"key": key, "style": style, "photo": photo, "model": model, "soft": soft, "prompt": prompt, "tag": tag,
               "input": os.path.relpath(src, ROOT), "src": PHOTOS[photo][0],
               "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input")},
               "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths]},
              open(os.path.join(OUT, key + ".json"), "w"), indent=1)
    return key, est


def gen(argv):
    dry, soft = "--dry-run" in argv, "--soft" in argv
    want = [a for a in argv if not a.startswith("--")]
    jobs = [(s, p, m, dry, soft) for s, p, m in JOBS if not want or any(w in f"{s}_{p}__{m}" for w in want)]
    os.makedirs(OUT, exist_ok=True)
    for s, p, m, *_ in jobs:
        input_for(p, m)
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda j: gen_one(*j), jobs))
    print(json.dumps(res, indent=1))
    print(f"{len(res)} calls, {sum(1 for _, e in res if e is None)} failed, "
          f"est ${sum(e for _, e in res if e):.2f}{' (dry run)' if dry else ''}")


def latest():
    """The newest successful still per style x photo x model: {key: json}."""
    best = {}
    for f in sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []:
        if f.endswith(".json") and "__" in f:
            d = json.load(open(os.path.join(OUT, f)))
            if d.get("out") and os.path.exists(os.path.join(ROOT, d["out"][0])):
                slot = d["key"].rsplit("_", 1)[0]
                if slot not in best or int(d["key"].rsplit("_", 1)[1]) > int(best[slot]["key"].rsplit("_", 1)[1]):
                    best[slot] = d
    return {d["key"]: d for d in best.values()}


# ------------------------------------------------------------------------------------------------- matte (EPY)
def matte(argv):
    import numpy as np
    import torch
    from PIL import Image
    from scipy import ndimage as ndi
    sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
    from matte import get_birefnet
    from gpulock import GpuSlot
    slot = GpuSlot(label="style_stills")
    slot.acquire()
    net = get_birefnet("cuda")
    os.makedirs(os.path.join(OUT, "_matte"), exist_ok=True)
    for k, d in latest().items():
        p = os.path.join(OUT, "_matte", k + ".png")
        if os.path.exists(p) and "--force" not in argv:
            continue
        a = np.asarray(Image.open(os.path.join(ROOT, d["out"][0])).convert("RGB"), np.float32) / 255
        H, W = a.shape[:2]
        x = torch.from_numpy(a).permute(2, 0, 1)[None].cuda()
        m = net(x)[0, 0].cpu().numpy()
        for x0, x1 in ((0, W * 5 // 8), (W * 3 // 8, W)):          # two overlapping halves for the hair wisps
            m[:, x0:x1] = np.maximum(m[:, x0:x1], net(x[..., x0:x1])[0, 0].cpu().numpy() * (m[:, x0:x1] > 0.02))
        lab, n = ndi.label(m > 0.5)
        if n > 1:                                                     # keep her: the largest component
            sizes = ndi.sum(np.ones_like(m), lab, range(1, n + 1))
            keep = 1 + int(np.argmax(sizes))
            m = m * ndi.binary_dilation(lab == keep, iterations=20)
        Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).save(p)
        print(k, "coverage", round(float((m > 0.5).mean()), 3))
    slot.release() if hasattr(slot, "release") else None


# ------------------------------------------------------------------------------------------------- comp (MPY)
STABLE = [33, 133, 362, 263, 168, 6, 197, 195, 5, 4, 1, 98, 327, 10, 151, 9, 127, 356, 234, 454]


def landmarks(rgb):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault("FACE_LANDMARKER", os.path.expanduser(
        "~/Documents/1-music-shipped/moongazing/tools/sync/models/face_landmarker.task"))
    import mouth as MT
    H, W = rgb.shape[:2]
    r = MT.detect(rgb, (0, 0, W, H))
    if r is None:
        for b in MT.grid_boxes(W, H):
            r = MT.detect(rgb, b)
            if r is not None:
                break
    return r


def comp(argv):
    import cv2
    import numpy as np
    from PIL import Image
    T = np.asarray(Image.open(os.path.join(ROOT, FRAME)).convert("RGB"))
    LT = landmarks(T)[0]
    FH, FW = T.shape[:2]
    x0, y0, x1, y1 = CROP
    out = {}
    for k, d in latest().items():
        mp_ = os.path.join(OUT, "_matte", k + ".png")
        if not os.path.exists(mp_):
            print("no matte:", k); continue
        F = np.asarray(Image.open(os.path.join(ROOT, d["out"][0])).convert("RGB"))
        A = np.asarray(Image.open(mp_), np.float32) / 255
        h, w = F.shape[:2]
        # soften the matte where the figure runs off the still's left/right/top edge (bottom stays: it is the frame bottom)
        ramp = 40
        e = np.ones((h, w), np.float32)
        e *= np.clip(np.arange(w) / ramp, 0, 1)[None] * np.clip((w - 1 - np.arange(w)) / ramp, 0, 1)[None]
        e *= np.clip(np.arange(h) / ramp, 0, 1)[:, None]
        A = A * e
        r = landmarks(F)
        if r is None:
            print("no face:", k); continue
        L = r[0]
        # scale + shift only (rotating would tilt the still's own cut edges into view): face size from the target's
        # eye-to-eye distance, eyes centred on the target's; the still's bottom edge sits on the frame bottom, and the
        # scale is capped so the top of her figure (bun, pencils) stays 40 px inside the frame
        io = np.linalg.norm(L[33] - L[263])
        s = np.linalg.norm(LT[33] - LT[263]) / io
        rows = np.where(A.max(1) > 0.5)[0]
        top = rows[0] if len(rows) else 0
        s = min(s, (FH - 40) / (h - top))
        ex = (L[33, 0] + L[263, 0]) / 2
        tx = (LT[33, 0] + LT[263, 0]) / 2
        M = np.array([[s, 0, tx - s * ex], [0, s, FH - s * h]])
        sc = s
        Fw = cv2.warpAffine(F.astype(np.float32), M, (FW, FH), flags=cv2.INTER_LANCZOS4 if sc > 1 else cv2.INTER_AREA,
                            borderMode=cv2.BORDER_REPLICATE)
        Aw = cv2.warpAffine(A, M, (FW, FH), flags=cv2.INTER_LINEAR, borderValue=0)
        Aw = np.clip((cv2.GaussianBlur(Aw, (0, 0), 1.0) - 0.08) / 0.84, 0, 1)
        P = np.asarray(Image.open(os.path.join(ROOT, PHOTOS[d["photo"]][1])).convert("RGB"), np.float32)[y0:y1, x0:x1]
        C = Fw * Aw[..., None] + P * (1 - Aw[..., None])
        o = os.path.join(OUT, k + "_comp.jpg")
        Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)).save(o, quality=93)
        out[k] = {"comp": os.path.relpath(o, ROOT), "scale": round(sc, 3)}
        print(o, "scale", round(sc, 3))
    json.dump(out, open(os.path.join(OUT, "_matte", "comp.json"), "w"), indent=1)


# ------------------------------------------------------------------------------------------------- sheet (MPY)
def sheet(argv):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=True):
        p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"
        return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

    cands = latest()
    TH, pad, lab, head = 390, 12, 46, 70
    nice = {"nbp": "nano-banana-pro", "gpt": "gpt-image-2.5-flare"}
    rows = [(s, p) for s in STYLE for p in PHOTOS]

    def fit(im, h):
        return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

    # source face crops: square box around the landmarked face, generous enough for glasses, hair and pencils
    srcs = {}
    for p, (sp, _) in PHOTOS.items():
        im = Image.open(os.path.join(ROOT, sp)).convert("RGB")
        L = landmarks(np.asarray(im))[0]
        cx, cy = L[:, 0].mean(), L[:, 1].mean()
        half = (L[:, 1].max() - L[:, 1].min()) * (1.05 if p == "pencils" else 0.85)
        cy -= half * (0.25 if p == "pencils" else 0.1)
        half = min(half, im.width / 2, im.height / 2)
        cx, cy = min(max(cx, half), im.width - half), min(max(cy, half), im.height - half)   # keep the box inside the photo
        srcs[p] = fit(im.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half))), TH)

    tiles = []
    for s, p in rows:
        row = [("source photo", p, srcs[p])]
        for m in MODELS:
            k = next((k for k, d in cands.items() if d["style"] == s and d["photo"] == p and k.split("__")[1].startswith(m)), None)
            if k is None:
                row += [(nice[m], "FAILED", None), (nice[m], "comp", None)]
                continue
            raw = fit(Image.open(os.path.join(ROOT, cands[k]["out"][0])).convert("RGB"), TH)
            cp = os.path.join(OUT, k + "_comp.jpg")
            c = fit(Image.open(cp).convert("RGB"), TH) if os.path.exists(cp) else None
            row += [(nice[m], k, raw), (nice[m] + "  on plate", os.path.basename(PHOTOS[p][1]), c)]
        tiles.append(row)
    widths = [sum((t[2].width if t[2] else 560) + pad for t in r) + pad for r in tiles]
    Wd = max(widths)
    Hd = head + len(tiles) * (TH + lab + pad) + pad
    S = Image.new("RGB", (Wd, Hd), (26, 26, 28))
    dr = ImageDraw.Draw(S)
    dr.text((pad, 14), "Rewind style test: gongbi vs soft painted (Braid-like).  Row = style / photo; per model: raw still, then on the plate.",
            fill=(235, 235, 235), font=font(26))
    y = head
    for (s, p), r in zip(rows, tiles):
        x = pad
        for i, (a, b, im) in enumerate(r):
            w = im.width if im else 560
            if im:
                S.paste(im, (x, y + lab))
            else:
                dr.rectangle((x, y + lab, x + w, y + lab + TH), outline=(120, 60, 60), width=3)
            t1 = f"{s.upper()} / {p}" if i == 0 else a
            dr.text((x + 4, y + 2), t1, fill=(255, 220, 140) if i == 0 else (255, 255, 255), font=font(20))
            dr.text((x + 4, y + 25), b if i else "likeness reference", fill=(165, 165, 170), font=font(15, False))
            x += w + pad
        y += TH + lab + pad
    o = os.path.join(OUT, "contact_sheet.jpg")
    S.save(o, quality=90)
    print(o, S.size)


if __name__ == "__main__":
    {"gen": gen, "matte": matte, "comp": comp, "sheet": sheet}[sys.argv[1]](sys.argv[2:])
