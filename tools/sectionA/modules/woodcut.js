// woodcut.js (section A, v3): in-world lyric lettering that looks cut into the woodblock, corner-pinned into the plate.
// Used for the lyric in the agent's sunglasses (D5: white-line letters on the black lenses) and on the rooftop bulb
// sign (D2: ink letters on the lit panels). Anton capitals (wood-type gothic), with engraved hatching through the
// lower part of every letter, wood-grain nicks, and gouge flecks around each word.
//   params: text ('\n' = new line), sync / times / at (word sources of the typography kit), corners (8 numbers,
//   keyframable) or x, y, rotate, box [w, h] (design px of the block before pinning; the text is fitted into it),
//   color, hatch (0..1 share of the cap height that is hatched, default .42), flecks (per word, default 14),
//   reveal 'carve' (outline first, then cut solid) | 'bulb' (flickers on like a lamp), pad, res, opacity,
//   unlit (0..1: the whole block is washed dark until the first word arrives, then flickers on), unlitColor
import { C, wordsFor, caseOf, fontName, scratch, warpQuad, quadOf } from '../../../render/engine/modules/lib/text.js';
import { hash } from '../../../render/engine/src/core.js';

const BULB = [1, 0.12, 0.85, 0.25, 1];

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t, res = p.res ?? 2;
  const [bw, bh] = p.box || [800, 400], W = bw * res, H = bh * res;
  const words = wordsFor(env, p).map(w => ({ ...w, display: caseOf(w.text, { uppercase: p.uppercase ?? true }) }));
  if (!words.length) return;
  const lines = []; for (const w of words) { if (!lines.length || w.br) lines.push([]); lines[lines.length - 1].push(w); }
  const font = fontName(p.font || 'slab'), pad = (p.pad ?? 26) * res, color = env.val(p.color, C.paper);
  const m = scratch('wc_measure', 4, 4).g; m.font = `400 100px ${font}`;
  const sp = 100 * (p.space ?? 0.24), capK = (m.measureText('H').actualBoundingBoxAscent || 73) / 100, step = 1.24;
  const widths = lines.map(ws => ws.reduce((a, w, i) => a + m.measureText(w.display).width + (i ? sp : 0), 0));
  const n = lines.length;
  const size = Math.min((W - 2 * pad) / Math.max(...widths) * 100, (H - 2 * pad) / (capK * (n * step - (step - 1))));
  const cap = capK * size, blockH = cap * (n * step - (step - 1));
  const blk = scratch('wc_block', W, H), b = blk.g;
  b.font = `400 ${size.toFixed(1)}px ${font}`; b.textBaseline = 'alphabetic'; b.textAlign = 'left'; b.lineJoin = 'round';
  const boxes = [];
  lines.forEach((ws, li) => {
    const lw = widths[li] * size / 100, base = (H - blockH) / 2 + cap + li * cap * step;
    let x = (W - lw) / 2;
    for (const w of ws) {
      const ww = b.measureText(w.display).width, f = (t - w.start) * 24;
      if (f >= 0) {
        b.save(); b.fillStyle = color; b.strokeStyle = color;
        if (p.reveal === 'bulb') { b.globalAlpha = BULB[Math.min(BULB.length - 1, Math.floor(f))]; b.fillText(w.display, x, base); }
        else if (f < 1) { b.lineWidth = size * 0.03; b.strokeText(w.display, x, base); }
        else if (f < 2) { b.globalAlpha = 0.78; b.fillText(w.display, x, base); }
        else b.fillText(w.display, x, base);
        b.restore();
        boxes.push({ x, y: base - cap, w: ww, h: cap, seed: hash(w.start, w.display.length), f });
      }
      x += ww + sp * size / 100;
    }
  });
  // a sign panel that is switched off until its first word arrives (bulb signs): a dark wash over the whole block
  const off = env.val(p.unlit, 0), f0 = (t - Math.min(...words.map(w => w.start))) * 24;
  const dark = off > 0 ? off * (f0 < 0 ? 1 : 1 - BULB[Math.min(BULB.length - 1, Math.floor(f0))]) : 0;
  if (!boxes.length && dark <= 0) return;
  // the cutter's work on the letters: hatching through the lower part, a few grain lines, small nicks
  b.save(); b.globalCompositeOperation = 'destination-out';
  const hk = env.val(p.hatch, 0.42), pitch = Math.max(3 * res, size * 0.055);
  for (const bx of boxes) {
    if (hk > 0) {
      b.save(); b.beginPath(); b.rect(bx.x - size * 0.1, bx.y + bx.h * (1 - hk), bx.w + size * 0.2, bx.h * hk + size * 0.1); b.clip();
      b.strokeStyle = '#000';
      for (let k = -4, i = 0; bx.x + k * pitch < bx.x + bx.w + bx.h; k++, i++) {
        // lines thicken toward the foot of the letter: drawn as two passes over the lower band
        const x0 = bx.x + k * pitch;
        b.lineWidth = pitch * 0.2; b.beginPath(); b.moveTo(x0, bx.y + bx.h + 4); b.lineTo(x0 + bx.h * hk * 0.7, bx.y + bx.h * (1 - hk)); b.stroke();
        b.lineWidth = pitch * 0.42; b.beginPath(); b.moveTo(x0, bx.y + bx.h + 4); b.lineTo(x0 + bx.h * hk * 0.35, bx.y + bx.h * (1 - hk * 0.5)); b.stroke();
      }
      b.restore();
    }
    b.fillStyle = '#000';
    for (let k = 0; k < 26; k++) {   // nicks where the wood chipped
      const nx = bx.x + hash(bx.seed, k, 1) * bx.w, ny = bx.y + hash(bx.seed, k, 2) * bx.h, s = size * (0.012 + 0.022 * hash(bx.seed, k, 3));
      b.beginPath(); b.moveTo(nx, ny); b.lineTo(nx + s * 2.4, ny + s * 0.5); b.lineTo(nx + s * 0.6, ny + s * 1.4); b.closePath(); b.fill();
    }
  }
  b.restore();
  // gouge flecks left standing around each word (the uncleared wood of a real cut)
  const nf = env.val(p.flecks, 14);
  b.save(); b.strokeStyle = color; b.lineCap = 'round';
  for (const bx of boxes) {
    if (bx.f < 2) continue;
    for (let k = 0; k < nf; k++) {
      const side = hash(bx.seed, k, 5) < 0.5 ? -1 : 1, fx = bx.x + (hash(bx.seed, k, 6) * 1.1 - 0.05) * bx.w;
      const fy = side < 0 ? bx.y - size * (0.07 + 0.1 * hash(bx.seed, k, 7)) : bx.y + bx.h + size * (0.07 + 0.1 * hash(bx.seed, k, 7));
      const len = size * (0.05 + 0.12 * hash(bx.seed, k, 8)), a = (hash(bx.seed, k, 9) - 0.5) * 0.5;
      b.globalAlpha = 0.35 + 0.4 * hash(bx.seed, k, 10); b.lineWidth = res * (1 + 1.6 * hash(bx.seed, k, 11));
      b.beginPath(); b.moveTo(fx, fy); b.lineTo(fx + Math.cos(a) * len, fy + Math.sin(a) * len); b.stroke();
    }
  }
  b.restore();
  if (dark > 0) { b.save(); b.globalCompositeOperation = 'destination-over'; b.globalAlpha = dark; b.fillStyle = p.unlitColor || C.ink; b.fillRect(0, 0, W, H); b.restore(); }
  g.globalAlpha = env.val(p.opacity, 1);
  warpQuad(g, blk, quadOf(env, p, bw, bh), { nx: p.mesh?.[0] ?? 16, ny: p.mesh?.[1] ?? 8 });
}
