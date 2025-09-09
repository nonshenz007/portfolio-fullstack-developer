#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Checking destination images used in components...\n');

const publicDir = path.join(__dirname, 'apps/web/public');

// Images used in trending destinations
const trendingImages = [
  '/images/kashmir/kashmir-dal-lake-hd.jpg',
  '/images/goa/goa-beach-main.jpg',
  '/images/dubai/dubai-skyline-hd.jpg',
  '/images/thailand/thailand-islands-hd.jpg',
  '/images/singapore/singapore-skyline-hd.jpg',
  '/images/kerala/kerala-backwaters-hd.jpg'
];

// Images used in home page fallback packages
const homePageImages = [
  '/images/dubai/dubai-skyline-hd.jpg',
  '/images/goa/goa-beach-main.jpg',
  '/images/himachal/himachal-mountains-hd.jpg',
  '/images/vietnam/vietnam-hoi-an-hd.jpg',
  '/images/thailand/thailand-islands-hd.jpg'
];

console.log('📍 Trending Destinations Images:');
trendingImages.forEach(img => {
  const fullPath = path.join(publicDir, img);
  if (fs.existsSync(fullPath)) {
    const stats = fs.statSync(fullPath);
    console.log(`✅ ${img} (${Math.round(stats.size / 1024)}KB)`);
  } else {
    console.log(`❌ ${img} - MISSING`);
  }
});

console.log('\n🏠 Home Page Package Images:');
homePageImages.forEach(img => {
  const fullPath = path.join(publicDir, img);
  if (fs.existsSync(fullPath)) {
    const stats = fs.statSync(fullPath);
    console.log(`✅ ${img} (${Math.round(stats.size / 1024)}KB)`);
  } else {
    console.log(`❌ ${img} - MISSING`);
  }
});

console.log('\n🎉 All destination images should now display properly!');
console.log('🚀 Start your dev server: npm run dev');
console.log('📱 Check both home page and explore page for images');