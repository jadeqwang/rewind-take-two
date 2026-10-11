// engine.js: boot, timeline normalisation, layer evaluation, deterministic renderFrame(i).
// Page query: ?render &timeline=<repo path> &w &h &cache=<repo path of the prepared video cache> &timing=<repo path>
//             &q (jpeg quality) — see render.mjs, which drives this page in headless Chrome.
import { Compositor } from './compositor.js';
import { TimeMap, TIMING_PATHS } from './timing.js';
import * as A from './assets.js';
import { val, integrate, vals } from './keys.js';
import { evalFx, contentTime, defaults, events, pulse } from './fx.js';
import * as core from './core.js';
import { DW, DH, FPS, clamp, hash, rng } from './core.js';

const Q = new URLSearchParams(location.search);
export const W = +(Q.get('w') || 1920), H = +(Q.get('h') || 1080), S = H / DH;
const E = window.E = { ready: false, W, H, S, fps: FPS, shots: [], overlays: [], inst: new Map(), lastVideo: [] };

// ------------------------------------------------------------------ boot
async function getJSON(paths) {
  for (const p of paths) { try { const r = await fetch(A.url(p), { cache: 'no-store' }); if (r.ok) return { path: p, json: await r.json() }; } catch (e) { /* next */ } }
  return null;
}
// every face the kit uses (OFL, vendored in render/fonts/); timelines may add more with `fonts: [{family, src, weight, style}]`
export const FONT_FILES = [
  { family: 'IM Fell English', src: 'IMFeENrm28P.ttf' }, { family: 'IM Fell English', src: 'IMFeENit28P.ttf', style: 'italic' },
  { family: 'Overpass', src: 'Overpass-wght.ttf', weight: '100 900' }, { family: 'Press Start 2P', src: 'PressStart2P-Regular.ttf' },
  { family: 'IBM Plex Mono', src: 'IBMPlexMono-Regular.ttf', weight: '400' }, { family: 'IBM Plex Mono', src: 'IBMPlexMono-Bold.ttf', weight: '700' },
  { family: 'Reenie Beanie', src: 'ReenieBeanie.ttf' }, { family: 'Anton', src: 'anton-latin-400-normal.woff2' },
  { family: 'JetBrains Mono', src: 'jetbrains-mono-latin-400-normal.woff2', weight: '400' }, { family: 'JetBrains Mono', src: 'jetbrains-mono-latin-700-normal.woff2', weight: '700' },
  { family: 'CMU Serif', src: 'cmu-serif-500-italic.ttf', style: 'italic', weight: '500' },
];
async function loadFonts(extra = []) {
  for (const f of [...FONT_FILES.map(f => ({ ...f, src: 'render/fonts/' + f.src })), ...extra]) {
    const ff = new FontFace(f.family, `url(${A.url(f.src)})`, { weight: f.weight || 'normal', style: f.style || 'normal' });
    document.fonts.add(await ff.load());
  }
  await document.fonts.ready;
}
// module paths: 'hud' → render/engine/modules/hud.js; 'render/x.js' (repo-relative); './x.js' (relative to the timeline file)
function modulePath(p, tlDir) {
  if (/^[\w-]+$/.test(p)) return `/render/engine/modules/${p}.js`;
  if (p.startsWith('./') || p.startsWith('../')) return new URL(p, location.origin + '/' + tlDir + '/').pathname;
  return A.url(p);
}

const asArr = x => (x === undefined || x === null ? [] : Array.isArray(x) ? x : [x]);
function fxList(fx) { if (!fx) return []; if (Array.isArray(fx)) return fx.map(f => ({ ...f })); return Object.entries(fx).map(([type, f]) => ({ type, ...(f === true ? {} : f) })); }
const localT = (x, origin, T) => (x === undefined ? undefined : typeof x === 'number' ? x : T.time(x) - origin);

