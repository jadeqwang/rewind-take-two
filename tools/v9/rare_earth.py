#!/usr/bin/env python3
"""v9 fix 11 (Jade 3:40): "RARE EARTH" lettering on the jacket back, under the pale-blue dot.

Canon (inputs/jade_in_outfit.png, BACK): small dark-grey sans-serif capitals, centred under the dot, about the dot's
diameter wide. Measured on the sheet (dot diameter D = 57 px): cap height 0.11 D, gap dot -> caps 0.14 D, text width
~1.0 D, ink ~(36-55) grey.

Per frame (same tracking idea as tools/jacket_back.py's "anchor": the existing blue dot is the anchor):
  1. track the dot: the pale-blue blob nearest the previous frame's dot, ellipse-fitted (centre, axes, angle). The dot is
     printed on the same panel as the lettering, so the unit circle -> fitted ellipse map carries the panel's position,
     scale, foreshortening and tilt; the lettering is placed in that dot frame (canonical units: dot radius = 1);
  2. lettering: rendered once at high resolution (spec font/tracking), inverse-mapped per pixel at 4x supersampling
     (optionally with a slight bow, "bow": sagitta in dot radii, + = smile), area-averaged to frame resolution;
  3. painted as a multiply onto the fabric: letter = pixel * (ink / local jacket white). The pixel's own shading,
     pencil grain and engraved hatching therefore carry through the letters (a hatch stroke is still darker inside a
     letter, a shadowed fold darkens the letters with it). Only jacket-bright regions take ink (a closed luminance mask,
     so thin hatch lines inside the panel are not treated as occluders, but hair/arm/outline masses are), so anything
     dark in front stays in front;
  4. strength follows the dot's own contrast (the doorway wash at the end of the take fades dot and letters alike).

    $PY tools/v9/rare_earth.py SPEC                         # write spec["out"]
    $PY tools/v9/rare_earth.py SPEC --compare 0,50,100 --outdir DIR [--zoom 3] [--name N]
    $PY tools/v9/rare_earth.py SPEC --track-only            # print the per-frame dot fit
$PY = tools/engrave/.venv/bin/python (cv2, av, numpy, PIL).
"""
import argparse
import json
import math
import os
import subprocess

import av
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/jade/Documents/rewind-take-two"
FFMPEG = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/"
                            "imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")


def frames(path):
    c = av.open(path)
    for f in c.decode(video=0):
        yield f.to_ndarray(format="rgb24")
    c.close()


# ---------------------------------------------------------------- 1. dot tracking
_OCC = {}


