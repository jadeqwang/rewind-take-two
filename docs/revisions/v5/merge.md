# 3:23, BLUE and ORANGE merge back into her ("un-Banach–Tarski"): plan for Jade

**Status (2026-10-12, `v5-merge`): plan finished, previz rendered, waiting for Jade's sign-off.** Spent **$0.134**
(one nano-banana-pro clean-plate edit, tag `v5_merge_plate`) of the $3 cap. No timeline file, `F_edl.json`, `edl.py` or
shared mix touched; nothing committed.

Jade (verbatim): "3:23 - maybe it makes sense for blue and orange variants to merge here and we just demonstrate that she
can un-banach-tarski herself into becoming original her".

**Look at:**
- previz (540p, with a previz sound pass): `media/reviews/v5/plans/merge/0323_merge_previz_A.mp4` (200.25–207.29)
- 9-frame strip: `media/reviews/v5/plans/merge/0323_merge_previz_A_strip.jpg`
- the same range in v4: `media/reviews/v5/plans/merge/0323_before_v4.mp4`

![strip](../../../media/reviews/v5/plans/merge/0323_merge_previz_A_strip.jpg)

## What is there now (v4 preview, read off frames)

The README's table puts the light burst in F7_06. It is actually in **F7_07**. F7_06 (202.88–203.76) is a second shot of
the colour-ghost stampede on the L tracks (F7a from 2.0 s at 1.12×, a near repeat of F7_01 at 197.60). F7_07
(203.76–205.52, `F7e` take 2, on the 203.78 swell, "BIG 2") is the shot Jade means. In it, two identical Jades in the
canon jacket leap at each other over the L platform, a white sun-burst covers them for about half a second, and one Jade
floats there, arms out. The idea is already in the cut but doesn't read: the two aren't BLUE and ORANGE, and the burst
hides the merge instead of showing it.

At 2:00 the split goes: freeze, flash, she bursts into orange/blue motes (127.88, `b_atomize`), the motes implode into
two Jades (128.32, `b_implode`), and the costume pass tags them. ORANGE (always screen-left) gets orange stripes, straps
and dots. BLUE gets blue stripes, straps, headphones and dots. Canon Jade is the white jacket with an **orange band and a
pale-blue dot**, so the original her is literally made of both: ORANGE's band and BLUE's dot.

Beats here (tracked, `timing.json`): 202.02 · 202.44 · **202.88 (bar 116)** · 203.32 · **203.76** (swell 203.78) · 204.20
· **204.64 (bar 117)** · 205.08 · **205.52** (F7_08, the rewind that paints). No SFX cue sits anywhere in the final
drop, so the music carries it.

## Option A (recommended): the reassembly. One shot, F7_07m, 202.88–205.52 (6 beats; F7_06 goes)

One wide shot over the L platform, cut on bar 116 straight from the melting clock (F7_05, unchanged):

| Beat | Picture |
|---|---|
| 202.88 | **ORANGE** (left) and **BLUE** (right) leap at each other, hands reaching: F7e take 2 recoloured by her matte (`approach_bo.mp4`) |
| 203.32 | They touch: freeze. Graphite lines sweep out from the joined hands and score both girls into equilateral triangles: the "pieces" of the paradox |
| 203.76 (swell) | Soft warm flash. Every triangle lifts off, turns and flies, rigid pieces moving like the paradox's rotations. ORANGE's pieces glow orange, BLUE's glow blue, and the two streams **braid**, ORANGE's dipping under and BLUE's arcing over. A small orange/blue Celeste mote ring snaps shut at the hands (the split's own effect from 127.88) |
| 204.20 | The streams cross. Mid-air she is a checkerboard of orange and blue triangles |
| 204.48 | The last pieces seat. Their outlines turn gold. The whole girl fills in under them |
| 204.64 (bar 117) | Small punch. **One Jade, canon colours** (orange band, pale-blue dot), arms out. The gold seams flash once and fade over 0.3 s. The take plays on (frame 40 →) |
| 205.52 | Cut to F7_08 as now |

Why it reads as "un-Banach–Tarski": the paradox cuts one ball into finitely many pieces and moves them rigidly into two
balls. Here two Jades are cut into pieces (you see the cut lines drawn), the pieces move rigidly (turn and translate,
never stretch), and they land as one Jade with nothing left over. Every piece of both lands on her. The colour coding
shows half of her came from each, and she ends in her canon colours, the original.