function normLayer(l, shot, i, T, tlDir) {
  l = { ...l };
  if (!l.type) l.type = l.module ? 'canvas' : /\.(mp4|webm|mov|mkv)$/i.test(l.src || '') ? 'video' : l.src ? 'image' : l.color ? 'solid' : l.layers ? 'parallax' : 'solid';
  l.id = l.id || `${shot.id}.${i}`;
  l._key = `${shot.id}/${l.id}`;                    // unique across shots (texture slots, rng seeds stay per-id)
  l._start = localT(l.start, shot.start, T) ?? 0;
  l._end = localT(l.end, shot.start, T) ?? 1e9;
  if (l.freeze !== undefined) l._freeze = localT(l.freeze, shot.start + l._start, T);
  if (l.module) l._modPath = modulePath(l.module, tlDir);
  if (l.kenBurns) {      // sugar: {from:{scale,x,y,rotate}, to:{...}, ease, dur}
    const kb = l.kenBurns, d = kb.dur ?? Math.min(l._end, shot.end - shot.start) - l._start;
    for (const k of ['scale', 'x', 'y', 'rotate']) if (kb.from?.[k] !== undefined || kb.to?.[k] !== undefined) l[k] = [[0, kb.from?.[k] ?? kb.to[k], kb.ease || 'inOutSine'], [d, kb.to?.[k] ?? kb.from[k]]];
  }
  if (l.type === 'comp' && Array.isArray(l.srcTime)) l.srcTime = l.srcTime.map(k => [k[0], typeof k[1] === 'string' ? T.time(k[1]) : k[1], ...k.slice(2)]);
  if (l.type === 'parallax') l.layers = (l.layers || []).map((c, k) => ({ fit: 'height', repeat: [true, false], ...c, id: `${l.id}.p${k}`, _key: `${l._key}.p${k}` }));
  if (l.type === 'ghosts') l._instances = ghostInstances(l);
  return l;
}
function normShots(list, T, tlDir, kind) {
  const out = [];
  list.forEach((s, i) => {
    const prev = out[out.length - 1];
    const start = s.start !== undefined ? T.time(s.start) : prev ? prev.end : 0;
    const shot = { ...s, id: s.id || `${kind}${i}`, start };
    shot.end = s.end !== undefined ? T.time(s.end) : s.dur !== undefined ? start + T.dur(start, s.dur) : undefined;
    out.push(shot);
  });
  out.forEach((s, i) => { if (s.end === undefined) s.end = out[i + 1] ? out[i + 1].start : s.start + 4; s._overlay = kind === 'overlay'; });
  for (const s of out) {
    if (!(s.end > s.start)) throw new Error(`${kind} "${s.id}": end (${s.end}) must be after start (${s.start})`);
    s._fx = fxList(s.fx);
    for (const f of s._fx) { if (f.at !== undefined && (f.type === 'tapeStop' || f.type === 'hold')) f._at = localT(f.at, s.start, T); if (f.until !== undefined) f._until = localT(f.until, s.start, T); }
    s.layers = asArr(s.layers).map((l, i) => normLayer(l, s, i, T, tlDir));
  }
  const ids = new Set(); for (const s of out) { if (ids.has(s.id)) throw new Error(`duplicate ${kind} id "${s.id}"`); ids.add(s.id); }
  return out.sort((a, b) => a.start - b.start);
}

// Module instances are created lazily on first draw (so a 228 s timeline with hundreds of text layers costs nothing up
// front) and share one W×H canvas / one render target per MSAA setting: each layer is drawn and composited before the
// next one starts. Instances whose module exports dispose() are released after 4 s unused (heavy 3D scenes).
const MODS = new Map();
async function loadModule(l) {
  let raw = MODS.get(l._modPath);
  if (!raw) { raw = await import(l._modPath); MODS.set(l._modPath, raw); }
  if (!(raw.createScene || raw.create || typeof raw.draw === 'function')) throw new Error(`module ${l.module} (layer ${l.id}) exports neither draw() nor createScene()/create()`);
  return raw;
}
function sharedCanvas() {
  if (!E.canvas) { E.canvas = document.createElement('canvas'); E.canvas.width = W; E.canvas.height = H; E.ctx = E.canvas.getContext('2d'); }
  return E.canvas;
}
async function ensureInst(l, shot) {
  let inst = E.inst.get(l);
  if (!inst) {
    const raw = await loadModule(l);
    const factory = raw.createScene || raw.create;
    const mod = factory ? await factory(l.params || {}) : raw;
    inst = { mod, state: null };
    if (l.linear === undefined && (raw.output === 'srgb' || raw.meta?.output === 'srgb')) l.linear = false;
    const env = { params: l.params || {}, T: E.T, W: DW, H: DH, S, layer: l, shot, rng: (...s) => rng(l.id, ...s), core, assets: A,
      loadImage: p => A.load(A.url(p)), loadJSON: async p => (await fetch(A.url(p))).json() };
    if (l.type === 'canvas') { sharedCanvas(); if (mod.init) inst.state = (await mod.init(E.ctx, l.params || {}, env)) ?? null; }
    else if (mod.init) inst.state = (await mod.init(E.comp.renderer, l.params || {}, { ...env, THREE: await import('three') })) ?? null;
    if (typeof mod.draw !== 'function') throw new Error(`module ${l.module} (layer ${l.id}) has no draw()`);
    E.inst.set(l, inst);
  }
  inst.last = E.frame;
  return inst;
}
function sweepModules() {
  for (const [l, inst] of E.inst) if (inst.mod.dispose && inst.last < E.frame - 96) { try { inst.mod.dispose(); } catch (e) { /* ignore */ } E.inst.delete(l); }
}

