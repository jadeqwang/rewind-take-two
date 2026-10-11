// b_dashfx.js (section B, chase restage): the drawn marks of a Celeste-style air dash. Canvas2D, a pure function of the
// layer clock, so it freezes with the shot's `hold` and replays backwards in a comp. Built by dash() in
// render/timeline/_B_fx.js, which adds the freeze (fx hold), the dark frame (video layer) and the afterimages (ghosts).
//   params.at      layer time of the dash (the freeze frame); the ring bursts on the first frame after it
//   params.center  follow spec for the ring centre, e.g. {layer: 'jade', point: 'centroid'}
//   params.ring    {r0 40, r1 270, frames 6, width 16} | false   white ring: expands and fades over `frames`
//   params.land    layer time of the landing (omit for no landing marks)
//   params.feet    follow spec for the landing point, e.g. {layer: 'jade', point: 'bottom'}
//   params.disc    {r 80} | false       white disc at her feet, one frame
//   params.dust    {r0 60, r1 270, frames 10, puffs 18, squash .3} | false   dust ring on the ground
//   params.line    {width 7, trail .25 (s), gap 70 (px short of her centre), fade 5 (frames after landing)} | false
//                  thin white speed line: a straight tapered stroke from where she was `trail` s ago to her
//   params.scroll  [vx, vy] px/s, or lt => [dx, dy] (cumulative): world motion, so marks stay where they were made
//   params.part    'under' (speed line: goes below her) | 'over' (ring, disc, dust) | 'all'
//   params.white '#ffffff', params.ink '#0b0b0c' (every white mark carries an ink keyline: the world is paper)
import { clamp, hash, EASE } from '../src/core.js';

const F = 24;
export function disp(scroll, t) {
  if (typeof scroll === 'function') { const d = scroll(t); return Array.isArray(d) ? d : [d, 0]; }
  const s = scroll || [0, 0]; return [s[0] * t, (s[1] || 0) * t];
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, at = p.at ?? 0, white = p.white || '#ffffff', ink = p.ink || '#0b0b0c';
  const now = disp(p.scroll, lt);
  const world = (pt, t0) => { const b = disp(p.scroll, t0); return [pt[0] + now[0] - b[0], pt[1] + now[1] - b[1]]; };
  const part = p.part || 'all', a = (lt - at) * F;
  g.lineJoin = 'round'; g.lineCap = 'round';

  // ---- the speed line: straight, tapered to nothing at the tail, world-anchored at the tail end
  const L = p.line === false ? null : { width: 7, trail: 0.25, gap: 70, fade: 5, ...(p.line || {}) };
  if (L && part !== 'over' && a > 0.5) {
    const stop = p.land ?? at + 0.5, th = Math.min(lt, stop), tt = Math.max(at, lt - L.trail);
    const al = lt <= stop ? 1 : clamp(1 - (lt - stop) * F / L.fade);
    const fol = env.follow(p.center), h0 = fol(th), t0 = fol(tt);
    if (al > 0 && h0 && t0 && th > tt) {
      const H = world(h0, th), Tl = world(t0, tt), dx = H[0] - Tl[0], dy = H[1] - Tl[1], len = Math.hypot(dx, dy);
      if (len > L.gap + 20) {
        const ux = dx / len, uy = dy / len, hx = H[0] - ux * L.gap, hy = H[1] - uy * L.gap, nx = -uy * L.width / 2, ny = ux * L.width / 2;
        g.globalAlpha = al;
        g.beginPath(); g.moveTo(Tl[0], Tl[1]); g.lineTo(hx + nx, hy + ny); g.lineTo(hx - nx, hy - ny); g.closePath();
        g.strokeStyle = ink; g.lineWidth = 5; g.stroke(); g.fillStyle = white; g.fill();
      }
    }
  }
  if (part === 'under') return;

  // ---- the ring: bursts where she was at the freeze
  const R = p.ring === false ? null : { r0: 40, r1: 270, frames: 6, width: 16, ...(p.ring || {}) };
  if (R && a > 0.5 && a < R.frames + 0.5) {
    const c0 = env.follow(p.center)(at);
    if (c0) {
      const [x, y] = world(c0, at), u = clamp((a - 1) / Math.max(1, R.frames - 1));
      const r = R.r0 + (R.r1 - R.r0) * EASE.outCubic(a / R.frames), w = R.width * (1 - 0.6 * u);
      g.globalAlpha = 1 - 0.85 * u;
      g.strokeStyle = ink; g.lineWidth = w + 6; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.stroke();
      g.strokeStyle = white; g.lineWidth = w; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.stroke();
    }
  }

  // ---- the landing: a one-frame disc, then a dust ring spreading along the ground
  if (p.land === undefined || p.land === null || lt < p.land) return;
  const b = (lt - p.land) * F, f0 = env.follow(p.feet || p.center)(p.land);
  if (!f0) return;
  const [fx, fy] = world(f0, p.land);
  const Dn = p.dust === false ? null : { r0: 60, r1: 270, frames: 10, puffs: 18, squash: 0.3, ...(p.dust || {}) };
  if (Dn && b < Dn.frames) {
    const u = clamp(b / Dn.frames), rx = Dn.r0 + (Dn.r1 - Dn.r0) * EASE.outCubic(u), ry = rx * Dn.squash, al = (1 - u) ** 0.8;
    // a ring of overlapping puffs: every outline first, then every fill, so they merge into one scalloped cloud that
    // breaks up into separate puffs as it spreads
    const puffs = Array.from({ length: Dn.puffs }, (_, j) => {
      const th = (j + 0.5 * hash('dust', j, 4)) / Dn.puffs * Math.PI * 2, k = hash('dust', j), k2 = hash('dust', j, 2);
      return [fx + Math.cos(th) * rx * (0.9 + 0.2 * k), fy + Math.sin(th) * ry * (0.9 + 0.2 * k) - (8 + 24 * k2) * u,
        (22 + 20 * k2) * (1 - 0.45 * u) * (0.6 + 0.4 * Math.min(1, b + 0.5))];
    });
    g.globalAlpha = al;
    g.strokeStyle = ink; g.lineWidth = 6; for (const q of puffs) { g.beginPath(); g.arc(q[0], q[1], q[2], 0, Math.PI * 2); g.stroke(); }
    g.fillStyle = white; for (const q of puffs) { g.beginPath(); g.arc(q[0], q[1], q[2], 0, Math.PI * 2); g.fill(); }
  }
  const Ds = p.disc === false ? null : { r: 80, ...(p.disc || {}) };
  if (Ds && b < 1) {
    g.globalAlpha = 1;
    g.fillStyle = white; g.beginPath(); g.arc(fx, fy, Ds.r, 0, Math.PI * 2); g.fill();
    g.strokeStyle = ink; g.lineWidth = 3; g.stroke();
  }
}
