#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🎨 Checking Hero Setup...\n');

// Check hero images
const heroImages = [
  'hero-home-stunning.jpg',
  'hero-explore-stunning.jpg', 
  'hero-mountains-stunning.jpg',
  'hero-beach-stunning.jpg'
];

const imageDir = path.join(__dirname, 'apps/web/public/images');

console.log('📸 Hero Images Status:');
heroImages.forEach(img => {
  const imgPath = path.join(imageDir, img);
  if (fs.existsSync(imgPath)) {
    const stats = fs.statSync(imgPath);
    const sizeKB = Math.round(stats.size / 1024);
    console.log(`✅ ${img} - ${sizeKB}KB ${sizeKB > 100 ? '(Good size)' : '(Small - might be placeholder)'}`);
  } else {
    console.log(`❌ ${img} - MISSING`);
  }
});

// Check component files
console.log('\n🔧 Component Files:');
const componentFiles = [
  'apps/web/src/components/HeroMasthead.tsx',
  'apps/web/src/app/page.tsx',
  'apps/web/src/components/EditorialTile.tsx'
];

componentFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file.split('/').pop()}`);
  } else {
    console.log(`❌ ${file.split('/').pop()} - MISSING`);
  }
});

console.log('\n🚀 Next Steps:');
console.log('1. Start dev server: npm run dev');
console.log('2. Visit http://localhost:3000');
console.log('3. Check browser console for any image loading errors');
console.log('4. Look for the image status widget in top-right corner');

console.log('\n💡 If hero still looks like solid color:');
console.log('- Check browser network tab for failed image requests');
console.log('- Verify images exist in public/images/ folder');
console.log('- Check browser console for errors');
console.log('- Try hard refresh (Cmd+Shift+R / Ctrl+Shift+R)');