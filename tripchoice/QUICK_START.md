# TripChoice - Quick Start (Fixed)

## 🔧 What Was Fixed

Your project had several performance issues causing Mac overheating:

1. **Massive build cache** (148MB in .next directory)
2. **Corrupted node_modules** (438MB with broken symlinks)
3. **Inefficient Next.js config** (no webpack optimizations)
4. **Missing development optimizations**

## 🚀 Quick Start (Optimized)

### 1. Start Development Server (Safe Mode)
```bash
npm run dev
```

This uses the optimized `dev-safe.js` script that:
- Limits memory usage to 4GB
- Disables telemetry
- Uses polling for file watching (prevents CPU spikes)
- Handles graceful shutdown

### 2. Alternative Commands
```bash
# Normal Next.js dev (if safe mode has issues)
npm run dev:normal

# Clean project (if you get issues again)
npm run clean

# Reinstall everything
npm run setup
```

## 🛠️ Optimizations Applied

### Next.js Config (`apps/web/next.config.js`)
- **SWC minification** enabled
- **Webpack watch optimizations** (polling, reduced aggregation)
- **Memory-efficient image settings**
- **Package import optimization**
- **Split chunks** for better caching

### Environment (`.env.local`)
- **Telemetry disabled**
- **Debug cache disabled**
- **Standalone mode** enabled

### Development Script (`dev-safe.js`)
- **Memory limit**: 4GB max
- **Graceful shutdown** handling
- **Optimized environment variables**

## 🎯 What You're Building

**TripChoice** - A travel package platform with:

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **CMS**: Directus (PostgreSQL backend)
- **Features**: Dynamic pricing, WhatsApp integration, personalization
- **Architecture**: Monorepo with workspace structure

## 📁 Project Structure
```
tripchoice/
├── apps/web/           # Next.js app (main frontend)
├── directus/           # CMS schema and data
├── dev-safe.js         # Optimized dev server
├── cleanup-safe.js     # Project cleanup utility
└── QUICK_START.md      # This guide
```

## 🚨 If You Still Get Issues

1. **Run cleanup**: `npm run clean`
2. **Check processes**: Activity Monitor → search "node"
3. **Kill runaway processes** if needed
4. **Restart with**: `npm run dev`

## 🎉 Next Steps

1. **Start the dev server**: `npm run dev`
2. **Visit**: http://localhost:3000
3. **Set up Directus** (see main README.md)
4. **Start building features**

The project should now run smoothly without overheating your Mac!