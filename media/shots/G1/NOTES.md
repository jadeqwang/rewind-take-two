# G1 (141.00–144.54): Jade floats on the blank page, looks at her hand, pencil glints

**Chosen:** `take_1_engraved.mp4` (from `take_1.mp4`), in 0.00 s, out 3.54 s, rate 1.0. Matte: `take_1_matte/` (PNG per frame + `matte.mp4`).

## Keyframes (google/nano-banana-pro, 16:9 2K, ref = canon turnaround), tag `E_G1_kf`, 2 × $0.134
- `kf_a.jpg`: three-quarter front, sitting-float pose, right hand raised palm-in, a lens-flare glint on the bun pencil. **Used.**
- `kf_b.jpg`: similar, a little more diagonal, smaller in frame.
Prompt (abridged; full text in `kf_*.jpg.json`): "A young woman floats weightless in mid-air in an empty white void ... gazes at her own hand with quiet wonder ... loose messy bun with a yellow pencil ... the pencil catches a small glint ... [exact outfit] ... Background: an empty blank page of warm off-white paper (#ECE7DC) ... a few short loose fragments of black engraved hatching ... drifting like iron filings ... Full bleed ... no text."

## Video (bytedance/seedance-2.0, 720p, 5 s, first frame only), tags `E_G1_a`, `E_G1_b`, 2 × $0.75
Prompt (shot `E_G1_a` in tools/gen/shots.py): "Slow motion, weightless, she floats in mid-air and drifts very slowly upward, her body turning gently. She slowly turns her raised hand and looks at it with quiet wonder. A soft glint of light runs along the yellow pencil in her bun ... Camera: slow steady push-in. [page + face + no-text clauses]"

| take | verdict |
|---|---|
| 1 (kf_a) | **Keep.** Gentle push-in from full body to knee/waist-up, she turns her hand and studies it, glint sparkles on the pencil ~2.7–3.7 s, so it lands at the end of G1. On-model. The tiny "1420 MHz" roundel is garbled at 720p (reads like "M2L NHC"); hardly readable at this size. |
| 2 (kf_b) | Alt. Nice slow rotation and glint at 1.3–2.5 s, but after ~3.5 s the camera pushes into a near face close-up and she stops looking at her hand. Usable 0–3.5 s only. |

## Engrave pass: **helps, with a blank-page preset**
- Default settings **hurt**: the near-uniform paper gets filled with a moiré / wood-grain line texture (the flat-area fallback hatching plus amplified compression noise), which kills the "empty page".
- `--fallback-weight 0 --gamma 1.8 --contrast 0.45` **helps**: paper is clean cream with grain, Seedance's soft gray hatch fragments and gray-wash smudges become crisp black ink strokes, and Jade passes through untouched with a thin ink outline. All G engraved files use this preset.
- The BiRefNet matte is clean (hair strands, flying strap, pencil). The lens-flare glint is outside the matte, so it gets engraved and comes out softer. If the glint matters, composite raw over engraved with a dilated matte near the bun.

Cost: $1.77 (2 keyframes + 2 takes).

## v3 revision (2026-10-11, stream GO): two pencils + roundel

- **Chosen now: take 3**, `take_3_engraved_patch.mp4` (raw `take_3.mp4` = `media/gen/revA_go_G1/take_1.mp4`), in 0.00, rate 1.0, matte `take_3_matte/matte.mp4`. 1080p engrave, blank-page preset.
- Keyframe `kf_v3_a.jpg`: a nano-banana-pro edit of `kf_a.jpg` (two crossed yellow pencils through the bun, pink and pale-blue erasers up; crisp `1420 / MHz` roundel). Same Seedance prompt as take 1 plus the two-pencil clause (`tools/sectionE/go_v3.py`, shot `revA_go_G1`). Cost $0.88.
- Seedance still garbles the roundel in motion ("M20 NNc"). `tools/sectionE/patchfix.py` re-letters it in every frame: `--init 1217,403,0 --from 0 --to 92 --guess 8`. The unpatched engrave is `take_3_engraved.mp4`.
- v2 pick (take 1, one pencil, garbled roundel) is untouched.
