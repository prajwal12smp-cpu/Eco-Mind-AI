import express from 'express';
import path from 'path';
import { spawn, ChildProcess } from 'child_process';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();
const PORT = 3000;
const PYTHON_PORT = 8001;

let pythonProcess: ChildProcess | null = null;

function startPythonBackend() {
  console.log(`[EcoMind Server] Starting Python FastAPI backend on port ${PYTHON_PORT}...`);
  pythonProcess = spawn('python3', [
    '-m', 'uvicorn',
    'backend.app.main:app',
    '--host', '127.0.0.1',
    '--port', String(PYTHON_PORT)
  ], {
    stdio: 'inherit',
    env: { ...process.env, PYTHONPATH: '.' }
  });

  pythonProcess.on('error', (err) => {
    console.error('[EcoMind Server] Failed to spawn Python backend:', err);
  });

  pythonProcess.on('exit', (code, signal) => {
    console.log(`[EcoMind Server] Python backend exited (code ${code}, signal ${signal})`);
  });
}

startPythonBackend();

function cleanup() {
  if (pythonProcess && !pythonProcess.killed) {
    try {
      pythonProcess.kill('SIGTERM');
    } catch {
      // ignore
    }
  }
}

process.on('exit', cleanup);
process.on('SIGINT', () => {
  cleanup();
  process.exit();
});
process.on('SIGTERM', () => {
  cleanup();
  process.exit();
});

// Proxy /api requests to FastAPI backend on port 8001
app.use(
  '/api',
  createProxyMiddleware({
    target: `http://127.0.0.1:${PYTHON_PORT}`,
    changeOrigin: true,
  })
);

async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[EcoMind Server] Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
