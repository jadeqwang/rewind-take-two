// Section B: fill a corner-pinned quad with a flat colour (the lit face of a billboard under woodcut lettering).
//   params.corners [x0,y0, x1,y1, x2,y2, x3,y3] TL, TR, BR, BL design px (keyframable), color, line (ink keyline px, 0 = none)
export function draw(lt, env) {
  const g = env.ctx, p = env.params, c = env.val(p.corners);
  g.beginPath(); g.moveTo(c[0], c[1]); g.lineTo(c[2], c[3]); g.lineTo(c[4], c[5]); g.lineTo(c[6], c[7]); g.closePath();
  g.fillStyle = env.val(p.color, '#efe7da'); g.fill();
  if (p.line) { g.strokeStyle = p.ink || '#0b0b0c'; g.lineWidth = p.line; g.stroke(); }
}
