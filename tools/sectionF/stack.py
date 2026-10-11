"""Stack vgen contact sheets vertically: stack.py OUT.jpg SHOT[/take_N] ..."""
import sys
from PIL import Image
R = "/home/jade/Documents/rewind-take-two/media/gen/"
ims = []
for a in sys.argv[2:]:
    s, _, t = a.partition("/")
    ims.append(Image.open(f"{R}{s}/{t or 'take_1'}_sheet.jpg"))
W = max(i.width for i in ims); S = Image.new("RGB", (W, sum(i.height for i in ims))); y = 0
for i in ims:
    S.paste(i, (0, y)); y += i.height
S.save(sys.argv[1], quality=85)
