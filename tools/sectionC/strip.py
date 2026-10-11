"""Dense frame strip for picking in-points: python strip.py CLIP.mp4 OUT.jpg [step_frames=4] [t0] [t1]"""
import sys
import av
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
step = int(sys.argv[3]) if len(sys.argv) > 3 else 4
t0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0
t1 = float(sys.argv[5]) if len(sys.argv) > 5 else 99
fr = []
with av.open(src) as c:
    st = c.streams.video[0]
    for i, f in enumerate(c.decode(st)):
        t = i / 24
        if t0 <= t <= t1 and i % step == 0:
            fr.append((t, f.to_image()))
W, cols = 400, 6
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
tiles = []
for t, im in fr:
    im = im.convert("RGB").resize((W, round(W * im.height / im.width)))
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 90, 24), fill=(0, 0, 0)); d.text((4, 2), f"{t:.2f}", fill=(255, 220, 0), font=font)
    tiles.append(im)
H = tiles[0].height
rows = (len(tiles) + cols - 1) // cols
S = Image.new("RGB", (W * cols, H * rows))
for k, t in enumerate(tiles): S.paste(t, ((k % cols) * W, (k // cols) * H))
S.save(out, quality=82); print(out, len(tiles))
