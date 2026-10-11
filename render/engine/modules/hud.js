// hud.js: game UI (Canvas2D module). One mode per layer (treatment rule: at most one HUD layer per frame).
//   params.mode:
//     'platformer'  death counter (+1 on every event), speedrun timer, iteration counter, level name
//                   {deaths: {base: 41, on: 'beat', from: <abs time>}, timer: {from: <abs time>, offset: 0}, iteration: 7, level: 'LSD-1'}
//     'rewind'      ◀◀ REWIND  ×N  {multiplier: keyframes (e.g. [[0,2,'hold'],[0.9,4,'hold'],[1.8,8]]), counter: keyframes (s) }
//     'pause'       ▶ RESUME / ◀◀ REWIND / QUIT  {cursor: keyframes of item index (fractional = moving), items?}
//     'loading'     LOADING + tip {tip: 'string', progress: keyframes 0..1}
//   params.color / accent / scale / opacity are keyframable.
// Pure function of (t, params): counters are counted from the timing grid, never accumulated.

const P = { ink: '#0b0b0c', paper: '#ece7dc', orange: '#ff7a1a', sky: '#7ec8ff', alert: '#ff2a2a' };

export function init(ctx, params) { return {}; }

export function draw(lt, env) {
  const g = env.ctx, p = env.params, mode = p.mode || 'platformer';
  const col = env.val(p.color, P.paper), acc = env.val(p.accent, P.orange), sc = env.val(p.scale, 1);
  g.globalAlpha = env.val(p.opacity, 1);
  if (mode === 'platformer') platformer(g, env, p, col, acc, sc);
  else if (mode === 'rewind') rewind(g, env, p, col, acc, sc, lt);
  else if (mode === 'pause') pause(g, env, p, col, acc, sc);
  else if (mode === 'loading') loading(g, env, p, col, acc, sc, lt);
}

function plate(g, x, y, w, h, a = 0.55) { g.fillStyle = `rgba(11,11,12,${a})`; g.fillRect(x, y, w, h); }

function skull(g, x, y, s, col) {
  g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = col;
  g.beginPath(); g.arc(0, -4, 13, Math.PI, 0); g.lineTo(13, 4); g.lineTo(8, 8); g.lineTo(8, 14); g.lineTo(-8, 14); g.lineTo(-8, 8); g.lineTo(-13, 4); g.closePath(); g.fill();
  g.fillStyle = P.ink; g.beginPath(); g.arc(-5, -2, 4, 0, 7); g.arc(5, -2, 4, 0, 7); g.fill();
  g.fillRect(-1.5, 4, 3, 4); g.restore();
}

function platformer(g, env, p, col, acc, sc) {
  const T = env.T, t = env.t;
  const d = p.deaths || {};
  const from = d.from !== undefined ? T.time(d.from) : env.shot.start;
  const list = d.on === 'downbeat' ? 'downbeats' : d.on === 'kick' ? 'kicks' : 'beats';
  const deaths = (d.base ?? 0) + T.countIn(from, t + 1e-6, list);
  const since = t - (T.lastEvent(t, list) ?? -9);
  const pop = since >= 0 && since < 0.25 && T.lastEvent(t, list) >= from ? Math.exp(-since / 0.07) : 0;
  g.save(); g.scale(sc, sc);
  // top-left: skull + deaths
  plate(g, 48, 44, 400, 86);
  skull(g, 96, 84, 1.45 + 0.35 * pop, pop > 0.3 ? acc : col);
  g.font = `${Math.round(64 + 14 * pop)}px Anton`; g.textBaseline = 'middle'; g.fillStyle = pop > 0.3 ? acc : col;
  g.fillText(String(deaths), 140, 90);
  const nw = g.measureText(String(deaths)).width;
  g.font = '700 18px "JetBrains Mono"'; g.fillStyle = col; g.globalAlpha *= 0.75; g.fillText('DEATHS', 140 + nw + 18, 76); g.globalAlpha /= 0.75;
  if (p.iteration !== undefined) { g.font = '700 18px "JetBrains Mono"'; g.fillStyle = col; g.fillText(`ITERATION ${env.val(p.iteration)}`, 140 + nw + 18, 104); }
  // top-right: speedrun timer
  const tm = p.timer || {};
  const tf = tm.from !== undefined ? T.time(tm.from) : env.shot.start;
  const clockT = (tm.offset ?? 0) + (t - tf) * (tm.rate ?? 1);
  plate(g, 1920 - 48 - 360, 44, 360, 86);
  g.font = '700 54px "JetBrains Mono"'; g.textAlign = 'right'; g.fillStyle = col;
  const c = env.core.clock(clockT);
  g.fillText(c.slice(0, -3), 1920 - 48 - 92, 90);
  g.font = '700 34px "JetBrains Mono"'; g.fillStyle = acc; g.fillText(c.slice(-3), 1920 - 48 - 22, 96);
  if (p.level) { g.font = '700 18px "JetBrains Mono"'; g.fillStyle = col; g.globalAlpha *= 0.7; g.fillText(String(p.level), 1920 - 48 - 22, 152); }
  g.restore();
}

