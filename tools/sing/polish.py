#!/usr/bin/env python3
"""Polish pass on the picked singing takes (rough-cut review v1, top-10 item 5). No new generation: every frame is the
approved take's own frame (likeness and lip sync unchanged).

  1. headphones pale pink -> canon orange #F08A24: keyed once on frame 0 (pink, low saturation, in a box under the
     lips round the neck, outside the face oval; cheek blush, lips, hair and the warm paper are the same hue, hence
     the box), carried through the take on a jaw/chin landmark fit, recoloured to the jacket band's hue and
     colored-pencil saturation at each pixel's own value;
  2. push in 1.3x: a fixed 985x554 window of the 1280x720 take (same for all three shots so they still rhyme), the
     selfie sleeve and lower band cropped off, upscaled to 1920x1080 (Lanczos);
  3. --grain: the engine's E3 treatment baked in (render/engine/src/shaders.js: grain .045 at 1.2 px boiling on twos,
     paper fibre .18), for shots whose timeline does not add it (S1, V3S; E3 gets it from Section D's fx).

    MPY=~/Documents/orbital-sunrise-video/video/out/.venv/bin/python
    $MPY tools/sing/polish.py SHOT TAKE [--grain] [--wide] [--still=T]
        TAKE e.g. take_1_lips. The first run moves TAKE.mp4 to TAKE_orig.mp4 (the backup); every run reads _orig and
        writes TAKE.mp4 in place, same frame count and fps. --wide: no push-in, written to TAKE_wide.mp4 (for a push
        that targets the old framing, e.g. S2). --still=T: write one frame at T s to media/sing/review/ and stop.
    $MPY tools/sing/polish.py remap-mask IN.png OUT.png    # a matte drawn on the old framing -> the pushed-in framing
"""
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deshadow as DS  # noqa: E402

ROOT = DS.ROOT
X0, Y0, CW, CH = 113, 20, 985, 554          # push-in window in 1280x720 take pixels (1.3x)
OUT_W, OUT_H = 1920, 1080
ORANGE = np.array([0x24, 0x8A, 0xF0], np.float32)  # BGR of #F08A24
HP_HUE = (232, 14)                           # OpenCV HSV_FULL hue (0-255) band of her pale-pink headphones (wraps)


def lum(a):
    return a[..., 0] * 0.114 + a[..., 1] * 0.587 + a[..., 2] * 0.299


JAW = [152, 148, 377, 176, 400, 172, 397, 136, 365, 58, 288, 1, 4]


def hp_mask0(img, L):
    """The headphones on one frame: pink-ish, low-saturation pixels in a box set from the face (below the lips, round
    the neck), outside the face oval; small holes (the pencil lines on the cups) filled."""
    H, W = img.shape[:2]
    fh = float(np.linalg.norm(L[10] - L[152]))
    nx, chin, lip = L[1][0], L[152][1], L[17][1]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    key = ((h >= HP_HUE[0]) | (h <= HP_HUE[1])) & (s >= 25) & (s <= 75) & (v >= 165)   # hair is darker
    box = np.zeros((H, W), bool)
    box[int(lip - 0.10 * fh):int(min(H, chin + 0.45 * fh)), int(max(0, nx - 0.58 * fh)):int(min(W, nx + 0.38 * fh))] = True
    face = np.zeros((H, W), np.uint8)
    cv2.fillPoly(face, [np.round(L[DS.OVAL]).astype(np.int32)], 1)
    face = cv2.dilate(face, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(0.05 * fh) | 1,) * 2))
    m = (key & box & (face == 0)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 0.01 * fh * fh]).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    inv = (1 - m).astype(np.uint8)
    ff = inv.copy(); cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 0)
    m = m | ff                                            # holes inside the cups
    return (m & (face == 0)).astype(np.float32)


def hp_mask(m0, L0, L):
    """Carry the frame-0 headphone mask to this frame on the jaw and chin (they rest on her neck)."""
    A, _ = cv2.estimateAffinePartial2D(L0[JAW].astype(np.float32), L[JAW].astype(np.float32), method=cv2.LMEDS)
    w = cv2.warpAffine(m0, A, (m0.shape[1], m0.shape[0]), flags=cv2.INTER_LINEAR)
    face = np.zeros(m0.shape, np.uint8)
    cv2.fillPoly(face, [np.round(L[DS.OVAL]).astype(np.int32)], 1)
    w = w * (1 - cv2.GaussianBlur(face.astype(np.float32), (0, 0), 1.5))
    return cv2.GaussianBlur(w, (0, 0), 1.2)


