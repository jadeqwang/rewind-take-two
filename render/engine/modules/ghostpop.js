// ghostpop.js: Celeste's death pop for one ghost (DeathEffect): eight orbs burst out of the body in a ring that turns a
// quarter as it opens; each orb swells to full size by mid-way, then shrinks to nothing as the ring reaches its radius.
// The orbs flicker between the ghost's colour and white every two frames and carry an ink outline, as Celeste outlines
// them in black. On the first two frames a white disc with a rim in her colour covers the body (the hit flash), so the
// ghost can end on the pop frame.
//   params: at (local s or absolute), x, y (design px, keyframable), color ('#F08A24'), dur .36 (s), R 150 (ring
//     radius, px), size 24 (orb radius at full, px), n 8, spin .25 (turns over dur), flash 1 (0 = no flash disc),
//     flashR 95, rim 7 (px, in color), flashColor ('#ffffff'), ink '#0b0b0c' (null = no outline), line 3
import { absT } from './lib/text.js';
import { clamp } from '../src/core.js';

const outCubic = u => 1 - (1 - u) ** 3;

export function draw(lt, env) {
  const g = env.ctx, p = env.params;
  const t0 = absT(env, p.at, 0), dt = env.t - t0, dur = p.dur ?? 0.36;
  if (dt < -1e-6 || dt > dur) return;
  const e = clamp(dt / dur), x = env.val(p.x, 960), y = env.val(p.y, 540);
  const R = (p.R ?? 150) * outCubic(e), n = p.n ?? 8, spin = p.spin ?? 0.25;
  const sc = e < 0.5 ? 0.5 + e : outCubic(1 - (e - 0.5) * 2);          // Celeste: grow to 1 by halfway, then shrink away
  const r = (p.size ?? 24) * sc;
  const white = Math.floor(dt * 12 + 1e-6) % 2 === 1;                    // colour / white, alternating every 2 frames
  const col = white ? '#ffffff' : (p.color || '#F08A24');
  g.save();
  const fl = p.flash ?? 1;
  if (fl > 0 && dt < 0.09) {                                             // the hit: a white disc with a rim in her colour
    const fr = (p.flashR ?? 95) * (1 - 0.35 * dt / 0.09), rim = p.rim ?? 7;   // (plain white would vanish on the paper)
    g.globalAlpha = fl * (1 - 0.5 * dt / 0.09);
    g.beginPath(); g.arc(x, y, fr, 0, Math.PI * 2);
    g.fillStyle = p.flashColor || '#ffffff'; g.fill();
    g.lineWidth = rim; g.strokeStyle = p.color || '#F08A24'; g.stroke();
    if (p.ink !== null) {
      g.beginPath(); g.arc(x, y, fr + rim / 2 + 1, 0, Math.PI * 2);
      g.lineWidth = 2; g.strokeStyle = p.ink || '#0b0b0c'; g.stroke();
    }
    g.globalAlpha = 1;
  }
  if (r > 0.3) {
    for (let j = 0; j < n; j++) {
      const a = (j / n + e * spin) * Math.PI * 2, ox = x + Math.cos(a) * R, oy = y + Math.sin(a) * R;
      g.beginPath(); g.arc(ox, oy, r, 0, Math.PI * 2);
      g.fillStyle = col; g.fill();
      if (p.ink !== null) { g.lineWidth = p.line ?? 3; g.strokeStyle = p.ink || '#0b0b0c'; g.stroke(); }
    }
  }
  g.restore();
}
