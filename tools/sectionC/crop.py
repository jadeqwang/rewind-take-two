"""Manual margin crop: python crop.py IMG px  (crops px from every side, keeps <name>_raw, re-forces 16:9)."""
import os, sys
from PIL import Image
p, px = sys.argv[1], int(sys.argv[2])
base, ext = os.path.splitext(p)
raw = base + "_raw" + ext
src = raw if os.path.exists(raw) else p
im = Image.open(src)
if not os.path.exists(raw):
    im.save(raw)
w, h = im.size
im = im.crop((px, px, w - px, h - px)); w, h = im.size
if w / h > 16 / 9:
    nw = round(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else:
    nh = round(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
im.save(p, quality=95); print(p, im.size)
