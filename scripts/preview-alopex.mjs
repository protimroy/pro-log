import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { dirname, extname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../build');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf' };
const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    if (!url.pathname.startsWith('/pro-log/')) return response.writeHead(404).end();
    const path = decodeURIComponent(url.pathname.slice('/pro-log/'.length));
    let target = resolve(root, path);
    if (target !== root && !target.startsWith(root + sep)) return response.writeHead(403).end();
    if (!extname(target)) target = join(target, 'index.html');
    const data = await readFile(target);
    response.writeHead(200, { 'Content-Type': types[extname(target)] || 'application/octet-stream' });
    response.end(data);
  } catch {
    response.writeHead(404).end();
  }
});
const port = Number(process.env.PORT || 8553);
server.listen(port, '127.0.0.1', () => console.log(`Pro-log preview: http://127.0.0.1:${port}/pro-log/`));