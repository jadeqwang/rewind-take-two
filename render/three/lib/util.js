// Deterministic helpers (no Math.random, no clock). Pure JS; shared by scenes.
export const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
export const lerp = (a, b, u) => a + (b - a) * u;
export const inv = (a, b, x) => clamp((x - a) / (b - a || 1e-9));
export const smooth = (a, b, x) => { const u = inv(a, b, x); return u * u * (3 - 2 * u); };
export const smoother = (a, b, x) => { const u = inv(a, b, x); return u * u * u * (u * (u * 6 - 15) + 10); };
export const fract = (x) => x - Math.floor(x);
export const mod = (x, m) => ((x % m) + m) % m;

export function hash(...xs) {
  let h = 0x9e3779b9 | 0;
  for (const x0 of xs) {
    let x = Math.round(x0 * 1000) | 0;
    x = Math.imul(x ^ (x >>> 16), 0x85ebca6b); x = Math.imul(x ^ (x >>> 13), 0xc2b2ae35); x ^= x >>> 16;
    h = Math.imul(h ^ x, 0x27d4eb2d); h ^= h >>> 15;
  }
  return (h >>> 0) / 4294967296;
}
export function noise1(x, seed = 0) {
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  return lerp(hash(i, seed) * 2 - 1, hash(i + 1, seed) * 2 - 1, u);
}

// Mechanical "clunk" easing for Monument Valley rotations: smooth ease to a 3.5% overshoot at u=0.8,
// then a damped settle back to exactly 1 at u=1 (C1 continuous at both ends).
export function clunk(u) {
  u = clamp(u);
  const k = 0.8, over = 0.035;
  if (u < k) { const v = u / k; return (1 + over) * v * v * (3 - 2 * v); }
  const v = (u - k) / (1 - k);
  return 1 + over * (1 - v * v * (3 - 2 * v)) * Math.cos(v * Math.PI * 1.0) ** 2;
}
