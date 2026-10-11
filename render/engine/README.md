# REWIND render engine

A timeline-driven compositor for the *Rewind* music video. Frames are drawn in JavaScript inside headless Chrome (three.js r186 on the RTX 3090 via ANGLE/Vulkan) and encoded with ffmpeg. Every frame depends only on its index, so ranges render in parallel workers and can be re-rendered in any order.

```bash
cd ~/Documents/rewind-take-two
(cd render/engine && npm install)                                     # playwright-core + three (node_modules is gitignored)

node render/engine/render.mjs --preview                               # the film (render/timeline.js), 960x540 draft + audio
node render/engine/render.mjs                                          # full 1920x1080, x264 High CRF 16 + AAC 320k
node render/engine/render.mjs --range 42.38 56.54 --encode            # a frame range (+ a clip with its audio slice)
node render/engine/render.mjs --range 25:1 33:1 --preview --encode    # ranges accept bar:beat / word / section times
node render/engine/render.mjs --still 84.5                            # one full-res PNG still at t
node render/engine/render.mjs --stills 83,85.2,"word:reload"          # several stills
node render/engine/render.mjs --sheet 82:95:0.5 --cols 6              # contact sheet
node render/engine/render.mjs --list                                  # resolved shot table with bar:beat
node render/engine/render.mjs --verify 8                              # determinism check (two browsers, opposite orders)
node render/engine/render.mjs --serve                                 # studio scrubber URL (arrow keys step frames)

node render/engine/render.mjs --timeline render/engine/demo/timeline.js --preview   # the 13 s engine demo
```

