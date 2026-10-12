# v5-coda: credits fade + post-credits Hilbert Hotel

Agent `v5-coda`, 2026-10-12. Cap before sign-off $5, tag `v5_coda_`. **Spent $1.58** (project total $245.82 of $400).

**Status (2026-10-12): built by `v5-build`** after Jade's round-2 notes. The credits now run straight into the Hilbert Hotel (no black gap; the bell rings one beat after the last counter tick), in full colour, with an engine-built door and the committee line; the film ends at 244.05. See `docs/revisions/v5/build.md`; clip `media/reviews/v5/coda_hilbert.mp4`. The plan below is kept as written.

Earlier status: the credits fade is **executed** (540p after clip below). The post-credits scene is **planned, with
candidate stills, a door take and a 540p previz; it is waiting for Jade's sign-off.** It is not in the film yet.

Jade's notes (v4 preview), verbatim:
> * credits sound fades out gradually as the life count ticks up in the corner
> * post credits scene: checking into the Hilbert Hotel
>   * emblem on the door (POV, Jade entering), a gloved hand opens the door, a slight ringing sound (of a door opening)
>   * cut to POV receptionist, looks up from desk and see an infinite line of Jades, led by protagonist Jade (a
>     committee of Jades from reference art, multi-colored ghosts from the video, etc), (no audible spoken words),
>     text box (styled like at 0:37 early in video)
>   * Receptionist: Of course we have space for you.

## Review files

| What | Path |
|---|---|
| Credits fade, after (540p, 221.0–234.0, with the new mix) | `media/reviews/v5/coda_credits_fade_after_540p.mp4` (0.8 MB) + `coda_credits_fade_after_sheet.jpg` |
| Credits, before | v4 preview `deliverables/wip/rewind_roughcut_v4_preview.mp4` 221.0–227.96 |
| New mix (beside the v4 one) | `media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3` (234.000 s), `mix_preview_v5coda.wav`, `sfx_only_v5coda.wav`, `cues_v5coda.json`, `stems_v5coda/` |
| Post-credits previz (540p, 230.0–245.2: end of the credits, black, door, lobby) | `media/reviews/v5/plans/coda/coda_previz_540p.mp4` (3 MB) + `coda_previz_sheet.jpg` |
| Candidate stills (each with a `.json` of model, prompt, refs) | `media/reviews/v5/plans/coda/`: `door_color.jpg`, `door_engraved.jpg`, `lobby_empty_engraved.jpg`, `lobby_line_engraved.jpg`, `lobby_line_color.jpg`, `committee_sheet.png` (+ cut-outs in `sprites/`) |
| Door take (Seedance 2.0 720p 5 s) | `media/gen/v5_coda_door/take_1.mp4` (+ `take_1_sheet.jpg`), red-checked copy `take_1_dered.mp4` |
| Door chime candidates | `media/reviews/v5/plans/coda/chime_procedural.wav` (used in the previz), `chime_musicv2.mp3` (ElevenLabs music-v2) |

## Findings (how the ending was built)

- **Where the film's length is set:** `render/timeline.js` returned `range: [0, T.duration]`. `T.duration` is
  `analysis/cinematic/timing.json` `source.duration_s`, 227.96 (not edited). `render.mjs` uses `tl.range` only for a
  whole-film render; `--range a b` renders anything. `mergeSections` fills slate gaps only up to `T.duration`, so shots
  after 227.96 are legal and nothing is filled after them. **No engine or timing.json change is needed.**
- **Audio:** `render.mjs` encodes `-ss a -t dur -i <audio>`, so a clip that runs past the end of its audio file just
  gets a short audio stream. The v4 SFX mix is exactly the song's length (10,942,080 samples).
- **What you heard under the credits in v4:** the ring-out Ab-major chord hits at 222.75 (−15 dBFS RMS) and decays to
  −39 by 225.75. The instrumental is then **cut** at 226.0 when the whisper starts (−45 → −55 dB within 0.25 s). After
  the whisper (226.0–226.86) there is only a −49 dB tail, and it stops dead at 227.96. Meanwhile the picture faded out
  227.0–227.96, and the counter rolled at 3/s from 226.45 (two or three ticks you could see). So the sound didn't fade:
  it was cut, and then the film ended.

## 1. Credits fade (executed)

**What changed**

