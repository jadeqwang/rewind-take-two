# v9 fix 11: "RARE EARTH" on the jacket back (O2, 3:38.92-3:42.78)

Jade: "3:40 - RARE EARTH on back of jacket should be readable (there are other places where it's missing, but here,
she's actually large enough and still enough for someone to notice)".

Status: done on the source clip. I didn't run render.mjs or edit any timeline file. The lead applies the EDL change
below and does the integrated preview.

## What was wrong
In O2 (the dissertation-defense door, master 3:38.92-3:42.78, frames 5254-5347) we see Jade from behind for the whole
shot. Her back is about 200 px wide at 1080p and she is close to still. The back panel had the big pale-blue dot but no
lettering. Canon (`inputs/jade_in_outfit.png`, BACK view): "RARE EARTH" in small dark-grey sans-serif capitals, centred
under the dot. Measured on the sheet, with D = the dot's diameter: text width about 1.0 D, cap height 0.11 D, gap from
the dot to the caps 0.14 D, gap from the text to the hem rib 0.23 D.

## What I made
- **Tool:** `tools/v9/rare_earth.py`. It uses the same tracking idea as `tools/jacket_back.py`: the existing blue dot is the anchor.
- **Spec:** `tools/v9/rare_earth_O2.json`.
- **Output:** `media/shots/O2/take_3_engraved_dered_blue_v9rare.mp4`. It matches the source: 1920x1080, 24 fps, 145
  frames, 6.042 s, H.264 High, yuv420p, CRF 14 (same as the `_blue` source). The input is
  `media/shots/O2/take_3_engraved_dered_blue.mp4`, so the v6 blue eraser is kept.
- **To reproduce:** `tools/engrave/.venv/bin/python tools/v9/rare_earth.py tools/v9/rare_earth_O2.json` (about 9 s).
  `--compare 0,50,100 --outdir DIR` makes before/after tiles. `--track-only` prints the per-frame fit.

Method, per frame:
1. **Track the dot.** Find the pale-blue blob nearest the previous frame's dot and fit an ellipse to it (centre and
   axes). The fit is clean on all 145 frames. The axes are lightly smoothed. The centre is not smoothed, because the
   take moves on twos and a smoothed centre would lag.
2. **Place the lettering in the dot's frame (units: dot radii).**
   - Width 2.15 radii, about 1.07 D.
   - Caps start 0.26 radii below the dot's bottom edge.
   - Font: Liberation Sans Bold, tracking 0.05 em, word space 1.5x. Compared side by side with the canon sheet, this is
     the closest weight and width.
   - Width scales with the dot's horizontal axis and height with its vertical axis, so the lettering grows, shrinks and
     foreshortens with the panel.
   - Baseline angle follows the hem rib just below it. Each frame it is fitted to the rib's top outline and smoothed over
     time. It runs about 9 deg at frame 0 (arms up, hem pulled), then 6, 3 and 2 deg as she walks.
   - The dot ellipse's own tilt (about -10 deg) is not the panel's tilt. When I tried it, the text ran off-centre and
     uphill, so it isn't used.
   - The text is centred straight under the dot.
3. **Paint it onto the fabric as a multiply:** `letter = pixel x ink / local jacket white`, with ink (52, 51, 56).
   - The pixel's own shading, pencil grain and engraved hatch and fold strokes carry through the letters. Where a fold
     stroke crosses a letter, it is darker inside the letter.
   - The edges are 4x supersampled with a 0.35 px soften, to match the plate's line softness.
   - Only jacket-bright regions take ink. A closed luminance mask means thin hatch lines don't count as occluders, but
     hair, arms and outlines would stay in front. In O2 nothing crosses the lettering area in any frame.
   - The lower third is drawn by the engine on top at y=990, well below the lettering.
4. **Fade with the doorway light.** The ink strength follows the dot's own contrast. In the doorway wash at the end of
   the take (source frames 131-144, off screen), the lettering fades with the dot.

Size at 1080p:
- Caps are 11.3 px at the start (3:38.92), 11.6 px at 3:40.5 and 10.2 px at 3:42.0. At the end of the shot (3:42.77)
  they are 8.9 px.
- The text is 97 px wide at the start, shrinking to 77 px at the end.
- It reads clearly at 1:1, and you can still make out "RARE EARTH" in the 540p preview.

