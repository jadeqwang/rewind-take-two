# v4 whole-film 540p preview render report

## Status: DONE (re-run by v4-B, 2026-10-11 19:12–19:15 CDT)

Codex's attempt (below) failed because its sandbox denies the engine's localhost server. v4-B ran the same command
from its own shell:

```sh
node render/engine/render.mjs --preview --force \
  --audio media/sfx/Rewind_cinematic_sfx_mix.mp3 \
  --out deliverables/wip/rewind_roughcut_v4_preview.mp4
```

- Wall time about 2 min (5471 frames in 111.9 s = 48.9 fps, encode 8.9 s). No backend fallback or lost context in
  the log (`deliverables/wip/rewind_roughcut_v4_preview_render.log`).
- Output: `deliverables/wip/rewind_roughcut_v4_preview.mp4`, 157,009,227 bytes; 960×540, 24 fps, 227.958 s; one video
  and one audio stream (AAC 48 kHz, from the SFX mix).
- Contact sheet (one frame every 4 s): `deliverables/wip/rewind_roughcut_v4_preview_sheet.jpg`. No slates, no
  unexpected black frames; black only on the ring-out (222.78–226.00) and behind the end text.
- Spot checks, all as intended: 9.5 legible "jade wang"; 12.62 the whole Bean, her small at the bottom; 27.0 TVA 1729
  in the wing mirror; 90.5 over her shoulder at the wheel, woodcut SIRENS; 92.5 TVA 1729 / 4104 / 4096 in the
  rear-view mirror, IN MY MIRROR; 99.4 agents from behind, HILBERT HOTEL, I ZIGZAG; 103.0 earpiece close-up; 120.0 the
  reversed climb with "Rewind." on the wall; 131.0 BLUE and ORANGE at the hinged pencil bridge; 214.6 ANOMALY REPORT;
  217.7 TIMELINE NOW CANON; 227.0 the two credit blocks, "never stop." and the counter.
- Audio sync not re-measured separately: the mix is the one every v4 review clip used, encoded from 0.000 s.

DONE

---

## Codex's attempt (FAILED)


Status: **FAILED** — the execution environment denied the renderer's local HTTP server bind (`listen EPERM: operation not permitted 127.0.0.1`). No v4 preview was produced.

## Render attempt

Run from `/home/jade/Documents/rewind-take-two`:

```sh
df -h .
node render/engine/render.mjs --preview --force \
  --audio media/sfx/Rewind_cinematic_sfx_mix.mp3 \
  --out deliverables/wip/rewind_roughcut_v4_preview.mp4
```

- Initial disk availability: **18 GB**, above the required 8 GB minimum.
- Started: **2026-10-12 00:11:22.547044 UTC** (2026-10-11 19:11:22 CDT).
- Finished: **2026-10-12 00:11:22.748880 UTC**.
- Wall time: **0.202 seconds**, process launch through exit.
- Exit code: **1**.
- Requested mode: forced 960×540 preview with the existing rebuilt v4 SFX mix; no audio rebuild was attempted.
- v4 MP4 file size: **unavailable**; `deliverables/wip/rewind_roughcut_v4_preview.mp4` does not exist.
- v3 preview remains at `deliverables/wip/rewind_roughcut_v3_preview.mp4`; its size (157,448,051 bytes) and modification timestamp were unchanged across the attempt.
- [Captured render log](../../deliverables/wip/rewind_roughcut_v4_preview_render.log).
- [Attempt metrics](../../deliverables/wip/rewind_roughcut_v4_preview_render_metrics.json).

## Exact error, warnings, and backends

```text
node:events:497
      throw er; // Unhandled 'error' event
      ^

Error: listen EPERM: operation not permitted 127.0.0.1
    at Server.setupListenHandle [as _listen2] (node:net:1919:21)
    at listenInCluster (node:net:1998:12)
    at node:net:2207:7
    at process.processTicksAndRejections (node:internal/process/task_queues:89:21)
Emitted 'error' event on Server instance at:
    at emitErrorNT (node:net:1977:8)
    at process.processTicksAndRejections (node:internal/process/task_queues:89:21) {
  code: 'EPERM',
  errno: -1,
  syscall: 'listen',
  address: '127.0.0.1'
}

Node.js v22.23.2
```

No backend fallback or other render warning was logged before the error. No retry was made: a denied server bind is not a transient lost WebGL context or worker crash. The task instructions require stopping and reporting a non-transient failure.

## Verification

The requested checks could not run because the v4 MP4 was not produced:

| Required check | Result |
| --- | --- |
| PyAV probe: 960×540, 24 fps, 227.96 ± 0.1 s, one video and one audio stream | Not verified; no output file |
| Four-second contact sheet and visual inspection | Not generated; no output file |
| 9.5 s: REWIND and legible “jade wang” | Not assessed |
| 12.62 s: whole Bean, Jade small at bottom | Not assessed |
| 27.0 s: TVA 1729 in mirror | Not assessed |
| 90.5 s: over-shoulder wheel shot and SIRENS sign | Not assessed |
| 92.5 s: TVA plates in rear-view mirror | Not assessed |
| 99.4 s: agents from behind on lawn, HILBERT HOTEL | Not assessed |
| 103.0 s: earpiece close-up | Not assessed |
| 131.0 s: blue/orange Jades and pencil bridge | Not assessed |
| 214.6 s: ANOMALY REPORT | Not assessed |
| 217.7 s: TIMELINE NOW CANON | Not assessed |
| 227.0 s: end credits | Not assessed |
| First sung word aligned with `analysis/cinematic/timing.json` | Not verified; no output audio |

Suspect timestamps: **not assessed**; no v4 preview frames were available. No claim is made that the visual or audio checks passed.

No creative content or source files were edited, no manual deletions were performed, and no git commit was made.

FAILED: renderer local-server bind denied (listen EPERM: operation not permitted 127.0.0.1); v4 preview not produced or verified.
