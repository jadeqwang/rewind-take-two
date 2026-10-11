// pencil.js: handwritten pencil text that writes itself (Reenie Beanie, a pencil hand): sticky notes, the anagram slip,
// "never stop" on walls. Each letter is swept in left→right behind a pencil point; graphite grain breaks the stroke.
//   params: text, at (local s or absolute), cps 9 (letters per second) or sync: 'lyric' / times (word-timed: each word
//   written across its duration), size 64, color graphite '#3c3a37' (or '#F08A24' for coloured pencil), x, y (start of
//   the baseline; align 'left'|'center'), rotate (deg), corners (8 numbers: pin onto a wall/note in perspective),
//   grain .45, wobble 1 (baseline jitter), point true (draw the pencil point while writing), lineHeight 1.05
import { C, wordsFor, absT, fontName, scratch, warpQuad, grainPattern } from './lib/text.js';
import { clamp, hsig } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const text = String(p.text ?? 'never stop'), size = env.val(p.size, 64), color = env.val(p.color, '#3c3a37'), res = p.res ?? 2;
  const font = `${Math.round(size * res)}px ${fontName(p.font || 'hand')}`;
  // per-letter timing
  const chars = [...text], T = new Array(chars.length).fill(Infinity), D = new Array(chars.length).fill(0.08);
  if (p.sync || p.times) {
    const ws = wordsFor(env, { text: text.replace(/\n/g, ' '), sync: p.sync, times: p.times, at: p.at }); let pos = 0;
    for (const w of ws) { const i0 = text.indexOf(w.text, pos); if (i0 < 0) continue; const d = Math.max(0.12, w.end - w.start); for (let k = 0; k < w.text.length; k++) { T[i0 + k] = w.start + d * k / w.text.length; D[i0 + k] = d / w.text.length; } pos = i0 + w.text.length; }
    for (let i = 0; i < chars.length; i++) if (!isFinite(T[i])) T[i] = i ? T[i - 1] + D[i - 1] : absT(env, p.at, 0);
  } else { const cps = p.cps ?? 9, t0 = absT(env, p.at, 0); chars.forEach((_, i) => { T[i] = t0 + i / cps; D[i] = 1 / cps; }); }
  if (t < T[0]) return;
  // render the block into a scratch canvas at res×
  const m = scratch('pencil_m', 4, 4).g; m.font = font;
  const lines = text.split('\n'), lh = size * res * (p.lineHeight ?? 1.05);
  const bw = Math.max(...lines.map(l => m.measureText(l).width)) + size * res, bh = lh * lines.length + size * res * 0.6;
  const blk = scratch('pencil_b', bw, bh), b = blk.g;
  b.font = font; b.textBaseline = 'alphabetic'; b.fillStyle = color; b.strokeStyle = color; b.lineWidth = 0.6 * res;
  let idx = 0, tip = null;
  lines.forEach((ln, li) => {
    let cx = size * res * 0.3; const by = size * res * 0.95 + li * lh;
    for (const ch of ln) {
      const cw = b.measureText(ch).width, u = clamp((t - T[idx]) / D[idx]);
      if (u > 0) {
        const jy = hsig(idx, 3) * 2.2 * res * (p.wobble ?? 1), jr = hsig(idx, 4) * 0.04 * (p.wobble ?? 1);
        b.save(); b.beginPath(); b.rect(cx - 2 * res, 0, (cw + 4 * res) * u, bh); b.clip();
        b.translate(cx, by + jy); b.rotate(jr);
        b.fillText(ch, 0, 0); b.globalAlpha = 0.5; b.strokeText(ch, 0.6 * res, 0.3 * res);   // a second, lighter pass
        b.restore();
        if (u < 1) tip = [cx + cw * u, by + jy - size * res * 0.25];
      }
      cx += cw; idx++;
    }
    idx++;   // the '\n'
  });
  b.save(); b.globalCompositeOperation = 'destination-out'; b.globalAlpha = env.val(p.grain, 0.45); b.fillStyle = grainPattern(b); b.fillRect(0, 0, bw, bh); b.restore();
  if (tip && p.point !== false) {   // the pencil point (graphite cone) riding the stroke
    b.save(); b.translate(tip[0], tip[1]); b.rotate(-0.9);
    b.fillStyle = '#d9b26a'; b.beginPath(); b.moveTo(0, 0); b.lineTo(16 * res, -6 * res); b.lineTo(16 * res, 6 * res); b.closePath(); b.fill();
    b.fillStyle = '#2a2826'; b.beginPath(); b.moveTo(0, 0); b.lineTo(5 * res, -2 * res); b.lineTo(5 * res, 2 * res); b.closePath(); b.fill();
    b.fillStyle = '#e8b730'; b.fillRect(16 * res, -6 * res, 60 * res, 12 * res); b.restore();
  }
  g.globalAlpha = env.val(p.opacity, 1);
  if (p.corners) warpQuad(g, blk, env.val(p.corners));
  else {
    const x = env.val(p.x, 760), y = env.val(p.y, 540), r = env.val(p.rotate, 0) * Math.PI / 180;
    g.save(); g.translate(x, y); g.rotate(r); g.drawImage(blk, (p.align === 'center' ? -bw / 2 : -size * res * 0.3) / res, -size * 0.95, bw / res, bh / res); g.restore();
  }
}
