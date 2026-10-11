// motes.js: Celeste-style death burst: a ring of shards and a halo of colored motes thrown out from a point, slowing
// with drag (freeze them with the shot's `hold` / `tapeStop` fx; replay backwards in a comp to implode).
//   params: at (local s or absolute, e.g. 40.24), x, y (keyframable centre), count 56, colors ['#F08A24', '#8DB8E8'],
//     speed 1100 (px/s), drag 3.4, gravity 60, size 9, life 1.6 (s fade), ring true (the 8-orb ring that expands and
//     snaps shut), shape 'diamond'|'square'|'circle', glow .7, spread 1 (0..1 of a full circle), angle (deg, centre of
//     the spread), seed
import { absT } from './lib/text.js';
import { clamp, hash, hsig, hexRgb } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params;
  const t0 = absT(env, p.at, 0), dt = env.t - t0; if (dt < 0) return;
  const life = p.life ?? 1.6; if (dt > life + 0.5) return;
  const x = env.val(p.x, 960), y = env.val(p.y, 540), n = p.count ?? 56, seed = p.seed ?? 11;
  const cols = (p.colors || ['#F08A24', '#8DB8E8']).map(hexRgb), sp = p.speed ?? 1100, k = p.drag ?? 3.4, gr = p.gravity ?? 60, size = p.size ?? 9;
  const spread = (p.spread ?? 1) * Math.PI * 2, a0 = (p.angle ?? 0) * Math.PI / 180 - spread / 2;
  const fade = clamp(1 - (dt - life * 0.55) / (life * 0.45));
  g.save(); g.globalCompositeOperation = 'lighter';
  const glow = p.glow ?? 0.7;
  if (glow > 0) { g.shadowBlur = 14 * glow; }
  for (let i = 0; i < n; i++) {
    const ang = a0 + spread * (i + hash(seed, i) * 0.8) / n, v = sp * (0.35 + 0.65 * hash(seed, i, 1)), kk = k * (0.7 + 0.6 * hash(seed, i, 2));
    const d = v / kk * (1 - Math.exp(-kk * dt));
    const px = x + Math.cos(ang) * d, py = y + Math.sin(ang) * d + 0.5 * gr * dt * dt;
    const c = cols[i % cols.length], flick = 0.75 + 0.25 * Math.sin(dt * 40 + i), a = fade * flick;
    const s = size * (0.5 + hash(seed, i, 3)) * (1 - 0.4 * clamp(dt / life));
    g.fillStyle = `rgba(${c.map(q => Math.round(q * 255)).join(',')},${a.toFixed(3)})`; g.shadowColor = g.fillStyle;
    g.save(); g.translate(px, py); g.rotate(dt * 6 * hsig(seed, i, 4) + ang);
    if ((p.shape || 'diamond') === 'circle') { g.beginPath(); g.arc(0, 0, s * 0.6, 0, 7); g.fill(); }
    else if (p.shape === 'square') g.fillRect(-s / 2, -s / 2, s, s);
    else { g.beginPath(); g.moveTo(0, -s); g.lineTo(s * 0.6, 0); g.lineTo(0, s); g.lineTo(-s * 0.6, 0); g.closePath(); g.fill(); }
    g.restore();
  }
  if (p.ring !== false && dt < 0.75) {   // Celeste: eight orbs fly out, hang, and snap shut
    const u = dt / 0.75, R = 150 * Math.sin(Math.PI * Math.min(1, u * 1.15)) * (1 - 0.15 * u), a = clamp(1 - Math.max(0, u - 0.7) / 0.3);
    for (let j = 0; j < 8; j++) {
      const an = j * Math.PI / 4 + dt * 1.5, c = cols[j % cols.length];
      g.fillStyle = `rgba(${c.map(q => Math.round(q * 255)).join(',')},${a.toFixed(3)})`; g.shadowColor = g.fillStyle;
      g.beginPath(); g.arc(x + Math.cos(an) * R, y + Math.sin(an) * R, 13 * (1 - 0.5 * u), 0, 7); g.fill();
    }
    if (dt < 0.08) { g.fillStyle = `rgba(255,250,240,${(1 - dt / 0.08).toFixed(3)})`; g.beginPath(); g.arc(x, y, 90, 0, 7); g.fill(); }   // the hit flash
  }
  g.restore();
}
