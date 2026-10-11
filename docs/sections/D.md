# Section D: Drop 2 + "Anomaly detected" (112.96–141.00)

Shots E1–E8. E3 (119.44–122.95, singing #2) uses the singing director's take; it was placed here in revision 3.
Timeline: `render/timeline/D.js`. It is **generated** by `tools/sections/D/build_timeline.py` from `media/shots/_D/takes.json`, so edit those two files rather than D.js.
EDL mirror: `media/shots/D_edl.json`.
Solo preview:
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

## Revision 3: E3 placed in this timeline

- **Take:** `media/sing/E3/take_3_lips.mp4` (720p). It is not engraved: the pencil look is approved as made. The engine upscales it to 1080p with Lanczos when it extracts frames.
- **Lip sync:** `clip_time = song_time − 119.14 + lag`. The lag is set by **`E3_VARIANT`** at the top of `tools/sections/D/build_timeline.py`. The values come from `media/sing/review/E3_take_3_lips_ABC.json`, so they match the A/B/C composites Jade listens to:

  | Variant | Lag | Clip in at 119.44 | Lips |
  |---|---|---|---|
  | A | 0.90 | 1.20 | 0.15 s earlier |
  | **B** (default) | 0.75 | 1.05 | as measured |
  | C | 0.60 | 0.90 | 0.15 s later |

  To switch: change the constant, rerun the build script, re-render.
- **Ribbons:** seven orange/pale-blue coloured-pencil ribbons spiral in from beyond the frame edges and settle onto a tilted orbit around her head and shoulders. The orbit is centred (900, 470), radii 570 × 335, −10°, so it clears her head.
  Where an orbit crosses her body it passes behind her. An occluder layer redraws the same take through her first-frame silhouette (`media/sing/first/her_mask_first_frame.png`, eroded, with a stray plaza blob removed; it becomes `media/shots/E3/occluder_mask.mp4`). Her face is never touched.
- **Look:** a light pencil grain (0.045, size 1.2, on twos) plus paper 0.18, so her glasses stay intact.
- **Lyric:** "Rewind." in IM Fell, orange #F08A24, in the lower third, timed to the word.
- **Risk:** the takes keep the first frame's head pose, but if she drifted, the static occluder would let a ribbon edge show over her hair rim. I didn't see this in 119.5–122.9.

## Revision 4: rough-cut v1 review fixes (`docs/reviews/roughcut_v1.md`, top-10 items 3, 4, 8 and 9)

1. **Ghosts read as Jades (113.89–119.44, 127.88–129.62).**
   - **New ghost look:** `ghostsprite.py` now bakes a translucent line-art Jade in the F6c/F8 manner. Her own drawing is turned into a duotone: crisp hue-ink line work, eyes, mouth and hair at full alpha, a pale hue fill at about 0.55, a bright near-white rim in the hue and a soft hue glow.
   - **E2c sizing:** every constellation ghost is now **290 px tall (27% of frame height)**. Horizontal poses are limited by their width.
   - **E2c layout:** each ghost has its own slot around the agents.
     - Ghosts 1–8 already stand there; 8 pops on its chop.
     - Ghosts 9–12 freeze exactly where she is on their chop, then grow and glide to their slot in 0.35 s.
     - Ghost 13 stays where it froze.
   - **E2c push-in:** now 1.00 → 1.08, so every slot stays in frame.
   - **E5b gold twin:** the opaque twin is now a ghost.
     - A nano clean plate removes her from the left half (`media/shots/E5/plate_e5b_left.png`, feathered before the warp's black wedge, which caused the earlier seam).
     - She is redrawn per frame as a gold line-art ghost at 0.85 × ~0.6 fill with a glow outline (`tools/sections/D/ghostseq.py` → `media/shots/E5/ghost_twin_gold_{rgb,alpha}.mp4`).
     - Live Jade on the right is matted by `take_e5_hand_1_right/`.
2. **Anagram stall (126.25–130.50).** The total timing is unchanged (126.25 → 130.50).
   - **E5a** keeps 126.25–127.88. Its blank right half is filled with a nano-painted Loop street canyon with an L trestle (`plate_e5a_fill.png`, masked to the blank region). The duplicate girl that nano drew there was removed with a second edit.
   - **E5b** hand-off now runs **127.88–129.62 (1.74 s)**; the slip is visible in the twin's hand.
   - **E5c** is **0.88 s (two beats, 129.62–130.50)**, and the question is already written when it appears.
3. **E3 lyric.** "Rewind." is now ink on a paper halo, size 112, y 1000, below the jacket band, with the period. The ribbon orbit was retuned for the singing director's 1.3× push-in (centre (949, 571), radii 740 × 435). The occluder mask builder now applies the same crop remap as `tools/sing/polish.py remap-mask`. Their remapped cached mask is used as is.
4. **NYC landmarks.**
   - **E5b:** the Empire State Building behind her is replaced by a flat-crowned Chicago tower (nano edit, patched).
   - **E6a/E6b:** the ESB and Chrysler in the rooftop skylines are replaced by Chicago towers, including a Willis-like one. The fix is a nano edit of an engraved frame, patched where it differs.
5. **E7 ribbons** are capped at 10, one more per beat, thinner and with more pencil grain, so the meter close-ups stay readable.

**Still open after revision 4:**
- E6b's camera drifts slightly, so a small spire near the centre skyline is still visible late in the shot (about 133+).
- The Grant Park field plate (E2b and the E7 reuse) also has a spire resembling the ESB in its distant skyline.
- E4's stream still uses engine-tinted ghosts, not line-art.
- E8 redaction is left as it is, per the coordinator.

Cost of revision 4: 9 nano-banana-pro edits, about $1.21.

## Revision 5 (v3 pass): the restaged chase

Jade's v2 notes (`docs/revisions/B.md`, plan in `docs/revisions/B_research.md`). Drop 2 now replays the rev-B level
(platform → beam → chasm → lawn → hotel → wall → the tabletop street of books), always left to right or up, never at an
agent. Every shot from E1 to E7 uses the new `media/shots/B_<take>/take_1*` clips; the v2 tables above and below are
history. Review clips: `media/reviews/v3/B/` (+ `manifest_drop2.json`).

| Shot | Time | Content | Clip |
|---|---|---|---|
| E1 + E2a | 112.96–114.905 | **v2, restored (rev 5b).** Residue bloom on the L tracks, the sprint, the superman dive and roll, the column kick; ghosts 1–3 with the counter. | v2 `trk_sprint`, `trk_dash`, `trk_walljump` |
| E2 4–8 | 114.905–116.95 | Hard cut to the v3 level; one cut per chop, each attempt ending on its chop and popping a line-art ghost over the next: off the platform mid-leap, short of the far wall, lawn zig, zag past the notice board, wall-kick at the hotel corner. ◀◀ scrub, flash, punch, `GHOSTS n`. Hues continue from v2's ghosts 1–3. | `leap` (in 0, ×1.6), `chasm_short`, `lawn`, `lawn2`, `kick` |
| E2 9–13 | 116.95–119.44 | One held shot of the side wall (plate ×1.4 from the top edge). Five attempts; ghosts at the awning, the ledge, the stairs, the top landing and just short of the cornice: a ladder of five Jades, 27–38% of frame height. Ghosts 11 and 12 step aside 0.3 s after freezing. | `climb` |
| E3 | 119.44–122.95 | rev-A's watercolor singer (`media/sing/E3/v3_sync_1080.mp4`, in 0, rate 1), push 1.0→1.08 on her head (960, 380). Orbit re-fitted: centre (960, 600), 780×400, −8°; occluder = the take matted by her per-frame matte, so ribbons always pass behind her. "Rewind." lower third as v2. | rev-A |
| E4a | 122.95–124.38 | **Up her own ghost ladder (rev 5b).** Same ×1.4 wall framing as E2 9–13; the five climb ghosts sit at their frozen poses as rungs and each brightens as she passes through it; she reaches the cornice in ghost 13's pose on the cut. "Rewind." painted large on the brickwork (IM Fell, residue orange, multiply) from 123.0. | `climb` (in 3.45, ×1.75) |
| E4b | 124.38–126.25 | A gold ghost lying on the roof hauls her up by the wrist; she is over the ledge before the cut. | `haul_b` (in 0.05, ×1.3) |
| E5 | 126.25–128.76 | **The hint while sliding (rev 5b).** Hand in hand down the giant book (Escher, *Still Life and Street*); the leading gold ghost points at the upright book at frame right and **both girls turn to look at it** (Jade's note); its spine label reads `BANACH–` / `TARSKI` (pinned on 1523–1687 × 222–345; locked camera, tracked, no drift). The engrave's black blots on the white cover are covered by the cover cut from the nano clean plate (`patch_slideptb_cover.png`). | `slide_point_b` (in 0.9, ×1.37) |
| E6a | 128.76–131.38 | **Swarm boost (rev 5b).** Agents rush in from both sides; the kneeling blue ghost heaves her straight up (foot leaves the hands on the 130.04 beat); the agents crash into each other beneath her on 130.94 (punch + shake); she hangs at the peak. The ghost is baked opaque (`ghostfill.py`: line art over a pale fill inside her matte) because the agents pile through her and a static clean plate would erase them. | `swarm_boost` (in 0.315, ×1.14) |
| E6b | 131.38–131.82 | Freeze + flash; she bursts into 150 motes in mid-air over the frozen heap (nano plate without the girls + the ghost still). | `swarm_boost` frame 79 |
| E6c | 131.82–134.00 | Two mote clouds implode into two crouched Jades over the heap; on the bar line 132.26 they sprint apart with an orange and a blue ribbon. The take's rainbow streaks: reds remapped, the rest hidden under the clean heap plate. | `two` |
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

## Revision 3: E3 placed in this timeline

- **Take:** `media/sing/E3/take_3_lips.mp4` (720p). It is not engraved: the pencil look is approved as made. The engine upscales it to 1080p with Lanczos when it extracts frames.
- **Lip sync:** `clip_time = song_time − 119.14 + lag`. The lag is set by **`E3_VARIANT`** at the top of `tools/sections/D/build_timeline.py`. The values come from `media/sing/review/E3_take_3_lips_ABC.json`, so they match the A/B/C composites Jade listens to:

  | Variant | Lag | Clip in at 119.44 | Lips |
  |---|---|---|---|
  | A | 0.90 | 1.20 | 0.15 s earlier |
  | **B** (default) | 0.75 | 1.05 | as measured |
  | C | 0.60 | 0.90 | 0.15 s later |

  To switch: change the constant, rerun the build script, re-render.
- **Ribbons:** seven orange/pale-blue coloured-pencil ribbons spiral in from beyond the frame edges and settle onto a tilted orbit around her head and shoulders. The orbit is centred (900, 470), radii 570 × 335, −10°, so it clears her head.
  Where an orbit crosses her body it passes behind her. An occluder layer redraws the same take through her first-frame silhouette (`media/sing/first/her_mask_first_frame.png`, eroded, with a stray plaza blob removed; it becomes `media/shots/E3/occluder_mask.mp4`). Her face is never touched.
- **Look:** a light pencil grain (0.045, size 1.2, on twos) plus paper 0.18, so her glasses stay intact.
- **Lyric:** "Rewind." in IM Fell, orange #F08A24, in the lower third, timed to the word.
- **Risk:** the takes keep the first frame's head pose, but if she drifted, the static occluder would let a ribbon edge show over her hair rim. I didn't see this in 119.5–122.9.

## Revision 4: rough-cut v1 review fixes (`docs/reviews/roughcut_v1.md`, top-10 items 3, 4, 8 and 9)

1. **Ghosts read as Jades (113.89–119.44, 127.88–129.62).**
   - **New ghost look:** `ghostsprite.py` now bakes a translucent line-art Jade in the F6c/F8 manner. Her own drawing is turned into a duotone: crisp hue-ink line work, eyes, mouth and hair at full alpha, a pale hue fill at about 0.55, a bright near-white rim in the hue and a soft hue glow.
   - **E2c sizing:** every constellation ghost is now **290 px tall (27% of frame height)**. Horizontal poses are limited by their width.
   - **E2c layout:** each ghost has its own slot around the agents.
     - Ghosts 1–8 already stand there; 8 pops on its chop.
     - Ghosts 9–12 freeze exactly where she is on their chop, then grow and glide to their slot in 0.35 s.
     - Ghost 13 stays where it froze.
   - **E2c push-in:** now 1.00 → 1.08, so every slot stays in frame.
   - **E5b gold twin:** the opaque twin is now a ghost.
     - A nano clean plate removes her from the left half (`media/shots/E5/plate_e5b_left.png`, feathered before the warp's black wedge, which caused the earlier seam).
     - She is redrawn per frame as a gold line-art ghost at 0.85 × ~0.6 fill with a glow outline (`tools/sections/D/ghostseq.py` → `media/shots/E5/ghost_twin_gold_{rgb,alpha}.mp4`).
     - Live Jade on the right is matted by `take_e5_hand_1_right/`.
2. **Anagram stall (126.25–130.50).** The total timing is unchanged (126.25 → 130.50).
   - **E5a** keeps 126.25–127.88. Its blank right half is filled with a nano-painted Loop street canyon with an L trestle (`plate_e5a_fill.png`, masked to the blank region). The duplicate girl that nano drew there was removed with a second edit.
   - **E5b** hand-off now runs **127.88–129.62 (1.74 s)**; the slip is visible in the twin's hand.
   - **E5c** is **0.88 s (two beats, 129.62–130.50)**, and the question is already written when it appears.
3. **E3 lyric.** "Rewind." is now ink on a paper halo, size 112, y 1000, below the jacket band, with the period. The ribbon orbit was retuned for the singing director's 1.3× push-in (centre (949, 571), radii 740 × 435). The occluder mask builder now applies the same crop remap as `tools/sing/polish.py remap-mask`. Their remapped cached mask is used as is.
4. **NYC landmarks.**
   - **E5b:** the Empire State Building behind her is replaced by a flat-crowned Chicago tower (nano edit, patched).
   - **E6a/E6b:** the ESB and Chrysler in the rooftop skylines are replaced by Chicago towers, including a Willis-like one. The fix is a nano edit of an engraved frame, patched where it differs.
5. **E7 ribbons** are capped at 10, one more per beat, thinner and with more pencil grain, so the meter close-ups stay readable.

**Still open after revision 4:**
- E6b's camera drifts slightly, so a small spire near the centre skyline is still visible late in the shot (about 133+).
- The Grant Park field plate (E2b and the E7 reuse) also has a spire resembling the ESB in its distant skyline.
- E4's stream still uses engine-tinted ghosts, not line-art.
- E8 redaction is left as it is, per the coordinator.

Cost of revision 4: 9 nano-banana-pro edits, about $1.21.

## Revision 5 (v3 pass): the restaged chase

Jade's v2 notes (`docs/revisions/B.md`, plan in `docs/revisions/B_research.md`). Drop 2 now replays the rev-B level
(platform → beam → chasm → lawn → hotel → wall → the tabletop street of books), always left to right or up, never at an
agent. Every shot from E1 to E7 uses the new `media/shots/B_<take>/take_1*` clips; the v2 tables above and below are
history. Review clips: `media/reviews/v3/B/` (+ `manifest_drop2.json`).

| Shot | Time | Content | Clip |
|---|---|---|---|
| E1 | 112.96–113.89 | v2 residue bloom + mote burst; she bursts off along the platform. Chop 1 freezes her mid-sprint. | `plat` |
| E2 1–8 | 113.89–116.95 | One hard cut per chop, each attempt ending on its chop and popping a line-art ghost that hangs over the next attempt: mid-leap, on the beam, short of the far wall, flat dive, lawn zig, zag past the notice board, wall-kick. ◀◀ scrub, flash, punch, `GHOSTS n`. | `leap` ×2, `chasm_short`, `chasm_dash`, `lawn`, `lawn2`, `kick` |
| E2 9–13 | 116.95–119.44 | One held shot of the side wall (plate ×1.4 from the top edge). Five attempts; ghosts at the awning, the ledge, the stairs, the top landing and just short of the cornice: a ladder of five Jades, 27–38% of frame height. Ghosts 11 and 12 step aside 0.3 s after freezing. | `climb` |
| E3 | 119.44–122.95 | rev-A's watercolor singer (`media/sing/E3/v3_sync_1080.mp4`, in 0, rate 1), push 1.0→1.08 on her head (960, 380). Orbit re-fitted: centre (960, 600), 780×400, −8°; occluder = the take matted by her per-frame matte, so ribbons always pass behind her. "Rewind." lower third as v2. | rev-A |
| E4a | 122.95–124.38 | The boost: a blue ghost (an earlier iteration) kneels and launches her (launch on 123.50, cornice catch on the cut). "Rewind." pinned on the limestone wall, IM Fell, residue orange. | `boost` (in 1.04, ×1.3) |
| E4b | 124.38–126.25 | A gold ghost lying on the roof hauls her up by the wrist; she is over the ledge before the cut. | `haul_b` (retake; in 0.05, ×1.3) |
| E5a | 126.25–128.76 | She and the gold ghost (leading, lower) slide hand in hand down a giant book in Escher's *Still Life and Street*. | `slide` (in 0, ×1.1) |
| E5b | 128.76–130.50 | The gold ghost points at two identical spines; both labels read `BANACH–` / `TARSKI` (pinned, IM Fell ink capitals); she realises and smirks. | `spine` (in 1.9) |
| E6a | 130.50–131.38 | Dodge roll; the agents collide on 130.94 (punch); jump cut on that beat to her spring from bare ground, airborne at 131.38. | `roll_b` (retake) |
| E6b | 131.38–131.82 | Freeze + flash; she bursts into 150 motes over a clean frozen plate. | `roll_b` frame 92 |
| E6c | 131.82–134.00 | Two mote clouds implode into two crouched Jades over the heap; on the bar line 132.26 they sprint apart with an orange and a blue ribbon. The take's rainbow streaks: reds remapped, the rest hidden under the clean heap plate. | `two` |
| E7 | 134.00–139.00 | `plat` and `leap` with the doubling (2, 4, 8, 16 on 134.00/134.44/134.88/135.32, continuing across the cut), the v2 meter insert; **chasm (rev 5b): the Super Meat Boy replay**: fifteen copies leave the beam stacked on her and fan into separate arcs; six fall short (lose ground, sag below the lip, freeze and drop out of frame, fading), four clip the far wall and end in a small mote burst in their own hue, five survive (orange, blue, magenta, green, violet) with the untinted Jade; `ear`; `lawn` with only the five survivors running away, in two interleaved rows. **HILBERT** on the hotel billboard in the chasm, `ear` and `lawn` (rev-A's `tools/sectionA/modules/woodcut.js`: Anton capitals, ink, `hatch` .15, `flecks` 0, box 420×140, pad 8 (identical to the Verse 2 sign), corner-pinned with the Verse 2 corners, `at: -1` so it is solid from the first frame; the chasm's hatched panel is painted lit first with `_B_quad.js`). v2 wash, capped ribbons, white flash on 139.00. | `plat`, `leap`, v2 meter, `chasm_dash`, `ear`, `lawn` |
| E8 | 139.00–141.00 | Unchanged. | v2 |

Rev 5b (Jade's notes on the v3 cut, `media/reviews/v3/B/manifest_drop2.json`): keep v2's opening and cut to the v3
retries; compress the hint (point while sliding, boost, swarm, double and split); thin the rainbow Jades the Super Meat
Boy way (most copies don't make it the chasm) and letter HILBERT on the hotel billboard. Dropped: `boost`, `slide`, `spine`,
`roll`, `roll_b`, and the retries on the beam and the flat dive.

**Ghost colour fix (rev 5b, Jade: the ghosts "slightly come out of their color").** Slide: `splitpair.py` splits the
colour-gated matte by tracking both bodies from a hand-drawn seed polygon (cut at the held hands; every matte pixel goes
to exactly one girl), `pairfinish.py` closes and hole-fills the live girl (engrave blots were notches the clean cover
showed through). Swarm: `swarmsplit.py` tracks the flier as her own component from the frame where she separates
(1.92) backward and forward; a hand-drawn foot polygon keeps her sneaker hers while it sits in the cupped hands; once
the agents reach the kneeling girl she keeps her own still pose (legs from 1.67, arms from 1.92) plus her raised hands.
Sweep (every frame 124.38–131.38 at 960×540, 168 frames, `--force` render): 0 px of her real orange/navy inside any
ghost; no ghost hue inside a live girl except the flier's own pale-blue badge. Note: render.mjs reuses rendered frames
unless the timeline/engine changed, so after re-baking mattes always render with `--force`.

**Ghost twins** (E4b, E5, E6a), as v2's E5b gold twin but per frame:
`split2.py` splits the shared engrave matte into the two girls (seed boxes + a marker watershed on the frame, tracked
frame to frame; `--kmeans` for the slide, where they hold hands throughout; `swarm_boost` = tracked before the launch,
k-means after, on the colour-gated `jmatte` so the agents stay out) → `take_1_ghost/` and `take_1_live/`;
`patch.py` lays a nano clean plate (`media/shots/B_plate_*/kf_v1.jpg`) only where the ghost girl ever is;
`ghostseq.py` bakes her as a moving line-art ghost (`media/shots/_D/v3/ghost_*_{rgb,alpha}.mp4`). The live girl is drawn
on top from her own matte. The lawn copies use a colour-gated matte (`jmatte.py`) because the engrave matte also holds
the agents. `HUE[5]` vermilion became amber `#E9A23B` (no red).

**Changed from the brief:** the atomize burst plays one beat on the frozen frame (131.38–131.82) before the implode,
so `two` runs 131.82–134.00; the boost→haul cut stays at 124.38; the haul is a retake because in take 1 the hauled
girl crawls over the lying one and the two cannot be separated.

**Cost:** 2 Seedance retakes (`roll_b`, `haul_b`) ≈ $1.50, 5 nano clean plates ≈ $0.67; rev 5b: 2 nano clean plates
(`plate_slidept`, `plate_swarm`) ≈ $0.27 (the `slide_point` and `swarm_boost` takes were ordered by the coordinator).

**Weak:** the first 0.3 s of the E7 chasm (before the copies peel off) is still a dense stream of colour, and the survivors are
still in the air above the far lip on the cut; the
level ghosts in E2 1–8 sit over a different place for 0.4 s (the next attempt), so they read as afterimages, not
positions; the haul plate's roof is slightly lighter inside the patch; in E6a the agents pile onto the blue ghost
(she stands among them, opaque and pale) rather than meeting in empty space, and the agents' arms that cross her are
drawn blue with her; a faint gold strip follows the slide's white trail along the book edge beside the gold ghost.

## Ghost choreography (the 13 chops)

The chop times come from `timing.json → lyrics.vocal_chops`. Ghost k is revealed on chop k (ghosts layer `on: [t]`, with a 0.12 s pop).
Each chop also gets a pale-blue flash (0.08 s, 0.35), a VHS-rewind blip (0.12 s) and a 3.5 % zoom punch.
Ghosts are the matted frame at `freeze` (source seconds) of the clip, baked as line-art sprites (see revision 4). The E2c slots below are superseded by `SLOTS_OLD`/`SLOTS_NEW` in `build_timeline.py` (revision 4).
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
