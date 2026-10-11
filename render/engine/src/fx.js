// fx.js: per-shot and global effects → post-pass parameters, plus the shot's content-time remap (tape stop, holds).
//
// fx entries ({type, ...}; numeric fields may be keyframed on the shot clock). Timeline-level `fx` apply to every shot
// first, then the shot's own list (a shot entry of the same type overrides grain/paper/letterbox/grade/vignette/isolate).
//   grain     {amount .05, size 1.5, seed: 'frame'|'shot'|'twos'}           paper   {amount .5}
//   vignette  {amount .25}          scanlines {amount .3}       chroma {amount px}        vhs {amount 0..1}
//   grade     {saturation, contrast, exposure, tint '#rrggbb', lift '#rrggbb'}
//   letterbox {aspect 2.39, amount 0..1 (keyframe it to animate the bars in), color}
//   isolate   {amount 1, ink '#0b0b0c', paper '#ece7dc', engrave 0..1, cell 6, angle .6}  world → ink on paper except layers with keepColor
//   fade      {in s, out s, color}                    dip to black at the shot's head / tail
//   flash     {at: [t...] | on: <events>, dur .12, amount 1, color}   (at: numbers = shot-local, strings = absolute)
//   punch     {amount .04, on: 'beat', decay .12}    zoom punch      shake {amp px, freq 8, steady 0, on?, decay .15}
//   tapeStop  {at (local s), dur .8, toBlack: .25 | false}   content time decelerates to a stop + tape sag visuals
//   hold      {at, until}                             freeze the content clock (freeze-frame of every layer)
//   rewind    {amount 1}                              VHS search look (bands, tracking, chroma, warble)
//   negative  {amount 1 (keyframe 0→1 over .3 s), ink, paper}  woodblock negative: white lines on ink; keepColor layers stay
//   ripple    {amount 1, speed 6}                     underwater/ripple distortion
//   warble    {amount}  wobble {amount}  tracking {amount}  zoom {amount (keys)}  spin {deg}
// Events (`on`): 'beat' | 'downbeat' | 'kick' | 'snare' | 'every:2' (every 2nd beat) | [abs times] | {list, every, offset}
import { clamp, hash, fbm1 } from './core.js';
import { val } from './keys.js';

export function defaults() {
  return { zoom: 1, spin: 0, drop: 0, squash: 0, warble: 0, warbleSeed: 0, wobble: 0, tracking: 0, trackPos: -200, rewindLines: 0, ripple: 0, ripplePhase: 0,
    chroma: 0, vhs: 0, iso: 0, neg: 0, engrave: 0, engraveCell: 6, engraveAngle: 0.6, sat: 1, contrast: 1, exposure: 1, lift: 0, tint: '#ffffff',
    isoInk: '#0b0b0c', isoPaper: '#ece7dc', bg: '#000000', grain: 0, grainSize: 1.5, grainSeed: 0, paper: 0, paperSeed: 0, scan: 0, vignette: 0,
    shakeX: 0, shakeY: 0, flash: 0, flashC: '#ffffff', fade: 0, letterbox: 0, boxC: '#000000', dither: 1, time: 0 };
}

// event list for an `on` spec, restricted to [from, to]
export function events(T, on, from = -1e9, to = 1e9) {
  if (!on) return [];
  let list, every = 1, offset = 0;
  if (Array.isArray(on)) list = on.map(x => T.time(x));
  else if (typeof on === 'object') { list = T.list(on.list || 'beats'); every = on.every || 1; offset = on.offset || 0; }
  else if (/^every:\d+$/.test(on)) { list = T.list('beats'); every = +on.split(':')[1]; }
  else list = T.list(on === 'beat' ? 'beats' : on === 'downbeat' ? 'downbeats' : on === 'kick' ? 'kicks' : on === 'snare' ? 'snares' : on);
  if (every > 1) list = list.filter((_, i) => (((i - offset) % every) + every) % every === 0);
  return list.filter(x => x >= from - 1e-6 && x <= to + 1e-6);
}
// exp pulse of the most recent event at or before t (events before the shot start are ignored, so nothing leaks over a cut)
export function pulse(T, on, t, decay, from) {
  const ev = events(T, on, from, t); if (!ev.length) return 0;
  return Math.exp(-(t - ev[ev.length - 1]) / Math.max(1e-3, decay));
}

// shot content clock: lt (real seconds into the shot) → ct (what the layers see)
export function contentTime(shot, lt, env) {
  let ct = shot.time !== undefined ? val(shot.time, lt, env) : lt;
  for (const f of shot._fx) {
    if (f.type === 'tapeStop') {
      const at = f._at, d = f.dur ?? 0.8;
      if (lt > at) { const u = clamp((lt - at) / d); ct = (shot.time !== undefined ? val(shot.time, at, env) : at) + d * (u - u * u / 2); }
    } else if (f.type === 'hold') {
      const a = f._at, b = f._until ?? 1e9;
      if (lt >= a) ct -= Math.min(lt, b) - a;
    }
  }
  return ct;
}

const OVERRIDE = new Set(['grain', 'paper', 'letterbox', 'grade', 'vignette', 'isolate', 'scanlines']);

