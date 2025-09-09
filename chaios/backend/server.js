// Simple Express server for ChaiOS backend
const express = require('express');
const cors = require('cors');
const path = require('path');

function createServer() {
  const app = express();
  app.use(cors());
  app.use(express.json());

  // Health check
  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  // Version from package.json
  app.get('/version', (_req, res) => {
    try {
      // eslint-disable-next-line import/no-dynamic-require, global-require
      const pkg = require(path.join(__dirname, 'package.json'));
      res.json({ name: pkg.name, version: pkg.version });
    } catch (err) {
      res.status(500).json({ error: 'version_unavailable' });
    }
  });

  // Placeholder API root
  app.get('/', (_req, res) => {
    res.json({ message: 'ChaiOS backend API' });
  });

  // Simple license validation endpoint (mock)
  app.post('/license/validate', (req, res) => {
    try {
      const { key } = req.body || {};
      if (!key || typeof key !== 'string') {
        return res.status(400).json({ valid: false, reason: 'missing_key' });
      }
      // Extremely naive mock validation
      const valid = key.trim().toUpperCase().startsWith('CHAI-');
      const days = valid ? 30 : 0;
      const expiry = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
      return res.json({ valid, expiry: expiry.toISOString() });
    } catch (err) {
      return res.status(500).json({ valid: false, reason: 'server_error' });
    }
  });

  return app;
}

if (require.main === module) {
  const port = process.env.PORT || 8080;
  const app = createServer();
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`ChaiOS backend running on http://localhost:${port}`);
  });
}

module.exports = { createServer };


