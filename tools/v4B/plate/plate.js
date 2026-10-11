// plate.js (v4, B): a car licence plate drawn in the engraving's hand and corner-pinned onto a tracked plate.
// First use: D3, the agents' sedan in the wing mirror reads TVA 1729 (Jade's v3 note at 0:26). Reusable for any car:
// the text is a parameter. Right-reading always (the film's mirror lettering reads normally).
//
//   params.text      'TVA 1729' ('\n' stacks two lines; a space is a half-width gap between the groups)
//   params.corners   [TLx,TLy, TRx,TRy, BRx,BRy, BLx,BLy] design px, keyframable: the track of the plate the TAKE drew
//                    (tools/v4B/plate/track_plate.py). Without corners: a flat plate at x, y (centre), w, rotate.
//   params.grow      width of the drawn plate / width of the tracked quad (default 1; 1.5 = a plate half as wide again)
//   params.aspect    width / height of the drawn plate (default 2 = a US plate, 12 x 6 in); null keeps the quad's own
//   params.offset    [dx, dy] design px, moves the plate off the quad's centre (e.g. up, when a grown plate would hang
//                    below the bumper)
//   params.cam       {scale, x, y}, each keyframable: the SAME numbers as the layer transform of the plate under it
//                    (a push on the video layer). Applied to the corners here instead of to this layer, so the glyphs
//                    are rasterised at their final size and stay sharp at preview size. Leave the layer untransformed.
//   params.light     0..1, keyframable (default 1): how lit the plate is (passing streetlights). Unlit, the field is
//                    crossed by horizontal ink lines under the letters, the way the engraving darkens a surface: no
//                    grey. `dim` (default .4) is the share of the field the lines cover at light 0, `pitch` (default
//                    4.6 design px, the engrave pass's line pitch at 1080p) their spacing
//   params.paper / ink / shade   field, letters + border; shade: optional flat unlit field colour (default: none)
//   params.font ('slab' = Anton, the kit's condensed gothic), weight, cap (cap height / plate height, default .6),
//   squeeze (minimum horizontal squeeze of the glyphs, default .5), tracking (em), pad (side margin / plate width),
//   border (dark border / plate height, default .05), radius, hatch (0..1 line texture, default .5), nicks (count),
//   soft (blur in design px, default .5), wobble (0..1 hand-cut edge, default .5), opacity, seed
import { C, fontName, scratch, warpQuad, quadOf } from '../../../render/engine/modules/lib/text.js';
import { hash, clamp } from '../../../render/engine/src/core.js';

