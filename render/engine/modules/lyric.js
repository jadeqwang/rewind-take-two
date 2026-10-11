// lyric.js: word-synced kinetic typography (Canvas2D module). Reads the sung line/word from the timing map
// through env.lyric(opts) = TimeMap.lyric(t): {line, words:[{text,start,end,state,progress}], word, lineProgress, appear, vanish}.
//   params.style: 'line'  the whole line stays; each word lights (accent colour + pop + underline) as it is sung
//                 'slam'  only the current word, big, punched in on its onset
//   params: x, y (design px, line centre), size (px), font ('Anton' | '"CMU Serif"' | ...), italic, color, accent, dim (future-word alpha),
//           maxWidth (auto-fit), clearing (0..1 soft dark field behind the text), lead/hold (s), uppercase, tracking (px)
import { clamp } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params;
  const L = env.lyric({ lead: p.lead ?? 0.3, hold: p.hold ?? 0.5 });
  if (p.style === 'slam') return slam(g, env, p, L);
  if (!L.line) return;
  const size = env.val(p.size, 64), x = env.val(p.x, 960), y = env.val(p.y, 930);
  const font = p.font || 'Anton', it = p.italic ? 'italic ' : '';
  const col = env.val(p.color, '#ece7dc'), acc = env.val(p.accent, '#ff7a1a'), dim = env.val(p.dim, 0.32);
  const words = L.words.map(w => (p.uppercase ? { ...w, text: w.text.toUpperCase() } : w));
  g.font = `${it}${size}px ${font}`; g.textBaseline = 'alphabetic';
  const sp = size * 0.28, widths = words.map(w => g.measureText(w.text).width);
  let total = widths.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
  const maxW = env.val(p.maxWidth, 1600), fit = Math.min(1, maxW / total);
  const appear = env.core.EASE.outCubic(L.appear), vanish = L.vanish;
  const alpha = appear * (1 - vanish);
  if (alpha <= 0.001) return;
  g.save(); g.translate(x, y); g.scale(fit, fit); g.translate(-total / 2, 0);
  if (p.clearing) {
    g.save(); g.globalAlpha = alpha * env.val(p.clearing, 0.5);
    const gr = g.createRadialGradient(total / 2, -size * 0.35, 0, total / 2, -size * 0.35, total * 0.62);
    gr.addColorStop(0, 'rgba(0,0,0,0.85)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(-size, -size * 2, total + size * 2, size * 3.4); g.restore();
  }
  let cx = 0;
  words.forEach((w, k) => {
    const on = w.state === 'current', past = w.state === 'past';
    const since = env.t - w.start;
    const pop = since >= 0 && since < 0.3 ? Math.exp(-since / 0.08) : 0;
    const rise = (1 - appear) * 30;
    g.save(); g.translate(cx + widths[k] / 2, -size * 0.35 + rise); g.scale(1 + 0.12 * pop, 1 + 0.12 * pop); g.translate(-widths[k] / 2, size * 0.35);
    g.globalAlpha = alpha * (past || on ? 1 : dim);
    g.fillStyle = on ? acc : col;
    if (on) { g.shadowColor = acc; g.shadowBlur = 18 * (0.4 + pop); }
    g.fillText(w.text, 0, 0);
    g.shadowBlur = 0;
    if (on) { g.fillStyle = acc; g.fillRect(0, size * 0.14, widths[k] * clamp(w.progress), Math.max(3, size * 0.06)); }
    g.restore();
    cx += widths[k] + sp;
  });
  g.restore();
}

function slam(g, env, p, L) {
  const w = L.word; if (!w) return;
  const since = env.t - w.start, size = env.val(p.size, 220), x = env.val(p.x, 960), y = env.val(p.y, 600);
  const txt = p.uppercase === false ? w.text : w.text.toUpperCase().replace(/[.,!?;]+$/, '');
  const s = 1 + 0.35 * Math.exp(-since / 0.06);
  const a = clamp(1 - Math.max(0, env.t - w.end) / 0.15);
  g.save(); g.translate(x, y); g.scale(s, s);
  g.font = `${size}px ${p.font || 'Anton'}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  const tw = g.measureText(txt).width, fit = Math.min(1, env.val(p.maxWidth, 1700) / tw); g.scale(fit, fit);
  g.globalAlpha = a; g.fillStyle = env.val(p.color, '#ece7dc'); g.fillText(txt, 0, 0);
  g.restore();
}
