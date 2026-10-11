# tools/engrave: the look-unifying filter

Chicago becomes a black-ink wood engraving on off-white paper. Jade (the matte) passes through in full colour.
This fixes the video models' drift: Seedance 2.0 keeps Jade in colour, but after ~0.5 s the engraved world slides into a soft gray-wash illustration.
The filter redraws every world frame from its tone and structure, so a whole clip looks like frame 0, or crisper.

Test outputs (gitignored) are in `media/engrave_tests/`:

| File | What |
|---|---|
| `ST_run_compare_src_vs_engraved.mp4` | Seedance source (left) next to the engraved 1080p output (right) |
| `ST_run_engraved_1080p_sbs.mp4` | 2×2 review grid: source, engraved, matte overlay, and a 1:1 centre crop |
| `ST_run_engraved_1080p.mp4`, `_2x.mp4`, `_native.mp4` | Outputs at 1882×1080, 1728×992 and 864×496 |
| `ST_run_bloom_demo_2x.mp4` | A growing `--bloom` mask showing colored-pencil residue in the world |
| `ST_run_matte_1080p/` | Matte PNG sequence plus `matte.mp4` |
| `engrave_stills_sheet.jpg` | Stills: source vs engraved for f0, f72 and f120, plate strengths 1 / 0.4 / auto, bloom, matte |
| `F_pencil_compare_sheet.jpg` | Phase 2: colour source / ink only / pencil + gold, old flat wash vs new strokes, gold sheen over time, 1:1 pencil crops, F1 flood frames, residue-palette bloom |
| `F_compare_src_ink_pencil.mp4` | Colour source, ink only and `--color pencil --gold auto` side by side (synthetic pan over the T3 keyframe) |
| `F1_flood_T1pan_1080p.mp4` (+`_sbs`) | A colour flood sweeping a clip via a `--bloom` PNG-sequence mask |
| `ST_run_residue_bloom_1080p.mp4` | The B&W Seedance clip with a growing `--bloom` mask and `--palette residue` |

## Setup

```bash
uv venv -p 3.12 tools/engrave/.venv
uv pip install -p tools/engrave/.venv/bin/python --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu124 -r tools/engrave/requirements.txt
PY=tools/engrave/.venv/bin/python
```

Weights download on first use:
- BiRefNet goes to the HF cache. Its revision is pinned because it loads remote code.
- Real-ESRGAN goes to `~/.cache/engrave`.

ffmpeg is taken from `$FFMPEG`, then `~/Documents/moongazing/.venv/bin/ffmpeg`, then `PATH`.

## Usage

```bash
# Video. For 480p Seedance sources, render at 1080p (or --upscale 2).
$PY tools/engrave/engrave.py IN.mp4 OUT.mp4 --out-height 1080 [--matte-out DIR] [--strength 0..1|auto] [--preview]

# Stills (one or many)
$PY tools/engrave/engrave_still.py IN.png -o OUT.png [--strength 0.4] [--side-by-side]
$PY tools/engrave/engrave_still.py a.png b.jpg -o OUTDIR/ --matte-out OUTDIR/
```

### Batch mode and the GPU lock

```bash
# clips.txt: one "IN OUT [per-clip flags]" per line, # comments allowed
#   media/gen/F2/take_1.mp4  media/F/F2_pencil.mp4  --color pencil --gold auto
#   media/gen/F1/take_2.mp4  media/F/F1_flood.mp4   --bloom work/F1_wipe/   # PNG dir
$PY tools/engrave/engrave.py --batch clips.txt --out-height 1080      # shared flags apply to every line
```

Batch mode loads BiRefNet and Real-ESRGAN once, then engraves the clips one after another. A clip that fails is reported and the rest still run.

Every `engrave.py` and `engrave_still.py` run takes a GPU slot first:
- The slots are flock locks in `~/.cache/engrave/locks/`. There are 2 by default; set `ENGRAVE_GPU_SLOTS` to change that.
- While both slots are busy, a job prints `[gpulock] all 2 GPU slots busy (pid … file …); waiting...` and polls every 2 s.
- The kernel drops a lock when its process dies, so a crashed job never leaves a stale slot.
- A batch holds one slot for its whole run.
- `--no-lock` skips the lock (only for debugging).
- In the test, two concurrent 1080p jobs each ran at about solo speed: one job does not saturate the 3090. Memory use is a few GB per job.

### Final-drop colour (section F)

```bash
# whole world in colored pencil over the engraving, colour from the source clip, Klimt gold leaf
$PY tools/engrave/engrave.py F5a.mp4 F5a_pencil.mp4 --out-height 1080 --color pencil --gold auto

# colour flood: an animated mask (video, PNG dir, 'dir/*.png' or 'dir/%05d.png'); white = coloured
$PY tools/engrave/engrave.py F1_color.mp4 F1_flood.mp4 --out-height 1080 --bloom work/F1_wipe/ --gold auto

# colour onto a B&W clip: from a palette gradient map, or from another (registered) colour clip
$PY tools/engrave/engrave.py bw.mp4 out.mp4 --bloom mask.mp4 --palette residue      # klimt | kandinsky | '#hex,...'
$PY tools/engrave/engrave.py bw.mp4 out.mp4 --bloom mask.mp4 --bloom-color color.mp4
```

