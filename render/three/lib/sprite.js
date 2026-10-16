// Anime sprite actors for the 3D shots: matted Jade clips (RGBA PNG frames + info.json from media/shots/E_sprites/<clip>/)
// packed into one atlas per clip and drawn as a vertical, camera-facing quad INSIDE the engraver's G-buffer, so the set
// occludes her, the ink outline and paper halo are drawn round her, and she is never hatched (she stays full colour).
// If the clips are missing, the actor falls back to the low-poly Jade figure (hair down, pencil in hand).
import * as THREE from 'three';
import { makeFigure } from './figures.js';

const COS_EL = Math.cos(Math.atan(1 / Math.SQRT2));   // vertical foreshortening of the magic camera (0.816)

async function loadImage(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error('missing ' + url);
  return createImageBitmap(await r.blob());
}

// clip: { dir (repo-relative), maxFrames } -> { tex, cols, rows, n, fps, boxW, boxH, feetY, topY }
export async function loadSpriteClip(dir, { maxFrames = 96, cellH = 512 } = {}) {
  const base = '/' + dir.replace(/^\/+/, '');
  const info = await (await fetch(base + '/info.json')).json();
  const count = info.frames ?? info.count ?? info.frame_count;
  // loop: [a, b] 0-based inclusive, or {first, last} 1-based where 'last' ~= 'first' (play first..last-1)
  const oneBased = /1-based/.test(info.frame_pattern || '') || info.first_index === 1;
  let a = 0, b = count - 1;
  if (Array.isArray(info.loop)) [a, b] = info.loop;
  else if (info.loop && info.loop.first) { a = info.loop.first - 1; b = info.loop.last - 2; }
  const step = Math.max(1, Math.ceil((b - a + 1) / maxFrames));
  const idx = []; for (let i = a; i <= b; i += step) idx.push(i);
  const pat = (info.pattern || info.frame_pattern || 'rgba/f_%04d.png').split(' ')[0];
  const name = (i) => pat.replace(/%0(\d)d/, (_, w) => String(i + (oneBased ? 1 : 0)).padStart(+w, '0'));
  const imgs = await Promise.all(idx.map((i) => loadImage(`${base}/${name(i)}`)));
  const bw = imgs[0].width, bh = imgs[0].height, sc = cellH / bh, cw = Math.round(bw * sc), ch = cellH;
  const cols = Math.max(1, Math.floor(8192 / cw)), rows = Math.ceil(imgs.length / cols);
  const cv = new OffscreenCanvas(cols * cw, rows * ch), g = cv.getContext('2d');
  imgs.forEach((im, k) => g.drawImage(im, (k % cols) * cw, Math.floor(k / cols) * ch, cw, ch));
  // her vertical extent (alpha bbox over a few frames) so world height is exact
  let top = ch, bot = 0;
  for (const k of [0, Math.floor(imgs.length / 2), imgs.length - 1]) {
    const d = g.getImageData((k % cols) * cw, Math.floor(k / cols) * ch, cw, ch).data;
    for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x += 2) if (d[(y * cw + x) * 4 + 3] > 128) { top = Math.min(top, y); bot = Math.max(bot, y); break; }
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.NoColorSpace; tex.generateMipmaps = true; tex.minFilter = THREE.LinearMipmapLinearFilter; tex.anisotropy = 4;
  const fb = info.baseline_y ?? info.feet_baseline_y;
  const feetY = fb != null ? fb * sc : bot;
  return { tex, cols, rows, n: imgs.length, fps: (info.fps || 24) / step, boxW: cw, boxH: ch, feetY, topY: top };
}

