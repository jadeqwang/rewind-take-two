# Frame-by-frame scan of a rendered clip: python fdiff.py CLIP.mp4 START_TIME  (HELD = near-duplicate, SPIKE = cut/pop).
# per-frame mean abs difference of a clip; flags held frames (~0) and spikes (cuts / pops)
import sys, av, numpy as np
path, t0 = sys.argv[1], float(sys.argv[2])
prev = None; rows = []
for i, f in enumerate(av.open(path).decode(video=0)):
    a = f.to_ndarray(format='gray').astype(np.float32)[::2, ::2]
    if prev is not None: rows.append((i, round(t0 + i / 24, 3), float(np.abs(a - prev).mean())))
    prev = a
d = np.array([r[2] for r in rows]); med = np.median(d)
for i, t, v in rows:
    tag = 'HELD' if v < 0.25 * med else ('SPIKE' if v > 4 * med else '')
    if tag or (len(sys.argv) > 3): print(i, t, round(v, 2), tag)
print('median', round(med, 2))
