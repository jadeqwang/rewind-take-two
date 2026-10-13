"""Jacket-back repaint (v6, Jade 2:54): canon = the orange band runs across the chest and arms only and stops at the side
seam under the arm; the BACK panel is plain white with one large pale-blue dot centred between the shoulder blades.

Per frame, inside a tracked back-panel polygon (spec keyframes, linear in between):
  1. orange -> the jacket's white, keeping shading/ink: target = white * (R / 245), blended by "orangeness"
     (so anti-aliased edges, hatching and hair strands over the band survive), cut clean at the seam lines;
  2. (optional, "dot": null skips it) a pale-blue dot with a thin ink outline, multiplied by the pixel's own shading
     and painted only on jacket-bright pixels, so hair, arms outside the polygon and ink lines stay in front of it.
Frames outside spec["ranges"] are passed through untouched.

    $PY tools/jacket_back.py tools/jacket_back_specs/F2.json              # write spec["out"]
    $PY tools/jacket_back.py SPEC --check 30,36,91 --outdir DIR             # overlays (polygon + dot) for review
    $PY tools/jacket_back.py SPEC --compare 30,33,36 --outdir DIR --box x0,y0,x1,y1   # before/after zoom tiles
$PY = tools/engrave/.venv/bin/python (cv2, av, numpy, PIL).
"""
import argparse
import json
import math
import os
import shutil
import subprocess

import av
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = "/home/jade/Documents/rewind-take-two"


def ffmpeg():
    for p in ("/home/jade/Documents/moongazing/.venv/bin/ffmpeg", shutil.which("ffmpeg")):
        if p and os.path.exists(p):
            return p
    raise SystemExit("no ffmpeg")


def in_ranges(i, ranges):
    return any(a <= i <= b for a, b in ranges)


def _tops(spec, k):
    """fill a key's TL/TR (top of the seam lines, under the hair) if not given: continue BL->L / BR->R upward"""
    k = dict(k)
    L, R, BL, BR = (np.array(k[n], float) for n in ("L", "R", "BL", "BR"))
    ext = spec.get("ext", 0.35) * float(np.linalg.norm(R - L))
    for top, a, b in (("TL", L, BL), ("TR", R, BR)):
        if top not in k:
            d = a - b
            n = np.linalg.norm(d)
            k[top] = (a + (d / n if n > 1e-6 else np.array([0, -1.0])) * ext).tolist()
    return k


def params(spec, i):
    keys = {int(k): _tops(spec, v) for k, v in spec["keys"].items()}
    ks = sorted(keys)
    if i <= ks[0]:
        a = b = ks[0]
    elif i >= ks[-1]:
        a = b = ks[-1]
    else:
        a = max(k for k in ks if k <= i)
        b = min(k for k in ks if k >= i)
    t = 0.0 if a == b else (i - a) / (b - a)
    out = {}
    for name in set(keys[a]) | set(keys[b]):
        va, vb = keys[a].get(name), keys[b].get(name)
        if va is None or vb is None or isinstance(va, (str, bool)):
            out[name] = va if t < 0.5 and va is not None else vb if vb is not None else va
            continue
        out[name] = (np.array(va, float) * (1 - t) + np.array(vb, float) * t).tolist() if isinstance(va, list) else va * (1 - t) + vb * t
    # hidden: a key may say "hide": true (no dot); interpolate only if both sides agree
    out["hide"] = bool(keys[a].get("hide")) and bool(keys[b].get("hide")) if a != b else bool(keys[a].get("hide"))
    return out


