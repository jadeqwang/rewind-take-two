# v9 fix 10: V2c5 sleeve band (Jade: "1:17 - jacket is missing orange stripes on arm")

## What was wrong
V2c5 (C.js row `[76.90, 78.66, 'V2c5', 2, 0.3, 1.2, { hero: true }]`, master 1:16.92-1:18.62, frames f1846-f1887)
plays `media/shots/V2c5/take_2_engraved.mp4` (1920x1080, 24 fps, 97 frames) from 0.3 s at rate 1.2. That uses
source frames 7-56: master frame n shows source frame floor((0.3 + (n/24 - 76.90) * 1.2) * 24). f1888 is already
V2c3. Jade drives, seen from behind her right shoulder. Her white jacket has no orange band on the sleeve. The NOTES
already said: "the near sleeve lost its orange band in the keyframe edit". `kf_n2.jpg` had the band, but the
kf_v3 edit that took the 1420 patch off the right sleeve took the band with it.

Canon (`inputs/jade_in_outfit.png`, and O2 at 3:40): one orange band round each upper arm, about a third of the way
from the shoulder seam to the elbow. It stops at the side seam, and the back panel stays plain white with the blue
dot.

Visible sleeves: only her RIGHT upper arm (screen-centre, reaching to the wheel). Of her left arm we see only the
forearm and cuff going to the top of the wheel; the left upper arm, where the band would be, is hidden behind her
back. So the band is painted on the right sleeve only.

## What I made
- `tools/v9/sleeve_band.py` (run with `tools/engrave/.venv/bin/python`, about 50 s):
  1. **Shape**: the band is the half of a ring round the upper arm that faces the camera. In source frame 7 it runs
     across the arm from the dark underside line (armpit end) to the top silhouette, 46 px thick. It bows 28 px
     toward the elbow in the middle because the arm points away from camera, so it reads as wrapping round the
     sleeve. Placement and angle follow the band in `kf_n2.jpg`.
  2. **Tracking**: an affine ECC fit of the upper arm (blurred grey, with Jade's matte as the template mask) from
     frame 7 to every frame (correlation 0.98-0.999 over frames 7-56).
  3. **Paint**: the reverse of `tools/jacket_back.py`: orange (242,134,80, the lit trouser-strap orange in this shot)
     times the pixel's own shading (mean RGB / jacket white 240). It is applied only to neutral (white/grey/ink)
     pixels inside Jade's matte and a hand-drawn upper-arm clip, so the engraved hatching, fold lines and contours
     stay drawn over the orange. Nothing lands on the back panel, the wheel, the hair or the torso.
- Output: `media/shots/V2c5/take_2_engraved_v9sleeve.mp4`. 1920x1080, 24 fps, 97 frames, yuv420p, x264 crf 12
  `-tune grain`, the same as the source. All 97 frames are painted (only 7-56 are used).
  Pixels changed by more than 40 levels all lie in x 492-680, y 695-877 (the band); the rest of the frame differs
  only by re-encode noise (mean about 2 levels).

## Timeline change (not applied: lead to apply)
`render/timeline/C.js`, add V2c5 take 2 to the `BLUE_ERASER` source map (the row itself stays the same):

```js
const BLUE_ERASER = { V2a3_3: 'take_3_engraved_blue.mp4', V2d2_4: 'take_4_engraved_blue_roundel.mp4', V2e2_2: 'take_2_engraved_blue.mp4',
  V2c5_2: 'take_2_engraved_v9sleeve.mp4' };   // v9 #10: orange band painted on her right sleeve (tools/v9/sleeve_band.py)
```
The matte path doesn't change (`take_2_matte/matte.mp4`). V2c5 isn't a stutter, ghost or ribbon shot, so only the
plate layer reads the file. Render with `--force`.

## Evidence (source plate; master time and frame alongside)
- `fix_10_sleeve_before_after.jpg`: v8 preview, plate before, plate after at 1:16.92 f1846 (src 7), 1:17.50 f1860
  (src 24), 1:18.33 f1880 (src 48) and 1:18.62 f1887 (src 56).
- `fix_10_sleeve_detail.jpg`: arm close-ups, before and after, at the same four frames.
- I checked all 50 used frames (src 7-56 = f1846-f1887, 1:16.92-1:18.62) by eye on contact sheets of the encoded
  output, plus 3x zooms of both band ends on src 20-35 and 20/24/28/44/52/56. The band holds its place on the arm
  (the top end stays on the silhouette line, the lower end on the underside line), hatching shows through, and
  there's no spill below the underside line or onto the black interior.

## Neighbours (checked in the master and the preview)
- V2c3 (1:15.12-1:16.02 f1803-f1824; 1:18.66-1:19.56 f1888-f1909): exterior shots of the Acura; Jade isn't
  visible. Nothing to fix.
- V2c4 (1:16.02-1:16.90 f1825-f1845): her legs on the pedals. Only the jacket hem, zip and a lower sleeve edge
  show at the top right, engraved grey; the upper arm is out of frame. Nothing missing.
- V2c6 (1:19.56-1:20.44 f1910-f1930): POV through the windscreen; no Jade. Nothing to fix.
So V2c5 is the only shot in this run with a missing sleeve band.

## Spend
$0 (no paid calls). Project total before and after: $262.90 of $400.

## Still imperfect
- The band is painted, not drawn by the model. It is a clean-edged orange strip with the plate's hatching through
  it, with no ink outline (kf_n2's band had none either). At 3x zoom its edges are crisper than the coloured-pencil
  fill elsewhere; at preview size it reads as part of the jacket.
- An affine track can't follow small cloth folds inside the band; the source fold lines show through it, so this
  doesn't show at full speed.
- Not touched: the steering-wheel rim matte pop in this shot (audit part 2 #12, f1851-f1859).
