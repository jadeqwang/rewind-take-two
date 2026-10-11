// lib/text.js: shared helpers for the typography kit (Canvas2D). All times here are absolute song seconds.
import { clamp, hash, hsig, PAL } from '../../src/core.js';

export const F = { fell: '"IM Fell English"', sign: 'Overpass', hud: '"Press Start 2P"', mono: '"IBM Plex Mono"', hand: '"Reenie Beanie"', slab: 'Anton' };
export const C = { ink: '#0b0b0c', paper: '#ece7dc', orange: PAL.orange, blue: PAL.blue, gold: PAL.gold, graphite: '#5e5b57' };
export const fontName = f => F[f] || f || F.fell;

const norm = s => String(s).toLowerCase().replace(/[^a-z0-9']/g, '').replace(/'/g, '');

// layer-local number or absolute expression → absolute seconds
export function absT(env, x, dflt = 0) {
  if (x === undefined || x === null) return env.origin + dflt;
  return typeof x === 'number' ? env.origin + x : env.T.time(x);
}
export const layerEnd = env => env.layerEnd ?? env.origin + 1e6;

// words to show: [{text, start, end, br}] (absolute times). Sources, in priority order:
//   params.text + params.times ([t per word], local or absolute)      explicit
//   params.text + sync: 'lyric'   each word matched to the next sung word with the same spelling after the layer start
//   params.text + cps             typewriter pace from the layer start (or params.at)
//   params.text                   everything at once at the layer start (or params.at)
//   no text, source: 'window'     every sung word whose onset falls inside the layer's time range
//   no text (default)             the lyric line being sung now (TimeMap.lyric), with lead/hold
export function wordsFor(env, p, opts = {}) {
  if (p.text === undefined || p.text === null) {
    if ((p.source || opts.source) === 'window') {
      const a = env.origin - 1e-3, b = layerEnd(env);
      return env.T.words.filter(w => w.start >= a && w.start < b).map(w => ({ text: w.text, start: w.start, end: w.end, line: w.line }))
        .map((w, i, arr) => ({ ...w, br: i > 0 && arr[i - 1].line !== w.line && !!p.lineBreaks }));
    }
    const L = env.lyric({ lead: p.lead ?? 0.3, hold: p.hold ?? 0.6 });
    if (!L.line) return [];
    return L.line.words.map(w => ({ text: w.text, start: w.start, end: w.end, lineEnd: L.line.end }));
  }
  const toks = [];
  String(p.text).split('\n').forEach((ln, li) => ln.split(/\s+/).filter(Boolean).forEach((w, k) => toks.push({ text: w, br: li > 0 && k === 0 })));
  const t0 = absT(env, p.at, 0);
  if (Array.isArray(p.times)) toks.forEach((w, i) => { w.start = absT(env, p.times[Math.min(i, p.times.length - 1)]); });
  else if (p.sync === 'lyric') {
    let after = t0 - (p.syncSlack ?? 1.0), last = t0;
    const until = layerEnd(env) + (p.syncSlack ?? 1.0);   // only words sung while this layer is up
    for (const w of toks) {
      const k = norm(w.text), m = env.T.words.find(x => x.key === k && x.start >= after - 1e-6 && x.start < until);
      if (m) { w.start = m.start; w.end = m.end; after = m.start + 1e-3; last = m.start; } else w.start = last;
    }
  } else if (p.cps) {
    let n = 0; for (const w of toks) { w.start = t0 + n / p.cps; n += w.text.length + 1; }
  } else toks.forEach(w => { w.start = t0; });
  toks.forEach((w, i) => { if (w.end === undefined) w.end = toks[i + 1] ? Math.max(w.start + 0.05, toks[i + 1].start) : w.start + 0.4; });
  return toks;
}

export function caseOf(s, p) { return p.uppercase ? s.toUpperCase() : p.lowercase ? s.toLowerCase() : s; }

// 2-frame ink bleed: frame 0 = a soaked blot, frame 1 = settling, then crisp. Returns draw params for a word.
export function bleed(t, start, fps = 24) {
  const f = (t - start) * fps;
  if (f < 0) return null;
  if (f < 1) return { blur: 3.2, spread: 3.0, alpha: 0.62, f: 0 };
  if (f < 2) return { blur: 1.0, spread: 1.1, alpha: 0.88, f: 1 };
  return { blur: 0, spread: 0, alpha: 1, f: 2 };
}
// draw text with a bleed state (g already has font/fill/align set). S = output px per design px (for filter radii).
export function inkText(g, s, x, y, b, color, S, seed = 0) {
  if (!b) return;
  g.save();
  g.globalAlpha *= b.alpha; g.fillStyle = color; g.strokeStyle = color;
  if (b.blur > 0) g.filter = `blur(${(b.blur * S).toFixed(2)}px)`;
  if (b.spread > 0) { g.lineWidth = b.spread; g.lineJoin = 'round'; g.strokeText(s, x, y); }
  g.fillText(s, x, y);
  g.filter = 'none';
  if (b.f === 0) {   // a few ink droplets thrown off on the first frame
    const w = g.measureText(s).width, sz = parseFloat(g.font.match(/(\d+(?:\.\d+)?)px/)?.[1] || 40);
    const x0 = g.textAlign === 'center' ? x - w / 2 : g.textAlign === 'right' ? x - w : x;
    for (let k = 0; k < 7; k++) { g.beginPath(); g.arc(x0 + w * hash(seed, k), y - sz * (0.15 + 0.7 * hash(seed, k, 1)) + hsig(seed, k, 2) * sz * 0.35, 0.8 + 2.2 * hash(seed, k, 3), 0, 7); g.fill(); }
  }
  g.restore();
}

// word layout: lines of words wrapped to maxWidth; returns [{words:[{w, x, width}], width}] with x relative to line start
export function layout(g, words, maxW, space) {
  const lines = [{ items: [], width: 0 }];
  for (const w of words) {
    const width = g.measureText(w.display ?? w.text).width;
    let L = lines[lines.length - 1];
    if (w.br || (L.items.length && L.width + space + width > maxW)) { L = { items: [], width: 0 }; lines.push(L); }
    const x = L.items.length ? L.width + space : 0;
    L.items.push({ w, x, width }); L.width = x + width;
  }
  return lines.filter(l => l.items.length);
}

// scratch canvases (per name), sized in output pixels
const pool = new Map();
export function scratch(name, w, h) {
  w = Math.max(1, Math.ceil(w)); h = Math.max(1, Math.ceil(h));
  let c = pool.get(name);
  if (!c) { c = document.createElement('canvas'); pool.set(name, c); c.g = c.getContext('2d'); }
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  c.g.setTransform(1, 0, 0, 1, 0, 0); c.g.globalAlpha = 1; c.g.globalCompositeOperation = 'source-over'; c.g.filter = 'none'; c.g.clearRect(0, 0, w, h);
  return c;
}

// static paper-tooth / pencil-grain mask (seeded): alpha holes where the pencil skips the paper
let grainTile = null;
export function grainPattern(g) {
  if (!grainTile) {
    grainTile = document.createElement('canvas'); grainTile.width = grainTile.height = 256;
    const q = grainTile.getContext('2d'), im = q.createImageData(256, 256);
    for (let y = 0; y < 256; y++) for (let x = 0; x < 256; x++) {
      const n = hash(x, y, 77), streak = 0.5 + 0.5 * Math.sin((x * 0.9 + y * 0.35) * 0.8 + hash(Math.floor(y / 3), 5) * 6);
      const a = clamp((n * 0.75 + streak * 0.45 - 0.62) * 2.2);
      im.data[(y * 256 + x) * 4 + 3] = Math.round(a * 255);
    }
    q.putImageData(im, 0, 0);
  }
  return g.createPattern(grainTile, 'repeat');
}

// ---- corner pin: draw src canvas onto the quad [x0,y0, x1,y1, x2,y2, x3,y3] (TL, TR, BR, BL; design px) with a
// projective mapping (mesh of affine triangles). g has the design transform (S) applied.
function homography(q) {   // unit square → quad
  const [x0, y0, x1, y1, x2, y2, x3, y3] = q;
  const dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2, sx = x0 - x1 + x2 - x3, sy = y0 - y1 + y2 - y3;
  const den = dx1 * dy2 - dx2 * dy1 || 1e-9;
  const g7 = (sx * dy2 - dx2 * sy) / den, h8 = (dx1 * sy - sx * dy1) / den;
  const a = x1 - x0 + g7 * x1, b = x3 - x0 + h8 * x3, c = x0, d = y1 - y0 + g7 * y1, e = y3 - y0 + h8 * y3, f = y0;
  return (u, v) => { const w = g7 * u + h8 * v + 1; return [(a * u + b * v + c) / w, (d * u + e * v + f) / w]; };
}
export function warpQuad(g, src, quad, { nx = 16, ny = 8, sw = src.width, sh = src.height } = {}) {
  const H = homography(quad), P = [];
  for (let j = 0; j <= ny; j++) for (let i = 0; i <= nx; i++) P.push(H(i / nx, j / ny));
  const tri = (s0, s1, s2, d0, d1, d2) => {
    // affine from src triangle to dst triangle
    const [x0, y0] = s0, [x1, y1] = s1, [x2, y2] = s2, [u0, v0] = d0, [u1, v1] = d1, [u2, v2] = d2;
    const den = x0 * (y1 - y2) + x1 * (y2 - y0) + x2 * (y0 - y1); if (Math.abs(den) < 1e-9) return;
    const a = (u0 * (y1 - y2) + u1 * (y2 - y0) + u2 * (y0 - y1)) / den, b = (u0 * (x2 - x1) + u1 * (x0 - x2) + u2 * (x1 - x0)) / den;
    const c = (u0 * (x1 * y2 - x2 * y1) + u1 * (x2 * y0 - x0 * y2) + u2 * (x0 * y1 - x1 * y0)) / den;
    const d = (v0 * (y1 - y2) + v1 * (y2 - y0) + v2 * (y0 - y1)) / den, e = (v0 * (x2 - x1) + v1 * (x0 - x2) + v2 * (x1 - x0)) / den;
    const f = (v0 * (x1 * y2 - x2 * y1) + v1 * (x2 * y0 - x0 * y2) + v2 * (x0 * y1 - x1 * y0)) / den;
    // grow the clip triangle by ~0.6 px around its centroid to hide seams
    const cx = (u0 + u1 + u2) / 3, cy = (v0 + v1 + v2) / 3, gr = (p) => { const dx = p[0] - cx, dy = p[1] - cy, m = Math.hypot(dx, dy) || 1; return [p[0] + dx / m * 0.6, p[1] + dy / m * 0.6]; };
    const A = gr(d0), B = gr(d1), Cc = gr(d2);
    g.save(); g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.lineTo(Cc[0], Cc[1]); g.closePath(); g.clip();
    g.transform(a, d, b, e, c, f); g.drawImage(src, 0, 0); g.restore();
  };
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const s = (ii, jj) => [ii / nx * sw, jj / ny * sh], d = (ii, jj) => P[jj * (nx + 1) + ii];
    tri(s(i, j), s(i + 1, j), s(i + 1, j + 1), d(i, j), d(i + 1, j), d(i + 1, j + 1));
    tri(s(i, j), s(i + 1, j + 1), s(i, j + 1), d(i, j), d(i + 1, j + 1), d(i, j + 1));
  }
}

// a quad from params: corners (8 numbers, keyframable) or a flat box at x,y (centre) with w,h and rotate
export function quadOf(env, p, w, h) {
  const c = env.val(p.corners);
  if (Array.isArray(c) && c.length === 8) return c;
  const x = env.val(p.x, 960), y = env.val(p.y, 540), r = env.val(p.rotate, 0) * Math.PI / 180, cs = Math.cos(r), sn = Math.sin(r);
  return [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]].flatMap(([u, v]) => [x + u * cs - v * sn, y + u * sn + v * cs]);
}
