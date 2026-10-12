# 2:00, the co-op level: plan for Jade

## Execution, phase 3: follow-ups and Jade's notes on the co-op clip (done 19:06, $0.88; coop total $4.34)

19:10: C2b's white flash at the 133.56 cut removed (hard cut); geography checked from single frames (girls on the far desk, agents thrown back onto the near desk, the raised pencil between them). Clip re-rendered.

Jade (verbatim, relayed by v4-B): "co-op is really good! just a few fixes" / "before the pencil bridge comes down, their
feet are missing and part of the pencil bridge mechanism is missing" / "agents look frozen instead of reacting to the
pencil bridge" / "maybe the pencil bridge can lift the other way up and when they let go of the second button and the
agents then get thrown back". Also "HILBERT HOTEL (missing HOTEL on a blank sign above)".

| Step | What | Status |
|---|---|---|
| F1 | bun pencils stay yellow (recolor.py `head_keep`) | **done**, checked on the split and level frames |
| F2 | HILBERT\nHOTEL on E7_04/05/06 | **done**, legible at 540p in all three |
| F3 | `b_miss_board` → turf-miss sound | **done**, mix rebuilt |
| J1 | feet | **done**: c1t2 keeps its whole matte, c2t1 colour test widened (281 px); every other frame 129.18–130.94 checked |
| J2 | drawbridge | **done**: hinge at the near lip (700,634), `hinge.py` bracket + `patch_tail.png`; raised = −78° |
| J3 | agents thrown back | **done**: `kf_agents_v1` → scaled on paper `kf_agents_v2` → `agents/take_1.mp4`, matte `agents.py`; keys AG_T/AG_X/AG_Y in build_timeline.py; cue `coop_bridge_throw` 134.00 |

## Execution, phase 2: build the level (ordered by v4-B after Jade's approval; cap $12, tag `v4B_coop_`; no commits)

**Status: done (18:45), $3.46 spent.** Clip `media/reviews/v4/B/0200_coop.mp4`; stills `media/reviews/v4/B/0200_coop_{split,hold,swap,bridge_up}.png`;
arm strip `media/reviews/v4/B/0200_e5_arm_before_after.jpg`; fragment `docs/revisions/v4/fragments/coop.json`; `docs/sections/D.md` Revision 6.
Rebuild order: `assets.py` → `level.py` → `build_timeline.py` → `tools/sfx/build.py` → render (`--force`). Jade (verbatim, relayed by v4-B, also in `docs/revisions/v4/B_progress.md`): "storyboard looks
good"; "instead of tagging them 1 and 2, let's go with blue and orange ... we should tag them at the moment of split,
so BLUE has white jacket with blue stripes, blue straps hanging from pants, and blue dots, and ORANGE has white jacket
with orange stripes, orange straps, and orange dots"; "the bridge: let's keep the environment still monochrome, so a
B/W pencil"; "yes, cutting a little bit of stopwatch is fine to make space for co-op"; "just noticed that at 2:00, gold
ethereal jade's arm pointing to Banach Tarski goes invisible for a moment when we need to see it".

Decisions that follow: no `1P` tags; twins told apart by costume from E6c on; ORANGE is always screen-left of BLUE
(E6c, C1, C2), so one x-split recolour pass can enforce the costumes; environment, pencil bridge and buttons stay
black and white; "held" is shown by the button sinking and the pencil sliding; E7's stopwatch insert goes and the
replay starts at 134.88; "Rewind." #2 stays unlettered.

New level beats (13 beats, 129.18–134.88): C1 129.18 run in · 130.06 skid at the lip · 130.50 ORANGE stamps the near
button, pencil slides out · 130.94 BLUE crosses · 131.82 agents come in behind ORANGE | cut 132.26 (bar line) C2: BLUE
stamps the far button · 132.68 ORANGE springs off and runs · 133.56 she is over · 134.00 (bar line) BLUE steps off, pencil
snaps back, agents stop at the lip · 134.44 both run on · 134.88 cut to E7.

