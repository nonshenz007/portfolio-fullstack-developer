# TripChoice Production Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Vercel (Recommended)
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy from project root
vercel

# 3. Set environment variables in Vercel dashboard
```

### Option 2: Docker + Any Cloud Provider
```bash
# 1. Build Docker image
docker build -t tripchoice .

# 2. Run container
docker run -p 3000:3000 tripchoice
```

## 📋 Prerequisites

### Domain & SSL
- [ ] Domain registered (e.g., tripchoice.com)
- [ ] SSL certificate configured
- [ ] DNS configured to point to hosting provider

### Environment Variables
Required for production:

```env
# Directus CMS
DIRECTUS_URL=https://your-directus-instance.com
DIRECTUS_TOKEN=your_production_directus_token

# WhatsApp
NEXT_PUBLIC_WHATSAPP_NUMBER=+919876543210

# Site Configuration
NEXT_PUBLIC_SITE_URL=https://tripchoice.com

# Analytics
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=tripchoice.com
```

### CMS Setup (Directus)
- [ ] PostgreSQL database ready
- [ ] Directus instance deployed
- [ ] Schema applied from `directus/snapshot.json`
- [ ] Seed data imported
- [ ] Admin token generated

## 🎯 Deployment Steps

### Step 1: Prepare Production Build
```bash
cd apps/web
npm run build
npm run start # Test production build locally
```

### Step 2: Vercel Deployment

#### A. Connect Repository
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Select the `apps/web` directory as root
4. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Development Command: `npm run dev`

#### B. Environment Variables
Add these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value | Type |
|----------|-------|------|
| `DIRECTUS_URL` | Your Directus URL | Production |
| `DIRECTUS_TOKEN` | Your admin token | Production |
| `NEXT_PUBLIC_WHATSAPP_NUMBER` | WhatsApp number | All |
| `NEXT_PUBLIC_SITE_URL` | https://tripchoice.com | All |
| `NEXT_PUBLIC_PLAUSIBLE_DOMAIN` | tripchoice.com | All |

#### C. Domain Configuration
1. Add custom domain in Vercel dashboard
2. Configure DNS records as instructed
3. Verify SSL certificate is active

### Step 3: Alternative Cloud Deployment

#### AWS/GCP/Azure with Docker
```dockerfile
# Dockerfile (create in apps/web/)
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

## 🔍 Post-Deployment Checklist

### Performance Verification
- [ ] Lighthouse Score ≥95 Performance
- [ ] Core Web Vitals passing
- [ ] Images optimized and loading
- [ ] Font loading optimized

### Functionality Testing
- [ ] Home page loads correctly
- [ ] Explore page filters work
- [ ] Package pages display properly
- [ ] Personalization modal functions
- [ ] WhatsApp integration works
- [ ] Flash sale countdown (if active)

### SEO & Analytics
- [ ] Meta tags present on all pages
- [ ] Structured data validates
- [ ] Sitemap accessible at `/sitemap.xml`
- [ ] Analytics tracking events
- [ ] Search console verification

### Security & Monitoring
- [ ] HTTPS enforced
- [ ] Headers security configured
- [ ] Error tracking enabled
- [ ] Uptime monitoring active

## 📊 Monitoring & Analytics

### Plausible Analytics Setup
1. Add domain in Plausible dashboard
2. Verify script loading on site
3. Test event tracking:
   - Package views
   - WhatsApp clicks
   - Search performed
   - Personalization saved

### Error Monitoring (Optional)
Consider adding Sentry for error tracking:
```bash
npm install @sentry/nextjs
```

## 🔧 Performance Optimization

### Image Optimization
- Use Next.js Image component
- Configure CDN for images
- Serve images in WebP format

### Bundle Optimization
- Analyze bundle: `npm run build && npx @next/bundle-analyzer`
- Implement code splitting
- Remove unused dependencies

### Caching Strategy
- Static assets: 1 year cache
- HTML pages: No cache / revalidate
- API responses: 5-30 minutes depending on data

## 🆘 Troubleshooting

### Common Issues

#### Build Fails
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

#### Environment Variables Not Working
- Ensure `NEXT_PUBLIC_` prefix for client-side variables
- Restart build after adding new variables
- Check Vercel environment variable settings

#### CMS Connection Issues
- Verify Directus URL is accessible
- Check token permissions
- Ensure CORS is configured for your domain

#### Slow Loading
- Enable Next.js Image optimization
- Configure CDN for static assets
- Optimize database queries

### Log Analysis
```bash
# View Vercel function logs
vercel logs

# Local debugging
npm run dev
```

## 📞 Support Contacts

- **Technical Issues**: Check GitHub Issues
- **CMS Problems**: Directus documentation
- **Domain/DNS**: Your domain registrar
- **Hosting**: Vercel support or your cloud provider

---

## 🎉 Go-Live Checklist

Final checklist before announcing launch:

- [ ] All acceptance criteria met
- [ ] Performance benchmarks achieved
- [ ] Security headers configured
- [ ] Backup & monitoring in place
- [ ] Team trained on support processes
- [ ] Marketing materials ready
- [ ] Social media accounts linked
- [ ] Customer support channels active

**🚀 Ready to launch? Double-check everything above, then announce to the world!**