// timeline ctx: helpers a timeline function gets (render.mjs passes Node equivalents)
const timelineCtx = (T, bust) => ({
  T, core,
  list: async dir => { const r = await fetch('/__ls/' + dir, { cache: 'no-store' }); return r.ok ? r.json() : []; },
  importModule: p => import(A.url(p) + bust),
  readJSON: async p => { const r = await fetch(A.url(p), { cache: 'no-store' }); if (!r.ok) throw new Error(`${p}: HTTP ${r.status}`); return r.json(); },
});

export async function boot() {
  const tlPath = Q.get('timeline') || 'render/timeline.js';
  const tlDir = tlPath.split('/').slice(0, -1).join('/');
  const tm = await getJSON(Q.get('timing') ? [Q.get('timing')] : TIMING_PATHS);
  if (!tm) throw new Error('no timing JSON found (' + TIMING_PATHS.join(', ') + ')');
  E.T = new TimeMap(tm.json, { source: tm.path });
  if (E.T.isStub) console.warn(`[timing] using ${tm.path} (stub; analysis/cinematic/timing.json not found)`);
  const mod = await import(A.url(tlPath) + (Q.has('v') ? '?v=' + Q.get('v') : ''));
  let tl = mod.default ?? mod.timeline;
  if (typeof tl === 'function') tl = await tl(timelineCtx(E.T, Q.has('v') ? '?v=' + Q.get('v') : ''));
  E.tl = tl;
  await loadFonts(tl.fonts || []);
  E.shots = normShots(asArr(tl.shots), E.T, tlDir, 'shot');
  E.overlays = normShots(asArr(tl.overlays), E.T, tlDir, 'overlay');
  E.globalFx = fxList(tl.fx);
  E.background = tl.background || '#000000';
  const idx = Q.get('cache') ? await getJSON([Q.get('cache') + '/index.json']) : null;
  A.configure({ index: idx ? idx.json : {}, base: Q.get('cache') ? A.url(Q.get('cache')) : '' });
  if (idx) for (const v of Object.values(idx.json)) if (typeof v.track === 'string') v.track = await (await fetch(A.url(Q.get('cache') + '/' + v.track))).json();
  E.out = document.getElementById('out'); E.out.width = W; E.out.height = H;
  E.comp = new Compositor(E.out, W, H);
  for (const s of [...E.shots, ...E.overlays]) for (const l of s.layers) if (l._modPath) await loadModule(l);   // fail fast on bad module paths
  E.range = [E.T.time(tl.range?.[0] ?? E.shots[0]?.start ?? 0), E.T.time(tl.range?.[1] ?? E.shots[E.shots.length - 1]?.end ?? 0)];
  window.timingInfo = { timing: tm.path, stub: E.T.isStub, gl: E.comp.info, shots: E.shots.length, overlays: E.overlays.length, range: E.range, W, H };
  E.ready = true; window.ready = true;
  return E;
}

// ------------------------------------------------------------------ evaluation
export function shotAt(t, exclude = null) {
  let r = null;
  for (const s of E.shots) if (t >= s.start - 1e-9 && t < s.end - 1e-9 && s !== exclude) r = s;
  return r;
}
const shotById = id => E.shots.find(s => s.id === id) || E.overlays.find(s => s.id === id);

// placement: inverse affine from design px to layer unit coords, plus the source crop
function placement(l, srcW, srcH, env) {
  const V = (x, d) => { const v = val(x, env.lt, env, d); return v === undefined ? d : v; };
  const crop = V(l.crop, [0, 0, 1, 1]);
  const cw = srcW * (crop[2] - crop[0]), ch = srcH * (crop[3] - crop[1]);
  const rect = V(l.rect, null);
  let w, h, px = DW / 2, py = DH / 2;
  if (rect) { w = rect[2]; h = rect[3]; px = rect[0] + w / 2; py = rect[1] + h / 2; }
  else {
    const fit = l.fit || 'cover';
    const s = fit === 'cover' ? Math.max(DW / cw, DH / ch) : fit === 'contain' ? Math.min(DW / cw, DH / ch) : fit === 'height' ? DH / ch : fit === 'width' ? DW / cw : fit === 'none' ? V(l.pxScale, 1) : 1;
    if (fit === 'stretch') { w = DW; h = DH; } else { w = cw * s; h = ch * s; }
  }
  const sc = V(l.scale, 1), sx = Array.isArray(sc) ? sc[0] : sc, sy = Array.isArray(sc) ? sc[1] : sc;
  const anchor = V(l.anchor, [0.5, 0.5]);
  px += V(l.x, 0) + (env.parallaxX || 0); py += V(l.y, 0);
  const r = V(l.rotate, 0) * Math.PI / 180, cs = Math.cos(r), sn = Math.sin(r);
  const a = cs / (sx * w), b = sn / (sx * w), d = -sn / (sy * h), e = cs / (sy * h);
  return { inv: [a, b, -(a * px + b * py) + anchor[0], d, e, -(d * px + e * py) + anchor[1], 0, 0, 1], crop: [crop[0], crop[1], crop[2] - crop[0], crop[3] - crop[1]] };
}

