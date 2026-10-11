#!/usr/bin/env node
// render.mjs: drive the REWIND engine page in headless Chrome and encode with ffmpeg. See README.md.
//
//   node render/engine/render.mjs [--timeline render/timeline.js] [--preview]            whole timeline range → frames → MP4 with audio
//   node render/engine/render.mjs --range 84 88 [--encode]                               frame range (seconds or time expressions: "17:1", "word:rewind")
//   node render/engine/render.mjs --frames 2016 2112                                      frame range by index (end exclusive)
//   node render/engine/render.mjs --still 84.5            --stills 83,85.2,"17:1"         full-res PNG stills
//   node render/engine/render.mjs --sheet 82:95:0.5 [--cols 6]                             contact sheet PNG
//   node render/engine/render.mjs --verify 6 | --verify 40.4,119.2                         render frames in two browsers, compare pixel hashes
//   node render/engine/render.mjs --list                                                   shot table (resolved times)
//   node render/engine/render.mjs --serve                                                  studio scrubber at a local URL
//   node render/engine/render.mjs --track media/shots/X/take_1_matte/ [--out track.json]   subject track of a matte (centroid/top/bottom per frame)
// Options: --preview (960x540 draft) | --w --h | --workers N (≤6) | --gpu nvidia|cpu | --audio file.mp3 | --timing file.json
//          --out file.mp4 | --crf N | --preset P | --q jpegQuality | --force (re-render existing frames) | --png (lossless frames)
import { chromium } from 'playwright-core';
import { spawn, spawnSync } from 'node:child_process';
import { mkdirSync, existsSync, readFileSync, readdirSync, statSync, writeFileSync, rmSync, renameSync } from 'node:fs';
import { dirname, resolve, join, relative, basename, extname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { homedir } from 'node:os';
import { serve } from './lib/server.mjs';
import { prepareVideos, computeTrack } from './lib/prepare.mjs';
import { TimeMap, TIMING_PATHS } from './src/timing.js';
import * as core from './src/core.js';

const HERE = dirname(fileURLToPath(import.meta.url)), ROOT = resolve(HERE, '../..');
const FPS = 24;

// ---------------------------------------------------------------- args
const argv = process.argv.slice(2), args = {};
for (let i = 0; i < argv.length; i++) {
  const a = argv[i]; if (!a.startsWith('--')) continue;
  const k = a.slice(2), eq = k.indexOf('=');
  if (eq >= 0) { args[k.slice(0, eq)] = k.slice(eq + 1); continue; }
  const vals = []; while (i + 1 < argv.length && !(argv[i + 1].startsWith('--'))) vals.push(argv[++i]);
  args[k] = vals.length === 0 ? true : vals.length === 1 ? vals[0] : vals;
}
const PREVIEW = !!args.preview;
const W = +(args.w || (PREVIEW ? 960 : 1920)), H = +(args.h || (PREVIEW ? 540 : 1080));
const MODE = PREVIEW ? 'preview' : (W === 1920 ? 'full' : `${W}x${H}`);
const WORKERS = Math.max(1, Math.min(6, +(args.workers || (PREVIEW ? 3 : 4))));
if (+(args.workers || 0) > 6) console.warn('[render] workers capped at 6 (handbook rule)');
const Q = +(args.q || (PREVIEW ? 0.85 : 0.95));
const FMT = args.png ? 'png' : 'jpg';
const GPU = args.gpu || process.env.REWIND_GPU || 'nvidia';
const CHROME = args.chrome || process.env.CHROME || '/opt/google/chrome/chrome';
const FFMPEG = args.ffmpeg || process.env.FFMPEG || [join(homedir(), 'Documents/moongazing/.venv/bin/ffmpeg'), join(ROOT, 'analysis/karaoke/bin/ffmpeg')].find(existsSync) || 'ffmpeg';

// handbook: /tmp is a 16 GB tmpfs that fills up and crashes Chrome; keep Chrome's temp files on disk
if (!process.env.TMPDIR || process.env.TMPDIR.startsWith('/tmp')) {
  const t = join(HERE, 'out/t'); mkdirSync(t, { recursive: true }); process.env.TMPDIR = t;
}

// ---------------------------------------------------------------- timeline + timing (Node side: ranges, video prep)
const TL_PATH = relative(ROOT, resolve(ROOT, args.timeline || 'render/timeline.js'));
const TIMING_PATH = args.timing ? relative(ROOT, resolve(args.timing)) : TIMING_PATHS.find(p => existsSync(join(ROOT, p)));
if (!TIMING_PATH) throw new Error('no timing JSON (' + TIMING_PATHS.join(', ') + ')');
const T = new TimeMap(JSON.parse(readFileSync(join(ROOT, TIMING_PATH), 'utf8')), { source: TIMING_PATH });
if (T.isStub) console.warn(`[timing] ${TIMING_PATH} (STUB: analysis/cinematic/timing.json not there yet; bar:beat uses the stub grid)`);
// the same ctx helpers the page gives timeline functions (render/timeline.js merges section files with them)
const nodeCtx = { T, core,
  list: async dir => { const d = join(ROOT, dir); return existsSync(d) ? readdirSync(d).filter(f => statSync(join(d, f)).isFile()).sort() : []; },
  importModule: async p => import(pathToFileURL(join(ROOT, p)).href),
  readJSON: async p => JSON.parse(readFileSync(join(ROOT, p), 'utf8')) };
let tl = (await import(pathToFileURL(join(ROOT, TL_PATH)).href)).default;
if (typeof tl === 'function') tl = await tl(nodeCtx);
const NAME = (tl.name || basename(TL_PATH, extname(TL_PATH))).replace(/[^\w-]/g, '_');
const AUDIO = resolve(ROOT, args.audio || tl.audio || 'inputs/Rewind - cinematic edition (Remastered).mp3');
const OUTDIR = join(HERE, 'out', NAME);
const shotsAll = tl.shots || [];
const tlRange = [T.time(tl.range?.[0] ?? shotsAll[0]?.start ?? 0), T.time(tl.range?.[1] ?? 228)];

const parseTimes = s => [].concat(s).join(',').split(',').filter(Boolean).flatMap(x => {
  const m = x.match(/^(.+?):(.+?):(\d*\.?\d+)$/);            // a:b:step sweep (a, b may be expressions without ':')
  if (m && !/^\d+:\d*\.?\d+$/.test(x)) { const a = T.time(isNaN(m[1]) ? m[1] : +m[1]), b = T.time(isNaN(m[2]) ? m[2] : +m[2]), st = +m[3]; const r = []; for (let t = a; t < b - 1e-9; t += st) r.push(t); return r; }
  return [T.time(isNaN(x) ? x : +x)];
});
const frameOf = t => Math.round(t * FPS + 1e-6);

// ---------------------------------------------------------------- fingerprint (stale frames are worse than slow renders)
function fingerprint() {
  const h = createHash('sha1');
  const walk = d => { for (const f of readdirSync(d).sort()) { if (['node_modules', 'out', 'demo_stills', 'fonts'].includes(f)) continue; const p = join(d, f), s = statSync(p);
    if (s.isDirectory()) walk(p); else if (/\.(m?js|json|html)$/.test(f)) h.update(p + '\0').update(readFileSync(p)); } };
  walk(join(ROOT, 'render'));
  if (!TL_PATH.startsWith('render/')) h.update(readFileSync(join(ROOT, TL_PATH)));
  h.update(readFileSync(join(ROOT, TIMING_PATH)));
  h.update(`${W}x${H}|${Q}|${FMT}|${GPU}`);
  return h.digest('hex').slice(0, 16);
}

// ---------------------------------------------------------------- browser
// nvidia: ANGLE on Vulkan (RTX 3090). --disable-vulkan-surface matters: without it headless Chrome loses the WebGL
// context ~100 ms after creation on this box. egl: ANGLE on NVIDIA's EGL (fallback). cpu: SwiftShader (slow, always works).
const GPU_FLAGS_ALL = {
  cpu: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  egl: ['--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist', '--enable-gpu'],
  nvidia: ['--use-angle=vulkan', '--enable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan', '--disable-vulkan-surface', '--ignore-gpu-blocklist', '--enable-gpu'],
};
if (!GPU_FLAGS_ALL[GPU]) throw new Error('--gpu must be nvidia | egl | cpu');
const EGL_ENV = { __EGL_VENDOR_LIBRARY_FILENAMES: '/usr/share/glvnd/egl_vendor.d/10_nvidia.json' };
const FLAGS_COMMON = ['--disable-renderer-backgrounding', '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows',
  '--force-color-profile=srgb', '--js-flags=--max-old-space-size=4096', '--no-sandbox', '--font-render-hinting=none', '--hide-scrollbars'];

let srv, cacheDir = '';
const browsers = new Set();
let gpuMode = GPU;
const flagsFor = mode => [...{ cpu: GPU_FLAGS_ALL.cpu, egl: GPU_FLAGS_ALL.egl, nvidia: GPU_FLAGS_ALL.nvidia }[mode], ...FLAGS_COMMON];
async function launchPage(tag, mode) {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: flagsFor(mode), env: { ...process.env, ...(mode === 'egl' ? EGL_ENV : {}) } });
  browsers.add(browser);
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.on('console', m => { if ((['error', 'warning'].includes(m.type()) && !/GL Driver Message|GPU stall due to ReadPixels|CONTEXT_LOST_WEBGL|Context Lost/.test(m.text())) || args.verbose) console.log(`[page${tag}] ${m.text()}`); });
  page.on('pageerror', e => console.log(`[page error${tag}] ${e.message}`));
  const q = new URLSearchParams({ render: '1', timeline: TL_PATH, w: W, h: H, cache: cacheDir, timing: TIMING_PATH, v: Date.now() % 1e9 });
  await page.goto(`${srv.url}/render/engine/page/index.html?${q}`, { waitUntil: 'load' });
  await page.waitForFunction('window.ready === true || window.bootError', null, { timeout: 180000, polling: 100 });
  const err = await page.evaluate('window.bootError'); if (err) throw new Error('page boot failed: ' + err);
  await new Promise(r => setTimeout(r, 250));   // a lost context shows up ~100 ms after creation
  if (await page.evaluate('window.E.comp.renderer.getContext().isContextLost()')) { await browser.close().catch(() => {}); browsers.delete(browser); return null; }
  return { page, browser };
}
// GPU contexts can be lost when the card is busy (other agents' CUDA jobs): retry, then fall back egl → cpu.
// Pixels differ slightly between backends, so a fallback is announced loudly; keep one backend per encode.
async function openPage(tag = '') {
  const order = gpuMode === 'nvidia' ? ['nvidia', 'nvidia', 'nvidia', 'egl', 'cpu'] : gpuMode === 'egl' ? ['egl', 'egl', 'cpu'] : ['cpu'];
  for (const mode of order) {
    const P = await launchPage(tag, mode);
    if (P) { if (mode !== gpuMode) { console.warn(`[render] WebGL context kept getting lost on ${gpuMode}; falling back to --gpu ${mode} for the rest of this run`); gpuMode = mode; } return P; }
    console.warn(`[render] worker${tag}: WebGL context lost after boot on ${mode}; retrying`);
  }
  throw new Error('could not get a stable WebGL context on any backend');
}
const closeAll = async () => { for (const b of browsers) await b.close().catch(() => {}); browsers.clear(); };

