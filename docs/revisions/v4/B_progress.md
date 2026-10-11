# v4-B progress (everything except the singer)

Brief: `docs/revisions/v4/B.md`. Rules: `docs/revisions/README.md`, `docs/revisions/v4/README.md`.
A fresh session can carry on from this file alone. Last updated: 2026-10-11 19:25.

## Setup facts (saves re-discovering them)

- ffmpeg is not on PATH: `FF=~/Documents/moongazing/.venv/bin/ffmpeg`. Python: `PY=~/Documents/moongazing/.venv/bin/python`.
- Pass `--preview` on every `render.mjs` call (stills and `--list` too), or it fills `media/engine_cache/full`.
- v3 frames at each note's timestamp: `media/reviews/v4/B/v3_frames/`, contact sheet `media/reviews/v4/B/v3_contact.jpg`.
- Spend at start: $222.57 of $400. B's soft limit this pass: $90. Tag calls `v4B_…`.
- Disk at start: 21 GB free.

## Notes and status

| # | v3 time | Note | Status | Files |
|---|---|---|---|---|
| 1 | 0:09 | name not legible | **done** 17:40: 92 px + ink plate; after `media/reviews/v4/B/0009_name.mp4` | `render/timeline/A.js` C3, `render/engine/modules/title.js` |
| 2 | 0:13 | Bean: start wide, move in | **done** 18:20 ($0.72): plate `media/sing/plates/plate_wide_v4*` (B2 chosen, notes `plate_wide_v4.md`), pre-rendered background `tools/v4B/bean/bg.py`, S1 + `A_S1_lyric` in `render/timeline/A.js` (constants `S1_MATTE`, `BEAN`). After `media/reviews/v4/B/0013_bean_wide.mp4` (re-rendered 18:30 on v4-A's `v4_sync_1080_open.mp4`, blink at 12.93 patched out, commit 1ec8d3e). | `render/timeline/A.js` S1 |
| 3 | 0:26 | plate `TVA 1729` | **done** 17:50 (sub-agent `v4B-plate`, $0): reads at 540p, small; alt with push in `0026_plate_alt_push.mp4`; write-up `docs/revisions/v4/plans/plate_d3.md`; reusable `tools/v4B/plate/plate.js` | `render/timeline/A.js` D3 |
| 4 | 1:30 | car | **done** 18:05 (option C, $0.67): two engraved stills + engine push, `tools/v4B/car/car_shot.js`, shots `media/shots/V2f3/`, `V2f4/`; `CAR_START = 89.26` in `render/timeline/C.js`; HUD and `C_lyr_back` end at `CAR_START`. After `media/reviews/v4/B/0130_car.mp4`. Open: keep 89.26?; mirror sedans are grey with light bars, not plain black | `render/timeline/C.js` |
| 5 | 1:39 | gunfire G1 | **done** 18:45 ($4.76): G1 98.28-100.70 from behind the agents; `V4_GUN = true` in `render/timeline/_B_verse2.js` (v3 in the else branch), new `_B_gunfire.js`, `_B_glayout.js`, `_B_gunribbon.js`, `_B_gtrack.js`, `_B_ggun.js`; shots `media/shots/B_g*`. After `media/reviews/v4/B/0139_gunfire.mp4` (SFX mix muxed in by v4-B). |
| 6 | 1:41 | gunfire G2 + G3 | **done** 18:45: G2 100.70-102.46 only C fires, A/B on earpieces; G3 102.46-104.22 earpiece close-up. TODO after co-op finishes with `tools/sfx/build.py`: `b_miss_board` (101.14) should become a turf miss. | 19:05: leads (she cuts 4 frames before each shot, round lands ~1.5 m ahead on her old line), engine re-aim + kick on the cut-outs, HILBERT HOTEL behind `HOTEL_SIGN` in `_B_verse2.js`. D shots E7_04/05/06 HOTEL: corners in `tools/v4B/gunfire/hotel_corners_D.json`, sent to `v4B-coop` to apply. |
| 7 | 2:00 | co-op level + E5 arm | **built** 18:55 ($3.46): C1/C2 generated, twins BLUE/ORANGE from 128.32, B/W pencil drawbridge, stopwatch out (replay from 134.88), E5 arm re-segmented; four procedural button/bridge cues; `docs/sections/D.md` Revision 6. After `media/reviews/v4/B/0200_coop.mp4`, arm strip `0200_e5_arm_before_after.jpg`. Open: BLUE's bun pencils tinted blue (canon: yellow); drawbridge vs slide (Jade). |
| 8 | 3:33 | "ANOMALY REPORT" | **done** 17:35; after `media/reviews/v4/B/0333_report_stamp_credit.mp4` | `tools/sectionF/edl.py` |
| 9 | 3:37 | stamp wording | **in the cut as `TIMELINE NOW CANON`**, 1.4x larger; both wordings in `media/reviews/v4/B/0337_stamp_both.jpg`; Jade to pick (`STAMP` in edl.py) | same |
| 10 | end | title credit in HUD face beside "never stop." | **built** 17:35 (overlay `O_credit`, module `tools/sectionF/modules/end_credit.js`, wording = `CREDIT` in edl.py); Jade to confirm wording | `tools/sectionF/edl.py` O4 |

## Running right now

The four execution sub-agents listed under "Execution round" below (started 19:25).

Budget split of B's $90 (estimates for the planners to work inside): car $15, gunfire $25, co-op $30, Bean $10,
D3 plate $3, reserve $7.

v4-B itself: text fixes 1, 8, 9, 10 (done).

`v4B-plate` finished 17:50. `v4B-coop` finished its plan 17:58 and was continued at 18:00 (same sub-agent) to do
the **free** part of note 7: E3 out, R1, the 3.50 s retime in `tools/sections/D/build_timeline.py`, the four SFX
cue moves, and a storyboard animatic standing in for C1/C2 on their beats. No spend. It writes its status to the
top of `docs/revisions/v4/plans/coop.md` ("Execution" section) and the check clip to
`media/reviews/v4/B/0200_coop_retime_animatic.mp4`. If it is missing on resume, redo from the beat plan below.

Told `v4-A` at 17:18: E3 is going; S1 needs her on-plate file plus matte dir at v3 scale/position/cut line, no
baked camera move, clean hair edge; she is bottom-anchored at 40-45% of v3 scale at the widest, push-in done by
about 13.9 s; S1/V3S in/out unchanged; A edits only `S1_SRC`/`S1_IN`.

## Next steps, in order

1. Done: text fixes 1, 8, 9, 10 (manifest entries written; committed). After any edit to `tools/sectionF/edl.py` run
   `$PY tools/sectionF/edl.py` to regenerate `media/shots/F_edl.json`; check with
   `node render/engine/render.mjs --timeline tools/sectionF/F_preview_timeline.js --preview --stills …`.
   Title check timeline: `tools/v4B/title/variants.js`. C3 after clips render through `render/timeline/_A_test.js`.
2. As each sub-agent reports: read its plan file, look at its stills, fix what is weak, then show Jade ONE summary of
   the four plans in the pane (what she will see, cost, questions) and wait for her go before any spend.
3. After her go: execute each plan (sub-agent per note again), after clips, manifest entries, commits.
4. Tell `v4-A` before editing S1 in `render/timeline/A.js`.

## Note 7 beat plan (from `plans/coop.md`; times are song seconds, every cut on a tracked beat or sung onset)

E3 out. The ladder-to-split block moves two bars (3.50 s) earlier, uncut; the level takes 129.62-134.00.

| In | Out | Shot | What |
|---|---|---|---|
| 119.44 | 119.98 | R1 (new, engine only) | "Rewind." #1: the failed climb runs backwards (`B_climb` reversed), word on the brickwork |
| 119.98 | 121.30 | E4a | ghost ladder (8% faster) |
| 121.30 | 123.00 | E4b | haul (10% faster) |
| 123.00 | 125.26 | E5 | book slide, `BANACH–TARSKI` hint (11% faster) |
| 125.26 | 127.88 | E6a | swarm boost (launch 126.56, crash 127.44) |
| 127.88 | 128.32 | E6b | atomize |
| 128.32 | 129.62 | E6c | two Jades, sprint apart on 128.76 (last 0.9 s trimmed) |
| 129.62 | 131.82 | C1 (new, generated) | Orange holds the button, Blue crosses the bridge, agents close on Orange |
| 131.82 | 134.00 | C2 (new, generated) | Blue holds from the far side, Orange runs, bridge snaps back, agents stop at the lip |
| 134.00 | 141.00 | E7, E8 | unchanged; 141.00 does not move |

Sound: `b_boost`, `b_pileup`, `b_atomize`, `b_implode` in `tools/sfx/build.py` move 3.50 s earlier; the level wants
a button and a bridge sound. Estimated spend for C1/C2: $3.50-4, ceiling $10.

Open questions put to Jade at 18:00: (1) bridge is a giant pencil prop, pencils stay in the bun, or the two Jades
draw the bridges; (2) show "Rewind." again at 123.00 or not; (3) tags `1P`/`1P`, `1P`/`2P` or none; (4) keep the
level at 4.4 s or take two more beats from E7's stopwatch insert (135.76-136.62).

Note 2 questions put to Jade at 18:12: (1) centred with her head in the arch, or off to one side; (2) land on
"before" at 13.92 or a bar later at 14.36; (3) tiny pedestrians for scale or an empty plaza; (4) the optional
$1.50 Seedance comparison (default: skip).

Note 4 questions put to Jade at 18:47: (1) option A (true mirror: her eyes over the shoulder, then cut to her
eye line and push into the mirror), B (mirror turned to the lens, cut in) or C (B as one take); (2) start the
over-shoulder shot at 89.26 (trimming V2f1 to two beats) or keep 90.14; (3) lyric split SIRENS on a road sign /
IN MY MIRROR on the mirror's edge; (4) plates right-reading and 1.5x as at 0:26 (default yes).

Notes 5/6 questions put to Jade at 19:02: (1) G2 as one 3.5 s shot, or keep the 102.46 cut with an earpiece
close-up (about $2 more); (2) her size, about a fifth of frame height with her back to camera, or nearer; (3) G1
shooters B, B, C, C with A only aiming, or all three fire.

**State at 19:02: all five sub-agents have finished. Nothing is running. Spend by B so far: $0.** Everything
left on notes 2, 4, 5, 6, 7 waits for Jade's go; total asked for is about $12-16 of B's $90. When she answers,
spawn one Opus sub-agent per note with the plan file as its brief (each plan ends with build notes).

19:10: `v4-A` reports the v4 singer has landed (`media/sing/S1/v4_sync_1080.mp4` + `v4_sync_1080_matte/`, same for
V3S) and is swapping `S1_SRC`, the S1 `HER.src`, `V3S_SRC` and the V3S `HER.src` in `A.js`/`E.js`. Build the Bean
push on those paths; her scale and bottom span match v3 within a few px.

## Jade's decisions (verbatim, with time)

**19:20, pasted into the pane, verbatim:**

> * storyboard looks good
> * instead of tagging them 1 and 2, let’s go with blue and orange since that is already in their color palette, but we should tag them at the moment of split, so BLUE has white jacket with blue stripes, blue straps hanging from pants, and blue dots, and ORANGE has white jacket with orange stripes, orange straps, and orange dots.
> * the bridge: let’s keep the environment still monochrome, so a B/W pencil
> * yes, cutting a little bit of stopwatch is fine to make space for co-op
> * bean update looks good, all those choices are fine in previz
> * just noticed that at 2:00, gold ethereal jade’s arm pointing to Banach Tarski goes invisible for a moment when we need to see it
> * animatic_C.mp4 is the best of the 3, split lyric is good, start over the shoulder is good, front readable is good
> * gunshot - go with the earpiece closeup
> * frame height seems fine, only 2 agents firing is fine

How v4-B reads it (v4-B's interpretation, told to Jade at 19:22 so she can correct it):

- **Co-op (note 7): go.** No `1P`/`2P` text tags. The twins are colour-coded in costume from the split (E6c, 128.32)
  on: BLUE = white jacket, blue band, blue straps, blue dots; ORANGE = white jacket, orange band, orange straps,
  orange dots. The environment stays black and white: the bridge is a giant pencil drawn in the engraving, and
  buttons and bridge take no colour. The level gets two more beats: the stopwatch insert in E7 (135.76-136.62) goes
  and the replay starts at 134.88, so the level is 129.62-134.88. Second "Rewind." at 123.00: not answered, default
  stays (no lettering).
- **New note (2:00 area):** the gold ghost's pointing arm in E5 (book slide, `BANACH–TARSKI`) disappears for a
  moment. Fix it.
- **Bean (note 2): go** as in the previz: centred, lands 13.92, pedestrians, no Seedance comparison.
- **Car (note 4): option C** (one take: hold wide over her shoulder, push between the seats to the mirror; mirror
  turned to the lens). Lyric split approved (SIRENS on the road sign, IN MY MIRROR on the mirror). Plates
  right-reading. "start over the shoulder is good" is read as yes to starting the shot at 89.26 (V2f1 trimmed to
  two beats): **this reading is v4-B's, flagged to Jade.**
- **Gunfire (notes 5, 6): go**, with the cut at 102.46 kept and an earpiece close-up after it; her size and two
  agents firing in G1 are fine.
- Not answered, defaults stay in the cut: stamp `TIMELINE NOW CANON`; end-credit wording (draft); plate size at 0:26.

**18:40, Jade in the pane, verbatim (after the gunfire clip):**

> * the gunfire is almost right. at “zigzag” it’s almost right, but it doesn’t seem like they’re trying hard. I expect them to be aiming for where they think she’s going to be except she changed direction. same with “across the field of grass”
> * HILBERT HOTEL (missing HOTEL on a blank sign above)

v4-B's reading: every miss in G1 and G2 is aimed where she WOULD be if she kept her line (a lead), and she cuts the
other way just before it lands, so the impact is ahead of her on her old line, not behind her. The rooftop sign reads
HILBERT HOTEL wherever it shows: HOTEL goes on the blank panel above HILBERT. Sent to `v4B-gun` at 18:42.
Jade, 18:44, verbatim: "the agent animation could just be trying to adjust to aim better and some gun kickback". So no
new take for the G1 agents: engine animation of the cut-outs (re-aim tracking her between shots, kickback on each
shot). Sent to `v4B-gun`.

**18:47, Jade, verbatim:** "0130_car.mp4 would be better if it were animated (even if you could just feel the cars
moving)". Sent to `v4B-car` (resumed): engine motion first (ride bob, road moving, streetlight sweeps, fleet cut-outs
swaying and closing, light bars flashing), Seedance only if that still reads as a still; cap = rest of its $8.

