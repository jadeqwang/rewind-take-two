// sections.js: merge per-section timelines into the film, load EDL-JSON fallbacks, check overlaps, fill gaps.
// Pure (Node + browser). Used by render/timeline.js through the ctx helpers the engine passes to timeline functions:
//   ctx.list(dir) → file names, ctx.importModule(path) → module, ctx.readJSON(path) → object (repo-relative paths).
//
// Section file  render/timeline/<section>.js : export default {section?, shots, overlays?, fx?}  or  ({T, core}) => same
// EDL fallback  media/shots/<section>_edl.json (used only when render/timeline/<section>.js does not exist):
//   { "section": "C", "fx": [...], "overlays": [...],
//     "shots": [ { "shot": "V2e", "file": "media/shots/V2e1/take_1_engraved.mp4" | "….png",
//                  "in": 84.86 | "49:1", "out": 88.38 | "51:1",          timeline in/out (or "dur")
//                  "clip_in": 0.4, "rate": 1.0, "reverse": false,       clip in-point (s), speed, play the segment backwards
//                  "chosen": "media/shots/V2e1/chosen.json",            optional: take file/in_sec/rate/reverse from it
//                  "matte": "media/shots/V2e1/take_1_matte/matte.mp4",  optional (keepColor, ghosts, follow, isolation)
//                  "freeze": 1.2, "fit": "cover", "scale": 1, "x": 0, "y": 0, "kenBurns": {...}, "grade": {...},
//                  "text": [ {"style": "lowerthird", "in": 85.0, "out": 88.3, "text": "back on the road", "sync": "lyric", ...} ],
//                  "layers": [ extra engine layers ], "fx": [ ... ], "background": "#ece7dc" } ] }
//   text styles → modules: lowerthird | slam | dialogue | sign | etch | ground | pin | title | terminal | whisper | trace |
//                          pencil | hud-modes (pause | continue | loading | iteration | platformer | rewind | race)
//   text in/out are timeline times (seconds or expressions); every other key is passed to the module as a param.
const VIDEO = /\.(mp4|webm|mov|mkv|m4v)$/i;

export function joinPath(base, p) {
  if (!p || /^(\/|https?:)/.test(p) || !(p.startsWith('./') || p.startsWith('../'))) return p;
  const parts = base.split('/').filter(Boolean);
  for (const s of p.split('/')) { if (s === '..') parts.pop(); else if (s !== '.' && s !== '') parts.push(s); }
  return parts.join('/');
}
function rebase(o, dir, depth = 0) {   // relative module paths inside a section file are relative to that file
  if (!o || typeof o !== 'object' || depth > 10) return o;
  if (Array.isArray(o)) { o.forEach(x => rebase(x, dir, depth + 1)); return o; }
  if (typeof o.module === 'string') o.module = joinPath(dir, o.module);
  for (const k of Object.keys(o)) if (typeof o[k] === 'object') rebase(o[k], dir, depth + 1);
  return o;
}

const TEXT_MODULE = { lowerthird: 'lowerthird', lyric: 'lowerthird', slam: 'slam', kinetic: 'slam', dialogue: 'dialogue', rpg: 'dialogue',
  sign: 'pin', etch: 'pin', ground: 'pin', pin: 'pin', plain: 'pin', title: 'title', terminal: 'terminal', whisper: 'whisper', trace: 'trace',
  pencil: 'pencil', handwritten: 'pencil', motes: 'motes' };
const HUD_MODES = new Set(['pause', 'continue', 'loading', 'iteration', 'platformer', 'rewind', 'race']);

export async function edlToSection(edl, T, ctx, path = 'EDL') {
  const shots = [];
  for (const [k, e] of (edl.shots || []).entries()) {
    const c = e.chosen ? await ctx.readJSON(e.chosen) : {};
    const file = e.file ?? c.file;
    const start = T.time(e.in ?? e.timeline_in ?? e.start);
    const end = e.out ?? e.timeline_out ?? e.end;
    const endT = end !== undefined ? T.time(end) : e.dur !== undefined ? start + T.dur(start, e.dur) : undefined;
    if (!(Number.isFinite(start) && Number.isFinite(endT))) throw new Error(`${path}: shot ${e.shot || k} needs in/out (timeline times)`);
    const dur = endT - start;
    const clipIn = +(e.clip_in ?? e.in_sec ?? c.in_sec ?? 0), rate = +(e.rate ?? c.rate ?? 1), reverse = !!(e.reverse ?? c.reverse);
    const frame = { fit: e.fit, scale: e.scale, x: e.x, y: e.y, crop: e.crop, kenBurns: e.kenBurns, grade: e.grade };
    for (const key of Object.keys(frame)) if (frame[key] === undefined) delete frame[key];
    const layers = [];
    if (file && VIDEO.test(file)) {
      const v = { id: 'plate', type: 'video', src: file, ...frame };
      if (reverse) v.srcTime = [[0, clipIn + dur * rate], [dur, clipIn]]; else { v.in = clipIn; v.rate = rate; }
      if (e.freeze !== undefined) v.freeze = e.freeze;
      if (e.matte) { v.matte = { src: e.matte, mode: 'luma' }; v.keepColor = e.keepColor ?? true; }
      layers.push(v);
    } else if (file) layers.push({ id: 'plate', type: 'image', src: file, ...frame });
    for (const tx of e.text || []) {
      const { style = 'lowerthird', in: tin, out: tout, stage, ...params } = tx;
      const mod = HUD_MODES.has(style) ? 'hud' : TEXT_MODULE[style];
      if (!mod) throw new Error(`${path}: shot ${e.shot || k}: unknown text style "${style}"`);
      if (mod === 'hud') params.mode = style; else if (mod === 'pin') params.style = params.style || style;
      const L = { type: 'canvas', module: mod, params, stage: stage || (mod === 'pin' ? 'pre' : 'post') };
      if (tin !== undefined) L.start = typeof tin === 'number' ? tin - start : tin;
      if (tout !== undefined) L.end = typeof tout === 'number' ? tout - start : tout;
      layers.push(L);
    }
    layers.push(...(e.layers || []));
    shots.push({ id: e.shot || `${edl.section || 'edl'}_${k}`, start, end: endT, layers, fx: e.fx || [], background: e.background });
  }
  return { section: edl.section, shots, overlays: edl.overlays || [], fx: edl.fx || [] };
}

