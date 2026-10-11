// Section E, M3 lyric (engine Canvas2D module): "a shadow chasing me — it couldn't trace"
// IM Fell, ink, lower third, each word inked on its sung onset (engine 2-frame bleed). The last word, "trace", is not
// printed: a dotted tracing line draws its letters (168.12 -> ~168.55), then loses the path: the dots drift apart and
// the line wanders off across the page and out of frame on the riser (168.6 -> 169.4).
//   params: size 62, y 960 (baseline), color ink, halo 0.6
import { wordsFor, bleed, inkText, fontName, C } from '../../engine/modules/lib/text.js';
import { clamp, hash, hsig } from '../../engine/src/core.js';

const smooth = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const words = wordsFor(env, { text: 'a shadow chasing me — it couldn\'t trace', sync: 'lyric' });
  if (!words.length) return;
  const size = p.size ?? 62, color = p.color ?? C.ink, y = p.y ?? 960;
  g.font = `${size}px ${fontName('fell')}`;
  g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  const space = size * 0.27;
  const ws = words.map((w) => ({ ...w, width: g.measureText(w.text).width }));
  const total = ws.reduce((a, w) => a + w.width + space, -space);
  let x = 960 - total / 2;
  const halo = p.halo ?? 0.85;
  // soft paper halo behind what is shown, for legibility over the diorama
  const shownW = ws.filter((w) => t >= w.start);
  if (halo > 0 && shownW.length) {
    g.save(); g.globalAlpha = halo; g.filter = `blur(${(size * 0.35 * env.S).toFixed(1)}px)`; g.fillStyle = C.paper;
    g.fillRect(x - size * 0.3, y - size * 0.85, total + size * 0.6, size * 1.15); g.restore();
  }
  for (const w of ws) {
    if (w.text === 'trace') drawTrace(g, w, x, y, size, t, env);
    else inkText(g, w.text, x, y, bleed(t, w.start), color, env.S, Math.round(w.start * 100));
    x += w.width + space;
  }
}

// the word drawn as a dotted trace, then the trace losing the path
function drawTrace(g, w, x, y, size, t, env) {
  const t0 = w.start, t1 = t0 + 0.45, tLose = 168.6, tEnd = 169.4;
  if (t < t0) return;
  const reveal = clamp((t - t0) / (t1 - t0));
  const lose = smooth(tLose, tEnd, t);
  g.save();
  g.strokeStyle = C.ink; g.fillStyle = C.ink;
  g.lineWidth = 2.2; g.lineCap = 'round';
  // letters: dotted outline, revealed left to right like a pen tracing them
  g.save();
  g.beginPath(); g.rect(x - 4, y - size * 1.2, (w.width + 8) * reveal, size * 1.6); g.clip();
  g.setLineDash([0.1, 6.5]);
  g.globalAlpha = 1 - 0.85 * lose;
  // the dots drift apart as the trace forgets the shape
  const jit = lose * size * 0.5;
  g.translate(hsig(1, Math.floor(t * 12)) * jit * 0.1, 0);
  g.strokeText(w.text, x, y);
  g.restore();
  // the wandering line: leaves the last letter and drifts off across the page and out of frame
  if (t > t0 + 0.3) {
    const len = smooth(t0 + 0.3, tEnd, t);
    const pts = [];
    let px = x + w.width + 4, py = y - size * 0.3, ang = -0.2;
    const N = 160;
    for (let i = 0; i < N * len; i++) {
      ang += hsig(7, i, Math.floor(i / 9)) * 0.22 + Math.sin(i * 0.07) * 0.05 - 0.004;
      px += Math.cos(ang) * 9; py += Math.sin(ang) * 9;
      pts.push([px, py]);
    }
    g.setLineDash([0.1, 7]);
    g.beginPath();
    pts.forEach(([a, b], i) => (i ? g.lineTo(a, b) : g.moveTo(a, b)));
    g.stroke();
    // the pen point
    if (pts.length) { const [a, b] = pts[pts.length - 1]; g.setLineDash([]); g.beginPath(); g.arc(a, b, 3.2, 0, 7); g.fill(); }
  }
  g.restore();
}
