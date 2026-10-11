// terminal.js: the agency terminal. IBM Plex Mono; every "█" run is a real solid redaction block (drawn, not a glyph),
// so "TIME VARIANCE █████████" always carries its black bar. Lines type out on a pace or on sung/spoken word timings.
//   params.lines: ['TIME VARIANCE █████████', {text: 'ANOMALY DETECTED', sync: 'lyric'}, {text: 'CASE 4,097', at: 1.2, cps: 30}]
//     strings type one after another at cps (default 28) from the layer start; objects may set at / cps / sync / times
//   params.mode 'full' (fills the frame) | 'panel' (rect [x, y, w, h] with a rule border)
//   params.alarm: 0/1 keyframes, inverted alarm (white ink on black); blink (Hz, 0 = steady) flips it while alarmed
//   size 54, x/y text origin (140, 220), lineHeight 1.5, cursor true, colors ink/paper
import { C, absT, wordsFor } from './lib/text.js';
import { clamp } from '../src/core.js';

function charTimes(env, ln, tStart, cps) {
  const n = ln.text.length;
  if (ln.sync || ln.times) {   // word-timed: each word's letters typed over its first .18 s
    const ws = wordsFor(env, { text: ln.text, sync: ln.sync, times: ln.times, at: ln.at });
    const out = new Array(n).fill(Infinity); let pos = 0;
    for (const w of ws) {
      const i0 = ln.text.indexOf(w.text, pos); if (i0 < 0) continue;
      for (let k = 0; k < w.text.length; k++) out[i0 + k] = w.start + 0.18 * k / w.text.length;
      for (let j = pos; j < i0; j++) out[j] = Math.min(out[j], w.start);   // spaces before it
      pos = i0 + w.text.length;
    }
    return out;
  }
  return Array.from({ length: n }, (_, i) => tStart + i / cps);
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const size = env.val(p.size, 54), lh = size * (p.lineHeight ?? 1.5);
  let alarm = env.val(p.alarm, 0) > 0.5;
  if (alarm && (p.blink ?? 0) > 0) alarm = Math.floor((t - env.origin) * p.blink * 2) % 2 === 0;
  const bg = alarm ? C.ink : env.val(p.paper, C.paper), fg = alarm ? env.val(p.paper, C.paper) : env.val(p.ink, C.ink);
  const mode = p.mode || 'full';
  g.globalAlpha = env.val(p.opacity, 1);
  let ox = env.val(p.x, 140), oy = env.val(p.y, 220);
  if (mode === 'full') { g.fillStyle = bg; g.fillRect(0, 0, 1920, 1080); }
  else {
    const [rx, ry, rw, rh] = env.val(p.rect, [120, 120, 1100, 420]);
    g.fillStyle = bg; g.fillRect(rx, ry, rw, rh); g.strokeStyle = fg; g.lineWidth = 3; g.strokeRect(rx + 10, ry + 10, rw - 20, rh - 20);
    if (p.x === undefined) ox = rx + 50; if (p.y === undefined) oy = ry + 50 + size;
  }
  g.font = `700 ${size}px "IBM Plex Mono"`; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  const cw = g.measureText('M').width;
  const lines = (p.lines || ['TIME VARIANCE █████████']).map(l => (typeof l === 'string' ? { text: l } : l));
  let cursor = absT(env, 0), last = null;
  lines.forEach((ln, li) => {
    const cps = ln.cps ?? p.cps ?? 28, tStart = ln.at !== undefined ? absT(env, ln.at) : cursor;
    const T = charTimes(env, ln, tStart, cps);
    cursor = (isFinite(T[T.length - 1]) ? T[T.length - 1] : tStart) + (p.gap ?? 0.15);
    const y = oy + li * lh;
    let shown = 0;
    for (let i = 0; i < ln.text.length; i++) {
      if (t < T[i]) break; shown = i + 1;
      const c = ln.text[i], x = ox + i * cw;
      if (c === '█') { g.fillStyle = fg; g.fillRect(x - 0.5, y - size * 0.8, cw + 1, size * 0.98); }
      else if (c !== ' ') { g.fillStyle = fg; g.fillText(c, x, y); }
    }
    if (shown > 0 || t >= tStart) last = { x: ox + shown * cw, y, typing: shown < ln.text.length };
  });
  if (p.cursor !== false && last && (last.typing || Math.floor(t * 2.5) % 2 === 0)) { g.fillStyle = fg; g.fillRect(last.x + 4, last.y - size * 0.78, cw * 0.62, size * 0.95); }
}