Sound (procedural, free, in the split's vocabulary): **203.32** three short pencil-scratch strokes (the scoring);
**203.76** `b_atomize`'s sparkle, same synthesis as the split at 127.88 (the pieces lift); **204.02→204.64** `b_implode`'s
reversed sparkle swelling into a soft wooden latch click on 204.64 (the pieces seat). The split's two sounds come back in
the same order, so the ear can hear the 2:00 split being undone. In the previz they sit 13–20 dB (RMS) under the final
drop: mostly the high sparkle and the click come through.

**What it needs:** engine only, from media already on disk. No video-model take.

| Asset | From | Status |
|---|---|---|
| `media/shots/F7m/approach_bo.mp4` | F7e take 2 frames 0–14; the costume pass of `tools/v4B/coop/recolor.py` limited to each twin's matte (F's world is full colour, so the co-op screen-split pass alone would recolour bricks) | **done** (bake.py) |
| `media/shots/F7m/plate.png` | empty L platform: per-pixel from take frames where her matte is clear; the hands/confetti region patched from a nano edit (`F7m/kf/plate_edit_v1.jpg`, registered by ORB homography, feathered box) | **done**, $0.134 |
| `media/shots/F7m/fig/` (32 RGBA frames, 1080p) | the scoring + flight, baked by `tools/v5/merge/bake.py` from the frame-9 twins and the frame-40 merged girl (`F7e/take_2_matte`, clean) | **done** |
| `media/shots/F7m/seams/` (7 frames) | gold seam flash on the merged girl | **done** |
| shot entry `tools/v5/merge/F7_07m.json` | the EDL row (layers + fx) | **done**, used by the previz |
| sound | 3 cues, now in `tools/v5/merge/previz_audio.py`; move to `tools/sfx/build.py` | previz only |

The matted sources at `media/shots/C_coop/` (c1/c2 takes, `two_bo`, `*_L/_R` mattes) don't fit here: those twins have
hair up in buns with pencils, on a black-and-white desk level, in side view. Section F's Jade has her hair down in a full-colour world. F7e's own
take and matte give BLUE and ORANGE in F's look for free. Co-op only supplies the costume rule and `recolor.py`'s colour masks.

**Cost to finish A: $0** (everything is baked). Ceiling if Jade wants changes to the pieces: still $0 (bake.py
parameters). A video-model take isn't needed and wouldn't help: Seedance cannot be trusted with a rigid tessellated
reassembly, and it would smooth the triangles into a morph.

## Option B: the split run backwards (keeps F7_06; F7_07 stays 203.76–205.52)

F7_06 stays. In F7_07 the twins are recoloured BLUE/ORANGE as in A. At the touch (≈203.95) each one bursts into motes in
her own colour (E6b's `motes` burst), and the cloud implodes into one Jade by 204.20 (E6c's implode, the comp played
backwards). The sun-burst is covered by the mote cloud. Cost $0, about half a day less work than A was.

Against it: motes read as a *dissolve*, the same teleport language as the split, so it says "they turned back into
one" without the cut-and-reassemble that makes it Banach–Tarski. It also lives inside the same 1.76 s as the current
burst, so it is over before it registers. Not prevized.

## Recommendation

**A.** It is the only one that *demonstrates* the paradox (scored pieces, rigid moves, nothing left over). It costs nothing more,
it is already built, and the shot it absorbs (F7_06) is a repeat of F7_01. The freeze-then-burst echoes the split at 2:00
(freeze, flash, motes), but forward instead of backward.

**Weak spots seen in the previz:**
- The 0.44 s approach is the take's first 0.33 s slowed to 0.74× with frame blending, so the leap has a slight soft
  double image.
- In flight the pieces are visibly flatter and cleaner than the plate (engine-drawn triangles with crisp outlines). It
  is deliberate (the maths reading), like the engine's Penrose stairs were before their restyle.
- The plate is a still, so the confetti and gold flakes in the take stop for 0.88 s. Hard to see under the pieces.
- At 540p the scoring lines on the frozen twins are thin. At 1080p they are 2 px graphite. If Jade wants them bolder,
  `edges_img(..., 2, ...)` → 3.

## Questions for Jade

