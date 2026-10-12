"""v5-coda2: an idle take (media/gen/v5_coda2_idle_<name>/take_N.mp4, on flat grey #bdbdbd) -> RGBA PNG frames for the
lobby queue (tools/sectionF/modules/hilbert_lobby.js `idle`).

    tools/engrave/.venv/bin/python tools/sectionF/coda/idle_matte.py NAME [NAME ...]

BiRefNet through tools/engrave/matte.py Matter (DIS-flow temporal smoothing; no colour cues: the ground is flat grey),
the grey unmixed from the edge pixels, one fixed box for all frames (the union of the silhouettes + margin), scaled to
about the largest size the figure is shown at in the film. The take's last frame is its first (first = last frame
image), so it is dropped and the sequence loops. -> media/shots/PC/idle/<name>/f_0001.png ... + info.json + sheet.jpg
"""
import glob
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
OUT = os.path.join(ROOT, "media/shots/PC/idle")
GREY = np.array([0xbd, 0xbd, 0xbd], np.float32)
# the largest on-screen height (1080p design px) each figure reaches: front.h / depth * max camScale (1.55)
SHOWN = {"jade": 1147, "glasses": 765, "teal": 590, "purple": 480, "braids": 403, "plain": 348, "sleepy": 306,
         "rainbow": 273, "mint": 247}
TAKE = {}          # name -> take number (default: the newest take)


def take_path(name):
    d = os.path.join(ROOT, f"media/gen/v5_coda2_idle_{name}")
    if name in TAKE:
        return os.path.join(d, f"take_{TAKE[name]}.mp4")
    ts = sorted(glob.glob(os.path.join(d, "take_[0-9]*.mp4")), key=lambda p: int(p.rsplit("_", 1)[1].split(".")[0]))
    ts = [t for t in ts if t.rsplit("_", 1)[1].split(".")[0].isdigit()]
    return ts[-1]


def run(name, check_only=False):
    import av
    import torch
    from matte import Flow, Matter, flow_to_torch
    src = take_path(name)
    frames = []
    with av.open(src) as c:
        for f in c.decode(video=0):
            frames.append(f.to_ndarray(format="rgb24"))
    H, W = frames[0].shape[:2]
    mt = Matter(min_color_frac=0, temporal=0.5, feather=0.7)
    mt.world_color = True
    fl = Flow(width=480)
    alphas = []
    for f in frames:
        flo = fl(f)
        x = torch.from_numpy(f).cuda().permute(2, 0, 1)[None].float() / 255
        ft = flow_to_torch(flo, H, W, W, "cuda") if flo is not None else None
        alphas.append(mt(x, ft)[0, 0].clamp(0, 1).cpu().numpy())
    # drift check: feet line and head top per frame (Seedance sometimes zooms despite camera_fixed)
    def ext(a):
        ys = np.where((a > 0.5).any(1))[0]
        xs = np.where((a > 0.5).any(0))[0]
        return ys[0], ys[-1], xs[0], xs[-1]
    e = np.array([ext(a) for a in alphas])
    print(f"{name}: {len(frames)} frames {W}x{H}  head y {e[:,0].min()}..{e[:,0].max()}  feet y {e[:,1].min()}..{e[:,1].max()}"
          f"  x {e[:,2].min()}..{e[:,3].max()}")
    if check_only:
        return e
    # drop the closing frame(s) that repeat frame 0 (first = last frame)
    n = len(frames)
    d_last = np.abs(frames[-1].astype(np.int16) - frames[0].astype(np.int16)).mean()
    if d_last < 6:
        n -= 1
    y0, y1 = max(0, e[:n, 0].min() - 12), min(H, e[:n, 1].max() + 4)
    x0, x1 = max(0, e[:n, 2].min() - 12), min(W, e[:n, 3].max() + 13)
    foot = e[0, 1] + 1 - y0
    figH = e[0, 1] + 1 - e[0, 0]
    a0 = alphas[0][y0:y1, x0:x1]
    cx = float((a0.sum(0) * np.arange(x1 - x0)).sum() / a0.sum())
    sc = min(1.0, SHOWN[name] * 1.15 / figH)
    ow, oh = round((x1 - x0) * sc), round((y1 - y0) * sc)
    od = os.path.join(OUT, name)
    os.makedirs(od, exist_ok=True)
    for p in glob.glob(os.path.join(od, "f_*.png")):
        os.remove(p)
    for i in range(n):
        rgb = frames[i][y0:y1, x0:x1].astype(np.float32)
        a = alphas[i][y0:y1, x0:x1]
        # unmix the grey ground from the soft edge
        fg = np.where(a[..., None] > 0.04, (rgb - (1 - a[..., None]) * GREY) / np.maximum(a[..., None], 0.04), rgb)
        out = np.dstack([np.clip(fg, 0, 255), a * 255]).astype(np.uint8)
        im = Image.fromarray(out)
        if sc < 1:
            im = im.resize((ow, oh), Image.LANCZOS)
        im.save(os.path.join(od, f"f_{i + 1:04d}.png"), compress_level=6)
    info = {"frames": n, "fps": 24, "w": ow, "h": oh, "footY": round(foot * sc, 2), "cx": round(cx * sc, 2),
            "figH": round(figH * sc, 2), "src": os.path.relpath(src, ROOT), "box": [int(x0), int(y0), int(x1), int(y1)],
            "scale": round(sc, 4)}
    json.dump(info, open(os.path.join(od, "info.json"), "w"), indent=1)
    # sheet: 8 frames over a teal-and-cream check, to judge the matte and the motion
    idx = np.linspace(0, n - 1, 8).round().astype(int)
    th = 520
    tw = round(ow * th / oh)
    sheet = Image.new("RGB", (tw * 8, th), (200, 190, 170))
    chk = np.indices((th, tw)).sum(0) // 20 % 2
    bgc = np.where(chk[..., None] == 1, np.array([40, 110, 120]), np.array([235, 225, 205])).astype(np.uint8)
    for j, i in enumerate(idx):
        fr = Image.open(os.path.join(od, f"f_{i + 1:04d}.png")).resize((tw, th))
        b = Image.fromarray(bgc).convert("RGBA")
        b.alpha_composite(fr)
        sheet.paste(b.convert("RGB"), (j * tw, 0))
    sheet.save(os.path.join(od, "sheet.jpg"), quality=88)
    print(f"  -> {od}: {n} frames {ow}x{oh} figH {info['figH']} foot {info['footY']}")
    return info


if __name__ == "__main__":
    chk = "--check" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--take="):
            for kv in a[7:].split(","):
                k, v = kv.split(":")
                TAKE[k] = int(v)
    for n in [a for a in sys.argv[1:] if not a.startswith("--")]:
        run(n, chk)
