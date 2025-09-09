#!/usr/bin/env node

/**
 * Directus Seed Data Import Script
 *
 * This script imports seed data into a Directus instance.
 * Make sure to set the following environment variables:
 * - DIRECTUS_URL: Your Directus instance URL
 * - DIRECTUS_TOKEN: Admin token for your Directus instance
 */

const fs = require('fs')
const path = require('path')

const DIRECTUS_URL = process.env.DIRECTUS_URL
const DIRECTUS_TOKEN = process.env.DIRECTUS_TOKEN

if (!DIRECTUS_URL || !DIRECTUS_TOKEN) {
  console.error('Please set DIRECTUS_URL and DIRECTUS_TOKEN environment variables')
  process.exit(1)
}

const SEED_DIR = path.join(__dirname, 'seed')

// Collections to import (in order of dependency)
const COLLECTIONS = [
  'packages',
  'itinerary_days',
  'variants',
  'price_rules',
  'inventory',
  'flash_sales',
  'reviews',
  'pages'
]

async function importCollection(collectionName) {
  const filePath = path.join(SEED_DIR, `${collectionName}.json`)

  if (!fs.existsSync(filePath)) {
    console.log(`Skipping ${collectionName} - file not found`)
    return
  }

  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'))

    console.log(`Importing ${data.length} items to ${collectionName}...`)

    // Import in batches to avoid timeout
    const batchSize = 10
    for (let i = 0; i < data.length; i += batchSize) {
      const batch = data.slice(i, i + batchSize)

      const response = await fetch(`${DIRECTUS_URL}/items/${collectionName}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${DIRECTUS_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(batch)
      })

      if (!response.ok) {
        const error = await response.text()
        console.error(`Failed to import batch ${i / batchSize + 1} for ${collectionName}:`, error)
      } else {
        console.log(`Imported batch ${i / batchSize + 1} for ${collectionName}`)
      }
    }

    console.log(`✅ Successfully imported ${collectionName}`)
  } catch (error) {
    console.error(`❌ Failed to import ${collectionName}:`, error.message)
  }
}

async function main() {
  console.log('🚀 Starting Directus seed data import...\n')

  for (const collection of COLLECTIONS) {
    await importCollection(collection)
    // Small delay between collections
    await new Promise(resolve => setTimeout(resolve, 1000))
  }

  console.log('\n🎉 Seed data import completed!')
  console.log('\nNext steps:')
  console.log('1. Review the imported data in your Directus admin panel')
  console.log('2. Upload images to the media library and update image references')
  console.log('3. Configure user roles and permissions')
  console.log('4. Set up your web application environment variables')
}

main().catch(console.error)
