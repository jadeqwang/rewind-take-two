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
const isSeqDir = p => /\/$/.test(p) || /_matte$/.test(p);   // image-sequence directory (e.g. tools/engrave --matte-out DIR/)
const isMedia = p => typeof p === 'string' && (VIDEO.test(p) || isSeqDir(p));

// walk a timeline object for video sources: {src: '*.mp4', alpha?} and {matte: {src} | '*.mp4'}
export function collectVideos(tl) {
  const out = new Map();
  const walk = (o, depth = 0) => {
    if (!o || typeof o !== 'object' || depth > 12) return;
    if (Array.isArray(o)) { for (const x of o) walk(x, depth + 1); return; }
    if (isMedia(o.src) && o.type !== 'image') out.set(o.src, { src: o.src, alpha: !!o.alpha, gray: false, ...(out.get(o.src) || {}) });
    if (o.matte) { const m = typeof o.matte === 'string' ? o.matte : o.matte.src; if (isMedia(m)) out.set(m, { src: m, alpha: false, gray: true }); }
    for (const k of Object.keys(o)) if (k !== 'matte' && typeof o[k] === 'object') walk(o[k], depth + 1);
  };
  walk(tl);
  return [...out.values()];
}

// ffmpeg input args for a source: a video file, or a directory of numbered PNG/JPG frames (fps from the dir's
// fps.txt, else 24; a matte.mp4 inside the directory is preferred when present)
function inputArgs(abs) {
  if (!statSync(abs).isDirectory()) return { args: ['-i', abs], key: abs };
  if (existsSync(join(abs, 'matte.mp4'))) return { args: ['-i', join(abs, 'matte.mp4')], key: join(abs, 'matte.mp4') };
  const files = readdirSync(abs).filter(f => /\.(png|jpe?g|webp)$/i.test(f)).sort();
  if (!files.length) throw new Error(`no frames in ${abs}`);
  const fps = existsSync(join(abs, 'fps.txt')) ? +readFileSync(join(abs, 'fps.txt'), 'utf8').trim() : 24;
  return { args: ['-framerate', String(fps), '-pattern_type', 'glob', '-i', join(abs, '*' + extname(files[0]))], key: join(abs, files[files.length - 1]), seqFps: fps };
}
function probe(ffmpeg, file) {
  const r = spawnSync(ffmpeg, ['-hide_banner', ...inputArgs(file).args], { encoding: 'utf8' });
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
    const abs = resolve(root, v.src.replace(/\/$/, ''));
    if (!existsSync(abs)) throw new Error(`video not found: ${v.src}`);
    const inp = inputArgs(abs), st = statSync(inp.key);
    const key = createHash('sha1').update(`${v.src}|${st.size}|${st.mtimeMs}|${maxW}x${maxH}|${v.alpha}|${v.gray}|v3`).digest('hex').slice(0, 10);
    const dir = `${basename(v.src.replace(/\/$/, ''), extname(v.src)).replace(/[^\w-]/g, '_')}_${key}`;
    const out = join(base, dir), ext = v.alpha ? 'png' : 'jpg';
    const have = index[v.src];
    if (have && have.dir === dir && existsSync(join(out, '.done'))) continue;
    const p = probe(ffmpeg, abs);
    const sc = Math.min(1, maxW / p.w, maxH / p.h);
    const w = Math.max(2, Math.round(p.w * sc / 2) * 2), h = Math.max(2, Math.round(p.h * sc / 2) * 2);
    rmSync(out, { recursive: true, force: true }); mkdirSync(out, { recursive: true });
    log(`[prepare] ${v.src} → ${variant}/${dir} (${p.w}x${p.h} @ ${p.fps} fps → ${w}x${h}${v.gray ? ' gray' : ''}${v.alpha ? ' rgba png' : ''})`);
    const vf = [`fps=${p.fps}`, `scale=${w}:${h}:flags=lanczos`, v.gray ? 'format=gray' : v.alpha ? 'format=rgba' : 'format=yuvj444p'].join(',');
    const r = spawnSync(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-y', ...inp.args, '-vf', vf, '-fps_mode', 'cfr', ...(ext === 'jpg' ? ['-q:v', '2'] : []), join(out, `%06d.${ext}`)], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error(`ffmpeg failed extracting ${v.src}`);
    const frames = readdirSync(out).filter(f => f.endsWith('.' + ext)).length;
    // per-frame subject track for mattes / alpha sources: [cx, cy, topX, topY, bottomX, bottomY, area] (0..1 of frame)
    const track = (v.gray || v.alpha) ? computeTrack(ffmpeg, inp.args, p.fps, v.alpha) : null;
    if (track) writeFileSync(join(out, 'track.json'), JSON.stringify(track));
    writeFileSync(join(out, '.done'), '');
    index[v.src] = { dir, fps: p.fps, frames, w, h, ext, src: v.src, srcW: p.w, srcH: p.h, track: track ? `${dir}/track.json` : null };
  }
  writeFileSync(idxFile + '.tmp', JSON.stringify(index, null, 1)); renameSync(idxFile + '.tmp', idxFile);
  for (const k of Object.keys(index)) if (index[k].track && !existsSync(join(base, index[k].track))) index[k].track = null;
  return { index, cacheDir: `media/engine_cache/${variant}` };
}

