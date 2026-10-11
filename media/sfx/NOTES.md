# Rewind (cinematic edition): sound-design layer

Music comes first. The original track is untouched: it is never re-levelled, ducked or normalised. The SFX sit in the
holes in `docs/recon/audio_map.md` (the intro, 41.22–41.89, 84.04–84.74, 92.79–93.07, 111.61–112.49,
161.63–162.27 and the ring-out), or they sit well under the music.

## Files (media/sfx/, gitignored apart from this note)

| File | What |
|---|---|
| `stems/NN_<id>.wav` | One cue per file, float32, 48 kHz stereo, at its final gain (any vocal ducking is baked in). Sample 0 sits at `start_s` / `start_sample` |
| `cues.json` | Every cue: placement (`start_s`, `start_sample`, `anchor_s`), source, priority, gain, plus the listening proxies below and a render summary |
| `sfx_only.wav` | All the cues summed over the full song length (227.960 s, 10,942,080 samples), 24-bit |
| `mix_preview.wav` | `source.wav` + SFX, sample-aligned, 24-bit |
| `Rewind_cinematic_sfx_mix.mp3` | The same mix as 320k MP3. Decoded, it is 0 samples off the WAV and the same length |
| `gen/` | The paid sources: five eleven-v3 "Continue?" takes and four music-v2 impact candidates |
| `verify.json`, `review_sheet.png` | Whisper lyric checks and a spectrogram sheet (original, mix and SFX for each cue) |

Rebuild everything with `~/Documents/moongazing/.venv/bin/python tools/sfx/build.py`, then run `tools/sfx/verify.py`.
Generation is cached in `tools/sfx/generate.py`, so re-running it costs nothing.

Time zero is the same as in `analysis/cinematic/source.wav`: the MP3 with its encoder delay removed, which is what an NLE plays.

## Render checks

