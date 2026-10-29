/**
 * =============================================================================
 *  AegisCore AI - MS4 Port Bridge / Transparent Proxy
 *  Bridges port 8000 (used by Angular MF1 frontend) to port 8004 (MS4 FastAPI)
 * =============================================================================
 */

const http = require('http');

const TARGET_HOST = '127.0.0.1';
const TARGET_PORT = 8004;
const LISTEN_PORT = 8000;

const server = http.createServer((req, res) => {
  const options = {
    hostname: TARGET_HOST,
    port: TARGET_PORT,
    path: req.url,
    method: req.method,
    headers: { ...req.headers }
  };

  // Ensure host header points to target
  options.headers['host'] = `${TARGET_HOST}:${TARGET_PORT}`;

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    console.error(`[MS4-Bridge] Error proxying ${req.method} ${req.url}:`, err.message);
    if (!res.headersSent) {
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: 'MS4 Gateway Connection Refused',
        message: 'Could not connect to MS4 backend on port 8004',
        details: err.message
      }));
    }
  });

  req.pipe(proxyReq, { end: true });
});

server.listen(LISTEN_PORT, '0.0.0.0', () => {
  console.log(`[MS4-Bridge] Active on http://127.0.0.1:${LISTEN_PORT} -> forwarding to http://${TARGET_HOST}:${TARGET_PORT}`);
});

