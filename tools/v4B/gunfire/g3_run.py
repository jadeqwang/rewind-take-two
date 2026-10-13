"""v6 (Jade's note 1:42, "she seems to be running really slowly"): B2_G3, the earpiece close-up (102.46-104.22).

In the take (media/shots/B_g3ear/take_1_engraved.mp4) she jogs nearly in place: ~1 m/s at a 3 steps/s cadence.
This script prepares her to be lifted off the plate and pushed down the lawn toward the hotel (render/timeline/
_B_gunfire.js g3()):

  1. clean_v6.png      RGBA patch: the lawn without her or her cast shadow (camera is locked; per-pixel median over
                       the take's frames where the pixel is uncovered, cv2 inpaint for the few never-uncovered ones)
  2. take_1_jsmatte_v6/matte.mp4   luma matte, her (take_1_matte) + her hatched shadow (soft, from local ink density
                       against the clean lawn), so the shadow travels with her feet
  3. render/timeline/_B_g3run.js   per source frame: the ground-plane scale r about the heading vanishing point V.
                       Moving a figure standing at depth Z to Z + d along a ground direction is, on screen, a uniform
                       scale by Z / (Z + d) about that direction's vanishing point, so one similarity per frame does it.
                       d only grows on her airborne / landing drawings and holds while a foot is planted (no skating).

Run: tools/engrave/.venv/bin/python tools/v4B/gunfire/g3_run.py
"""
import json, os, subprocess
import numpy as np, cv2, av

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
D = os.path.join(ROOT, 'media/shots/B_g3ear')
FF = os.path.expanduser('~/Documents/moongazing/.venv/bin/ffmpeg')
W, H, FPS = 1920, 1080, 24
X0, Y0, X1, Y1 = 1100, 400, 1920, 900        # working ROI (her whole take + shadow)

# ---- geometry (measured from take_1_matte, see docs/revisions/v6/ear_run.md) --------------------------------------
YH = 535.0            # horizon: h / (y_feet - YH) is constant across her contacts (334 px @ 816, 290 px @ 779)
VX = 1900.0           # heading vanishing point x: her own drift in the take points at ~2000 (right half of the hotel)
# take is on twos; per 8-frame step: C C F L (pairs): planted, planted, airborne, landing. Contact pairs (first frame):
CONTACTS = {4: 816, 10: 807, 12: 807, 18: 798, 20: 799, 26: 793, 28: 793, 34: 785, 36: 785, 42: 779, 44: 778,
            50: 773, 52: 772, 58: 768, 60: 767}   # beyond 60 the take is not used
D_STEP = 0.118        # extra depth per step, in units of her starting distance (~1.25 m at ~10.5 m: see the doc)


def frames():
    c = av.open(os.path.join(D, 'take_1_engraved.mp4'))
    out = [f.to_ndarray(format='rgb24') for f in c.decode(video=0)]
    c.close(); return out


def mattes(n):
    return [cv2.imread(os.path.join(D, f'take_1_matte/{i:05d}.png'), 0) for i in range(n)]