def recolour(img, w):
    """Hue and saturation of the jacket's orange band (#F08A24 as drawn in colored pencil), the pixel's own value."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL).astype(np.float32)
    v = hsv[..., 2]
    o = np.stack([np.full_like(v, 19), np.clip(150 * (0.55 + 0.45 * v / 255), 0, 255), v * 0.98], -1)
    o = cv2.cvtColor(o.astype(np.uint8), cv2.COLOR_HSV2BGR_FULL).astype(np.float32)
    a = w[..., None]
    return np.clip(img.astype(np.float32) * (1 - a) + o * a, 0, 255).astype(np.uint8)


def push(img):
    c = img[Y0:Y0 + CH, X0:X0 + CW]
    return cv2.resize(c, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)


def wide(img):
    return cv2.resize(img, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)


def _hash(x, y, seed):
    """Deterministic per-cell hash in [0,1) (integer mix, not the shader's sin hash; same statistics)."""
    h = (x.astype(np.int64) * 374761393 + y.astype(np.int64) * 668265263 + int(seed) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(0x1000000)


def _fbm(W, H, sx, sy, seed, oct=4):
    out = np.zeros((H, W), np.float32)
    amp, tot = 0.5, 0.0
    for o in range(oct):
        fx, fy = sx * 2 ** o, sy * 2 ** o
        gw, gh = int(W * fx) + 2, int(H * fy) + 2
        gy, gx = np.mgrid[0:gh, 0:gw]
        g = _hash(gx, gy, seed + 17 * o).astype(np.float32)
        out += amp * cv2.resize(g, (int(gw / fx), int(gh / fy)), interpolation=cv2.INTER_CUBIC)[:H, :W]
        tot += amp
        amp *= 0.5
    return out / tot


_PAPER = None


def paper_grain(img, frame, paper=0.18, grain=0.045, size=1.2):
    global _PAPER
    H, W = img.shape[:2]
    if _PAPER is None:     # static paper fibre, long in y like the engine's (px * (.012, .03))
        f = _fbm(W, H, 0.012, 0.03, 7) - 0.5
        yy, xx = np.mgrid[0:H, 0:W]
        fine = _hash((xx * 0.7).astype(int), (yy * 0.7).astype(int), 11) - 0.5
        _PAPER = (1 + paper * (f * 0.22 + fine * 0.06)).astype(np.float32)
    c = img.astype(np.float32) / 255 * _PAPER[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    g = (_hash((xx / size).astype(int), (yy / size).astype(int), 1000 + frame // 2) - 0.5).astype(np.float32)
    l = lum(c)
    c += (g * grain * (0.35 + 1.3 * l * (1 - l)))[..., None]
    return np.clip(c * 255, 0, 255).astype(np.uint8)


def frames_landmarks(frames):
    Ls, prev = [], None
    for f in frames:
        L = DS.find(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), prev)
        if L is not None:
            prev = [L[:, 0].min(), L[:, 1].min(), L[:, 0].max(), L[:, 1].max()]
        Ls.append(L)
    ok = [i for i, L in enumerate(Ls) if L is not None]
    A = np.array([Ls[i] for i in ok])
    full = np.empty((len(Ls), 478, 2))
    for j in range(478):
        for c in range(2):
            full[:, j, c] = np.interp(np.arange(len(Ls)), ok, A[:, j, c])
    return full, len(Ls) - len(ok)


def run(shot, take, grain=False, wide_out=False, still=None):
    d = os.path.join(ROOT, "media/sing", shot)
    cur, orig = os.path.join(d, take + ".mp4"), os.path.join(d, take + "_orig.mp4")
    if not os.path.exists(orig):
        shutil.copy2(cur, orig)
        print("backup", os.path.relpath(orig, ROOT))
    cap = cv2.VideoCapture(orig)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    idx = range(len(frames)) if still is None else [min(len(frames) - 1, round(still * fps))]
    Ls, miss = frames_landmarks(frames)
    m0 = hp_mask0(frames[0], Ls[0])
    geo = wide if wide_out else push
    outs = []
    for i in idx:
        g = geo(recolour(frames[i], hp_mask(m0, Ls[0], Ls[i])))
        if grain:
            g = paper_grain(g, i)
        outs.append(g)
    if still is not None:
        p = os.path.join(ROOT, "media/sing/review", f"polish_{shot}_{take}{'_wide' if wide_out else ''}_{still:.2f}.jpg")
        cv2.imwrite(p, outs[0], [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(p)
        return
    out = os.path.join(d, take + ("_wide" if wide_out else "") + ".mp4")
    tmp = out[:-4] + "_png"
    os.makedirs(tmp, exist_ok=True)
    for k, g in enumerate(outs):
        cv2.imwrite(f"{tmp}/{k:04d}.png", g)
    subprocess.run([DS.FF, "-y", "-loglevel", "error", "-framerate", f"{fps:g}", "-i", tmp + "/%04d.png", "-c:v", "libx264",
                    "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p", out], check=True)
    shutil.rmtree(tmp)
    print(os.path.relpath(out, ROOT), "frames", len(outs), "no face in", miss)


def remap_mask(src, dst):
    """A 1920x1080 matte drawn on the old (uncropped) framing -> the pushed-in framing."""
    m = cv2.imread(src, 0)
    s = m.shape[1] / 1280
    c = m[int(Y0 * s):int((Y0 + CH) * s), int(X0 * s):int((X0 + CW) * s)]
    cv2.imwrite(dst, cv2.resize(c, (OUT_W, OUT_H), interpolation=cv2.INTER_LINEAR))
    print(dst)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict((x[2:].split("=", 1) + [""])[:2] for x in sys.argv[1:] if x.startswith("--"))
    if a[0] == "remap-mask":
        remap_mask(a[1], a[2])
    else:
        run(a[0], a[1], "grain" in o, "wide" in o, float(o["still"]) if o.get("still") else None)
