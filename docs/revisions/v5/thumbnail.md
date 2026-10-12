# REWIND v5: YouTube thumbnails (`v5-thumb`, 2026-10-12)

Jade asked: "think about a YouTube thumbnail image that would encapsulate the video, maximize likelihood of clicking,
and also include the song name? (or if you have 2-3 good concepts, render more than one and YouTube has A/B testing)".
YouTube's Test & Compare takes up to 3 thumbnails: four were built (A–D) and the recommended three are C, A, D.

**Status: done.** Four 1280×720 PNGs (A–D; **the Test & Compare three are C, A, D**, see Ranking) plus a check sheet in
`deliverables/thumbnails/`. Spend: **$0.134** of the $5 cap
(one clean-up upscale, tag `v5_thumb_A_upscale`). Project total after: $252.18 of $400.

| | File | Size | Red audit* |
|---|---|---|---|
| A | `deliverables/thumbnails/rewind_thumb_A_ghost_leap.png` | 0.94 MB | 0.008 % |
| B | `deliverables/thumbnails/rewind_thumb_B_platform_leap.png` | 1.06 MB | 0.000 % |
| C | `deliverables/thumbnails/rewind_thumb_C_ghost_sprint.png` | 1.99 MB | 0.007 % |
| D | `deliverables/thumbnails/rewind_thumb_D_ghost_dash.png` | 1.72 MB | 0.000 % |
| | `deliverables/thumbnails/check_sheet.png` (all four at 1280×720, 320×180 and 168×94 on a mock dark-mode feed with three plain dummies; duration box drawn in) | 6.8 MB | |

All are 1280×720 RGB PNGs with an embedded sRGB ICC profile. *Red audit: section F's criteria (`tools/sectionF/dered.py`: hue
within 15° of 0, saturation > 0.45, value > 0.2). The remaining specks are anti-aliased edge pixels of Jade's orange bands.

## Constraints from Jade (via the setup session), in order received

1. **No spoilers.** No Hilbert Hotel (the post-credits door, lobby, queue of Jades, ledger) and no Banach–Tarski BLUE/ORANGE
   split or merge (2:00, 3:23). E7_04_chasm has a HILBERT HOTEL sign on a building at the right of frame, so A's crop stops
   at x = 1320 of 1920 and the sign is out of frame.
2. **No fish-eye Bean shot** (watercolor Jade singing in the Bean, 0:13 and 2:35, including its plate). My first concept,
   "Only one in colour" (watercolor Jade with REWIND and the ring), was dropped before it was built.
3. **Lead with anime Jade in action with the ghost trail**, with REWIND large; at least one other thumbnail should vary it.
4. **Use the 2:15 leap (E7) and the 1:35 leap (B2)**, one thumbnail each, rendered at 1080p from the engine; the third is my call.
   It's the F6c sprint (3:15), the film's clearest ghost-trail image.
5. **Late addition: "1:53 leap to dodge roll may also have a strong frame for the thumbnail."** Scanned and built as D
   (below); it replaces B in the Test & Compare three.

Standing canon: no red, the agency never written "Authority" (no agency text appears at all), Jade on model (anime Jade,
straight from the game sections).

## Design rules applied

- One focal subject: Jade mid-action, large, with her face visible (3/4 or profile), plus the ghost trail as the second read.
- The song title is the only word: **REWIND** in Anton (the film's slab sign face, as on A SHADOW, MEN IN SHADES and SIRENS), in the
  film's residue orange `#F08A24` with a 9 px ink stroke and soft shadow. Cap height is about 22 % of the frame, so it stays
  legible at 168×94 (about 20 px tall). The same title treatment on all three keeps the test about the image, not the type.
- No artist name on the image: the channel line already carries it, and extra type is noise at 168 px.
- Bottom-right 15 % × 12 % kept clear for the duration box (checked with a drawn box on the sheet).
- The whole frame is from the film: each image is a real frame of the video, not a re-imagining.

## The concepts (with the hook each one bets on)

### A — "Ghost leap" (E7, 2:16): `rewind_thumb_A_ghost_leap.png`

Jade launches up and to the right across the chasm with her arms spread, face in 3/4 view. Behind her is a diagonal stack of
translucent colour copies (green, gold, orange, magenta, blue), every failed attempt jumping with her, over the
black-and-white engraved sky. REWIND sits top-left.
**Hook:** spectacle and curiosity ("why are there a dozen of her?"), plus a black-and-white world where only she is in
colour. It's the most dynamic pose in the film.

- Source: engine still at **136.833**, shot `E7_04_chasm` (136.62–137.50). The coordinator's E7 range (E7_01_plat /
  E7_02_leap, 134.88–136.62) shows the ghosts leaping the gap but Jade herself running in the pack; her own leap with the
  ghost stack behind her is the next shot, 0.2 s later. 136.833 is the frame where her face turns to camera (136.75–136.875
  all work; 137.0–137.3 is the flatter "superman" dive with her face turned away).