function run(cmd, a) { return new Promise((ok, bad) => { const p = spawn(cmd, a, { stdio: 'inherit' }); p.on('close', c => (c ? bad(new Error(`${basename(cmd)} exited ${c}`)) : ok())); }); }

// ---------------------------------------------------------------- frame range render
async function renderRange(i0, i1, dir) {
  mkdirSync(dir, { recursive: true });
  const fp = fingerprint(), fpFile = join(dir, '.fingerprint');
  if (existsSync(fpFile) && readFileSync(fpFile, 'utf8') !== fp && !args.keep) {
    const old = readdirSync(dir).filter(f => /^f\d{6}\.(jpg|png)$/.test(f));
    if (old.length) console.log(`[render] sources changed since the frames in ${relative(ROOT, dir)} were rendered: discarding ${old.length} stale frames`);
    for (const f of old) rmSync(join(dir, f));
  }
  writeFileSync(fpFile, fp);
  const fname = i => `f${String(i).padStart(6, '0')}.${FMT}`;
  const todo = []; for (let i = i0; i < i1; i++) if (args.force || !existsSync(join(dir, fname(i))) || statSync(join(dir, fname(i))).size < 500) todo.push(i);
  console.log(`[render] ${NAME} ${MODE} ${W}x${H}: frames ${i0}–${i1 - 1} (${((i1 - i0) / FPS).toFixed(2)} s); ${todo.length} to render, ${i1 - i0 - todo.length} cached; ${WORKERS} workers, gpu=${GPU}`);
  if (!todo.length) return { frames: 0, wall: 0 };
  const token = 'w' + Math.random().toString(36).slice(2, 8);
  const sink = srv.sink(token, dir);
  const CH = 24, chunks = []; for (let k = 0; k < todo.length; k += CH) chunks.push(todo.slice(k, k + CH));
  let next = 0, done = 0, msIn = 0; const t0 = Date.now();
  const type = FMT === 'png' ? 'image/png' : 'image/jpeg';
  const work = async w => {
    if (next >= chunks.length) return;
    let P = await openPage('#' + w);
    while (next < chunks.length) {
      const chunk = chunks[next++];
      for (const i of chunk) {
        const go = () => P.page.evaluate(([i, o]) => window.renderFrame(i, o), [i, { upload: sink + fname(i), type, q: Q }]);
        let r;
        try { r = await go(); } catch (e) {
          console.log(`[worker ${w}] frame ${i} failed: ${e.message.split('\n')[0]}; restarting its browser`);
          await P.browser.close().catch(() => {}); browsers.delete(P.browser);
          P = await openPage('#' + w); r = await go();
        }
        msIn += r.ms + r.msEnc;
        if (++done % 48 === 0 || done === todo.length) {
          const el = (Date.now() - t0) / 1000;
          console.log(`  ${done}/${todo.length}  ${(done / el).toFixed(2)} fps wall  (in-page ${(msIn / done).toFixed(0)} ms/frame per worker)  eta ${((todo.length - done) / (done / el)).toFixed(0)} s`);
        }
      }
    }
    await P.browser.close().catch(() => {}); browsers.delete(P.browser);
  };
  await Promise.all(Array.from({ length: WORKERS }, (_, w) => work(w)));
  const wall = (Date.now() - t0) / 1000;
  console.log(`[render] ${todo.length} frames in ${wall.toFixed(1)} s = ${(todo.length / wall).toFixed(2)} fps (${(todo.length / wall / FPS).toFixed(2)}x realtime), incl. browser start-up`);
  return { frames: todo.length, wall };
}

