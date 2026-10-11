# REWIND (cinematic edition): morning handoff, 2026-10-11

## Watch this first

These files are local only and gitignored:

| File | What it is |
|---|---|
| `deliverables/rewind_v2_upload_1080p_sfx.mp4` | **Upload copy.** 1080p24, about 14.5 Mb/s, 415 MB, with the sound-design mix |
| `deliverables/rewind_v2_upload_1080p_original_audio.mp4` | The same picture with the untouched original track |
| `deliverables/rewind_v2_master_1080p_sfx.mp4` | Master, CRF 18, 1.6 GB, for archiving or re-editing |
| `deliverables/wip/rewind_roughcut_v2_preview.mp4` | 540p preview of the same cut |
| `deliverables/wip/rewind_roughcut_v1_preview.mp4` | The first rough cut, before the review fixes |

- **Length:** 3:47.96. Every cut is locked to the tracked beats.
- **Audio:** the SFX mix (`media/sfx/Rewind_cinematic_sfx_mix.mp3`) leaves the original track bit-identical, with cues only in the gaps, at the same loudness of −15.8 LUFS.
- **New mp3:** you asked for a new mp3 if the sound changed. It's `media/sfx/Rewind_cinematic_sfx_mix.mp3`.

## The idea, in one line

The world is a drawing (Escher-style engraved Chicago) and Jade is the only thing in colour. Colour is the residue the Time Variance █████████ tracks her by, until she pulls the pencil from her hair and redraws the map. Once everything is in colour, "it couldn't trace" her. The full treatment is in `docs/treatment.md`, and the bar-locked shot list is in `docs/shotlist.md`.

## How it was made

- **Pipeline:** keyframes from Cloudflare image models, then Seedance video, then `tools/engrave`, a post-pass that keeps the world engraved and only Jade in colour. Shots are composited in the deterministic engine `render/engine` (headless three.js, frame-exact to `analysis/cinematic/timing.json`).
- **Sections:** each section has its own write-up (`docs/sections/A.md`, `C.md`, `D.md`, `E.md`, `F.md`), with chosen takes, what differs from the shot list and why, and what's weak.
- **Review:** a critic pass on v1, which used Gemini as a second opinion, is in `docs/reviews/roughcut_v1.md`. Its whole top-10 list was fixed for v2:
  - Jade's blank face in V2m.
  - The colour spoiler in the opening teaser.
  - Ghosts redrawn as line-art Jades.
  - Unreadable lyrics.
  - Red removed everywhere.
  - The singing shots tightened and given orange headphones and pencil grain.
  - The pause menu.
  - Continuity: the car, the skyline and P1.
  - The sag in the final drop.

## Choices for you

1. **Audio:** the SFX mix or the original track. There's an upload copy of each.
2. **Headphones in the singing shots:** the film uses canon orange, but your real ones are pale pink. The pink versions are kept next to each clip as `media/sing/*/take_*_lips_orig.mp4`.
3. **Lip-sync offset:** the variants are in `media/sing/review/` (A/B/C at ±0.15 s). Current lags are S1 +1.04, E3 +0.75 and V3S −0.12.
4. **"…and time stops":** it's now a small whisper line under the pause menu (41 s) and the CONTINUE? panel (111.6 s). Remove it if the menus say enough on their own.

## Known weak spots (v2)

- **E2 (about 116 s):** the first frozen ghosts are still soft colour shapes. The E2c ring and everything later read as Jades. E4's ghost stream still uses the older tinted look.
- **P5/P6:** the freeze-frame negative is mid-grey rather than stark.
- **LOADING screen:** the tip text is small.
- **Skyline:** a faint Empire-State-like spire remains in the distant Grant Park skyline (E2b/E7) and late in E6b.
- **V2k:** a faint silhouette outline shows on the frozen frame-skip layer.
- **R2:** one death tableau has a Mercedes-like grille.
- **G1:** has no head turn.

## Spend

About **$156 of the $400 cap** (`tools/gen/spend.py`, list-price estimates), plus about $0.10 of Gemini review calls that the tool can't price.

## Re-rendering

```
node render/engine/render.mjs --preview --audio media/sfx/Rewind_cinematic_sfx_mix.mp3 --out deliverables/wip/x.mp4   # about 2 min
node render/engine/render.mjs --force --audio media/sfx/Rewind_cinematic_sfx_mix.mp3 --crf 18 --out deliverables/x.mp4  # about 7 min, needs about 5 GB free disk
```

Disk was nearly full at 08:00 (about 7 GB free). `render/engine/out/` and `media/engine_cache/` can be regenerated and are safe to clear.
