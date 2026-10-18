# Style stills v8: Chinese watercolour (look test, 2026-10-18)

Stills only. Nothing is wired into the film and no video was made. The question: can a painted Jade bring back what
the original watercolour singing shots had (the calm, slightly sultry painted portrait whose style mismatches the
engraved plates) without losing her likeness the way the earlier style test did?

**Start with `contact_sheet.jpg`.** There is one block per shot (S1 hair up with pencils over `plate_close_1`, V3S hair
down over `plate_truth_1`). The top row shows the source photo, the v7 first frame, the original watercolour (v4 take at
1.0 s), then each style on its plate. The bottom row shows the face at one scale under each. `_faces.jpg` has the face
crop of every still made (40), for checking.

Sources: the v7 outpaint canvases (`media/sing/outpaint/v7/S1_nbp_2_merged.png`, `V3S_nbp_5_merged.png`). Every pixel the
selfies show is hers; only the shoulders are outpainted. S1 got 120 px more jacket at the bottom for the wider framing.
Placement uses v7's geometry at 0.88x face height ("a little wider"), with the eyes on v7's x.

Script: `tools/sing/style8.py` (prep / gen / fix / extend / lock / metrics / matte / comp / faces / sheet; venvs in its
docstring). Every still has a `<key>.json` with its prompt, parent and request.

## Routes

- **raw**: one model repaints the photo. nbp = nano-banana-pro, gpt = gpt-image-2.5-flare, sdr = seedream-5-pro.
- **fix** (model alternation, the route that worked): nano-banana-pro paints, then gpt-image-2.5-flare gets the painting
  plus her photo and is asked to correct only the face's proportions and features to the photo, keeping the painting.
  `__fixx` keeps the painting's expression and light. `__fixx2` also says her hair is black.
- **lock** (geometry): the painted face is warped onto her photo's MediaPipe landmarks (thin-plate spline, feathered to
  the face; lips excluded except the corners, so a closed painted mouth is not stretched open). It moves at most
  7-16 px. It corrects proportions, but not what actually makes the nbp faces look like someone else (pursed closed
  mouth, older or doll-like modelling, heavy flush). Its numbers flatter it, because it is scored on the points it was
  warped to.
- **extend**: glow_V3S was reframed tighter by nano-banana and ended 190 px above the frame bottom. nano-banana painted it
  on downward, and the still's own pixels were pasted back above the seam (invisible at full size).

## The stills on the sheet

| still | what it does |
|---|---|
| **glow_S1__nbp_1__fixx2** | Loose watercolour with ink contour: warm amber light from the left, lavender shadow side on the jacket, flush, slightly lowered lids. Pencils right (pink left, blue right), patch clean. The bun keeps an orange light-wash streak. |
| wash_S1__sdr_1 | Soft wet watercolour on rice paper with the **strongest warm side light** (a real light/shadow split across the face), jacket dissolving into paper. The face keeps a lot of photo texture, so it reads half-photo. The top of the hair is a pale wash that goes grey over the plate. |
| gongbi_S1__nbp_1__fix | Refined light-colour gongbi: fine even line, flat pale washes, ribbed turtleneck. The cleanest and most graphic. Hair is grey ink, so it reads grey over the plate. Flat, neutral light (no sultry light). |
| xieyi_S1__nbp_1__fix | Ink-wash xieyi jacket (broad grey strokes, vermilion bands, azurite dab) with a controlled face. The splashy flyaways look noisy over the engraving. |
| glow_S1__nbp_1 (before fix) | Shown for contrast: the mood is right (dreamy, heavy-lidded, closed soft lips), but it is not her: rounder face, glossy pursed lips, heavy flush, brown hair. |
| **glow_V3S__nbp_1__fixx2__ext** | **Closest to the original watercolour's feel**: warm glow from the left on the face and hair, soft calm gaze, soft lips, painterly jacket. Hair is black with a warm sheen. |
| wash_V3S__nbp_1__fix | Delicate watercolour with ink line, good likeness, neutral light. Her expression stays the photo's slightly tense, singing face. |
| gongbi_V3S__nbp_1__fix | Gongbi line with pale washes, good likeness. The hair reads grey over the plate. |
| xieyi_V3S__nbp_1__fix | Bold brush jacket. **The patch text is garbled.** The face is near-photographic. |
| glow_V3S__nbp_1 (before fix) | Shown for contrast: the most sultry still of all, but brown hair, a heavier face and closed full lips. Its bottom is cut (unextended). |

Not on the sheet but in the folder: every raw nbp/gpt/sdr still per style, the `__lock` versions, the plain `__fix` and
`__fixx` of glow, and `wash_S1__sdr_1__fix`. As before, the gpt-only stills look like a filter, especially gongbi.
seedream's gongbi_V3S is lovely as a painting but whitens and smooths her into someone younger.

## Likeness numbers

