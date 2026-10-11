// end_credit.js (section F, outro overlay): the song credit set like a game's end credit. Press Start 2P, small, in a
// bottom corner; each line types on from its own time (a block caret while it types) and then holds.
//   params: lines [{text, at (absolute song time or local s), size?, color?}], side 'left' | 'right', margin 64,
//     y 1016 (baseline of the LAST line), size 22, leading 1.9 (× size), cps 40, color paper, dim (colour of lines
//     after the first)
import { absT } from '../../../render/engine/modules/lib/text.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const size0 = p.size ?? 22, lead = p.leading ?? 1.9, cps = p.cps ?? 40, m = p.margin ?? 64, right = p.side === 'right';
  const lines = p.lines || [];
  g.textBaseline = 'alphabetic'; g.textAlign = right ? 'right' : 'left';
  let y = p.y ?? 1016;
  for (let i = lines.length - 1; i >= 0; i--) {
    const L = lines[i], size = L.size ?? size0, since = t - absT(env, L.at ?? 0);
    const n = Math.floor(Math.min(L.text.length, Math.max(0, since * cps)));
    if (n > 0) {
      g.font = `${size}px "Press Start 2P"`;
      g.fillStyle = L.color || (i === 0 ? p.color || '#ece7dc' : p.dim || p.color || '#ece7dc');
      const s = L.text.slice(0, n), x = right ? 1920 - m : m;
      g.fillText(s, x, y);
      if (n < L.text.length && !right) g.fillRect(x + g.measureText(s).width + size * 0.15, y - size, size * 0.7, size);
    }
    y -= size * lead;
  }
}
