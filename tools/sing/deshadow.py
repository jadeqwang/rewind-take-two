#!/usr/bin/env python3
"""Take the shadow of her glasses off her cheeks (an artifact of the overhead light in the traced photo).
Copied from moongazing-public-version work/singer4/deshadow.py (Jade picked --tint=1.8 there); only paths changed:
KEY is that project's first frame (read-only, the zones are drawn on it), takes live in media/sing/<SHOT>/.

    MPY tools/sing/deshadow.py still IN.jpg OUT.jpg [--dbg=OUT_dbg.jpg] [--flat=1] [--tint=K]   (flat: paint the zone smooth)
    MPY tools/sing/deshadow.py take SHOT take_N take_M [--tint=1]   (writes take_M.mp4 + sidecar, same length and fps;
                                                                     tint: colour back into her face, see tint())

The shadow is the hatched band under each lens: its lower part seen through the lens, and the cheek under the rim.
ZONES are drawn on the first frame (media/keyframes/S_3.4a_os.jpg px; all three first frames share the face to 2 px)
and carried to each frame by an affine fit of the cheek's face-mesh points. Inside a zone a pixel darker than the
lit skin round it is lifted to that skin (a smooth fill from the lit pixels just outside the zone); the frames of the
glasses are much darker than the shadow and are left alone. Nothing outside the two zones changes."""
import json, os, shutil, subprocess, sys
import cv2
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mouth as MT

FF = os.environ.get("FFMPEG", os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg"))
KEY = os.path.expanduser("~/Documents/moongazing-public-version/work/engine/media/keyframes/S_3.4a_os.jpg")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# polygons in 5x-crop coordinates of the first frame: (origin x, origin y), points, (x where the fade starts, x of full strength), lowest y of the glasses frames
ZONES = {
    "l": ((1080, 640), [(500, 387), (600, 339), (700, 309), (850, 284), (1000, 270), (1100, 272), (1148, 300),
                        (1152, 400), (1152, 480), (1125, 545), (1100, 612), (1000, 672), (915, 698), (770, 763),
                        (650, 833), (560, 888), (420, 915), (300, 760), (290, 560), (330, 430), (430, 385)], (300, 520), 545),
    "r": ((1340, 640), [(252, 290), (330, 265), (410, 244), (520, 237), (640, 244), (765, 287), (802, 318),
                        (806, 420), (808, 520), (800, 650), (785, 740), (680, 750), (580, 722), (500, 696),
                        (420, 692), (345, 665), (298, 560), (260, 470), (238, 400)], (-900, -800), 490),
}
RIM = 30                                                    # darker than the lit skin by this much: the frames, not the shadow
LIT = 62                                                    # lit skin: the brighter part of the skin round a zone
PTS = {"l": [117, 118, 119, 100, 101, 50, 36, 142, 126, 47, 121, 120, 123, 116, 111],
       "r": [346, 347, 348, 329, 330, 280, 266, 371, 355, 277, 350, 349, 352, 345, 340]}
RIGID = [33, 133, 362, 263, 168, 6, 197, 195, 127, 356, 10, 151, 9, 8]
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
        150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
_K = None
_Z = None


def key():
    global _K
    if _K is None:
        im = cv2.imread(KEY)
        L, _ = MT.detect(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), (800, 0, 1950, 1300))
        _K = L
    return _K


def lum(a):
    return a[..., 0] * 0.114 + a[..., 1] * 0.587 + a[..., 2] * 0.299


def zone_key():
    """The two zones as soft masks on the first frame (key px), cached: {z: (mask, x0, y0)}."""
    global _Z
    if _Z is None:
        _Z = {}
        for z, ((ox, oy), poly, (xa, xb), yb_max) in ZONES.items():
            P = np.array(poly, np.float32) / 5 + [ox, oy]
            x0, y0 = np.floor(P.min(0)).astype(int) - 40; x1, y1 = np.ceil(P.max(0)).astype(int) + 40
            m = np.zeros((y1 - y0, x1 - x0), np.float32)
            cv2.fillPoly(m, [np.round((P - [x0, y0]) * 8).astype(np.int32)], 1.0, lineType=cv2.LINE_AA, shift=3)
            m = cv2.GaussianBlur(m, (0, 0), 3.0)
            xs = np.arange(x0, x1, dtype=np.float32)          # long fade towards the side of the face
            m *= np.clip((xs - (ox + xa / 5)) / ((xb - xa) / 5), 0, 1)[None, :] ** 1.5
            # where the frames of the glasses run in this zone: thick dark drawing in the first frame, with a margin
            yb = cv2.GaussianBlur(lum(cv2.imread(KEY)[y0:y1, x0:x1].astype(np.float32)), (0, 0), 1.2)
            inz = cv2.dilate((m > 0.02).astype(np.uint8), np.ones((9, 9), np.uint8))
            n, lab, st, _ = cv2.connectedComponentsWithStats(((yb < 152) & (inz > 0)).astype(np.uint8))
            big = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 250]).astype(np.uint8)
            band = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))).astype(np.float32)
            band[max(0, int(oy + yb_max / 5) - y0):] = 0     # only the frames: not the pencil strokes that run on down the cheek
            _Z[z] = (m, band, x0, y0)
    return _Z