The re-encode differs from the source only inside the lettering box. Elsewhere the mean difference is 1.4-1.8/255,
which is codec noise.

## The EDL change (the lead applies it)
In `tools/sectionF/edl.py`, in the `CHOSEN` dict, change the O2 entry's `file`. Leave the rest of the line, including
the notes, unchanged:

```diff
-    "O2": dict(take=3, file=S + "O2/take_3_engraved_dered_blue.mp4", in_sec=0.0, rate=1.33, reverse=False, notes="v3 (Jade 3:40), retake: ...
+    # v9 fix 11 (Jade 3:40, docs/revisions/v9/fix_11_rare_earth.md): *_v9rare = the _blue plate with "RARE EARTH" lettered
+    # under the back dot, tracked per frame (tools/v9/rare_earth.py, spec tools/v9/rare_earth_O2.json)
+    "O2": dict(take=3, file=S + "O2/take_3_engraved_dered_blue_v9rare.mp4", in_sec=0.0, rate=1.33, reverse=False, notes="v3 (Jade 3:40), retake: ...
```

In `media/shots/F_edl.json`, the O2 shot (about line 1223):

```diff
-   "file": "media/shots/O2/take_3_engraved_dered_blue.mp4",
+   "file": "media/shots/O2/take_3_engraved_dered_blue_v9rare.mp4",
```

Re-running edl.py also rewrites `media/shots/O2/chosen.json` with the same `file` change. `clip_in` (0.0), `rate`
(1.33), the lower third, the flash and `matte_file` don't change. The matte is Jade's own silhouette, and the lettering is
inside it. edl.py already has other agents' uncommitted v9 edits (F1, F4, F7b, F7c, F8). I didn't touch the file, so
those stay.

## Evidence (`docs/revisions/v9/fix_11/`)
Master time to O2 source frame: src = (t - 218.92) x 1.33 x 24. On screen are source frames 0-123.

- `before_after_3m39_50.jpg`: 3:39.50, master f5268, src f18 (hands at the bun).
- `before_after_3m40_50.jpg`: 3:40.50, master f5292, src f50.
- `before_after_3m42_00.jpg`: 3:42.00, master f5328, src f98 (hand on the knob).
- About those three pairs:
  - They are 960x540 pairs. "Before" is the current preview frame (`render/engine/out/rewind/rewind_preview.mp4`).
  - "After" is that same preview frame plus the plate change (new minus old, scaled to 540p), so the grade, the flash
    and the lower third are all the real ones.
  - The source frame is matched to the preview frame by image difference.
- `lettering_fullres_3m40_50.jpg`: a 1:1 1080p crop at 3:40.50 (src f50), before | after.
- `every_frame_src000-047.jpg`, `every_frame_src048-095.jpg`, `every_frame_src096-144.jpg`: every one of the 145
  frames, decoded from the encoded output, cropped around the back.

I checked every frame by eye on those sheets at 1.5x zoom:
- The lettering stays centred under the dot and parallel to the hem, and never touches the rib or a seam.
- No frame jumps.
- Fold strokes pass through the letters at 3:38.9-3:39.9 (src 0-35, arms up).
- In the off-screen wash (src 131-144) it fades with the dot.

Spend: $0. Painting and compositing only, no paid calls. The ledger reads $262.90 of $400. That total includes other v9
agents' spend since the brief's $252.72; none of it is mine.

## Still imperfect
- The lettering is a clean typeset multiply. It follows the panel as an affine plane (position, scale, foreshortening,
  hem tilt). It doesn't bend into individual folds; it only takes their shading and strokes. In O2 the panel under the
  dot is smooth, so this doesn't show, but on a crumpled back it would look flat.
- The panel tilt comes from the hem fit, which is smoothed over about 3 frames. In src 0-35 (3:38.92-3:39.97) the hem is
  pulled up by her raised arms, so the text runs about 6-9 deg downhill to the right, parallel to that hem. It looks
  right next to the hem, but at a glance it reads as slightly tilted.

## Other shots where her back is large and still enough to notice the missing lettering (not fixed)
To find these I scanned the 540p preview every 4 frames for a pale-blue dot on white fabric, then checked the candidates
by eye.

