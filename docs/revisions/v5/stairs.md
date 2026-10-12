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
