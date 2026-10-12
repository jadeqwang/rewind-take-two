"""v5-coda2: prepare the Round 3 assets (docs/revisions/v5/coda2.md).

    tools/engrave/.venv/bin/python tools/sectionF/coda/prep_coda2.py [door] [sprites] [idle NAME ...]

door   : media/shots/PC/door_frame_v2.png (door_frame.png + the brass push-plate patch from gen2/door_plate.jpg) and
         media/shots/PC/press_hand.png (the doorman's gloved hand from gen2/door_press.png, differenced against
         door_plate and refined by BiRefNet, in design px, with its offset in door_geom_v2.json)
sprites: media/shots/PC/sprites_v2/ (jade = gen2/jade_v3, glasses = gen2/glasses_v2, the other committee sprites
         copied, ghosts rebuilt from the new protagonist, the 8-bit sprite + a 2-frame idle partner) + info.json
idle   : the Seedance idle take of NAME (media/gen/v5_coda2_idle_<NAME>/take_N.mp4, chosen in IDLE below) -> BiRefNet
         matte (temporal smoothing) -> RGBA PNG frames in one fixed box, feet on the box bottom, scaled to the size it
         is shown at -> media/shots/PC/idle/<NAME>/f_0001.png ... + info.json
"""
import glob
import json
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
sys.path.insert(0, os.path.join(ROOT, "tools/sectionF/coda"))
PC = os.path.join(ROOT, "media/shots/PC")
G2 = os.path.join(PC, "gen2")


def design(path):
    """a 2752x1536 door still -> design px (cover-fit to 1920x1080), as prep_pc.door() does"""
    im = Image.open(path).convert("RGB")
    s = 1080 / im.height
    W = round(im.width * s)
    ox = (W - 1920) / 2
    return np.asarray(im.resize((W, 1080), Image.LANCZOS).crop((round(ox), 0, round(ox) + 1920, 1080)))


def birefnet_alpha(rgb):
    import torch
    from matte import get_birefnet
    x = torch.from_numpy(np.ascontiguousarray(rgb)).cuda().permute(2, 0, 1)[None].float() / 255
    return (get_birefnet()(x)[0, 0].clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)


PLATE = (1790, 600, 1920, 800)      # design px box around the brass push-plate (on the right stone pier)


def door():
    D0 = design(os.path.join(PC, "door.jpg"))
    P = design(os.path.join(G2, "door_plate.jpg"))
    Q = design(os.path.join(G2, "door_press.png"))
    # ---- the plate patch, feathered into the existing frame
    fr = np.asarray(Image.open(os.path.join(PC, "door_frame.png")).convert("RGBA")).copy()
    x0, y0, x1, y1 = PLATE
    m = np.zeros(fr.shape[:2], np.float32)
    m[y0:y1, x0:x1] = 1
    m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    fr[..., :3] = (fr[..., :3] * (1 - m) + P * m).astype(np.uint8)
    Image.fromarray(fr).save(os.path.join(PC, "door_frame_v2.png"))
    # ---- the hand: BiRefNet on the lower-right crop of door_press (the white glove is too close to the pale stone
    # for a difference key; BiRefNet alone gives the whole arm cleanly), largest component only
    bx0, by0, bx1, by1 = 1200, 500, 1920, 1080
    crop = Q[by0:by1, bx0:bx1]
    al = birefnet_alpha(crop)
    m = al > 128
    lab, k = ndimage.label(m)
    if k > 1:
        big = 1 + int(np.argmax(ndimage.sum(m, lab, range(1, k + 1))))
        al = (al * ndimage.binary_dilation(lab == big, iterations=3)).astype(np.uint8)
    Image.fromarray(np.dstack([crop, al])).save(os.path.join(PC, "press_hand.png"))
    ys, xs = np.where(al > 128)
    i = int(np.argmax(xs))
    tip = [int(xs[i] + bx0), int(ys[i] + by0)]           # the fingertip on the button (design px)
    geom = json.load(open(os.path.join(PC, "door_geom.json")))
    geom["press"] = {"xy": [int(bx0), int(by0)], "size": [int(bx1 - bx0), int(by1 - by0)], "tip": tip, "plate": PLATE}
    json.dump(geom, open(os.path.join(PC, "door_geom_v2.json"), "w"), indent=1)
    print("door v2 done; hand box", bx0, by0, bx1, by1, "tip", tip)