- **Sound** (`tools/sfx/build.py --coda`, new mode; without the flag the v4 mix is rebuilt exactly as before, and the
  v4 stem numbering is unchanged, which I checked):
  - The song is padded with digital silence to `CODA_END` = 234.00.
  - `coda_pad`: the ring-out chord is held. It is a spectral freeze of the instrumental stem (223.3–224.5, two freezes
    with a slow drift between them). It enters as the original decays through −36 dB (225.0–225.7), sits ducked under
    the whisper, then fades out slowly: 0 → −40 dB as −40·x^1.7 over 226.9–232.6, so the start of the fade is gentle.
    Its low-pass closes towards 1.2 kHz as it fades.
  - `coda_clock`: the intro's 8th-note clock (v4 `outro_clock`) carries on past the whisper and fades with the chord.
    The last tick is at 232.5.
  - `coda_counter`: one soft 8-bit blip (F6/Bb6) per counter tick, fading with the chord. The ticks after 232.6 are
    silent, so **the counter keeps going after the sound has gone**.
  - v4's `outro_clock` and `counter_roll` are replaced in coda mode.
  - Measured (0.5 s RMS, dBFS): 226.5 −28 (whisper) · 227.0 −37 · 228.0 −40 · 229.0 −46 · 230.0 −53 · 231.0 −62 ·
    232.0 −73 · 233.0 silence. Everything before 222 is bit-identical to the v4 mix. The original song is bit-exact
    outside the cues, and no music ducking is used. The whisper keeps about 12 dB over the pad in the speech band
    (p90 of SFX−vocal −11.9 dB).
- **Picture** (`tools/sectionF/edl.py` → `media/shots/F_edl.json`; I checked the EDL regenerated byte-identically
  before the edit):
  - **O4** now runs 226.00–234.00. "never stop." holds, then fades out over 231.00–232.80.
  - **ITERATION** is a mechanical snap odometer. It reads 4,097 at the bar-129 downbeat (226.400) and goes up by one
    on every ring-out beat (0.4526 s): 4,098 at 226.853, …, 4,113 at 233.642. It fades over the last 0.4 s, and
    flicker is lowered to 0.2.
  - **O_credit** holds to 232.80 with the same 1.8 s fade.
  - The 227.0–227.96 shot fade is gone.
  - Constants: `CODA_END`, `CODA_T0`, `CODA_BEAT`, `CODA_TEXT_FADE` in edl.py. They mirror `CODA_END`, `CODA_T0`,
    `CODA_BEAT`, `COUNTER_TICKS` and `CODA_FADE` in build.py, so keep the two in step.
- **Length:** `render/timeline.js` now uses `range: [0, Math.max(T.duration, ...shots.map(s => s.end))]`, so the film
  ends where its last shot ends: **234.00 now** (+6.04 s), **245.20 with the post-credits scene** (+17.24 s).
  - This edit changed the frame-cache fingerprint of everything under `render/`. Every edit to a
    `render/timeline/*.js` does the same.
  - A whole-film render must now pass `--audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3`. The original mp3
    stops at 227.96, so an "original audio" upload would end in 6 s of silence. Use the coda mix for that version too,
    or keep that upload at the old length.

**Rendered:** `node render/engine/render.mjs --range 221.0 234.0 --preview --encode --force --audio
media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --out media/reviews/v5/coda_credits_fade_after_540p.mp4`.
I checked the frames: the counter reads 4,097 / 4,099 / 4,101 / 4,104→5 / 4,109 / 4,111 / 4,112 / 4,113 at
226.5 / 227.4 / 228.3 / 230.0 / 231.9 / 232.9 / 233.5 / 233.9, which matches the blip times.

## 2. Post-credits scene: plan (waiting for sign-off)

### Shot list (film times; the scene starts after the credits end at 234.00)

