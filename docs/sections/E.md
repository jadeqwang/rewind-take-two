# Section E: glitch break + verse 3 (141.00–169.40), plus O1 and F6's 3D element

Director: section E agent (3D / technical art). Timeline: `render/timeline/E.js`. 3D modules: `render/three/` (README there).
Status: **complete: every shot 141.00–169.40 plus O1 is in `render/timeline/E.js` and renders in the engine.**
Preview with audio: `node render/engine/render.mjs --timeline render/timeline/E.js --range 141 169.4 --preview --encode`.

## The idea

The glitch break is the turn. The engraving comes loose from the world and drifts round her like iron filings (G1). On the
low boom she pulls the pencil out of her hair (G2). One stroke of colour (G3) and, on the kick, the world snaps to
orthographic and clunks into the magic angle: the Loop rebuilds itself as a Monument Valley diorama, piece by piece,
on the music box (G4). From then on she plays it like a puzzle. She turns cranks, re-routes roads and sends the agency
round the Penrose stairs (M1–M3). Colour (her residue) blooms round her wherever she redraws something.

## Cut list (every cut and move on the tracked grid, `analysis/cinematic/timing.json`)

| Shot | In–out | Bars | One idea | Source |
|---|---|---|---|---|
| G1 | 141.00–144.54 | 81:1–83:1 | weightless on a blank page; the engraving lines drift round her like iron filings | GEN clip (matted) over `canvas/drift_lines.js` |
| G2 | 144.54–146.32 | 83:1–84:1 | **boom 144.54**: pencil out, hair falls (hero) | GEN clip; the boom also throws the filings outward |
| G3 | 146.32–148.08 | 84:1–85:1 | one stroke of colour; the loose lines near it bloom to coloured pencil (146.62→) | GEN clip + drift lines with bloom |
| G4 | 148.08–151.62 | 85:1–87:1 | **kick 148.08**: perspective snaps to ortho and clunks 90° into the magic angle (lands 85:2 + 0.12 s); the Loop assembles: B 85:2, C 85:3, stair steps one per 16th from 85:4, track A 85:4, turntable/spur 86:1, exit 86:2, **leg D lands last on 86:4 (151.18)**, which closes the impossible circuit | 3D `e_loop.js` shot G4 |
| M1 | 151.62–153.98 | 87:1– | continuous from G4: push in from the whole diorama to Jade (hair down, pencil) walking the L track; agents enter down leg D and up the stairs | 3D `e_loop.js` shot M1 |
| V3S | 153.98–159.14 | 88:2.3–91:2 | singing #3 (`media/sing/V3S/take_2_lips.mp4`, not engraved), V3-1 lower third (IM Fell, paper with an ink halo). The lip lag is a one-line switch: `V3S_VARIANT = 'A'|'B'|'C'` (B = −0.12 s; A/C = ±0.15 s). **Cutaway 157.39–157.84 (90:2–90:3)** to agents climbing the stairs (diorama in close-up) covers the take's brief brow crease; the lyric continues over it | singing take + 3D `penrose_loop` close-up |
| M2 | 159.14–165.18 | 91:2– | **Möbius Lake Shore Drive**: a 3-half-twist Möbius road over the engraved lake; the agency's sedans drive both faces (upside down on the 2nd lap). The join swings open toward Jade and the lead car heads for the exit. In the instrumental hole (161.63–162.27) she turns the crank, and it **clunks shut on the 162.30 chord stab**, carrying the car back into the loop forever. The lyric "I'm speeding down Lake Shore, I dreamt" is painted on the road, word by word on its onset, following the twist | 3D `e_mobius.js` |
| M3 | 165.18–169.40 | –97:1 | "a shadow chasing me — it couldn't **trace**": three agents run up her spur onto the swing bridge; she turns the stoop crank on **95:2 (166.30)**, the bridge clunks round on 95:4 (167.16) carrying them into the Penrose circuit, and they march *Ascending and Descending*. Pull back on the riser (168.6→169.4). "trace" is drawn by a dotted line that loses the path and wanders off frame | 3D `e_loop.js` shot M3 + `canvas/trace_lyric.js` |
| O1 | 211.64–218.92 | 121:1–125:1 | Ascending and Descending forever; slow pull-back from agents climbing flight B to the whole circuit; the world in colour (post-drop), agents in ink. Variance report overlay: engine | 3D `penrose_loop.js` `{pull:[7.5,25], color:1}` |
| (F6) | 190.58–195.86 | 109–112 | offered to Section F: the melting clock's hands become the Penrose staircase. Off-angle, the hour hand floats 6 units above the face; the camera orbits with her gesture and clunks into the magic angle on 194.10, where the hands and flights close into the loop; agents drip off the melting lip and march it | 3D `f6_clock.js` (not placed in E.js; F's timeline can add `{type:'three', module:'render/three/scenes/f6_clock.js', linear:false}`) |

