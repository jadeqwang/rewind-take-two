# v9 fix #2 (D3) + #3 (C_V2f_car): one real rear-view mirror, one car interior

Status: DONE, not yet seen in an engine render (the brief forbids render.mjs here; checked on my own clips and a
Python stand-in of the car shot). Agent cap $15; spent **$2.54** (10 nano-banana-pro edits `v9_mirrors_*` = $1.34;
2 Seedance 2.0 720p takes, tag `v9_d3` = $1.20). Project total after: $260.78 (other v9 agents included).

## What was wrong (checked by eye on the v8 master, f612/640/680, f2150/2185/2192/2196/2210/2225)
- D3 (0:25.34-0:28.40): camera at the dash looking back at her; the driver's door mirror fills the right half with its
  glass face-on to the lens (it should show the back of its housing), showing the TVA 1729 sedan.
- C_V2f_car (1:29.29-1:31.46): wide over her right shoulder has no roof: no headliner, no windscreen header, no stem,
  no right A-pillar; the mirror floats in the night among the overpass girders and the SIRENS gantry hangs ABOVE where
  the roof should be. At f2196 the close still fades in with a headliner, visors and a stem: two different cars.

## Plan
- V2f: keep the Seedance take (her breathing / glance that Jade asked for in v4c). Add the roof as a static engraved
  overlay cut from a nano-banana edit of the wide still (headliner, header, visor, mount + stem, right A-pillar),
  with the header placed where the close still's header lands (y~334 design px), so the push travels under the roof
  into the close still's own headliner. The SIRENS gantry moves below the header, seen through the windscreen.
- D3: re-stage as an over-the-shoulder close in the same interior (refs: the fixed V2f wide and the close mirror),
  her eye glancing up into the interior mirror on its stem; the unlit sedan in the glass through the rear window.

## Progress log
- V2f roof edit: `tools/v9/mirrors/v2f_roof_guide.py` (grey placeholders on the raw wide) -> nano-banana edits
  `media/shots/V2f3/v9_roof_a|b.png` (`tools/v9/mirrors/gen.py`, tags `v9_mirrors_v2f_roof_a|b`). **a chosen** (b
  greyed her headphones and redrew the passenger seat). Engraved: `v9_roof_a_engraved.png`. Registration vs the
  original wide: within 1-4 px.