function layerEnv(base, l, clock) {
  const lt = clock - l._start;
  const env = { ...base, layer: l, params: l.params || {}, origin: base.origin + l._start, layerEnd: base.origin + Math.min(l._end, base.dur) };
  env.lt = l.time !== undefined ? val(l.time, lt, env) : lt;
  env.val = (x, d) => { const v = val(x, env.lt, env, d); return v === undefined ? d : v; };
  env.rng = (...s) => rng(l.id, ...s);
  env.state = E.inst.get(l)?.state ?? null;
  env.follow = spec => { const f = followFn(base, l, spec); return tau => f(tau + l._start); };
  return env;
}
function opacityOf(l, env, lt, dur) {
  let o = env.val(l.opacity, 1);
  if (l.fadeIn && lt < l.fadeIn) o *= clamp(lt / l.fadeIn);
  if (l.fadeOut && lt > dur - l.fadeOut) o *= clamp((dur - lt) / l.fadeOut);
  return o;
}
const MATTE = { luma: 1, alpha: 2, lumaInv: 3, alphaInv: 4 };

function videoSrcTime(l, env, m) {
  let x = env.lt; if (l._freeze !== undefined) x = Math.min(x, l._freeze);
  let st = l.srcTime !== undefined ? val(l.srcTime, x, env) : env.val(l.in, 0) + integrate(l.rate ?? 1, x, env);
  const D = m.frames / m.fps;
  if (l.loop === 'pingpong') { const p = ((st % (2 * D)) + 2 * D) % (2 * D); st = p < D ? p : 2 * D - p; }
  else if (l.loop) st = ((st % D) + D) % D;
  return clamp(st, 0, D - 0.5 / m.fps);
}