const NW = 600;   // nominal plate width the drawing is laid out in
const hex = c => { const m = /^#?([0-9a-f]{6})$/i.exec(c); const n = parseInt(m ? m[1] : 'ece7dc', 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; };
const mix = (a, b, k) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * k)).join(',')})`; };

// the quad to draw into: the tracked quad, resized about its centre to grow x its width and to the plate's aspect,
// moved by offset, then put through the camera (the layer transform of the plate underneath)
function plateQuad(env, p, aspect) {
  let q = quadOf(env, p, env.val(p.w, 120), env.val(p.w, 120) / (aspect || 2));
  const grow = env.val(p.grow, 1), off = env.val(p.offset, [0, 0]);
  const cx = (q[0] + q[2] + q[4] + q[6]) / 4, cy = (q[1] + q[3] + q[5] + q[7]) / 4;
  // the quad's own axes: u along the top/bottom edges, v down the sides (keeps the take's tilt and perspective)
  const ux = (q[2] - q[0] + q[4] - q[6]) / 2, uy = (q[3] - q[1] + q[5] - q[7]) / 2;
  const vx = (q[6] - q[0] + q[4] - q[2]) / 2, vy = (q[7] - q[1] + q[5] - q[3]) / 2;
  const wq = Math.hypot(ux, uy) || 1, hq = Math.hypot(vx, vy) || 1;
  const gx = grow, gy = aspect ? (wq * grow / aspect) / hq : grow;
  const out = [];
  for (let i = 0; i < 4; i++) {
    const dx = q[i * 2] - cx, dy = q[i * 2 + 1] - cy;
    // components of the corner along u and v (they are near-orthogonal for a plate seen nearly face-on)
    const a = (dx * ux + dy * uy) / (wq * wq), b = (dx * vx + dy * vy) / (hq * hq);
    out.push(cx + off[0] + a * gx * ux + b * gy * vx, cy + off[1] + a * gx * uy + b * gy * vy);
  }
  const cam = p.cam;
  if (cam) {
    const s = env.val(cam.scale, 1), x = env.val(cam.x, 0), y = env.val(cam.y, 0);
    for (let i = 0; i < 4; i++) { out[i * 2] = env.W / 2 + x + s * (out[i * 2] - env.W / 2); out[i * 2 + 1] = env.H / 2 + y + s * (out[i * 2 + 1] - env.H / 2); }
  }
  return out;
}

// the plate face in nominal units (NW x NH), into context b
export function drawPlate(b, NH, text, o = {}) {
  const { paper = C.paper, ink = C.ink, shade = null, light = 1, dim = 0.4, pitchN = 28, font = 'slab', weight = 400, cap = 0.6, squeeze = 0.5,
    tracking = 0.04, pad = 0.055, border = 0.05, radius = 0.1, hatch = 0.5, nicks = 10, wobble = 0.5, seed = 7 } = o;
  const L = clamp(light), field = shade ? mix(shade, paper, L) : paper, bw = border * NH, r = radius * NH;
  // hand-cut outline: the rounded rectangle walked as a polygon with a little wander
  const outline = (inset, jit) => {
    const x0 = inset, y0 = inset, x1 = NW - inset, y1 = NH - inset, rr = Math.max(2, r - inset), pts = [];
    const arc = (cx, cy, a0) => { for (let k = 0; k <= 4; k++) { const a = a0 + k / 4 * Math.PI / 2; pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); } };
    const edge = (ax, ay, bx, by, n) => { for (let k = 1; k < n; k++) pts.push([ax + (bx - ax) * k / n, ay + (by - ay) * k / n]); };
    arc(x0 + rr, y0 + rr, Math.PI); edge(x0 + rr, y0, x1 - rr, y0, 9);
    arc(x1 - rr, y0 + rr, -Math.PI / 2); edge(x1, y0 + rr, x1, y1 - rr, 5);
    arc(x1 - rr, y1 - rr, 0); edge(x1 - rr, y1, x0 + rr, y1, 9);
    arc(x0 + rr, y1 - rr, Math.PI / 2); edge(x0, y1 - rr, x0, y0 + rr, 5);
    b.beginPath();
    pts.forEach(([x, y], k) => {
      const jx = (hash(seed, k, inset, 1) - 0.5) * jit, jy = (hash(seed, k, inset, 2) - 0.5) * jit;
      if (k) b.lineTo(x + jx, y + jy); else b.moveTo(x + jx, y + jy);
    });
    b.closePath();
  };
  const jit = wobble * NH * 0.03;
  b.fillStyle = ink; outline(0, jit); b.fill();                 // the dark border is the plate's outer edge
  b.fillStyle = field; outline(bw, jit * 0.8); b.fill();         // pale field
  b.save(); outline(bw, 0); b.clip();
  // unlit: horizontal ink lines across the field at the engraving's pitch, each a little uneven, thicker the darker
  const dark = (1 - L) * dim;
  b.strokeStyle = ink; b.lineCap = 'butt';
  if (dark > 0.02) {
    for (let k = 0, y = pitchN * (0.3 + 0.4 * hash(seed, 31)); y < NH; k++, y += pitchN) {
      let x = bw;
      for (let sgm = 0; x < NW - bw && sgm < 12; sgm++) {
        const len = NW * (0.1 + 0.25 * hash(seed, k, sgm, 32));
        b.lineWidth = pitchN * dark * (0.8 + 0.4 * hash(seed, k, sgm, 33));
        b.beginPath(); b.moveTo(x, y); b.lineTo(Math.min(NW - bw, x + len), y + (hash(seed, k, sgm, 34) - 0.5) * pitchN * 0.12); b.stroke();
        x += len;
      }
    }
  }
  // lit: a few burin strokes along the foot and up the right side (the shadow side), so the field is not a blank slab
  if (hatch > 0) {
    b.lineCap = 'round';
    for (let k = 0; k < 4; k++) {
      const y = NH * (0.97 - border - 0.085 * k) , lw = hatch * NH * 0.022 * (1 - k / 5) * (0.5 + 0.5 * L);
      const xa = NW * (0.3 + 0.19 * k + 0.08 * hash(seed, k, 12));
      b.lineWidth = lw; let x = xa;
      for (let sgm = 0; x < NW - bw && sgm < 6; sgm++) {
        const len = NW * (0.1 + 0.22 * hash(seed, k, sgm, 13));
        b.beginPath(); b.moveTo(x, y); b.lineTo(Math.min(NW - bw, x + len), y + (hash(seed, k, sgm, 14) - 0.5) * NH * 0.012); b.stroke();
        x += len + NW * (0.012 + 0.03 * hash(seed, k, sgm, 15));
      }
    }
  }
  b.restore();
  // lettering: fitted into the field, squeezed like stamped plate characters; a space is a half-width gap
  const lines = String(text).toUpperCase().split('\n'), nl = lines.length;
  const fam = fontName(font), m = scratch('plate_measure', 4, 4).g; m.font = `${weight} 100px ${fam}`;
  const capK = (m.measureText('H').actualBoundingBoxAscent || 73) / 100;
  const innerW = NW - 2 * bw - 2 * pad * NW, innerH = NH - 2 * bw;
  const lineGap = 0.2, capH = nl === 1 ? cap * NH : Math.min(cap * NH, innerH * 0.86 / (nl + (nl - 1) * lineGap));
  const size = capH / capK, blockH = capH * (nl + (nl - 1) * lineGap);
  b.font = `${weight} ${size.toFixed(2)}px ${fam}`; b.textBaseline = 'alphabetic'; b.textAlign = 'left'; b.fillStyle = ink;
  const boxes = [];
  lines.forEach((ln, li) => {
    const chars = [...ln], gap = size * 0.3, tr = tracking * size;
    const ws = chars.map(ch => ch === ' ' ? gap : b.measureText(ch).width);
    const nat = ws.reduce((a, w) => a + w, 0) + tr * (chars.length - 1);
    const sx = clamp(innerW / nat, squeeze, 1);
    const sxy = nat * sx > innerW ? innerW / (nat * sx) : 1;     // still too wide at the minimum squeeze: shrink uniformly
    const base = (NH - blockH) / 2 + capH + li * capH * (1 + lineGap) + NH * 0.01;
    let x = (NW - nat * sx * sxy) / 2;
    chars.forEach((ch, k) => {
      const w = ws[k] * sx * sxy;
      if (ch !== ' ') {
        b.save(); b.translate(x, base - (1 - sxy) * capH / 2); b.scale(sx * sxy, sxy); b.fillText(ch, 0, 0); b.restore();
        boxes.push({ x, y: base - capH, w, h: capH, k: li * 20 + k });
      }
      x += w + tr * sx * sxy;
    });
  });
  // nicks where the wood chipped out of the letters (kept few and small: the plate has to read)
  if (nicks > 0) {
    b.save(); b.fillStyle = field;
    for (const bx of boxes) for (let k = 0; k < nicks / 4; k++) {
      const nx = bx.x + hash(seed, bx.k, k, 21) * bx.w, ny = bx.y + hash(seed, bx.k, k, 22) * bx.h, s = NH * (0.008 + 0.012 * hash(seed, bx.k, k, 23));
      b.beginPath(); b.moveTo(nx, ny); b.lineTo(nx + s * 2.2, ny + s * 0.5); b.lineTo(nx + s * 0.5, ny + s * 1.3); b.closePath(); b.fill();
    }
    b.restore();
  }
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params;
  if (!p.text) return;
  const aspect = p.aspect === null ? null : env.val(p.aspect, 2);
  const q = plateQuad(env, p, aspect);
  const wq = (Math.hypot(q[2] - q[0], q[3] - q[1]) + Math.hypot(q[4] - q[6], q[5] - q[7])) / 2;
  const hq = (Math.hypot(q[6] - q[0], q[7] - q[1]) + Math.hypot(q[4] - q[2], q[5] - q[3])) / 2;
  const NH = NW * hq / wq;
  // block resolution: about 2 block px per output px (downscaling more than that through the triangle warp aliases)
  const k = clamp((p.res ?? 2) * env.S * wq / NW, 0.05, 4);
  const face = scratch('plate_face', NW * k, NH * k), b = face.g;
  b.scale(k, k);
  drawPlate(b, NH, p.text, { paper: env.val(p.paper, C.paper), ink: env.val(p.ink, C.ink), shade: p.shade ? env.val(p.shade) : null,
    dim: env.val(p.dim, 0.4), pitchN: env.val(p.pitch, 4.6) * (p.cam ? env.val(p.cam.scale, 1) : 1) * NW / wq,
    light: env.val(p.light, 1), font: p.font, weight: p.weight, cap: p.cap, squeeze: p.squeeze, tracking: p.tracking, pad: p.pad,
    border: p.border, radius: p.radius, hatch: env.val(p.hatch, 0.5), nicks: p.nicks, wobble: p.wobble, seed: p.seed });
  // soften into a block with a clear margin (so the plate's own edge softens too), then pin the block: the quad
  // grows by the same margin along its own axes
  const M = 0.05, soft = env.val(p.soft, 0.5), bpd = k * NW / wq;   // bpd: block px per design px
  const blk = scratch('plate_block', NW * k * (1 + 2 * M), NH * k + NW * k * 2 * M), c = blk.g;
  if (soft > 0) c.filter = `blur(${(soft * bpd).toFixed(2)}px)`;
  c.drawImage(face, NW * k * M, NW * k * M);
  const ux = (q[2] - q[0] + q[4] - q[6]) / 2 / wq, uy = (q[3] - q[1] + q[5] - q[7]) / 2 / wq;
  const vx = (q[6] - q[0] + q[4] - q[2]) / 2 / hq, vy = (q[7] - q[1] + q[5] - q[3]) / 2 / hq;
  const m = M * wq, sg = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
  const Q = sg.flatMap(([su, sv], i) => [q[i * 2] + m * (su * ux + sv * vx), q[i * 2 + 1] + m * (su * uy + sv * vy)]);
  g.save();
  g.globalAlpha = env.val(p.opacity, 1); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
  if (Math.hypot(Q[0] - Q[2] + Q[4] - Q[6], Q[1] - Q[3] + Q[5] - Q[7]) < 0.5) {
    // a parallelogram (a plate seen nearly face-on): one affine draw, no mesh seams
    g.transform((Q[2] - Q[0]) / blk.width, (Q[3] - Q[1]) / blk.width, (Q[6] - Q[0]) / blk.height, (Q[7] - Q[1]) / blk.height, Q[0], Q[1]);
    g.drawImage(blk, 0, 0);
  } else warpQuad(g, blk, Q, { nx: 4, ny: 2 });
  g.restore();
}