These are MediaPipe landmarks on each still against her photo (the outpaint canvas). NME is the mean landmark error after
similarity alignment, as a % of her eye distance. The other columns are each ratio's % change against the photo:
io/fw = eye distance / face width; fw/fh = face width / forehead-to-chin (a negative value would mean slimmed); eye w =
eye width / eye distance (positive = enlarged); eye h = eye opening / eye width; jaw = gonial width / face width; nose
and mouth = width / eye distance.

| still | NME % | io/fw | fw/fh | eye w | eye h | jaw | nose | mouth |
|---|---|---|---|---|---|---|---|---|
| glow_S1__nbp_1 (raw) | 1.68 | -3.8 | +7.3 | +0.2 | -9.5 | +0.6 | -2.2 | -6.7 |
| **glow_S1__nbp_1__fixx2** | 0.95 | -1.3 | +3.3 | -1.9 | -4.3 | -0.2 | -1.2 | -4.5 |
| wash_S1__sdr_1 | 1.23 | +0.4 | +1.3 | -3.6 | +0.6 | -2.5 | -0.0 | -2.3 |
| wash_S1__nbp_1 (raw) | 1.66 | -0.0 | +4.8 | -2.4 | -6.6 | +0.0 | -1.6 | -4.9 |
| wash_S1__nbp_1__lock | 0.87 | -2.2 | +2.7 | -0.2 | -2.1 | +0.7 | +3.0 | +1.5 |
| gongbi_S1__nbp_1 (raw) | 1.32 | +0.1 | +3.7 | -2.4 | +2.1 | +0.5 | -3.4 | -5.2 |
| gongbi_S1__nbp_1__fix | 0.87 | -1.4 | +1.5 | +0.2 | -4.0 | +1.4 | +2.2 | -1.0 |
| xieyi_S1__nbp_1 (raw) | 1.68 | -3.1 | +7.3 | -2.4 | -4.7 | +0.4 | -1.5 | -7.3 |
| xieyi_S1__nbp_1__fix | 1.03 | -1.8 | +3.6 | -1.7 | +10.9 | +1.3 | -1.5 | -2.3 |
| wash_S1__gpt_1 (gpt only) | 0.77 | -0.4 | +2.3 | -1.0 | +0.6 | -0.4 | +1.5 | +0.3 |
| glow_V3S__nbp_1 (raw) | 1.03 | +0.2 | +0.2 | +3.5 | -0.0 | +1.8 | +0.3 | -4.0 |
| **glow_V3S__nbp_1__fixx2__ext** | 1.28 | +0.7 | +1.7 | +4.7 | -1.3 | +0.7 | -0.4 | -3.6 |
| wash_V3S__nbp_1 (raw) | 1.19 | +2.2 | +0.1 | +0.1 | -7.7 | +0.9 | -1.2 | -6.5 |
| wash_V3S__nbp_1__fix | 1.54 | +1.0 | -0.2 | +0.3 | +0.0 | +0.4 | -0.5 | -5.5 |
| wash_V3S__nbp_1__lock | 0.74 | +0.6 | -1.1 | +0.9 | +0.7 | +0.5 | +0.1 | -3.5 |
| wash_V3S__sdr_1 | 1.03 | +2.0 | -1.0 | +0.6 | +4.4 | +0.3 | +0.7 | +0.3 |
| gongbi_V3S__nbp_1 (raw) | 1.26 | -0.3 | +2.0 | +4.0 | -3.1 | +1.0 | -2.2 | -2.6 |
| gongbi_V3S__nbp_1__fix | 1.21 | -0.2 | +0.9 | +1.7 | +2.2 | +0.1 | -1.0 | -4.7 |
| xieyi_V3S__nbp_1 (raw) | 0.94 | -1.7 | +2.6 | +0.5 | -1.0 | -0.1 | -3.9 | -5.7 |
| xieyi_V3S__nbp_1__fix | 1.23 | +1.0 | +0.0 | +0.8 | -1.9 | -0.3 | -1.9 | -4.3 |
| wash_V3S__gpt_1 (gpt only) | 0.87 | +0.1 | +1.4 | -0.1 | -3.2 | -0.2 | +0.2 | -3.5 |

All 40 are in `likeness.tsv` / `likeness.json`. How to read the numbers:
- **No still is slimmed.** fw/fh is 0 or wider everywhere. The +3 to +7% on S1 comes mostly from the mouth closing or
  narrowing, which shortens the forehead-to-chin height, not from a wider face (io/fw stays within about 2-4%).
- **Mouths are drawn narrower** (-2 to -7%), most of all by nano-banana. The fix route brings S1 back to -1 to -4.5%.
- **Eyes:** glow_V3S's fixed still is +4.7% eye width (slightly larger), the most of the picks. Worth Jade's eye.
  eye h is the lid opening: glow's -4 to -10% is the heavier, calmer lid that was asked for, not a shape change.
  xieyi_S1's fix opened the eyes +11%.
