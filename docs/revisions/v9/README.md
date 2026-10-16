# v9: fixes for the headline items of the v8 AI-error audit (2026-10-15)

Next-instance handoff: `HANDOFF.md` (2026-10-16).

Spec: the Headliners table in `ai_error_audit.md` (Jade's edited version). Shared rules for the fix agents: `fix_brief.md`.
Checked by eye in a forced 540p whole-film preview (`render/engine/out/rewind/rewind_preview.mp4`, `--force`).
Round spend about $11 (project total $263.44 of $400). Not committed.

| # | Time | Fix | Where | Report |
|---|---|---|---|---|
| 1a, 9 | 0:37.96-0:40.24 | P1/P1b/P2 re-staged from D7's keyframe: Acura nose left, Jade driving | A.js `PLATE.P1`, `PLATE.P2`, P2 kenBurns | `fix_1a_9_car.md` |
| 1b | 1:06.29-1:07.16 | V2b3 re-staged: driver's seat, two pencils, headphones, hand-built matte | C.js CUTS row V2b3 (take 2, in 0.45, rate 1.5) | `fix_1b_v2b3.md` |
| 2 | 0:23.16-0:28.40 | Round 3-4 (Jade): D2+D3 rebuilt as one three.js scene, camera in the passenger seat looking left across her at the driver's wing mirror; true reflection, but the billboard lyric and the TVA 1729 plate read forward (Jade); D3 zooms into the glass. Round 5 (Jade 0:25): door mirror rebuilt to the 1999-2003 Acura TL's shape from reference photos, TVA plate fitted to the drawn plate, sedan headlights on, etch moved to the glass's top left. Round 6 (Jade): a blink at 0:24.1 and a lip press at 0:24.6-0:25.0. Round 7 (Jade 0:24, 2026-10-16: too high, looks unlike the film's other TL mirrors): mirror on its sail at the window's front lower corner, camera 23 cm forward with her plate redrawn, drawn housing card in place of the CG cap | A.js D2/D3 blocks, `tools/v9/d23/` (`build_r7.sh`), `media/shots/D23/v9r7_engraved.mp4`, `d23_tracks_r7.js` | `fix_2_round3_threejs.md` |
| 3 | 1:29.29-1:31.46 | V2f: roof layer with a solid stem into the mirror; fleet plates read forward ("TVA 1729", round 5, Jade; round 2 had them reversed) | C.js imports `tools/v4B/car/car_shot_v9.js`; `plate.js` `mirror` option | `fix_2_3_mirrors.md` |
| 4 | 2:13.6-2:14.5 | Twins coloured by identity (SAM tracking), not screen side | D.js C2a/C2b + `tools/sections/D/build_timeline.py` | `fix_4_twins.md` |
| 5 | 2:26.32-2:28.08 | Round 3 (Jade "3 legs is still there"): the take has three legs in every frame, so G3 is reframed to a waist-up close-up (scale/y keys), timing back to v8 | E.js `G_CLIPS.G3`, bloom centre | `fix_5_round3_g3.md` |
| 6 | 3:00.0-3:02.8 | Bean reflection rebuilt as a true mirror of the falling Jade; roundel re-lettered | F_edl.json + edl.py F4 | `fix_6_bean.md` |
| 7 | 2:31-2:49 | Sprite blink: frame index wrapped by clip length, not atlas cells | `render/three/lib/sprite.js` | here |
| 10 | 1:16.90-1:18.66 | V2c5: orange band painted on her right sleeve (Jade 1:17); her left upper arm is hidden. Neighbours V2c3/4/6 checked, none needs it | C.js `BLUE_ERASER` V2c5_2, `tools/v9/sleeve_band.py` | `fix_10_sleeve.md` |
| 11 | 3:38.92-3:42.78, 1:06.29-1:07.16 | O2: "RARE EARTH" lettered under the back dot (Jade 3:40); V2b3 (Jade 1:06): the same, centred and locked to the fabric, cut off by the seat | `tools/sectionF/edl.py` O2 + F_edl.json, C.js `BLUE_ERASER` V2b3_2, `tools/v9/rare_earth.py` | `fix_11_rare_earth.md` |
| 8 | various | Roundel re-lettered 1420 / MHz: C1, R2 x5, F7_02, F7_04/F7_13, F8, B2_glance; round 2: C27_V2d2 (badge repainted), F1/F7_10 | A.js, A_R2.js, _B_verse2.js, C.js `BLUE_ERASER`, F_edl.json + edl.py | `fix_8_roundel.md` |

`media/shots/F_edl.json` is gitignored: its v9 changes live in `tools/sectionF/edl.py` (regenerate to restore).
Render gotcha: the frame cache ignores module and clip changes, so use `--force` after edits like these.

Known leftovers (see each report): in D2/D3 the CG road/trees outside engrave as wavy bands (round 7 leftovers: `HANDOFF.md`); P2 is a medium shot now; Jade's hand on the wheel greys
for a few P1b frames; F4 ghosting and a dent under her chin at 3:02.4-3:03.0; C27_V2d2 has no headphones; small patch
specks on F7_02 f21/23 and F1 f70/71/84.
