# G3 (146.32–148.08): hair down, she draws ONE colored-pencil stroke in the air

**Chosen:** take 4, `take_4_engraved_soft.mp4` (raw `take_4.mp4`), **in 1.20 s, out 3.66 s, rate 1.4** (the stroke starts ~1.3 s and is complete ~3.7 s).
Matte: `take_4_matte/matte.mp4`. It contains Jade **and** the stroke, because the matte's colour cue keeps saturated pixels near her. `matte_dilated6.mp4` is the 6 px dilated and feathered version used for the "soft" engrave.

## Keyframes (nano-banana-pro 16:9 2K), tag `E_G3_kf`, 3 × $0.134
- `kf_first.jpg` (refs canon + pencil panel 2): hair down and floating, right arm out, pencil poised. **Used for all takes** (copied as `E_G3_kf_first.jpg` for round 2, because media/gen/refs caches refs by basename).
- `kf_last.jpg`: standing pose with an orange-to-blue S stroke. The pose didn't match kf_first: not used.
- `kf_last2.jpg`: nano edit of kf_first that adds an orange-to-blue loop stroke. Same pose. Used as last frame for take 2.

## Video (seedance-2.0, 720p, 5 s), 4 × $0.75
| take | shot | verdict |
|---|---|---|
| 1 | E_G3_free (first frame only; "thick coloured-pencil line ... orange ... pale sky blue") | Dramatic: one long stroke that wraps around her body, but the blue half is a **glowing cyan neon ribbon** (Seedance VFX), not pencil texture. The matte misses parts of the stroke, so the engrave pass turns them into black smears. Alt only if the engine wants spectacle. |
| 2 | E_G3_last (first = kf_first, last = kf_last2) | **Reject.** Seedance ignored the first frame: the stroke is already there at frame 0, then she redraws a second blue loop. |
| 3 | E_G3_matte #1 ("flat matte crayon line ... does not glow") | Pencil texture is good and the stroke is long, but the colours drift orange → **pink** → blue, and around 3.8 s her arm sweeps across her face. Second choice. |
| **4** | E_G3_matte #2 | **Keep.** One clean C-shaped arc with crayon grain, orange outer edge with pale-blue inner edge, no glow. On-model. The stroke is modest in size, and the gradient runs across the stroke's width more than along its length. |

Prompt (E_G3_matte): "Slow motion, weightless, she floats in mid-air, her long loose hair drifting. She draws ONE single slow curved stroke in the empty air with the yellow pencil, her arm moving in one smooth graceful arc. The pencil tip leaves a flat matte coloured-pencil line like a crayon mark on paper, grainy waxy texture, vivid orange where it starts, fading to pale powder blue toward the pencil. The line is flat and does not glow: no light, no neon, no sparkles, no glow, no particles. The line stays still in the air after it is drawn. Camera: very slow push-in." + page/face/no-text clauses.

## Engrave
- Blank-page preset (as G1/G2) with the default ink outline: the stroke gets a black cartoon outline (`take_4_engraved.mp4`). That makes it look inked, not pencil.
- `--outline 0` with the tight matte: speckled black fringes along the stroke's soft edge.
- **`--outline 0` + 6 px dilated matte (`take_4_engraved_soft.mp4`): best.** The stroke reads as pure coloured pencil on clean engraved paper. Because the background is near-blank paper, the dilated halo is invisible.
- The "engraving blooms into coloured pencil" part of G3 is left for the engine (`--bloom`). The matte can seed it, but there is no separate stroke-only mask.

Cost: $3.40 (3 keyframes + 4 takes).

## v3 revision (2026-10-11, stream GO): rainbow pencil, rainbow-cored stroke

- **Chosen now: take 5**, `take_5_engraved_soft_patch.mp4` (raw `take_5.mp4` = `media/gen/revA_go_G3/take_2.mp4`), **in 1.3, rate 1.6** (out 4.12; the stroke starts at 1.3 s and is about 85% drawn at the cut), matte `take_5_matte/matte_dilated9.mp4` (9 px dilated at 1080p, feathered; the stroke is inside it).
- Keyframe `kf_v3_first2.jpg`: edit of `E_G3_kf_first.jpg` (pencil with a pale-blue eraser and a rainbow point; crisp roundel).
- The stroke is one C-shaped coloured-pencil band whose colours run orange, yellow, green, blue, violet across its width. The prompt asked for one thin line changing colour along its length; Seedance drew bands both times.
- Engrave: blank-page preset, then `--outline 0 --matte-in matte_dilated9.mp4` (same recipe as take 4's soft version). Roundel ("14ZR MITS" in the take) re-lettered with `patchfix.py --init 1481,543,84 --from 20 --to 110 --guess -10`.
- Rejected: `media/gen/revA_go_G3/take_1.mp4` (a wide rainbow arch already present in frame 0). v2 pick take 4 (orange-to-blue stroke, pink eraser) is untouched.
- Cost: 2 keyframe edits + 2 takes = $1.77.
