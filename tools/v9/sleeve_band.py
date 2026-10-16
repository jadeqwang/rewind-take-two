"""v9 fix 10 (Jade 1:17, "jacket is missing orange stripes on arm"): paint the canon orange sleeve band onto V2c5 take 2.

Canon (inputs/jade_in_outfit.png): one orange band round each upper arm, continuing the chest band, stopping at the
side seam, so the back panel stays plain white with the pale-blue dot. In V2c5 we see her from behind; only her
RIGHT upper arm is visible (the left arm shows only the forearm and cuff reaching to the wheel, its upper arm is
hidden behind her back), so only the right sleeve gets the band.

Per frame:
  1. Geometry: the band is the visible (camera-facing) half of a ring round the upper arm, drawn in the reference
     frame (REF) as a strip whose centre line is a half-ellipse arc: across the arm (direction p) it spans the arm
     from the underside line (A_bot) to the top silhouette (A_top); along the arm it bows toward the elbow by `bow`
     px in the middle (the arm points away from camera, so the near half of the ring curves toward the elbow).
     Placement follows the band the edit model drew in media/shots/V2c5/kf_n2.jpg (before kf_v3 lost it), about a
     third of the way from the armhole seam to the elbow, as in the O2 back view (3:40).
  2. Tracking: an affine ECC fit of the upper arm (blurred grey, Jade's matte as the template mask) from REF to every
     frame moves the band with the arm.
  3. Paint (jacket_back.py in reverse): target = orange x the pixel's own shading (mean RGB / jacket white), only on
     neutral (white/grey/ink) pixels inside Jade's matte and a hand-drawn upper-arm clip, so the engraved hatching,
     fold lines and contours stay over the orange and nothing spills onto the back panel, the wheel or the torso.

    PY=tools/engrave/.venv/bin/python   # cv2, av, numpy
    $PY tools/v9/sleeve_band.py                       # writes media/shots/V2c5/take_2_engraved_v9sleeve.mp4
    $PY tools/v9/sleeve_band.py --check 7,30,56 --outdir DIR   # before/after crops only
"""
import argparse
import os
import subprocess

import av
import cv2
import numpy as np

ROOT = "/home/jade/Documents/rewind-take-two"
SHOT = f"{ROOT}/media/shots/V2c5"
SRC, MATTE = f"{SHOT}/take_2_engraved.mp4", f"{SHOT}/take_2_matte/matte.mp4"
OUT = f"{SHOT}/take_2_engraved_v9sleeve.mp4"
FFMPEG = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/"
                            "imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")

REF = 7   # first source frame the cut uses (C.js: in 0.3 s, rate 1.2 -> source frames 7..56)
P = {
    "C": [592, 781],            # ring centre in REF (1920x1080)
    "p": [0.70, -0.71],         # across the arm, toward the top silhouette
    "A_top": 95, "A_bot": 118,  # half-spans across the arm (to the top silhouette / to the underside line)
    "bow": 28,                  # px the band's middle bows toward the elbow
    "width": 46,                # band thickness along the arm
    "orange": [242, 134, 80],   # lit orange = her trouser straps in this shot (median 242,137,90)
    "white_lum": 240.0,         # lit jacket white (sleeve p90 246,239,236)
    # upper-arm clip in REF: armhole seam, top silhouette, elbow, underside line
    "arm_poly": [[470, 700], [520, 650], [600, 640], [650, 690], [700, 760], [780, 800], [800, 900], [700, 920],
                 [560, 880], [470, 850], [455, 780]],
}
BOX = (430, 600, 830, 960)    # ECC region (x0, y0, x1, y1)
H, W = 1080, 1920


def load(path, fmt="rgb24"):
    with av.open(path) as c:
        return [f.to_ndarray(format=fmt) for f in c.decode(video=0)]


def ref_masks():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    C = np.array(P["C"], np.float32)
    ph = np.array(P["p"], np.float32)
    ph /= np.linalg.norm(ph)
    ah = np.array([-ph[1], ph[0]], np.float32)       # along the arm
    if ah[0] + ah[1] < 0:                             # point it toward the elbow (down-right)
        ah = -ah
    dx, dy = xx - C[0], yy - C[1]
    v = dx * ph[0] + dy * ph[1]
    u = dx * ah[0] + dy * ah[1]
    A = np.where(v >= 0, P["A_top"], P["A_bot"])
    q = np.clip(v / A, -1, 1)
    d = u - P["bow"] * np.sqrt(np.clip(1 - q * q, 0, 1))
    hw = P["width"] / 2
    band = np.clip(hw + 0.75 - np.abs(d), 0, 1.5) / 1.5
    band *= np.clip((1.02 - np.abs(v / A)) * 40, 0, 1)
    clip = np.zeros((H, W), np.uint8)
    cv2.fillPoly(clip, [np.array(P["arm_poly"], np.int32)], 255)
    clip = cv2.GaussianBlur(clip.astype(np.float32) / 255, (0, 0), 1.0)
    return band.astype(np.float32), clip


def track(E, M):
    def prep(im):
        return cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), 2.5)
    G = [prep(e) for e in E]
    x0, y0, x1, y1 = BOX
    tm = np.zeros((H, W), np.uint8)
    tm[y0:y1, x0:x1] = 1
    tm &= (M[REF] > 128).astype(np.uint8)
    warps = np.zeros((len(E), 2, 3), np.float32)
    warps[REF] = np.eye(2, 3)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5)
    for order in (range(REF + 1, len(E)), range(REF - 1, -1, -1)):
        w = np.eye(2, 3, dtype=np.float32)            # warm start from the neighbour
        for i in order:
            _, w = cv2.findTransformECC(G[REF], G[i], w.copy(), cv2.MOTION_AFFINE, crit, tm, 5)
            warps[i] = w
    return warps


def paint(img, band, clip, matte):
    a = img.astype(np.float32)
    s = np.clip(a.mean(-1) / P["white_lum"], 0, 1)
    tgt = np.array(P["orange"], np.float32)[None, None, :] * s[..., None]
    sat = a.max(-1) - a.min(-1)
    neutral = np.clip((60 - sat) / 25, 0, 1)          # jacket white/grey/ink only
    m = band * clip * neutral * np.clip(matte.astype(np.float32) / 255 * 1.5 - 0.25, 0, 1)
    return np.clip(a + m[..., None] * (tgt - a) + 0.5, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="frame list: write before/after crops instead of the video")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--crf", type=int, default=12)
    a = ap.parse_args()
    E, M = load(SRC), load(MATTE, "gray")
    assert len(E) == len(M) == 97, (len(E), len(M))
    warps = track(E, M)
    b0, c0 = ref_masks()
    frames = [int(x) for x in a.check.split(",")] if a.check else range(len(E))
    out = []
    for i in frames:
        b = cv2.warpAffine(b0, warps[i], (W, H))
        c = cv2.warpAffine(c0, warps[i], (W, H))
        out.append(paint(E[i], b, c, M[i]))
    if a.check:
        from PIL import Image
        for i, o in zip(frames, out):
            t = np.concatenate([E[i][560:1000, 400:880], o[560:1000, 400:880]], 1)
            Image.fromarray(t).save(os.path.join(a.outdir, f"sleeve_{i:03d}.png"))
        return
    with av.open(SRC) as c:
        fps = c.streams.video[0].average_rate
    p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
                          "-tune", "grain", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for o in out:
        p.stdin.write(o.tobytes())
    p.stdin.close()
    assert p.wait() == 0
    print("wrote", OUT)


if __name__ == "__main__":
    main()
