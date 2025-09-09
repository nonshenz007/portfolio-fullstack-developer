#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting TripChoice development server (safe mode)...');

// Set environment variables for optimal performance
process.env.NODE_OPTIONS = '--max-old-space-size=4096';
process.env.NEXT_TELEMETRY_DISABLED = '1';
process.env.WATCHPACK_POLLING = 'true';

// Change to web app directory
process.chdir(path.join(__dirname, 'apps', 'web'));

// Start Next.js with optimized settings
const nextDev = spawn('npx', ['next', 'dev', '--port', '3000'], {
  stdio: 'inherit',
  env: {
    ...process.env,
    NODE_ENV: 'development',
    FORCE_COLOR: '1'
  }
});

// Handle process cleanup
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down development server...');
  nextDev.kill('SIGTERM');
  process.exit(0);
});

nextDev.on('close', (code) => {
  console.log(`\n✅ Development server exited with code ${code}`);
  process.exit(code);
});