def geometry(spec, p):
    L, R, BL, BR = (np.array(p[k], float) for k in ("L", "R", "BL", "BR"))
    W = float(np.linalg.norm(R - L))
    # bottom edge = the hem rib's top outline, which arcs up in the middle (seen from below)
    arc = spec.get("rib_arc", 0.06) * W
    nrm = np.array([(BR - BL)[1], -(BR - BL)[0]]) / max(np.linalg.norm(BR - BL), 1e-6)   # points "up" for BL->BR
    ctrl = (BL + BR) / 2 + nrm * 2 * arc
    bez = [(1 - t) ** 2 * BR + 2 * (1 - t) * t * ctrl + t * t * BL for t in np.linspace(0, 1, 9)[1:-1]]
    poly = np.array([BL, L, np.array(p["TL"], float), np.array(p["TR"], float), R, BR] + bez)
    ang = 0.5 * (math.atan2(R[1] - L[1], R[0] - L[0]) + math.atan2(BR[1] - BL[1], BR[0] - BL[0]))
    c = np.array(p["c"], float) if "c" in p else (L + R) / 2 + np.array([0.0, p.get("dy", 0.0)])
    rx = p.get("rx", spec.get("dot_w", 0.23) * W)
    ry = rx * spec.get("dot_aspect", 0.8)
    # keep the dot clear of the rib: bottom at least gap*ry above the arc's apex
    apex = (BL + BR) / 2 + nrm * arc
    lim = apex[1] - spec.get("rib_gap", 0.2) * ry - ry
    if "c" not in p and c[1] > lim:
        c = np.array([c[0], lim])
    return poly, c, rx, ry, ang, W


def poly_mask(poly, shape, ss=4):
    H, W = shape
    x0, y0 = np.floor(poly.min(0)).astype(int) - 2
    x1, y1 = np.ceil(poly.max(0)).astype(int) + 2
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, W), min(y1, H)
    m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    pts = np.round((poly - [x0, y0]) * ss).astype(np.int32)
    cv2.fillPoly(m, [pts], 255)
    m = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return m, (x0, y0, x1, y1)


