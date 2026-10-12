# v5-build: merge option A + Hilbert Hotel post-credits scene

Agent `v5-build`, 2026-10-12. Cap $10, tag `v5_build_`. Spend at start $245.82; **spent $0.81** (six nano-banana-pro
2K stills); project total **$246.62** of $400. Nothing committed.

**Status: both parts built and checked at 540p.**

| Clip | Path |
|---|---|
| 3:23 merge, after (200–208, v4 mix audio, 3.4 MB) | `media/reviews/v5/0323_merge.mp4` |
| Credits → Hilbert Hotel, after (230–244.05, v5 coda mix, 7.3 MB) | `media/reviews/v5/coda_hilbert.mp4` |
| Contact sheet of that clip (20 frames, 230.0 → 243.3 every 0.7 s) | `media/reviews/v5/coda_hilbert_sheet.jpg` |

Owned this round: `tools/sectionF/edl.py`, `tools/sfx/build.py`, `render/timeline.js` (not edited, it already follows
the last shot) and the section F timeline (`media/shots/F_edl.json`, regenerated). Not touched: S1/V3S stair layers
(`v5-stairs2`), `render/engine/**`, `timing.json`, the car shots.

## Jade decisions (this round)

- Merge: option A exactly as previewed (README Round 2: "merge looks good").
- Coda (README Round 2): committee line order (protagonist, glasses, teal tips, purple, braids, rest of the committee,
  colour ghosts, 8-bit Jade, more variants to infinity); the door opens the correct way; the ledger is full; the lobby is
  in full colour. Setup-session calls: FRONT DESK tab, no queue-shuffle gag, ledger = artists and mathematicians the
  film quotes, no game characters.
- **New, relayed by the coordinator (verbatim):** "i think the sound fade of the credits can build right into the
  coda, actually, so the ticking up of the lives is followed by the hotel door ring". Credits and post-credits are now
  one continuous piece. There's no black gap (coda.md's PC0 is dropped). The last counter tick (4,113 at 233.642) is
  followed one beat later by the door's bell (234.094) as the door starts to swing.
  - **My call on the ticks:** the blips fade but stay audible up to the ring (−12 dB over the fade instead of to
    silence). The last three peak at about −42 dBFS over a −55…−60 dB room, and the bell answers at −29 dBFS. Silent
    last ticks would have lost the hand-off.

## Part 1: the 3:23 merge (done)

- `tools/sectionF/edl.py`: F7_06 and F7_07 are replaced by F7_07m 202.88–205.52, the row from
  `tools/v5/merge/F7_07m.json`; the v4 lines are kept as comments. `--list` shows F7_05 202.02–202.88, F7_07m, F7_08
  205.52–207.28, and `F7_06` no longer appears in `F_edl.json`.
- **Soft leap fixed** (in `F7_07m.json`). The approach now plays at 1.0x via `srcTime`: frame 0 is held 0.065 s under
  the cut flash, then frames 1–9 show one per output frame, freezing on frame 9 at 0.44 s. Before, it was 0.74x with
  frameBlend, which gave the double image. Checked on frames: crisp, same freeze frame.
- `tools/sfx/build.py`: `merge_score` 203.32 (−16), `merge_lift` 203.76 (−12), `merge_seat` 204.64 (−11, 0.62 s
  pre-roll). Levels are the previz's measured peaks (−16 / −11.9 / −10.6). They are appended after the coda cues
  (stems 56–58), so no existing stem file was renamed (checked against the old cues.json). The cues are in both the v4
  mix and the v5 coda mix; both builds report `original_bit_exact_outside_cues` true and no ducking.
- Also updated: `docs/revisions/v5/fragments/merge.json`, `docs/sections/F.md` (cut list + v5 section),
  `media/shots/F7e/NOTES.md`, merge.md status line.

## Part 2: credits → Hilbert Hotel (done)

### Timeline (all on the ring-out beat grid, CODA_T0 226.400 + k × 0.4526)

| Time | Picture | Sound |
|---|---|---|
| 226.00–232.80 | O4: black, "never stop." (fades 231.0–232.8); credits overlay fades 231.0–232.8 | held chord + clock fade (−40 dB at the bell); counter blips fade to −12 dB |
| 226.00–234.19 | **O_counter** overlay (moved out of O4): ITERATION ticks 4,098 … 4,113 (233.642), fades 233.79–234.19 | one blip per tick |
| 232.80–236.357 | **PC1_door**: the door fades up from black (0.6 s) under the counter; the white glove slides in (233.10–233.75) and takes the handle | lobby air fades in |
| 234.034 / **234.094** | the push: the latch gives, and the door swings on its LEFT hinges into the lobby (0 → 64°, 1.05 s); the spring bell swings | `coda_door_latch`, **`coda_door_bell`** (tick k = 17) |
| 234.65–236.357 | the camera glides in (frame ×2.6, lobby ×1.9 for parallax); the glove stays on the handle | lobby air up to −38 dB RMS |
| 236.357–244.05 | **PC2_lobby**: the ledger close-up (1.3 s hold), the look up (to 3.0 s), the queue; the text box from 3.3 s types "Of course we have space for you." (▼, holds to the cut); a slow push toward the vanishing point 3.0 → 7.7 s; cut to black | lobby air, cut with the picture |

