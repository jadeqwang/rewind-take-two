// pin.js: in-world text, corner-pinned into the plate (highway signs, mirror etching, ID cards, text on the ground).
//   params.corners  [x0,y0, x1,y1, x2,y2, x3,y3] TL, TR, BR, BL in design px, keyframable (track the plate by keying
//                   the corners); without corners: a flat block at x, y (centre), rotate (deg)
//   params.style    'sign'   highway sign: Overpass 700 on a panel with a rounded border (panel ink, text paper by default;
//                            panel '#1f5a3a' for a real green sign); first line is the big legend, later lines smaller
//                   'etch'   mirror etching: IM Fell, frosted pale glyphs with a groove shadow and highlight
//                   'ground' ink laid into a surface (use layer blend: 'multiply'); pencil grain
//                   'plain'  just text
//   text ('\n' = new line), sync / times / cps (word-timed reveal with ink bleed), size (px of the block's base text,
//   before pinning), font, color, panel, border, padding, align, uppercase, res (block render scale, default 2)
import { C, wordsFor, bleed, inkText, layout, caseOf, fontName, scratch, warpQuad, quadOf, grainPattern } from './lib/text.js';
import { clamp, hash } from '../src/core.js';

const STYLE = {
  sign: { font: 'sign', weight: 700, size: 90, color: C.paper, panel: C.ink, border: C.paper, padding: 46, align: 'left', second: 0.62 },
  etch: { font: 'fell', weight: 400, size: 64, color: 'rgba(236,231,220,0.62)', panel: null, padding: 14, align: 'left', second: 1 },
  ground: { font: 'fell', weight: 400, size: 96, color: C.ink, panel: null, padding: 10, align: 'center', second: 1 },
  plain: { font: 'fell', weight: 400, size: 72, color: C.ink, panel: null, padding: 10, align: 'center', second: 1 },
};

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t, st = { ...STYLE[p.style || 'plain'] };
  const res = p.res ?? 2, size = env.val(p.size, st.size), pad = env.val(p.padding, st.padding), color = env.val(p.color, st.color);
  const words = wordsFor(env, p).map(w => ({ ...w, display: caseOf(w.text, { uppercase: p.uppercase ?? p.style === 'sign', lowercase: p.lowercase }) }));
  if (!words.length) return;
  // measure lines (first line big, later lines `second` × size for signs)
  const fontAt = (li) => `${st.weight} ${Math.round((li === 0 ? size : size * st.second) * res)}px ${fontName(p.font || st.font)}`;
  const m = scratch('pin_measure', 4, 4).g;
  const lineWords = []; for (const w of words) { if (!lineWords.length || w.br) lineWords.push([]); lineWords[lineWords.length - 1].push(w); }
  const L = lineWords.map((ws, li) => { m.font = fontAt(li); return { li, line: layout(m, ws, 1e9, (li === 0 ? size : size * st.second) * res * 0.28)[0], h: (li === 0 ? size : size * st.second) * res * 1.22 }; });
  const bwid = Math.max(...L.map(l => l.line.width)) + pad * 2 * res, bhei = L.reduce((a, l) => a + l.h, 0) + pad * 2 * res;
  const blk = scratch('pin_block', bwid, bhei), b = blk.g;
  // panel
  const panel = p.panel !== undefined ? p.panel : st.panel;
  if (panel) {
    const r = 22 * res; b.fillStyle = panel; b.beginPath(); b.roundRect(0, 0, bwid, bhei, r); b.fill();
    b.strokeStyle = env.val(p.border, st.border); b.lineWidth = 6 * res; b.beginPath(); b.roundRect(9 * res, 9 * res, bwid - 18 * res, bhei - 18 * res, r * 0.7); b.stroke();
  }
  let y = pad * res;
  for (const l of L) {
    y += l.h * 0.82; b.font = fontAt(l.li); b.textBaseline = 'alphabetic'; b.textAlign = 'left';
    const align = p.align || st.align, x0 = align === 'center' ? (bwid - l.line.width) / 2 : align === 'right' ? bwid - pad * res - l.line.width : pad * res;
    for (const it of l.line.items) {
      const bl = bleed(t, it.w.start); if (!bl) continue;
      if (p.style === 'etch') {   // groove: dark edge below-right, light edge above-left, frosted fill
        b.save(); b.globalAlpha = bl.alpha;
        b.fillStyle = 'rgba(0,0,0,0.55)'; b.fillText(it.w.display, x0 + it.x + 1.5 * res, y + 1.5 * res);
        b.fillStyle = 'rgba(255,255,255,0.75)'; b.fillText(it.w.display, x0 + it.x - 1 * res, y - 1 * res);
        b.fillStyle = color; b.fillText(it.w.display, x0 + it.x, y); b.restore();
      } else inkText(b, it.w.display, x0 + it.x, y, bl, color, res, hash(it.w.start, it.w.text.length) * 1e6);
    }
    y += l.h * 0.18;
  }
  if (p.style === 'ground' || p.grain) {   // the surface's tooth breaks the ink up
    b.save(); b.globalCompositeOperation = 'destination-out'; b.globalAlpha = env.val(p.grain, 0.55); b.fillStyle = grainPattern(b); b.fillRect(0, 0, bwid, bhei); b.restore();
  }
  if (p.style === 'etch') {   // fine scratches through the etching
    b.save(); b.globalCompositeOperation = 'destination-out'; b.strokeStyle = 'rgba(0,0,0,0.5)'; b.lineWidth = res;
    for (let k = 0; k < 18; k++) { const yy = hash(k, 3) * bhei; b.beginPath(); b.moveTo(0, yy); b.lineTo(bwid, yy + (hash(k, 4) - 0.5) * 40 * res); b.stroke(); }
    b.restore();
  }
  g.globalAlpha = env.val(p.opacity, 1);
  warpQuad(g, blk, quadOf(env, p, bwid / res, bhei / res), { nx: p.mesh?.[0] ?? 16, ny: p.mesh?.[1] ?? 8 });
}
