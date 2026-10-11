#!/usr/bin/env node
// Screenshot the 1:30 car blockout (tools/v4B/car/car_scene.html) with headless Chrome, 960x540.
//   node tools/v4B/car/capture.mjs                       all stills of the plan -> media/reviews/v4/B/plans/car/
//   node tools/v4B/car/capture.mjs A:90.2 C:89.2:name    chosen stills (opt:songtime[:name][:extra query])
// Software GL (swiftshader), so it does not touch the shared GPU. No paid calls.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const require = createRequire(path.join(REPO, 'render/engine/package.json'));
const { chromium } = require('playwright-core');
const OUT = process.env.OUT || path.join(REPO, 'media/reviews/v4/B/plans/car');
const PLAN = [
  'A:90.18:A_1_start', 'A:91.06:A_2_cutin', 'A:92.74:A_3_end',
  'B:90.18:B_1_start', 'B:91.06:B_2_cutin', 'B:92.74:B_3_end',
  'C:90.18:C_1_start', 'C:91.35:C_2_mid', 'C:92.74:C_3_end',
  'A:92.74:X_true_plates:plates=true', 'A:90.18:X_plan_A:view=plan', 'B:90.18:X_plan_B:view=plan',
];
const jobs = (process.argv.length > 2 ? process.argv.slice(2) : PLAN).map((s) => { const [opt, t, name, extra] = s.split(':'); return { opt, t, name: name || `${opt}_${t}`, extra }; });
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.ttf': 'font/ttf', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const file = path.join(REPO, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(REPO)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(data);
  });
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/google/chrome/chrome',
  args: ['--headless=new', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
page.on('pageerror', (e) => console.error('[page]', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.error('[page]', m.text()); });
fs.mkdirSync(OUT, { recursive: true });
const infos = fs.existsSync(path.join(OUT, 'info.json')) ? JSON.parse(fs.readFileSync(path.join(OUT, 'info.json'), 'utf8')) : {};
for (const j of jobs) {
  await page.goto(`http://127.0.0.1:${server.address().port}/tools/v4B/car/car_scene.html?opt=${j.opt}&t=${j.t}${j.extra ? '&' + j.extra : ''}`);
  await page.waitForFunction('window.__ready === true', null, { timeout: 60000 });
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(OUT, `${j.name}.png`) });
  infos[j.name] = await page.evaluate('window.__info');
  console.log(j.name, JSON.stringify(infos[j.name]));
}
fs.writeFileSync(path.join(OUT, 'info.json'), JSON.stringify(infos, null, 1));
await browser.close(); server.close();