**18:49, Jade, verbatim:** "SIRENS text should feel more woodblock textured". Sent to `v4B-car`: re-letter with
`tools/sectionA/modules/woodcut.js`.

**19:10, Jade, verbatim:**

> * co-op is really good! just a few fixes:
>   * before the pencil bridge comes down, their feet are missing and part of the pencil bridge mechanism is missing
>   * agents look frozen instead of reacting to the pencil bridge
>   * maybe the pencil bridge can lift the other way up and when they let go of the second button and the agents then get thrown back
>   * is this a job for threejs or a video model to help with?

Sent to `v4B-coop`: fix feet and layer order; pencil + visible hinge as rigid engine sprites; agents run onto the
bridge, and on BLUE's release (134.00) the bridge lifts the other way and flings them back onto the near desk
(slapstick, nobody falls). Agents' motion from one Seedance take (matted), bridge in the engine. v4-B's answer to
her question: engine for the bridge, video model for the agents, three.js not needed.

## Execution round

**Correction:** clock times written in this file before 17:55 ran ahead of the real clock (the "19:xx" entries
were all before 17:45 CDT). Jade's decisions above came at about 17:40.

**17:44: all four sub-agents died mid-step on an API login error** ("Not logged in · Please run /login"). Jade
resumed the session at 17:55; v4-B restarted co-op at 17:55; bean, car and gunfire were hung, so v4-B stopped them and restarted all three at 17:58 (Jade: "restart the other three now, don't wait"). Spend at the
restart: $234.68 total; B's v4 calls so far about $2.6 (bean $0.72, car $0.40, coop $0.40, gun $1.08).

