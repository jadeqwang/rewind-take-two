// hilbert_door.js (v5 post-credits PC1; docs/revisions/v5/build.md): Jade's POV at the Hilbert Hotel's front door.
// Built in the engine so the door moves the physically right way (Jade: "hotel door should open in the correct way"):
// the leaf (media/shots/PC/door_leaf.png, its glass at partial alpha, the gold crest opaque) is hinged on its LEFT edge;
// the doorman's white glove comes in from the right, takes the handle on the right stile and pushes the door open INTO
// the lobby, staying on the handle as it swings. The leaf is drawn in vertical strips under a true perspective rotation
// about the hinge (each column foreshortens by its depth), behind the fixed frame (door_frame.png, the leaf's opening
// cut out) and in front of the open doorway (doorway.jpg). The spring bell hangs inside and is set swinging as the door
// starts to move (the bell rings on the beat after the counter's last tick). Then the camera glides through, the
// lobby moving less than the frame (parallax).
//   params: door, doorway, leaf, bell, glove (images), geom (door_geom.json from tools/sectionF/coda/prep_pc.py),
//     handIn [t0, t1] (the glove slides in and takes the handle), swing [t0, t1] (0 -> angle deg, ease), angle,
//     glide [t0, t1], glideScale (frame scale at the end of the glide), focal (px, default 1700)
const ease = x => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const easeOut = x => (x <= 0 ? 0 : x >= 1 ? 1 : 1 - (1 - x) ** 3);

export async function init(ctx, p, env) {
  const [frame, doorway, leaf, bell, glove, geom] = await Promise.all([
    env.loadImage(p.frame || p.door.replace('door.jpg', 'door_frame.png')), env.loadImage(p.doorway), env.loadImage(p.leaf),
    env.loadImage(p.bell), env.loadImage(p.glove), env.loadJSON(p.geom)]);
  return { frame, doorway, leaf, bell, glove, geom };
}

function swingAngle(lt, p) {
  const [a, b] = p.swing;
  if (lt <= a) return 0;
  const x = Math.min(1, (lt - a) / (b - a));
  // a push: quick start (the shove), then it coasts to its stop
  return (p.angle ?? 74) * Math.PI / 180 * (1 - (1 - x) ** 2.2);
}

