# Lighthouse CI Setup & Performance Monitoring

## Overview

This document provides comprehensive setup instructions for Lighthouse CI integration, performance budgets, automated accessibility testing, and visual regression coverage for the premium UI redesign. The configuration ensures continuous monitoring of Core Web Vitals and accessibility compliance.

## Lighthouse CI Configuration

### Installation & Setup

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Install as dev dependency for project
npm install --save-dev @lhci/cli
```

### Lighthouse CI Configuration File

Create `lighthouserc.js` in project root:

```javascript
module.exports = {
  ci: {
    collect: {
      // URLs to test
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/explore',
        'http://localhost:3000/package/kashmir-valley',
        'http://localhost:3000/collections/weekend',
      ],
      // Collection settings
      numberOfRuns: 3,
      settings: {
        // Chrome flags for consistent testing
        chromeFlags: [
          '--no-sandbox',
          '--headless',
          '--disable-gpu',
          '--disable-dev-shm-usage',
          '--disable-extensions',
          '--no-first-run',
          '--disable-default-apps',
        ],
        // Throttling settings
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0,
        },
        // Screen emulation
        screenEmulation: {
          mobile: false,
          width: 1350,
          height: 940,
          deviceScaleFactor: 1,
          disabled: false,
        },
      },
    },
    assert: {
      // Performance budgets
      assertions: {
        // Core Web Vitals
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'first-input-delay': ['error', { maxNumericValue: 100 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        
        // Lighthouse scores
        'categories:performance': ['error', { minScore: 0.95 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.90 }],
        'categories:seo': ['error', { minScore: 0.95 }],
        
        // Specific metrics for premium experience
        'speed-index': ['error', { maxNumericValue: 3000 }],
        'interactive': ['error', { maxNumericValue: 3500 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }],
        
        // Resource budgets
        'resource-summary:document:size': ['error', { maxNumericValue: 50000 }],
        'resource-summary:image:size': ['error', { maxNumericValue: 2000000 }], // 2MB
        'resource-summary:script:size': ['error', { maxNumericValue: 500000 }],
        'resource-summary:stylesheet:size': ['error', { maxNumericValue: 100000 }],
        
        // Network requests
        'resource-summary:total:count': ['warn', { maxNumericValue: 100 }],
        'resource-summary:image:count': ['warn', { maxNumericValue: 30 }],
        
        // Accessibility specific
        'color-contrast': 'error',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',
        'button-name': 'error',
        'document-title': 'error',
        'html-has-lang': 'error',
        'html-lang-valid': 'error',
        'meta-viewport': 'error',
        'aria-allowed-attr': 'error',
        'aria-required-attr': 'error',
        'aria-valid-attr-value': 'error',
        'aria-valid-attr': 'error',
        'heading-order': 'error',
        'landmark-one-main': 'error',
        'list': 'error',
        'listitem': 'error',
        'definition-list': 'error',
        'dlitem': 'error',
        'bypass': 'error',
        'focus-traps': 'error',
        'focusable-controls': 'error',
        'interactive-element-affordance': 'error',
        'logical-tab-order': 'error',
        'managed-focus': 'error',
        'offscreen-content-hidden': 'error',
        'use-landmarks': 'error',
        'visual-order-follows-dom': 'error',
      },
    },
    upload: {
      target: 'temporary-public-storage',
      // For production, use LHCI server or GitHub integration
      // target: 'lhci',
      // serverBaseUrl: 'https://your-lhci-server.com',
      // token: process.env.LHCI_TOKEN,
    },
  },
};
```

### Mobile Configuration

Create `lighthouserc.mobile.js` for mobile testing:

```javascript
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/explore',
        'http://localhost:3000/package/kashmir-valley',
      ],
      numberOfRuns: 3,
      settings: {
        chromeFlags: [
          '--no-sandbox',
          '--headless',
          '--disable-gpu',
          '--disable-dev-shm-usage',
        ],
        // Mobile emulation
        screenEmulation: {
          mobile: true,
          width: 375,
          height: 667,
          deviceScaleFactor: 2,
          disabled: false,
        },
        // Mobile throttling
        throttling: {
          rttMs: 150,
          throughputKbps: 1638,
          cpuSlowdownMultiplier: 4,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0,
        },
      },
    },
    assert: {
      assertions: {
        // Adjusted mobile budgets
        'largest-contentful-paint': ['error', { maxNumericValue: 3000 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'first-input-delay': ['error', { maxNumericValue: 100 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2200 }],
        'speed-index': ['error', { maxNumericValue: 4000 }],
        'interactive': ['error', { maxNumericValue: 5000 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
        
        // Mobile-specific scores
        'categories:performance': ['error', { minScore: 0.90 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.90 }],
        'categories:seo': ['error', { minScore: 0.95 }],
      },
    },
  },
};
```

## Package.json Scripts

Add these scripts to `package.json`:

```json
{
  "scripts": {
    "lhci:collect": "lhci collect",
    "lhci:assert": "lhci assert",
    "lhci:upload": "lhci upload",
    "lhci:full": "lhci collect && lhci assert && lhci upload",
    "lhci:mobile": "lhci collect --config=lighthouserc.mobile.js && lhci assert --config=lighthouserc.mobile.js",
    "performance:test": "npm run build && npm run start & sleep 10 && npm run lhci:full && kill %1",
    "performance:mobile": "npm run build && npm run start & sleep 10 && npm run lhci:mobile && kill %1"
  }
}
```

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/lighthouse-ci.yml`:

```yaml
name: Lighthouse CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lighthouse-ci:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build application
        run: npm run build
        
      - name: Start application
        run: npm start &
        
      - name: Wait for application
        run: sleep 10
        
      - name: Run Lighthouse CI (Desktop)
        run: |
          npm install -g @lhci/cli
          lhci collect --numberOfRuns=3
          lhci assert
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
          
      - name: Run Lighthouse CI (Mobile)
        run: lhci collect --config=lighthouserc.mobile.js && lhci assert --config=lighthouserc.mobile.js
        
      - name: Upload results
        run: lhci upload
        env:
          LHCI_TOKEN: ${{ secrets.LHCI_TOKEN }}
          
      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const path = require('path');
            
            // Read Lighthouse results
            const resultsPath = '.lighthouseci/';
            if (fs.existsSync(resultsPath)) {
              const files = fs.readdirSync(resultsPath);
              const reportFile = files.find(f => f.endsWith('.report.json'));
              
              if (reportFile) {
                const report = JSON.parse(fs.readFileSync(path.join(resultsPath, reportFile)));
                const scores = report.categories;
                
                const comment = `
## 🚦 Lighthouse CI Results

| Category | Score |
|----------|-------|
| Performance | ${Math.round(scores.performance.score * 100)} |
| Accessibility | ${Math.round(scores.accessibility.score * 100)} |
| Best Practices | ${Math.round(scores['best-practices'].score * 100)} |
| SEO | ${Math.round(scores.seo.score * 100)} |

### Core Web Vitals
- **LCP**: ${report.audits['largest-contentful-paint'].displayValue}
- **CLS**: ${report.audits['cumulative-layout-shift'].displayValue}
- **FID**: ${report.audits['first-input-delay'].displayValue}

[View detailed report](${report.finalUrl})
                `;
                
                github.rest.issues.createComment({
                  issue_number: context.issue.number,
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  body: comment
                });
              }
            }
```

### Jenkins Pipeline

Create `Jenkinsfile` for Jenkins integration:

```groovy
pipeline {
    agent any
    
    environment {
        NODE_VERSION = '18'
        LHCI_TOKEN = credentials('lhci-token')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'nvm use ${NODE_VERSION}'
                sh 'npm ci'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Start Application') {
            steps {
                sh 'npm start &'
                sh 'sleep 10'
            }
        }
        
        stage('Lighthouse CI - Desktop') {
            steps {
                sh 'npx @lhci/cli collect --numberOfRuns=3'
                sh 'npx @lhci/cli assert'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.lighthouseci',
                        reportFiles: '*.report.html',
                        reportName: 'Lighthouse Desktop Report'
                    ])
                }
            }
        }
        
        stage('Lighthouse CI - Mobile') {
            steps {
                sh 'npx @lhci/cli collect --config=lighthouserc.mobile.js'
                sh 'npx @lhci/cli assert --config=lighthouserc.mobile.js'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.lighthouseci',
                        reportFiles: '*.mobile.report.html',
                        reportName: 'Lighthouse Mobile Report'
                    ])
                }
            }
        }
        
        stage('Upload Results') {
            steps {
                sh 'npx @lhci/cli upload'
            }
        }
    }
    
    post {
        failure {
            emailext (
                subject: "Lighthouse CI Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Performance or accessibility budgets exceeded. Check the reports for details.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

## Axe-Core Accessibility Testing

### Axe-Core Integration Script

Create `scripts/axe-test.js`:

```javascript
const { AxePuppeteer } = require('@axe-core/puppeteer');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const urls = [
  'http://localhost:3000/',
  'http://localhost:3000/explore',
  'http://localhost:3000/package/kashmir-valley',
  'http://localhost:3000/collections/weekend',
];

const axeConfig = {
  rules: {
    // Enable all WCAG 2.1 AA rules
    'wcag2a': { enabled: true },
    'wcag2aa': { enabled: true },
    'wcag21aa': { enabled: true },
    
    // Premium UI specific rules
    'color-contrast': { enabled: true },
    'focus-order-semantics': { enabled: true },
    'landmark-one-main': { enabled: true },
    'page-has-heading-one': { enabled: true },
    'region': { enabled: true },
    
    // Disable rules that conflict with design
    'landmark-no-duplicate-banner': { enabled: false }, // Hero can be banner
  },
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'],
};

async function runAxeTests() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  
  const results = [];
  
  for (const url of urls) {
    console.log(`Testing ${url}...`);
    
    const page = await browser.newPage();
    
    // Set viewport for consistent testing
    await page.setViewport({ width: 1350, height: 940 });
    
    try {
      await page.goto(url, { waitUntil: 'networkidle0' });
      
      // Wait for dynamic content
      await page.waitForTimeout(2000);
      
      // Run axe-core
      const axe = new AxePuppeteer(page);
      const axeResults = await axe
        .configure(axeConfig)
        .analyze();
      
      results.push({
        url,
        violations: axeResults.violations,
        passes: axeResults.passes.length,
        incomplete: axeResults.incomplete,
        timestamp: new Date().toISOString(),
      });
      
      // Log violations
      if (axeResults.violations.length > 0) {
        console.error(`❌ ${axeResults.violations.length} violations found on ${url}`);
        axeResults.violations.forEach(violation => {
          console.error(`  - ${violation.id}: ${violation.description}`);
          console.error(`    Impact: ${violation.impact}`);
          console.error(`    Elements: ${violation.nodes.length}`);
        });
      } else {
        console.log(`✅ No violations found on ${url}`);
      }
      
    } catch (error) {
      console.error(`Error testing ${url}:`, error);
      results.push({
        url,
        error: error.message,
        timestamp: new Date().toISOString(),
      });
    }
    
    await page.close();
  }
  
  await browser.close();
  
  // Save results
  const reportPath = path.join(process.cwd(), 'axe-results.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  
  // Generate summary
  const totalViolations = results.reduce((sum, result) => 
    sum + (result.violations ? result.violations.length : 0), 0);
  
  console.log('\n📊 Accessibility Test Summary:');
  console.log(`Total URLs tested: ${urls.length}`);
  console.log(`Total violations: ${totalViolations}`);
  
  if (totalViolations > 0) {
    console.error('❌ Accessibility tests failed');
    process.exit(1);
  } else {
    console.log('✅ All accessibility tests passed');
  }
}

// Run if called directly
if (require.main === module) {
  runAxeTests().catch(console.error);
}

module.exports = { runAxeTests, axeConfig };
```

### Axe-Core Package.json Scripts

Add to `package.json`:

```json
{
  "devDependencies": {
    "@axe-core/puppeteer": "^4.7.3",
    "puppeteer": "^20.7.2"
  },
  "scripts": {
    "axe:test": "node scripts/axe-test.js",
    "axe:ci": "npm run build && npm run start & sleep 10 && npm run axe:test && kill %1",
    "accessibility:full": "npm run axe:ci && npm run lhci:full"
  }
}
```

## Visual Regression Testing

### Percy Integration

Create `percy.config.js`:

```javascript
module.exports = {
  version: 2,
  discovery: {
    allowedHostnames: ['localhost'],
    networkIdleTimeout: 750,
  },
  snapshot: {
    widths: [375, 768, 1280, 1920],
    minHeight: 1024,
    percyCSS: `
      /* Hide dynamic content for consistent snapshots */
      .flash-countdown { display: none !important; }
      .loading-spinner { display: none !important; }
      
      /* Ensure consistent state */
      .hero-background {
        animation-play-state: paused !important;
        transform: scale(1.01) !important;
      }
    `,
  },
};
```

### Percy Test Script

Create `scripts/percy-test.js`:

```javascript
const percySnapshot = require('@percy/puppeteer');
const puppeteer = require('puppeteer');

const testCases = [
  {
    name: 'Homepage - Hero Section',
    url: 'http://localhost:3000/',
    selector: '.hero-section',
  },
  {
    name: 'Homepage - Search Band',
    url: 'http://localhost:3000/',
    selector: '.search-band',
  },
  {
    name: 'Homepage - Editorial Tiles',
    url: 'http://localhost:3000/',
    selector: '.editorial-section',
  },
  {
    name: 'Explore Page - Filter Rail',
    url: 'http://localhost:3000/explore',
    selector: '.explore-filters',
  },
  {
    name: 'Explore Page - Results Grid',
    url: 'http://localhost:3000/explore',
    selector: '.results-grid',
  },
  {
    name: 'Package Detail - Hero',
    url: 'http://localhost:3000/package/kashmir-valley',
    selector: '.package-hero',
  },
  {
    name: 'Error State - No Results',
    url: 'http://localhost:3000/explore?q=nonexistent',
    selector: '.empty-results',
  },
];

async function runVisualTests() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox'],
  });
  
  const page = await browser.newPage();
  
  for (const testCase of testCases) {
    console.log(`Capturing: ${testCase.name}`);
    
    await page.goto(testCase.url, { waitUntil: 'networkidle0' });
    
    // Wait for animations to settle
    await page.waitForTimeout(1000);
    
    // Take snapshot
    await percySnapshot(page, testCase.name, {
      widths: [375, 768, 1280, 1920],
      minHeight: 1024,
      scope: testCase.selector,
    });
  }
  
  await browser.close();
}

