/**
 * =============================================================================
 *  AegisCore AI - MS4 Port Bridge / Transparent Proxy
 *  Bridges port 8000 (used by Angular MF1 frontend) to port 8004 (MS4 FastAPI)
 * =============================================================================
 */

const http = require('http');
const net = require('net');

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

// Soporte de actualización para WebSockets (ws://)
server.on('upgrade', (req, socket, head) => {
  const proxySocket = net.connect(TARGET_PORT, TARGET_HOST, () => {
    proxySocket.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      const key = req.rawHeaders[i];
      let val = req.rawHeaders[i + 1];
      if (key.toLowerCase() === 'host') {
        val = `${TARGET_HOST}:${TARGET_PORT}`;
      }
      proxySocket.write(`${key}: ${val}\r\n`);
    }
    proxySocket.write('\r\n');
    if (head && head.length > 0) {
      proxySocket.write(head);
    }
    proxySocket.pipe(socket);
    socket.pipe(proxySocket);
  });

  proxySocket.on('error', (err) => {
    console.error('[MS4-Bridge] WebSocket proxy error:', err.message);
    socket.destroy();
  });
  socket.on('error', () => {
    proxySocket.destroy();
  });
});

server.listen(LISTEN_PORT, '0.0.0.0', () => {
  console.log(`[MS4-Bridge] Active on http://127.0.0.1:${LISTEN_PORT} -> forwarding to http://${TARGET_HOST}:${TARGET_PORT}`);
});

