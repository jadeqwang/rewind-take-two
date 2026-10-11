# 0:13, the Bean: start wide, then move in (plan for Jade)

## Execution (v4B-bean; keep current; resume from here)

Jade approved at 19:20 ("bean update looks good, all those choices are fine in previz"; verbatim in
`docs/revisions/v4/B_progress.md`): centred, head in the arch; land 13.92; pedestrians; no Seedance comparison.
Cap $5, tag `v4B_bean_*`. Singer is now v4: `media/sing/S1/v4_sync_1080.mp4` + `v4_sync_1080_matte/`.

| Step | Status |
|---|---|
| 1. Wide plate (nano-banana-pro 4K, outpaint of `plate_close_1.jpg` pasted unscaled at (1350, 106) in a 5504x3072 canvas). Script `tools/v4B/bean/plate.py` (`guides` free, `gen A|B` paid). Guides written: `media/sing/plates/plate_wide_v4_guide_{A,B}.jpg`. Candidates go to `media/sing/plates/plate_wide_v4_<A|B><i>.png` + `.json`. | generating B1, A1 (17:50 file clock) |
| 2. Three-plane push in `render/timeline/A.js` (S1 + `A_S1_lyric` only) | not started |
| 3. 540p check via `render/timeline/_A_test.js`, stills 12.62 / 13.04 / 13.33 / 13.5 / 13.92 / 15.5; R4 and C2 | not started |
| 4. Hand-over: `media/reviews/v4/B/0013_bean_wide.mp4`, `0013_bean_wide.jpg`, `docs/revisions/v4/fragments/bean.json` | not started |

Spend so far: $0.

---

The plan as approved follows.

Status: **plan and free previz done, waiting for Jade's go-ahead.** Nothing was spent and no existing file was
edited. Written by `v4B-bean` (sub-agent of `v4-B`), 2026-10-11.

> 0:13 - I realize we're at the bean, but it's not super obvious unless you already know. maybe we can start
> further away and then zoom in?

**Watch:** `media/reviews/v4/B/plans/bean/previz.mp4` (960×540, 12.1–16.6 s, with sound). The wide plate in it is a
crude stand-in assembled from old plates, and it is labelled as one. Everything after the move lands is the v3 shot.

![start, hold, mid-move / mid-move, landed, later](../../../../media/reviews/v4/B/plans/bean/previz_sheet.jpg)

## Why v3 doesn't read

In v3 the Bean is bigger than the frame: about 1.3 frame widths across, with only its upper middle on screen. No
outline, no arch underneath, no ground, nothing for scale. So it reads as a fisheye lens.

## The wide frame (first beat of the shot)

- The **whole Bean**, 62 % of the frame width, sitting on the plaza: the kidney outline with clear sky round it
  and the arch underneath. Those two are what make it the Bean in under a second.
- The skyline twice: dark towers standing **behind** it and the bright city bent **across** its mirror.
- A few tiny pedestrians at its foot (a person is a sixth of its height) and lamp posts, for scale.
- **You**, small at bottom centre, cut at the chest by the frame like a presenter near the lens: 42 % of your v3
  size, your head inside the arch.

## The move

| Song time | What happens |
|---|---|
| 12.60 (cut, beat 8:1) | Wide. It creeps in 2 % so it is never frozen. |
| 13.04 (beat 8:2) | The push starts. "The" (13.20) is cut into the Bean while it is still nearly whole. |
| 13.48 (beat 8:3) | Fastest point. "night" (13.42) appears on the way in. |
| 13.92 (beat 8:4) | Lands on the v3 framing, exactly as "before" (13.89) is sung and cut in. |
| to 16.14 | v3's slow push, unchanged. The cut to the reflection stays at 16.14. |

It is honestly a **zoom with a short crane-down**, not a dolly: at the end you are about 0.6 m from the lens and
the Bean about 9 m, so a dolly that doubled the Bean would pass through you. To keep it from feeling like a zoom on
a flat picture, three planes move at three rates: you grow 2.4× from the bottom edge, the Bean and plaza grow 2.1×
from a point near the Bean's top (so the Bean sinks behind you as you rise), and the towers behind grow only 1.5×.