def build_mattes_and_clean(F, M):
    n = len(F)
    roi = lambda a: a[Y0:Y1, X0:X1]
    G = np.stack([cv2.cvtColor(roi(f), cv2.COLOR_RGB2GRAY) for f in F]).astype(np.float32)
    ink = np.stack([cv2.GaussianBlur(255 - g, (0, 0), 5) for g in G])
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    body = np.stack([cv2.dilate((roi(m) > 60).astype(np.uint8), k) for m in M]).astype(bool)
    # pass 1: ink density of the lawn without her (her shadow still in some samples, the median ignores it)
    inkm = np.ma.masked_array(ink, body)
    ink_bg = np.ma.median(inkm, axis=0).filled(np.median(ink))
    # her shadow per frame: denser ink than the lawn, in a box left of / under her feet, attached to her
    shadows = []
    for i in range(n):
        ys, xs = np.nonzero(roi(M[i]) > 127)
        bot, cx = ys.max(), int(np.median(xs[ys > ys.max() - 0.2 * (ys.max() - ys.min())]))
        box = np.zeros_like(body[0]); box[max(0, bot - 50):bot + 28, max(0, cx - 330):cx + 70] = True
        excess = ink[i] - ink_bg
        s = (excess > 35) & box & ~(roi(M[i]) > 127)
        s = cv2.morphologyEx(s.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        nl, lab, st, _ = cv2.connectedComponentsWithStats(s)
        keep = np.zeros_like(s)
        foot = cv2.dilate((roi(M[i]) > 127).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
        for j in range(1, nl):
            if st[j, cv2.CC_STAT_AREA] > 150 and (foot[lab == j]).any(): keep[lab == j] = 1
        soft = np.clip((excess - 20) / 45, 0, 1) * cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        shadows.append(cv2.GaussianBlur(soft.astype(np.float32), (0, 0), 1.2))
    shadows = np.stack(shadows)
    # pass 2: clean lawn = per-pixel median of the RGB over frames where neither she nor her shadow is there
    cover = body | (np.stack([cv2.dilate((s > 0.05).astype(np.uint8), k) for s in shadows]) > 0)
    R = np.stack([roi(f) for f in F]).astype(np.float32)
    clean = np.zeros(R.shape[1:], np.float32)
    for ch in range(3):
        clean[..., ch] = np.ma.median(np.ma.masked_array(R[..., ch], cover), axis=0).filled(0)
    hole = cover.all(axis=0).astype(np.uint8)
    clean = clean.astype(np.uint8)
    if hole.any(): clean = cv2.inpaint(clean, hole, 5, cv2.INPAINT_TELEA)
    # patch alpha: everywhere she or her shadow ever is in the take, feathered
    ever = cover.any(axis=0).astype(np.uint8)
    a = cv2.GaussianBlur(cv2.dilate(ever, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))).astype(np.float32), (0, 0), 4)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[Y0:Y1, X0:X1, :3] = clean; rgba[Y0:Y1, X0:X1, 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(D, 'clean_v6.png'), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
    # matte: her (as cut) + her shadow
    out = os.path.join(D, 'take_1_jsmatte_v6'); os.makedirs(out, exist_ok=True)
    p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', os.path.join(out, 'matte.mp4')],
                         stdin=subprocess.PIPE)
    for i in range(n):
        m = M[i].astype(np.float32) / 255
        m[Y0:Y1, X0:X1] = np.maximum(m[Y0:Y1, X0:X1], shadows[i])
        p.stdin.write(np.clip(m * 255, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    return n


def run_track(n):
    """Per source frame: plate depth Z (her contact y, interpolated through the air), extra depth d, scale r."""
    zc = lambda y: (CONTACTS[4] - YH) / (y - YH)
    known = {c + k: y for c, y in CONTACTS.items() for k in (0, 1)}     # planted frames: the foot's ground y
    contact, ks = set(known), sorted(known)
    def plate_y(i):                                                       # airborne: interpolate between plants
        if i in known: return known[i]
        a = max([k for k in ks if k < i], default=ks[0]); b = min([k for k in ks if k > i], default=ks[-1])
        return known[a] if a == b else known[a] + (known[b] - known[a]) * (i - a) / (b - a)
    d, out = 0.0, []
    for i in range(n):
        if i > 4 and i not in contact and i <= 61: d += D_STEP / 4      # the four airborne / landing frames per step
        z = zc(plate_y(i))
        out.append({'i': i, 'z': round(z, 4), 'd': round(d, 4), 'r': round(z / (z + d), 5), 'planted': i in contact})
    return out


if __name__ == '__main__':
    F = frames(); M = mattes(len(F))
    n = build_mattes_and_clean(F, M)
    T = run_track(n)
    js = os.path.join(ROOT, 'render/timeline/_B_g3run.js')
    with open(js, 'w') as f:
        f.write('// generated by tools/v4B/gunfire/g3_run.py (v6, note 1:42): B2_G3 run, per source frame of\n'
                '// media/shots/B_g3ear/take_1_engraved.mp4. r = her scale about V (ground-plane push down the lawn).\n')
        f.write(f'export const G3RUN = {{ V: [{VX}, {YH}], r: {json.dumps([t["r"] for t in T])} }};\n')
    with open(os.path.join(D, 'run_v6.json'), 'w') as f: json.dump(T, f, indent=0)
    for t in T[:50]: print(t)
