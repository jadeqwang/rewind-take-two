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