**The lyric** "THE NIGHT BEFORE" is one layer fixed to the Bean's surface. It rides the Bean through the move, each
word appears on its sung onset as now, and nothing is shown twice.

**The end of the move is the existing close plate**, so the landed frame is pixel-for-pixel v3's framing and still
rhymes with V3S at 2:34.

## What gets generated

One new picture: the **wide plate**, painted outward from the close plate (nano-banana-pro, 4K, 16:9). The close
plate is placed at its real size inside a 4K canvas and the model paints the rest of the Bean, the plaza and the
towers round it; the original pixels are then laid back in. Because the wide plate contains the close plate, the
push ends in register and stays sharp (the close region is 2570 px across for a 1920 px frame; a 2K plate would be
soft). If the model will not keep the inset, the fallback is a freely painted wide plate cross-dissolved to the
close plate inside the fast part of the move. The previz already works that way, and it holds.

| Item | Cost |
|---|---|
| Wide plate, 4 candidates at 4K ($0.24 each) | $0.96 |
| Up to 2 corrective edits | $0.48 |
| Optional: 2 Seedance takes of a real camera move between the two plates, to compare (720p, 5 s, $0.75 each) | $1.50 |
| **Total** | **$1.44, or $2.94 with the comparison** (budget $10) |

## Risks

- The painted Bean comes out too round or loses the arch. Four candidates; `plate_sane_1` goes in as a shape reference.
- Your pale jacket nearly vanishes against bare white paving (seen in the previz). The plate needs mid-tone
  hatching behind your shoulders, with the bright pool of light further back.
- The engine has no motion blur and the push peaks at 7 % growth per frame for about 8 frames, so fine hatching may
  shimmer. If it does, the background move is pre-rendered with blur (free) and played as a clip.
- At the start your face is 13 % of the frame height, so the lips on "The" are tiny. By "night" you are at 66 %.

## Questions for Jade

1. **Where you stand in the wide.** Centred with your head in the arch (previz), or off to one side with the
   camera swinging round to centre you? Centred is simpler and lands cleaner in under a second.
2. **When it lands.** On "before" at 13.92 (previz), or one bar later at 14.36: a longer look at the Bean, but you
   stay small through "The night before".
3. **People on the plaza.** A few tiny pedestrians for scale (recommended), or empty, as in a dream?
4. **The $1.50 Seedance comparison:** only if the move still feels flat to you in the previz.

---

## For the build (v4-B and v4-A; not part of the two-minute read)

**Stills:** `media/reviews/v4/B/plans/bean/previz_{start_12.62,hold_end_13.04,mid_13.33,mid2_13.50,land_13.92,end_15.50}.jpg`,
`previz_sheet.jpg`, `standin_wide_plate.jpg`. **Script:** `tools/v4B/bean/previz.py` (PIL, numpy, PyAV; no engine,
no GPU; about 55 s; `--late` renders the 14.36 landing as `previz_late.*`). The singer is two constants at the top
(`SINGER`, `SINGER_MATTE`).

**Numbers (1920×1080 design px; one eased progress `e(t)`, scales log-interpolated):**

- `e`: 0 at 12.60, 0.03 at 13.04, then `0.03 + 0.97 * (1 - (1 - smoothstep(x))^1.4)`, x from 13.04 to 13.92.
- Her: scale `0.42^(1-e)` about (960, 1080). Head top y 667 at the start, 97 landed.
- Bean plane (Bean, plaza, arc lyric): scale `0.467^(1-e)` about (955.6, 112.5). Bean top y 60 at the start, 0 landed.
  The v3 frame sits in the wide frame at x 510–1406, y 60–564.