| Step | What | Status |
|---|---|---|
| P1 | Timeline: E6c cut at 129.18; E7 without the stopwatch, starting 134.88; R1 flash softened; C1/C2 slots 129.18–132.26–134.88 | **done** in `build_timeline.py` (24 shots; E7 plat 134.88–135.76, leap 135.76–136.62, doubling on 134.88/135.32/135.76/136.19, first copy now blue; ribbons overlay starts 134.88 with v3 song times; chasm, ear, lawn, E8 untouched). No SFX cue sat on the moved part of E7 (next cues: `b_fall_short` 136.96, `b_wall_burst` 137.32, unchanged) |
| P2 | E6c recolour: BLUE and ORANGE from the split (`media/shots/C_coop/two_bo/`) | **done and checked** (128.4–129.1 frames: right twin has the blue band and straps, left stays orange; agents and paper untouched). Tool `tools/v4B/coop/recolor.py` |
| P3 | E5: the gold ghost's pointing arm vanishes for a moment; find and fix; before/after strip | **done**: the engrave matte lost her forearm and hand on take frames ~25–86 (123.1–124.8 in the cut), so the clean patch showed. `tools/v4B/coop/armfix.py` re-segments a crop with BiRefNet (+3-frame union) → `media/shots/C_coop/e5_arm/ghost_matte/`; `ghostseq.py` rebake → `media/shots/C_coop/e5_arm/ghost_slideptb_v4_{rgb,alpha}.mp4` (frame 0 identical to v3); wired via `twin_shot(ghost_stem=…)`. Strip: `media/reviews/v4/B/0200_e5_arm_before_after.jpg` |
| P4 | C1/C2 | **done**: takes `c1/take_2` (from composite kf `kf_c1_v8.png`), `c2/take_1`; C2 split at the 133.56 beat (jump cut over the landing, where the take swaps the girls); composited from the plate with sprite bridge/buttons. Shots `C1_hold`, `C2a_swap`, `C2b_letgo` |
| P5 | Sound | **done**: four procedural cues (`coop_*`), mix rebuilt (free); v3 mix kept as `media/sfx/Rewind_cinematic_sfx_mix_v3.mp3` |
| P6 | Hand-over | **done** (see status line) |

Spend log for this phase: `v4B_coop_` total $3.46 (3 kf, 6 edits, 3 Seedance takes); project $241.83.

## Execution, phase 1 (free part, ordered by v4-B at about 17:20; no paid calls, no commits)

**Status: all four steps done (17:25).** Jade has not yet decided on C1/C2; the cut now holds the retime and an animatic of the level so she can see it. Nothing is committed.

| Step | What | Status |
|---|---|---|
| 1 | `tools/sections/D/build_timeline.py`: E3 out, R1 in (119.44–119.98), E4a–E6c retimed, `D.js` regenerated | **done** (25 shots, no gap or overlap 112.96–141.00; shots before 119.44, E7, E8 and overlays identical to v3; `takes.json` untouched) |
| 2 | Animatic stills of storyboard panels 2–9 in `media/shots/C_coop/animatic/`, shots C1 and C2 at 129.62–134.00 | **done** (`storyboard.py --animatic` writes `p2.png`–`p9.png`; shots `C1_hold`, `C2_swap`) |
| 3 | `tools/sfx/build.py`: four cues 3.50 s earlier; v3 mix copied to `media/sfx/Rewind_cinematic_sfx_mix_v3.mp3`; rebuild only if free | **done**: `b_boost` 126.56, `b_pileup` 127.44, `b_atomize` 127.88, `b_implode` 128.32 (v3 times in a comment). No other cue sits in 119.44–134.00 (E3, the wall word, the haul and the slide never had one). The build is local DSP plus cached sources in `media/sfx/gen/`, no paid call, so the mix was rebuilt: `media/sfx/Rewind_cinematic_sfx_mix.mp3`; v3 copies: `Rewind_cinematic_sfx_mix_v3.mp3`, `cues_v3.json` |
| 4 | `--list` check, preview render 116.5–135.3, `media/reviews/v4/B/0200_coop_retime_animatic.mp4`, contact sheet | **done**: `--list --preview` shows 25 shots back to back, 112.96–141.00. Clip: `media/reviews/v4/B/0200_coop_retime_animatic.mp4` (960×540, 18.8 s, 7.4 MB, rebuilt mix as audio). Sheet: `media/reviews/v4/B/0200_coop_retime_contact.jpg` |

