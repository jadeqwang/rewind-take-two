# Task for codex: render the v4 preview of the whole film (540p)

Jade asked for a check render of the whole cut after the v4 revision pass (instances v4-A and v4-B). This is a
mechanical job: render, verify and report. Don't change creative content.

## Render

From the repo root, `/home/jade/Documents/rewind-take-two`:

```
df -h .      # stop and report if under 8 GB free
node render/engine/render.mjs --preview --force \
  --audio media/sfx/Rewind_cinematic_sfx_mix.mp3 \
  --out deliverables/wip/rewind_roughcut_v4_preview.mp4
```

- `--preview` is 960×540. **Do not render 1080p.** Jade wants check renders below 1080p.
- `--force` is required: shot media was replaced under the same paths during the revision pass, and cached frames
  are not invalidated by that.
- Audio: `media/sfx/Rewind_cinematic_sfx_mix.mp3` is the current sound build (rebuilt during v4). Use it as is;
  don't rebuild it.
- Leave `deliverables/wip/rewind_roughcut_v3_preview.mp4` where it is: Jade compares the two.
- Expect it to take several minutes. Run it in the foreground or poll it until it finishes.

## Rules

- Don't edit anything under `render/`, `media/shots/`, `media/sfx/`, `media/sing/`, `tools/` or `docs/` except
  your report.
- Don't delete anything. If the disk fills up, stop and report.
- If the render fails, read the error, retry once if it is transient (a lost WebGL context, or a worker crash), and
  otherwise stop and report the exact error. Don't patch timelines to make it pass.
- If the log says a worker fell back to egl or cpu, re-run with `--force` once so the backends don't mix.
- No git commits (the mp4 is gitignored anyway).

## Verify

1. Probe the output (there is no ffprobe; use PyAV: `~/Documents/moongazing/.venv/bin/python -c "import av; ..."`):
   960×540, 24 fps, duration about 227.96 s (within 0.1 s), one video and one audio stream.
2. Make a contact sheet of one frame every 4 s at `deliverables/wip/rewind_roughcut_v4_preview_sheet.jpg`
   (ffmpeg is `~/Documents/moongazing/.venv/bin/ffmpeg`), and look at it for black frames, grey "slate" placeholders
   (an uncovered range shows a slate with the section name), or obviously broken frames. Note the timestamps of any
   you find. Black is expected only at 222.78–226.00 (the ring-out) and behind the end text after 226.00.
3. Spot-check these v4 changes by pulling single frames (ffmpeg `-ss <t>`) and looking at them:
   9.5 (REWIND with a legible "jade wang"), 12.62 (the whole Bean, Jade small at the bottom), 27.0 (TVA 1729 on the
   car in the mirror), 90.5 (over her shoulder at the wheel, SIRENS on a sign), 92.5 (TVA plates in the rear-view
   mirror), 99.4 (agents from behind on the lawn, HILBERT HOTEL), 103.0 (earpiece close-up), 131.0 (two Jades, one
   blue, one orange, and a pencil bridge), 214.6 (ANOMALY REPORT), 217.7 (TIMELINE NOW CANON), 227.0 (end credits).
4. Check that the audio lines up: the first sung word should land where `analysis/cinematic/timing.json` says.

## Report

Write `docs/revisions/render_v4_preview_report.md` with the command you ran, the wall time, the file size, the
probe summary, any warnings or backend fallbacks, the spot-check results, and any suspect timestamps. Then print
`DONE` or `FAILED: <reason>` as your last line.
