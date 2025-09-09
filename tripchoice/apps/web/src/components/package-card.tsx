'use client'

import Link from 'next/link'
import { useState } from 'react'
import { MapPin, Clock, Users, MessageCircle, Heart, Share2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Magnetic } from '@/components/magnetic'
import { SafeImage } from '@/components/safe-image'
import { SocialShare } from '@/components/social-share'
import { getPrice, formatPrice } from '@/lib/pricing'
import { Package } from '@/types'
import { analytics } from '@/lib/analytics'
import { cn } from '@/lib/utils'

interface PackageCardProps {
  pkg: Package
  className?: string
}

export function PackageCard({ pkg, className }: PackageCardProps) {
  const [selectedVariant, setSelectedVariant] = useState<string>('flight')
  const [isLiked, setIsLiked] = useState(false)
  const [showShare, setShowShare] = useState(false)

  const variants = [
    { id: 'flight', type: 'flight', adj_pp: 0 },
    { id: 'train', type: 'train', adj_pp: -2000 },
    { id: 'bus', type: 'bus', adj_pp: -3000 }
  ]

  const handleCardClick = () => {
    analytics.trackPackageViewed(pkg.slug)
  }

  // Use pricing system
  const priceResult = getPrice(pkg, selectedVariant, new Date(), 2, 'Mumbai')
  const displayPrice = priceResult ? formatPrice(priceResult.pp) : 'Contact us'

  const handleWhatsApp = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const message = `Hi! I'm interested in the ${pkg.title} package. Price: ${displayPrice}. Can you help me with more details?`
    const whatsappUrl = `https://wa.me/919447003974?text=${encodeURIComponent(message)}`
    window.open(whatsappUrl, '_blank')
  }

  return (
    <div className={className}>
      <div
        className="group bg-surface rounded-xl overflow-hidden shadow-e2 hover:shadow-e3 transition-all duration-200 hover:-translate-y-[6px] border border-cloud/20"
        data-testid="package-card"
        data-package-slug={pkg.slug}
        data-testid-slug={`package-card-${pkg.slug}`}
      >
        {/* Image - fixed 4:3 ratio with subtle zoom on hover */}
        <div className="relative overflow-hidden">
          {/* Interactive Action Buttons */}
          <div className="absolute top-3 right-3 z-10 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setIsLiked(!isLiked)
              }}
              className={cn(
                "p-2 rounded-full transition-all duration-200 hover:scale-110 shadow-lg",
                isLiked
                  ? "bg-red-500 text-white"
                  : "bg-white/90 text-slate-600 hover:bg-white"
              )}
            >
              <Heart className={cn("w-4 h-4", isLiked && "fill-current")} />
            </button>

            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setShowShare(!showShare)
              }}
              className="p-2 rounded-full bg-white/90 text-slate-600 hover:bg-white hover:scale-110 shadow-lg transition-all duration-200"
            >
              <Share2 className="w-4 h-4" />
            </button>
          </div>

          {/* Share Menu */}
          {showShare && (
            <div className="absolute top-16 right-3 z-20 bg-white rounded-lg shadow-lg border border-slate-200 p-3 min-w-[200px]">
              <SocialShare
                url={`/package/${pkg.slug}`}
                title={`Check out ${pkg.title}`}
                description={pkg.summary}
                className="flex-col space-y-2 space-x-0"
              />
            </div>
          )}

          <SafeImage
            src={pkg.hero}
            alt={pkg.title}
            ratio="4:3"
            className="transition-transform duration-300 group-hover:scale-[1.03]"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px"
          />
        </div>

        {/* Caption bar */}
        <div className="p-4">
          <div className="flex items-start">
            <div className="flex-1 pr-2">
              <Link href={`/package/${pkg.slug}`} onClick={handleCardClick}>
                <h3 className="font-display text-[22px] font-semibold text-ink leading-snug line-clamp-2">
                  {pkg.title}
                </h3>
              </Link>
              <div className="mt-2 flex items-center gap-4 text-sm text-slate">
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" strokeWidth={1.75} />
                  <span className="truncate max-w-[160px]">{pkg.destinations[0]}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" strokeWidth={1.75} />
                  <span>{pkg.duration_days} days</span>
                </div>
                <div className="hidden sm:flex items-center gap-1">
                  <Users className="h-4 w-4" strokeWidth={1.75} />
                  <span>{pkg.min_pax}-{pkg.max_pax} pax</span>
                </div>
              </div>
            </div>
            {/* Price capsule */}
            <div className="ml-2">
              <div className="rounded-full px-3 py-2 bg-cloud/15 border border-cloud/30 text-right">
                <div className="text-[11px] text-slate leading-none mb-1">From</div>
                <div className="text-sm font-semibold text-ink leading-none">{displayPrice}</div>
              </div>
            </div>
          </div>

          {/* Reveal row: tabs + actions (hidden on desktop until hover; always visible on mobile) */}
          <div className="mt-3 space-y-3">
            <div className="flex gap-1 p-1 bg-cloud/10 rounded-md md:opacity-0 md:h-0 md:overflow-hidden md:group-hover:opacity-100 md:group-hover:h-auto md:transition-all">
              {variants.map((variant) => (
                <button
                  key={variant.id}
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedVariant(variant.id)
                  }}
                  className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${
                    selectedVariant === variant.id
                      ? 'bg-ink text-surface shadow-e1'
                      : 'text-ink/70 hover:text-ink hover:bg-cloud/20'
                  }`}
                >
                  <span className="capitalize">{variant.type}</span>
                </button>
              ))}
            </div>

            <div className="flex gap-2 md:opacity-0 md:h-0 md:overflow-hidden md:group-hover:opacity-100 md:group-hover:h-auto md:transition-all">
              <Link href={`/package/${pkg.slug}`} className="flex-1">
                <Magnetic>
                  <Button className="w-full bg-ink hover:bg-ink/90 text-surface">View details</Button>
                </Magnetic>
              </Link>
              <Magnetic>
                <Button
                  onClick={handleWhatsApp}
                  variant="outline"
                  className="flex-1 border-accent-cool/40 text-accent-cool hover:bg-accent-cool/5"
                >
                  <MessageCircle className="h-4 w-4 mr-2" strokeWidth={1.75} />
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
