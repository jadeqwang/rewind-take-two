// hilbert_lobby.js (v5 post-credits PC2; docs/revisions/v5/build.md): the receptionist's POV at the Hilbert Hotel.
// One camera move over a tall full-colour plate (media/shots/PC/lobby.jpg, 4:3: the hall on top, the desk and the open
// guest ledger below): it starts looking down at the ledger (every line filled: room numbers down the margin, the
// artists and mathematicians the film quotes, in ink) and tilts up to the hall, where an endless queue of Jades runs
// straight down the carpet into the vanishing point, the protagonist at its head.
//
// Queue geometry (one-point perspective, design px of the plate's world, plate width = 1920): person k stands at depth
// d_k (d = 1 is the protagonist); everything scales by 1/d about the vanishing point vp, so feet = vp.y + (feet0 - vp.y)/d
// and height = H0/d. The camera is a little above their heads (head0 > vp.y), so each Jade further back stands a
// little higher in frame and the line rises over the protagonist's bun into the vanishing point. The queue's axis is
// a straight line down the hall through her (x = vp.x + (front.x - vp.x)/d); people alternate a little left and right
// of it (like a real queue, so each one's face and identifying feature shows) by `lat` px at d = 1, tapering.
//   params: plate, plateW/plateH (source px), sprites (dir: <name>.png + info.json), vp [x, y], deskY,
//     front {x, feet, h}, order (sprite names after the protagonist, nearest first), cycle (names for the endless tail),
//     depth: {step, near: [d1, d2, ...]} (explicit depths of the first people, then +step each), lat, latTaper, count,
//     snake / snakeF: past the eight committee Jades the line snakes +-snake px (at d = 1) with phase step snakeF per person,
//     camScale / camX / camY (keys, layer-local s: the world point at screen centre), ledger {left, right: [8 numbers,
//     TL TR BR BL], rows: [[room, name], ...] (5 per page)}
const PIX = new Set(['pixel']);

function quadH(q) {   // homography unit square -> quad (TL, TR, BR, BL)
  const [x0, y0, x1, y1, x2, y2, x3, y3] = q;
  const dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2, sx = x0 - x1 + x2 - x3, sy = y0 - y1 + y2 - y3;
  const den = dx1 * dy2 - dx2 * dy1;
  const g = (sx * dy2 - dx2 * sy) / den, h = (dx1 * sy - sx * dy1) / den;
  const a = x1 - x0 + g * x1, b = x3 - x0 + h * x3, d = y1 - y0 + g * y1, e = y3 - y0 + h * y3;
  return (u, v) => { const w = g * u + h * v + 1; return [(a * u + b * v + x0) / w, (d * u + e * v + y0) / w]; };
}

function pageTexture(rows, first, W = 1000, H = 660) {
  const cv = new OffscreenCanvas(W, H), g = cv.getContext('2d');
  const top = 0.17 * H, rh = (0.94 * H - top) / rows.length, mx = 0.17 * W;
  g.strokeStyle = 'rgba(96,118,150,0.55)'; g.lineWidth = 2.2;                         // ruled lines (faded blue)
  for (let i = 0; i <= rows.length; i++) { g.beginPath(); g.moveTo(0.02 * W, top + i * rh); g.lineTo(0.98 * W, top + i * rh); g.stroke(); }
  g.strokeStyle = 'rgba(122,88,150,0.6)'; g.lineWidth = 2.6;                          // margin rule (violet, not red)
  g.beginPath(); g.moveTo(mx, 0.03 * H); g.lineTo(mx, 0.97 * H); g.stroke();
  g.fillStyle = 'rgba(70,58,50,0.85)'; g.font = 'italic 40px "IM Fell English"'; g.textBaseline = 'alphabetic';
  g.textAlign = 'center'; g.fillText('Room', mx / 2 + 6, top - 18); g.textAlign = 'left'; g.fillText('Guest', mx + 34, top - 18);
  g.fillStyle = '#2a2420'; g.strokeStyle = '#2a2420'; g.lineJoin = 'round';
  rows.forEach(([room, name], i) => {
    const base = top + (i + 1) * rh - rh * 0.2, rot = ((first + i) * 37 % 7 - 3) * 0.004;
    g.save(); g.translate(0, base); g.rotate(rot);
    g.font = '86px "Reenie Beanie"'; g.lineWidth = 2.6;
    g.textAlign = 'center'; g.fillText(String(room), mx / 2 + 4, 0); g.strokeText(String(room), mx / 2 + 4, 0);
    g.textAlign = 'left'; g.font = '92px "Reenie Beanie"'; g.lineWidth = 2.8;
    const x = mx + 30 + ((first + i) * 53 % 5) * 6;
    g.fillText(name, x, 0); g.strokeText(name, x, 0);
    g.restore();
  });
  return cv;
}

