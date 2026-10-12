// hud_backing.js (v5-coda2 Round 5, docs/revisions/v5/coda2.md): a faint, soft dark backing behind a HUD line, so the
// ITERATION counter's last ticks stay readable over the door's hatched stone. Not a box: a blurred, rounded shade.
//   params: rect [x, y, w, h] (design px), color ('#1a120c'), alpha (0.35), blur (px, 10), radius (px, 14)
export function draw(lt, env) {
  const g = env.ctx, p = env.params;
  const [x, y, w, h] = p.rect, r = p.radius ?? 14;
  g.save();
  g.filter = `blur(${(p.blur ?? 10) * env.S}px)`;
  g.globalAlpha = p.alpha ?? 0.35;
  g.fillStyle = p.color ?? '#1a120c';
  g.beginPath();
  g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); g.fill();
  g.restore();
}