def fix(img, L, dbg=None, flat=0.0):
    """img BGR uint8, L face-mesh landmarks in img px. Returns the corrected image."""
    K = key(); H, W = img.shape[:2]
    fh = float(np.linalg.norm(L[10] - L[152])); kfh = float(np.linalg.norm(K[10] - K[152])); s = fh / kfh
    x0, y0 = np.maximum(L.min(0) - 0.15 * fh, 0).astype(int); x1, y1 = np.minimum(L.max(0) + 0.15 * fh, [W, H]).astype(int)
    f = img[y0:y1, x0:x1].astype(np.float32); h, w = f.shape[:2]; off = np.array([x0, y0], np.float32)
    zone = np.zeros((h, w), np.float32); band = np.zeros((h, w), np.float32)
    for z, (m, bd, zx, zy) in zone_key().items():
        A, _ = cv2.estimateAffine2D(K[PTS[z]].astype(np.float32), L[PTS[z]].astype(np.float32), method=cv2.LMEDS)
        A = A.copy(); A[:, 2] += A[:, :2] @ [zx, zy] - off
        zone = np.maximum(zone, cv2.warpAffine(m, A, (w, h), flags=cv2.INTER_LINEAR))
        # the glasses ride on the nose and ears, not on the cheeks (which move with the mouth)
        G, _ = cv2.estimateAffinePartial2D(K[RIGID].astype(np.float32), L[RIGID].astype(np.float32), method=cv2.LMEDS)
        G = G.copy(); G[:, 2] += G[:, :2] @ [zx, zy] - off
        band = np.maximum(band, cv2.warpAffine(bd, G, (w, h), flags=cv2.INTER_LINEAR))
    sk = np.zeros((h, w), np.uint8); cv2.fillPoly(sk, [np.round(L[OVAL] - off).astype(np.int32)], 1)
    Yr = lum(f)
    # thin dark drawing, darker than its own neighbourhood: the frames of the glasses, and the pencil edge and hatching
    # of the shadow itself. Neither goes into the tone under the detail (no halo round the frames).
    line = (cv2.GaussianBlur(Yr, (0, 0), 6.5 * s) - Yr) > (12 + 16 * np.clip((s - 0.46) / 0.54, 0, 1))
    line = cv2.dilate(line.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=max(1, round(1.6 * s))).astype(np.float32)
    sg = max(0.9, 2.6 * s)
    kb = cv2.GaussianBlur(1 - line, (0, 0), sg)
    low = cv2.GaussianBlur(f * (1 - line)[..., None], (0, 0), sg) / np.maximum(kb, 1e-3)[..., None]
    Y = lum(low)
    wide = cv2.dilate((zone > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=max(1, round(8 * s)))
    near = cv2.dilate(wide, np.ones((3, 3), np.uint8), iterations=max(2, round(0.16 * fh)))
    cand = (near > 0) & (wide == 0) & (sk > 0) & (line == 0)
    src = cand & (Y > np.percentile(Y[cand], LIT))
    wsrc = src.astype(np.float32)
    fill = conf = None
    for q in (0.045, 0.09, 0.2):                            # nearest lit skin first, wider where none is near
        den = cv2.GaussianBlur(wsrc, (0, 0), q * fh)
        num = cv2.GaussianBlur(low * wsrc[..., None], (0, 0), q * fh) / np.maximum(den, 1e-6)[..., None]
        c = np.clip(den / 0.06, 0, 1)[..., None]
        fill, conf = (num, c) if fill is None else (fill * conf + num * (1 - conf), np.maximum(conf, c))
    fill = cv2.GaussianBlur(fill, (0, 0), 0.02 * fh)
    d = lum(fill) - Y
    # the frames are far darker than the shadow: they keep their own pixels and only take the tone change of the skin
    # under them. The shadow's own pencil lines are painted out to the lit skin.
    core = ((((lum(fill) - Yr) > RIM) & (band > 0.5)) | ((lum(fill) - Yr) > RIM + 60)).astype(np.uint8)
    rim = cv2.dilate(core, np.ones((3, 3), np.uint8), iterations=max(1, round(1.5 * s))).astype(np.float32)
    faint = cv2.GaussianBlur(line * (1 - rim), (0, 0), max(0.5, 1.0 * s))[..., None]
    faint = np.maximum(faint, flat * (1 - rim)[..., None])   # flat=1 (stills): every pixel of the zone is painted to the lit skin
    base = low * (1 - faint) + f * faint
    de = lum(fill) - lum(base)                              # at a pencil line of the shadow: how dark the line itself is
    a = zone * np.clip((de - 1.5) / 5.0, 0, 1) * (1 - np.clip((d - 48) / 14, 0, 1)) * sk
    a = cv2.GaussianBlur(a, (0, 0), max(0.5, 1.2 * s))
    out = img.copy(); out[y0:y1, x0:x1] = np.clip(f + (fill - base) * a[..., None], 0, 255).astype(np.uint8)
    if dbg:
        v = lambda m: cv2.cvtColor(np.clip(m * 255, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        cv2.imwrite(dbg, np.hstack([f.astype(np.uint8), out[y0:y1, x0:x1], np.clip(fill, 0, 255).astype(np.uint8), v(a), v(wsrc), v(zone), v(band), v(rim)]))
    return out


PINK = (186.0, 170.0, 214.0)                               # the headphones, BGR (measured on the takes)
SKIN = (0.70, 0.82, 1.0)                                   # warm skin, BGR proportions (hue about 22 degrees, quiet)
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
EYE_R = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
EYE_L = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]


def tint(img, L, k=1.0, dbg=None):
    """A little colour back into her face: a warm skin tone over the whole face, and a soft pink (towards the headphones)
    on the cheekbones. k = strength (1 = light). Lightness is kept: only the colour of a pixel moves."""
    if k <= 0:
        return img
    H, W = img.shape[:2]
    fh = float(np.linalg.norm(L[10] - L[152]))
    x0, y0 = np.maximum(L.min(0) - 0.45 * fh, 0).astype(int); x1, y1 = np.minimum(L.max(0) + 0.2 * fh, [W, H]).astype(int)
    f = img[y0:y1, x0:x1].astype(np.float32); h, w = f.shape[:2]; off = np.array([x0, y0], np.float32)
    up = (L[10] - L[152]) / fh; side = np.array([-up[1], up[0]])           # unit vectors: up the face, across it
    c = (L[33] + L[263]) / 2
    P = L[OVAL].copy()
    for i, p in enumerate(P):                               # the mesh stops short of her hairline: carry the mask up over the
        a = float((p - c) @ up) / fh                        # high forehead (the dark hair is gated out by lightness below)
        if a > 0:
            P[i] = p + up * fh * 0.30 * min(1.0, a / 0.25)
    m = np.zeros((h, w), np.float32)
    cv2.fillPoly(m, [np.round((P - off) * 8).astype(np.int32)], 1.0, lineType=cv2.LINE_AA, shift=3)
    for e, sgn in ((234, 1), (454, -1)):                    # the ears
        q = L[e] - off + sgn * side * 0.0 - up * 0.02 * fh
        d = L[e] - c; d = d / (np.linalg.norm(d) + 1e-6)
        cv2.circle(m, tuple(np.round((q + d * 0.07 * fh) * 8).astype(int)), int(0.115 * fh * 8), 1.0, -1, cv2.LINE_AA, 3)
    m = cv2.GaussianBlur(m, (0, 0), 0.018 * fh)
    Y = lum(f); r, b = f[..., 2], f[..., 0]
    skin = np.clip((Y - 120) / 35, 0, 1) * np.clip((r - b + 14) / 14, 0, 1)   # light and not blue: skin, not hair, sky or frames
    skin = cv2.GaussianBlur(skin, (0, 0), max(0.6, 0.006 * fh))
    m = m * skin
    # 1. skin tone: each pixel's colour moves part of the way to one warm skin colour of the same lightness (the three
    #    shots come out of the video model with different greys; this also brings them together). Lips and eyes keep theirs.
    hole = np.zeros((h, w), np.float32)
    for idx in (LIPS, EYE_R, EYE_L):
        cv2.fillPoly(hole, [np.round((L[idx] - off) * 8).astype(np.int32)], 1.0, lineType=cv2.LINE_AA, shift=3)
    hole = cv2.GaussianBlur(hole, (0, 0), max(0.6, 0.008 * fh))
    sk = np.array(SKIN, np.float32); sk = sk / lum(sk[None, None])[0, 0]
    a = np.clip(0.30 * k * m * (1 - hole), 0, 0.8)[..., None]
    g = f * (1 - a) + (Y[..., None] * sk) * a
    # 2. cheekbones: a soft patch under the outer half of each lens, tilted up towards the ear
    blush = np.zeros((h, w), np.float32); yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for ia, ib, ic in ((50, 205, 123), (280, 425, 352)):
        q = 0.72 * L[ia] + 0.28 * L[ib] - off
        ax = L[ic] - L[ia]; ax = ax / (np.linalg.norm(ax) + 1e-6); ay = np.array([-ax[1], ax[0]])
        u = (xx - q[0]) * ax[0] + (yy - q[1]) * ax[1]; v = (xx - q[0]) * ay[0] + (yy - q[1]) * ay[1]
        blush = np.maximum(blush, np.exp(-0.5 * ((u / (0.10 * fh)) ** 2 + (v / (0.06 * fh)) ** 2)))
    blush = blush * m * np.clip((Y - 135) / 30, 0, 1)
    pink = np.array(PINK, np.float32); pink = pink / lum(pink[None, None])[0, 0]
    a = np.clip(0.24 * k * blush, 0, 0.6)[..., None]
    g = g * (1 - a) + (lum(g)[..., None] * pink) * a
    g = g * (Y / np.maximum(lum(g), 1e-3))[..., None]       # lightness as it was
    out = img.copy(); out[y0:y1, x0:x1] = np.clip(g, 0, 255).astype(np.uint8)
    if dbg:
        v8 = lambda x: cv2.cvtColor(np.clip(x * 255, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        cv2.imwrite(dbg, np.hstack([f.astype(np.uint8), out[y0:y1, x0:x1], v8(m), v8(blush)]))
    return out


def find(rgb, prev):
    H, W = rgb.shape[:2]
    if prev is not None:
        x0, y0, x1, y1 = prev
        for k in (0.8, 1.0, 0.65, 1.3, 1.8):
            cx, cy, s = (x0 + x1) / 2, (y0 + y1) / 2, k * max(x1 - x0, y1 - y0)
            hit = MT.detect(rgb, (max(0, cx - s), max(0, cy - s), min(W, cx + s), min(H, cy + s)))
            if hit is not None:
                return hit[0]
    for b in MT.grid_boxes(W, H):
        hit = MT.detect(rgb, b)
        if hit is not None:
            return hit[0]
    return None


def still(src, dst, dbg=None, flat=1.0, tk=0.0):
    im = cv2.imread(src); L = find(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), None)
    cv2.imwrite(dst, tint(fix(im, L, dbg, flat), L, tk), [cv2.IMWRITE_JPEG_QUALITY, 96]); print(dst)


def take(shot, a, b, tk=0.0):
    d = os.path.join(ROOT, "media/sing", shot) + "/"; cap = cv2.VideoCapture(d + a + ".mp4"); fps = cap.get(cv2.CAP_PROP_FPS)
    tmp = d + b + "_png"; os.makedirs(tmp, exist_ok=True)
    Ls = []; frames = []
    prev = None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        L = find(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), prev)
        if L is not None:
            prev = [L[:, 0].min(), L[:, 1].min(), L[:, 0].max(), L[:, 1].max()]
        Ls.append(L); frames.append(f)
    miss = [i for i, L in enumerate(Ls) if L is None]
    ok = [i for i, L in enumerate(Ls) if L is not None]
    A = np.array([Ls[i] for i in ok])                       # (n, 478, 2)
    # landmarks jitter by a pixel from frame to frame: smooth them over 5 frames (the head moves slowly)
    full = np.empty((len(Ls), 478, 2))
    for j in range(478):
        for c in range(2):
            full[:, j, c] = np.interp(np.arange(len(Ls)), ok, A[:, j, c])
    k = np.array([1, 2, 3, 2, 1], float); k /= k.sum()
    pad = np.concatenate([full[:1].repeat(2, 0), full, full[-1:].repeat(2, 0)])
    sm = sum(k[i] * pad[i:i + len(Ls)] for i in range(5))
    for i, f in enumerate(frames):
        cv2.imwrite(f"{tmp}/{i:04d}.png", tint(fix(f, sm[i]), sm[i], tk))
    out = d + b + ".mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", f"{fps:g}", "-i", tmp + "/%04d.png", "-c:v", "libx264", "-crf", "10",
                    "-preset", "slow", "-pix_fmt", "yuv420p", out], check=True)
    shutil.rmtree(tmp)
    S = json.load(open(d + a + ".json")); n = int(b.split("_")[1])
    S.update(take=n, file=out, est_usd=0, est_basis="derived locally, no paid call", derived_from=a, job=None, raw_file=None,
             notes=f"{a} with the glasses shadow taken off the cheeks" + (f" and colour in the face (tint {tk:g})" if tk else "") + " (tools/sing/deshadow.py)")
    S.pop("ff_r", None); S.pop("ff_shift_px", None)
    json.dump(S, open(d + b + ".json", "w"), indent=1, ensure_ascii=False)
    print(out, "frames", len(frames), "no face in", len(miss))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]; o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--"))
    if a[0] == "still":
        still(a[1], a[2], o.get("dbg"), float(o.get("flat", 1)), float(o.get("tint", 0)))
    else:
        take(a[1], a[2], a[3], float(o.get("tint", 0)))
