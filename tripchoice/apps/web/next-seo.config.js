/** @type {import('next-seo').DefaultSeoProps} */
const defaultSEOConfig = {
  title: 'TripChoice - Plan less. Travel more.',
  titleTemplate: '%s | TripChoice',
  defaultTitle: 'TripChoice - Plan less. Travel more.',
  description: 'Curated travel packages at honest prices. Find your perfect getaway from Goa to Dubai with TripChoice.',
  canonical: 'https://tripchoice.com',
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'https://tripchoice.com',
    title: 'TripChoice - Plan less. Travel more.',
    description: 'Curated travel packages at honest prices. Find your perfect getaway from Goa to Dubai.',
    siteName: 'TripChoice',
    images: [
      {
        url: 'https://tripchoice.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'TripChoice - Travel Packages',
      },
    ],
  },
  twitter: {
    handle: '@tripchoice',
    site: '@tripchoice',
    cardType: 'summary_large_image',
  },
  additionalMetaTags: [
    {
      name: 'viewport',
      content: 'width=device-width, initial-scale=1',
    },
    {
      name: 'theme-color',
      content: '#ED6B08',
    },
    {
      name: 'msapplication-TileColor',
      content: '#ED6B08',
    },
    {
      name: 'apple-mobile-web-app-capable',
      content: 'yes',
    },
    {
      name: 'apple-mobile-web-app-status-bar-style',
      content: 'default',
    },
  ],
  additionalLinkTags: [
    {
      rel: 'icon',
      href: '/favicon.ico',
    },
    {
      rel: 'apple-touch-icon',
      href: '/apple-touch-icon.png',
      sizes: '180x180',
    },
    {
      rel: 'manifest',
      href: '/manifest.json',
    },
  ],
}

module.exports = defaultSEOConfig
