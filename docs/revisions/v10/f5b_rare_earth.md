# v10: "RARE EARTH" on the jacket back in F5b (3:07.08-3:08.84)

Jade (2026-10-18): "see if you can add RARE EARTH lettering to the back of the jacket in 3:07 (flowing with the way the
jacket sways."

Status: done on the source plate. I didn't edit `media/shots/F_edl.json`, `tools/sectionF/edl.py` or any timeline file,
and I didn't run render.mjs. The lead applies the swap below. Spend: $0 (no paid calls).

## The shot
- F5b, master 3:07.08-3:08.84, `clip_in` 0.05 s, rate 1.0. The plate is `media/shots/F5b/take_3_engraved_dered.mp4`
  (1920x1080, 24 fps, 121 frames). It is the colour-pencil rooftop: she is seen from behind on the right, with the
  dripping clock and the falling agents beyond, and the camera slowly pushes in and drifts right.
- **Frame mapping.** The engine samples `floor(sT x 24)`, so song frame N plays source frame N - 4489. Master
  f4490-f4532 play src 1-43.
- **Is it doable?** Yes. The cropped jacket's back panel is clear, and the pale-blue dot is visible in every frame. The
  dot is 43 px across at 3:07.08 and 57 px at 3:08.82. (The v9 note estimated 28 px, which was wrong.) The hair blows
  over the top of the dot and the shoulders, but never reaches the area between the dot and the waist-rib seam, where
  the lettering goes.

## Output
- **Plate:** `media/shots/F5b/take_3_engraved_dered_v10rare.mp4`. It matches the source: 1920x1080, 24 fps, 121 frames,
  5.042 s, timebase 1/12288, H.264 High, yuv420p, CRF 13 preset slow, `+faststart`.
  - Src 0-66 are lettered: the used span 1-43 plus 1 spare frame before and 23 after.
  - Src 67-120 are the source frames re-encoded unchanged. They aren't used, and she leaves the frame there.
  - Outside the lettering box, the mean difference is 1.9-2.3/255 and p99 is 5-7/255 (codec noise). At most 2 pixels
    per frame differ by more than 25.
- **Tool:** `tools/v10/rare_earth_F5b.py`, spec `tools/v10/rare_earth_F5b.json`.
  - Reproduce: `tools/engrave/.venv/bin/python tools/v10/rare_earth_F5b.py tools/v10/rare_earth_F5b.json` (about 20 s).
  - `--track-only` prints the per-frame fit and a measure of how far the lettering slides against the cloth.
  - `--sheet a:b` and `--compare` write the evidence images.

## Method (per frame)
1. **Dot.** I find the pale-blue blob near the last position and fit an ellipse only to the visible part of its outline.
   Outline points next to black hair are dropped. The dot's own dark-blue outline is not counted as hair. This gives
   the panel's position and scale; the dot's semi-diameters along and across the baseline give the foreshortening.
2. **Seam.** For each column under the dot, I find the thin grey-black seam between the back panel and the waist rib
   and fit a robust quadratic to it. The tangent at the dot's x gives the panel's tilt, which runs from -0.3 deg to
   -6 deg (rising to the right) as the jacket rocks. The x^2 term gives the panel's arch, because the seam bows over
   her back.
3. **Geometry.** This is the canon layout from `inputs/jade_in_outfit.png` BACK, the same as O2: Liberation Sans Bold
   caps, tracking 0.05 em, word space 1.5x, text width 2.15 dot radii (about 1.07 D), caps starting 0.28 radii below
   the dot's edge, centred under the dot. The text is laid out in dot units. A dot/seam mesh maps it to the frame:
   - rotation and scale come from the dot, with the tilt set by the seam;
   - the seam's arch is blended in, from 0 at the dot's bottom edge to 1 at the seam, so the word bows slightly with
     the hem.
4. **Following the sway: flow lattice.** A 9x3 grid of control points around the word rides the fabric:
   - each frame the points move by the plate's Farneback optical flow, averaged over jacket-white pixels only so hair
     can't drag them;
   - the flow update is fitted to a smooth low-order field (constant, linear, u^2, uv), so letters don't wobble
     against each other;
   - each frame the points are pulled 20% of the way back toward the dot/seam mesh, so they can't drift;
   - a forward pass and a backward pass are averaged, so there is no lag;
   - the text is warped through this lattice (bilinear) by inverse mapping at 4x supersampling.

   Measured slide of the lettering against the cloth (plate flow minus lettering motion, median, per frame): 0.07-0.45
   px in src 0-66. Placing it from the dot and seam alone gives 0.3-2.1 px. The lattice stays within about 0.3-2.6 px of
   the dot/seam placement.
5. **Ink.** Dark grey (52, 51, 56), as in canon. It is applied as a multiply: `pixel x ink / local jacket white`, so
   the cloth's shading, pencil grain and fold strokes come through the letters. The glyphs carry a fixed ink texture
   in text space (slightly rough edges, 78-100% density grain), so it moves with the cloth and never crawls. The edges
   are softened by 0.35 px.
