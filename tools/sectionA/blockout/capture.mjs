#!/usr/bin/env node
// Screenshot the D7/D8 staging blockout (tools/sectionA/blockout/id_scene.html) with headless Chrome.
//   node tools/sectionA/blockout/capture.mjs D7b media/shots/D7/blockout_D7b.png [--overlay] [--rect=150,850,1620,190]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const require = createRequire(path.join(REPO, 'render/engine/package.json'));
const { chromium } = require('playwright-core');
const [shot, out, ...rest] = process.argv.slice(2);
const overlay = rest.includes('--overlay');
const rect = (rest.find((a) => a.startsWith('--rect=')) || '').slice(7);
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const file = path.join(REPO, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(REPO)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' }); res.end(data);
  });
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/google/chrome/chrome',
  args: ['--headless=new', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', (e) => console.error('[page]', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.error('[page]', m.text()); });
await page.goto(`http://127.0.0.1:${server.address().port}/tools/sectionA/blockout/id_scene.html?shot=${shot}${overlay ? '&overlay=1' : ''}${rect ? '&rect=' + rect : ''}`);
await page.waitForFunction('window.__ready === true', null, { timeout: 30000 });
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
await page.screenshot({ path: out });
await browser.close(); server.close();
console.log('wrote', out);
