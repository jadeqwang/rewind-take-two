# G2 (144.54–146.32): HERO: she pulls the pencil, her hair falls loose (slow motion)

**Chosen:** take 4, `take_4_engraved.mp4` (raw `take_4.mp4`, matte `take_4_matte/`), **in 0.46 s, out 2.24 s, rate 1.0**.
Pull timing in take 4 (clip seconds): her hand starts sliding the pencil out at 0.25, the pencil clears the bun at 0.58, the bun releases at 0.83, the hair is fully loose at 1.0, and the fan peaks over 1.6–2.6.
With in 0.46: the boom (144.54) lands mid-yank, the pencil comes free at ≈144.66, the hair drops at ≈144.91–145.08, and the fan opens through to the cut. If the engine wants more of the fan in 1.78 s, use rate ≈1.2 (out ≈2.6).
Comparison sheet of all takes: `G2_takes_sheet.jpg`. Per-take 0.25 s strips: `take_N_strip.jpg`.

## Keyframes (nano-banana-pro 16:9 2K), tag `E_G2_kf`, 3 × $0.134
- `kf_first_b.jpg`: sitting-float, knee-up, right hand pinching the pencil in the intact bun (refs: canon turnaround + pencil sheet panel 1). **Used for takes 1, 2, 4.**
- `kf_first_a.png`: full body, more upright, hand on the pencil (take 3).
- `kf_last_a.jpg`: same sitting-float pose, hair down and floating, pencil in her right hand in front of her chest (refs: canon + panel 3). Used as `last_frame_image` for takes 1 and 4.

## Video (seedance-2.0, 720p, 5 s), 4 × $0.75
Common prompt: "Slow motion, weightless, she floats in mid-air. Early in the shot, within the first second, she pulls the yellow pencil out of her bun in one smooth motion; the bun comes undone and her long black hair falls loose and unfurls slowly, spreading out weightlessly to waist length, floating and rippling as if underwater for the rest of the shot. She brings the pencil down in front of her chest and looks at it." + camera + page/face/no-text clauses.

| rank | take | shot name | first / last frame | camera | verdict |
|---|---|---|---|---|---|
| **1** | 4 | E_G2_bl_orbit | first_b / last_a | slow low-angle orbit | **Best.** Closest framing, clean early pull (0.25–0.6 s), biggest and most readable hair release, ends in the landed pose. On-model, roundel reads "1420 MHz". Weak spots: the raised hand and pencil touch or leave the top edge around 0.4–1.1 s, and the matte has a small hole in the hair mass around 1.2 s. |
| 2 | 1 | E_G2_bl_push | first_b / last_a | slow push-in | Very good. Pull at ~0.5–0.75 s, then an exaggerated "explosion" of hair (1.25–2.25 s) before it settles long. Wider, so the pencil stays in frame. Alt: in_sec 0.55, rate 1.0. |
| 3 | 2 | E_G2_b_orbit | first_b / – | low orbit | Good. Pull at 0.6–0.9 s, hair loose ~1.0 s. The camera swings to a frontal low angle and the pencil is cropped at the top 1.0–1.6 s. Ends with her looking at the pencil. |
| 4 | 3 | E_G2_a_push | first_a / – | push-in | **Reject for hero.** The pull reads fine, but the "1420 MHz" sleeve roundel morphs into garbage text ("TADS PAG") from ~1.5 s on and stays visible at medium-close size. |

## Engrave
Same blank-page preset as G1 (`--fallback-weight 0 --gamma 1.8 --contrast 0.45`): it helps by turning the drifting hatches into crisp ink on clean paper. Default settings fill the empty paper with moiré (tested on take 2: rejected). All four takes have engraved versions, mattes and `_sbs` previews.

Cost: $3.40 (3 keyframes + 4 takes).

## v3 revision (2026-10-11, stream GO): two pencils, the rainbow one is pulled

- **Chosen now: take 5**, `take_5_engraved_patch.mp4` (raw `take_5.mp4` = `media/gen/revA_go_G2/take_2.mp4`), **in 0.68, rate 1.15** (out 2.73), matte `take_5_matte/matte.mp4`. 1080p engrave, blank-page preset.
- Keyframes: `kf_v3_first3.jpg` (edit of `kf_first_b.jpg`; the model kept drawing a third pencil, so the last one was removed with an OpenCV inpaint) and `kf_v3_last2.jpg` (edit of `kf_last_a.jpg`: the pencil in her hand has a pale-blue eraser and a rainbow point). Prompt: shot `revA_go_G2` in `tools/sectionE/go_v3.py`.
- In the take: her hand slides the pale-blue-eraser pencil out (0.4-0.85 s), the pink-eraser pencil slips out of the collapsing bun (0.92 s) and drifts off to the right (gone by ~2.4 s), the hair is loose by 1.5 s and fans 2.0-2.75 s. Framing is knees-up, a little wider than take 4.
- Roundel: Seedance wrote "1AZO NAz"; re-lettered with `patchfix.py --init 1315,558,40 --from 0 --to 80 --guess -18`.
- Rejected: `media/gen/revA_go_G2/take_1.mp4` (three pencils in the bun). v2 pick take 4 (one pencil) is untouched; its own roundel reads "1420 MHz" without help.
- Cost: 3 keyframe edits + 2 takes = $1.90.
