# render/three: Monument Valley impossible geometry, engraved

Prototypes for the Verse 3 "Monument Valley" sequence of *Rewind* (treatment: the Loop, *Ascending and Descending*, the
perspective shift, colour = Jade's residue). They show three things:

1. Escher-style impossible geometry works in Three.js with an orthographic "magic angle" camera.
2. A rotating piece can visibly reconnect paths through that perspective trick.
3. The world reads as a **wood engraving** (and later as a coloured-pencil drawing) rather than a filtered CG render.

| Clip (1920×1080, 24 fps, 10 s) | Module | Stills |
|---|---|---|
| `media/three_proto/penrose_loop.mp4`: Penrose circuit on the Loop; six agents march forever; the camera orbits off-angle (leg D is left hanging in mid-air), then snaps back. Loops seamlessly. | `scenes/penrose_loop.js` | `stills/penrose_loop_magic_angle.jpg`, `stills/penrose_loop_orbit_reveal.jpg` |
| `media/three_proto/rotate_connect.mp4`: a crank turntable rotates 90°. Jade's spur joins a street-level stoop through the impossible joint, and she walks across into a door. The second turn carries the pursuer round into the loop. | `scenes/rotate_connect.js` | `stills/rotate_connect_crossing.jpg`, `stills/rotate_connect_pursuer_ride.jpg` |
| `media/three_proto/color_bloom.mp4`: the same beat, framed wide. The world is B&W engraving; when the joint locks, coloured pencil floods out from the pivot (orange / sky blue / gold, Klimt mosaic on the tower, Kandinsky rings in the sun). Agents stay ink. | `scenes/color_bloom.js` | `stills/color_bloom_flood.jpg`, `stills/color_bloom_full.jpg` |

`stills/detail_engraving_1to1.jpg` is an unscaled crop that shows the line work.

## Running

```sh
cd render/three
# stills (PNG) and clips (H.264, CRF 16); headless Chrome on the GPU, no npm dependencies
node tools/capture.mjs --scene penrose_loop --stills 1.5,4.2 --out /tmp/stills
node tools/capture.mjs --scene color_bloom --from 0 --to 10 --jobs 3 --out ../../media/three_proto/color_bloom.mp4
#   --ss 1 for fast previews (default 2 = 2x2 supersampling), --p.<key> <value> passes scene params, --debug 1 logs anchors
# interactive: serve render/three and open harness.html?scene=rotate_connect (scrub bar + play)
```

- `harness.html` is the standalone harness. An import map points `three` at `vendor/three.module.js` (r186, copied from
  `rare-earth-techno-remix`; MIT licence in `vendor/LICENSE.three`).
- `tools/capture.mjs` starts a tiny static server and launches `/opt/google/chrome/chrome --headless=new --use-angle=gl`.
  The page renders each frame into a `WebGLRenderTarget`, reads it back, and POSTs the raw RGBA; the server writes the PNG.
  ffmpeg comes from `~/Documents/moongazing/.venv/bin/ffmpeg`. A 10 s clip at 2x supersampling takes about 25 s with 3 jobs on the RTX 3090.
- **Use ANGLE's GL backend, not Vulkan.** Under `--use-angle=vulkan` the WebGL context was lost after the first frame
  (`CONTEXT_LOST_WEBGL`), which produced blank or repeated frames. The harness now checks every frame for blankness and retries.
  Set `ANGLE=vulkan` only to re-test.
- Rendering is deterministic: no `Math.random`, no clock. The same `t` gives byte-identical frames. Ink boil runs on twos
  (12 drawings/s) and is seeded from `t`.

## How the illusion is built

**Magic camera.** The camera is a true isometric orthographic camera: azimuth 45°, elevation atan(1/√2) = 35.264°, looking
down −(1,1,1) (`lib/stage.js`). Under this projection any two points that differ by k·(1,1,1) land on the same pixel. Every
impossible joint is two real pieces separated by such an offset.

**The Penrose circuit** (`lib/loopset.js`, constants at the top of the file):

| Leg | What it is | From → to |
|---|---|---|
| A | L girder track along +x at y = 3, on columns | S = (0,3,0) → (13.3,3,0) |
| B | 12-step stone flight on the roof of the east building, rising 3 → 6 | along −z |
| C | 12-step flight on the north building, rising 6 → 9 | along −x |
| D | L track along +z at y = 9 | (6,9,−7.3) → **E = (6,9,6) = S + 6·(1,1,1)** |

So the circuit really climbs 6 units per lap, and leg D ends six units in front of, above, and beside its own start. With
straight flights this offset can't be avoided: in exact isometric the flat legs must be longer (net xz offset = rise).
Two flat L-track legs absorb it.

The tricks that make the joint invisible:

- **Open ends.** D's end faces are not generated (`girderTrack({skipEnd})`, `Builder.obox({skip})`), and all materials cull
  back faces. Through D's open end you see the far piece (A's corner) exactly where the end cap would have been drawn.
