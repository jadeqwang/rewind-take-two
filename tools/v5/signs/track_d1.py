"""track_d1.py (v5 signs): re-track the two blank gantry panels of D1 (media/shots/D1/take_1_engraved.mp4), one quad
per source frame, and write tools/v5/signs/tracks.js (D1_signL, D1_signR: [[k/24, [TL, TR, BR, BL]], ...]).

Why: the v3 tracks (render/timeline/_A_tracks.js) drift on the right panel from ~0.6 s (the quad shears to a
parallelogram), which the v4 black `pin` panels hid but the woodcut face shows.
How: the panel faces are the large near-white blobs above the horizon. For each blob, fit a line to each of its four
edges (median-filtered extreme pixels over the middle 70 % of the opposite span, so the rounded corners do not bend
them) and intersect. While a face is cut by the frame top (it rushes overhead from ~1.1 s), its height is extrapolated
from the bottom edge with the last fully-visible height/width ratio. A 3-frame centred smoothing removes pixel noise.
Run: $PY tools/v5/signs/track_d1.py [--debug out.jpg]
"""
import json, sys, subprocess, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

FF = os.path.expanduser('~/Documents/moongazing/.venv/bin/ffmpeg')
SRC = 'media/shots/D1/take_1_engraved.mp4'
N = 44   # frames used by D1 (1.78 s at 24 fps) plus one


