// hud.js: game UI in Press Start 2P (shot list: small, top corners only, at most one HUD cluster on screen).
// One mode per layer. Every value is a pure function of time (counters count timing events; nothing accumulates).
//   common: color '#ece7dc' (ink '#0b0b0c' over paper), accent '#F08A24', side 'left'|'right' (cluster corner), size 26,
//           margin 56, opacity, pop (frames of scale-pop on a counter change, 4)
//   'platformer'  ITERATION n / skull ×deaths / speedrun timer.  iteration: number | keys, deaths: {base, on: 'beat'|
//                 'downbeat'|event list, from (abs/local; default layer start)} or number, timer: {from, offset, rate} | false
//   'iteration'   the rolling odometer: value = base + rate·(t − from) (rate per second; keep rolling forever for the
//                 ending) or keyframed `value`; snap (mechanical ticks instead of a continuous roll), label 'ITERATION',
//                 flicker 0..1, digits roll with carry
//   'pause'       PAUSED / ▶ RESUME / ◀◀ REWIND / QUIT; cursor (item index keys, fractional = moving), blinkAt (the
//                 selection blinks for .4 s), dim (overlay alpha .45)
//   'continue'    CONTINUE? + countdown: from 9, every (s, .8) or on (events), start (abs/local), press ('PRESS ◀◀')
//   'loading'     LOADING screen: title ('Reload.'), tip (string), deaths (×n top-right), spinner (spinning pencil),
//                 progress keys, bg ('#0b0b0c'; null = transparent)
//   'rewind'      ◀◀ ×N (multiplier keys), ring (clock ring sweeping counter-clockwise; sweep keys 0..1 or rate),
//                 counter (tape counter keys, s), scrub (0..1 keys)
//   'race'        GHOST: ITERATION n + split (keys, s; negative = ahead: pale blue; behind: orange), splitColor keys
import { absT, fontName } from './lib/text.js';
import { clamp, clock as fmtClock, hash } from '../src/core.js';

const P2 = fontName('hud');
const fmt = n => Math.round(n).toLocaleString('en-US');
const SKULL = ['00111100', '01111110', '11011011', '11011011', '11111111', '01110110', '00111100', '00101000'];

export function draw(lt, env) {
  const g = env.ctx, p = env.params, mode = p.mode || 'platformer';
  g.globalAlpha = env.val(p.opacity, 1); g.textBaseline = 'alphabetic'; g.letterSpacing = '0px';
  const M = { platformer, iteration, pause, continue: cont, loading, rewind, race }[mode];
  if (!M) throw new Error(`hud: unknown mode "${mode}"`);
  M(g, env, p, lt);
}

const colOf = (env, p) => env.val(p.color, '#ece7dc'), accOf = (env, p) => env.val(p.accent, '#F08A24');
function corner(env, p, width) { const m = env.val(p.margin, 56); return (p.side || 'left') === 'right' ? 1920 - m - width : m; }
function skull(g, x, y, px, color) { g.fillStyle = color; SKULL.forEach((r, j) => [...r].forEach((b, i) => { if (b === '1') g.fillRect(x + i * px, y + j * px, px, px); })); }
function tri(g, x, y, s, dir = -1) { g.beginPath(); g.moveTo(x + dir * s, y); g.lineTo(x - dir * s * 0.2, y - s * 0.85); g.lineTo(x - dir * s * 0.2, y + s * 0.85); g.closePath(); g.fill(); }
function rw(g, x, y, s) { tri(g, x, y, s); tri(g, x + s * 1.15, y, s); }

function count(env, d, t) {
  if (typeof d === 'number' || Array.isArray(d)) return { n: env.val(d, 0), since: 9 };
  d = d || {};
  const from = d.from !== undefined ? absT(env, d.from) : env.origin, on = d.on || 'beat';
  const list = on === 'beat' ? 'beats' : on === 'downbeat' ? 'downbeats' : on;
  const n = (d.base ?? 0) + env.T.countIn(from, t + 1e-6, list) * (d.step ?? 1);
  const last = env.T.lastEvent(t, list);
  return { n, since: last !== null && last >= from ? t - last : 9 };
}

