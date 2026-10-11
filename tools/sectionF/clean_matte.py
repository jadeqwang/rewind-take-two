"""Jade-only matte for colour-world clips: tools/engrave's Matter with world_color=True (colour no longer extends the
matte, so a colourful wave next to her stays out). Fixes the F1 matte leak in the engraved twin.
    tools/engrave/.venv/bin/python tools/sectionF/clean_matte.py IN.mp4 OUT_matte.mp4"""
import os
import subprocess
import sys

sys.path.insert(0, "/home/jade/Documents/rewind-take-two/tools/engrave")
import av  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from matte import Flow, Matter, flow_to_torch  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
c = av.open(src)
vs = c.streams.video[0]
W, H, fps = vs.codec_context.width, vs.codec_context.height, vs.average_rate
ff = os.path.expanduser("~/Documents/moongazing/.venv/bin/ffmpeg")
p = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                      "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
m = Matter("cuda")
m.world_color = True
fl = Flow()
for fr in c.decode(vs):
    a = fr.to_ndarray(format="rgb24")
    f = fl(a)
    t = torch.from_numpy(a).cuda().permute(2, 0, 1)[None].float() / 255
    ft = flow_to_torch(f, H, W, W, "cuda") if f is not None else None
    mt = m(t, ft)
    p.stdin.write((mt[0, 0].clamp(0, 1) * 255).byte().cpu().numpy().tobytes())
p.stdin.close(); p.wait()
print("wrote", out)
