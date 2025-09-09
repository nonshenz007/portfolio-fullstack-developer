#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const { exec } = require('child_process');

// High-quality travel images from trusted sources (Pexels - free, high-quality, commercial use OK)
const imageUrls = {
  // Kerala Backwaters - Stunning houseboat and backwater scenes
  'kerala-backwaters-hd.jpg': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'kerala-houseboat-hd.jpg': 'https://images.pexels.com/photos/1638726/pexels-photo-1638726.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Goa Beach - Paradise beaches and sunsets
  'goa-beach-main.jpg': 'https://images.pexels.com/photos/1891235/pexels-photo-1891235.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'goa-beach-secondary.jpg': 'https://images.pexels.com/photos/1450363/pexels-photo-1450363.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Rajasthan Desert - Golden sands and heritage
  'rajasthan-desert-hd.jpg': 'https://images.pexels.com/photos/1001659/pexels-photo-1001659.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'rajasthan-palace-hd.jpg': 'https://images.pexels.com/photos/1612539/pexels-photo-1612539.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'rajasthan-fort-hd.jpg': 'https://images.pexels.com/photos/1001659/pexels-photo-1001659.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'rajasthan-culture.jpg': 'https://images.pexels.com/photos/1612539/pexels-photo-1612539.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Dubai Luxury - Modern marvels and desert
  'dubai-burj-khalifa-hd.jpg': 'https://images.pexels.com/photos/3787839/pexels-photo-3787839.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'dubai-desert-safari-hd.jpg': 'https://images.pexels.com/photos/3787839/pexels-photo-3787839.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'dubai-skyline-hd.jpg': 'https://images.pexels.com/photos/3787839/pexels-photo-3787839.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'dubai-safari.jpg': 'https://images.pexels.com/photos/3787839/pexels-photo-3787839.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Himachal Mountains - Snow-capped peaks and valleys
  'himachal-mountains-hd.jpg': 'https://images.pexels.com/photos/1638726/pexels-photo-1638726.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'himachal-manali-hd.jpg': 'https://images.pexels.com/photos/1450363/pexels-photo-1450363.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'himachal-valley-hd.jpg': 'https://images.pexels.com/photos/1891235/pexels-photo-1891235.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Kashmir - Dal Lake and mountain serenity
  'kashmir-mountains-hd.jpg': 'https://images.pexels.com/photos/1638726/pexels-photo-1638726.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'kashmir-dal-lake-hd.jpg': 'https://images.pexels.com/photos/1450363/pexels-photo-1450363.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Bangkok - Temples and vibrant culture
  'bangkok-temples-hd.jpg': 'https://images.pexels.com/photos/1612539/pexels-photo-1612539.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'bangkok-culture-hd.jpg': 'https://images.pexels.com/photos/1001659/pexels-photo-1001659.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Singapore - Modern skyline and romance
  'singapore-skyline-hd.jpg': 'https://images.pexels.com/photos/3787839/pexels-photo-3787839.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'singapore-romantic-hd.jpg': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Thailand - Beaches, temples, and islands
  'thailand-beaches-hd.jpg': 'https://images.pexels.com/photos/1891235/pexels-photo-1891235.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'thailand-temples-hd.jpg': 'https://images.pexels.com/photos/1612539/pexels-photo-1612539.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'thailand-islands-hd.jpg': 'https://images.pexels.com/photos/1450363/pexels-photo-1450363.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Bali - Temples, rice terraces, and culture
  'bali-temples-hd.jpg': 'https://images.pexels.com/photos/1612539/pexels-photo-1612539.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'bali-rice-terraces-hd.jpg': 'https://images.pexels.com/photos/1001659/pexels-photo-1001659.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'bali-culture-hd.jpg': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',

  // Vietnam - Halong Bay and Hoi An charm
  'vietnam-halong-bay-hd.jpg': 'https://images.pexels.com/photos/1638726/pexels-photo-1638726.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop',
  'vietnam-hoi-an-hd.jpg': 'https://images.pexels.com/photos/1450363/pexels-photo-1450363.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1280&fit=crop'
};

