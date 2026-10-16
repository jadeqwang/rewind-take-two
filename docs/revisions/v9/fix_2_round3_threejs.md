# v9 fix #2, round 3: D2 + D3 as one three.js scene (driver's door mirror)

Status: DONE. It is in `render/timeline/A.js` and I checked it in engine range renders at 540p. Every frame of 23.16-28.40
was stepped through by eye, plus the neighbours (22.4-29.2) and the R3 replay (51.3-52.3).
Spend: **$0.80** (6 nano-banana-pro calls, tags `v9_d23_*`), against a cap of $8. Project total after: $262.36.

## Jade's notes (verbatim)
- "0:24 impossible mirror isn't fixed. Here's a suggestion: use three.js to build model of Jade in the driver's seat
  looking at the rearview outside the driver's side window. position the camera as though you're in the passenger seat
  looking out the driver's side window. That's where you see 'a shadow chasing'"
- "0:27 in that same three.js model, now have her continue to look at the driver's side rearview outside the car and
  zoom the camera into the mirror. Have the license plate be legible though, even though it should be reversed in real life."

## What it is now
There is one continuous take from 23.16 to 28.40 (D2 is clip 0-2.18, D3 is clip 2.18-5.24). The cut at 25.34 is inside a
continuous move, so it cannot pop.
- **Scene (three.js, `tools/v9/d23/scene.js` + `rig.js`).** Lake Shore Drive at night, southbound, in the car's frame:
  the road, lane dashes, the median Jersey wall with double-armed lamps, the lakefront park and trees, the skyline, and
  northbound traffic. Jade's white Acura is left-hand drive, seen from the passenger seat (camera at
  `[0.25, 1.08, 0.42]` m). The interior is built in 3D: door panel, sill, A-pillar, roof rail, B-pillar, roof liner,
  dash, instrument hood, console and driver's seat. Outside the window are the white hood and fender.
- **The mirror is a real object.** It has a white rounded housing, a neck and an arm bolted to the black sail at the
  front of her window, a bezel, and flat glass.
- **The reflection is geometrically real.** The glass shows a live render from a virtual camera: the passenger's eye
  mirrored in the glass plane, with an off-axis frustum that is exactly the glass rectangle. The glass normal is aimed
  for the driver (check printed by `tracks.mjs`: her eye sees 1.8° outward and 2.8° down, i.e. straight back along her
  flank). From the passenger seat the same glass shows the lane to her left, where the TVA sedan follows.
- **Jade** is a matted 2D anime plate (nano-banana-pro, drawn over the scene's own layout render with a grey mannequin
  in the seat), laid on a card that is registered to the guide camera's frustum. In the scene she is in the driver's
  seat with both hands on the wheel, her head turned to the mirror. She has two crossed pencils (pink and pale-blue
  erasers, in colour), orange headphones round her neck, and the white jacket with the orange band. Her near (right)
  sleeve has no roundel, which is correct because the roundel is on the left sleeve.
- **D2 (23.16-25.34).** The take opens medium-wide: both hands on the wheel, the mirror small outside the window. It
  pushes in (log-zoom 47° → 12°) and lands on "A" (23.97) as a tight two-shot of her ear and cheek and the mirror. The
  bulb billboard (two lit panels on a lattice tower on the lakefront) is in the glass. "A SHADOW" / "CHASING" use the
  same WOODCUT bulb reveal, lyric-synced, pinned to the reflected panels.
- **D3 (25.34-28.40).** The same scene. She keeps looking at the mirror while the camera zooms into the glass (12° →
  6.6°, eased in and out, on a log scale). The black sedan closes from about 40 m to 19 m. By about 26.8 it fills the
  glass, and it holds there to the end. Its headlights are off, and you see the two agents in shades. The plate reads
  **TVA 1729** (plate.js, pinned to the reflected plate). "me I couldn't place" is etched along the bottom of the glass
  under the bumper, clear of the plate, word by word on the lyric. The billboard stays lit with the whole line behind
  the sedan's roof.
- **Text cheat (as Jade asked).** All authored text reads forward. The plate and the billboard lyric are pinned to the
  mirror image of their real surfaces, with the quad's corners swapped left↔right, so the place, size and perspective
  are those of the reflection but the glyphs are not reversed. Everything else in the glass is a true mirror image.
- **Occlusion.** The scene also renders a billboard-visibility mask (`pass=billmask`). The engine re-draws the clip
  through its inverse over the pinned lyric, so lamp poles, the glass edge, the A-pillar and, in D3, the sedan's roof
  correctly cover the lettering.
- **Look.** The beauty render goes through the same section A engrave pass (`tools/engrave/engrave.py`) with the
  scene's own Jade matte (`--matte-in`), so the world is hatched ink on paper and she passes through in colour, like
  every other take. Flat areas are engraved with horizontal lines (`--fallback-angle 0 --fallback-weight 1`); without
  that, the plain CG planes came out as fingerprint swirls. Starbursts are drawn on every lamp, as in D1.

Evidence:
- `fix_2_r3_before_after.jpg`: v8 master on top, round 3 below, at f560 / 585 / 600 / 615 / 640 / 672.
- `fix_2_r3_steps_2324.jpg` (f602-617, across the 25.34 boundary) and `fix_2_r3_steps_2627.jpg` (f652-667, the plate
  and etch): step sheets from the engine render.

