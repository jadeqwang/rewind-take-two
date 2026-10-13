# v6: the gold ghost's leg and the protagonist's sneakers in E5 (2:03)

Jade: "2:03 - Banach-Tarski pointing scene: ethereal gold Jade's butt is opaque for a split second and protagonist Jade's sneaker is partly erased."

Shot `E5_slide_point` runs 123.00-125.26 and plays take `B_slide_point_b` frames 21.6-104 (in 0.9, x1.52). Film time is 123 + (frame/24 - 0.9)/1.52.

## What is visible (engine preview 960x540, every frame 122.917-125.292)

| Film time | Take frames | What shows |
|---|---|---|
| 123.000-123.250 | 21-30 | The gold ghost's left leg (hip, thigh, knee, shin with the orange pocket strap) is opaque navy. On 123.00-123.04 her sneaker is opaque too. |
| 123.250-123.475 | 30-39 | The same leg, shrinking to an opaque navy strip down her left thigh |
| 123.000-125.170 | 22-101 | The protagonist's sneakers lose their lower half and soles, which show the white book cover. What remains reads as a dark blob beside her foot (e.g. 124.2). |
| 123.667-123.750 | 45-49 | A white bite out of the protagonist's trouser leg above her sneakers |

E4b_haul (121.30-123.00), checked frame by frame: no defect there. The gold girl lying on the roof stays translucent, and the climbing girl is intact.

## Cause

Neither the layer order nor the `clean`/`cover` patches caused this. Both faults come from the split of the two girls (`splitpair.py` on `take_1_jmatte`), which produced `B_slide_point_b/take_1_live`, the matte of the `jade` layer:

1. **Opaque butt/leg.** The split walks out from a seed frame. On take frames 19-39 it gave the gold girl's near (left) leg to the live girl, so the `jade` layer drew it in its real navy over the ghost. The ghost matte (`e5_arm/ghost_matte`) did not have the leg either, so the ghost sprite had no leg there.
2. **Erased sneaker.** `take_1_jmatte` is colour-gated: it keeps only the matte near her coloured pixels, such as the navy trousers and orange straps. Her pale sneaker soles over the pale cover fell outside it on almost every frame, and so did a patch of trouser on frames 45-49. Those pixels were in neither matte, so the `cover` patch showed through.

## Fix

- New `tools/v4B/coop/e5feet.py` (`tools/engrave/.venv/bin/python tools/v4B/coop/e5feet.py [--check=sheet.jpg]`). It touches take frames 19-104 only. It also runs BiRefNet on a crop around the girls' legs, the same method as `armfix.py`.
  - Leg: one hand-keyed polygon per keyframe (frames 19-39, interpolated in between) around the ghost's left leg. Inside it, the leg is cut from the live matte and the figure pixels are added to the ghost matte. Near the polygon, thin slivers and bare plate left in the live matte are also removed: the leg's outline and the shadow strokes between her toe and the leg.
  - Sneakers: BiRefNet figure pixels are added to the live matte if they touch it, are not ghost, and lie in the bottom 100 px of her figure (her feet). On frames 44-50, the trouser box is also filled.
  - Output: `media/shots/C_coop/e5_arm/live_v6/` (PNG + `matte.mp4`) and `media/shots/C_coop/e5_arm/ghost_matte_v6/`. The inputs `take_1_live/` and `e5_arm/ghost_matte/` are untouched.
- The ghost was rebaked from `ghost_matte_v6` with the same arguments: `tools/sections/D/ghostseq.py media/shots/B_slide_point_b/take_1_engraved.mp4 media/shots/C_coop/e5_arm/ghost_matte_v6 "#C9A227" media/shots/C_coop/e5_arm/ghost_slideptb_v6 0.85 4.4333`. Against v4, frames 40-106 differ only by re-encode noise (mean 0.1/255).
- `tools/sections/D/build_timeline.py`, E5 only: `ghost_stem` changed from `ghost_slideptb_v4` to `ghost_slideptb_v6`. The `jade` layer's matte `src` is set to `e5_arm/live_v6/matte.mp4` (one line after the `twin_shot` call), with a v6 comment. `render/timeline/D.js` was regenerated. The only E5 change is those three `src` paths, and no other shot changed.
- `media/shots/C_coop/NOTES.md`: added a line for the v6 assets.
- New media is about 6 MB (`media/` is gitignored). The v4 files are kept for rollback.

## Verification (engine preview 960x540, every frame 122.917-125.292)