# ---- Round 4: the accessible push-plate on the right return of the entry (faces into the entrance), lower
R4_SRC = [(1685, 670), (1769, 662), (1782, 820), (1695, 814)]     # the plate as gen2/door_plate_r4_b drew it (design px)
R4_DST = [(1714, 864), (1774, 870), (1777, 977), (1716, 962)]     # ~6 in, below the wall's ledge and the handle's middle,
                                                                   # its edges sloping like that wall's ledge lines
S_DES = 1080 / 1536


def to_orig(p):
    return [((x + 8) / S_DES, y / S_DES) for x, y in p]


def plate_r4():
    """gen2/door_plate_r4c.jpg: the original door with the r4_b plate re-seated (scaled, lowered, sheared) on the return"""
    src = np.asarray(Image.open(os.path.join(G2, "door_plate_r4_b.jpg")).convert("RGB"))
    base = np.asarray(Image.open(os.path.join(PC, "door.jpg")).convert("RGB")).copy()
    Hm = cv2.getPerspectiveTransform(np.float32(to_orig(R4_SRC)), np.float32(to_orig(R4_DST)))
    warped = cv2.warpPerspective(src, Hm, (base.shape[1], base.shape[0]), flags=cv2.INTER_LANCZOS4)
    m = np.zeros(base.shape[:2], np.float32)
    cv2.fillPoly(m, [np.int32(np.round(to_orig(R4_DST)))], 1.0)
    m = cv2.GaussianBlur(m, (0, 0), 1.6)[..., None]
    out = (base * (1 - m) + warped * m).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(G2, "door_plate_r4c.jpg"), quality=95)
    print("plate_r4c written")


def _cx(a, b):
    return float(a[0] * b[1] - a[1] * b[0])


# ---- Round 5 (Jade: "the top of the button is not parallel to the groove in the wall it's on"): the plate is pinned
# into the plane of the pier's inner face. That face's horizontals (the groove right above the plate and the hatch lines
# around it, measured on the plate-free door) meet at VP_H; its two vertical edges meet at VP_V. A rectangle in that
# plane maps to a quad whose top/bottom edges run through VP_H and whose sides run through VP_V.
def _orig_gray():
    return np.asarray(Image.open(os.path.join(PC, "door.jpg")).convert("L")).astype(np.float32)


def wall_vps(verbose=True):
    im = _orig_gray()

    def band_slope(x0, x1, y0, y1):
        X0, Y0 = (x0 + 8) / S_DES, y0 / S_DES
        X1, Y1 = (x1 + 8) / S_DES, y1 / S_DES
        c = cv2.GaussianBlur(im[int(Y0):int(Y1), int(X0):int(X1)], (0, 0), 1.2)
        gx = cv2.Sobel(c, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(c, cv2.CV_32F, 0, 1, ksize=3)
        m = (np.abs(gy) > 2 * np.abs(gx)) & (np.hypot(gx, gy) > 20)
        Jxx, Jyy, Jxy = (gx * gx)[m].sum(), (gy * gy)[m].sum(), (gx * gy)[m].sum()
        return float(np.tan(0.5 * np.arctan2(2 * Jxy, Jxx - Jyy) + np.pi / 2))
    lines = [((1747.0, 852.0), band_slope(1695, 1795, 842, 862))]          # the groove right above the plate
    lines += [((1747.0, y + 10.0), band_slope(1700, 1795, y, y + 20)) for y in range(860, 1000, 20)]   # hatch rows
    A, b = [], []
    for (px, py), m in lines:
        n = np.array([-m, 1.0]) / np.hypot(m, 1.0)
        A.append(n)
        b.append(n @ np.array([px, py]))
    vph = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0]
    # the face's vertical edges (left: the wood stile / hatch boundary; right: the pier's corner), measured on the plate
    # -free door: left x 1665 @ y 450 -> 1690 @ y 1050; right x 1801 @ 870, 1805 @ 920, 1808 @ 970
    L = ((1665.0, 450.0), (1690.0, 1050.0))
    R = ((1801.0, 870.0), (1808.0, 970.0))

    def isect(p, q, r, s):
        p, q, r, s = map(np.array, (p, q, r, s))
        d1, d2 = q - p, s - r
        t = _cx(r - p, d2) / _cx(d1, d2)
        return p + t * d1
    vpv = isect(L[0], L[1], R[0], R[1])
    if verbose:
        print("groove/hatch slopes", [round(m, 3) for _, m in lines], "VP_H", vph.round(1), "VP_V", vpv.round(1))
    return vph, vpv, lines[0]