1. **V2b3, 1:06.28-1:07.16 (master f1591-1612; C.js, the v9 1b driver's-seat take_2).** This is the strongest candidate.
   - We see her from behind and over the left shoulder in the driver's seat, with the dot huge: about 200 px wide at
     1080p (checked in the preview at f1592, f1598, f1604 and f1610).
   - At 1:06.33-1:06.6 (f1592-1598) the seat's edge cuts off the left part of the dot. The white panel under the dot is
     visible.
   - From about 1:06.83 (f1604) she hunches over the wheel and the back faces the camera squarely, with the panel under
     the dot in full view.
   - It is only 0.88 s and there's crash motion, but the back is far bigger than in O2.
   - It is a black-and-white engraved plate with her in colour, so the lettering would need the same multiply with the
     seat kept in front.
2. **F5b, 3:07.08-3:08.84 (f4490-4532), rooftop by the melting clock.** She stands still, seen from behind.
   - The dot is only about 28 px at 1080p and partly under her hair.
   - The lettering would have about 3 px caps, so it couldn't be read even if added. Probably not worth it.
3. **F2 / F2b wall-run, 2:52.96-2:56.48 (f4151-4236).**
   - The back is 90-110 px wide at most, running away from camera, with her hair swinging over it.
   - The lettering would be about 5 px caps and moving. Low priority.
4. **Lawn takes:**
   - E2_06_lawn at 1:55.67-1:56.03 (f2776-2785).
   - E2_07_lawn2 at 1:56.03-1:56.52.
   - E7_06_lawn at 2:18.38-2:19.00 (f3321-3336, in the ghost crowd).
   - All three are small and in motion. Not noticeable.

Smaller back views also came up: the "ACROSS THE" run at 1:40.8-1:42.0 and 0:05.5, and the g1/g2 gunfire around
1:38-1:42. In all of these she is a tiny running figure, and lettering could not be read.

---

# Part 2: V2b3 at 1:06 (Jade approved this one too)

Shot: `render/timeline/C.js` CUTS row `[66.28, 67.16, 'V2b3', 2, 0.45, 1.5]`, master 1:06.28-1:07.16 (f1591-1612).
- **Plate:** `media/shots/V2b3/take_2_engraved.mp4` (1920x1080, 24 fps, 97 frames). It is take 2 of the v9 1b re-stage,
  with Jade in the driver's seat (`docs/revisions/v9/fix_1b_v2b3.md`).
- **Source frames used:** src = 10.8 + (N - 1590.72) x 1.5, so master f1591-1612 play source f11-f42.
- **Camera:** locked off. The driver's seatback and bolster sit in front of her lower back.

## What I made
- **`media/shots/V2b3/take_2_engraved_v9rare.mp4` (the recommended file).**
  - It matches the source: 1920x1080, 24 fps, 97 frames, 4.042 s, H.264 High, yuv420p, CRF 16 `-tune grain`
    `+faststart` (as engrave.py).
  - Only pixels inside the lettering change. Elsewhere the p99 difference is about 6/255, which is codec noise in the
    engraving.
  - No geometry changes, so the hand-built `take_2_matte/` stays valid. The matte path in C.js is derived from the take
    number, not from the plate file, so it doesn't change.
  - Spec: `tools/v9/rare_earth_V2b3.json`.
- **`media/shots/V2b3/take_2_engraved_v9rare_canon.mp4`: for comparison only, not recommended.**
  - Here the lettering is strictly centred under the dot, as in O2.
  - In this take the dot is drawn left of her spine, close to the seat, so once she hunches the seat covers "RARE".
    Only "ARTH"/"EARTH" shows, which isn't readable.
  - Spec: `tools/v9/rare_earth_V2b3_canon.json`.
- **Reproduce:** `tools/engrave/.venv/bin/python tools/v9/rare_earth.py tools/v9/rare_earth_V2b3.json` (and the `_canon`
  spec).

New in `tools/v9/rare_earth.py`. All of it is opt-in per spec; I checked that O2's output is unchanged (the difference is
codec noise only):

- **`occ`: the seat in front of her.**
  - It is a static polygon traced on the bolster's ink outline. On f12/f20/f30/f40, a row scan of the outline lands on
    the same x (±1 px) every time, because the camera is locked off.
  - The polygon is the `SEAT` cut-out from `tools/v9/v2b3_matte.py`, extended along the outline of the bolster's lit
    band, which `SEAT` doesn't cover. It is grown by 3 px.
  - Letters inside it are hidden.
  - The dot ellipse is fitted only to its visible arc: contour points within 8 px of the seat are dropped. Until she
    ducks, the seat cuts off the dot's lower-left part.