Engine fx in E.js: a camera shake on 148.08 (kick), 162.30 (the Möbius clunk) and 167.16 (the bridge clunk). Typography:
M2's lyric is in-world (painted on the road surface, inside the module). M3 uses `canvas/trace_lyric.js` (IM Fell, ink, lower
third, the engine's 2-frame ink bleed, paper halo).

## How Jade gets into the 3D shots

Matted anime sprite clips render **inside** the engraver's G-buffer (`lib/sprite.js`, `Engraver.spriteMaterial`). Each clip
is a vertical, camera-facing quad with an alpha-tested atlas, so the set occludes her and she gets the ink outline and
the engraver's paper halo but no hatching (she stays full colour). Clips: walk ¾-front, walk ¾-back (flipped for the
other diagonals) and crank, loaded from `media/shots/E_sprites/<clip>/` (`rgba/f_####.png` + `info.json`). If they are
missing, a low-poly Jade (hair down, pencil in hand) stands in. The tighter cameras put her at about 175–210 px tall in M1/M3
(M2 ~140–170 px, so the whole Möbius loop and the road lyric stay legible).
Residue: a coloured-pencil bloom follows her (M1–M3), and grows when she cranks.

## Generated shots (G1–G3, sprites)

Made by a generation sub-agent (Seedance 2.0 720p from nano-banana-pro keyframes with the canon refs). Details are in
`media/shots/G*/NOTES.md` and `media/shots/E_sprites/NOTES.md`.

| Shot | Chosen | Clip in / rate | Notes |
|---|---|---|---|
| G1 | take 1 (`take_1_engraved.mp4` + matte) | 0.00 / 1.0 | slow push-in, she studies her hand; the bun pencil glints in the last second |
| G2 | **take 4** of 4 (`G2_takes_sheet.jpg`: 4 > 1 > 2; take 3 rejected for a garbled sleeve patch) | 0.46 / 1.15 | the boom lands mid-yank; the pencil clears the bun at ~144.64; the hair falls and fans out until the cut |
| G3 | take 4 (`take_4_engraved_soft.mp4`, dilated matte) | 1.20 / 1.4 | one C-shaped crayon stroke, orange outside, sky blue inside; the loose engraving lines near it bloom into coloured pencil (drift_lines `bloomAt 146.85`) |

- The clips are engraved with a blank-page preset (`--fallback-weight 0 --gamma 1.8 --contrast 0.45`): the default
  engrave pass filled the empty page with wood grain.
- The engine composites each clip's matte over `paper + drift_lines`. The boom throws the filings outward, and they
  drift back for G3.
- Sprites (`media/shots/E_sprites/{walk_front,walk_back,crank}`): RGBA, stabilised walk-in-place loops with feet
  baselines, used by `lib/sprite.js` in M1–M3. Jade is ~240 px tall in M3 and ~200 px at the end of M1.

## What's weak / next

- G4's first ~0.3 s (perspective) hatches heavily, because the line pitch maths assumes an orthographic camera. It reads
  as a dark engraving and is gone by the clunk.
- Sedans are simple blocks at this scale. The Möbius twist bunches on the left by design (it leaves a flat back
  stretch for the lyric).
- M2's "I'm" sits close to the twist peak. All the words read from 162.3 s on.
- The sprites were shot at a ~25° high angle, not the true 35° isometric one, so her feet sit a touch flat on the
  deck. The ¾-back walk is unused (no shot needs it yet). The crank mime is modest.
- G2 take 4: her raised hand brushes the top frame edge (~144.6–145.2), and the matte has a small hole in the hair at
  ~145.3. Alternate: take 1, in 0.55.
- The tiny "1420 MHz" roundel is garbled in G1 and in the sprites at 720p.
- `render/timeline.js` (the merged film) currently fails to load because of another section's in-progress file
  (`_A_tracks.js` import). Section E renders fine with `--timeline render/timeline/E.js`.
- The perspective "snap" of G4 is a projection-matrix blend, not a true dolly zoom. It is fast enough to read as a
  snap.

## Cost

- **Generation:** $13.61 (16 nano-banana-pro keyframes $2.15, 15 Seedance 2.0 720p clips $11.25; tags `E_*`). Budget
  $25.
- **3D:** $0.
