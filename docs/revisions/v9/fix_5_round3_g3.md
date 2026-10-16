# v9 fix #5, round 3: G3 "three legs" (2:26.32-2:28.08, f3512-f3553)

Jade, after round 2 (in 2.15, rate 1.12): "2:27 - 3 legs is still there".

## What was wrong
The take itself has a broken lower body for its whole length (`media/shots/G3/take_5_engraved_soft_patch.mp4`,
source frames 24-104 checked). Three things come out of one pair of hips:
1. a bent thigh going left, with a cargo pocket and an orange strap, whose shin comes back down to a sneaker,
2. a wide trouser leg sweeping down-left below it,
3. a second "thigh" at the right under the hip, with its own vertical orange strap.

Round 2 moved the in-point past the frames with three sneakers, but the three trouser legs are there in every frame.
A different in-point can't fix this.

## Choice: (a) reframe. No regeneration and no paint-out.
- (a) works. G3 becomes a medium close-up cut at the waistband. G1 is wide, G2 medium and G3 closer, so the push-in
  continues across the three shots. The stroke, the pencil, her drawing arm, face, headphones, chest dot and roundel are
  in frame in all 42 frames.
- I didn't do (b) (Seedance regen plus engrave, matte and roundel patch). It costs about $2-3, and a new take brings new
  stroke timing and new anatomy risk, all to fix a part of the body that the shot doesn't need.
- I didn't do (c) (paint-out). That means 42+ frames of hand-drawn trouser contours on a moving engraved figure, and it's
  the most likely of the three to look wrong.

### How the framing is set
- I measured the top of the navy trousers inside the matte for every source frame (`keys.py`). It descends steadily
  as Seedance's camera pushes in: about 560 px at source frame 31 and 714 px at source frame 99, roughly 2.3 px per frame.
- I fitted a line under that, so the line never sits below the measured top, and added 10 source px so a sliver of
  the black belt still shows. The frame bottom follows that line. At most about 10 source px (about 15 screen px) of
  waistband is ever on screen, and no thigh.
- Scale eases from 1.55 to 1.40 over the shot. At 1.55 her head isn't too low at the cut. At 1.40 the finished stroke
  and the pencil tip are well inside the frame at the end (the tip is about 80 px above the bottom edge at f3553).
  This is a mild pull-out against Seedance's push-in. She drifts upward about 150 px over 1.76 s, which reads as
  weightless float.
- **Timing back to v8: in 1.3, rate 1.6.** Round 2 changed the in-point only to get past the sneakers, and the crop now
  hides them. At 1.3 the stroke starts at the cut and is about 85% drawn at the out point (source 4.12 s, the same as
  v8 and round 2). With in 2.15 the stroke was already about a third drawn at the cut.
  If you'd rather keep 2.15/1.12, the matching keys are:
  `scale: [[0,1.5],[0.44,1.475],[0.88,1.45],[1.32,1.425],[1.76,1.4]], y: [[0,452.4],[0.44,414.8],[0.88,378.5],[1.32,343.5],[1.76,309.9]]`
  These were computed but not frame-stepped.

## The timeline change (E.js `G_CLIPS.G3`, for the lead to apply)
```js
  // v9 round 3 (Jade "2:27 - 3 legs is still there"): the take's lower body has three trouser legs in every frame, so G3
  // is reframed to a medium close-up whose bottom edge tracks her waistband (scale 1.55 -> 1.4, y keyed to the measured
  // trouser top + 10 src px); timing back to v8 (in 1.3, rate 1.6: the stroke starts at the cut, ~85% drawn at the out).
  // Round 2 was in 2.15, rate 1.12, no reframe. docs/revisions/v9/fix_5_round3_g3.md
  G3: { src: 'media/shots/G3/take_5_engraved_soft_patch.mp4', matte: 'media/shots/G3/take_5_matte/matte_dilated9.mp4', in: 1.3, rate: 1.6,
    scale: [[0, 1.55], [0.44, 1.5125], [0.88, 1.475], [1.32, 1.4375], [1.76, 1.4]],
    y: [[0, 525.2], [0.44, 466.6], [0.88, 411.0], [1.32, 358.4], [1.76, 308.6]] },
```
`gShot()` passes `c.y` and `c.scale` straight to the video layer. The engine's `placement()` evaluates them with
`val(..., lt)`, so `[[t, v], ...]` keyframes on the layer clock work as they are. The matte uses the same placement.
Keys are in shot-local seconds. y is in design px, positive is down. Scale is about the frame centre.

Optional, and it touches the `gShot('G3', ...)` call, not `G_CLIPS`: the drift-line colour bloom was centred on the old
stroke position (`bloomX: 640, bloomY: 400`). With the new framing the stroke's centre is at about **(580, 640)** at
the bloom time (146.85) and still there at the end. So `bloomX: 580, bloomY: 640` keeps the bloom on the stroke. If it
is left alone, the bloom starts about 240 px above the stroke.

## Verification
- I simulated the layer exactly as the engine places it (fit cover, scale about the centre, y offset, luma matte from
  `matte_dilated9`, floor frame pick), over flat paper without drift lines, for all 42 frames f3512-f3553. Simulator:
  `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/fdedb5e1-e35f-4469-b1dc-21deb2924ae1/scratchpad/g3/sim.py`.
  Key fitter:
  `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/fdedb5e1-e35f-4469-b1dc-21deb2924ae1/scratchpad/g3/keys.py`.
  I didn't run render.mjs.
- I checked the bottom 200 px of every frame at full 1080p, one frame at a time. Every frame shows midriff, jacket
  hem, roundel and hair, plus at most a thin strip of black belt. There is no trouser leg, thigh or shoe in any frame.
- Every frame has the stroke, the pencil (pale-blue eraser), her drawing hand and arm, face, orange headphones, pale-blue
  dot on her left chest and the "1420 MHz" roundel on her left sleeve. The stroke grows from a short orange start at
  the cut to the full orange-yellow-green-blue-violet C at f3553.
- Evidence, next to this report:
  - `fix_5_round3_g3_before_after.jpg`: f3512, f3533 and f3553. Before is the current 540p preview; after is the simulation.
  - `fix_5_round3_g3_after_all42.jpg`: every frame of the new G3.
  - `fix_5_round3_g3_after_bottom_fullres.jpg`: the bottom strip of all 42 frames at 1080p, for the leg check.

## Still imperfect
- Upscaling 1.4-1.55x makes the linework a little softer than in G1/G2. That's fine at preview size. At 1080p the
  outlines are slightly thicker and softer, but not blurry.
- At the cut, the top third of the frame is empty paper; in the film the drift lines fill it. Check this in the
  integrated preview.
- The belt sliver at the bottom edge is meant to show. It reads as a waistband.
- G3 now opens on a closer framing than G2 ends on (G2's last frame shows her to mid-thigh). That's a normal push-in
  cut, but check it in the integrated preview.

## Spend
$0.00. No paid calls; spend is unchanged at $261.56 per `tools/gen/spend.py`.
