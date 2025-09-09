import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { Gallery16x9 } from '@/components/gallery-16x9'
import { VariantSelector } from '@/components/variant-selector'
import { PriceBox } from '@/components/price-box'
import { ItineraryAccordion } from '@/components/itinerary-accordion'
import { InclusionsExclusions } from '@/components/inclusions-exclusions'
import { ReviewsStub } from '@/components/reviews-stub'
import { WhatsAppCTA } from '@/components/whatsapp-cta'
import { getPackage } from '@/lib/cms'
import { generatePackageJsonLd, generatePackageSEO } from '@/lib/seo'

interface PackagePageProps {
  params: { slug: string }
}

export async function generateMetadata({ params }: PackagePageProps): Promise<Metadata> {
  try {
    const pkg = await getPackage(params.slug)
    if (!pkg) return { title: 'Package Not Found' }
    
    return generatePackageSEO(pkg)
  } catch {
    return { title: 'Package Not Found' }
  }
}

export default async function PackagePage({ params }: PackagePageProps) {
  let pkg
  try {
    pkg = await getPackage(params.slug)
  } catch (error) {
    console.error('Failed to fetch package:', error)
    notFound()
  }

  if (!pkg) {
    notFound()
  }

  const jsonLd = generatePackageJsonLd(pkg)

  return (
    <>
      {/* JSON-LD Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 relative overflow-hidden">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 pointer-events-none">
          {/* Primary gradient orbs */}
          <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-20 w-80 h-80 bg-gradient-to-br from-emerald-400/20 to-teal-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-br from-indigo-400/10 to-pink-400/10 rounded-full blur-3xl animate-pulse delay-500"></div>

          {/* Secondary floating elements */}
          <div className="absolute top-1/4 right-1/4 w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
          <div className="absolute bottom-1/4 left-1/4 w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping delay-1000"></div>
          <div className="absolute top-3/4 right-1/3 w-1 h-1 bg-purple-400 rounded-full animate-ping delay-2000"></div>
        </div>

        {/* Hero Gallery with Overlay */}
        <div className="relative">
          <Gallery16x9
            images={[pkg.hero, ...(pkg.gallery || [])]}
            alt={pkg.title}
            priority
          />

          {/* Gradient overlay for better text readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent"></div>

          {/* Package Title Overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-4xl md:text-6xl font-black mb-4 animate-fade-in-up">
                {pkg.title}
              </h1>
              <p className="text-xl text-blue-100 max-w-2xl leading-relaxed animate-fade-in-up delay-200">
                {pkg.summary}
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="relative z-10">
          <div className="max-w-7xl mx-auto px-4 py-16">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              {/* Left Column - Content */}
              <div className="lg:col-span-2 space-y-12">
                {/* Enhanced Package Header */}
                <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border border-white/20 animate-fade-in-up">
                  {/* Professional Package Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                    <div className="text-center p-4 bg-white/50 rounded-lg border border-gray-200">
                      <div className="text-2xl font-bold text-blue-600 mb-1">{pkg.rating.toFixed(1)}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Rating</div>
                      <div className="text-xs text-gray-400 mt-1">({pkg.ratings_count} reviews)</div>
                    </div>
                    <div className="text-center p-4 bg-white/50 rounded-lg border border-gray-200">
                      <div className="text-2xl font-bold text-green-600 mb-1">{pkg.min_pax}-{pkg.max_pax}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Group Size</div>
                      <div className="text-xs text-gray-400 mt-1">Perfect for families</div>
                    </div>
                    <div className="text-center p-4 bg-white/50 rounded-lg border border-gray-200">
                      <div className="text-2xl font-bold text-purple-600 mb-1">{pkg.duration_days}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Days</div>
                      <div className="text-xs text-gray-400 mt-1">Well planned</div>
                    </div>
                    <div className="text-center p-4 bg-white/50 rounded-lg border border-gray-200">
                      <div className="text-2xl font-bold text-orange-600 mb-1">₹{pkg.base_price_pp.toLocaleString()}</div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Per Person</div>
                      <div className="text-xs text-gray-400 mt-1">All inclusive</div>
                    </div>
                  </div>

                  {/* Destinations */}
                  <div className="bg-white/30 rounded-lg p-4 border border-gray-200 mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-bold text-sm">📍</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-800 mb-1">Destinations</h3>
                        <p className="text-gray-600">{pkg.destinations.join(' • ')}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Professional Transport Section */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-gray-200 animate-fade-in-up delay-300">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">Transportation Options</h2>
                    <p className="text-gray-600">Choose your preferred mode of transport with detailed comparisons</p>
                  </div>

                  <VariantSelector packageId={pkg.id} />
                </div>

                {/* Professional Itinerary Section */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-gray-200 animate-fade-in-up delay-500">
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">Detailed Itinerary</h2>
                    <p className="text-gray-600">Comprehensive day-by-day breakdown of your journey</p>
                  </div>

                  <ItineraryAccordion packageId={pkg.id} />
                </div>

                {/* Professional Inclusions & Exclusions */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-gray-200 animate-fade-in-up delay-700">
                  <InclusionsExclusions
                    inclusions={pkg.inclusions}
                    exclusions={pkg.exclusions}
                  />
                </div>

                {/* Professional Reviews */}
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-gray-200 animate-fade-in-up delay-900">
                  <ReviewsStub packageId={pkg.id} rating={pkg.rating} count={pkg.ratings_count} />
                </div>
              </div>

              {/* Right Column - Enhanced Sticky Price Box */}
              <div className="lg:col-span-1">
                <div className="space-y-8 lg:sticky top-24">
                  <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200 animate-fade-in-up delay-1100">
                    <PriceBox pkg={pkg} />
                  </div>

                  {/* Professional Trust Elements */}
                  <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-200 animate-fade-in-up delay-1300">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-green-600 text-xl">✓</span>
                      </div>
                      <h3 className="font-bold text-gray-800 mb-3">Secure & Trusted</h3>
                      <p className="text-sm text-gray-600 mb-4">Bank-grade security • Instant confirmation • 24/7 support</p>
                      <div className="flex justify-center gap-3 text-xs text-gray-500">
                        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">Verified</span>
                        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">Protected</span>
                        <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full font-medium">Insured</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Professional Mobile CTA */}
        <div className="fixed bottom-6 right-6 z-50 lg:hidden">
          <div className="bg-blue-600 text-white px-6 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center gap-3">
            <span className="text-lg">📞</span>
            <span className="font-semibold">Book Now</span>
          </div>
        </div>

        <WhatsAppCTA pkg={pkg} />
      </div>
    </>
  )
}
