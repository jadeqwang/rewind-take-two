# REWIND — shot list v1 (locked to the cinematic edition)

Times are in seconds. Bar numbers come from `analysis/cinematic/timing.json`, where bar 1 = 0.10 s and 1 bar ≈ 1.77 s.
Cut on the tracked beat or bar times in that file, never on a computed 136-BPM grid. Picture is 1920×1080 at 24 fps.
Read `docs/treatment.md` first.

**Method key:**

| Key | Meaning |
|---|---|
| GEN | Engraved keyframe (nano-banana-pro, or seedream-5-pro for night/dusk) with color Jade from the canon turnaround → Seedance 2.0 (720p, first-frame-locked, "extremely fast" when needed) → `tools/engrave` pass |
| STILL | One generated image animated in the engine (push-in, parallax, particles) for time-frozen moments only. Every living thing must still move a little: hair, cloth or residue. |
| ENG | Pure engine work: HUD, typography, procedural effects |
| REUSE | Earlier footage replayed reversed or scrubbed by the engine |
| 3D | Three.js module from `render/three/` |
| SING | Pencil singing Jade, made with the Orbital Sunrise method |

## Global design system

### Palette

- **World:** engraved black ink on warm off-white paper. Nothing else is in color.
- **Jade:** full anime color. Her white jacket's orange band (#F08A24) and pale-blue dot (#8DB8E8) are **the residue colors**.
- **Residue ribbons:** gradient orange → pale blue, with additive glow and a colored-pencil grain texture.
  Each ghost iteration gets a hue shift along a Kandinsky spectrum (orange, blue, gold, magenta, green).
