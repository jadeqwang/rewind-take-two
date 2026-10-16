#!/usr/bin/env python3
"""Round 5: does the pinned TVA 1729 quad (d23_tracks_r5.js D3_PLATE_R3) sit on the plate the sedan card draws?
For every D3 film frame k (609..673): clip frame n = k - 556 of the beauty render (r5_src_frames), the track quad at
lt = k/24 - 25.34 (keys interpolated like the engine). Measures, inside the glass (billmask region + plate quad):
  out  = drawn-plate pixels (pale field) OUTSIDE the quad, as a share of the drawn plate (should be ~0)
  fill = share of the quad covered by the drawn plate (the quad should not float off it)
Writes a sheet of the four checkpoints with the quad outlined.
Run: tools/engrave/.venv/bin/python tools/v9/d23/plate_check.py"""
import json, re, subprocess, sys
import cv2, numpy as np
D = 'media/shots/D23'
js = subprocess.run(['node', '-e', "import('./tools/v9/d23/d23_tracks_r5.js').then(T=>console.log(JSON.stringify(T.D3_PLATE_R3)))"], capture_output=True, text=True).stdout
keys = json.loads(js)
def quad(lt):
    for i in range(len(keys) - 1):
        (t0, q0), (t1, q1) = keys[i], keys[i + 1]
        if t0 <= lt <= t1:
            u = (lt - t0) / (t1 - t0); return [a + (b - a) * u for a, b in zip(q0, q1)]
    return keys[-1][1] if lt > keys[-1][0] else keys[0][1]
rows, shots = [], {}
for k in range(609, 674):
    n, lt = k - 556, k / 24 - 25.34
    src = cv2.imread(f'{D}/r5_src_frames/f_{n:05d}.png')
    if src is None: continue
    q = np.array(quad(lt)).reshape(4, 2)
    poly = np.zeros(src.shape[:2], np.uint8); cv2.fillPoly(poly, [np.round(q).astype(np.int32)], 1)
    # the drawn plate: pale, low-chroma pixels near the quad (a box 60% bigger than it)
    c = q.mean(0); big = ((q - c) * 1.6 + c).astype(np.int32)
    near = np.zeros_like(poly); cv2.fillPoly(near, [big], 1)
    g = src.astype(np.float32); lum = g.mean(2); chroma = g.max(2) - g.min(2)
    pale = ((lum > 150) & (chroma < 30) & (near > 0)).astype(np.uint8)
    pale = cv2.morphologyEx(pale, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    tot = pale.sum(); w = np.linalg.norm(q[1] - q[0])
    if tot < 30 or w < 12: continue
    out = (pale & (1 - poly)).sum() / tot; fill = (pale & poly).sum() / max(1, poly.sum())
    rows.append((k, w, out, fill))
    if k in (636, 667) or abs(k / 24 - 26.5) < 0.021 or abs(k / 24 - 27.8) < 0.021:
        vis = src.copy(); cv2.polylines(vis, [np.round(q).astype(np.int32)], True, (0, 0, 255), 1)
        x0, y0 = np.maximum(0, big.min(0) - 20); x1, y1 = big.max(0) + 20
        shots[k] = cv2.resize(vis[y0:y1, x0:x1], (400, int(400 * (y1 - y0) / max(1, x1 - x0))))
for k, w, o, f in rows: print(f'f{k} {k/24:.2f}  quad {w:5.1f}px  drawn plate outside quad {o*100:5.1f}%  quad filled {f*100:5.1f}%')
print('max outside', max(r[2] for r in rows) * 100, '% ; min fill', min(r[3] for r in rows) * 100, '%')
if shots:
    h = max(v.shape[0] for v in shots.values()); S = np.zeros((h, 400 * len(shots), 3), np.uint8)
    for i, (k, v) in enumerate(sorted(shots.items())): S[:v.shape[0], i * 400:(i + 1) * 400] = v; cv2.putText(S, f'f{k}', (i * 400 + 4, 14), 0, 0.45, (0, 255, 0), 1)
    cv2.imwrite(sys.argv[1] if len(sys.argv) > 1 else 'plate_check.jpg', S)
