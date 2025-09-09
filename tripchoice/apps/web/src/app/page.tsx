import { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { HeroMasthead } from '@/components/HeroMasthead'
import { TrustSlice } from '@/components/TrustSlice'
import { Footer } from '@/components/Footer'
import { HomepageSearch } from '@/components/homepage-search'
import { getPackages } from '@/lib/cms'
import { Package } from '@/types'



function HomePageClient({ packages }: { packages: Package[] }) {
  // Fallback packages if CMS fails
  const fallbackPackages: Package[] = [
    {
      id: 'dubai-fallback',
      slug: 'dubai-city-lights-4d',
      title: 'Dubai Luxury Experience',
      summary: 'Experience the city of gold with luxury hotels and desert adventures',
      destinations: ['Dubai'],
      themes: ['Luxury', 'City', 'Adventure'],
      duration_days: 4,
      base_price_pp: 75000,
      min_pax: 2,
      max_pax: 8,
      hero: '/images/dubai/dubai-skyline-hd.jpg',
      gallery: [],
      inclusions: ['Hotel', 'Transfers'],
      exclusions: ['Flights'],
      policies: 'Standard policies apply',
      domestic: false,
      rating: 4.8,
      ratings_count: 150,
      status: 'published',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'goa-fallback',
      slug: 'goa-beach-3n',
      title: 'Goa Beach Weekend',
      summary: 'Relax on pristine beaches with vibrant nightlife',
      destinations: ['Goa'],
      themes: ['Beach', 'Weekend'],
      duration_days: 4,
      base_price_pp: 12500,
      min_pax: 2,
      max_pax: 8,
      hero: '/images/goa-beaches-4k.jpg',
      gallery: [],
      inclusions: ['Hotel', 'Activities'],
      exclusions: ['Flights'],
      policies: 'Standard policies apply',
      domestic: true,
      rating: 4.6,
      ratings_count: 200,
      status: 'published',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'shimla-fallback',
      slug: 'shimla-kufri-3n',
      title: 'Shimla Mountain Escape',
      summary: 'Experience the colonial charm of Himachal Pradesh',
      destinations: ['Shimla'],
      themes: ['Mountains', 'Culture'],
      duration_days: 4, 
      base_price_pp: 10999,
      min_pax: 2,
      max_pax: 8,
      hero: '/images/shimla-mountains-4k.jpg',
      gallery: [],
      inclusions: ['Hotel', 'Sightseeing'],
      exclusions: ['Flights'],
      policies: 'Standard policies apply',
      domestic: true,
      rating: 4.5,
      ratings_count: 100,
      status: 'published',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'kashmir-fallback',
      slug: 'kashmir-valley-4n',
      title: 'Kashmir Valley Paradise',
      summary: 'Experience the heaven on earth with Dal Lake and snow-capped mountains',
      destinations: ['Srinagar', 'Gulmarg'],
      themes: ['Mountains', 'Nature', 'Weekend'],
      duration_days: 4, 
      base_price_pp: 15999,
      min_pax: 2,
      max_pax: 8,
      hero: '/images/kashmir/kashmir-dal-lake-hd.jpg',
      gallery: [],
      inclusions: ['Hotel', 'Houseboat', 'Sightseeing'],
      exclusions: ['Flights'],
      policies: 'Standard policies apply',
      domestic: true,
      rating: 4.9,
      ratings_count: 180,
      status: 'published',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'vietnam-fallback',
      slug: 'vietnam-saigon-4n',
      title: 'Vietnam Heritage Tour',
      summary: 'Explore ancient temples and vibrant culture',
      destinations: ['Ho Chi Minh City', 'Hanoi'],
      themes: ['Culture', 'History'],
      duration_days: 5, 
      base_price_pp: 38999,
      min_pax: 2,
      max_pax: 8,
      hero: '/images/vietnam/vietnam-hoi-an-hd.jpg',
      gallery: [],
      inclusions: ['Hotel', 'Flights', 'Tours'],
      exclusions: ['Personal expenses'],
      policies: 'Visa required',
      domestic: false,
      rating: 4.9,
      ratings_count: 80,
      status: 'published',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'thailand-fallback',
      slug: 'thailand-bangkok-5n',
      title: 'Thailand Paradise', 
      summary: 'Beautiful beaches and ancient temples',
      destinations: ['Bangkok', 'Phuket'],
      themes: ['Beach', 'Culture'],
      duration_days: 6, 
      base_price_pp: 35999,
      min_pax: 2,
      max_pax: 8,
      hero: '/images/thailand-islands-4k.jpg',
      gallery: [],
      inclusions: ['Hotel', 'Flights', 'Transfers'],
      exclusions: ['Personal expenses'],
      policies: 'Visa on arrival',
      domestic: false,
      rating: 4.7,
      ratings_count: 120,
      status: 'published',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
  ]

  // Use fallback packages to ensure images work
  const allPackages = fallbackPackages

  const weekend = allPackages.filter((p) => p.duration_days <= 4 || p.themes?.includes('Weekend')).slice(0, 4)
  const international = allPackages.filter((p) => !p.domestic).slice(0, 3)



  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <HeroMasthead />

      {/* Weekend Getaways - Real & Authentic */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          {/* Simple, honest header */}
          <div className="text-center mb-16">
            <div className="inline-block bg-blue-50 text-blue-700 px-4 py-2 rounded-lg mb-6 text-sm font-medium">
              Perfect for quick escapes
            </div>
            
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Weekend Getaways
            </h2>
            
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Short on time but big on adventure? These weekend trips are designed for busy people who want to make the most of their time off.
            </p>
          </div>

          {/* Clean package grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            {weekend.length > 0 ? (
              weekend.slice(0, 4).map((pkg, index) => (
                <Link key={pkg.id} href={`/package/${pkg.slug}`} className="group block">
                  <div className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
                    {/* Image */}
                    <div className="relative aspect-[4/3] overflow-hidden">
                      <Image
                        src={pkg.hero}
                        alt={pkg.title}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-500"
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px"
                      />
                      
                      {/* Simple price badge */}
                      <div className="absolute top-4 right-4 bg-white rounded-lg px-3 py-2 shadow-md">
                        <div className="text-sm text-gray-600">From</div>
                        <div className="text-lg font-bold text-gray-900">₹{pkg.base_price_pp.toLocaleString()}</div>
                      </div>

                      {/* Rating badge */}
                      <div className="absolute top-4 left-4 bg-white rounded-lg px-3 py-2 shadow-md">
                        <div className="flex items-center gap-1">
                          <span className="text-yellow-500">★</span>
                          <span className="text-sm font-medium">{pkg.rating.toFixed(1)}</span>
                          <span className="text-xs text-gray-500">({pkg.ratings_count})</span>
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                            {pkg.title}
                          </h3>
                          <div className="flex items-center gap-1 text-gray-500 text-sm">
                            <span>📍</span>
                            <span>{pkg.destinations.join(', ')}</span>
                          </div>
                        </div>
                      </div>

                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {pkg.summary}
                      </p>

                      {/* Trip details */}
                      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                        <div className="flex items-center gap-4">
                          <span>📅 {pkg.duration_days} days</span>
                          <span>👥 {pkg.min_pax}-{pkg.max_pax} people</span>
                        </div>
                      </div>

                      {/* Themes */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        {pkg.themes?.slice(0, 2).map((theme, i) => (
                          <span key={i} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                            {theme}
                          </span>
                        ))}
                      </div>

                      {/* CTA */}
                      <div className="flex items-center justify-between">
                        <div className="text-blue-600 font-medium group-hover:text-blue-700 transition-colors">
                          View Details →
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <div className="text-4xl mb-4">🏖️</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Loading weekend getaways...</h3>
                <p className="text-gray-600">Finding the perfect short trips for you</p>
              </div>
            )}
          </div>

          {/* Simple CTA */}
          <div className="text-center">
            <Link href="/explore" className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
              <span>See All Weekend Trips</span>
              <span>→</span>
            </Link>
          </div>
        </div>
      </section>

      {/* International Adventures - Clean & Professional */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          {/* Straightforward header */}
          <div className="text-center mb-16">
            <div className="inline-block bg-orange-50 text-orange-700 px-4 py-2 rounded-lg mb-6 text-sm font-medium">
              Global experiences
            </div>
            
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              International Adventures
            </h2>
            
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Ready to explore beyond borders? Our international packages include flights, visas, and local experiences to make your dream trip hassle-free.
            </p>
          </div>

          {/* Featured international trips */}
          <div className="space-y-12">
            {international.length > 0 ? (
              international.map((pkg, index) => (
                <Link key={pkg.id} href={`/package/${pkg.slug}`} className="group block">
                  <div className={`bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300 ${
                    index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'
                  } flex flex-col lg:flex`}>
                    
                    {/* Image */}
                    <div className="lg:w-1/2 relative">
                      <div className="aspect-[4/3] lg:aspect-auto lg:h-full overflow-hidden">
                        <Image
                          src={pkg.hero}
                          alt={pkg.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-500"
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 600px"
                        />
                        
                        {/* Price badge */}
                        <div className="absolute top-4 right-4 bg-white rounded-lg px-4 py-3 shadow-md">
                          <div className="text-xs text-gray-600">Starting from</div>
                          <div className="text-xl font-bold text-gray-900">₹{pkg.base_price_pp.toLocaleString()}</div>
                          <div className="text-xs text-gray-500">per person</div>
                        </div>

                        {/* Rating */}
                        <div className="absolute top-4 left-4 bg-white rounded-lg px-3 py-2 shadow-md">
                          <div className="flex items-center gap-1">
                            <span className="text-yellow-500">★</span>
                            <span className="text-sm font-medium">{pkg.rating.toFixed(1)}</span>
                            <span className="text-xs text-gray-500">({pkg.ratings_count})</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="lg:w-1/2 p-8 flex flex-col justify-center">
                      <div>
                        <div className="flex items-center gap-3 mb-4">
                          <span className="text-3xl">✈️</span>
                          <div>
                            <h3 className="text-2xl font-bold text-gray-900 group-hover:text-orange-600 transition-colors">
                              {pkg.title}
                            </h3>
                            <div className="flex items-center gap-1 text-gray-500">
                              <span>📍</span>
                              <span className="text-sm">{pkg.destinations.join(' • ')}</span>
                            </div>
                          </div>
                        </div>

                        <p className="text-gray-600 mb-6 leading-relaxed">
                          {pkg.summary}
                        </p>

                        {/* Trip details */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                          <div className="bg-gray-50 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-lg">📅</span>
                              <span className="font-semibold text-gray-900">{pkg.duration_days} Days</span>
                            </div>
                            <div className="text-sm text-gray-600">Duration</div>
                          </div>
                          
                          <div className="bg-gray-50 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-lg">👥</span>
                              <span className="font-semibold text-gray-900">{pkg.min_pax}-{pkg.max_pax} People</span>
                            </div>
                            <div className="text-sm text-gray-600">Group Size</div>
                          </div>
                        </div>

                        {/* Themes */}
                        <div className="flex flex-wrap gap-2 mb-6">
                          {pkg.themes?.map((theme, i) => (
                            <span key={i} className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm">
                              {theme}
                            </span>
                          ))}
                        </div>

                        {/* CTA */}
                        <div className="flex items-center justify-between">
                          <div className="text-orange-600 font-medium group-hover:text-orange-700 transition-colors">
                            Explore This Journey →
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">✈️</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Loading international adventures...</h3>
                <p className="text-gray-600">Preparing amazing global experiences</p>
              </div>
            )}
          </div>

          {/* Simple CTA */}
          <div className="text-center mt-16">
            <Link href="/explore" className="inline-flex items-center gap-2 bg-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-700 transition-colors">
              <span>View All International Trips</span>
              <span>→</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Simple & Honest CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Plan Your Next Trip?
          </h2>

          <p className="text-xl text-blue-100 mb-12 max-w-2xl mx-auto">
            We've helped thousands of travelers create amazing memories. Let us help you plan your perfect getaway.
          </p>

          <HomepageSearch />

          {/* Main CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Link href="/explore" className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-50 transition-colors">
              Browse All Trips
            </Link>

            <button className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/10 transition-colors">
              Call +91-XXXXXXXXX
            </button>
          </div>

          {/* Trust indicators */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-white mb-2">15,000+</div>
              <div className="text-blue-200 text-sm">Happy Travelers</div>
            </div>
            
            <div>
              <div className="text-3xl font-bold text-white mb-2">4.8★</div>
              <div className="text-blue-200 text-sm">Average Rating</div>
            </div>
            
            <div>
              <div className="text-3xl font-bold text-white mb-2">50+</div>
              <div className="text-blue-200 text-sm">Destinations</div>
            </div>
            
            <div>
              <div className="text-3xl font-bold text-white mb-2">24/7</div>
              <div className="text-blue-200 text-sm">Support</div>
            </div>
          </div>

          {/* Why choose us */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="bg-blue-700/50 rounded-lg p-6">
              <div className="text-2xl mb-3">🎯</div>
              <h3 className="font-semibold text-white mb-2">Expert Planning</h3>
              <p className="text-blue-100 text-sm">Our travel experts craft personalized itineraries based on your interests and budget.</p>
            </div>

            <div className="bg-blue-700/50 rounded-lg p-6">
              <div className="text-2xl mb-3">💰</div>
              <h3 className="font-semibold text-white mb-2">Best Prices</h3>
              <p className="text-blue-100 text-sm">Transparent pricing with no hidden fees. We guarantee competitive rates.</p>
            </div>

            <div className="bg-blue-700/50 rounded-lg p-6">
              <div className="text-2xl mb-3">🛡️</div>
              <h3 className="font-semibold text-white mb-2">Peace of Mind</h3>
              <p className="text-blue-100 text-sm">24/7 support, travel insurance, and flexible booking policies included.</p>
            </div>
          </div>
        </div>
      </section>

      <TrustSlice />
      <Footer />
    </main>
  )
}

export const metadata: Metadata = {
  title: 'TripChoice - Plan less. Travel more.',
  description: 'Curated travel packages at honest prices. Find your perfect getaway.',
}

async function getFeaturedPackages(): Promise<Package[]> {
  try {
    const packages = await getPackages({ limit: 20 }) // Get more packages to ensure we have enough for filtering
    return packages
  } catch (error) {
    console.error('Failed to fetch packages:', error)
    return []
  }
}

export default async function HomePage() {
  const packages = await getFeaturedPackages()
  return (
    <div className="pt-16 md:pt-18">
      <HomePageClient packages={packages} />
    </div>
  )
}