def repaint(img, spec, p):
    """img: HxWx3 uint8 RGB -> repainted copy"""
    poly, c, rx, ry, ang, W = geometry(spec, p)
    m, (x0, y0, x1, y1) = poly_mask(poly, img.shape[:2])
    a = img[y0:y1, x0:x1].astype(np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    white = np.array(spec.get("white", [244, 233, 222]), np.float32)
    # 1. orange -> white
    # the band is coloured-pencil texture (pale-orange specks between strokes): find the solid band, grow it a little,
    # and inside that region convert every warm pixel (so no orange stipple survives); ink/hair stay dark because
    # the target keeps the pixel's own red-channel lightness
    strong = (np.clip((R - B - 70) / 50, 0, 1) * np.clip((R - G - 45) / 35, 0, 1)).astype(np.float32)
    k = spec.get("band_grow", 4)
    region = cv2.dilate(strong, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    region = cv2.GaussianBlur(region, (0, 0), 1.0)
    warm = np.clip((R - B - 15) / 20, 0, 1)
    wo = np.clip(np.maximum(strong, region * np.maximum(warm, (R < 200).astype(np.float32))), 0, 1)
    wo = cv2.GaussianBlur(wo, (0, 0), 0.8) * m
    # lightness: the band's pencil strokes are faint darker streaks that would read as grey scan-lines on white, so
    # use the band's local max red (broad shading) and only let clearly darker detail (ink, hair, folds) through
    # normalised (masked) blur so the local band lightness does not fall off at the band's edges
    sm = (strong > 0.5).astype(np.float32)
    rml = cv2.dilate(R * sm, np.ones((5, 5), np.uint8))
    num = cv2.GaussianBlur(rml, (0, 0), 2.0)
    den = cv2.GaussianBlur(cv2.dilate(sm, np.ones((5, 5), np.uint8)), (0, 0), 2.0)
    rml = np.where(den > 0.05, num / np.maximum(den, 1e-3), R)
    # calibrate per frame: lit band orange -> this frame's own jacket white (median of the white pixels in the panel)
    wpx = a[(m > 0.5) & (R - B < 40) & (a.mean(-1) > 200)]
    wref = np.median(wpx, 0) if len(wpx) > 50 else white
    opx = R[(strong > 0.9) & (m > 0.5)]
    oref = max(float(np.percentile(opx, 90)), 200.0) if len(opx) > 30 else 245.0
    f = (np.clip(np.minimum(np.maximum(rml, R), R / spec.get("detail", 0.65)) / oref, 0, 1.0))[..., None]
    white = wref.astype(np.float32)
    a = a + wo[..., None] * (white * f - a)
    # 2. dot
    dot = spec.get("dot")
    if dot is not None and not p.get("hide"):
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        ca, sa = math.cos(ang), math.sin(ang)
        u = (xx - c[0]) * ca + (yy - c[1]) * sa
        v = -(xx - c[0]) * sa + (yy - c[1]) * ca
        r = np.sqrt((u / rx) ** 2 + (v / ry) ** 2) + 1e-6
        g = np.sqrt((u / (rx * rx * r)) ** 2 + (v / (ry * ry * r)) ** 2) + 1e-6
        d = (r - 1) / g                                      # ~signed distance to the ellipse (px)
        lw = max(spec.get("ink_min", 1.4), spec.get("ink_w", 0.014) * W)
        fill = np.clip(0.5 - d, 0, 1)
        ring = np.clip(lw / 2 + 0.5 - np.abs(d), 0, 1)
        lum = a.mean(-1)
        wj = np.clip((lum - 95) / 45, 0, 1)                  # jacket-bright pixels only: hair/ink stay in front
        shade = np.clip(lum / white.mean(), 0.72, 1.0)[..., None]
        af = (fill * wj * m)[..., None]
        a = a + af * (np.array(dot, np.float32) * shade - a)
        if spec.get("ink", [42, 40, 58]) is not None:       # "ink": null = no outline (B_lawn's dot has none)
            ar = (ring * wj * m)[..., None]
            a = a + ar * (np.array(spec.get("ink", [42, 40, 58]), np.float32) - a)
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(a + 0.5, 0, 255).astype(np.uint8)
    return out


def blue_anchor(img, spec, prev=None):
    """centroid of the existing pale-blue back dot (largest blue blob; near `prev` if given)"""
    a = img.astype(np.int16)
    R, B = a[..., 0], a[..., 2]
    m = ((B - R > 45) & (B > 150)).astype(np.uint8)
    if spec.get("anchor_ymax"):
        m[spec["anchor_ymax"]:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    if n < 2:
        return prev
    idx = [k for k in range(1, n) if st[k, 4] >= spec.get("anchor_min_area", 150)]
    if not idx:
        return prev
    if prev is not None:
        idx.sort(key=lambda k: np.hypot(*(cen[k] - prev)) - st[k, 4] / 50)
        return cen[idx[0]]
    return cen[max(idx, key=lambda k: st[k, 4])]


def absolute(p, anchor):
    """keys given relative to the tracked anchor -> absolute frame coordinates"""
    p = dict(p)
    for k in ("L", "R", "BL", "BR", "TL", "TR", "c"):
        if k in p:
            p[k] = (np.array(p[k], float) + anchor).tolist()
    return p


def frames(path):
    c = av.open(path)
    for f in c.decode(video=0):
        yield f.to_ndarray(format="rgb24")
    c.close()


def overlay(img, spec, p):
    poly, c, rx, ry, ang, W = geometry(spec, p)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    d.line([tuple(q) for q in poly] + [tuple(poly[0])], fill=(0, 255, 0), width=1)
    for k, col in (("L", (255, 0, 255)), ("R", (255, 0, 255)), ("BL", (0, 255, 255)), ("BR", (0, 255, 255))):
        x, y = p[k]
        d.ellipse([x - 2, y - 2, x + 2, y + 2], outline=col)
    pts = []
    for t in np.linspace(0, 2 * math.pi, 48):
        u, v = rx * math.cos(t), ry * math.sin(t)
        pts.append((c[0] + u * math.cos(ang) - v * math.sin(ang), c[1] + u * math.sin(ang) + v * math.cos(ang)))
    d.line(pts + [pts[0]], fill=(255, 255, 0), width=1)
    return np.array(im)


def tile(arrs, labels, box, z, cols):
    ts = []
    for j, (a, lab) in enumerate(zip(arrs, labels)):
        bx = box[j] if isinstance(box, list) else box
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
    ap.add_argument("--check", help="frames to overlay (comma list)")
    ap.add_argument("--compare", help="frames for before/after tiles (comma list)")
    ap.add_argument("--box", help="crop box x0,y0,x1,y1 for --check/--compare (else auto around the polygon)")
    ap.add_argument("--zoom", type=float, default=3)
    ap.add_argument("--perframe", help="WxH: crop each frame around its own polygon instead of one shared box")
    ap.add_argument("--after-only", action="store_true", help="--compare: only the repainted frames, 4 per row")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--name", default="sheet")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    clip = os.path.join(ROOT, spec["clip"])
    ranges = spec["ranges"]
    if a.check or a.compare:
        want = [int(x) for x in (a.check or a.compare).split(",")]
        arrs, labs = [], []
        boxes = []
        prev = None
        for i, img in enumerate(frames(clip)):
            if spec.get("anchor") and in_ranges(i, ranges):
                prev = blue_anchor(img, spec, prev)
            if i not in want:
                continue
            p = params(spec, i)
            if spec.get("anchor"):
                p = absolute(p, prev)
            poly = geometry(spec, p)[0]
            boxes.append((*poly.min(0), *poly.max(0)))
            if a.check:
                arrs.append(overlay(repaint(img, spec, p) if in_ranges(i, ranges) else img, spec, p))
                labs.append(f"#{i}")
            else:
                aft = repaint(img, spec, p) if in_ranges(i, ranges) else img
                if a.after_only:
                    arrs.append(aft)
                    labs.append(f"#{i}")
                else:
                    arrs += [img, aft]
                    labs += [f"#{i} before", f"#{i} after"]
        if a.perframe:
            pw, ph = (int(v) for v in a.perframe.split("x"))
            box = []
            for b in boxes:
                cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
                bb = (int(cx - pw / 2), int(cy - ph / 2), int(cx - pw / 2) + pw, int(cy - ph / 2) + ph)
                box += [bb] if (a.check or a.after_only) else [bb, bb]
        elif a.box:
            box = tuple(int(v) for v in a.box.split(","))
        else:
            b = np.array(boxes)
            box = (int(b[:, 0].min()) - 25, int(b[:, 1].min()) - 10, int(b[:, 2].max()) + 25, int(b[:, 3].max()) + 25)
        os.makedirs(a.outdir, exist_ok=True)
        out = os.path.join(a.outdir, a.name + ".jpg")
        tile(arrs, labs, box, a.zoom, 4 if a.after_only else 2 if a.compare else 3).save(out, quality=90)
        print(out)
        return
    c = av.open(clip)
    s = c.streams.video[0]
    W, H, fps = s.width, s.height, s.average_rate
    c.close()
    out = os.path.join(ROOT, spec["out"])
    tmp = out + ".tmp.mp4"
    enc = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", str(spec.get("crf", 14)), "-pix_fmt", "yuv420p",
                          *spec.get("x264_extra", []), tmp], stdin=subprocess.PIPE)
    n = 0
    prev = None
    for i, img in enumerate(frames(clip)):
        if in_ranges(i, ranges):
            p = params(spec, i)
            if spec.get("anchor"):
                prev = blue_anchor(img, spec, prev)
                p = absolute(p, prev)
            img = repaint(img, spec, p)
        enc.stdin.write(img.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    if enc.returncode:
        raise SystemExit("ffmpeg failed")
    os.replace(tmp, out)
    print(out, n, "frames")


if __name__ == "__main__":
    main()
