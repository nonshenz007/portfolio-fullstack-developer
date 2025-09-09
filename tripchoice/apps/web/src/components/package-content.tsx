'use client'

import React, { useState } from 'react'
import Image from 'next/image'
import { Star, MapPin, Calendar, Users, ChevronLeft } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Magnetic } from '@/components/magnetic'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ItineraryAccordion } from '@/components/itinerary-accordion'
import { VariantTabs } from '@/components/variant-tabs'
import { PriceTag } from '@/components/price-tag'
import { usePackageDetails } from '@/hooks/use-packages'
import { usePriceBreakdown } from '@/hooks/use-pricing'
import { Package } from '@/types'
import { formatCurrency, cn } from '@/lib/utils'
import { analytics } from '@/lib/analytics'

interface PackageContentProps {
  package: Package
}

export function PackageContent({ package: pkg }: PackageContentProps) {
  const [selectedVariant, setSelectedVariant] = useState<any>(null)
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [paxCount, setPaxCount] = useState(2)

  const { itinerary, variants, reviews, isLoading } = usePackageDetails(pkg.slug)

  const { breakdown, totalPerPerson, totalForGroup, hasDiscount, flashSale } = usePriceBreakdown({
    package: pkg,
    variant: selectedVariant,
    date: selectedDate,
    pax: paxCount,
    originCity: 'Mumbai', // This could come from personalization
  })

  // Track package view
  React.useEffect(() => {
    analytics.trackPackageViewed(pkg.slug)
  }, [pkg.slug])

  const handleVariantChange = (variant: any) => {
    setSelectedVariant(variant)
    if (variant) {
      analytics.trackVariantSelected(pkg.slug, variant.type, variant.id)
    }
  }

  const handleWhatsAppEnquiry = () => {
    const message = `Hi! I'm interested in the ${pkg.title} package for ${paxCount} people on ${selectedDate.toLocaleDateString()}. ${selectedVariant ? `I'd like the ${selectedVariant.subclass} option.` : ''} Can you provide more details and pricing?`

    // Create WhatsApp deep-link with UTM parameters
    const utmParams = new URLSearchParams({
      utm_source: 'website',
      utm_medium: 'whatsapp',
      utm_campaign: 'package_enquiry',
      utm_content: pkg.slug,
      variant: selectedVariant?.id || '',
      date: selectedDate.toISOString().split('T')[0],
      pax: paxCount.toString()
    })

    const whatsappUrl = `https://wa.me/919447003974?text=${encodeURIComponent(message)}&${utmParams.toString()}`
    window.open(whatsappUrl, '_blank')

    analytics.trackWhatsAppClick(pkg.slug, {
      variant: selectedVariant?.id,
      date: selectedDate.toISOString(),
      pax: paxCount,
      utm: utmParams.toString()
    })
  }

  if (isLoading) {
    return <div>Loading package details...</div>
  }

  return (
    <div>
      {/* Wide Gallery - 16:9 aspect */}
      <div className="relative aspect-[16/9] overflow-hidden">
        <Image
          src={pkg.hero}
          alt={pkg.title}
          fill
          className="object-cover"
          priority
          sizes="100vw"
          unoptimized
          referrerPolicy="no-referrer"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink/80 via-transparent to-transparent" />

        {/* Back Button - Floating */}
        <div className="absolute top-6 left-6">
          <Link href="/explore">
            <Button variant="ghost" className="bg-surface-primary/90 backdrop-blur-sm text-ink hover:bg-surface-primary border-0 shadow-premium-subtle">
              <ChevronLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
        </div>

        {/* Package Info Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 text-surface-primary">
          <div className="container mx-auto">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold mb-3">{pkg.title}</h1>
            <p className="text-lg md:text-xl mb-4 opacity-90 max-w-3xl">{pkg.summary}</p>

            <div className="flex flex-wrap items-center gap-4 text-sm md:text-base">
              <div className="flex items-center bg-surface-primary/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                <MapPin className="h-4 w-4 mr-2" />
                {pkg.destinations.join(', ')}
              </div>
              <div className="flex items-center bg-surface-primary/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                <Calendar className="h-4 w-4 mr-2" />
                {pkg.duration_days} days
              </div>
              <div className="flex items-center bg-surface-primary/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                <Users className="h-4 w-4 mr-2" />
                {pkg.min_pax}-{pkg.max_pax} people
              </div>
              <div className="flex items-center bg-surface-primary/20 backdrop-blur-sm px-3 py-1.5 rounded-full">
                <Star className="h-4 w-4 mr-2 fill-accent-warm text-accent-warm" />
                {pkg.rating.toFixed(1)} ({pkg.ratings_count})
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Details */}
          <div className="lg:col-span-2 space-y-8">
          {/* Gallery */}
          {pkg.gallery && pkg.gallery.length > 1 && (
            <div>
              <h2 className="text-h3 font-semibold text-ink mb-4">Gallery</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {pkg.gallery.slice(1).map((image, index) => (
                  <div key={index} className="aspect-[16/10] relative rounded-lg overflow-hidden">
                    <Image
                      src={image}
                      alt={`${pkg.title} - Image ${index + 2}`}
                      fill
                      className="object-cover hover:scale-105 transition-transform cursor-pointer"
                      sizes="(max-width: 768px) 100vw, 800px"
                      unoptimized
                      referrerPolicy="no-referrer"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tabs for different content */}
          <Tabs defaultValue="itinerary" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
              <TabsTrigger value="inclusions">What's Included</TabsTrigger>
              <TabsTrigger value="policies">Policies</TabsTrigger>
              <TabsTrigger value="reviews">Reviews ({reviews.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="itinerary" className="mt-6">
              {/* Day-by-day Itinerary as Vertical Timeline */}
              <div className="space-y-6">
                {itinerary.map((day, index) => (
                  <div key={index} className="flex gap-4">
                    {/* Timeline Dot */}
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 bg-accent-warm rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      {index < itinerary.length - 1 && (
                        <div className="w-0.5 h-16 bg-cloud/30 mt-2" />
                      )}
                    </div>
                    
                    {/* Day Content */}
                    <div className="flex-1 pb-8">
                      <h4 className="font-bold text-lg text-ink mb-2">{day.title}</h4>
                      <ul className="space-y-1">
                        {day.bullets.slice(0, 3).map((bullet, bulletIndex) => (
                          <li key={bulletIndex} className="text-slate flex items-start gap-2">
                            <span className="text-accent-cool mt-1.5">•</span>
                            <span>{bullet}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="inclusions" className="mt-6">
              {/* Two Slim Panels Side by Side */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="glass-card p-6">
                  <h3 className="font-bold text-lg text-ink mb-4 flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    What's Included
                  </h3>
                  <div className="space-y-3">
                    {pkg.inclusions.map((inclusion, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <span className="text-green-500 mt-0.5">✓</span>
                        <span className="text-slate text-sm">{inclusion}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {pkg.exclusions && pkg.exclusions.length > 0 && (
                  <div className="glass-card p-6">
                    <h3 className="font-bold text-lg text-ink mb-4 flex items-center gap-2">
                      <span className="text-red-500">✗</span>
                      Not Included
                    </h3>
                    <div className="space-y-3">
                      {pkg.exclusions.map((exclusion, index) => (
                        <div key={index} className="flex items-start gap-3">
                          <span className="text-red-500 mt-0.5">✗</span>
                          <span className="text-slate text-sm">{exclusion}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="policies" className="mt-6">
              <div className="prose prose-slate max-w-none">
                <h3 className="text-h3 font-semibold text-ink mb-4">Important Policies</h3>
                <div dangerouslySetInnerHTML={{ __html: pkg.policies.replace(/\n/g, '<br>') }} />
              </div>
            </TabsContent>

            <TabsContent value="reviews" className="mt-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-lg text-ink">Guest Reviews</h3>
                  <div className="flex items-center gap-2 bg-accent-cool/10 px-3 py-1.5 rounded-full">
                    <Star className="h-4 w-4 fill-accent-warm text-accent-warm" />
                    <span className="font-bold text-ink">{pkg.rating.toFixed(1)}</span>
                    <span className="text-slate text-sm">({pkg.ratings_count})</span>
                  </div>
                </div>

                {reviews.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">💬</div>
                    <p className="text-slate">No reviews yet. Be the first to share your experience!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {reviews.map((review) => (
                      <div key={review.id} className="glass-card p-6">
                        {/* Photo-forward Snippet */}
                        <div className="flex items-start gap-4">
                          <div className="w-12 h-12 bg-accent-warm rounded-full flex items-center justify-center">
                            <span className="font-bold text-white">
                              {review.author_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <span className="font-semibold text-ink">{review.author_name}</span>
                                <Badge variant="secondary" className="ml-2 text-xs">
                                  {review.source}
                                </Badge>
                              </div>
                              <div className="flex items-center">
                                {Array.from({ length: 5 }).map((_, i) => (
                                  <Star key={i} className={`h-4 w-4 ${i < review.rating ? 'fill-accent-warm text-accent-warm' : 'text-cloud/40'}`} />
                                ))}
                              </div>
                            </div>
                            <p className="text-slate leading-relaxed">{review.text}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>

          {/* Right Column - Compact Price Box */}
          <div className="space-y-6">
            <div className="glass-card p-6 sticky top-24">
              {/* Segmented Control for Variants */}
              {variants.length > 0 && (
                <div className="mb-6">
                  <div className="flex bg-cloud/10 rounded-xl p-1">
                    {variants.slice(0, 3).map((variant) => (
                      <button
                        key={variant.id}
                        onClick={() => handleVariantChange(variant)}
                        className={cn(
                          "flex-1 px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200",
                          selectedVariant?.id === variant.id
                            ? "bg-ink text-surface shadow-sm"
                            : "text-slate hover:text-ink"
                        )}
                      >
                        {variant.type === 'flight' ? '✈️' : variant.type === 'train' ? '🚂' : '🚌'}
                        <span className="ml-1 capitalize">{variant.type}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Price Display */}
              <div className="text-center mb-6">
                <div className="text-3xl font-bold text-ink mb-1">
                  From ₹{totalPerPerson ? totalPerPerson.toLocaleString('en-IN') : pkg.base_price_pp.toLocaleString('en-IN')}
                </div>
                <div className="text-sm text-slate">per person</div>
                <button className="text-xs text-accent-cool hover:underline mt-1">
                  breakdown
                </button>
              </div>

              {/* Quick Selectors */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="text-sm font-medium text-ink mb-2 block">People</label>
                  <select
                    value={paxCount}
                    onChange={(e) => setPaxCount(Number(e.target.value))}
                    className="w-full p-3 border border-cloud/30 rounded-lg focus:border-accent-cool bg-surface-primary text-ink"
                  >
                    {Array.from({ length: pkg.max_pax - pkg.min_pax + 1 }, (_, i) => (
                      <option key={i} value={pkg.min_pax + i}>
                        {pkg.min_pax + i} {pkg.min_pax + i === 1 ? 'person' : 'people'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium text-ink mb-2 block">Date</label>
                  <input
                    type="date"
                    value={selectedDate.toISOString().split('T')[0]}
                    onChange={(e) => setSelectedDate(new Date(e.target.value))}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full p-3 border border-cloud/30 rounded-lg focus:border-accent-cool bg-surface-primary text-ink"
                  />
                </div>
              </div>

              {/* WhatsApp CTA */}
              <Magnetic>
                <Button
                  onClick={handleWhatsAppEnquiry}
                  className="w-full bg-accent-warm hover:bg-accent-warm/90 text-white font-bold py-4 text-lg shadow-e2 transition-all duration-200"
                >
                  Enquire on WhatsApp
                </Button>
              </Magnetic>

              <p className="text-xs text-slate text-center mt-3">
                Instant response • Best price guaranteed
              </p>
            </div>
          </div>
        </div>

        {/* Mobile Sticky Bottom Bar */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-surface-primary/95 backdrop-blur-xl border-t border-cloud/20 p-4 safe-area-bottom">
          <Button
            onClick={handleWhatsAppEnquiry}
            className="w-full bg-accent-warm hover:bg-accent-warm/90 text-white font-bold py-4 text-lg shadow-e2"
          >
            Enquire on WhatsApp
          </Button>
        </div>
      </div>
    </div>
  )
}