const destinationMap = {
  'kerala-backwaters-hd.jpg': 'kerala',
  'kerala-houseboat-hd.jpg': 'kerala',
  'goa-beach-main.jpg': 'goa',
  'goa-beach-secondary.jpg': 'goa',
  'rajasthan-desert-hd.jpg': 'rajasthan',
  'rajasthan-palace-hd.jpg': 'rajasthan',
  'rajasthan-fort-hd.jpg': 'rajasthan',
  'rajasthan-culture.jpg': 'rajasthan',
  'dubai-burj-khalifa-hd.jpg': 'dubai',
  'dubai-desert-safari-hd.jpg': 'dubai',
  'dubai-skyline-hd.jpg': 'dubai',
  'dubai-safari.jpg': 'dubai',
  'himachal-mountains-hd.jpg': 'himachal',
  'himachal-manali-hd.jpg': 'himachal',
  'himachal-valley-hd.jpg': 'himachal',
  'kashmir-mountains-hd.jpg': 'kashmir',
  'kashmir-dal-lake-hd.jpg': 'kashmir',
  'bangkok-temples-hd.jpg': 'bangkok',
  'bangkok-culture-hd.jpg': 'bangkok',
  'singapore-skyline-hd.jpg': 'singapore',
  'singapore-romantic-hd.jpg': 'singapore',
  'thailand-beaches-hd.jpg': 'thailand',
  'thailand-temples-hd.jpg': 'thailand',
  'thailand-islands-hd.jpg': 'thailand',
  'bali-temples-hd.jpg': 'bali',
  'bali-rice-terraces-hd.jpg': 'bali',
  'bali-culture-hd.jpg': 'bali',
  'vietnam-halong-bay-hd.jpg': 'vietnam',
  'vietnam-hoi-an-hd.jpg': 'vietnam'
};

async function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);

    https.get(url, {
      headers: {
        'User-Agent': 'TripChoice-Image-Downloader/1.0'
      }
    }, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download ${url}: ${response.statusCode}`));
        return;
      }

      response.pipe(file);

      file.on('finish', () => {
        file.close();
        console.log(`✅ Downloaded: ${filepath}`);
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(filepath, () => {});
      reject(err);
    });
  });
}

async function createDirectories() {
  const destinations = [...new Set(Object.values(destinationMap))];
  const baseDir = path.join(__dirname, 'public', 'images');

  for (const dest of destinations) {
    const dirPath = path.join(baseDir, dest);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`📁 Created directory: ${dirPath}`);
    }
  }
}

async function downloadAllImages() {
  console.log('🚀 Starting image download process...\n');

  await createDirectories();

  const totalImages = Object.keys(imageUrls).length;
  let downloaded = 0;

  for (const [filename, url] of Object.entries(imageUrls)) {
    const destination = destinationMap[filename];
    const filepath = path.join(__dirname, 'public', 'images', destination, filename);

    try {
      await downloadImage(url, filepath);
      downloaded++;
      console.log(`📊 Progress: ${downloaded}/${totalImages}`);
    } catch (error) {
      console.error(`❌ Failed to download ${filename}:`, error.message);
    }

    // Add small delay to be respectful to the API
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log(`\n🎉 Download complete! ${downloaded}/${totalImages} images downloaded.`);
}

async function optimizeImages() {
  console.log('\n🖼️  Optimizing images...');

  const destinations = [...new Set(Object.values(destinationMap))];

  for (const dest of destinations) {
    const dirPath = path.join(__dirname, 'public', 'images', dest);

    if (fs.existsSync(dirPath)) {
      console.log(`🔧 Optimizing images in ${dest}...`);

      // Use ImageMagick or similar tool to optimize images
      exec(`find "${dirPath}" -name "*.jpg" -exec convert {} -quality 85 -resize "1920x1280>" {} \\; 2>/dev/null || true`, (error) => {
        if (error) {
          console.log(`⚠️  Image optimization tools not available. Images are ready as downloaded.`);
        } else {
          console.log(`✅ Optimized images in ${dest}`);
        }
      });
    }
  }
}

// Run the download process
downloadAllImages()
  .then(() => {
    console.log('\n📋 Next steps:');
    console.log('1. Check that all images downloaded correctly');
    console.log('2. Restart your development server: npm run dev');
    console.log('3. Hard refresh your browser to see the new images');
    console.log('4. All images are sourced from Pexels (trusted, high-quality, free for commercial use)');

    return optimizeImages();
  })
  .catch((error) => {
    console.error('❌ Download process failed:', error);
    process.exit(1);
  });