// ---- ghosts: one matted clip drawn many times (hue/colour, opacity, time offset, placement per instance) ----
// Instances that land on the same source frame share one texture upload, so 100 ghosts with offsets quantised to a
// dozen frames cost a dozen decodes. Explicit `instances` or a seeded `generate` spec (see README).
function ghostInstances(l) {
  if (Array.isArray(l.instances)) return l.instances.map((g, k) => ({ i: k, x: 0, y: 0, scale: 1, opacity: l.opacity ?? 0.55, ...g }));
  const G = l.generate || {}, n = G.count ?? 13, r = rng(l.id, G.seed ?? 1);
  const area = G.area || [-700, -220, 700, 220], sc = G.scale || [0.8, 1.05], op = G.opacity || [0.35, 0.6], off = G.offset || [0, 0];
  const colors = G.colors || core.KANDINSKY, q = G.quantize ?? 1 / 12;
  const out = [];
  for (let k = 0; k < n; k++) {
    const u = r(), v = r(), w = r(), z = r(), f = r(), o = r();
    out.push({ i: k, x: area[0] + (area[2] - area[0]) * u, y: area[1] + (area[3] - area[1]) * v, scale: sc[0] + (sc[1] - sc[0]) * w,
      opacity: op[0] + (op[1] - op[0]) * z, flip: G.flip !== false && f < 0.5, offset: Math.round((off[0] + (off[1] - off[0]) * o) / q) * q,
      color: colors[k % colors.length] });
  }
  if (G.sort !== false) out.sort((a, b) => a.y - b.y);       // lower on screen = nearer = drawn last
  return out;
}
function ghostOps(l, env, base) {
  const m = A.videoMeta(l.src), mm = l.matte ? A.videoMeta(l.matte.src || l.matte) : null, D = m.frames / m.fps;
  const baseSt = videoSrcTime(l, env, m);
  // how many are visible: `show` keyframes (fractional = the next one fading in) or one more per event (`on`)
  const all = l._instances;
  let show = all.length;
  if (l.show !== undefined) show = env.val(l.show, all.length);
  else if (l.on) show = events(env.T, l.on, env.t - env.lt - 1e-6, env.t).length;
  const pop = l.on ? env.pulse(l.on, 0.12) : 0;
  const ordered = [...all].sort((a, b) => a.i - b.i).slice(0, Math.ceil(show));
  const vis = new Set(ordered.map(g => g.i));
  const ops = [];
  const lx = env.val(l.x, 0), ly = env.val(l.y, 0), lsRaw = env.val(l.scale, 1), ls = Array.isArray(lsRaw) ? lsRaw[0] : lsRaw;
  const amt = env.val(l.tint, 0.65);
  for (const g of all) {
    if (!vis.has(g.i)) continue;
    let fade = clamp(show - g.i);                               // the newest one fades in
    let sT = g.freeze !== undefined ? g.freeze : baseSt + (g.offset || 0);
    if (l.loop !== false) sT = ((sT % D) + D) % D; else sT = clamp(sT, 0, D - 0.5 / m.fps);
    const i = Math.max(0, Math.min(m.frames - 1, Math.floor(sT * m.fps + 1e-4)));
    const bmp = A.get(A.frameUrl(m, i)); if (!bmp) continue;
    const op = { ...base, blend: g.blend || l.blendMode || base.blend, tex: E.comp.tex(`gh:${l.src}:${i}`, bmp) };
    if (mm) { const mi = Math.max(0, Math.min(mm.frames - 1, Math.floor(sT * mm.fps + 1e-4))); const mb = A.get(A.frameUrl(mm, mi)); if (!mb) continue; op.matte = E.comp.tex(`ghm:${l.matte.src || l.matte}:${mi}`, mb); op.matteMode = MATTE[l.matte.mode || 'luma']; }
    else if (l.key) op.key = vals(l.key, env.lt, env);
    const s = ls * (g.scale ?? 1);
    Object.assign(op, placement({ ...l, x: lx + (g.x || 0), y: ly + (g.y || 0), scale: [g.flip ? -s : s, s] }, bmp.width, bmp.height, env));
    op.grade = { ...(base.grade || {}), ...(g.grade || {}), hue: g.hue ?? base.grade?.hue, colorize: g.color, colorizeAmount: g.tint ?? amt };
    const isNew = g.i === ordered.length - 1 && l.on ? pop : 0;
    op.opacity = (g.opacity ?? 0.55) * fade * (1 + 0.8 * isNew);
    ops.push(op);
  }
  return ops;
}

// ---- follow: a design-space point riding a video layer's matte (centroid / top / bottom), smoothed over ±n frames ----
function findLayer(shot, id) { return shot.layers.find(x => x.id === id || x.id === `${shot.id}.${id}`); }
const TRACK_PT = { centroid: [0, 1], top: [2, 3], bottom: [4, 5] };
function followFn(base, self, spec) {
  if (typeof spec === 'string') spec = { layer: spec };
  const target = findLayer(base.shot, spec.layer);
  if (!target || !['video', 'ghosts'].includes(target.type)) throw new Error(`follow: no video layer "${spec.layer}" in shot ${base.shot.id}`);
  const m = A.videoMeta(target.src);
  const tsrc = spec.matte || (target.matte && (target.matte.src || target.matte)) || target.src;
  const tm = A.videoMeta(tsrc);
  if (!tm.track) throw new Error(`follow: no track data for ${tsrc} (render.mjs computes it for mattes and alpha sources)`);
  const [ix, iy] = TRACK_PT[spec.point || 'centroid'], sm = spec.smooth ?? 3, off = spec.offset || [0, 0], minA = spec.minArea ?? 0.002;
  return clock => {
    const env = layerEnv(base, target, clock);
    const st = videoSrcTime(target, env, m), fi = Math.round(st * tm.fps);
    let sx = 0, sy = 0, sw = 0;
    for (let k = -sm; k <= sm; k++) {
      const p = tm.track[Math.max(0, Math.min(tm.track.length - 1, fi + k))];
      if (!p || p[6] < minA) continue;
      const w = sm + 1 - Math.abs(k); sx += p[ix] * w; sy += p[iy] * w; sw += w;
    }
    if (!sw) return null;
    const pl = placement(target, m.w, m.h, env), [a, b, c, d, e, f] = pl.inv, cr = pl.crop;
    const u = (sx / sw - cr[0]) / cr[2], v = (sy / sw - cr[1]) / cr[3], det = a * e - b * d;
    return [(e * (u - c) - b * (v - f)) / det + off[0], (a * (v - f) - d * (u - c)) / det + off[1]];
  };
}

