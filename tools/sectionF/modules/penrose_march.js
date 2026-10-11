// penrose_march.js (section F, F6b 192.34-195.42 and its reuse F7_03): a real Penrose staircase (Escher's Ascending
// and Descending) drawn on the clock face, with every agent marching the same way round (clockwise on screen), one
// step per beat.
//
// The stairs are a true 3D spiral of N steps that rises m units per lap and ends m*(1,1,1) in front of its own start.
// Seen from the isometric "magic" elevation atan(1/sqrt2) = 35.264 deg that offset lies exactly along the view axis,
// so the top step lands one riser below the bottom step and the loop closes. From any other elevation the top of the
// stairs hangs in mid-air over the bottom step: `clunk` starts the shot off-angle and snaps to the magic angle.
// Flight plan (travel order, all ascending): landing R, A along +z (near right), landing B, B along -x (near left),
// landing L, C along -z (far left), landing T, D along +x (far right) back to R. nA - nC = nD - nB = m, riser = m / N.
//   params: cx, cy (design px, centre of the ring), S (px per unit; one tread = 1 unit), n [nA, nB, nC, nD], w (stair
//   width), wall (wall depth under the treads), beats [absolute times of each march step], hop (s), agents (keep 1 of
//   every k steps empty; 0 = one agent per step), clunk {at, from (deg), dur}, stairs (false = agents only), boil

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const R2 = Math.SQRT2, MAGIC = Math.atan(1 / R2);
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const INK = '#151517', PAPER = '#f4ecd8';

function build(p) {
  const [nA, nB, nC, nD] = p.n || [8, 3, 3, 8], w = p.w ?? 1.6, hw = w / 2;
  const m = nA - nC, N = nA + nB + nC + nD + 4, h = m / N, steps = [];
  const add = (x0, x1, z0, z1, flight) => steps.push({ x0, x1, z0, z1, y: steps.length * h, flight, i: steps.length });
  add(-hw, hw, -hw, hw, 'R');
  for (let j = 0; j < nA; j++) add(-hw, hw, hw + j, hw + j + 1, 'A');
  const zB = w + nA; add(-hw, hw, zB - hw, zB + hw, 'B0');
  for (let j = 0; j < nB; j++) add(-hw - j - 1, -hw - j, zB - hw, zB + hw, 'B');
  const xL = -(w + nB); add(xL - hw, xL + hw, zB - hw, zB + hw, 'L');
  for (let j = 0; j < nC; j++) add(xL - hw, xL + hw, zB - hw - j - 1, zB - hw - j, 'C');
  const zT = zB - (w + nC); add(xL - hw, xL + hw, zT - hw, zT + hw, 'T');
  for (let j = 0; j < nD; j++) add(xL + hw + j, xL + hw + j + 1, zT - hw, zT + hw, 'D');
  return { steps, N, h, m };
}

// wobbly ink line (hand-drawn: the pen never runs dead straight); seed keeps it stable, boil changes it on twos
function inkLine(g, a, b, seed, amp = 0.9) {
  const n = Math.max(2, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / 22));
  const nx = -(b[1] - a[1]), ny = b[0] - a[0], L = Math.hypot(nx, ny) || 1;
  g.beginPath(); g.moveTo(a[0], a[1]);
  for (let k = 1; k <= n; k++) {
    const u = k / n, j = k === n ? 0 : (hash(seed + k * 7.3) - 0.5) * 2 * amp;
    g.lineTo(a[0] + (b[0] - a[0]) * u + nx / L * j, a[1] + (b[1] - a[1]) * u + ny / L * j);
  }
  g.stroke();
}