Commands: `tools/engrave/.venv/bin/python tools/sections/D/build_timeline.py` (rebuilds `D.js`);
`~/Documents/moongazing/.venv/bin/python tools/v4B/coop/storyboard.py --animatic` (the stills);
`~/Documents/moongazing/.venv/bin/python tools/sfx/build.py` (the mix, local, free);
`node render/engine/render.mjs --timeline render/timeline/_D_solo.js --range 116.5 135.3 --preview --encode --force --audio media/sfx/Rewind_cinematic_sfx_mix.mp3`
(`--force` because the engine does not notice a changed still). v3 values are in comments marked `v3:`;
`git diff tools/sections/D/build_timeline.py tools/sfx/build.py` shows every change.

**Checked on the contact sheet and a frame-by-frame strip of R1:**

- R1 goes the right way: from ghost 13's pose at the cornice down to the foot of the stairs in 13 frames, under the
  VHS search look, with a `◀◀ ×4` chip and the word on the brickwork; ghosts 11 and 12 slide back into the ladder.
  It reads as a rewind, not as smooth backwards running: at about 4.4× her pose jumps between frames, and the first
  frame is washed out by the word's flash.
- Launch (126.56), crash (127.44), mote burst (127.88) and the implode into two (128.32) sit on their beats, and the
  four sounds are on them. The launch picture is 0.02 s ahead of its sound (half a frame).
- E7 from 134.00, E8 and everything before 119.44 are identical to v3 in `D.js`.
- Not judged from stills: whether E4a (×1.89, was ×1.75) and E5 (×1.52, was ×1.37) look hurried. Watch the clip.
- E6c's last 0.3 s is the heap alone with the take's own white speed streaks and the two ribbons.
- "Rewind." #2 (123.00) has no lettering, as planned (question 2).
- No button or bridge sounds yet: 129.62–134.00 is music only.

**To swap in the real takes later:** replace the `layers` of `C1_hold` and `C2_swap` in `build_timeline.py`
(the block marked `C1, C2 (v4)`); ids and times stay.

---

**Plan status: complete, waiting for Jade's go-ahead on C1/C2.** Nothing generated, nothing spent.
Written 2026-10-11 by `v4B-coop` for `v4-B`. Times are song seconds (v3 preview timecode).

Jade's note: the sung "Rewind." at 2:00 goes; Banach–Tarski happens a smidge earlier; the two Jades then play a
two-player co-op level, probably before the Super Meat Boy traces.

**In short:** E3 comes out. Everything from the ghost ladder to the split moves two bars (3.5 s) earlier, uncut. The
freed time, plus 0.9 s of dazed agents trimmed from the end of the split, becomes a 4.4 s co-op level at
129.62–134.00, straight before the replay. Two new generated shots, about $4.

![storyboard](../../../../media/reviews/v4/B/plans/coop/storyboard.jpg)

Storyboard: `media/reviews/v4/B/plans/coop/storyboard.jpg`. What plays now:
`media/reviews/v4/B/plans/coop/v3_contact_108_142.jpg` (every 0.5 s, 108–142 s).

## The proposed order, 119.44–141.00

Every cut is on a tracked beat or on a sung-word onset (119.44, 123.00), as in v3. Up to 119.44 nothing changes.

| In | Out | Shot | What happens | Source |
|---|---|---|---|---|
| 119.44 | 119.98 | **R1** (new, free) | "Rewind." #1: the climb that just failed runs **backwards**. She un-climbs the fire escape through her five ghosts, which stay. The word is painted on the brickwork. | `B_climb` reversed; v3's wall lettering |
| 119.98 | 121.30 | E4a | Bar line: forwards again, up her own ghost ladder to the cornice. | v3, 8% faster |
| 121.30 | 123.00 | E4b | The gold ghost hauls her onto the roof. | v3, 10% faster |
| 123.00 | 125.26 | E5 | "Rewind." #2 sung over the slide down the giant book; the gold ghost points at `BANACH–TARSKI`. No lettering for the word here. | v3, 11% faster |
| 125.26 | 127.88 | E6a | Agents rush in; the blue ghost boosts her (126.56); they crash beneath her (127.44). | v3, same speed |
| 127.88 | 128.32 | E6b | Freeze, flash, she bursts into motes. | v3 |
| 128.32 | 129.62 | E6c | The motes land as **two Jades**; on the 128.76 bar line they sprint apart. Ends as they leave frame. | v3, last 0.9 s trimmed |
| 129.62 | 131.82 | **C1** (new) | Co-op, first half: Orange holds the bridge, Blue crosses, agents close on Orange. | new take |
| 131.82 | 134.00 | **C2** (new) | Co-op, second half: Blue holds, Orange runs, the bridge snaps back, agents stop at the lip, both run on. | new take |
| 134.00 | 139.00 | E7 | The Super Meat Boy replay. **Unchanged.** | v3 |
| 139.00 | 141.00 | E8 | "Anomaly detected." **Unchanged; 141.00 does not move.** | v3 |