Pixel diff of before against after: E4b's last frames and E6a's first frame are identical. Inside E5, changes are limited to the two girls' legs. All images are in the scratch folder (not in the repo):

- `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/e5/ba_leg.jpg`: before (top) / after (bottom), every frame 123.000-123.458, cropped on the legs
- `.../e5/ba_leg_zoom.jpg`: 2x zoom, 123.000, 123.083, 123.125, 123.250, 123.292, 123.375
- `.../e5/ba_feet.jpg`: before/after, 123.542-125.125, including the trouser bite at 123.708 and 123.750
- `.../e5/all_before.jpg` / `all_after.jpg`: every frame of the shot, cropped on both girls
- `.../e5/raw_a.jpg`, `raw_c.jpg`, `diag_b.jpg`: the raw take with the old live (red) and ghost (blue) mattes, showing the leg in the live matte and the cut sneaker soles
- `.../e5/fix_sheet3.jpg`: `e5feet.py --check` output (magenta = moved out of live, green = added to live)
- `.../e5/prev_E4b.jpg`, `e4b_zoom.jpg`: the E4b check

Known leftovers: at 123.125 a few of the plate's black shadow strokes sit at the gold girl's heel. They are the cast shadow in the plate, and they were there before. They are most visible in that frame.

## v6b: the gold girl's trouser edge beside the protagonist's sneaker

Jade, on `deliverables/wip/rewind_v6b_preview_540p_sfx.mp4`: "at 2:03, gold ghost's edge of pants (near protagonist Jade's sneaker) is opaque for a couple frames".

**Frames.** I rendered every frame from 122.958 to 125.292 at 960x540 and zoomed on the feet. At 123.417-124.875 (take frames 37-90), an opaque navy strip runs right of the protagonist's toe and down the left edge of the gold girl's trousers, from her belt to her knee. It is up to about 35 px wide in source pixels and is widest at 124.2-124.8, where it reads as a dark wedge beside the sneaker. On 123.417-123.5 it is the tail of the leg that the v6 polygons ended on (frame 39).

**Cause.** This is the same split fault as the leg. After frame 39, the live matte still held the edge of her trousers. Its boundary with the ghost matte runs inside her trousers rather than along their edge, so the `jade` layer drew that strip opaque. I had missed it in v6 because the two matte contours sat on top of each other in my checks.

**Fix (`e5feet.py`, step 1b; frames 36-92; nothing else in the shot touched).**
- Row by row, from the ghost body's left edge, the script walks left over dark (navy) live pixels. The walk stops at the white cover or at the protagonist's pale sneaker.
- Those pixels, and dark live pixels just inside the ghost matte, are moved from the live matte to the ghost matte.
- A row whose walk runs past 45 px is her own trousers or her toe's dark sole touching the strip. Those rows take the strip width interpolated from the nearest clean rows above and below (both within 40 rows), and only dark pixels move. This keeps the sneaker and her trousers opaque. A first version with no such guard put a gold sliver on her trousers at 123.625, and one with a hard cut-off left horizontal navy streaks; both were caught and fixed before this version.
- I also added a second trouser-hole box (frames 90-97). It fills the white bite out of the protagonist's thigh at 124.958-125.000, which was in the take's live matte from the start.

The ghost was rebaked with the same `ghostseq.py` arguments. `D.js` paths are unchanged (still `ghost_slideptb_v6` and `live_v6/matte.mp4`), so no regeneration was needed.

**Verification.** Every frame from 122.958 to 125.292 was compared, v6 against v6b. Changes are confined to 123.417-125.083 and to the hem/sneaker area. 123.000-123.375 and 125.125 onwards are identical. The navy strip is gone in every frame, and the sneaker and her trousers are intact. The small black marks under the toe are her sneaker's own sole and shadow, the same as before. Images:
- `.../e5/ba_hem.jpg`: v6 (top) against v6b (bottom), every 3rd frame 123.417-125.000, cropped on the feet
- `.../e5/toe_zoom2.jpg`: 3x zoom on the toe at 123.542, 123.833, 124.000, 124.208, 124.417, 124.625
- `.../e5/hem_all_before.jpg` / `hem_all_after.jpg`: every frame of the shot
- `.../e5/edge1.jpg` (raw take | live | ghost masks at frames 44 and 56, showing the strip in the live matte), `edge2.jpg` (the same after the fix), `fix_sheet4.jpg` (`--check` output)