export function draw(lt, env) {
  const g = env.ctx, p = env.params, S = env.state, G = S.geom;
  const f = p.focal ?? 1700, cx = 960, cy = 540;
  const th = swingAngle(lt, p);
  const [gl0, gl1] = p.glide, gx = Math.min(1, Math.max(0, (lt - gl0) / (gl1 - gl0)));
  const gk = gx * gx * (3 - 2 * gx) * 0.6 + gx * gx * 0.4;          // eases in, keeps moving at the cut
  const sF = 1 + ((p.glideScale ?? 2.6) - 1) * gk, sI = 1 + (sF - 1) * 0.55;   // frame / lobby (parallax)
  const [lx0, ly0, lx1, ly1] = G.leaf, hinge = G.hinge;
  const pivot = [(lx0 + lx1) / 2, 600];
  const cam = s => { g.translate(pivot[0], pivot[1]); g.scale(s, s); g.translate(-pivot[0], -pivot[1]); };
  // ---- the lobby through the doorway
  g.save(); cam(sI); g.drawImage(S.doorway, 0, 0, 1920, 1080);
  // warm light spilling out as the door opens
  const open = Math.sin(th);
  if (open > 0) {
    const rg = g.createRadialGradient(pivot[0], 560, 40, pivot[0], 560, 700);
    rg.addColorStop(0, `rgba(255,214,150,${0.32 * open})`); rg.addColorStop(1, 'rgba(255,214,150,0)');
    g.globalCompositeOperation = 'lighter'; g.fillStyle = rg; g.fillRect(lx0, ly0, lx1 - lx0, 1080 - ly0); g.globalCompositeOperation = 'source-over';
  }
  g.restore();
  g.save(); cam(sF);
  // ---- the bell on its spring (inside, at the top of the doorway), set swinging when the door starts to move
  const tb = p.swing[0], [bx0, by0, bx1, by1] = G.bell, [btx, bty] = G.bellTop, pad = 30;
  let ang = 0;
  if (lt > tb) { const u = lt - tb; ang = 0.30 * Math.exp(-u / 0.55) * Math.sin(2 * Math.PI * 3.1 * u) + 0.08 * Math.exp(-u / 0.25) * Math.sin(2 * Math.PI * 7.3 * u); }
  g.strokeStyle = '#6b5326'; g.lineWidth = 3; g.beginPath(); g.moveTo(btx, ly0 + 18); g.lineTo(btx, bty + 4); g.stroke();   // its bracket rod
  g.save(); g.translate(btx, bty); g.rotate(ang);
  g.drawImage(S.bell, bx0 - pad - btx, by0 - pad - bty, bx1 - bx0 + 2 * pad, by1 - by0 + 2 * pad);
  g.restore();
  // ---- the leaf, rotated about its left (hinge) edge, swinging away from us into the lobby
  const W = S.leaf.width, H = S.leaf.height, N = 140, c = Math.cos(th), s = Math.sin(th);
  const proj = (x, y) => {                                  // design point on the closed leaf -> screen, depth
    const dX = x - hinge, z = 1 + dX * s / f, X = hinge - cx + dX * c;
    return [cx + X / z, cy + (y - cy) / z, z];
  };
  // shade the leaf a touch as it turns away from the light
  for (let i = 0; i < N; i++) {
    const u0 = i / N, u1 = (i + 1) / N, xa = lx0 + u0 * (lx1 - lx0), xb = lx0 + u1 * (lx1 - lx0);
    const A = proj(xa, ly0), B = proj(xb, ly0), Ab = proj(xa, ly1);
    const top = Math.min(A[1], B[1]), bot = Math.max(Ab[1], proj(xb, ly1)[1]);
    const left = Math.min(A[0], B[0]), w = Math.abs(B[0] - A[0]) + 0.7;
    g.drawImage(S.leaf, u0 * W, 0, (u1 - u0) * W + 0.5, H, left, top, w, bot - top);
    // the door goes on below the frame's bottom edge: continue its last rows down to y 1600 (else a gap opens under it)
    const bot2 = Math.max(proj(xa, 1600)[1], proj(xb, 1600)[1]);
    g.drawImage(S.leaf, u0 * W, H - 3, (u1 - u0) * W + 0.5, 3, left, bot - 1, w, bot2 - bot + 1);
  }
  if (th > 0) {                                             // darken the turned leaf (it faces away from the street light)
    const L = proj(lx0, ly0), R = proj(lx1, ly0), Rb = proj(lx1, ly1);
    g.fillStyle = `rgba(30,20,12,${0.35 * s})`;
    g.beginPath(); g.moveTo(L[0], L[1]); g.lineTo(R[0], R[1]); g.lineTo(Rb[0], Rb[1]); g.lineTo(L[0], proj(lx0, ly1)[1]); g.closePath(); g.fill();
  }
  // ---- the fixed frame (arch, jambs, stained-glass sidelights) over the leaf's edges
  g.drawImage(S.frame, 0, 0, 1920, 1080);
  // ---- the glove: slides in from the right, takes the handle, then rides it as the door swings
  const gm = G.glove, [hx, hy] = G.handle;
  const [px, py, pz] = proj(hx, hy);
  const k = easeOut((lt - p.handIn[0]) / (p.handIn[1] - p.handIn[0]));
  if (lt > p.handIn[0] - 0.01) {
    const press = lt > tb - 0.08 && lt < tb ? -4 * Math.sin(Math.PI * (lt - tb + 0.08) / 0.08) : 0;   // the push before it gives
    const slide = (1 - k) * 760, lift = (1 - k) * 60;
    const sc = 1 / pz, gw = gm.size[0], gh = gm.size[1], split = gm.split;
    const fx0 = px + slide + press - gm.grip[0] * sc, fy0 = py + lift - gm.grip[1] * sc;
    // fist + cuff (left of `split`) at the handle's depth
    g.drawImage(S.glove, 0, 0, split, gh, fx0, fy0, split * sc, gh * sc);
    // the sleeve stretches back to where the doorman stands (off the right edge)
    const restX = hx - gm.grip[0] + split + slide;                // where the sleeve starts when the door is shut
    const rightEnd = hx - gm.grip[0] + gw + slide + 40;
    const sx0 = fx0 + split * sc - 1, stretch = Math.max(0.2, (rightEnd - sx0) / (rightEnd - restX));
    g.drawImage(S.glove, split, 0, gw - split, gh, sx0, fy0 + (1 - sc) * 0, (gw - split) * stretch, gh * sc);
  }
  g.restore();
}
