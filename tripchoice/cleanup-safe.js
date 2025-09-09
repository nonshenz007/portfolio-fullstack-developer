#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function safeDelete(dirPath) {
    try {
        if (fs.existsSync(dirPath)) {
            const files = fs.readdirSync(dirPath);

            files.forEach((file) => {
                const curPath = path.join(dirPath, file);
                try {
                    if (fs.lstatSync(curPath).isDirectory()) {
                        safeDelete(curPath);
                    } else {
                        fs.unlinkSync(curPath);
                    }
                } catch (err) {
                    console.log(`⚠️  Skipping ${curPath}: ${err.message}`);
                }
            });

            fs.rmdirSync(dirPath);
            return true;
        }
    } catch (err) {
        console.log(`⚠️  Could not remove ${dirPath}: ${err.message}`);
        return false;
    }
    return false;
}

console.log('🧹 Safe cleanup of TripChoice project...');

const pathsToClean = [
    'node_modules',
    '.turbo'
];

pathsToClean.forEach(dirPath => {
    if (safeDelete(dirPath)) {
        console.log(`✅ Removed ${dirPath}`);
    } else {
        console.log(`⏭️  ${dirPath} already clean or protected`);
    }
});

console.log('✨ Safe cleanup complete!');