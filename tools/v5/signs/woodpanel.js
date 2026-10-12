// woodpanel.js (v5 signs): the face of a road sign as cut in the woodblock, corner-pinned into the plate. An ink face
// cleared by evenly spaced vertical gouge lines (each a little uneven, as cut by hand), with a paper rule standing
// just inside the edge: the SIRENS gantry panel of the car shot (V2f), which Jade signed off. Lettering goes on top
// with tools/sectionA/modules/woodcut.js in paper.
//   params: corners (8 numbers, keyframable), box [w, h] (the face's proportions), lines (count across, default 34),
//   cut (0..1 share of each pitch cleared to paper, default .26), rule (inset of the paper rule as a share of the
//   height, default .07; 0 = none), plain ([[v0, v1], ...] bands of the height left solid ink), ink, paper, opacity, seed
import { C, scratch, warpQuad, quadOf } from '../../../render/engine/modules/lib/text.js';
import { hash } from '../../../render/engine/src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, q = quadOf(env, p, 400, 200);
  const [bw, bh] = p.box || [400, 200];
  // block resolution follows the face's size on screen (about 1.3 canvas px per output px), so the cut lines are
  // neither minified into moire nor blown up into blur as the gantry rushes in
  const span = Math.max(Math.hypot(q[2] - q[0], q[3] - q[1]), Math.hypot(q[4] - q[6], q[5] - q[7]));
  const k = Math.min(3, Math.max(0.15, span * (env.S || 1) * 1.3 / bw));
  const W = Math.round(bw * k), H = Math.round(bh * k);
  if (W < 4 || H < 4) return;
  const blk = scratch('wp_block', W, H), b = blk.g, seed = p.seed ?? 1;
  const ink = env.val(p.ink, C.ink), paper = env.val(p.paper, C.paper);
  b.fillStyle = ink; b.fillRect(0, 0, W, H);
  // vertical gouges: the pitch is fixed to the face, so lines grow with the sign
  const n = p.lines ?? 34, pitch = W / n, cut = env.val(p.cut, 0.26);
  b.strokeStyle = paper; b.lineCap = 'butt';
  for (let i = 0; i < n; i++) {
    const x = (i + 0.5) * pitch, segs = 6;
    b.lineWidth = Math.max(0.6, pitch * cut * (0.8 + 0.4 * hash(seed, i, 1)));
    b.globalAlpha = 0.75 + 0.25 * hash(seed, i, 2);
    b.beginPath();
    for (let s = 0; s <= segs; s++) {
      const y = H * s / segs, dx = (hash(seed, i, s, 3) - 0.5) * pitch * 0.12;
      if (s === 0) b.moveTo(x + dx, y); else b.lineTo(x + dx, y);
    }
    b.stroke();
  }
  b.globalAlpha = 1;
  // bands left solid ink (v0..v1 of the height) behind small lettering, so the gouges never cross thin strokes
  b.fillStyle = ink;
  for (const [v0, v1] of p.plain || []) b.fillRect(0, H * v0, W, H * (v1 - v0));
  // a paper rule left standing just inside the edge, over an ink margin
  const rk = env.val(p.rule, 0.07);
  if (rk > 0) {
    const m = H * rk, lw = Math.max(1, H * 0.022);
    b.fillStyle = ink;
    b.fillRect(0, 0, W, m + lw); b.fillRect(0, H - m - lw, W, m + lw); b.fillRect(0, 0, m + lw, H); b.fillRect(W - m - lw, 0, m + lw, H);
    b.strokeStyle = paper; b.lineWidth = lw; b.strokeRect(m, m, W - 2 * m, H - 2 * m);
  }
  g.globalAlpha = env.val(p.opacity, 1);
  g.imageSmoothingQuality = 'high';
  warpQuad(g, blk, q, { nx: 8, ny: 4 });
}
