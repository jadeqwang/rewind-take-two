// server.mjs: static file server over the repo root (same origin, so canvases are never tainted) plus a PUT endpoint
// the page uses to hand finished frames straight to disk (no base64 round trip through CDP).
import { createServer } from 'node:http';
import { createReadStream, existsSync, statSync, writeFileSync, renameSync, mkdirSync, readdirSync } from 'node:fs';
import { resolve, extname, join, sep, basename } from 'node:path';

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.png': 'image/png', '.webp': 'image/webp', '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff2': 'font/woff2', '.woff': 'font/woff', '.mp3': 'audio/mpeg', '.svg': 'image/svg+xml' };

export async function serve(root, { verbose = false } = {}) {
  const sinks = new Map();   // token → directory
  const server = createServer((req, res) => {
    const path = decodeURIComponent(req.url.split('?')[0]);
    if (req.method === 'PUT' && path.startsWith('/__out/')) {
      const [, , token, name] = path.split('/');
      const dir = sinks.get(token);
      if (!dir || !/^[\w.-]+$/.test(name || '')) { res.writeHead(404); res.end(); return; }
      const chunks = [];
      req.on('data', c => chunks.push(c));
      req.on('end', () => {
        const f = join(dir, basename(name)), buf = Buffer.concat(chunks);
        writeFileSync(f + '.tmp', buf); renameSync(f + '.tmp', f);    // atomic: a killed render never leaves a half frame
        res.writeHead(200); res.end('ok');
      });
      return;
    }
    if (path.startsWith('/__ls/')) {   // directory listing for timeline functions (section files, EDLs)
      const d = resolve(root, '.' + path.slice(5));
      const ok = (d === root || d.startsWith(root + sep)) && existsSync(d) && statSync(d).isDirectory();
      res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' });
      res.end(JSON.stringify(ok ? readdirSync(d).filter(f => statSync(join(d, f)).isFile()).sort() : []));
      return;
    }
    const p = resolve(root, '.' + path);
    if (!(p === root || p.startsWith(root + sep)) || !existsSync(p) || statSync(p).isDirectory()) { if (verbose) console.log('404 ' + req.url); res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': MIME[extname(p).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
    createReadStream(p).pipe(res);
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  return {
    port, url: `http://127.0.0.1:${port}`, server,
    sink(token, dir) { mkdirSync(dir, { recursive: true }); sinks.set(token, dir); return `/__out/${token}/`; },
    close: () => new Promise(r => server.close(r)),
  };
}
