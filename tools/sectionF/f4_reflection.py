#!/usr/bin/env python
"""v9 fix 6 (Jade 3:00): F4's Bean reflection did not match the falling Jade (no headphones, no pale-blue chest dot,
legs apart). This throws the video model's reflection away and builds a new one from the falling Jade's own pixels, so
every costume detail (headphones, chest dot, re-lettered roundel, legs together, pencil hand) matches by construction.

    tools/engrave/.venv/bin/python tools/sectionF/f4_reflection.py IN.mp4 OUT.mp4 [--work DIR] [--debug SHEET.jpg]

IN is the roundel-fixed plate (tools/sectionE/patchfix.py on take_2_engraved_dered.mp4). Steps per frame:
  1. track: the headphone band's row on Jade's centre line (orange, the first orange run below her legs) gives her
     vertical position; chin = band + 112 px.
  2. mattes (BiRefNet, tools/engrave/matte.py): Jade from a crop that stops just under her chin, gated by a cleaned
     frame-54 silhouette moved with her (BiRefNet also grabs the Bean behind her arms in early frames); the old
     reflection from a crop below her chin (largest components on the centre line).
  3. remove the old reflection: masked pixels are refilled from the same frame (see fill()).
  4. new reflection: her cutout flipped about the mirror surface (heads meet, as a dive onto a mirror does), shrunk by
     a convex-mirror magnification that grows to 1 at contact, and compressed toward her feet (the far parts of her
     are farther from the mirror); cooled and dimmed a touch as chrome does, clipped to the Bean, faded out as the
     ripples break the mirror.
  5. Jade's own pixels are put back on top, untouched.
"""
import argparse
import json
import os
import subprocess
import sys

import cv2
import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
FFMPEG = os.environ.get("FFMPEG", os.path.expanduser(
    "~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"))
MATTE = os.path.join(ROOT, "media/shots/F4/take_2_matte/matte.mp4")   # Jade + Bean silhouette (the Bean clip)

XC = 958          # Jade's centre line (she falls straight down the frame centre)
CHIN = 112        # headphone band top (centre line) -> chin (px)
REF = 54          # frame whose BiRefNet silhouette is clean (template for the gate)
TC = 78           # contact frame (her head meets the mirror; ripples start ~76)
FB = 1600.0       # body compression length (px): lateral scale falls as 1/(1+q/FB) toward her feet
GAP0 = 70.0       # chin-to-reflected-chin gap at frame 0 (px), matching the old reflection's placement
M0 = 0.42         # magnification of the reflection's head at frame 0 (old reflection was ~0.4 of her)
RIP0 = 70          # ripples start under her head
FADE0, FADE1 = 72, 80   # the ripples break the mirror up: reflection full until FADE0, gone by FADE1
LATE = 80         # from here only her face column is protected from the clean-up (see head_zone)
RING = 80         # from here the old reflection sits on the ripple rings: ring fill instead of plates


def read(path):
    cap = cv2.VideoCapture(path)
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(f)
    return out


def track_band(frames):
    hp = []
    for i, im in enumerate(frames):
        hsv = cv2.cvtColor(im[:, XC - 28:XC + 32], cv2.COLOR_BGR2HSV)
        org = (hsv[..., 0] >= 5) & (hsv[..., 0] <= 22) & (hsv[..., 1] > 120) & (hsv[..., 2] > 150)
        rows = np.where(org.sum(1) > 6)[0]
        groups = []
        for r in rows:
            if groups and r - groups[-1][-1] <= 3:
                groups[-1].append(r)
            else:
                groups.append([r])
        prev = hp[-1] if hp else 458
        g = min(groups, key=lambda g: abs(g[0] - prev)) if groups else None
        hp.append(float(g[0]) if g and abs(g[0] - prev) < 25 else prev)
    hp = np.array(hp)
    k = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2)
    k /= k.sum()
    pad = np.pad(hp, 6, mode="edge")
    return np.convolve(pad, k, mode="valid")