**The film now ends at 244.05** (coda.md planned 245.20 with a 0.7 s black gap; Jade's hand-off note removed it).
`render.mjs --list` range is [0, 244.05]. The 234.0 credits-only mix is kept as
`media/sfx/Rewind_cinematic_sfx_mix_v5coda_credits.mp3`; the new `Rewind_cinematic_sfx_mix_v5coda.mp3` is 244.050 s
(11,714,400 samples, the same as the picture). Constants that must stay in step: `CODA_BELL`, `CODA_DOOR_IN`, `CODA_END`
in both `edl.py` and `build.py` (`CODA_LOBBY` in edl.py only).

### The door (engine, $0; no Seedance retake)

`tools/sectionF/modules/hilbert_door.js`. The leaf (`media/shots/PC/door_leaf.png`) is cut from the de-redded
`door_color` still. Its glass is 0.55 alpha so the lobby shows through, and the gold crest stays opaque. It is hinged on
its **left** edge (x 560; the handle is on the right stile at x 1348), drawn in 140 vertical strips under a true
perspective rotation about the hinge, and swings **away from us into the lobby**. It sits behind the fixed frame
(`door_frame.png`, opening cut out) and in front of the open doorway (`doorway.jpg`, a nano edit with the door removed and
the lobby in focus). The **glove** is cut from Seedance take 1 at 1.25 s (the fist round the bar, BiRefNet + an arm
polygon). Its fist rides the projected handle point at the handle's depth, and the sleeve stretches back to the right
edge, so the hand never leaves the handle. The spring bell hangs inside the doorway (it was behind the glass in the
still) and is set swinging (damped, 3.1 Hz) when the door starts to move. A warm light spill grows as it opens.

### The lobby (full colour) and the line of Jades

- Plate `media/shots/PC/lobby.jpg` is built in three steps:
  - a nano empty hall in O2's palette with a teal-and-gold carpet (`gen/lobby.png`);
  - an outpaint to 4:3 showing the whole open ledger, blank (`gen/lobby_tall.jpg`);
  - de-red (the desk was 24% red), Real-ESRGAN ×2, de-red again, saved as 4:4:4 JPEG (0.07% red).
- Sprites `media/shots/PC/sprites/`:
  - **Committee, standing:** two nano edits of `inputs/committee_v3_long_ponytails_ff.png`, keyed off a flat grey ground:
    `glasses` (round glasses, twin-tails), `teal` (teal tips), `purple` (bob), `braids`, `plain`, `sleepy` (bun, eyes
    closed, head tilted), `rainbow` (curly, bag of chips), `mint` (mint jacket, bubblegum). The jacket is white with the
    orange band and pale-blue dot; each has black trousers and white sneakers added.
  - The protagonist: v5-coda's `jade.png`.
  - Seven ghosts: her drawing tinted in the film's ghost palette, translucent, with a glow.
  - **8-bit Jade:** a nano pixel-art sprite re-gridded to 17×46 pixels with a 14-colour palette, drawn unsmoothed.
- `tools/sectionF/modules/hilbert_lobby.js`: one-point perspective about vp (960, 523).
  - The camera is above their heads (her head is 140 px below the vanishing point), so each Jade further back stands
    higher and the line **rises over the protagonist's bun into the vanishing point**.
  - The order is protagonist (centre front, at the desk), then glasses (right behind her, to her left), teal, purple,
    braids, plain, sleepy, rainbow, mint, then the seven ghosts, then 8-bit Jade, then a seeded mix of all of them,
    about 1,600 deep (specks at the end).
  - The named eight alternate ±125 px around the queue's axis (a real queue, each face showing). Past them the line
    snakes gently along the carpet (±230 px at d = 1), so the tail stays visible one behind another into the vanishing
    point.
  - The desk is re-drawn over everyone's legs.
- **Ledger:** room numbers down a violet margin rule, Reenie Beanie ink (stroked for weight), warped onto the two page
  quads by strip homography and multiplied onto the paper. Every line is filled:
  1 Maurits Escher · 2 Roger Penrose · 3 Lionel Penrose · 4 Wassily Kandinsky · 5 Salvador Dalí · 6 Gustav Klimt ·
  7 August Möbius · 8 Stefan Banach · 9 Alfred Tarski · 10 David Hilbert.
  - These are the names the docs show the film quoting: Escher (*Relativity*, *Ascending and Descending*), the Penroses
    (the stairs), Kandinsky (shapes, ghost palette), Dalí (the melting clock), Klimt (the gold sky), Möbius (the road),
    Banach–Tarski (3:23), Hilbert (the billboard, the hotel).
  - Cantor is not referenced anywhere, so he is left out.
  - "M. C. Escher" became "Maurits Escher" because the hand's capital C reads as an L.
- Text box: the engine `dialogue` module with A_dialogue's rect/size, `speaker: FRONT DESK`, `close: 0`.

### Checks done

- Frames reviewed on two contact sheets (door every 0.2 s, lobby every 0.4 s) and on full-res stills at 236.6, 242.4
  and 244.0:
  - the hinge is opposite the handle and the glove is on the handle throughout;
  - the bell lands as the door moves;
  - the ledger is legible in the close-up;
  - the queue runs straight down the carpet with the protagonist at its head;
  - glasses Jade is right behind her, then teal, purple and braids;
  - the tail goes into the vanishing point;
  - the ghosts and 8-bit Jade are in the tail.
- Counter readings: 4,110 at 232.4, 4,111 at 232.8–233.1, 4,112 at 233.2–233.6, then 4,113 as it fades.
- Clip audio: the last ticks peak at −42 dBFS (232.74 / 233.19 / 233.64), and the bell at −28.8 dBFS on 234.094.
- **Red:**
  - The plates measure 0.07% (lobby), 0.23% (door), 0.29% (doorway).
  - The encoded 540p clip flags at most 1.4% (door) and 1.9% (lobby). These are dark brown ink-line pixels (mean RGB
    99,51,47) plus the protagonist's canon orange headphones; no visible red.
  - For comparison, the accepted clips flag 1.4% (`0323_merge.mp4`) and 3.4% (`coda_credits_fade_after_540p.mp4`, O2).
- No speech and no "Authority" anywhere; no game characters.

### Weak spots / open

- The ghosts and 8-bit Jade are small: at d ≈ 5–8 behind eight committee Jades they read as colour in the tail at 540p,
  and as figures at 1080p. A longer hold or a bigger push would show them more.
- At the widest swing (64°) the fist sits at the door's edge, so the brass bar is hidden under it. It reads as holding
  the door, but the bar itself isn't visible.
- The lobby push-in and the door glide are 2D (the lobby plate is one image). The door shot has two-layer parallax.
- The glove is a 720p Seedance cut, scaled 1.53×. It is a little soft next to the 2K leaf at 1080p.
- The previz files `tools/sectionF/coda/previz_timeline.js` / `hilbert_lobby.js` are superseded. The previz timeline
  would now overlap PC1, so don't run it.

## Files

- Edited:
  - `tools/sectionF/edl.py`
  - `tools/sfx/build.py`
  - `tools/v5/merge/F7_07m.json`
  - `docs/sections/F.md`
  - `docs/revisions/v5/merge.md`
  - `docs/revisions/v5/coda.md` (status)
  - `docs/revisions/v5/fragments/merge.json`
  - `media/shots/F7e/NOTES.md`
  - regenerated: `media/shots/F_edl.json`, `chosen.json`s
- New code:
  - `tools/sectionF/modules/hilbert_door.js`
  - `tools/sectionF/modules/hilbert_lobby.js`
  - `tools/sectionF/coda/gen_build.py` (the stills, prompts in it)
  - `tools/sectionF/coda/prep_pc.py` (plates / sprites / door: `tools/engrave/.venv/bin/python tools/sectionF/coda/prep_pc.py [plates] [sprites] [door]`)
  - `tools/sectionF/coda/pc_test_timeline.js` (stills of the coda without the whole film)
- Media (gitignored):
  - `media/shots/PC/` (`gen/` holds the stills, each with a `.json` of model, prompt and refs)
  - `media/sfx/*_v5coda*`, rebuilt
  - `media/sfx/Rewind_cinematic_sfx_mix_v5coda_credits.mp3` (the 234.0 version)
  - the v4 mix rebuilt with the merge cues
  - the clips above
- Hand-over: `docs/revisions/v5/fragments/build.json`.
- **Whole-film render (setup session):** pass `--audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3`. The film is
  244.05 s.
