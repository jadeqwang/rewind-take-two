# v9 fix 1b: C10_V2b3 passenger-seat staging (1:06.28-1:07.16)

Status: done, pending the lead's integrated preview render.

## What was wrong
- Source: `render/timeline/C.js` CUTS row `[66.28, 67.16, 'V2b3', 1, 0.0, 1]` (not `_B_gunfire.js`/`_B_verse2.js`),
  plate `media/shots/V2b3/take_1_engraved.mp4` (colour Jade is baked into the engraved plate; C.js adds no matte layer
  for this row).
- The keyframe `media/shots/V2b3/kf_n.jpg` already has the error: wheel on the left, Jade in the right seat reaching
  across with her left arm. The section C JADE prompt block asked for "a yellow wooden pencil" (singular), hence one
  pencil; no headphones drawn.
- C2 (`render/timeline/B.js`) is a `comp` of the finished film (`source: 'film'`); its f145 flash plays film time
  ~66.9 s backward at x8, i.e. V2b3 local ~0.58-0.64 s. It picks up the new plate automatically: no separate change.

## What I made
- Keyframe script `tools/v9/v2b3_kf.py` (nano-banana-pro; refs = the C_V2f_car wide `media/shots/V2f3/kf_wide_b_fix_engraved.png`
  for the LHD staging and Acura interior, the canon turnaround, the two-pencil bun sheet). Tags `v9_1b_kf_<v>`.
  - `kf_v9a.png`: staging right, pencils not a clean X, back dot split in two.
  - `kf_v9b.png`: clean X, but off-model western-cartoon face and she drifts toward the middle. Rejected.
  - `kf_v9c.png` (chosen): left seat behind the Acura wheel, passenger seat empty, two crossed pencils (pink + blue
    erasers), orange headphones round her neck, one back dot, the upside-down sedan outside the windshield.
- Video: Seedance 2.0 720p 4 s from `kf_v9c` via `tools/sectionC/vid.py` (`C_TAG_PREFIX=v9_1b_`):
  take_2 = sedan flies up over the roof (roof hides it); take_3 = sedan tumbles left-to-right outside the glass.
  - take_3 rejected: the sedan rights itself and turns into a white car mid-air.
  - take_2 chosen: the sedan tumbles toward the windshield, its underside fills the glass, and it goes up over the
    roof. The headliner, the A-pillars and the side-window frames stay in front of it in every frame. She ducks
    behind the wheel at about src f22-27 and stays down.
- Matte: the engrave tool's own BiRefNet matte took in the whole cabin for f0-f21 (so the cabin stayed un-engraved and
  then popped to engraving at f22: the same "matte pop" as take 1). Running it backward in time didn't help.
  `tools/v9/v2b3_matte.py` builds the matte itself: BiRefNet on a crop of her side of the frame for f0-21, full frame
  from f22, minus a fixed polygon for the driver's seatback/headrest, which sits in front of her and which both passes
  included. Then the engrave colour cue, a 3-tap temporal median and the engrave feather. The result is
  `media/shots/V2b3/take_2_matte/` (PNGs + matte.mp4). I checked overlays every 3-6 frames: tight on Jade, pencils
  inside the matte, no cabin or seat.
- Plate: `media/shots/V2b3/take_2_engraved.mp4` = `tools/engrave/engrave.py take_2.mp4 ... --out-height 1080
  --matte-in take_2_matte/matte.mp4` (defaults otherwise). The first auto-matte engrave and the reversed-run tests
  are in `media/shots/V2b3/v9_work/` (scratch; safe to delete).
- Preview (640x360, v8 V2b2 tail + new V2b3 + v8 V2b4 head): `media/shots/V2b3/v9_work/preview_cut_in045_rate15.mp4`.
- Evidence: `docs/revisions/v9/fix_1b_v2b3_before_after.jpg` (top: v8 f1593/f1600/f1608 + the C2 flash f145; bottom:
  the new plate at the same timeline frames).

## Look and continuity checks
- She's in the left seat with the Acura wheel (logo on the hub) in front of her and the passenger seat empty. The
  interior and the over-the-shoulder angle match C_V2f_car (1:29).
- The world is a dark night engraving like V2b2/V2b4 and C_V2f_car. v8's V2b3 was a pale paper interior, the odd one out.
- Canon: two crossed pencils (pink + blue erasers), orange headphones round her neck (visible while upright, hidden by
  her arms once she ducks), one pale-blue dot on the back panel, orange bands on the sleeves only. The left-sleeve
  roundel and chest dot face away from camera.
- No matte pop: Jade is in colour from frame 0. No white cut-out blobs. The sedan never comes inside the cabin.
- C2 at f145 replays the finished film (`source: 'film'`, B.js), sampling about 66.86-66.92 s. With the new in/rate
  that's source f32-34: ducked, with the sedan's underside filling the windshield. It updates on its own: no change
  to B.js.

## Spend
$1.60 against the $12 cap: 3 keyframes (`v9_1b_kf_a/b/c`, $0.134 each) and 2 Seedance takes (`v9_1b_V2b3`, $0.60 each).
Project total was $260.78 after this (other agents spent in parallel; $252.72 at the start of the round).

## Exact timeline change (`render/timeline/C.js`, CUTS)
```diff
-  [66.28, 67.16, 'V2b3', 1, 0.0, 1],
+  [66.28, 67.16, 'V2b3', 2, 0.45, 1.5],   // v9 1b: re-staged in the driver's seat (take_2, hand-built matte)
```
`plate()` resolves this to `media/shots/V2b3/take_2_engraved.mp4` (a new path, so the engine cache doesn't apply).
Nothing else changes: same start, end and duration. The window plays source 0.45-1.77 s (f11-f42): the sedan
tumbling in, filling the windshield, going over; she flinches and ducks; the road clears. The rate is 1.5, in line
with the neighbouring V2b cuts (1.2-1.6). The original was rate 1 from 0.0. For a slower, calmer read, use
`2, 0.6, 1.2` (src f14-f40).

## What still looks wrong
- Eraser colour flicker: in source f20-24 (the first frames of the duck) the generator draws the erasers grey-white,
  and one engraves as a small white blob against a streetlight burst at f22. That's about 2 timeline frames and
  roughly 20 px at 1080p. If Jade spots it, `tools/blue_eraser.py`/`tools/matte_fix.py` can recolour it.
- Once she ducks, the X reads more as a "+" (one pencil horizontal across the bun, one upright). There are still two.
- Her driver's headrest sits a little to her left instead of squarely behind her head (in the keyframe). From this
  angle it reads as her seat, but it's not quite right.
- As the sedan clears (src f37-42) its trailing edge smears into long white diagonal bars across the windshield and
  right side window. At 1.5x they read as speed lines, but they're the video model's motion smear.
- Direction: in V2b2 the sedan arcs over the car from the left/behind. Here it comes over front-to-back, as in the
  v8 take. That's a continuity cheat, unchanged from v8.
- I haven't checked this in the full engine (HUD over it, grain, punch fx). The HUD is paper-coloured, and the new
  top-right corner is dark headliner, so it should read like it does on V2b1/V2b2.