- **`conj`: proper perspective for the turned and hunched back.**
  - The circle-to-ellipse map uses the baseline direction and the ellipse's conjugate semi-diameter, so the lettering
    takes the panel's foreshortening and shear. The handedness is fixed, so the text is never mirrored.
  - The ellipse's own tilt (-29° upright, +48° hunched) is the long-axis angle of a nearly round dot, not the panel's
    tilt, so it isn't used as the baseline.
- **`rot` keyframes: the baseline angle, set by eye against the hem and shoulder line.**
  - Src f0-21 (upright): 2°.
  - f22: 5°.
  - f24: 10°.
  - f26 onward (hunched; her head is down to the right and the back is tilted): 12°.
- **`shift_u` keyframes: how far the lettering slides along the baseline, in dot radii.**
  - Src f26 onward: 1.45. The lettering sits on the visible back panel's midline, just right of and below the dot's
    centre, and clears the seat. This take draws the dot left of her spine, so centring under the dot would hide half
    the word.
  - Src f0-21: -0.25. While she is upright, the lettering stays fully behind the seat, so no stray letters show.
  - Src f22-25: interpolated. During the duck she moves 100+ px right in four frames, and the word slides out from
    behind the seat with her body. This is the only stretch where the lettering moves relative to the fabric. It is
    hidden in the crash motion; in every frame from src f26 on it holds the same position relative to the dot.
  - This is a deliberate departure from "centred under the dot". The `_canon` file shows the alternative.

## What is visible, frame by frame
| master frames | time | src frames | lettering |
|---|---|---|---|
| f1591-1597 | 1:06.29-1:06.54 | 11-21 | none (upright; the lettering is behind the seat) |
| f1598-1599 | 1:06.58-1:06.63 | 22-23 | a "TH" fragment at the hem, starting to come out from behind the seat |
| f1600 | 1:06.67 | 24-25 | "RE EARTH", with the first letters still behind the seat |
| f1601-1612 | 1:06.71-1:07.17 | 26-42 | **"RARE EARTH" in full**, on the hunched back below the dot, tilted with the panel |

Size: the dot is about 175 px across, so the text is about 190 px wide with caps about 19 px. That is clearly readable
at 1080p, and you can still make it out in the 540p preview.

## The C.js change (the lead applies it)
In `render/timeline/C.js`, add one entry to the `BLUE_ERASER` map (the per-take plate override). The CUTS row stays as
it is:

```diff
 const BLUE_ERASER = { V2a3_3: 'take_3_engraved_blue.mp4', V2d2_4: 'take_4_engraved_blue_roundel.mp4', V2e2_2: 'take_2_engraved_blue.mp4',
-  V2c5_2: 'take_2_engraved_v9sleeve.mp4' };   // v9 #10 (Jade 1:17): orange band painted on her right sleeve (tools/v9/sleeve_band.py)
+  V2c5_2: 'take_2_engraved_v9sleeve.mp4',     // v9 #10 (Jade 1:17): orange band painted on her right sleeve (tools/v9/sleeve_band.py)
+  V2b3_2: 'take_2_engraved_v9rare.mp4' };     // v9 #11 (Jade 1:06): RARE EARTH under the back dot (tools/v9/rare_earth.py)
```

`plate('V2b3', 2)` then resolves to `media/shots/V2b3/take_2_engraved_v9rare.mp4`. This is a new path, so the engine
cache doesn't apply. `matte('V2b3', 2)` still gives `take_2_matte/matte.mp4`.

The C2 teaser flash (B.js, `source: 'film'`) replays about 66.86-66.92 s, which is master f1605-1606. It picks the
lettering up from the finished film automatically.

## Evidence (`docs/revisions/v9/fix_11/`)
- `v2b3_before_after_1m06_50.jpg`: 1:06.50, master f1596, src f18. She is upright and the lettering is hidden behind
  the seat, so before and after are the same.