def _isect(p, q, r, s):
    p, q, r, s = map(lambda v: np.array(v, float), (p, q, r, s))
    d1, d2 = q - p, s - r
    t = _cx(r - p, d2) / _cx(d1, d2)
    return p + t * d1


def r5_quad(vph, vpv, tl=(1716.0, 866.0), x_right=1775.0, y_bottom_left=966.0):
    """the plate's corners in that plane: TL given; TR on the line TL-VP_H at x_right; the sides through VP_V; BL on the
    left side at y_bottom_left; BR where the line BL-VP_H meets the right side"""
    TL = np.array(tl)
    d = TL - vph
    TR = TL + d * (x_right - TL[0]) / d[0]
    dl = TL - vpv
    BL = TL + dl * (y_bottom_left - TL[1]) / dl[1]
    BR = _isect(BL, vph, TR, vpv)
    return [tuple(TL), tuple(TR), tuple(BR), tuple(BL)]


def plate_rim(src_rgb, base_rgb, rough):
    """the source plate's brass face, as 4 corners (orig px): an HSV brass key (the re-drawn hatching makes a difference
    key useless) -> largest component, holes filled -> convex hull -> 4 sides by line fits, neighbours intersected"""
    r = np.array(rough)
    x0, y0 = r.min(0).astype(int) - 25
    x1, y1 = r.max(0).astype(int) + 25
    hsv = cv2.cvtColor(np.ascontiguousarray(src_rgb[y0:y1, x0:x1]), cv2.COLOR_RGB2HSV).astype(int)
    H, S_, V = hsv[..., 0] * 2, hsv[..., 1], hsv[..., 2]
    m = ((H >= 30) & (H <= 62) & (S_ > 70) & (V > 70)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    lab, k = ndimage.label(m)
    m = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, k + 1))))).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    ap = cv2.approxPolyDP(hull, 0.04 * cv2.arcLength(hull, True), True).reshape(-1, 2).astype(np.float32)
    assert len(ap) == 4, ap
    # order TL, TR, BR, BL
    ssum, sdif = ap.sum(1), ap[:, 0] - ap[:, 1]
    q = np.array([ap[np.argmin(ssum)], ap[np.argmax(sdif)], ap[np.argmax(ssum)], ap[np.argmin(sdif)]])
    pts = c.reshape(-1, 2).astype(np.float32)

    def dist_seg(p, a, b):
        ab = b - a
        t = np.clip(((p - a) @ ab) / (ab @ ab), 0.15, 0.85)
        return np.hypot(*(p - (a + t[:, None] * ab)).T)
    D = np.stack([dist_seg(pts, q[i], q[(i + 1) % 4]) for i in range(4)], 1)
    side = D.argmin(1)
    fits = []
    for i in range(4):
        sp = pts[(side == i) & (D.min(1) < 6)]
        vx, vy, px, py = cv2.fitLine(sp, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        fits.append(((px, py), (px + vx, py + vy)))
    return [_isect(*fits[(i - 1) % 4], *fits[i]) + [x0, y0] for i in range(4)]


def plate_r5():
    """gen2/plate_r5_flat.png (the r4_b plate rectified to a flat rectangle), gen2/door_plate_r5.jpg (pinned into the
    pier face's plane), door_frame_r5.png, and the geometry in door_geom_r5.json (+ the check overlay)"""
    src = np.asarray(Image.open(os.path.join(G2, "door_plate_r4_b.jpg")).convert("RGB"))
    base = np.asarray(Image.open(os.path.join(PC, "door.jpg")).convert("RGB")).copy()
    rim = plate_rim(src, base, to_orig(R4_SRC))
    print("source rim (design px)", [(round(x * S_DES - 8, 1), round(y * S_DES, 1)) for x, y in rim])
    TW, TH, PAD = 240, 400, 9                               # flat texture: the brass face + a 9 px rim all round
    Hf = cv2.getPerspectiveTransform(np.float32(rim), np.float32([(PAD, PAD), (TW - PAD, PAD), (TW - PAD, TH - PAD), (PAD, TH - PAD)]))
    flat = cv2.warpPerspective(src, Hf, (TW, TH), flags=cv2.INTER_LANCZOS4)
    Image.fromarray(flat).save(os.path.join(G2, "plate_r5_flat.png"))
    vph, vpv, groove = wall_vps()
    Q = r5_quad(vph, vpv)
    print("plate quad (design px)", [tuple(np.round(p, 1)) for p in Q])
    Ht = cv2.getPerspectiveTransform(np.float32([(0, 0), (TW, 0), (TW, TH), (0, TH)]), np.float32(to_orig(Q)))
    warped = cv2.warpPerspective(flat, Ht, (base.shape[1], base.shape[0]), flags=cv2.INTER_LANCZOS4)
    m = np.zeros(base.shape[:2], np.float32)
    cv2.fillPoly(m, [np.int32(np.round(np.array(to_orig(Q)) * 4))], 1.0, shift=2)
    m = cv2.GaussianBlur(m, (0, 0), 0.9)[..., None]
    out = (base * (1 - m) + warped * m).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(G2, "door_plate_r5.jpg"), quality=95)
    # the frame: door_frame.png + the plate quad (design px)
    P = design(os.path.join(G2, "door_plate_r5.jpg"))
    fr = np.asarray(Image.open(os.path.join(PC, "door_frame.png")).convert("RGBA")).copy()
    mq = np.zeros(fr.shape[:2], np.float32)
    cv2.fillPoly(mq, [np.int32(np.round(np.array(Q) * 4))], 1.0, shift=2)
    mq = cv2.GaussianBlur(cv2.dilate(mq, np.ones((3, 3), np.uint8)), (0, 0), 1.0)[..., None]
    fr[..., :3] = (fr[..., :3] * (1 - mq) + P * mq).astype(np.uint8)
    Image.fromarray(fr).save(os.path.join(PC, "door_frame_r5.png"))
    geom = json.load(open(os.path.join(PC, "door_geom_r4.json")))
    cx, cy = np.mean(np.array(Q), 0)
    geom["press"]["plate"] = [list(map(float, p)) for p in Q]
    geom["press"]["plateCentre"] = [float(cx), float(cy)]
    geom["wall"] = {"vpH": vph.tolist(), "vpV": vpv.tolist()}
    json.dump(geom, open(os.path.join(PC, "door_geom_r5.json"), "w"), indent=1)
    # check overlay (design px, x4 zoom): the groove line and the plate's top and bottom edges extended toward VP_H,
    # the plate's sides extended toward VP_V
    x0, y0, x1, y1 = 1650, 800, 1840, 1000
    z = 4
    ov = Image.fromarray(fr[y0:y1, x0:x1, :3]).resize(((x1 - x0) * z, (y1 - y0) * z), Image.LANCZOS)
    from PIL import ImageDraw
    dr = ImageDraw.Draw(ov)
    Z = lambda p: ((p[0] - x0) * z, (p[1] - y0) * z)
    gp, gm = groove
    for p, col in ((np.array(gp), (0, 200, 255)), (np.array(Q[0]), (255, 0, 255)), (np.array(Q[3]), (255, 160, 0))):
        d_ = vph - p
        a, b_ = p - d_ * 0.06, p + d_ * 0.08 if col != (0, 200, 255) else p - d_ * -0.08
        dr.line([Z(p - d_ * 0.07), Z(p + d_ * 0.07)], fill=col, width=3)
    for p in (Q[0], Q[1]):
        d_ = np.array(p) - vpv
        dr.line([Z(np.array(p) - d_ * 0.03), Z(np.array(p) + d_ * 0.03)], fill=(120, 255, 120), width=2)
    ov.save(os.path.join(G2, "plate_r5_check.png"))
    return Q


