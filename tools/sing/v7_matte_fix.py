#!/usr/bin/env python3
"""Singing Jade (v7), S1: two fixes to the per-frame matte after the pencil key (v5_pencils.py --ferrule).

1. Pencil gap. The pale-blue-eraser pencil goes into light, see-through bun hair that BiRefNet drops, so in many frames
   (v7_sync_1080_open file frames 0-14, 65-89, 115-123, ...) the keyed pencil hovers 3-9 px above the dark hair with
   plate between. A detached piece of matte that holds eraser colour (pale blue or pink) is extended along its own long
   axis, from the end away from the eraser, until it meets her matte (at most 30 px), as wide as the pencil.
2. Plate slivers. A detached piece below the bun (more than 90 px under the top of her head) that is bright and
   uncoloured (mean luma > 150, mean saturation < 40) is the plate behind her (file frames 30-34: the white edge of a
   tower beside her right temple) and is removed. Dark detached pieces (flyaway strands) stay.

    EPY=tools/engrave/.venv/bin/python
    $EPY tools/sing/v7_matte_fix.py media/sing/S1/v7_sync_1080_open.mp4 media/sing/S1/v7_sync_1080_open_matte
        -> the PNGs updated in place (the pencil-keyed ones kept once in <matte>_pencils/); prints what changed per frame
"""
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image


def fix(rgb, m8):
    m = m8.astype(np.float32)
    b = (m8 > 100).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    if n < 3:
        return m8, []
    big = int(np.argmax(st[1:, 4]) + 1)
    top = int(np.nonzero(lab == big)[0].min())
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.int32)
    H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    eraser = (((H >= 92) & (H <= 122)) | (H >= 150) | (H <= 6)) & (S > 60) & (V > 110)
    body = lab == big
    dist_body = cv2.distanceTransform((~body).astype(np.uint8), cv2.DIST_L2, 5)
    notes = []
    for k in range(1, n):
        if k == big or st[k, 4] < 15:
            continue
        comp = lab == k
        ys, xs = np.nonzero(comp)
        if (comp & eraser).sum() >= 8 and st[k, 4] > 120:                 # a pencil
            gap = float(dist_body[comp].min())
            if gap < 1.5:
                continue
            P = np.stack([xs, ys], 1).astype(np.float32)
            c = P.mean(0)
            _, _, vt = np.linalg.svd(P - c, full_matrices=False)
            ax = vt[0]
            ey, ex = np.nonzero(comp & eraser)
            if np.dot(np.array([ex.mean(), ey.mean()]) - c, ax) > 0:
                ax = -ax                                                   # point away from the eraser
            proj = (P - c) @ ax
            width = max(4, int(round(st[k, 4] / max(proj.max() - proj.min(), 1) * 0.9)))
            end = c + ax * proj.max()
            for t in range(1, 31):
                q = end + ax * t
                qx, qy = int(round(q[0])), int(round(q[1]))
                if not (0 <= qx < b.shape[1] and 0 <= qy < b.shape[0]):
                    break
                if body[qy, qx] or dist_body[qy, qx] < 1.5:
                    cv2.line(m, (int(end[0]), int(end[1])), (qx, qy), 255, width)
                    notes.append(f"pencil gap {gap:.1f}px bridged ({t} px, w {width})")
                    break
        elif ys.min() > top + 90:
            if V[comp].mean() > 150 and S[comp].mean() < 40:                # plate sliver
                m[cv2.dilate(comp.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = 0
                notes.append(f"plate sliver removed at ({xs.min()},{ys.min()}) area {st[k, 4]}")
    return np.clip(m, 0, 255).astype(np.uint8), notes


def main(src, mdir):
    import av
    bak = mdir.rstrip("/") + "_pencils"
    if not os.path.exists(bak):
        shutil.copytree(mdir, bak)
    with av.open(src) as c:
        for i, f in enumerate(c.decode(c.streams.video[0])):
            p = os.path.join(bak, f"{i:05d}.png")
            if not os.path.exists(p):
                break
            m8 = np.asarray(Image.open(p))
            rgb = f.to_ndarray(format="rgb24")
            if rgb.shape[:2] != m8.shape:                    # v9w: 720p takes against 1080 mattes
                rgb = np.asarray(Image.fromarray(rgb).resize((m8.shape[1], m8.shape[0]), Image.LANCZOS))
            out, notes = fix(rgb, m8)
            Image.fromarray(out).save(os.path.join(mdir, f"{i:05d}.png"))
            if notes:
                print(i, "; ".join(notes))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
