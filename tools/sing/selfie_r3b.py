#!/usr/bin/env python3
"""Selfie round 3b (Jade, 2026-10-16): "hybrid's fuller hair looks good, model del has right posture". Start from the round-3
model edit (selfie_r3_pick_model.png = r3/nb2_4: right posture, shoulders, framing, collar) and
  1. hair:   a model makes her hair a little fuller and smoother, like the gpt_4 take (r3/gpt_4.png, hair reference only);
             same length, part, colour and placement (locks in front of the shoulders); nothing else changes
  2. face:   her exact face from inputs/light_makeup_irl.png pasted back (oval to the hairline + glasses band, feathered,
             landmark-aligned, light freckle conceal only), the mask CLIPPED above the jaw/chin line so the collar, its
             snaps and the turtleneck edge stay the model edit's (Jade: "the hybrid erased part of the collar")
  3. patch:  pad right (+ a little left / bottom) and outpaint the rest of her left sleeve with the complete '1420 MHz'
             patch; the composite's own pixels pasted back over everything it shows (as tools/sing/v5_outpaint.py)

    PY=~/Documents/1-music-shipped/moongazing/.venv/bin/python
    MPY=~/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python
    $PY  tools/sing/selfie_r3b.py gen KEY ...                  hair edits, KEY = <nb2|nbp|gpt>_<n>     (tags selfie_r3b_hair_<m>)
    $MPY tools/sing/selfie_r3b.py face KEY ...                 -> r3b/face_<KEY>.png (2x photo frame)
    $MPY tools/sing/selfie_r3b.py canvas KEY                   -> r3b/_in/canvas_<KEY>.png (face_<KEY> on the padded canvas)
    $PY  tools/sing/selfie_r3b.py outpaint KEY OPKEY ...       OPKEY = <nb2|nbp>_<n>  (tags selfie_r3b_outpaint_<m>)
    $MPY tools/sing/selfie_r3b.py merge KEY OPKEY              -> r3b/fin_<KEY>__<OPKEY>.png
    $MPY tools/sing/selfie_r3b.py check                        -> media/sing/selfie/contact_sheet_r3b.jpg (+ collar row,
                                                                  posture), r3b/metrics_r3b.json, r3b/posture_r3b.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selfie_dress as SD  # noqa: E402
import selfie_r3 as R3  # noqa: E402

ROOT = SD.ROOT
SRC = R3.SRC                                                       # inputs/light_makeup_irl.png (512x683)
OUT = os.path.join(SD.OUT, "r3b")
EDIT = os.path.join(SD.OUT, "selfie_r3_pick_model.png")            # r3/nb2_4, 1792x2400
HYB = os.path.join(SD.OUT, "selfie_r3_pick_hybrid.png")            # r3/hyb_gpt_4
HAIR_REF = os.path.join(SD.OUT, "r3", "gpt_4.png")                 # the fuller hair Jade liked
POSE_MODEL = os.path.expanduser("~/Documents/1-archive/rewind-music-video/tools/roto/models/pose_landmarker_heavy.task")
# outpaint canvas (in the 2x photo frame, 1024x1366): 4:5 for nano-banana, composite placed at (PAD_L, 0)
PAD_L, CANVAS_W, CANVAS_H = 64, 1280, 1600

HAIR = (
    "IMAGE 1 is a real photo of a woman in a white jacket; it is the photo to edit. IMAGE 2 is only a hair reference: the "
    "same woman with slightly fuller, smoother hair.\n\n"
    "Make one change to IMAGE 1: make her hair a little fuller and smoother, with more body and a soft natural sheen, like "
    "the hair in IMAGE 2. Keep the same length, the same centre part, the same black-brown colour and the same placement: "
    "both long locks hang down in front of her shoulders exactly where they are in IMAGE 1, over the jacket's front. A few "
    "flyaways may be smoothed.\n\n"
    "Everything else in IMAGE 1 stays exactly as it is, pixel for pixel: her face, skin, makeup, eyebrows, eyes, glasses, "
    "expression and head position; her posture and shoulders; the white jacket with its stand-up collar and its two snaps "
    "beside her chin, the black turtleneck neckline, the epaulets, orange bands, blue disc and the patch; the room, the "
    "light, the framing and crop. The hair must not cover or redraw the collar or the turtleneck. Take only the hair "
    "style from IMAGE 2: not her face, not the jacket, not the framing. It stays the same real phone photo.")
OUTPAINT = (
    "This is a real photograph of a woman that has been placed on a larger canvas: the flat light-grey areas on the right, "
    "on the left and along the bottom are empty canvas, not part of the photo. Fill them in so the photograph simply "
    "continues past its old edges, as if the camera had been a little further back. On the right side of the image, "
    "complete her left shoulder and upper arm in the same white jacket: the sleeve continues down from the epaulet, the "
    "orange band continues around the sleeve, and the round white patch with a thick black ring on that upper sleeve is "
    "complete, a full circle reading '1420' above 'MHz' in bold black letters. On the left side her other sleeve continues "
    "the same way with its orange band, and at the bottom the jacket, zip and black turtleneck continue down. Her long "
    "dark hair hangs in front of her shoulders as it does. The background continues the same room: the light beige wall, "
    "the same light. Do not change anything that is already in the photograph: her face, glasses, hair, the collar, the "
    "visible jacket and turtleneck stay exactly as they are. Same lighting, colour, sharpness and grain; no retouching, no "
    "extra people or objects, no text other than the patch.")

HAIR_MODELS = {
    "nb2": ("google/nano-banana-2", lambda e, r: {"prompt": HAIR, "aspect_ratio": "3:4", "resolution": "2K",
                                                   "output_format": "png", "image_input": [e, r]}),
    "nbp": ("google/nano-banana-pro", lambda e, r: {"prompt": HAIR, "aspect_ratio": "3:4", "image_size": "2K",
                                                     "output_format": "png", "image_input": [e, r]}),
    "gpt": ("openai/gpt-image-2.5-flare", lambda e, r: {"prompt": HAIR, "size": "1024x1536", "quality": "high",
                                                         "output_format": "png", "images": [e, r]}),
}
OP_MODELS = {
    "nb2": ("google/nano-banana-2", lambda c: {"prompt": OUTPAINT, "aspect_ratio": "4:5", "resolution": "2K",
                                                "output_format": "png", "image_input": [c]}),
    "nbp": ("google/nano-banana-pro", lambda c: {"prompt": OUTPAINT, "aspect_ratio": "4:5", "image_size": "2K",
                                                  "output_format": "png", "image_input": [c]}),
}


def rel(p):
    return os.path.relpath(p, ROOT)


def prep():
    from PIL import Image
    os.makedirs(os.path.join(OUT, "_in"), exist_ok=True)
    e = Image.open(EDIT).convert("RGB")
    e.save(os.path.join(OUT, "_in", "edit.jpg"), quality=95)
    w, h = e.size
    x0 = (w - h * 2 // 3) // 2
    e.crop((x0, 0, x0 + h * 2 // 3, h)).save(os.path.join(OUT, "_in", "edit_crop2x3.jpg"), quality=95)
    Image.open(HAIR_REF).convert("RGB").save(os.path.join(OUT, "_in", "hair_ref.jpg"), quality=95)


def _gen(keys, models, build, tagp, dry, extra=None):
    sys.path.insert(0, os.path.join(ROOT, "tools/gen"))
    import cf
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image

    def one(key):
        short = key.split("_")[-2] if "__" in key else key.split("_")[0]
        model, mk = models[short]
        if os.path.exists(os.path.join(OUT, f"{key}.json")) and not dry:
            print("exists, skipped:", key); return key, None
        inp = build(short, mk, key)
        tag = f"{tagp}_{short}"
        try:
            est, why = cf.estimate(model, inp)
            paths = cf.generate(model, inp, os.path.join(OUT, key + ".png"), tag=tag, dry_run=dry)
        except Exception as e:  # noqa: BLE001
            print(f"[fail] {key}: {str(e)[:400]}", file=sys.stderr); return key, None
        if not dry:
            json.dump({"key": key, "model": model, "tag": tag, "prompt": inp.get("prompt"),
                       "inputs": [x for x in (inp.get("image_input") or inp.get("images") or [])],
                       "request": {k: v for k, v in inp.items() if k not in ("prompt", "images", "image_input")},
                       "est_usd": est, "est_basis": why, "out": [rel(x) for x in paths],
                       "out_size": list(Image.open(paths[0]).size), **(extra or {})},
                      open(os.path.join(OUT, key + ".json"), "w"), indent=1)
        return key, est

    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(one, keys))
    print(json.dumps(res), f"est ${sum(e for _, e in res if e):.3f}{' (dry run)' if dry else ''}")


def gen(argv):
    prep()
    keys = [a for a in argv if not a.startswith("--")]

    def build(short, mk, key):
        e = "file:" + rel(os.path.join(OUT, "_in", "edit_crop2x3.jpg" if short == "gpt" else "edit.jpg"))
        return mk(e, "file:" + rel(os.path.join(OUT, "_in", "hair_ref.jpg")))
    _gen(keys, HAIR_MODELS, build, "selfie_r3b_hair", "--dry-run" in argv)


def widen(argv):
    """gpt-image only sees a 2:3 centre crop of the model edit. Put its hair edit back into the model edit's full frame
    (registered by the face; ~2 px body shift measured), feathered 40 px inside the crop edges, so the sides
    (sleeves, part of the patch) stay the model edit's own pixels. -> r3b/full_<KEY>.png"""
    import cv2
    import numpy as np
    from PIL import Image
    import tint_match as T
    e = T.load(EDIT)
    Le = T.landmarks(e)
    for key in [a for a in argv if not a.startswith("--")]:
        d = json.load(open(os.path.join(OUT, key + ".json")))
        a = T.load(os.path.join(ROOT, d["out"][0]))
        M, _ = to_edit_frame(a, Le)
        w = cv2.warpAffine(a, M, (e.shape[1], e.shape[0]), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        valid = cv2.warpAffine(np.ones(a.shape[:2], np.float32), M, (e.shape[1], e.shape[0]), flags=cv2.INTER_NEAREST)
        valid = cv2.GaussianBlur(cv2.erode(valid, np.ones((3, 3), np.uint8), iterations=40), (0, 0), 14)
        out = (w * valid[..., None] + e * (1 - valid[..., None]) + 0.5).astype(np.uint8)
        name = "full_" + key
        Image.fromarray(out).save(os.path.join(OUT, name + ".png"))
        json.dump({"key": name, "model": f"{d['model']} hair edit put back into the model edit's full frame", "base": key,
                   "est_usd": 0, "out": [rel(os.path.join(OUT, name + ".png"))]}, open(os.path.join(OUT, name + ".json"), "w"), indent=1)
        print("wrote", name)


# ---------------------------------------------------------------------------------------------- 2. face back
def face(argv):
    SD.hybrid(argv, cand_dir=OUT, look=R3.conceal_only, src_path=SRC, sharpen=0, edge_tone_only=True, crop_invalid=True,
              clip_jaw=True, band_in_oval=True, prefix="face_",
              label="her exact face (light_makeup_irl) on the hair edit, mask clipped above the jaw; light conceal only")


# ---------------------------------------------------------------------------------------------- 3. patch outpaint
def wall(a):
    import numpy as np
    return np.median(a[60:300, -120:].reshape(-1, 3), 0)          # the plain wall at the top right of the frame


def canvas(argv):
    import numpy as np
    from PIL import Image
    key = argv[0]
    a = np.asarray(Image.open(os.path.join(OUT, f"face_{key}.png")).convert("RGB"))
    h, w = a.shape[:2]
    c = np.zeros((CANVAS_H, CANVAS_W, 3), np.uint8)
    c[:] = np.clip(wall(a) * 0.92 + 8, 0, 255).astype(np.uint8)
    c[:h, PAD_L:PAD_L + w] = a
    os.makedirs(os.path.join(OUT, "_in"), exist_ok=True)
    Image.fromarray(c).save(os.path.join(OUT, "_in", f"canvas_{key}.png"))
    json.dump({"key": key, "canvas": [CANVAS_W, CANVAS_H], "x0": PAD_L, "y0": 0, "size": [w, h]},
              open(os.path.join(OUT, "_in", f"canvas_{key}.json"), "w"))
    print("canvas", key, (CANVAS_W, CANVAS_H), "composite", (w, h), "at x", PAD_L)


def outpaint(argv):
    key, opkeys = argv[0], [a for a in argv[1:] if not a.startswith("--")]
    keys = [f"op_{key}__{k}" for k in opkeys]

    def build(short, mk, k):
        return mk("file:" + rel(os.path.join(OUT, "_in", f"canvas_{key}.png")))
    _gen(keys, OP_MODELS, build, "selfie_r3b_outpaint", "--dry-run" in argv, extra={"composite": f"face_{key}"})


def merge(argv):
    """Register the outpaint on the canvas by her face (similarity), then paste the composite back over everything it
    shows, ~25 px feathered inward; only the new margins come from the model."""
    import cv2
    import numpy as np
    from PIL import Image
    import tint_match as T
    key, op = argv[0], argv[1]
    meta = json.load(open(os.path.join(OUT, "_in", f"canvas_{key}.json")))
    ref = np.asarray(Image.open(os.path.join(OUT, "_in", f"canvas_{key}.png")).convert("RGB"))
    d = json.load(open(os.path.join(OUT, f"op_{key}__{op}.json")))
    o = np.asarray(Image.open(os.path.join(ROOT, d["out"][0])).convert("RGB").resize((CANVAS_W, CANVAS_H), Image.LANCZOS))
    L0, L1 = T.landmarks(ref), T.landmarks(o)
    M, _ = cv2.estimateAffinePartial2D(L1[T.STABLE].astype(np.float32), L0[T.STABLE].astype(np.float32), method=cv2.LMEDS)
    o = cv2.warpAffine(o, M, (CANVAS_W, CANVAS_H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    drift = np.linalg.norm((L1 @ M[:, :2].T + M[:, 2]) - L0, axis=1)
    x0, (w, h) = meta["x0"], meta["size"]
    keep = np.zeros((CANVAS_H, CANVAS_W), np.float32)
    keep[:h, x0:x0 + w] = 1
    # the cut-off patch at the composite's right edge: hand that whole zone to the model, or the half patch and the
    # model's whole patch ghost into each other ("1420" doubled). Found as the dark ring pixels in the right 100 px.
    comp = ref[:h, x0:x0 + w]
    strip = comp[:, w - 100:].astype(int).sum(2) < 180
    rows = np.where(strip.mean(1) > 0.08)[0]
    rows = rows[rows > h // 2]
    patch_box = None
    if len(rows):
        py0, py1 = max(0, rows.min() - 40), min(h, rows.max() + 40)
        keep[py0:py1, x0 + w - 220:x0 + w] = 0
        patch_box = [int(x0 + w - 220), int(py0), int(x0 + w), int(py1)]
    top = keep[:1].copy()                     # the photo's top edge is the frame edge: no feather needed there
    keep = cv2.erode(keep, np.ones((3, 3), np.uint8), iterations=12)
    keep[:12][:, x0 + 12:x0 + w - 12] = top[:, x0 + 12:x0 + w - 12]
    keep = cv2.GaussianBlur(keep, (0, 0), 8)
    out = (ref * keep[..., None] + o * (1 - keep[..., None]) + 0.5).astype(np.uint8)
    name = f"fin_{key}__{op}"
    Image.fromarray(out).save(os.path.join(OUT, name + ".png"))
    band = (keep > 0.05) & (keep < 0.95)
    step = float(np.abs(o[band].astype(float) - ref[band].astype(float)).mean())
    json.dump({"key": name, "model": f"final: face_{key} + outpaint {d['model']}", "est_usd": 0, "out": [rel(os.path.join(OUT, name + ".png"))],
               "outpaint_face_drift_px_mean": round(float(drift.mean()), 2), "outpaint_face_drift_px_max": round(float(drift.max()), 2),
               "seam_band_mean_abs_diff": round(step, 1), "patch_zone_from_model": patch_box}, open(os.path.join(OUT, name + ".json"), "w"), indent=1)
    print(name, "drift", round(float(drift.mean()), 2), round(float(drift.max()), 2), "seam step", round(step, 1))


def collar(argv):
    """Jade: "the model edit has the correct collar". Put the model edit's own collar back on a finished candidate: the
    edit is mapped onto the candidate by the face, refined by phase correlation on the collar box, and pasted inside a
    feathered box from just below the jaw (the face mask's clip line) to below the lower snap, between the hair locks.
    -> r3b/col_<KEY>.png"""
    import cv2
    import numpy as np
    from PIL import Image
    import tint_match as T
    e = T.load(EDIT)
    Le = T.landmarks(e)
    for key in [a for a in argv if not a.startswith("--")]:
        a = T.load(os.path.join(OUT, key + ".png"))
        La = T.landmarks(a)
        M, _ = cv2.estimateAffinePartial2D(Le[T.STABLE].astype(np.float32), La[T.STABLE].astype(np.float32), method=cv2.LMEDS)
        io = float(np.linalg.norm(La[33] - La[263]))
        cx, cy = La[152]
        x0, x1, y0, y1 = int(cx - 0.62 * io), int(cx + 0.62 * io), int(cy - 0.1 * io), int(cy + 1.0 * io)
        w = cv2.warpAffine(e, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        ga = cv2.cvtColor(a[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float32)
        gw = cv2.cvtColor(w[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float32)
        (dx, dy), resp = cv2.phaseCorrelate(gw, ga, cv2.createHanningWindow(ga.shape[::-1], cv2.CV_32F))
        M2 = M.copy(); M2[:, 2] += (dx, dy)
        w = cv2.warpAffine(e, M2, (a.shape[1], a.shape[0]), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        m = np.zeros(a.shape[:2], np.float32)
        m[y0:y1, int(cx - 0.45 * io):int(cx + 0.52 * io)] = 1
        m *= 1 - SD.jaw_clip(a.shape, La, io, inset=0.0)            # nothing above the jaw line: her pasted face stays
        m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8), iterations=6), (0, 0), 5)
        out = (w * m[..., None] + a * (1 - m[..., None]) + 0.5).astype(np.uint8)
        name = "col_" + key
        Image.fromarray(out).save(os.path.join(OUT, name + ".png"))
        Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(OUT, "_in", name + "_mask.png"))
        json.dump({"key": name, "model": f"{key} with the model edit's collar pasted back", "base": key, "est_usd": 0,
                   "collar_refine_px": [round(dx, 2), round(dy, 2)], "collar_refine_response": round(float(resp), 3),
                   "out": [rel(os.path.join(OUT, name + ".png"))]}, open(os.path.join(OUT, name + ".json"), "w"), indent=1)
        print("wrote", name, "refine", round(dx, 2), round(dy, 2), "resp", round(float(resp), 3))


# ---------------------------------------------------------------------------------------------- checks
_POSE = None


def pose(rgb):
    global _POSE
    import mediapipe as mp
    import numpy as np
    from mediapipe.tasks.python import BaseOptions, vision
    if _POSE is None:
        _POSE = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=POSE_MODEL), num_poses=1))
    r = _POSE.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    if not r.pose_landmarks:
        return None
    lm = r.pose_landmarks[0]
    H, W = rgb.shape[:2]
    return np.array([[lm[i].x * W, lm[i].y * H] for i in range(len(lm))])


def to_edit_frame(a, Le):
    """Similarity map of image a onto the model edit by its face; returns (M, landmarks)."""
    import cv2
    import numpy as np
    import tint_match as T
    L = T.landmarks(a)
    M, _ = cv2.estimateAffinePartial2D(L[T.STABLE].astype(np.float32), Le[T.STABLE].astype(np.float32), method=cv2.LMEDS)
    return M, L


def posture_collar(paths):
    """Posture vs the model edit (in the 2x photo frame's px = edit px x 1024/1792): shoulder points (pose 11/12) after
    mapping by the face, shoulder-line angle, and the head's own position/scale in the frame. Collar: mean abs RGB diff
    in the collar box (between the jaw corners, chin to below the snaps) after the same mapping."""
    import cv2
    import numpy as np
    from PIL import Image
    import tint_match as T
    e = T.load(EDIT)
    Le, Pe = T.landmarks(e), pose(e)
    k = 1024 / e.shape[1]
    io = float(np.linalg.norm(Le[33] - Le[263]))
    cx0, cx1 = int(Le[152, 0] - 0.58 * io), int(Le[152, 0] + 0.58 * io)     # the stand-up collar, snaps, turtleneck edge
    cy0, cy1 = int(Le[152, 1] - 0.15 * io), int(Le[152, 1] + 0.95 * io)
    by0 = int(Le[152, 1] + 0.5 * io)                                          # jacket/body region for the posture shift
    win = cv2.createHanningWindow((e.shape[1], e.shape[0] - by0), cv2.CV_32F)
    ge = cv2.cvtColor(e[by0:], cv2.COLOR_RGB2GRAY).astype(np.float32)
    res, crops = {}, {}
    for key, p in paths:
        a = T.load(p)
        M, L = to_edit_frame(a, Le)
        P = pose(a)
        w = cv2.warpAffine(a, M, (e.shape[1], e.shape[0]), flags=cv2.INTER_AREA, borderValue=(28, 28, 30))
        crops[key] = w[cy0:cy1, cx0:cx1]
        r = {}
        # posture: with the head registered, how far the jacket/body below the chin has moved (phase correlation)
        gw = cv2.cvtColor(w[by0:], cv2.COLOR_RGB2GRAY).astype(np.float32)
        (dx, dy), resp = cv2.phaseCorrelate(ge, gw, win)
        r["body_shift_px"] = [round(dx * k, 1), round(dy * k, 1)]
        r["body_shift_response"] = round(float(resp), 3)
        if P is not None:
            Pw = P @ M[:, :2].T + M[:, 2]
            for i, n in ((11, "shoulder_L"), (12, "shoulder_R")):
                r[n + "_shift_px"] = round(float(np.linalg.norm(Pw[i] - Pe[i])) * k, 1)
            ang = lambda Q: np.degrees(np.arctan2(Q[11, 1] - Q[12, 1], Q[11, 0] - Q[12, 0]))
            r["shoulder_angle_change_deg"] = round(float(ang(Pw) - ang(Pe)), 2)
        # head position in the frame (no face fit): eye-midpoint, normalised to each image's width, in edit-2x px
        hp = lambda LL, img: ((LL[33] + LL[263]) / 2) / img.shape[1] * 1024
        r["head_pos_shift_px"] = round(float(np.linalg.norm(hp(L, a) - hp(Le, e))), 1) if a.shape[1] / a.shape[0] == e.shape[1] / e.shape[0] else None
        r["collar_mean_abs_rgb"] = round(float(np.abs(crops[key].astype(int) - e[cy0:cy1, cx0:cx1].astype(int)).mean()), 2)
        res[key] = r
    return res, crops


VERDICT = {      # written after looking at every image (see media/sing/selfie/README.md, round 3b)
    "nb2_1": ("REJECT", "hair barely fuller; collar redrawn (diff 47)"),
    "nb2_2": ("REJECT", "fuller hair but collar redrawn (44)"),
    "nb2_3": ("REJECT", "collar redrawn (43)"),
    "nb2_4": ("REJECT", "collar redrawn (37); hair restyled"),
    "nbp_1": ("REJECT", "collar redrawn (47); body +11px"),
    "nbp_2": ("REJECT", "collar redrawn; body -18px"),
    "nbp_3": ("REJECT", "collar redrawn (41)"),
    "gpt_1": ("OK", "collar kept (11); hair fuller; 2:3 only"),
    "gpt_2": ("OK", "collar kept; lost the blue disc"),
    "gpt_3": ("REJECT", "body -5px; collar 17"),
    "gpt_4": ("PICK", "fuller hair, collar kept (12), body 2px"),
    "full_gpt_2": ("OK", "gpt_2 hair in the edit's full frame"),
    "full_gpt_4": ("OK", "gpt_4 hair in the edit's full frame"),
    "face_nb2_1": ("REJECT", "base collar redrawn"), "face_nb2_2": ("REJECT", "base collar redrawn"),
    "face_nbp_1": ("REJECT", "base collar redrawn"), "face_nbp_2": ("REJECT", "base collar redrawn"),
    "face_gpt_1": ("OK", "her face on gpt_1 (2:3 crop)"),
    "face_full_gpt_2": ("OK", "her face; no blue disc"),
    "face_full_gpt_4": ("OK", "her face on gpt_4 hair, full frame"),
    "op_full_gpt_2__nb2_1": ("OK", "raw outpaint (before paste-back)"),
    "op_full_gpt_2__nbp_1": ("OK", "raw outpaint (before paste-back)"),
    "op_full_gpt_4__nb2_1": ("OK", "raw outpaint (before paste-back)"),
    "op_full_gpt_4__nbp_1": ("OK", "raw outpaint (before paste-back)"),
    "fin_full_gpt_4__nbp_1": ("OK", "patch complete; collar = gpt's"),
    "fin_full_gpt_4__nb2_1": ("OK", "patch ok, small mark by '0'"),
    "fin_full_gpt_2__nb2_1": ("OK", "no blue disc"),
    "fin_full_gpt_2__nbp_1": ("OK", "no blue disc"),
    "col_fin_full_gpt_4__nbp_1": ("PICK", "hair+face+edit collar+full patch"),
    "col_fin_full_gpt_4__nb2_1": ("OK", "small mark by the '0'"),
    "col_fin_full_gpt_2__nb2_1": ("REJECT", "blue disc missing"),
    "col_fin_full_gpt_2__nbp_1": ("REJECT", "blue disc missing"),
}


def check(argv):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    SD.check(argv, cand_dir=OUT, sheet="contact_sheet_r3b.jpg", metrics_name="metrics_r3b.json",
             head=[("r3_model", EDIT), ("r3_hybrid", HYB)],
             verdict={**VERDICT, "r3_model": ("REF", "round-3 model edit (posture, collar)"),
                      "r3_hybrid": ("REF", "round-3 hybrid (hair Jade liked)")},
             src_path=SRC, skin=True, src_label="ORIGINAL light makeup")
    keys = [("r3_model", EDIT), ("r3_hybrid", HYB)]
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".json") and not f.startswith("metrics"):
            d = json.load(open(os.path.join(OUT, f)))
            if d.get("out") and os.path.exists(os.path.join(ROOT, d["out"][0])):
                keys.append((d["key"], os.path.join(ROOT, d["out"][0])))
    keys = keys[:2] + sorted(keys[2:], key=lambda kv: SD._order(kv[0]))
    pc, crops = posture_collar(keys)
    json.dump(pc, open(os.path.join(OUT, "posture_r3b.json"), "w"), indent=1)
    for k, v in pc.items():
        print(f"{k:28s} {v}")
    # collar + posture strip (appended under the sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    tw = 230
    ch = round(tw * next(iter(crops.values())).shape[0] / next(iter(crops.values())).shape[1])
    cols = 10
    rows = -(-len(crops) // cols)
    S = Image.new("RGB", (cols * (tw + 8) + 8, rows * (ch + 52) + 30), (28, 28, 30))
    dr = ImageDraw.Draw(S)
    dr.text((8, 6), "COLLAR crops (mapped onto the model edit by the face; collar = mean abs RGB diff vs the model edit) + body "
            "shift below the chin vs the model edit with the head registered (2x-photo px)",
            fill=(255, 255, 255), font=font)
    for i, (k, c) in enumerate(crops.items()):
        x, y = 8 + (i % cols) * (tw + 8), 30 + (i // cols) * (ch + 52)
        S.paste(Image.fromarray(c).resize((tw, ch), Image.LANCZOS), (x, y + 36))
        v = pc[k]
        dr.text((x, y), k[:30], fill=(255, 255, 255), font=font)
        dr.text((x, y + 17), f"collar {v['collar_mean_abs_rgb']:.1f}  body {v['body_shift_px'][0]:+.0f},{v['body_shift_px'][1]:+.0f}px",
                fill=(170, 170, 175), font=font)
    main = Image.open(os.path.join(SD.OUT, "contact_sheet_r3b.jpg"))
    T_ = Image.new("RGB", (max(main.size[0], S.size[0]), main.size[1] + S.size[1]), (28, 28, 30))
    T_.paste(main, (0, 0)); T_.paste(S, (0, main.size[1]))
    T_.save(os.path.join(SD.OUT, "contact_sheet_r3b.jpg"), quality=90)
    print("sheet", T_.size)


if __name__ == "__main__":
    {"gen": gen, "widen": widen, "collar": collar, "face": face, "canvas": canvas, "outpaint": outpaint, "merge": merge, "check": check}[sys.argv[1]](sys.argv[2:])
