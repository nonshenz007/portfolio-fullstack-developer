#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function deleteRecursive(dirPath) {
  if (fs.existsSync(dirPath)) {
    const files = fs.readdirSync(dirPath);
    
    files.forEach((file) => {
      const curPath = path.join(dirPath, file);
      if (fs.lstatSync(curPath).isDirectory()) {
        deleteRecursive(curPath);
      } else {
        fs.unlinkSync(curPath);
      }
    });
    
    fs.rmdirSync(dirPath);
  }
}

console.log('🧹 Cleaning up TripChoice project...');

// Clean build artifacts
const pathsToClean = [
  'apps/web/.next',
  'apps/web/node_modules',
  'node_modules',
  'apps/web/.turbo',
  '.turbo'
];

pathsToClean.forEach(dirPath => {
  if (fs.existsSync(dirPath)) {
    console.log(`Removing ${dirPath}...`);
    deleteRecursive(dirPath);
    console.log(`✅ Removed ${dirPath}`);
  } else {
    console.log(`⏭️  ${dirPath} doesn't exist, skipping`);
  }
});

console.log('✨ Cleanup complete!');