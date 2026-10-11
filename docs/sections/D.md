# Section D: Drop 2 + "Anomaly detected" (112.96–141.00)

Shots E1, E2, E4–E8. E3 (119.44–122.95, singing #2) belongs to the singing director, and its slot is left empty.
Timeline: `render/timeline/D.js`. It is **generated** by `tools/sections/D/build_timeline.py` from `media/shots/_D/takes.json`, so edit those two files rather than D.js.
EDL mirror: `media/shots/D_edl.json`.
Solo preview, with a slate in the E3 slot:
`node render/engine/render.mjs --timeline render/timeline/_D_solo.js --range 112.96 141 --preview --encode`
→ `render/engine/out/D_solo/D_solo_preview_112.96-141.00.mp4`.

## Status

All shots are in the engine and render end to end. The merge check against E.js shows no overlaps: D ends at 141.00 and G1 starts there.
`render/timeline.js --list` currently fails because of **section A**: `A.js` imports a missing `_A_tracks.js`. That is not a D problem.

| Shot | Time | Content | Source clips (Seedance 2.0 720p, engraved) |
|---|---|---|---|
| E1 | 112.96–113.89 | The frame floods orange, a pale-blue multiply wash passes over it, and a 260-mote Kandinsky burst comes from her start pose with a white flash and shake. Underneath, she bursts off her mark on the L tracks. | `trk_sprint_1` |
| E2a | 113.89–114.905 | **L tracks, chops 1–3.** Each attempt ends exactly on its chop and freezes there as a coloured ghost. The next attempt begins with a 3-frame ◀◀ scrub (0.25 s of source), then plays: sprint → superman dash → wall-kick backflip. | `trk_sprint_1`, `trk_dash_1`, `trk_walljump_1` over a clean plate `E2/plate_trk.png` |
| E2b | 114.905–116.95 | **Grant Park ground level, chops 4–8, a hard cut on every chop**: slide under the arms, aerial cartwheel over them, leapfrog vault, spin past (two poses). | `fld_slide/cartwheel/vault/spin_1` |
| E2c | 116.95–119.44 | **The constellation, chops 9–13.** In a wide, she circles the ring of 8 agents. Ghosts 1–8 already stand around it: 1–3 small on the elevated tracks, 4–8 on the lawn. Every chop freezes another ghost where she is at that moment. A slow 1.06 push-in runs throughout. | `ring_circle_1` (srcTime remap so every chop lands on a visible pose) |
| HUD | 113.89–119.44 | `GHOSTS n`, Press Start 2P, top right, ink on a paper chip. It ticks +1 on each chop with a snap odometer roll. | |
| E4 | 122.95–126.25 | **"Rewind." #2, Super Meat Boy replay.** She leaps the gap in the L tracks toward the bewildered agents. Six earlier and later attempts on the same route (±0.33/0.67/1.0 s) fan in over 0.6 s, each in its own hue, so a stream of colour pours across the gap. A residue ribbon follows her matte. The lyric is IM Fell in Jade orange (residue). | `e4_stream_2` |
| E5a | 126.25–127.88 | **Co-op boost** (Celeste). The kneeling twin is a blue ghost: the left part of the frame's matte is colourised. She steps into the cupped hands and vaults onto the roof. | `e5_boost_2` |
| E5b | 127.88–128.76 | **Slip hand-off.** A gold ghost twin hands her the folded slip. | `e5_hand_1` |
| E5c | 128.76–130.50 | Insert: her hands hold the slip, and *What's an anagram of / Banach–Tarski?* is already written in graphite (`pencil` module, corner-pinned to the paper; the slip barely moves, ≤8 px). It is held 1.74 s. | `e5_slip_1` |
| E6a | 130.50–131.38 | **Banach–Tarski.** She stands, smirking, as agents close in from both sides. On beat 75:2 (130.94) the frame freezes and flashes. She bursts into 150 orange/blue/white motes, and her spot becomes a clean plate (nano-banana removal → engraved → feathered composite). | `e6_single_1` |
| E6b | 131.38–134.00 | Two motes clouds implode (time-reversed) into **two Jades**, back to back. They burst apart in opposite directions while the agents collide and split. The orange and blue ribbons trail them. | `e6_split_1` |
| E7 | 134.00–139.00 | **A cut on every beat (12 cuts):** hero run at camera with ghosts flanking, agent's residue meter spinning (×3, the shake grows), Loop aerial (×2), stream gap jump, field vault, split pair, cartwheel. Over the top, 24 Kandinsky ribbons pile up (one every half beat, none leave), and a multiply colour wash rises to 0.4 so the frame saturates. A full white flash ends the last cut. | `e7_hero_1`, `e7_meter_1`, `e7_city_1` + reuse |
| E8a | 139.00–139.68 | **"Anomaly"**: hard freeze (0.08 s hold) and a woodblock negative. In the ring of agents, all heads snap to camera in unison and the sunglasses read white. A terminal panel types `TIME VARIANCE █████████` / `ANOMALY DETECTED.` on the spoken words. | `e8_ring_1` |
| E8b | 139.68–140.12 | "detected": a row of six agents in profile snaps to camera together, still in negative. | `e8_line_1` |
| E8c | 140.12–141.00 | The agency terminal fills the screen in alarm, white on ink, IBM Plex Mono 88 px: `TIME VARIANCE █████████` / `ANOMALY DETECTED.` / `TRACE: LOCKED` (typed). It cuts to G1 on 141.00. | ENG |

## Revision 2 (coordinator notes)

1. **E1** is now residue, not confetti. A coloured-pencil radial bloom (`tools/sections/D/bloom.py` → `media/shots/_D/e1_bloom.png`: orange core, pale blue, a little gold at the rim, radial pencil strokes and paper tooth, with an additive glow copy) expands from her as a wave and clears. Nine residue ribbons (orange → blue or gold, pencil grain, bloom) stream outward, and the motes are round orange/blue/gold only. The flat orange solid is gone.
2. **Ghosts are luminous coloured-pencil afterimages.** Each frozen iteration is baked by `tools/sections/D/ghostsprite.py` into a full-frame RGBA sprite (cached in `media/shots/_D/sprites/`):
   - lifted pastel interior at about 0.9 alpha, with her own line work kept as darker hue strokes and 45° pencil hatching;
   - a thin bright outline in the hue;
   - a soft outer glow in the hue.

   Distant ghosts get a thicker outline and glow so they survive downscaling. They are placed as image layers. In E2a/E2b each ghost freezes where she was, then glides over 0.35 s to its own spot (E2b fans away from the agents). E2c positions were re-spread so nothing stacks on the agents. The moving ghosts in E4/E7 are engine ghost instances, raised to 0.75–0.8 opacity.
3. **E2c** runs a slow push-in from 1.10 to 1.22, and ghosts 1–3 on the track deck are larger (scale 0.24) and outlined. They now read as small coloured Jades.
4. **E8** redaction: left as the engine's inverted mode, as directed.
5. **Wall-kick retake swapped in:** `trk_walljump` take 2, re-prompted "no visual effects". It has no rainbow trail and does a clean column kick into an inverted backflip. Ghost 3 freezes on the inverted flip (3.62 s, played at 1.4×).

**A bug found while doing this:** the ribbon module wants absolute design px, but my paths were centre-origin, so most residue ribbons in revision 1 were half off-screen. `ribbon()` now converts. The E2 trails, E4 follow, E6b split trails and E7 pile-up all show now.

## Ghost choreography (the 13 chops)

The chop times come from `timing.json → lyrics.vocal_chops`. Ghost k is revealed on chop k (ghosts layer `on: [t]`, with a 0.12 s pop).
Each chop also gets a pale-blue flash (0.08 s, 0.35), a VHS-rewind blip (0.12 s) and a 3.5 % zoom punch.
Ghosts are the matted frame at `freeze` (source seconds) of the clip, baked as luminous sprites (see revision 2).
For hits 1–8, the clip's in-point is solved backwards from the freeze, so the live pose on the chop frame *is* the ghost.
Hues follow the Kandinsky order (orange, blue, gold, magenta, green), then the in-betweens.

| # | Chop | Clip (engraved) | Freeze s | Hue | Where it lives in E2c (design px from centre; scale) |
|---|---|---|---|---|---|
| 1 | 113.89 | `E2/take_trk_sprint_1` | 2.75 | #F08A24 | elevated track deck (−404, −288) × 0.24 |
| 2 | 114.35 | `E2/take_trk_dash_1` | 1.96 | #3E6FD8 | track deck (−34, −356) × 0.25 |
| 3 | 114.78 | `E2/take_trk_walljump_2` | 3.62 | #C9A227 | track deck (370, −288) × 0.24 |
| 4 | 115.24 | `E2/take_fld_slide_1` (jmatte) | 3.15 | #C23B8E | lawn front-left (−820, 390) × 0.40 |
| 5 | 115.67 | `E2/take_fld_cartwheel_1` (jmatte) | 1.83 | #3FA55B | lawn left (−654, 81) × 0.40 |
| 6 | 116.03 | `E2/take_fld_vault_1` (jmatte) | 3.00 | #E4572E | lawn back-right (679, −225) × 0.30, flipped |
| 7 | 116.52 | `E2/take_fld_spin_1` (jmatte) | 2.30 | #8DB8E8 | lawn front-right (482, 288) × 0.42 |
| 8 | 116.95 | `E2/take_fld_spin_1` (jmatte) | 0.95 | #E8D04A | back-left (−688, −234) × 0.30, flipped; pops on the cut |
| 9 | 117.39 | `E2/take_ring_circle_1` (jmatte) | 1.13 | #8E5CC8 | where she is (front right) |
| 10 | 117.83 | same | 1.71 | #2BA59A | back right |
| 11 | 118.25 | same | 2.40 | #F28DB2 | back left |
| 12 | 118.71 | same | 3.21 | #4B4FC4 | front left |
| 13 | 119.15 | same | 3.62 | #9CCB3B | front right, by the agents |

Ghosts 1–3 and 4–7 first appear in their own shots, frozen exactly where she was. In E2c they reappear as the committee around the agents.
The full table, including the E4 swarm instances, is in `media/shots/_D/ghost_table.json`.

## Typography

| Shot | Text | Module and font |
|---|---|---|
| E2 | `GHOSTS n` counter (one HUD cluster only) | `hud` mode `iteration`, Press Start 2P |
| E4 | "Rewind." | `lowerthird`, IM Fell, Jade orange, because the lyric is residue |
| E5c | Anagram slip | `pencil`, Reenie Beanie graphite, corner-pinned |
| E8 | Agency terminal | `terminal`, IBM Plex Mono, alarm inverted |

The agency is always written `TIME VARIANCE █████████`. In alarm the redaction bar draws in the inverted ink, so it is a paper-coloured bar on black. The engine's terminal module does this.
No model-drawn text anywhere: every keyframe was prompted blank, and the slip was blank paper.

## Changes from the shot list (and why)

- **E1** comes out of the CONTINUE ◀◀ (section C) straight into her first deliberate attempt on the L tracks, under the colour flood. The impact gets the burst and the colour fill, and she is moving before chop 1, so the first ghost has a run to freeze.
- **E2** cuts by setting (tracks → field → ring) rather than "around the field and the L tracks" at random. The ghost count stays legible, and every ghost freezes where she was before E2c gathers them into the constellation.
- **E5** "boost onto a rooftop": the Seedance take has her vault a blank engraved wall onto a cornice rather than a rooftop seen from above. It still reads.
- **E7** adds an agent's **residue meter** prop: a pocket-watch-like dial whose needle spins wildly, shown three times with growing shake. "Agents' residue meters spinning wildly" needed an object. The dial has tick marks only, no numbers.
- **E8**: the agents turn in two shots (ring, then line) on "Anomaly" and "detected", then the full-screen terminal holds for the last 0.88 s. The words are typed by the panel first, so the terminal never lags the voice.

## What's weak

- **E2c is still a medium-wide** (push-in 1.10 → 1.22). The ghosts on the track deck are small and only read as poses thanks to the outlines; the 720p source keeps them soft.
- **E2 ghosts glide** from where she froze to their spread positions (0.35 s). This keeps them legible, but it is not strictly "stays where it was".
- **E7 ribbons** now cover most of the frame by the last bar (24 ribbons plus the wash). That is the "saturating" intent, but the meter close-ups get busy.
- **E5a and E5b**: both girls are generated as two copies of Jade, and the "ghost" is a colourised matte region of the left girl, with a box split at x = 0.345 / 0.5. In E5a, if the jumping Jade crosses that line, part of her would tint; that does not happen in 126.25–127.88.
- **E6a's clean plate** shows a faint blur where her shadow was. It is hidden under the motes and lasts 0.44 s.
- **E8a**: the ring agents only half-turn (Seedance made a mild move). The unison snap really lands in E8b, the line.
- **chosen.json**: each shot folder holds several clips, so `chosen.json` is keyed by clip name. The real timeline usage (in/rate/srcTime/freeze) is in D.js and `takes.json`.
- **E3 → E4 seam**: E4 starts at 122.95, the end of the E3 slot, rather than 123.00, to avoid a 1-frame gap. The singing director's E3 should end at 122.95.

## Cost

Section D spend (unchanged by revision 2): **$18.47** list-price estimate (budget $50). This already counts walljump take 2, which was still queued at hand-off.

| Item | Cost |
|---|---|
| 16 nano-banana-pro calls (15 keyframes, including the ring retry, plus 1 clean-plate edit) | ≈ $2.15 |
| 1 seedream-5-pro ring alternative | $0.10 |
| 23 Seedance 2.0 720p takes, 4–5 s, including walljump take 2 | ≈ $16.2 |

Project total at hand-off: $123.02 of $400.

## Tools written (`tools/sections/D/`)

| File | What it does |
|---|---|
| `kf.py` | Keyframe prompts and generation |
| `dgen.py` | Registers the D_* shots into `vgen` at run time, so the shared `tools/gen/shots.py` is untouched; submit/collect |
| `publish.py` | Links a take into `media/shots/E#` and runs `tools/engrave` with the matte kept |
| `jmatte.py` | Jade-only matte. BiRefNet keeps agents that touch her; this gates the matte by her coloured pixels and/or a box (`--box --nocolor` makes the twin mattes) |
| `mtrack.py` | Matte centroid/bbox per frame |
| `ghostcheck.py` | Ghost freeze-frame review sheets |
| `trim.py` | Model paper-margin trim |
| `sheet.py` | Dense contact sheets |
| `build_timeline.py` | Generates D.js, the EDL mirror and the ghost table |
