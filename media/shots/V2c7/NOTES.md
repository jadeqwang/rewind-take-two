# V2c7 (section C)

## Keyframes
- `kf_s` — bytedance/seedream-5-pro (refs: none)
  > It is night, drawn as an M.C. Escher wood engraving: the dark sky and shadows carved from dense black ink with fine white engraved lines, every light (headlights, streetlamps, siren strobes) a crisp white engraved starburst of radiating lines, warm off-white paper showing only in the lit areas, no gray wash, no airbrush, no photographic shading. High wide aerial view from behind and above at night: a small white sedan at the apex races toward a raised bascule bridge across the Chicago River, and behind it a vast V formation of thirty identical black 1990s government sedans drawn in solid black ink with thin white engraved highlight lines, each with a roof light bar blazing as a crisp WHITE engraved starburst of radiating lines (no color at all) fanning out across all lanes, their headlight beams converging on the white car; engraved skyscrapers on both banks of the river. Rendered as an 
- `kf_n` — google/nano-banana-pro (refs: none)
  > It is night, drawn as an M.C. Escher wood engraving: the dark sky and shadows carved from dense black ink with fine white engraved lines, every light (headlights, streetlamps, siren strobes) a crisp white engraved starburst of radiating lines, warm off-white paper showing only in the lit areas, no gray wash, no airbrush, no photographic shading. High wide aerial view from behind and above at night: a small white sedan at the apex races toward a raised bascule bridge across the Chicago River, and behind it a vast V formation of thirty identical black 1990s government sedans drawn in solid black ink with thin white engraved highlight lines, each with a roof light bar blazing as a crisp WHITE engraved starburst of radiating lines (no color at all) fanning out across all lanes, their headlight beams converging on the white car; engraved skyscrapers on both banks of the river. Rendered as an 
- `kf_n2` — google/nano-banana-pro (refs: none)
  > It is night, drawn as an M.C. Escher wood engraving: the dark sky and shadows carved from dense black ink with fine white engraved lines, every light (headlights, streetlamps, siren strobes) a crisp white engraved starburst of radiating lines, warm off-white paper showing only in the lit areas, no gray wash, no airbrush, no photographic shading. High wide aerial view from high above and BEHIND the chase at night, looking forward along a wide avenue toward a raised Chicago River bascule bridge in the distance. Every car faces AWAY from the camera, driving toward the bridge: we see their rear ends and small tail lights, their headlight beams projecting forward away from us. A small white sedan at the very front leads the chase toward the rising bridge, and behind it a vast V formation of thirty identical black 1990s government sedans drawn in solid black ink with thin white engraved highli

## Takes
- take_1: bytedance/seedance-2.0 720p 5 s, est $0.75, first frame `media/shots/V2c7/kf_n2.jpg`, state done
  > The high aerial camera glides forward behind the formation; the V of black sedans spreads wider across all lanes as they chase the white car toward the raised bridge; roof strobes flash in a ripple. Keep the black-and-white wood-engraving look of the first frame; no color anywhere. No text, no letters, no logos.

## Use in the cut

- 80.44–82.22: take_1 from 1.0 s at rate 1.0

## Judgement

OK hero: the pack fans out behind the white car, but the cars face the camera, so the bridge reads as behind them. Legible as 'they fan out behind her'.

## v3 (2026-10-11, stream TESS): the fleet as an Escher tessellation

Jade: "what if the fleet of cars pursuing her car were tesselating (and also transforming) like another Escher artwork?"
Look tests: `media/style_tests/tessellation/` (A works, B does not). Spend $0.88 (tags `revA_tess_*`) plus $0.27 for the two tests.

- **Plate:** `kf_v3.jpg` (nano-banana-pro; refs `guide_v3.png` = layout guide drawn from the module's camera, and
  `kf_n2.jpg` for style). High view looking back along Lake Shore Drive at night: empty eight-lane road, lake, park
  with lamps, skyline, a bascule truss in a bottom corner, her white car alone. `take_2` (Seedance 2.0 720p 5 s, $0.75):
  locked camera, the car holds its place, lane dashes streak, the road stays empty for all 5 s. Engraved as usual.
- **Fleet:** engine module `render/engine/modules/tessellate.js` (new). One tile shape on a square lattice, coloured
  like a checkerboard: straight sides, and a nose curve that is the tail curve moved one tile length, so it tiles
  without gaps for any nose depth. With distance: solid sedans (ink bodies, white-line drawing, roof strobes) → flat
  car tiles, black and white → plain cells → wave hatching. White tiles thin into hatching near the camera so the
  plate's road shows. The lattice advances 0.42 tile per beat, eased onto the beat.
- **Camera fit:** f 1100, pitch 21°, height 4.6 lane widths, principal point (960, 540); horizon y = 118, road edges
  at lane offsets −4.8 / +3.8. The model followed the guide to within a few px, and the take holds it.
- **In the cut** (`render/timeline/C.js`, constants `TESS*` above `CUTS`, row V2c7, and the `x.over` hook in
  `shotFor`): 80.44–82.22, take 2 from 1.0 s. Opens at 2.8× on the flat tiling (pivot 960, 330), pulls out to 1.27×
  by 81.64, drifts to 1.2×. Not mirrored: she drives south and the camera looks back north, so the lake is on
  screen-right and the park on screen-left (a mirrored version was tried for HUD legibility and dropped on rev-A's
  call). `x0: -0.5`, `parity: 1` (the front-row slot in her lane is a white tile: the one she came out of). The HUD
  sits on `TESS_CHIP`, an ink panel flush in the top-right corner (post stage, this shot only), because the lake
  behind it is bright.
- **Switch back to v2:** replace the V2c7 row with `[80.44, 82.22, 'V2c7', 1, 1.0, 1, { hero: true }]` (the comment
  above `TESS_PV` in C.js has it). Nothing of v2 was overwritten.
- **Dev harness:** `_tess_test.js` in this folder (plate + module alone); always run it with `--preview`.
- **Weak:** the solid sedans are procedural and flatter than the generated engraving; far tiles in the wide are
  small (they read as a checkerboard of car icons; the tile's car outline reads only in the zoomed opening); the plate
  is soft for the first half second (2.8× of 1080p); the HUD chip is a visible black corner panel.
