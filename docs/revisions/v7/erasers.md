# v7: pencil and eraser continuity (Jade's notes at 0:11, 0:27, 0:33 and 0:39)

Source: Jade's review of `deliverables/rewind_v6_upload_720p_sfx_100MB.mp4` (film time = file time).

Canon: two crossed pencils through the bun, one with a pale-blue eraser (RGB ~175,200,224) and one with a pink eraser.

Every fix is a pixel pass, with no generative model and no paid API. Each fixed clip is a new file next to its source take, and `render/timeline/A.js` points at the new files. No source take was overwritten.

**Checked in context.** I rendered `node render/engine/render.mjs --range 10.5 40 --preview --encode` to the scratchpad, then compared it with the v6 720p upload at the defect times.

**Sheets.** All of these are in this folder and each is under 300 KB:
- one before/after crop sheet per shot, in source pixels;
- `film_v6_vs_v7.jpg`, the in-film comparison of v6 against the v7 preview.

## Why the prior audit missed these

`docs/revisions/v6/eraser_audit.md` used 2 fps sheets. Three of the four defects are matte dropouts in the engrave pass: `tools/engrave` keeps Jade in colour through a segmentation matte (`take_N_matte/`), and in these frames the matte lost the pencil tops. The pencil tops were then engraved as world: white paper with hatching.

The raw takes still have the colour, except D6's right eraser, which the raw take draws pale lavender-grey.

## 0:27, D3 (`media/shots/D3/take_2_engraved.mp4`, shot 25.34-28.40, in 0)

- **What was wrong:** a streetlight flash passes behind the bun in source frames **34-47** (film 26.76-27.30). The matte dropped both pencil tops:
  - the blue eraser and ferrule went white in frames 34-41, 43, 46 and 47, and were part white in 42, 44 and 45;
  - the pink pencil's ferrule and eraser were part white in frames 34-47.
  
  The same dropout happens at frames 82-83, 89-91 and 96-97. Those are outside the cut (it uses frames 0-73), but I fixed them as well.
- **What I did:** `tools/matte_fix.py` with spec `tools/matte_fix_specs/D3.json`:
  1. **Repair the matte.** I took the pencil tops from the matte of the nearest good frame (33, 81, 88 or 92) and moved them rigidly with each pencil, using an ECC fit on the raw take.
  2. **Re-run the engrave pass.** I ran `tools/engrave/engrave.py` on the raw take with `--matte-in` set to the repaired matte. The pipeline is deterministic: outside the changed area, the re-run matches the shipped take to within encode noise (about 2.5/255 mean).
  3. **Splice.** Only the regained pencil area, plus 10 px around it, comes from the re-run, and only in the listed frames. That 10 px also takes away the ink halo the engraving drew round the white pencil top.
- **Output:** `media/shots/D3/take_2_engraved_eraser.mp4`. Pale-blue pixel count in the eraser box:
  - v6: 0 in frames 34-41;
  - v7: 350-390 in every frame of the cut, which matches frames 0-33.
- **Sheet:** `erasers_D3_0m27.jpg` (frames 33, 35, 38, 41, 44 and 47, before and after).

## 0:33, D6 (`media/shots/D6/take_2_engraved.mp4`, shot 32.36-33.66, in 0.4 = source frames ~10-40)

0:33 is D6, not D7. I checked D7 frame by frame: it has a stable pink and blue pair in every frame, and I left it unchanged.

- **What was wrong:** in every frame of the cut (source frames 0-41), the matte held only half of the pink eraser and none of the right pencil's top, so both were engraved white. Frames 42-45 were the only ones with a whole pink eraser. The right eraser was never blue in any frame. It is pale lavender-grey (193,190,201) in the raw take too, so restoring the matte alone gives grey, not blue.
- **What I did, in two passes:**
  1. `tools/matte_fix.py` with `tools/matte_fix_specs/D6.json`: hand polygons round both pencil tops, drawn in raw frame 20 and tracked over the take. This gives the intermediate `media/shots/D6/take_2_engraved_matte.mp4`, which the second pass reads.
  2. `tools/blue_eraser.py` with `tools/blue_eraser_specs/D6.json`: the right eraser is set to canon blue using the new modes `any_hue`, `sat_mode: "target"` and `v_gain` 1.11. The result is about (174,192,220), hue 218° and saturation 0.24. The ferrule stays silver.
- **Output:** `media/shots/D6/take_2_engraved_eraser.mp4`.
- **Sheet:** `erasers_D6_0m33.jpg` (frames 10, 20, 30 and 40).

## 0:39, P2 (`media/shots/P2/take_2_engraved.mp4`, shot 38.9-39.68, in 0.3 = source frames ~7-26)

- **What was wrong:** the matte cut the blue pencil's top in **every frame but 18**. The eraser was half white and the ferrule was engraved. The pink pencil's ferrule was also engraved in about frames 4-17.
- **What I did:** `tools/matte_fix.py` with `tools/matte_fix_specs/P2.json`. Frame 18 is an odd frame, with the pencils redrawn larger, so I could not use its matte. The masks are hand polygons round the eraser and ferrule, drawn in raw frames 12 and 30, tracked over all 97 frames and spliced as for D3.
- **Output:** `media/shots/P2/take_2_engraved_eraser.mp4`. The blue pixel count goes from about 180-200 to about 485-530, which is steady and matches frame 18.
- **Sheet:** `erasers_P2_0m39.jpg` (frames 8, 12, 15, 20 and 24).

