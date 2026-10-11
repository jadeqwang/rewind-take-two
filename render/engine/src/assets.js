// assets.js: deterministic, miss-driven image loading (pattern from rewind-music-video/render/src/roto.js).
//
// get(url) returns a cached ImageBitmap, or null and records a miss. The engine draws the frame, awaits the misses,
// and draws again, so pixels never depend on cache state or load timing. prefetch() warms upcoming video frames in the
// background (it never changes the current frame). An LRU bounds memory.
//
// Video layers read pre-extracted frame sequences (render.mjs prepares them with ffmpeg into media/engine_cache/<variant>/):
//   index.json = { "<src path>": { dir, fps, frames, w, h, ext } }
const cache = new Map();      // url → {bmp, last}
const pending = new Map();
let clock = 0, MAX = 360;
export const misses = new Set();
export const stats = { loads: 0, failed: [] };
let videoIndex = {}, cacheBase = '';

export function configure({ max, index, base }) { if (max) MAX = max; if (index) videoIndex = index; if (base !== undefined) cacheBase = base; }
export const url = p => (/^(https?:|data:|blob:|\/)/.test(p) ? p : '/' + p);   // repo-root relative paths

function evict() {
  if (cache.size <= MAX) return;
  const old = [...cache.entries()].sort((a, b) => a[1].last - b[1].last).slice(0, cache.size - MAX + 32);
  for (const [k, v] of old) { if (v.bmp && v.bmp.close) v.bmp.close(); cache.delete(k); }
}
export function load(u) {
  if (cache.has(u)) return Promise.resolve(cache.get(u).bmp);
  if (pending.has(u)) return pending.get(u);
  const p = fetch(u).then(r => { if (!r.ok) throw new Error(r.status + ' ' + u); return r.blob(); })
    .then(b => createImageBitmap(b, { premultiplyAlpha: 'none', colorSpaceConversion: 'none' }))
    .then(bmp => { stats.loads++; cache.set(u, { bmp, last: ++clock }); pending.delete(u); evict(); return bmp; })
    .catch(e => { stats.failed.push(u); console.error('asset failed: ' + e.message); cache.set(u, { bmp: null, last: ++clock }); pending.delete(u); return null; });
  pending.set(u, p);
  return p;
}
// synchronous lookup; a miss is recorded and resolved by the engine before the frame is accepted
export function get(path) {
  const u = url(path), e = cache.get(u);
  if (e) { e.last = ++clock; return e.bmp; }
  misses.add(u); return null;
}
export async function resolveMisses() { const l = [...misses]; misses.clear(); await Promise.all(l.map(load)); return l.length; }

// ---- video frame sequences ----
export function videoMeta(src) {
  const m = videoIndex[src];
  if (!m) throw new Error(`video "${src}" is not prepared (render.mjs extracts every video/matte the timeline names; is the src a static string?)`);
  return m;
}
export const frameUrl = (m, i) => `${cacheBase}/${m.dir}/${String(i + 1).padStart(6, '0')}.${m.ext || 'jpg'}`;
export function frameIndex(m, srcT, mode = 'floor') {
  const x = srcT * m.fps;
  const i = mode === 'round' ? Math.round(x) : Math.floor(x + 1e-4);
  return Math.max(0, Math.min(m.frames - 1, i));
}
export function videoFrame(src, i) { const m = videoMeta(src); return get(frameUrl(m, Math.max(0, Math.min(m.frames - 1, i)))); }
export function prefetchVideo(src, i0, dir = 1, n = 12) {
  const m = videoIndex[src]; if (!m) return;
  for (let k = 0; k < n; k++) { const i = i0 + k * Math.sign(dir || 1); if (i < 0 || i >= m.frames) break; load(frameUrl(m, i)); }
}
