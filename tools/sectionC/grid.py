"""Quick review grid: python grid.py OUT.jpg cols img1 img2 ... (labels = parent dir + file)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
out, cols, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
W = 2400 // cols
tiles = []
for p in paths:
    im = Image.open(p).convert("RGB"); im = im.resize((W, round(W * im.height / im.width)))
    d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 30), fill=(0, 0, 0))
    d.text((6, 4), os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p), fill=(255, 220, 0),
           font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22))
    tiles.append(im)
H = max(t.height for t in tiles)
rows = (len(tiles) + cols - 1) // cols
S = Image.new("RGB", (W * cols, H * rows), (20, 20, 20))
for k, t in enumerate(tiles): S.paste(t, ((k % cols) * W, (k // cols) * H))
S.save(out, quality=85); print(out, S.size)