Four Opus sub-agents, the same ones that wrote the plans, continued with Jade's decisions. They die with this
session; on resume, read each plan file's "Execution" section and respawn from there with the plan as the brief.
Each writes a manifest fragment to `docs/revisions/v4/fragments/<name>.json`; v4-B merges fragments into
`review_B.json` and commits. No sub-agent commits.

| Sub-agent | Notes | Edits | Cap, tag | After clip |
|---|---|---|---|---|
| `v4B-bean` | 2 | `render/timeline/A.js` (S1, `A_S1_lyric` only), new plate under `media/sing/plates/` | $5, `v4B_bean_` | `media/reviews/v4/B/0013_bean_wide.mp4` |
| `v4B-car` | 4 | `render/timeline/C.js` (V2f rows, `C_lyr_sirens`), new shot folders beside `media/shots/V2f2/` | $8, `v4B_car_` | `media/reviews/v4/B/0130_car.mp4` |
| `v4B-gun` | 5, 6 | `render/timeline/_B_verse2.js` (lawn shots), new `media/shots/B_g*` | $12, `v4B_gun_` | `media/reviews/v4/B/0139_gunfire.mp4` |
| `v4B-coop` | 7 + E5 arm | `tools/sections/D/build_timeline.py` → `render/timeline/D.js`, `tools/sfx/build.py`, new `media/shots/C_coop/` | $12, `v4B_coop_` | `media/reviews/v4/B/0200_coop.mp4` |

None yet in this pane. Defaults from the brief: plates `TVA 1729` (hero), `TVA 4104`, `TVA 4096`, `TVA 0900`;
stamp `TIMELINE NOW CANON`; end credit yes, wording to confirm.

## Open questions

- End credit wording (draft in the brief).