// produce draw ops for one layer (may draw nested comps / modules as a side effect)
async function layerOps(l, env, depth) {
  const comp = E.comp, ops = [];
  const base = { blend: l.blend || 'normal', key: l.key ? vals(l.key, env.lt, env) : null, grade: l.grade ? vals(l.grade, env.lt, env) : null };
  if (l.type === 'solid') ops.push({ ...base, solid: env.val(l.color, '#000000'), ...placement({ fit: 'stretch', ...l }, DW, DH, env) });
  else if (l.type === 'image') {
    const bmp = A.get(l.src); if (!bmp) return ops;
    ops.push({ ...base, tex: comp.tex('img:' + l._key, bmp), ...placement(l, bmp.width, bmp.height, env), repeat: l.repeat });
  } else if (l.type === 'parallax') {
    const scroll = l.speed !== undefined ? env.val(l.speed, 0) * env.lt : env.val(l.scroll, 0);
    for (const c of l.layers) {
      const bmp = A.get(c.src); if (!bmp) continue;
      const cenv = { ...env, parallaxX: -scroll * (c.depth ?? 1) };
      ops.push({ ...base, blend: c.blend || 'normal', grade: c.grade ? vals(c.grade, env.lt, env) : base.grade, tex: comp.tex('img:' + c._key, bmp),
        ...placement(c, bmp.width, bmp.height, cenv), repeat: c.repeat, opacity: val(c.opacity, env.lt, env, 1) });
    }
  } else if (l.type === 'video') {
    const m = A.videoMeta(l.src);
    const st = videoSrcTime(l, env, m);
    const st2 = videoSrcTime(l, { ...env, lt: env.lt - 1 / 48 }, m), dir = st >= st2 ? 1 : -1;
    const frameOp = (sT, slot) => {
      const x = sT * m.fps, i0 = Math.max(0, Math.min(m.frames - 1, Math.floor(x + 1e-4)));
      const b0 = A.get(A.frameUrl(m, i0)); if (!b0) return null;
      const op = { ...base, tex: comp.tex(`vid:${l._key}:${slot}`, b0), ...placement(l, b0.width, b0.height, env) };
      if (l.frameBlend) { const f = x - Math.floor(x); const i1 = Math.min(m.frames - 1, i0 + 1); if (f > 1e-3 && i1 !== i0) { const b1 = A.get(A.frameUrl(m, i1)); if (!b1) return null; op.tex2 = comp.tex(`vid:${l._key}:${slot}b`, b1); op.mix = f; } }
      if (l.matte) {
        const mm = A.videoMeta(l.matte.src || l.matte);
        const mi = Math.max(0, Math.min(mm.frames - 1, Math.floor((sT + (l.matte.offset || 0)) * mm.fps + 1e-4)));
        const mb = A.get(A.frameUrl(mm, mi)); if (!mb) return null;
        op.matte = comp.tex(`mat:${l._key}:${slot}`, mb); op.matteMode = MATTE[l.matte.mode || 'luma'];
      }
      E.lastVideo.push({ src: l.src, i: i0, dir }); if (l.matte) E.lastVideo.push({ src: l.matte.src || l.matte, i: Math.floor(sT * A.videoMeta(l.matte.src || l.matte).fps), dir });
      return op;
    };
    const ech = l.echo ? vals(l.echo, env.lt, env) : null;
    if (ech && ech.n > 0) {
      for (let k = ech.n; k >= 1; k--) {          // ghosts of the frames it just came from, oldest first
        const op = frameOp(clamp(st - dir * k * (ech.dt ?? 0.08), 0, m.frames / m.fps), 'e' + k); if (!op) continue;
        op.blend = ech.blend || 'screen'; op.opacity = (ech.alpha ?? 0.35) * (1 - (k - 1) / ech.n); ops.push(op);
      }
    }
    const op = frameOp(st, 'm'); if (op) ops.push(op);
    env._srcT = st;
  } else if (l.type === 'canvas') {
    const inst = await ensureInst(l, env.shot), cv = sharedCanvas(), g = E.ctx;
    env.state = inst.state;
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.shadowBlur = 0; g.letterSpacing = '0px'; g.clearRect(0, 0, W, H);
    g.setTransform(S, 0, 0, S, 0, 0);
    g.save(); await inst.mod.draw(env.lt, { ...env, ctx: g, canvas: cv }); g.restore();
    ops.push({ ...base, tex: comp.tex('cv:shared', cv, { mips: false }), ...placement({ fit: 'stretch', ...l }, DW, DH, env) });
  } else if (l.type === 'three') {
    const inst = await ensureInst(l, env.shot), r = comp.renderer, rt = comp.rt('three:s' + (l.samples ?? 4), { depth: true, samples: l.samples ?? 4 });
    env.state = inst.state;
    comp.clear(rt);
    r.setRenderTarget(rt);
    await inst.mod.draw(env.lt, { ...env, renderer: r, target: rt });
    r.setRenderTarget(null); r.autoClear = false;
    ops.push({ ...base, tex: rt.texture, flip: true, premul: true, linear: l.linear ?? true, ...placement({ fit: 'stretch', ...l }, DW, DH, env) });
  } else if (l.type === 'ghosts') {
    ops.push(...ghostOps(l, env, base));
  } else if (l.type === 'comp') {
    if (depth >= 2) throw new Error(`comp layer ${l.id}: nesting deeper than 2`);
    const ech = l.echo ? vals(l.echo, env.lt, env) : null;
    if (l.srcTime === undefined) throw new Error(`comp layer ${l.id} needs srcTime (keyframes: layer time → absolute song time)`);
    const abs = v => (typeof v === 'string' ? E.T.time(v) : v);
    const srcT = abs(env.val(l.srcTime));                  // absolute song time to show
    const pick = tt => (l.source && l.source !== 'film' ? shotById(l.source) : shotAt(tt, env.shot));
    const one = async (tt, slot) => {
      let sh = pick(tt), guard = 0;
      while (sh && (sh.noRewind || sh.layers.some(x => x.type === 'comp')) && guard++ < 16) sh = shotAt(sh.start - 1e-3, env.shot);   // skip other comps
      if (!sh) return null;
      const rt = comp.rt(`nest${depth}:${slot}`);
      await renderShotLayers(sh, Math.min(tt, sh.end - 1e-4), rt, null, depth + 1, 'pre');
      return { ...base, tex: rt.texture, flip: true, premul: true, ...placement({ fit: 'stretch', ...l }, DW, DH, env) };
    };
    env._srcT = srcT;
    if (ech && ech.n > 0) {
      const dir = Math.sign(abs(val(l.srcTime, env.lt + 0.02, env)) - srcT) || -1;
      for (let k = ech.n; k >= 1; k--) {
        const op = await one(srcT - dir * k * (ech.dt ?? 0.1), 'e'); if (!op) continue;
        op.blend = ech.blend || 'screen'; op.opacity = (ech.alpha ?? 0.3) * (1 - (k - 1) / ech.n);
        await emit([op], env);   // the nested target is reused per echo, so composite immediately
      }
    }
    const op = await one(srcT, 'm'); if (op) ops.push(op);
  } else throw new Error(`unknown layer type "${l.type}" (${l.id})`);
  return ops;
}

