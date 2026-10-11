# REWIND v3 revision pass: shared ground rules (2026-10-11)

Jade reviewed the v2 cut (`deliverables/rewind_v2_upload_1080p_sfx.mp4`, 540p copy in
`deliverables/wip/rewind_roughcut_v2_preview.mp4`). All timestamps in her notes are v2 timecodes.
Two instances revise in parallel; a third renders afterwards.

| Instance | Scope | Brief |
|---|---|---|
| **A** | Everything outside the chase: 0:00–1:34 and 2:21–end | `docs/revisions/A.md` |
| **B** | The main chase sequence only: 1:34–2:21 (94.06–141.00 s, shots V2i–V2n and E1–E8) | `docs/revisions/B.md` |
| Render | Final 1080p render, after Jade has reviewed the clips | not started yet |

Background reading, in this order: `docs/MORNING.md`, `docs/treatment.md`, `docs/shotlist.md`, then the section
write-up for your shots (`docs/sections/*.md`), `docs/TOOLS.md`, `render/engine/README.md`.

## Who you can talk to

- **Jade** types into your tmux pane directly (session `rewind-rev`, A on the left, B on the right).
- **The other instance:** use `ListAgents` to find it, then `SendMessage`. The sessions were started with the names
  `rev-A` and `rev-B`. If the listing shows a different name, use what the listing shows.
- **Fallback** if `SendMessage` is unavailable: `tools/streams/tell A "…"` or `tools/streams/tell B "…"` types the
  message into the other pane. Use it sparingly, because it lands in the middle of whatever Jade is typing there.
- **Setup session** (`rewind-take-two-dc`, outside tmux): wrote these briefs. Message it if the setup itself is wrong.

Message the other instance when you touch anything shared, when you change something it depends on (a character
detail, a prop, a typeface, a cut point at 94.06 or 141.00), or when you need its shots to match yours. Keep
messages short and say which file or shot you mean.

## Working in one tree without collisions

Both instances work in the same checkout. `media/` and `work/` are gitignored, so git will not save you there.

- **Own your shots.** Only regenerate, re-edit or re-cut shots inside your scope.
- **Shared files** need a heads-up before you edit them, and you should re-read them right before editing:
  - `render/timeline/C.js` holds Verse 2. A owns V2a–V2h (up to 94.06 s), B owns V2i–V2n. Edit only your own shot
    entries.
  - `render/timeline.js`, `render/engine/**`, `render/fonts/`, `analysis/cinematic/timing.json`, `docs/shotlist.md`,
    `docs/treatment.md`, `media/sfx/**` and `tools/sfx/**`.
  - `render/timeline/D.js` is generated from `tools/sections/D/build_timeline.py` and `media/shots/_D/takes.json`.
    It is B's.
- **New takes go beside old ones.** Don't overwrite or delete a v2 take; add a new take and point the timeline at it,
  so Jade can compare before and after.
- **Git:** commit only the paths you changed, by name. No `git add -A`, no pushes, no history rewriting unless Jade
  asks. The repo is public: no secrets. `inputs/jade_watercolor*.png` are new and untracked; leave them uncommitted
  unless Jade says to add them.

## Constraints

- **Disk is nearly full:** about 3.8 GB free at 12:00. Check `df -h .` before generating or rendering.
  `media/engine_cache/` (19 GB) and `render/engine/out/` (3 GB) are regenerable, but ask Jade before clearing either,
  because the other instance and the final render use them too.
- **Spend:** about $156 of the $400 cap was used by v2 (`tools/gen/spend.py`). Treat $100 per instance as a soft
  limit for this pass, tag your calls so the two streams can be told apart, and check with Jade before going past it.
- **No full render.** Preview only your own ranges (`node render/engine/render.mjs --range … --preview --encode`).
  The 1080p render waits for Jade's review.
- **Check renders are smaller than 1080p** (Jade, 2026-10-11, to rev-A: "when we render for me to check, we can do
  it at smaller than 1080p because we might make more changes anyway"). A whole-cut render for her to check uses
  `--preview` (960×540). 1080p is only for the cut she has signed off. `media/engine_cache/full` was cleared at
  12:45 with her approval, so a 1080p render re-extracts its frames first.
- **Canon stays canon:** every cut stays on the tracked beats in `analysis/cinematic/timing.json`; never write
  "Authority", "TVA" or Marvel terms; no red; no head shots.

## What you hand over: clips for the review artifact

Jade reviews the revised clips in an artifact before the final render. For every note in your brief, produce:

1. A short **after** clip with its audio slice: 540p H.264, under 10 MB, in `media/reviews/v3/<A|B>/`.
2. An entry in `docs/revisions/review_<A|B>.json`, a list of objects:

```json
{
  "note": "Jade's note, verbatim",
  "v2_time": "0:29",
  "shots": ["D4"],
  "status": "done | partial | blocked | question",
  "after": "media/reviews/v3/A/0029_pulled_over.mp4",
  "before_range": [28.5, 31.0],
  "what_changed": "One or two sentences on what you did and anything you could not fix.",
  "question": "Only if you need Jade to decide something."
}
```

Keep the manifest current as you go, so the artifact can be built from it at any point. If a note needs a decision
from Jade, ask her in your pane as soon as you know, and carry on with the rest.
