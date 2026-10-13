# v6: one blue eraser, one pink eraser (O2, V2a3, V2d2, V2e2, B_shot)

Jade's notes:
- 3:42 "dissertation defense - the pencils should have one blue eraser and one pink eraser" (O2)
- 0:59 (V2a3), 1:24 (V2d2), 1:26 (V2e2), 1:51 (B_shot): the same problem.

Canon (render/timeline/E.js G_CLIPS, media/shots/O2/_ref_bun_two_pencils.jpg): two crossed yellow pencils in the bun,
one with a **pale-blue** eraser and one with a **pink** eraser. In all five takes both erasers were drawn pink.

## Method (all five clips)

This is a pixel recolour, with no generative model. The tool is `tools/blue_eraser.py`, with one spec per clip in `tools/blue_eraser_specs/<shot>.json`.
To reproduce a clip: `tools/engrave/.venv/bin/python tools/blue_eraser.py apply tools/blue_eraser_specs/<shot>.json`.

- **Blue value.** The median of the pale-blue eraser in G1 take_3 and G2 take_5 (the E.js G_CLIPS plates) and in the ref sheet is
  RGB ~(175, 200, 224) (#AFC8E0): hue 214 deg, saturation ~0.22. Measured samples: G1 (167-189, 186-203, 207-217),
  G2 (166-179, 183-201, 208-222), ref (172-177, 204-205, 225-231).
- **Recolour.** Inside the eraser mask, the hue is set to 214 deg and the saturation is scaled by 56/95 (the canon blue's
  saturation over the O2 pink eraser's), capped at 0.27. Value is kept, so shading, paper grain, fades and motion blur carry over.
  The pink eraser in O2, (226, 142, 168), becomes about (176, 198, 226). The eraser's own dark-red ink outline turns dark
  slate (low saturation), like the canon pencils. The mask edge is feathered by a 0.6 px blur. The lavender/silver
  ferrule is excluded by hue and keeps its colour.
- **Mask and tracking.** Each frame has an anchor (the chosen eraser's centroid). The mask is the eraser region
  nearest that anchor, within 12 px.
  - O2: the wall behind her is the same pink as the eraser (hue 174-178 vs 171-174), so colour alone cannot separate them.
    There the mask is the non-dark region enclosed by the eraser's ink outline. In the motion-smeared frames the smeared
    pink next to the eraser is added, and a frame with no enclosed region reuses the previous frame's mask, because the
    take moves in 2-frame steps.
  - C clips and B_shot: the backdrops are black-and-white engraving with no pink, so the mask is the strong-pink blob
    (hue >= 320 deg or <= 8 deg, saturation > 0.18) nearest the anchor.
  - Anchors came from a first-pass tracker: continuity tracking for O2, and for the night and B plates the two eraser
    blobs per frame, taking the right-hand one. All anchors were then reviewed frame by frame.
- **Encode.** Each output matches its source: libx264 High, yuv420p, 24 fps, same frame count and duration. O2 uses CRF 14
  (as tools/sectionF/dered.py). The engraved takes use CRF 16 `-tune grain` `+faststart` (as tools/engrave/engrave.py).
  Outside the eraser, the re-encode differs from the source by a mean of about 1.7/255 per channel (generation noise only).
- **Check.** I reviewed every frame of every clip as a zoomed before/after crop. I also ran an automated pass over
  the encoded files: there is no residual eraser pink in any frame (the only flagged pixels were near-black backdrop noise).

## O2 (section F, 218.92-222.78; take_3_engraved_dered.mp4, 145 frames)

- **Pencil:** the upper-left one. It is already through the bun at frame 0. The upper-right one is the pencil she slides in
  at about 0.6-1.2 s (its eraser is in or near her right hand early on). It stays pink.
- **Visibility:** the blue eraser is visible and recoloured in all 145 frames. It is never fully occluded.
  - Frames 93-116 are motion-smeared over the door frame. The smear was taken too (spec "smear").
  - Frames 141-144 are washed out by the doorway light and go pale blue-grey, matching the fade.
  - Frame 144 reuses frame 143's mask (a near-duplicate frame).
- **Output:** `media/shots/O2/take_3_engraved_dered_blue.mp4`.
- **EDL:** tools/sectionF/edl.py's O2 entry now names that file. I re-ran edl.py, and the only files that changed were
  media/shots/O2/chosen.json and the O2 "file" in media/shots/F_edl.json. Today's TVA REPORT, CASE 4,098 and base 4098
  edits are still in place.

## V2a3 take 3 (section C, 59.20-60.08 and 62.30-63.62; 121 frames)

- **Pencil:** the right-hand (windscreen-side) pencil. Its eraser is the right one of the pair in every frame. The left one
  stays pink.
- **Visibility:** the blue eraser is visible in all 121 frames.
  - Frame 13 is motion-blurred; the smear went blue.
  - The other (pink) eraser is drawn white by the take in frame 53, which is not on screen.
- **Output:** `media/shots/V2a3/take_3_engraved_blue.mp4`.

## V2d2 take 4 (section C, 83.98-84.86, clip 2.0 to ~2.53 at 0.6x with frameBlend; 121 frames)

- **Pencil:** the right-hand pencil, whose eraser is above her right temple. The left one stays pink.
- **Visibility:** the blue eraser is visible in all 121 frames.
  - In about frames 81-102 the engrave pass whitened part of it. Only the pink part is recoloured, and the white part is left as drawn.
  - The other eraser is drawn white in frames ~83-111.
  - The recolour is the same in every frame, so frameBlend does not flicker.
- **Output:** `media/shots/V2d2/take_4_engraved_blue.mp4`.

## V2e2 take 2 (section C, 86.18-87.06, zoomed 1.4x; 97 frames)

- **Pencil:** the right-hand (windscreen-side) pencil, as in V2a3. The other stays pink.
- **Visibility:** both erasers are visible in all 97 frames, and the blue one is recoloured in all of them.
- **Output:** `media/shots/V2e2/take_2_engraved_blue.mp4`.

C.js gets one small map instead of `plate()`'s fixed path:
`BLUE_ERASER = { V2a3_3, V2d2_4, V2e2_2 }`. `plate(clip, take)` returns the `_blue` file for those takes and the usual
`take_N_engraved.mp4` for everything else. `matte()` is unchanged, so the GIRL matte + keepColor layers draw the blue
eraser too. Today's other C.js edits (RELOAD_SKIP, deaths, loading tip) are kept.

## B_shot take 1 (section B, B2_shot 110.78-111.22 and the CONTINUE? freeze 111.22-112.66; 97 frames)

- **Pencil:** the right-hand pencil. The left one stays pink.
- **Visibility:** both erasers are visible in all 97 frames (the head barely moves), and the blue one is recoloured in all of them.
- **Output:** `media/shots/B_shot/take_1_engraved_blue.mp4`.
- **_B_verse2.js:** a `SHOT_BLUE` const sits beside the B2_shot block. B2_shot's plate and both C_V2n_continue video layers
  (the plain one and the matte + keepColor one) point at it. `matte('shot')` is unchanged, and nothing else in the file was touched.

## Verification images

These are in the session scratch folder, not in the repo:
`/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/`

- **O2**
  - `o2/o2_every6_before_after.jpg`: every 6th frame, head crop, before and after (decoded from the encoded file).
  - `o2/c0.png`, `o2/c1.png`, `o2/c2.png`: every frame, eraser zoom, before and after.
  - `o2/stills/rewind_preview_t219_500.png` ... `t222_500.png`: engine stills at preview size, plus `o2_stills_grid.jpg` and `o2_stills_zoom.jpg`.
- **V2a3:** `c/V2a3_ba_0.png` and `c/V2a3_ba_64.png` (every frame, before and after).
- **V2d2:** `c/V2d2_ba_0.png` and `c/V2d2_ba_64.png` (every frame, before and after).
- **V2e2:** `c/V2e2_ba_0.png` (every frame, before and after).
- **B_shot:** `c/B_shot_ba_0.png` (every frame, before and after).
- **Section C engine stills:** `c/stills/rewind_preview_t59_500.png`, `t59_917`, `t62_583`, `t63_292`, `t84_083`, `t84_417`,
  `t84_750`, `t86_292`, `t86_583`, `t86_958`, plus `c/stills/C_stills_zoom.jpg` (one pink and one blue eraser in every still).
- **B_shot engine stills:** `c/stills_b/rewind_preview_t110_917.png`, `t111_083.png`, `t111_792.png`, plus `c/stills_b/B_shot_stills_zoom.jpg`.
  The CONTINUE? negative keeps her in colour through the matte, with one pink and one blue eraser.

The B.js drop-1 rewind and the C2 teaser composite the film (`source: 'film'`), so they inherit the change.

## Eraser audit follow-ups (docs/revisions/v6/eraser_audit.md)

### E4b_haul: B_haul_b take 1 (section D, 121.30-123.00; take 0.05 -> 2.48 s at 1.43x, so take frames 1-60 are on screen)

Fixed.

- **Pencil:** the live (climbing) Jade's right-hand pencil is now blue and her left one stays pink.
  - While she hangs (frames 0-25), the blue one is the lower-right pencil of the X.
  - From frame 34 on it is the right arm of the V. The two pencils keep their left/right order through her climb, so the
    blue stays on the same physical pencil.
- **Frames:** the blue eraser is recoloured in frames 0-73. From frame 74 it is above the top of the frame, so 74-120 are left alone.
  - Frames 29, 32 and 33 are motion-blurred. Their anchors are interpolated, and the previous frame's mask is carried
    along with the anchors and kept only on pink pixels.
- **The lying Jade is not recoloured.** In the film she is not drawn from the plate. She is the baked gold line-art ghost
  (`media/shots/_D/v3/ghost_haul_{rgb,alpha}.mp4`), and `patch_haul.png` covers the plate wherever she ever is, so her
  plate erasers never reach the screen. Her ghost is monochrome gold, so it has no eraser colour to fix.
- **Output:** `media/shots/B_haul_b/take_1_engraved_blue.mp4`, with spec `tools/blue_eraser_specs/B_haul_b.json`.
- **Wiring:** `tools/sections/D/build_timeline.py` `twin_shot()` takes an optional `plate=` (a re-coloured copy of the take
  for the bg and live-jade layers; the mattes stay the take's), and E4b passes the `_blue` file.
  - I regenerated D.js. Compared with the D.js already on disk, only E4b's two layers changed: `bg` and the
    matte + keepColor `jade` layer. In D_edl.json only the same two `src` lines changed, and ghost_table.json is unchanged.
  - The other agents' edits in build_timeline.py (E2 ghost-gun solo, E5 v6 ghost/matte, C2 `Lc` mattes) are kept and
    were already in the D.js on disk.
- **Tool change:** in `tools/blue_eraser.py`, a frame with no detected eraser now carries the previous mask *moved with the
  anchors* and keeps only its pink pixels. Before, it stayed in place, which only worked for still frames.
  - The one earlier clip that used this is O2 (frame 144). Re-running its spec now gives a fractionally smaller mask
    there. That is below codec noise, so the O2 file was not re-encoded.

### V2h1 take 2 (C.js 93.66-94.06): not changed

At full resolution there is no readable eraser pair. Each pencil is a short pale rose-beige stick (hue 0-15°,
saturation ~0.18-0.25) with no separate eraser band. A trial recolour of the right pencil turned its whole shaft blue,
so I dropped it. No `_blue` file was made and the C.js map is unchanged.

### B_round_corner_b take 1 (107.28-109.92): not changed

- **Which layers render here:** `V4_GUN` replaces only the lawn block (B2_lawn/B2_lawn2/B2_ear) with `_B_gunfire.js`.
  107.28-109.92 is still rendered by `B2_corner` and `B2_corner_in` in `_B_verse2.js`; the engine stills show those shot ids.
- **What the take shows:** in the run-up (take frames 0-25, on screen in B2_corner) both pencil ends are near-white blush
  (saturation ~0.15-0.18). After she meets the agent they are dark or hidden. At preview size they read as white tips,
  not as a pink pair, so there is no pink pair to fix.

### Verification images (scratch, not in the repo)

These are in `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/aud/`:

- **B_haul_b, every frame:** `haul_ba0.png` (frames 0-39) and `haul_ba1.png` (frames 40-73), zoomed before and after.
- **B_haul_b, engine stills:** `haul_stills/rewind_preview_t121_417.png` ... `t122_917.png` at preview size, plus
  `haul_stills/haul_stills_zoom.jpg`, which zooms on the bun (take frames 5-57, one pink and one blue in each).
- **The two unclear shots:**
  - `V2h1_heads3.png` and `V2h1_ba0.png`: the V2h1 full-res crops and the rejected trial.
  - `corner_z.png` and `corner_mid.jpg`: the round_corner_b full-res crops.
  - `unclear_preview_zoom.jpg`: engine preview zooms of both shots.
