// quad.js (v5 signs): projective sub-quads of a corner-pin track, for laying several pieces (an engraved panel face,
// a large and a small line of lettering) inside one tracked sign. Pure maths; imported by render/timeline/A.js.
//   subQuad(keys, [u0, v0, u1, v1]) -> keys of the same times whose quads are the rectangle [u0..u1] x [v0..v1] of the
//   unit square mapped through each key's quad (TL, TR, BR, BL), so text stays in the sign's own perspective.
function homography(q) {   // unit square -> quad (same as render/engine/modules/lib/text.js)
  const [x0, y0, x1, y1, x2, y2, x3, y3] = q;
  const dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2, sx = x0 - x1 + x2 - x3, sy = y0 - y1 + y2 - y3;
  const den = dx1 * dy2 - dx2 * dy1 || 1e-9;
  const g7 = (sx * dy2 - dx2 * sy) / den, h8 = (dx1 * sy - sx * dy1) / den;
  const a = x1 - x0 + g7 * x1, b = x3 - x0 + h8 * x3, c = x0, d = y1 - y0 + g7 * y1, e = y3 - y0 + h8 * y3, f = y0;
  return (u, v) => { const w = g7 * u + h8 * v + 1; return [(a * u + b * v + c) / w, (d * u + e * v + f) / w]; };
}
export const subOf = (q, [u0, v0, u1, v1]) => { const H = homography(q); return [...H(u0, v0), ...H(u1, v0), ...H(u1, v1), ...H(u0, v1)]; };
export const subQuad = (keys, r) => keys.map(([t, q, ...rest]) => [t, subOf(q, r), ...rest]);
// per-frame keys (k/24) -> a corners function that holds each quad for its whole source frame, the way the engine
// shows a video layer (frame = floor(t * 24)); interpolated keys run up to a frame ahead of the plate on fast moves
export const stepKeys = (keys, fps = 24) => (lt) => keys[Math.max(0, Math.min(keys.length - 1, Math.floor(lt * fps + 1e-4)))][1];