if (require.main === module) {
  runVisualTests().catch(console.error);
}
```

## Bundle Size Monitoring

### Bundle Analyzer Setup

Create `scripts/bundle-analysis.js`:

```javascript
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const fs = require('fs');
const path = require('path');

// Bundle size thresholds (in bytes)
const BUNDLE_THRESHOLDS = {
  'main': 500000,      // 500KB
  'vendor': 800000,    // 800KB
  'css': 100000,       // 100KB
  'total': 2000000,    // 2MB
};

function analyzeBundleSize() {
  const buildPath = path.join(process.cwd(), '.next');
  const statsPath = path.join(buildPath, 'analyze');
  
  if (!fs.existsSync(statsPath)) {
    console.error('Bundle analysis files not found. Run npm run analyze first.');
    process.exit(1);
  }
  
  // Read bundle stats
  const clientStatsPath = path.join(statsPath, 'client.json');
  const clientStats = JSON.parse(fs.readFileSync(clientStatsPath, 'utf8'));
  
  // Calculate bundle sizes
  const bundles = {};
  let totalSize = 0;
  
  clientStats.chunks.forEach(chunk => {
    const size = chunk.size || 0;
    totalSize += size;
    
    if (chunk.names.includes('main')) {
      bundles.main = (bundles.main || 0) + size;
    } else if (chunk.names.some(name => name.includes('vendor'))) {
      bundles.vendor = (bundles.vendor || 0) + size;
    }
  });
  
  bundles.total = totalSize;
  
  // Check thresholds
  let failed = false;
  console.log('\n📦 Bundle Size Analysis:');
  
  Object.entries(BUNDLE_THRESHOLDS).forEach(([bundle, threshold]) => {
    const size = bundles[bundle] || 0;
    const sizeKB = Math.round(size / 1024);
    const thresholdKB = Math.round(threshold / 1024);
    const percentage = Math.round((size / threshold) * 100);
    
    const status = size <= threshold ? '✅' : '❌';
    if (size > threshold) failed = true;
    
    console.log(`${status} ${bundle}: ${sizeKB}KB / ${thresholdKB}KB (${percentage}%)`);
  });
  
  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    bundles,
    thresholds: BUNDLE_THRESHOLDS,
    passed: !failed,
  };
  
  fs.writeFileSync('bundle-report.json', JSON.stringify(report, null, 2));
  
  if (failed) {
    console.error('\n❌ Bundle size limits exceeded');
    process.exit(1);
  } else {
    console.log('\n✅ All bundle sizes within limits');
  }
}

