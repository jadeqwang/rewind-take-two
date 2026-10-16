# v9 fix round: shared brief for fix agents (2026-10-15)

Jade's spec is the **Headliners** table at the top of `docs/revisions/v9/ai_error_audit.md`. Only those nine items are
in scope this round. Where Jade's wording differs from the per-part reviewer notes further down, Jade wins: reviewers
were wrong at least twice (P2 marked fine; the F4 Bean reflection misdescribed) and Jade had to eyeball them. So look at
the frames yourself, and check every result against the canon shots by eye before you call it fixed.

## Already done by the lead (don't redo)
- #7 sprite blink: `render/three/lib/sprite.js` now wraps the frame index by clip length.
- #5 G3 three legs: `render/timeline/E.js` G3 in 2.05, rate 1.17.

## Canon (see `docs/director_brief.md`)
Jade: two crossed pencils in the bun, orange headphones round her neck, white cropped jacket with orange band, a
"1420 MHz" roundel on her LEFT sleeve, a pale-blue dot on her LEFT chest, black crop top, navy cargo trousers with orange
straps. Her car: a white Acura sedan, left-hand drive, Jade in the LEFT (driver) seat with the wheel in front of her.
The engraved look (fine hatching + coloured pencil) comes from the engrave pass (`tools/engrave/README.md`).

## Tools
- Read `docs/TOOLS.md` first (generation how-to). Its paths to `~/Documents/moongazing` are stale:
  - Python: `~/Documents/1-music-shipped/moongazing/.venv/bin/python` (`PY`)
  - ffmpeg: `~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2`
    (no drawtext; no ffprobe — use PyAV)
- The current master is `deliverables/rewind_v8_master_1080p_sfx.mp4` (24 fps). Grab exact frames with
  `-vf select=eq(n\,N)` or `-ss (N-0.5)/24`; plain `-ss t` grabs can land on the wrong shot.
- How earlier fixes were made: `docs/revisions/v5`, `v6`, `v7` (e.g. `tools/matte_fix.py`, `tools/sectionE/patchfix.py`,
  `tools/c4_pencils.py`, `tools/jacket_back.py`). Shot sources and in-points are in `render/timeline/*.js`.

## Rules
- Budget: spend is $252.72 of the $400 cap. Each agent has its own cap (in its prompt). Run `$PY tools/gen/spend.py`
  before and after; use `--dry-run` first. Tag every paid call `v9_<item>`.
- Repo is public: no secrets; media stays in gitignored `media/`. Don't commit or push.
- **Don't run `render/engine/render.mjs`** (concurrent renders collide; `--range` ignores `--outdir`). Verify on your
  own clips and stills; the lead does the integrated preview render.
- **Don't edit `render/timeline/*.js`** (several agents share those files). Write new source files under
  `media/shots/<shot>/` with new filenames (the engine caches by path), and put the exact timeline change in your report.
- Review stills at reduced size; no 1080p renders.
- Report to `docs/revisions/v9/fix_<item>.md`: what was wrong, what you made (paths), the exact timeline change,
  before/after evidence images (small jpgs next to the report), spend, and anything still imperfect. Write the report
  progressively so it survives if you're interrupted.
