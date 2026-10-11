# Instance A: work streams and canon decisions (v3 pass, 2026-10-11)

Instance A (`rev-A`) split its brief (`docs/revisions/A.md`) into parallel streams. Every stream reads
`docs/revisions/README.md` and `docs/revisions/A.md` first; the rules there apply to sub-agents too.
This file holds what all streams share. rev-A keeps it current; B reads the canon section.

## Streams

| Stream | Notes (v2 time) | Shots | Timeline it may edit | Soft spend cap | Tag prefix |
|---|---|---|---|---|---|
| SING | watercolor singer | S1 (+S1b, S2_her source), E3, V3S | none (hands specs to rev-A) | $30 | `revA_sing_` |
| V1A | intro bullet, 0:24, 0:25, 0:29, 0:30 | C1, D2, D3, D4, D5 | `render/timeline/A.js` (own shots), `_A_tracks.js` | $18 | `revA_v1a_` |
| V1B | 0:35, 0:37 | D7, D8 | `render/timeline/A.js` (own shots + dialogue overlay) | $10 | `revA_v1b_` |
| V2 | 1:24, 1:26, 1:33, 1:52 | V2d2, V2e2, V2h, `continue_vo` | `render/timeline/C.js` (V2a–V2h entries only), `render/engine/modules/hud.js` (loading mode), `tools/sfx/build.py` | $10 | `revA_v2_` |
| F | 3:05, 3:13, 3:21, tabletop objects | F5a, F6b, F7c (F7_04 + recap uses) | `tools/sectionF/edl.py` → `media/shots/F_edl.json` (not O2) | $22 | `revA_f_` |
| GO | 2:21, 3:40 | G1–G3 (+ M sprites if cheap), O2 | `render/timeline/E.js` (G1–G3), `tools/sectionF/edl.py` (O2 entry only) | $16 | `revA_go_` |
| TESS | new idea (1:20): the pursuing fleet as an Escher tessellation | V2c7 | `render/timeline/C.js` (V2c7 entry only), a new engine module | $6 | `revA_tess_` |

Two streams share `A.js` and two share `edl.py`: edit only your own shot entries with targeted edits, re-read the
file right before each edit, and never reformat or reorder the file.

## Canon (binding for A's streams and for B)

- **Pencils: exactly two, always** (Jade, 2026-10-11: "maybe we have 2 pencils, one graphite, one rainbow"; this
  replaces the earlier one-pencil line).
  - Both are classic yellow hex pencils with a silver ferrule, so they match at any size. The **graphite** pencil has
    a pink eraser and a dark graphite point. The **rainbow** pencil has a pale-blue eraser and a point whose core is
    a multicolour swirl; the line it draws is rainbow-cored coloured pencil.
  - **In the bun** (everything before 144.54, and again from O2): the two are crossed in an X through the bun,
    erasers up, points leaving the far side of the bun. **Each pencil is one straight line** from eraser to point;
    never an eraser end and a tip that don't line up, never one pencil, never three.
  - **Hair down** (G2 at 144.54 until O2): she pulls the rainbow pencil and it is the one in her drawing hand in
    every shot after. The graphite pencil comes free as the bun falls and is not featured again until O2, where both
    go back in, crossed.
  - Reference image: `media/design/jade_bun_two_pencils.png` (three heads + a callout of both pencils). Use it
    together with `jade_canon_turnaround.png`, which still shows one pencil.
  - The rainbow point is the one sanctioned place for a full spectrum (it may include a little red). Skies and
    backgrounds still follow "no red" and "rainbows out".
- **Hair:** black, centre part, **curtain bangs** (long face-framing strands swept to both sides). Never hime bangs,
  never a blunt straight fringe. This holds in the colour world too.
- **Jacket:** white cropped bomber; one orange band across the chest and both sleeves; pale-blue dot on **her left**
  chest; roundel on **her left** upper sleeve reading `1420` / `MHz` on two lines (capital M, capital H, lowercase z);
  back: one large pale-blue circle. Black **mock-neck** crop top. Orange headphones round her neck. Navy cargo pants with
  orange straps, chunky white sneakers. The outfit does not change when the world turns to colour.
  Refs: `media/design/jade_canon_turnaround.png`, `media/design/jade_expressions.png`, `media/design/jade_action_pencil.png`.