6. **Occlusion.** Ink goes only on jacket-white pixels (bright, low chroma), so the dot, the orange band and skin never
   take it. Black hair and outlines are keyed on raw luminance, not a closed one, so single blown strands count. The
   key is dilated by 1 px with a soft edge. In the used span nothing actually crosses the lettering.

Size at 1080p: caps are 5.3 px and the word 47 px wide at 3:07.08 (src 1), 6.2 / 52 px at 3:07.9 and 7.0 / 61 px at
3:08.82 (src 43).

## The EDL swap (the lead applies it)
`media/shots/F_edl.json`, the F5b shot (line 462):

```diff
-   "file": "media/shots/F5b/take_3_engraved_dered.mp4",
+   "file": "media/shots/F5b/take_3_engraved_dered_v10rare.mp4",
```

Make the same change in `tools/sectionF/edl.py` so a rebuild keeps it. In `CHOSEN`, add a `file` to the F5b entry and
leave the rest unchanged:

```diff
-    "F5b": dict(take=3, in_sec=0.05, rate=1.0, reverse=False, notes="wide; ink drips ...
+    # v10 (Jade 3:07, docs/revisions/v10/f5b_rare_earth.md): *_v10rare = the dered plate with RARE EARTH under the back
+    # dot, riding the jacket's sway (tools/v10/rare_earth_F5b.py, spec tools/v10/rare_earth_F5b.json)
+    "F5b": dict(take=3, file=S + "F5b/take_3_engraved_dered_v10rare.mp4", in_sec=0.05, rate=1.0, reverse=False, notes="wide; ink drips ...
```

- `plate()` then looks for `..._v10rare_dered.mp4`. That file doesn't exist, so the v10rare file is used as given.
- `matte` is derived from the take number, so it stays `take_3_matte/matte.mp4`. The geometry is unchanged, so it is
  still valid.
- `clip_in` (0.05), `rate` (1.0), `in`/`out` and the flash are unchanged.
- This is a new path, so the engine cache doesn't apply.

## Evidence (`docs/revisions/v10/f5b/`)
- **Every frame, from the encoded output** (each crop is 160x110 px around the back at 3x, labelled with the src frame,
  song m:ss and song frame; spare frames are grey):
  - `every_frame_src000-023.jpg`
  - `every_frame_src024-047.jpg`
  - `every_frame_spare_src048-066.jpg` (2x)
- **Before/after tiles.** In each, the top row is 1:1 at 1080p and the bottom row is a 3x zoom:
  - `before_after_3m07_3_src06.jpg`: 3:07.29, f4495.
  - `before_after_3m07_9_src21.jpg`: 3:07.92, f4510.
  - `before_after_3m08_5_src35.jpg`: 3:08.50, f4524.

I looked at all of them myself:
- The word holds the same place under the dot and parallel to the seam in every frame.
- It tilts with the panel: about 6 deg uphill at 3:07.3-3:07.6, flattening to about 0 deg at 3:08.1-3:08.4, then back
  to about 5 deg.
- No frame jumps or jitters.
- No letter touches the seam, the dot, the orange band or the sleeve outlines.
- No hair crosses the word.

## Weak list (honest)
1. **It is small.**
   - Caps are 5-7 px at 1080p. It reads as "RARE EARTH" at 1:1. In a 540p preview it is a thin grey line of type you
     can just about make out.
   - That is the canon proportion (about 1 D wide). I didn't enlarge it beyond canon.
2. **The pencil/ink texture is effectively invisible at this size.**
   - Rough edges and density grain only show at 3x zoom.
   - At 1:1 it reads as a clean printed graphic on the jacket. The multiply with the cloth's grain keeps it from looking
     pasted on.
3. **"Flowing" is low-order.**
   - The word rocks and arches with the panel and rides its measured motion: tilt from -0.3 to -6 deg, and the seam's
     arch blended in, about 40% at the text.
   - It doesn't crease into individual wrinkles. The panel under the dot is smooth in this take, so there are none to
     follow.
   - The arch is subtle: the ends sit about 1 px lower than the middle.
4. **The tilt reads as tilted at 3:07.29-3:07.50 (f4495-f4500, src 6-11).**
   - The word runs about 6 deg uphill to the right there, parallel to the seam, which is right next to the seam.
   - If Jade wants it level, a smaller tilt factor is a one-line spec change.
5. **The hair key is in place but untested by this take.** In the used span the hair never reaches the lettering. It
   stays above the dot's lower half: closest at 3:08.2-3:08.5, f4517-f4524, where it covers the dot's top third.
6. **Only src 0-66 are lettered.**
   - From src 67 (3:09.82, f4556), the seam fit jumps as she leaves the frame, so I stopped there.
   - It isn't used now. If the cut is ever extended past 3:09.78, the lettering would disappear at that frame.
7. **The shot opens on a 0.08 s warm flash.** The lettering is there under it, as on the rest of the plate.
