// _arc_lyric.js (v3, singing shots S1 / S1b / V3S): in-world lyric lettering set on a circular arc, like the legend
// round a medal. It is cut into the Bean's mirror just inside its rim, so it follows the rim's curve, sits behind the
// singer (the timeline lays her matte over it) and moves with the plate's push.
//   params: text, times / sync / at (word sources of the typography kit; one word appears per onset),
//   cx, cy, r        the arc: centre and BASELINE radius in design px (letters stand outward, tops toward the rim)
//   mid | from | to  where the text sits, degrees clockwise from 12 o'clock: `mid` centres it there, `from` starts it
//                    there, `to` ends it there (rows of one block share a `from` or a `to`, like a ragged paragraph)
//   size (font px, default 94), font ('slab' = Anton, the wood-type capitals of the other in-world lyrics), tracking (px),
//   style 'woodcut'  white-line letters cut into the block: paper letters with an ink keyline, engraved hatching through
//                    the foot of every letter, nicks, and gouge flecks left standing round each word
//         'pencil'   coloured pencil laid over the print: grainy strokes in `color` (default residue orange), a soft
//                    paper ground under them so they hold on the dark hatching
//   color, edge (keyline colour), hatch (0..1 share of the cap height, default .4), flecks (per word, default 10),
//   grain (pencil tooth 0..1, default .5), ground (0..1 paper under pencil letters, default .55), opacity
// Reveal per word (as tools/sectionA/modules/woodcut.js 'carve'): frame 0 the outline, frame 1 78 %, then solid.
import { C, wordsFor, caseOf, fontName, grainPattern } from '../engine/modules/lib/text.js';
import { hash } from '../engine/src/core.js';

