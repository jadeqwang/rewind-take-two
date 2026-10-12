# v5-stairs: the rooftop staircase becomes an impossible (Penrose) staircase (Jade 0:13 & 2:35)

Cap $6, tag `v5_stairs_`. Spend at start: $243.44.

## Findings

- The "rooftop staircase" is the square stairwell (steps round a square hatch) on the near rooftop at lower left of the
  Bean's reflection: plate_close_1 px L (137,1242) T (215,1122) R (362,1187) B (290,1310); take px ~(30..200, 780..930).
  At 0:13 it shows mid-frame left in the wide Bean; at 2:35 lower left of her. It is the one object in both shots.
- The plate is **baked into both sing takes** (`media/sing/S1/v4_sync_1080_open.mp4`, `media/sing/V3S/v4_sync_1080.mp4`);
  the S1 wide part (12.60–14.00) is pre-rendered frames `media/shots/S1_wide/bg_1080/` from `plate_wide_v4_bean.png`.
- Both takes' backgrounds are static (best shift 0,0 across the take) and her matte never goes left of x 474, so a
  still overlay on the take works and her hair edge is untouched (no re-matting needed).
- Take fit to the close plate on the rooftop (blurred correlation 0.98): S1 s 0.731, (-67.5, -42.5); V3S s 0.734, (-68, -46).

## Done

- `tools/v5/stairs/penrose.py`: the stair as a real 3-D object (z-buffer, orthographic), the four flights climbing
  all the way round; the loop's footprint is left open by exactly the total climb along the camera's view axis, so the
  picture closes (true Penrose construction). Camera: the roof's azimuth and roll, lowered from the roof's 55 deg to
  46 deg (at 55 deg the risers are too foreshortened to read). Engraved masonry hatching per face.
  Picked guide **g15**: `--el=46 --size=0.97 --ring=0.30 --rise=0.05 --base=0.04 --ox=64 --oy=52 --steps=6,5,6,5`.
- `tools/v5/stairs/comp.py`: new close plate `media/sing/plates/plate_close_1_stairs.png`; overlays
  `media/sing/plates/stairs_v5/overlay_{S1,V3S}.png` (tone matched per take); new wide Bean plane
  `media/sing/plates/plate_wide_v4_stairs_bean.png` and pushed frames `media/shots/S1_wide/bg_1080_stairs/`.
- AI candidates (nano-banana-pro 2K, `tools/v5/stairs/gen.py`, json beside each): A1 (text only; drew an ordinary,
  possible stair: up one side, down the other), B1–B3 (restyle of the drawn guide; all "fixed" the seam, so the loop
  stopped being impossible). **Not used**; the drawn stair is used as is.

- Picked drawing is **g16** (= `P` defaults in penrose.py; lit walls lighter than g15 so the wall separates from the
  roof hatch at 540p). Notes on every file: `media/sing/plates/stairs_v5.md`.
- Timeline: `render/timeline/A.js` S1: `S1_wide` src -> `media/shots/S1_wide/bg_1080_stairs/`, new `S1_stairs` image
  layer over `S1_take` (same `BEAN.bean` transform and `BEAN.takeIn` fade). `render/timeline/E.js`: `v3s()` adds a
  `stairs` image layer over the take (V3S and V3S_b).
- Rendered and checked frame by frame: `media/reviews/v5/0013_stairs.mp4` (12.60–16.14),
  `media/reviews/v5/0235_stairs.mp4` (153.98–159.14). The wide plane's stair hands over to the take's without a jump;
  static, no flicker; her matte/hair edge untouched; at 1.04 push the loop's left corner just touches the frame edge.
- Hand-over fragment: `docs/revisions/v5/fragments/stairs.json`. Spend: $0.67 (5 nano-banana-pro calls, none used).

## Running

Nothing.

## Next

Jade's review. Open questions in the fragment (viewing angle; the V3S ramp mid-left is unchanged).

## Decisions

