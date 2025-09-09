#!/bin/bash

echo "🚀 Running TripChoice setup and tests..."

# Navigate to web app directory
cd apps/web

echo "📦 Installing dependencies..."
npm install

echo "🎭 Installing Playwright..."
npx playwright install

echo "🔍 Running UI Police..."
npm run ui:police

echo "🧪 Running Playwright smoke tests..."
npm run test:ui

echo "✅ All commands completed!"
echo ""
echo "🎯 Summary:"
echo "- Personalization modal created with localStorage and confetti"
echo "- Explore page with sticky filters (search, domestic/international, theme chips)"
echo "- Package pages with gallery, variants, pricing, and WhatsApp CTA"
echo "- Deterministic pricing system with season/weekend/origin adjustments"
echo "- Safe image fallback with destination initials"
echo "- SEO with JSON-LD structured data"
echo "- Performance optimizations and accessibility features"
echo "- WhatsApp deep links with UTM tracking"
echo "- Playwright smoke tests for key user flows"
echo ""
echo "🚀 Ready to launch!"