def frames():
    raw = subprocess.run([FF, '-v', 'error', '-i', SRC, '-frames:v', str(N), '-vf', 'fps=24,format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8)
    return a.reshape(-1, 1080, 1920)


def fit_line(us, vs):
    """least squares v = a*u + b with one round of outlier rejection"""
    a, b = np.polyfit(us, vs, 1)
    r = np.abs(vs - (a * us + b)); keep = r < max(2.0, np.percentile(r, 80) * 1.5)
    return np.polyfit(us[keep], vs[keep], 1)


def edges(mask):
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cut = {'top': y0 <= 1, 'left': x0 <= 1, 'right': x1 >= mask.shape[1] - 2}
    cols = np.arange(int(x0 + 0.15 * (x1 - x0)), int(x1 - 0.15 * (x1 - x0)) + 1)
    rows = np.arange(int(y0 + 0.15 * (y1 - y0)), int(y1 - 0.15 * (y1 - y0)) + 1)
    top = np.array([np.nonzero(mask[:, c])[0].min() for c in cols]); bot = np.array([np.nonzero(mask[:, c])[0].max() for c in cols])
    left = np.array([np.nonzero(mask[r])[0].min() for r in rows]); right = np.array([np.nonzero(mask[r])[0].max() for r in rows])
    T = fit_line(cols.astype(float), top.astype(float)); B = fit_line(cols.astype(float), bot.astype(float))
    L = fit_line(rows.astype(float), left.astype(float)); R = fit_line(rows.astype(float), right.astype(float))
    return T, B, L, R, cut


def meet(h, v):
    """h: y = a x + b ; v: x = c y + d"""
    a, b = h; c, d = v
    y = (a * d + b) / (1 - a * c); return [c * y + d, y]


def track():
    """measured quads while both faces are whole; once the frame cuts a face, a per-frame scale + translation of the
    last whole frame's quads, fitted to the corners that are still visible (the gantry is nearly square-on, so it
    looms by scaling); after the faces are gone, the scale/translation are carried on geometrically."""
    F = frames(); meas = []
    for k, f in enumerate(F):
        m = f > 200
        m[620:] = False                         # faces are above the horizon
        m = ndimage.binary_opening(m, iterations=2)
        lab, n = ndimage.label(m)
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        big = [i + 1 for i in np.argsort(sizes)[::-1][:6] if sizes[i] > 3000]
        cands = []
        for i in big:
            ys, xs = np.nonzero(lab == i); w, h = np.ptp(xs) + 1, np.ptp(ys) + 1
            fill = len(xs) / (w * h)
            if fill > 0.8 and (1.2 < w / h < 3.5 or ys.min() <= 1 or xs.min() <= 1 or xs.max() >= 1918):
                cands.append((xs.mean(), i))
        cands.sort()
        if len(cands) < 2: break
        fr = {}
        for side, (_, i) in zip('LR', [cands[0], cands[-1]]):
            T, B, L, R, cut = edges(lab == i)
            q = [*meet(T, L), *meet(T, R), *meet(B, R), *meet(B, L)]
            ok = [not (cut['top'] or cut['left']), not (cut['top'] or cut['right']), not cut['right'], not cut['left']]
            fr[side] = (q, ok)
        meas.append(fr)
    whole = [k for k, fr in enumerate(meas) if all(all(fr[s][1]) for s in 'LR')]
    K = max(k for k in whole if all(j in whole for j in range(k + 1)))   # last frame of the uncut run from 0
    ref = np.array([meas[K]['L'][0], meas[K]['R'][0]]).reshape(-1, 2)   # 8 corners
    st = []
    for k in range(N):
        if k <= K: st.append(None); continue
        P, Q = [], []
        if k < len(meas):
            for si, side in enumerate('LR'):
                q, ok = meas[k][side]
                for c in range(4):
                    if ok[c]: P.append(ref[si * 4 + c]); Q.append(q[2 * c:2 * c + 2])
        if len(P) >= 2:   # least squares q = s * p + t
            P, Q = np.array(P), np.array(Q); pm, qm = P.mean(0), Q.mean(0)
            sc = ((P - pm) * (Q - qm)).sum() / ((P - pm) ** 2).sum(); st.append((sc, qm - sc * pm))
        else:             # carried on: the scale keeps growing at its last rate, the translation follows it
            (s1, t1), (s0, t0) = (st[-1] if st[-1] else (1.0, np.zeros(2))), (st[-2] if st[-2] else (1.0, np.zeros(2)))
            g = s1 / s0; st.append((s1 * g, t1 + (t1 - t0) * g))
    out = {'L': [], 'R': []}
    for k in range(N):
        for si, side in enumerate('LR'):
            if st[k] is None: q = np.array(meas[k][side][0])
            else: sc, t = st[k]; q = (ref[si * 4:si * 4 + 4] * sc + t).reshape(-1)
            out[side].append(q)
    for side in 'LR':   # centred 3-frame smoothing (ends kept)
        q = np.array(out[side]); s = q.copy(); s[1:-1] = (q[:-2] + 2 * q[1:-1] + q[2:]) / 4
        out[side] = [[round(k / 24, 4), [round(float(x), 1) for x in row]] for k, row in enumerate(s)]
    print('measured whole to frame', K, '; fitted/carried', N - K - 1, 'frames; tracked', len(meas))
    return F, out


if __name__ == '__main__':
    F, out = track()
    with open('tools/v5/signs/tracks.js', 'w') as fh:
        fh.write('// D1 gantry panel faces, one quad per source frame (k/24 s, TL TR BR BL, design px). Generated by\n'
                 '// tools/v5/signs/track_d1.py from media/shots/D1/take_1_engraved.mp4. Do not edit by hand.\n'
                 'export default {\n')
        for side in 'LR': fh.write(f'  D1_sign{side}: {json.dumps(out[side], separators=(",", ":"))},\n')
        fh.write('};\n')
    print('frames', len(out['L']), len(out['R']))
    if '--debug' in sys.argv:
        tiles = []
        for k in range(0, 33, 2):
            im = Image.fromarray(F[k]).convert('RGB'); d = ImageDraw.Draw(im)
            for side, c in (('L', (255, 0, 255)), ('R', (0, 200, 255))):
                q = out[side][k][1]; d.polygon([(q[0], q[1]), (q[2], q[3]), (q[4], q[5]), (q[6], q[7])], outline=c, width=4)
            tiles.append(im.resize((640, 360)))
        sheet = Image.new('RGB', (640 * 3, 360 * ((len(tiles) + 2) // 3)))
        for i, t in enumerate(tiles): sheet.paste(t, ((i % 3) * 640, (i // 3) * 360))
        sheet.save(sys.argv[sys.argv.index('--debug') + 1])
