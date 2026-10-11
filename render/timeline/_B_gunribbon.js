// _B_gunribbon.js (v4 gunfire G1): her orange residue ribbon laid on the grass along her zigzag, in world space, so it
// stays on the lawn while the camera pushes in. Canvas2D, pure function of the song time (env.t).
//   params: trail (s, default 2.4), width (m, default 0.32), color
import { camAt, project, jadeAt } from './_B_glayout.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t, cam = camAt(t), trail = p.trail ?? 2.4, wm = p.width ?? 0.32;
  const n = 90, pts = [];
  for (let i = 0; i <= n; i++) {
    const tt = t - trail + (trail * i) / n - 0.06;            // ends a little behind her heels
    if (tt < 97.7) continue;
    const q = project(cam, jadeAt(tt));
    if (q[2] > 0.3) pts.push([q[0], q[1], cam.f * wm / q[2], i / n]);
  }
  g.save(); g.lineCap = 'round'; g.strokeStyle = p.color || '#F08A24';
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i];
    g.globalAlpha = 0.25 + 0.65 * b[3];
    g.lineWidth = Math.max(1.5, b[2] * 0.35);                // seen edge-on from eye height: flattened
    g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke();
  }
  g.restore();
}