| Shot | In–Out (dur) | Picture | Style | Sound |
|---|---|---|---|---|
| PC0 | 234.00–234.70 (0.70) | black | | silence (a breath after the counter) |
| PC1 door | 234.70–237.70 (3.00) | Jade's POV at the Hilbert Hotel's front door. The gold emblem on the glass is an oval crest: **HILBERT HOTEL** arched over an infinity sign made from the looped bow of an antique room key. A **doorman's white-gloved hand** (dark-green livery cuff, thin gold braid; only hand and cuff, never a face) comes in from the right (~234.9), takes the brass handle and pulls the door open (it starts moving at 235.75). Warm light spills out, the little brass bell on its spring jiggles, and the camera glides in at walking pace. | Colour: coloured pencil in engraved hatching, the O2 look (her door at dawn rhymes with this one) | latch click 235.69 + the spring bell 235.75 (2–4 light strikes, Ab6/Eb7, in the ring-out's key), lobby room tone opening with the door |
| PC2 lobby | 237.70–245.20 (7.50) | The receptionist's POV from behind the desk. It starts looking down at the open guest ledger (lines numbered 1, 2, 3, 4 …), the brass service bell and the queue's legs past the desk edge (scale 2.2). It **looks up** (237.70+0.7 → +2.2, ease in-out) to the full frame: an endless one-point-perspective hall of columns and chandeliers. **Protagonist Jade** (canon outfit, bun with two crossed pencils, rainbow pencil in hand) stands at the desk, right of centre, facing us. Behind her the queue snakes back down the carpet to the vanishing point: the committee first (watercolour Jade, graphite-sketch Jade, woodcut-engraved Jade, then the orange and pale-blue ghosts), then Kandinsky-coloured ghost Jades (orange, pale blue, gold, magenta, green) shrinking to specks at the vanishing point. Everyone breathes (a slow bob); nobody speaks. **Text box** at 240.10, lower left like 0:37: the nameplate tab plus a white IM Fell box, typing **"Of course we have space for you."** (~2 s), ▼ caret, held to 245.20, then a cut to black. | **Recommended:** the lobby is a black-and-white woodcut engraving and only the Jades are in colour (the film's grammar: the receptionist's world is the engraving, and colour is Jade's perspective). Alternative: all colour (`lobby_line_color.jpg`) | room tone only; no speech; the box types silently, as at 0:37 |
| end | 245.20 | black; the film ends | | |

**Why the doorman's white glove:**
- It says *hotel* at once.
- White reads against the dark wood and the warm glass.
- It is the opposite of the agents' black suits, so the hand that opens the door is a welcome, not a threat.
- The livery cuff is dark green with gold, so no red.

The Seedance take delivered exactly this.

### How the infinite line is built (engine, cheap, already working in the previz)

- **Plate:** `lobby_empty_engraved.jpg` (nano-banana-pro, empty hall, strict one-point perspective, vanishing point at
  design (960, 518), desk top edge at y 853).
- **Sprites:** `committee_sheet.png` (nano, six Jades on white) is cut into RGBA by `tools/sectionF/coda/sprites.py`
  (border-connected white = background, so white jackets stay opaque) → `sprites/{jade, watercolor, engraved,
  graphite, ghost_orange, ghost_blue}.png`.
- **Module** `tools/sectionF/coda/hilbert_lobby.js` (Canvas2D) draws three things under one camera move: the plate;
  the queue far to near; then the desk strip again over their legs.
  - Person k stands at depth d = 1 + k·step. Their position is x = vp + (lane + zig + weave)/d, feet at
    vp.y + (feet − vp.y)/d, and height h/d.
  - The first 10 people zig-zag so each head shows.
  - Beyond them the queue snakes (±380 px world), so the tail reads as separate coloured figures running into the
    vanishing point instead of one smear.
  - About 600 people are drawn, and anyone under 4 px becomes a gold speck.
  - Ghosts are the graphite sprite tinted in the Kandinsky palette.
  - Optional `shift` key (0→1): the **Hilbert shuffle**. Everyone behind her steps up one place on a beat. It is not
    used in the previz.
- The text box is the engine's `dialogue` module with A_dialogue's rect and size (`[80, 856, 960, 132]`, 46 px).
- Previz params: `tools/sectionF/coda/previz_timeline.js` (front `{x 1210, feet 1311, h 1090}`, lane −340, step 0.8,
  zig 110 × 10, weave 380 / 0.42, count 600).

### What still needs work before final (from the previz)

- The near committee overlaps: the two ghost sprites (k 4–5) hide behind the engraved Jade. Fix it by spreading the
  first five wider (bigger `zig`, or per-person x offsets), or by making the line bend in a gentle S.
- At the desk close-up (scale 2.2) the 2K plate is soft at 1080p. Fix it by upscaling the plate ×2 with the repo's
  Real-ESRGAN (`tools/engrave`, free) or regenerating at 4K.
- The sprites are clean anime/watercolour against the engraving. That is the film's intended mismatch for Jade, but
  the protagonist could take a light `tools/engrave` colour pass (strength 0, bloom) to sit in the same hand as F.
- PC1 take 1 has a slightly odd double-door moment at 2.0–2.4 s of the clip (the door swings and a second handle shows
  through the glass). At film speed it reads fine. If Jade dislikes it, a retake costs $0.75.
- The lobby inside the door take is smooth and painterly (Seedance softening). It is out of focus, so it barely shows.
- Red: the colour door has mahogany and pinks. `tools/sectionF/dered.py` took take 1 from 6.5% to 0.7% max red
  (`take_1_dered.mp4`, used in the previz). The engraved lobby is at 0.06%.

### Cost

| Item | Spent (candidates) | To finish |
|---|---|---|
| 6 stills (nano-banana-pro 2K) | $0.80 | 0–2 more if Jade picks the all-colour lobby or wants more committee variants: $0–0.27 |
| Door take (Seedance 2.0 720p 5 s) | $0.75 | $0 if take 1 is kept; $0.75 per retake |
| Chime (music-v2) | $0.01 | $0 (the procedural bell is free) |
| Plate upscale, sprites, module, sound, renders | $0 | $0 |
| **Total** | **$1.58** | **≈ $0–1.0** |

### Questions for Jade

1. **Credits fade:** is this the fade you meant? The sound is gone by about 232.6, and the counter ticks on silently
   to 4,113 before the cut at 234.0, 6 s longer than v4.
2. **Lobby look:** woodcut-engraved lobby with only the Jades in colour (the previz), or all colour like O2
   (`lobby_line_color.jpg`)?
3. **Name on the text box tab:** `FRONT DESK` (previz), `RECEPTIONIST`, `HILBERT HOTEL`, or no tab?
4. **Optional gag:** at the end the whole infinite queue shuffles up one place, Hilbert's trick. Yes or no?

## Execution (after sign-off; a later agent can follow this)

Nothing below is done. Re-read every shared file right before editing it, and use exact-string edits.

1. **Assets into the shot tree** (new files; nothing overwritten):
   - Create `media/shots/PC/`.
   - Copy in `lobby_empty_engraved.jpg` (upscale ×2 first with tools/engrave Real-ESRGAN) and `sprites/`. Re-cut the
     sprites with `tools/sectionF/coda/sprites.py <sheet> media/shots/PC/sprites` if a new committee sheet is made.
   - PC1 source: `media/gen/v5_coda_door/take_1_dered.mp4` (or a retake via
     `$PY tools/sectionF/coda/vgen_coda.py submit v5_coda_door --res=720p`, then `dered.py`).
   - If Jade picks the all-colour lobby: generate an empty colour lobby with the `lobby_line_color` prompt minus the
     queue (the prompt text is in `media/reviews/v5/plans/coda/lobby_line_color.json`). Also run
     `dered.py --check`.
2. **Module:** move `tools/sectionF/coda/hilbert_lobby.js` to `tools/sectionF/modules/hilbert_lobby.js`. Fix the near
   overlap (see "What still needs work").
3. **EDL** (`tools/sectionF/edl.py`, after the O4 block):
   - Add `PC0_black` 234.00–234.70.
   - Add `PC1_door` 234.70–237.70: a `video` layer, `in` 0.4, `rate` 1.0, section grain.
   - Add `PC2_lobby` 237.70–245.20 with the two layers from `tools/sectionF/coda/previz_timeline.js` (`hilbert_lobby`
     params, and `dialogue` at local 2.40 with the speaker Jade chose).
   - Use explicit `layers` (as O4 now does), not `text`, so the layers keep `start`/`fadeOut`.
   - Then run `$PY tools/sectionF/edl.py` and `node render/engine/render.mjs --list` (range should read
     `[0, 245.2]`).
4. **Sound** (`tools/sfx/build.py`, coda mode):
   - Set `CODA_END = 245.20`.
   - Add coda-only cues ported from `tools/sectionF/coda/previz_audio.py`: `coda_door_latch` 235.69 (−30),
     `coda_door_bell` 235.75 (procedural `spring_bell`, −21, or the music-v2 file if Jade prefers it), and
     `coda_lobby_tone` from 234.70 (env −38 → −24 dB peak, as in the previz, ending with the 245.20 cut).
   - Add each new id to `CODA_ONLY`, and append the cues after `coda_counter` so the stem numbers hold.
   - Run `$PY tools/sfx/build.py --coda`. This writes `Rewind_cinematic_sfx_mix_v5coda.mp3` again. If the 234.0
     version must be kept, rename it first (e.g. `_v5coda_credits`).
5. **Check at 540p:**
   `node render/engine/render.mjs --range 222.78 245.2 --preview --encode --force --audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --out media/reviews/v5/coda_after_540p.mp4`.
   Then:
   - Check the contact sheet.
   - Check that the counter and blips match, and that the bell lands as the door moves.
   - Check that no red shows (`dered.py --check`) and that no "Authority" appears.
6. **Whole-film / 1080p** happens only in the setup session's final render (not in this pass), with
   `--audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3`.

## Files touched or added by v5-coda (not committed)

- Edited:
  - `tools/sfx/build.py` (coda mode, 3 cues, suffixed outputs)
  - `tools/sectionF/edl.py` (O4 / O_credit, coda constants; regenerated `media/shots/F_edl.json`)
  - `render/timeline.js` (range follows the last shot)
- New: `tools/sectionF/coda/` (`sprites.py`, `hilbert_lobby.js`, `previz_timeline.js`, `previz_audio.py`, `vgen_coda.py`).
- Media (gitignored):
  - `media/sfx/*_v5coda*`, `media/sfx/stems_v5coda/`
  - `media/reviews/v5/coda_credits_fade_after_540p.mp4`, `media/reviews/v5/coda_credits_fade_after_sheet.jpg`
  - `media/reviews/v5/plans/coda/`
  - `media/gen/v5_coda_door/`
- The v4 EDL and chosen.json backups are in the session scratchpad only. The v4 EDL can be regenerated from git's
  `tools/sectionF/edl.py`.