class Seg:
    def __init__(self):
        from matte import get_birefnet
        self.net = get_birefnet("cuda")

    def __call__(self, im, x0, y0, x1, y1):
        t = torch.from_numpy(im[y0:y1, x0:x1, ::-1].copy()).permute(2, 0, 1)[None].float().cuda() / 255
        return self.net(t)[0, 0].cpu().numpy()


def masks(frames, hp, work, n):
    os.makedirs(work, exist_ok=True)
    cache = os.path.join(work, "masks.npz")
    if os.path.exists(cache):
        z = np.load(cache)
        return z["J"], z["R"]
    seg = Seg()
    H, W = frames[0].shape[:2]
    J = np.zeros((n, H, W), np.uint8)
    R = np.zeros((n, H, W), np.uint8)
    for i in range(n):
        im = frames[i]
        c = int(round(hp[i])) + CHIN
        J[i, 0:c + 14, 560:1360] = (seg(im, 560, 0, 1360, c + 14) * 255).astype(np.uint8)
        y1 = min(H, c + 470)
        R[i, c - 40:y1, 680:1240] = (seg(im, 680, c - 40, 1240, y1) * 255).astype(np.uint8)
    np.savez_compressed(cache, J=J, R=R)
    return J, R


# her lower outline (head, hair, collar) relative to (XC, band): below it is never Jade. The old reflection's feet
# touch her chin in frames 24-70, and BiRefNet takes them (and the Bean) as part of her.
OUTLINE = [(-140, 60), (-130, 80), (-110, 95), (-80, 110), (-60, 121), (-40, 119), (-20, 119), (0, 120), (20, 119),
           (40, 119), (60, 121), (80, 113), (100, 96), (120, 78), (130, 70), (140, 60)]


def below_outline(band, H, W):
    xs = np.array([p[0] for p in OUTLINE], np.float32)
    ys = np.array([p[1] for p in OUTLINE], np.float32)
    x = np.arange(W) - XC
    lim = band + np.interp(x, xs, ys)
    m = np.arange(H)[:, None] > lim[None, :]
    m[:, np.abs(x) > 140] = False
    return m


def masks_contact(frames, hp, work, n, f0=60):
    """At the contact the old reflection's arms rise beside her head: BiRefNet on a crop from her shoulders down
    (her and the old reflection both), for frames f0..n-1."""
    cache = os.path.join(work, "masks_contact.npz")
    if os.path.exists(cache):
        return np.load(cache)["R2"]
    seg = Seg()
    H, W = frames[0].shape[:2]
    R2 = np.zeros((n, H, W), np.uint8)
    for i in range(f0, n):
        y0 = max(0, int(hp[i]) - 40)
        y1 = min(H, int(hp[i]) + CHIN + 470)
        R2[i, y0:y1, 500:1420] = (seg(frames[i], 500, y0, 1420, y1) * 255).astype(np.uint8)
    np.savez_compressed(cache, R2=R2)
    return R2


