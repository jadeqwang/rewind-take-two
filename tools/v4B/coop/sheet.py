"""contact sheet of a clip: sheet.py SRC OUT [step=0.25] [cols=6] [w=400]"""
import sys
import av
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6
w = int(sys.argv[5]) if len(sys.argv) > 5 else 400
c = av.open(src)
fr = [(float(f.pts * f.time_base), f.to_image()) for f in c.decode(video=0)]
pick, nxt = [], 0.0
for t, im in fr:
    if t + 1e-6 >= nxt:
        pick.append((t, im)); nxt += step
h = int(w * fr[0][1].height / fr[0][1].width)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
rows = (len(pick) + cols - 1) // cols
S = Image.new("RGB", (cols * w, rows * (h + 20)), (20, 20, 20))
d = ImageDraw.Draw(S)
for i, (t, im) in enumerate(pick):
    x, y = (i % cols) * w, (i // cols) * (h + 20)
    S.paste(im.resize((w - 2, h)), (x, y + 20)); d.text((x + 4, y + 2), f"{t:.2f}", fill=(255, 220, 120), font=font)
S.save(out, quality=85)
print(out, S.size, len(pick))
