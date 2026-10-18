#!/usr/bin/env python
"""Contact sheets for the F4 Bean mirror check renders (render.mjs output).
    ~/Documents/1-music-shipped/moongazing/.venv/bin/python tools/sectionF/f4_threejs/sheets.py RAW_DIR OUT_DIR
Per case: row 1 normal, row 2 x-ray (her direct image at 30%, so the reflection behind her shows), each frame labelled
with the F4 source frame and her distance to the mirror. Also measure.json: per case/frame, the reflection's bounding
box, area and centroid from the id pass (G channel), and how much of it is hidden behind her (R channel)."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

raw, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
poses = json.load(open(os.path.join(raw, "poses.json")))
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except OSError:
    font = small = ImageFont.load_default()
names = sorted(os.listdir(raw))
cases = sorted({n.split("_")[0] for n in names if n.endswith(".png")})
frames = sorted({int(n.split("_")[1][1:]) for n in names if n.endswith(".png")})
meas = {}
for c in cases:
    rows = []
    for mode in (0, 1):
        tiles = []
        for f in frames:
            im = Image.open(os.path.join(raw, f"{c}_f{f:03d}_{mode}.png")).convert("RGB")
            idm = np.asarray(Image.open(os.path.join(raw, f"{c}_f{f:03d}_2.png")).convert("RGB")) > 127
            P = poses[f"{c}_f{f}"]
            cam, head, contact = np.array(P["cam"]["pos"]), np.array(P["head"]), np.array(P["contact"])
            dist = float(np.linalg.norm(contact - head)) - 0.12
            her, refl = idm[..., 0], idm[..., 1]
            ys, xs = np.where(refl)
            m = {"dist_m": round(dist, 2), "her_px": int(her.sum()), "refl_px": int(refl.sum()),
                 "refl_hidden_by_her": round(float((refl & her).sum() / max(1, refl.sum())), 2)}
            if len(xs):
                m.update(bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                         centroid=[round(float(xs.mean()), 1), round(float(ys.mean()), 1)])
            hy, hx = np.where(her)
            if len(hx):
                m["her_bbox"] = [int(hx.min()), int(hy.min()), int(hx.max()), int(hy.max())]
            meas[f"{c}_f{f}"] = m
            d = ImageDraw.Draw(im)
            lab = f"F4 frame {f}   {dist:.1f} m to the mirror" + ("   x-ray" if mode else "")
            d.rectangle([0, 0, im.width, 28], fill=(0, 0, 0))
            d.text((8, 4), lab, fill=(255, 255, 255), font=small)
            tiles.append(im)
        rows.append(tiles)
    w, h = rows[0][0].size
    n = len(frames)
    cols = 4
    nr = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, 40 + 2 * nr * h), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), f"case {c}", fill=(240, 160, 64), font=font)
    for k in range(n):
        r, cc = divmod(k, cols)
        sheet.paste(rows[0][k], (cc * w, 40 + (2 * r) * h))
        sheet.paste(rows[1][k], (cc * w, 40 + (2 * r + 1) * h))
    sheet = sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS)
    sheet.save(os.path.join(out, f"case_{c}.jpg"), quality=88)
json.dump(meas, open(os.path.join(out, "measure.json"), "w"), indent=1)
print("wrote", [f"case_{c}.jpg" for c in cases])
