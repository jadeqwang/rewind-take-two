# 2:00, the co-op level: plan for Jade

## Execution (free part, ordered by v4-B at about 17:20; no paid calls, no commits)

**Status: in progress.** Jade has not yet decided on C1/C2; this builds the retime and an animatic so she can see it.

| Step | What | Status |
|---|---|---|
| 1 | `tools/sections/D/build_timeline.py`: E3 out, R1 in (119.44–119.98), E4a–E6c retimed, `D.js` regenerated | **done** (25 shots, no gap or overlap 112.96–141.00; shots before 119.44, E7, E8 and overlays identical to v3; `takes.json` untouched) |
| 2 | Animatic stills of storyboard panels 2–9 in `media/shots/C_coop/animatic/`, shots C1 and C2 at 129.62–134.00 | **done** (`storyboard.py --animatic` writes `p2.png`–`p9.png`; shots `C1_hold`, `C2_swap`) |
| 3 | `tools/sfx/build.py`: four cues 3.50 s earlier; v3 mix copied to `media/sfx/Rewind_cinematic_sfx_mix_v3.mp3`; rebuild only if free | not started |
| 4 | `--list` check, preview render 116.5–135.3, `media/reviews/v4/B/0200_coop_retime_animatic.mp4`, contact sheet | not started |

To resume: `git diff tools/sections/D/build_timeline.py tools/sfx/build.py` shows what is done; v3 values are kept
in comments marked `v3:`. Rebuild with `tools/engrave/.venv/bin/python tools/sections/D/build_timeline.py`.

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