- **Integrated loudness:** original −15.77 LUFS, mix −15.77 LUFS (Δ −0.001 LU). No gain compensation was needed.
- **True peak:** original −3.74 dBTP, mix −3.74 dBTP, and the decoded MP3 −3.72 dBTP. Nothing clips; the loudest cue moment reaches −4.4 dBFS.
- **Original untouched:** every sample outside the cues is bit-identical to `source.wav` (this is verified). No music ducking was used anywhere, so the ≤2 dB allowance went unused.
- **Lyrics are still intelligible:** Whisper large-v3 gives the same transcript for the original and the mix on every lyric that shares time with a cue. The checked lines are "I get shot and time stops" ×2, "And now I'm back", "Sirens in my mirror", "Reload", "Anomaly detected", "speeding down Lakeshore" and "Never stop".
- **Announcer:** the stem alone transcribes as "Continue."; in the mix the window transcribes as "Can you continue?" (Jade's breathy "and" runs into it).

## Cues

The listening proxies, computed per cue over its active window (where the cue is within 20 dB of its own peak):

- **S−M:** cue loudness minus music loudness, in LU.
- **mom:** the worst 400 ms window of the same comparison.

"Gain" is the stem's peak in dBFS before any vocal ducking. "Duck" is the most the cue is pulled down under the vocal stem's envelope (vocal sidechain).

| # | Cue | Start (s) | Shot / moment | Source | Gain | Duck | S−M / mom (LU) | Priority |
|---|---|---|---|---|---|---|---|---|
| 1 | rew_button | 1.900 | C2: cassette REW key press + latch | procedural | −31 | – | −19.6 / −19.6 | optional |
| 2 | rewind_whir | 1.900–7.240 | C2: the song itself read **backwards** at ×2/×4/×8/×16 from 213 s (octave steps keep it in key), tape-head band-pass, flutter, Bb motor tone, hiss; hard cut at 7.24 | procedural (copy of the mix) | −29 | – | −17.6 / −13.4 | **essential** |
| 3 | rewind_ticks | 1.900–7.22 | C2: clock ticks accelerating 8ths → 16ths (3.68) → 32nds (5.48) → 64ths (6.36), subdivided from the tracked beats | procedural | −26 | – | −30.7 / −27.2 | **essential** |
| 4 | rewind_stop | 7.240 | C3 landing: STOP key clack + transport thunk under the sub swell | procedural | −21 | – | −19.7 / −19.7 | **essential** |
| 5 | shot1 | 40.240 | P4 whispered "shot": distant gunshot slowed to 0.8× and low-passed at 1.4 kHz (below the whisper's fricative band), with a sub body and a dreamy tail into the freeze | music-v2 `gunshot_far` + procedural | −19 | 3 | −19.8 / −19.8 | **essential** |
| 6 | tapestop1 | 40.650 | P5: the last instrumental beat (stem copy, 40.21–40.65) slowed to a halt over 0.5 s | procedural (instrumental stem) | −26 | – | −10.4 / −10.4 (over the band's stop tail) | **essential** |
| 7 | pause_open | 41.400 | P6 menu appears: 8-bit Bb5 → F6 | procedural (pulse) | −31 | 2 | −16.3 / −16.3 | **essential** |
| 8 | cursor_move | 41.620 | P6 cursor RESUME → REWIND: Bb6 tick | procedural (pulse) | −33 | 2 | −12.7 / −12.7 (in the hole) | **essential** |
| 9 | menu_select | 42.060 | P6 REWIND chosen on "st-": F5 Bb5 C6 F6 arpeggio over the riser | procedural (pulse) | −31 | 2 | −23.0 / −23.0 | **essential** |
| 10 | siren_v2a | 56.540–63.62 | V2a chase: two distant sirens, wail Bb4↔F5 and C5↔F5 over 2-bar periods, low-passed and reverberant | procedural | −25 | – | −22.3 / −18.9 | optional |
| 11 | bridge_bell | 72.480–76.0 | V2c: bascule-bridge warning bell (Bb5 partials) on 8ths, ducked under the "oh" swell | procedural | −25 | 8 | −22.7 / −18.2 | optional |
| 12 | jump_whoosh | 84.040–84.84 | V2d airborne in the full-band hole: sub rumble plus high air, skipping the vocal band | procedural | −31 | – | −23.7 / −21.6 | optional |
| 13 | car_slam | 84.860 | V2e "back" on the bar-49 downbeat: generated slam + 48 Hz thud + spark scrape L→R | music-v2 `car_slam` + procedural | −15 | 3 | −17.6 / −17.6 | **essential** |
| 14 | siren_v2f | 88.600–92.7 | V2f "sirens in my mirror": one far siren peaking in the vocal rest 89.26–90.19, fading as the line starts | procedural | −26 | 10 | −27.1 / −16.1 | optional |
| 15 | train_smash | 92.790–92.935 | V2g Kaizo trap: L-train crash, hard-cut with the cut to black | music-v2 `train_smash` + procedural | −20 | – | −11.8 / −11.8 | **essential** |
| 16 | reload_click | 92.955 | V2g→h: slide "chk" (92.955) + "chk" (93.015) in the 0.28 s vocal gap | procedural | −17 | – | −10.4 / −10.4 | **essential** |
| 17 | loading_blip | 93.070 | V2h LOADING: soft F6 → Bb6 boot blip under "Reload." | procedural (pulse) | −35 | 4 | −16.8 / −16.8 | optional |
| 18 | shot2 | 110.780 | V2m whispered "shot" #2: same gunshot from another angle (0.75×, panned R, tail cleared by 111.39) | music-v2 `gunshot_far` + procedural | −20 | 3 | −21.6 / −21.3 | **essential** |
| 19 | tapestop2 | 111.220 | V2n: tape stop of the last instrumental beat over 0.36 s | procedural (instrumental stem) | −30 | – | −24.0 / −24.0 | optional |
| 20 | continue_vo | 111.270 | V2n arcade announcer **"Continue?"** in the quiet 111.26–111.62 window, clearing before "time" (111.94). Arnold voice, tape-slowed to 0.89×, cabinet-speaker EQ, short hall. Sits 7 LU under Jade's "time" | eleven-v3 `continue_arnold_a` | −19 | – | −2.0 / −1.1 (hole) | **essential** |
| 21 | rewind_slam | 112.660 | V2n: her hand slams the arcade ◀◀ button on "st-" | procedural | −30 | 3 | −21.6 / −21.6 | optional |
| 22 | anomaly_glitch | 139.000–140.18 | E8: sparse HUD glitch ticks, bit-crushed bursts and micro-stutters on a 32nd grid, high-passed | procedural (+ grains of the mix) | −15 | – | −22.6 / −20.1 | optional |
| 23 | pencil_stroke | 146.320–147.57 | G3: graphite-on-paper stroke (velocity-shaped grain, paper resonances), panned L→R | procedural | −28 | – | −21.8 / −20.3 | **essential** |
| 24 | crank_ratchet | 147.640–148.03 | G4: wooden ratchet clicks on 32nds into the turn | procedural | −26 | – | −27.8 / −27.8 | **essential** |
| 25 | crank_clunk | 148.080 | G4: the city clunks 90° on the returning kick (F2 body, F3 knock, short grind) | procedural | −21 | – | −17.2 / −17.2 | **essential** |
| 26 | mobius_crank | 161.640–162.30 | M2: crank ratchet on 16ths through the 161.63–162.27 hole, soft clunk on the 162.30 chord | procedural | −29 | 3 | −27.5 / −25.4 | optional |
| 27 | outro_clock | 223.685–227.6 | Ring-out → O4: the intro's 8th-note clock returns (0.226 s), fades in under the decaying pad, ducks under the final whisper | procedural | −25 | 9 | −27.8 / −7.8 (over silence) | **essential** |
| 28 | counter_roll | 226.852–227.87 | O4 `ITERATION 4,097` keeps rolling: 8-bit digit flicks after the whisper, accelerating like the cold open and fading out | procedural (pulse) | −32 | – | +0.2 / +1.0 (over −45 LUFS room tone; absolute −44.7 LUFS) | **essential** |

### Tuning and key

The track centres on F minor / A♭ major, and chroma shows B♭ dominant in the intro and verse 2. Every tonal cue therefore uses only F, A♭, B♭, C and D♭:

- **Blips:** B♭5, F6, C6, B♭6, F5.
- **Sirens:** wail between B♭4/C5 and F5.
- **Bell:** B♭5.
- **Crank clunks:** F2 and F3.
- **Rewind motor:** B♭ stepping up in octaves.

The rewind chatter is the song itself transposed by exact octaves (×2, ×4, ×8, ×16), so it stays in key.

### HUD sync for the editor

The rewind speed steps land at these times:

| HUD | Time (s) | Position |
|---|---|---|
| ◀◀ ×2 | 1.90 | bar 2 |
| ×4 | 3.68 | bar 3 |
| ×8 | 5.48 | bar 4 |
| ×16 | 6.36 | bar 4, beat 3 |

The whir hard-stops at 7.24. Counter-roll flicks fall at 226.852, 227.078, 227.248, 227.378, 227.478, 227.558, 227.624 and 227.680.

## Recommendation

**Essential (18).** These carry the game grammar and sit in holes or under transients:

- **Cold open:** rewind whir, accelerating ticks and the stop at 7.24.
- **Both deaths:** the gunshots, plus tape stop 1.
- **Pause menu:** the three blips (open, cursor, select).
- **The jump:** the car slam on "back".
- **The Kaizo trap:** train smash and reload click.
- **"Continue?"**
- **The pencil:** stroke, ratchet and crank clunk.
- **The ending:** the outro clock and counter roll, which loop back to the intro tick.

If the mix should be even sparser, keep these nine from that list: whir, ticks, shot1, the three menu blips, train smash, "Continue?" and counter roll.

**Optional (10).** Audition these against picture:

- **The sirens (10, 14) and bridge bell (11):** these are the only cues that sit inside a full groove. They measure −18 to −23 LU under the music; siren_v2f is fully masked on average and only surfaces in the 89.3–90.1 vocal rest. Keep them if the chase needs more "world"; drop them if anything feels busy.
- **anomaly_glitch (22):** in the loudest section of the song. The proxies say it is mostly masked (73 % of its energy is 15 dB or more under the music in its band), so at best it is a texture. It would only read with more gain, and I chose not to push it.
- **tapestop2 (19):** redundant with the band's own stop at 111.22, and it shares the window with "Continue?". Drop it first if that moment feels crowded.
- **Small sweeteners:** rew_button, jump_whoosh, loading_blip, rewind_slam and mobius_crank. They are harmless and cheap to drop.

Cut entirely: a tick-tock under the 210.90–211.50 band drop-out. It was fully masked by the whispered "Never stop", and raising it would have fought the whisper.

## Method notes and caveats

- **Proxies, not ears:** level against the music (LU), per-band masking (third-octave; "masked" = share of the cue's energy 15 dB or more under the music in its band), speech-band SFX-to-vocal ratio while she sings, and Whisper transcripts. All of them err quiet. A human pass on the optional cues and on the "Continue?" voice character is still the real test.
- **Generated sources:** music-v2 has no SFX mode. Its "single impact" prompts returned noise-like single hits (harmonic ratio ≤ 0.26, one onset, clean decay), and these are used only as trimmed layers on top of procedural cores. `train_smash_b` was not used.
- **Unused announcer takes:** four alternatives sit in `gen/`. Clyde has the deepest voice (f0 ≈ 108 Hz) and is a good swap if Arnold sounds too young.
- **Cost:** $0.045 in total (music-v2 4 × $0.0075, eleven-v3 5 × ≈$0.003).

## v3 revision (2026-10-11): "Continue?" removed

Jade's v2 note at 1:52: "don't use 'continue' voiceover". `continue_vo` is listed in `DISABLED` in `tools/sfx/build.py`
(its code and its stem slot 20 are kept, so the other stems keep their numbers) and is no longer in `cues.json` or
the mix: 27 cues, integrated loudness -15.77 LUFS (delta 0.0), original bit-exact outside the cues. The v2 outputs
are kept as `Rewind_cinematic_sfx_mix_v2.mp3`, `cues_v2.json`, `sfx_only_v2.wav`, `verify_v2.json`;
`stems/20_continue_vo.wav` is the stale v2 stem. Everything above that calls "Continue?" essential describes v2.

## v3 rebuild (2026-10-11, rev-A)

- `continue_vo` disabled (Jade, 1:52). Its stem slot 20 is kept so the other stem numbers don't shift.
- 13 cues from instance B's restaged chase (94.06–141.00), all procedural or reusing `gen/gunshot_far.mp3`, appended
  after the v2 cues in `tools/sfx/build.py`: `b_shadow_crumble` 97.18, `b_dash` 97.92, `b_land_skid` 98.16,
  `b_miss_1…4` 98.94/99.38/99.82/100.26, `b_miss_board` 101.14, `b_miss_turf` 102.00, `b_spawn` 107.75, `b_skid` 108.18,
  `b_atomize` 131.38, `b_implode` 131.82. Levels as B specified.
- Verify: original bit-exact outside the cues, integrated −15.77 LUFS (delta 0.0), true peak −3.74 dBTP, every lyric
  transcribes as in the original. At B's levels `b_dash`, `b_miss_1` and `b_spawn` (essential) and `b_shadow_crumble`,
  `b_miss_board`, `b_implode` measure fully masked (`sfx_energy_masked` 1.0); B decides whether to raise them.
- Previous mixes kept beside: `*_v2.*` (v2 delivery) and `*_v3a.*` (after the `continue_vo` removal, before B's cues).
- Second rebuild (B's final 2:03–2:14 cut): `b_dash` −20, `b_miss_1` −21, `b_spawn` −24 (+6 dB each, now 25 % / 75 % /
  11 % masked); new `b_boost` 130.04 (whoosh leads in from 129.79, palm-slap on the beat) and `b_pileup` 130.94, both
  optional; `b_atomize` / `b_implode` unchanged. 42 cues. Verify: bit-exact outside the cues, loudness delta 0.0, lyrics
  transcribe as before.
