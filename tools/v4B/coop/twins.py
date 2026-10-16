#!/usr/bin/env python3
"""v9 #4: twin colours by identity, not by screen side (C2a_swap / C2b_letgo, take c2/take_1).

level.py split the two girls with one vertical seam per frame and recolour.py made everything right of it BLUE. In
c2/take_1 ORANGE (the springer) leaps over BLUE (crouched on the far button) at take frames ~40-50, and in C2b BLUE
rises from the button into ORANGE's silhouette (frames ~86-100), so the seam ran through bodies: half-orange/half-blue
girls, mixed jackets, colours flipping between the girls. Here each girl is tracked through the take with SAM 2.1
(video, two objects, local GPU, no paid calls) and every pixel of the existing girl matte (c2t1_Lc | c2t1_R, which
already has the agents and the pencil tip cleaned out) is given to the girl whose track holds it.

    tools/engrave/.venv/bin/python tools/v4B/coop/twins.py track   # SAM 2.1 -> media/shots/C_coop/c2t1_v9/track_{O,B}.npz
    tools/engrave/.venv/bin/python tools/v4B/coop/twins.py build   # -> c2t1_v9_{bo,bo_O,O,B}.mp4

Outputs (media/shots/C_coop/; c2t1_v9/ keeps the tracks and the PNG mattes):
  c2t1_v9_bo.mp4    the engraved take recoloured by identity: ORANGE orange, BLUE blue; bun and pencils, skin line art
                    (lips, eyelids, finger outlines) untouched. The BLUE layer's source.
  c2t1_v9_bo_O.mp4  the same, plus (C2a take frames only) the strip behind BLUE's head inpainted from ORANGE: C2a
                    draws BLUE 18 px lower than ORANGE, which opened a gap at the leap. The ORANGE layer's source.
  c2t1_v9_O.mp4     ORANGE's matte (replaces c2t1_Lc), c2t1_v9_B.mp4 BLUE's matte (replaces c2t1_R).
"""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recolor  # noqa: E402

D = "/home/jade/Documents/rewind-take-two/media/shots/C_coop"
OUT = f"{D}/c2t1_v9"
FF = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/"
                        "binaries/ffmpeg-linux-x86_64-v7.0.2")
SRC = f"{D}/c2/take_1_engraved.mp4"
SAM = "facebook/sam2.1-hiera-large"
O_ID, B_ID = 1, 2
# Prompt frames: the girls are apart. Boxes are the bounding boxes of level.py's L/R mattes on those frames
# (frame 30: ORANGE running in on the left, BLUE crouched on the far button; frame 104: BLUE on the left after
# letting go, ORANGE running out on the right). Positive points sit on each girl's torso.
PROMPTS = {
    30: {O_ID: (963, 91, 1432, 660), B_ID: (1442, 278, 1726, 719)},
    104: {B_ID: (1399, 133, 1699, 692), O_ID: (1709, 257, 1919, 693)},
}


def read_frames(path):
    import av
    return [f.to_ndarray(format="rgb24") for f in av.open(path).decode(video=0)]


def track():
    import torch
    from PIL import Image
    from transformers import Sam2VideoModel, Sam2VideoProcessor
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engrave"))
    from gpulock import GpuSlot
    frames = read_frames(SRC)
    n = len(frames)
    slot = GpuSlot(label="v9_twins")
    slot.acquire()
    dev = "cuda"
    model = Sam2VideoModel.from_pretrained(SAM).to(dev, dtype=torch.bfloat16)
    proc = Sam2VideoProcessor.from_pretrained(SAM)
    logits = {O_ID: np.zeros((n, 1080, 1920), np.float16), B_ID: np.zeros((n, 1080, 1920), np.float16)}
    seen = {O_ID: np.zeros(n, bool), B_ID: np.zeros(n, bool)}
    # one session per prompt frame, propagated both ways; the two passes are merged by distance to the prompt
    dist = np.full(n, 1e9)
    for pf, boxes in PROMPTS.items():
        sess = proc.init_video_session(video=[Image.fromarray(f) for f in frames], inference_device=dev,
                                       dtype=torch.bfloat16)
        ids = sorted(boxes)
        proc.add_inputs_to_inference_session(inference_session=sess, frame_idx=pf, obj_ids=list(ids),  # (the processor empties the list it is given)
                                             input_boxes=[[list(boxes[i]) for i in ids]])
        model(inference_session=sess, frame_idx=pf)
        for rev in (False, True):
            for out in model.propagate_in_video_iterator(sess, start_frame_idx=pf, reverse=rev):
                fi = out.frame_idx
                d = abs(fi - pf)
                if d > dist[fi]:
                    continue
                dist[fi] = d
                m = proc.post_process_masks([out.pred_masks], original_sizes=[[1080, 1920]], binarize=False)[0]
                for k, oid in enumerate(ids):
                    logits[oid][fi] = m[k, 0].float().cpu().numpy().astype(np.float16)
                    seen[oid][fi] = True
        del sess
        torch.cuda.empty_cache()
    os.makedirs(OUT, exist_ok=True)
    # keep it small: store the masks at half size as uint8 (sigmoid*255)
    for oid, name in ((O_ID, "O"), (B_ID, "B")):
        sm = np.stack([cv2.resize((1 / (1 + np.exp(-l.astype(np.float32))) * 255).astype(np.uint8), (960, 540),
                                  interpolation=cv2.INTER_AREA) for l in logits[oid]])
        np.savez_compressed(f"{OUT}/track_{name}.npz", p=sm)
    print("tracked", n, "frames; prompt frames", list(PROMPTS))