const RAD = Math.PI / 180;

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const words = wordsFor(env, p).map(w => ({ ...w, display: caseOf(w.text, { uppercase: p.uppercase ?? true }) }));
  if (!words.length) return;
  const size = env.val(p.size, 94), font = fontName(p.font || 'slab'), track = env.val(p.tracking, size * 0.03);
  const cx = env.val(p.cx, 960), cy = env.val(p.cy, 980), r = env.val(p.r, 1040), style = p.style || 'woodcut';
  const color = env.val(p.color, style === 'pencil' ? C.orange : C.paper), edge = env.val(p.edge, style === 'pencil' ? '#5a2a08' : C.ink);
  g.font = `400 ${size}px ${font}`; g.textBaseline = 'alphabetic'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineCap = 'round';
  const cap = g.measureText('H').actualBoundingBoxAscent || size * 0.73, space = size * 0.26;
  // lay the glyphs out along the baseline (arc length), then turn lengths into angles
  const glyphs = []; let x = 0;
  words.forEach((w, wi) => {
    if (wi) x += space;
    const x0 = x, f = (t - w.start) * 24;
    for (const ch of w.display) { const a = g.measureText(ch).width; glyphs.push({ ch, x: x + a / 2, wi, f }); x += a + track; }
    x -= track;
    w._x0 = x0; w._x1 = x; w._f = f; w._seed = hash(Math.round(w.start * 100), w.display.length, wi);
  });
  const total = x, span = total / r / RAD;
  const a0 = (p.from !== undefined ? env.val(p.from) : p.to !== undefined ? env.val(p.to) - span : env.val(p.mid, 0) - span / 2) * RAD;
  const ang = s => a0 + s / r, pt = (s, rr) => [cx + rr * Math.sin(ang(s)), cy - rr * Math.cos(ang(s))];
  const each = (fn) => { for (const q of glyphs) { if (q.f < 0) continue; const [px, py] = pt(q.x, r); g.save(); g.translate(px, py); g.rotate(ang(q.x)); fn(q); g.restore(); } };
  const shown = words.filter(w => w._f >= 0);
  if (!shown.length) return;
  g.globalAlpha = 1;

  // 1. the letters
  each(q => {
    if (q.f < 1) { g.strokeStyle = color; g.lineWidth = size * 0.035; g.strokeText(q.ch, 0, 0); return; }
    g.globalAlpha = q.f < 2 ? 0.78 : 1; g.fillStyle = color; g.fillText(q.ch, 0, 0);
  });

  if (style === 'woodcut') {
    // 2. the cutter's work inside the letters: hatching through the foot, a few nicks (ink, only where letters are)
    g.save(); g.globalCompositeOperation = 'source-atop'; g.strokeStyle = edge; g.fillStyle = edge;
    const hk = env.val(p.hatch, 0.4), pitch = Math.max(5, size * 0.06);
    for (const w of shown) {
      if (w._f < 1) continue;
      if (hk > 0) for (let s = w._x0 - cap; s < w._x1 + 4; s += pitch) {
        const [ax, ay] = pt(s, r - 3), [bx, by] = pt(s + cap * hk * 0.7, r + cap * hk), [mx, my] = pt(s + cap * hk * 0.32, r + cap * hk * 0.46);
        g.lineWidth = pitch * 0.2; g.beginPath(); g.moveTo(ax, ay); g.lineTo(bx, by); g.stroke();
        g.lineWidth = pitch * 0.42; g.beginPath(); g.moveTo(ax, ay); g.lineTo(mx, my); g.stroke();   // thicker toward the foot
      }
      for (let k = 0; k < 14; k++) {
        const [nx, ny] = pt(w._x0 + hash(w._seed, k, 1) * (w._x1 - w._x0), r + hash(w._seed, k, 2) * cap), s = size * (0.012 + 0.02 * hash(w._seed, k, 3));
        g.beginPath(); g.moveTo(nx, ny); g.lineTo(nx + s * 2.4, ny + s * 0.5); g.lineTo(nx + s * 0.6, ny + s * 1.4); g.closePath(); g.fill();
      }
    }
    g.restore();
    // 3. the ink left standing round every letter, so the white holds against light buildings as well as dark sky
    g.save(); g.globalCompositeOperation = 'destination-over'; g.strokeStyle = edge;
    each(q => { if (q.f < 1) return; g.lineWidth = size * 0.11; g.strokeText(q.ch, 0, 0); });
    g.restore();
    // 4. gouge flecks round each word (the uncleared wood of a real cut)
    const nf = env.val(p.flecks, 10);
    g.save(); g.strokeStyle = color;
    for (const w of shown) {
      if (w._f < 2) continue;
      for (let k = 0; k < nf; k++) {
        const out = hash(w._seed, k, 5) < 0.5, s = w._x0 + (hash(w._seed, k, 6) * 1.08 - 0.04) * (w._x1 - w._x0);
        const rr = out ? r + cap + size * (0.13 + 0.1 * hash(w._seed, k, 7)) : r - size * (0.13 + 0.1 * hash(w._seed, k, 7));
        const len = size * (0.05 + 0.11 * hash(w._seed, k, 8)), [fx, fy] = pt(s, rr), [ex, ey] = pt(s + len, rr + (hash(w._seed, k, 9) - 0.5) * len * 0.5);
        g.globalAlpha = 0.35 + 0.4 * hash(w._seed, k, 10); g.lineWidth = 1.6 + 2 * hash(w._seed, k, 11);
        g.beginPath(); g.moveTo(fx, fy); g.lineTo(ex, ey); g.stroke();
      }
    }
    g.restore();
  } else {
    // coloured pencil: the paper's tooth breaks the strokes up, a darker pencil line holds the edge, and a soft
    // rubbed-out paper ground keeps the colour bright where it crosses black hatching
    g.save(); g.globalCompositeOperation = 'destination-out'; g.globalAlpha = env.val(p.grain, 0.5); g.fillStyle = grainPattern(g);
    g.fillRect(0, 0, 1920, 1080); g.restore();
    g.save(); g.globalCompositeOperation = 'destination-over';
    each(q => { if (q.f < 1) return; g.globalAlpha = 0.85; g.strokeStyle = edge; g.lineWidth = size * 0.045; g.strokeText(q.ch, 0, 0); });
    const gr = env.val(p.ground, 0.55);
    if (gr > 0) each(q => { if (q.f < 1) return; g.globalAlpha = gr * (q.f < 2 ? 0.6 : 1); g.fillStyle = C.paper; g.strokeStyle = C.paper; g.lineWidth = size * 0.2; g.strokeText(q.ch, 0, 0); g.fillText(q.ch, 0, 0); });
    g.restore();
  }
  if (p.opacity !== undefined) {   // whole-layer strength (the engine's layer opacity also works; this one is keyframable per module)
    g.save(); g.globalCompositeOperation = 'destination-in'; g.globalAlpha = env.val(p.opacity, 1); g.fillStyle = '#000'; g.fillRect(0, 0, 1920, 1080); g.restore();
  }
}