def track_matte(frames, Jr, hp, n, work):
    """Jade's matte, carried from the clean REF frame by dense flow and snapped to BiRefNet where the two agree.
    BiRefNet alone grabs the Bean behind her arms (frames 0-48) and drops an arm in others (62-68, 74)."""
    cache = os.path.join(work, "jade.npz")
    if os.path.exists(cache):
        return np.load(cache)["M"]
    H, W = frames[0].shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    T = (Jr[REF] > 127).astype(np.uint8)
    T[(yy > hp[REF] + 40) & (np.abs(xx - XC) > 140)] = 0
    T[below_outline(hp[REF], H, W)] = 0
    T = cv2.morphologyEx(T, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    M = np.zeros((n, H, W), np.float32)
    M[REF] = T.astype(np.float32)
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames[:n]]
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    kd = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    kt = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    for order in (range(REF - 1, -1, -1), range(REF + 1, n)):
        for i in order:
            j = i + 1 if i < REF else i - 1
            F = dis.calc(gray[i], gray[j], None)
            Wp = cv2.remap(M[j], (xx + F[..., 0]).astype(np.float32), (yy + F[..., 1]).astype(np.float32), cv2.INTER_LINEAR)
            b = (Wp > 0.5).astype(np.uint8)
            jr = (Jr[i] > 127).astype(np.uint8)
            jr[int(hp[i]) + CHIN + 10:] = 0
            jr[below_outline(hp[i], H, W)] = 0
            if i > REF:     # carry the flowed silhouette (BiRefNet drops an arm in 62-68 and 74 and takes the old
                m = b       # reflection's grey arms at the contact); the flow drags bits of trees and ripple off her
                c = int(hp[i]) + CHIN    # hands, so out on the arms drop anything green or blue
                hsv = cv2.cvtColor(frames[i], cv2.COLOR_BGR2HSV)
                cool = (hsv[..., 0] >= 35) & (hsv[..., 0] <= 130) & (hsv[..., 1] > 35) & (hsv[..., 2] > 50)
                arms = (np.abs(xx - XC) > 90) & (yy < c)
                m = m & ~(cool & arms).astype(np.uint8)
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            else:
                m = b | (jr & cv2.dilate(b, kd))
            if i < REF:     # BiRefNet grabs the Bean behind her arms here: never stray far from the REF silhouette
                Ts = cv2.warpAffine(T, np.float32([[1, 0, 0], [0, 1, hp[i] - hp[REF]]]), (W, H), flags=cv2.INTER_NEAREST)
                m &= cv2.dilate(Ts, kg)
            m[below_outline(hp[i], H, W)] = 0
            M[i] = m.astype(np.float32)
    for i in range(REF + 1, n):     # flow drags bits of her matte across the ripples: keep her one piece
        k, lab, st, _ = cv2.connectedComponentsWithStats((M[i] > 0.5).astype(np.uint8), 8)
        if k > 2:
            M[i] *= (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
    M = np.stack([cv2.GaussianBlur(x, (0, 0), 0.8) for x in M])
    np.savez_compressed(cache, M=(M * 255).astype(np.uint8))
    return (M * 255).astype(np.uint8)


def reflection_source(Mj, Jr, band, H, W):
    """Her matte for the reflection. After REF the carried matte drags bits of the plaza off her rising hands; where
    BiRefNet sees that arm, keep only what lies within 12 px of it."""
    m = Mj.astype(np.float32) / 255
    jr = (Jr > 127).astype(np.uint8)
    jd = cv2.dilate(jr, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) > 0
    yy, xx = np.mgrid[0:H, 0:W]
    c = int(band) + CHIN
    for side in (xx < XC - 90, xx > XC + 90):
        zone = side & (yy < c)
        bz = (Mj > 127) & zone
        if bz.sum() and ((jr > 0) & bz).sum() > 0.6 * bz.sum():
            m[zone & ~jd] = 0
    return m


def head_zone(band, H, W, late=False, i=None):
    """Her head (never the old reflection). After the contact (late) the old reflection's arms crowd round her head
    and her own matte is reliable there, so only her face column is protected."""
    yy = np.arange(H)[:, None]
    x = np.abs(np.arange(W) - XC)[None, :]
    if late:        # her face and the hair framing it: an ellipse from the headphone band to her chin, which rises as
        bot = float(np.interp(i, [80, 86, 92, 100], [118, 108, 98, 95]))   # her head sinks into the mirror
        return (x / 60.0) ** 2 + ((yy - (band + (30 + bot) / 2)) / ((bot - 30) / 2)) ** 2 < 1
    return ~below_outline(band, H, W) & (x <= 140) & (yy < band + CHIN + 20)


def old_mask(Rr, Mj, chin, H, W, im=None, R2=None, late=False, i=None):
    """The model's reflection: BiRefNet's crop below her chin, the components on her centre line, minus Jade.
    With the frame given, its pencil too (BiRefNet misses it): brown-orange strokes in the box round it."""
    yy = np.arange(H)[:, None]
    m = ((Rr > 110) & (yy > chin - 40)).astype(np.uint8)
    if R2 is not None:  # the contact: its arms beside her head, i.e. what BiRefNet sees there that is not her
        her = cv2.dilate((Mj > 100).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        m |= ((R2 > 110) & ~her & (yy > chin - CHIN + 20)).astype(np.uint8)
    k, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(k, bool)
    for j in range(1, k):
        x, y, w, h, area = st[j]
        keep[j] = area > 60 and x < XC + 60 and x + w > XC - 60 and y < chin + 150
    if keep.any():      # and whatever it holds that BiRefNet split off (the pencil), inside its box
        xs, ys = st[keep, 0], st[keep, 1]
        bx0, by0 = xs.min() - 50, ys.min() - 20
        bx1, by1 = (st[keep, 0] + st[keep, 2]).max() + 50, (st[keep, 1] + st[keep, 3]).max() + 20
        for j in range(1, k):
            x, y, w, h, area = st[j]
            if area > 15 and x >= bx0 and y >= by0 and x + w <= bx1 and y + h <= by1:
                keep[j] = True
    m = keep[lab].astype(np.uint8)
    # never above her own outline: from ~82 her face sinks into the ripple and her carried matte loses it
    band = chin - CHIN
    above = head_zone(band, H, W, late, i)
    m[above] = 0
    if im is not None and keep.any():
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        pen = ((hsv[..., 0] >= 6) & (hsv[..., 0] <= 24) & (hsv[..., 1] > 90) & (hsv[..., 2] < 210)).astype(np.uint8)
        box = np.zeros_like(pen)
        box[max(0, by0):by1, max(0, bx0):bx1] = 1
        pen &= box
        k2, lab2, st2, _ = cv2.connectedComponentsWithStats(pen, 8)
        near = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
        for j in range(1, k2):
            if st2[j, 4] > 12 and (near[lab2 == j] > 0).any():
                m[lab2 == j] = 1
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    m[cv2.dilate((Mj > 100).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = 0
    m[above] = 0
    return m


class Plates:
    """Clean plates: Bria fibo-edit-1.5 erased the old reflection on keyframes (media/shots/F4/v9_plates/kNNN_*);
    every other frame gets the two nearest plates carried over by a homography of the Bean around the hole."""

    def __init__(self, frames, Rr, Mj, hp, pdir):
        """pdir/chosen.json: {key frame: [plate dir, chosen Bria output]}; each plate dir holds kNNN_in.png (the crop
        sent), kNNN_mask.png (the hole) and boxes*.json (crop corners)."""
        self.fr, self.Rr, self.Mj, self.hp = frames, Rr, Mj, hp
        self.P, self.keys = {}, []
        chosen = {int(k): v for k, v in json.load(open(os.path.join(pdir, "chosen.json"))).items()}
        for k, (d, name) in sorted(chosen.items()):
            d = os.path.join(ROOT, d)
            boxes = {}
            for fn in sorted(os.listdir(d)):
                if fn.startswith("boxes") and fn.endswith(".json"):
                    boxes.update({int(kk): v for kk, v in json.load(open(os.path.join(d, fn))).items()})
            x0, y0 = boxes[k]
            src = os.path.join(d, name)
            pdir_k = d
            crop = cv2.imread(os.path.join(pdir_k, f"k{k:03d}_in.png"))
            ch, cw = crop.shape[:2]
            gen = cv2.resize(cv2.imread(src), (cw, ch), interpolation=cv2.INTER_AREA).astype(np.float32)
            m = cv2.imread(os.path.join(pdir_k, f"k{k:03d}_mask.png"), 0) > 127
            # match the generated fill to the frame: low-frequency colour offset measured on a ring round the hole
            ring = (cv2.dilate(m.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0) & ~m
            dif = (crop.astype(np.float32) - gen) * ring[..., None]
            num = cv2.GaussianBlur(dif, (0, 0), 25)
            den = cv2.GaussianBlur(ring.astype(np.float32), (0, 0), 25)[..., None]
            gen = gen + num / np.maximum(den, 1e-3) * (den > 0.02)
            mf = cv2.GaussianBlur(cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 2)[..., None]
            P = frames[k].astype(np.float32).copy()
            P[y0:y0 + ch, x0:x0 + cw] = crop * (1 - mf) + gen * mf
            self.P[k] = P
            self.keys.append(k)

    def homography(self, k, i):
        if k == i:
            return np.eye(3)
        H, W = self.fr[0].shape[:2]
        gk = cv2.cvtColor(self.fr[k], cv2.COLOR_BGR2GRAY)
        gi = cv2.cvtColor(self.fr[i], cv2.COLOR_BGR2GRAY)
        c = int(self.hp[k]) + CHIN
        roi = np.zeros((H, W), np.uint8)
        roi[max(0, c - 60):min(H, c + 420), XC - 520:XC + 520] = 255
        bad = old_mask(self.Rr[k], self.Mj[k], c, H, W) | (self.Mj[k] > 50)
        roi[cv2.dilate(bad.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0] = 0
        pts = cv2.goodFeaturesToTrack(gk, 600, 0.01, 6, mask=roi)
        if pts is None or len(pts) < 12:
            return None
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(gk, gi, pts, None, winSize=(25, 25), maxLevel=4)
        back, st2, _ = cv2.calcOpticalFlowPyrLK(gi, gk, nxt, None, winSize=(25, 25), maxLevel=4)
        ok = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(back - pts, axis=2)[:, 0] < 1.0)
        if ok.sum() < 12:
            return None
        Hm, _ = cv2.findHomography(pts[ok], nxt[ok], cv2.RANSAC, 2.0)
        return Hm

    def __call__(self, i):
        lo = [k for k in self.keys if k <= i]
        hi = [k for k in self.keys if k >= i]
        cand = ([lo[-1]] if lo else []) + ([hi[0]] if hi and (not lo or hi[0] != lo[-1]) else [])
        H, W = self.fr[0].shape[:2]
        acc, wsum = np.zeros((H, W, 3), np.float32), 0.0
        for k in cand:
            Hm = self.homography(k, i)
            if Hm is None:
                continue
            # nearest plate only, with a short cross-fade at the midpoint: blending two different fills ghosts
            t = 0.5 if len(cand) == 1 else abs(i - k) / abs(cand[1] - cand[0])
            w = float(np.clip((0.5 - t) / 0.25 + 0.5, 0, 1)) if len(cand) == 2 else 1.0
            if w <= 0:
                continue
            acc += w * cv2.warpPerspective(self.P[k], Hm, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            wsum += w
        return acc / wsum if wsum > 0 else None


def ring_params(gray, valid, cx0, cy0, prev=None):
    """Centre and aspect of the ripple ellipses: the fit whose rings are most uniform."""
    ys, xs = np.where(valid)
    sel = np.random.default_rng(0).choice(len(xs), min(30000, len(xs)), replace=False)
    ys, xs = ys[sel].astype(np.float32), xs[sel].astype(np.float32)
    v = gray[ys.astype(int), xs.astype(int)].astype(np.float32)

    def cost(cx, cy, asp):
        b = (np.sqrt((xs - cx) ** 2 + ((ys - cy) / asp) ** 2) / 3).astype(int)
        cnt = np.bincount(b)
        s = np.bincount(b, v)
        s2 = np.bincount(b, v * v)
        ok = cnt > 5
        return (s2[ok] - s[ok] ** 2 / cnt[ok]).sum() / cnt[ok].sum()
    if prev is None:
        grid = [(cx, cy, asp) for asp in np.arange(0.55, 1.01, 0.05) for cy in range(int(cy0) - 80, int(cy0) + 81, 8)
                for cx in range(cx0 - 30, cx0 + 31, 10)]
    else:
        cx, cy, asp = prev
        grid = [(cx + dx, cy + dy, asp + da) for dx in (-6, 0, 6) for dy in (-9, -6, -3, 0, 3, 6, 9) for da in (-0.03, 0, 0.03)]
    return min(grid, key=lambda g: cost(*g))


def ring_fill(im, valid, cx, cy, asp, rmax=760, nt=2048):
    """Fill along the ripple rings: in (radius, angle) every ring is filled across its gaps from its own pixels."""
    rho = np.arange(rmax, dtype=np.float32)
    th = np.linspace(0, 2 * np.pi, nt, endpoint=False).astype(np.float32)
    TH, RH = np.meshgrid(th, rho)
    mx = (cx + RH * np.cos(TH)).astype(np.float32)
    my = (cy + asp * RH * np.sin(TH)).astype(np.float32)
    P = cv2.remap(im.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    V = cv2.remap(valid.astype(np.float32), mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0) > 0.5
    out = P.copy()
    idx = np.arange(nt)
    for r in range(rmax):
        ok = V[r]
        if ok.sum() < 3 or ok.all():
            continue
        for c in range(3):
            out[r, :, c] = np.interp(idx, idx[ok], P[r, ok, c], period=nt)
    H, W = im.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, (yy - cy) / asp
    rr = np.sqrt(dx * dx + dy * dy)
    tt = np.mod(np.arctan2(dy, dx), 2 * np.pi) / (2 * np.pi) * nt
    return cv2.remap(out, tt.astype(np.float32), rr.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP), rr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--work", default=os.path.join(ROOT, "media/shots/F4/v9_work"))
    ap.add_argument("--plates", default=os.path.join(ROOT, "media/shots/F4/v9_plates2"))
    ap.add_argument("--debug", default=None)
    ap.add_argument("--last", type=int, default=104, help="last frame to process (later frames are copied)")
    ap.add_argument("--only", default=None, help="comma list of frames to process (debug)")
    ap.add_argument("--dump", default=None, help="with --only: write those output frames here as PNG")
    a = ap.parse_args()

    fr = read(a.src)
    H, W = fr[0].shape[:2]
    n = min(len(fr), a.last + 1)
    hp = track_band(fr)
    os.makedirs(a.work, exist_ok=True)
    json.dump([round(float(v), 1) for v in hp], open(os.path.join(a.work, "band.json"), "w"))
    Jr, Rr = masks(fr, hp, a.work, n)
    bean = read(MATTE)
    Mj = track_matte(fr, Jr, hp, n, a.work)
    R2 = masks_contact(fr, hp, a.work, n)
    plates = Plates(fr, Rr, Mj, hp, a.plates)
    print("plates:", plates.keys)
    yy, xx = np.mgrid[0:H, 0:W]

    out = [f.copy() for f in fr]
    dbg = []
    rp = None
    todo = [int(v) for v in a.only.split(",")] if a.only else range(n)
    for i in todo:
        im = fr[i].astype(np.float32)
        chin = hp[i] + CHIN
        if i >= LATE:   # her carried matte drags the old reflection's face up under her chin: nothing of her is there
            bot = float(np.interp(i, [80, 86, 92, 100], [118, 108, 98, 95]))
            below_chin = (np.abs(xx - XC) < 75) & (yy > hp[i] + bot) & ~head_zone(hp[i], H, W, True, i)
            Mj[i][below_chin] = 0
        Jm = Mj[i].astype(np.float32) / 255
        her = Mj[i] > 100
        # ---- remove the old reflection
        Rm = old_mask(Rr[i], Mj[i], chin, H, W, fr[i], R2[i] if i >= 60 else None, i >= LATE, i) > 0
        if i < RING:
            P = plates(i)
            base = im.copy()
            if P is not None:
                mf = cv2.GaussianBlur(Rm.astype(np.float32), (0, 0), 1.5)[..., None]
                base = im * (1 - mf) + P * mf
            # the old reflection's feet stood on her chin: a thin dark strip under her outline the plates keep
            strip = below_outline(hp[i], H, W) & ~below_outline(hp[i] + 30, H, W) & (np.abs(xx - XC) < 75)
            strip &= i < 62            # later the reflection's own head covers that strip
            b8 = np.clip(base, 0, 255).astype(np.uint8)
            g = cv2.cvtColor(b8, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(b8, cv2.COLOR_BGR2HSV)
            strip = cv2.dilate((strip & (g < 200)).astype(np.uint8), np.ones((5, 5), np.uint8))
            strip[her] = 0
            # its navy trouser hems peek out just above that line, under her chin and hair
            navy = ((hsv[..., 0] >= 95) & (hsv[..., 0] <= 130) & (hsv[..., 1] > 70) & (hsv[..., 2] < 140)
                    & (np.abs(xx - XC) < 75) & (yy > hp[i] + 100) & ~below_outline(hp[i] + 30, H, W))
            strip |= cv2.dilate(navy.astype(np.uint8), np.ones((5, 5), np.uint8))
            if strip.any():
                b8 = cv2.inpaint(b8, strip, 6, cv2.INPAINT_TELEA)
                base = b8.astype(np.float32)
                im = im.copy()
                im[strip > 0] = base[strip > 0]       # so Jade-on-top does not paste the hems back
        else:
            herd = cv2.dilate(her.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
            head = head_zone(hp[i], H, W, i >= LATE, i)
            herd |= head
            g = cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY)
            zone = (np.abs(xx - XC) < 520) & (yy > chin - 250)
            rp = ring_params(g, zone & ~herd & ~Rm, XC, chin - 30, rp)
            model, rr = ring_fill(im, ~herd & ~Rm, *rp)
            res = np.abs(im - model).max(2)                 # what is left of it: grey arms and hands off the rings
            bad = ((res > 40) & ~herd & (rr < 460) & (yy > hp[i] + 40)).astype(np.uint8)
            bad = cv2.morphologyEx(bad, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            Rm = (Rm | (cv2.dilate(bad, np.ones((11, 11), np.uint8)) > 0)) & ~her & ~head
            model, _ = ring_fill(im, ~herd & ~Rm, *rp)
            mf = cv2.GaussianBlur(Rm.astype(np.float32), (0, 0), 1.5)[..., None]
            base = im * (1 - mf) + model * mf
            # right under her chin the rings are hidden all round (her head, the old face), so the ring fill has
            # nothing of its own there: shade it as the dark dent her head is pushing into the liquid mirror
            bot = float(np.interp(i, [80, 86, 92, 100], [118, 108, 98, 95]))
            pit = ((xx - XC) / 78.0) ** 2 + ((yy - (hp[i] + bot)) / 44.0) ** 2 < 1
            pit = cv2.GaussianBlur((pit & ~head & ~her).astype(np.float32), (0, 0), 7)[..., None]
            ring_dark = np.median(im[(rr < 400) & ~Rm & ~herd & (g < 90)], 0) if ((rr < 400) & (g < 90)).any() else np.array([70, 55, 45])
            lum = cv2.cvtColor(np.clip(model, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
            shade = ring_dark * (0.75 + 0.5 * (lum / 255.0))
            base = base * (1 - pit) + shade * pit
        # ---- new reflection
        d = max(0.0, 1.0 - i / TC)
        r0 = M0 / (1 - M0)
        mh = r0 / (d + r0)
        yrc = chin + GAP0 * d
        op = 0.9 * float(np.clip((FADE1 - i) / (FADE1 - FADE0), 0, 1))
        if op > 0:
            src = reflection_source(Mj[i], Jr[i], hp[i], H, W) if i > REF else Jm
            refl, ra = reflect(im, src, chin, yrc, mh, H, W)
            if i > RIP0:     # the mirror starts to ripple under her: the reflection rides the rings
                refl, ra = ripple(refl, ra, XC, chin - 30, min(1.0, (i - RIP0) / 8.0), i)
            clip = cv2.cvtColor(bean[i], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
            ra = ra * clip * op
            refl = refl * (clip * op)[..., None]
            base = base * (1 - ra[..., None]) + refl
        # ---- Jade back on top, untouched
        res = base * (1 - Jm[..., None]) + im * Jm[..., None]
        out[i] = np.clip(res, 0, 255).astype(np.uint8)
        if a.debug and (a.only or i % 6 == 0):
            c0 = int(chin)
            y0 = max(0, c0 - 300)
            crop = lambda z: cv2.resize(z[y0:y0 + 600, XC - 400:XC + 400], (400, 300))
            tile = np.vstack([crop(fr[i]), crop(out[i])])
            cv2.putText(tile, str(i), (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            dbg.append(tile)
    if a.debug and dbg:
        while len(dbg) % 6:
            dbg.append(np.zeros_like(dbg[0]))
        cv2.imwrite(a.debug, np.vstack([np.hstack(dbg[r:r + 6]) for r in range(0, len(dbg), 6)]))
    if a.only:
        if a.dump:
            os.makedirs(a.dump, exist_ok=True)
            for i in todo:
                cv2.imwrite(os.path.join(a.dump, f"{i:03d}.png"), out[i])
        return
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24",
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", a.out],
                         stdin=subprocess.PIPE)
    for f in out:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", a.out)


def ripple(col, al, cx, cy, amt, i, asp=0.8, lam=72.0, amp=9.0):
    """Radial ripple displacement (rings of wavelength lam px, travelling outward) applied to a premultiplied layer."""
    H, W = al.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, (yy - cy) / asp
    r = np.sqrt(dx * dx + dy * dy) + 1e-3
    d = amp * amt * np.sin(2 * np.pi * (r / lam - 0.12 * i))
    mx = (xx + d * dx / r).astype(np.float32)
    my = (yy + d * dy / r * asp).astype(np.float32)
    col = cv2.remap(col, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = cv2.remap(al, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return col, al


def reflect(im, Jm, chin, yrc, mh, H, W, ss=2):
    """Premultiplied reflection colour and alpha (full frame)."""
    src = np.dstack([im * Jm[..., None], Jm])
    sig = max(0.0, 0.5 / mh - 0.5)
    if sig > 0.05:
        src = cv2.GaussianBlur(src, (0, 0), sig)
    y0 = int(max(0, np.floor(yrc - 40)))
    y1 = H
    x0, x1 = XC - 420, XC + 420
    oy, ox = np.mgrid[y0 * ss:y1 * ss, x0 * ss:x1 * ss].astype(np.float32) / ss + 0.5 / ss - 0.5
    u = oy - yrc
    q = FB * (np.exp(u / (mh * FB)) - 1)               # distance above her chin of the source point
    m = mh / (1 + q / FB)
    ys = chin - q
    xs = XC + (ox - XC) / np.maximum(m, 1e-3)
    big = cv2.remap(src.astype(np.float32), xs.astype(np.float32), ys.astype(np.float32), cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    small = cv2.resize(big, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    col = np.zeros((H, W, 3), np.float32)
    al = np.zeros((H, W), np.float32)
    tint = np.array([1.0, 0.95, 0.88], np.float32) * 0.9      # chrome: a touch cooler and darker than she is (BGR)
    col[y0:y1, x0:x1] = small[..., :3] * tint
    al[y0:y1, x0:x1] = small[..., 3]
    return col, al


if __name__ == "__main__":
    main()