function tri(g, x, y, s, dir = -1) { g.beginPath(); g.moveTo(x + dir * s, y); g.lineTo(x - dir * s * 0.2, y - s * 0.85); g.lineTo(x - dir * s * 0.2, y + s * 0.85); g.closePath(); g.fill(); }

function rewind(g, env, p, col, acc, sc, lt) {
  const mult = Math.round(env.val(p.multiplier, 2));
  const blink = Math.floor(lt * 2.5) % 2 === 0;
  g.save(); g.scale(sc, sc);
  const x = 96, y = 104;
  g.fillStyle = col;
  if (blink || p.steady) { tri(g, x + 26, y, 30); tri(g, x + 66, y, 30); }
  g.font = '64px Anton'; g.textBaseline = 'middle'; g.fillText('REWIND', x + 120, y + 4);
  // multiplier, punched when it changes
  const keys = Array.isArray(p.multiplier) ? p.multiplier.map(k => k[0]).filter(k => k <= lt) : [];
  const since = keys.length ? lt - keys[keys.length - 1] : 9;
  const pop = Math.exp(-since / 0.12);
  g.font = `${Math.round(72 + 30 * pop)}px Anton`; g.fillStyle = acc; g.textAlign = 'left';
  g.fillText(`×${mult}`, x + 360, y + 4);
  // tape counter (bottom-right), running backward
  const cnt = p.counter !== undefined ? env.val(p.counter) : null;
  if (cnt !== null) {
    g.font = '700 40px "JetBrains Mono"'; g.textAlign = 'right'; g.fillStyle = col;
    g.fillText(env.core.clock(cnt), 1920 - 80, 1080 - 90);
  }
  // scrubbing bar (bottom): position keyframable 0..1
  if (p.scrub !== undefined) {
    const u = env.val(p.scrub, 0.5);
    g.fillStyle = 'rgba(236,231,220,.25)'; g.fillRect(200, 1080 - 64, 1520, 6);
    g.fillStyle = acc; g.fillRect(200, 1080 - 64, 1520 * u, 6); g.beginPath(); g.arc(200 + 1520 * u, 1080 - 61, 12, 0, 7); g.fill();
  }
  g.restore();
}

function pause(g, env, p, col, acc, sc) {
  const items = p.items || ['▶ RESUME', '◀◀ REWIND', 'QUIT'];
  const cur = env.val(p.cursor, 0);
  g.save(); g.scale(sc, sc);
  g.fillStyle = 'rgba(11,11,12,.62)'; g.fillRect(0, 0, 1920, 1080);
  g.font = '120px Anton'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = col; g.fillText('PAUSED', 960, 330);
  items.forEach((it, k) => {
    const y = 520 + k * 110, on = Math.max(0, 1 - Math.abs(cur - k));
    g.font = `${Math.round(64 + 10 * on)}px Anton`; g.fillStyle = on > 0.5 ? acc : col; g.globalAlpha = 0.55 + 0.45 * on;
    g.fillText(it.replace(/[▶◀]/g, '').trim(), 960, y);
    if (/^▶/.test(it)) { g.fillStyle = g.fillStyle; tri(g, 960 - 230, y, 22, 1); }
    if (/^◀◀/.test(it)) { tri(g, 960 - 270, y, 22); tri(g, 960 - 236, y, 22); }
  });
  g.globalAlpha = 1;
  const y = 520 + cur * 110; g.fillStyle = acc; tri(g, 960 - 330 - 8 * Math.sin(env.t * 12), y, 26, 1);
  g.restore();
}

function loading(g, env, p, col, acc, sc, lt) {
  const prog = env.val(p.progress, Math.min(1, lt / 1.5));
  g.save(); g.scale(sc, sc);
  g.font = '72px Anton'; g.textBaseline = 'middle'; g.fillStyle = col; g.textAlign = 'left';
  const dots = '.'.repeat(1 + (Math.floor(lt * 4) % 3));
  g.fillText('LOADING' + dots, 96, 120);
  g.fillStyle = 'rgba(128,124,118,.35)'; g.fillRect(96, 170, 560, 10);
  g.fillStyle = acc; g.fillRect(96, 170, 560 * prog, 10);
  if (p.tip) {
    g.font = '700 26px "JetBrains Mono"'; g.textAlign = 'right'; g.fillStyle = col;
    g.fillText('TIP: ' + p.tip, 1920 - 96, 124);
  }
  g.restore();
}
