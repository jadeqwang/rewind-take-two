#!/usr/bin/env python3
"""Watercolor singing Jade (v4), step 0: candidate stills. Jade's v4 notes: hair "more glossy and natural looking",
"try a couple image models", and "reduce smiling magnitude". Hair and expression are edited SEPARATELY on the
reference portrait (inputs/jade_watercolor_jacket_v6.png, never overwritten), so she can pick "this hair, that face".

    PY=~/Documents/moongazing/.venv/bin/python; MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
    $PY  tools/sing/v4_stills.py gen [KEY ...] [--round=1] [--dry-run] [--jobs=6]
    $MPY tools/sing/v4_stills.py sheet           -> media/sing/v4/stills/sheet_hair.jpg, sheet_face.jpg, metrics.json

Outputs media/sing/v4/stills/<key>.png with <key>.json beside it (model, prompt, input crop, cost estimate).
Each model gets the top of the portrait cropped to an aspect it can return (media/sing/v4/stills/_in/). `sheet`
maps every candidate back onto the portrait by its eye and nose landmarks (similarity fit, mouth left out), so all
tiles are the same crop at the same scale. Logged and capped by tools/gen/cf.py (tags v4A_still_*)."""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "inputs/jade_watercolor_jacket_v6.png")
OUT = os.path.join(ROOT, "media/sing/v4/stills")
W0, H0 = 971, 1620

# model -> (short name, rows of the portrait sent (0..rows), request fields)
MODELS = {
    "nbp": ("google/nano-banana-pro", 1214, lambda p, f: {"prompt": p, "aspect_ratio": "4:5", "image_size": "2K",
                                                           "output_format": "png", "image_input": [f]}),
    "gpt": ("openai/gpt-image-2.5-flare", 1456, lambda p, f: {"prompt": p, "size": "1024x1536", "quality": "high",
                                                               "output_format": "png", "images": [f]}),
    "sdr": ("bytedance/seedream-5-pro", 1214, lambda p, f: {"prompt": p, "size": "1792x2240", "watermark": False, "image": f}),
    "grok": ("xai/grok-imagine-image-2.0", 1295, lambda p, f: {"prompt": p, "aspect_ratio": "3:4", "resolution": "2k",
                                                                "quality": "medium", "response_format": "b64_json",
                                                                "images": [{"url": f}]}),
    "kontext": ("black-forest-labs/flux-1-kontext-max", 1214, lambda p, f: {"prompt": p, "input_image": f, "aspect_ratio": "4:5",
                                                                             "output_format": "png"}),
}

WHAT = ("This is a hand-painted watercolour portrait of a real woman on cream textured paper. Make one change to it and "
        "nothing else.\n\n")
KEEP_FACE = ("Her face stays exactly as painted, stroke for stroke: the same wide heart-shaped face and high forehead, the "
             "same hairline and centre part, the two slightly different eyebrows, the same eyes, nose, open smile and teeth, "
             "the thin dark glasses, the warm peach skin with pink cheeks and freckles. ")
KEEP_HAIR = ("Her hair stays exactly as painted: every strand and wisp, the same shape, length, colour and brushwork. ")
KEEP_REST = ("Her head keeps its size, tilt and position. The white cropped jacket with its orange band, pale-blue disc and "
             "round '1420 MHz' sleeve patch, the black mock-neck top, her pose, the plum blossom, the ink mountains and the "
             "paper all stay exactly as they are. Same framing: do not crop, zoom, move or extend the picture. It stays the "
             "same hand-painted watercolour on the same textured paper, not a photo, not digital art, not anime. Do not "
             "beautify, slim, smooth, age or restyle her; no makeup; nothing added.")

