// Headless renders of the F4 Bean mirror check (index.html) with the system Chrome on the GPU.
//   node tools/sectionF/f4_threejs/render.mjs --out DIR [--cases A,B,C] [--frames 0,20,40,52,60,70,76] [--modes 0,1,2]
//        [--w 960 --h 540] [--override '{"cam0":[0,7.5,22],"tilt":-4}']   (override: try other case fields, for the fit)
// Writes DIR/{case}_f{frame}_{mode}.png and DIR/poses.json. Run from the repo root.
import { createRequire } from 'module';
import { createServer } from 'http';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname, extname } from 'path';
import { fileURLToPath } from 'url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '../../..');
const require = createRequire(join(ROOT, 'render/engine/package.json'));
const { chromium } = require('playwright-core');

const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, all) => (x.startsWith('--') ? a.concat([[x.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]]) : a), []));
const OUT = args.out || join(HERE, 'out');
mkdirSync(OUT, { recursive: true });
const W = +(args.w || 960), H = +(args.h || 540);
const cases = String(args.cases || 'A,B,C').split(',');
const { FRAMES } = await import('./cases.js');
const fr = args.frames ? String(args.frames).split(',').map(Number) : FRAMES.map(f => f[0]);
const dists = fr.map(f => FRAMES.find(x => x[0] === f));   // [frame, fraction of the start distance]
const modes = String(args.modes || '0,1,2').split(',').map(Number);
const override = args.override ? JSON.parse(args.override) : null;   // fitting: replace case fields

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png' };
const srv = createServer((req, res) => {
  const p = join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
  res.end(readFileSync(p));
});
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const port = srv.address().port;

let browser, page;
async function open() {     // a busy GPU can lose the WebGL context: reopen and redo the view
  if (browser) await browser.close().catch(() => {});
  browser = await chromium.launch({ executablePath: '/opt/google/chrome/chrome', headless: true,
    args: ['--use-angle=vulkan', '--enable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan', '--disable-vulkan-surface',
           '--ignore-gpu-blocklist', '--enable-gpu', '--no-sandbox'] });
  page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) console.log('[page]', m.text()); });
  page.on('pageerror', e => console.log('[page error]', e.message));
  await page.goto(`http://127.0.0.1:${port}/tools/sectionF/f4_threejs/index.html?render=1&w=${W}&h=${H}`);
  await page.waitForFunction('window.ready === true', null, { timeout: 60000 });
  await new Promise(r => setTimeout(r, 300));
}
await open();

const poses = {};
for (const c of cases) for (const d of dists) for (const m of modes) {
  let r;
  for (let k = 0; k < 6; k++) {
    if (await page.evaluate('window.isLost()')) { console.log('[render] context lost, reopening'); await open(); continue; }
    r = await page.evaluate(([c, d, m, o]) => window.renderView({ case: c, frac: d[1], mode: m, ss: 2, override: o }), [c, d, m, override]);
    if (!(await page.evaluate('window.isLost()'))) break;
    console.log('[render] context lost, reopening'); await open(); r = null;
  }
  if (!r) throw new Error(`could not render ${c} ${d} ${m}`);
  writeFileSync(join(OUT, `${c}_f${String(d[0]).padStart(3, '0')}_${m}.png`), Buffer.from(r.url.split(',')[1], 'base64'));
  poses[`${c}_f${d[0]}`] = r.pose;
}
writeFileSync(join(OUT, 'poses.json'), JSON.stringify(poses, null, 1));
await browser.close();
srv.close();
console.log('wrote', Object.keys(poses).length, 'poses x', modes.length, 'modes to', OUT);