if (require.main === module) {
  analyzeBundleSize();
}
```

### Bundle Size CI Integration

Add to GitHub Actions workflow:

```yaml
- name: Analyze bundle size
  run: |
    npm run build
    npm run analyze
    node scripts/bundle-analysis.js
    
- name: Comment bundle size changes
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v6
  with:
    script: |
      const fs = require('fs');
      const report = JSON.parse(fs.readFileSync('bundle-report.json'));
      
      const comment = `
## 📦 Bundle Size Report

| Bundle | Size | Limit | Status |
|--------|------|-------|--------|
| Main | ${Math.round(report.bundles.main / 1024)}KB | ${Math.round(report.thresholds.main / 1024)}KB | ${report.bundles.main <= report.thresholds.main ? '✅' : '❌'} |
| Vendor | ${Math.round(report.bundles.vendor / 1024)}KB | ${Math.round(report.thresholds.vendor / 1024)}KB | ${report.bundles.vendor <= report.thresholds.vendor ? '✅' : '❌'} |
| Total | ${Math.round(report.bundles.total / 1024)}KB | ${Math.round(report.thresholds.total / 1024)}KB | ${report.bundles.total <= report.thresholds.total ? '✅' : '❌'} |

${report.passed ? '✅ All bundle sizes within limits' : '❌ Bundle size limits exceeded'}
      `;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment
      });
