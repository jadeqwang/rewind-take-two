# AI-error audit of v8: resume notes (2026-10-15)

Task (Jade): frame-by-frame audit of `deliverables/rewind_v8_master_1080p_sfx.mp4` for impossible things that read as
unintentional AI errors (not intentional surrealism), incl. the passenger-seat shot. LIST ONLY, no fixes this round.
Final output: `docs/revisions/v9/ai_error_audit.md` (merged, deduped, ranked).

- Contact sheets of every frame (16/sheet, 367 sheets, labelled f#/time/shot): built by `sheets.py` here into
  the session scratchpad (`.../scratchpad/sheets/`, may be gone; rebuild: ~3.5 min,
  `~/Documents/1-music-shipped/moongazing/.venv/bin/python -I sheets.py <master> shots.txt <outdir>`).
- 8 reviewers, 46 sheets each: part_k covers sheets 46k..46k+45. A part is complete when its file ends with `DONE:`.
  Incomplete parts carry a `PROGRESS: last sheet reviewed = ...` line; resume from the next sheet.
- ffmpeg: `~/Documents/1-music-shipped/moongazing/.venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2`;
  grab frame N exactly with `-ss (N-0.5)/24`.
- Status: all 8 parts DONE; merged into ai_error_audit.md (copies here are snapshots; the live
  files are in the scratchpad `findings/`).
- Known headline items: 3 legs = G3 2:26.33-2:26.75 (f3512-f3522); passenger seat = C10_V2b3 1:06.29-1:07.16;
  D3 impossible side mirror 0:25.34-0:28.40; V2f car rear-view mirror floats outside the car 1:29.29-1:31.46.
