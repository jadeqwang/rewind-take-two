# v9 fix 1a + 9: the stop at the lakefront (P1 / P2 / P1b, 0:37.96-0:40.24)

Status: done, ready for the lead's integrated preview (not rendered through render.mjs).

## What was wrong
- **Reference geography (D6-D8, 0:32.36-0:37.96).** D7 (`media/shots/D7/kf_v3_2.jpg`, master f840) is the agent's
  view through her open driver's window: the car's nose is screen LEFT, she is in the left (driver's) seat with the
  wheel in front of her. D6 and D8 look out of that same window: the agent stands at her door with the lake behind him.
  So the agent and the lake are on the car's driver's side.
- **P2 (0:38.90-0:39.68, `media/shots/P2/take_2_engraved_eraser.mp4`, f943).** Close-up of her facing the camera: the
  wheel sits at lower frame-left with an empty gap between it and her, so she reads as the passenger and nobody is
  driving. The cabin is not D7's cabin from D7's side.
- **P1 / P1b (0:37.96-0:38.90 and 0:39.68-0:40.24, `media/shots/P1/take_2_engraved.mp4`, f920/f960).** We see the
  Acura's rear and its RIGHT (passenger) side; its nose points screen-right and away, the opposite of D7. The cabin is
  empty (two bare headrests). The agent is on the passenger side with the lake beyond the car, the opposite of D6/D8.
- **C2 flash (f154-156).** C2 is a `comp` of the finished film (`source: 'film'`, `render/timeline/B.js`). Its source
  times at f154/155/156 are 39.593 / 39.655 / 38.988 s, all inside P2 (f153 = 40.26 is P4; P1b and P1 are not hit).
  It picks up a new P2 plate automatically: no separate change.

Evidence (before): `fix_1a_9/before.jpg` (D7 f840 reference, P1 f920, P2 f943, P1b f960).

## What I made
Seedance 2.0 cannot take reference images together with a first frame (catalog schema: `reference_images` "cannot be
used with ... first/last frame images"), so the 0:35 context goes in through the keyframe: every new keyframe is a
nano-banana-pro call with D7's own keyframe `media/shots/D7/kf_v3_2.jpg` (the image the 0:35 frame is drawn from,
without the letterbox and dialogue box) as a reference, plus the current P1 / P2 keyframe.

- Script: `tools/v9/car_kf.py` (keyframes, tags `v9_1a_kf_*`, `v9_9_kf_*`; prompts and refs logged to
  `media/shots/P1|P2/kf_log_v9.jsonl`), `tools/v9/car_vid.py` (Seedance takes, tags `v9_1a_P2`, `v9_9_P1`).
- **P2 keyframe** `media/shots/P2/kf_v9d.png`: refs D7 kf, old P2 kf, bun sheet. The same side of the car and camera
  direction as D7 (agent at her open driver's window), nose screen left, she is in the driver's seat with the wheel
  right in front of her (left hand on the rim, right hand on the sill), two crossed pencils (pink + pale-blue
  erasers), orange headphones, dot and 1420 MHz roundel on her LEFT. Made in three steps: `kf_v9a.png` (staging),
  `kf_v9c.jpg` = nano-banana edit of a (shocked face like the old P2; water beyond the passenger windows replaced by
  park, since the lake is on the driver's side), `kf_v9d.png` = c with the green/blue pixels outside Jade desaturated
  (the edit had painted the park in colour; pixel pass `tools/v9/p2_kf_desat.py`, erasers and chest dot excluded).
  `kf_v9b.png` (rejected: one pencil reads as a stub).
- **P1 keyframe** `media/shots/P1/kf_v9a.jpg`: refs old P1 kf (`kf_nbp2.jpg`), D7 kf, bun sheet. The agent unchanged
  (same pose, hand into the jacket, right half of frame), now standing at the Acura's driver's door with his back to
  it; the car is seen from its driver's side, nose screen LEFT (as D7), Jade in the driver's seat behind the wheel,
  visible through the open window just left of his shoulder. The lake is behind the camera (agent and lake on the
  driver's side, as D6/D8); beyond the car: Lake Shore Drive, lamp posts, trees, the skyline. `kf_v9b.jpg` (rejected:
  near-identical, a stray mark in the bottom-right corner).
- **Takes** (Seedance 2.0, 720p, 4 s, first-frame-locked, static camera; 2 per shot):
  - P2: `media/shots/P2/take_v9_1.mp4` (**chosen**: her mouth opens wider, shoulders tense, hands tighten; she stays
    in the driver's seat behind the wheel throughout) and `take_v9_2.mp4` (calmer). Prompts in `tools/v9/car_vid.py`.
  - P1: `media/shots/P1/take_v9_2.mp4` (**chosen**: his right hand goes inside the jacket by ~1.5 s and stays there
    through P1b's range 2.02-2.58; a pistol comes out after ~3.2 s, unused) and `take_v9_1.mp4` (hands stay at the
    lapel). Jade stays in the driver's seat, hands on the wheel, in both.
  - Engraved with `tools/sectionA/engrave_take.sh P2 v9_1` / `P1 v9_2` → `take_v9_N_engraved.mp4` + `take_v9_N_matte/`.
- **P1 matte.** The engrave matte (BiRefNet on the whole frame) lost Jade in every frame of `take_v9_2` (she is
  small in the window), so she came out engraved grey. `tools/v9/p1_matte.py` runs BiRefNet on a crop of the driver's
  window only, limits it to that window (no agent, no steering column) and merges it into the engrave matte →
  `media/shots/P1/take_v9_2_matte_jade/`; then `engrave.py take_v9_2.mp4 take_v9_2_engraved_jade.mp4 --out-height 1080
  --matte-in .../%05d.png` → **`media/shots/P1/take_v9_2_engraved_jade.mp4`** (Jade in colour, stable: chroma in her
  region 17.8-18.1 across frames 0-70). `take_v9_2_engraved.mp4` is the plain engrave (grey Jade): don't use it.
- **P2 plate:** **`media/shots/P2/take_v9_1_engraved.mp4`** (plain engrave; both erasers stay in colour, pink and
  pale blue, every frame: no `matte_fix` pass needed this time).
- Checking: `tools/v9/car_preview.py` emulates the engine for one video layer (cover fit, in/rate, kenBurns, 2.39
  letterbox); checked against the shipped P2 (matches master f943's framing). Stills at 640 px only.

Evidence (after): `fix_1a_9/after.jpg` (D7 f840 reference; P1, P2, P1b from the new plates through the emulated
framing and letterbox).

## Exact timeline change (`render/timeline/A.js`, not edited by me)
In `PLATE`:
```js
  P1: { src: S('P1', 'take_v9_2_engraved_jade.mp4'), in: 0.3, rate: 1 },   // v9 (Jade 0:38, #9): re-staged to agree with D7: the agent at her driver's door, nose screen left, Jade in the driver's seat (in colour: tools/v9/p1_matte.py). v8: take_2_engraved.mp4
  P2: { src: S('P2', 'take_v9_1_engraved.mp4'), in: 0.3, rate: 1 },   // v9 (Jade 0:39, #1a): D7's angle (agent at her open driver's window), she is behind the wheel. tools/v9/car_kf.py, car_vid.py. v8: take_2_engraved_eraser.mp4
```
In the P2 shot (38.9-39.68), replace the kenBurns (the new plate is wider than the old close-up; this keeps both
erasers and both hands inside the 2.39 band and pushes in toward her face):
```js
      layers: [vid('P2', { kenBurns: { from: { scale: 1.0, y: 60 }, to: { scale: 1.1, y: 100 } } })], fx: [LETTERBOX] },
```
P1 (37.96-38.9) and P1b (39.68-40.24): no change beyond the `PLATE.P1` src. P1b keeps `in: 0.3 + (39.68 - 37.96)` and
its push (1.3 → 1.6 on his hand); Jade stays in the window at the left of frame for the whole push.
C2 (`render/timeline/B.js`): no change. Its f154-156 flashes replay film time 38.99-39.66 (P2) from the film comp, so
they show the new P2 once A.js changes. KF (`USE_STILLS`) entries can stay; optionally `P1: 'kf_v9a.jpg', P2: 'kf_v9d.png'`.

## Spend
$3.07 of the $15 cap: 5 nano-banana-pro keyframes ($0.67, tags `v9_1a_kf_a|b|c`, `v9_9_kf_a|b`) and 4 Seedance 2.0
720p 4 s takes ($2.40, tags `v9_1a_P2`, `v9_9_P1`). Project total after: $260.78 (includes other agents' spend).

## Still imperfect
- **P2 is no longer a tight close-up.** It is a medium shot from D7's position (the wheel, both hands and her face
  in frame), pushed 1.0 → 1.1. That was the price of a readable wheel-in-front-of-her; it rhymes with D7 3 s earlier.
  A tighter push (≥ 1.2) starts cutting the erasers or the hands and softens the 720p source.
- **P1/P1b: her hand on the wheel is engraved, not in colour**, in some frames (the matte stops just below her wrist so
  that the steering column stays out of it). Visible only when pausing on P1b's first frames, where the hand is at the
  left edge.
- **The lake is not in P1 any more.** To put the agent and the lake on the driver's side (as D6/D8), the camera
  now looks inland across the car: Lake Shore Drive, lamp posts, trees and the skyline behind. The old P1's waves
  are gone.
- P1's agent is a new drawing of the same man (same pose and size); a pistol comes out of the jacket after 3.2 s of
  the take, outside the used ranges (P1 uses 0.3-1.24 s, P1b 2.02-2.58 s).
- P2's passenger-side windows show a parkland (grey-washed by `tools/v9/p2_kf_desat.py` before the engrave pass);
  it engraves fine but a little flatter than the rest of the night.
