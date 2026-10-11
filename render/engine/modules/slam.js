// slam.js: kinetic lyric. Words slam in on their onsets (overshoot scale, ink smear, decaying shake).
//   params.mode: 'stack' (default: the line builds word by word in place, each word slamming) | 'word' (only the current
//   word, huge, centred). text/sync/times as lib/text.js (default: the sung line). font 'fell', size 150, x 960, y 600,
//   color ink, accent (colour of the word that just landed, default = color), impact 1 (shake/scale strength),
//   tilt (deg of seeded per-word rotation), uppercase, maxWidth 1700, hold .5
import { C, wordsFor, layout, caseOf, fontName } from './lib/text.js';
import { clamp, hsig, hashStr } from '../src/core.js';

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  let words = wordsFor(env, p); if (!words.length) return;
  const size = env.val(p.size, 150), color = env.val(p.color, C.ink), accent = env.val(p.accent, color), imp = env.val(p.impact, 1);
  const lineEnd = Math.max(...words.map(w => w.end));
  const fade = clamp(1 - (t - lineEnd - (p.hold ?? 0.5)) * 6);
  if (fade <= 0) return;
  g.font = `${p.italic ? 'italic ' : ''}${size}px ${fontName(p.font || 'fell')}`; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  const x = env.val(p.x, 960), y = env.val(p.y, 600);
  if (p.mode === 'word') {
    const cur = [...words].reverse().find(w => t >= w.start); if (!cur) return;
    words = [cur];
  }
  const ws = words.map(w => ({ ...w, display: caseOf(w.text, p) }));
  const lines = layout(g, ws, env.val(p.maxWidth, 1700), size * 0.26), lh = size * 1.05;
  // shake from the most recent landing
  const last = [...ws].reverse().find(w => t >= w.start);
  const since = last ? t - last.start : 9, k = Math.exp(-since / 0.09) * imp;
  const sx = hsig(Math.floor(t * 48), 1) * 14 * k, sy = hsig(Math.floor(t * 48), 2) * 10 * k;
  g.globalAlpha = env.val(p.opacity, 1) * fade;
  lines.forEach((L, li) => {
    const y0 = y + (li - (lines.length - 1) / 2) * lh;
    const x0 = x - L.width / 2;
    for (const it of L.items) {
      const w = it.w, ds = t - w.start; if (ds < 0) continue;
      const u = clamp(ds / 0.14), sc = 1 + (1.9 - 1) * Math.pow(1 - u, 3) * imp - 0.06 * Math.sin(u * Math.PI) * imp;
      const rot = (env.val(p.tilt, 3) * Math.PI / 180) * hsig(hashStr(w.text), w.start * 10);
      const cx = x0 + it.x + it.width / 2, cy = y0 - size * 0.35;
      const isLast = w === last;
      g.save(); g.translate(cx + sx, cy + sy); g.rotate(rot); g.scale(sc, sc); g.translate(-it.width / 2, size * 0.35);
      if (u < 1) {   // ink smear: two trailing ghosts from the direction it flew in
        for (let m = 2; m >= 1; m--) { g.globalAlpha = env.val(p.opacity, 1) * fade * 0.18 * (1 - u); g.fillStyle = color; g.fillText(w.display, 0, -m * 18 * (1 - u)); }
      }
      g.globalAlpha = env.val(p.opacity, 1) * fade * (0.55 + 0.45 * clamp(ds * 24));
      g.fillStyle = isLast && ds < 0.35 ? accent : color;
      g.fillText(w.display, 0, 0);
      g.restore();
    }
  });
}
