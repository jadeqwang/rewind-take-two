"""Stage the engine demo's test media into media/engine_demo/ (gitignored). Idempotent.

  ~/Documents/moongazing/.venv/bin/python render/engine/tools/make_demo_media.py

  run.mp4          Jade running through the grass field at night (rewind-music-video assets/clips/J7w_v3.mp4)
  circle.mp4       Jade drawing rewind circles on black (assets/clips/J5_circle_v3.mp4)
  circle_matte.mp4 luma matte of circle.mp4 (threshold + morphological close), exercises the alpha-matte path
  far.jpg          parallax far layer: Lake Shore Drive night plate, mirrored so it tiles (assets/sets/lake_shore_drive/2.jpg)
  mid.png          parallax mid layer: procedural woodcut skyline strip with alpha (tiles horizontally)
  near.png         parallax near layer: lamp posts + railing silhouettes with alpha (tiles horizontally)
"""
import pathlib
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'media/engine_demo'
RW1 = pathlib.Path.home() / 'Documents/rewind-music-video/assets'
FF = str(pathlib.Path.home() / 'Documents/moongazing/.venv/bin/ffmpeg')
OUT.mkdir(parents=True, exist_ok=True)


def copy(src, name):
    d = OUT / name
    if not d.exists():
        shutil.copy2(src, d)
        print('copied', name)


copy(RW1 / 'clips/J7w_v3.mp4', 'run.mp4')
copy(RW1 / 'clips/J5_circle_v3.mp4', 'circle.mp4')

if not (OUT / 'circle_matte.mp4').exists():
    vf = ("scale=in_range=tv:out_range=pc,format=gray,lutyuv=y='clip((val-6)*20,0,255)',"
          "dilation,dilation,dilation,erosion,erosion,erosion,gblur=sigma=1.2")
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(OUT / 'circle.mp4'), '-vf', vf, '-c:v', 'libx264', '-crf', '12',
                    '-pix_fmt', 'yuv420p', str(OUT / 'circle_matte.mp4')], check=True)
    print('made circle_matte.mp4')

if not (OUT / 'far.jpg').exists():
    im = Image.open(RW1 / 'sets/lake_shore_drive/2.jpg').convert('RGB')
    w, h = im.size
    tile = Image.new('RGB', (w * 2, h))
    tile.paste(im, (0, 0))
    tile.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (w, 0))
    tile.save(OUT / 'far.jpg', quality=92)
    print('made far.jpg', tile.size)

rng = np.random.default_rng(1420)

if not (OUT / 'mid.png').exists():
    W, H = 3200, 1080
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 0
    while x < W:
        bw = int(rng.integers(90, 230))
        bh = int(rng.integers(220, 640))
        top = H - 260 - bh
        x1 = min(W, x + bw)
        d.rectangle([x, top, x1, H], fill=(16, 16, 18, 255))
        # woodcut: light hatching on the lit side, a few windows
        for yy in range(top + 8, H - 260, 7):
            d.line([x + 4, yy, x + 4 + int(bw * 0.18), yy - 3], fill=(200, 196, 186, 120), width=1)
        for wy in range(top + 20, H - 280, 34):
            for wx in range(x + 16, x1 - 16, 26):
                if rng.random() < 0.28:
                    d.rectangle([wx, wy, wx + 8, wy + 14], fill=(236, 231, 220, 230))
        if rng.random() < 0.3:   # antenna
            d.line([x + bw // 2, top, x + bw // 2, top - 60], fill=(16, 16, 18, 255), width=4)
        x += bw + int(rng.integers(6, 40))
    # elevated track (the Loop) across the strip
    d.rectangle([0, H - 300, W, H - 280], fill=(12, 12, 14, 255))
    for px in range(0, W, 160):
        d.rectangle([px, H - 280, px + 14, H], fill=(12, 12, 14, 255))
        d.line([px, H - 280, px + 80, H - 200], fill=(12, 12, 14, 255), width=5)
        d.line([px + 160, H - 280, px + 80, H - 200], fill=(12, 12, 14, 255), width=5)
    img.save(OUT / 'mid.png')
    print('made mid.png')

if not (OUT / 'near.png').exists():
    W, H = 2400, 1080
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 120, W, H], fill=(6, 6, 7, 255))                       # ground
    d.rectangle([0, H - 190, W, H - 180], fill=(6, 6, 7, 255))                 # railing
    d.rectangle([0, H - 150, W, H - 144], fill=(6, 6, 7, 255))
    for px in range(0, W, 60):
        d.rectangle([px, H - 190, px + 6, H - 120], fill=(6, 6, 7, 255))
    for px in (300, 1500):                                                       # lamp posts with sodium glow
        d.rectangle([px, H - 760, px + 16, H - 120], fill=(6, 6, 7, 255))
        d.line([px + 8, H - 760, px + 120, H - 800], fill=(6, 6, 7, 255), width=12)
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(glow)
        g.ellipse([px + 70, H - 840, px + 190, H - 760], fill=(255, 170, 60, 200))
        glow = glow.filter(ImageFilter.GaussianBlur(28))
        img = Image.alpha_composite(img, glow)
        d = ImageDraw.Draw(img)
        d.ellipse([px + 104, H - 812, px + 140, H - 790], fill=(255, 226, 170, 255))
    img.save(OUT / 'near.png')
    print('made near.png')

print('media/engine_demo:', sorted(p.name for p in OUT.iterdir()))
