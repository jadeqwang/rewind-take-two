#!/usr/bin/env python
"""Visual check of ghost freezes: for each (clip_stem, t) show engraved frame | matte | colourised ghost cut-out.
    ghostcheck.py OUT.jpg media/shots/E2/take_fld_slide_1:3.15 ...  [--matte=SUFFIX]"""
import sys
import av
import cv2
import numpy as np
from PIL import Image

def frame(p, i):
    with av.open(p) as c:
        for k, f in enumerate(c.decode(video=0)):
            if k == i:
                return np.asarray(f.to_image().convert('RGB'))

out = sys.argv[1]
msuf = next((a.split('=')[1] for a in sys.argv if a.startswith('--matte=')), '_matte')
rows = []
for spec in [a for a in sys.argv[2:] if not a.startswith('--')]:
    stem, t = spec.rsplit(':', 1)
    i = round(float(t) * 24)
    e = frame(stem + '_engraved.mp4', i)
    m = cv2.imread(f'{stem}{msuf}/{i:05d}.png', 0)
    m = cv2.resize(m, (e.shape[1], e.shape[0])).astype(np.float32) / 255
    g = (e.mean(2, keepdims=True) / 255 * np.array([0.25, 0.45, 1.0]) * 255 * 1.4).clip(0, 255)
    ghost = (np.full_like(e, 236) * (1 - 0.6 * m[..., None]) + g * 0.6 * m[..., None]).astype(np.uint8)
    rows.append(np.hstack([e, (m[..., None].repeat(3, 2) * 255).astype(np.uint8), ghost]))
im = Image.fromarray(np.vstack(rows))
im = im.resize((1800, round(1800 * im.height / im.width)))
im.save(out, quality=85)