HAIR = {
    "gloss": ("THE CHANGE: repaint only her hair so that it reads as healthy, glossy, natural hair. Keep its length, the centre "
              "part, the high hairline, the long face-framing strands swept to both sides and the way it falls over her "
              "shoulders and jacket. Paint it in confident watercolour as smooth, flowing locks with weight and body: soft "
              "wet-on-wet washes of deep warm brown-black, with clear soft bands of light where the hair curves over the crown "
              "and along its lengths (the paper left lighter there, a gentle sheen), a few fine single strands, and soft "
              "natural edges. Take away the dry, stringy, scratchy ink-line look, the wet-looking separated strands and the "
              "frizzy flyaway wisps round the outline. It should look like well-brushed real hair catching the light.\n\n"),
    "natural": ("THE CHANGE: repaint only her hair so that it looks more natural and alive. Keep its length, the centre part, "
                "the high hairline, the long face-framing strands swept to both sides, its loose, slightly tousled fall over "
                "her shoulders and jacket, and a few stray wisps. Give it natural volume and softness: strands gathered into "
                "soft locks instead of thin scratchy lines, gentle changes of tone from deep brown-black in the shadows to a "
                "lighter warm brown where the light falls, and a subtle natural sheen along the curves (not a strong shine). "
                "It should look like real, soft, healthy hair painted in watercolour, less stringy and less flat than now.\n\n"),
}
FACE = {
    "e1_soft": ("THE CHANGE: only her expression. Instead of the wide open smile showing her teeth, she has a small, soft, "
                "closed-lip smile: lips together, the corners gently lifted. Her cheeks relax a little to go with it. "),
    "e2_trace": ("THE CHANGE: only her expression. Instead of the wide open smile showing her teeth, her lips are closed and "
                 "relaxed, with only the faintest trace of warmth at the corners of the mouth: almost neutral, calm and "
                 "thoughtful. Her cheeks relax to go with it. "),
    "e3_neutral": ("THE CHANGE: only her expression. She is not smiling: her lips are closed and relaxed in a neutral line, her "
                   "cheeks relaxed, her face calm and composed, with a steady, quietly determined look at the viewer. Not sad "
                   "and not angry; her forehead stays smooth. "),
    "e4_tense": ("THE CHANGE: only her expression. She is not smiling: she looks serious and a little tense, like someone "
                 "wide awake the night before something that matters. Lips closed, jaw set a little, a watchful, resolute "
                 "look straight at the viewer. Her forehead stays smooth, no frown lines; not angry and not sad. "),
}
FACE_TAIL = ("Everything else about her face stays exactly as painted, stroke for stroke: the same wide heart-shaped face and "
             "high forehead, the same hairline, the two slightly different eyebrows, the same eye shape and eye colour, the "
             "same nose, lip shape and lip colour, the thin dark glasses, the warm peach skin with pink cheeks and "
             "freckles. She is the same person, instantly recognisable.\n\n")


def prompt_for(kind, var):
    if kind == "hair":
        return WHAT + HAIR[var] + KEEP_FACE + KEEP_REST
    return WHAT + FACE[var] + FACE_TAIL + KEEP_HAIR + KEEP_REST


# round -> [(kind, variant, model, n)]
ROUNDS = {
    1: [("hair", "gloss", m, 1) for m in ("nbp", "gpt", "sdr", "grok", "kontext")]
       + [("hair", "natural", m, 1) for m in ("nbp", "gpt", "sdr")]
       + [("face", v, m, 1) for v in FACE for m in ("nbp", "gpt")]
       + [("face", v, "sdr", 1) for v in ("e2_trace", "e3_neutral")],
}


def crop_for(short):
    from PIL import Image
    rows = MODELS[short][1]
    p = os.path.join(OUT, "_in", f"crop_{rows}.png")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        Image.open(SRC).convert("RGB").crop((0, 0, W0, rows)).save(p)
    return p


def gen_one(kind, var, short, dry):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    model, rows, mk = MODELS[short]
    i = 1
    while os.path.exists(os.path.join(OUT, f"{kind}_{var}__{short}_{i}.json")):
        i += 1
    key = f"{kind}_{var}__{short}_{i}"
    prompt = prompt_for(kind, var)
    crop = crop_for(short)
    inp = mk(prompt, "file:" + os.path.relpath(crop, ROOT))
    tag = f"v4A_still_{kind}"
    try:
        est, why = cf.estimate(model, inp)
        paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
    except Exception as e:  # one model failing must not lose the rest of the batch
        print(f"[fail] {key}: {str(e)[:300]}", file=sys.stderr)
        return key, None
    if dry:
        return key, est
    json.dump({"key": key, "kind": kind, "variant": var, "model": model, "prompt": prompt, "tag": tag,
               "input": os.path.relpath(crop, ROOT), "input_rows": [0, rows], "src": os.path.relpath(SRC, ROOT),
               "request": {k: v for k, v in inp.items() if k not in ("prompt", "image", "images", "image_input", "input_image")},
               "est_usd": est, "est_basis": why, "out": [os.path.relpath(x, ROOT) for x in paths]},
              open(os.path.join(OUT, key + ".json"), "w"), indent=1)
    return key, est


def gen(argv):
    o = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    dry = "--dry-run" in argv
    want = [a for a in argv if not a.startswith("--")]
    jobs = []
    for kind, var, short, n in ROUNDS[int(o.get("round", 1))]:
        if want and not any(w in f"{kind}_{var}__{short}" for w in want):
            continue
        jobs += [(kind, var, short, dry)] * n
    os.makedirs(OUT, exist_ok=True)
    for s in {j[2] for j in jobs}:
        crop_for(s)
    with ThreadPoolExecutor(int(o.get("jobs", 6))) as ex:
        res = list(ex.map(lambda j: gen_one(*j), jobs))
    tot = sum(e for _, e in res if e)
    print(json.dumps(res, indent=1))
    print(f"{len(res)} calls, {sum(1 for _, e in res if e is None)} failed, est ${tot:.2f}{' (dry run)' if dry else ''}")


# ---------------------------------------------------------------------------------------------- contact sheets
STABLE = [33, 133, 362, 263, 168, 6, 197, 195, 5, 4, 1, 98, 327, 10, 151, 9, 127, 356, 234, 454]   # eyes, nose, brow, temples


