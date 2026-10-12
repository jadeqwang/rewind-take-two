# REWIND v5 revision pass: shared ground rules (2026-10-12)

Jade reviewed the v4 whole-film preview, `deliverables/wip/rewind_roughcut_v4_preview.mp4` (960×540, 227.958 s;
contact sheet `deliverables/wip/rewind_roughcut_v4_preview_sheet.jpg`). **All timestamps in her notes are v4
preview timecodes.** Her opening line: "It's looking really good!"

## Jade's notes, verbatim

> * 0:13 & 2:35 - left of singer, make that rooftop staircase an actual impossible staircase
> * 0:22 - highway signs, add woodcut texture
> * 0:50 - during rewind, lyrics on billboards and highway signs
> * 3:23 - maybe it makes sense for blue and orange variants to merge here and we just demonstrate that she can
>   un-banach-tarski herself into becoming original her
>
> * credits sound fades out gradually as the life count ticks up in the corner
> * post credits scene: checking into the Hilbert Hotel
>   * emblem on the door (POV, Jade entering), a gloved hand opens the door, a slight ringing sound (of a door
>     opening)
>   * cut to POV receptionist, looks up from desk and see an infinite line of Jades, led by protagonist Jade (a
>     committee of Jades from reference art, multi-colored ghosts from the video, etc), (no audible spoken words),
>     text box (styled like at 0:37 early in video)
>   * Receptionist: Of course we have space for you.
>
> other notes:
> * sedans are fine
> * keep these car shots

The last two settle v4-B's open questions (the grey mirror sedans with light bars; the car shots at 88.38–92.79,
`CAR_START = 89.26`). **Do not touch the car shots.**

## What each note points at (v4 timeline, `node render/engine/render.mjs --list`)

| Note | Shots | Where it lives |
|---|---|---|
| 0:13 & 2:35 staircase | S1 12.60–16.14 (+S1x to 19.64), V3S 153.98–157.39, V3S_b 157.84–159.14 | `render/timeline/A.js` (S1), `render/timeline/E.js` (V3S); the stair is in the plate behind her (`media/sing/plates/`, `media/shots/S1_wide/`) |
| 0:22 highway signs | D1 21.38–23.16 (LAKE SHORE DR / SOUTH gantry) | `render/timeline/A.js`; woodcut lettering module `tools/sectionA/modules/woodcut.js` (v4-B used it for SIRENS) |
| 0:50 rewind lyrics | the rewind run R2_01–R4, 42.65–56.54 (blank billboard in R4 at ~52) | `render/timeline/A.js`, `render/timeline/A_R2.js` |
| 3:23 merge | F7_07 203.76–205.52 (the two-figure light burst; corrected by v5-merge), with F7_06 202.88–203.76 before it | section F timeline (find it with `grep -l F7_06 render/timeline/*.js tools/sectionF -r`); blue/orange variants are from the 2:00 co-op (`media/shots/C_coop/`, `docs/revisions/v4/plans/coop.md`) |
| credits fade + counter | O3_black 222.78–226.00, O4 226.00–227.96, O_credit 223.23–227.96 | `tools/sectionF/modules/end_credit.js`, the hud counter in O4, the mix `tools/sfx/build.py` → `media/sfx/Rewind_cinematic_sfx_mix.mp3` |
| post-credits Hilbert Hotel | new, after the credits (past 227.96) | new; text box = the `dialogue` module used by `A_dialogue` at 33.6–37.96 in `render/timeline/A.js` |

## Workstreams (Opus sub-agents of the v5 setup session)

| Name | Notes | Mode | Soft cap, tag | Plan / progress file |
|---|---|---|---|---|
| `v5-stairs` | 0:13 & 2:35 | execute through to an after clip | $6, `v5_stairs_` | `docs/revisions/v5/stairs.md` |
| `v5-signs` | 0:22, 0:50 | execute through to after clips | $4, `v5_signs_` | `docs/revisions/v5/signs.md` |
| `v5-merge` | 3:23 | **plan + candidate stills/previz, then stop for Jade's sign-off** | $3 before sign-off, `v5_merge_` | `docs/revisions/v5/merge.md` |
| `v5-coda` | credits fade, post-credits scene | **plan + candidate stills/previz, then stop for Jade's sign-off** (the audio fade alone may be executed) | $5 before sign-off, `v5_coda_` | `docs/revisions/v5/coda.md` |

Spend before this pass: **$243.44 of $400** (`python3 tools/gen/spend.py`).

## Rules (the v3/v4 rules still apply: `docs/revisions/README.md`, `docs/revisions/v4/README.md`)

- **Save to disk as you go.** Keep your plan/progress file current (done, running, next, decisions, open
  questions) so a fresh session can resume from it after a usage-limit stop. Candidate stills sit beside their
  prompts, seeds and model names.
- **New takes beside old ones**; point the timeline at the new file. Never overwrite or delete a v4 take.
- **Shared timeline files:** re-read right before editing, edit only your own shot rows/overlays with exact-string
  edits. `A.js` is shared by `v5-stairs` (S1 plate only) and `v5-signs` (D1, R2–R4 only). Nobody else edits
  `render/engine/**`, `analysis/cinematic/timing.json`, or the car shots.