def door_r4():
    """door_frame_r4.png (door_frame.png + the r4 plate) and press_hand_r4.png (BiRefNet on gen2/door_press_r4)"""
    P = design(os.path.join(G2, "door_plate_r4c.jpg"))
    # the hand: cut from door_press_r4.png. Nano put it on the door handle (and door_press_r4_b brought the arm in from
    # the lower left), but its pose is the one wanted: flat glove, fingers pointing left, back of the hand to camera, the
    # forearm from the right. hilbert_door.js scales / rotates it onto the plate (press.scale, press.baseRot, press.target).
    Q = design(os.path.join(G2, "door_press_r4.png"))
    fr = np.asarray(Image.open(os.path.join(PC, "door_frame.png")).convert("RGBA")).copy()
    m = np.zeros(fr.shape[:2], np.float32)
    cv2.fillPoly(m, [np.int32(R4_DST)], 1.0)
    m = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5), np.uint8)), (0, 0), 2)[..., None]
    fr[..., :3] = (fr[..., :3] * (1 - m) + P * m).astype(np.uint8)
    Image.fromarray(fr).save(os.path.join(PC, "door_frame_r4.png"))
    bx0, by0, bx1, by1 = 1270, 420, 1920, 1000
    crop = Q[by0:by1, bx0:bx1]
    al = birefnet_alpha(crop)
    mm = al > 128
    lab, k = ndimage.label(mm)
    if k > 1:
        big = 1 + int(np.argmax(ndimage.sum(mm, lab, range(1, k + 1))))
        al = (al * ndimage.binary_dilation(lab == big, iterations=3)).astype(np.uint8)
    Image.fromarray(np.dstack([crop, al])).save(os.path.join(PC, "press_hand_r4.png"))
    ys, xs = np.where(al > 128)
    geom = json.load(open(os.path.join(PC, "door_geom.json")))
    geom["press"] = {"xy": [bx0, by0], "size": [bx1 - bx0, by1 - by0], "plate": R4_DST,
                     "tip": [int(xs.min() + bx0), int(np.median(ys[xs <= xs.min() + 2]) + by0)],
                     "bbox": [int(xs.min() + bx0), int(ys.min() + by0), int(xs.max() + bx0), int(ys.max() + by0)]}
    json.dump(geom, open(os.path.join(PC, "door_geom_r4.json"), "w"), indent=1)
    print("door r4 done; hand bbox", geom["press"]["bbox"])