// draw ops into the current pass target (+ the isolation mask)
let PASS = null;
async function emit(ops, env) {
  for (const op of ops) {
    op.opacity = (op.opacity ?? 1) * env._opacity;
    E.comp.drawLayer(op, PASS.target);
    if (PASS.mask) E.comp.drawLayer({ ...op, mode: 'coverage', blend: env.layer.keepColor ? 'normal' : 'erase' }, PASS.mask);
  }
}

// render a shot's layers of one stage at absolute time t into target (cleared first when clear)
async function renderShotLayers(shot, t, target, mask, depth, stage, clear = true) {
  const lt = t - shot.start;
  const baseEnv = { t, frameT: E.frameT, frame: E.frame, fps: FPS, T: E.T, W: DW, H: DH, S, shot, dur: shot.end - shot.start, origin: shot.start, depth,
    rewinding: depth > 0, core, assets: A, lyric: (opt) => E.T.lyric(t, opt), pulse: (on, decay = 0.12) => pulse(E.T, on, t, decay, shot.start), events: (on) => events(E.T, on, shot.start, t) };
  const ct = contentTime(shot, lt, baseEnv);
  const saved = PASS;
  PASS = { target, mask };
  if (clear) { E.comp.clear(target); if (mask) E.comp.clear(mask); }
  if (stage === 'pre' && !shot._overlay) await emit([{ solid: shot.background || E.background, inv: [1 / DW, 0, 0, 0, 1 / DH, 0, 0, 0, 1] }], { _opacity: 1, layer: {} });
  for (const l of shot.layers) {
    if ((l.stage || (shot._overlay ? 'post' : 'pre')) !== stage) continue;
    if (depth > 0 && l.noRewind) continue;
    const clock = l.realtime ? lt : ct;
    if (clock < l._start - 1e-9 || clock >= l._end - 1e-9) continue;
    const env = layerEnv(baseEnv, l, clock);
    env._opacity = opacityOf(l, env, clock - l._start, Math.min(l._end, shot.end - shot.start) - l._start);
    if (env._opacity <= 0.001) continue;
    const ops = await layerOps(l, env, depth);
    await emit(ops, env);
  }
  PASS = saved;
  return ct;
}

