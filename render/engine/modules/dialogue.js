// dialogue.js: RPG dialogue box with typewriter text (the cutscene's signature, shot list D7–D8).
//   Text: default = every sung word whose onset falls inside the layer's time range (so one layer spanning D7–D8
//   types "I reach for my ID to show them … and I do,"), each word's letters typed across its first 0.22 s; or
//   params.text + sync/times/cps (lib/text.js).
//   params: rect [x, y, w, h] ([150, 790, 1620, 230]), font 'fell' (or 'hud' for Press Start 2P), size 46, color ink,
//   fill paper, border ink, speaker (name tab, optional), typeTime .22 (s per word), open 4 (frames to open the box),
//   caret (▼ blinks when typing is done), close (frames to close at the layer end, 0 = cut)
import { C, wordsFor, layout, fontName, absT } from './lib/text.js';
import { clamp } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const words = wordsFor(env, p, { source: 'window' });
  const [bx, by, bw, bh] = env.val(p.rect, [150, 790, 1620, 230]);
  const fill = env.val(p.fill, C.paper), ink = env.val(p.border, C.ink), color = env.val(p.color, C.ink);
  const openF = p.open ?? 4, closeF = p.close ?? 3;
  const o = clamp((lt * 24) / Math.max(1, openF)), cl = closeF ? clamp(((env.layerEnd - t) * 24) / closeF) : 1;
  const sy = Math.min(o, cl); if (sy <= 0) return;
  g.save(); g.globalAlpha = env.val(p.opacity, 1);
  g.translate(bx + bw / 2, by + bh / 2); g.scale(1, sy); g.translate(-(bx + bw / 2), -(by + bh / 2));
  g.fillStyle = fill; g.fillRect(bx, by, bw, bh);
  g.strokeStyle = ink; g.lineWidth = 6; g.strokeRect(bx + 3, by + 3, bw - 6, bh - 6);
  g.lineWidth = 2; g.strokeRect(bx + 14, by + 14, bw - 28, bh - 28);
  g.fillStyle = ink; for (const [cx, cy] of [[bx, by], [bx + bw, by], [bx, by + bh], [bx + bw, by + bh]]) g.fillRect(cx - 9, cy - 9, 18, 18);   // corner rivets
  if (p.speaker) {
    g.font = `${p.font === 'hud' ? 22 : 30}px ${fontName(p.font === 'hud' ? 'hud' : 'fell')}`;
    const tw = g.measureText(p.speaker).width + 40;
    g.fillStyle = ink; g.fillRect(bx + 40, by - 44, tw, 50); g.fillStyle = fill; g.textBaseline = 'middle'; g.fillText(p.speaker, bx + 60, by - 19);
  }
  g.restore();
  if (sy < 1) return;
  // typed text
  const size = env.val(p.size, p.font === 'hud' ? 30 : 46), tt = p.typeTime ?? 0.22;
  g.font = `${size}px ${fontName(p.font || 'fell')}`; g.textBaseline = 'alphabetic'; g.textAlign = 'left'; g.fillStyle = color;
  const lines = layout(g, words, bw - 120, size * 0.3), lh = size * (p.font === 'hud' ? 1.7 : 1.32);
  let done = true;
  lines.forEach((L, li) => {
    const y0 = by + 40 + size + li * lh;
    for (const it of L.items) {
      const w = it.w, n = w.text.length, k = Math.floor(clamp((t - w.start) / tt) * n + 1e-6);
      if (k < n) done = false;
      if (k > 0) g.fillText(w.text.slice(0, k), bx + 60 + it.x, y0);
    }
  });
  if (done && p.caret !== false && words.length && Math.floor(t * 3) % 2 === 0) {
    g.beginPath(); const cx = bx + bw - 60, cy = by + bh - 46; g.moveTo(cx - 14, cy - 8); g.lineTo(cx + 14, cy - 8); g.lineTo(cx, cy + 10); g.closePath(); g.fill();
  }
}