function drawWarped(g, tex, quad, strips = 48) {
  const H = quadH(quad), tw = tex.width, th = tex.height;
  for (let i = 0; i < strips; i++) {
    const v0 = i / strips, v1 = (i + 1) / strips, sh = th / strips;
    const p00 = H(0, v0), p10 = H(1, v0), p01 = H(0, v1);
    g.save();
    g.transform((p10[0] - p00[0]) / tw, (p10[1] - p00[1]) / tw, (p01[0] - p00[0]) / sh, (p01[1] - p00[1]) / sh, p00[0], p00[1]);
    g.drawImage(tex, 0, v0 * th, tw, sh + 0.6, 0, 0, tw, sh + 0.6);
    g.restore();
  }
}

export async function init(ctx, p, env) {
  const info = await env.loadJSON(p.sprites + '/info.json');
  const S = {};
  for (const n of Object.keys(info)) S[n] = await env.loadImage(`${p.sprites}/${n}.png`);
  const plate = await env.loadImage(p.plate);
  try { await document.fonts.load('92px "Reenie Beanie"'); await document.fonts.load('italic 40px "IM Fell English"'); } catch (e) { /* fonts are preloaded by the engine */ }
  const L = p.ledger, pages = [];
  if (L) {
    const half = Math.ceil(L.rows.length / 2);
    pages.push([pageTexture(L.rows.slice(0, half), 0), L.left]);
    pages.push([pageTexture(L.rows.slice(half), half), L.right]);
  }
  return { S, plate, pages };
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, st = env.state, t = env.t;
  const [vx, vy] = p.vp, deskY = p.deskY, F = p.front;
  const pw = 1920, ph = 1920 * st.plate.height / st.plate.width;
  const sc = env.val(p.camScale, 1), cx = env.val(p.camX, 960), cy = env.val(p.camY, 540);
  g.save();
  g.translate(960, 540); g.scale(sc, sc); g.translate(-cx, -cy);
  g.drawImage(st.plate, 0, 0, pw, ph);
  // ---- the queue, far to near
  const order = p.order, cyc = p.cycle, count = p.count ?? 1500, D = p.depth || {};
  const near = D.near || [], step = D.step ?? 0.5, lat = p.lat ?? 300, taper = p.latTaper ?? 12;
  const depth = k => (k === 0 ? 1 : k <= near.length ? near[k - 1] : near[near.length - 1] + (k - near.length) * step);
  for (let k = count; k >= 0; k--) {
    const d = depth(k), h = F.h / d;
    if (h < 0.7) continue;
    const name = k === 0 ? 'jade' : k <= order.length ? order[k - 1] : cyc[Math.floor(env.core.hash(k, 911) * cyc.length) % cyc.length];
    const im = st.S[name];
    const side = k === 0 ? 0 : (k % 2 ? -1 : 1);
    const amp = k === 0 ? 0 : lat * (0.55 + 0.45 / (1 + (k - 1) / taper)) * (0.85 + 0.3 * env.core.hash(k, 5));
    // past the named Jades the line snakes gently along the carpet (world px at d = 1), so the far figures stay
    // visible one behind another all the way into the vanishing point instead of stacking into one smear
    const kn = order.length - 8, sn = k > kn ? (p.snake ?? 0) * Math.min(1, (k - kn) / 5) * Math.sin((k - kn) * (p.snakeF ?? 0.45)) : 0;
    const x = vx + (F.x - vx + side * amp * (k > kn ? 0.35 : 1) + sn) / d;
    const bob = Math.sin(t * 2 * Math.PI * 0.3 + k * 1.7) * 0.004 * F.h;      // breathing
    const feet = vy + (F.feet - vy) / d, hh = (F.h + bob) / d;
    if (h < 3) { g.globalAlpha = 0.85; g.fillStyle = name.startsWith('ghost') ? '#c9a227' : '#4a4038'; g.fillRect(x - hh * 0.12, feet - hh, hh * 0.24, hh); g.globalAlpha = 1; continue; }
    const w = hh * im.width / im.height;
    g.imageSmoothingEnabled = !PIX.has(name);
    g.drawImage(im, x - w / 2, feet - hh, w, hh);
  }
  g.imageSmoothingEnabled = true;
  // ---- the desk in front of their legs: the plate again below the desk's far edge
  const sy = deskY / ph * st.plate.height;
  g.drawImage(st.plate, 0, sy, st.plate.width, st.plate.height - sy, 0, deskY, pw, ph - deskY);
  // ---- the ledger, every line filled in ink
  g.globalCompositeOperation = 'multiply';
  for (const [tex, quad] of st.pages) drawWarped(g, tex, quad);
  g.globalCompositeOperation = 'source-over';
  g.restore();
}