async function drawFrame(i) {
  const t = i / FPS; E.frame = i; E.frameT = t; E.lastVideo = [];
  const comp = E.comp, shot = shotAt(t);
  const overlays = E.overlays.filter(o => t >= o.start - 1e-9 && t < o.end - 1e-9);
  const rtComp = comp.rt('comp'), rtPost = comp.rt('post');
  let P;
  if (shot) {
    const env = { T: E.T, origin: shot.start };
    P = evalFx(shot, E.globalFx, t - shot.start, t, i, E.T, env);
    const mask = P.iso > 0 || P.neg > 0 ? comp.rt('mask') : null;
    await renderShotLayers(shot, t, rtComp, mask, 0, 'pre');
    for (const o of overlays) await renderShotLayers(o, t, rtComp, mask, 0, 'pre', false);
    comp.post(rtComp, mask, rtPost, P);
    await renderShotLayers(shot, t, rtPost, null, 0, 'post', false);
  } else {
    P = defaults(); P.time = t;
    comp.clear(rtPost); PASS = { target: rtPost }; await emit([{ solid: E.background, inv: [1 / DW, 0, 0, 0, 1 / DH, 0, 0, 0, 1] }], { _opacity: 1, layer: {} }); PASS = null;
  }
  for (const o of overlays) await renderShotLayers(o, t, rtPost, null, 0, 'post', false);
  comp.final(rtPost, P);
  return { shot, P };
}

// deterministic frame: draw, load whatever was missing, draw again
export async function renderFrame(i) {
  let r;
  for (let pass = 0; pass < 6; pass++) {
    E.rand = rng('frame', i); A.misses.clear();
    r = await drawFrame(i);
    if (!A.misses.size) break;
    await A.resolveMisses();
    if (pass === 5) throw new Error('frame ' + i + ': assets still missing after 6 passes');
  }
  if (A.stats.failed.length) throw new Error('assets failed to load: ' + [...new Set(A.stats.failed)].slice(0, 5).join(', '));
  for (const v of E.lastVideo) A.prefetchVideo(v.src, v.i + v.dir, v.dir, 8);     // warms the cache only; never changes pixels
  E.comp.sweep(); sweepModules();
  return r;
}

// ------------------------------------------------------------------ page API (render.mjs drives these)
let chain = Promise.resolve();
const serial = fn => (chain = chain.then(fn, fn));
const blob = (type, q) => new Promise(res => E.out.toBlob(res, type, q));
window.renderFrame = (i, o = {}) => serial(async () => {
  const a = performance.now(); const r = await renderFrame(i); const b = performance.now();
  if (E.comp.renderer.getContext().isContextLost()) throw new Error('WebGL context lost');   // never save a black frame
  const out = { i, t: i / FPS, shot: r.shot?.id || null, ms: b - a };
  if (o.hash) out.hash = E.comp.hashPixels();
  if (o.upload) { const bl = await blob(o.type || 'image/jpeg', o.q ?? 0.95); const res = await fetch(o.upload, { method: 'PUT', body: bl }); if (!res.ok) throw new Error('upload failed ' + res.status); out.bytes = bl.size; }
  else if (o.type) out.url = E.out.toDataURL(o.type, o.q ?? 0.95);
  out.msEnc = performance.now() - b;
  return out;
});
window.listShots = () => [...E.shots, ...E.overlays].map(s => ({ id: s.id, start: s.start, end: s.end, overlay: s._overlay, layers: s.layers.map(l => l.type + (l.module ? ':' + l.module : '')) }));
window.renderSheet = (frames, cols = 4, tw = 480) => serial(async () => {
  const th = Math.round(tw * 9 / 16), rows = Math.ceil(frames.length / cols), lab = 20;
  const C = document.createElement('canvas'); C.width = cols * tw; C.height = rows * (th + lab);
  const g = C.getContext('2d'); g.fillStyle = '#111'; g.fillRect(0, 0, C.width, C.height);
  for (let k = 0; k < frames.length; k++) {
    const r = await renderFrame(frames[k]); const x = (k % cols) * tw, y = Math.floor(k / cols) * (th + lab);
    g.drawImage(E.out, x, y, tw, th); g.fillStyle = '#bbb'; g.font = '13px monospace';
    g.fillText(`${(frames[k] / FPS).toFixed(3)}s  f${frames[k]}  ${r.shot ? r.shot.id : '-'}`, x + 6, y + th + 14);
  }
  return C.toDataURL('image/png');
});

// Math.random is reseeded per frame so third-party code stays deterministic (modules should still use env.rng)
Math.random = () => (E.rand ? E.rand() : 0.5);