```

## Production Monitoring Dashboard

### Core Web Vitals Monitoring

Create `lib/performance-monitoring.js`:

```javascript
// Real User Monitoring (RUM) setup
export function initPerformanceMonitoring() {
  if (typeof window === 'undefined') return;
  
  // Core Web Vitals tracking
  import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
    getCLS(sendToAnalytics);
    getFID(sendToAnalytics);
    getFCP(sendToAnalytics);
    getLCP(sendToAnalytics);
    getTTFB(sendToAnalytics);
  });
  
  // Custom performance marks
  performance.mark('app-start');
  
  // Track hero image load time
  const heroImage = document.querySelector('.hero-background img');
  if (heroImage) {
    heroImage.addEventListener('load', () => {
      performance.mark('hero-loaded');
      performance.measure('hero-load-time', 'app-start', 'hero-loaded');
      
      const measure = performance.getEntriesByName('hero-load-time')[0];
      sendToAnalytics({
        name: 'hero-load-time',
        value: measure.duration,
        id: 'hero-image',
      });
    });
  }
}

function sendToAnalytics(metric) {
  // Send to your analytics service
  if (window.gtag) {
    window.gtag('event', metric.name, {
      custom_parameter_1: metric.value,
      custom_parameter_2: metric.id,
    });
  }
  
  // Send to custom monitoring service
  fetch('/api/performance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metric: metric.name,
      value: metric.value,
      id: metric.id,
      url: window.location.pathname,
      timestamp: Date.now(),
    }),
  }).catch(console.error);
}