- **Agents and their UI:** pure black and white. Alarms invert the frame (white ink on black) rather than adding red.
- **Final drop:** the world floods with colored pencil. Use Klimt gold leaf (#C9A227 plus foil texture) as the "canon" color.

### Typography (OFL fonts vendored in `render/fonts/`)

| Use | Font | Treatment |
|---|---|---|
| Sung lyrics (default) | **IM Fell English** (engraved period serif) | Ink-black on paper, or Jade-orange when the lyric *is* residue. Words appear exactly on their timing, with a 2-frame ink-bleed reveal. |
| In-world lyrics (signs, mirror etching, ID card, sunglasses) | Highway-sign gothic (**Overpass**) for road signs; IM Fell for etchings | Corner-pinned into the plate and moving with it |
| Game HUD | **Press Start 2P**, small, top corners only | At most one HUD cluster on screen. Counters: `ITERATION 4,097`, death skull `×4096`, speedrun timer. |
| Agency terminal | **IBM Plex Mono** | Every reference reads `TIME VARIANCE █████████`. The redaction bar is a solid black block. |
| Whispers ("shot", "never stop") | IM Fell *italic*, lowercase, small, graphite gray, tracked out | |

### Rules

- One idea per frame.
- Jade is large in frame unless the shot is a deliberate wide.
- No head shots. The hit is to the body and reads as a burst of colored motes, never blood.
- Never write "Authority", "TVA" or Marvel terms.
- Singing Jade appears three times, all at the Bean: S1, D2-SING and V3-SING.

---

## 0. Cold open + intro (0.00–12.60, bars 1–7)

The track is quiet here: plucked arpeggio plus an 8th-note clock tick. Picture carries the hook.

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| C1 | 0.00–1.90 | **First frame = the most arresting image in the film.** Frozen moment: Jade mid-wall-jump between two engraved Loop buildings. A bullet hangs in the air an arm's length from her ribs, trailing an engraved wake. Five agents below aim upward. Orange/blue residue motes hang in the air. Slow push-in; her hair strands and the motes drift slightly. | HUD top-left fades in at 0.4: `ITERATION 4,096` | STILL |
| C2 | 1.90–7.24 | **Rewind teaser.** The C1 frame starts going backward. A ◀◀ glyph appears and the speed accelerates on every clock tick (8ths ≈ 0.22 s). We fly backward through 2–4-frame flashes of *later* shots in reverse: the Bean, the color flood, the Penrose stairs, the Möbius Lake Shore Drive, the pause menu, the ghost swarm. Residue ribbons whip backward through the frame. Each flash is held exactly to a tick; the last flashes are only 2 frames. The iteration counter rolls 4,096 → 4,097. | `◀◀ ×2 ×4 ×8 ×16` | REUSE (assembled late, from final shots) |
| C3 | 7.24–10.82 | Bar-5 sub swell: **land.** Hard stop on a wide of the engraved Chicago skyline at night from over the lake, with Lake Shore Drive's curve of streetlights. One white car, tiny, moving south. | Title **REWIND** in IM Fell, centered, ink-bleeds in on 7.24, then the letters reverse into place (D N I W E R → R E W I N D) over 1 s. Small line under it: *jade wang*. | GEN |
| C4 | 10.82–12.60 | Bar-7 chord change: inside the car, side profile. Anime Jade driving, bun with pencil, orange headphones round her neck, dashboard glow (white). On the passenger seat, a thick bound dissertation with a sticky note. | Sticky note, handwritten: `DEFENSE 9AM` | GEN |

## 1. Verse 1 (12.60–37.96, bars 8–22): "the cutscene"

Lyrics live **in the world** wherever possible. Cuts land on bars.

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| S1 | 12.60–19.64 | **SINGING #1.** Pencil singing Jade (real likeness, glasses) at the Bean at night, chest-up, slightly right of center. The Bean's mirror behind her reflects the engraved city like Escher's *Hand with Reflecting Sphere*, sensible geometry. A tiny pair of headlights moves along Lake Shore Drive in the reflection. Hidden in the far reflection: a staircase on a rooftop that loops (nobody will notice yet). | V1-1 "The night before my dissertation defense," in IM Fell, lower third, word-timed | SING |
| S2 | 19.64–21.38 | Transition: push into the Bean's reflection, keeping the distortion, onto the car on Lake Shore Drive. The reflection becomes the world. | (V1-2 begins 20.12) | ENG over S1 + GEN plate |
| D1 | 21.38–23.16 | Lake Shore Drive, chase-cam behind the white Acura at speed. An overhead green highway sign gantry approaches and passes overhead. | Sign reads **LAKE SHORE DR** with the lyric as the sign's second line: "I'm speeding down Lake Shore". Corner-pinned. "I dreamt" floats under the gantry as it passes. | GEN + ENG sign |
| D2 | 23.16–24.90 | Side window, the city sliding by. A rooftop hotel sign passes: **HILBERT** / `VACANCY` (easter egg, never featured). | | GEN |
| D3 | 24.90–28.40 | Rearview mirror close-up, Jade's eyes glancing (anime, color). In the mirror: a dark shape with no lights following. | Etched along the mirror's bottom edge in the style of "OBJECTS IN MIRROR…": **"a shadow chasing me I couldn't place"**, word-timed | GEN + ENG etch |
| D4 | 28.40–30.16 | "I pulled over": exterior, the car rolls onto the shoulder. The headlights of a black sedan behind flare white across the frame. | | GEN |
| D5 | 30.16–31.92 | Agents step out: three silhouettes in shades and suits, backlit, symmetrical. | "men in shades and suits" mirrored in the lenses of the center agent's sunglasses (small, reflected) | GEN + ENG |
| D6 | 31.92–33.66 | Low angle past Jade's shoulder: the agents at her window. One holds up a stopwatch/Geiger "residue meter" that starts clicking. | | GEN |
| D7 | 33.66–36.30 | Close on her hands pulling the ID from her jacket. **The ID card is in color** (it's hers): `DOCTORAL CANDIDATE — JADE WANG`, with an anime photo. | V1-5 "I reach for my ID to show them …" as an RPG dialogue box, typewriter, bottom of frame. This is the only dialogue box in the film, the cutscene's signature. | GEN + ENG card graphics |
| D8 | 36.30–37.96 | "and I do": the agent takes the ID. The residue meter's needle slams to max, because the ID shimmers with color residue. The agent's head tilts. | "… and I do," completes in the box | GEN |

## 2. Pre-drop → shot → time stops (37.96–42.38)

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| P1 | 37.96–38.90 | Agent's hand moves to his jacket. | "With no warning" (box gone; IM Fell lower third) | GEN |
| P2 | 38.90–39.68 | Jade's eyes widen (color). Percussion swell. | "I get" | GEN |
| P3 | 39.68–40.24 | The pistol rises, aimed low at body level. Shallow focus. | | GEN |
| P4 | 40.24–40.65 | **Whispered "shot":** muzzle flash as an engraved starburst. Hard cut to Jade's torso (jacket, orange band) as the hit becomes a burst of orange/blue motes, as in a Celeste death. | *shot* (whisper style, tiny) | GEN + ENG motes |
| P5 | 40.65–41.40 | **Tape stop: freeze.** The motes hang in the air. The whole world inverts to the woodblock negative (white lines on black) over 0.3 s with a tape-slowdown wobble. Jade stays in color. | | ENG over P4 last frame |
| P6 | 41.40–42.38 | **Pause menu** over the frozen inverted frame: `PAUSED` / `▶ RESUME` / `◀◀ REWIND` / `QUIT`. The cursor moves RESUME → REWIND on "and time" and the selection blinks on "st-" (42.06). | menu (Press Start 2P) | ENG |

## 3. Drop 1 (42.38–56.54, bars 25–32): Braid rewind, half-time underwater

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| R1 | 42.38–42.65 | Impact: white flash, then the inverted frame shatters back to positive. | | ENG |
| R2 | 42.65–48.42 | **Thirteen "stop" chops = thirteen past deaths.** On each chop, hard-cut to a different frozen death tableau from earlier iterations: Kaizo-trap deaths around Chicago. Hit by an L train, falling past Marina City's corncobs, pinned under the Picasso, a bascule bridge rising under her, the Buckingham Fountain, a dropped water tower, swarmed by agents on the Riverwalk, and so on. In each she's mid-burst into motes. The counter jumps backward every hit (`ITERATION 4,084 … 4,096`, randomized but decreasing). VHS scrub lines between hits. | counter only | STILL ×13 |
| R3 | 48.42–52.48 | "Rewind." #1: **the Braid rewind.** All of Verse 1 plays backward at speed (D8 → D1) under an underwater caustic ripple and half-time judder. Jade's residue ribbon unspools backward through the frames. A clock-ring HUD sweeps counter-clockwise. | **REWIND** in IM Fell, huge, the letters arriving in reverse order (D first), mirrored, then flipping right-reading | REUSE + ENG |
| R4 | 52.48–56.54 | "Rewind." #2: continue the rewind, past the singing shot (S1 in reverse) and the title, and the rewind decelerates onto the road. The last bar slows to a stop on Lake Shore Drive with the ripple calming. | second **REWIND**, smaller, already right-reading | REUSE + ENG |

## 4. Verse 2 (56.54–108.67, bars 33–62): the precision platformer

Dark trap. Side-scroll grammar. The HUD cluster lives top-right in this section only: `ITERATION 4,097`, skull `×4096`, speedrun timer.
Cuts every 1–2 beats in action, with a hero moment on each wordless "oh" swell.

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| V2a | 56.54–63.62 | **Car chase, side-scroll.** Hard cut on bar 33. Side-on tracking of the white Acura on Lake Shore Drive, the lake behind. A pack of black agent sedans behind, their siren strobes as white engraved starbursts. Intercut every bar: tire close-up, her hands on the wheel, sedans multiplying. | HUD appears with a 4-frame pop | GEN ×4 |
| V2b | 63.62–72.48 | **Kaizo road.** The dream road misbehaves: lanes tilt like platforms, a sedan flips over the car (near miss), a lamppost falls (dodge), the car threads between two closing trucks. Cut every 2 beats. | | GEN ×5 |
| V2c | 72.48–83.10 | **The bridge.** A Chicago River bascule bridge ahead starts to rise; a bell rings. Three "oh" swells = three beats of anticipation: (73.34) the bridge leaves rising; (76.93) the speedometer needle pins; (80.46) the agents' sedans fan out behind. | | GEN ×4 |
| V2d | 83.10–84.86 | **The jump** (Blues Brothers homage). The car launches off the rising bridge leaf at 83.5. Through the full-band hole (84.04–84.74) it hangs in slow motion mid-air over the river. Jade grins (color). | "And now I'm" | GEN |
| V2e | 84.86–88.38 | **"back" lands on the bar-49 downbeat:** SLAM onto the far side, sparks, on the road again. | "back on the road" (IM Fell, kinetic, slams with the landing) | GEN |
| V2f | 88.38–92.79 | Rearview mirror callback (same composition as D3). Now it shows a river of agent sedans with white strobes. | Mirror etching: **"sirens in my mirror …"** | GEN + ENG |
| V2g | 92.79–93.07 | **Kaizo trap.** An elevated L train crashes down onto the road in front of her out of nowhere. SMASH, cut to black. | | GEN (2–3 frames) |
| V2h | 93.07–94.06 | **"Reload."** A LOADING screen: black, a spinning pencil glyph, a tip line: `TIP: The Time Variance █████████ can only follow what it can trace.` Death counter `×4097`. Instant respawn: snap to her on foot at a checkpoint flag. | **Reload.** large, centered, Press Start 2P | ENG |
| V2i | 94.06–98.28 | **The race.** Side-scroll sprint on foot along the L tracks over the Loop. Running parallel with her: a translucent graphite **ghost runner**, her own previous attempt (speedrun ghost). Race HUD: `GHOST: ITERATION 4,096` with a split time going red→green as she pulls ahead. | "A shadow chasing me like it's a race" | GEN ×2 + ENG ghost (reuse her clip, tinted gray, offset) |
| V2j | 98.28–103.74 | **The field.** Hard cut to **top-down** over Grant Park's lawn (engraved grass strokes). She zigzags hard between converging agents. Her residue trail draws a bright zigzag on the grass. | "I zigzag across the field of grass", laid into the grass plane with perspective | GEN (top-down) + ENG trail |
| V2k | 104.17–108.67 | **"too fast."** The agents move by **frame-skipping**: they don't run, they jump positions every beat like dropped frames, always closer. Ground-level shot over her shoulder; she looks back. | "they chase me and they're just too fast" | GEN + ENG (frame-hold stutter on agents) |
| V2l | 108.67–110.78 | Surrounded in the middle of the field, a ring of agents. Ring closes on each beat. | "With no warning I get" | GEN |
| V2m | 110.78–111.22 | Whispered "shot": muzzle flash and mote burst (P4 grammar, different angle). | *shot* | GEN + ENG |
| V2n | 111.22–112.96 | Freeze and invert (P5 grammar). Then, instead of the pause menu, an arcade **CONTINUE?** countdown: `9 … 8 …`. On "st-" (112.66) a hand (hers, in color) slams the ◀◀ button. | CONTINUE? 9 | ENG |

## 5. Drop 2 (112.96–139.00, bars 65–79): Braid shadows → the committee

Euphoric trance. The first big color moment.

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| E1 | 112.96–113.89 | Impact: an explosion of residue color fills the frame, then clears. | | ENG |
| E2 | 113.89–119.35 | **Thirteen "stop" chops = thirteen ghosts.** She rewinds a few seconds on every chop and the previous iteration *stays*: a translucent colored Jade freezes in place in a pose (sprint, wall-kick, roll…), each a different hue. Hard cuts around the field and the L tracks. By hit 13 a constellation of 13 ghost Jades surrounds the stunned agents. | counter ticks up each hit | GEN poses + ENG ghosts |
| E3 | 119.44–122.95 | **SINGING #2: "Rewind."** Pencil singing Jade at the Bean, held note. The color residue that has escaped the dream swirls around her in ribbons (still pencil). | **Rewind.** | SING + ENG ribbons |
| E4 | 123.00–126.25 | "Rewind." #2: **Super Meat Boy replay.** Every ghost runs at once with Jade, a stream of colored Jades pouring across the L tracks and leaping in unison. The agents can't tell which one is real. | **Rewind.** | GEN + ENG ghost multiplication |
| E5 | 126.25–130.50 | **Co-op platforming (bars 72–74).** Celeste shadow-Maddy beat: a ghost Jade cups her hands and boosts Jade up onto a rooftop. Another ghost hands her a **slip of paper**. | Slip, handwritten: *What's an anagram of Banach–Tarski?* (held 1.5 s) | GEN + ENG paper |
| E6 | 130.50–134.00 | **Banach–Tarski:** Jade atomizes into motes and reassembles as **two** Jades, who split in opposite directions. Agents split, confused. | | GEN + ENG motes |
| E7 | 134.00–139.00 | Color everywhere: ribbons layered over every surface, agents' residue meters spinning wildly, the frame saturating. Cuts on each beat. | | GEN ×3 + ENG |
| E8 | 139.00–141.00 | **"Anomaly detected."** Hard freeze. The frame inverts. Every agent in every shot turns to camera **in unison**, sunglasses flaring white. Agency terminal full screen: `TIME VARIANCE █████████` / `ANOMALY DETECTED`, typed on the spoken words. | terminal | GEN (agents turning) + ENG |

## 6. Glitch break (141.00–151.62, bars 81–86): the pencil

Weightless music box; drums out. This is the emotional turn.

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| G1 | 141.00–144.54 | Silence of drums. Jade floats in an empty white page. The world's engraving lines detach and drift around her like iron filings, slowly. She looks at her hand. The pencil in her bun glints. | none | GEN + ENG lines |
| G2 | 144.54–146.32 | **Low boom (144.54): she pulls the pencil from her bun and her hair falls loose**, waist-length, slow motion. The anime hero beat. | | GEN (hero clip, multiple takes) |
| G3 | 146.32–148.08 | She draws one stroke in the air with the pencil. The stroke is **full color** and where it passes, the engraving around it blooms into colored pencil. | | GEN + ENG stroke/bloom |
| G4 | 148.08–151.62 | **Kick returns (148.08): the world rotates.** The camera snaps to orthographic and the city clunks 90° like a Monument Valley crank on the kick. The diorama of the Loop assembles itself, piece by piece, to the music box. | | 3D |

## 7. Verse 3 (151.62–169.40, bars 87–96): Monument Valley

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| M1 | 151.62–153.98 | Isometric Loop diorama (engraved shader). Tiny Jade (hair down, pencil in hand) on a walkway. Agents enter from the edges. | | 3D + Jade sprite |
| V3S | 153.98–159.14 | **SINGING #3**, a deliberate echo of S1, same framing. "The night before my dissertation defense," but now the Bean's reflection shows the **truth**: an impossible Escher city, Penrose stairs looping around the Loop, patches of color. Hidden in plain sight all along. | V3-1 lyric, IM Fell, lower third | SING (new plate) |
| M2 | 159.14–165.18 | **Möbius Lake Shore Drive.** In the diorama, Lake Shore Drive is a Möbius strip (Escher's *Möbius Strip II*). Agents' sedans drive it forever; Jade turns a crank and the strip's join re-routes. | V3-2 "I'm speeding down Lake Shore, I dreamt", written along the road surface and following the Möbius twist | 3D |
| M3 | 165.18–169.40 | **"it couldn't trace."** Agents follow her path onto a rotating segment; she rotates it and they are routed onto the **Penrose staircase**, *Ascending and Descending*, marching forever. A residue meter falls to zero. | V3-3: "a shadow chasing me — it couldn't trace". The final word "trace" is drawn by a dotted tracing line that **loses the path** and wanders off. Riser into the drop. | 3D + ENG |

## 8. Final drop (169.40–211.64, bars 97–120): everything at once

Orchestral DnB. **The world is in color now**, in colored pencil, with Klimt-gold accents and Kandinsky shapes in the sky. Cuts are fast but every 2-bar phrase has one clear idea. Each whispered "never stop" is written in pencil somewhere in the world, small.

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| F1 | 169.40–172.96 | **IMPACT: color flood.** A wave of color sweeps across the engraved skyline from the pencil point; Jade sprints out of the wave at camera, hair streaming. | | GEN + ENG color wipe (engrave pass with color mask) |
| F2 | 172.96–176.48 | Wall-run up a skyscraper (Willis/Sears) with ghosts flanking. | *never stop* (pencil, on the wall) | GEN |
| F3 | 176.48–180.02 | **Relativity flip.** The city turns 90° and gravity changes; she runs across a ceiling of stairs (Escher *Relativity*). Agents fall off. | *never stop* | GEN or 3D |
| F4 | 180.02–183.56 | She leaps; the Bean below reflects her in color, and she dives *into* the reflection (inverse of S2). | *never stop* | GEN |
| F5 | 183.56–190.58 | **Heavier half: the boss.** A colossal **melting clock** (Dalí) hangs over the Loop as the agency's heart, dripping agents. Choir swell (183.72–187.08): a hero shot, Jade airborne, pencil drawn back like a sword. | | GEN |
| F6 | 190.58–197.60 | **The perspective move.** She draws a single loop in the air around the clock. The camera rotates with her gesture until the clock's own hands become a Penrose staircase. The agents pour onto it and loop. Super Meat Boy replay: thousands of ghost Jades in every color run beside her. | *never stop* at 196.68 | GEN + ENG + 3D |
| F7 | 197.60–209.90 | Escalating hero cuts (bars 113–119, every 2 beats). Ghost swarm, gold leaf, color, the melting clock folding into itself, agents on infinite stairs, her grin, the Banach–Tarski pair reuniting, a rewind ◀◀ that now *paints* instead of erasing. Wordless swells at 200.25 and 203.78 get the two biggest images. | | GEN ×6 |
| F8 | 209.90–211.64 | Band drop-out (210.90): she stops running, center frame, breathing, hair moving. All the ghost Jades behind her settle into one line, the committee. | *never stop* (210.77) | GEN |

## 9. Outro (211.64–227.96): trailer cards

| ID | In–Out | Picture | Text | Method |
|---|---|---|---|---|
| O1 | 211.64–218.92 | **Impact 1.** *Ascending and Descending*: the agents marching the Penrose Loop forever, slow pull-back. A variance report slides in and **un-writes itself** line by line. | `CASE 4,097 — SUBJECT: ████ NOT FOUND` → stamp: `TIMELINE IS NOW CANON` | 3D + ENG |
| O2 | 218.92–222.78 | **Impact 2.** Dawn. Jade (hair down, color world) at a door marked `DISSERTATION DEFENSE — 9:00 AM`. She pushes the pencil back into her hair and walks in. | | GEN |
| O3 | 222.78 | **Impact 3: HARD CUT TO BLACK.** | | |
| O4 | 226.00–227.96 | Over black, the final whisper "Never stop." A small HUD in the corner, `ITERATION 4,097`, flickers and the last digit **keeps rolling** (4,098 … 4,099 …). Fade to black at 227.0. | *never stop.* handwritten in pencil, drawn as she whispers | ENG |

## Sound design (later pass; keep subtle; music first)

- Clock tick reinforcement and a tape-rewind whir under C2.
- Muffled gunshot tails at 40.24 and 110.78.
- Tape-stop SFX at 40.65 and 111.22.
- 8-bit menu blips for P6.
- Arcade "CONTINUE?" voice (eleven-v3) at V2n.
- Sirens in V2a and V2f; bridge bell in V2c.
- Reload click in the 92.79 gap.
- L-train smash at 92.79.
- Pencil scratch at G3.
- Monument Valley crank clunk at 148.08.
- Mixed and exported only if it improves the track.
