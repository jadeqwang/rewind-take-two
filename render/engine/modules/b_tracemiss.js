// b_tracemiss.js (section B, chase restage): "they shoot where she was". For each shot time tb: a thin ruled, dashed
// ink line draws from the pistol to the spot she left `lag` s earlier (tb - lead → tb; while it draws, its head keeps
// trailing her by `lag`), then a 2-frame muzzle starburst at the pistol, a burst of ink turf flecks at the spot she
// left at tb - lag, and an ink scar that stays there. No bullet, no colour: ink and
// paper only. Canvas2D, a pure function of the layer clock. Built by traceMiss() in render/timeline/_B_fx.js.
//   params.times    [tb, ...] layer-local seconds
//   params.origin   [x, y] design px (keyframable: [[t, [x, y]], ...]): the pistol
//   params.target   follow spec for her feet, e.g. {layer: 'jade', point: 'bottom', smooth: 4, offset: [0, 0]}
//   params.targets  optional [[x, y] | null, ...] explicit target per shot (design px at tb - lag), overrides the track
//   params.lag .25  she is aimed at where she was this long before tb;  params.lead .33  the line starts this early
//   params.scroll   [vx, vy] px/s, or lt => [dx, dy] (cumulative): world motion, so target, flecks and scar stay in
//                   world space on a side-tracking plate
//   params.part     'under' (scars) | 'over' (line, starburst, flecks) | 'all'
//   params.size 1   scales every mark (they are drawn for a figure about a third of the frame tall)
//   params.width 4 (line), dash [22, 13], burst 110 (starburst radius), flecks 18, scar 1 (scale), ink, paper
import { clamp, hash, hsig, EASE } from '../src/core.js';
import { disp } from './b_dashfx.js';

const F = 24, TAU = Math.PI * 2;

function starburst(g, x, y, R, dir, seed, ink, paper) {
  const n = 9, pts = [];
  for (let i = 0; i < n * 2; i++) {
    const a = dir + (i / (n * 2)) * TAU, tip = i % 2 === 0;
    const along = Math.cos(a - dir);                                   // longer spikes down the barrel
    const r = tip ? R * (0.62 + 0.5 * hash(seed, i)) * (1 + 0.55 * Math.max(0, along)) : R * (0.22 + 0.1 * hash(seed, i, 2));
    pts.push([x + Math.cos(a) * r, y + Math.sin(a) * r]);
  }
  g.lineJoin = 'miter'; g.miterLimit = 6;
  g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.closePath();
  g.fillStyle = paper; g.fill(); g.strokeStyle = ink; g.lineWidth = 3.2; g.stroke();
  // engraved: short hatch strokes down the middle of each spike, and loose ticks beyond the tips
  g.lineCap = 'butt';
  for (let i = 0; i < n * 2; i += 2) {
    const a = dir + (i / (n * 2)) * TAU, tipR = Math.hypot(pts[i][0] - x, pts[i][1] - y);
    g.lineWidth = 1.6; g.beginPath(); g.moveTo(x + Math.cos(a) * R * 0.2, y + Math.sin(a) * R * 0.2); g.lineTo(x + Math.cos(a) * tipR * 0.62, y + Math.sin(a) * tipR * 0.62); g.stroke();
    const a2 = a + (0.5 / n) * TAU, r0 = R * (0.75 + 0.3 * hash(seed, i, 5));
    g.lineWidth = 2.2; g.beginPath(); g.moveTo(x + Math.cos(a2) * r0, y + Math.sin(a2) * r0); g.lineTo(x + Math.cos(a2) * (r0 + R * (0.14 + 0.2 * hash(seed, i, 6))), y + Math.sin(a2) * (r0 + R * (0.14 + 0.2 * hash(seed, i, 6)))); g.stroke();
  }
  g.fillStyle = ink; g.beginPath(); g.arc(x, y, R * 0.07, 0, TAU); g.fill();
}