function platformer(g, env, p) {
  const t = env.t, size = env.val(p.size, 26), col = colOf(env, p), acc = accOf(env, p);
  const it = p.iteration !== undefined ? env.val(p.iteration) : null;
  const dc = p.deaths !== undefined ? count(env, p.deaths, t) : null;
  const tm = p.timer === false ? null : (p.timer || {});
  const rows = [];
  if (it !== null) rows.push({ text: `ITERATION ${fmt(it)}` });
  if (dc) rows.push({ text: `×${fmt(dc.n)}`, skull: true, pop: dc.since * 24 < (p.pop ?? 4) });
  if (tm) { const from = tm.from !== undefined ? absT(env, tm.from) : env.origin; rows.push({ text: fmtClock((tm.offset ?? 0) + (t - from) * (tm.rate ?? 1)), timer: true }); }
  g.font = `${size}px ${P2}`;
  const width = Math.max(...rows.map(r => g.measureText(r.text).width + (r.skull ? size * 1.5 : 0)));
  const x0 = corner(env, p, width), right = (p.side || 'left') === 'right';
  rows.forEach((r, k) => {
    const y = env.val(p.margin, 56) + size + k * size * 1.75, w = g.measureText(r.text).width + (r.skull ? size * 1.5 : 0);
    let x = right ? x0 + width - w : x0;
    g.save();
    if (r.pop) { g.translate(x + w / 2, y - size / 2); g.scale(1.25, 1.25); g.translate(-(x + w / 2), -(y - size / 2)); }
    if (r.skull) { skull(g, x, y - size, size / 8, r.pop ? acc : col); x += size * 1.5; }
    g.fillStyle = r.pop ? acc : col; g.fillText(r.text, x, y);
    g.restore();
  });
}

function iteration(g, env, p) {
  const t = env.t, size = env.val(p.size, 26), col = colOf(env, p);
  const v = p.value !== undefined ? env.val(p.value) : (p.base ?? 4097) + (p.rate ?? 0) * Math.max(0, t - absT(env, p.from, 0));
  let N = Math.floor(v + 1e-9), frac = v - N;
  if (p.snap) frac = clamp((frac - 0.82) / 0.18) ** 2;
  const fl = env.val(p.flicker, 0); if (fl > 0) g.globalAlpha *= 1 - fl * (hash(env.frame, 5) > 0.7 ? 0.8 * hash(env.frame, 6) : 0);
  const label = (p.label ?? 'ITERATION') + ' ', s = fmt(N);
  g.font = `${size}px ${P2}`;
  const cw = g.measureText('0').width, lw = g.measureText(label).width, width = lw + cw * s.length;
  const x0 = corner(env, p, width), y = env.val(p.y, env.val(p.margin, 56) + size);
  g.fillStyle = col; g.fillText(label, x0, y);
  // odometer: digit k rolls only while every digit to its right is a 9 (carry)
  const digits = [...s]; let lowerNines = true;
  for (let k = digits.length - 1; k >= 0; k--) {
    const ch = digits[k], x = x0 + lw + k * cw;
    if (ch === ',') { g.fillText(',', x, y); continue; }
    const d = +ch, f = lowerNines ? frac : 0;
    g.save(); g.beginPath(); g.rect(x - 2, y - size * 1.15, cw + 4, size * 1.3); g.clip();
    g.fillText(String(d), x, y - f * size * 1.25); if (f > 0) g.fillText(String((d + 1) % 10), x, y + (1 - f) * size * 1.25);
    g.restore();
    if (d !== 9) lowerNines = false;
  }
}