export function evalFx(shot, globalFx, lt, t, frame, T, env) {
  const P = defaults(); P.time = t;
  const list = [...globalFx.filter(g => !(OVERRIDE.has(g.type) && shot._fx.some(f => f.type === g.type))), ...shot._fx];
  const V = (x, d) => { const v = val(x, lt, env, d); return v === undefined ? d : v; };
  const dur = shot.end - shot.start;
  for (const f of list) {
    switch (f.type) {
      case 'grain': {
        P.grain = V(f.amount, 0.05); P.grainSize = V(f.size, 1.5);
        P.grainSeed = f.seed === 'shot' ? hash(shot.id) * 997 : f.seed === 'twos' ? Math.floor(frame / 2) : frame; break;
      }
      case 'paper': P.paper = V(f.amount, 0.5); P.paperSeed = hash(f.seed ?? 'paper') * 100; break;
      case 'vignette': P.vignette = V(f.amount, 0.25); break;
      case 'scanlines': P.scan = V(f.amount, 0.3); break;
      case 'chroma': P.chroma += V(f.amount, 2); break;
      case 'vhs': P.vhs += V(f.amount, 0.6); break;
      case 'warble': P.warble += V(f.amount, 0.5); P.warbleSeed = frame; break;
      case 'wobble': P.wobble += V(f.amount, 0.5); break;
      case 'tracking': P.tracking += V(f.amount, 0.5); P.trackPos = ((t * 160) % 1300) - 110; break;
      case 'zoom': P.zoom *= V(f.amount, 1); break;
      case 'spin': P.spin += V(f.amount, 0) * Math.PI / 180; break;
      case 'grade': {
        const g = f; if (g.saturation !== undefined) P.sat *= V(g.saturation, 1); if (g.contrast !== undefined) P.contrast *= V(g.contrast, 1);
        if (g.exposure !== undefined) P.exposure *= V(g.exposure, 1); if (g.tint) P.tint = V(g.tint); if (g.lift !== undefined) P.lift = V(g.lift, 0); break;
      }
      case 'letterbox': { const a = V(f.aspect, 2.39), amt = V(f.amount, 1); P.letterbox = Math.max(0, (1 - (16 / 9) / a) / 2) * clamp(amt); if (f.color) P.boxC = f.color; break; }
      case 'isolate': {
        P.iso = V(f.amount, 1); if (f.ink) P.isoInk = f.ink; if (f.paper) P.isoPaper = f.paper;
        P.engrave = V(f.engrave, 0); P.engraveCell = V(f.cell, 6); P.engraveAngle = V(f.angle, 0.6); break;
      }
      case 'fade': {
        const i = V(f.in, 0), o = V(f.out, 0);
        if (i > 0 && lt < i) P.fade = Math.max(P.fade, 1 - lt / i);
        if (o > 0 && lt > dur - o) P.fade = Math.max(P.fade, (lt - (dur - o)) / o);
        break;
      }
      case 'flash': {
        const d = V(f.dur, 0.12), amt = V(f.amount, 1);
        const times = f.at !== undefined ? [].concat(f.at).map(x => (typeof x === 'number' ? shot.start + x : T.time(x))) : events(T, f.on, shot.start, t);
        for (const e of times) if (t >= e - 1e-6) {
          const k = t - e < 1 / 24 - 1e-6 ? 1 : Math.exp(-(t - e - 1 / 24) / d);   // first frame full, then decay
          if (amt * k > P.flash) { P.flash = amt * k; if (f.color) P.flashC = f.color; }
        }
        break;
      }
      case 'punch': P.zoom *= 1 + V(f.amount, 0.04) * pulse(T, f.on || 'beat', t, V(f.decay, 0.12), shot.start); break;
      case 'shake': {
        const amp = V(f.amp, 8), fr = V(f.freq, 8), k = V(f.steady, 0) + (f.on ? pulse(T, f.on, t, V(f.decay, 0.15), shot.start) : (f.steady === undefined ? 1 : 0));
        P.shakeX += amp * k * fbm1(t * fr, 11); P.shakeY += amp * k * fbm1(t * fr, 23);
        P.zoom *= 1 + Math.abs(amp * k) / 1080;   // overscan so the shake never shows an edge
        break;
      }
      case 'tapeStop': {
        const at = f._at, d = f.dur ?? 0.8;
        if (lt > at) {
          const u = clamp((lt - at) / d), s = 1 - u, k = 1 - s;               // s: tape speed 1 → 0
          P.warble += 1.4 * k; P.warbleSeed = frame; P.wobble += 0.9 * k; P.drop += 70 * k * k; P.squash += 0.05 * k * k;
          P.chroma += 5 * k; P.sat *= 1 - 0.55 * k; P.exposure *= 1 - 0.4 * k * k; P.tracking += 0.8 * k; P.trackPos = 1080 - ((lt - at) * 900) % 1250;
          const tb = f.toBlack === false ? 0 : (f.toBlack ?? 0.25);
          if (tb > 0 && lt > at + d) P.fade = Math.max(P.fade, clamp((lt - at - d) / tb));
        }
        break;
      }
      case 'rewind': {
        const a = V(f.amount, 1);
        P.rewindLines += a; P.chroma += 3 * a; P.warble += 0.5 * a; P.warbleSeed = frame; P.tracking += 0.6 * a; P.trackPos = ((t * 520) % 1300) - 110;
        P.vhs += 0.55 * a; P.scan = Math.max(P.scan, 0.25 * a); break;
      }
      case 'negative': P.neg = Math.max(P.neg, V(f.amount, 1)); if (f.ink) P.isoInk = f.ink; if (f.paper) P.isoPaper = f.paper; break;
      case 'ripple': P.ripple += V(f.amount, 1); P.ripplePhase = t * V(f.speed, 6); break;
      case 'hold': break;
      case 'bg': P.bg = f.color; break;
      default: if (!f._warned) { f._warned = true; console.warn(`unknown fx type "${f.type}" in shot ${shot.id}`); }
    }
  }
  return P;
}