- Drawn procedurally, not by a model: every model pass made the loop possible again.
- The overlay sits only over the take (her matte and the take's in-point/framing untouched).

## Round 2 (v5-stairs2, cap $3, tag `v5_stairs2_`): the 3:13 clock stair, copied

Jade: "staircase looks bad, because it's not an actual impossible staircase. can you just copy the one from later in
the same video? the one inside the clock at 3:13?"

### Done

- **Lifted, not redrawn.** `tools/v5/stairs2/lift.py` rasterises the engine's exact block faces
  (`tools/sectionF/penrose_guide.py`: 22 steps, flights 7 / landing / 2 / landing / 2 / landing / 7 / landing, magic
  angle) on the F6b plate `media/shots/F6b/kf_v3_F6b_redraw_crop_dered.png` (the 3:13 plate; the agents are a separate
  sprite layer, so the plate's stair is clean). That polygon union (+2 px for the outline ink) is the cut-out mask:
  watch face, ticks and agents excluded. Plate box of the blocks: (836, 405)–(1564, 825).
- **Toned into the Bean's engraving** (`tools/v5/stairs2/comp.py`, free, deterministic, no model): luminance only, mapped
  onto the Bean's paper (250,241,230) and ink (8,5,2); tops stay paper; walls keep the plate's own vertical hand
  hatching and its face tones (light from the left, as at 3:13), contrast raised; outline lines thickened by 1 px. No
  colour, no red. The plate's own hatched cast shadow (under the near flights and inside the well) is multiplied onto the
  roof; the clock ticks inside that region are removed (morphological opening).
- **Same shape, step count and viewing angle:** uniform scale only (0.446), no rotation or shear. Checked by drawing the
  22 exact tread outlines over the result: every tread lands on its block, the loop closes at step 21 → 0
  (`media/sing/plates/stairs_v5/clock_geometry_check.png`).
- **Old square stairwell removed** under and round it: every hole pixel is the roof's hatch line through it, interpolated
  between the hole's two edges along a per-pixel searched (then smoothed) line direction, slope 0.29–0.58. Hole =
  the stairwell with its drawn base, widened, +28 px.
- **Placement** on the close plate: blocks centred (302, 1218), 325 px wide (stair box 138..466 × 1122..1313). The roof
  is tight here: its right parapet leans left going down, and the S1 take's slow 1.04 push (about the frame centre)
  eats ~19 px of the left edge by 16.14; 325 px is the largest that keeps the whole loop on the roof and in frame for the
  whole shot (380 px clipped the left corner block at the end of S1 and touched the parapet). At 540p the loop is ~120 px
  wide, each block ~10 px.
- Files (round-1 files untouched): `media/sing/plates/plate_close_1_stairs_clock.png`;
  `media/sing/plates/stairs_v5/overlay_S1_clock.png`, `overlay_V3S_clock.png` (same take fits and per-channel tone match
  as round 1); `media/sing/plates/plate_wide_v4_stairs_clock_bean.png` and `media/shots/S1_wide/bg_1080_stairs_clock/`
  (bg.py push); checks `stairs_v5/clock_check_{S1,V3S}_{1080.jpg,540.png}`, `clock_lift.png`, `clock_mask_close.png`.
- Timeline: `render/timeline/A.js` `S1_wide` → `bg_1080_stairs_clock/`, `S1_stairs` → `overlay_S1_clock.png`;
  `render/timeline/E.js` `V3S_STAIRS` → `overlay_V3S_clock.png`. Round-1 paths are in the comments.
- Clips (540p, sfx mix audio): `media/reviews/v5/0013_stairs_clock.mp4` (12.60–16.14),
  `media/reviews/v5/0235_stairs_clock.mp4` (153.98–159.14). Checked frame by frame: the wide → take hand-over shows one
  stair (no doubling), the loop stays whole in frame through the S1 push, no seams round the patch at 540p, static in
  V3S/V3S_b (inter-frame change 0.1–0.3 grey levels).
- Spend: $0 (no model calls).

### Rebuild (free)

    PY=~/Documents/moongazing/.venv/bin/python
    $PY tools/v5/stairs2/comp.py --wide      # placement override: ST_CX, ST_CY, ST_W; wall levels ST_CURVE

### Notes / open

- The stair keeps the 3:13 viewing angle (isometric, ~35° elevation), which is lower than the roof's own (~55°), so
  it reads as a solid object standing on the roof and seen a little more from the side than the roof is. Jade asked for
  the same angle; say if it should be squashed to the roof's angle (that would no longer be the identical picture).
- Its wall shading follows the 3:13 plate (light from the left); the roof is lit from the right. Not noticeable at 540p.
- Mis-step during this round: `render.mjs --help` is not a flag and started a whole-film 1080p render; it was stopped
  after ~36 s and its 864 frames deleted from `render/engine/out/rewind/full/frames/` (the engine cache
  `media/engine_cache/full/` got the prepared `bg_1080_stairs_clock` and the F7m sources, which are valid caches).
