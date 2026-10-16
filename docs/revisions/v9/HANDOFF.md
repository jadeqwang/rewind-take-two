# v9 handoff (2026-10-16)

For the next instance. v9 is the fix round on the v8 AI-error audit. Its table of fixes is in `README.md` here. Nothing
in v9 is committed and there is no 1080p render yet. The last shipped cut is v8 (commit 04e3752,
`deliverables/rewind_v8_master_1080p_sfx.mp4`).

## Where things stand
- Every v9 item in `README.md` is wired into `render/timeline/*.js` and checked in 540p previews.
- **Latest work (2026-10-16): the D2/D3 door mirror, 0:23.16-0:28.40, round 7 plus a pencil fix.** Jade: "it looks
  much better" after round 7, then "this looks much better" after the pencils.
  - The mirror sits on its black sail at the window's front lower corner, as on a real 1999-2003 TL. The camera
    moved 23 cm forward in the passenger seat so the wheel doesn't hide it, and her plate was redrawn for that view.
  - The 3D cap is replaced by a drawn housing (ink outline, hatching), styled on the film's own TL mirrors at 0:28.6
    (D4) and 0:38.5 (P1).
  - The pencil bodies are yellow; only the erasers are pink / pale blue (`make_plate_r7.py` step 1b).
  - Write-up: "## Round 7" at the end of `fix_2_round3_threejs.md`. Evidence: `fix_2_r7_*.jpg`.
  - Rebuild: `bash tools/v9/d23/build_r7.sh` (about 80 s; `SKIP_PLATE=1` skips the plate steps). It writes
    `media/shots/D23/v9r7_engraved.mp4`, `r7_billmask_frames/` and `tools/v9/d23/d23_tracks_r7.js`, which A.js uses
    now. Round 6's files are untouched, for rollback.
- **The whole-film preview is stale.** `render/engine/out/rewind/rewind_preview.mp4` (08:36 on 10-16) predates round 7.
  Only `rewind_preview_23.00-28.58.mp4` has the new mirror. C2 (0:01.9-0:07.2) and R3 (0:51.3-0:52.3) replay this
  shot, so they change too.

## Next steps
1. Render a whole-film preview: `node render/engine/render.mjs --preview --force` (about 95 s). Check C2 and R3 by eye,
   then give it to Jade for a full watch.
2. On her sign-off, commit v9. The repo is PUBLIC: no secrets, and media stays in gitignored `media/`. Then ask before
   rendering 1080p.
3. The final render uses `--audio media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3 --crf 16 --preset slow`, then
   ONE 100 MB upload at 1080p (no 720p). Free about 9 GB first: frames are about 6.4 GB. Delete
   `render/engine/out/rewind/full/frames` afterwards.

## Open items Jade may raise (round 7)
- **Smaller lyric.** In the 0:24.5-0:25.3 two-shot the lyric in the glass is about 55 px wide at 540p (was about
  90), and she is cropped to her face at the left edge. The real mirror spot is lower and further from her face.
  Tightening `FOV_TWO` / `FOV_TWO_END` in `tools/v9/d23/rig_r7.js` enlarges it but crops her more.
- **Etch on the rim.** The "t" of "couldn't" rides on the glass rim at about 0:26.7-0:26.9.
- **"CHASING" hidden.** The sedan's roof covers it from about 0:26.4, as in rounds 4-6.
- **Plain sail.** It is a flat painted triangle, plainer than the hatched door around it.
- **Wavy road.** The road and park outside the window are CG through the engrave pass, so they read as wavy bands.
- **Erasers letterboxed.** The top letterbox bar hides the erasers at the 0:23.2 open; only the yellow pencil bodies show.
- **Older leftovers:** see "Known leftovers" in `README.md`.

## Gotchas
- **Set `FFMPEG` first.** Without it, `render.mjs` fails with an empty "cannot probe" error. Export
  `FFMPEG=~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2`.
  The `.venv/bin/ffmpeg` symlink is broken (it points at the old moongazing path). There is no ffprobe; use PyAV.
- **Always pass `--force`.** The frame cache reuses frames after module or clip changes.
- **The engine caches images by path.** A redrawn plate image needs a new filename. Videos are keyed by size and mtime.
- **`/tmp` is a 16 GB in-memory disk.** On 2026-10-16 Jade had the scratch folders of finished Rewind sessions cleared
  (it went from full to 8.2 GB free). Folders of still-running sessions were kept, among them `fdedb5e1` (2.5 GB). If
  headless Chrome logs FILE_ERROR_NO_SPACE again, check `/tmp/claude-1000/`.
- **Spend:** about $266.13 of the $400 cap. Log paid calls with `tools/gen/spend.py`.

## Working with Jade
- Before passing on any agent's visual verdict, look at the frames yourself. Reviewers have been wrong before
  (P2, F4).
- Give times as m:ss.xx, plus frame numbers if useful; she can't use bare frame numbers.
- Review renders are 540p (`--preview`). Render 1080p only for a signed-off cut.
- Mirror text reads forward (her cheat): "legible though, even though it should be reversed in real life."
- Canon: two crossed YELLOW pencils with pink and pale-blue erasers, orange headphones on her neck, white cropped
  jacket with orange band, "1420 MHz" roundel on her LEFT sleeve, navy trousers. White 2001 Acura TL, left-hand drive,
  Jade driving.
