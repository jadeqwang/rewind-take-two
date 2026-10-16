#!/usr/bin/env python3
"""Round 7 (round 6 redone on the r7 plate, plate_r7_base.png; same method): variants of her plate that
differ ONLY at the eye or the mouth, so the linework everywhere else is identical.
  half / blink : nano-banana edits of a 1:1 face crop (r6_half.png, r6_blink.png), registered back onto the crop by
                 phase correlation on the unchanged hair/cheek, then only a feathered ellipse round the eye pasted in
  press50/100  : a lip press made by WARPING her own lines (no redraw): the lower lip draws in and up a few px, the
                 upper lip settles a hair; a smooth Gaussian displacement field, so no seam is possible
Writes media/shots/D23/plate_r6_<name>.png at the plate's size (2752 x 1536). Run with tools/engrave/.venv/bin/python."""
import cv2, numpy as np
D = 'media/shots/D23'
base = cv2.imread(f'{D}/plate_r7_base.png')
X0, Y0, S = 660, 330, 480                      # the face crop sent to the model (plate px), resized to 1024
crop = base[Y0:Y0 + S, X0:X0 + S]
def register(edit):
    e = cv2.resize(edit, (S, S), interpolation=cv2.INTER_AREA)
    a = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float32); b = cv2.cvtColor(e, cv2.COLOR_BGR2GRAY).astype(np.float32)
    win = np.zeros_like(a); win[20:300, 20:200] = 1          # hair and ear, away from the eye and the mouth
    (dx, dy), r = cv2.phaseCorrelate(a * win, b * win)
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
    return cv2.warpAffine(e, M, (S, S), borderMode=cv2.BORDER_REPLICATE), (dx, dy, r)
def paste(edit_name, cx, cy, rx, ry):
    e, info = register(cv2.imread(f'{D}/{edit_name}.png'))
    m = np.zeros((S, S), np.float32); cv2.ellipse(m, (cx - X0, cy - Y0), (rx, ry), -15, 0, 360, 1, -1)
    m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    out = base.copy(); out[Y0:Y0 + S, X0:X0 + S] = (crop * (1 - m) + e * m).astype(np.uint8)
    return out, info
def press(k):
    H, W = base.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    def bump(cx, cy, sx, sy, dx, dy):
        g = np.exp(-((xx - cx) ** 2 / (2 * sx * sx) + (yy - cy) ** 2 / (2 * sy * sy))); return g * dx, g * dy
    ax, ay = bump(952, 662, 10, 8, 3.6 * k, 1.6 * k)     # lower lip: in (left) and up -> sample from right/below
    bx, by = bump(950, 642, 9, 6, 0.8 * k, -1.0 * k)    # upper lip settles down a hair
    cx_, cy_ = bump(940, 651, 6, 4, -1.2 * k, 0.0)       # the mouth line shortens at its inner end
    mx, my = xx + ax + bx + cx_, yy + ay + by + cy_
    return cv2.remap(base, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
if __name__ == '__main__':
    for name, (cx, cy, rx, ry) in {'r7_half': (910, 540, 44, 40), 'r7_blink': (910, 540, 44, 40)}.items():
        out, info = paste(name, cx, cy, rx, ry)
        cv2.imwrite(f'{D}/plate_{name.replace("r7_", "r7_")}.png', out); print(name, 'shift dx,dy,resp', [round(v, 2) for v in info])
    for k, nm in ((0.75, 'r7_press50'), (1.5, 'r7_press100')):
        cv2.imwrite(f'{D}/plate_{nm}.png', press(k)); print(nm)
