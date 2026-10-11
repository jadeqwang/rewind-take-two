# F6b check (v3): run on frames extracted from the rendered clip: python penrose_track.py DIR (DIR holds f_<t>.png).
# Find agents in rendered frames (dense dark blobs), fit the tread table to them, report each agent's step index.
import json, sys, glob, numpy as np
from PIL import Image
from scipy import ndimage
tab = json.load(open('media/shots/F6b/kf_v3_F6b_steps.json'))
C = np.array([s['design'] for s in tab['steps']]) / 2.0          # preview px (960 wide)
N = len(C)
def blobs(path):
    g = np.asarray(Image.open(path).convert('L')).astype(np.float32)
    dark = ndimage.uniform_filter((g < 70).astype(np.float32), 5) > 0.55
    lab, n = ndimage.label(dark)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        cx = sl[1].start + w / 2; cy = sl[0].start + h / 2
        if 22 <= h <= 70 and 0.25 * h <= w <= 0.8 * h and abs(cx - 480) < 240 and 90 < cy < 380:   # standing figures on the clock face
            ys, xs = np.where(lab[sl] == i + 1)
            out.append((xs.mean() + sl[1].start, sl[0].stop))     # x centre, feet
    return np.array(out)
def fit(B):
    # similarity transform (s, theta, tx, ty) mapping tread centres onto agent feet: grid init + ICP
    best = None
    for s in np.linspace(1.1, 1.6, 11):
        for th in np.radians(np.linspace(-3, 3, 7)):
            for dy in np.linspace(-20, 60, 17):
                R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
                P = (C - [480, 270]) @ R.T * s + [480, 270 + dy]
                d = np.min(np.linalg.norm(B[:, None] - P[None], axis=2), 1)
                e = np.mean(np.minimum(d, 15))
                if best is None or e < best[0]: best = (e, P)
    return best
res = {}
for f in sorted(glob.glob(sys.argv[1] + '/f_*.png')):
    t = f.split('_')[-1][:-4]; B = blobs(f); e, P = fit(B)
    idx = [int(np.argmin(np.linalg.norm(P - b, axis=1))) for b in B]
    res[t] = sorted(zip(idx, [tuple(np.round(b).astype(int)) for b in B]))
    print(t, 'agents', len(B), 'fit err %.1f px' % e, 'steps', sorted(idx))
json.dump({k: [[i, list(map(int, p))] for i, p in v] for k, v in res.items()}, open(sys.argv[1] + '/track.json', 'w'))
# occupancy per frame (only blobs within 9 px of a fitted tread), then the shift that best maps frame n onto n+1
occ = {}
for f in sorted(glob.glob(sys.argv[1] + '/f_*.png')):
    t = f.split('_')[-1][:-4]; B = blobs(f); e, P = fit(B)
    o = {}
    for b in B:
        d = np.linalg.norm(P - b, axis=1); i = int(np.argmin(d))
        if d[i] < 9: o[i] = tuple(int(v) for v in np.round(b))
    occ[t] = o
    print(t, 'occupied', sorted(o))
ts = sorted(occ)
for a, b in zip(ts, ts[1:]):
    sc = {s: len({(i + s) % N for i in occ[a]} & set(occ[b])) for s in (-2, -1, 0, 1, 2)}
    print(a, '->', b, 'matches by shift', sc)
json.dump({t: {str(k): v for k, v in o.items()} for t, o in occ.items()}, open(sys.argv[1] + '/occ.json', 'w'))
