// lowerthird.js: the default sung-lyric treatment. IM Fell English, lower third; each word appears exactly on its
// onset with a 2-frame ink-bleed reveal and stays until the line clears (4-frame fade after end + hold).
//   params: text?/sync/times (see lib/text.js; default = the line being sung), color ('#0b0b0c' ink; '#F08A24' when the
//   lyric is residue; '#ece7dc' over dark plates), size 62, x 960, y 960 (baseline), align 'center', maxWidth 1500,
//   halo (0..1 soft paper glow behind for legibility; colour haloColor), italic, uppercase/lowercase, tracking (px),
//   lead .3, hold .6, fadeFrames 4
import { F, C, wordsFor, bleed, inkText, layout, caseOf, fontName } from './lib/text.js';
import { clamp, hashStr } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const words = wordsFor(env, p); if (!words.length) return;
  const size = env.val(p.size, 62), color = env.val(p.color, C.ink);
  g.font = `${p.italic ? 'italic ' : ''}${size}px ${fontName(p.font || 'fell')}`;
  g.letterSpacing = `${env.val(p.tracking, 0)}px`; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  const ws = words.map(w => ({ ...w, display: caseOf(w.text, p) }));
  const lines = layout(g, ws, env.val(p.maxWidth, 1500), size * 0.27);
  const lineEnd = Math.max(...words.map(w => w.end)), hold = p.hold ?? 0.6;
  const fade = clamp(1 - (t - lineEnd - hold) * 24 / (p.fadeFrames ?? 4));
  if (fade <= 0) return;
  const x = env.val(p.x, 960), y = env.val(p.y, 960), lh = size * 1.18, align = p.align || 'center';
  g.globalAlpha = env.val(p.opacity, 1) * fade;
  lines.forEach((L, li) => {
    const y0 = y - (lines.length - 1 - li) * lh;
    const x0 = align === 'center' ? x - L.width / 2 : align === 'right' ? x - L.width : x;
    const halo = env.val(p.halo, 0);
    if (halo > 0) {
      const shown = L.items.filter(it => t >= it.w.start);
      if (shown.length) {
        g.save(); g.globalAlpha *= halo; g.filter = `blur(${(size * 0.35 * env.S).toFixed(1)}px)`; g.fillStyle = env.val(p.haloColor, C.paper);
        const last = shown[shown.length - 1];
        g.fillRect(x0 - size * 0.3, y0 - size * 0.85, last.x + last.width + size * 0.6, size * 1.15); g.restore();
      }
    }
    for (const it of L.items) inkText(g, it.w.display, x0 + it.x, y0, bleed(t, it.w.start), color, env.S, hashStr(it.w.text) + Math.round(it.w.start * 100));
  });
}