## 0:11, C4 (`media/shots/C4/take_4_engraved.mp4`, shot 10.82-12.60, in 0)

- **What was wrong:** this is a placement problem in every frame, not a flicker. The take comes from the kf_v3_b keyframe edit, which draws the two pencils as a big X lying on the back of her head, with no bun round them. The X crosses at about (318,161) at 1080p:
  - the pink-eraser pencil's point reaches her neck;
  - the blue-eraser pencil's point reaches the headrest.
  
  In D3, D6 and P2 a dark bun has the pencils pushed through it: erasers out one side, short points out the other, the middles hidden.
- **First try (rejected by Jade):** `tools/c4_pencils.py` → `take_4_engraved_pencils.mp4`. It moved the X up and shortened it, but every part of both pencils still lay on top of her hair. The file is kept but no longer used, and can be deleted (51 MB).
- **Options weighed:**
  - **Trimming or re-timing:** no use, because every frame has the same placement.
  - **Another take:** take 2 has one pencil, and take 3 has the same X.
  - **Regeneration:** not needed.
- **What I did:** `tools/c4_bun.py`, a pixel pass that writes `media/shots/C4/take_4_engraved_bun.mp4`.
  1. **Bun.** The round bun from C4 take 2, frame 0. It comes from the same keyframe family, the same framing and the same engraved black-hair linework.
     - It is cut along its own ink outline, and take 2's own pencil inside it is inpainted dark.
     - It is registered onto take 4 by an affine fit on her head, face and ear (correlation 0.96).
     - It sits at take 2's position, roughly x 263-376, y 61-201 at 1080p. I tried it 35 px lower and rejected that: the patch edge showed inside her hair, and take 4's own small bun showed above it.
     - It covers the crossing and the middle of both pencils: the pink-eraser pencil over about 130 px and the blue-eraser one over about 115 px.
  2. **Tracking.** One rigid fit per frame on the pencils, always against frame 0 so it cannot drift. The bun, the new points and the fills all ride the same warp, so nothing swims against the hair. Her head moves up to about 12 px across the take.
  3. **Short points.** Each pencil ends about 62 px past where it leaves the bun: about 9 px of body plus the sharpened cone.
     - The rest of each old lower leg is removed.
     - Both cones are resampled from the pink-eraser pencil's own point. That point lies over her neck, which the colour matte keeps in every frame; the blue-eraser pencil's own point lay on the headrest, where the matte flickers, and it went white in some frames.
  4. **Fills where the old legs were** (this also removes v7's first-try headrest dashes and neck mark):
     - **Blue-eraser leg** (along the headrest edge): the engraved hatching there changes with every streetlight sweep, so the leg is removed in the **raw** take instead. A clean plate of the static background is made once from raw frame 0 by a vertical copy that follows the headrest stripes, and tone-matched to each frame. The colour matte there is set the same way as its neighbours in each frame, the take is re-engraved with `tools/engrave`, and only the old-leg strip (plus 6 px) is spliced in. The re-engraved strip therefore carries the same hatching as the headrest round it in every frame.
     - **Pink-eraser leg** (hanging hair and the neck under her ear): take 2's frame 0 at the same place on her head, which shows hair and neck with no pencil there. It is registered and tracked like the bun, and tone-matched to each frame by a smooth difference fill.
  5. **Layers**, back to front: the filled frame, then the pencils, then the bun.
- **Reframe:** kept and raised to 60 px. The y keys of `C4_PUSH` start at `C4_DOWN = 60`, where they were 0 in v6 and 40 in the first try. At 40 px most of the bun was under the top letterbox bar; at 60 px the bun's lower two thirds and both points show during the hold, and the push still ends on the sticky note exactly as before. The eraser ends are above the bar during the hold, so their colours don't read there.
- **Check:** I rendered `node render/engine/render.mjs --range 10 13 --preview --encode` (`render/engine/out/rewind/rewind_preview_10.00-13.00.mp4`) and went through every frame from 10.83 to 11.79 s at 2.5× zoom. The bun is present in every frame, its edge is stable from frame to frame, and only the points show below it. I also checked consecutive source frames 14-21 at full resolution.
- **Sheet:** `pencils_C4_0m11.jpg`. The top half is source frames 0, 10 and 20, v6 against v7; the bottom half is the film at 10.88, 11.25 and 11.50 s, v6 upload against the v7 preview. The C4 rows of `film_v6_vs_v7.jpg` show the rejected first try and are superseded by this sheet.

## Left open

- **C4:**
  - The bun is take 2's and is a little larger and rounder than take 4's own hair suggests. Up close, its outer edge reads as a separate knot, which is the intended look.
  - The re-engraved headrest strip is clean but slightly busier than the headrest round it in a few frames, mostly around 11.3-11.45 s.
  - The 60 px reframe puts the sticky note's lower edge about 20 px under the bottom bar during the hold.
  - To revert: point C4 back at `take_4_engraved.mp4` and set `C4_DOWN` to 0.
- **Intermediate file:** `media/shots/D6/take_2_engraved_matte.mp4` (29 MB) is the input to the D6 blue pass. I kept it so the fix can be reproduced; the timeline does not use it.
- **Not done:** no full-film or 1080p render. The deliverables still need a re-render. Nothing is committed.