export class SpriteActor {
  // clips: { walkFront, walkBack, crank, idle } of loadSpriteClip results (any may be missing)
  constructor(eng, clips, { height = 1.3, strideWorld = 0.62, id = 88.8, pushConst = null } = {}) {
    this.eng = eng; this.clips = clips; this.height = height; this.strideWorld = strideWorld;
    this.root = new THREE.Group();
    this.pushConst = pushConst || { value: 0 };
    this.meshes = {};
    for (const [k, c] of Object.entries(clips)) {
      if (!c) continue;
      const m = eng.spriteMaterial({ atlas: c.tex, cols: c.cols, rows: c.rows, id: id + Object.keys(this.meshes).length * 0.37, pushConst: this.pushConst });
      const geo = new THREE.PlaneGeometry(1, 1); geo.translate(0, 0.5, 0);
      const mesh = new THREE.Mesh(geo, m);
      mesh.userData.noShadow = true; mesh.visible = false; mesh.frustumCulled = false;
      // scale so her body is `height` world units tall on screen, with the image aspect preserved
      const personPx = Math.max(10, c.feetY - c.topY);
      const Hq = height * c.boxH / personPx;               // quad height (world, vertical)
      const Wq = Hq * COS_EL * c.boxW / c.boxH;            // quad width so screen aspect = image aspect
      mesh.scale.set(Wq, Hq, 1);
      mesh.userData.feetOffset = (c.boxH - c.feetY) / c.boxH * Hq;   // quad bottom below the feet
      this.root.add(mesh);
      this.meshes[k] = mesh;
    }
    this.fallback = null;
    if (!this.meshes.walkFront) { this.fallback = makeFigure(eng, 'jade', { hairDown: true }); this.fallback.pushConst = this.pushConst; this.root.add(this.fallback.root); }
  }

  // pos: feet (world). dir: walking/facing direction (world xz). mode: 'walk' | 'crank' | 'idle'. dist: distance walked
  // (drives the walk cycle), t: seconds (drives crank/idle cycles). camAz: camera azimuth (rad).
  update({ pos, dir, mode = 'walk', dist = 0, t = 0, camAz = Math.PI / 4, gait = 1, push = 0 }) {
    this.pushConst.value = push;
    if (this.fallback) {
      const f = this.fallback;
      f.root.position.copy(pos); f.root.rotation.y = Math.atan2(dir.x, dir.z);
      f.pose(mode === 'walk' ? dist / 0.66 * Math.PI * 2 : t * 6, mode === 'walk' ? gait : 0.15, 0);
      return;
    }
    const right = new THREE.Vector3(Math.cos(camAz), 0, -Math.sin(camAz));
    const toCam = new THREE.Vector3(Math.sin(camAz), 0, Math.cos(camAz));
    const sx = dir.x * right.x + dir.z * right.z, front = dir.x * toCam.x + dir.z * toCam.z;
    let key, flip, frame;
    if (mode === 'walk' && gait > 0.05) {
      key = front >= -0.05 || !this.meshes.walkBack ? 'walkFront' : 'walkBack';
      flip = key === 'walkFront' ? sx < 0 : sx > 0;
      const c = this.clips[key];
      frame = (dist / this.strideWorld) * c.n;
    } else {
      key = mode === 'crank' && this.meshes.crank ? 'crank' : (this.meshes.idle ? 'idle' : (this.meshes.crank ? 'crank' : 'walkFront'));
      flip = sx < 0;
      const c = this.clips[key];
      frame = key === 'walkFront' ? 0 : t * c.fps;
    }
    for (const [k, m] of Object.entries(this.meshes)) m.visible = k === key;
    const m = this.meshes[key];
    // wrap by the clip's frame count, not the atlas cell count: cells past n are empty (v9: sprite blinked out)
    const n = this.clips[key].n;
    frame = ((Math.floor(frame) % n) + n) % n;
    this.eng.spriteFrame(m.material, frame, flip);
    m.position.set(pos.x, pos.y - m.userData.feetOffset, pos.z);
    m.rotation.set(0, camAz, 0);
  }
}

export async function loadJadeSprites(root = 'media/shots/E_sprites') {
  const tryLoad = async (n, o) => { try { return await loadSpriteClip(`${root}/${n}`, o); } catch (e) { return null; } };
  const pick = async (a, b) => (await tryLoad(a)) || (await tryLoad(b));
  const [walkFront, walkBack, crank] = await Promise.all([pick('walk_front', 'E_walk_front'), pick('walk_back', 'E_walk_back'), pick('crank', 'E_crank')]);
  return { walkFront, walkBack, crank };
}