- Cut-outs (`tools/v9/mirrors/v2f_cutouts.py`, free): `media/shots/V2f3/v9_roof.png`, `v9_gantry.png`; choked Jade
  matte `media/shots/V2f3/take_1_matte_v9/matte.mp4` (4x erosion; the old soft edge ringed her bun with the take's sky).
- New module `tools/v4B/car/car_shot_v9.js` (car_shot.js + roof layer, gantry below the header, new SIGN_Q, choked matte).
- Preview without the engine: `tools/v9/mirrors/mock_car.py` (Python re-implementation of the picture layers;
  checked against the v8 master at f2150/2185/2192/2196: same framing).
- D3 keyframes: free-text a/b rejected (a: headphones on her head and the sedan ahead through the windshield; b:
  mirror-in-mirror). Layout guide `tools/v9/mirrors/d3_guide.py` (the roof-fixed wide, camera moved in behind her
  right ear) -> c/d; d kept, its mirror showed the sedan between the rear seats (inside the cabin) -> mirror edits e/f
  (f came back corrupt), g/h (g/h redrew the whole frame: rejected). Final `media/shots/D3/kf_v9.png` =
  `tools/v9/mirrors/d3_kf_fix.py`: e (correct optics: rear seats, parcel shelf, rear window) + d's sedan laid into
  e's rear window so its plate shows above the shelf.
- D3 Seedance 2.0 720p 4 s, 2 takes (`gen.py vid v9_d3`, $1.20).

## Result

### #3 C_V2f_car (1:29.26-1:32.79): the same take, now under a roof
- `tools/v4B/car/car_shot_v9.js` = car_shot.js plus:
  - `media/shots/V2f3/v9_roof.png`: roof liner, both sun visors, the windshield header, the mirror's mount and a short
    stem down to the mirror, the right A-pillar and the passenger-side glass. Its header sits at y~321 (design px) in
    the wide, which is where the close still's own header lands under the push, so the camera now travels under one
    continuous roof into the close still's headliner and stem (91.40 / 91.75 in the after sheet). Behind her head the
    roof liner is filled from its own texture, so her moving bun never shows a second copy or a halo.
  - The SIRENS gantry is now seen through the windshield, below the header (`v9_gantry.png`, sign quad
    `[660,352 .. 990,446]`); it grows about the road's vanishing point and climbs behind the header as it nears.
    SIRENS is ~330 px wide on screen at 90.19 (v8: ~414 px).
  - Jade comes back through `media/shots/V2f3/take_1_matte_v9/matte.mp4` (the take's matte eroded ~4 px), drawn
    over the roof.
- Evidence: `fix_3_v2f_before.jpg` (v8 layering) / `fix_3_v2f_after.jpg` (v9), both from `tools/v9/mirrors/mock_car.py`
  at 89.40 90.19 90.80 / 91.40 91.75 92.20. The v8 mock matches the master frames f2150/f2185/f2192/f2196.
- Driving staging is unchanged (LHD, she's on the left, both hands on the wheel).

### #2 D3 (0:25.34-0:28.40): over her right shoulder into the interior mirror
- Camera on the back seat close behind her right ear, in the same car (built from the roof-fixed 1:30 wide):
  roof liner, visors, and the interior mirror hanging on its stem from the header at the top centre of the
  windshield; Lake Shore Drive ahead (streetlights, the lake wall); she's in the left seat, hands on the wheel in
  front of her. In the glass, correctly for a rear-view mirror: her own car's rear seats, headrests, parcel shelf and
  rear window, and through it the black sedan following close, plate above the shelf. Two crossed pencils (pink + pale-blue erasers, in colour every frame) and orange headphones round her neck.
- Files: keyframe `media/shots/D3/kf_v9.png`; take `v9_take_2.mp4` (Seedance; take 1 is an equal spare) ->
  `v9_take_2_engraved.mp4` (+ `v9_take_2_matte/`) -> **`v9_take_2_push.mp4`** (`tools/v9/mirrors/d3_push.py`: a
  baked push toward the mirror, 1.0 -> 1.38 over the 3.06 s, eased; the picture sits 70 px lower so the 2.39
  letterbox shows the roof liner, visors and stem mount above the mirror; it echoes the 1:30 push into the same mirror).
- Plate: tracked on the push clip (`media/shots/D3/track_plate_v9.json`); the etch quad (left half of the rear
  window in the glass, left of the sedan) follows the push exactly. Both are in `tools/v9/mirrors/d3_tracks.js`
  (from `d3_tracks.py`).
- Evidence: `fix_2_d3_before.jpg` (master f612/640/680), `fix_2_d3_after.jpg` (push clip at lt 0.3/1.3/2.2/3.0 under
  the letterbox; plate and etch are PIL stand-ins, so only their size and place carry over).

### Scripts (all under `tools/v9/mirrors/`)
`gen.py` (every paid call), `v2f_roof_guide.py`, `v2f_cutouts.py` (run with tools/engrave/.venv for cv2),
`mock_car.py`, `d3_guide.py`, `d3_kf_fix.py`, `d3_push.py`, `d3_tracks.py`. New module `tools/v4B/car/car_shot_v9.js`.

## Exact timeline changes (not applied: the lead applies them)

**render/timeline/C.js** line 5:
```js
import carShot from '../../tools/v4B/car/car_shot_v9.js';   // v9 #3: the car shot with a roof: the mirror hangs on a stem from the header (docs/revisions/v9/fix_2_3_mirrors.md)
```
(was `'../../tools/v4B/car/car_shot.js'`; nothing else in C.js changes; CAR_START, rows and overlays stay.)

**render/timeline/A.js**
1. Add after the other imports (line 8):
```js
import { D3_PLATE_V9, D3_ETCH_V9 } from '../../tools/v9/mirrors/d3_tracks.js';   // v9 #2: D3 plate + etch tracks
```
2. `PLATE.D3` (line 21) becomes:
```js
  D3: { src: S('D3', 'v9_take_2_push.mp4'), in: 0.0, rate: 1 },   // v9 (Jade 0:25, impossible door mirror): over her right shoulder into the interior rear-view mirror on its stem, same car as the 1:30 shot; the push toward the mirror is baked in (tools/v9/mirrors/, docs/revisions/v9/fix_2_3_mirrors.md). v8: take_2_engraved_eraser.mp4
```
3. In `KF` (line 73): `D3: 'kf_v9.png'` (was `'kf_sdr3.jpg'`; stills mode only).
4. The D3 shot (lines 207-218) becomes:
```js
    { id: 'D3', start: 25.34, end: 28.4, background: INK,
      layers: [
        vid('D3'),
        // v4 (Jade, 0:26): the sedan's front plate reads TVA 1729. v9: the sedan is seen in the interior mirror, through
        // her rear window; the plate is tracked on the push clip
        { type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { text: 'TVA 1729', corners: D3_PLATE_V9, grow: 1.6, aspect: 2.3, dim: 0.12, light: 0.8 } },
        // etch on the mirror glass, over the left half of the rear window (left of the sedan): the billboard carried
        // "a shadow chasing", the mirror finishes the line
        { type: 'canvas', module: 'etch', noRewind: true, x: 2, y: 2, opacity: 0.85, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, corners: D3_ETCH_V9, color: INK } },
        { type: 'canvas', module: 'etch', noRewind: true, params: { text: "me I couldn't\nplace", sync: 'lyric', size: 60, corners: D3_ETCH_V9, color: '#fbf8f1' } },
      ], fx: [LETTERBOX] },
```
(`D3_QUAD` and `tracks.D3_*` are then unused; leave them for rollback.)

## What still looks wrong / to check in the lead's render
- **D3 glance:** neither Seedance take does the "eye flicks up to the mirror": she blinks once and keeps her eyes on
  the road. The mirror and the sedan in it carry the beat, but the glance isn't there. Another 2 takes would cost $1.20.
- **D3 plate and etch are small.** The interior mirror is ~30 % of the frame, where the old door mirror filled half of it. Even with
  the push, the drawn plate is ~50 -> 69 px wide at 1080p (v8: ~99), and the two etched lines sit in a ~190x92 ->
  262x127 px quad (v8: ~397x184). Check that they read at 540p. If they don't, raise `grow` to ~2 and/or `Z_END` in
  `d3_push.py` (then re-run `d3_push.py`, `track_quad.py` and `d3_tracks.py`).
- D3: the following sedan in the mirror is a paste from another edit (`d3_kf_fix.py`). Seedance read the paste's
  lighter edge as two streetlight poles behind the car, which is plausible. The sedan's headlights are dimly lit, not
  off, and it has a tiny grille badge (~3 px). The plate reads right-way-round (film convention, as before).
- D3 is a lot calmer than v8's. The push ends tight on her cheek and eye with the mirror at top centre; the pencils
  leave frame by ~1.2 s.
- V2f: the stem reads as two pale edges with a dark gap between them at 91.4 (that's how the edit drew it). The
  roof liner is lighter in the wide than in the close still's headliner. The take's own passing gantries still show
  through the lower windshield as small shapes. The engine stand-in leaves out the shake/roll fx, the light sweep
  and the strobes, so the roof should be checked in motion in the real render (it rides `wideCam`, like the take).
- V2f mirror glass still shows the fleet with no rear-window frame (audit item 23, LOW, out of scope); D3's glass
  now does show the rear window, so the two mirrors differ in that one detail.
- The R3 rewind and C2 teaser reuse rendered shots, so they pick up the new D3/V2f automatically when re-rendered.

## Round 2 (2026-10-15, after the lead's 540p integrated preview)

Spend this round: **$0** (no paid calls; all fixes are local). Checked with range renders at 540p, the only ones
I ran: `--range 88.5 92.8 --encode --force` on the film timeline (V2f; car_shot_v9.js is already imported by C.js),
and the D3 block below as a solo timeline `tools/v9/mirrors/_d3_solo.js` (`--range 25.34 28.4`), because A.js still
holds the round-1 D3. I stepped through every frame of both. Evidence: `fix_3_v2f_round2.jpg`, `fix_2_d3_round2.jpg`.

### #3 V2f: the stem now runs from the mount into the mirror in every frame
- Cause: the stem I cut from the nano-banana edit was two pale edges with the windshield/gantry showing between
  them, so mount, stub and mirror read as three separate things. Painting it dark (first try) read the same way.
- Fix: `tools/v9/mirrors/stem.py` paints a solid engraved stem. It has a mid-grey body crossed by fine ink lines (like the
  mount), an ink contour, a shadow side, a paper highlight and a ball joint. It runs from the mount (y 334) into the mirror
  housing's top edge (y 367; the mirror body is drawn over its foot). It is 31 to 27 design px wide, which covers the
  edit's two edges. It is baked into the roof layer, so it rides `wideCam` exactly like the mount and the take, and the
  mirror body (`closeCam`) lands on it by construction. New roof: `media/shots/V2f3/v9_roof_r2c.png`
  (`v2f_cutouts.py`), used by `tools/v4B/car/car_shot_v9.js`.
- Checked frame by frame at f2143-2226: mount, stem and housing are continuous in every frame up to the handover. At
  f2195-2196 the close still's own stem fades in over the same place. No pops. The gantry girders still show beside
  the stem, through the windshield, but not between the stem and the mirror.

### Mirror-reversed plates (Jade)
- `tools/v4B/plate/plate.js` has a new option, `params.mirror: true`, which flips the whole plate face left to right
  (glyph order and shapes). It defaults to off, so other shots are unchanged.
- V2f: the three fleet plates (`TVA 1729`, `TVA 4104`, `TVA 4096`) are the `car_hero_plate`, `car_left_plate` and
  `car_right_plate` canvas layers (plate.js) in `tools/v4B/car/car_shot_v9.js`. They now have `mirror: true` (the
  close still's own plates are blank). They read `9271 AVT` etc., reversed. `IN MY MIRROR` stays right-reading
  because it is on the housing, not in the glass.
- D3: the plate layer gets `mirror: true` (see the A.js block below).

### #2 D3: plate and etch readable at 540p, solid stem
- `media/shots/D3/v9_take_2_push_r2.mp4` (`d3_push.py`):
  - The push is now 1.0 to 1.9, eased out, so most of it lands while the line is sung. Her eye holds for about the
    first second ("me I"), then the mirror fills the frame. The picture starts 70 px low so the roof liner, visors and
    mount show under the letterbox, and ends 0 px low.
  - The take's two pale stem edges are covered with the windshield's own line texture. A solid stem (`stem.py`) is
    painted from the mount (y 174) to the housing's top edge (y 230). The mirror holds within 1 px for the whole take,
    so a static paint is enough.
- Plate: re-tracked on the new clip (`media/shots/D3/track_plate_v9_r2.json`), with `grow` raised to 2.4. It is about
  90 to 140 px wide at 1080p from about 1 s, which is about 45 to 70 px at 540p. It reads `9271 AVT` (reversed),
  clearly.
- Etch: split in two so neither overlaps the sedan. `me I` sits in the rear window left of the car; `couldn't / place`
  sits right of it. Both quads follow the push exactly. The m is no longer clipped by the bezel, and couldn't no
  longer touches the car. Tracks are in `tools/v9/mirrors/d3_tracks_r2.js` (from `d3_tracks_r2.py`).

### Timeline changes needed (A.js only; C.js needs nothing more)
1. Replace the round-1 import (line 9) with:
```js
import { D3_PLATE_R2, D3_ETCH_L_R2, D3_ETCH_R_R2 } from '../../tools/v9/mirrors/d3_tracks_r2.js';   // v9 #2 round 2: D3 plate + etch tracks
```
2. `PLATE.D3` (line 22): change the src to `S('D3', 'v9_take_2_push_r2.mp4')`. The rest is unchanged
   (`in: 0.0, rate: 1`); add "round 2: push to 1.9, solid stem" to the comment.
3. The D3 shot's layers (lines 211-217), after `vid('D3'),`, become:
```js
        // v4 (Jade, 0:26): the sedan's front plate reads TVA 1729. v9: seen in the interior mirror, through her rear
        // window, so it reads mirror-reversed (Jade, round 2); tracked on the push clip
        { type: 'canvas', module: 'tools/v4B/plate/plate.js', noRewind: true, params: { text: 'TVA 1729', corners: D3_PLATE_R2, grow: 2.4, aspect: 2.3, dim: 0.12, light: 0.8, mirror: true } },
        // etch on the mirror glass, either side of the sedan: "me I" | "couldn't / place" (the billboard carried "a shadow chasing")
        { type: 'canvas', module: 'etch', noRewind: true, x: 2, y: 2, opacity: 0.85, params: { text: 'me I', sync: 'lyric', size: 60, padding: 4, corners: D3_ETCH_L_R2, color: INK } },
        { type: 'canvas', module: 'etch', noRewind: true, params: { text: 'me I', sync: 'lyric', size: 60, padding: 4, corners: D3_ETCH_L_R2, color: '#fbf8f1' } },
        { type: 'canvas', module: 'etch', noRewind: true, x: 2, y: 2, opacity: 0.85, params: { text: "couldn't\nplace", sync: 'lyric', size: 60, padding: 4, corners: D3_ETCH_R_R2, color: INK } },
        { type: 'canvas', module: 'etch', noRewind: true, params: { text: "couldn't\nplace", sync: 'lyric', size: 60, padding: 4, corners: D3_ETCH_R_R2, color: '#fbf8f1' } },
```
4. Render with `--force` for 25.34-28.40 and 89.26-92.79. The frame cache does not see the changes to `plate.js`,
   `car_shot_v9.js` or the re-baked clip.

### Still imperfect
- D3 is now mostly about the mirror. Her eye is in frame for about the first second only, and the pencils for about
  0.5 s. That is the price of a readable plate and etch from an interior mirror. She still doesn't do the
  "glance up" (round-1 note).
- D3: `place` reveals on its sung onset at 27.30, so it shows for only the last ~1.1 s.
- V2f: the gantry's pale posts stand close beside the stem. They are behind the windshield and read as such in motion,
  but in a paused frame they sit near the stem.
- V2f mirror glass still has no rear-window frame (audit item 23); D3's glass does.