- **`--color pencil`** keeps the same ink engraving and lays colored pencil under it:
  - **Layers:** three stroke layers at 0°, +22° and −34° to the hatch flow field. Where there is no structure, such as sky, they fall back to a hand-hatched −35° diagonal.
  - **Build-up:** pressure comes from the source chroma. Light colour is one sparse layer that skips the paper tooth; strong colour builds all three layers and fills the tooth. Neutral areas stay clean paper.
  - **Colour fidelity:** the pigment is solved so that strokes plus the paper between them average to the source colour. The source's own warm paper and its dark linework are removed first.
  - **Ink:** in coloured areas the ink follows value instead of luma, so a saturated blue wall is hatched lightly rather than going black. The source's own pencil texture is kept from turning into ink dashes.
- **`--gold auto|MASK`:**
  - `auto` picks gold/ochre areas of the colour source (hue 35–62°, saturated, bright, with morphological closing). A mask (video, image or sequence) also works.
  - The leaf is a crinkled foil height field, shaded by a light that orbits every 5 s, with point flakes that twinkle smoothly. Nothing is random per frame.
  - Ink hatching is lifted off the leaf, and a crisp ink line runs along its edge.
  - The leaf only shows where the bloom mask is on. With `--color pencil` that is everywhere.
- **Temporal stability:**
  - The stroke grain and foil are not re-drawn each frame. Two texture-coordinate fields ride on smoothed background flow and are reset alternately with a cross-fade (Neyret texture advection). The pigment is flow-warped and smoothed over time.
  - Measured on a pan over the T3 keyframe, the flow-compensated frame difference is 19.8 for pencil vs 28.7 for ink only. The per-frame series is flat: there are no pops at the 24-frame resets.
- **`--bloom` uses the same strokes.** It replaces the old flat wash, which went pale and muddy.

Key flags (both CLIs):