Options: `--timeline <file>` (default `render/timeline.js`), `--preview` or `--w/--h`, `--workers N` (default 4 full, 3 preview, capped at 6), `--gpu nvidia|egl|cpu`, `--audio <mp3>` (default: the timeline's `audio`, else `inputs/Rewind - cinematic edition (Remastered).mp3`), `--timing <json>`, `--out <mp4>`, `--crf`, `--preset`, `--q <jpeg quality>`, `--png` (lossless intermediate frames), `--force` (re-render cached frames), `--noaudio`.

Outputs (gitignored): `render/engine/out/<timeline name>/{full,preview}/frames/f000000.jpg`, `…/<name>_<mode>[_a-b].mp4`, `…/stills/`. Extracted video frames: `media/engine_cache/{full,preview}/`.

## Architecture

```
render.mjs (Node)
  ├─ imports the timeline + timing JSON (resolves ranges, finds every video/matte)
  ├─ lib/prepare.mjs  ffmpeg → CFR JPEG sequences per source (media/engine_cache/<mode>/, keyed by size+mtime+res)
  ├─ lib/server.mjs   static server over the repo root + PUT /__out/… (the page uploads finished frames straight to disk)
  ├─ N workers = N headless Chrome processes, each takes 1-second chunks off a shared queue (resumable, atomic writes)
  └─ ffmpeg: frames + audio slice (-ss = first frame / 24) → H.264 High, BT.709 tagged, AAC 48 kHz

page/index.html → src/engine.js (one frame, i → t = i / 24)
  shotAt(t) → content clock (shot.time remap, tapeStop, hold) → fx.js → post parameters
  layers (bottom → top), each → draw ops → compositor.js (one three.js WebGLRenderer owns the GL context):
      'pre' layers ─► comp RT (premultiplied) ──► post pass ──► 'post' layers (HUD, lyrics) ──► final pass ─► canvas
                      └─ isolation mask RT (keepColor layers)     (distort, tape, VHS, isolate,     (flash, fade, dither)
                                                                    grade, paper, grain, letterbox)
  assets.js: miss-driven loads (draw → await whatever was missing → draw again), so pixels never depend on cache timing
```

Lineage: the CLI/worker harness, TimeMap and miss-driven loader come from `rewind-music-video/render` (Rewind take one); the single-three.js-context compositor with Canvas2D type layers from `rare-earth-techno-remix/render`; chunked resumable workers and studio scrubber from `orbital-sunrise-video/video`. New here: a declarative shot/layer timeline, keyframes, a real video layer (reverse, ramps, freeze, mattes, keys), nested comps for rewinds, module hosting for three.js and Canvas2D, GPU rendering, and frames uploaded instead of base64-returned.

## Timeline

`render/timeline.js` (or any file passed with `--timeline`) default-exports an object, or a function `({T, core}) => object` (T is the TimeMap, so shots can be generated from sections or lyrics). It must import cleanly in Node (no DOM at top level): render.mjs reads it to find videos and the range.

```js
export default {
  name: 'rewind', audio: 'inputs/Rewind - cinematic edition (Remastered).mp3', range: [0, 227.96],
  background: '#000000',
  fx: [{ type: 'grain', amount: 0.04 }],                    // global effects, applied to every shot first
  shots: [                                                   // base track: one shot at a time; carries post fx
    { id: 'drop1_rewind', start: '25:1', end: '33:1',        // or dur: '8bar' | '16b' | 3.5
      time: [[0, 0], [2, 1, 'inOut'], [4, 4]],               // optional content-clock remap for every layer
      background: '#0b0b0c',
      layers: [ /* bottom → top */ ],
      fx: [{ type: 'rewind', amount: 1 }, { type: 'punch', on: 'downbeat' }] },
  ],
  overlays: [                                                // any number at once (HUD, lyrics); default stage 'post'
    { id: 'lyrics', start: 0, end: 227.96, layers: [{ type: 'canvas', module: 'lyric', params: { style: 'line' } }] },
  ],
};
```

**Times.** Shot `start`/`end`, ranges and absolute keyframe times accept: seconds (`86.5`), `"bar:beat"` (1-based, fractional beats ok, on the tracked grid: `"25:1"` = 42.38 s), `"beat:64"`, `"word:reload"`, `"word:rewind#2"`, `"word:stop@40"` (first after 40 s), `"wordEnd:…"`, `"line:12"`, `"section:drop1"`, `"sectionEnd:drop1"`, `"event:impact#2"`, plus offsets: `"17:1+0.5b"`, `"word:rewind-2f"`, `"section:drop2+1bar"`, `"33+0.25"`. A missing word or section throws (a silent fallback would cut on the wrong frame). `end` defaults to the next shot's start.

**Timing source.** `analysis/cinematic/timing.json` (beats, bars, sections, `lyrics.lines[].words`, typed events) is used automatically; until it existed, `data/timing.stub.json` (from `tools/make_stub_timing.py`) stood in. The loader is tolerant of other shapes (see `src/timing.js`).

**Keyframes.** Any animatable value may be a constant, `[[t, value, ease?], …]` (t = local seconds or an absolute time string; ease on the left key: `linear` `hold` `in` `out` `inOut` `inCubic` `outCubic` `inOutCubic` `inExpo` `outExpo` `inOutSine` `outBack` `smooth`), `{keys, ease}`, or a function `(lt, env) => value`. Numbers, arrays and `#rrggbb` colours interpolate.

### Layers

Common: `id`, `type`, `start`/`end` (shot-local or absolute), `opacity`, `fadeIn`/`fadeOut` (s), `blend` (`normal` `add` `screen` `multiply` `erase`), `stage` (`pre` default for shots, `post` for overlays: post layers sit above grain/VHS/letterbox), `keepColor` (stays in colour under `isolate`), `realtime` (ignore the shot's time remap), `time` (layer clock remap), `noRewind` (skipped when replayed inside a comp), transform: `fit` (`cover` `contain` `height` `width` `stretch` `none`), `x`, `y` (design px from centre), `scale` (or `[sx, sy]`), `rotate` (deg), `anchor` (`[0.5, 0.5]`), `crop` (`[x0, y0, x1, y1]` normalised), `rect` (`[x, y, w, h]` design px), `kenBurns: {from: {scale, x, y, rotate}, to: {…}, ease}`, `grade: {saturation, exposure, contrast, gamma, tint, lift, invert}`, `key: {type: 'luma', low, high, invert} | {type: 'chroma', color, tolerance, softness, spill}`.

| type | specific params |
|---|---|
| `solid` | `color` |
| `image` | `src`, `repeat: [x, y]` |
| `parallax` | `speed` (px/s) or `scroll` (keyframed px); `layers: [{src, depth (scroll factor), y, scale, repeat, grade, opacity, blend}]` (tiles horizontally) |
| `video` | `src` (mp4/webm/mov), `in` (source s), `rate` (number or keyframes; negative = reverse; ramps are integrated), or `srcTime` (keyframes: layer time → source time), `freeze` (layer time to hold from), `loop` (`true` / `'pingpong'`), `frameBlend` (cross-fade neighbouring frames for slow motion), `echo: {n, dt, alpha, blend}` (ghosts of the frames it came from), `matte: {src, mode: 'luma' / 'alpha' / 'lumaInv' / 'alphaInv', offset}`, `alpha: true` (source has alpha: extracted as PNG) |
| `canvas` | `module`, `params` (Canvas2D module) |
| `three` | `module`, `params`, `samples` (MSAA, default 4), `linear` (default true: module renders linear light; `false` for modules that output display-ready colour, e.g. `render/three` Engraver scenes) |
| `comp` | `source: 'film'` (whatever shot covers the source time, skipping other comps) or a shot id; `srcTime` keyframes (layer time → absolute song time, e.g. `[[0, 86.5, 'inCubic'], [3, 82]]` = rewind); `echo`. Renders that shot's `pre` layers (not its post fx), max nesting depth 2 |

### Effects (`fx`, shot-level; numbers keyframable on the shot clock)

`grain {amount, size, seed: 'frame'|'twos'|'shot'}` · `paper {amount}` · `vignette` · `scanlines` · `chroma {amount px}` · `vhs` · `warble` · `wobble` · `tracking` · `ripple {amount, speed}` · `zoom` · `spin` · `grade {saturation, contrast, exposure, tint, lift}` · `letterbox {aspect 2.39, amount}` · `isolate {amount, ink, paper, engrave, cell, angle}` (world → ink on paper / engraving, `keepColor` layers stay in colour) · `fade {in, out}` · `flash {at: [...] | on: events, dur, amount, color}` · `punch {amount, on, decay}` (zoom punch) · `shake {amp, freq, steady, on, decay}` · `tapeStop {at, dur, toBlack}` (content clock decelerates to a stop + sag, wobble, chroma, darkening) · `hold {at, until}` (freeze frame of every layer) · `rewind {amount}` (VHS search bands, tracking, chroma, warble) · `bg {color}`.

Events for `on`: `'beat'`, `'downbeat'`, `'every:2'`, any event type in timing.json (`'impact'`, `'trailer_impact'`, `'vocal_chops'`, `'words'`, `'lines'`, …), an array of times, or `{list, every, offset}`. Events before the shot's start are ignored, so nothing leaks across a cut.

## Modules (Canvas2D and three.js)

A module is an ES module; the timeline names it as `'hud'` (→ `render/engine/modules/hud.js`), a repo path (`'render/three/scenes/penrose_loop.js'`) or a path relative to the timeline file.

```js
// Canvas2D: drawn into a cleared W×H canvas already scaled to 1920×1080 design units
export async function init(ctx, params, env) { return { /* state, e.g. loaded images */ }; }   // optional, once
export function draw(lt, env) { const g = env.ctx; /* draw from lt / env.t only */ }

// three.js: draw into the render target the engine has bound (transparent, MSAA)
import * as THREE from 'three';                       // always the bare specifier (import map → node_modules three r186)
export async function init(renderer, params, env) { const scene = …, camera = …; return { scene, camera }; }
export function draw(lt, env) { env.renderer.render(env.state.scene, env.state.camera); }
// Factory form (used by render/three): export function createScene() { return { init(renderer, params), draw(t) }; }
```

`env`: `lt` (layer clock, after remaps), `t` (absolute song time being drawn; inside a comp, the source time), `frame`, `frameT` (output time), `dur`, `shot`, `layer`, `params`, `state`, `val(x, default)` (evaluate a keyframed param at lt), `T` (TimeMap), `lyric(opts)`, `pulse(on, decay)`, `events(on)`, `rng(...seed)` (seeded), `core` (hash, noise, easing, palette, clock), `assets`, `rewinding`, `W`/`H` (1920/1080), `S` (px per design px); three modules also get `renderer`, `target`, and `THREE` in init. Rules: no `Math.random` (it is reseeded per frame anyway), no `Date`/`performance.now` in pixels, no state carried between `draw` calls, never call `renderer.setRenderTarget`, restore any renderer state you change.

Built-ins: **hud** (`platformer`: death counter that counts timing events since `from`, speedrun timer, iteration, level; `rewind`: ◀◀ REWIND ×N with keyframed multiplier, tape counter, scrub bar; `pause`: ▶ RESUME / ◀◀ REWIND / QUIT with a keyframed cursor; `loading`: LOADING + tip), **lyric** (`line`: whole line, each word lights, pops and underlines as sung; `slam`: current word big), **ribbon** (causal residue: Catmull-Rom path from keyframes or a track JSON, orange→sky gradient, twist, glow, pencil hatching, motes, `drift` to stream behind a tracked subject; replayed backwards it un-spools), **slate** (animatic placeholder), **iso_test** (reference three.js module).

### Lyric/timing helpers

`env.lyric({lead, hold})` (= `T.lyric(t)`) returns `{line, lineIndex, text, words: [{text, start, end, state: 'past' | 'current' | 'future', progress}], word, wordIndex, lineProgress, appear, vanish, next}`. Also `T.wordAt(t)`, `T.lineAt(t)`, `T.word('rewind', 2)`, `T.section('drop1')`, `T.sectionAt(t)`, `T.barBeat(bar, beat)`, `T.barBeatAt(t)`, `T.beatTime(x)`, `T.beatIndexAt(t)`, `T.countIn(a, b, 'beats')`, `T.pulse(t, 'downbeat', 0.12)`, `T.time(expr)`.

## How to…

- **Add a shot:** append to `shots` with `start`/`end` (bar:beat is best), `layers`, `fx`. `--list` shows the resolved table, `--stills` / `--range … --encode --preview` checks it.
- **Add a layer:** add an object to the shot's `layers` (order = stacking). Media paths are repo-relative; videos are extracted on the next run automatically. Use `stage: 'post'` for anything that must not get grain/VHS/letterbox.
- **Add a module:** write `render/<somewhere>/my_module.js` with `init`/`draw` (above), reference it as `{type: 'canvas' | 'three', module: 'render/<somewhere>/my_module.js', params: {...}}`. Drop-in 3D scenes from `render/three/scenes/*.js` work as `{type: 'three', module: 'render/three/scenes/penrose_loop.js', linear: false}`.
- **Add an effect:** a `case` in `src/fx.js` setting post parameters, plus the shader code in `src/shaders.js` (`FS_POST`) and the uniform name in `Compositor.post`.

## Determinism and hygiene

- Frame i depends only on i: all randomness is hashed from (seed, frame/time), counters are counted from the timing grid, assets load miss-driven, `Math.random` is reseeded per frame. `--verify N` renders N frames in two browsers in opposite orders and compares pixel hashes (demo: 8/8 identical on nvidia).
- Cached frames carry a fingerprint of every `.js/.json/.html` under `render/` plus the timing JSON and size/quality; any change discards stale frames. Media replaced under the same path is re-extracted (size+mtime key) but its rendered frames are not invalidated: pass `--force`.
- Chrome's TMPDIR is forced onto disk (`render/engine/out/t`) because `/tmp` is a small tmpfs; workers are capped at 6.
- Pixels are reproducible per GPU backend; do not mix `--gpu nvidia` and `--gpu cpu` frames in one encode.

## Throughput (engine demo, 13 s = 312 frames, this machine)

| mode | workers | wall | fps | × realtime | in-page per frame |
|---|---|---|---|---|---|
| preview 960×540 (JPEG q.85) | 3 | 3.4 s | 91 | 3.8× | ~25 ms |
| full 1920×1080 (JPEG q.95) | 4 | 8.2 s | 38 | 1.6× | ~90 ms |
| full 1920×1080 | 6 | 8.3 s | 38 | 1.6× | (no gain: GPU readback/JPEG bound, start-up ~1.5 s) |

Encode: x264 `slow` CRF 16 High + AAC 320k took 8 s for the 13 s demo (≈45 Mb/s with per-frame grain; use `--crf 18`–`20` or grain `seed: 'twos'` for upload sizes). The `render/three` Engraver diorama costs ~600 ms per 1080p frame on its own. Whole film at demo complexity: ≈2.5 min full, ≈1 min preview.

## Demo (`demo/timeline.js`, song 82.0–95.0 s, "And now I'm back on the road … Reload")

1. `run` (82.0 → bar 50:1): Jade runs (video, push-in), a residue ribbon trails her, platformer HUD counts a death every beat, the lyric lights word by word, the tape stops under her (`tapeStop`).
2. `rewind` (50:1 → 51:4): a `comp` layer replays shot 1 backwards and accelerating, with echo ghosts, VHS rewind bands and ripple; HUD ◀◀ REWIND ×2 → ×4 → ×8 on bar:beat keys; the ribbon un-spools.
3. `level` (51:4 → word "reload"): three-layer parallax side-scroller under `isolate` + engrave; Jade (alpha-matte video) and her pencil residue circle stay in colour; speed ramp to 0.35× with frame blending, freeze at 3.3 s, letterbox animates in, beat punch and downbeat shake.
4. `loading` (word "reload" → 95.0): the three.js isometric module turns a quarter on bar 54:1, Jade luma-keyed as a freeze frame, LOADING screen with a tip; the lyric switches to ink on paper via absolute-time colour keys.

Stills: `demo_stills/01_run_hud_ribbon_lyric_t84.583.jpg`, `02_rewind_comp_x4_t88.208.jpg`, `03_parallax_isolate_matte_t91.917.jpg`, `04_three_iso_loading_t94.292.jpg`. Demo media is staged by `tools/make_demo_media.py` into `media/engine_demo/` (gitignored; clips from rewind-music-video assets).

## Known limitations

- Video is decoded ahead of time to JPEG sequences at native fps (exact random access, but ~50 MB of cache per 10 s of 1080p source). VFR sources are forced to CFR. Alpha sources need `alpha: true`.
- Frame blending is a linear cross-fade (no optical flow). Keys are basic (luma; chroma with simple spill pull; no matte choke/erode); bad mattes should be fixed upstream.
- `comp` layers render the source shot's `pre` layers only (no post fx) and re-render once per echo ghost; nesting is limited to depth 2. Absolute-time keyframes inside a remapped clock are approximate.
- No bloom or motion blur in the compositor (modules can glow with Canvas `shadowBlur`); no audio mixing (the mux takes a slice of one mp3).
- Intermediate frames are JPEG q.95 by default (`--png` for lossless, slower). Per-frame grain makes the CRF 16 master large.
- The ribbon accepts a track JSON, but the engine has no tracker; paths are keyframed by hand or come from another tool.
- Three modules must import bare `'three'` (one instance, r186). Modules that output display-ready colour need `linear: false`.
- On this dual-GPU box Chrome's Vulkan path needs `--disable-vulkan-surface` (otherwise the WebGL context is lost ~100 ms after creation); `--gpu egl` (NVIDIA EGL) and `--gpu cpu` (SwiftShader, several times slower) are fallbacks.
