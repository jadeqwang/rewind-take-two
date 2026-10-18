// Reflection maps for the F4 comp (tools/sectionF/f4_reflection_v10.py): for each F4 frame, the check's case at that
// frame's distance, rendered in mode 3 (where the mirror sends each pixel's ray onto the plane of her body).
//   node tools/sectionF/f4_threejs/refmap.mjs --case A --fracs '[[0,1.0],[1,0.99],...]' --out DIR [--box 480,200,1440,1080]
//        [--planefrac 0.21] [--ref REF.png]
// The picture plane: what the mirror sees of her at --planefrac (mirrorView in cases.js), kept for every frame.
// Writes DIR/map_{frame}.bin (float32 h x w x 3: picture x, y in metres, valid), DIR/maps.json (box, crown, soles per
// frame, the plane) and, with --ref, an orthographic pose reference of the mannequin seen along the plane's view
// direction (1600x1600, 2.4 m tall, centred on the plane anchor: pixel = 800 + (x, -y) * 1600 / 2.4).
import { createRequire } from 'module';
import { createServer } from 'http';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname, extname } from 'path';
import { fileURLToPath } from 'url';
import { CASES, mirrorView } from './cases.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '../../..');
const require = createRequire(join(ROOT, 'render/engine/package.json'));
const { chromium } = require('playwright-core');
const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, all) => (x.startsWith('--') ? a.concat([[x.slice(2), all[i + 1]]]) : a), []));
const OUT = args.out; mkdirSync(OUT, { recursive: true });
const fracs = JSON.parse(args.fracs);
const box = (args.box || '480,200,1440,1080').split(',').map(Number);
const W = 1920, H = 1080;

const srv = createServer((req, res) => {
  const p = join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': { '.html': 'text/html', '.js': 'text/javascript' }[extname(p)] || 'application/octet-stream' });
  res.end(readFileSync(p));
});
await new Promise(r => srv.listen(0, '127.0.0.1', r));
let browser, page;
async function open() {
  if (browser) await browser.close().catch(() => {});
  browser = await chromium.launch({ executablePath: '/opt/google/chrome/chrome', headless: true,
    args: ['--use-angle=vulkan', '--enable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan', '--disable-vulkan-surface',
           '--ignore-gpu-blocklist', '--enable-gpu', '--no-sandbox'] });
  page = await browser.newPage({ viewport: { width: 400, height: 300 } });
  page.on('pageerror', e => console.log('[page error]', e.message));
  await page.goto(`http://127.0.0.1:${srv.address().port}/tools/sectionF/f4_threejs/index.html?render=1&w=${W}&h=${H}`);
  await page.waitForFunction('window.ready === true', null, { timeout: 60000 });
  await new Promise(r => setTimeout(r, 300));
}
await open();
const plane = mirrorView(CASES[args.case || 'A'], +(args.planefrac || 0.21));
console.log('[refmap] plane: view', plane.fL.map(v => v.toFixed(3)), 'from camera row', plane.py);
if (args.ref) {
  await page.setViewportSize({ width: 1600, height: 1600 });
  await page.goto(`http://127.0.0.1:${srv.address().port}/tools/sectionF/f4_threejs/index.html?render=1&w=1600&h=1600`);
  await page.waitForFunction('window.ready === true', null, { timeout: 60000 });
  const url = await page.evaluate(([c, fr, pl]) => window.renderRef({ case: c, frac: fr, plane: pl, oscale: 2.4 }), [args.case || 'A', +(args.planefrac || 0.21), plane]);
  writeFileSync(args.ref, Buffer.from(url.split(',')[1], 'base64'));
  console.log('[refmap] wrote', args.ref);
  await open();
}
const meta = { plane };
for (const [f, frac] of fracs) {
  let r = null;
  for (let k = 0; k < 6 && !r; k++) {
    if (await page.evaluate('window.isLost()')) { await open(); continue; }
    r = await page.evaluate(([c, fr, b, pl]) => window.renderMap({ case: c, frac: fr, box: b, plane: pl }), [args.case || 'A', frac, box, plane]);
    if (await page.evaluate('window.isLost()')) { console.log('[refmap] context lost, retry', f); r = null; await open(); }
  }
  if (!r) throw new Error('could not render frame ' + f);
  writeFileSync(join(OUT, `map_${String(f).padStart(3, '0')}.bin`), Buffer.from(r.data, 'base64'));
  meta[f] = { frac, w: r.w, h: r.h, box: r.box, crown: r.crown, soles: r.soles, headc: r.headc };
}
writeFileSync(join(OUT, 'maps.json'), JSON.stringify(meta, null, 1));
await browser.close(); srv.close();
console.log('wrote', Object.keys(meta).length, 'maps to', OUT);
