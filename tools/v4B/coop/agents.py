"""v4 phase 3: matte of the two agents in media/shots/C_coop/agents/take_1.mp4 (black suits on blank paper).
Ink darker than the paper, closed and hole-filled (faces and shirts are white inside ink outlines); thin strokes the
model drew (the springboard line at ~2.5 s) are dropped.  ->  agents/take_1_matte.mp4 (+ PNGs in take_1_matte/)
    tools/engrave/.venv/bin/python tools/v4B/coop/agents.py"""
import os
import subprocess
import cv2
import numpy as np

D = "/home/jade/Documents/rewind-take-two/media/shots/C_coop/agents"
FF = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
os.makedirs(f"{D}/take_1_matte", exist_ok=True)
cap = cv2.VideoCapture(f"{D}/take_1.mp4")
i = 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    ink = (g < 140).astype(np.uint8)
    m = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a > 1500 and h > 40 and not (h < 0.3 * w and h < 90):   # drop the flat springboard stroke
            keep[lab == k] = 1
    # fill holes: flood the background from the border
    ff = keep.copy() * 255
    h_, w_ = ff.shape
    mask = np.zeros((h_ + 2, w_ + 2), np.uint8)
    bg = ff.copy()
    cv2.floodFill(bg, mask, (0, 0), 128)
    holes = (bg == 0).astype(np.uint8)            # enclosed paper: fill only small holes (faces, shirts, cuffs),
    nh, lh, sh, _ = cv2.connectedComponentsWithStats(holes)   # not the paper between the two men
    filled = keep.copy()
    for k in range(1, nh):
        if sh[k, cv2.CC_STAT_AREA] < 2200:
            filled[lh == k] = 1
    filled = (filled * 255).astype(np.uint8)
    if 50 <= i <= 76:                             # the springboard wedge the model drew under them: a shape that lies
        nf, lf, sf, _ = cv2.connectedComponentsWithStats((filled > 0).astype(np.uint8))   # wholly in the lower part
        for k in range(1, nf):
            if sf[k, cv2.CC_STAT_TOP] > 420:
                filled[lf == k] = 0
    filled = cv2.GaussianBlur(cv2.erode(filled, np.ones((3, 3), np.uint8)), (0, 0), 1.0)
    cv2.imwrite(f"{D}/take_1_matte/{i:05d}.png", filled)
    i += 1
subprocess.run([FF, "-v", "error", "-y", "-framerate", "24", "-i", f"{D}/take_1_matte/%05d.png", "-c:v", "libx264", "-pix_fmt",
                "yuv420p", "-crf", "14", f"{D}/take_1_matte.mp4"], check=True)
print(i, "frames")