function pause(g, env, p) {
  const t = env.t, col = colOf(env, p), acc = accOf(env, p), items = p.items || ['RESUME', 'REWIND', 'QUIT'], icons = p.icons || ['play', 'rw', null];
  const dim = env.val(p.dim, 0.45); if (dim > 0) { g.fillStyle = `rgba(11,11,12,${dim})`; g.fillRect(0, 0, 1920, 1080); }
  const cur = env.val(p.cursor, 0), sel = Math.round(cur);
  const blinkAt = p.blinkAt !== undefined ? absT(env, p.blinkAt) : null;
  const blinking = blinkAt !== null && t >= blinkAt && t < blinkAt + (p.blinkDur ?? 0.4) && Math.floor((t - blinkAt) * 16) % 2 === 1;
  g.textAlign = 'left'; g.font = `64px ${P2}`; g.fillStyle = col; const tw = g.measureText('PAUSED').width; g.fillText('PAUSED', 960 - tw / 2, 380);
  g.font = `40px ${P2}`;
  const x = 760;
  items.forEach((it, k) => {
    const y = 540 + k * 96, on = k === sel;
    if (on && blinking) return;
    g.fillStyle = on ? acc : col;
    if (icons[k] === 'play') tri(g, x + 18, y - 18, 20, 1); else if (icons[k] === 'rw') rw(g, x + 10, y - 18, 18);
    g.fillText(it, x + 80, y);
  });
  const cy = 540 + cur * 96 - 18; g.fillStyle = acc; tri(g, x - 60 - 6 * Math.sin(t * 10), cy, 18, 1);
}

function cont(g, env, p) {
  const t = env.t, col = colOf(env, p), acc = accOf(env, p), start = absT(env, p.start, 0);
  let n = p.from ?? 9;
  if (p.on) n -= env.T.countIn(start, t + 1e-6, p.on === 'beat' ? 'beats' : p.on);
  else n -= Math.floor(Math.max(0, t - start) / (p.every ?? 0.8));
  n = Math.max(0, n);
  g.textAlign = 'center'; g.fillStyle = col; g.font = `72px ${P2}`; g.fillText('CONTINUE?', 960, 400);
  g.font = `220px ${P2}`; g.fillStyle = acc; g.fillText(String(n), 960, 690);
  if (Math.floor(t * 3) % 2 === 0) { g.font = `28px ${P2}`; g.fillStyle = col; g.fillText(p.press ?? 'PRESS', 900, 820); rw(g, 1065, 808, 16); }
}

function loading(g, env, p, lt) {
  const t = env.t, col = colOf(env, p), acc = accOf(env, p), bg = p.bg === undefined ? '#0b0b0c' : p.bg;
  if (bg) { g.fillStyle = bg; g.fillRect(0, 0, 1920, 1080); }
  g.textAlign = 'center'; g.fillStyle = col;
  if (p.title !== null) { g.font = `${env.val(p.titleSize, 84)}px ${P2}`; g.fillText(p.title ?? 'LOADING', 960, 560); }
  g.font = `24px ${P2}`; g.textAlign = 'left';
  const dots = '.'.repeat(1 + (Math.floor(lt * 4) % 3)); g.fillText('LOADING' + dots, 96, 1000);
  if (p.progress !== undefined) { const u = env.val(p.progress, 0); g.fillStyle = 'rgba(128,124,118,.4)'; g.fillRect(96, 1020, 420, 8); g.fillStyle = acc; g.fillRect(96, 1020, 420 * u, 8); }
  if (p.tip) { g.fillStyle = col; g.font = `22px ${P2}`; g.textAlign = 'center'; g.fillText('TIP: ' + p.tip, 960, 860); }
  if (p.deaths !== undefined) { const d = env.val(p.deaths); g.font = `26px ${P2}`; g.textAlign = 'left'; const s = `×${fmt(d)}`, w = g.measureText(s).width + 40; skull(g, 1920 - 56 - w, 56, 26 / 8, col); g.fillStyle = col; g.fillText(s, 1920 - 56 - w + 40, 82); }
  if (p.spinner !== false) {   // spinning pencil glyph
    g.save(); g.translate(1780, 990); g.rotate(-t * 5);
    g.fillStyle = col; g.fillRect(-6, -40, 12, 56); g.beginPath(); g.moveTo(-6, 16); g.lineTo(6, 16); g.lineTo(0, 34); g.closePath(); g.fill();
    g.fillStyle = acc; g.fillRect(-6, -46, 12, 8); g.restore();
  }
}

