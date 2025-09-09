import { Metadata } from 'next'
import { Suspense } from 'react'
import { ModernExploreHero } from '@/components/modern-explore-hero'
import { QuickFilters } from '@/components/quick-filters'
import { TrendingDestinations } from '@/components/trending-destinations'
import { ExploreGrid } from '@/components/explore-grid'
import { Footer } from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Explore Destinations | TripChoice',
  description: 'Discover curated travel packages for your next adventure. Filter by destination, theme, and budget.',
  openGraph: {
    title: 'Explore Destinations | TripChoice',
    description: 'Discover curated travel packages for your next adventure.',
  }
}

export default function ExplorePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 pt-16 md:pt-18">
      {/* Hero Section */}
      <ModernExploreHero />

      {/* Search & Filters */}
      <section className="py-20 bg-gradient-to-b from-white via-slate-50/30 to-slate-100 relative overflow-hidden">
        {/* Subtle background elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-32 h-32 bg-slate-300 rounded-full blur-2xl"></div>
          <div className="absolute bottom-20 right-20 w-40 h-40 bg-slate-200 rounded-full blur-2xl"></div>
          <div className="absolute top-1/2 left-1/3 w-24 h-24 bg-slate-100 rounded-full blur-2xl"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <QuickFilters />
        </div>
      </section>

      {/* Trending Destinations */}
      <section className="py-24 bg-gradient-to-b from-slate-100 via-slate-50/30 to-white relative">
        {/* Subtle background elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 right-10 w-48 h-48 bg-slate-300 rounded-full blur-3xl"></div>
          <div className="absolute bottom-10 left-10 w-36 h-36 bg-slate-200 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-slate-200 text-slate-700 rounded-full text-sm font-medium mb-4">
              Trending Now
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Hot Destinations
            </h2>
            <p className="text-slate-600 text-lg max-w-2xl mx-auto">
              Discover the most popular travel destinations loved by thousands of travelers
            </p>
          </div>
          <TrendingDestinations />
        </div>
      </section>

      {/* All Destinations */}
      <section className="py-24 bg-gradient-to-b from-white via-slate-50/20 to-slate-100/50 relative overflow-hidden">
        {/* Subtle background elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 right-20 w-56 h-56 bg-slate-300 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-20 w-44 h-44 bg-slate-200 rounded-full blur-3xl"></div>
          <div className="absolute top-1/3 right-1/4 w-28 h-28 bg-slate-100 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-slate-200 text-slate-700 rounded-full text-sm font-medium mb-4">
              Explore All
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Complete Destination Guide
            </h2>
            <p className="text-slate-600 text-lg max-w-3xl mx-auto">
              From pristine beaches to majestic mountains, explore our comprehensive collection of handpicked travel experiences
            </p>
          </div>

          <div className="animate-fade-in delay-500">
            <Suspense fallback={
              <div className="text-center py-16">
                <div className="animate-bounce">
                  <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600 mx-auto mb-4"></div>
                </div>
                <h3 className="text-2xl font-semibold text-indigo-900 mb-2">Discovering Amazing Places</h3>
                <p className="text-indigo-600">Loading your next adventure...</p>
              </div>
            }>
              <ExploreGrid />
            </Suspense>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-24 bg-slate-900 text-white relative overflow-hidden">
        {/* Subtle background elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 bg-slate-700 rounded-full blur-3xl"></div>
          <div className="absolute bottom-10 right-10 w-48 h-48 bg-slate-800 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-slate-600 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready for Your Next Adventure?
          </h2>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            Join thousands of happy travelers who have discovered their perfect trip with TripChoice
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="px-8 py-4 bg-white text-slate-900 font-semibold rounded-full hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 hover:shadow-xl">
              Start Planning Now
            </button>
            <button className="px-8 py-4 border-2 border-white text-white font-semibold rounded-full hover:bg-white/10 transition-all duration-300 transform hover:scale-105">
              Talk to Expert
            </button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
