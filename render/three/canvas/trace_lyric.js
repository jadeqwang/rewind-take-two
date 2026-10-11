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
  const halo = p.halo ?? 0.9;
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

// "trace": a pencil point traces the word left to right in a crisp dotted line (~0.4 s, legible), the letters settle into
// solid ink behind the pen, then the tracing line loses the path: it leaves the last letter and wanders off-frame on
// the riser. The word itself stays put and readable to the cut.
function drawTrace(g, w, x, y, size, t, env) {
  const t0 = w.start, t1 = t0 + 0.42, tLose = 168.62, tEnd = 169.4;
  if (t < t0) return;
  const reveal = clamp((t - t0) / (t1 - t0));
  const settle = smooth(t1 - 0.05, t1 + 0.25, t);
  g.save();
  g.strokeStyle = C.ink; g.fillStyle = C.ink; g.lineCap = 'round'; g.lineJoin = 'round';
  // revealed region follows the pen
  g.save();
  g.beginPath(); g.rect(x - 6, y - size * 1.3, (w.width + 12) * reveal, size * 1.8); g.clip();
  // dotted tracing line round each letter: bold dots, legible at phone size
  g.lineWidth = Math.max(3, size * 0.06);
  g.setLineDash([0.1, size * 0.11]);
  g.globalAlpha = 1 - 0.55 * settle;
  g.strokeText(w.text, x, y);
  // the traced letters fill in with ink as the pen passes (crisp, no blur)
  g.setLineDash([]);
  g.globalAlpha = 0.35 + 0.65 * settle;
  g.fillText(w.text, x, y);
  g.restore();
  // pen point while tracing
  const penX = x + (w.width + 8) * reveal, penY = y - size * (0.32 + 0.18 * Math.sin(reveal * 19));
  // after the word: the line loses the path and wanders off
  const pts = [[penX, penY]];
  if (t > t1) {
    const len = smooth(t1, tEnd, t) * (0.3 + 0.7 * smooth(tLose - 0.2, tEnd, t));
    let px = penX, py = penY, ang = -0.35;
    const N = 190;
    for (let i = 0; i < N * len; i++) {
      ang += hsig(7, i, Math.floor(i / 9)) * 0.24 + Math.sin(i * 0.07) * 0.06 - 0.006;
      px += Math.cos(ang) * 9; py += Math.sin(ang) * 9;
      pts.push([px, py]);
    }
    g.lineWidth = Math.max(3, size * 0.05);
    g.setLineDash([0.1, size * 0.13]);
    g.beginPath();
    pts.forEach(([a, b], i) => (i ? g.lineTo(a, b) : g.moveTo(a, b)));
    g.stroke();
  }
  const [a, b] = pts[pts.length - 1];
  g.setLineDash([]); g.beginPath(); g.arc(a, b, Math.max(3.5, size * 0.065), 0, 7); g.fill();
  g.restore();
}
