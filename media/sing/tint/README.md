# Tint match: updo photo with the hair-down tints

Jade asked (2026-10-16) for the makeup and skin tint of `inputs/jade_ref_image_music_video_long_hair.png` (hair down: neutral skin, little blush, muted lips) on `inputs/jade_ref_image2_music_video_pencils.png` (updo with pencils: rosy flushed cheeks, pinker glossy lips, warm glowing skin). Only the tint was to change. These are candidates for her to look at and are not wired into anything. Neither input was modified.

Script: `tools/sing/tint_match.py` (`gen`, `local`, `check`). Sheet: `contact_sheet.jpg`. The top row shows the full frames and the bottom row shows face crops at the same scale. Numbers are in `metrics.json`.

**Pick: `pencils_tint_pick.png`**, a copy of `local_b.png`.

## Spend
Total: **$0.69** (list-price estimate) against the $1.50 cap. That was 4 calls, all tagged `tint_*` in `media/genlog.jsonl`:
- nano-banana-pro: 2 calls at $0.134 each.
- gpt-image-2.5-flare (high): 2 calls at $0.213 each.

The local pass cost nothing.

## Candidates

| file | how | likeness | tint | verdict |
|---|---|---|---|---|
| `local_a.png` | local LAB pass with no model: skin a\*/b\* matched to the target's means, a\* spread compressed, lips moved to the target lips, highlights rolled off by 50% | exact: every pixel outside the skin/lip masks is bit-identical (pencils, glasses frame, hair, jacket, background all 0.0 change) | skin a\*b\* matches the target (Δ 0.02); lips Δ 0.5 (was 5.2) | OK. Some cheek blush is left on the cheek on the viewer's left. |
| **`local_b.png`** | same as local_a, plus "flush" removal: 80% of the blotchy a\* excess over the face-scale trend is taken out | exact (same as local_a) | skin Δ 0.4, lips Δ 0.5; the cheeks end up a touch more even than the target's | **PICK.** The flush on the cheeks and nose is gone, the lips are a muted rose, the freckles and texture are untouched, and the result still looks like a photo. |
| `nbp_1.png` | nano-banana-pro, both photos given as references | landmarks within the noise floor (1.2 / 4.5 px) | skin and cheeks close; lips pushed to a flat beige-mauve (Δ 8.5, further off than the original) | REJECT. The wall, the couch and the skin are posterized into contour bands, and her skin is smoothed. |
| `nbp_2.png` | nano-banana-pro, take 2 (asked for no banding and rosy-peach lips) | 0.8 / 2.8 px | lips still beige (Δ 6.9) | REJECT. The banding is the same, and there are blue-white glints on the forehead and nose. |
| `gpt_1.png` | gpt-image-2.5, both photos given (the source was cropped to 3:2, rows 40–1005) | 1.6 / 3.8 px | barely moved: the blush and lip pink are still there (lips Δ 3.4) | REJECT. Too little change, and the skin is smoothed and the freckles softened. |
| `gpt_2.png` | gpt-image-2.5, take 2 (asked for a "clearly visible" change, no smoothing) | 1.7 / 4.3 px; the features, glasses, both erasers and the patch look right by eye | blush clearly reduced, lips muted (Δ 4.3) | RUNNER-UP, the best model edit. The skin is still smoothed and the freckles softened. It is a 3:2 re-render, so the bottom of the jacket is cropped and every pixel is regenerated. |

## Likeness check
Each candidate was mapped onto the original by its eye, nose and brow landmarks (a similarity fit). The table reports the mean and max movement of all 478 face landmarks, in original pixels; the inter-ocular distance is 248 px.

Expect a shift of about 1 / 3.3 px even when nothing moved. The local passes do not move a single pixel of geometry, yet they read about 1.0 / 3.3 px, because that is just the detector re-running on recoloured skin. All the model edits fall within or just above that noise floor, so none of them visibly changed her features. They were rejected for image quality (the nano-banana banding) and skin smoothing (both gpt takes), not for geometry.

## Notes
- The masks (`_in/local_b_mask.png`) cover the face oval, the neck below the jaw and the ears. They exclude the eyes, brows, glasses frame, dark hair and lit hair wisps.
- To push the local pass further or pull it back, re-run `local` with a different `--flush`, `--blush`, `--lips` or `--shine`. A `--shine` of 0.8 made the nose highlight look retouched, so it is left at 0.5.
- The scratch files in `_in/` are the aligned candidates, the masks, the gpt 3:2 input crop and the full-resolution face strip.
