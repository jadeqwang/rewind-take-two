#!/usr/bin/env python
"""v10 F4 (Jade 2026-10-18, 3:01): the Bean reflection, rebuilt from the three.js mirror check
(tools/sectionF/f4_threejs, docs/revisions/v10/f4_reflection.md).

The check ray-traces the F4 geometry (camera fit to frame 0, she moves along its line of sight onto the Bean's front
face) and says: the reflection sits just below her crown, shows her BACK, feet above (same way up as she is), is small
and squashed (the Bean curves more top-to-bottom than side-to-side), then grows and rises behind her until, at contact,
its head is just under hers and its body is hidden behind her.

This script keeps v9's clean-up of the video model's reflection (clean plates, ring fill; tools/sectionF/f4_reflection.py,
its caches in media/shots/F4/v9_work) and draws a new reflection placed and warped by the check, per frame: the check's
mode 3 map gives, for each pixel of the mirror, the point of her body plane it reflects (refmap.mjs). A flat picture of
her is laid on that plane:
  --side back : a painted back view of her in the same pose (media/shots/F4/v10_back/back_3.jpg, nano-banana-pro),
                mirror-reversed as a mirror does. The physically right one.
  --side front: her own front pixels from the same frame, mirror-reversed (Jade's version: her front, feet above, the
                same place and size). Not what this mirror would show with her facing the camera.

    tools/engrave/.venv/bin/python tools/sectionF/f4_reflection_v10.py IN.mp4 OUT.mp4 --side back|front [--debug SHEET.jpg]

IN is the roundel-fixed plate (media/shots/F4/take_2_engraved_dered_patch.mp4), as for v9.
"""
import argparse
import json
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f4_reflection as R  # noqa: E402

ROOT = R.ROOT
XC, CHIN = R.XC, R.CHIN
TC = 77                 # contact (the check's schedule reaches her head to the mirror here)
RIP0, FADE0, FADE1 = 70, 72, 80     # as v9: ripples from 70; the reflection fades out 72-80 as the mirror goes liquid
BOX = (480, 200, 1440, 1080)         # check pixels rendered for the maps
BACK = os.path.join(ROOT, "media/shots/F4/v10_back/back_3.jpg")
TINT = np.array([1.0, 0.95, 0.88], np.float32) * 0.88     # chrome: a touch cooler and darker (BGR)
BODY = 1.72             # crown to soles in the check's body frame (crown -0.12 m, soles +1.60 m)


def bean_widths(n):
    cap = cv2.VideoCapture(R.MATTE)
    w = []
    for i in range(n):
        ok, f = cap.read()
        m = f[..., 0] > 127
        best = 0
        for y in range(560, 1080, 5):
            xs = np.where(m[y])[0]
            if len(xs) and xs[-1] - xs[0] > best:
                best = xs[-1] - xs[0]
        w.append(best)
    return np.array(w, np.float32)


def schedule(n):
    """Fraction of her start distance to the mirror left at each frame. The camera's distance to the Bean goes as
    1/(Bean width) while the Bean is in frame (to 61); in the check's case A the camera is 0.48 of its start distance
    from the Bean's centre at contact. Past 61 the width is out of frame: a power curve with the same slope reaches
    contact at TC."""
    w = bean_widths(62)
    r = w[0] / w
    r = np.convolve(np.pad(r, 3, mode="edge"), np.ones(7) / 7, mode="valid")
    rc = 0.48
    slope = (r[61] - r[55]) / 6
    p = max(1.0, -slope * (TC - 61) / (r[61] - rc))
    out = []
    for i in range(n):
        ri = r[i] if i <= 61 else rc + (r[61] - rc) * max(0.0, (TC - i) / (TC - 61)) ** p
        out.append(max(0.004, (ri - rc) / (1 - rc)))
    return out


def maps(fracs, work):
    d = os.path.join(work, "maps")
    js = os.path.join(d, "maps.json")
    want = [[i, round(f, 5)] for i, f in enumerate(fracs)]
    if os.path.exists(js):
        meta = json.load(open(js))
        if all(str(i) in meta and abs(meta[str(i)]["frac"] - f) < 1e-6 for i, f in want):
            return meta, d
    subprocess.run(["node", os.path.join(HERE, "f4_threejs/refmap.mjs"), "--case", "A", "--fracs", json.dumps(want),
                    "--out", d, "--box", ",".join(map(str, BOX))], check=True)
    return json.load(open(js)), d


