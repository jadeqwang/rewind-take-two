// ribbon.js: "causal residue": a colour ribbon trailing a keyframed or tracked path (Canvas2D module).
//   params.path   [[t, x, y], ...]  t = layer-local seconds (or absolute time strings); Catmull-Rom between keys
//   params.track  'path/to/track.json'  [[t,x,y],...] or [{t,x,y}] (layer-local seconds), used when path is absent
//   params.trail  seconds of history drawn (default: everything since the path starts: residue stays in the world)
//   params.drift  [vx, vy] px/s: world motion applied to older points (camera follows her, so residue streams behind)
//   params.width (px) | colors ['#ff7a1a', '#7ec8ff'] (head → tail) | twist (0..1 ribbon twist) | glow (0..1)
//   params.pencil (bool: hatched colored-pencil strokes instead of a solid band) | motes (0..1 density of motes shed along the trail)
//   params.seed
// Deterministic: points are sampled on a fixed 60 Hz grid of path time, so the trail never shimmers between frames;
// drawn backwards in time (a comp layer replaying it in reverse) the ribbon simply un-spools.
import { clamp, lerp, hexRgb, hash, hsig, noise1 } from '../src/core.js';

export async function init(ctx, params, env) {
  let path = params.path;
  if (!path && params.track) { const j = await env.loadJSON(params.track); path = j.map(p => (Array.isArray(p) ? p : [p.t, p.x, p.y])); }
  const keys = (path || []).map(k => [typeof k[0] === 'number' ? k[0] : env.T.time(k[0]) - env.shot.start, k[1], k[2]]).sort((a, b) => a[0] - b[0]);
  return { keys };
}