async function encode(i0, i1, dir, out) {
  const a = i0 / FPS, dur = (i1 - i0) / FPS;
  mkdirSync(dirname(out), { recursive: true });
  const crf = args.crf ?? (PREVIEW ? 24 : 16), preset = args.preset || (PREVIEW ? 'veryfast' : 'slow');
  const hasAudio = existsSync(AUDIO) && !args.noaudio;
  if (!hasAudio) console.warn(`[encode] no audio (${AUDIO}); writing picture only`);
  console.log(`[encode] ${i1 - i0} frames → ${relative(ROOT, out)} (x264 ${preset} crf ${crf}${hasAudio ? `, AAC ${PREVIEW ? 192 : 320}k from ${relative(ROOT, AUDIO)} @ ${a.toFixed(3)} s` : ''})`);
  const t0 = Date.now();
  await run(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-stats', '-y', '-framerate', String(FPS), '-start_number', String(i0), '-i', join(dir, `f%06d.${FMT}`),
    ...(hasAudio ? ['-ss', a.toFixed(6), '-t', dur.toFixed(6), '-i', AUDIO, '-map', '0:v', '-map', '1:a'] : []),
    '-frames:v', String(i1 - i0), '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
    '-c:v', 'libx264', '-preset', preset, '-crf', String(crf), '-profile:v', 'high', ...(PREVIEW ? [] : ['-tune', 'grain', '-x264-params', 'aq-mode=3']),
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    ...(hasAudio ? ['-c:a', 'aac', '-b:a', PREVIEW ? '192k' : '320k', '-ar', '48000'] : []), '-movflags', '+faststart', out]);
  console.log(`[encode] done in ${((Date.now() - t0) / 1000).toFixed(1)} s → ${out}`);
}