def sprites():
    import prep_pc
    SPV = os.path.join(PC, "sprites_v2")
    os.makedirs(SPV, exist_ok=True)
    info = json.load(open(os.path.join(PC, "sprites/info.json")))
    for n in ["teal", "purple", "braids", "plain", "sleepy", "rainbow", "mint"]:
        shutil.copy(os.path.join(PC, "sprites", n + ".png"), SPV)
    out = {n: info[n] for n in ["teal", "purple", "braids", "plain", "sleepy", "rainbow", "mint"]}

    def save(name, rgba):
        Image.fromarray(rgba).save(os.path.join(SPV, name + ".png"))
        out[name] = [int(rgba.shape[1]), int(rgba.shape[0])]
        print("  sprite", name, rgba.shape[1], rgba.shape[0])
    for name, src in (("jade", "jade_v3.jpg"), ("glasses", "glasses_v2.jpg")):
        save(name, prep_pc.key_figures(np.asarray(Image.open(os.path.join(G2, src)).convert("RGB")), 1)[0])
    jade = np.asarray(Image.open(os.path.join(SPV, "jade.png")))
    # ghosts are the protagonist's drawing at the committee sprites' resolution (~1340 px tall)
    h = 1339
    jade_s = np.asarray(Image.fromarray(jade).resize((round(jade.shape[1] * h / jade.shape[0]), h), Image.LANCZOS))
    for k, col in enumerate(["#F08A24", "#8DB8E8", "#C9A227", "#C23B8E", "#3FA55B", "#8E5CC8", "#2BA59A"]):
        save(f"ghost{k}", prep_pc.ghost(jade_s, col))
    # the 8-bit Jade (unchanged) + its idle partner: head and torso one pixel lower (the classic 2-frame breath)
    px = np.asarray(Image.open(os.path.join(PC, "sprites/pixel.png")))
    save("pixel", px)
    b = px.copy()
    legs = int(px.shape[0] * 0.58)
    b[1:legs + 1] = px[0:legs]
    b[0] = 0
    save("pixel_b", b)
    json.dump(out, open(os.path.join(SPV, "info.json"), "w"), indent=1)


if __name__ == "__main__":
    what = sys.argv[1:] or ["door", "sprites"]
    i = 0
    while i < len(what):
        w = what[i]
        if w == "idle":
            import idle_matte
            for n in what[i + 1:]:
                idle_matte.run(n)
            break
        globals()[w]()
        i += 1