// one face: coloured-pencil fill, pencil tooth, engraved hatching in the face's own direction, ink outline
function face(g, pts, style, seed, boil) {
  g.save();
  g.beginPath(); pts.forEach((q, k) => (k ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.closePath();
  g.fillStyle = style.fill; g.fill();
  g.clip();
  const xs = pts.map(q => q[0]), ys = pts.map(q => q[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  // pencil tooth: short lighter and darker strokes along one slant
  g.lineCap = 'round';
  const nt = Math.round((x1 - x0) * (y1 - y0) / 260);
  for (let k = 0; k < nt; k++) {
    const r = hash(seed * 3.1 + k), r2 = hash(seed * 5.7 + k * 1.3), r3 = hash(seed + k * 2.9);
    const x = x0 + r * (x1 - x0), y = y0 + r2 * (y1 - y0), len = 8 + r3 * 14;
    g.strokeStyle = r3 > 0.5 ? style.light : style.dark; g.globalAlpha = 0.22; g.lineWidth = 1.6;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + len * 0.8, y - len * 0.6); g.stroke();
  }
  // engraved hatching: parallel ink lines following the face (dir = screen vector of the face's hatch direction)
  g.globalAlpha = style.hatchAlpha; g.strokeStyle = INK; g.lineWidth = style.hatchW;
  const [dx, dy] = style.dir, dl = Math.hypot(dx, dy), ux = dx / dl, uy = dy / dl, px = -uy, py = ux;
  const cxm = (x0 + x1) / 2, cym = (y0 + y1) / 2, ext = Math.hypot(x1 - x0, y1 - y0) / 2 + 4;
  for (let o = -ext; o <= ext; o += style.pitch) {
    const jit = (hash(seed + o * 0.37 + boil) - 0.5) * 1.2, br = hash(seed * 1.9 + o);
    if (br < style.skip) continue;                                   // broken lines in the lights
    const ax = cxm + px * (o + jit) - ux * ext, ay = cym + py * (o + jit) - uy * ext;
    inkLine(g, [ax, ay], [ax + ux * 2 * ext, ay + uy * 2 * ext], seed + o + boil, 0.5);
  }
  g.restore();
  g.globalAlpha = 1; g.strokeStyle = INK; g.lineWidth = style.edge; g.lineJoin = 'round'; g.lineCap = 'round';
  for (let k = 0; k < pts.length; k++) inkLine(g, pts[k], pts[(k + 1) % pts.length], seed * 2.3 + k * 11 + boil, 0.8);
}

// a TIME VARIANCE agent, pure ink: black suit, white shirt and tie, shades. (x, y) = feet, H = height in px,
// front = walking toward the viewer, dir = +1 walks screen-right, stride -1..1 (leg split), all deterministic.
function agent(g, x, y, H, front, dir, stride) {
  const u = H / 100;
  g.save(); g.translate(x, y); g.scale(dir * u, u);
  const leg = (sx, lift) => { g.beginPath(); g.moveTo(-5, -46); g.lineTo(5, -46); g.lineTo(sx + 5, -lift); g.lineTo(sx - 4, -lift); g.closePath(); };
  const body = () => {
    leg(-4 + stride * 9, stride > 0 ? 0 : -stride * 4); g.fill(); g.stroke();
    leg(4 - stride * 9, stride < 0 ? 0 : stride * 4); g.fill(); g.stroke();
    g.beginPath(); g.moveTo(-13, -78); g.lineTo(13, -78); g.lineTo(10, -42); g.lineTo(-10, -42); g.closePath(); g.fill(); g.stroke();   // jacket
    for (const s of [-1, 1]) {                                                                                                       // arms
      g.beginPath(); g.moveTo(s * 12, -77); g.lineTo(s * 17, -74); g.lineTo(s * 15 - s * stride * 6, -46); g.lineTo(s * 10 - s * stride * 6, -47); g.closePath();
      g.fill(); g.stroke();
    }
    g.beginPath(); g.ellipse(0, -89, 8, 10, 0, 0, Math.PI * 2); g.fill(); g.stroke();                                                  // head
  };
  // engraver's halo: a band of paper round the silhouette so the black figure reads against hatching
  g.fillStyle = PAPER; g.strokeStyle = PAPER; g.lineWidth = 7; g.lineJoin = 'round'; body();
  g.fillStyle = INK; g.strokeStyle = INK; g.lineWidth = 1.5; body();
  g.fillStyle = PAPER;
  if (front) {
    g.beginPath(); g.ellipse(0, -87, 6.4, 8, 0, 0, Math.PI * 2); g.fill();                    // face
    g.beginPath(); g.moveTo(-5, -78); g.lineTo(5, -78); g.lineTo(0, -60); g.closePath(); g.fill();   // shirt
    g.fillStyle = INK;
    g.fillRect(-6.6, -91, 13.2, 4.2);                                                        // shades
    g.beginPath(); g.moveTo(-1.6, -78); g.lineTo(1.6, -78); g.lineTo(0.9, -62); g.lineTo(-0.9, -62); g.closePath(); g.fill();   // tie
    g.beginPath(); g.ellipse(0, -95.5, 7.6, 4.6, 0, Math.PI, 0); g.fill();                    // hair
    g.strokeStyle = PAPER; g.lineWidth = 0.9; g.globalAlpha = 0.8;                            // white-line lapels, trouser crease
    g.beginPath(); g.moveTo(-5, -78); g.lineTo(-7, -66); g.moveTo(5, -78); g.lineTo(7, -66);
    g.moveTo(-11.5, -72); g.lineTo(-9.5, -48); g.moveTo(11.5, -72); g.lineTo(9.5, -48);
    g.moveTo(0, -42); g.lineTo(0, -30); g.stroke(); g.globalAlpha = 1;
  } else {
    g.fillRect(-5.5, -80.5, 11, 2.2);                                                        // collar
    g.strokeStyle = PAPER; g.lineWidth = 1; g.globalAlpha = 0.75;                           // white-line seam on the back
    g.beginPath(); g.moveTo(0, -76); g.lineTo(0, -45); g.moveTo(-11.5, -72); g.lineTo(-9.5, -48); g.moveTo(11.5, -72); g.lineTo(9.5, -48);
    g.moveTo(0, -42); g.lineTo(0, -30); g.stroke(); g.globalAlpha = 1;
  }
  g.restore();
}

// v3 restyle: ink-engraved agent sprites (tools/sectionF/agent_sprites.py), all drawn walking screen-right; flipped
// for the flights that run screen-left. params.sprites = directory with front_<k>.png, back_<k>.png and info.json
export async function init(ctx, p, env) {
  if (!p.sprites) return null;
  const info = await env.loadJSON(p.sprites + '/info.json');
  const load = async pre => Promise.all(Object.keys(info).filter(n => n.startsWith(pre)).sort().map(n => env.loadImage(`${p.sprites}/${n}.png`)));
  return { front: await load('front_'), back: await load('back_') };
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, t = env.t;
  const absT = (_, x) => (typeof x === 'number' ? x : env.T.time(x));     // times in params are absolute song times
  const { steps, N, h } = build(p);
  let S = 1; const wall = p.wall ?? 1.1;
  // elevation: off-angle before the clunk (the top of the stairs hangs over the bottom step), magic after
  let el = MAGIC;
  if (p.clunk) {
    const at = absT(env, p.clunk.at), dur = p.clunk.dur ?? 0.2, from = (p.clunk.from ?? 27) * Math.PI / 180;
    if (t < at) { const u = clamp(1 - (at - t) / dur); el = from + (MAGIC - from) * u * u * u; }
    else el = MAGIC + (MAGIC - from) * 0.22 * Math.exp(-(t - at) / 0.05) * Math.cos((t - at) * 60);   // overshoot, settle
  }
  const proj0 = (x, y, z, e) => [S * (x - z) / R2, S * ((x + z) * Math.sin(e) / R2 - y * Math.cos(e))];
  // centre the ring on (cx, cy) at the magic angle (the centre does not move when the angle changes)
  let bx0 = 1e9, bx1 = -1e9, by0 = 1e9, by1 = -1e9;
  for (const s of steps) for (const [x, z] of [[s.x0, s.z0], [s.x1, s.z0], [s.x1, s.z1], [s.x0, s.z1]]) {
    const q = proj0(x, s.y, z, MAGIC); bx0 = Math.min(bx0, q[0]); bx1 = Math.max(bx1, q[0]); by0 = Math.min(by0, q[1]); by1 = Math.max(by1, q[1]);
  }
  if (S === 1) {                                                   // first pass measured the ring at 1 px per unit
    S = p.S ?? (p.width ?? 500) / (bx1 - bx0);
    bx0 *= S; bx1 *= S; by0 *= S; by1 *= S;
  }
  // pivot for the angle change: the centre of the lap in 3D, so the figure tips about its middle
  const mid = steps[Math.floor(N / 2)], pc = proj0(mid.x0, mid.y, mid.z0, el), pm = proj0(mid.x0, mid.y, mid.z0, MAGIC);
  const ox = (p.cx ?? 960) - (bx0 + bx1) / 2 + (pm[0] - pc[0]), oy = (p.cy ?? 540) - (by0 + by1) / 2 + (pm[1] - pc[1]);
  const P = (x, y, z) => { const q = proj0(x, y, z, el); return [q[0] + ox, q[1] + oy]; };
  const boil = p.boil === false ? 0 : Math.floor(t * 12) % 3 * 17.7;

  if (p.stairs !== false) {
    const TOP = { fill: '#f6eed8', light: '#fffaf0', dark: '#e3cf9a', dir: [1, 0.577], pitch: 7.5, hatchW: 0.9, hatchAlpha: 0.4, skip: 0.45, edge: 2.2 };
    const GOLD = { fill: '#dcab3d', light: '#f0cd6a', dark: '#b07f1f', dir: [0, 1], pitch: 5.2, hatchW: 1.0, hatchAlpha: 0.62, skip: 0.1, edge: 2.2 };
    const BLUE = { fill: '#4a5fb4', light: '#7f93dc', dark: '#27357e', dir: [0, 1], pitch: 4.2, hatchW: 1.1, hatchAlpha: 0.78, skip: 0.04, edge: 2.2 };
    const SHADE = { fill: '#cdb98a', light: '#e3cf9a', dark: '#8d7a4c', dir: [1, -0.577], pitch: 3.4, hatchW: 1.0, hatchAlpha: 0.8, skip: 0, edge: 0.01 };
    const far = steps.filter(s => 'CTD'.includes(s.flight[0])), near = steps.filter(s => !'CTD'.includes(s.flight[0]));
    const depth = s => s.x0 + s.x1 + s.z0 + s.z1;
    for (const grp of [far, near]) {
      for (const s of [...grp].sort((a, b) => depth(a) - depth(b))) {
        const yb = s.y - wall, sd = s.i * 13.37;
        // +x face (right-hand wall / riser of the flights climbing toward -x); hidden inside flight D
        if (s.flight !== 'D') face(g, [P(s.x1, s.y, s.z0), P(s.x1, s.y, s.z1), P(s.x1, yb, s.z1), P(s.x1, yb, s.z0)], GOLD, sd + 1, boil);
        // +z face (left-hand wall / riser of the flights climbing toward -z); hidden inside flight A
        if (s.flight !== 'A' && s.flight !== 'R') face(g, [P(s.x0, s.y, s.z1), P(s.x1, s.y, s.z1), P(s.x1, yb, s.z1), P(s.x0, yb, s.z1)], BLUE, sd + 2, boil);
        face(g, [P(s.x0, s.y, s.z0), P(s.x1, s.y, s.z0), P(s.x1, s.y, s.z1), P(s.x0, s.y, s.z1)], TOP, sd + 3, boil);
        // flights A and D climb toward the viewer, so their risers face away: a hatched shadow under the lip of the
        // next step up keeps the level change readable
        const sh = 2 * h + (p.shade ?? 0.3);      // the next step up hides 2h of this tread at the magic angle
        if (s.flight === 'A' || s.flight === 'R') face(g, [P(s.x0, s.y, s.z1 - sh), P(s.x1, s.y, s.z1 - sh), P(s.x1, s.y, s.z1), P(s.x0, s.y, s.z1)], SHADE, sd + 4, boil);
        if (s.flight === 'D' || s.flight === 'T') face(g, [P(s.x1 - sh, s.y, s.z0), P(s.x1, s.y, s.z0), P(s.x1, s.y, s.z1), P(s.x1 - sh, s.y, s.z1)], SHADE, sd + 4, boil);
      }
    }
  }

  // ---- the march: one step per beat, everyone the same way round ------------------------------------------------
  const beats = (p.beats || []).map(b => absT(env, b)), hop = p.hop ?? 0.2;
  let k = 0, u = 1;
  for (let j = 0; j < beats.length; j++) if (t >= beats[j]) { k = j + 1; u = clamp((t - beats[j]) / hop); }
  const e = 1 - (1 - u) ** 3, pos = k - 1 + e;                     // steps climbed so far (fractional during a hop)
  const centre = s => P((s.x0 + s.x1) / 2, s.y, (s.z0 + s.z1) / 2);
  const every = p.agents ?? 3, H = (p.agentH ?? 1.45) * S, list = [];
  for (let a = 0; a < N; a++) {
    if (every && a % every === every - 1) continue;                // a gap now and then, so the file reads as a file
    const f = ((a + pos) % N + N) % N, i0 = Math.floor(f), fr = f - i0, s0 = steps[i0], s1 = steps[(i0 + 1) % N];
    const c0 = centre(s0), c1 = centre(s1);
    const x = c0[0] + (c1[0] - c0[0]) * fr, y = c0[1] + (c1[1] - c0[1]) * fr - Math.sin(Math.PI * fr) * 0.16 * S;
    const s = fr > 0.5 ? s1 : s0, fl = s.flight[0];
    // facing by flight: A (+z) comes toward the viewer going screen-left, D (+x) toward the viewer going right,
    // B (-x) and C (-z) walk away (back view)
    const front = fl === 'A' || fl === 'R' || fl === 'D' || fl === 'T';
    const dir = (fl === 'D' || fl === 'C' || fl === 'T' || fl === 'L') ? 1 : -1;
    const stride = (fr > 0 ? 0.22 + 0.78 * Math.sin(Math.PI * fr) : 0.22) * ((a + k) % 2 ? 1 : -1);
    const frame = a + 2 * k + (u < 1 ? Math.floor(u * 2) : 0);        // two walk drawings per step
    list.push({ x, y, front, dir, stride, frame, a });
  }
  list.sort((a, b) => a.y - b.y);
  const spr = env.state;
  for (const a of list) {
    if (!spr) { agent(g, a.x, a.y, H, a.front, a.dir, a.stride); continue; }
    const set = a.front ? spr.front : spr.back, im = set[((a.frame % set.length) + set.length) % set.length];
    const h = H * 1.08, w = h * im.width / im.height;                 // sprite height includes the paper halo
    g.save(); g.translate(a.x, a.y); g.scale(a.dir, 1);
    g.drawImage(im, -w / 2, -h, w, h);
    g.restore();
  }
}
