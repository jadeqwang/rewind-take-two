# v4-B progress (everything except the singer)

Brief: `docs/revisions/v4/B.md`. Rules: `docs/revisions/README.md`, `docs/revisions/v4/README.md`.
A fresh session can carry on from this file alone. Last updated: 2026-10-11 19:02.

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
| 2 | 0:13 | Bean: start wide, move in | **plan + free previz ready** 18:10 (`docs/revisions/v4/plans/bean.md`, `media/reviews/v4/B/plans/bean/previz.mp4`); shown to Jade 18:12, waiting for her go ($1.44: one 4K wide plate outpainted from `plate_close_1_crop`). Build numbers are in the plan's "For the build" section. v4-A told the four singer details at 18:12. | `render/timeline/A.js` S1 |
| 3 | 0:26 | plate `TVA 1729` | **done** 17:50 (sub-agent `v4B-plate`, $0): reads at 540p, small; alt with push in `0026_plate_alt_push.mp4`; write-up `docs/revisions/v4/plans/plate_d3.md`; reusable `tools/v4B/plate/plate.js` | `render/timeline/A.js` D3 |
| 4 | 1:30 | car: over-the-shoulder, real mirror, TVA plates (Three.js) | **plan + Three.js blockout ready** 18:45 (`docs/revisions/v4/plans/car.md`, sheet `media/reviews/v4/B/plans/car/contact_sheet.jpg`, `animatic_A|B|C.mp4`, code `tools/v4B/car/`); shown to Jade 18:47, waiting for her pick (A/B/C) and go (about $1.80-3). v4-B recommends A with the over-shoulder shot starting at 89.26 so it gets 1.76 s instead of 0.88 s. | `render/timeline/C.js` V2f1/V2f2 |
| 5 | 1:39 | gunfire: behind the agents, push in past shoulders | **plan + blockout ready** 19:00 (`docs/revisions/v4/plans/gunfire.md`, sheet `media/reviews/v4/B/plans/gunfire/contact_sheet.jpg`, tool `tools/v4B/gunfire/blockout.py`, `geometry.json`); shown to Jade 19:02, waiting for her go ($3.70 first round, about $7.50 with retakes, ask at $12). G1 = 98.28-100.70. | `render/timeline/_B_verse2.js` |
| 6 | 1:41 | one fires, two on earpieces | same plan: G2 = 100.70-104.22, only C fires, A then B go to earpieces; replaces `B2_lawn2` and `B2_ear` | same |
| 7 | 2:00 | replace E3 with co-op level; Banach–Tarski earlier | **plan ready** 17:58 (`docs/revisions/v4/plans/coop.md`, storyboard `media/reviews/v4/B/plans/coop/storyboard.jpg`), shown to Jade 18:00, waiting for her go on the two generated shots (C1, C2). **Free retime done 18:25 and in the cut**: E3 out, `R1_unclimb`, E4a-E6c 3.50 s earlier, `C1_hold`/`C2_swap` as animatic stills (`media/shots/C_coop/animatic/`), four SFX cues moved and the mix rebuilt (v3 mix kept as `media/sfx/Rewind_cinematic_sfx_mix_v3.mp3`). Check clip `media/reviews/v4/B/0200_coop_retime_animatic.mp4`. Rough: R1's pose jumps (4.4x reverse); E6c's last 0.3 s is the agent heap alone; `docs/sections/D.md` not yet updated. | `tools/sections/D/build_timeline.py` |
| 8 | 3:33 | "ANOMALY REPORT" | **done** 17:35; after `media/reviews/v4/B/0333_report_stamp_credit.mp4` | `tools/sectionF/edl.py` |
| 9 | 3:37 | stamp wording | **in the cut as `TIMELINE NOW CANON`**, 1.4x larger; both wordings in `media/reviews/v4/B/0337_stamp_both.jpg`; Jade to pick (`STAMP` in edl.py) | same |
| 10 | end | title credit in HUD face beside "never stop." | **built** 17:35 (overlay `O_credit`, module `tools/sectionF/modules/end_credit.js`, wording = `CREDIT` in edl.py); Jade to confirm wording | `tools/sectionF/edl.py` O4 |

## Running right now

Nothing (see "State at 19:02" below). Sub-agent outputs are listed per note in the table above.

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

## Jade's decisions (verbatim, with time)

None yet in this pane. Defaults from the brief: plates `TVA 1729` (hero), `TVA 4104`, `TVA 4096`, `TVA 0900`;
stamp `TIMELINE NOW CANON`; end credit yes, wording to confirm.

## Open questions

- End credit wording (draft in the brief).