- Far plane (sky, towers): grows `1.5^e`, its horizon locked to the plaza's horizon (y 640 in the wide frame). It
  grows slower than the Bean, so the Bean always covers the hole it leaves; no inpainting.
- On top of all three, v3's `S1_PUSH(1.0, 1.04)` over the shot.
- Values at 13.20 / 13.33 / 13.48 / 13.60 / 13.75: her 0.48 / 0.57 / 0.73 / 0.86 / 0.97; Bean 0.52 / 0.61 / 0.76 / 0.87 / 0.97.
- Engine: a similarity about fixed point c is `scale: s, x: (c.x - 960) * (1 - s), y: (c.y - 540) * (1 - s)`
  (same convention as `C4_PUSH` in `A.js`); scale, x and y accept functions of layer time.
- Layer order: far plate, Bean-plane plate, the take full frame (fades in over 4 frames at landing, so the live
  headlights return), the two arc layers (Bean-plane transform in place of `S1_PUSH`), her by matte. v3's stack
  after landing is unchanged.

**Wide plate recipe.** Canvas 5504×3072. Paste `media/sing/plates/plate_close_1_crop.jpg` (2576×1449) unscaled at
(1461, 172). Bean outline in the canvas: about x 1046–4458, top y 172, foot about y 2090; plaza horizon y 1835; she
later covers x 2180–3330 below y 1900. References: the canvas (to extend), `plate_sane_1.jpg` (shape of the lower
body and arch only). After generation: lay the close plate's pixels back inside the rim with a feather; cut the
Bean and plaza from the sky locally (BiRefNet, as `tools/sing/wc_post.py`) for the far plane. Draft prompt, to go
after the `ENGRAVING` block of `tools/sing/paint.py`:

> Extend this picture outward to fill the whole canvas; do not change anything inside the existing picture. It is
> a close view of the top of Cloud Gate ("the Bean") in Millennium Park, Chicago, at night. Pull the camera back so
> the whole sculpture is seen from the side: continue its outline down both sides into the full seamless kidney-bean
> shape, twice as wide as it is tall, with the low arch underneath its middle (image 2 shows the lower body and
> arch; copy their form, not its reflection), resting on the stone paving of the plaza. The mirror below the
> existing picture goes on reflecting the plaza, curving under. Behind the Bean, dark towers of the Chicago Loop
> rise out of the top of the picture, windows as tiny white cells, darker and quieter than the Bean so the polished
> steel is the brightest thing; a low hedge and lamp posts along the far edge of the plaza. Six or seven tiny
> pedestrians near the foot of the Bean, each about a sixth of its height, none in the bottom centre. The paving in
> the bottom centre is in mid-tone engraved hatching (a pale figure will stand there later); the pool of lamp light
> is under and beside the Bean. Light as in the existing picture: the bright highlight on the Bean's upper right.
> The new parts are seen small, so draw them with a bolder, more open line. Black ink on off-white paper only, no
> colour, no red, no text, no border, no margin.

**From v4-A, beyond the agreed fixed points:**

1. Name the matte directory `<take file minus .mp4>_matte/` (`v4_sync_1080_matte/`, as planned), so `S1_SRC` stays
   the only path to change; B derives the matte path from it.
2. Keep the matte as tight as v3's (BiRefNet on the synced file, no grow, no extra feather). Over white paper at
   42 % scale v3's edge is clean; a grown matte would carry a dark rim of the old plate.
3. Her figure must reach the bottom edge of frame across her whole width on every frame from 12.60 to 13.92, arms
   at her sides (the v3 pose). She is anchored to that edge while small; a gap or a rising shoulder would show.
4. Behind her, keep `plate_close_1` in the v3 crop, with no baked push, grain or grade: the take's own plate takes
   over from the clean plate at landing.
5. Tell B if her scale, position or bottom cut line moves by more than a few px: the arc lyric and both curves
   hang on them.

**Check after the build:** R4 (52.48–56.54) and the C2 teaser replay S1 through `comp`; watch that the reversed
pull-out reads there.
