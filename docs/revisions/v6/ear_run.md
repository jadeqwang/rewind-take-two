# v6 — 1:42 "she seems to be running really slowly / making progress on the grass too slowly"

Shot: **B2_G3**, 102.46–104.22 (the earpiece close-up: the lead agent, two fingers to his earpiece, speaks; she is
small, far right on the lawn, heading for the Hilbert Hotel).

## Which shot this is

The brief pointed at `B2_ear` in `render/timeline/_B_verse2.js`. That block only runs when `V4_GUN = false`. Since v4,
`V4_GUN = true`, so the film uses `gunfireShots()` from `render/timeline/_B_gunfire.js`, and 102.46–104.22 is
**`g3()` → `B2_G3`**, with plate `media/shots/B_g3ear/take_1_engraved.mp4` (the v4 close-up of the two agents, not
`B_ear`). The fix is in `_B_gunfire.js` `g3()`. `_B_verse2.js` is untouched. The same applies to 100.70–102.46: the
live shot is `g2()` / `B2_G2` in `_B_gunfire.js`, not `B2_lawn2` in `_B_verse2.js`.

## Diagnosis

The camera is locked: phase correlation of the lawn and hotel against frame 4 stays within 0.1 px over the whole take.
The take is animated on twos. In the frames the shot uses (source 0.2–1.96, frames 5–46) she runs at a running
cadence: one step every 8 frames, which is **3 steps/s**. Each step is two planted drawings, one airborne drawing and
one landing drawing (C C F L). Her matte's height only goes from 334 to 290 px, though, and her feet only rise from
y 816 to 779. With the horizon at y 535 (h / (y_feet − 535) is constant across her plants), that is a depth change
of ×1.15: about **0.15 of her starting distance**, roughly 1.6 m in 1.76 s (~1 m/s, ~0.3 m per step). The legs say
"sprint" and the ground says "jog on the spot".

## Approach

1. **Matte of her + her shadow** (`media/shots/B_g3ear/take_1_jsmatte_v6/matte.mp4`, 156 KB). `take_1_matte/` is
   already her alone (no agents). Her hatched cast shadow (to the left of her feet) is added as a soft matte: local ink
   density above the clean lawn's, inside a box at her feet, keeping only the components that touch her. The shadow
   then travels with her.
2. **Clean lawn** (`media/shots/B_g3ear/clean_v6.png`, 0.9 MB RGBA patch, alpha only where she or her shadow ever is).
   It is the per-pixel median over the take's frames in which that pixel is uncovered; cv2 inpaint fills any pixel
   that is never uncovered. Because the camera is locked, one still works. No seam is visible at preview size.
3. **Re-composite** with the same plate, in 0.2, rate 1, through the new matte, `keepColor: true`. The agents' plate is
   unchanged and so is their timing. Moving a figure at depth Z to Z + d along a ground direction is, on screen, a
   uniform scale by r = Z / (Z + d) about that direction's vanishing point V. So one similarity transform per source
   frame does it (`anchor` = V, `scale` = r), and her feet stay on the ground plane by construction.
   V = (1900, 535). Her own drift in the take points at x ≈ 2000; I used 1900 so that she aims at the hotel's right
   half and goes right and up into depth.
4. **No skating:** d increases only on her airborne and landing frames, by a quarter step on each. It holds on the
   four planted frames of every step. Re-projecting the matte's lowest point through the transform, the planted foot
   stays at a fixed y (to the pixel) on all four planted frames of each step, and its x varies by ≤ 10 px at 1080p
   (≤ 5 px at preview size) as the drawn foot rolls. Plants, in 1080p px: (1512, 779) → (1549, 750) → (1592, 730) →
   (1619, 711) → (1655, 696).
5. Layer order: plate, clean patch, HILBERT HOTEL sign, then her. Her path (x 1430→1655, y 816→691) never reaches the
   agents (x < ~1200), so nothing occludes her and nothing needs to cover her.

## Travel and speed

- Extra depth: 0.118 × her starting distance per step, ~5.25 steps in the shot. Total depth goes from 1.00 to **1.78**
  (it was 1.15).
- On screen (1080p): her feet go from (1430, 816) to (1650, 691), which is **~220 px right and ~125 px up**. Her height
  goes from 334 px to **~192 px** (×0.57; it was ×0.87).
- In her own units: ~5 body heights in 1.76 s, so a step of about 1 body height at 3 steps/s. With H = 1.6 m and a
  ~40 mm-equivalent lens (f ≈ 2200 px, starting distance ≈ 10.5 m): **≈ 8 m in 1.76 s ≈ 4.6 m/s, ≈ 1.5 m per step**.
  That is a real run for her cadence; before, it was ~1 m/s.
- The step on screen shrinks from ~45 px to ~30 px as she recedes. The motion is on the airborne frames, which gives
  a light bounding rhythm, and the plants are pinned.

## Continuity

- Cut in (102.46): her first frame is unchanged (d = 0): far right, back to camera, same as before. G2 has her exiting
  frame right, so screen direction holds.
- Cut out (104.22): she now ends smaller, right of where she started, heading into the hotel's side. The next shot
  (B2_skip) has her side-on, running screen right, so the direction carries over.
- Everything else in the shot is unchanged: the agents, the "grass" lower third (an overlay in `_B_verse2.js`), the
  HUD and the HILBERT HOTEL sign.

## Files

- `render/timeline/_B_gunfire.js`: `g3()` only (clean patch layer + moving `jade` layer), plus one import.
- `render/timeline/_B_g3run.js` (new, generated): V and r per source frame.
- `tools/v4B/gunfire/g3_run.py` (new): builds the patch, the matte, `_B_g3run.js` and `media/shots/B_g3ear/run_v6.json`
  (per-frame z, d, r, planted). Run it with `tools/engrave/.venv/bin/python tools/v4B/gunfire/g3_run.py`. Tune
  `D_STEP` for speed and `VX` for heading.
- `media/shots/B_g3ear/clean_v6.png`, `media/shots/B_g3ear/take_1_jsmatte_v6/matte.mp4`, `media/shots/B_g3ear/run_v6.json`.

## Images (scratch: `/tmp/claude-1000/-home-jade-Documents-rewind-take-two/5c16a6f7-8726-4ff9-89a4-a5a70f33aa2b/scratchpad/ear/`)

- `before/preview_tile.jpg`: v6 preview 102.3–104.4, before.
- `before/gait_tile.jpg`: take frames 4–51 (gait / contacts).
- `check/clean_matte.jpg`: plate | her+shadow matte | clean patch, six frames.
- `after1/`: preview stills for every frame 102.29–104.38 (after).
- `after1_tile.jpg`: full frames, 102.33–104.25 (cut in, the shot, cut out).
- `after1_crop.jpg`, `after1_zoom.jpg`: crops on her (foot contacts, matte edge, shadow).
- `before_after.jpg`: before | after at 102.50 / 102.83 / 103.17 / 103.50 / 103.83 / 104.17.