- **Residue ribbons removed.** In the film this frame has the D_E7_ribbons overlay (wavy orange/gold/teal/pink ribbons) crossing
  her body. At 168 px they turned her into a tangle, so the still is re-rendered from a scratch timeline holding only
  E7_04_chasm with the ribbon layer dropped (the overlay's colour wash is kept):
  `node render/engine/render.mjs --timeline tools/thumbnails/tl_e7_noribbon.mjs --stills 136.833`.
  It doesn't touch the film's timeline files. If Jade prefers the ribbons, the film still is
  `media/thumbnails/src/e7_04_chasm_t136_833.png`; swap it in at `thumb_A()`.
- Crop (520, 0)–(1320, 450): a 1.6× zoom on Jade. Graded contrast 1.1 and saturation 1.45 so the ghost stack separates into
  colours, then de-redded (the saturation lift pushed skin shadows toward red), and a grey debris smudge beside her legs inpainted.
- **Generation (clean-up/upscale only):** the 1.6× crop was soft and smeared from video compression, so the crop (Lanczos to
  1600×900, `media/thumbnails/src/A_crop_1600.png`) went through one faithful upscale. Checked side by side at 100 %: same pose,
  face, figures, colours and hatching, with clean outlines. Output `media/thumbnails/gen/v5_thumb_A_upscale.jpg`
  (2752×1536, centre-cropped to 16:9). Model `google/nano-banana-pro`, 2K, 16:9, $0.1344, tag `v5_thumb_A_upscale`. Prompt:

  > Upscale this exact image to a crisp high-resolution version. It is a frame from a hand-made animation: an anime girl in a
  > white cropped jacket with orange bands and navy cargo pants dives up and to the right, arms spread, with a stack of
  > translucent coloured copies of herself trailing behind her, over a black-and-white wood-engraved background of horizontal
  > hatching. Remove the video compression smear and blur; restore clean ink outlines and flat cel shading. Keep everything
  > identical: same composition and framing, same pose, same face, same colours, same number and placement of every figure,
  > same hatching. Do not add, remove or move anything. No text, no letters, no logos.

### B — "Race your ghost" (B2, 1:35): `rewind_thumb_B_platform_leap.png`

Jade in a full split leap over the gap between two elevated-track platforms (precision-platformer section), face in 3/4 view.
Her grey graphite ghost racer from the previous iteration leaps just ahead of her, and the film's own HUD reads
`GHOST: ITERATION 4,096 / +0.19`. REWIND sits lower right over the empty paper.
**Hook:** the video game. It's instantly legible as a platformer, and it raises the question of why she's racing her own ghost
on iteration 4,096. It's the cleanest and calmest of the three, and the pale cream frame stands out as the brightest tile in
dark mode.

- Source: engine still at **95.458**, shot `B2_leap` (95.46–96.30). It's the peak of the leap: legs fully split and the face
  clear (95.54–95.63 are flatter).
- Crop (430, 20)–(1590, 672), 1.1×. The film's HUD plate (1300–1900 × 36–148) would have been clipped by the crop, so its
  place is filled with the neighbouring band of horizontal hatching (x 1000–1300, tiled) and the whole plate is pasted back
  inside the frame at 80 %: the same pixels, moved left.
- No generation.

### C — "Ghost sprint" (F6c, 3:15): `rewind_thumb_C_ghost_sprint.png`

The final-drop sprint, in full colour: Jade at full stride with her hair streaming and a pencil in her hand, and the stream of
ghost copies of her in step behind her (orange, sky blue, magenta, green, gold, violet), against the coloured-pencil Chicago
with Kandinsky shapes. REWIND sits top-left.
**Hook:** colour and motion. It's the most saturated tile in a feed, and the rainbow of selves reads at a glance as a
time-loop / clone story, with the biggest, clearest face of the three. It's the "third slot, my call": the strongest
ghost-trail image in the film.

- Source: `media/shots/F6c/kf_clean.jpg` (2731×1536), the keyframe (first frame) of take 3, which the film plays at
  195.42–197.60 (`F6c`, starting 0.3 s in). It's crisper than any rendered still because it isn't video-compressed. The
  1080p stills at 195.5–197.3 show the same pose, so the thumbnail matches the film.
- De-redded with `dered.fix(..., "orange")`, as the film's take is (`take_3_engraved_dered.mp4`: the brick on the left and
  right goes to terracotta). Cropped inside the keyframe's paper margin, (208, 82)–(2684, 1475), exact 16:9. No sharpening,
  which keeps the file under 2 MB.
- No generation.

### D — "Ghost dash" (E1_E2a, 1:54): `rewind_thumb_D_ghost_dash.png`

Jade flat out in a horizontal "superman" dash along the elevated tracks, arms forward, pencil in her bun. The big orange
outline ghost of her previous attempt is behind her, the dense engraved el-track and tenement background runs across the
frame, and the film's `GHOSTS 1` HUD sits top right. REWIND sits bottom-left over the tracks.
**Hook:** pure speed, with one colour ghost that reads even at 168 px. It's the most "action game" frame of the four.