- `v2b3_before_after_1m06_92.jpg`: 1:06.92, master f1606, src f33.
- `v2b3_before_after_1m07_08.jpg`: 1:07.08, master f1610, src f39.
- About those three pairs:
  - They are 960x540. "Before" is the current preview frame.
  - "After" is that frame plus the plate change, registered to it with an affine ECC fit (cc 0.999). The HUD and grade
    are the real ones.
- `v2b3_lettering_fullres.jpg`: src f36 (1:06.97, master f1608), 1:1 at 1080p, before | after.
- `v2b3_every_used_frame_src010-044.jpg`: every frame from src f10 to f44, decoded from the encoded output.

I checked each of those frames by eye, zooming into the start and end of the word on f26, f32, f36 and f42:
- The first R clears the bolster outline.
- The final H stays on the jacket.
- Fold strokes run through the letters.
- No stray letters show while she is upright, and nothing jumps from f26 on.

## Still imperfect
- The slide during the duck (src f22-25, 1:06.58-1:06.67) is a cheat. It is hidden by her 100+ px move in those
  frames, but frame by frame the word isn't fixed to the fabric there.
- The lettering is placed relative to the panel, not the dot (`shift_u`), because the dot in this take is off-centre.
  Next to the dot it reads as "under the dot, a little right".
- The tilt is keyframed by eye (12° hunched), not measured. The hem here is hard to fit automatically because the seat
  and her arm cut across it.

---

# Part 3: V2b3 round 2 (replaces Part 2's recommendation)

Jade on the Part 2 file: "1:06 - RARE EARTH on jacket is off center. part of the word should be cut off, the way it
naturally would be on a jacket. the words don't move around when you hunch." The Part 2 `shift_u` slide is gone, and so
is the "fully behind the seat while upright" rule. Part 2's `take_2_engraved_v9rare.mp4` and `_v9rare_canon.mp4` are
superseded. Don't use them.

## What I made
- **Output:** `media/shots/V2b3/take_2_engraved_v9rare2.mp4`.
  - It matches the source: 1920x1080, 24 fps, 97 frames, 4.042 s, H.264 High, yuv420p, CRF 16 `-tune grain`
    `+faststart`.
  - Only pixels inside the lettering change. Outside the lettering box, at most 83 pixels per frame differ by more than
    25/255 (codec noise in the engraving).
  - No geometry changes, so `take_2_matte/` stays valid.
- **Spec:** `tools/v9/rare_earth_V2b3_r2.json`.
- **Reproduce:** `tools/engrave/.venv/bin/python tools/v9/rare_earth.py tools/v9/rare_earth_V2b3_r2.json`.

Every frame uses one rule, derived only from the panel's tracked motion:
- **Position and scale come from the dot.**
  - The dot is ellipse-fitted every frame, using only its visible arc: contour points against the seat are dropped,
    because the seat cuts off its lower-left part while she is upright.
  - The word is centred under the dot, perpendicular to the hem, 0.26 dot radii below its edge, and 2.15 dot radii wide.
  - It is scaled by the dot's semi-diameters along and across the baseline (the new `scale_dir`). As the dot
    foreshortens when she hunches (vertical semi-diameter from 103 to 95 px), the caps go from 21.6 to 19.6 px with it.
- **Tilt comes from the hem.**
  - The jacket's bottom outline is line-fitted every frame (new `rot: "hem"`), smoothed over about 5 frames.
  - While she is upright the hem is mostly behind the seat. The fit holds the value from the nearest frame where at
    least 30 columns of hem are visible.
  - The result: -5.7° upright, easing to -2.7° hunched.
- **No per-frame "where is it readable" rule and no keyframed shift.** The word's centre sits 139 px below the dot centre
  upright and 127 px hunched. The change is the dot's own foreshortening; the word keeps the same place relative to the
  dot and the hem.
- **Seat occlusion uses a static mask of the driver's seat bolster.**
  - The camera is locked off.
  - The mask is traced on the bolster's black ink outline, which row scans on f12/20/30/40 put at the same x within ±1 px.
  - It is grown by only 1 px, so the letters are cut right at the outline's edge.
  - Whatever falls behind the seat is hidden; there is no sliding.

## Frame table (src = 10.8 + (master f - 1590.72) x 1.5)