| Flag | Meaning |
|---|---|
| `--strength S` | 1 means a full engraving. 0 means the source, re-printed in the paper/ink palette. `auto` sets it per frame from crispness: a crisp engraved plate (high-pass ≥ 0.10 at 480 lines) gets 0.35, a gray-wash frame (≤ 0.05) gets 1, and the value is smoothed over time. |
| `--ramp-in SEC` (video) | Ramps strength from `--strength-start` (0.25) up to `--strength` over the first SEC seconds, so a crisp plate frame dissolves into the filter. |
| `--bloom MASK` `--bloom-color SRC` | Video, image, PNG directory, glob or `%05d` pattern. It is animated (the last frame is held if the mask is shorter than the clip). Where the mask is white, colored-pencil strokes in SRC's colour (default: the input) are laid under the ink. |
| `--color pencil` / `--palette P` / `--gold auto\|MASK` / `--color-lift` | Final-drop colour (see above). `--palette` takes `residue`, `klimt`, `kandinsky` or `'#hex,#hex,…'`. Gray areas get a luminance gradient map; coloured areas snap to the nearest palette hue. |
| `--batch FILE` / `--no-lock` | See "Batch mode and the GPU lock". |
| `--matte-out DIR` / `--matte-in M` | Write the matte (PNGs plus `matte.mp4`), or reuse one. Reusing skips BiRefNet: about 6.5 fps instead of 2.7, which is useful for look tweaks. |
| `--keep-color` | Any saturated pixel anywhere stays in colour: residue ribbons, ghost Jades. |
| `--no-matte` | Engrave the whole frame. |
| `--upscale 2` / `--out-height 1080` | Output size. Jade is upscaled with `--upscaler` (default Real-ESRGAN `animevideov3`). The world uses `--world-upscaler` (default `lanczos`, which engraves more cleanly than SR's painterly smoothing). |
| `--preview` | Also writes `OUT_sbs.mp4`. |
| Look | `--period` (line spacing in px, default height/190), `--gamma` (1.15), `--contrast` (0.55), `--edges`, `--carve`, `--no-cross`, `--fallback-angle` (0 = horizontal lines in flat areas), `--tensor-sigma` (1.5 periods), `--outline` (ink line around Jade), `--grain`. |
| Motion | `--advect flow|pan|fixed` (default `flow`), `--iters` (2). |

## How it works

1. **Matte (`matte.py`)**
   - BiRefNet runs at 1024² in fp16 on the (SR-upscaled) frame.
   - A colour cue (chroma > 0.1–0.2) adds saturated bits near her silhouette, such as flying orange straps.
   - Blobs with less than 1.5 % coloured pixels are dropped: gray props or agents. Her hair, top and pants are near-gray, so colour alone is never the matte.
   - A temporal prior uses the previous matte, warped by DIS flow:
     - BiRefNet output is accepted only within a motion-sized reach of that silhouette, or near colour. The reach widens while she re-emerges from an occluder.
     - If the area balloons past 1.6× her running size, the matte hugs the previous silhouette. This catches BiRefNet flipping to the whole steel structure, as on f42 of the test.
     - Where the two mattes agree, they are blended (weight 0.45), then feathered.
2. **Engraving (`engrave_core.py`, all on the GPU)**
   - **Tone:** luminance → auto-levels (percentiles smoothed over time) → local contrast boost → darkness. The tone is analysed with Jade filled in from the surrounding world.
   - **Line direction:** a smoothed structure tensor makes lines run along edges and forms. Where coherence is low (crossings, vortex points that would become fingerprint loops) or the image is flat, the direction blends to a screen-space fallback angle.
   - **Line field:** a continuous stripe field f ≈ cos(phase), made by iterated oriented-Gabor filtering (16-angle bank, the fingerprint-enhancement trick). Lines bend with the form, and fork or end like burin cuts.
   - **Stroke width follows tone:** ink is laid wherever f > cos(π·coverage), with analytic anti-aliasing.
   - **Cross-hatching:** a 55° layer for mid-darks fades out in the deepest darks, which become solid black with thin white lines.
   - **Ink edges:** two-scale XDoG contour ink, plus white-line carving on the lit side of edges inside the darks.
   - **Paper and ink:** static paper grain and slight ink starvation. The output is pure two-colour, with no gray wash.
   - **Jade:** composited back in through the matte, with a thin ink outline.
3. **Temporal stability**
   - Each frame, the line field, the tensor and the tone are advected from the previous frame with background flow. DIS flow is used, with the flow inside Jade replaced by the median background motion.
   - Lines are then only re-aligned by 2 damped Gabor iterations, so they stick to the world instead of boiling.
   - Measured as the flow-compensated frame difference in the world region (lower is better):

     | Variant | Difference |
     |---|---|
     | `flow` (default) | 27 |
     | `pan` | 32.5 |
     | Fixed screen (`fixed`) | 33 |
     | Re-synthesised every frame | 35.5 |
     | Source thresholded into a binary texture | 33 |

     The last row is a control: a binary texture attached to the content. That makes the default about as stable as content-attached detail can be by this measure.
   - `fixed` gives the deliberate shower-door print look, if wanted.

## Speed (RTX 3090, 121-frame 864×496 Seedance clip)

| Output | fps | ms/frame |
|---|---|---|
| 1882×1080 (`--out-height 1080`) | **2.7** | Matte ~160, engrave ~110, SR ~32, flow ~9 |
| 1728×992 (`--upscale 2`) | 3.2 | |
| 864×496 native | 5.4 | |
| 1080p with `--matte-in` | ~6.5 | |

| 1920×1080 `--color pencil --gold auto` | 1.6 | Matte ~240, engrave ~200, SR ~95 |
| 1080p `--bloom --palette` with `--matte-in` | 3.2 | |

So a 5 s shot takes about 45 s at 1080p (about 75 s in pencil mode). BiRefNet is the bottleneck. `anime6b` for Jade costs about 290 ms/frame more than `animevideov3`.

## Caveats

- **Native 480p works, but it is coarse.** Lines are about 3 px apart, which is legible but low on detail. Render 480p sources at 1080p (`--out-height 1080`) for the edit; the engraving hides upscale softness.
- **Crisp, already-engraved images get re-hatched.** At strength 1, their fine detail turns into a darker stipple. Use `--strength 0.3–0.5` or `auto` for plates and stills from the image models.
- **The matte follows the source.** When Seedance ghosts Jade through a foreground column (test f41–43), the matte follows. A one-frame semi-transparent box can appear around a ghosted Jade.
- **Low-colour silhouettes may be dropped.** A heavily occluded Jade with no visible orange or skin may lose components. A shot that is all hair and black top from behind may need `--matte-in` with a hand-made or SAM matte.
- **Multiple Jades.** Ghost Jades and the committee are colourful, so they pass the colour test. Gray TVA agents are rejected by design. Translucent ghosts are segmented as solid unless `--keep-color` catches them.
- **Line spacing is screen-relative.** It does not change with zoom, and big dolly-ins will look printed-on. Lines follow motion through flow advection, but large parallax or disocclusions re-grow lines over 2–4 frames. That is visible as a soft shimmer at the edges of fast-moving foreground props.
- **Matte in colour worlds.** In pencil/bloom mode, colour is no longer a Jade cue, because the world is coloured too. The matte then relies on BiRefNet plus the temporal prior. Colourful props that BiRefNet calls salient may pass through unengraved; use `--matte-in` for hero shots.
- **`--gold auto` catches every gold-ish pixel.** That includes ochre buildings and an orange-yellow wave stripe. Give a mask when you only want specific shapes gilded.
- **Palette mode follows the source's luminance.** On B&W clips the palette tracks soft gradients in the source sky, which can read as wood-grain bands.
- **A flood edge is only as good as its mask.** Feather the mask over 40 px or more.
- **Output is bitrate-hungry.** Fine line art needs a lot of bitrate: CRF 16 is about 10–15 MB/s at 1080p.