1. **Option A (triangle pieces braiding into one) or B (motes, the split replayed backwards)?**
2. A replaces F7_06 (a second shot of the colour-ghost stampede, 202.88–203.76) to give the merge 6 beats. OK to lose it?
3. In the merge the variants have their hair down like every other F shot, and are told apart by costume colour only
   (the co-op buns don't come back). Fine?
4. Too much or too little? E.g. fewer, bigger pieces (Banach–Tarski famously needs only 5; the previz uses about 240 a
   girl), or less orange/blue glow in flight.

## Files (all new, none committed; media gitignored)

- `tools/v5/merge/bake.py`: builds everything in `media/shots/F7m/` (`tools/engrave/.venv/bin/python tools/v5/merge/bake.py --sheet`, ~10 s, free)
- `tools/v5/merge/F7_07m.json`: the shot's EDL row
- `tools/v5/merge/previz_timeline.js`: section F's EDL with F7_06/F7_07 swapped for F7_07m (does not modify any shared file)
- `tools/v5/merge/previz_audio.py`: previz sound (mix slice + 3 cues), muxed onto the clip
- `media/shots/F7m/`: `approach_bo.mp4`, `plate.png`, `fig/`, `seams/`, `layout.json`, `fig_sheet.jpg`, `kf/` (frame 40,
  the nano edit and its prompt `plate_edit.prompt.txt`, model google/nano-banana-pro 2K; the catalog exposes no seed)
- `media/reviews/v5/plans/merge/`: previz clip, strip, v4 before clip
- `docs/revisions/v5/fragments/merge.json`

## Execution (after Jade signs off on A; a later agent can follow this step by step)

Budget: $0 expected (all media is baked). Tag `v5_merge_` if anything paid is needed. No commits; `render/engine/**`,
`timing.json` and the car shots are off limits. `tools/sectionF/edl.py` and `tools/sfx/build.py` are **shared with
`v5-coda`** (it owns the `CODA_*` lines and the credits fade): re-read right before editing and use exact-string edits.

1. **Apply Jade's tweaks, if any**, in `tools/v5/merge/bake.py` (piece size `S`, glow `0.4`, seam width, timings
   `T_SCORE`/`T_FLY` must stay on the beats 203.32/203.76/204.64), then rebake:
   `tools/engrave/.venv/bin/python tools/v5/merge/bake.py --sheet` and check `media/shots/F7m/fig_sheet.jpg`.
2. **EDL.** In `tools/sectionF/edl.py` `build()`, replace exactly these two lines
   ```
           cut("F7_06", 202.88, 203.76, "F7a", clip_in=2.0, scale=1.12, fx=[FLASH(0.4)]),
           cut("F7_07", 203.76, 205.52, "F7e", fx=[FLASH(1.0, "#ffffff", 0.16)]),                                               # BIG 2
   ```
   with
   ```
           # v5 (Jade 3:23): BLUE + ORANGE reassemble into her, replaces F7_06 (stampede, closer) and F7_07 (sun-burst merge)
           # v4: cut("F7_06", 202.88, 203.76, "F7a", clip_in=2.0, scale=1.12, fx=[FLASH(0.4)]),
           # v4: cut("F7_07", 203.76, 205.52, "F7e", fx=[FLASH(1.0, "#ffffff", 0.16)]),   # BIG 2
           {k: v for k, v in json.load(open(os.path.join(ROOT, "tools/v5/merge/F7_07m.json"))).items() if k != "_doc"},  # BIG 2
   ```
   (`json`/`os`/`ROOT` are already imported/defined there.) Also update the `F7a` notes string ("reused at F7_06" → "reused at F7_06 until v4").
   Regenerate: `~/Documents/moongazing/.venv/bin/python tools/sectionF/edl.py` (rewrites `media/shots/F_edl.json` and the
   `chosen.json` files; v5-coda's changes in the same file are carried along, which is fine).
3. **Check:** `node render/engine/render.mjs --list --preview | grep -E "F7_0[5-8]"` → F7_05 202.02–202.88, **F7_07m
   202.88–205.52**, F7_08 205.52–207.28, no overlap errors. `grep -c F7_06 media/shots/F_edl.json` → 0.
4. **Sound.** Port the three cues from `tools/v5/merge/previz_audio.py` `cues()` into `tools/sfx/build.py` as
   `@cue("merge_score", 203.32, …, "procedural", "optional", G)`, `@cue("merge_lift", 203.76, …)`,
   `@cue("merge_seat", 204.64, …)` (seat returns its pre-roll as the offset: `return y, -0.62`; reuse the file's own
   `pings`, `click`, `reverb`, `room()`). Place them after the coop block. Set `G` by ear against the final drop, starting where
   the split cues sit (`-28`/`-30`) and raising until the sparkle and click are just audible. Rebuild once, coordinated with
   v5-coda: `~/Documents/moongazing/.venv/bin/python tools/sfx/build.py` (local, free). Check
   `media/sfx/cues.json` lists the three cues and that `original_bit_exact_outside_cues` stays true.
5. **Render the after clip** (check `df -h .` first):
   `node render/engine/render.mjs --range 200.24 207.28 --preview --encode --force --audio media/sfx/Rewind_cinematic_sfx_mix.mp3`
   (if another section's file is broken, use `--timeline tools/sectionF/F_preview_timeline.js`). Copy to
   `media/reviews/v5/0323_merge.mp4` (<10 MB). Watch it at preview size: the cut from F7_05 on 202.88, the freeze on
   203.32, the lift on the 203.78 swell, the seat on 204.64, and that the plate→take hand-off at 204.64 doesn't jump.
6. **Hand-over:** update `docs/revisions/v5/fragments/merge.json` (`status: "done"`, `after`), add a "v5" section
   to `docs/sections/F.md` (cut list rows F7_06/F7_07 → F7_07m) and a v5 line to `media/shots/F7e/NOTES.md`, and set
   this file's status line.
