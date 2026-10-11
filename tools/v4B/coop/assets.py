#!/usr/bin/env python3
"""Co-op level assets cut from the engraved takes and the clean plate (all 1920x1080, design px):
  plate.png          the clean plate (kf_plate_v1, no girls, pencil or buttons), resized to the frame
  pencil.png         full-frame RGBA: only the giant pencil, cut from C1 engraved take at 2.5 s (nobody on it)
  btn_l.png, btn_r.png  full-frame RGBA: one button each, cut from C1 engraved frame 0 (difference to the plate)
  kf_c1_comp.png     C1 first frame rebuilt with both girls moved back from the gap (girls from frame 0 + matte)
    tools/engrave/.venv/bin/python tools/v4B/coop/assets.py
"""
import os
import cv2
import numpy as np

D = "/home/jade/Documents/rewind-take-two/media/shots/C_coop"
W, H = 1920, 1080
PENCIL = np.array([[548, 596], [1336, 596], [1432, 630], [1336, 668], [548, 668]], np.int32)   # eraser .. point
BTN_L, BTN_R = (300, 600, 505, 720), (1425, 600, 1630, 720)


def frame(path, t):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, round(t * 24))
    ok, f = cap.read()
    return cv2.resize(f, (W, H)) if f.shape[1] != W else f


def rgba(img, mask, feather=1.5):
    a = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), feather) if feather else mask.astype(np.float32)
    return np.dstack([img, np.clip(a * 255, 0, 255).astype(np.uint8)])


def main():
    plate = cv2.resize(cv2.imread(f"{D}/kf_plate_v1.jpg"), (W, H), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"{D}/plate.png", plate)
    eng = f"{D}/c1/take_1_engraved.mp4"
    f25, f0 = frame(eng, 2.5), frame(eng, 0.0)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [PENCIL], 1)
    cv2.imwrite(f"{D}/pencil.png", rgba(f25, m > 0))
    for name, (x0, y0, x1, y1) in (("btn_l", BTN_L), ("btn_r", BTN_R)):
        d = np.abs(cv2.GaussianBlur(f0, (0, 0), 1.5).astype(np.int16) - cv2.GaussianBlur(plate, (0, 0), 1.5).astype(np.int16)).max(2)
        bm = np.zeros((H, W), np.uint8)
        bm[y0:y1, x0:x1] = (d[y0:y1, x0:x1] > 30).astype(np.uint8)
        bm = cv2.morphologyEx(bm, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(bm)
        k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        bm = (lab == k).astype(np.uint8)
        cnt, _ = cv2.findContours(bm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        hull = np.zeros_like(bm)
        cv2.fillPoly(hull, [cv2.convexHull(cnt[0])], 1)
        cv2.imwrite(f"{D}/{name}.png", rgba(f0, hull > 0))
        ys, xs = np.nonzero(hull)
        print(name, "box", xs.min(), ys.min(), xs.max(), ys.max())
    # plate patches drawn over the sprites: the hinge (the pencil's short tail turns down into the right table when the
    # bridge is raised) and a strip under each button (a held button sinks into the table)
    hinge = np.zeros((H, W), np.uint8)
    hinge[672:1080, 1150:1330] = 1
    cv2.imwrite(f"{D}/patch_hinge.png", rgba(plate, hinge > 0, 0))
    for name, (x0, y0, x1, y1) in (("strip_l", BTN_L), ("strip_r", (1437, 613, 1630, 720))):
        st = np.zeros((H, W), np.uint8)
        st[y1 - 2:y1 + 40, x0 - 6:x1 + 6] = 1
        cv2.imwrite(f"{D}/patch_{name}.png", rgba(plate, st > 0, 0))
    # C1 first frame, girls moved back: ORANGE (left) -230 px, BLUE (right) -330 px, BLUE drawn behind ORANGE
    mt = cv2.imread(f"{D}/c1/take_1_matte/00000.png", 0) > 127
    X = np.arange(W)[None, :]
    girls = {"L": mt & (X < 615), "R": mt & (X >= 615)}
    comp = plate.copy()
    for lay in (cv2.imread(f"{D}/pencil.png", -1), cv2.imread(f"{D}/btn_l.png", -1), cv2.imread(f"{D}/btn_r.png", -1)):
        a = lay[..., 3:4] / 255.0
        comp = (comp * (1 - a) + lay[..., :3] * a).astype(np.uint8)
    for key, dx in (("R", -330), ("L", -230)):
        a = cv2.GaussianBlur(girls[key].astype(np.float32), (0, 0), 1.0)
        M = np.float32([[1, 0, dx], [0, 1, 0]])
        src = cv2.warpAffine(f0, M, (W, H))
        aa = cv2.warpAffine(a, M, (W, H))[..., None]
        comp = (comp * (1 - aa) + src * aa).astype(np.uint8)
    cv2.imwrite(f"{D}/kf_c1_v8.png", comp)
    print("written", f"{D}/kf_c1_v8.png")


if __name__ == "__main__":
    main()