| master frames | time | src frames | what shows of the word |
|---|---|---|---|
| f1591-1597 | 1:06.29-1:06.54 | 11-20 | only the final "H" (or "TH") at the seat's edge. In this take the seat covers the panel under the dot's left half and the dot's lower-left part, so the centred word is almost all behind it. |
| f1598-1599 | 1:06.58-1:06.63 | 21-23 | "TH", then "RTH": she starts to duck and more of the panel clears the seat |
| f1600 | 1:06.67 | 24-25 | "EARTH" / "E EARTH" |
| f1601-1612 | 1:06.71-1:07.17 | 26-42 | "RE EARTH" or "E EARTH": the R and A of RARE (and sometimes the first R) are behind the seat |

Size: about 206 px wide, caps 21.6 px upright and 19.6 px hunched. EARTH reads clearly at 1080p, and you can make it out
in the 540p preview.

## The C.js change (the lead applies it)
In `render/timeline/C.js`, the `BLUE_ERASER` entry for V2b3_2 is `'take_2_engraved_v9rare2.mp4'`. The CUTS row is
unchanged:

```diff
 const BLUE_ERASER = { V2a3_3: 'take_3_engraved_blue.mp4', V2d2_4: 'take_4_engraved_blue_roundel.mp4', V2e2_2: 'take_2_engraved_blue.mp4',
-  V2c5_2: 'take_2_engraved_v9sleeve.mp4' };   // v9 #10 (Jade 1:17): orange band painted on her right sleeve (tools/v9/sleeve_band.py)
+  V2c5_2: 'take_2_engraved_v9sleeve.mp4',     // v9 #10 (Jade 1:17): orange band painted on her right sleeve (tools/v9/sleeve_band.py)
+  V2b3_2: 'take_2_engraved_v9rare2.mp4' };    // v9 #11 (Jade 1:06): RARE EARTH centred under the back dot, seat in front (tools/v9/rare_earth.py)
```

If the Part 2 line (`'take_2_engraved_v9rare.mp4'`) was already applied, change only that value to
`'take_2_engraved_v9rare2.mp4'`. `matte('V2b3', 2)` is unchanged (`take_2_matte/matte.mp4`).

## Evidence (`docs/revisions/v9/fix_11/`)
- `v2b3_r2_every_used_frame_src010-044.jpg`: every used frame, src f10-44, cropped to her back. Each tile is labelled
  with the src frame, master frame and m:ss.
- `v2b3_r2_dot_stabilised_src010-044.jpg`: the same frames, each cropped centred on the tracked dot, with a red line
  through the dot centre. It is the check that the word doesn't move against the dot.
  - Upright (src 10-23), the visible "H" stays at the same place.
  - Through the duck (src 24-26), the word comes in with the panel. The dot centre is 0.1-0.15 of the word's width left
    of its middle because the seat hides the left part; the word's position is the same.
  - Hunched (src 26-44), "E EARTH" holds the same position under the dot to within about 2 px at 1080p.
- `v2b3_r2_hidden_part.jpg`: src f12, f18, f30 and f40. The fitted dot is drawn in yellow, the seat outline in green,
  and the whole word, including its hidden part, in red. It shows the word is centred and that the seat really covers
  what is missing.
- `v2b3_r2_before_after_1m06_50.jpg`: 1:06.50, master f1596, src f18.
- `v2b3_r2_before_after_1m06_92.jpg`: 1:06.92, master f1606, src f33.
- `v2b3_r2_before_after_1m07_08.jpg`: 1:07.08, master f1610, src f39.
- About those three pairs: they are 960x540. "Before" is the current preview frame; "after" adds the plate change,
  ECC-registered to that frame (cc 0.999).
- `v2b3_r2_lettering_fullres.jpg`: src f36 (1:06.97, master f1608), 1:1 at 1080p.

I checked every used frame by eye on both sheets, plus 3x zooms of the seat-edge cut at src 14, 22, 25, 28, 34 and 42.
The letters are cut cleanly at the seat's black outline, with no gap and nothing over the seat.

## Still imperfect
- While she is upright (1:06.29-1:06.63), only "H" to "RTH" shows at the seat's edge. That is the honest consequence of
  centring under a dot that this take draws partly behind the seat. It reads as a letter at the edge of the seat, not as
  a word.
- The tilt changes by 3° over the duck (-5.7° to -2.7°), following the hem fit. If Jade wants it rock-steady, a fixed
  -3° would also sit fine against the hem.