The split now lands at 128.32 instead of 131.82. E7 needs two Jades at 134.00 (it doubles 2, 4, 8, 16) and its own
clips (`B_plat`, `B_leap`, `B_chasm_dash`, `B_ear`, `B_lawn`, the v2 meter); it gets both. The level also mends a jump
v3 has: there the two sprint apart and are side by side on the platform one cut later.

## The co-op level in five lines

1. A gap too wide to jump. A bridge is parked on the far side. One big floor button on each side.
2. The bridge is out only while a button is held down, so one Jade can hold it or cross it, never both.
3. Orange stamps the near button and stays down. Blue sprints across. Agents come in behind Orange, who cannot move.
4. Blue lands on the far button; the bridge is now held from her side. Orange springs off as a hand closes on air, and runs.
5. Blue lets go. The bridge snaps back, away from the agents, who stop at the lip. Nobody falls. Both run on.

**Telling the twins apart.** They are the same girl in the same jacket, so each gets a floor ring, a trail and a small
tag in her colour (orange and blue, the two trails v3 already gives them in the split). Both tags read `1P`: neither
is the copy. Lit buttons and the bridge take the colour of whoever is holding.

**Where.** The street of giant books from E5 and E6, so the split, the level and the hint share a place. The button is
the round arcade button she slams for ◀◀ at 112.5, at floor size. The bridge is a giant pencil off the desk: an object
she runs on, not a line anyone draws (see question 1).

**Agents.** They are the clock. She can only escape by holding still while they close in, and trusting her double.
The buttons answer only to her colour, so the agents cannot follow; one stamps a dead button (optional gag).

## Why this mechanic

| Mechanic | Reads in a few seconds? | Needs two of her? |
|---|---|---|
| **Hold the bridge** (chosen) | Yes. One cause and effect, press then bridge in her colour, shown twice with the roles swapped. One fixed side view. | Yes. It is the "be in two places at once" puzzle, and the second half is the first half again with the other self. |
| Seesaw launch, then a haul | Yes | Weakly. It is the third boost-and-haul in twelve seconds, and the favour is not returned in kind. |
| Push a giant book across the gap | Yes | No. One Jade could push it and cross it herself. |

## What plays now (v3), for comparison

Read off the contact sheet (labels there are within a quarter second) and `render/timeline/D.js`.

