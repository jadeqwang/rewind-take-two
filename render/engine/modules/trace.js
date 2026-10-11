// trace.js: "it couldn't trace". A dotted line traces the letters of a word, then loses the path and wanders off.
//   params: text 'trace', font 'fell', size 220, x 960, y 620 (baseline centre), color ink (or '#F08A24'),
//     at (start: local s or absolute, e.g. 'word:trace'), dur 1.6 (s to reach the point where it loses the path),
//     lose .62 (fraction of the outline traced before it loses it), wander 1.4 (s of wandering), wanderLen 520 (px),
//     spacing 9 (px between dots), dot 2.6 (radius), ghost 0 (alpha of the faint word underneath), fadeOut .6, seed
// The outline is extracted once (init) from the rendered glyphs: edge pixels ordered by a nearest-neighbour walk
// (jumps between letters become pen lifts). Everything after that is a pure function of time.
import { C, absT, fontName } from './lib/text.js';
import { clamp, noise1, EASE } from '../src/core.js';

export function init(ctx, p) {
  const size = p.size ?? 220, text = p.text ?? 'trace', font = `${size}px ${fontName(p.font || 'fell')}`;
  const c = document.createElement('canvas'), g = c.getContext('2d', { willReadFrequently: true });
  g.font = font; const w = Math.ceil(g.measureText(text).width + size * 0.4), h = Math.ceil(size * 1.6);
  c.width = w; c.height = h; g.font = font; g.textBaseline = 'alphabetic'; g.fillStyle = '#000'; g.fillText(text, size * 0.2, size * 1.15);
  const a = g.getImageData(0, 0, w, h).data, step = 3, pts = [];
  const on = (x, y) => x >= 0 && y >= 0 && x < w && y < h && a[(y * w + x) * 4 + 3] > 128;
  for (let y = 0; y < h; y += step) for (let x = 0; x < w; x += step) if (on(x, y) && (!on(x - step, y) || !on(x + step, y) || !on(x, y - step) || !on(x, y + step))) pts.push([x, y]);
  // nearest-neighbour ordering from the leftmost point
  pts.sort((p1, p2) => p1[0] - p2[0] || p1[1] - p2[1]);
  const used = new Uint8Array(pts.length), path = []; let cur = 0; used[0] = 1; path.push({ x: pts[0][0], y: pts[0][1], lift: true });
  for (let k = 1; k < pts.length; k++) {
    let best = -1, bd = 1e18;
    for (let j = 0; j < pts.length; j++) if (!used[j]) { const dx = pts[j][0] - pts[cur][0], dy = pts[j][1] - pts[cur][1], d = dx * dx + dy * dy; if (d < bd) { bd = d; best = j; } }
    used[best] = 1; path.push({ x: pts[best][0], y: pts[best][1], lift: bd > (step * 4) ** 2 }); cur = best;
  }
  let len = 0; for (let k = 0; k < path.length; k++) { if (k && !path[k].lift) len += Math.hypot(path[k].x - path[k - 1].x, path[k].y - path[k - 1].y); path[k].s = len; }
  return { path, len, w, h, ox: -w / 2 + 0, oy: -size * 1.15, text, font };
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, S = env.state, t = env.t;
  const x = env.val(p.x, 960), y = env.val(p.y, 620), color = env.val(p.color, C.ink);
  const t0 = absT(env, p.at, 0), dur = p.dur ?? 1.6, lose = p.lose ?? 0.62, wd = p.wander ?? 1.4, sp = p.spacing ?? 9, r = p.dot ?? 2.6;
  if (t < t0) return;
  const u = clamp((t - t0) / dur), sMax = S.len * lose * EASE.inOutSine(u);
  const fade = clamp(1 - (t - (t0 + dur + wd)) / (p.fadeOut ?? 0.6)); if (fade <= 0) return;
  g.save(); g.translate(x + S.ox, y + S.oy); g.fillStyle = color;
  if (p.ghost) { g.globalAlpha = p.ghost; g.font = S.font; g.textBaseline = 'alphabetic'; g.fillText(S.text, (p.size ?? 220) * 0.2, (p.size ?? 220) * 1.15); }
  g.globalAlpha = env.val(p.opacity, 1) * fade;
  let next = 0, lastPt = null, dir = [1, 0];
  for (let k = 0; k < S.path.length; k++) {
    const q = S.path[k]; if (q.s > sMax) break;
    if (q.s >= next || q.lift) { g.beginPath(); g.arc(q.x, q.y, r, 0, 7); g.fill(); next = q.s + sp; }
    if (lastPt && !q.lift) { const dx = q.x - lastPt.x, dy = q.y - lastPt.y, m = Math.hypot(dx, dy) || 1; dir = [dx / m, dy / m]; }
    lastPt = q;
  }
  // lost: the line keeps going, curving on noise, drifting away from the letters
  if (lastPt && t > t0 + dur) {
    const wu = clamp((t - t0 - dur) / wd), L = (p.wanderLen ?? 520) * EASE.outCubic(wu), seed = p.seed ?? 4;
    let px = lastPt.x, py = lastPt.y, ang = Math.atan2(dir[1], dir[0]);
    for (let s = 0; s < L; s += 3) {
      ang += noise1(s * 0.012, seed) * 0.11 + 0.004;
      px += Math.cos(ang) * 3; py += Math.sin(ang) * 3;
      if (Math.floor(s / sp) !== Math.floor((s - 3) / sp)) { g.globalAlpha = env.val(p.opacity, 1) * fade * (1 - 0.7 * s / Math.max(1, L)); g.beginPath(); g.arc(px, py, r * (1 - 0.4 * s / 600), 0, 7); g.fill(); }
    }
    g.globalAlpha = fade; g.beginPath(); g.arc(px, py, r * 2.2, 0, 7); g.lineWidth = 1.5; g.strokeStyle = color; g.stroke();   // the lost tracer head
  } else if (lastPt) { g.beginPath(); g.arc(lastPt.x, lastPt.y, r * 2.2, 0, 7); g.lineWidth = 1.5; g.strokeStyle = color; g.stroke(); }
  g.restore();
}
