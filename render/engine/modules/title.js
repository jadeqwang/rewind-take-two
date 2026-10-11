// title.js: the REWIND title. Letters arrive in reverse order (D first) mirrored, as the word's mirror image, then each
// card-flips to right-reading and slides into place (D N I W E R → R E W I N D).
//   params: text 'REWIND', font 'fell', size 230, x 960, y 560 (baseline), color ink,
//     arrive: {at 0 (local s or absolute), every .1 (s between letters; 0 = the whole mirrored word ink-bleeds in at once)}
//     flip: {at (default: after the last arrival + .25), dur .45 (per letter), stagger .08}
//     mirrored: true (false = letters simply ink-bleed in right-reading, e.g. the smaller second REWIND)
//     subtitle: 'jade wang' (IM Fell italic, appears after the flip), subtitleSize 40
import { C, bleed, inkText, absT, fontName } from './lib/text.js';
import { clamp, EASE } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const text = p.text ?? 'REWIND', size = env.val(p.size, 230), color = env.val(p.color, C.ink);
  const x = env.val(p.x, 960), y = env.val(p.y, 560);
  g.font = `${size}px ${fontName(p.font || 'fell')}`; g.textBaseline = 'alphabetic'; g.textAlign = 'center';
  g.letterSpacing = `${env.val(p.tracking, size * 0.04)}px`;
  const ch = [...text], widths = ch.map(c => g.measureText(c).width), total = widths.reduce((a, b) => a + b, 0);
  let acc = -total / 2; const cxs = widths.map(w => { const c = acc + w / 2; acc += w; return c; });   // right-reading centres
  const n = ch.length, arr = p.arrive || {}, a0 = absT(env, arr.at, 0), every = arr.every ?? 0.1;
  const mirrored = p.mirrored !== false;
  const lastArrive = a0 + every * (n - 1);
  const fl = p.flip || {}, f0 = fl.at !== undefined ? absT(env, fl.at) : lastArrive + 0.25, fd = fl.dur ?? 0.45, fs = fl.stagger ?? 0.08;
  g.globalAlpha = env.val(p.opacity, 1);
  for (let k = n - 1; k >= 0; k--) {
    const order = n - 1 - k;                          // D (last letter) arrives first
    const tA = a0 + order * every, b = bleed(t, tA); if (!b) continue;
    let px = cxs[k], sx = 1;
    if (mirrored) {
      const u = EASE.inOutCubic(clamp((t - (f0 + order * fs)) / fd));
      px = -cxs[k] + (cxs[k] - -cxs[k]) * u;          // from its mirror position to its real one
      sx = -Math.cos(Math.PI * u);                     // -1 (mirrored) → 0 (edge-on) → 1
    }
    g.save(); g.translate(x + px, y); g.scale(Math.abs(sx) < 0.02 ? 0.02 * Math.sign(sx || 1) : sx, 1);
    inkText(g, ch[k], 0, 0, b, color, env.S, k * 31 + 7);
    g.restore();
  }
  if (p.subtitle) {
    const ts = mirrored ? f0 + (n - 1) * fs + fd : lastArrive + 0.2, b = bleed(t, ts);
    if (b) { g.font = `italic ${env.val(p.subtitleSize, 40)}px ${fontName('fell')}`; g.letterSpacing = '6px'; inkText(g, p.subtitle, x, y + size * 0.42, b, color, env.S, 99); }
  }
}
