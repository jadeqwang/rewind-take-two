#!/usr/bin/env python3
"""Watercolor singing Jade (v3), step 4: her figure (the restored painting) laid over the clean engraved plates, so
the background of every first frame is the plate itself, pixel for pixel, and S1 / E3 / V3S share one figure, one
place and one scale (after tools/sing/comp.py; the silhouette here comes from BiRefNet on the painting, because the
watercolor portrait has blossom and mountains on its paper and no clean outline of its own).

    EPY tools/sing/wc_comp.py matte FIGURE                 -> media/sing/first/v3_her_alpha.png (sheet geometry, soft)
    MPY tools/sing/wc_comp.py comp FIGURE PLATE OUT [--mask=PNG]   -> OUT (cropped to media/sing/first/crop.json box)
    MPY tools/sing/wc_comp.py align FIGURE PLATE           # how well the painting's background matches the plate

(matte needs torch + BiRefNet: EPY = tools/engrave/.venv/bin/python; comp and align need only OpenCV: EPY or MPY.)

Edge colour: inside the soft edge band the figure's colour is pulled from just inside her silhouette (foreground
estimate), so the painting's own background never fringes her hair on a different plate."""
import json
import os
import sys

import numpy as np

try:
    import cv2
except ImportError:      # the torch venv has no OpenCV; matte() does not need it
    cv2 = None
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALPHA = os.path.join(ROOT, f"media/sing/first/{os.environ.get('WC_VER', 'v3')}_her_alpha.png")
CROP = json.load(open(os.path.join(ROOT, "media/sing/first/crop.json")))["box"]


def rd(p):
    return np.asarray(Image.open(p).convert("RGB"), np.float32)


def matte(fig):
    import torch
    sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
    from matte import get_birefnet
    from gpulock import GpuSlot
    a = rd(fig)
    slot = GpuSlot(label="wc_comp")
    slot.acquire()
    net = get_birefnet("cuda")
    x = torch.from_numpy(a / 255).permute(2, 0, 1)[None].cuda()
    H, W = a.shape[:2]
    # whole frame + two overlapping halves at full attention for the hair wisps, max-merged
    m = net(x)[0, 0].cpu().numpy()
    for x0, x1 in ((0, W * 5 // 8), (W * 3 // 8, W)):
        m[:, x0:x1] = np.maximum(m[:, x0:x1], net(x[..., x0:x1])[0, 0].cpu().numpy() * (m[:, x0:x1] > 0.02))
    # she is the only colour and the only large connected figure: keep the component that holds the frame centre
    from scipy import ndimage as ndi
    lab, n = ndi.label(m > 0.5)
    keep = lab[int(H * 0.6), W // 2]
    region = ndi.binary_dilation(lab == keep, iterations=20)
    m = m * region
    Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).save(ALPHA)
    print(os.path.relpath(ALPHA, ROOT), "coverage", round(float((m > 0.5).mean()), 3))


def foreground(F, a):
    """Colour just inside the silhouette, spread outward over the soft edge band."""
    core = (a > 0.92).astype(np.float32)
    num = np.zeros_like(F); den = np.zeros_like(core)
    for s in (1.5, 3, 6):
        num += cv2.GaussianBlur(F * core[..., None], (0, 0), s) / s
        den += cv2.GaussianBlur(core, (0, 0), s) / s
    est = num / (den[..., None] + 1e-4)
    k = np.clip((0.92 - a) / 0.5, 0, 1)[..., None] * (den[..., None] > 1e-3)
    return F * (1 - k) + est * k


def refine(F, a):
    """Where the painting left bare white paper behind her hair (the sky over her head), the wisps are dark on white,
    so their true coverage is a luminance key; BiRefNet's soft band there is only a blur. Elsewhere its matte stays."""
    lum = F @ np.array([0.299, 0.587, 0.114], np.float32)
    band = (a > 0.02) & (a < 0.98)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    bg = cv2.dilate(lum, k)                                    # the lightest thing nearby = the paper
    white = cv2.erode((cv2.GaussianBlur(np.where(a < 0.5, lum, 255.0).astype(np.float32), (0, 0), 6) > 215).astype(np.uint8),
                      np.ones((9, 9), np.uint8)) > 0             # the painting's background here is bare paper
    key = np.clip((bg - lum) / np.maximum(bg - 70, 1), 0, 1)
    near = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    zone = (band | (near & (a <= 0.02))) & white & (bg > 215)
    out = np.where(zone, key, a)
    return np.clip(out, 0, 1).astype(np.float32)


def comp(fig, plate, out, choke=1.0, mask_out=None):
    F, P = rd(fig), rd(plate)
    if F.shape != P.shape:
        P = np.asarray(Image.fromarray(P.astype(np.uint8)).resize((F.shape[1], F.shape[0]), Image.LANCZOS), np.float32)
    a = refine(F, np.asarray(Image.open(ALPHA), np.float32) / 255)
    if choke:
        a = np.clip((cv2.GaussianBlur(a, (0, 0), choke) - 0.08) / 0.84, 0, 1)
    C = foreground(F, a) * a[..., None] + P * (1 - a[..., None])
    x0, y0, x1, y1 = CROP
    Image.fromarray(np.clip(C, 0, 255).astype(np.uint8)[y0:y1, x0:x1]).save(out, quality=96)
    if mask_out:
        Image.fromarray((a[y0:y1, x0:x1] * 255).astype(np.uint8)).save(mask_out)
    print(out, "crop", CROP)


def align(fig, plate):
    F, P = rd(fig), rd(plate)
    a = np.asarray(Image.open(ALPHA), np.float32) / 255
    far = cv2.dilate((a > 0.05).astype(np.uint8), np.ones((61, 61), np.uint8)) == 0
    x0, y0, x1, y1 = CROP
    box = np.zeros_like(far); box[y0:y1, x0:x1] = True
    far &= box
    g1, g2 = F.mean(2), P.mean(2)
    d = np.abs(g1 - g2)[far]
    sh, resp = cv2.phaseCorrelate(np.where(far, g2, 0).astype(np.float64), np.where(far, g1, 0).astype(np.float64))
    print(f"background mean |diff| {d.mean():.1f}/255, p90 {np.percentile(d, 90):.1f}; shift {np.round(sh, 2)} (resp {resp:.2f})")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    if a[0] == "matte":
        matte(a[1])
    elif a[0] == "comp":
        comp(a[1], a[2], a[3], float(o.get("choke", 1.0)), o.get("mask"))
    elif a[0] == "align":
        align(a[1], a[2])