- **Renders:** 540p ranges only (`--range a b --preview --encode`). Changes under `tools/` are not in the frame
  cache fingerprint: pass `--force`. No whole-film render and no 1080p. Check `df -h .` first (14 GB free at
  start). Codex cannot run `render.mjs` (sandbox); render from your own shell.
- **Canon:** cuts on the tracked beats in `analysis/cinematic/timing.json`; no red; no head shots; the agency is
  `TIME VARIANCE █████████`, "Authority" never appears; `TVA` only on licence plates. Watercolor/engraved Jade canon
  in `docs/revisions/A_streams.md` (pencils, hair, jacket, patch).
- **No commits by sub-agents.** The setup session commits by path.
- **Hand-over:** a 540p after clip (<10 MB, with its audio slice) in `media/reviews/v5/`, and a fragment
  `docs/revisions/v5/fragments/<name>.json`: a list of `{note, v4_time, shots, status, after, before_range,
  what_changed, question}`.

## Round 2: Jade's answers (2026-10-12), verbatim

> * signs look good, merge looks good
> * staircase looks bad, because it's not an actual impossible staircase. can you just copy the one from later in
>   the same video? the one inside the clock at 3:13?
>
> coda:
> * infinite Jades, I just added "committee_v3_long_ponytails_ff.png" to /inputs which is from the previous version
>   of the Rewind video. I thought it would be fun to have glasses Jade right after protagonist Jade, followed by
>   teal tips, purple, braids, etc., and then the colorful ghosts and 8bit Jade, etc.
> * hotel door should open in the correct way
> * I think the ledger should be full (should it be video game characters? mathematicians? artists whose work are
>   visually referenced in the video? or kept illegible?)
> * I kinda like this part in full color

Setup-session calls where Jade left it open: signs stay as built (light-on-dark faces, no extra rewind lettering);
merge is option A exactly as previewed (F7_06 dropped, hair down, piece count as is); credits fade stays as built;
text box tab stays FRONT DESK; no queue-shuffle gag. Ledger: **full, legible at a glance, the artists and
mathematicians whose work the film quotes** (the Hilbert joke: the book is full and there is still room). Video
game characters are out (public video, other people's IP).

| Name | Work | Cap, tag | File |
|---|---|---|---|
| `v5-stairs2` | replace the v5 stair with the 3:13 clock Penrose stair | $3, `v5_stairs2_` | `docs/revisions/v5/stairs.md` (append a Round 2 section) |
| `v5-build` | build merge option A, then the post-credits scene with Jade's notes | $10, `v5_build_` | `docs/revisions/v5/build.md` |

**Later, Jade, verbatim:** "i think the sound fade of the credits can build right into the coda, actually, so the
ticking up of the lives is followed by the hotel door ring". Sent to `v5-build`: no black gap between credits and
the door; the last counter tick is followed by the bell, on the same beat grid.

## Round 3: Jade on the v5 whole-film preview (2026-10-12), verbatim

> * almost the entire video looks great!
> * hilbert hotel opening: the arm stretches awkwardly in front of the camera and also doesn't interact with the
>   actual door handle in a realistic way. I'll leave you a choice here about which way you are confident we can do
>   better: (1) push a button on the side and the door opens automatically (2) a fullsized doorman in uniform behind
>   the door we can't quite see clearly because he's behind the door which obscures him somewhat
> * guestbook text should bend naturally with the page
> * all the Jade's should move slightly, whether that's a fidget, foot-tapping, breathing, adjusting jacket slightly,
>   head scratch, tucking hair behind ear, each one a little different and out of sync with the others, not bob up
>   and down like a cardboard cutout
> * give the rectangular-ish glasses to Jade #2 (the one currently with round glasses, and have the rest of her hair
>   be a bit fuller (you shouldn't see carpet through the gaps), but you can reduce the volume of the half-up
>   ponytails by about 40%, which is what it looks like in real life, and then you'd be able to see the purple-haired
>   Jade behind her a bit better. Protagonist Jade should look the same as she does in the video, without the
>   glasses.
> * you can have the whole front desk sentence render at once or at least faster, for faster readers.

Setup-session call on the door: **option 1** (button; the door swings itself on its existing correct hinge).
Only the post-credits scene changes. Work: `v5-coda2`, cap $15, tag `v5_coda2_`, log `docs/revisions/v5/coda2.md`.

## Round 4: Jade on the push-plate door (2026-10-12), verbatim

> * the brass button looks like a doorbell rather than a square plate you'd expect as a mechanism. I'd naively expect
>   the brass button to be a little bit lower, placed facing into the entrance the way you'd see an ADA compliant
>   button to be, just, made of brass instead of the usual stainless steel square plate button
> * probably makes sense for the doorman to be physically offscreen to the right so as to not be in the way of the
>   guest

Sent to `v5-coda2` (resumed). Setup-session call: the plate carries the engraved accessibility symbol, so it reads
as an automatic-door opener at a glance.
