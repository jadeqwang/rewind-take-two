# v5 final render: 100 MB encode and verification (codex brief)

Jade signed off v5 on 2026-10-12 and asked for the final render "including a 100MB version". Claude rendered the
1080p master itself (codex's sandbox cannot run `render.mjs`). **Do not run `render/engine/render.mjs`.** Your job is
the boring part: the 100 MB encode and the checks, from files already on disk.

## Inputs (read-only; do not modify or delete)

- Master: `deliverables/rewind_v5_master_1080p_sfx.mp4`, 1920×1080, 24 fps, x264 CRF 16, AAC 320k, 244.05 s.
- Mix: `media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3` (244.050 s, 48 kHz stereo).
- Render log: `deliverables/wip/rewind_v5_master_render.log`.
- Tools: `docs/TOOLS.md`. There is no system ffmpeg or ffprobe: use `~/Documents/moongazing/.venv/bin/ffmpeg`, and PyAV
  through `~/Documents/moongazing/.venv/bin/python` for probing.

## Tasks

1. **Disk first.** `df -h .`; stop and report if under 2 GB free.
2. **100 MB version:** `deliverables/rewind_v5_upload_1080p_sfx_100MB.mp4`. The file must be **≤ 100,000,000 bytes**,
   and should land as close as possible under it (aim for 95–99 MB).
   - 1920×1080, 24 fps, H.264 High, yuv420p, `-movflags +faststart`. Two-pass x264 `-preset slow` at the target
     video bitrate.
   - Audio: AAC 192k, 48 kHz stereo, taken from the master's audio stream (not re-mixed).
   - Budget: 244.05 s; total ≈ 0.97 × 800 Mbit / 244.05 s ≈ 3.18 Mb/s, so video ≈ 2.98 Mb/s after audio and
     container overhead. If the first result is over 100,000,000 bytes, lower the video bitrate and redo it. Keep
     the 1080p frame size; do not downscale.
3. **Verify both files** (master and 100 MB):
   - Probe: frame size, fps, duration (244.05 ± 0.05 s), frame count (5857 ± 1), one video and one audio stream,
     codecs and bitrates, byte size.
   - Full decode of every frame with no errors (`ffmpeg -v error -i X -f null -`).
   - Audio matches the mix: correlate the decoded audio of each file against
     `media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3` (mono, 8 kHz is fine) and report the offset in ms (should be
     within ±20 ms) and the correlation.
   - Black-frame scan (`blackdetect`) with times. Expected black only on the credits background (about
     222.8–232.8 s, where there is text on black) and nowhere else.
   - Contact sheet of the master, one frame every 4 s, at `deliverables/wip/rewind_v5_master_sheet.jpg`. Look at it
     and list any frame that looks wrong (a slate, a missing layer, a blank or glitched frame).
   - Spot checks, compared visually with the 100 MB file at the same times: 13.9 s (Penrose stair on the rooftop,
     lower left), 21.8 s (woodcut LAKE SHORE DR / SOUTH signs), 51.6 s (A SHADOW / CHASING billboard behind
     REWIND), 204.0 s (orange and blue triangle pieces merging), 233.9 s (gloved hand pressing the brass plate,
     ITERATION 4,113 readable), 236.5 s (open ledger with names), 243.5 s (the lobby queue with the FRONT DESK text
     box). Save these 7 frames from both files side by side in `deliverables/wip/rewind_v5_spotchecks/`, and say
     whether the 100 MB file shows visible blocking or banding anywhere, especially in the rewind (42–57 s), the
     ghost-heavy shots (94–98 s and 134–138 s), and the colour gradients of the lobby.
4. **Report:** write `docs/revisions/render_v5_final_report.md`: the commands you ran, the results of every check
   above, byte sizes, and any problem. End with a line `DONE` or `FAILED: <reason>`.

## Rules

- Write only the 100 MB file, the files under `deliverables/wip/`, and the report.
- Do not edit, move or delete any other file; no git commands.
- If something fails in a way that a retry won't fix, stop and write it up in the report.

## Task 5 (added after your report): a 720p 100 MB alternative

The 93.00–93.08 s black is the authored cut before "Reload." (`C_V2g_black`), so it is expected; my brief missed it.
Thanks for flagging it. New task, same rules:

1. Encode `deliverables/rewind_v5_upload_720p_sfx_100MB.mp4` from the master: 1280×720 (lanczos scale), 24 fps,
   H.264 High, yuv420p, two-pass x264 `-preset slow`, the same video bitrate as the 1080p 100 MB file (2,980k), AAC 192k
   from the master's audio, `+faststart`, ≤ 100,000,000 bytes.
2. Probe it, decode every frame, and check audio alignment as before.
3. Compare it with the 1080p 100 MB file at 51.6, 96.5, 136.5, 204.0, 234.5 and 243.5 s. Upscale the 720p frame to
   1080p (lanczos) for a fair side-by-side. Save the pairs in `deliverables/wip/rewind_v5_spotchecks/720_vs_1080/`,
   and say plainly which one looks better at normal viewing size, and where.
4. Append a "Task 5" section to `docs/revisions/render_v5_final_report.md`, ending with `DONE-5` or `FAILED-5: <reason>`.