def read_mp4_gray(path):
    import av
    return [f.to_ndarray(format="gray") for f in av.open(path).decode(video=0)]


def top_keep(m, frac=0.16):
    """recolour.head_keep for one girl: the top `frac` of her own silhouette (bun and two pencils) stays as drawn"""
    ys = np.flatnonzero(m.any(1))
    if len(ys) < 20:
        return np.zeros(m.shape, bool)
    cut = int(ys[0] + frac * (ys[-1] - ys[0]))
    band = np.zeros(m.shape, bool)
    band[:cut + 1] = True
    return cv2.dilate((m & band).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool) & band


def skin_lines_out(cand, hsv, ring_px=6, max_skin=0.5):
    """the reddish-brown line art inside skin (lips, eyelids, nostrils, finger outlines) falls in recolor.masks' orange
    range; turning it blue gave BLUE blue lips and fingers. A candidate blob is dropped when most of the ring around it
    is skin (pale warm pink), not the cream jacket or black ink that rings the stripes, straps and headphones."""
    h, s, v = hsv[..., 0] * 2.0, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    ink = v < 0.4                          # black outlines do not count either way
    skin = (h >= 4) & (h <= 24) & (s >= 0.2) & (s <= 0.4) & (v >= 0.7)   # cream jacket: s 0.09-0.22, h 18-42
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
    out = cand.copy()
    k = np.ones((2 * ring_px + 1, 2 * ring_px + 1), np.uint8)
    for c in range(1, n):
        x, y, w, hh = st[c, :4]
        x0, y0 = max(x - ring_px, 0), max(y - ring_px, 0)
        x1, y1 = min(x + w + ring_px, cand.shape[1]), min(y + hh + ring_px, cand.shape[0])
        comp = lab[y0:y1, x0:x1] == c
        ring = (cv2.dilate(comp.astype(np.uint8), k) > 0) & ~cand[y0:y1, x0:x1] & ~ink[y0:y1, x0:x1]
        if ring.sum() and (skin[y0:y1, x0:x1] & ring).sum() / ring.sum() > max_skin:
            out[y0:y1, x0:x1][comp] = False
    return out


C2A_LAST = 60      # C2a_swap plays take frames 3-46; C2b_letgo plays 85-117
BLUE_DY = 18       # C2a draws the BLUE layer 18 px lower (she is on the held button); ORANGE is at 0 from 0.2 s
BOOK_FROM = 104    # take frames from which matte blobs outside both tracks are dropped (the book slab)
GATE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))   # SAM masks grown 15 px: the gate for the above


def fill_behind(g, mo, mb):
    """C2a only: BLUE's layer is drawn BLUE_DY px lower than ORANGE's, so where BLUE's head hid ORANGE (the leap),
    a BLUE_DY-px strip of plate showed between them. ORANGE's matte is extended over that strip (only within BLUE_DY px of
    reach) and the strip is inpainted from her pixels in a copy of the frame used by her layer only."""
    shifted = np.zeros_like(mb)
    shifted[BLUE_DY:] = mb[:-BLUE_DY]
    missing = mb & ~shifted & ~mo
    # the strip under her: missing pixels with ORANGE directly above them within BLUE_DY + 3 px (the vertical gap the
    # shift opened), not BLUE's bun or pencil tips beside her chin
    above = np.zeros_like(mo)
    for k in range(1, BLUE_DY + 4):
        above[k:] |= mo[:-k]
    fill = missing & above
    if fill.sum() < 20:
        return g, mo, 0
    # inpaint from ORANGE's own pixels only: inside a box round the strip everything that is not her is the hole
    ys, xs = np.nonzero(fill)
    y0, y1 = max(ys.min() - 40, 0), min(ys.max() + 41, mo.shape[0])
    x0, x1 = max(xs.min() - 40, 0), min(xs.max() + 41, mo.shape[1])
    hole = (~mo[y0:y1, x0:x1]).astype(np.uint8) * 255
    gO = g.copy()
    inp = cv2.inpaint(np.ascontiguousarray(g[y0:y1, x0:x1]), hole, 9, cv2.INPAINT_TELEA)
    sub = fill[y0:y1, x0:x1]
    gO[y0:y1, x0:x1][sub] = inp[sub]
    return gO, mo | fill, int(fill.sum())