- **Depth push** (the Monument Valley occlusion fix). Near the joint, the near piece would wrongly occlude far geometry that
  the viewer believes is in front of it (A's corner column and girders). The G-buffer vertex shader pushes such pieces back
  along the view axis by up to k·√3, so they depth-sort like the piece they visually join. Screen position is unchanged
  because the projection is orthographic. D's push ramps from 0 to 6√3 over its last 4 units (`D_PUSH0 … D_END`). Agents
  on D get the same push per frame (`loopPush`), so an agent's depth is continuous as it "teleports" from E back to S. The
  push is multiplied by `uMagic`, which fades to 0 as the camera leaves the magic angle (`Stage.setCamera`). Off-angle
  you see the true geometry.
- **Stub columns.** D's columns stop at y = 6. Seen from the magic angle that is exactly the street under the seam
  (6·(1,1,1) behind), so D appears to stand on the same bents as A. On the orbit they visibly hang in mid-air.
- **Agents teleport** from E to S (arc length wraps). Seam crossings are timed (t = 1.5 + 5k) so none happens while
  the camera is off-angle (1.8–6.4 s).

**Turntable** (clips 2 and 3). A crank-driven swing bridge sits in a gap in leg A, pivoting at (9.6, 3, 0) (a nod to
Chicago's swing bridges and to Tower 18, the Loop's junction).

- At 0° and 180° it is part of leg A, which closes the loop.
- At −90° it runs along z. Its near end meets Jade's spur in real 3D. Its far end at (9.6,3,−1.2) is exactly 2·(1,1,1)
  in front of the stoop `P2_START` = (7.6,1,−3.2), so at the magic angle the elevated bridge joins a street-level
  walkway. Jade switches from the bridge to the stoop at that point and her screen position does not jump.
- The second turn starts while the pursuer is standing on the bridge, so it carries him round into leg A, facing +x, and
  he walks off into the loop.
- Loop agents queue at the gap while the bridge is away. Everything is simulated once at init at 240 Hz (`simulate()`),
  so `draw(t)` is a pure lookup.
- The crank on the pier front turns 4× the bridge angle. Rotation uses a "clunk" ease: overshoot, then settle
  (`lib/util.js`).

## The engraving look (`lib/engrave.js`)

The renderer is deferred. A shadow pass (orthographic sun, own depth texture, 5×5 PCF) is followed by a G-buffer pass
(MRT: normal + material id, world position + view depth, sun·shadow + albedo + facade pattern + object id). A single
composite shader then draws the image at 2× and downsamples it with a tent filter.

- **Engraved lines are world-anchored but screen-uniform.** Each line family is u = dot(P, w), where w lies in the face
  plane. Its screen-space pitch is computed analytically from the camera basis (`pitchOf`), so lines stay about 5.2 px
  apart on every face, as a hand engraver would cut them, yet stick to the surfaces while the camera orbits.
- **Directions per face:**

  | Face | Family 1 | Family 2 | Family 3 |
  |---|---|---|---|
  | Walls | horizontal courses | verticals | diagonals |
  | Tops | along x | along z | diagonal |

  Family 2 switches on below tone 0.58 and family 3 below 0.26. Their coverage is capped so thin white lines survive in
  the darks (white-line engraving).
- **Line width swells with darkness.** Lines also swell along their length, vary from line to line, and break into
  flicks in the lights. A slow wave plus tremor bends them, with boil on twos.
- **Ink outlines** come from plane-distance, normal-crease, object-id and background tests at 8 taps, plus heavier
  silhouettes at 2× radius. They use their own wobbled sampling, so they sit slightly off the hatching, like a drawing.
  Pressure varies along them.
- **Facades are procedural.** Chicago windows (wide pane between two narrow sashes) and belt courses are computed in the
  G-buffer from world position and the building's box, and feed both tone and outlines.
- **Paper** gets fibres, tooth, blotches and a vignette. Ink granulates on the tooth.
- **Engraver's halo.** A thin band of paper is reserved around figures so dark agents read against hatching.
- **The drawing is unfinished.** Below y ≈ 0 and at the island's edge, each hatch line stops crisply at its own random
  threshold, and the ground plane frays into blank paper. The diorama floats, Monument Valley-style. This also hides
  where columns would betray depth.
- **Aerial perspective.** Fewer lines for whatever lies far behind the camera target.
- **Sky.** Fine horizontal lines that swell toward the top, clouds left as reserved paper, and a ringed sun
  (screen-space). The sun becomes Kandinsky rings in colour.
- **Coloured pencil.** Screen-space strokes at about 60°, with streaks, pressure and paper-tooth thresholding.
  - A second cross layer cools the shadows toward ultramarine.
  - Colour multiplies onto the paper under the ink, like a hand-coloured print.
  - Jade's materials are always coloured, and her hatching is reduced to a quarter.
  - The bloom mask is a screen-space radius from the pivot. Its front is jagged per stroke (strokes end at staggered
    lengths) and wanders with fbm.
  - Klimt gold mosaic (squares and spirals) on the tower and turntable materials.
- Palette slots are per material (`PALETTE`). Paper `#ECE7DC`, ink and orange `#FF7A1A` match `render/engine/src/core.js`
  `PAL`.

## Module interface (for `render/engine`)

Every scene module exports:

```js
export const meta;              // { name, duration, fps, width, height, loop? }
export function init(renderer, params) // -> meta. Builds the scene and engraver; params below
export function draw(t)                // renders frame at t (seconds) INTO renderer.getRenderTarget() (null = canvas)
export function anchors(t)             // screen-space positions for compositing (see below)
export function dispose()
export function createScene(defaults)  // factory, for several independent instances
export default { meta, init, draw, anchors, dispose }
```

- **`params`**:
  - `width`, `height`: output size in px. Default: the renderer's drawing buffer.
  - `ss`: supersampling factor. Default 2; use 1 for previews.
  - `style`: overrides `DEFAULT_STYLE`, e.g. `{ hatchPx, edgePx, contrast, boil, ambient, sun: [x,y,z], skyBox, aerial, paper, ink }`.
  - `penrose_loop` also takes `orbit` (bool), `orbitAz`, `orbitEl` (radians at the orbit's peak).
  - `rotate_connect` takes `bloom` (bool). `color_bloom` is `rotate_connect` with `bloom: true` and a wider camera.
- **`draw(t)`** saves and restores the renderer's render target, clear colour and `autoClear`. It writes opaque RGB with
  alpha 1. Internal targets are FloatType MRT, so the renderer needs WebGL2 (`EXT_color_buffer_float`). Modules
  `import * as THREE from 'three'`, so the engine page needs the same import-map entry, or esbuild resolving `three`
  to one copy of r186.
- **`anchors(t)`** returns:
  - `penrose_loop`: `{ seam, pivot, pixelsPerUnit, magic }`
  - `rotate_connect`: `{ jade: {x, y, depth, visible, heading, world}, pivot, pixelsPerUnit, bridgeAngle, magic }`

  `x`/`y` are output pixels from the top-left. `depth` is view-space distance (larger = farther).

## Compositing Jade (2D anime sprites with alpha) into these scenes

The placeholder figure stands where Jade's sprite would. The plan:

- **Billboard at the walkway anchor.** Scale the sprite by `pixelsPerUnit`: the placeholder is 1.2 world units tall,
  about 52 px in clip 1 and 85 px in clip 2. For "Jade large in frame" shots, push the ortho `viewH` down to 4–6 units.
  Line patterns stay screen-uniform, so the engraving survives the zoom. Anchor the sprite's feet at `anchors(t).jade`.
  Facing comes from `heading`: flip the sprite left/right in iso screen space.
- **Depth.** Two options:
  - (a) Draw her as a camera-facing textured quad inside the Three scene, at the anchor's world position, using an
    engraver material variant that samples the sprite's colour and alpha (alpha-tested in the G-buffer). The scene then
    occludes her for free: railings, door jambs, the bridge. She gets ink outlines and the halo, and her `pushConst`
    keeps her depth right across impossible joints. This is the robust option.
  - (b) Composite in 2D. The engine reads a depth/occluder matte from the scene. The cheapest version is to add an
    `occluderMask` render of the G-buffer's view depth and test `depth < anchor.depth` per pixel.
- **Across a magic joint** her world position jumps by k·(1,1,1) but her screen position does not. Use the screen anchor
  for placement and the pushed depth for occlusion, never the raw world depth.
- **Colour.** Leave her sprite in full colour (she is the only colour in the world). Optionally run it through the
  `pencil()` stroke layer and paper multiply at low strength so she sits on the same paper. Keep the engine's light
  pencil pass under about 45%: heavy stylisation broke glasses and faces in earlier projects.
- **Residue and bloom.** `bloom: {x, y, r}` is plain screen-space data, so the engine can drive it from her rewinds:
  centre on her anchor, radius from the beat map, several centres merged.
- **Pencil in her hair.** The placeholder already carries the bun-and-pencil silhouette, so the "she draws the
  connection" beat can be staged at the pivot anchor. She pulls the pencil, the crank turns, and the bloom starts there.

## Files

- `lib/engrave.js`: Engraver (shadow, G-buffer material, composite, downsample), MAT ids, palette, style.
- `lib/loopset.js`: diorama builder, Penrose path (`loopPath`), depth-push helper, turntable, spur, exit.
- `lib/figures.js`: agent and Jade placeholder rigs with a walk cycle (`pose(phase, gait, march)`).
- `lib/build.js`: flat-shaded quad/box builder with per-part ids and skippable faces.
- `lib/stage.js`: camera (magic angle, `uMagic`), projection, boil seed.
- `lib/util.js`: deterministic helpers and `clunk` easing.
- `scenes/*.js`: the three modules.
- `harness.html`, `tools/capture.mjs`: standalone harness and headless capture.
- `vendor/`: three r186.

## Known limits and next steps

- Figures are about 50–85 px tall in these framings, so sunglasses are only a few pixels. Closer shots will need a
  higher `viewH` zoom or bigger figures.
- Jade's switch at the joint is invisible: her screen position is continuous (verified frame by frame around
  t ≈ 4.9 s), while her world position jumps by 2·(1,1,1). Her cast shadow does switch from the deck to the stoop,
  which is a small tell; mark her `noShadow` near joints if it matters. She gets no depth push on the bridge, because
  nothing occluded her in this layout. A different layout may need one (`f.pushConst`).
- Cast shadows are physically real, so at the magic angle D's shadow lands on the courtyard (it reads fine). Set
  `userData.noShadow` on impossible pieces if a shadow ever gives the trick away.
- Engraving lines are about 5 px apart. At 4K, raise `hatchPx` to keep the same look. Encodes are CRF 16 with
  `-tune grain` (about 40 Mbps, because engraving is dense). Use CRF 20+ for review copies.
