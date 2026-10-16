#!/usr/bin/env python
"""v9 fix 1b: matte for media/shots/V2b3/take_2.mp4 (the engrave tool's own matte flips to the whole cabin for
f0-f21: BiRefNet calls the full interior salient until she ducks, which is the "matte pop" Jade flagged on take 1).

Per frame: BiRefNet on a crop round her (x0..X1 of the 720p source) for frames < SPLIT, full frame from SPLIT on
(where full-frame BiRefNet holds her alone); then the seat cut-out (SEAT), the engrave matte's colour cue (saturated pixels near the silhouette
join), a 1-frame temporal median and the engrave feather. Writes take_2_matte/%05d.png + matte.mp4 at 1080p.

    tools/engrave/.venv/bin/python tools/v9/v2b3_matte.py [--check DIR]
"""
import os
import subprocess
import sys

import av
import cv2
import numpy as np
import torch

ROOT = "/home/jade/Documents/rewind-take-two"
sys.path.insert(0, os.path.join(ROOT, "tools/engrave"))
from engrave_core import gblur, smoothstep  # noqa: E402
from matte import chroma_map, get_birefnet  # noqa: E402

SRC = os.path.join(ROOT, "media/shots/V2b3/take_2.mp4")
OUT = os.path.join(ROOT, "media/shots/V2b3/take_2_matte")
SPLIT, X1 = 22, 600
# the driver's seatback + headrest (static: the camera is locked off) sit in FRONT of her at lower left and both
# BiRefNet passes include them; cut them out of every frame (1080p px, traced on f0/f40 with a grid)
SEAT = [(0, 240), (160, 240), (228, 290), (228, 700), (222, 738), (240, 758), (305, 788), (358, 838), (398, 918),
        (428, 1000), (452, 1080), (0, 1080)]
FF = os.path.expanduser("~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/"
                        "imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")


def dil(x, r):
    r = max(1, int(r))
    x = torch.nn.functional.max_pool2d(x, (1, 2 * r + 1), stride=1, padding=(0, r))
    return torch.nn.functional.max_pool2d(x, (2 * r + 1, 1), stride=1, padding=(r, 0))


@torch.no_grad()
def main():
    net = get_birefnet()
    seat = np.zeros((1080, 1920), np.uint8)
    cv2.fillPoly(seat, [np.array(SEAT, np.int32)], 255)
    seat = cv2.GaussianBlur(cv2.resize(seat, (1280, 720), interpolation=cv2.INTER_AREA), (0, 0), 1.2) / 255.0
    keep = torch.from_numpy(1 - seat).float().cuda()[None, None]
    frames = [f.to_ndarray(format="rgb24") for f in av.open(SRC).decode(video=0)]
    raw = []
    for i, im in enumerate(frames):
        t = torch.from_numpy(im).cuda().permute(2, 0, 1)[None].float() / 255
        h, w = t.shape[-2:]
        if i < SPLIT:
            m = torch.zeros(1, 1, h, w, device="cuda")
            m[..., :X1] = net(t[..., :X1])
        else:
            m = net(t)
        col = smoothstep(0.10, 0.20, gblur(chroma_map(t), 0.8))
        near = dil((m > 0.3).float(), 0.04 * h)
        m = torch.maximum(m, col * near) * keep
        raw.append(m[0, 0].cpu().numpy())
    raw = np.stack(raw)
    med = np.stack([np.median(raw[max(0, i - 1):i + 2], 0) for i in range(len(raw))])   # 3-tap temporal median
    os.makedirs(OUT, exist_ok=True)
    for i, m in enumerate(med):
        t = torch.from_numpy(m).cuda()[None, None]
        t = smoothstep(0.08, 0.92, gblur(t, 1.0))
        u = cv2.resize((t[0, 0].cpu().numpy() * 255).astype(np.uint8), (1920, 1080), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(OUT, f"{i:05d}.png"), u)
    subprocess.run([FF, "-loglevel", "error", "-y", "-framerate", "24", "-i", os.path.join(OUT, "%05d.png"),
                    "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", os.path.join(OUT, "matte.mp4")], check=True)
    print("wrote", OUT, len(med))


if __name__ == "__main__":
    main()