def labels(pO, pB, girls):
    """split the girl matte between the two tracks: the stronger track wins where both claim a pixel; pixels neither
    claims go to the nearer track. Returns (ORANGE matte, BLUE matte, per-pixel owner map for recolouring)."""
    o = (pO >= pB) & (pO > 0.5)
    b = (pB > pO) & (pB > 0.5)
    do = cv2.distanceTransform((~o).astype(np.uint8), cv2.DIST_L2, 5)
    db = cv2.distanceTransform((~b).astype(np.uint8), cv2.DIST_L2, 5)
    if not o.any():
        do[:] = 1e9
    if not b.any():
        db[:] = 1e9
    own_o = do <= db                      # whole frame: who owns each pixel (for the colour fringe outside the matte)
    return girls & own_o, girls & ~own_o, own_o


def build():
    frames = read_frames(SRC)
    n = len(frames)
    Lc = read_mp4_gray(f"{D}/c2t1_Lc.mp4")
    tO = np.load(f"{OUT}/track_O.npz")["p"]
    tB = np.load(f"{OUT}/track_B.npz")["p"]
    os.makedirs(f"{OUT}/O", exist_ok=True)
    os.makedirs(f"{OUT}/B", exist_ok=True)

    def enc(name):
        return subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080",
                                 "-r", "24", "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12" if name.startswith("bo") else "14",
                                 "-pix_fmt", "yuv420p", f"{D}/c2t1_v9_{name}.mp4"], stdin=subprocess.PIPE)
    E = {k: enc(k) for k in ("bo", "bo_O", "O", "B")}
    log = []
    for i in range(n):
        f = cv2.cvtColor(frames[i], cv2.COLOR_RGB2BGR)
        girls = (Lc[i] > 127) | (cv2.imread(f"{D}/c2t1_R/{i:05d}.png", 0) > 127)
        pO = cv2.resize(tO[i], (1920, 1080), interpolation=cv2.INTER_LINEAR) / 255.0
        pB = cv2.resize(tB[i], (1920, 1080), interpolation=cv2.INTER_LINEAR) / 255.0
        sam = cv2.dilate(((pO > 0.5) | (pB > 0.5)).astype(np.uint8), GATE) > 0
        if i >= BOOK_FROM:
            # the old R matte took in the take's own (untitled) book slab as the girls run past it (take 107-109), which
            # covered plate_titled's book title for two frames: drop big blobs that lie outside both tracks. (Not done
            # earlier: SAM misses ORANGE's head on take 100-103, and that must stay in.)
            out = (girls & ~sam).astype(np.uint8)
            nb, lb, sb, _ = cv2.connectedComponentsWithStats(out)
            for c in range(1, nb):
                if sb[c, cv2.CC_STAT_AREA] > 8000:
                    girls &= lb != c
        mo, mb, own_o = labels(pO, pB, girls)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
        o_px, b_px, s, v = recolor.masks(hsv)
        near = cv2.dilate(girls.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0   # the girls plus their AA fringe
        # bun-keep band from each girl's tracked silhouette (the matte's book slab moved BLUE's "top" off her bun)
        keep = top_keep(mo & sam) | top_keep(mb & sam)
        to_blue = skin_lines_out(o_px & near & ~own_o & ~keep, hsv)
        to_orange = b_px & near & own_o & ~keep
        hsv[..., 0][to_blue] = recolor.BLUE_H
        hsv[..., 1][to_blue] = np.clip(s[to_blue] * 0.86, 0, 1) * 255
        hsv[..., 2][to_blue] = np.clip(v[to_blue] * 0.93, 0, 1) * 255
        hsv[..., 0][to_orange] = recolor.ORANGE_H
        hsv[..., 1][to_orange] = np.clip(np.maximum(s[to_orange] * 1.6, 0.7), 0, 0.88) * 255
        hsv[..., 2][to_orange] = np.clip(np.maximum(v[to_orange], 0.92), 0, 1) * 255
        g = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        E["bo"].stdin.write(g.tobytes())
        gO, nfill = g, 0
        if i < C2A_LAST:
            gO, mo, nfill = fill_behind(g, mo, mb)
        E["bo_O"].stdin.write(gO.tobytes())
        for k, m in (("O", mo), ("B", mb)):
            u = (m * 255).astype(np.uint8)
            cv2.imwrite(f"{OUT}/{k}/{i:05d}.png", u)
            E[k].stdin.write(cv2.cvtColor(u, cv2.COLOR_GRAY2BGR).tobytes())
        log.append((i, int(mo.sum()), int(mb.sum()), int(to_blue.sum()), int(to_orange.sum()), nfill))
    for p in E.values():
        p.stdin.close()
        p.wait()
    for r in log[::10]:
        print("frame %3d  O px %6d  B px %6d  ->blue %5d  ->orange %5d  fill %4d" % r)


if __name__ == "__main__":
    {"track": track, "build": build}[sys.argv[1]]()
