#!/usr/bin/env node
// Headless GPU capture for render/three scenes. Zero npm dependencies: a tiny static server receives PNG
// frames POSTed by harness.html (capture mode) and headless Chrome renders on the GPU (ANGLE/Vulkan).
//
//   node tools/capture.mjs --scene penrose_loop --stills 1,4.2,8 --out ../../media/three_proto/stills_penrose
//   node tools/capture.mjs --scene penrose_loop --from 0 --to 10 --fps 24 --jobs 3 \
//        --out ../../media/three_proto/penrose_loop.mp4 [--crf 16] [--keep]
//   extra scene params: --p.orbit false   (passed through as p.orbit=false)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';

// minimal PNG writer for bottom-up RGBA (WebGL readPixels order) -> top-down RGB PNG
const CRC = new Int32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c; });
const crc32 = (b) => { let c = -1; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ -1) >>> 0; };
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type), data]);
  const c = Buffer.alloc(4); c.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, c]);
}
function encodePNG(rgba, w, h) {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  for (let y = 0; y < h; y++) {
    const src = (h - 1 - y) * w * 4, dst = y * (w * 3 + 1);
    raw[dst] = 0;
    for (let x = 0; x < w; x++) { raw[dst + 1 + x * 3] = rgba[src + x * 4]; raw[dst + 2 + x * 3] = rgba[src + x * 4 + 1]; raw[dst + 3 + x * 3] = rgba[src + x * 4 + 2]; }
  }
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw, { level: 3 })), chunk('IEND', Buffer.alloc(0))]);
}

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const args = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) { const k = argv[i].slice(2); const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : '1'; args[k] = v; }

const CHROME = process.env.CHROME || '/opt/google/chrome/chrome';
const FFMPEG = process.env.FFMPEG || path.join(process.env.HOME, 'Documents/moongazing/.venv/bin/ffmpeg');
const scene = args.scene || 'penrose_loop';
const W = +(args.w || 1920), H = +(args.h || 1080), FPS = +(args.fps || 24);
const JOBS = +(args.jobs || 1);
const isVideo = !args.stills;
const out = path.resolve(args.out || path.join(ROOT, '../../media/three_proto', isVideo ? `${scene}.mp4` : `stills_${scene}`));
const frameDir = isVideo ? (args.framedir ? path.resolve(args.framedir) : out.replace(/\.mp4$/, '') + '_frames') : out;
fs.mkdirSync(frameDir, { recursive: true });

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp' };
let done = 0, received = 0, lastProgress = Date.now();
const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://x');
  if (req.method === 'POST') {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => {
      const body = Buffer.concat(chunks);
      if (u.pathname === '/__frame') {
        const name = path.basename(u.searchParams.get('name'));
        const fw = +u.searchParams.get('w'), fh = +u.searchParams.get('h');
        fs.writeFileSync(path.join(frameDir, name), fw ? encodePNG(body, fw, fh) : body);
        received++; lastProgress = Date.now();
        if (received % 24 === 0 || !isVideo) process.stdout.write(`  ${received} frames\r`);
      } else if (u.pathname === '/__log') console.log('[page]', body.toString());
      else if (u.pathname === '/__done') { console.log('\n[done]', body.toString()); done++; }
      res.writeHead(200); res.end('ok');
    });
    return;
  }
  let p = decodeURIComponent(u.pathname); if (p === '/') p = '/harness.html';
  const file = path.join(ROOT, p);
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(data);
  });
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const port = server.address().port;

const extra = Object.entries(args).filter(([k]) => k.startsWith('p.')).map(([k, v]) => `&${k}=${encodeURIComponent(v)}`).join('');
const base = `http://127.0.0.1:${port}/harness.html?scene=${scene}&w=${W}&h=${H}&ss=${args.ss || 2}&capture=1${extra}${args.debug ? "&debug=1" : ""}`;
const procs = [];
const t0 = Date.now();
for (let j = 0; j < JOBS; j++) {
  const url = isVideo ? `${base}&from=${args.from || 0}&to=${args.to || 10}&fps=${FPS}&job=${j}&jobs=${JOBS}` : `${base}&stills=${args.stills}`;
  const prof = path.join(ROOT, `../../media/three_proto/.chrome/p${process.pid}_${j}`);
  fs.mkdirSync(prof, { recursive: true });
  const p = spawn(CHROME, ['--headless=new', '--no-sandbox', ...(process.env.ANGLE === 'vulkan' ? ['--use-angle=vulkan', '--enable-features=Vulkan'] : ['--use-angle=gl']), '--ignore-gpu-blocklist',
    '--enable-gpu', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', `--user-data-dir=${prof}`,
    `--window-size=${W},${H}`, '--hide-scrollbars', '--mute-audio', url], { stdio: ['ignore', 'ignore', 'pipe'] });
  p.stderr.on('data', (d) => { const s = d.toString(); if (/error/i.test(s) && !/dbus|Fontconfig|gcm|DEPRECATED|ALSA|bus\.cc|viz_main|sandbox/i.test(s)) process.stderr.write('[chrome] ' + s); });
  procs.push({ p, prof });
}
const need = isVideo ? JOBS : 1;
await new Promise((resolve, reject) => {
  const iv = setInterval(() => {
    if (done >= need) { clearInterval(iv); resolve(); }
    else if (Date.now() - lastProgress > +(args.timeout || 120) * 1000) { clearInterval(iv); reject(new Error('capture stalled')); }
  }, 200);
}).catch((e) => { console.error(e.message); });
await Promise.all(procs.map(({ p }) => new Promise((r) => { if (p.exitCode !== null) return r(); p.on('exit', r); p.kill('SIGKILL'); })));
await new Promise((r) => setTimeout(r, 300));
for (const { prof } of procs) { try { fs.rmSync(prof, { recursive: true, force: true, maxRetries: 5 }); } catch { /* profile cleanup is best effort */ } }
server.close();
console.log(`captured ${received} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s -> ${frameDir}`);

if (isVideo && received > 0 && !args.noenc) {
  const r = spawnSync(FFMPEG, ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frameDir, 'f_%05d.png'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', args.crf || '16', '-tune', 'grain', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: 'inherit' });
  console.log(r.status === 0 ? `wrote ${out}` : 'ffmpeg failed');
  if (r.status === 0 && !args.keep) fs.rmSync(frameDir, { recursive: true, force: true });
}
process.exit(0);
