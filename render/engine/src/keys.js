// keys.js: keyframed / animated values. Pure (Node + browser).
//
// Any animatable parameter may be:
//   a constant           12, '#ff7a1a', [x, y]
//   keyframes            [[t, value, ease?], ...]   t = local seconds (shot or layer clock) or an absolute time
//                         expression string ("17:1", "word:rewind", "86.5" ...; see timing.js), converted to local time.
//                         ease (on the LEFT key, shapes the segment to the next key): linear (default) | hold | in | out |
//                         inOut | inCubic | outCubic | inOutCubic | inExpo | outExpo | inOutSine | outBack | smooth
//   {keys: [...], ease: 'inOut'}   same, with a default ease
//   a function           (lt, env) => value         (JS timelines only)
// Values interpolate component-wise (numbers, arrays) or in RGB ('#rrggbb'); other strings step.
import { ease as easeFn, hexRgb, lerp } from './core.js';

export const isKeys = x => Array.isArray(x) && x.length > 0 && x.every(k => Array.isArray(k) && k.length >= 2 && (typeof k[0] === 'number' || typeof k[0] === 'string'));
const isHex = v => typeof v === 'string' && /^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(v);

function interp(a, b, u) {
  if (typeof a === 'number' && typeof b === 'number') return a + (b - a) * u;
  if (Array.isArray(a) && Array.isArray(b)) return a.map((x, i) => interp(x, b[i] ?? x, u));
  if (isHex(a) && isHex(b)) { const A = hexRgb(a), B = hexRgb(b); return '#' + A.map((x, i) => Math.round(lerp(x, B[i], u) * 255).toString(16).padStart(2, '0')).join(''); }
  return u < 1 ? a : b;
}

const resolved = new WeakMap();   // keys array → Map(origin → [{t, v, e}])
function resolveKeys(keys, env, dflt) {
  const origin = env?.origin ?? 0;
  let m = resolved.get(keys); if (!m) { m = new Map(); resolved.set(keys, m); }
  let r = m.get(origin);
  if (!r) {
    r = keys.map(k => ({ t: typeof k[0] === 'number' ? k[0] : env.T.time(k[0]) - origin, v: k[1], e: k[2] ?? dflt }));
    r.sort((a, b) => a.t - b.t); m.set(origin, r);
  }
  return r;
}

// evaluate x at local time lt
export function val(x, lt, env, dflt = undefined) {
  if (x === undefined || x === null) return dflt;
  if (typeof x === 'function') return x(lt, env);
  let keys = null, de = 'linear';
  if (isKeys(x)) keys = x; else if (x && typeof x === 'object' && Array.isArray(x.keys)) { keys = x.keys; de = x.ease || de; }
  if (!keys) return x;
  const K = resolveKeys(keys, env, de);
  if (lt <= K[0].t) return K[0].v;
  const n = K.length; if (lt >= K[n - 1].t) return K[n - 1].v;
  let i = 0; while (i < n - 2 && lt >= K[i + 1].t) i++;
  const a = K[i], b = K[i + 1], u = (lt - a.t) / Math.max(1e-9, b.t - a.t);
  return interp(a.v, b.v, easeFn(a.e, u));
}

// ∫_0^lt x(τ) dτ for an animated rate (constant rates are exact; keyframes use a cached 1/480 s table)
const tables = new WeakMap();
export function integrate(x, lt, env) {
  if (typeof x === 'number') return x * lt;
  if (x === undefined || x === null) return lt;
  if (lt < 0) return val(x, 0, env, 1) * lt;
  const h = 1 / 480;
  const key = typeof x === 'object' ? x : null;
  let tb = key && tables.get(key);
  if (!tb || tb.origin !== (env?.origin ?? 0)) { tb = { origin: env?.origin ?? 0, cum: [0] }; if (key) tables.set(key, tb); }
  const L = lt, n = Math.floor(L / h);
  while (tb.cum.length <= n + 1) {          // trapezoid steps (deterministic: the table only ever grows the same way)
    const i = tb.cum.length - 1, a = i * h, b = (i + 1) * h;
    tb.cum.push(tb.cum[i] + 0.5 * (val(x, a, env, 1) + val(x, b, env, 1)) * h);
  }
  const f = (L - n * h) / h;
  return tb.cum[n] + (tb.cum[n + 1] - tb.cum[n]) * f;
}

// resolve every animatable field of an object at lt (shallow)
export function vals(obj, lt, env, skip = null) {
  const o = {};
  for (const k in obj) o[k] = skip && skip.has(k) ? obj[k] : val(obj[k], lt, env);
  return o;
}