function scar(g, x, y, s, seed, ink, paper) {
  g.save(); g.translate(x, y); g.rotate(hsig(seed, 1) * 0.18); g.scale(s, s);
  g.fillStyle = paper; g.beginPath(); g.ellipse(4, -7, 40, 9, 0, 0, TAU); g.fill();                 // thrown soil: a pale lip behind the gouge
  g.fillStyle = ink; g.beginPath(); g.ellipse(0, 0, 36, 8, 0, 0, TAU); g.fill();                     // the gouge
  g.strokeStyle = ink; g.lineCap = 'round';
  for (let i = 0; i < 9; i++) {                                                                      // hatch strokes fanning out of it
    const a = -Math.PI * (0.08 + 0.84 * (i + 0.5 * hash(seed, i)) / 9), r0 = 16 + 12 * hash(seed, i, 2), r1 = r0 + 16 + 26 * hash(seed, i, 3);
    g.lineWidth = 2.6 - 1.2 * hash(seed, i, 4);
    g.beginPath(); g.moveTo(Math.cos(a) * r0 * 1.9, Math.sin(a) * r0 * 0.55); g.lineTo(Math.cos(a) * r1 * 1.9, Math.sin(a) * r1 * 0.75); g.stroke();
  }
  g.restore();
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, part = p.part || 'all', ink = p.ink || '#0b0b0c', paper = p.paper || '#fbf8f1';
  const lag = p.lag ?? 0.25, lead = p.lead ?? 0.33, over = part !== 'under', under = part !== 'over', Z = p.size ?? 1;
  const fol = p.target ? env.follow(p.target) : null;
  const O = env.val(p.origin, [300, 520]);
  // where the point she stood on at time `then` is on screen at time `when` (the world may have scrolled since)
  const spot = (k, then, when) => {
    const P = (p.targets && p.targets[k]) || (fol && fol(then)); if (!P) return null;
    const a = disp(p.scroll, when), b = disp(p.scroll, then); return [P[0] + a[0] - b[0], P[1] + a[1] - b[1]];
  };
  (p.times || []).forEach((tb, k) => {
    if (lt < tb - lead) return;
    const dt = lt - tb, fr = dt * F, seed = 31 + k * 7;
    const hit = spot(k, tb - lag, lt); if (!hit) return;                 // the hit point: fixed in the world from tb on
    const [tx, ty] = hit, dir = Math.atan2(ty - O[1], tx - O[0]);

    if (under && dt >= 0) scar(g, tx, ty, (p.scar ?? 1) * Z * (fr < 1 ? 1.3 : 1), seed, ink, paper);
    if (!over) return;

    // the announcement: a ruled dashed line from the pistol toward her residue, which trails her by `lag` the whole
    // time it is drawn (paper band underneath so it reads over hatching and black suits)
    if (fr < 2) {
      const aim = dt < 0 ? spot(k, lt - lag, lt) || hit : hit;
      const u = clamp((lt - (tb - lead)) / lead), e = EASE.out(Math.min(1, u * 1.6)), hx = O[0] + (aim[0] - O[0]) * e, hy = O[1] + (aim[1] - O[1]) * e;
      const al = dt < 0 ? 1 : fr < 1 ? 0.6 : 0.25, w = (p.width ?? 4) * Z;
      g.save(); g.lineCap = 'butt';
      g.globalAlpha = al * 0.9; g.strokeStyle = paper; g.lineWidth = w + 7 * Z; g.beginPath(); g.moveTo(O[0], O[1]); g.lineTo(hx, hy); g.stroke();
      g.globalAlpha = al; g.strokeStyle = ink; g.lineWidth = w; g.setLineDash((p.dash || [22, 13]).map(x => x * Z)); g.beginPath(); g.moveTo(O[0], O[1]); g.lineTo(hx, hy); g.stroke();
      g.setLineDash([]);
      // the head: a small surveyor's cross in a ring on the spot it is reaching for
      const c = 20 * Z; g.lineCap = 'round';
      g.fillStyle = paper; g.beginPath(); g.arc(hx, hy, c * 0.95, 0, TAU); g.fill();
      g.lineWidth = w * 0.8; g.strokeStyle = ink; g.beginPath(); g.arc(hx, hy, c * 0.95, 0, TAU); g.moveTo(hx - c * 1.5, hy); g.lineTo(hx + c * 1.5, hy); g.moveTo(hx, hy - c * 1.5); g.lineTo(hx, hy + c * 1.5); g.stroke();
      g.restore();
    }
    if (dt < 0) return;

    // the hit: a pale puff on the first two frames, turf flecks kicked up and forward
    const life = p.fleckLife ?? 0.42;
    if (dt < life) {
      const n = p.flecks ?? 18, fwd = Math.sign(Math.cos(dir)) || 1, G = 2600;
      g.save();
      if (fr < 2) {
        const q = fr < 1 ? 1 : 1.35, lumps = [[0, -14, 40], [-38, 0, 28], [36, -2, 30], [-8, -40, 26], [22, -34, 22]].map(c => [tx + c[0] * Z * q, ty + c[1] * Z * q, c[2] * Z * q]);
        g.globalAlpha = fr < 1 ? 1 : 0.65;
        g.strokeStyle = ink; g.lineWidth = 6; for (const c of lumps) { g.beginPath(); g.arc(c[0], c[1], c[2], 0, TAU); g.stroke(); }
        g.fillStyle = paper; for (const c of lumps) { g.beginPath(); g.arc(c[0], c[1], c[2], 0, TAU); g.fill(); }
      }
      g.fillStyle = ink; g.globalAlpha = clamp(1 - (dt / life) ** 2);
      for (let i = 0; i < n; i++) {
        const a = -Math.PI / 2 + fwd * 0.35 + hsig(seed, i) * 1.05, v = (420 + 680 * hash(seed, i, 2)) * Math.sqrt(Z);
        const x = tx + Math.cos(a) * v * dt, y = ty + Math.sin(a) * v * dt + 0.5 * G * dt * dt, s = (8 + 13 * hash(seed, i, 3)) * Z;
        g.save(); g.translate(x, y); g.rotate(a + dt * 14 * hsig(seed, i, 4));
        g.beginPath(); g.moveTo(-s, -s * 0.3); g.lineTo(s, 0); g.lineTo(-s * 0.7, s * 0.45); g.closePath(); g.fill();
        g.restore();
      }
      g.restore();
    }
    // the muzzle starburst: two frames, the second smaller and turned
    if (fr < 2) starburst(g, O[0], O[1], (p.burst ?? 110) * Z * (fr < 1 ? 1 : 0.62), dir + (fr < 1 ? 0 : 0.35), seed + (fr < 1 ? 0 : 3), ink, paper);
  });
}
