# v6 final render: 100 MB encodes and verification (codex brief)

Jade signed off v6 on 2026-10-12 (commit 512d6a7) and asked for the 1080p render. Claude is rendering the 1080p master
itself, because codex's sandbox cannot run `render.mjs`. **Do not run `render/engine/render.mjs`.** Your job is the encodes
and the checks, using files already on disk. Same shape as v5 (`docs/revisions/render_v5_final.md` and your report
`docs/revisions/render_v5_final_report.md`). Reuse your v5 commands.

## Wait for the master

The master is still rendering when you get this. Before you start, wait until
`deliverables/wip/rewind_v6_master_render.log` contains a line starting `[encode] done`; poll every 30 s, for up to
25 min. If the log shows an error and no `[encode] done`, stop and write that up.

## Inputs (read-only; do not modify or delete)

- Master: `deliverables/rewind_v6_master_1080p_sfx.mp4`: 1920×1080, 24 fps, x264 slow CRF 16, AAC 320k, 244.05 s.
- Mix: `media/sfx/Rewind_cinematic_sfx_mix_v5coda.mp3` (unchanged from v5).
- Render log: `deliverables/wip/rewind_v6_master_render.log`. Worker lines like `frame 57xx failed: ... image source is
  detached; restarting its browser` are known: the worker retries the frame. Check that the final `[render] N frames`
  line accounts for all 5857 frames.
- Tools: there's no system ffmpeg or ffprobe. Use `~/Documents/moongazing/.venv/bin/ffmpeg`, and PyAV via
  `~/Documents/moongazing/.venv/bin/python`.

## Tasks

1. **Disk first.** Run `df -h .` and stop and report if it's under 2 GB free.
2. **1080p 100 MB:** `deliverables/rewind_v6_upload_1080p_sfx_100MB.mp4`. Same recipe as v5: 1920×1080, 24 fps,
   H.264 High, yuv420p, two-pass x264 `-preset slow` at about 2,980k video, AAC 192k / 48 kHz stereo from the master's
   audio stream, `+faststart`. The file must be ≤ 100,000,000 bytes (aim for 95–99 MB). If it's over, lower the bitrate
   and redo it.
3. **720p 100 MB:** `deliverables/rewind_v6_upload_720p_sfx_100MB.mp4`. Same as v5 task 5: 1280×720 (lanczos), the same
   video bitrate as step 2, AAC 192k, `+faststart`, ≤ 100,000,000 bytes.
4. **Verify all three files** (master and both uploads):
   - Probe: size, fps, duration (244.05 ± 0.05 s), frame count (5857 ± 1), streams, codecs, bitrates, byte size.
   - Decode every frame with no errors.
   - Audio alignment against the mix: offset (within ±20 ms) and correlation.
   - `blackdetect` with times. Expected black: the authored 2-frame cut at 93.00–93.08 s (`C_V2g_black`, before
     "Reload."), and the credits on black (about 222.8–232.8 s). Nothing else.
   - A contact sheet of the master, one frame every 4 s: `deliverables/wip/rewind_v6_master_sheet.jpg`. Look at it and
     list any frame that looks wrong (a slate, a missing layer, a blank or glitched frame).
5. **Spot checks of today's fixes.** Grab these frames from the master and the 1080p 100 MB file side by side, and save
   them in `deliverables/wip/rewind_v6_spotchecks/`. For each, say whether it shows what's described:
   - 0.5 s: top left reads `ITERATION 4,095`.
   - 59.5 s: car interior, two pencils in her bun, one pink eraser and one pale-blue eraser.
   - 93.3 s: "Reload." screen, `×4,096` top right, tip `TIP: TVA agents can only follow what they can trace.`
   - 95.0 s: race HUD reads `GHOST: ITERATION 4,094`, and below it a clock (about `04:08`) with a split beside it.
   - 98.5 s: field HUD reads `ITERATION 4,097`, `×4,096` and a clock of about `04:11`.
   - 101.3 s: the notice board ("ACROSS THE …") stands well behind her; no floating elbow or see-through arm on any
     agent.
   - 103.5 s: earpiece close-up, she is small and far off toward the hotel.
   - 116.2 s: orange ghost beside her at the notice board, with no floating pistol hand.
   - 124.3 s: gold ghost beside her on the book, and the ghost's trousers are translucent next to her sneaker.
   - 133.0 s: co-op pencil bridge, with no oversized agent head.
   - 140.6 s: full-screen terminal `TVA ALERT` / `ANOMALY DETECTED.`
   - 145.2 s: pencil pull, with a blue dot on her left chest.
   - 175.0 s: running up the tower from behind; her jacket back is white with a large blue dot and no orange band.
   - 215.0 s: report box `TVA REPORT` / `ANOMALY DETECTED` / `CASE 4,098`.
   - 221.0 s: dissertation door, one blue and one pink eraser in the bun.
   - 233.9 s: `ITERATION 4,114` bottom right while the gloved hand presses the plate.
   Also say whether either 100 MB file shows visible blocking or banding, especially in 42–57 s, 94–98 s, 134–138 s and
   the lobby gradients. Say plainly which 100 MB file looks better at normal viewing size.
6. **Report:** write `docs/revisions/render_v6_final_report.md` with the commands, every result above, the byte sizes and
   any problem. End with a line `DONE` or `FAILED: <reason>`.

## Rules

- Write only the two upload files, files under `deliverables/wip/`, and the report.
- Don't edit, move or delete any other file, and run no git commands.
- If a failure won't be fixed by a retry, stop and write it up in the report.
