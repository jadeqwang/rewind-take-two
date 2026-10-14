#!/usr/bin/env python
"""Put colour back on pencil tops that the engrave matte dropped (v7, docs/revisions/v7/erasers.md).

tools/engrave keeps Jade in colour through a per-frame segmentation matte (take_N_matte/). In some frames the matte
loses the tops of her bun pencils (a streetlight flash behind them, or a thin silver ferrule), so the eraser and
ferrule there are engraved as world: white paper with hatching, for a few frames (a colour flicker) or for the
whole take (half an eraser white). The raw take still has the colour. This is a pixel pass, no generative model:

  1. repair the matte: per listed frame, add the pencil-top mask, taken from a reference frame where the matte is
     right (matte[ref] inside a box) or from a polygon, moved rigidly with the pencil (ECC, Euclidean, fitted on the
     raw take's gray pixels under the mask, frame to frame from the reference);
  2. re-run tools/engrave/engrave.py on the raw take with --matte-in = the repaired matte (same flags as
     tools/sectionA/engrave_take.sh: --out-height 1080, defaults otherwise). The pipeline is deterministic: outside
     the added mask the re-run differs from the shipped take only by encode noise (~2.5/255 mean);
  3. splice: only inside the added mask (dilated 2 px, feathered) and only in the listed frames does the output take
     the re-run; every other pixel is the shipped take. Encode as the engrave tool (CRF 16, -tune grain, faststart).

  tools/engrave/.venv/bin/python tools/matte_fix.py SPEC.json [--tmp DIR] [--check-only]

Spec: {"raw", "engraved", "matte" (dir of %05d.png), "out", "pencils": [{"name", "ref", "box": [x0,y0,x1,y1]
(1080p px, or a list of boxes; mask = matte[ref] > 127 inside) | "poly": [[x,y],...] (1080p px, in frame ref), "frames":
[i | [a, b]], "grow": px (optional dilation of the mask before use)}],
"halo": px (default 10; the splice reaches this far beyond the gained matte)}.
"""
import argparse
import json
import os
import subprocess
import sys

import av
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from blue_eraser import encode, frames_of  # noqa: E402


def ranges(spec_list):
    out = []
    for r in spec_list:
        a, b = (r, r) if isinstance(r, int) else r
        out += list(range(a, b + 1))
    return sorted(set(out))


def ref_mask(p, mattes, H, W):
    m = np.zeros((H, W), np.uint8)
    if "poly" in p:
        cv2.fillPoly(m, [np.array(p["poly"], np.int32)], 255)
    else:
        ref = mattes(p["ref"])
        for x0, y0, x1, y1 in (p["box"] if isinstance(p["box"][0], list) else [p["box"]]):
            m[y0:y1, x0:x1] = (ref[y0:y1, x0:x1] > 127) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))   # matte notches
    if p.get("grow"):
        k = 2 * p["grow"] + 1
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    return m


