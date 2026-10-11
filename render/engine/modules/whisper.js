// whisper.js: whispered words ("shot", "never stop"): IM Fell italic, lowercase, small, graphite, tracked out.
// Each word breathes in over ~6 frames on its onset (drifting up a few px) and out after the line ends.
//   params: text (default: the sung line), sync/times, size 34, color '#5e5b57', tracking (em, .38), x 960, y 900,
//   align 'center', hold .5, breath (s, .25)
import { C, wordsFor, caseOf, fontName } from './lib/text.js';
import { clamp } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const words = wordsFor(env, p); if (!words.length) return;
  const size = env.val(p.size, 34), br = p.breath ?? 0.25, end = Math.max(...words.map(w => w.end)) + (p.hold ?? 0.5);
  const out = clamp((end - t) / br); if (out <= 0) return;
  g.font = `italic ${size}px ${fontName(p.font || 'fell')}`; g.letterSpacing = `${env.val(p.tracking, 0.38) * size}px`; g.textBaseline = 'alphabetic';
  const txt = words.map(w => caseOf(w.text, { lowercase: p.lowercase !== false }));
  const sp = g.measureText(' ').width, widths = txt.map(s => g.measureText(s).width), total = widths.reduce((a, b) => a + b, 0) + sp * (txt.length - 1);
  const x = env.val(p.x, 960), y = env.val(p.y, 900), align = p.align || 'center';
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  g.fillStyle = env.val(p.color, C.graphite);
  txt.forEach((s, k) => {
    const a = clamp((t - words[k].start) / br);
    if (a > 0) { g.globalAlpha = env.val(p.opacity, 1) * a * out; g.fillText(s, cx, y + (1 - a) * 6); }
    cx += widths[k] + sp;
  });
}
