// prepare.mjs: find every video / matte the timeline names and pre-extract it to a CFR frame sequence with ffmpeg.
// Why sequences, not <video>/WebCodecs: seeking a <video> is not frame-exact and decode timing is nondeterministic;
// WebCodecs needs an in-page MP4 demuxer. JPEG sequences give exact random access (reverse, ramps, freeze frames),
// are shared by every worker, and decode in ~5 ms with createImageBitmap.
//   media/engine_cache/<variant>/<name>_<hash>/000001.jpg   (variant = full | preview)
//   media/engine_cache/<variant>/index.json                 { "<src>": {dir, fps, frames, w, h, ext, src} }
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync, renameSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, resolve, basename, extname } from 'node:path';

const VIDEO = /\.(mp4|webm|mov|mkv|m4v)$/i;

// walk a timeline object for video sources: {src: '*.mp4', alpha?} and {matte: {src} | '*.mp4'}
export function collectVideos(tl) {
  const out = new Map();
  const walk = (o, depth = 0) => {
    if (!o || typeof o !== 'object' || depth > 12) return;
    if (Array.isArray(o)) { for (const x of o) walk(x, depth + 1); return; }
    if (typeof o.src === 'string' && VIDEO.test(o.src)) out.set(o.src, { src: o.src, alpha: !!o.alpha, gray: false, ...(out.get(o.src) || {}) });
    if (o.matte) { const m = typeof o.matte === 'string' ? o.matte : o.matte.src; if (m && VIDEO.test(m)) out.set(m, { src: m, alpha: false, gray: true }); }
    for (const k of Object.keys(o)) if (k !== 'matte' && typeof o[k] === 'object') walk(o[k], depth + 1);
  };
  walk(tl);
  return [...out.values()];
}

function probe(ffmpeg, file) {
  const r = spawnSync(ffmpeg, ['-hide_banner', '-i', file], { encoding: 'utf8' });
  const s = r.stderr || '';
  const v = s.split('\n').find(l => /Stream #.*Video:/.test(l)) || '';
  const fps = +(v.match(/([\d.]+) fps/) || v.match(/([\d.]+) tbr/) || [])[1];
  const wh = v.match(/, (\d{2,5})x(\d{2,5})/);
  const dur = s.match(/Duration: (\d+):(\d+):([\d.]+)/);
  if (!fps || !wh) throw new Error(`cannot probe ${file}:\n${s.slice(-600)}`);
  return { fps, w: +wh[1], h: +wh[2], duration: dur ? +dur[1] * 3600 + +dur[2] * 60 + +dur[3] : null };
}

export function prepareVideos({ root, tl, variant, maxW, maxH, ffmpeg, log = console.log }) {
  const base = join(root, 'media/engine_cache', variant);
  mkdirSync(base, { recursive: true });
  const idxFile = join(base, 'index.json');
  const index = existsSync(idxFile) ? JSON.parse(readFileSync(idxFile, 'utf8')) : {};
  for (const v of collectVideos(tl)) {
    const abs = resolve(root, v.src);
    if (!existsSync(abs)) throw new Error(`video not found: ${v.src}`);
    const st = statSync(abs);
    const key = createHash('sha1').update(`${v.src}|${st.size}|${st.mtimeMs}|${maxW}x${maxH}|${v.alpha}|${v.gray}|v2`).digest('hex').slice(0, 10);
    const dir = `${basename(v.src, extname(v.src)).replace(/[^\w-]/g, '_')}_${key}`;
    const out = join(base, dir), ext = v.alpha ? 'png' : 'jpg';
    const have = index[v.src];
    if (have && have.dir === dir && existsSync(join(out, '.done'))) continue;
    const p = probe(ffmpeg, abs);
    const sc = Math.min(1, maxW / p.w, maxH / p.h);
    const w = Math.max(2, Math.round(p.w * sc / 2) * 2), h = Math.max(2, Math.round(p.h * sc / 2) * 2);
    rmSync(out, { recursive: true, force: true }); mkdirSync(out, { recursive: true });
    log(`[prepare] ${v.src} → ${variant}/${dir} (${p.w}x${p.h} @ ${p.fps} fps → ${w}x${h}${v.gray ? ' gray' : ''}${v.alpha ? ' rgba png' : ''})`);
    const vf = [`fps=${p.fps}`, `scale=${w}:${h}:flags=lanczos`, v.gray ? 'format=gray' : v.alpha ? 'format=rgba' : 'format=yuvj444p'].join(',');
    const r = spawnSync(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-y', '-i', abs, '-vf', vf, '-fps_mode', 'cfr', ...(ext === 'jpg' ? ['-q:v', '2'] : []), join(out, `%06d.${ext}`)], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error(`ffmpeg failed extracting ${v.src}`);
    const frames = readdirSync(out).filter(f => f.endsWith('.' + ext)).length;
    writeFileSync(join(out, '.done'), '');
    index[v.src] = { dir, fps: p.fps, frames, w, h, ext, src: v.src, srcW: p.w, srcH: p.h };
  }
  writeFileSync(idxFile + '.tmp', JSON.stringify(index, null, 1)); renameSync(idxFile + '.tmp', idxFile);
  return { index, cacheDir: `media/engine_cache/${variant}` };
}
