#!/usr/bin/env python3
"""Round 7: the plate for the moved camera (media/shots/D23/plate_r7_n.png, nano-banana edit of plate_r7_h).
  1. her skin: the model drew it uncoloured (white with engraved hatching); tint the bright pixels inside hand-drawn
     face/ear/neck and hand polygons warm peach (lines and hatching stay black: hatching + coloured pencil, the film's look)
  2. the sail: the TL's black triangular inner trim in the window's FRONT LOWER corner (where the mirror is mounted),
     painted into the green corner: it sits in front of the mirror's neck, as seen from inside the car
Writes media/shots/D23/plate_r7_base.png (2752 x 1536), which then goes through make_plate_r4.py like round 4's plate.
Run with tools/engrave/.venv/bin/python from the repo root."""
import cv2, numpy as np
D = 'media/shots/D23'
im = cv2.imread(f'{D}/plate_r7_n.png')
H, W = im.shape[:2]
f = im.astype(np.float32)
# ---- 1. skin tint
FACE = [(712, 520), (760, 500), (830, 470), (905, 452), (955, 470), (985, 560), (992, 600), (975, 640), (972, 680),
        (950, 700), (905, 712), (840, 735), (760, 740), (690, 730), (688, 640), (700, 570)]
HAND_UP = [(1510, 875), (1545, 845), (1600, 828), (1675, 828), (1682, 860), (1662, 902), (1642, 938), (1600, 948),
           (1560, 938), (1525, 915)]
HAND_LO = [(1566, 1000), (1600, 975), (1680, 955), (1760, 958), (1792, 1000), (1762, 1062), (1700, 1092), (1640, 1102),
           (1576, 1096), (1566, 1050)]
m = np.zeros((H, W), np.uint8)
for poly in (FACE, HAND_UP, HAND_LO): cv2.fillPoly(m, [np.int32(poly)], 255)
m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 3)
lum = f.mean(2); chroma = f.max(2) - f.min(2)
w = m * np.clip((lum - 120) / 80, 0, 1) * (chroma < 40)                 # bright, neutral pixels only (not the green)
SKIN = np.float32([206, 224, 253])                                       # BGR: warm light peach (D6's skin)
tinted = f * (SKIN / 255.0)
f = f * (1 - w[..., None]) + tinted * w[..., None]
# a faint cheek blush (D6 has one), under the eye
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
bl = np.exp(-(((xx - 930) / 30) ** 2 + ((yy - 595) / 16) ** 2)) * w * 0.35
f = f * (1 - bl[..., None]) + np.float32([180, 170, 248]) * bl[..., None]
# ---- 1b. pencils (Jade 2026-10-16: "the body of the pencils are now pink and blue when it's only the erasers that are
# those colors. the pencil body is yellow"): the model painted the shafts in the eraser colours. Recolour the pink/blue
# pieces below the ferrules to pencil yellow (hue only; the drawn shading and lines stay). The erasers are separate
# pieces above the metal bands (tops at y < 300) and keep their colours.
PX0, PY0, PX1, PY1 = 440, 200, 760, 620
sub8 = np.clip(f[PY0:PY1, PX0:PX1], 0, 255).astype(np.uint8)
hsv = cv2.cvtColor(sub8, cv2.COLOR_BGR2HSV).astype(np.float32)
hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
col = (((hh >= 140) | (hh <= 5)) | ((hh >= 85) & (hh <= 110))) & (ss > 40) & (vv > 90)
n, lab, st, _ = cv2.connectedComponentsWithStats(col.astype(np.uint8) * 255, 8)
shaft = np.zeros(col.shape, np.uint8)
for i in range(1, n):
    if st[i, 1] + PY0 >= 300: shaft[lab == i] = 255
# take in the anti-aliased rim too: tinted pixels next to a shaft piece
rim = cv2.dilate(shaft, np.ones((5, 5), np.uint8)) > 0
wgt = np.where(shaft > 0, 1.0, rim * np.clip((ss - 15) / 40, 0, 1) * ((hh >= 140) | (hh <= 5) | ((hh >= 85) & (hh <= 110))))
yel = hsv.copy(); yel[..., 0] = 22; yel[..., 1] = 190                   # golden pencil yellow, the drawn value kept
yel = cv2.cvtColor(yel.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
f[PY0:PY1, PX0:PX1] = f[PY0:PY1, PX0:PX1] * (1 - wgt[..., None]) + yel * wgt[..., None]
# ---- 2. the sail: black triangle in the window's front lower corner, a thin pale engraved edge on its rear side
CORNER, TOP, REAR = (1814, 697), (1811, 590), (1712, 697)
sail = np.zeros((H, W), np.uint8); cv2.fillPoly(sail, [np.int32([CORNER, TOP, REAR])], 255)
f[sail > 0] = (14, 13, 13)
# its rear edge catches a little light: one thin pale line just inside it (round 7 v2: no tick hatching, it read as a ruler
# at the tight end of the zoom)
cv2.line(f, (TOP[0] - 4, TOP[1] + 8), (REAR[0] + 8, REAR[1] - 4), (120, 120, 120), 2, cv2.LINE_AA)
cv2.imwrite(f'{D}/plate_r7_base.png', np.clip(f, 0, 255).astype(np.uint8))
print('wrote', f'{D}/plate_r7_base.png')

# ---- 3. (after engrave_still --matte-out) the Jade matte: BiRefNet took the seat and headrest too; clip it to a
# hand-drawn region round her (bun, pencils, back, legs), and add her tinted skin (the hands it half missed)
import os, sys
if os.path.exists(f'{D}/plate_r7_base_matte.png'):
    bm = cv2.imread(f'{D}/plate_r7_base_matte.png', cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    HER = [(530, 250), (700, 240), (1050, 330), (1050, 720), (1950, 760), (1950, 1536), (760, 1536), (760, 1420),
           (700, 1330), (612, 1280), (600, 1000), (598, 800), (615, 700), (600, 640), (560, 560), (500, 520), (495, 420),
           (510, 340)]
    reg = np.zeros((H, W), np.uint8); cv2.fillPoly(reg, [np.int32(HER)], 255)
    reg = cv2.GaussianBlur(reg.astype(np.float32) / 255, (0, 0), 1.5)
    skin = np.zeros((H, W), np.uint8)
    for poly in (FACE, HAND_UP, HAND_LO): cv2.fillPoly(skin, [np.int32(poly)], 255)
    skin = cv2.erode(skin, np.ones((5, 5), np.uint8)).astype(np.float32) / 255
    out = np.maximum(bm * reg, skin)
    cv2.imwrite(f'{D}/plate_r7_base_matte_fixed.png', (out * 255).astype(np.uint8))
    print('wrote', f'{D}/plate_r7_base_matte_fixed.png')
