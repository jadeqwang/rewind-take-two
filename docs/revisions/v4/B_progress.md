# v4-B progress (everything except the singer)

Brief: `docs/revisions/v4/B.md`. Rules: `docs/revisions/README.md`, `docs/revisions/v4/README.md`.
A fresh session can carry on from this file alone. Last updated: 2026-10-11 17:42.

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
| 2 | 0:13 | Bean: start wide, move in | not started (needs plan + v4-A) | `render/timeline/A.js` S1 |
| 3 | 0:26 | plate `TVA 1729` | not started | `render/timeline/A.js` D3 |
| 4 | 1:30 | car: over-the-shoulder, real mirror, TVA plates (Three.js) | not started (plan to Jade first) | `render/timeline/C.js` V2f1/V2f2 |
| 5 | 1:39 | gunfire: behind the agents, push in past shoulders | not started (plan to Jade first) | `render/timeline/_B_verse2.js` |
| 6 | 1:41 | one fires, two on earpieces | not started (plan to Jade first) | same |
| 7 | 2:00 | replace E3 with co-op level; Banach–Tarski earlier | not started (plan to Jade first) | `tools/sections/D/build_timeline.py` |
| 8 | 3:33 | "ANOMALY REPORT" | **done** 17:35; after `media/reviews/v4/B/0333_report_stamp_credit.mp4` | `tools/sectionF/edl.py` |
| 9 | 3:37 | stamp wording | **in the cut as `TIMELINE NOW CANON`**, 1.4x larger; both wordings in `media/reviews/v4/B/0337_stamp_both.jpg`; Jade to pick (`STAMP` in edl.py) | same |
| 10 | end | title credit in HUD face beside "never stop." | **built** 17:35 (overlay `O_credit`, module `tools/sectionF/modules/end_credit.js`, wording = `CREDIT` in edl.py); Jade to confirm wording | `tools/sectionF/edl.py` O4 |

## Running right now

Five Opus sub-agents, spawned 17:20 by v4-B (background `Agent` calls; they die with this session, so if you are
resuming and a plan file below is missing or says "in progress", respawn that one with the same task).
The four planners spend **nothing** and edit **no shared timeline file**; they write a plan for Jade to approve.

| Sub-agent | Note | Task | Writes |
|---|---|---|---|
| `v4B-car` | 4 (1:30) | Three.js blockout of the over-the-shoulder car shot, 2-3 camera options as 540p stills, finishing pipeline + cost | `docs/revisions/v4/plans/car.md`, `media/reviews/v4/B/plans/car/`, new files under `tools/v4B/car/` |
| `v4B-gun` | 5, 6 (1:39, 1:41) | Plan + blockout of the behind-the-agents lawn shots on the beats, tracer geometry, earpieces, cost | `docs/revisions/v4/plans/gunfire.md`, `media/reviews/v4/B/plans/gunfire/`, `tools/v4B/gunfire/` |
| `v4B-coop` | 7 (2:00) | Beat plan for 119.44-141.00 with E3 removed, Banach-Tarski earlier, co-op level storyboard, cost | `docs/revisions/v4/plans/coop.md`, `media/reviews/v4/B/plans/coop/` |
| `v4B-bean` | 2 (0:13) | Plan for the wide Bean opening and push-in (plate, composite, lyric arc), cost | `docs/revisions/v4/plans/bean.md`, `media/reviews/v4/B/plans/bean/` |
| `v4B-plate` | 3 (0:26) | Execute: track the sedan's plate in D3, pin `TVA 1729`, after clip; cap $3, tag `v4B_d3_` | `docs/revisions/v4/plans/plate_d3.md`, `media/reviews/v4/B/0026_plate.mp4`, D3 entry of `render/timeline/A.js` |

Budget split of B's $90 (estimates for the planners to work inside): car $15, gunfire $25, co-op $30, Bean $10,
D3 plate $3, reserve $7.

v4-B itself: text fixes 1, 8, 9, 10.

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

## Jade's decisions (verbatim, with time)

None yet in this pane. Defaults from the brief: plates `TVA 1729` (hero), `TVA 4104`, `TVA 4096`, `TVA 0900`;
stamp `TIMELINE NOW CANON`; end credit yes, wording to confirm.

## Open questions

- End credit wording (draft in the brief).
