"""Round 7: share of each billboard panel's projected quad that is white in the visibility mask, per frame (dips = something crosses the lyric). Usage: billcov_r7.py MASK_FRAME_DIR"""
import json, subprocess, sys, glob
import cv2, numpy as np
d = sys.argv[1]
T = json.loads(subprocess.run(['node', '-e', "import('./tools/v9/d23/d23_tracks_r7.js').then(T=>console.log(JSON.stringify(T)))"], capture_output=True, text=True).stdout)
def key(keys, lt):
    best = min(keys, key=lambda k: abs(k[0] - lt)); return np.array(best[1]).reshape(4, 2)
cov = []
for f in sorted(glob.glob(d + '/f_*.png')):
    n = int(f[-9:-4]); k = 556 + n; t = k / 24
    m = cv2.imread(f, cv2.IMREAD_GRAYSCALE) > 128
    d2 = t < 25.34; lt = t - (23.16 if d2 else 25.34)
    tot = 0; white = 0
    for nm in (('D2_BILL_TOP', 'D2_BILL_BOT') if d2 else ('D3_BILL_TOP', 'D3_BILL_BOT')):
        q = key(T[nm], lt); poly = np.zeros(m.shape, np.uint8); cv2.fillPoly(poly, [np.round(q).astype(np.int32)], 1)
        tot += poly.sum(); white += (poly & m).sum()
    cov.append((k, white / max(1, tot)))
c = np.array([v for _, v in cov])
dips = [(k, round(v, 2)) for i, (k, v) in enumerate(cov) if 0 < i < len(cov) - 1 and v < 0.85 * max(cov[i - 1][1], cov[i + 1][1]) and k >= 575]
print('min cov (k>=575)', round(min(v for k, v in cov if k >= 575), 2), 'dips', dips[:12])
