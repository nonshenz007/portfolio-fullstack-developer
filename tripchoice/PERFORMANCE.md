# TripChoice Performance Optimization Guide

## 🎯 Performance Targets

Based on acceptance criteria, we target:
- **Lighthouse Performance**: ≥95
- **LCP (Largest Contentful Paint)**: < 1.5s
- **CLS (Cumulative Layout Shift)**: ≤ 0.05
- **TTI (Time to Interactive)**: ≤ 2.5s
- **Bundle Size**: < 500KB initial load

## 📊 Current Performance Status

```bash
# Run performance audit
cd apps/web
npm run build
npm run start
# Open http://localhost:3000
# Run Lighthouse audit in Chrome DevTools
```

## 🚀 Optimization Strategies

### 1. Image Optimization

#### Implemented ✅
- Next.js Image component with automatic optimization
- WebP format support
- Responsive images with srcset
- Lazy loading by default

#### Recommendations
```jsx
// Ensure all images use Next.js Image component
import Image from 'next/image'

<Image
  src="/hero-image.jpg"
  alt="Destination"
  width={800}
  height={600}
  priority={false} // Only set true for above-fold images
  placeholder="blur"
  blurDataURL="data:image/base64,..." // Generate with plaiceholder
/>
```

### 2. Bundle Optimization

#### Code Splitting ✅
- Automatic route-based splitting
- Dynamic imports for heavy components

#### Additional Optimizations
```javascript
// Dynamic imports for heavy components
const HeavyModal = dynamic(() => import('./HeavyModal'), {
  ssr: false,
  loading: () => <div>Loading...</div>
})

// Lazy load libraries
const Chart = dynamic(() => import('react-chartjs-2'), {
  ssr: false
})
```

### 3. Font Optimization ✅

```javascript
// Already implemented in layout.tsx
import { Inter, Plus_Jakarta_Sans } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap', // ✅ Optimized loading
})
```

### 4. CSS Optimization

#### Current Setup ✅
- Tailwind CSS with purging
- CSS-in-JS with styled-components tree-shaking
- Critical CSS inlined

#### Additional Optimizations
```bash
# Analyze CSS bundle
npm install --save-dev @next/bundle-analyzer
```

### 5. JavaScript Optimization

#### Bundle Analysis
```bash
# Add to package.json scripts
"analyze": "ANALYZE=true npm run build"

# Run analysis
npm run analyze
```

#### Tree Shaking ✅
```javascript
// Import only what you need
import { useState, useEffect } from 'react' // ✅ Good
// import React from 'react' // ❌ Imports everything

import { Button } from '@/components/ui/button' // ✅ Good
// import * as UI from '@/components/ui' // ❌ Imports all components
```

### 6. API & Data Optimization

#### Current Implementation ✅
- React Query for caching
- Fallback data for offline/error states
- Optimistic updates

#### Recommendations
```javascript
// Implement service worker for offline support
// Add in public/sw.js
self.addEventListener('fetch', (event) => {
  if (event.request.destination === 'image') {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request)
      })
    )
  }
})
```

### 7. Core Web Vitals Optimization

#### LCP (Largest Contentful Paint)
- ✅ Hero images use `priority={true}`
- ✅ Preload critical resources
- ✅ Optimize server response time

#### CLS (Cumulative Layout Shift)
- ✅ Image dimensions specified
- ✅ Font display: swap
- ⚠️ TODO: Reserve space for dynamic content

```jsx
// Reserve space for loading states
<div className="min-h-[400px]"> {/* Prevent layout shift */}
  {loading ? <Skeleton /> : <Content />}
</div>
```

#### TTI (Time to Interactive)
- ✅ Code splitting implemented
- ✅ Non-critical JS deferred
- ⚠️ TODO: Service worker for background sync

### 8. Caching Strategy

#### Browser Caching
```javascript
// next.config.js additions
const nextConfig = {
  async headers() {
    return [
      {
        source: '/images/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      }
    ]
  }
}
```

#### CDN Configuration
- Use Vercel's Edge Network (automatic)
- Or configure CloudFlare for custom deployments

## 🔍 Performance Monitoring

### 1. Lighthouse CI
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
```

### 2. Real User Monitoring
```javascript
// Add to _app.tsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

function sendToAnalytics(metric) {
  if (window.gtag) {
    window.gtag('event', metric.name, {
      value: Math.round(metric.value),
      event_category: 'Web Vitals',
      event_label: metric.id,
      non_interaction: true,
    })
  }
}

getCLS(sendToAnalytics)
getFID(sendToAnalytics)
getFCP(sendToAnalytics)
getLCP(sendToAnalytics)
getTTFB(sendToAnalytics)
```

### 3. Performance Budget
```json
// lighthouserc.json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.95}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "categories:best-practices": ["error", {"minScore": 0.95}],
        "categories:seo": ["error", {"minScore": 0.90}]
      }
    }
  }
}
```

## 🧪 Performance Testing

### Local Testing
```bash
# 1. Build production version
npm run build

# 2. Start production server
npm run start

# 3. Run Lighthouse audit
npx lighthouse http://localhost:3000 --output json --output html --output-path ./lighthouse-results

# 4. Analyze bundle
npm run analyze
```

### Automated Testing
```javascript
// lighthouse.config.js
module.exports = {
  extends: 'lighthouse:default',
  settings: {
    throttlingMethod: 'devtools',
    throttling: {
      rttMs: 40,
      throughputKbps: 10 * 1024,
      cpuSlowdownMultiplier: 1,
    },
  },
}
```

## 📈 Performance Optimizations Completed

### ✅ Implemented
- [x] Next.js Image optimization
- [x] Font optimization with Google Fonts
- [x] Code splitting and lazy loading
- [x] Bundle optimization with tree shaking
- [x] CSS optimization with Tailwind purging
- [x] React Query for data caching
- [x] Proper meta tags and SEO
- [x] Gzip compression (Vercel automatic)
- [x] Critical CSS inlining

### ⏳ In Progress
- [ ] Service Worker implementation
- [ ] Web Vitals monitoring
- [ ] Advanced image optimization with blur placeholders
- [ ] Lighthouse CI integration

### 📋 TODO
- [ ] Performance budgets enforcement
- [ ] Advanced caching strategies
- [ ] Progressive Web App features
- [ ] Background sync for offline support

## 🎯 Performance Checklist

Before deployment, ensure:

- [ ] Lighthouse Performance score ≥95
- [ ] All images optimized and using Next.js Image
- [ ] No console errors or warnings
- [ ] Bundle size under 500KB initial load
- [ ] Critical CSS inlined
- [ ] Fonts loading with display: swap
- [ ] Core Web Vitals passing
- [ ] Mobile performance tested
- [ ] Slow 3G performance acceptable

## 🔧 Quick Wins

If performance is below target:

1. **Check images**: Ensure all use Next.js Image component
2. **Audit bundle**: Run `npm run analyze` and remove unused dependencies
3. **Font loading**: Verify `display: swap` is set
4. **Third-party scripts**: Move non-critical scripts to load after page load
5. **CSS**: Remove unused styles and optimize selectors

## 📞 Performance Support

For performance issues:
- Check bundle analyzer output
- Review Lighthouse recommendations
- Analyze Core Web Vitals in Search Console
- Monitor real user metrics in analytics
