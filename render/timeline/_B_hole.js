// Section B (chase restage): a bullet hole punched through a board, with splinters. Canvas2D, a pure function of the
// layer clock. Ink and paper only.
//   params.at (layer-local s), x, y (design px), r 15 (hole radius), cracks 7, splinters 14, ink, paper
import { clamp, hash, hsig } from '../engine/src/core.js';

const F = 24, TAU = Math.PI * 2;

export function draw(lt, env) {
  const g = env.ctx, p = env.params, at = p.at ?? 0;
  if (lt < at) return;
  const dt = lt - at, fr = dt * F, x = p.x, y = p.y, r = p.r ?? 15, ink = p.ink || '#0b0b0c', paper = p.paper || '#fbf8f1', s = 31;
  g.lineCap = 'round'; g.lineJoin = 'round';
  // cracks radiating from the hole (they stay)
  g.strokeStyle = ink;
  for (let i = 0; i < (p.cracks ?? 7); i++) {
    const a = (i + 0.6 * hash(s, i)) / (p.cracks ?? 7) * TAU, l = r * (1.3 + 1.9 * hash(s, i, 2));
    g.lineWidth = 2.4 - 1.2 * hash(s, i, 3);
    g.beginPath(); g.moveTo(x + Math.cos(a) * r * 0.8, y + Math.sin(a) * r * 0.8);
    g.lineTo(x + Math.cos(a + 0.12 * hsig(s, i, 4)) * (r + l * 0.55), y + Math.sin(a + 0.12 * hsig(s, i, 4)) * (r + l * 0.55));
    g.lineTo(x + Math.cos(a) * (r + l), y + Math.sin(a) * (r + l)); g.stroke();
  }
  // the hole: a ragged ink polygon with a pale torn rim
  const pts = Array.from({ length: 11 }, (_, i) => { const a = i / 11 * TAU, rr = r * (0.75 + 0.45 * hash(s, i, 5)); return [x + Math.cos(a) * rr, y + Math.sin(a) * rr]; });
  g.fillStyle = paper; g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q[0] * 1 + (q[0] - x) * 0.35, q[1] + (q[1] - y) * 0.35) : g.moveTo(q[0] + (q[0] - x) * 0.35, q[1] + (q[1] - y) * 0.35))); g.closePath(); g.fill();
  g.strokeStyle = ink; g.lineWidth = 2; g.stroke();
  g.fillStyle = ink; g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.closePath(); g.fill();
  // first two frames: a paper puff around it
  if (fr < 2) {
    g.globalAlpha = fr < 1 ? 1 : 0.6; g.strokeStyle = ink; g.lineWidth = 4; g.fillStyle = paper;
    for (let k = 0; k < 6; k++) { const a = k / 6 * TAU + 0.4, R = r * (2.2 + (fr < 1 ? 0 : 0.8)); g.beginPath(); g.arc(x + Math.cos(a) * R, y + Math.sin(a) * R * 0.8, r * (0.9 + 0.5 * hash(s, k, 9)), 0, TAU); g.stroke(); g.fill(); }
    g.globalAlpha = 1;
  }
  // splinters: thin wooden slivers thrown out, tumbling, falling
  const life = 0.55;
  if (dt < life) {
    g.fillStyle = ink; g.globalAlpha = clamp(1 - (dt / life) ** 2);
    for (let i = 0; i < (p.splinters ?? 14); i++) {
      const a = -Math.PI / 2 + hsig(s, i, 6) * 1.9, v = 380 + 620 * hash(s, i, 7);
      const px = x + Math.cos(a) * v * dt, py = y + Math.sin(a) * v * dt + 0.5 * 2200 * dt * dt, L = 10 + 16 * hash(s, i, 8);
      g.save(); g.translate(px, py); g.rotate(a + dt * 16 * hsig(s, i, 10));
      g.beginPath(); g.moveTo(-L, -1.5); g.lineTo(L, 0); g.lineTo(-L, 2.5); g.closePath(); g.fill();
      g.restore();
    }
    g.globalAlpha = 1;
  }
}