def track(raw, mask_out, ref, frames, sx):
    """Rigid (Euclidean) warps ref -> i on the raw take's gray, chained frame to frame from the reference.
    mask_out is the 1080p mask; sx = raw / output scale. Returns {i: 2x3 warp in OUTPUT pixels}."""
    gray = [cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY), (0, 0), 1.0).astype(np.float32) for f in raw]
    m_raw = cv2.resize(mask_out, (raw[0].shape[1], raw[0].shape[0]), interpolation=cv2.INTER_NEAREST)
    m_raw = cv2.dilate(m_raw, np.ones((5, 5), np.uint8))   # the ink outline round the pencil carries the shape
    ys, xs = np.nonzero(m_raw)
    pad = 24
    x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    x1, y1 = min(m_raw.shape[1], xs.max() + pad), min(m_raw.shape[0], ys.max() + pad)
    warps = {ref: np.eye(2, 3, dtype=np.float32)}
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5)
    for step in (1, -1):
        W = np.eye(2, 3, dtype=np.float32)
        i = ref
        while True:
            j = i + step
            if j < 0 or j >= len(raw) or (step > 0 and j > max(frames)) or (step < 0 and j < min(frames)):
                break
            # template: frame i, input: frame j; the mask (valid input pixels) is the pencil where it was in frame i
            mi = cv2.warpAffine(m_raw, W, (m_raw.shape[1], m_raw.shape[0]), flags=cv2.INTER_NEAREST)
            t = gray[i][y0:y1, x0:x1]
            s = gray[j][y0:y1, x0:x1]
            d = np.eye(2, 3, dtype=np.float32)
            try:
                _, d = cv2.findTransformECC(t, s, d, cv2.MOTION_EUCLIDEAN, crit, mi[y0:y1, x0:x1], 5)
            except cv2.error:
                d = np.eye(2, 3, dtype=np.float32)
            # ECC's warp maps template (frame i) coords to input (frame j) coords, in crop pixels: ref -> i -> j
            A = np.vstack([W, [0, 0, 1]])
            off = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]], np.float32)
            W = (np.linalg.inv(off) @ np.vstack([d, [0, 0, 1]]) @ off @ A)[:2].astype(np.float32)
            warps[j] = W.copy()
            i = j
    S = np.array([[1 / sx, 0, 0], [0, 1 / sx, 0], [0, 0, 1]], np.float32)
    Si = np.linalg.inv(S)
    return {k: (S @ np.vstack([w, [0, 0, 1]]) @ Si)[:2].astype(np.float32) for k, w in warps.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--tmp", default="/tmp")
    ap.add_argument("--check-only", action="store_true", help="write the repaired matte + a mask sheet, no engrave")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    J = lambda p: os.path.join(ROOT, p)  # noqa: E731
    raw, fps = frames_of(J(spec["raw"]))
    eng, _ = frames_of(J(spec["engraved"]))
    n = len(eng)
    H, W = eng[0].shape[:2]
    sx = raw[0].shape[1] / W
    mdir = J(spec["matte"])
    mattes = lambda i: cv2.imread(os.path.join(mdir, f"{i:05d}.png"), 0)  # noqa: E731
    add = {}
    for p in spec["pencils"]:
        fr = ranges(p["frames"])
        m0 = ref_mask(p, mattes, H, W)
        warps = track(raw, m0, p["ref"], fr + [p["ref"]], sx)
        for i in fr:
            w = cv2.warpAffine(m0, warps[i], (W, H), flags=cv2.INTER_LINEAR)
            add[i] = np.maximum(add.get(i, 0), w)
        dx = [float(warps[i][0, 2]) for i in fr]
        print(f"{p['name']}: {len(fr)} frames, ref {p['ref']}, mask {int((m0 > 0).sum())} px, "
              f"track dx {min(dx):.1f}..{max(dx):.1f}")
    tag = os.path.splitext(os.path.basename(spec["out"]))[0]
    rep = os.path.join(a.tmp, tag + "_matte")
    os.makedirs(rep, exist_ok=True)
    alpha = {}
    for i in range(n):
        m = mattes(i)
        if i in add:
            new = np.maximum(m, add[i])
            gain = (new.astype(np.int16) - m).clip(0, 255).astype(np.uint8)
            # take the re-run a little beyond the gained matte too: the engraving inked a halo round the
            # dropped pencil top, and the re-run (with the pencil in the matte) has the clean background there
            k = 2 * spec.get("halo", 10) + 1
            g = cv2.dilate(gain, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
            alpha[i] = cv2.GaussianBlur(g.astype(np.float32) / 255, (0, 0), 2.0)[..., None]
            m = new
        cv2.imwrite(os.path.join(rep, f"{i:05d}.png"), m)
    if a.check_only:
        print("matte written to", rep)
        return
    re_path = os.path.join(a.tmp, tag + "_re.mp4")
    subprocess.run([sys.executable, J("tools/engrave/engrave.py"), J(spec["raw"]), re_path, "--out-height", str(H),
                    "--matte-in", os.path.join(rep, "%05d.png"), "--crf", "12"], check=True,
                   stdout=subprocess.DEVNULL)
    re, _ = frames_of(re_path)
    out = []
    for i in range(n):
        f = eng[i]
        if i in alpha:
            f = (f * (1 - alpha[i]) + re[i] * alpha[i] + 0.5).astype(np.uint8)
        out.append(f)
    encode(out, fps, J(spec["out"]), 16, ["-tune", "grain", "-movflags", "+faststart"])
    print(f"wrote {spec['out']}: {n} frames, spliced {len(alpha)} frames")


if __name__ == "__main__":
    main()
