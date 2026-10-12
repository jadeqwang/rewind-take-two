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
//     camScale / camX / camY (keys, layer-local s: the world point at screen centre), idle {dir, figs: {name: [phase s,
//     rate]}} (v5-coda2: per-figure looping idle frames, dir/<name>/f_0001.png + info.json), ledger {left, right: [8 numbers,
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

function pageTexture(rows, first, W = 1000, H = 660, k = 1) {
  const cv = new OffscreenCanvas(W * k, H * k), g = cv.getContext('2d');
  g.scale(k, k);
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

// ---- v5-coda2 (Jade, Round 3: "guestbook text should bend naturally with the page"): each page is a curved surface,
// not a flat quad. Its far (top) and near (bottom) edges are polylines measured off the plate (left -> right on screen);
// a point at page fraction u (left -> right) and depth v (far -> near) is T(u) + (B(u) - T(u)) * w(v), w = perspective
// (the near edge is r times wider than the far one). The page's lift shows as the top edge's rise above its chord; the
// handwriting is laid out by surface arc length (sqrt(dx^2 + (lift' / cos elev)^2)), so it foreshortens where the paper
// dives into the gutter and rises at the outer edge. Drawn once, in init, as affine triangles into a world-space canvas.
function polyAt(P, x) {
  if (x <= P[0][0]) return P[0][1];
  for (let i = 1; i < P.length; i++) if (x <= P[i][0]) { const [x0, y0] = P[i - 1], [x1, y1] = P[i]; return y0 + (y1 - y0) * (x - x0) / (x1 - x0); }
  return P[P.length - 1][1];
}

function pageMesh(top, bot, NU = 96, NV = 24, cosE = 0.78) {
  const tx0 = top[0][0], tx1 = top[top.length - 1][0], bx0 = bot[0][0], bx1 = bot[bot.length - 1][0];
  const r = (bx1 - bx0) / (tx1 - tx0);
  const T = u => { const x = tx0 + u * (tx1 - tx0); return [x, polyAt(top, x)]; };
  const B = u => { const x = bx0 + u * (bx1 - bx0); return [x, polyAt(bot, x)]; };
  const lift = u => { const [x, y] = T(u); const yc = top[0][1] + (top[top.length - 1][1] - top[0][1]) * u; return yc - y; };
  // texture coordinate = normalised surface arc length across the page
  const S = [0];
  for (let i = 1; i <= NU; i++) {
    const u0 = (i - 1) / NU, u1 = i / NU, dx = (tx1 - tx0) / NU, dz = (lift(u1) - lift(u0)) / cosE;
    S.push(S[i - 1] + Math.hypot(dx, dz));
  }
  const w = v => v * r / (1 + v * (r - 1));
  const pts = [];
  for (let j = 0; j <= NV; j++) {
    const row = [];
    for (let i = 0; i <= NU; i++) {
      const u = i / NU, a = T(u), b = B(u), k = w(j / NV);
      row.push({ x: a[0] + (b[0] - a[0]) * k, y: a[1] + (b[1] - a[1]) * k, s: S[i] / S[NU], v: j / NV });
    }
    pts.push(row);
  }
  return pts;
}

function drawTri(g, tex, a, b, c) {
  const tw = tex.width, th = tex.height;
  const sx0 = a.s * tw, sy0 = a.v * th, sx1 = b.s * tw, sy1 = b.v * th, sx2 = c.s * tw, sy2 = c.v * th;
  const den = (sx1 - sx0) * (sy2 - sy0) - (sx2 - sx0) * (sy1 - sy0);
  if (Math.abs(den) < 1e-9) return;
  const m11 = ((b.x - a.x) * (sy2 - sy0) - (c.x - a.x) * (sy1 - sy0)) / den;
  const m12 = ((c.x - a.x) * (sx1 - sx0) - (b.x - a.x) * (sx2 - sx0)) / den;
  const m21 = ((b.y - a.y) * (sy2 - sy0) - (c.y - a.y) * (sy1 - sy0)) / den;
  const m22 = ((c.y - a.y) * (sx1 - sx0) - (b.y - a.y) * (sx2 - sx0)) / den;
  const dx = a.x - m11 * sx0 - m12 * sy0, dy = a.y - m21 * sx0 - m22 * sy0;
  const cx = (a.x + b.x + c.x) / 3, cy = (a.y + b.y + c.y) / 3, grow = p => [p.x + (p.x - cx) * 0.04 + Math.sign(p.x - cx) * 0.4, p.y + (p.y - cy) * 0.04 + Math.sign(p.y - cy) * 0.4];
  g.save();
  g.beginPath(); const A = grow(a), B = grow(b), C = grow(c); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.lineTo(C[0], C[1]); g.closePath(); g.clip();
  g.transform(m11, m21, m12, m22, dx, dy);
  const x0 = Math.max(0, Math.floor(Math.min(sx0, sx1, sx2)) - 2), y0 = Math.max(0, Math.floor(Math.min(sy0, sy1, sy2)) - 2);
  const x1 = Math.min(tw, Math.ceil(Math.max(sx0, sx1, sx2)) + 2), y1 = Math.min(th, Math.ceil(Math.max(sy0, sy1, sy2)) + 2);
  if (x1 > x0 && y1 > y0) g.drawImage(tex, x0, y0, x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0);
  g.restore();
}

function curvedLedger(pages, box, k) {
  const [bx, by, bw, bh] = box, cv = new OffscreenCanvas(Math.round(bw * k), Math.round(bh * k)), g = cv.getContext('2d');
  g.scale(k, k); g.translate(-bx, -by);
  for (const [tex, curve] of pages) {
    const M = pageMesh(curve.top, curve.bottom);
    for (let j = 0; j < M.length - 1; j++) for (let i = 0; i < M[0].length - 1; i++) {
      drawTri(g, tex, M[j][i], M[j][i + 1], M[j + 1][i + 1]);
      drawTri(g, tex, M[j][i], M[j + 1][i + 1], M[j + 1][i]);
    }
  }
  return cv;
}

export async function init(ctx, p, env) {
  const info = await env.loadJSON(p.sprites + '/info.json');
  const S = {};
  for (const n of Object.keys(info)) S[n] = await env.loadImage(`${p.sprites}/${n}.png`);
  const plate = await env.loadImage(p.plate);
  const idle = {};       // v5-coda2: name -> info.json of its idle sequence (+ phase, rate)
  if (p.idle) for (const [n, [phase, rate]] of Object.entries(p.idle.figs)) {
    try { idle[n] = { ...(await env.loadJSON(`${p.idle.dir}/${n}/info.json`)), phase, rate }; } catch (e) { /* not built yet: sprite + engine idle */ }
  }
  try { await document.fonts.load('92px "Reenie Beanie"'); await document.fonts.load('italic 40px "IM Fell English"'); } catch (e) { /* fonts are preloaded by the engine */ }
  const L = p.ledger, pages = [];
  let curved = null;
  if (L) {
    const half = Math.ceil(L.rows.length / 2);
    if (L.curves) {        // v5-coda2: curved pages, pre-rendered once in world px (box) at the plate's resolution
      const k = L.res ?? 2.5;
      curved = curvedLedger([[pageTexture(L.rows.slice(0, half), 0, 1000, 660, 2), L.curves.left],
                             [pageTexture(L.rows.slice(half), half, 1000, 660, 2), L.curves.right]], L.box, k);
    } else {
      pages.push([pageTexture(L.rows.slice(0, half), 0), L.left]);
      pages.push([pageTexture(L.rows.slice(half), half), L.right]);
    }
  }
  return { S, plate, pages, curved, idle };
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
    const feet = vy + (F.feet - vy) / d, hh = F.h / d;
    if (h < 3) { g.globalAlpha = 0.85; g.fillStyle = name.startsWith('ghost') ? '#c9a227' : '#4a4038'; g.fillRect(x - hh * 0.12, feet - hh, hh * 0.24, hh); g.globalAlpha = 1; continue; }
    // v5-coda2 (Jade: "each one a little different and out of sync ... not bob up and down like a cardboard cutout"):
    // the protagonist and the eight committee Jades (their first, near appearance) play their own idle takes, each at
    // her own phase and rate; everyone else idles in the engine with her own period and phase.
    const iv = k <= order.length ? st.idle[name] : null;
    if (iv) {
      const dur = iv.frames / iv.fps, u = ((t * iv.rate + iv.phase) % dur + dur) % dur;
      const fi = Math.min(iv.frames - 1, Math.floor(u * iv.fps));
      const bmp = env.assets.get(`${p.idle.dir}/${name}/f_${String(fi + 1).padStart(4, '0')}.png`);
      if (bmp) { const sc = hh / iv.figH; g.drawImage(bmp, x - iv.cx * sc, feet - iv.footY * sc, iv.w * sc, iv.h * sc); }
      continue;    // a miss is loaded by the engine, which then draws the frame again
    }
    const H = env.core.hash, P1 = 2.6 + 2.2 * H(k, 31), P2 = 3.4 + 2.6 * H(k, 37), ph1 = 6.283 * H(k, 41), ph2 = 6.283 * H(k, 43);
    const sway = 0.012 * Math.sin(6.283 * t / P1 + ph1) * (0.6 + 0.8 * H(k, 47));            // weight shift, rad about the feet
    const breath = 1 + 0.007 * Math.sin(6.283 * t / P2 + ph2);                                 // chest rise (height only)
    const shift = 0.018 * hh * Math.sin(6.283 * t / (P1 * 1.7) + ph2);                         // a slow step side to side
    let img = im;
    if (name === 'pixel' && st.S.pixel_b && Math.floor(t * 2.4 + H(k, 53) * 2) % 2) img = st.S.pixel_b;   // 2-frame idle
    const w = hh * img.width / img.height;
    g.imageSmoothingEnabled = !PIX.has(name);
    g.save(); g.translate(x + shift, feet);
    if (!PIX.has(name)) { g.rotate(sway); g.scale(1, breath); }
    g.drawImage(img, -w / 2, -hh, w, hh);
    g.restore();
  }
  g.imageSmoothingEnabled = true;
  // ---- the desk in front of their legs: the plate again below the desk's far edge
  const sy = deskY / ph * st.plate.height;
  g.drawImage(st.plate, 0, sy, st.plate.width, st.plate.height - sy, 0, deskY, pw, ph - deskY);
  // ---- the ledger, every line filled in ink
  g.globalCompositeOperation = 'multiply';
  for (const [tex, quad] of st.pages) drawWarped(g, tex, quad);
  if (st.curved) { const [bx, by, bw, bh] = p.ledger.box; g.drawImage(st.curved, bx, by, bw, bh); }
  g.globalCompositeOperation = 'source-over';
  g.restore();
}
