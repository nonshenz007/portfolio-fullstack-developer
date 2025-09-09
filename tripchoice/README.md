# TripChoice - Travel Package Platform

**Plan less. Travel more.** Curated travel packages at honest prices.

![TripChoice](https://img.shields.io/badge/TripChoice-Travel_Platform-blue?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=flat-square)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-38B2AC?style=flat-square)

## 🚀 Overview

TripChoice is a modern travel package platform built with Next.js 14, featuring:

- **Curated Travel Packages**: Handpicked destinations from Goa to Dubai
- **Dynamic Pricing Engine**: Deterministic pricing with season/weekend multipliers
- **WhatsApp Integration**: Direct lead generation and customer support
- **Personalization**: Client-side user preferences and recommendations
- **SEO Optimized**: Schema.org markup and comprehensive meta tags
- **Responsive Design**: Mobile-first approach with beautiful animations
- **Admin CMS**: Directus-powered content management

## 🏗️ Architecture

```
tripchoice/
├── apps/web/                 # Next.js 14 application
├── directus/                 # CMS schema and seed data
├── cypress/                  # End-to-end tests
└── acceptance/              # Acceptance criteria
```

### Tech Stack

**Frontend:**
- Next.js 14 (App Router, TypeScript)
- Tailwind CSS + shadcn/ui
- Framer Motion animations
- TanStack Query for data fetching
- Next SEO for search optimization

**Backend/CMS:**
- Directus (PostgreSQL)
- RESTful API integration
- Media management
- User roles and permissions

**Business Logic:**
- Deterministic pricing engine
- Dynamic price rules (season, weekend, origin)
- Flash sales system
- Inventory management

## 🛠️ Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- PostgreSQL (for Directus)
- Git

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/tripchoice.git
cd tripchoice

# Install root dependencies
npm install

# Install web app dependencies
cd apps/web
npm install
cd ../..
```

### 2. Environment Configuration

```bash
cd apps/web
cp .env.sample .env.local
```

Edit `.env.local`:
```env
# Directus CMS Configuration
DIRECTUS_URL=http://localhost:8055
DIRECTUS_TOKEN=your_directus_admin_token_here

# WhatsApp Integration
NEXT_PUBLIC_WHATSAPP_NUMBER=+919876543210

# Site Configuration
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 3. Directus Setup

```bash
# Install Directus globally
npm install -g @directus/cli

# Create new Directus project
npx directus init directus-project

# Apply schema
cd directus
npx directus schema apply snapshot.json

# Import seed data
node import-seed.js
```

### 4. Development

```bash
# Start Directus (from directus directory)
npx directus start

# Start Next.js app (from apps/web directory)
npm run dev

# Visit http://localhost:3000
```

## 📊 Features

### 🏠 Home Page
- Cinematic hero with word swapper animation
- Featured packages (Weekend, International)
- Flash sale ribbon with countdown
- Quick filter chips

### 🔍 Explore Page
- Advanced filtering (themes, destinations, price, type)
- Real-time search
- Sort options (rating, price, duration)
- Responsive grid layout

### 📦 Package Details
- Comprehensive package information
- Dynamic pricing with breakdown
- Travel variant selection
- Itinerary accordion
- Customer reviews
- WhatsApp enquiry integration

### 👤 Personalization
- Client-side user preferences
- Travel persona, vibe, home city
- Persistent localStorage
- Personalized recommendations

### 💰 Pricing Engine
- Base price per person
- Season multipliers (peak: 1.25x, low: 0.9x)
- Weekend surcharge (1.05x)
- Origin-based adjustments
- Variant price deltas
- Flash sale discounts

### 📱 WhatsApp Integration
- Direct lead generation
- Package-specific payloads
- UTM tracking
- Mobile-optimized messaging

## 🎨 Design System

### Brand Colors
- **Primary**: `#ED6B08` (Warm accent)
- **Secondary**: `#0647AE` (Cool accent)
- **Ink**: `#071C3C` (Primary dark)
- **Surface**: `#FDFDF9` (Background)
- **Slate**: `#4A5365` (Text)
- **Cloud**: `#AEB5BC` (Borders)

### Typography
- **Display**: Plus Jakarta Sans
- **UI**: Inter
- **Scale**: Responsive font sizes with proper line heights

### Components
- shadcn/ui component library
- Custom animations with Framer Motion
- Accessible focus states
- Mobile-first responsive design

## 🔧 Development

### Scripts

```bash
# Web app
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint
npm run test         # Cypress tests
npm run type-check   # TypeScript check

# Root
npm run dev          # Start web app
npm run build        # Build all apps
```

### Project Structure

```
apps/web/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── (routes)/        # Route groups
│   │   ├── api/            # API routes
│   │   ├── globals.css     # Global styles
│   │   └── layout.tsx      # Root layout
│   ├── components/         # React components
│   │   ├── ui/            # shadcn/ui components
│   │   └── ...            # Custom components
│   ├── lib/               # Utilities and business logic
│   │   ├── cms.ts         # Directus client
│   │   ├── pricing.ts     # Pricing engine
│   │   ├── analytics.ts   # Tracking utilities
│   │   └── ...
│   ├── types/             # TypeScript definitions
│   └── hooks/             # Custom React hooks
```

## 🧪 Testing

### Cypress E2E Tests

```bash
cd apps/web
npm run test          # Run all tests
npm run test:ui       # Open Cypress UI
```

Test scenarios:
- Personalization modal saves preferences
- Explore page filters work correctly
- Package variant selection updates pricing
- WhatsApp CTA generates correct links
- Flash sale countdown displays properly

### Acceptance Criteria

See `acceptance/ACCEPTANCE.md` for detailed acceptance criteria covering:
- Performance metrics (Lighthouse scores)
- Accessibility compliance (WCAG AA)
- SEO requirements
- Business logic validation

## 🚀 Deployment

### Vercel (Recommended)

1. Connect GitHub repository
2. Set environment variables
3. Deploy with zero configuration

### Manual Deployment

```bash
# Build the application
npm run build

# Start production server
npm run start
```

### Directus Hosting

- **Directus Cloud**: Managed hosting with automatic scaling
- **Self-hosted**: Docker deployment on any cloud provider
- **Database**: PostgreSQL required for production

## 📈 Analytics & Monitoring

### Plausible Analytics
- Privacy-focused, no cookies
- Real-time visitor metrics
- Custom event tracking

### Custom Events
- `search_performed`: Search queries and filters
- `package_viewed`: Package detail page views
- `variant_selected`: Travel option selections
- `whatsapp_click`: Lead generation tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Style
- ESLint configuration included
- Prettier for code formatting
- TypeScript strict mode enabled
- Component-driven development

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Next.js** for the amazing React framework
- **Directus** for the flexible CMS
- **shadcn/ui** for beautiful components
- **Tailwind CSS** for utility-first styling
- **Framer Motion** for smooth animations

## 📞 Support

- **WhatsApp**: +91 98765 43210
- **Email**: hello@tripchoice.com
- **Issues**: GitHub Issues
- **Docs**: This README and inline code comments

---

**Built with ❤️ for travelers who want honest, curated experiences.**
