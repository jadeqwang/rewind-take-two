// variance_report.js (section F, O1 overlay 211.64-218.92): the agency's variance report slides in over the 3D Penrose
// Loop, types out, then UN-WRITES itself line by line (characters retract right to left, last line first) and a stamp
// slams on: TIMELINE NOW CANON. IBM Plex Mono, ink on paper; every '█' is a solid redaction block.
//   params (absolute song times or local seconds): slideIn [t0, t1], lines [...], cps 30, unwrite [t0, t1],
//   stamp {text, at, scale 1.25 (x size)}, rect [x, y, w, h] (design px), size 30, ink, paper, stampColor
import { absT } from '../../../render/engine/modules/lib/text.js';

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const outCubic = u => 1 - (1 - u) ** 3;

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const ink = p.ink || '#0b0b0c', paper = p.paper || '#ece7dc', size = p.size ?? 30;
  const [rx, ry, rw, rh] = p.rect || [1060, 600, 780, 380];
  const [s0, s1] = (p.slideIn || [0, 0.35]).map(x => absT(env, x));
  const slide = outCubic(clamp((t - s0) / Math.max(1e-3, s1 - s0)));
  if (slide <= 0) return;
  const dx = (1 - slide) * (1920 - rx + 40);
  g.save(); g.translate(dx, 0);
  g.fillStyle = paper; g.globalAlpha = 0.96; g.fillRect(rx, ry, rw, rh); g.globalAlpha = 1;
  g.strokeStyle = ink; g.lineWidth = 3; g.strokeRect(rx + 10, ry + 10, rw - 20, rh - 20);
  g.font = `700 ${size}px "IBM Plex Mono"`; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  const cw = g.measureText('M').width, lh = size * 1.55;
  const lines = p.lines || [];
  const cps = p.cps ?? 30;
  const [u0, u1] = (p.unwrite || [1e9, 1e9]).map(x => absT(env, x));
  let cursor = s1;
  const n = lines.length;
  lines.forEach((text, li) => {
    const tStart = cursor;
    cursor += text.length / cps + 0.12;
    // un-write: last line first, each line gets an equal slice of [u0, u1]
    const slice = (u1 - u0) / Math.max(1, n), k = n - 1 - li;
    const ua = u0 + k * slice, ub = ua + slice * 0.9;
    const typed = Math.floor(clamp((t - tStart) * cps, 0, text.length));
    const gone = Math.floor(clamp((t - ua) / Math.max(1e-3, ub - ua)) * text.length);
    const shown = Math.max(0, typed - gone);
    const x0 = rx + 46, y = ry + 46 + size + li * lh;
    for (let i = 0; i < shown; i++) {
      const c = text[i], x = x0 + i * cw;
      if (c === '█') { g.fillStyle = ink; g.fillRect(x - 0.5, y - size * 0.8, cw + 1, size * 0.98); }
      else if (c !== ' ') { g.fillStyle = ink; g.fillText(c, x, y); }
    }
    if (typed > 0 && shown > 0 && (typed < text.length || (t >= ua && t < ub))) {     // cursor while typing / retracting
      g.fillStyle = ink; g.fillRect(x0 + shown * cw + 3, y - size * 0.78, cw * 0.6, size * 0.95);
    }
  });
  // stamp
  if (p.stamp) {
    const ts = absT(env, p.stamp.at);
    if (t >= ts) {
      const since = t - ts, s = 1 + 0.6 * Math.exp(-since / 0.05);
      const col = p.stampColor || ink;      // agency UI is black and white only (no red)
      g.save(); g.translate(rx + rw / 2, ry + rh / 2); g.rotate(-0.12); g.scale(s, s);
      const ss = size * (p.stamp.scale ?? 1.25) / 1.25;      // box and stroke grow with the type
      g.font = `700 ${ss * 1.25}px "IBM Plex Mono"`; g.textAlign = 'center'; g.textBaseline = 'middle';
      const tw = g.measureText(p.stamp.text).width;
      g.globalAlpha = clamp(since / 0.04) * 0.92;
      g.strokeStyle = col; g.lineWidth = 6 * ss / size; g.strokeRect(-tw / 2 - 26 * ss / size, -ss * 1.05, tw + 52 * ss / size, ss * 2.1);
      g.fillStyle = col; g.fillText(p.stamp.text, 0, 2);
      g.restore();
    }
  }
  g.restore();
}