function rewind(g, env, p, lt) {
  const t = env.t, col = colOf(env, p), acc = accOf(env, p), mult = Math.round(env.val(p.multiplier, 2));
  const keys = Array.isArray(p.multiplier) ? p.multiplier.map(k => (typeof k[0] === 'number' ? k[0] : env.T.time(k[0]) - env.origin)).filter(k => k <= lt) : [];
  const pop = keys.length && (lt - keys[keys.length - 1]) * 24 < (p.pop ?? 4);
  const x = env.val(p.x, 96), y = env.val(p.y, 120);
  g.fillStyle = col; if (Math.floor(lt * 2.5) % 2 === 0 || p.steady) rw(g, x + 30, y - 20, 28);
  g.font = `${pop ? 64 : 52}px ${P2}`; g.fillStyle = acc; g.fillText(`×${mult}`, x + 110, y);
  if (p.ring) {   // clock ring sweeping counter-clockwise
    const sw = p.sweep !== undefined ? env.val(p.sweep, 0) : lt * (p.rate ?? 0.5), R = env.val(p.ringRadius, 380);
    g.save(); g.strokeStyle = col; g.globalAlpha *= 0.7; g.lineWidth = 3; g.beginPath(); g.arc(960, 540, R, 0, 7); g.stroke();
    for (let k = 0; k < 12; k++) { const a = k * Math.PI / 6; g.beginPath(); g.moveTo(960 + Math.cos(a) * (R - 18), 540 + Math.sin(a) * (R - 18)); g.lineTo(960 + Math.cos(a) * R, 540 + Math.sin(a) * R); g.stroke(); }
    const a1 = -Math.PI / 2, a2 = a1 - (sw % 1) * Math.PI * 2;
    g.strokeStyle = acc; g.globalAlpha /= 0.7; g.lineWidth = 10; g.beginPath(); g.arc(960, 540, R, a1, a2, true); g.stroke();
    g.fillStyle = acc; g.beginPath(); g.arc(960 + Math.cos(a2) * R, 540 + Math.sin(a2) * R, 12, 0, 7); g.fill(); g.restore();
  }
  if (p.counter !== undefined) { g.font = `30px ${P2}`; g.textAlign = 'right'; g.fillStyle = col; g.fillText(fmtClock(env.val(p.counter)), 1920 - 80, 1080 - 90); g.textAlign = 'left'; }
  if (p.scrub !== undefined) {
    const u = env.val(p.scrub, 0.5);
    g.fillStyle = 'rgba(236,231,220,.25)'; g.fillRect(200, 1080 - 64, 1520, 6);
    g.fillStyle = acc; g.fillRect(200, 1080 - 64, 1520 * u, 6); g.beginPath(); g.arc(200 + 1520 * u, 1080 - 61, 12, 0, 7); g.fill();
  }
}

function race(g, env, p) {
  const size = env.val(p.size, 24), col = colOf(env, p);
  const label = `GHOST: ITERATION ${fmt(env.val(p.iteration, 4096))}`, sp = env.val(p.split, 0);
  g.font = `${size}px ${P2}`;
  const s = (sp >= 0 ? '+' : '-') + Math.abs(sp).toFixed(2), width = Math.max(g.measureText(label).width, g.measureText(s).width);
  const x0 = corner(env, p, width), y = env.val(p.margin, 56) + size;
  g.fillStyle = col; g.fillText(label, x0, y);
  g.fillStyle = env.val(p.splitColor, sp < 0 ? '#8DB8E8' : '#F08A24'); g.fillText(s, x0, y + size * 1.75);
}
