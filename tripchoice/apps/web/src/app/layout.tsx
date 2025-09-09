import type { Metadata } from 'next'
import { Header } from '@/components/header'
import { Providers } from '@/components/providers'
import RouteTransitions from '@/components/RouteTransitions'
import { LiveChatWidget } from '@/components/live-chat-widget'
import { PerformanceMonitor } from '@/components/performance-monitor'
import { defaultSEO } from '@/lib/seo'
import './globals.css'
// Intro overlay CSS removed (landing directly on hero)

export const metadata: Metadata = {
  title: defaultSEO.title,
  description: defaultSEO.description,
  keywords: 'travel, packages, vacation, holiday, tour, domestic, international, curated trips',
  authors: [{ name: 'TripChoice' }],
  creator: 'TripChoice',
  publisher: 'TripChoice',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Theme color for mobile browsers */}
        <meta name="theme-color" content="#071C3C" />
        <meta name="msapplication-TileColor" content="#071C3C" />

        {/* Viewport with safe area insets */}
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />

        {/* Performance: Preload a representative hero image (remote) */}
        <link rel="preload" href="https://source.unsplash.com/1600x900/?goa%20beach%20sunset" as="image" fetchPriority="high" />
        <link rel="dns-prefetch" href="//images.unsplash.com" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />

      </head>
      <body className={`antialiased bg-surface text-ink`}>
        {/* Performance monitoring */}
        <PerformanceMonitor />

        {/* Intro overlay removed; direct landing on hero */}
        <Providers>
          <div id="page-shell">
            <Header />
            <RouteTransitions>
              <main id="main-content" className="min-h-screen">
                {children}
              </main>
            </RouteTransitions>
          </div>
          {/* Live Chat Widget */}
          <LiveChatWidget />
        </Providers>
        
        {/* Analytics Scripts */}
        {process.env.NODE_ENV === 'production' && (
          <>
            {/* Plausible Analytics */}
            <script
              defer
              data-domain="tripchoice.com"
              src="https://plausible.io/js/script.js"
            />
            
            {/* Google Analytics */}
            <script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
            />
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
                `,
              }}
            />
          </>
        )}
      </body>
    </html>
  )
}