## Files
- `tools/v9/d23/rig.js`: geometry, camera move, sedan and billboard motion (shared by the scene and the tracks).
- `tools/v9/d23/scene.js`: the three.js scene module (render/three module interface). Passes: `beauty`, `matte`
  (Jade's card alpha), `billmask`, `guide` (mannequin).
- `tools/v9/d23/tracks.mjs` → `tools/v9/d23/d23_tracks.js`: per-frame corner keys `D2_BILL_TOP/BOT`, `D3_BILL_TOP/BOT`,
  `D3_PLATE_R3`, `D3_ETCH_R3` (plus `D2_GLASS`/`D3_GLASS`, unused).
- `tools/v9/d23/build.sh`: the whole rebuild, about 1 min. It runs capture → matte → billmask → engrave → tracks.
- `tools/v9/d23/gen.py`: every paid call. `pencil_tip.py` repaints a wrong pencil end (plate_c came back with an eraser
  at both ends of the blue pencil; that end is now a sharpened point). `make_plate.py` builds the RGBA plate (BiRefNet
  matte + Real-ESRGAN 2x). `sedan_card.py` keys the sedan.
- Media (`media/shots/D23/`):
  - **`v9r3_engraved.mp4`** (the take).
  - `r3_billmask_frames/` (engine occlusion matte).
  - `r3_matte_frames/`, `r3_matte.mp4` (Jade's matte).
  - `r3_src.mp4` (beauty render).
  - `jade_plate_rgba.png` (from `plate_c_tip.png`).
  - `sedan_a_rgba.png`.
  - `guide_s0.png`.
  - Rejected plates: `plate_a/b/d`, `sedan_b`.
- Running the scene by hand: `cd render/three && node tools/capture.mjs --scene ../../../tools/v9/d23/scene --stills 0,2.5 --ss 1 --out DIR`
  (add `--p.pass matte|billmask|guide`). Time 0 is song time 23.16.

## Exactly what changed in `render/timeline/A.js`
I only touched the import line, `PLATE.D2`/`PLATE.D3`, and the D2 and D3 shot blocks. `D2_DOWN`, `D3_QUAD` and the
`tracks.D2_*`/`D3_*` keys are now unused; I left them for rollback.
1. Import: replaced the round-2 line (`d3_tracks_r2.js`) with
   `import { D2_BILL_TOP, D2_BILL_BOT, D3_BILL_TOP, D3_BILL_BOT, D3_PLATE_R3, D3_ETCH_R3 } from '../../tools/v9/d23/d23_tracks.js';`
2. `PLATE.D2` → `{ src: S('D23', 'v9r3_engraved.mp4'), in: 0.0, rate: 1 }` (was `S('D2', 'take_2_engraved.mp4')`).
   `PLATE.D3` → `{ src: S('D23', 'v9r3_engraved.mp4'), in: 2.18, rate: 1 }` (was round 2's `S('D3', 'v9_take_2_push_r2.mp4')`).
3. D2 layers:
   - `vid('D2')` (no `D2_DOWN`).
   - WOODCUT `A SHADOW` and `CHASING` (bulb reveal, lyric sync, `box: [460, 96]`, `pad: 6`) on `D2_BILL_TOP` / `D2_BILL_BOT`.
   - `vid('D2', { id: 'D2_occluder', matte: { src: S('D23', 'r3_billmask_frames/'), mode: 'lumaInv' } })`.
   - The two R3-only layers (`RW_ONLY`), moved after the occluder and re-pinned to `D2_BILL_TOP/BOT`.
   - Shot start/end and `fx: [LETTERBOX]` are unchanged.
4. D3 layers:
   - `vid('D3')`.
   - WOODCUT `A SHADOW` / `CHASING` held lit (`at: -1`) on `D3_BILL_TOP/BOT`, then the `D3_occluder` (same mask).
   - plate.js `TVA 1729` on `D3_PLATE_R3` (`grow: 1.0, aspect: null`, no `mirror`).
   - One etch line, `"me I couldn't place"`, as an ink shadow plus a paper copy on `D3_ETCH_R3`, lyric-synced.
   - Shot start/end and `fx: [LETTERBOX]` are unchanged.

## Checks (540p engine renders, every frame)
- **She reads as driving.** Both hands are on the wheel rim through the opening, and the right hand stays on the wheel
  through the two-shot.
- **The mirror is attached.** The arm runs into the sail and the housing sits outside the window, with the A-pillar
  passing in front of it from the passenger's eye line.
- **The reflection is consistent.** As the car moves, the lamps, dashes and traffic in the glass stream away to the
  rear. The sedan is in the lane she just left, and the billboard recedes slowly.
- **Legibility at 540p:**
  - "A SHADOW" / "CHASING" read from about 24.25 (in the glass, about 90 px wide at 540p).
  - TVA 1729 reads from about 26.1 and is about 70 px wide at 540p by 27.0.
  - The etch reads from about 26.4.
- **Pops:**
  - 23.16: hard cut from D1, as before.
  - 25.34: none (one continuous take; the lettering continues).
  - 28.40: hard cut to D4, as before.
  - Within D2/D3, the lamp starbursts are dropped in direct view once the zoom is tighter than 15°, so a lamp can't
    flash across the frame for a single frame at the tight framing. They stay in the glass.

## Rewinds
- **R3** (B.js, 48.42-52.48) is a `comp` of the film, so it already shows the new D3 then D2 backward (checked
  51.3-52.3). The REWIND title sits across the mirror. The R3-only lettering is drawn small on the reflected panel.
- **C2** (1.90-7.24) flashes film times 27.0 ("mirror") and 24.0 from the same comp, so it now shows the new mirror
  shots. Its noRewind layers (lyric, plate, etch) are not drawn there, as before. Nothing to change.
- **Re-render:** no other timeline references D2 or D3 sources. Re-render with `--force` for 23.16-28.40 and wherever
  C2 and R3 are previewed. The engine cache keys by path, and the new source is a new path.

## What still looks wrong
- **Jade is a still.** She is a static 2D plate on a card: no breathing, no blink, and the hands don't move on the
  wheel. Only the camera moves and the engrave line boil plays over her. Animating her would need a Seedance take of
  the plate (or a few hand-made holds).
- **The interior is simple.** It is boxes, and after engraving its large flat planes (door panel, dash, roof) read as
  plain hatched slabs, not as the detailed AI-drawn interiors of D6/C_V2f. It is darker and plainer than its neighbours.
- **The billboard and the sedan are flat cards.** The billboard is real geometry. The sedan is a nano-banana engraved
  image on a card, so it doesn't change perspective as it closes. It is about 10° off-axis, which is fine at this
  distance. The 3D box sedan is still in the scene, hidden (`p.boxSedan`).
- **The "I" in the etch** sits over a reflected lane dash at 27.4-28.4, so it is lower-contrast than the other words.
- **Continuity with D4:** the sedan's headlights are off here (round-2 canon), but D4's sedan has them on.
- **The skyline is barely visible.** It is behind the camera direction, so it only shows in the glass, as dotted window
  texture above the trees.
- **It doesn't come from the engine.** The scene is rendered offline to a clip (headless Chrome, `capture.mjs`), not
  live as a `type: 'three'` layer. That keeps the film's engrave pass on it. Any change to `rig.js`/`scene.js` needs
  `tools/v9/d23/build.sh` and then a `--force` render.

## Round 4 (2026-10-15, after the coordinator's look at round 3)

Status: DONE. Checked with `--preview --force --range 22.5 28.6 --encode`, stepping through all 146 frames, plus R3 at
51.3-52.3. Spend this round: **$0.54** (4 nano-banana-pro calls, tags `v9_d23_r4_*`). Total for the item: $1.34.
Project total: $262.90.

### The coordinator's notes and what changed
1. **Camera (was behind her, over her right shoulder).** The camera is now at the passenger's head, `CAM = [0.50, 1.10,
   -0.12]`, level with her head and beside her. It looks LEFT across her at the driver's window (6.5° forward of
   straight left), as in D6. The mirror is outside the side glass, in the window's front corner where the A-pillar
   meets the belt line, not in the windscreen. The camera never moves, only turns and zooms, so the plate stays exact.
2. **Wheel.** The wheel is now in front of her, seen in three-quarter between her and the dash, with both hands on
   the rim. Her near arm reaches forward to it, not across her.
3. **Jade plate.** I regenerated her on-model in D6's fine anime linework, with D6's keyframe as the style reference.
   - She is in profile facing forward, eyes cut right to the door mirror, and her face is fully visible.
   - Canon: two pencils in the bun (pink and pale-blue erasers, sharpened lower ends), orange headphones on her neck,
     the white jacket with the orange band and no patch on the near sleeve, navy trousers.
   - The plate is the whole near interior, drawn by the model in the film's engraving: door panel with armrest, handle
     and switches, window frame, B-pillar, roof liner and grab handle, A-pillar, dash, instrument cluster, vents,
     console, and the stitched seat and headrest. That also covers point 5. The model left the side window and
     windscreen flat chroma green. Behind them the 3D world shows: the road, the lamps, the real mirror and its live
     reflection.
4. **Mid-D2 (no extreme ear close-up).** D2 now goes from a medium shot, with both hands on the wheel and the window
   beyond her, to a two-shot: her profile on the left, the mirror on the right, eyes on it. Vertical FOV runs 44° →
   23° by "A" (23.97), creeping to 19.5° by 25.34. D3 then zooms into the glass (to 8°).
5. **Interior.** It is now the plate's own drawn interior (see 3), not the boxes. The 3D interior is used only for
   the layout guide and the outside parts.

**A-pillar.** It crosses the frame diagonally at top right through D3. I checked every frame: it stays outside the
glass, so it never covers the plate or the lyric. The housing's bezel and the pillar overlap only on the housing.

### How (files)
- `media/shots/D23/guide_r4.png`: layout guide. It is the 3D cabin and a grey mannequin from the new camera, with
  the outside keyed green (`pass=guidekey`).
- Plates:
  - `plate_r4_a.png` is nano-banana-pro with refs guide + D6 `kf_v3_2` + `inputs/jade_in_outfit.png`.
  - `plate_r4_e2.png` is an edit of a: the wheel slightly lower, the model's own drawn door mirror removed (the corner
    is green again), erasers checked.
  - Rejects: `plate_r4_b` (head fine, layout drifted) and `plate_r4_e1` (JPEG, wheel unchanged).
- `tools/v9/d23/make_plate_r4.py` → `r4_plate_rgba.png` (green keyed to alpha, despilled, Real-ESRGAN 2x) and
  `r4_plate_jade.png`. The second is a Jade-only matte (BiRefNet × not-green, plus saturated pixels near her for the
  eraser tips). It feeds the engrave pass, so only she stays in colour.
- Registration: I fitted the plate's camera to it (`GUIDE` in `rig.js`: 6.5° forward, 9.25° down, vfov 58) and put the
  card on that frustum. `platePoint()` places the mirror glass on a plate pixel, the clear window corner just left of
  the drawn A-pillar, 1.1 m out. The arm root (`ARM0`) sits behind the drawn pillar.
- Mirror aim: still set for HER (straight back, a touch down). From the passenger seat, the same glass looks further
  out, so I moved things to where that glass looks:
  - Billboard: moved to the lakefront at `x -85, z0 262`. I also cut a clearing in the park trees in front of it
    (trees at z 60-330 skipped).
  - Sedan: comes up in the far-left lane, then edges right toward her lane line between 25.9 and 27.3 (x -7.3 →
    -5.25), so it slides into the glass during the zoom.
- **The plate is under the occluder now.** The mask pass also draws the sedan's plate quad, and A.js draws the plate
  layer before the `D3_occluder`. So TVA 1729 only shows where the plate is really seen: inside the glass, not on the
  housing while the sedan is still outside the glass.
- Tight framing: lamp heads, starbursts and traffic headlight bursts are dropped in direct view below 24° vfov (once
  the camera is past the open). This stops one-frame white flashes as lamps whip past the side window. They stay in
  the mirror.
- Etch band: glass-local `a -0.70..0.74, b -0.92..-0.77`, along the bottom of the glass under the bumper.
- Round 4 has new file names (the engine caches by path): `v9r4_engraved.mp4`, `r4_matte_frames/`,
  `r4_billmask_frames/`, `r4_src.mp4`. `tools/v9/d23/build.sh` writes them. The round-3 take, `v9r3_engraved.mp4`,
  is kept for rollback, but its frame folders are deleted.

### A.js (D2/D3 parts only), changes since round 3
- `PLATE.D2` and `PLATE.D3` src → `S('D23', 'v9r4_engraved.mp4')` (in 0 / 2.18 as before).
- Both occluder layers → `matte: { src: S('D23', 'r4_billmask_frames/'), mode: 'lumaInv' }`.
- D3: the plate.js layer moved before the `D3_occluder`, with a comment. Nothing else changed: same shot times,
  LETTERBOX, the bulb-reveal lyric pinned to `D2_BILL_TOP/BOT` and `D3_BILL_TOP/BOT`, the plate on `D3_PLATE_R3`, and
  the etch on `D3_ETCH_R3` (all re-generated by `tracks.mjs` from the new rig).

### Checks (540p, every frame of 22.50-28.58)
- **Driving.** 23.16-23.6: both hands on the wheel, which is in front of her. Hands leave frame by about 23.7 as the
  camera pushes to the two-shot.
- **Mirror.** It is attached to the door and outside the side glass. The A-pillar is drawn in front, the arm runs
  behind it, and the housing's back is seen as you would expect.
- **Reflection.**
  - The lamps, park and lane dashes in the glass stream away.
  - The billboard is in the glass from about 23.9, centred by about 24.2, and stays through D3 behind the sedan's roof.
  - The sedan enters the glass from the left at about 26.0 and fills it by about 26.8.
- **Legibility at 540p:**
  - "A SHADOW" from 24.25 (it lights on the word) and "CHASING" from 24.8.
  - TVA 1729 is legible from about 26.6.
  - The etch "me I couldn't place" runs along the bottom from 26.0; "place" appears at 27.3.
- **Pops:**
  - 23.16: hard cut from D1, as before.
  - 25.34: none (one continuous take).
  - 28.40: hard cut to D4, as before.
  - No flashes after the lamp fix.
- **R3 (51.3-52.3)** shows the new shots backward under REWIND, with no change needed. C2 replays the film the same way.

Evidence:
- `fix_2_r4_before_after.jpg`: round 3 on top, round 4 below, at f560 / 575 / 590 / 605 / 640 / 672.
- `fix_2_r4_steps_2324.jpg` (f556-571, the open: hands on the wheel), `fix_2_r4_steps_2526.jpg` (f604-619, across
  25.34) and `fix_2_r4_steps_2728.jpg` (f652-667, plate and etch).

### What still looks wrong (round 4)
- **Jade is still a still.** One drawn plate: no blink, no breath, no head turn. The camera move carries the shot.
- **The plate's line art is finer than round 3, but she's lit flatly.** There's no streetlight passing over her, and
  her skin is a touch pink-flushed (the model's blush).
- **The world outside the window is CG put through the engrave pass.** The road, park and trees outside the side
  window read as wavy engraved bands, not the crisp drawn hatching of the plate's interior, so there are two textures
  side by side. The 3D trees are dark blobs.
- **The housing is simple CG.** It is a rounded white box with a plain bezel. It holds up, but it's less drawn than
  the interior around it.
- **The etch's "me" sits on a reflected lane dash** from about 27.0, so it is a bit lower-contrast than the other words.
- **The sedan is still a flat card**, 10° off-axis, and its headlights are off (D4 has them on).

## Round 5 (2026-10-15, Jade's notes on v9r4)

Jade: "0:25 - very good improvement, the staging is very good, but can you have a subagent do a google image search for
an actual acura model TL rear view mirror shape, because that rectangle shape is inaccurate. also where the TVA license
place is made readable, it doesn't perfectly line up with the plate that the video model drew."

Status: DONE (offline). Per the round rules I did **not** run render.mjs or edit A.js. I checked with my own builds:
- `tools/v9/d23/plate_check.py`: plate fit measured on every D3 frame.
- `tools/v9/d23/mock_r5.py`: a stand-in of the engine composite, made of the clip, the pinned text layers in A.js
  order, the occluder mask, the etch and the letterbox. The text uses PIL fonts, not the woodcut/plate/etch modules,
  so only position, size, order and occlusion carry over from it.

Spend this round: **$0** (no paid calls). Project total: $262.90.

### 1. Mirror shape: the real 1999-2003 Acura TL door mirror
- **Generation.** The film's car is a white 2001 Acura TL, the second generation (UA4/UA5, 1999-2003). Every V2/D4
  prompt in media/shots/*/NOTES.md says "white 2001 Acura TL", and D4's drawn car (master 0:28-0:30) has that
  generation's grille, headlights and five-spoke wheels.
- **References** (public domain, Wikimedia Commons, by IFCAR and Bull-Doser), saved next to this report:
  - `fix_2_r5_ref_1_white_tl_99-01.jpg`: https://commons.wikimedia.org/wiki/File:1999-2001_Acura_TL_--_03-20-2012.JPG
    (white, driver's side mirror)
  - `fix_2_r5_ref_2_red_tl_99-01.jpg`: https://commons.wikimedia.org/wiki/File:1999-2001_Acura_3.2TL.JPG (driver's side
    mirror, close)
  - `fix_2_r5_ref_3_silver_tl_99-01.jpg`: https://commons.wikimedia.org/wiki/File:1999-2001_Acura_TL_--_03-21-2012.JPG
    (passenger side, for the cap's depth)
  - Also searched: Go-Parts' 1999-01 TL left mirror listing (OEM 76250-S0K-A11ZF,
    https://www.go-parts.com/9901-acura-tl-side-view-mirror-left-driver-p-900186182.html). No usable image could be
    scraped, and I found no glass-outline diagram for this generation online.
- **What the photos show:**
  - The cap is about 2:1. The inboard end (against the car) is tall and nearly square, with a tight bottom corner.
  - The top edge runs almost flat, falling slightly outboard.
  - The outboard end is one big rounded sweep (a teardrop corner).
  - The bottom edge rises toward the outboard end, so the cap tapers outboard.
  - The cap bulges forward.
  - A short neck at the inboard BOTTOM sits on a triangular sail foot at the window's front corner, on the belt line.
  - The body-colour cap wraps right to the glass, with only a thin dark seam.
- **What I built (`rig.js` `TL_OUTLINE`, used by `scene.js` and the track checks):**
  - The glass outline, made from Bézier segments in glass-local coordinates.
  - The cap, from the outline grown 2.2 cm and extruded with a deep rounded back. It is body colour.
  - A body-colour lip and a thin dark seam round the glass.
  - A neck moved to the inboard bottom (`glassPt(0.9, -0.62)`), and a black triangular sail foot.
  - The reflection is still a live virtual-camera render, now cut to the TL outline.
  - The glass keeps its 24 × 15.5 cm bounding box, so the reflection mapping and every track are unchanged in kind.
- Evidence: `fix_2_r5_mirror_ref_vs_ours.jpg`. Reading left to right: ref 1, ref 2, round 4's rounded rectangle, round
  5 at 25.00, round 5 zoomed at 27.79. The photos show the cap side from the car's front-left, so inboard is on their
  left. Ours shows the glass side from inside the car, so inboard is on the right. The silhouette is the same, mirrored.

### 2. Plate alignment: why it was off and the fix
- **Cause: a sign bug.** The sedan card's plane was translated by `-(W/2 - cx)/k` instead of `+(W/2 - cx)/k`. So the
  drawn car sat 28 image px (about 11 % of the plate's width, about 3.4 cm) to one side of the plate track, which is
  computed from the same image coordinates.
- **Second cause: a guessed plate rectangle.** I had eyeballed the drawn plate's rectangle. It is now measured from
  sedan_a.png (a pale-field component with its thin pale frame): `[1551, 964, 1803, 1103]`.
- **Third cause: sub-frame slip.** The engine reads clip frame `floor((t - 23.16) * 24)`, but 23.16 is 0.16 frame off
  the film's 24 fps grid. So the clip ran 0.16 frame early against the per-frame tracks, a few px at the zoom's
  fastest. The clip is now rendered from `CLIP0 = 556/24`, so clip frame n is exactly film frame 556 + n.
- **Result.** The TVA 1729 quad is now the drawn plate's own four corners, tracked per frame from the rig. The card
  doesn't deform, so the plate's corners follow it exactly. The quad is pinned to the reflection and reads forward
  (corners swapped, Jade's cheat, as before).
- **Check.** `plate_check.py` outlines the quad on the beauty render. On every D3 frame from 26.0 on, the drawn plate
  and the quad agree to about 1 px at 540p. The remaining "outside" pixels are headlight rays and bumper chrome, see
  the crops. The plate stays under the occluder, so it only shows where the plate is really seen in the glass.

### 3. Headlights on (as in D4)
White starbursts sit on the card's two drawn headlamps (`SEDAN_IMG.lamps`), additive. They show in the glass, through
the engrave pass, as white engraved bursts.

### Etch moved (forced by the fixes)
With the plate now where it really is (low in the glass) and the TL glass's bottom edge rising outboard, the bottom
band no longer fits. "me I couldn't / place" is now two lines in the top-left sky of the glass. That spot is outboard
of the billboard, above the sedan's roof, and inside the outline: `ETCH = { a0 -0.80, a1 0.0, out [0.44, 0.74],
in [0.52, 0.88] }`. The quad tilts with the cap's top sweep. All four corners are tested inside `TL_OUTLINE`, clear of
the billboard (a ≥ 0.03 from 26.6) and of the roof line (b ≈ 0.59).

### New outputs (`tools/v9/d23/build.sh`)
- `media/shots/D23/v9r5_engraved.mp4` (the take)
- `media/shots/D23/r5_billmask_frames/` (occluder)
- `media/shots/D23/r5_matte_frames/`, `r5_src.mp4`, `r5_src_frames/`
- `tools/v9/d23/d23_tracks_r5.js` (tracks)

Round 4's files are untouched, so A.js as it stands still renders round 4.

### Exact A.js change for the lead (D2/D3 parts only)
1. The import line:
   ```js
   import { D2_BILL_TOP, D2_BILL_BOT, D3_BILL_TOP, D3_BILL_BOT, D3_PLATE_R3, D3_ETCH_R3 } from '../../tools/v9/d23/d23_tracks_r5.js';   // v9 #2 round 5: TL mirror, plate fit (round 4: d23_tracks.js)
   ```
   (was `'../../tools/v9/d23/d23_tracks.js'`; the export names are the same).
2. In `PLATE.D2` and `PLATE.D3`, the `src` becomes `S('D23', 'v9r5_engraved.mp4')`, with `in` unchanged (0.0 and
   2.18).
3. In both occluders (`D2_occluder`, `D3_occluder`), `matte.src` becomes `S('D23', 'r5_billmask_frames/')`.
4. In both D3 etch layers (the ink shadow and the paper copy), `text` becomes `"me I couldn't\nplace"`. Everything
   else stays (`sync: 'lyric'`, `size: 60`, `padding: 4`, `corners: D3_ETCH_R3`). The etch style is left-aligned, so
   "place" sits under "me".
5. Nothing else. The plate layer stays as it is (`corners: D3_PLATE_R3, grow: 1.0, aspect: null`, before the
   occluder). Shot times and LETTERBOX are unchanged.

Then render with `--force` for 23.16-28.40. New paths, so the engine cache can't serve round 4.

### Checks by eye (stand-in composite, `fix_2_r5_checkpoints.jpg`)
- **0:23.5:** both hands on the wheel in front of her. The TL mirror is small in the window's front corner, on its
  low neck, the A-pillar in front.
- **0:25.0:** a two-shot of her profile and the mirror. "A SHADOW / CHASING" is in the glass, centred and legible.
- **0:26.5:** the sedan has slid into the glass with its headlights on. TVA 1729 sits on its plate. "me I" is etched
  top-left. The billboard is behind the sedan's roof.
- **0:27.8:** the sedan fills the TL glass. TVA 1729 is square on the drawn plate. "me I couldn't / place" is
  top-left in the sky.
- I also stepped through every 6th frame of 23.17-27.92. There's no lettering outside the glass and no plate floating
  off the car. 25.34 is inside one continuous take.

### Still to check / still wrong
- **Not engine-verified.** This round is checked on stand-ins only. The real woodcut, plate.js and etch modules need
  the lead's `--force` render. In particular, check that plate.js's own border and field fill the quad to its corners
  (a rounded `radius` would let the drawn plate's square corners peek through).
- **The cap is CG.** It is a smooth extrude with no crease line, so it is plainer than the photos' cap.
- **The etch is smaller than round 4's** (two lines in the top-left sky, about 22 px letters at 540p by 27.3).
- **Jade is still a still.** One drawn plate: no blink, no breath, no head turn. The camera move carries the shot.
- **The world outside the window is CG through the engrave pass.** The road, park and trees read as wavy engraved
  bands next to the plate's crisp drawn interior.

## Round 6 (2026-10-15): a little life in her

Jade: "please give her a little bit of motion, not a lot. she's concentrating on driving. maybe a lip bite or a blink."

Status: DONE (offline: no render.mjs, no A.js edit). Spend: **$0.54** (4 nano-banana-pro calls, tags `v9_2_r6_*`;
`r6_lip` was rejected). Project total: $263.44.

### What she does now
- **One blink, 0:24.12-0:24.25** (f579 half, f580-581 closed, f582 half, f583 open again). It falls while "shadow"
  is sung (24.22), well clear of the cuts at 23.16 and 25.34, and after the camera has landed on the two-shot.
- **A lip press, 0:24.62-0:25.04** (f591 ease in, f592-600 held, f601 ease out). Her lower lip draws in and up a
  little, the press of concentration, as "chasing" lands (24.78). Mouth closed, no teeth.
- Her gaze stays on the mirror and her hands stay on the wheel. The camera move, mirror, plate, lyric, tracks and
  occlusion mask are all unchanged. `d23_tracks_r5.js` came out byte-identical, and the r6 mask matches r5 exactly
  (max pixel diff 0).

### How (same linework, no seam possible)
- `tools/v9/d23/r6_frames.py` builds plate variants that differ from `plate_r4_e2.png` only at the eye or the mouth.
  - **Eye:** nano-banana-pro edits of a 1:1 crop of her face (`r6_half.png`, `r6_blink.png`, prompts in `gen.py`),
    registered back onto the crop by phase correlation on the unchanged hair and cheek (shift ≤ 0.2 px). Only a
    feathered ellipse round the eye is pasted in.
  - **Mouth:** her own drawn lips are warped by a smooth Gaussian displacement field, not redrawn. The change is
    confined to a 22×46 px patch of the 2752 px plate. The model's lip-bite attempt (`r6_lip`) bared teeth and
    changed her profile, and the closed-mouth retry (`r6_lip2`) recoloured the lips, so I rejected both and used
    the warp.
- `make_plate_r4.py` turned each variant into `r6_plate_<v>_rgba.png` + `_jade.png` (same key, matte and upscale as
  round 4).
- `scene.js` swaps her card's texture and her matte per film frame from `rig.js FACE_KEYS`. Everything goes through the
  same engrave pass with the same matte path, so the moving parts and the still parts are one image.

### New outputs (`tools/v9/d23/build.sh`)
- `media/shots/D23/v9r6_engraved.mp4` (the take)
- `media/shots/D23/r6_billmask_frames/` (identical to r5, but new path for cache safety)
- `r6_matte_frames/`, `r6_src.mp4`
- Tracks are unchanged: `tools/v9/d23/d23_tracks_r5.js`

Round 5's files are untouched.

### Exact A.js change (D2/D3 parts only)
1. `PLATE.D2` and `PLATE.D3`: `src` → `S('D23', 'v9r6_engraved.mp4')` (`in` 0.0 / 2.18 unchanged).
2. Both occluders (`D2_occluder`, `D3_occluder`): `matte.src` → `S('D23', 'r6_billmask_frames/')`. (r5's mask
   is pixel-identical, so leaving it would also be correct; switching keeps each round's files together.)
3. Nothing else: the import stays `d23_tracks_r5.js`, and the lyric, plate and etch layers are unchanged.

Render with `--force` for 23.16-28.40.

### Frame check (every frame, 0:23.16-0:25.34, stand-in composite of the r6 clip + text + occluder + letterbox)
- **f556-f571 (0:23.17-0:23.79):** the open and the push. Both hands on the wheel, eyes open on the mirror, face as in
  round 5. No change.
- **f572-f578 (0:23.83-0:24.08):** two-shot, eyes open.
- **f579 (0:24.12):** half-closed. **f580 (0:24.17), f581 (0:24.21):** closed (a curved lash line). **f582
  (0:24.25):** half. **f583 (0:24.29):** open. No seam round the eye in any of them.
- **f584-f590 (0:24.33-0:24.58):** eyes open; "A SHADOW" lit in the glass from f582.
- **f591 (0:24.62):** press easing in. **f592-f600 (0:24.67-0:25.00):** lips pressed (lower lip tucked). **f601
  (0:25.04):** easing out.
- **f602-f608 (0:25.08-0:25.33):** relaxed, eyes on the mirror.
- **f609 (0:25.38):** D3 starts in the same take, face unchanged, no pop.
- She leaves frame early in D3 as the zoom moves to the glass, so no D3 face motion is needed.
- Evidence: `fix_2_r6_blink_press.jpg` (1080p crops of f578-583 and f590-603).

### Still to check / still wrong
- **The press is faint at 540p.** It reads at 1080p and on a second watch, as asked ("not a lot"). If Jade wants it
  more visible, raise the warp strength `k` in `r6_frames.py` (1.5 → 2.2) and rerun it, `make_plate_r4.py` and
  `build.sh` (all free).
- **No breath or hand motion.** I left both out. Any card motion would slide her against the drawn wheel and seat,
  which are part of the same plate.
- **Not engine-verified.** Checked on stand-ins only; it needs the lead's `--force` render.

## Round 7 (2026-10-16): the mirror's placement and a drawn housing

Jade: "there's something about the acura mirror in 0:24. I think it's both that the placement feels unnaturally high,
and also although the other instance said the three.js model was built from an actual reference of an acura model tl
mirror, something about it feels off, perhaps because it looks visually different from other mirrors of the acura model
tl in this video"

Status: DONE (offline: no render.mjs, no A.js edit). I checked every frame from 0:23.17 to 0:28.38 (f556-f681) on
540p stand-in composites. Spend: **$2.69** (20 nano-banana-pro calls, tags `v9_2_r7_*`), against a cap of $4. Project
total: $266.13.

### What changed (summary)
- **The mirror is at the real spot.** It sits on the black sail at the window's FRONT LOWER corner, where the A-pillar
  foot meets the sill. The cap's bottom is on the belt line. The glass centre is at y 1.045 m, 9 cm below her eye (it
  was 6 cm), and at z -0.63 m (was -0.53, mid-window).
- **The camera moved.** It is 23 cm further forward in the passenger seat: `CAM [0.45, 1.12, -0.35]`. From the old
  camera the wheel rim covered that corner, and the image model would not draw the wheel lower (6 tries). From the new
  camera the wheel is left of and below the glass, and the push into the glass is clean all the way.
- **Her plate is redrawn for the new view** (`plate_r7_n`). It has the real TL dash and both hands on the wheel. Her
  eyes cut right and a little down to the mirror. Canon: crossed pencils with pink and pale-blue erasers, orange
  headphones, the white jacket with the orange band, navy trousers. Round 6's blink and lip press are redone on it.
- **The housing is drawn** (nano-banana-pro, with the film's own D4/P1 TL mirrors as the style reference). It has a
  bold ink outline, a fat rounded cream cap with hatched shading, the cap's rounded back curving forward on the inboard
  side, and only a thin rim round the glass. It is a high-res card registered to the rig. The live reflection shows
  through its glass hole, and the in-glass checks use that hole's outline.
- **The aim is fixed.** Rounds 4-6 had the glass looking 5.7° INWARD (a sign slip: +x is the car's right). It is now
  set as a driver sets it: the glass centre looks straight back for her eye, 2.3° down. From the passenger seat it
  shows 31° outward.
- **The beats are re-placed to land at the same times.**
  - The billboard is far back on the lakefront and stays inside the glass the whole take.
  - Lake Shore Drive gets its fourth southbound lane. The TVA sedan comes up in the far-left lane, angled toward us
    (yaw -28°), and fills the glass by about 0:26.6.
  - The etch moves to the bottom band of the glass, under the plate.
  - The northbound traffic is re-phased, so no car crosses the lyric.

### Log (written as I go)
- **Why it read high.** Round 4 placed the glass on plate pixel (1570, 568), mid-window, about 50 cm behind the A-pillar
  foot, because the drawn wheel rim covered the real spot. Round 4's layout guide had the 3D wheel's top 8 cm above
  the belt line (centre y 0.86), and the model drew it there. From that camera, a mirror at the window's front lower
  corner sits behind the rim's top (plate_r4_e2 px 1660-1940 × 660-1000).
- **Keeping the camera failed (6 paid calls, all rejected).** I lowered the 3D wheel to a real TL height (top about
  0.97 m, `rig_r7.js WHEEL`). I then tried, from round 4's camera: two fresh plates (`plate_r7_a`, `_b`), two cleanups
  of a paste-up of e2 with the wheel moved down (`pasteup_r7.py`, `plate_r7_c`, `_d`), and two crop-level cleanups
  (`plate_r7_e_crop`, `_f_crop`). In every one the model put the rim back above the sill, over the corner (r7_d also
  drew a mirror). Round 4's edit (R4_EDIT) had the same problem.
- **So the camera moved (Jade's fallback).** `CAM` went from `[0.50, 1.10, -0.12]` to `[0.45, 1.12, -0.35]`: the
  passenger leans 23 cm forward, 5 cm inboard and 2 cm up. From there the wheel rim spans 2-13° forward of straight
  left and the glass 15-17.5°, so the wheel is left of the glass and 4° below it. Her face is 37° from the glass
  (round 4: 29°). Guide: `media/shots/D23/guide_r7b.png` (GUIDE aim 2° back of straight left, 9° down, vfov 58).
  - `plate_r7_g`, `_h`: fresh plates from that guide. Both have the wheel low and left and the corner clear, but the
    dash copied the guide's box. h has the better linework.
  - `plate_r7_i`, `_j`: an edit of h with e2 as the dash reference. Rejected: the model returned e2, high wheel and all.
  - `plate_r7_k`, `_l`: the same edit with D6 as the reference. Rejected: a full redraw, wheel high again.
  - `plate_r7_m`, `_n`: a single-image edit of h, the dash described in words. Both kept h's layout and drew a real
    dash. **n is the plate** (round side vent, clean cowl).
  - The window's front lower corner is at plate px about (1815, 695), and the corner is clear green. The guide's
    real-spot 3D mirror (glass centre about [-1.10, 1.045, -0.80]) lands just rearward of it, on the drawn sill. The
    model drew her skin uncoloured (white with hatching), so I tint it peach by hand (`make_plate_r7.py`).

- **Plate, final.** `plate_r7_base.png` is n with her skin tinted by hand and the sail painted in. The model drew her
  skin uncoloured, as hatched white. I clipped the BiRefNet Jade matte to a polygon round her (it had taken in the seat
  and headrest) and keyed and upscaled it like round 4 (`r7_plate_rgba.png`, `r7_plate_jade.png`).
- **Glass placement on the plate.** I measured the drawn window on n: the sill is at y 693, and the vertical front frame
  is at x ~1810 from y 590 down, under the A-pillar's lower edge. The glass centre sits on plate px (1679, 610), 1.10 m
  out. The cap's bottom is on the sill, and its inboard top corner clears the pillar. The glass is now 22 × 14.2 cm
  (rounds 3-6: 24 × 15.5). The painted sail is the triangle (1814, 697), (1811, 590), (1712, 697). Its single pale
  rear-edge line replaces an early hatched version that read like a ruler at the tight end of the zoom.
- **Drawn housing.**
  - `housing_guide_r7b.png` is the CG cap, slimmed (rim 1.4 cm, a rounder ~11 cm back), alone on green. It is rendered
    from `rig_r7.housingCam()`, a fixed 10° frustum on the mirror from the same eye point.
  - `housing_r7_c.png` is nano-banana-pro with refs guide + P1 and D4 drawn-mirror crops (`ref_tl_mirror_p1/d4.png`).
    Rejects: a/b (first guide, rim too thick, boxy), d (JPEG).
  - `housing_r7.py`: ECC-registers the drawing onto the guide's silhouette (cc 0.99, about 5 px shift), keys the green
    (the glass hole becomes transparent), and back-projects the drawn hole onto the glass plane, giving
    `tl_outline_r7.js`. `rig_r7.inGlass` now uses that outline (`GLASS_OUTLINE`).
  - `scene_r7.js buildHousingCard()` puts the card on the housing frustum. The glass mesh runs 6 mm under the drawn rim,
    and the reflection frustum is 1.12× the glass (`MIRROR_FR`), so nothing smears at the edge. The CG cap, arm and
    sail foot are hidden (`housing: 'cg'` brings them back).
- **Sedan card.** `sedan_a_r7_rgba.png` is a copy of sedan_a with a pale wedge under the bumper inked out, because it
  sat on the etch's "me".
- **Blink and press redone on the new plate.** `r7_frames.py` (round 6's method) uses r7_half/r7_blink (registered to
  0.03 px) and the lip warp re-centred on the new mouth. Same frames as round 6 (`FACE_KEYS`).

### Files (all new; round 6's are untouched, so A.js still renders round 6)
- Code (`tools/v9/d23/`):
  - `rig_r7.js`, `scene_r7.js`, `tracks_r7.mjs`
  - `make_plate_r7.py`, `pasteup_r7.py` (the failed paste-up route), `r7_frames.py`, `housing_r7.py`, `tl_outline_r7.js`
  - `mock_r7.py`, `plate_check_r7.py`, `billcov_r7.py`
  - **`build_r7.sh`** (about 40 s with `SKIP_PLATE=1`)
  - New jobs in `gen.py`
- Tracks: **`tools/v9/d23/d23_tracks_r7.js`**. The export names are unchanged.
- Media (`media/shots/D23/`):
  - **`v9r7_engraved.mp4`** (the take)
  - **`r7_billmask_frames/`** (the occluder)
  - `r7_matte_frames/`, `r7_src.mp4`, `r7_src_frames/`
  - `r7_plate_*` (plate and face variants)
  - `r7_housing_rgba.png`
  - `guide_r7b.png`, `housing_guide_r7b.png`
  - `sedan_a_r7_rgba.png`
  - Rejected plates: `plate_r7_a`-`m`, `housing_r7_a/b/d`

### Exact A.js change for the lead (D2/D3 parts only)
1. The import line:
   ```js
   import { D2_BILL_TOP, D2_BILL_BOT, D3_BILL_TOP, D3_BILL_BOT, D3_PLATE_R3, D3_ETCH_R3 } from '../../tools/v9/d23/d23_tracks_r7.js';   // v9 #2 round 7: mirror on its sail at the window's front lower corner, drawn housing, camera 23 cm forward (rounds 5-6: d23_tracks_r5.js)
   ```
2. In `PLATE.D2` and `PLATE.D3`, the `src` becomes `S('D23', 'v9r7_engraved.mp4')`, with `in` unchanged (0.0 / 2.18).
3. In both occluders (`D2_occluder`, `D3_occluder`), `matte.src` becomes `S('D23', 'r7_billmask_frames/')`.
4. Nothing else. The etch text stays `"me I couldn't\nplace"`, and the plate layer stays as it is (`corners:
   D3_PLATE_R3, grow: 1.0, aspect: null`, before the occluder). The layer order, shot times and LETTERBOX are unchanged.

Render with `--force` for 23.16-28.40, plus C2/R3 where previewed.

### Checks by eye (540p stand-ins, every frame f556-f681)
- **0:23.17-0:23.79 (f556-f571), the open.** Both hands are on the wheel, under the sill. The mirror is small, on its
  sail in the window's front lower corner, and it doesn't float. The wheel never overlaps the glass.
- **0:23.83-0:25.33 (f572-f608), the two-shot.** Her profile is at left and the mirror on its sail at right, her eyes
  on it.
  - "A" is lit from 0:23.97 (f575), "A SHADOW" from 0:24.25 (f582), and "CHASING" from 0:24.79 (f595). The lettering
    is ~51-59 px wide at 540p (round 6: ~90 px).
  - Blink: 0:24.12-0:24.25 (f579 half, f580-f581 closed, f582 half). Lip press: 0:24.62-0:25.04 (f591-f601).
  - From 0:24.45 the camera eases toward the glass and comes to rest at 0:25.33 (f608).
- **0:25.38 (f609).** D3 starts from rest in the same take: no pop, no velocity jump.
- **0:25.75-0:26.46 (f618-f635), the zoom.** The glass and its drawn cap grow cleanly. The A-pillar stays outside the
  glass, and the wheel is out of frame from 0:25.7.
  - The sedan enters the glass at about 0:26.12 (f627), headlights on, in the far-left lane.
  - TVA 1729 shows from 0:26.29 (f631) and reads by 0:26.6.
  - The billboard stays lit above the sedan's roof the whole time. The sedan's roof clips the bottom of "CHASING"
    from about 0:26.4, as in rounds 4-6.
- **0:26.50-0:28.38 (f636-f681).** The sedan fills the glass.
  - The etch sits under the plate: "me" from 0:25.53, "I" 0:25.87, "couldn't" 0:26.53, "place" 0:27.30.
  - The plate is about 49 px wide at 540p by 0:26.67 and 59 px by 0:28.0.
  - The drawn housing holds up at the final ~7.2° vfov.
- **Plate fit (`plate_check_r7.py`, every D3 frame).** From 0:26.38 (f633) to the end, the quad sits on the drawn plate
  to ~1 px. "Outside" is ~15 %: bumper chrome and the plate frame, as in round 5's 19 %. f623-f632 score badly only
  because the meter counts the cream housing rim as "plate" while the plate is still outside the glass. There the plate
  is correctly hidden by the occluder, which I checked on crops.
- **Occlusion.** On the mask, the billboard is fully visible every frame except three:
  - f579-f580 (0:24.12-0:24.17): a lamp pole in the reflection.
  - f635 (0:26.46): the sedan's roof edge.
  Both are real and short. No passing car crosses the lyric, after re-phasing the traffic (`TRAFFIC_SHIFT 400`; at 0 a
  car hid CHASING at 0:25.92-0:26.00).

Evidence (`docs/revisions/v9/`):
- `fix_2_r7_before_after.jpg`: round 6 against round 7 at 0:23.29 f559, 0:24.46 f587, 0:25.00 f600, 0:26.04 f625,
  0:26.67 f640, 0:27.50 f660.
- `fix_2_r7_style_vs_d4_p1.jpg`: the drawn TL caps at 0:28.60 f686 (D4) and 0:38.50 f924 (P1) from the current preview,
  next to round 6's CG cap and round 7's drawn cap.
- `fix_2_r7_steps_2317_2379.jpg`, `_2450_2513`, `_2517_2579`, `_2583_2646`, `_2717_2779`: every frame of those ranges.
- `fix_2_r7_blink_press.jpg`: her face at f578-f583 and f590-f602.

### Still wrong / not checked
- **Not engine-verified.** These are stand-ins with PIL fonts. The real woodcut, plate.js and etch modules need the
  lead's `--force` render.
- **The lyric is smaller than round 6** (~55 px wide at 540p in the two-shot, against ~90). The real spot is lower and
  further away, and the two-shot has to hold both her face and the mirror (37° apart). It reads at 540p, but small. If
  Jade wants it bigger, tighten `FOV_TWO`/`FOV_TWO_END` in `rig_r7.js` (her profile then crops further).
- **The two-shot crops her** at the left edge. As the camera creeps toward the glass, by 0:25.0 only her face from
  forehead to chin is in frame. The pencils are out of frame from about 0:23.7; they read clearly in the open.
- **The housing is one drawing seen from one angle.** That is exact here because the camera never translates, but the
  drawn hatching doesn't boil with the engrave pass the way the plate does; it passes through the same engraver, so it
  is close.
- **Her skin colour is my hand tint**, not the model's. It matches D6's peach at 540p, but at 1080p the cheek blush is
  a soft blob.
- **The sail is painted by me** (a flat black triangle with one pale edge line), not drawn by the model. It reads at
  540p; it is plain next to the hatched door.
- **The world outside the window is still CG through the engrave pass** (the wavy bands), as in rounds 4-6.

### Round 7 follow-up (2026-10-16): pencil bodies
Jade: "the body of the pencils are now pink and blue when it's only the erasers that are those colors. the pencil body is
yellow." The r7 plate's model had painted both shafts in the eraser colours. `make_plate_r7.py` step 1b now recolours the
pink/blue pieces below the ferrules to pencil yellow (hue/saturation only, the drawn value kept); the erasers are separate
pieces above the bands and keep pink / pale blue. Rebuilt with `build_r7.sh` (same r7 filenames) and checked in a 540p
engine preview of 23.0-28.6. No paid calls.