- **The numbers are weak judges.** MediaPipe pulls every face toward an average, so the drifted raw nano-banana faces
  still score only 1-1.7% NME, and the fix route that visibly brings her back sometimes scores *worse* (wash_V3S,
  glow_V3S). The landmarks miss age, lip shape, gloss, flush and texture, which is where nano-banana drifts. Trust the
  bottom row of the sheet over the table.

## Favourites

1. **glow_V3S__nbp_1__fixx2__ext** (V3S). It has what Kenton said v7 lacks: warm light from one side, a soft flush,
   calm lids, soft lips, and a painted Jade who visibly does not belong to the engraving, while still looking like her
   (fix route plus the black-hair instruction). This is the one to show first.
2. **glow_S1__nbp_1__fixx2** (S1), the same recipe. The likeness is good, the pencils are right, and the look is loose
   watercolour with ink contour. The mood is a little weaker than V3S because the photo's open, singing mouth survives
   the fix.
3. **gongbi_S1__nbp_1__fix**, if Jade wants something more graphic and "Chinese painting" than soft watercolour. It is
   refined, clean, and an honest likeness, but neutral rather than sultry.

The general finding: **paint with nano-banana-pro, then correct the face with gpt-image-2.5-flare against her photo.**
That is the likeness-protecting route that works. Asking the painter for the mood (glow prompt) and the corrector to
keep that expression gives the closest match to the original watercolour. The landmark lock alone is not enough.

## Weak list

- **Resolution:** every fixed still is gpt-image's 1536x1024, scaled about 1.1-1.5x in the comp. That is soft at 1080p.
  A chosen still needs an upscale (or a 2K re-paint of the face region) before it goes to Seedance.
- **Hair over the plate:** pale ink-wash hair edges matte semi-transparent, so the hair reads grey or thin over the
  engraving. This is worst in both gongbi stills, xieyi_S1 and wash_S1_sdr. It needs a darker hair edge or a matte
  choke on hair.
- **glow_S1 fixx2:** an orange light-wash streak at the top of the bun and on the left temple. It reads as bleached hair.
- **glow_V3S fixx2:** eye width +4.7%, and the lower face is a bit longer (nose-to-chin / face height +2.9%). Check it
  against her photo.
- **xieyi_V3S fix:** the "1420 MHz" patch text is garbled. xieyi_V3S's face is close to a photo inside a brushed jacket.
- **wash_S1__sdr_1:** a semi-photographic face and a pale hair top. It is still the best light of any S1 still.
- **The sultry gaze only partly lands:** both selfies are mid-song with the mouth open and the brows slightly raised.
  Without re-posing (not done, for likeness), the 15-20° turn and chin-down of the original watercolour are absent.
- The source-photo tile on the sheet has black side padding (the photo is narrower than its crop box).
- The xieyi direction never fully worked: the jackets are good, but the flyaways and splashes get noisy over the
  engraved plate.

## Animation risk (if a painted still is chosen)

The original watercolour's chin distortion came from Seedance re-inventing a painted face it cannot track as well as a
photo. To reduce it:
- **Feed Seedance the fixed still at full resolution** (upscaled first). Soft inputs invite the model to redraw the jaw.
- **Lock the face in the prompt**: "her face, jaw and chin keep exactly the shape of the first frame; only the lips,
  lids and brows move; head movement is a small rigid turn". Prefer the takes with the smallest jaw-landmark variance
  (jaw/fw and lower/fh per frame from `look.py`-style tracking). That variance is a measurable reject criterion.
- **Keep the painted face mostly static and let the hair and jacket carry the motion**: modest head motion (v6b-level
  rather than v7's expression range) and wind in the hair.
- **Fallback:** after the take, re-apply the landmark lock per frame to the jaw contour only (the `lock` code with the
  lips excluded, run on video frames against the first frame's jaw), or composite the first frame's chin and jaw over
  frames where it drifts, with the mouth left free. The lock is cheap and has no model cost.

## Spend

34 billed calls, **$5.63** (list-price estimates). Tags: style8_wash/gongbi/xieyi $0.82 each, style8_glow $0.27,
style8_fix (13 gpt-image corrections) $2.77, style8_extend $0.13. Another 9 calls failed and were not billed
(6 seedream size errors, 3 seedream server errors). The project total was $378.79 of the $600 cap at the end of this run.

## Files (all in `media/sing/style/v8/`)

- `contact_sheet.jpg` (4948x1730), `_faces.jpg` (every still's face at one scale)
- `<key>.png|jpg` + `<key>.json` for each still. Raw keys are `<style>_<shot>__<model>_1`. Derived keys add `__fix`,
  `__fixx`, `__fixx2`, `__lock`, `__ext` (`__ext_raw.png` is nano-banana's unmerged extension).
- `<key>_comp.jpg`: each still on its plate, in the 2576x1449 first-frame crop.
- `_matte/<key>.png` (BiRefNet alpha), `_matte/comp.json` (placement scale, still bottom in the frame)
- `likeness.json`, `likeness.tsv`
- `_in/`: the model inputs (padded canvases). The source photos are untouched.
