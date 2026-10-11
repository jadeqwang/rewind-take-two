// slate.js: placeholder animatic card (Canvas2D module): section name, game genre, bar:beat counter and a beat pulse.
// Used by the starter render/timeline.js until real shots replace each section.
//   params: title, subtitle, note, color, ink
export function draw(lt, env) {
  const g = env.ctx, p = env.params, T = env.T, t = env.t;
  const ink = p.ink || '#0b0b0c', col = p.color || '#ece7dc';
  g.fillStyle = col; g.fillRect(0, 0, 1920, 1080);
  const pulse = env.pulse('beat', 0.15), down = env.pulse('downbeat', 0.25);
  g.strokeStyle = ink; g.globalAlpha = 0.12 + 0.25 * down; g.lineWidth = 2;
  for (let x = 0; x <= 1920; x += 120) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 1080); g.stroke(); }
  g.globalAlpha = 1; g.fillStyle = ink; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.font = '140px Anton'; g.fillText(String(p.title || env.shot.id).toUpperCase(), 120, 360);
  g.font = 'italic 500 54px "CMU Serif"'; g.fillText(p.subtitle || '', 124, 450);
  if (p.note) { g.font = '400 26px "JetBrains Mono"'; g.globalAlpha = 0.7; g.fillText(p.note, 124, 520); g.globalAlpha = 1; }
  const bb = T.barBeatAt(t);
  g.font = '700 40px "JetBrains Mono"';
  g.fillText(`bar ${bb.bar}:${Math.floor(bb.beat)}   ${t.toFixed(2)} s   (${(t - env.shot.start).toFixed(2)} / ${(env.shot.end - env.shot.start).toFixed(2)})`, 124, 640);
  g.beginPath(); g.arc(1760, 200, 30 + 30 * pulse, 0, 7); g.fill();
  g.fillRect(124, 680, 1672 * Math.min(1, (t - env.shot.start) / (env.shot.end - env.shot.start)), 8);
}
