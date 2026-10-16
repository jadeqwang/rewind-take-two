#!/usr/bin/env python3
"""Round 5 stand-in for the engine composite (render.mjs is off-limits this round): for film frame k, the D2/D3 clip
frame (v9r5_engraved.mp4, n = k - 556), the pinned text layers drawn as A.js draws them (PIL stand-ins: plain fonts,
not the woodcut/plate.js/etch modules, so only place, size, order and occlusion carry over), the occluder (the clip
again through the inverse of r5_billmask: text survives only where the mask is white), the etch on top, 2.39
letterbox. Usage: mock_r5.py OUT.jpg k [k ...]"""
import json, subprocess, sys
import av, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
D = 'media/shots/D23'
T = json.loads(subprocess.run(['node', '-e', "import('./tools/v9/d23/d23_tracks_r5.js').then(T=>console.log(JSON.stringify(T)))"], capture_output=True, text=True).stdout)
WORDS = {'A': 23.97, 'SHADOW': 24.22, 'CHASING': 24.78, 'me': 25.53, 'I': 25.871, "couldn't": 26.534, 'place': 27.30}
FONT = 'render/fonts/Overpass-wght.ttf'; FELL = 'render/fonts/IMFeENrm28P.ttf'
def keyq(keys, lt):
    for i in range(len(keys) - 1):
        (t0, q0), (t1, q1) = keys[i], keys[i + 1]
        if t0 <= lt <= t1: u = (lt - t0) / (t1 - t0); return np.array([a + (b - a) * u for a, b in zip(q0, q1)]).reshape(4, 2)
    return np.array(keys[-1][1] if lt > keys[-1][0] else keys[0][1]).reshape(4, 2)
def warp(img_rgba, q, W=1920, H=1080):
    h, w = img_rgba.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(q))
    return cv2.warpPerspective(img_rgba, M, (W, H), flags=cv2.INTER_LINEAR)
def text_card(text, w, h, fg, bg=None, font=FONT, border=None):
    im = Image.new('RGBA', (w, h), bg or (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if border: d.rectangle([0, 0, w - 1, h - 1], outline=border, width=max(2, h // 18))
    size = h
    while size > 6:
        f = ImageFont.truetype(font, size); bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] < w * 0.9 and bb[3] - bb[1] < h * 0.78: break
        size -= 2
    bb = d.textbbox((0, 0), text, font=f); d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=fg)
    return np.array(im)
def over(base, rgba):
    a = rgba[..., 3:4] / 255.0; base[:] = base * (1 - a) + rgba[..., :3] * a
import os
clip = [f.to_ndarray(format='rgb24') for f in av.open(os.environ.get('CLIP', f'{D}/v9r6_engraved.mp4')).decode(video=0)]
out = []
for k in map(int, sys.argv[2:]):
    t, n = k / 24, k - 556
    fr = clip[n].astype(np.float32); base = fr.copy()
    d2 = t < 25.34; lt = t - (23.16 if d2 else 25.34)
    if d2:
        for word, key in (('A SHADOW', 'D2_BILL_TOP'), ('CHASING', 'D2_BILL_BOT')):
            lit = [w for w in word.split() if t >= WORDS[w]]
            if lit: over(base, warp(text_card(' '.join(lit) if word != 'CHASING' else word, 460, 96, (11, 11, 12, 255)), keyq(T[key], lt)))
    else:
        over(base, warp(text_card('A SHADOW', 460, 96, (11, 11, 12, 255)), keyq(T['D3_BILL_TOP'], lt)))
        over(base, warp(text_card('CHASING', 460, 96, (11, 11, 12, 255)), keyq(T['D3_BILL_BOT'], lt)))
        pq = keyq(T['D3_PLATE_R3'], lt); w = int(np.linalg.norm(pq[1] - pq[0]) * 4) + 8; h = int(np.linalg.norm(pq[3] - pq[0]) * 4) + 4
        over(base, warp(text_card('TVA 1729', w, h, (20, 18, 16, 255), (236, 231, 220, 255), border=(20, 18, 16, 255)), pq))
    m = cv2.imread(f'{D}/r6_billmask_frames/f_{n:05d}.png', cv2.IMREAD_GRAYSCALE).astype(np.float32)[..., None] / 255
    comp = base * m + fr * (1 - m)
    if not d2:
        words = [w for w in ['me', 'I', "couldn't", 'place'] if t >= WORDS[w]]
        if words:
            l1 = ' '.join(w for w in words if w != 'place'); l2 = 'place' if 'place' in words else ''
            card = np.zeros((300, 1100, 4), np.uint8)
            card[:150] = text_card(l1, 1100, 150, (251, 248, 241, 235), font=FELL) if l1 else 0
            if l2: card[150:] = text_card(l2, 1100, 150, (251, 248, 241, 235), font=FELL)
            over(comp, warp(card, keyq(T['D3_ETCH_R3'], lt)))
    bar = int((1080 - 1920 / 2.39) / 2); comp[:bar] = 11; comp[-bar:] = 11
    im = Image.fromarray(comp.clip(0, 255).astype(np.uint8)).resize((960, 540)); ImageDraw.Draw(im).text((6, 4), f'f{k} {t:.2f}', fill=(255, 80, 80))
    out.append(im)
S = Image.new('RGB', (960 * 2, 540 * ((len(out) + 1) // 2)))
for i, im in enumerate(out): S.paste(im, ((i % 2) * 960, (i // 2) * 540))
S.save(sys.argv[1], quality=88)