| Time | Shot | Picture | Made from |
|---|---|---|---|
| 108.0–112.96 | V2k–V2n | The corner: bump, pistol, the hit, CONTINUE?, her hand on the ◀◀ button | takes + HUD (not this note's) |
| 112.96–116.95 | E1, E2 1–8 | Bloom, then eight retries, a cut per "stop", a ghost left by each | v2 and v3 takes, ghost sprites |
| 116.95–119.44 | E2 9–13 | Held wall: five climbs leave a ladder of five ghosts | `B_climb` |
| 119.44–122.95 | **E3** | **Watercolor Jade sings "Rewind."** (the shot that goes) | `media/sing/E3/` |
| 122.95–124.38 | E4a | Up the ghost ladder; "Rewind." on the brickwork | `B_climb` |
| 124.38–126.25 | E4b | Gold ghost hauls her onto the roof | `B_haul_b` |
| 126.25–128.76 | E5 | Book slide; the ghost points at `BANACH–TARSKI` | `B_slide_point_b`, pinned label |
| 128.76–131.38 | E6a | Blue ghost boosts her; agents crash beneath | `B_swarm_boost` |
| 131.38–134.00 | E6b, E6c | Motes; two Jades; they sprint apart at 132.26; from 133.0 only dazed agents | still + motes, `B_two` |
| 134.00–139.00 | E7 | Replay: doubling on platform and beam, stopwatch, chasm, earpiece, lawn | v3 takes, engine copies |
| 139.00–141.00 | E8 | "Anomaly detected." | v2 |

## How the new shots get made, and cost

| Shot | Method | Cost |
|---|---|---|
| R1 | Engine only. `media/shots/B_climb/take_1_engraved.mp4` with a negative rate (source 5.95 → 3.45 in 0.54 s), same ×1.4 wall framing and ghost rungs as E4a, v3's pinned "Rewind." retimed to `word:rewind#3`, the ◀◀ blip used on the chops. | $0 |
| C1, C2 | One keyframe each (nano-banana-pro; refs `media/design/jade_canon_turnaround.png`, `jade_bun_two_pencils.png`, `media/shots/B_two/kf_v1.jpg` for the street). Seedance 2.0, 720p, 5 s, locked camera, one retake each allowed. Engrave and matte as v3 (`tools/sections/D/publish.py`); the girls never touch, so `split2.py` separates them easily. | 2 keyframes $0.27, 4 takes $3.00 |
| Bridge in and out | The bridge is really there in both takes, so she runs on something solid. A clean plate without it (one nano edit per take) is wiped on and off by the engine. Colour, button glow, rings, trails and `1P` tags are engine layers keyed from her matte (`mtrack.py`, `ribbon`, Press Start 2P). | 2 clean plates $0.27 |
| E4a–E6c | The same clips, patches and baked ghosts (`media/shots/B_haul_b`, `B_slide_point_b`, `B_swarm_boost`, `B_two`, `media/shots/_D/v3/`), with new start times and rates in `build_timeline.py`. | $0 |

**Expected about $3.50–4, ceiling $10** of the $30 for this note. **Two new generated shots.**
Fallback if two takes cannot be got clean: build the level from sprites (her run from the `B_plat` matte over the
clean plate). Free, but fewer poses and a cut-out look.

## Rejected

- **Drawing the bridge with the pencils:** reads fast and looks good, but she would draw 14 s before the scene where she first finds she can (pencil out at 144.54), and the pencils would leave the bun early.
- **The level at the main chasm** (free plate `media/shots/B_level/kf_v1.jpg`): E7 replays that chasm three seconds later with copies falling short; a bridge there would undo it.
- **The level after the replay:** it would cost the earpiece and lawn shots and run into "Anomaly detected."
- **The split on "Rewind." #2 (123.00):** needs the climb, haul and swarm boost cut to under a second each; they were Jade's v3 notes.
- **One held shot for the whole level:** possible; a cut at the swap gives each half one idea and a closer look at the second.
- **`1P` and `2P` tags:** clearer as game shorthand, but it names one of them the copy.

## Risks

- **Twins at 540p.** At a third of frame height they are told apart only by ring, trail and tag. If that is not enough, tint the whole button side of the frame, or push in further on C2.
- **Generation.** Two identical girls, agents and a precise order of events in one take. The mechanism is done by the engine to keep the takes simple, but expect a retake.
- **The wall is on screen 4.4 s without a break** (116.95–121.30), where v3 cut away to the singer.
- **The hint is a quarter of a second shorter** (2.26 s, was 2.51 s). The label is there from the first frame.
- **E6c to C1.** They sprint apart, then enter the room together from the left. A cheat, smaller than the one in v3.
- **Sound.** Four cues in the shared `tools/sfx/build.py` move 3.50 s earlier (`b_boost`, `b_pileup`, `b_atomize`, `b_implode`), and the level wants a button and a bridge sound.
- **A lot in C2** (swap, run, bridge back, agents stop, exit in 2.2 s). First thing to cut: the dead-button gag.

## Questions for Jade

1. **Pencils.** I kept them in the bun and made the bridge a giant pencil lying on the desk, so nobody draws before 2:24. Would you rather the two Jades draw the bridges (graphite one way, rainbow back)? Same beats, same cost.
2. **"Rewind." #2** now plays over the book slide with no lettering, so the spine is the only text in the shot. Fine, or do you want the word shown again at 123.00?
3. **Tags:** both `1P`, or `1P` and `2P`, or none (rings and trails only)?
4. **Length.** The level is 4.4 s. For two more beats I would drop E7's stopwatch insert (135.76–136.62) and start the replay at 134.88. Want that?
