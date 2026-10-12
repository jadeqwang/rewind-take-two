// hilbert_lobby.js (v5 coda, post-credits PC2; docs/revisions/v5/coda.md): the receptionist's POV. Draws the lobby
// plate (one-point perspective, desk across the bottom), an endless queue of Jades receding to the vanishing point
// (the committee sprites first, then Kandinsky-coloured ghosts shrinking to specks), the desk again on top of their
// legs, all under one camera move (the "look up from the desk": a push-out and tilt-up from the ledger).
//   params: plate (image path), sprites (dir with <name>.png + info.json from tools/sectionF/coda/sprites.py),
//     vp [x, y] design px of the vanishing point in plate coords (cover-fitted), deskY (desk top edge, design px),
//     front {x, feet, h}: the protagonist at depth 1 (design px; feet may be below the desk edge),
//     lane: queue axis offset at depth 1 (px from vp.x; the queue converges from there), step (depth step per person),
//     zig / zigN: the first zigN people stand alternately zig px left / right of the lane (at depth 1), tapering,
//     weave / weaveF: beyond them the queue snakes ±weave px (world, at depth 1) with phase step weaveF per person,
//     count, order (committee sprite names, nearest first, after the protagonist), ghostAlpha, jitter (px at depth 1),
//     camScale / camX / camY: keys (layer-local s) of the camera (scale about the design point placed at screen centre),
//     shift: keys 0..1, the Hilbert shuffle (every Jade behind the protagonist steps up one place; optional)
const KAND = ['#F08A24', '#8DB8E8', '#C9A227', '#C23B8E', '#3FA55B'];   // residue orange, pale blue, gold, magenta, green

export async function init(ctx, p, env) {
  const info = await env.loadJSON(p.sprites + '/info.json');
  const S = {};
  for (const n of Object.keys(info)) S[n] = await env.loadImage(`${p.sprites}/${n}.png`);
  // tinted ghosts from the graphite sprite (light grey line art): colour laid over it, source-atop
  const base = S.graphite, tinted = KAND.map(c => {
    const cv = new OffscreenCanvas(base.width, base.height), g = cv.getContext('2d');
    g.drawImage(base, 0, 0); g.globalCompositeOperation = 'source-atop'; g.globalAlpha = 0.62; g.fillStyle = c;
    g.fillRect(0, 0, cv.width, cv.height); return cv;
  });
  const plate = await env.loadImage(p.plate);
  return { S, tinted, plate };
}

function coverRect(im) {
  const s = Math.max(1920 / im.width, 1080 / im.height), w = im.width * s, h = im.height * s;
  return [(1920 - w) / 2, (1080 - h) / 2, w, h];
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, st = env.state, t = env.t;
  const [vx, vy] = p.vp || [960, 518], deskY = p.deskY ?? 853;
  const F = p.front || { x: 1300, feet: 1180, h: 900 };
  const lane = p.lane ?? (F.x - vx), step = p.step ?? 0.6, count = p.count ?? 500;
  const order = p.order || ['watercolor', 'engraved', 'graphite', 'ghost_orange', 'ghost_blue'];
  const sc = env.val(p.camScale, 1), cx = env.val(p.camX, 960), cy = env.val(p.camY, 540), shift = env.val(p.shift, 0);
  const rect = coverRect(st.plate);
  g.save();
  g.translate(960, 540); g.scale(sc, sc); g.translate(-cx, -cy);
  g.drawImage(st.plate, ...rect);
  // the queue, far to near; person k stands at depth d = 1 + (k - shift) * step (k = 0 is the protagonist, who stays)
  const people = [];
  for (let k = count; k >= 0; k--) {
    const d = k === 0 ? 1 : 1 + Math.max(0.0, k - shift) * step;
    const h = F.h / d; if (h < 1.2) continue;
    const jit = k === 0 ? 0 : (env.core.hash(k, 77) - 0.5) * (p.jitter ?? 70);
    const zig = k > 0 && k <= (p.zigN ?? 8) ? (k % 2 ? -1 : 1) * (p.zig ?? 0) * (1 - (k - 1) / (p.zigN ?? 8)) : 0;   // heads poke out left / right
    const kz = p.zigN ?? 8, wv = k > kz ? (p.weave ?? 0) * Math.min(1, (k - kz) / 6) * Math.sin((k - kz) * (p.weaveF ?? 0.55)) : 0;   // the far queue snakes, so each figure shows
    const x = k === 0 ? F.x : vx + (lane + jit + zig + wv) / d, feet = vy + (F.feet - vy) / d;
    const bob = Math.sin(t * 2 * Math.PI * 0.32 + k * 1.7) * 3 / d;
    let im, alpha = 1;
    if (k === 0) im = st.S.jade;
    else if (k <= order.length) { im = st.S[order[k - 1]]; alpha = order[k - 1].startsWith('ghost') ? (p.ghostAlpha ?? 0.8) : 1; }
    else { im = st.tinted[(k - order.length - 1) % st.tinted.length]; alpha = (p.ghostAlpha ?? 0.8) * Math.min(1, 0.55 + 4 / d); }
    people.push({ im, alpha, x, feet: feet + bob, h });
  }
  for (const a of people) {
    const w = a.h * a.im.width / a.im.height;
    g.globalAlpha = a.alpha;
    if (a.h < 4) { g.fillStyle = '#c9a227'; g.fillRect(a.x - 0.6, a.feet - a.h, 1.2, a.h); continue; }
    g.drawImage(a.im, a.x - w / 2, a.feet - a.h, w, a.h);
  }
  g.globalAlpha = 1;
  // the desk in front of them: the plate again, below the desk's top edge
  const [rx, ry, rw, rh] = rect, sy = (deskY - ry) / rh * st.plate.height;
  g.drawImage(st.plate, 0, sy, st.plate.width, st.plate.height - sy, rx, deskY, rw, ry + rh - deskY);
  g.restore();
}