- **Frames compared** (1080p engine stills every 2 frames, 111.9–116.3): `C_V2n_continue` (CONTINUE? 9/8; Jade standing),
  `B2_V2n1` (slapping the rewind button), `E1_E2a_tracks` 113.08–113.83 (sprint with residue sparks; face small),
  **114.08–114.33 (the dash: chosen)**, 114.42–114.83 (the dodge roll: Jade upside down with a blue ghost streak, a
  striking frame but the face is inverted and the figure reads as a tangle at 168 px), `E2_04_leap` 114.92–115.17 (the
  leap: Jade tiny in a wide frame), `E2_05_chasm_short` (small figure, pink ghost), and `E2_06/07_lawn` (agents firing;
  Jade seen from behind).
- Chosen: **114.333** (`E1_E2a_tracks`). 114.17–114.33 are near-identical; 114.333 has the ghost's glow at its fullest.
- Weakness: her face is mostly hidden behind her arm (closed eye, a sliver of profile). This is the only one of the four
  without a readable face; the full-body gesture carries it instead.
- Crop (220, 30)–(1900, 975), 1.3×, which keeps the HUD whole. Contrast 1.06, saturation 1.15, light sharpen, de-red.
  No generation.

## Check sheet and legibility verdict (168×94)

`deliverables/thumbnails/check_sheet.png`: the three at 1280×720; a desktop home row at 320×180 alternating with three plain
dummies (a lo-fi purple gradient, a yellow "I TRIED IT" vlog tile, a grey "OFFICIAL VIDEO" tile); the mobile up-next list at
168×94 in actual pixels; and the same 168×94 cards blown up 3× nearest-neighbour for pixel-level judging.

- **REWIND reads on all three at 168×94** (about 20 px tall letters, ink-outlined orange).
- **A:** Jade's figure and the rainbow stack read; the face is a few pixels, so the gesture carries it. The duration box is clear.
- **B:** the leaping figure and the ghost read clearly; the HUD becomes a small dark bar (a game cue, not meant to be read).
- **C:** strongest pop of the seven tiles; the colour stream is unmistakable and Jade's figure is the largest.
- **D:** the long horizontal figure and the orange ghost read; the busy grey engraving behind is the weakness (REWIND holds
  thanks to its ink stroke). The face doesn't read at this size.

Iterations: A v1 had the title over her legs and the ribbons across her body, and read as a smear at 168 px. A v2 moved the
title top-left. A v3 dropped the ribbons, zoomed 1.6× and lifted saturation, then had the faithful upscale. B: fixed the
clipped HUD. C: removed the keyframe's paper border and a dark rule at the bottom edge.

## Ranking (my call) and how to test

Moments compared for the leap/action slots: the 2:15 E7 ghost leap (A), the 1:35 B2 leap (B), the 1:53 dash and dodge
roll (D), plus the F6c sprint (C).

**Test & Compare three: C, A, D.**

1. **C — Ghost sprint.** Highest click odds: the most colour in a dark feed, the largest face, and the clone stream is the
   film's core idea read in under a second. Risk: the busiest background (REWIND holds because of the ink stroke).
2. **A — Ghost leap (2:15).** The most dynamic pose and the best "how is that happening?" curiosity. Its black-and-white
   world with one rainbow streak tells the film's colour-equals-residue idea.
3. **D — Ghost dash (1:53).** It replaces B because, on the brief Jade set (anime Jade in action with the ghost trail), D
   has the bigger action and a colour ghost that survives at 168 px. B's graphite ghost almost vanishes at that size, so B
   reads as one girl jumping. D gives up the face, so the test also says whether a face matters for this audience.
4. **B — Race your ghost (1:35)** (kept on disk as the alternate). It has the cleanest frame, a clear face and the
   brightest tile, but the least colour. Swap it in for D if Jade wants a readable face on all three.

C and A carry the ghost-trail hook in colour versus engraved worlds, and D is the speed/game-UI variant. The result will
say whether colour, the stacked clones or raw speed pulls clicks.

## Rebuild

```
tools/engrave/.venv/bin/python tools/thumbnails/make_thumbnails.py          # all four + check sheet
tools/engrave/.venv/bin/python tools/thumbnails/make_thumbnails.py A --sheet
```

The sources are staged in `media/thumbnails/src/` (gitignored): `thumb_e7_noribbon_full_t136_833.png`,
`e7_04_chasm_t136_833.png` (with ribbons), `b2_leap_t95_458.png`, `e1_e2a_tracks_t114_333.png` (D),
`e1_e2a_tracks_t114_583.png` (the dodge roll, not used), `A_crop_1600.png`. The upscale is in `media/thumbnails/gen/`.
Engine stills: `node render/engine/render.mjs --stills 95.458,114.333,136.833` and the scratch timeline above. Fonts are from
`render/fonts/` (Anton, Press Start 2P via the film's HUD pixels, IBM Plex Mono for the sheet). No timeline files were edited
and nothing was committed.