def soles_of(Mj, band):
    """Top of her matte on her centre line (her soles)."""
    col = (Mj[:, XC - 80:XC + 80] > 127).any(1)
    ys = np.where(col[: int(band)])[0]
    return float(ys[0]) if len(ys) else 40.0


def back_source():
    """The painted back view, matted (BiRefNet), premultiplied BGRA float, with its crown, soles and centre line."""
    cache = os.path.join(os.path.dirname(BACK), "back_3_matte.png")
    im = cv2.imread(BACK)
    if not os.path.exists(cache):
        import torch
        from matte import get_birefnet
        net = get_birefnet("cuda")
        t = torch.from_numpy(im[..., ::-1].copy()).permute(2, 0, 1)[None].float().cuda() / 255
        cv2.imwrite(cache, (net(t)[0, 0].cpu().numpy() * 255).astype(np.uint8))
    a = cv2.imread(cache, 0).astype(np.float32) / 255
    k, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    keep = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    a *= cv2.dilate((lab == keep).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    rows = np.where((a > 0.5).any(1))[0]
    soles, crown = float(rows[0]), float(rows[-1])
    # centre line: the middle of the torso rows (the jacket back between the arms)
    mid = int(soles + 0.62 * (crown - soles))
    xs = np.where(a[mid] > 0.5)[0]
    xc = float((xs[0] + xs[-1]) / 2)
    src = np.dstack([im.astype(np.float32) * a[..., None], a])
    return src, crown, soles, xc


def layer(src, sx0, crown_s, scale_s, flip, mp, meta, crown_f, s_f, H, W):
    """The reflection layer (premultiplied BGR, alpha) in footage pixels.
    src: premultiplied BGRA source picture of her; her body point (x, y) [m] sits at
    (sx0 + flip * x * scale_s, crown_s - (y + 0.12) * scale_s) in it. mp: the check's map (h, w, 3) over BOX.
    Footage pixel f maps to check pixel c = (f - (XC, crown_f)) / s_f + crown_c."""
    x0, y0, x1, y1 = BOX
    cc = meta["crown"]
    fy, fx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx = ((fx - XC) / s_f + cc[0] - x0).astype(np.float32)
    cy = ((fy - crown_f) / s_f + cc[1] - y0).astype(np.float32)
    mp = np.ascontiguousarray(mp)
    X = cv2.remap(np.ascontiguousarray(mp[..., 0]), cx, cy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    Y = cv2.remap(np.ascontiguousarray(mp[..., 1]), cx, cy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    V = cv2.remap(np.ascontiguousarray(mp[..., 2]), cx, cy, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # erode the valid region a pixel so the bilinear X, Y never mix with the zeros outside it
    V = cv2.erode(V, np.ones((3, 3), np.uint8))
    sxp = sx0 + flip * X * scale_s
    syp = crown_s - (Y + 0.12) * scale_s
    fig = (V > 0.5) & (np.abs(X) < 1.2) & (Y > -0.3) & (Y < 1.8)
    if fig.sum() < 4:
        return np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)
    # anti-alias: the mirror shrinks her a lot (5-20x early on, more top-to-bottom): pre-shrink the source by the median
    # source-pixels-per-output-pixel along each axis, then sample
    gx = np.abs(np.gradient(sxp, axis=1))[fig]
    gy = np.abs(np.gradient(syp, axis=0))[fig]
    mx, my = max(1.0, float(np.median(gx)) / 1.15), max(1.0, float(np.median(gy)) / 1.15)
    sh, sw = src.shape[:2]
    small = cv2.resize(src, (max(2, int(round(sw / mx))), max(2, int(round(sh / my)))), interpolation=cv2.INTER_AREA)
    mp = None
    ux = ((sxp + 0.5) * small.shape[1] / sw - 0.5).astype(np.float32)
    uy = ((syp + 0.5) * small.shape[0] / sh - 0.5).astype(np.float32)
    s = cv2.remap(small, ux, uy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    s *= (V > 0.5)[..., None]
    return s[..., :3] * TINT, s[..., 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--side", choices=["back", "front"], required=True)
    ap.add_argument("--work", default=os.path.join(ROOT, "media/shots/F4/v9_work"))
    ap.add_argument("--plates", default=os.path.join(ROOT, "media/shots/F4/v9_plates2"))
    ap.add_argument("--v10work", default=os.path.join(ROOT, "media/shots/F4/v10_work"))
    ap.add_argument("--last", type=int, default=104)
    ap.add_argument("--only", default=None)
    ap.add_argument("--dump", default=None)
    ap.add_argument("--debug", default=None)
    ap.add_argument("--noref", action="store_true", help="debug: the cleaned plate only, no new reflection")
    a = ap.parse_args()

    fr = R.read(a.src)
    H, W = fr[0].shape[:2]
    n = min(len(fr), a.last + 1)
    hp = R.track_band(fr)
    Jr, Rr = R.masks(fr, hp, a.work, n)
    bean = R.read(R.MATTE)
    Mj = R.track_matte(fr, Jr, hp, n, a.work)
    R2 = R.masks_contact(fr, hp, a.work, n)
    plates = R.Plates(fr, Rr, Mj, hp, a.plates)
    os.makedirs(a.v10work, exist_ok=True)
    nref = FADE1 + 1
    fracs = schedule(nref)
    json.dump([round(f, 4) for f in fracs], open(os.path.join(a.v10work, "schedule.json"), "w"))
    meta, mdir = maps(fracs, a.v10work)
    if a.side == "back":
        bsrc, b_crown, b_soles, b_xc = back_source()
        b_scale = (b_crown - b_soles) / BODY
        print(f"back view: crown {b_crown:.0f} soles {b_soles:.0f} centre {b_xc:.0f} ({b_scale:.0f} px/m)")
    yy, xx = np.mgrid[0:H, 0:W]
    soles0 = soles_of(Mj[0], hp[0])
    log = {}

    out = [f.copy() for f in fr]
    dbg = []
    rp = None
    todo = [int(v) for v in a.only.split(",")] if a.only else range(n)
    for i in todo:
        im = fr[i].astype(np.float32)
        chin = hp[i] + CHIN
        # ---------------------------------------------------------------- v9's clean-up, unchanged
        if i >= R.LATE:
            bot = float(np.interp(i, [80, 86, 92, 100], [118, 108, 98, 95]))
            below_chin = (np.abs(xx - XC) < 75) & (yy > hp[i] + bot) & ~R.head_zone(hp[i], H, W, True, i)
            Mj[i][below_chin] = 0
        Jm = Mj[i].astype(np.float32) / 255
        her = Mj[i] > 100
        Rm = R.old_mask(Rr[i], Mj[i], chin, H, W, fr[i], R2[i] if i >= 60 else None, i >= R.LATE, i) > 0
        if i < R.RING:
            P = plates(i)
            base = im.copy()
            if P is not None:
                mf = cv2.GaussianBlur(Rm.astype(np.float32), (0, 0), 1.5)[..., None]
                base = im * (1 - mf) + P * mf
            strip = R.below_outline(hp[i], H, W) & ~R.below_outline(hp[i] + 30, H, W) & (np.abs(xx - XC) < 75)
            strip &= i < 62
            b8 = np.clip(base, 0, 255).astype(np.uint8)
            g = cv2.cvtColor(b8, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(b8, cv2.COLOR_BGR2HSV)
            strip = cv2.dilate((strip & (g < 200)).astype(np.uint8), np.ones((5, 5), np.uint8))
            strip[her] = 0
            navy = ((hsv[..., 0] >= 95) & (hsv[..., 0] <= 130) & (hsv[..., 1] > 70) & (hsv[..., 2] < 140)
                    & (np.abs(xx - XC) < 75) & (yy > hp[i] + 100) & ~R.below_outline(hp[i] + 30, H, W))
            strip |= cv2.dilate(navy.astype(np.uint8), np.ones((5, 5), np.uint8))
            if strip.any():
                b8 = cv2.inpaint(b8, strip, 6, cv2.INPAINT_TELEA)
                base = b8.astype(np.float32)
                im = im.copy()
                im[strip > 0] = base[strip > 0]
        else:
            herd = cv2.dilate(her.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
            head = R.head_zone(hp[i], H, W, i >= R.LATE, i)
            herd |= head
            g = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
            zone = (np.abs(xx - XC) < 520) & (yy > chin - 250)
            rp = R.ring_params(g, zone & ~herd & ~Rm, XC, chin - 30, rp)
            model, rr = R.ring_fill(im, ~herd & ~Rm, *rp)
            res = np.abs(im - model).max(2)
            bad = ((res > 40) & ~herd & (rr < 460) & (yy > hp[i] + 40)).astype(np.uint8)
            bad = cv2.morphologyEx(bad, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            Rm = (Rm | (cv2.dilate(bad, np.ones((11, 11), np.uint8)) > 0)) & ~her & ~head
            model, _ = R.ring_fill(im, ~herd & ~Rm, *rp)
            mf = cv2.GaussianBlur(Rm.astype(np.float32), (0, 0), 1.5)[..., None]
            base = im * (1 - mf) + model * mf
            bot = float(np.interp(i, [80, 86, 92, 100], [118, 108, 98, 95]))
            pit = ((xx - XC) / 78.0) ** 2 + ((yy - (hp[i] + bot)) / 44.0) ** 2 < 1
            pit = cv2.GaussianBlur((pit & ~head & ~her).astype(np.float32), (0, 0), 7)[..., None]
            ring_dark = np.median(im[(rr < 400) & ~Rm & ~herd & (g < 90)], 0) if ((rr < 400) & (g < 90)).any() else np.array([70, 55, 45])
            lum = cv2.cvtColor(np.clip(model, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
            shade = ring_dark * (0.75 + 0.5 * (lum / 255.0))
            base = base * (1 - pit) + shade * pit
        # ---------------------------------------------------------------- the new reflection, from the check
        op = 0.9 * float(np.clip((FADE1 - i) / (FADE1 - FADE0), 0, 1))
        if op > 0 and str(i) in meta and not a.noref:
            m = meta[str(i)]
            mp = np.fromfile(os.path.join(mdir, f"map_{i:03d}.bin"), np.float32).reshape(m["h"], m["w"], 3)
            crown_f = chin
            # her size in the footage vs the check: crown-to-soles (her soles from the frame-0 matte, carried with
            # the band: she keeps her size in the shot and the late mattes lose her feet in the flash)
            soles_f = soles0 + (hp[i] - hp[0])
            s_f = (crown_f - soles_f) / (m["crown"][1] - m["soles"][1])
            if a.side == "back":
                col, al = layer(bsrc, b_xc, b_crown, b_scale, +1, mp, m, crown_f, s_f, H, W)
            else:       # her own front, mirror-reversed: her body x runs to the image right
                src = np.dstack([im * Jm[..., None], Jm])
                scale_f = (crown_f - soles_f) / BODY
                col, al = layer(src, XC, crown_f, scale_f, +1, mp, m, crown_f, s_f, H, W)
                # her own pixels must not feed back into the frame where she stands: the layer only shows on the
                # mirror, below/behind her (Jade on top covers the rest)
            if i > RIP0:
                col, al = R.ripple(col, al, XC, chin - 30, min(1.0, (i - RIP0) / 8.0), i)
            clip = cv2.cvtColor(bean[i], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
            al = al * clip * op
            col = col * (clip * op)[..., None]
            base = base * (1 - al[..., None]) + col
            ys, xs = np.where(al > 0.2)
            if len(xs):
                log[i] = dict(frac=round(fracs[i], 4), bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                              visible_px=int(((al > 0.2) & ~her).sum()), s_f=round(s_f, 3))
        res = base * (1 - Jm[..., None]) + im * Jm[..., None]
        out[i] = np.clip(res, 0, 255).astype(np.uint8)
        if a.debug and (a.only or i % 6 == 0):
            c0 = int(chin)
            y0 = max(0, c0 - 300)
            crop = lambda z: cv2.resize(z[y0:y0 + 600, XC - 400:XC + 400], (400, 300))
            tile = np.vstack([crop(fr[i]), crop(out[i])])
            cv2.putText(tile, str(i), (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            dbg.append(tile)
    json.dump(log, open(os.path.join(a.v10work, f"reflection_{a.side}.json"), "w"), indent=1)
    if a.debug and dbg:
        while len(dbg) % 6:
            dbg.append(np.zeros_like(dbg[0]))
        cv2.imwrite(a.debug, np.vstack([np.hstack(dbg[r:r + 6]) for r in range(0, len(dbg), 6)]))
    if a.only:
        if a.dump:
            os.makedirs(a.dump, exist_ok=True)
            for i in todo:
                cv2.imwrite(os.path.join(a.dump, f"{a.side}_{i:03d}.png"), out[i])
        return
    p = subprocess.Popen([R.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24",
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", a.out],
                         stdin=subprocess.PIPE)
    for f in out:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
