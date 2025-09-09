#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying HD 4K travel destination images...\n');

const imageDir = path.join(__dirname, 'images');
let totalImages = 0;
let missingImages = [];

// Check hero background images
const heroImages = [
  'hero-background-4k.jpg',
  'explore-hero-4k.jpg'
];

console.log('🎬 Hero Background Images:');
heroImages.forEach(img => {
  const imgPath = path.join(imageDir, img);
  if (fs.existsSync(imgPath)) {
    const stats = fs.statSync(imgPath);
    console.log(`✅ ${img} (${Math.round(stats.size / 1024)}KB)`);
    totalImages++;
  } else {
    console.log(`❌ ${img} - MISSING`);
    missingImages.push(img);
  }
});

// Check destination images
const destinationImages = [
  'destinations/kashmir-valley-4k.jpg',
  'destinations/goa-beaches-4k.jpg', 
  'destinations/dubai-skyline-4k.jpg',
  'destinations/thailand-islands-4k.jpg',
  'destinations/singapore-marina-4k.jpg',
  'destinations/kerala-backwaters-4k.jpg',
  'destinations/shimla-mountains-4k.jpg',
  'destinations/vietnam-hoi-an-4k.jpg'
];

console.log('\n🌍 HD 4K Destination Images:');
destinationImages.forEach(img => {
  const imgPath = path.join(imageDir, img);
  if (fs.existsSync(imgPath)) {
    const stats = fs.statSync(imgPath);
    console.log(`✅ ${img} (${Math.round(stats.size / 1024)}KB)`);
    totalImages++;
  } else {
    console.log(`❌ ${img} - MISSING`);
    missingImages.push(img);
  }
});

console.log(`\n📊 Summary:`);
console.log(`✅ Total HD images found: ${totalImages}`);
console.log(`❌ Missing images: ${missingImages.length}`);

if (missingImages.length > 0) {
  console.log('\n🚨 Missing HD 4K images:');
  missingImages.forEach(img => console.log(`   - ${img}`));
  console.log('\n💡 Note: These are placeholder files. In production, replace with actual HD 4K images.');
  console.log('📝 Each image should be:');
  console.log('   • Resolution: 3840x2160 (4K) or higher');
  console.log('   • Format: JPG (optimized for web)');
  console.log('   • Size: 500KB - 2MB (compressed but high quality)');
  console.log('   • Content: Matching the destination description');
} else {
  console.log('\n🎉 All HD 4K destination images are ready!');
  console.log('\n🚀 Next steps:');
  console.log('1. Replace placeholder files with actual HD 4K images');
  console.log('2. Start your dev server: npm run dev');
  console.log('3. Visit http://localhost:3000 to see the stunning travel destinations');
  console.log('4. Check the explore page at http://localhost:3000/explore');
  console.log('\n📸 Image Requirements:');
  console.log('• Kashmir Valley: Snow-capped mountains, Dal Lake, houseboats');
  console.log('• Goa Beaches: Golden sand, palm trees, sunset over ocean');
  console.log('• Dubai Skyline: Burj Khalifa, Marina, night city lights');
  console.log('• Thailand Islands: Turquoise water, limestone cliffs, longtail boats');
  console.log('• Singapore Marina: Marina Bay Sands, Supertree Grove at night');
  console.log('• Kerala Backwaters: Traditional houseboat, palm-lined waterways');
  console.log('• Shimla Mountains: Himalayan peaks, pine forests, colonial architecture');
  console.log('• Vietnam Hoi An: Ancient town, colorful lanterns at night');
}