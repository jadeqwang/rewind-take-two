// core.js: math, easing, deterministic hashing / RNG / noise, colour helpers. Pure (runs in Node and the browser).
// Contract for everything the engine draws: no Math.random(), no Date, no wall clock. A frame is a function of its index.

export const DW = 1920, DH = 1080;     // design resolution: every layer, module and effect is authored in these units
export const FPS = 24;

export const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
export const lerp = (a, b, u) => a + (b - a) * u;
export const inv = (a, b, x) => clamp((x - a) / (b - a || 1e-9));
export const smooth = (a, b, x) => { const u = inv(a, b, x); return u * u * (3 - 2 * u); };
export const fract = x => x - Math.floor(x);
export const fin = (x, d = 0) => (Number.isFinite(x) ? x : d);

// ---- easing (u in 0..1) ----
const c = clamp;
export const EASE = {
  linear: u => c(u),
  hold: u => (u >= 1 ? 1 : 0),            // step: value of the left key until the next key
  in: u => c(u) ** 2, out: u => 1 - (1 - c(u)) ** 2, inOut: u => { u = c(u); return u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2; },
  inCubic: u => c(u) ** 3, outCubic: u => 1 - (1 - c(u)) ** 3,
  inOutCubic: u => { u = c(u); return u < 0.5 ? 4 * u * u * u : 1 - (-2 * u + 2) ** 3 / 2; },
  inExpo: u => (u <= 0 ? 0 : 2 ** (10 * c(u) - 10)), outExpo: u => (u >= 1 ? 1 : 1 - 2 ** (-10 * c(u))),
  inOutSine: u => -(Math.cos(Math.PI * c(u)) - 1) / 2,
  outBack: u => { u = c(u) - 1; return 1 + u * u * (2.70158 * u + 1.70158); },
  smooth: u => { u = c(u); return u * u * (3 - 2 * u); },
};
export const ease = (name, u) => (typeof name === 'function' ? name(u) : (EASE[name] || EASE.linear)(u));

// ---- hashing / RNG ----
export function hashStr(s) { let h = 2166136261 >>> 0; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
// hash(...xs) → [0,1). Numbers are quantised to 1e-3 so float noise in t never changes a hash.
export function hash(...xs) {
  let h = 0x9e3779b9 | 0;
  for (const x0 of xs) {
    let x = typeof x0 === 'string' ? hashStr(x0) : (Math.round(x0 * 1000) | 0);
    x = Math.imul(x ^ (x >>> 16), 0x85ebca6b); x = Math.imul(x ^ (x >>> 13), 0xc2b2ae35); x ^= x >>> 16;
    h = Math.imul(h ^ x, 0x27d4eb2d); h ^= h >>> 15;
  }
  return (h >>> 0) / 4294967296;
}
export const hsig = (...xs) => hash(...xs) * 2 - 1;
// mulberry32 stream seeded by any mix of strings/numbers: rng('shot', 3)() → [0,1)
export function rng(...seed) {
  let a = Math.floor(hash(...seed) * 4294967296) >>> 0;
  return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export function noise1(x, seed = 0) { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hsig(i, seed), hsig(i + 1, seed), u); }
export function noise2(x, y, seed = 0) {
  const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j, ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
  return lerp(lerp(hsig(i, j, seed), hsig(i + 1, j, seed), ux), lerp(hsig(i, j + 1, seed), hsig(i + 1, j + 1, seed), ux), uy);
}
// fractal 1-D noise, roughly in [-1,1]
export function fbm1(x, seed = 0, oct = 3) { let v = 0, a = 0.5, n = 0; for (let k = 0; k < oct; k++) { v += a * noise1(x, seed + k * 17); n += a; x *= 2.03; a *= 0.5; } return v / n; }

// ---- colour ----
export function hexRgb(hex) {
  if (Array.isArray(hex)) return hex.length === 3 ? hex : hex.slice(0, 3);
  let h = String(hex).replace('#', ''); if (h.length === 3) h = h.split('').map(x => x + x).join('');
  return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255];
}
export const rgba = (hex, a = 1) => { const [r, g, b] = hexRgb(hex); return `rgba(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)},${clamp(fin(a))})`; };
export const mixHex = (a, b, u) => { const A = hexRgb(a), B = hexRgb(b); return '#' + A.map((x, i) => Math.round(lerp(x, B[i], clamp(u)) * 255).toString(16).padStart(2, '0')).join(''); };

// REWIND palette (treatment: the world is a black-and-white woodcut; Jade and her residue are the only colour)
export const PAL = {
  ink: '#0B0B0C', paper: '#ECE7DC', graphite: '#2A2A2C', pencil: '#8D8A84',
  orange: '#FF7A1A', sky: '#7EC8FF', paleBlue: '#BFE3FF', navy: '#1C2A4A',
  alert: '#FF2A2A', hud: '#F4F1EA',
};

// mm:ss.cc speedrun clock
export function clock(t, cs = true) {
  const neg = t < 0; t = Math.abs(fin(t));
  const m = Math.floor(t / 60), s = Math.floor(t % 60), h = Math.floor((t * 100) % 100);
  return (neg ? '-' : '') + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0') + (cs ? '.' + String(h).padStart(2, '0') : '');
}