// Performance observer for long tasks
if ('PerformanceObserver' in window) {
  const observer = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
      if (entry.duration > 50) { // Long task threshold
        sendToAnalytics({
          name: 'long-task',
          value: entry.duration,
          id: entry.name,
        });
      }
    });
  });
  
  observer.observe({ entryTypes: ['longtask'] });
}
```

### Alert Configuration

Create monitoring alerts configuration:

```yaml
# alerts.yml - For monitoring service configuration
alerts:
  - name: "LCP Degradation"
    condition: "avg(lcp) > 2500ms over 5min"
    severity: "critical"
    channels: ["#dev-alerts", "performance-team@company.com"]
    
  - name: "CLS Spike"
    condition: "avg(cls) > 0.1 over 5min"
    severity: "warning"
    channels: ["#dev-alerts"]
    
  - name: "Bundle Size Increase"
    condition: "bundle_size > 2MB"
    severity: "warning"
    channels: ["#dev-alerts"]
    
  - name: "Accessibility Score Drop"
    condition: "accessibility_score < 95"
    severity: "critical"
    channels: ["#dev-alerts", "accessibility-team@company.com"]
    
  - name: "Error Rate Spike"
    condition: "error_rate > 1% over 10min"
    severity: "critical"
    channels: ["#dev-alerts", "on-call"]
```

This comprehensive Lighthouse CI setup ensures continuous monitoring of performance and accessibility standards while providing detailed reporting and alerting for the premium UI redesign.