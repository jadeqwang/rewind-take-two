// v9 round 3: D2 + D3 (23.16-28.40) as one three.js scene: Jade driving, seen from the passenger seat, her head
// turned to the driver's door mirror; the mirror is a real object (housing, arm, flat glass) and its glass shows a
// REAL reflection, rendered through a virtual camera (the passenger's eye mirrored in the glass plane, with an off-axis
// frustum whose window is the glass rectangle). The geometry and timing live in rig.js (shared with tracks.mjs).
//
// Rendered offline (render/three/tools/capture.mjs, scene=../../../tools/v9/d23/scene) as a plain night render; the
// film's look comes from the section A engrave pass (tools/engrave), with Jade's matte passed in (pass=matte), so she
// stays in colour like every other section A take. Lettering (billboard lyric, plate, glass etch) is NOT rendered here:
// the engine pins it onto the tracks from tracks.mjs (reading forward: Jade's cheat).
//
// params: pass 'beauty' | 'matte' | 'guide' (mannequin, no plate), plate (url of Jade's RGBA plate), t = song time
// offset: draw(lt) renders song time S0 + lt.
import * as THREE from 'three';
import * as R from './rig_r7.js';

const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);

export function createScene() {
  const meta = { name: 'd23_mirror', duration: R.S2 - R.S0, fps: 24, width: R.W, height: R.H };
  let renderer, params, scene, cam, mirrorCam, mainRT, mirrorRT, blit, blitScene, quadCam, glass, card, cardMatte, matteScene;
  const dyn = {};   // moving things

  // ------------------------------------------------------------------ materials
  const lam = (c, extra = {}) => new THREE.MeshLambertMaterial({ color: c, ...extra });
  const phong = (c, sh = 40, spec = 0x444444, extra = {}) => new THREE.MeshPhongMaterial({ color: c, shininess: sh, specular: spec, ...extra });
  const glow = (c) => new THREE.MeshBasicMaterial({ color: c });

  // ------------------------------------------------------------------ geometry helpers
  function box(x0, y0, z0, x1, y1, z1, mat, parent) {
    const g = new THREE.BoxGeometry(Math.abs(x1 - x0), Math.abs(y1 - y0), Math.abs(z1 - z0));
    const m = new THREE.Mesh(g, mat); m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
    (parent || scene).add(m); return m;
  }
  // a beam of square-ish section w x d between two points (d along `side`)
  function beam(a, b, w, d, mat, parent, side = [0, 0, 1]) {
    const A = V(a), B = V(b), len = A.distanceTo(B);
    const g = new THREE.BoxGeometry(w, len, d);
    const m = new THREE.Mesh(g, mat);
    const yax = B.clone().sub(A).normalize();
    let zax = V(side).sub(yax.clone().multiplyScalar(V(side).dot(yax))); if (zax.length() < 1e-4) zax = new THREE.Vector3(1, 0, 0); zax.normalize();
    const xax = new THREE.Vector3().crossVectors(yax, zax);
    m.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(xax, yax, zax));
    m.position.copy(A).add(B).multiplyScalar(0.5);
    (parent || scene).add(m); return m;
  }
  function quad(p0, p1, p2, p3, mat, parent) {   // CCW seen from the front
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute([...p0, ...p1, ...p2, ...p0, ...p2, ...p3], 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1], 2));
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, mat); (parent || scene).add(m); return m;
  }
  function canvasTex(w, h, fn, srgb = true) {
    const c = new OffscreenCanvas(w, h), g = c.getContext('2d'); fn(g, w, h);
    const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
  }
  // deterministic hash
  const hh = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

  // value-noise fbm canvas (deterministic), for the hand variation the engrave pass needs to draw from
  function fbmCanvas(w, h, sx, sy, oct, seed, fn) {
    const c = new OffscreenCanvas(w, h), g = c.getContext('2d'), img = g.createImageData(w, h);
    const N = 64, grid = new Float32Array(N * N); for (let i = 0; i < N * N; i++) grid[i] = hh(i * 1.37 + seed * 91.1);
    const vn = (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi; const ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
      const G = (i, j) => grid[(((j % N) + N) % N) * N + (((i % N) + N) % N)];
      return (G(xi, yi) * (1 - ux) + G(xi + 1, yi) * ux) * (1 - uy) + (G(xi, yi + 1) * (1 - ux) + G(xi + 1, yi + 1) * ux) * uy; };
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      let v = 0, a = 0.5, f = 1; for (let o = 0; o < oct; o++) { v += a * vn(x / w * sx * f, y / h * sy * f); a *= 0.5; f *= 2.03; }
      const [r, gg, b] = fn(v, x / w, y / h); const k = (y * w + x) * 4; img.data[k] = r; img.data[k + 1] = gg; img.data[k + 2] = b; img.data[k + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }

  // ------------------------------------------------------------------ build
  async function init(r, p = {}) {
    renderer = r; params = { pass: 'beauty', plate: '/media/shots/D23/r7_plate_rgba.png', plateMatte: '/media/shots/D23/r7_plate_jade.png', housing: 'drawn', ...p };   // round 7: the r7 plate (camera moved), the drawn housing card
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    cam = new THREE.PerspectiveCamera(40, R.W / R.H, 0.05, 6000);
    cam.matrixAutoUpdate = false;
    mirrorCam = new THREE.PerspectiveCamera(30, 1, 0.1, 6000);
    mirrorCam.matrixAutoUpdate = false;
    mainRT = new THREE.WebGLRenderTarget(R.W, R.H, { samples: 4, type: THREE.HalfFloatType });
    const MW = 2048, MH = Math.round(MW * R.MIRROR.h / R.MIRROR.w);
    mirrorRT = new THREE.WebGLRenderTarget(MW, MH, { samples: 4, type: THREE.HalfFloatType });
    blit = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: null } }, depthTest: false, depthWrite: false,
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: `uniform sampler2D tSrc; varying vec2 vUv;
        vec3 enc(vec3 c){ c = clamp(c, 0.0, 1.0); return mix(c * 12.92, 1.055 * pow(c, vec3(1.0/2.4)) - 0.055, step(0.0031308, c)); }
        void main(){ gl_FragColor = vec4(enc(texture2D(tSrc, vUv).rgb), 1.0); }`,
    });
    blitScene = new THREE.Scene(); { const q = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), blit); q.frustumCulled = false; blitScene.add(q); }
    quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

    buildSky(); buildRoad(); buildCity(); buildBillboard(); buildSedan(); await buildSedanCard(); buildTraffic(); buildCar(); buildMirror(); buildLights();
    if (params.housing === 'drawn' && params.pass !== 'housingguide') await buildHousingCard();
    if (params.pass === 'housingguide') housingGuide();
    if (params.pass === 'guide' || params.pass === 'guidekey') { buildMannequin(); if (params.pass === 'guidekey') keyOutside(); }
    else await buildCard();
    if (params.pass === 'billmask') maskMaterials();
    if (params.pass === 'housingguide' && card) scene.remove(card);   // round 7: the cap alone on green
    return meta;
  }

  // ---- sky: dark dome, a little city glow at the horizon, a few stars
  function buildSky() {
    // night sky: dark, a little city glow at the horizon, long streaky clouds lit from below
    const tex = fbmCanvas(2048, 1024, 10, 40, 5, 3, (v, u, y) => {
      const el = (0.5 - y) * 2;                      // +1 zenith .. 0 horizon .. -1 nadir
      let base = el > 0 ? 8 + 46 * Math.exp(-el * 7) : 6;
      const cl = Math.max(0, v - 0.42) * 2.4 * Math.exp(-Math.abs(el - 0.15) * 3) * (el > 0 ? 1 : 0);
      base += cl * 120;
      return [base * 0.92, base * 0.95, base * 1.08];
    });
    const sky = new THREE.Mesh(new THREE.SphereGeometry(5000, 48, 32), new THREE.MeshBasicMaterial({ map: tex, side: THREE.BackSide, depthWrite: false, fog: false }));
    sky.renderOrder = -10; scene.add(sky); dyn.sky = sky;
    // stars
    const pos = [];
    for (let i = 0; i < 500; i++) {
      const az = hh(i) * Math.PI * 2, el = 0.08 + Math.pow(hh(i + 99), 1.6) * 1.3;
      pos.push(4500 * Math.cos(el) * Math.sin(az), 4500 * Math.sin(el), 4500 * Math.cos(el) * Math.cos(az));
    }
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    const stars = new THREE.Points(sg, new THREE.PointsMaterial({ color: 0x9aa0b0, size: 2.2, sizeAttenuation: false }));
    scene.add(stars);
  }

  // ---- Lake Shore Drive: our three southbound lanes, the median wall with lamps, the northbound lanes, the lakefront
  const LAMP_DZ = 46;
  function buildRoad() {
    const asphalt = canvasTex(512, 512, (g, w, h) => {
      g.fillStyle = '#2c2c2e'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 9000; i++) { const v = 30 + hh(i) * 40; g.fillStyle = `rgb(${v},${v},${v + 2})`; g.fillRect(hh(i + 1) * w, hh(i + 2) * h, 2, 2); }
    });
    asphalt.wrapS = asphalt.wrapT = THREE.RepeatWrapping; asphalt.repeat.set(40, 400);
    const road = new THREE.Mesh(new THREE.PlaneGeometry(90, 1600), lam(0xffffff, { map: asphalt }));
    road.rotation.x = -Math.PI / 2; road.position.set(-15, 0, 200); scene.add(road); dyn.road = road; dyn.asphalt = asphalt;
    // lakefront park (dark grass) and the lake beyond, far left; the right shoulder wall and the city side
    const park = new THREE.Mesh(new THREE.PlaneGeometry(300, 3000), lam(0x1b1d1b)); park.rotation.x = -Math.PI / 2; park.position.set(-204, 0.02, 600); scene.add(park);   // round 7: wider (the billboard stands on it at x -303)
    const lake = new THREE.Mesh(new THREE.PlaneGeometry(4000, 9000), phong(0x0a0c12, 90, 0x666666)); lake.rotation.x = -Math.PI / 2; lake.position.set(-2114, -0.4, 1500); scene.add(lake);
    const shoulder = new THREE.Mesh(new THREE.PlaneGeometry(400, 3000), lam(0x1a1a1a)); shoulder.rotation.x = -Math.PI / 2; shoulder.position.set(226, -0.01, 600); scene.add(shoulder);
    // lane dashes (instanced; they stream back) and solid edge lines
    const dashG = new THREE.BoxGeometry(0.14, 0.01, 3.0), dashM = glow(0xbdbdb6);
    const lines = [-1.8, -5.4, -9.0, -18.2, -21.8];   // round 7: a fourth southbound lane (line -9.0); the northbound lines move 3.6 m left too
    const N = 60;
    dyn.dashes = new THREE.InstancedMesh(dashG, dashM, lines.length * N); dyn.dashes.frustumCulled = false; scene.add(dyn.dashes);
    dyn.dashLines = lines; dyn.dashN = N;
    box(1.75 + 3.6, 0.005, -800, 1.9 + 3.6, 0.012, 1600, dashM);       // right edge line
    box(-12.7, 0.005, -800, -12.56, 0.012, 1600, dashM);                // left edge line (median side), round 7: 3.6 m further left
    box(-14.05, 0.005, -800, -13.9, 0.012, 1600, dashM);
    // the median: a concrete Jersey wall (sloped faces) running the whole way
    const wallM = lam(0x5a5a57);
    const wall = new THREE.Group(); scene.add(wall);
    const wg = new THREE.BufferGeometry();
    const prof = [[-12.85, 0], [-12.95, 0.25], [-13.22, 0.82], [-13.58, 0.82], [-13.85, 0.25], [-13.95, 0]];   // round 7: 3.6 m further left
    const pos = [];
    for (let i = 0; i < prof.length - 1; i++) {
      const [x0, y0] = prof[i], [x1, y1] = prof[i + 1];
      pos.push(x0, y0, -800, x1, y1, -800, x1, y1, 1600, x0, y0, -800, x1, y1, 1600, x0, y0, 1600);
    }
    wg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); wg.computeVertexNormals();
    wall.add(new THREE.Mesh(wg, new THREE.MeshLambertMaterial({ color: 0x5a5a57, side: THREE.DoubleSide })));
    // lamp posts on the median (double-armed) and on the right shoulder: a group that streams back
    dyn.lamps = new THREE.Group(); scene.add(dyn.lamps);
    const poleM = lam(0x55555a), headM = glow(0xfff6dc);
    dyn.lampHeads = [];
    for (let k = -8; k < 32; k++) {
      const z = k * LAMP_DZ;
      const g = new THREE.Group(); g.position.z = z; dyn.lamps.add(g);
      beam([-13.4, 0.8, 0], [-13.4, 10.5, 0], 0.22, 0.22, poleM, g);
      beam([-13.4, 10.3, 0], [-11.2, 10.9, 0], 0.12, 0.12, poleM, g);
      beam([-13.4, 10.3, 0], [-15.6, 10.9, 0], 0.12, 0.12, poleM, g);
      for (const hx of [-11.1, -15.7]) {
        box(hx - 0.35, 10.72, -0.18, hx + 0.35, 10.92, 0.18, poleM, g);
        const h = box(hx - 0.28, 10.64, -0.13, hx + 0.28, 10.72, 0.13, headM, g); dyn.lampHeads.push(h);
      }
      const g2 = new THREE.Group(); g2.position.z = z + LAMP_DZ / 2; dyn.lamps.add(g2);
      beam([9.4, 0, 0], [9.4, 10.5, 0], 0.22, 0.22, poleM, g2);
      beam([9.4, 10.3, 0], [7.2, 10.9, 0], 0.12, 0.12, poleM, g2);
      box(6.75, 10.72, -0.18, 7.45, 10.92, 0.18, poleM, g2);
      box(6.82, 10.64, -0.13, 7.38, 10.72, 0.13, headM, g2);
    }
    // starburst glows on every lamp (the film draws lights as white engraved starbursts)
    const burst = canvasTex(256, 256, (g, w, h) => {
      const c = w / 2; const gr = g.createRadialGradient(c, c, 0, c, c, c);
      gr.addColorStop(0, 'rgba(255,250,235,1)'); gr.addColorStop(0.08, 'rgba(255,248,230,0.9)'); gr.addColorStop(0.25, 'rgba(255,240,210,0.18)'); gr.addColorStop(1, 'rgba(255,240,210,0)');
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.strokeStyle = 'rgba(255,250,235,0.85)'; g.lineCap = 'round';
      for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 + 0.1, L = c * (i % 2 ? 0.55 : 0.95); g.lineWidth = i % 2 ? 1.5 : 2.5; g.beginPath(); g.moveTo(c, c); g.lineTo(c + Math.cos(a) * L, c + Math.sin(a) * L); g.stroke(); }
    });
    dyn.burstTex = burst;
    const sm = new THREE.SpriteMaterial({ map: burst, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true });
    for (const g of dyn.lamps.children) for (const h of g.children) if (h.material === headM) {
      const s = new THREE.Sprite(sm); s.scale.set(3.2, 3.2, 1); s.position.copy(h.position).add(new THREE.Vector3(0, -0.15, 0)); g.add(s); (dyn.bursts = dyn.bursts || []).push(s);
    }
    // a lakefront path fence and a few trees on the park strip
    const treeM = lam(0x111311);
    for (let k = 0; k < 70; k++) {
      const x = -58 - hh(k) * 30, z = -300 + k * 23 + hh(k + 5) * 10, hgt = 5 + hh(k + 9) * 5;
      if (z > -60 && z < 450) continue;   // a clearing in front of the billboard (round 4: 60-330; round 7: wider, its sight line moved)
      const t = new THREE.Mesh(new THREE.SphereGeometry(2.4 + hh(k + 3) * 1.2, 10, 8), treeM); t.position.set(x, hgt, z); t.scale.y = 1.25;
      const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.25, hgt, 6), treeM); tr.position.set(x, hgt / 2, z);
      dyn.lamps.add(t); dyn.lamps.add(tr);
    }
  }

  // ---- the city: the downtown skyline far behind (north), a row of lakefront towers on the right
  function buildCity() {
    const winTex = (seed) => canvasTex(256, 512, (g, w, h) => {
      g.fillStyle = '#121216'; g.fillRect(0, 0, w, h);
      for (let y = 6; y < h; y += 12) for (let x = 6; x < w; x += 10) {
        const r = hh(seed + x * 0.37 + y * 1.91);
        if (r > 0.55) { const v = 120 + r * 135; g.fillStyle = `rgb(${v},${v * 0.96},${v * 0.85})`; g.fillRect(x, y, 6, 7); }
      }
    });
    const texs = [winTex(1), winTex(2), winTex(3)];
    const city = new THREE.Group(); scene.add(city); dyn.city = city;
    for (let i = 0; i < 70; i++) {
      const x = -380 + hh(i * 3.1) * 1700, z = 1700 + hh(i * 7.7) * 1900;
      const w = 30 + hh(i * 1.3) * 45, d = 30 + hh(i * 2.9) * 40, hgt = 60 + Math.pow(hh(i * 5.3), 2.2) * 380;
      const t = texs[i % 3].clone(); t.needsUpdate = true; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(w / 40, hgt / 70);
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, hgt, d), new THREE.MeshBasicMaterial({ map: t, color: 0x9a9a9a }));
      m.position.set(x, hgt / 2, z); city.add(m);
      if (i % 9 === 0) { const sp = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 1.4, hgt * 0.25, 6), new THREE.MeshBasicMaterial({ color: 0x2a2a2a })); sp.position.set(x, hgt * 1.12, z); city.add(sp); }
    }
    // the near city side on the right (low and mid-rise blocks beyond the shoulder)
    for (let i = 0; i < 40; i++) {
      const z = -400 + i * 32, hgt = 15 + hh(i * 4.1) * 60, w = 24 + hh(i) * 10;
      const t = texs[i % 3].clone(); t.needsUpdate = true; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(w / 40, hgt / 70);
      const m = new THREE.Mesh(new THREE.BoxGeometry(18, hgt, w), new THREE.MeshBasicMaterial({ map: t, color: 0x8a8a8a }));
      m.position.set(40 + hh(i * 2) * 20, hgt / 2, z); dyn.lamps.add(m);
    }
  }

  // ---- the bulb billboard (lattice tower on the lakefront, two lit panels ringed with bulbs)
  function buildBillboard() {
    const B = R.BILL, g = new THREE.Group(); scene.add(g); dyn.bill = g;
    const steel = lam(0x4a4a4e), hw = B.w / 2;
    const yb1 = B.y0, yt1 = yb1 + B.ph, yb2 = yt1 + B.gap, yt2 = yb2 + B.ph;
    const panelTex = canvasTex(512, 128, (c, w, h) => {
      c.fillStyle = '#e8e2d2'; c.fillRect(0, 0, w, h);
      for (let x = 0; x < w; x += 32) { c.fillStyle = 'rgba(0,0,0,0.08)'; c.fillRect(x, 0, 2, h); }   // panel seams
    });
    const panelM = new THREE.MeshBasicMaterial({ map: panelTex, color: 0xd8d2c4 });
    for (const [yb, yt] of [[yb1, yt1], [yb2, yt2]]) {
      // face toward -z (the road ahead, so it faces the cars coming toward it... and us in the mirror)
      const pm = quad([B.x + hw, yb, 0], [B.x - hw, yb, 0], [B.x - hw, yt, 0], [B.x + hw, yt, 0], panelM, g); pm.geometry.computeVertexNormals();
      (dyn.panels = dyn.panels || []).push(pm);
      // frame
      box(B.x - hw - 0.35, yb - 0.35, 0.02, B.x + hw + 0.35, yb, 0.4, steel, g);
      box(B.x - hw - 0.35, yt, 0.02, B.x + hw + 0.35, yt + 0.35, 0.4, steel, g);
      box(B.x - hw - 0.35, yb, 0.02, B.x - hw, yt, 0.4, steel, g);
      box(B.x + hw, yb, 0.02, B.x + hw + 0.35, yt, 0.4, steel, g);
    }
    // bulbs round each panel
    const bulbs = [];
    for (const [yb, yt] of [[yb1, yt1], [yb2, yt2]]) {
      const ring = [];
      for (let x = -hw; x <= hw + 1e-6; x += 1.3) { ring.push([B.x + x, yb - 0.18]); ring.push([B.x + x, yt + 0.18]); }
      for (let y = yb + 1.1; y < yt - 0.5; y += 1.3) { ring.push([B.x - hw - 0.18, y]); ring.push([B.x + hw + 0.18, y]); }
      bulbs.push(...ring);
    }
    const bm = new THREE.InstancedMesh(new THREE.SphereGeometry(0.42, 8, 6), glow(0xfffbe8), bulbs.length);
    const mm = new THREE.Matrix4();
    bulbs.forEach(([x, y], i) => { mm.makeTranslation(x, y, -0.25); bm.setMatrixAt(i, mm); });
    g.add(bm);
    // lattice tower and catwalk
    for (const x of [B.x - hw * 0.6, B.x + hw * 0.6]) {
      for (const dz of [0.6, 3.6]) beam([x - 1.2, 0, dz], [x - 0.6, yb1 - 0.4, dz], 0.35, 0.35, steel, g), beam([x + 1.2, 0, dz], [x + 0.6, yb1 - 0.4, dz], 0.35, 0.35, steel, g);
      for (let y = 0.8; y < yb1 - 0.6; y += 1.6) { beam([x - 1.1, y, 0.6], [x + 1.0, y + 1.5, 0.6], 0.12, 0.12, steel, g); beam([x + 1.1, y, 0.6], [x - 1.0, y + 1.5, 0.6], 0.12, 0.12, steel, g); }
    }
    box(B.x - hw - 0.5, yb1 - 0.9, -1.2, B.x + hw + 0.5, yb1 - 0.75, 0.5, steel, g);   // catwalk
    for (let x = -hw; x <= hw; x += 2.0) beam([B.x + x, yb1 - 0.75, -1.15], [B.x + x, yb1 - 0.0, -1.15], 0.05, 0.05, steel, g);
    // a low lakefront pavilion behind it
    box(B.x - 16, 0, 4, B.x + 16, 1.6, 20, lam(0x3a3a3a), g);   // (behind the tower, low: it must not hide the lower panel)
  }

  // ---- the TVA sedan: a plain boxy black 1990s sedan, lights OFF, a blank pale front plate
  function buildSedan() {
    const S = R.SEDAN, g = new THREE.Group(); scene.add(g); dyn.sedan = g;
    const paint = phong(0x050506, 60, 0x2a2a2a), glassM = phong(0x050507, 120, 0xbbbbbb), chrome = phong(0x8a8a8a, 90, 0xffffff), rubber = lam(0x0a0a0a);
    // side profile in (z, y), front at z = 0 (the sedan faces -z), extruded along x
    const body = new THREE.Shape();
    const pb = [[0.0, 0.30], [0.0, 0.66], [0.06, 0.78], [1.05, 0.86], [1.25, 0.88], [3.95, 0.90], [4.95, 0.93], [5.12, 0.84], [5.15, 0.55], [5.12, 0.30]];
    body.moveTo(pb[0][0], pb[0][1]); for (const q of pb.slice(1)) body.lineTo(q[0], q[1]); body.closePath();
    const bg = new THREE.ExtrudeGeometry(body, { depth: S.w - 0.12, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.05, bevelSegments: 3, curveSegments: 4 });
    const bm = new THREE.Mesh(bg, paint);
    // shape x -> car z, shape y -> y, extrude z -> car x : rotate so that shape (x, y, z) maps to (z->x?)
    bm.rotation.y = -Math.PI / 2; bm.position.set(-(S.w - 0.12) / 2, 0, 0); g.add(bm);
    // after rotation.y = -90deg: shape x -> world +z, extrude z -> world -x... fix the x offset accordingly
    bm.position.x = (S.w - 0.12) / 2;
    const cabin = new THREE.Shape();
    const pc = [[1.25, 0.86], [2.05, 1.40], [3.35, 1.43], [4.10, 0.92]];
    cabin.moveTo(pc[0][0], pc[0][1]); for (const q of pc.slice(1)) cabin.lineTo(q[0], q[1]); cabin.closePath();
    const cw = S.w - 0.40;
    const cg = new THREE.ExtrudeGeometry(cabin, { depth: cw, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.04, bevelSegments: 2 });
    const cm = new THREE.Mesh(cg, glassM); cm.rotation.y = -Math.PI / 2; cm.position.set(cw / 2, 0, 0); g.add(cm);
    // pillars and roof skin in paint over the glass cabin
    const roof = new THREE.Shape(); const pr = [[1.98, 1.36], [2.08, 1.445], [3.33, 1.475], [3.45, 1.40]];
    roof.moveTo(pr[0][0], pr[0][1]); for (const q of pr.slice(1)) roof.lineTo(q[0], q[1]); roof.closePath();
    const rg = new THREE.ExtrudeGeometry(roof, { depth: cw + 0.04, bevelEnabled: false });
    const rm = new THREE.Mesh(rg, paint); rm.rotation.y = -Math.PI / 2; rm.position.set((cw + 0.04) / 2, 0, 0); g.add(rm);
    for (const sx of [-1, 1]) beam([sx * (cw / 2 + 0.01), 0.88, 1.27], [sx * (cw / 2 - 0.06), 1.41, 2.05], 0.07, 0.09, paint, g, [1, 0, 0]);   // A-pillars
    // grille, headlights (off), bumper, plate
    box(-0.42, 0.50, -0.07, 0.42, 0.68, 0.02, phong(0x060606, 30, 0x555555), g);
    for (let i = 0; i < 6; i++) box(-0.40, 0.515 + i * 0.028, -0.085, 0.40, 0.525 + i * 0.028, -0.06, chrome, g);
    for (const sx of [-1, 1]) {
      box(sx * 0.48 - 0.19, 0.55, -0.06, sx * 0.48 + 0.19, 0.69, 0.02, phong(0x3a3c40, 120, 0xffffff), g);   // headlight lens, off
      box(sx * 0.80 - 0.06, 0.55, -0.045, sx * 0.80 + 0.06, 0.66, 0.03, phong(0x2a2a2a, 100, 0xcccccc), g);
    }
    box(-0.92, 0.26, -0.12, 0.92, 0.48, 0.05, phong(0x0a0a0a, 40, 0x666666), g);    // bumper
    const plate = box(-R.PLATE.w / 2, R.PLATE.y - R.PLATE.h / 2, -0.15, R.PLATE.w / 2, R.PLATE.y + R.PLATE.h / 2, -0.125, lam(0xd8d4c8, { emissive: 0x2a2924 }), g);
    dyn.plate = plate;
    // wheels
    const tire = new THREE.CylinderGeometry(0.34, 0.34, 0.24, 18); tire.rotateZ(Math.PI / 2);
    for (const z of [0.95, 3.95]) for (const sx of [-1, 1]) { const w = new THREE.Mesh(tire, rubber); w.position.set(sx * 0.80, 0.34, z); g.add(w); }
    // two agents behind the windshield: dark head-and-shoulder shapes with a pale shirt collar
    for (const sx of [-0.38, 0.40]) {
      const hd = new THREE.Mesh(new THREE.SphereGeometry(0.11, 12, 10), lam(0x1e1c1c)); hd.position.set(sx, 1.18, 2.45); hd.scale.set(1, 1.2, 1.05); g.add(hd);
      box(sx - 0.22, 0.88, 2.35, sx + 0.22, 1.05, 2.70, lam(0x101012), g);
      box(sx - 0.05, 1.0, 2.36, sx + 0.05, 1.05, 2.40, lam(0xcfcfcf), g);
      box(sx - 0.085, 1.185, 2.335, sx + 0.085, 1.215, 2.36, glassM, g);   // shades
    }
  }

  // the sedan as an engraved card (the 3D box sedan above stays hidden: params.boxSedan shows it)
  async function buildSedanCard() {
    let tex;
    try { tex = await new THREE.TextureLoader().loadAsync(params.sedan || '/media/shots/D23/sedan_a_r7_rgba.png')   // round 7: the pale wedge under the bumper inked out (it sat on the etch's "me")
     ; } catch (e) { console.warn('no sedan card'); return; }
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
    const I = R.SEDAN_IMG, k = R.SEDAN_PPM, w = I.size[0] / k, h = I.size[1] / k;
    const g = new THREE.PlaneGeometry(w, h);
    // plane centre: image centre (size/2) -> world, relative to the sedan's front point
    // round 5: x sign fixed (was -(W/2 - cx)/k, which put the card 28 image px off the plate track): image px -> local x
    // = (px - cx)/k before the half-turn below
    g.translate((I.size[0] / 2 - I.cx) / k, (I.ground - I.size[1] / 2) / k, 0);
    const m = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, side: THREE.DoubleSide });
    const mesh = new THREE.Mesh(g, m); mesh.rotation.y = Math.PI;   // face -z: image right -> world -x
    mesh.renderOrder = 2;
    dyn.sedanCard = mesh; dyn.sedanCardMat = m; dyn.sedan.add(mesh);
    // round 5: headlights ON, as in D4 (white starbursts on the drawn lamps; the card faces -z, image right = world -x)
    if (params.lights !== false) {
      const sm = new THREE.SpriteMaterial({ map: dyn.burstTex, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false, transparent: true });
      for (const [px, py] of I.lamps) { const sp = new THREE.Sprite(sm); sp.scale.set(1.5, 1.5, 1); sp.position.set(-(px - I.cx) / k, (I.ground - py) / k, -0.08); sp.renderOrder = 4; dyn.sedan.add(sp); }
    }
    // the plate's quad, white in the billboard/lettering mask only (pass=billmask): the engine's pinned TVA 1729 is then
    // occluded like the lyric (only where the plate is really seen, i.e. inside the glass)
    // round 7: the group is yawed (R.SEDAN.yaw), so the mask quad is built in the card's own (unrotated) frame
    const [x0, y0, x1, y1] = I.plate, L = (px, py) => [-(px - I.cx) / k, (I.ground - py) / k, -0.02];
    const loc = [L(x0, y0), L(x1, y0), L(x1, y1), L(x0, y1)];
    dyn.plateMask = quad(loc[1], loc[0], loc[3], loc[2], new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: true, depthWrite: false }), dyn.sedan);   // transparent: drawn after the (transparent) card
    dyn.plateMask.visible = params.pass === 'billmask'; dyn.plateMask.renderOrder = 3;
    for (const c of dyn.sedan.children) if (c !== mesh && c !== dyn.plateMask && !c.isSprite) c.visible = !!params.boxSedan;
  }

  // ---- traffic: northbound cars beyond the median (headlights toward us as they come, tail lamps as they go)
  function buildTraffic() {
    dyn.traffic = [];
    const bodyM = phong(0x2a2a2c, 60, 0x777777), lampM = glow(0xfff2d8), tailM = glow(0xc8c0b8);
    const sm = new THREE.SpriteMaterial({ map: dyn.burstTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true });
    for (let i = 0; i < 9; i++) {
      const g = new THREE.Group(); scene.add(g);
      box(-0.88, 0.25, -2.4, 0.88, 0.85, 2.4, bodyM, g);
      box(-0.75, 0.85, -1.0, 0.75, 1.35, 1.3, bodyM, g);
      for (const sx of [-0.6, 0.6]) {
        box(sx - 0.15, 0.55, 2.38, sx + 0.15, 0.68, 2.45, lampM, g);   // headlights face +z (northbound)
        const s = new THREE.Sprite(sm); s.scale.set(1.6, 1.6, 1); s.position.set(sx, 0.62, 2.6); g.add(s); (dyn.bursts = dyn.bursts || []).push(s);
        box(sx - 0.14, 0.62, -2.45, sx + 0.14, 0.72, -2.38, tailM, g);
      }
      dyn.traffic.push({ g, lane: [-16.0, -20.0, -23.8][i % 3], z0: -420 + i * 97 + hh(i) * 40 + (+(params.trafficShift ?? R.TRAFFIC_SHIFT ?? 0)),   // round 7: phase chosen so no car crosses the far billboard in the glass
        v: 2 * R.SPEED + hh(i + 3) * 6 });
    }
  }

  // ---- Jade's car: the driver's side of the cabin as seen from the passenger seat, plus the bits outside the window
  function buildCar() {
    const C = R.CAR;
    const trim = lam(0x3c3c42), trim2 = lam(0x55555c), dash = lam(0x2e2e33), liner = lam(0x9c9890), seatM = lam(0x38383e), white = phong(0xe8e6e0, 50, 0x777777, { side: THREE.DoubleSide });
    const car = new THREE.Group(); scene.add(car); dyn.car = car;
    const grain = fbmCanvas(512, 512, 5, 9, 5, 7, (v) => { const k = 70 + v * 185; return [k, k, k]; });
    for (const m of [trim, trim2, dash, liner, seatM]) m.map = grain;
    // door panel (inside), armrest, handle, the window sill
    box(-0.86, 0.28, -0.98, C.doorIn, C.belt - 0.02, C.bZ, trim, car);
    box(C.doorIn, 0.56, -0.30, -0.70, 0.64, 0.30, trim2, car);           // armrest
    box(C.doorIn, 0.62, -0.62, -0.76, 0.70, -0.42, lam(0x3a3a3e), car);  // pull handle
    box(-0.86, 0.40, -0.70, -0.79, 0.52, 0.10, lam(0x151517), car);       // map pocket
    box(-0.93, C.belt - 0.03, -0.96, -0.78, C.belt + 0.02, C.bZ, trim2, car);   // sill trim
    box(-0.95, C.belt - 0.05, -0.96, -0.90, C.belt + 0.005, C.bZ, white, car);  // the white door skin's top edge outside
    // A-pillar (window side): a thick trimmed post from the sail up to the roof
    beam(C.aBase, C.aTop, 0.10, 0.09, trim, car, [1, 0, 0]);
    beam([-0.90, 0.97, -0.99], [-0.79, 1.38, -0.27], 0.07, 0.05, white, car, [1, 0, 0]);   // the body-colour pillar outside
    // the sail (the black triangle at the front of the window, where the mirror is mounted)
    quad([-0.89, 0.965, -0.93], [-0.89, 0.965, -0.76], [-0.87, 1.13, -0.86], [-0.87, 1.13, -0.86], lam(0x0e0e10, { side: THREE.DoubleSide }), car);
    // window frame rail along the roof, B-pillar
    box(-0.84, C.roof - 0.03, -0.25, -0.76, C.roof + 0.03, C.bZ, trim, car);
    box(-0.86, C.belt, C.bZ - 0.03, -0.76, C.roof, C.bZ + 0.09, trim, car);
    // roof liner
    box(-0.80, C.roof, -0.30, 0.80, C.roof + 0.04, 1.4, liner, car);
    box(-0.78, C.roof - 0.02, -0.32, 0.78, C.roof + 0.01, -0.22, lam(0x4a4844), car);   // header trim
    // sun visor (folded up) over her
    box(-0.70, C.roof - 0.05, -0.30, -0.12, C.roof - 0.01, -0.06, lam(0x6a6762), car);
    // windshield frame (no glass drawn), dashboard, instrument hood, vents
    beam([-0.84, 0.99, -1.02], [0.84, 0.99, -1.02], 0.05, 0.05, trim, car);
    box(-0.86, 0.55, -1.30, 0.86, 0.97, -0.70, dash, car);
    box(-0.64, 0.95, -0.92, -0.12, 1.04, -0.66, dash, car);            // instrument hood over the cluster
    box(-0.60, 0.82, -0.72, -0.16, 0.95, -0.69, lam(0x0b0b0c), car);     // the cluster face (dark)
    box(-0.84, 0.86, -0.70, -0.70, 0.93, -0.66, lam(0x101012), car);    // left vent
    box(-0.86, 0.52, -0.72, 0.86, 0.56, -0.40, lam(0x141416), car);      // lower dash lip
    // centre console and the gear lever
    box(-0.13, 0.30, -0.70, 0.13, 0.62, 0.40, trim2, car);
    beam([0.0, 0.62, -0.20], [0.0, 0.76, -0.24], 0.03, 0.03, lam(0x333336), car);
    // driver's seat: cushion, back, headrest (behind her), and the passenger seat's own edge is behind the camera
    box(-0.62, 0.30, -0.25, -0.12, 0.48, 0.30, seatM, car);
    beam([-0.37, 0.48, 0.32], [-0.37, 1.02, 0.44], 0.52, 0.14, seatM, car, [0, 0, 1]);
    box(-0.49, 1.08, 0.36, -0.25, 1.30, 0.48, seatM, car);
    beam([-0.43, 1.0, 0.42], [-0.43, 1.09, 0.42], 0.015, 0.015, lam(0x777777), car); beam([-0.31, 1.0, 0.42], [-0.31, 1.09, 0.42], 0.015, 0.015, lam(0x777777), car);
    // the seat belt anchor on the B-pillar
    box(-0.79, 1.14, C.bZ - 0.05, -0.75, 1.22, C.bZ + 0.02, lam(0x3c3c40), car);
    // steering wheel (rim, hub, three spokes) and its column
    const Wc = V(R.WHEEL.c), Wn = V(R.WHEEL.n);
    const wheel = new THREE.Group(); wheel.position.copy(Wc); wheel.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), Wn); car.add(wheel);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(R.WHEEL.r, 0.017, 10, 48), lam(0x161618)); wheel.add(rim);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.085, 0.06, 20), lam(0x1d1d20)); hub.rotation.x = Math.PI / 2; wheel.add(hub);
    for (const a of [Math.PI, 0, -Math.PI / 2]) beam([Math.cos(a) * 0.07, Math.sin(a) * 0.07, 0], [Math.cos(a) * R.WHEEL.r, Math.sin(a) * R.WHEEL.r, 0], 0.035, 0.012, lam(0x1d1d20), wheel, [0, 0, 1]);
    dyn.wheel = wheel;
    beam(R.WHEEL.c, [-0.37, 0.80, -0.70], 0.07, 0.07, lam(0x141416), car);
    // outside: the white hood and the front fender ahead of the window
    const hood = new THREE.Shape(); hood.moveTo(-0.86, 0); hood.lineTo(0.86, 0); hood.lineTo(0.80, -1.5); hood.lineTo(-0.80, -1.5); hood.closePath();
    const hm = new THREE.Mesh(new THREE.ShapeGeometry(hood), white); hm.rotation.x = Math.PI / 2 + 0.06; hm.position.set(0, 0.97, -1.05); car.add(hm);
    box(-0.93, 0.70, -2.5, -0.84, 0.95, -1.0, white, car);              // fender top edge
  }

  // ---- the driver's door mirror: arm from the sail, white housing, black bezel, the glass (a live reflection)
  function buildMirror() {
    const M = R.MIRROR, g = new THREE.Group(); scene.add(g); dyn.mirror = g;
    const white = phong(0xe6e4de, 60, 0x888888), black = phong(0x0b0b0c, 30, 0x333333);
    const basis = new THREE.Matrix4().makeBasis(V(M.u), V(M.v), V(M.n));
    const mg = new THREE.Group(); mg.position.copy(V(M.c)); mg.quaternion.setFromRotationMatrix(basis); g.add(mg);
    // round 5: the real 1999-2003 TL mirror outline (rig.js TL_OUTLINE) instead of a rounded rectangle
    const outline = (grow, P = R.TL_OUTLINE) => { const sh = new THREE.Shape(); P.forEach(([a, b], k) => { const x = a * (M.w / 2 + grow), y = b * (M.h / 2 + grow); if (k) sh.lineTo(x, y); else sh.moveTo(x, y); }); return sh; };
    const rr = (w, h) => outline((w - M.w) / 2);   // kept for the backing below
    // the cap: the outline grown by the bezel, extruded with a deep rounded back (the TL's cap bulges forward)
    // round 7 (Jade: the rim read as a picture frame): the cap's edge only ~1.4 cm beyond the glass (was 4 cm: grown 2.2 +
    // bevel 1.8), a rounder, shallower back (~11 cm deep): the guide for the drawn housing, and the fallback (housing=cg)
    const hg = new THREE.ExtrudeGeometry(outline(0.004), { depth: 0.02, bevelEnabled: true, bevelThickness: 0.045, bevelSize: 0.010, bevelSegments: 10, curveSegments: 6 });
    const housing = new THREE.Mesh(hg, white); housing.position.z = -0.07; mg.add(housing); dyn.cg = [housing];
    // the bezel lip round the glass
    // the body-colour cap wraps to the glass (TL photos): a white lip, then only a thin dark seam round the glass
    const bez = outline(0.008); bez.holes.push(outline(0.002));   // round 7: a thin lip (was 1.6 cm)
    const bezel = new THREE.Mesh(new THREE.ExtrudeGeometry(bez, { depth: 0.01, bevelEnabled: true, bevelThickness: 0.005, bevelSize: 0.004, bevelSegments: 3 }), white);
    bezel.position.z = -0.008; mg.add(bezel); dyn.cg.push(bezel);
    const backing = new THREE.Mesh(new THREE.ShapeGeometry(outline(0.0035)), black); backing.position.z = -0.003; mg.add(backing); dyn.cg.push(backing);
    // the glass: samples the virtual camera's render (flipped left-right: that IS the mirror image)
    // round 7: with the drawn housing, the glass mesh is grown 1.2 cm under the drawn rim (the drawing's own glass hole is
    // the visible outline) and the reflection frustum covers FR x the glass rectangle, so nothing smears at the edge
    const FR = R.MIRROR_FR, gg = new THREE.ShapeGeometry(params.housing === 'drawn' ? outline(0.006, R.GLASS_OUTLINE) : outline(0.0));
    const pos = gg.attributes.position, uv = gg.attributes.uv;
    for (let i = 0; i < pos.count; i++) uv.setXY(i, pos.getX(i) / (M.w * FR) + 0.5, pos.getY(i) / (M.h * FR) + 0.5);
    glass = new THREE.Mesh(gg, new THREE.ShaderMaterial({
      uniforms: { tMir: { value: mirrorRT.texture }, uGain: { value: 0.86 }, uEdge: { value: 1 } },
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: `uniform sampler2D tMir; uniform float uGain, uEdge; varying vec2 vUv;
        void main(){
          vec3 c = texture2D(tMir, vec2(1.0 - vUv.x, vUv.y)).rgb * uGain;
          float edge = 1.0;
          gl_FragColor = vec4(c * mix(1.0 - 0.25 * uEdge, 1.0, edge) + vec3(0.006 * uEdge), 1.0);
        }`,
    }));
    glass.position.z = 0.001; mg.add(glass);
    // the arm: from the sail to the housing's inboard end, a tapered fairing
    // round 5: the TL's neck is short and low, at the inboard bottom of the cap, on a triangular sail foot
    const inb = new THREE.Vector3(...R.glassPt(0.9, -0.62)).add(V(M.n).multiplyScalar(-0.07));
    // round 4: the root is R.ARM0, on the door skin at the window's front corner (behind the plate's A-pillar base)
    const a0 = R.ARM0;
    dyn.cg.push(beam(a0, [inb.x, inb.y, inb.z], 0.06, 0.07, white, g, [0, 1, 0]));
    dyn.cg.push(beam([a0[0], a0[1] - 0.03, a0[2]], [inb.x + 0.01, inb.y - 0.03, inb.z], 0.045, 0.05, white, g, [0, 1, 0]));
    { const f = new THREE.Mesh(new THREE.ConeGeometry(0.055, 0.12, 3), black); f.position.set(a0[0] + 0.01, a0[1] + 0.02, a0[2] + 0.02); f.rotation.z = Math.PI / 2; g.add(f); dyn.cg.push(f); }   // the sail foot
    dyn.mg = mg;
    if (params.housing === 'drawn' || params.housing === 'none') for (const m of dyn.cg) m.visible = false;   // round 7: the drawn card replaces them
  }

  // ---- round 7: the DRAWN housing (Jade: the CG cap read as a pasted vector object next to the drawn interior). A
  // nano-banana drawing of the TL cap in the film's linework (tools/v9/d23/housing_r7.py), keyed and registered to the
  // housing guide's frustum (R.housingCam), on a card in front of the glass. Its glass hole is transparent: the live
  // reflection shows through it. Under the plate card (her interior, with the sail painted in the window corner).
  async function buildHousingCard() {
    let tex;
    try { tex = await new THREE.TextureLoader().loadAsync(params.housingTex || '/media/shots/D23/r7_housing_rgba.png'); } catch (e) { console.warn('no housing card'); return; }
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.minFilter = THREE.LinearMipmapLinearFilter;
    const c0 = R.housingCam(), dist = 1.2;
    const hgt = 2 * dist * Math.tan(c0.fov * Math.PI / 360), wid = hgt * R.W / R.H;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(wid, hgt), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, depthWrite: false, toneMapped: false }));
    m.position.copy(V(c0.pos).addScaledVector(V(c0.fwd), dist));
    m.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(V(c0.right), V(c0.up), V(c0.fwd).negate()));
    m.renderOrder = 5; scene.add(m); dyn.housingCard = m;
  }
  // the guide for the drawing (pass=housingguide): only the CG cap, lit, on flat chroma green, the glass flat green too
  function housingGuide() {
    scene.background = new THREE.Color(0x00ff00);
    const keep = new Set(); dyn.mirror.traverse((o) => keep.add(o));
    scene.traverse((o) => { if ((o.isMesh || o.isSprite || o.isPoints) && !keep.has(o)) o.visible = false; });
    glass.material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    for (const m of dyn.cg) m.visible = true;
    for (const m of dyn.cg.slice(2)) m.visible = false;   // no black backing ring (the drawing's own thin seam), no arm or sail foot (behind the painted sail)
  }

  // ---- lights: night. Weak moonlight from the lake, the streetlamps as point lights (the nearest few, streaming
  // back over the car and over the sedan), the instrument glow on her
  function buildLights() {
    scene.add(new THREE.HemisphereLight(0x3a4050, 0x101010, 0.35));
    // the cabin's key: sodium/LED wash through the windshield from the front left, high (keeps the interior's planes apart)
    const key = new THREE.DirectionalLight(0xfff2dc, 1.6); key.position.set(-0.6, 1.0, -0.8); scene.add(key);
    const rim = new THREE.DirectionalLight(0xc8d4ea, 0.35); rim.position.set(0.8, 0.3, 0.6); scene.add(rim);
    const moon = new THREE.DirectionalLight(0xb8c4d8, 0.35); moon.position.set(-60, 80, 30); scene.add(moon);
    dyn.pl = [];
    for (let i = 0; i < 6; i++) { const l = new THREE.PointLight(0xfff0d6, 0, 70, 1.6); scene.add(l); dyn.pl.push(l); }
    const cl = new THREE.PointLight(0x9fb4d8, 0.35, 1.4, 1.5); cl.position.set(-0.38, 0.90, -0.62); scene.add(cl);
    const fill = new THREE.PointLight(0xd8d0c0, 0.25, 3, 1.5); fill.position.set(0.1, 1.25, 0.2); scene.add(fill);
  }

  // ---- the billboard-visibility mask (pass=billmask): white where a billboard panel is the visible surface, black
  // everywhere else. The engine re-draws the clip through the inverse of this over the pinned lyric, so the sedan, lamp
  // poles, the glass edge and the A-pillar all occlude the lettering.
  function maskMaterials() {
    const black = new THREE.MeshBasicMaterial({ color: 0x000000 }), white = new THREE.MeshBasicMaterial({ color: 0xffffff });
    scene.background = new THREE.Color(0x000000);
    scene.traverse((o) => {
      if (o.isSprite || o.isPoints) { o.visible = false; return; }
      if (!o.isMesh || o === glass) return;
      if (o === dyn.plateMask) return;
      if (dyn.panels.includes(o)) o.material = white;
      else if (o === card || o === dyn.sedanCard || o === dyn.housingCard) { o.material = o.material.clone(); o.material.color.set(0x000000); }
      else o.material = black;
    });
    glass.material.uniforms.uGain.value = 1; glass.material.uniforms.uEdge.value = 0;
  }

  // ---- the layout guide for the plate (pass=guidekey): everything outside the car is flat chroma green, so the model
  // keeps the window open and the 3D outside (road, mirror, reflection) can be keyed in behind her plate
  function keyOutside() {
    scene.background = new THREE.Color(0x00ff00);
    const keep = new Set(); dyn.car.traverse((o) => keep.add(o));
    scene.traverse((o) => { if ((o.isMesh || o.isSprite || o.isPoints) && !keep.has(o) && !o.userData.mannequin) o.visible = false; });
  }

  // ---- a grey mannequin for the layout guide only (nano-banana draws Jade over it)
  function buildMannequin() {
    const m = lam(0xb4b4b4), g = new THREE.Group(); scene.add(g); dyn.mannequin = g;
    const H = V(R.HEAD);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.105, 24, 18), m); head.position.copy(H); head.scale.set(0.92, 1.12, 1.0); g.add(head);
    // looking at the mirror: a nose pointing at it, the bun at the back of the head with two crossed sticks
    // round 4: the head turned ~20 deg to her left (her eyes do the rest, onto the mirror)
    const toM = new THREE.Vector3(-Math.sin(0.35), -0.05, -Math.cos(0.35)).normalize();
    const nose = new THREE.Mesh(new THREE.ConeGeometry(0.03, 0.08, 10), m); nose.position.copy(H).addScaledVector(toM, 0.11); nose.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), toM); g.add(nose);
    const back = H.clone().addScaledVector(toM, -0.11).add(new THREE.Vector3(0, 0.06, 0));
    const bun = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 12), m); bun.position.copy(back); g.add(bun);
    for (const s of [-1, 1]) beam([back.x - 0.0, back.y - 0.08, back.z + s * 0.08], [back.x, back.y + 0.12, back.z - s * 0.08], 0.012, 0.012, lam(0xd0c060), g);
    beam([R.HEAD[0], 1.0, 0.08], [R.HEAD[0], 1.08, 0.07], 0.06, 0.06, m, g);   // neck
    const torso = beam([-0.39, 0.55, 0.20], [-0.40, 1.0, 0.12], 0.38, 0.22, m, g, [0, 0, 1]);
    // arms to the wheel (hands at ten and two)
    const Wc = V(R.WHEEL.c); const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), V(R.WHEEL.n));
    const hand = (a) => new THREE.Vector3(Math.cos(a) * R.WHEEL.r, Math.sin(a) * R.WHEEL.r, 0).applyQuaternion(q).add(Wc);
    for (const [sx, a] of [[-0.58, 2.6], [-0.20, 0.55]]) {
      const sh = new THREE.Vector3(sx, 0.98, 0.14), hd = hand(a), el = sh.clone().lerp(hd, 0.5).add(new THREE.Vector3(sx < -0.4 ? -0.08 : 0.06, -0.12, 0.05));
      beam([sh.x, sh.y, sh.z], [el.x, el.y, el.z], 0.075, 0.075, m, g); beam([el.x, el.y, el.z], [hd.x, hd.y, hd.z], 0.06, 0.06, m, g);
      const hm = new THREE.Mesh(new THREE.SphereGeometry(0.04, 10, 8), m); hm.position.copy(hd); g.add(hm);
    }
    // thighs
    beam([-0.48, 0.52, 0.10], [-0.48, 0.56, -0.38], 0.15, 0.14, m, g); beam([-0.26, 0.52, 0.10], [-0.26, 0.56, -0.38], 0.15, 0.14, m, g);
    g.traverse((o) => { o.userData.mannequin = true; });
  }

  // ---- Jade: her matted anime plate, drawn from the wide (S0) camera, on a card in front of the camera
  async function buildCard() {
    const c0 = R.guideCam(), dist = 0.62;
    const hgt = 2 * dist * Math.tan(c0.fov * Math.PI / 360), wid = hgt * R.PLATE_IMG.w / R.PLATE_IMG.h;
    let tex;
    try { tex = await new THREE.TextureLoader().loadAsync(params.plate); } catch (e) { console.warn('no plate', params.plate); return; }
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.minFilter = THREE.LinearMipmapLinearFilter;
    const geo = new THREE.PlaneGeometry(wid, hgt);
    card = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, toneMapped: false }));
    const ctr = V(c0.pos).addScaledVector(V(c0.fwd), dist);
    card.position.copy(ctr);
    card.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(V(c0.right), V(c0.up), V(c0.fwd).negate()));
    card.renderOrder = 10; scene.add(card);
    // round 6 (Jade: "a little bit of motion ... a lip bite or a blink"): the card swaps between plate variants that
    // differ only at her eye or her mouth (tools/v9/d23/r6_frames.py), keyed by film frame (R.faceAt)
    dyn.faceTex = { open: tex };
    if (params.face !== false) for (const v of ['half', 'blink', 'press50', 'press100']) {
      try { const t = await new THREE.TextureLoader().loadAsync(`/media/shots/D23/r7_plate_${v}_rgba.png`); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.minFilter = THREE.LinearMipmapLinearFilter; dyn.faceTex[v] = t; }
      catch (e) { console.warn('no face variant', v); }
    }
    dyn.car.visible = false;   // round 4: the plate IS the near interior (door, frame, dash, seat, wheel): the 3D car is only the layout
    let mtex = null;
    try { mtex = await new THREE.TextureLoader().loadAsync(params.plateMatte); mtex.colorSpace = THREE.NoColorSpace; } catch (e) { console.warn('no plate matte'); }
    // the matte: Jade only (white on black), from the plate's own Jade matte
    matteScene = new THREE.Scene(); matteScene.background = new THREE.Color(0x000000);
    cardMatte = new THREE.Mesh(geo, new THREE.ShaderMaterial({
      uniforms: { tMap: { value: mtex || tex }, uLum: { value: mtex ? 1 : 0 } }, transparent: false,
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: 'uniform sampler2D tMap; uniform float uLum; varying vec2 vUv; void main(){ vec4 t = texture2D(tMap, vUv); float a = uLum > 0.5 ? t.r : t.a; gl_FragColor = vec4(vec3(a), 1.0); }',
    }));
    cardMatte.position.copy(card.position); cardMatte.quaternion.copy(card.quaternion); matteScene.add(cardMatte);
    dyn.faceMatte = { open: mtex || tex };
    if (params.face !== false && mtex) for (const v of ['half', 'blink', 'press50', 'press100']) {
      try { const t = await new THREE.TextureLoader().loadAsync(`/media/shots/D23/r7_plate_${v}_jade.png`); t.colorSpace = THREE.NoColorSpace; dyn.faceMatte[v] = t; }
      catch (e) { console.warn('no face matte', v); }
    }
  }

  // ------------------------------------------------------------------ per frame
  const tmpM = new THREE.Matrix4();
  function update(s) {
    const dz = R.SPEED * (s - R.S0);
    // road texture and dashes stream back
    dyn.asphalt.offset.y = -(dz / 1600) * 400 % 1;
    const per = 12, N = dyn.dashN;
    let i = 0;
    for (const x of dyn.dashLines) for (let k = 0; k < N; k++) {
      const z = ((k * per + dz) % (N * per)) - 200;
      tmpM.makeTranslation(x, 0.006, z); dyn.dashes.setMatrixAt(i++, tmpM);
    }
    dyn.dashes.instanceMatrix.needsUpdate = true;
    dyn.lamps.position.z = dz;
    // the lamp point lights: the nearest median/shoulder lamps around the car and around the sedan
    const sd = R.sedanAt(s);
    const lampZ = (k) => k * LAMP_DZ + dz;
    const near = (z0) => { const k = Math.round((z0 - dz) / LAMP_DZ); return [k - 1, k, k + 1].map(lampZ); };
    const zs = [...near(0), ...near(sd.front[2] + 2)];
    zs.forEach((z, j) => { const l = dyn.pl[j]; l.position.set(-11.1, 10.6, z); l.intensity = +(params.lamp ?? 260); });
    dyn.bill.position.z = R.worldZ(R.BILL.z0, s);
    dyn.city.position.z = dz * 0.0;   // too far to move visibly in 5 s; it stays put relative to the horizon
    dyn.sedan.position.set(...sd.front); dyn.sedan.rotation.y = R.SEDAN.yaw || 0;   // round 7: angled toward us
    if (card && dyn.faceTex) {   // round 6: her blink and lip press
      const f = R.faceAt(s), t = dyn.faceTex[f] || dyn.faceTex.open, mt = dyn.faceMatte[f] || dyn.faceMatte.open;
      card.material.map = t; if (cardMatte) cardMatte.material.uniforms.tMap.value = mt;
    }
    if (dyn.sedanCardMat && params.pass !== 'billmask') {   // the lamps passing over it
      const ph = (((sd.front[2] - dz) % LAMP_DZ) + LAMP_DZ) % LAMP_DZ, dd = Math.min(ph, LAMP_DZ - ph);
      const v = 0.72 + 0.38 * Math.exp(-(dd / 9) * (dd / 9)); dyn.sedanCardMat.color.setRGB(v, v, v);
    }
    for (const t of dyn.traffic) {
      let z = t.z0 + t.v * (s - R.S0); z = ((z + 420) % 1100 + 1100) % 1100 - 420;
      t.g.position.set(t.lane, 0, z);
    }
    // camera
    const c = R.camAt(s);
    cam.fov = c.fov; cam.aspect = R.W / R.H; cam.updateProjectionMatrix();
    cam.matrix.makeBasis(V(c.right), V(c.up), V(c.fwd).negate()).setPosition(V(c.pos));
    cam.updateMatrixWorld(true);
    // the virtual mirror camera: the passenger's eye reflected in the glass plane, frustum = the glass rectangle
    const pe = V(R.reflect(c.pos));
    const FR = R.MIRROR_FR, pa = V(R.glassPt(FR, -FR)), pb = V(R.glassPt(-FR, -FR)), pc = V(R.glassPt(FR, FR));
    const vr = pb.clone().sub(pa).normalize(), vu = pc.clone().sub(pa).normalize(), vn = new THREE.Vector3().crossVectors(vr, vu).normalize();
    const va = pa.clone().sub(pe), vb = pb.clone().sub(pe), vc = pc.clone().sub(pe);
    const d = -va.dot(vn), near_ = d;
    const l = vr.dot(va) * near_ / d, r = vr.dot(vb) * near_ / d, b = vu.dot(va) * near_ / d, t = vu.dot(vc) * near_ / d;
    mirrorCam.projectionMatrix.makePerspective(l, r, t, b, near_, 6000);
    mirrorCam.projectionMatrixInverse.copy(mirrorCam.projectionMatrix).invert();
    mirrorCam.matrix.makeBasis(vr, vu, vn).setPosition(pe);
    mirrorCam.updateMatrixWorld(true);
    return c;
  }

  function draw(lt) {
    const s = R.CLIP0 + lt;   // round 5: clip frame n = film frame 556 + n exactly (the engine floors (t - 23.16) * 24)
    update(s);
    if (params.pass === 'housingguide' || params.housingView) { const c = R.housingCam(); cam.fov = c.fov; cam.updateProjectionMatrix(); cam.matrix.makeBasis(V(c.right), V(c.up), V(c.fwd).negate()).setPosition(V(c.pos)); cam.updateMatrixWorld(true); }
    else if (params.pass === 'guide' || params.pass === 'guidekey' || params.guideView) { const c = R.guideCam(); cam.fov = c.fov; cam.updateProjectionMatrix(); cam.matrix.makeBasis(V(c.right), V(c.up), V(c.fwd).negate()).setPosition(V(c.pos)); cam.updateMatrixWorld(true); }
    const out = renderer.getRenderTarget();
    renderer.setClearColor(0x000000, 1);
    if (params.pass === 'matte') {
      if (!matteScene) { renderer.setRenderTarget(out); renderer.clear(); return; }
      renderer.setRenderTarget(out); renderer.render(matteScene, cam);
      return;
    }
    // 1. the reflection (the glass, the card and the housing are behind the near plane or hidden)
    glass.visible = false; if (card) card.visible = false; if (dyn.housingCard) dyn.housingCard.visible = false;
    renderer.setRenderTarget(mirrorRT); renderer.render(scene, mirrorCam);
    glass.visible = true; if (card) card.visible = true; if (dyn.housingCard) dyn.housingCard.visible = true;
    // 2. the passenger's view
    // once the zoom is tight, a lamp passing the window in direct view would cross the frame in a frame or two: a
    // one-frame flash. The lamps stay in the mirror (pass 1); in direct view their starbursts (and lamp heads) are dropped below 24 deg (round 4).
    const tight = cam.fov < 24; if (dyn.bursts && params.pass !== 'billmask') for (const b of dyn.bursts) b.visible = !tight;
    if (params.pass !== 'billmask') for (const h of dyn.lampHeads) h.visible = !tight;
    renderer.setRenderTarget(mainRT); renderer.render(scene, cam);
    if (dyn.bursts && params.pass !== 'billmask') for (const b of dyn.bursts) b.visible = true;
    if (params.pass !== 'billmask') for (const h of dyn.lampHeads) h.visible = true;
    blit.uniforms.tSrc.value = mainRT.texture;
    renderer.setRenderTarget(out); renderer.render(blitScene, quadCam);
  }
  function anchors() { return {}; }
  function dispose() {}
  return { meta, init, draw, anchors, dispose };
}

const inst = createScene();
export const meta = inst.meta;
export const init = inst.init, draw = inst.draw, anchors = inst.anchors, dispose = inst.dispose;
export default inst;