def sheet(argv):
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mouth as MT

    src = np.asarray(Image.open(SRC).convert("RGB"))
    L0 = MT.detect(src, (0, 0, W0, H0))[0]
    io0 = np.linalg.norm(L0[33] - L0[263])
    cands = []
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".json") and "__" in f:
            d = json.load(open(os.path.join(OUT, f)))
            if d.get("out") and os.path.exists(os.path.join(ROOT, d["out"][0])):
                cands.append(d)
    metrics, warped = {}, {"current": src}
    for d in cands:
        a = np.asarray(Image.open(os.path.join(ROOT, d["out"][0])).convert("RGB"))
        r = MT.detect(a, (0, 0, a.shape[1], a.shape[0]))
        if r is None:
            print("no face:", d["key"]); continue
        L, bs = r
        M, _ = cv2.estimateAffinePartial2D(L[STABLE].astype(np.float32), L0[STABLE].astype(np.float32), method=cv2.LMEDS)
        s = float(np.hypot(M[0, 0], M[0, 1]))
        w = cv2.warpAffine(a, M, (W0, H0), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LANCZOS4, borderValue=(246, 237, 226))
        Lw = L @ M[:, :2].T + M[:, 2]
        up = [i for i in range(468) if L0[i, 1] < L0[2, 1]]             # everything above the nose base
        d_up = np.linalg.norm(Lw[up] - L0[up], axis=1) / io0 * 100
        metrics[d["key"]] = {"model": d["model"], "px_per_portrait_px": round(1 / s, 3),
                             "upper_face_shift_pct_io_mean": round(float(d_up.mean()), 2),
                             "upper_face_shift_pct_io_max": round(float(d_up.max()), 2),
                             "smile": round((bs.get("mouthSmileLeft", 0) + bs.get("mouthSmileRight", 0)) / 2, 3),
                             "jawOpen": round(bs.get("jawOpen", 0), 3),
                             "mouth_width_ratio": round(float(np.linalg.norm(Lw[61] - Lw[291]) / np.linalg.norm(L0[61] - L0[291])), 3)}
        warped[d["key"]] = w
        Image.fromarray(w).save(os.path.join(OUT, "_in", d["key"] + "_aligned.jpg"), quality=95)
    json.dump(metrics, open(os.path.join(OUT, "metrics.json"), "w"), indent=1)
    for k, v in metrics.items():
        print(k, v)

    def font(sz):
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    def build(name, keys, box, cols, tile_w, labels):
        x0, y0, x1, y1 = box
        th = round(tile_w * (y1 - y0) / (x1 - x0))
        rows = -(-len(keys) // cols)
        pad, lab = 14, 54
        S = Image.new("RGB", (cols * (tile_w + pad) + pad, rows * (th + lab + pad) + pad), (28, 28, 30))
        dr = ImageDraw.Draw(S)
        for i, k in enumerate(keys):
            t = Image.fromarray(warped[k][y0:y1, x0:x1]).resize((tile_w, th), Image.LANCZOS)
            x, y = pad + (i % cols) * (tile_w + pad), pad + (i // cols) * (th + lab + pad)
            S.paste(t, (x, y + lab))
            dr.text((x + 4, y + 2), labels[k][0], fill=(255, 255, 255), font=font(26))
            dr.text((x + 4, y + 31), labels[k][1], fill=(170, 170, 175), font=font(17))
        p = os.path.join(OUT, name)
        S.save(p, quality=92)
        print(p, S.size)

    short = {v[0]: k for k, v in MODELS.items()}
    nice = {"nbp": "nano-banana-pro", "gpt": "gpt-image-2.5", "sdr": "seedream-5-pro", "grok": "grok-imagine-2", "kontext": "flux-kontext-max"}
    for kind, name, box, cols, tw in (("hair", "sheet_hair.jpg", (60, 20, 910, 1060), 5, 520),
                                      ("face", "sheet_face.jpg", (215, 150, 745, 720), 5, 520)):
        ks = [d["key"] for d in cands if d["kind"] == kind and d["key"] in warped]
        ks.sort(key=lambda k: (k.split("__")[0], list(MODELS).index(k.split("__")[1].rsplit("_", 1)[0])))
        letters = {}
        for i, k in enumerate(ks):
            d = next(c for c in cands if c["key"] == k)
            letters[k] = (f"{'H' if kind == 'hair' else 'F'}{i + 1}  {d['variant']}", nice[short[d['model']]])
        letters["current"] = ("NOW (v3 look)", "inputs/jade_watercolor_jacket_v6")
        build(name, ["current"] + ks, box, cols, tw, letters)
        json.dump({v[0].split()[0]: k for k, v in letters.items()}, open(os.path.join(OUT, name.replace(".jpg", "_keys.json")), "w"), indent=1)


if __name__ == "__main__":
    {"gen": gen, "sheet": sheet}[sys.argv[1]](sys.argv[2:])