// ---------------------------------------------------------------- main
if (args.track) {   // standalone: dump a matte's per-frame track (JSON) for use outside the engine
  const { spawnSync: sp } = await import('node:child_process');
  let abs = resolve(ROOT, String(args.track).replace(/\/$/, '')), inArgs, fps = +(args.fps || 24);
  if (statSync(abs).isDirectory()) {
    if (existsSync(join(abs, 'matte.mp4'))) inArgs = ['-i', join(abs, 'matte.mp4')];
    else { const f = readdirSync(abs).filter(x => /\.(png|jpe?g)$/i.test(x)).sort(); inArgs = ['-framerate', String(fps), '-pattern_type', 'glob', '-i', join(abs, '*' + extname(f[0]))]; }
  } else inArgs = ['-i', abs];
  const pr = sp(FFMPEG, ['-hide_banner', ...inArgs], { encoding: 'utf8' }).stderr || '';
  fps = +((pr.match(/([\d.]+) fps/) || [])[1] || fps);
  const tr = computeTrack(FFMPEG, inArgs, fps, !!args.alpha);
  const json = JSON.stringify({ src: relative(ROOT, abs), fps, fields: ['t', 'cx', 'cy', 'topX', 'topY', 'bottomX', 'bottomY', 'area'], frames: tr.map((p, i) => [+(i / fps).toFixed(4), ...p]) });
  if (args.out) { writeFileSync(resolve(args.out), json); console.log(`${tr.length} frames → ${args.out}`); } else console.log(json);
  process.exit(0);
}
try {
  if (args.serve) {
    ({ cacheDir } = prepareVideos({ root: ROOT, tl, variant: MODE, maxW: W, maxH: H, ffmpeg: FFMPEG }));
    srv = await serve(ROOT, { verbose: !!args.verbose });
    const q = new URLSearchParams({ timeline: TL_PATH, w: W, h: H, cache: cacheDir, timing: TIMING_PATH });
    console.log(`studio: ${srv.url}/render/engine/page/index.html?${q}   (ctrl-c to stop)`);
    await new Promise(() => {});
  }
  ({ cacheDir } = prepareVideos({ root: ROOT, tl, variant: MODE, maxW: W, maxH: H, ffmpeg: FFMPEG }));
  srv = await serve(ROOT, { verbose: !!args.verbose });

  if (args.list) {
    const { page } = await openPage();
    console.log(JSON.stringify(await page.evaluate('window.timingInfo')));
    for (const s of await page.evaluate('window.listShots()')) {
      const bb = T.barBeatAt(s.start);
      console.log(`${(s.overlay ? '+' : ' ') + s.id.padEnd(18)} ${s.start.toFixed(3).padStart(8)} → ${s.end.toFixed(3).padStart(8)}  (${(s.end - s.start).toFixed(2)} s, bar ${bb.bar}:${bb.beat.toFixed(2)})  ${s.layers.join(' ')}`);
    }
  } else if (args.still || args.stills) {
    const { page } = await openPage(); const out = args.outdir ? resolve(args.outdir) : join(OUTDIR, 'stills'); mkdirSync(out, { recursive: true });
    for (const t of parseTimes(args.still || args.stills)) {
      const i = frameOf(t);
      const r = await page.evaluate(([i]) => window.renderFrame(i, { type: 'image/png' }), [i]);
      const f = join(out, `${NAME}_${MODE}_t${(i / FPS).toFixed(3).replace('.', '_')}.png`);
      writeFileSync(f, Buffer.from(r.url.slice(r.url.indexOf(',') + 1), 'base64'));
      console.log(`${relative(ROOT, f)}  t=${(i / FPS).toFixed(3)} f${i} shot=${r.shot}  render ${r.ms.toFixed(0)} ms`);
    }
  } else if (args.sheet) {
    const { page } = await openPage(); const frames = parseTimes(args.sheet).map(frameOf);
    const url = await page.evaluate(([f, c, tw]) => window.renderSheet(f, c, tw), [frames, +(args.cols || 6), +(args.tw || 320)]);
    const f = args.out ? resolve(args.out) : join(OUTDIR, `${NAME}_sheet.png`); mkdirSync(dirname(f), { recursive: true });
    writeFileSync(f, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64')); console.log(relative(ROOT, f));
  } else if (args.verify) {
    // determinism: the same frames in two independent browsers (different order) must hash identically
    const v = args.verify === true ? '6' : String([].concat(args.verify).join(','));
    const [a, b] = tlRange;
    const frames = /^\d+$/.test(v) ? Array.from({ length: +v }, (_, k) => frameOf(a + (b - a) * (k + 0.5) / +v)) : parseTimes(v).map(frameOf);   // N evenly spaced, or explicit times
    const A = await openPage('#A'), B = await openPage('#B');
    const ha = [], hb = [];
    for (const i of frames) ha.push((await A.page.evaluate(i => window.renderFrame(i, { hash: true }), i)).hash);
    for (const i of [...frames].reverse()) hb.unshift((await B.page.evaluate(i => window.renderFrame(i, { hash: true }), i)).hash);
    let bad = 0; frames.forEach((i, k) => { const ok = ha[k] === hb[k]; if (!ok) bad++; console.log(`f${i} (${(i / FPS).toFixed(3)} s)  ${ha[k]}  ${hb[k]}  ${ok ? 'OK' : 'MISMATCH'}`); });
    console.log(bad ? `[verify] ${bad}/${frames.length} frames differ: something reads state outside the frame index` : `[verify] all ${frames.length} frames identical across browsers and orders`);
    if (bad) process.exitCode = 2;
  } else {
    let i0, i1;
    if (args.frames) { [i0, i1] = [].concat(args.frames).map(Number); }
    else if (args.range) { const r = [].concat(args.range).map(x => T.time(isNaN(x) ? x : +x)); [i0, i1] = [frameOf(r[0]), frameOf(r[1])]; }
    else [i0, i1] = [frameOf(tlRange[0]), frameOf(tlRange[1])];
    const dir = join(OUTDIR, MODE, 'frames');
    await renderRange(i0, i1, dir);
    await closeAll();
    const whole = !args.range && !args.frames;
    if (whole || args.encode) {
      const out = args.out ? resolve(args.out) : join(OUTDIR, `${NAME}_${MODE}${whole ? '' : `_${(i0 / FPS).toFixed(2)}-${(i1 / FPS).toFixed(2)}`}.mp4`);
      await encode(i0, i1, dir, out);
    }
  }
} finally {
  await closeAll();
  if (srv) await srv.close();
}