// resolve a section's shot times to numbers (end defaults to the next shot's start inside the same section)
function resolveSection(sec, T, src) {
  const out = sec.shots.map(s => ({ ...s, start: s.start !== undefined ? T.time(s.start) : undefined }));
  out.forEach((s, i) => {
    const raw = sec.shots[i];
    if (s.start === undefined) { if (i === 0) throw new Error(`${src}: first shot "${s.id}" needs a start`); s.start = out[i - 1].end; }
    s.end = raw.end !== undefined ? T.time(raw.end) : raw.dur !== undefined ? s.start + T.dur(s.start, raw.dur) : out[i + 1]?.start !== undefined ? T.time(sec.shots[i + 1].start) : undefined;
    if (!Number.isFinite(s.end)) throw new Error(`${src}: shot "${s.id}" needs an end (or dur)`);
    if (!(s.end > s.start)) throw new Error(`${src}: shot "${s.id}" ends (${s.end.toFixed(3)}) before it starts (${s.start.toFixed(3)})`);
    s._src = src; s._section = sec.section;
    if (sec.fx?.length) s.fx = [...sec.fx, ...(Array.isArray(s.fx) ? s.fx : [])];
  });
  return out;
}

// sections: [{section, shots, overlays, fx, _src}] → {shots, overlays}; throws on any overlap of base-track shots
export function mergeSections(sections, T, { fill = true, fillShot } = {}) {
  let shots = [], overlays = [];
  for (const sec of sections) {
    shots.push(...resolveSection(sec, T, sec._src));
    overlays.push(...(sec.overlays || []).map(o => ({ ...o, _src: sec._src })));
  }
  shots.sort((a, b) => a.start - b.start);
  const ids = new Map();
  for (const s of shots) {
    if (ids.has(s.id)) throw new Error(`duplicate shot id "${s.id}" in ${s._src} and ${ids.get(s.id)}`);
    ids.set(s.id, s._src);
  }
  const errs = [];
  for (let i = 1; i < shots.length; i++) {
    const a = shots[i - 1], b = shots[i];
    if (b.start < a.end - 1e-3) errs.push(`  "${a.id}" ${a.start.toFixed(3)}–${a.end.toFixed(3)} (${a._src}) overlaps "${b.id}" ${b.start.toFixed(3)}–${b.end.toFixed(3)} (${b._src}) by ${(a.end - b.start).toFixed(3)} s`);
  }
  if (errs.length) throw new Error('timeline: overlapping shots\n' + errs.join('\n'));
  if (fill) {
    const gaps = [], end = T.duration;
    let cur = 0;
    for (const s of [...shots, { start: end, end }]) { if (s.start - cur > 1 / 48) gaps.push([cur, s.start]); cur = Math.max(cur, s.end); }
    for (const [a, b] of gaps) {
      // split each gap at the song's section boundaries so the slate names what belongs there
      const cuts = [a, ...T.sections.map(s => s.start).filter(x => x > a + 1 / 48 && x < b - 1 / 48), b];
      for (let k = 0; k < cuts.length - 1; k++) {
        const sec = T.sectionAt(cuts[k] + 1e-3);
        shots.push(fillShot ? fillShot(cuts[k], cuts[k + 1], sec) : { id: `gap_${cuts[k].toFixed(2)}`, start: cuts[k], end: cuts[k + 1], layers: [] });
      }
    }
    shots.sort((a, b) => a.start - b.start);
  }
  return { shots, overlays };
}

// load every render/timeline/*.js plus media/shots/*_edl.json whose section has no .js file
export async function loadSections(ctx, T, { dir = 'render/timeline', edlDir = 'media/shots' } = {}) {
  const out = [];
  const js = (await ctx.list(dir)).filter(f => /\.m?js$/.test(f) && !f.startsWith('_')).sort();
  const have = new Set();
  for (const f of js) {
    const path = `${dir}/${f}`, mod = await ctx.importModule(path);
    let sec = mod.default ?? mod.section ?? mod.timeline;
    if (typeof sec === 'function') sec = await sec({ T, core: ctx.core });
    if (!sec || !Array.isArray(sec.shots)) throw new Error(`${path}: default export must be {shots: [...]} or a function returning it`);
    sec = rebase({ ...sec }, dir);
    sec.section = sec.section || f.replace(/\.m?js$/, ''); sec._src = path; have.add(sec.section); have.add(f.replace(/\.m?js$/, ''));
    out.push(sec);
  }
  for (const f of (await ctx.list(edlDir)).filter(f => /_edl\.json$/.test(f)).sort()) {
    const name = f.replace(/_edl\.json$/, '');
    if (have.has(name)) continue;
    const path = `${edlDir}/${f}`, edl = await ctx.readJSON(path);
    const sec = await edlToSection(edl, T, ctx, path);
    if (have.has(sec.section)) continue;
    sec.section = sec.section || name; sec._src = path; out.push(sec);
  }
  return out;
}
