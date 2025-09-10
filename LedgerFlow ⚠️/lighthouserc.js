module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:5000/',
        'http://localhost:5000/login',
        'http://localhost:5000/generate',
        'http://localhost:5000/import',
        'http://localhost:5000/export',
        'http://localhost:5000/settings'
      ],
      startServerCommand: 'python app.py',
      startServerReadyPattern: 'Running on',
      startServerReadyTimeout: 30000,
      numberOfRuns: 3
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', {minScore: 0.8}],
        'categories:accessibility': ['error', {minScore: 0.9}],
        'categories:best-practices': ['warn', {minScore: 0.85}],
        'categories:seo': ['warn', {minScore: 0.8}],
        'categories:pwa': 'off'
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
};