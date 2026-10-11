// Section E, G1-G3 (engine Canvas2D module): the world's engraving has come loose. Clusters of short parallel hatch
// strokes drift round Jade on the empty page like iron filings in a field, slowly orbiting and aligning to circles
// about her. On the low boom (144.54) they are thrown outward; in G3 the strokes near her pencil bloom into
// coloured pencil (orange -> sky blue). Deterministic in t (absolute song time). Draw it under a matted Jade clip.
//   params: cx 960, cy 520 (field centre, design px), n 150 clusters, boom 144.54, bloomAt 146.6, bloomX/Y, ink
import { hash, hsig, clamp } from '../../engine/src/core.js';

const smooth = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };
const ORANGE = [240, 138, 36], SKY = [126, 200, 255], INK = [20, 18, 16];

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const cx = p.cx ?? 960, cy = p.cy ?? 520, n = p.n ?? 150, boom = p.boom ?? 144.54;
  const bloomAt = p.bloomAt ?? 1e9, bx = p.bloomX ?? cx + 220, by = p.bloomY ?? cy - 160;
  const kick = smooth(boom, boom + 1.4, t) * (1 - 0.7 * smooth(p.regather ?? 146.3, (p.regather ?? 146.3) + 1.2, t)); // the boom throws the filings outward; they drift back for the stroke
  const twos = Math.floor(t * 12) / 12;                   // drawn on twos
  g.save();
  g.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    // cluster placement: a ring field around her, avoiding her body
    const r0 = 260 + 720 * Math.sqrt(hash(i, 1));
    const a0 = hash(i, 2) * Math.PI * 2;
    const w = (0.035 + 0.05 * hash(i, 3)) * (hash(i, 4) < 0.5 ? 1 : -1) * 0.6;
    const ang = a0 + w * (twos - 141) + 0.0;
    const r = r0 * (1 + 0.55 * kick * (0.6 + 0.8 * hash(i, 5))) + 14 * Math.sin(twos * 0.9 + i);
    const x = cx + Math.cos(ang) * r * 1.35, y = cy + Math.sin(ang) * r * 0.82;
    if (x < -150 || x > 2070 || y < -150 || y > 1230) continue;
    // iron filings: strokes align to the tangent of the field, with a little disorder that settles over time
    const settle = smooth(141, 144.0, twos);
    const dir = ang + Math.PI / 2 + hsig(i, 6) * (1.2 - 0.9 * settle) + 0.25 * kick * hsig(i, 7);
    const len = 30 + 110 * hash(i, 8), k = 2 + Math.floor(hash(i, 9) * 5), gap = 7 + 4 * hash(i, 10);
    const ca = Math.cos(dir), sa = Math.sin(dir), nx = -sa, ny = ca;
    // colour bloom (G3): strokes near the pencil's stroke turn to coloured pencil, spreading outward
    const bd = Math.hypot(x - bx, y - by);
    const bloom = t > bloomAt ? clamp(((t - bloomAt) * 900 - bd) / 220) : 0;
    const c = bloom > 0 ? mix(INK, mix(ORANGE, SKY, clamp((x - bx) / 700 + 0.5)), bloom) : INK;
    g.strokeStyle = `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
    const alpha = (0.55 + 0.45 * hash(i, 11)) * (1 - 0.35 * kick);
    for (let j = 0; j < k; j++) {
      const off = (j - (k - 1) / 2) * gap;
      const lj = len * (0.75 + 0.5 * hash(i, j, 12)), sh = hsig(i, j, 13) * 10;
      const x0 = x + nx * off + ca * (sh - lj / 2), y0 = y + ny * off + sa * (sh - lj / 2);
      const x1 = x0 + ca * lj, y1 = y0 + sa * lj;
      // swelling engraved stroke: two passes, thick middle
      g.globalAlpha = alpha;
      g.lineWidth = 1.4 + 1.6 * hash(i, j, 14) + (bloom > 0 ? 1.2 * bloom : 0);
      g.beginPath(); g.moveTo(x0, y0);
      g.quadraticCurveTo((x0 + x1) / 2 + nx * 3 * hsig(i, j, 15), (y0 + y1) / 2 + ny * 3 * hsig(i, j, 15), x1, y1);
      g.stroke();
    }
  }
  g.restore();
}
const mix = (a, b, u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u];
