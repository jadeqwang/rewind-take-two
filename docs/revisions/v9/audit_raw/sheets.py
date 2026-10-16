import av, sys, re
from PIL import Image, ImageDraw, ImageFont
src, shots_txt, out = sys.argv[1:4]
shots = []
for line in open(shots_txt):
    m = re.match(r'\s+(\S+)\s+([\d.]+) →\s+([\d.]+)', line)
    if m and not m.group(1).startswith('+'): shots.append((m.group(1), float(m.group(2)), float(m.group(3))))
def shot_at(t):
    for n, a, b in shots:
        if a <= t < b: return n
    return '?'
TW, TH, LH, C, R = 384, 216, 16, 4, 4
font = ImageFont.load_default()
sheet = None; k = 0; idx = []
def flush(si):
    sheet.save(f'{out}/sheet_{si:04d}.jpg', quality=88)
c = av.open(src)
for i, fr in enumerate(c.decode(video=0)):
    if i % (C*R) == 0:
        if sheet: flush(si)
        si = i // (C*R); sheet = Image.new('RGB', (C*TW, R*(TH+LH)), 'black'); d = ImageDraw.Draw(sheet)
        first_t = i/24
    t = i / 24; j = i % (C*R); x, y = (j % C)*TW, (j//C)*(TH+LH)
    sheet.paste(fr.to_image().resize((TW, TH), Image.BILINEAR), (x, y+LH))
    mm, ss = divmod(t, 60)
    d.text((x+3, y+2), f'f{i}  {int(mm)}:{ss:05.2f}  ({t:.3f}s)  {shot_at(t)}', fill='yellow', font=font)
    if j == 0: idx.append((si, i, t, shot_at(t)))
flush(si)
with open(f'{out}/index.tsv', 'w') as f:
    for si, i, t, n in idx: f.write(f'sheet_{si:04d}.jpg\tf{i}-f{i+15}\t{t:.3f}-{(i+15)/24:.3f}\t{n}\n')
