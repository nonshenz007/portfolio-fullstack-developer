"use client"

import Link from 'next/link'
import { useState, useEffect, useRef } from 'react'
import { MessageCircle, MapPin, Clock, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Magnetic } from '@/components/magnetic'
import { SafeImage } from '@/components/safe-image'
import { getPrice, formatPrice } from '@/lib/pricing'
import { Package } from '@/types'
import { useIntersectionObserver } from '@/lib/performance'
import { LazyWrapper } from '@/components/lazy-wrapper'

type EditorialTileProps = {
  pkg: Package
  className?: string
}

export function EditorialTile({ pkg, className }: EditorialTileProps) {
  const [variant, setVariant] = useState<'flight' | 'train' | 'bus'>('flight')
  const tileRef = useRef<HTMLDivElement>(null)

  const priceResult = getPrice(pkg, variant, new Date(), 2, 'Mumbai')
  const displayPrice = priceResult ? formatPrice(priceResult.pp) : 'Contact us'

  // Apply will-change optimization for hover animations
  useEffect(() => {
    if (!tileRef.current) return

    const element = tileRef.current
    element.style.willChange = 'transform, box-shadow'

    const cleanup = () => {
      element.style.willChange = 'auto'
    }

    // Remove will-change after animation completes
    const timeout = setTimeout(cleanup, 300)
    return () => {
      clearTimeout(timeout)
      cleanup()
    }
  }, [])

  const handleWhatsApp = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const message = `Hi! I'm interested in the ${pkg.title} package. Price: ${displayPrice}. Can you help me with more details?`
    const whatsappUrl = `https://wa.me/919447003974?text=${encodeURIComponent(message)}`
    window.open(whatsappUrl, '_blank')
  }

  return (
    <div ref={tileRef} className={className}>
      <div className="group rounded-3xl overflow-hidden bg-surface border border-cloud/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
        {/* 4:3 Image - lazy loaded with intersection observer */}
        <div className="relative overflow-hidden">
          <LazyWrapper fallback={<div className="aspect-[4/3] bg-gradient-to-br from-slate-100 to-slate-200 animate-pulse" />}>
            <SafeImage
              src={pkg.hero}
              alt={pkg.title}
              ratio="4:3"
              className="transition-transform duration-500 group-hover:scale-110"
              priority={false}
            />
          </LazyWrapper>
          {/* Gradient overlay for better text readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          
          {/* Floating badge for domestic/international */}
          <div className="absolute top-4 left-4">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-md ${
              pkg.domestic 
                ? 'bg-emerald-500/90 text-white' 
                : 'bg-purple-500/90 text-white'
            }`}>
              {pkg.domestic ? 'Domestic' : 'International'}
            </span>
          </div>

          {/* Rating badge */}
          <div className="absolute top-4 right-4">
            <div className="flex items-center gap-1 bg-white/90 backdrop-blur-md rounded-full px-3 py-1">
              <span className="text-yellow-500 text-sm">★</span>
              <span className="text-xs font-semibold text-ink">{pkg.rating}</span>
            </div>
          </div>
        </div>

        {/* Enhanced Caption bar */}
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="flex-1 min-w-0">
              <Link href={`/package/${pkg.slug}`}>
                <h3 className="font-display text-lg font-extrabold text-ink leading-tight line-clamp-2 hover:text-accent-cool transition-colors duration-200">
                  {pkg.title}
                </h3>
              </Link>
              
              {/* Theme tags */}
              <div className="mt-3 flex flex-wrap gap-2">
                {pkg.themes.slice(0, 3).map((theme, index) => (
                  <span key={index} className="px-2 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-md">
                    {theme}
                  </span>
                ))}
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2 text-slate text-sm">
                  <MapPin className="h-4 w-4 text-accent-cool" strokeWidth={1.75} />
                  <span className="font-medium">{pkg.destinations?.[0]}</span>
                  {pkg.destinations.length > 1 && (
                    <span className="text-xs text-slate-400">+{pkg.destinations.length - 1} more</span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-slate text-sm">
                  <span className="inline-flex items-center gap-1">
                    <Clock className="h-4 w-4 text-accent-warm" strokeWidth={1.75} />
                    {pkg.duration_days} days
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <Users className="h-4 w-4 text-accent-cool" strokeWidth={1.75} />
                    {pkg.min_pax}-{pkg.max_pax} pax
                  </span>
                </div>
              </div>
            </div>
            <div className="shrink-0">
              <div className="rounded-2xl px-4 py-3 bg-gradient-to-br from-accent-cool/10 to-accent-warm/10 border border-accent-cool/20 text-right">
                <div className="text-xs text-slate leading-none mb-1">Starting from</div>
                <div className="text-lg font-bold text-ink leading-none">{displayPrice}</div>
                <div className="text-xs text-slate-500 mt-1">per person</div>
              </div>
            </div>
          </div>

          {/* Enhanced hover reveal section */}
          <div className="mt-4 opacity-0 max-h-0 overflow-hidden group-hover:opacity-100 group-hover:max-h-40 transition-all duration-300 ease-out">
            {/* Transport tabs */}
            <div className="flex gap-1 p-1 bg-gradient-to-r from-slate-100 to-slate-50 rounded-xl mb-4">
              {(['flight', 'train', 'bus'] as const).map((id) => (
                <button
                  key={id}
                  onClick={(e) => {
                    e.stopPropagation()
                    setVariant(id)
                  }}
                  className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 ${
                    variant === id 
                      ? 'bg-gradient-to-r from-accent-cool to-accent-warm text-white shadow-lg transform scale-105' 
                      : 'text-slate-600 hover:text-ink hover:bg-white/80 hover:shadow-sm'
                  }`}
                >
                  <span className="capitalize">{id}</span>
                </button>
              ))}
            </div>

            {/* Enhanced Actions */}
            <div className="flex gap-3">
              <Link href={`/package/${pkg.slug}`} className="flex-1">
                <Magnetic>
                  <Button className="w-full bg-gradient-to-r from-accent-cool to-accent-warm hover:from-accent-cool/90 hover:to-accent-warm/90 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.02]">
                    View Details
                  </Button>
                </Magnetic>
              </Link>
              <Magnetic>
                <Button
                  variant="outline"
                  onClick={handleWhatsApp}
                  className="flex-1 border-2 border-emerald-500/40 text-emerald-600 hover:bg-emerald-50 hover:border-emerald-500 font-semibold py-3 rounded-xl transition-all duration-200 transform hover:scale-[1.02]"
                >
                  <MessageCircle className="h-4 w-4 mr-2" strokeWidth={2} />
                  WhatsApp
                </Button>
              </Magnetic>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