// subject track from a matte (luma) or alpha channel at 128 px wide: area-weighted centroid, top and bottom points
// (2% / 98% of the mass from the top; x = centroid of that band). Pure function of the pixels.
export function computeTrack(ffmpeg, inArgs, fps, alpha = false) {
  const TW = 128;
  const probeR = spawnSync(ffmpeg, ['-hide_banner', ...inArgs], { encoding: 'utf8' });
  const wh = (probeR.stderr || '').match(/, (\d{2,5})x(\d{2,5})/); if (!wh) return null;
  const TH = Math.max(2, Math.round(TW * +wh[2] / +wh[1]));
  const vf = `fps=${fps},scale=${TW}:${TH}:flags=area,` + (alpha ? 'alphaextract,format=gray' : 'format=gray');
  const r = spawnSync(ffmpeg, ['-hide_banner', '-loglevel', 'error', ...inArgs, '-vf', vf, '-f', 'rawvideo', '-'], { maxBuffer: 1 << 30 });
  if (r.status !== 0) return null;
  const buf = r.stdout, n = TW * TH, frames = Math.floor(buf.length / n), out = [];
  for (let f = 0; f < frames; f++) {
    const o = f * n; let sum = 0, sx = 0, sy = 0; const rows = new Float64Array(TH);
    for (let y = 0; y < TH; y++) for (let x = 0; x < TW; x++) { const v = buf[o + y * TW + x] / 255; if (v < 0.25) continue; sum += v; sx += v * x; sy += v * y; rows[y] += v; }
    if (sum <= 0) { out.push([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0]); continue; }
    const band = (fr0, fr1) => { let acc = 0, y0 = -1, y1 = -1; for (let y = 0; y < TH; y++) { acc += rows[y]; if (y0 < 0 && acc >= sum * fr0) y0 = y; if (y1 < 0 && acc >= sum * fr1) { y1 = y; break; } }
      let bx = 0, bw = 0; for (let y = Math.max(0, y0); y <= Math.max(y0, y1); y++) for (let x = 0; x < TW; x++) { const v = buf[o + y * TW + x] / 255; if (v < 0.25) continue; bx += v * x; bw += v; }
      return [(bw ? bx / bw : sx / sum) / TW, (y0 + 0.5) / TH]; };
    const top = band(0.0, 0.02), bot = band(0.98, 1.0);
    out.push([+(sx / sum / TW).toFixed(4), +(sy / sum / TH).toFixed(4), +top[0].toFixed(4), +top[1].toFixed(4), +bot[0].toFixed(4), +bot[1].toFixed(4), +(sum / n).toFixed(5)]);
  }
  return out;
}