function at(keys, t) {
  const n = keys.length; if (!n) return [960, 540];
  if (t <= keys[0][0]) return [keys[0][1], keys[0][2]];
  if (t >= keys[n - 1][0]) return [keys[n - 1][1], keys[n - 1][2]];
  let i = 0; while (i < n - 2 && t >= keys[i + 1][0]) i++;
  const p0 = keys[Math.max(0, i - 1)], p1 = keys[i], p2 = keys[i + 1], p3 = keys[Math.min(n - 1, i + 2)];
  const u = (t - p1[0]) / (p2[0] - p1[0]), u2 = u * u, u3 = u2 * u;
  const cr = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3);
  return [cr(p0[1], p1[1], p2[1], p3[1]), cr(p0[2], p1[2], p2[2], p3[2])];
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, keys = env.state.keys;
  if (!keys.length) return;
  const t0 = keys[0][0], tEnd = Math.min(lt, keys[keys.length - 1][0] + (p.extend ?? 1e9));
  if (tEnd <= t0) return;
  const trail = env.val(p.trail, 1e9), from = Math.max(t0, tEnd - trail);
  const drift = p.drift || [0, 0], width = env.val(p.width, 28), twist = env.val(p.twist, 0.6), glow = env.val(p.glow, 0.6);
  const cols = (p.colors || ['#ff7a1a', '#7ec8ff']).map(hexRgb);
  const seed = p.seed ?? 7;
  // samples on a fixed grid
  const pts = [];
  const k0 = Math.ceil(from * 60 - 1e-6), k1 = Math.floor(tEnd * 60 + 1e-6);
  const push = tau => { const q = at(keys, tau), age = lt - tau; pts.push({ x: q[0] + drift[0] * age, y: q[1] + drift[1] * age, tau, age }); };
  for (let k = k0; k <= k1; k++) push(k / 60);
  if (!pts.length || pts[pts.length - 1].tau < tEnd - 1e-6) push(tEnd);
  if (pts.length < 2) return;
  const n = pts.length;
  // normals + half widths (twist: the band turns over, so its width breathes along the length)
  const L = [], R = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
    let dx = b.x - a.x, dy = b.y - a.y; const m = Math.hypot(dx, dy) || 1; dx /= m; dy /= m;
    const u = i / (n - 1);                                                 // 0 tail → 1 head
    const taper = Math.min(1, u * 6) * (0.35 + 0.65 * u);
    const tw = 1 - twist * 0.85 * Math.abs(Math.sin(pts[i].tau * 2.2 + seed));
    const hw = width * 0.5 * taper * tw * (1 + 0.12 * noise1(pts[i].tau * 3, seed));
    L.push([pts[i].x - dy * hw, pts[i].y + dx * hw]); R.push([pts[i].x + dy * hw, pts[i].y - dx * hw]);
  }
  const colAt = u => { const c = cols.length === 1 ? cols[0] : (() => { const x = (1 - u) * (cols.length - 1), j = Math.min(cols.length - 2, Math.floor(x)); const f = x - j; return cols[j].map((v, q) => lerp(v, cols[j + 1][q], f)); })(); return c.map(v => Math.round(v * 255)); };
  g.save();
  g.lineJoin = 'round'; g.lineCap = 'round';
  if (glow > 0) {   // soft bloom under the band
    g.globalCompositeOperation = 'lighter';
    for (let i = 1; i < n; i += 2) {
      const c = colAt(i / (n - 1));
      g.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${0.10 * glow})`; g.lineWidth = width * 2.2 * Math.min(1, i / n * 4);
      g.beginPath(); g.moveTo(pts[i - 1].x, pts[i - 1].y); g.lineTo(pts[i].x, pts[i].y); g.stroke();
    }
    g.globalCompositeOperation = 'source-over';
  }
  if (p.pencil) {   // coloured pencil: many thin hatched strokes across the band
    for (let i = 0; i < n - 1; i++) {
      const c = colAt(i / (n - 1));
      for (let s = 0; s < 3; s++) {
        const kk = Math.round(pts[i].tau * 60), r = hash(seed, kk, s), r2 = hash(seed, kk, s, 9);
        const a = L[i], b = R[Math.min(n - 1, i + 1)];
        g.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${0.35 + 0.5 * r})`; g.lineWidth = 1.2 + 1.4 * r2;
        g.beginPath(); g.moveTo(lerp(a[0], R[i][0], r * 0.3), lerp(a[1], R[i][1], r * 0.3)); g.lineTo(lerp(b[0], L[i + 1][0], r2 * 0.3), lerp(b[1], L[i + 1][1], r2 * 0.3)); g.stroke();
      }
    }
  } else {
    for (let i = 0; i < n - 1; i++) {
      const c = colAt((i + 0.5) / (n - 1)), shade = 0.82 + 0.18 * Math.cos(pts[i].tau * 2.2 + seed);   // the twist catches light
      g.fillStyle = `rgb(${Math.round(c[0] * shade)},${Math.round(c[1] * shade)},${Math.round(c[2] * shade)})`;
      g.beginPath(); g.moveTo(L[i][0], L[i][1]); g.lineTo(L[i + 1][0], L[i + 1][1]); g.lineTo(R[i + 1][0], R[i + 1][1]); g.lineTo(R[i][0], R[i][1]); g.closePath(); g.fill();
      g.strokeStyle = g.fillStyle; g.lineWidth = 1; g.stroke();   // hide hairline seams
    }
    // bright core thread
    g.strokeStyle = 'rgba(255,248,236,0.55)'; g.lineWidth = Math.max(1.5, width * 0.08);
    g.beginPath(); g.moveTo(pts[0].x, pts[0].y); for (let i = 1; i < n; i++) g.lineTo(pts[i].x, pts[i].y); g.stroke();
  }
  // motes shed along the trail (tied to grid ticks, so each mote is the same mote on every frame), drifting and fading with age
  const density = env.val(p.motes, 0.25);
  for (let i = 0; i < n; i++) {
    const kk = Math.round(pts[i].tau * 60); if (hash(seed, kk) > density) continue;
    const q = pts[i], age = q.age, c = colAt(i / (n - 1)), a = clamp(1 - age / 2.5) * (0.4 + 0.6 * hash(seed, kk, 2));
    if (a <= 0.01) continue;
    const ox = hsig(seed, kk, 3) * width * (0.8 + age * 1.5), oy = hsig(seed, kk, 4) * width * 0.8 - age * 18;
    g.fillStyle = `rgba(${c[0]},${c[1]},${c[2]},${a})`;
    g.beginPath(); g.arc(q.x + ox, q.y + oy, 1.5 + 2.5 * hash(seed, kk, 5), 0, 7); g.fill();
  }
  g.restore();
}
