// fx_car.js (v4, B): Canvas2D layers that make the 1:30 car shot move (see car_shot.js). Deterministic: only env.t.
//   params.kind 'strobe'  roof light-bar flashes: white engraved starbursts, the bar's two ends alternating on twos.
//                         points [[x, y, r], ...] in the layer's own design px, cam {scale, x, y} (functions ok) maps
//                         them to the screen exactly as the image layer under them; phase (0..1) staggers cars
//   params.kind 'sweep'   a passing streetlight: a soft pale band crossing the cabin from front to back once per
//                         `every` beats (on the tracked beat grid), `amount` = peak opacity; screen blend on the layer
const PAPER = [236, 231, 220];

function starburst(g, x, y, r, a) {
  g.save(); g.translate(x, y); g.globalAlpha = a;
  const rg = g.createRadialGradient(0, 0, 0, 0, 0, r * 0.45);
  rg.addColorStop(0, `rgba(${PAPER},1)`); rg.addColorStop(1, `rgba(${PAPER},0)`);
  g.fillStyle = rg; g.beginPath(); g.arc(0, 0, r * 0.45, 0, 7); g.fill();
  g.strokeStyle = `rgba(${PAPER},1)`; g.lineCap = 'round';
  for (let i = 0; i < 16; i++) {
    const ang = i * Math.PI / 8 + 0.1, len = r * (i % 2 ? 0.55 : 1) * (i % 4 === 0 ? 1.15 : 1);
    g.lineWidth = Math.max(0.8, r * (i % 2 ? 0.03 : 0.05));
    g.beginPath(); g.moveTo(Math.cos(ang) * r * 0.12, Math.sin(ang) * r * 0.12); g.lineTo(Math.cos(ang) * len, Math.sin(ang) * len); g.stroke();
  }
  g.restore();
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  if (p.kind === 'strobe') {
    const c = p.cam || {}, s = env.val(c.scale, 1), cx = env.val(c.x, 0), cy = env.val(c.y, 0);
    const k = Math.floor(t * 12 + (p.phase || 0) * 12);              // on twos at 24 fps
    p.points.forEach(([x, y, r], i) => {
      const on = ((k >> 1) + i) % 2 === 0, a = on ? 1 : 0.18;          // the two ends of the bar alternate
      starburst(g, 960 + cx + s * (x - 960), 540 + cy + s * (y - 540), r * s * (on ? 1 : 0.6), a * env.val(p.opacity, 1));
    });
  } else if (p.kind === 'sweep') {
    const B = env.T.beats, every = p.every || 2;
    let i = 0; while (i < B.length - 1 && B[i + 1] <= t + 1e-6) i++;
    i -= i % every;
    const b0 = B[i], b1 = B[Math.min(B.length - 1, i + every)], u = (t - b0) / Math.max(0.1, b1 - b0);   // 0..1 over one sweep
    if (u < 0 || u > 1) return;
    const amt = env.val(p.amount, 0.16) * Math.sin(Math.PI * Math.min(1, u * 1.15));
    // a band perpendicular to the direction of travel, from the top of the windshield (front) to the bottom-left (back)
    const x0 = 1500 - 2100 * u, y0 = -200 + 1300 * u, gr = g.createLinearGradient(x0 - 260, y0 - 150, x0 + 260, y0 + 150);
    gr.addColorStop(0, `rgba(${PAPER},0)`); gr.addColorStop(0.5, `rgba(${PAPER},${amt.toFixed(3)})`); gr.addColorStop(1, `rgba(${PAPER},0)`);
    g.fillStyle = gr; g.fillRect(0, 0, 1920, 1080);
  }
}