- **Car:** white 2001 Acura TL, **left-hand drive** (Chicago). Camera outside her driver's window sees her facing
  screen-left; camera from the passenger seat or through the windshield from the passenger side sees her facing
  screen-right with the wheel in front of her. Agents' car: a plain black sedan, never a limo.
- **No visible bullets.** Shots are a muzzle flare (engraved starburst) and a mote burst on the body. No head shots.
- **Singing Jade** is the watercolor Jade of `inputs/jade_watercolor_jacket_v6.png`, **no headphones** (Jade, final). Her art style is meant to
  mismatch the world around her.
- **Unchanged:** no red; never "Authority", "TVA" or Marvel terms; every cut on the tracked beats; one idea per frame.

## Environmental lyrics (Jade's note; reference `~/Downloads/kdh_screenshots/`)

Jade: "let's use the environment for some of the words, instead of all subtitles … large text lyrics that fit
naturally into the environment". In the reference the words are **big** (a third of the frame), sit on a real
surface of the scene (billboard, street sign, phone screen, floor, wall, stage screen), take that surface's own
material and typeface, and one phrase gets one surface. The rest of the lyric is not subtitled at the same time.

- When a shot of yours carries a sung phrase, prefer putting the phrase on a surface of that shot over the lower
  third. If it goes in-world, remove the lower third for those words: never both.
- It must read at 540p in the time the shot is on screen. Large, few words, high contrast.
- The lettering is native to the surface: highway gothic on road signs, bulb letters on a rooftop sign, white-line
  woodcut letters cut into the engraving, pencil in the colour world. Either have the image model draw the lettering
  into the keyframe (static text; check the spelling at full size) or pin it with the engine's `pin`/`etch`/`pencil`
  modules (word-timed text). Adding an OFL font to `render/fonts/` is allowed: tell rev-A first (shared folder).
- Not every line. Whispers, the RPG dialogue box and HUD stay as they are unless a note says otherwise.

## Working rules for streams

- **Disk:** about 5 GB free, shared with B. Run `df -h .` before every generation or render batch; stop and tell rev-A
  below 1.5 GB. Keep takes few: one keyframe round, one Seedance take, a second only if the first fails the note.
- **Spend:** `~/Documents/moongazing/.venv/bin/python tools/gen/spend.py --tags | grep revA_` before and after each
  batch. Stop at your cap and report.
- **GPU** is shared (B, other streams, `tools/engrave`, headless Chrome). Retry once on a CUDA/WebGL failure before
  reporting it.
- **One engrave at a time, across everyone:** wrap every `tools/engrave` / colour-pass run as
  `flock media/.engrave.lock <command>`. Each run writes a temporary matte PNG sequence of several hundred MB;
  several at once took the disk to 43 MB free at 12:35. Start one only with at least 1.5 GB free.
- **Takes go beside old ones** (`take_N+1…`, `kf_v3_…`). Never overwrite or delete a v2 file. Update `chosen.json`
  and the shot's `NOTES.md`.
- **Pass `--preview` on every `render.mjs` call**, including `--list`, `--still(s)` and `--sheet`. Without it the
  engine extracts every video of the timeline at 1080p into `media/engine_cache/full` (it refilled to 9.4 GB in
  minutes after being cleared).
- **Render only your own ranges** through a solo timeline (`_A_test.js`, `_C_solo.js`, `E.js`,
  `tools/sectionF/F_preview_timeline.js`), preview size. No full renders. No commits, no pushes (rev-A commits).
- **Look before you ship:** view frames of the after clip at the note's timestamp and check them against the note
  and the canon above. A generated shot that still breaks the note is `partial`, not `done`; say what is wrong.
- **Hand-off:** for each note, a 540p H.264 after clip under 10 MB with its audio slice in `media/reviews/v3/A/`
  (`<mmss>_<slug>.mp4`, a couple of seconds of context each side), and an entry in your fragment
  `docs/revisions/streams/<STREAM>.json` (the entry format is in `docs/revisions/README.md`). Keep the fragment
  current as you go; rev-A merges fragments into `docs/revisions/review_A.json`. Put anything rev-A or Jade must
  decide in `question`.

## Jade's rules from the v3 review (2026-10-11, 13:15)

- **No lyric word in more than one shot.** A word that was shown in one shot is not shown again in the next.
- **When she stops singing, cut away.** Don't hold on the singer after her line; cut into the car or the scene.
- **Colour on her stays visible** even when she is small in frame (e.g. in the driver's seat): face, headphones, hands.