def occluder(spec, shape):
    """static foreground occluder (spec "occ": {"poly": [[x, y], ...], "grow": px, "feather": px}), 0..1 float, cached.
    For a locked-off camera (V2b3: the driver's seat bolster in front of her): letters there are hidden and dot
    contour points next to it are not used for the ellipse fit."""
    o = spec.get("occ")
    if not o:
        return None
    if "m" not in _OCC:
        m = np.zeros(shape, np.uint8)
        cv2.fillPoly(m, [np.array(o["poly"], np.int32)], 255)
        g = int(o.get("grow", 3))
        if g:
            m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * g + 1, 2 * g + 1)))
        m = m.astype(np.float32) / 255
        if o.get("feather", 1.0) > 0:
            m = cv2.GaussianBlur(m, (0, 0), o.get("feather", 1.0))
        _OCC["m"] = m
        _OCC["dist"] = cv2.distanceTransform((m < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    return _OCC["m"]


def find_dot(img, prev, spec):
    """ellipse fit of the pale-blue dot nearest `prev` -> dict(c, ax, ang, con) or None"""
    a = img.astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    win = spec.get("win", 130)
    x0, y0 = max(int(prev[0] - win), 0), max(int(prev[1] - win), 0)
    x1, y1 = int(prev[0] + win), int(prev[1] + win)
    for dbr, bmin in ((40, 140), (22, 190), (14, 205)):          # strict first; relaxed for the washed-out frames
        m = ((B - R > dbr) & (B > bmin) & (G > 120))[y0:y1, x0:x1].astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        idx = [k for k in range(1, n) if st[k, 4] >= spec.get("min_area", 1500)]
        if not idx:
            continue
        k = min(idx, key=lambda k: np.hypot(*(cen[k] + [x0, y0] - prev)) - st[k, 4] / 40)
        blob = (lab == k).astype(np.uint8)
        blob = cv2.morphologyEx(blob, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = max(cnts, key=cv2.contourArea)
        if len(cnt) < 20:
            continue
        occ = occluder(spec, img.shape[:2])
        if occ is not None:          # fit the visible arc only: drop contour points against the occluder
            pts = cnt[:, 0, :] + [x0, y0]
            keep = _OCC["dist"][pts[:, 1], pts[:, 0]] > spec["occ"].get("gap", 6)
            if keep.sum() >= 20:
                cnt = cnt[keep]
        (cx, cy), (w, h), ang = cv2.fitEllipse(cnt)
        inside = blob.astype(bool)
        con = float(np.median((B - R)[y0:y1, x0:x1][inside]))
        return dict(c=[cx + x0, cy + y0], ax=[w / 2, h / 2], ang=ang, con=con)
    return None


def find_rib(img, d, spec):
    """slope (deg, + = down to the right) of the hem rib's top outline under the dot: per column, the first dark row
    below the dot (luminance blurred along x so the rib's stripes merge), robust line fit. None if not found."""
    cx, cy = d["c"]
    rx, ry = d["ax"]
    lum = cv2.blur(img.astype(np.float32).mean(-1), (7, 1))
    y0 = int(cy + spec.get("rib_from", 1.25) * ry)
    y1 = int(cy + spec.get("rib_to", 3.2) * ry)
    pts = []
    for x in range(int(cx - 0.8 * rx), int(cx + 0.8 * rx)):
        idx = np.nonzero(lum[y0:y1, x] < spec.get("rib_lum", 150))[0]
        if len(idx):
            pts.append((x, idx[0] + y0))
    if len(pts) < 10:
        return None
    pts = np.array(pts, float)
    keep = np.ones(len(pts), bool)
    for _ in range(4):
        p = np.polyfit(pts[keep, 0], pts[keep, 1], 1)
        r = pts[:, 1] - np.polyval(p, pts[:, 0])
        keep = np.abs(r) < max(2.5, np.median(np.abs(r[keep])) * 2.5)
    return float(np.degrees(np.arctan(p[0])))


def find_hem(img, d, spec):
    """slope (deg, + = down to the right) of the jacket's bottom (hem) outline below the dot, for a cropped jacket whose
    hem has no striped rib (V2b3): per column, the first dark run below the dot that has bright jacket just above it,
    columns behind the occluder skipped; robust line fit. None unless at least spec["hem_min"] columns agree."""
    cx, cy = d["c"]
    rx, ry = d["ax"]
    lum = cv2.blur(img.astype(np.float32).mean(-1), (5, 1))
    occ = occluder(spec, img.shape[:2])
    x0, x1 = spec.get("hem_x", [-1.6, 2.1])
    pts = []
    for x in range(int(cx + x0 * rx), int(cx + x1 * rx), 3):
        if x < 0 or x >= img.shape[1]:
            continue
        for y in range(int(cy + spec.get("hem_from", 1.0) * ry), min(img.shape[0] - 3, int(cy + 3 * ry))):
            if occ is not None and _OCC["dist"][y, x] < 6:
                break
            if (lum[y:y + 3, x] < spec.get("hem_lum", 70)).all():
                if lum[y - 6:y - 2, x].mean() > spec.get("hem_bright", 160):
                    pts.append((x, y))
                break
    if len(pts) < 6:
        return None
    pts = np.array(pts, float)
    keep = np.ones(len(pts), bool)
    for _ in range(5):
        p = np.polyfit(pts[keep, 0], pts[keep, 1], 1)
        r = pts[:, 1] - np.polyval(p, pts[:, 0])
        keep = np.abs(r) < max(3, np.median(np.abs(r[keep])) * 2.5)
    if keep.sum() < spec.get("hem_min", 30):
        return None
    return float(np.degrees(np.arctan(p[0])))


def track(clip, spec):
    prev = np.array(spec["start"], float)
    out = []
    for img in frames(clip):
        d = find_dot(img, prev, spec)
        if d:
            d["rib"] = find_hem(img, d, spec) if spec.get("rot") == "hem" else find_rib(img, d, spec)
            prev = np.array(d["c"])
        out.append(d)
    return out


def normalise(tr, spec):
    """angle wrapped to (-90, 90] for the width axis; light smoothing of axes/angle (not the centre: the take moves on
    twos and jumps, a smoothed centre would lag); per-frame strength from the dot's contrast"""
    n = len(tr)
    ok = [i for i in range(n) if tr[i]]
    ang = np.array([((tr[i]["ang"] + 90) % 180) - 90 for i in ok])
    ax = np.array([tr[i]["ax"] for i in ok])
    con = np.array([tr[i]["con"] for i in ok])
    sig = spec.get("smooth", 1.0)
    if sig > 0 and len(ok) > 3:
        k = np.exp(-0.5 * (np.arange(-3, 4) / sig) ** 2)
        k /= k.sum()
        pad = lambda v: np.concatenate([v[:1].repeat(3, 0), v, v[-1:].repeat(3, 0)])
        # cut the smoothing at hard jumps (a cut inside the take): segment where the centre jumps > jump px
        cs = np.array([tr[i]["c"] for i in ok])
        brk = [0] + [j for j in range(1, len(ok)) if np.hypot(*(cs[j] - cs[j - 1])) > spec.get("jump", 60)] + [len(ok)]
        for s0, s1 in zip(brk[:-1], brk[1:]):
            for arr in (ang, ax[:, 0], ax[:, 1]):
                seg = pad(arr[s0:s1].astype(float))
                arr[s0:s1] = np.convolve(seg, k, "valid")
    rib = np.array([tr[i]["rib"] if tr[i].get("rib") is not None else np.nan for i in ok])
    good = ~np.isnan(rib)
    rib = np.interp(np.arange(len(rib)), np.nonzero(good)[0], rib[good]) if good.any() else np.zeros(len(rib))
    rs = spec.get("rib_smooth", 3.0)
    if rs > 0:
        k = np.exp(-0.5 * (np.arange(-9, 10) / rs) ** 2)
        k /= k.sum()
        rib = np.convolve(np.concatenate([rib[:1].repeat(9), rib, rib[-1:].repeat(9)]), k, "valid")
    ref = float(np.median(con[: max(5, len(con) // 2)]))
    res = [None] * n
    for j, i in enumerate(ok):
        res[i] = dict(c=tr[i]["c"], ax=ax[j].tolist(), ang=float(ang[j]), rib=float(rib[j]),
                      s=float(np.clip((con[j] / ref - spec.get("wash_floor", 0.0)) / (1 - spec.get("wash_floor", 0.0)), 0, 1)))
    rk = spec.get("rot")
    if isinstance(rk, dict):         # keyframed baseline angle {"frame": deg}, linear in between
        kk = sorted(int(k) for k in rk)
        for i in range(n):
            if res[i]:
                res[i]["rot_key"] = float(np.interp(i, kk, [rk[str(k)] for k in kk]))
    sk = spec.get("shift_u")
    if isinstance(sk, dict):         # keyframed shift along the baseline {"frame": dot radii}
        kk = sorted(int(k) for k in sk)
        for i in range(n):
            if res[i]:
                res[i]["shift_key"] = float(np.interp(i, kk, [sk[str(k)] for k in kk]))
    if spec.get("frames"):
        for i in range(n):
            if not any(a <= i <= b for a, b in spec["frames"]):
                res[i] = None
    for i in spec.get("skip", []):
        res[i] = None
    for i, o in spec.get("override", {}).items():
        if res[int(i)]:
            res[int(i)].update(o)
    return res


# ---------------------------------------------------------------- 2. lettering art
def glyphs(spec):
    """high-res coverage mask of the text, tight to the cap box; returns (mask float32, cap_h_px, width_px)"""
    font = ImageFont.truetype(spec.get("font", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"), 400)
    text = spec.get("text", "RARE EARTH")
    track = spec.get("tracking", 0.12) * 400
    word = spec.get("word_space", 1.0)
    xs, x = [], 0.0
    for ch in text:
        xs.append(x)
        adv = font.getlength(ch) * (word if ch == " " else 1.0)
        x += adv + track
    W = int(x + 200)
    im = Image.new("L", (W, 800), 0)
    d = ImageDraw.Draw(im)
    for ch, cx in zip(text, xs):
        d.text((100 + cx, 200), ch, font=font, fill=255)
    a = np.asarray(im, np.float32) / 255
    ys, xs_ = np.nonzero(a > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs_.min(), xs_.max() + 1
    return a[y0:y1, x0:x1].copy()


# ---------------------------------------------------------------- 3. paint
def letter(img, spec, d, art):
    """img HxWx3 uint8 RGB, d = dot fit -> painted copy, plus the coverage (for overlays)"""
    H, W = img.shape[:2]
    rx, ry = d["ax"]
    tw = spec.get("width", 2.05)                       # text width in dot radii (dot diameter = 2)
    ah, aw = art.shape
    capw = tw
    caph = tw * ah / aw
    top = 1.0 + spec.get("gap", 0.28)                  # cap top, in dot radii below the dot centre
    # baseline angle: "rib" = parallel to the hem rib a few px below (smoothed), "dot" = the dot ellipse's tilt,
    # or a number = fixed; "rot_add" adds a constant
    rs = spec.get("rot", "rib")
    rot = d["rot_key"] if isinstance(rs, dict) else d["rib"] if rs in ("rib", "hem") else d["ang"] if rs == "dot" else float(rs)
    rot += spec.get("rot_add", 0.0) + d.get("rot_add", 0.0)
    # where "below the dot" is: perpendicular to the baseline ("base"), along the dot's axis ("dot") or straight down
    adir = spec.get("anchor_dir", "base")
    aang = math.radians(rot if adir == "base" else d["ang"] if adir == "dot" else 0.0)
    # the dot frame used for placement: centre shifted so the canonical "below" runs along aang
    th = math.radians(rot)
    if spec.get("scale_dir"):
        # scale from the dot's semi-diameters ALONG the baseline and perpendicular to it (not its fitted axes, whose
        # orientation is arbitrary for a near-round dot): the lettering foreshortens with the dot, without shear
        e = math.radians(d["ang"])
        sd = lambda phi: 1.0 / math.sqrt((math.cos(phi - e) / d["ax"][0]) ** 2 + (math.sin(phi - e) / d["ax"][1]) ** 2)
        rx, ry = sd(th), sd(th + math.pi / 2)
    A = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]) @ np.diag([rx, ry])
    Ai = np.linalg.inv(A)
    mid = top + caph / 2
    want = np.array(d["c"]) + np.array([-math.sin(aang), math.cos(aang)]) * mid * ry
    got = np.array(d["c"]) + A @ np.array([0.0, mid])
    cx, cy = np.array(d["c"]) + (want - got) + np.array(d.get("nudge", [0.0, 0.0]))
    if spec.get("conj"):
        # proper affine image of the dot's circle: canonical x along the baseline direction (the ellipse's semi-diameter
        # that way), canonical y along its CONJUGATE semi-diameter (the panel's own "down" under perspective/shear)
        e = math.radians(d["ang"])
        ea, eb = d["ax"]
        bl = th - e                                     # baseline angle in the ellipse's own frame
        t0 = math.atan2(ea * math.sin(bl), eb * math.cos(bl))
        Re = np.array([[math.cos(e), -math.sin(e)], [math.sin(e), math.cos(e)]])
        u = Re @ np.array([ea * math.cos(t0), eb * math.sin(t0)])
        v = Re @ np.array([-ea * math.sin(t0), eb * math.cos(t0)])
        if u @ np.array([math.cos(th), math.sin(th)]) < 0:
            u, v = -u, -v
        # (u, v) keeps det > 0, so the lettering is never mirrored; with u pointing along the baseline, v points down
        A = np.stack([u, v], 1)
        Ai = np.linalg.inv(A)
        # "shift_u": slide the lettering along the baseline by this many dot radii (constant, so it stays printed on the
        # fabric; used where the canon centring would put half of it behind an occluder)
        cx, cy = np.array(d["c"]) + u * d.get("shift_key", spec.get("shift_u", 0.0) if not isinstance(spec.get("shift_u"), dict) else 0.0) \
            + np.array(d.get("nudge", [0.0, 0.0]))
    bow = spec.get("bow", 0.0)
    # bounding box in frame px
    corners = np.array([[-capw / 2, top - 0.1], [capw / 2, top - 0.1], [-capw / 2, top + caph + 0.1 + abs(bow)],
                        [capw / 2, top + caph + 0.1 + abs(bow)]]) @ A.T + [cx, cy]
    bx0, by0 = np.floor(corners.min(0)).astype(int) - 3
    bx1, by1 = np.ceil(corners.max(0)).astype(int) + 3
    bx0, by0, bx1, by1 = max(bx0, 0), max(by0, 0), min(bx1, W), min(by1, H)
    SS = 4
    yy, xx = np.mgrid[0:(by1 - by0) * SS, 0:(bx1 - bx0) * SS].astype(np.float32)
    P = np.stack([(xx + 0.5) / SS + bx0 - cx, (yy + 0.5) / SS + by0 - cy], -1)
    U = P @ Ai.T                                       # frame px -> dot units
    u, v = U[..., 0], U[..., 1]
    v = v - bow * (1 - (2 * u / capw) ** 2)            # bow: baseline sags (smile) by `bow` at the centre
    mx = ((u + capw / 2) / capw * aw).astype(np.float32)
    my = ((v - top) / caph * ah).astype(np.float32)
    cov = cv2.remap(art, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    cov = cv2.resize(cov, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
    if spec.get("soft", 0) > 0:
        cov = cv2.GaussianBlur(cov, (0, 0), spec["soft"])
    a = img[by0:by1, bx0:bx1].astype(np.float32)
    lum = a.mean(-1)
    # occluders: closed (max then min) luminance, so thin hatch strokes inside the fabric do not count as occluders
    k = spec.get("close", 5)
    lc = cv2.erode(cv2.dilate(lum, np.ones((k, k), np.uint8)), np.ones((k, k), np.uint8))
    wj = np.clip((lc - spec.get("lum_lo", 120)) / 40, 0, 1)
    # local jacket white: bright pixels in the box (excluding the dot)
    wpx = a[(lum > 170) & (a[..., 2] - a[..., 0] < 25)]
    wref = np.percentile(wpx, 75, axis=0) if len(wpx) > 40 else np.array([235, 230, 225], np.float32)
    ink = np.array(spec.get("ink", [52, 51, 56]), np.float32)
    kf = np.clip(ink / np.maximum(wref, 1), 0, 1)
    kf = 1 - d.get("s", 1.0) * (1 - kf)                # washed-out frames: lighter, like the dot
    occ = occluder(spec, img.shape[:2])
    if occ is not None:
        cov = cov * (1 - occ[by0:by1, bx0:bx1])
    al = (cov * wj)[..., None]
    a = a * (1 - al) + a * kf * al
    out = img.copy()
    out[by0:by1, bx0:bx1] = np.clip(a + 0.5, 0, 255).astype(np.uint8)
    full = np.zeros((H, W), np.float32)
    full[by0:by1, bx0:bx1] = cov
    return out, full, (bx0, by0, bx1, by1)


def tile(arrs, labels, boxes, z, cols):
    ts = []
    for a, lab, bx in zip(arrs, labels, boxes):
        x0, y0, x1, y1 = bx
        im = Image.fromarray(a).crop(bx).resize((int((x1 - x0) * z), int((y1 - y0) * z)), Image.LANCZOS)
        ImageDraw.Draw(im).text((4, 4), lab, fill=(255, 255, 0))
        ts.append(im)
    w, h = ts[0].size
    rows = (len(ts) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), (0, 0, 0))
    for k, t in enumerate(ts):
        sheet.paste(t, ((k % cols) * w, (k // cols) * h))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--compare", help="frames for before/after tiles (comma list or a:b:step)")
    ap.add_argument("--after-only", action="store_true")
    ap.add_argument("--crop", default="260x200", help="WxH crop around the dot for --compare")
    ap.add_argument("--zoom", type=float, default=2)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--name", default="sheet")
    ap.add_argument("--track-only", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    clip = os.path.join(ROOT, spec["clip"])
    tr = normalise(track(clip, spec), spec)
    if a.track_only:
        for i, d in enumerate(tr):
            print(i, None if d is None else "c=(%.1f,%.1f) ax=(%.1f,%.1f) ang=%.1f s=%.2f" % (*d["c"], *d["ax"], d["ang"], d["s"]))
        return
    art = glyphs(spec)
    if a.compare:
        if ":" in a.compare:
            s0, s1, st = (int(v) for v in a.compare.split(":"))
            want = list(range(s0, s1 + 1, st))
        else:
            want = [int(x) for x in a.compare.split(",")]
        cw, ch = (int(v) for v in a.crop.split("x"))
        arrs, labs, boxes = [], [], []
        for i, img in enumerate(frames(clip)):
            if i not in want:
                continue
            d = tr[i]
            aft = letter(img, spec, d, art)[0] if d else img
            cx, cy = (d["c"] if d else (960, 540))
            cy = cy + (d["ax"][1] * 0.9 if d else 0)
            bx = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
            if a.after_only:
                arrs.append(aft); labs.append(f"#{i}"); boxes.append(bx)
            else:
                arrs += [img, aft]; labs += [f"#{i} before", f"#{i} after"]; boxes += [bx, bx]
        os.makedirs(a.outdir, exist_ok=True)
        out = os.path.join(a.outdir, a.name + ".jpg")
        tile(arrs, labs, boxes, a.zoom, a.cols).save(out, quality=90)
        print(out)
        return
    c = av.open(clip)
    s = c.streams.video[0]
    W, H, fps = s.width, s.height, s.average_rate
    c.close()
    out = os.path.join(ROOT, spec["out"])
    tmp = out + ".tmp.mp4"
    enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", str(spec.get("crf", 14)),
                            "-pix_fmt", "yuv420p", "-profile:v", "high", *spec.get("x264_extra", []), tmp],
                           stdin=subprocess.PIPE)
    n = done = 0
    for i, img in enumerate(frames(clip)):
        if tr[i] is not None:
            img = letter(img, spec, tr[i], art)[0]
            done += 1
        enc.stdin.write(img.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    if enc.returncode:
        raise SystemExit("ffmpeg failed")
    os.replace(tmp, out)
    print(out, n, "frames,", done, "lettered")


if __name__ == "__main__":
    main()
