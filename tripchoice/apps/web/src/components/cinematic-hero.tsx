'use client'

import { useState, useEffect, useRef } from 'react'
import { ChevronDown, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Personalization } from '@/types'
import Image from 'next/image'

export function CinematicHero() {
  const [searchQuery, setSearchQuery] = useState('')
  const [personalization, setPersonalization] = useState<Personalization | null>(null)
  const [offset, setOffset] = useState(0)
  const targetRef = useRef(0)
  const rafRef = useRef<number | null>(null)
  const [current, setCurrent] = useState(0)

  // Use diverse destination-specific images for a cinematic slideshow
  const slides = [
    'https://source.unsplash.com/1600x900/?kashmir%20mountains%20snow',
    'https://source.unsplash.com/1600x900/?thailand%20beach%20islands',
    'https://source.unsplash.com/1600x900/?dubai%20desert%20safari',
    'https://source.unsplash.com/1600x900/?bangkok%20temple%20wat',
    'https://source.unsplash.com/1600x900/?singapore%20skyline%20night'
  ]

  const quickChips = ['Weekend', 'Under ₹15k', 'Visa-free', 'Honeymoon', 'Mountains']

  useEffect(() => {
    const stored = localStorage.getItem('tc_profile')
    if (stored) {
      try {
        setPersonalization(JSON.parse(stored))
      } catch (error) {
        console.error('Error parsing personalization data:', error)
      }
    }
  }, [])

  useEffect(() => {
    const reduce = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) return

    const onScroll = () => {
      const y = window.scrollY
      targetRef.current = Math.min(10, y * 0.08)
    }

    const animate = () => {
      setOffset((prev) => {
        const next = prev + (targetRef.current - prev) * 0.12
        return Math.abs(next - prev) < 0.01 ? targetRef.current : next
      })
      rafRef.current = requestAnimationFrame(animate)
    }

    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    rafRef.current = requestAnimationFrame(animate)
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [])

  // Crossfade slideshow (reduced-motion aware)
  useEffect(() => {
    const reduce = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) return
    const id = setInterval(() => {
      setCurrent((i) => (i + 1) % slides.length)
    }, 6000) // Slightly slower for better UX
    return () => clearInterval(id)
  }, [slides.length])

  const handleSearch = () => {
    if (searchQuery.trim()) {
      window.location.href = `/explore?q=${encodeURIComponent(searchQuery)}`
    }
  }

  const scrollToExplore = () => {
    const exploreSection = document.getElementById('explore-section')
    if (exploreSection) {
      exploreSection.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <>
      {/* Editorial Masthead */}
      <section className="relative min-h-[85vh] md:min-h-[90vh] flex items-center overflow-hidden">
        {/* Background slideshow */}
        <div className="absolute inset-0">
          {slides.map((src, i) => (
            <div
              key={src}
              className={`absolute inset-0 transition-opacity duration-\[1500ms\] will-change-transform ${i === current ? 'opacity-100' : 'opacity-0'}`}
              style={{ transform: `translateY(${offset}px) scale(${i === current ? 1.01 : 1})` }}
              aria-hidden
            >
              <Image src={src} alt="Hero background" fill priority={i === 0} quality={85} sizes="100vw" className="object-cover cinematic-grade-strong" unoptimized referrerPolicy="no-referrer" />
            </div>
          ))}
          {/* Color film + depth */}
          <div className="absolute inset-0 bg-gradient-to-b from-ink/15 via-ink/30 to-ink/75" />
          <div className="absolute inset-0 bg-gradient-to-t from-ink/40 via-transparent to-transparent" />
          {/* Grain */}
          <div
            className="absolute inset-0 mix-blend-overlay"
            style={{
              backgroundImage:
                "radial-gradient(1px 1px at 10% 20%, rgba(7,28,60,.05) 1px, transparent 1px),radial-gradient(1px 1px at 30% 60%, rgba(6,71,174,.05) 1px, transparent 1px),radial-gradient(1px 1px at 70% 80%, rgba(74,83,101,.05) 1px, transparent 1px)",
              backgroundSize: '64px 64px',
              opacity: 0.03,
            }}
          />
        </div>

        {/* Copy */}
        <div className="relative z-10 w-full px-6 md:px-10 max-w-6xl mx-auto text-center rise-in">
          {personalization?.name && (
            <div className="text-sm md:text-base text-white/90 mb-3 md:mb-4">
              Welcome back, {personalization.name}
            </div>
          )}
          <h1 className="font-display text-white text-[36px] leading-[1.1] md:text-[72px] md:leading-[1.05] font-semibold tracking-tight drop-shadow-xl mb-4 md:mb-6">
            Plan less.<br className="md:hidden" />
            Travel more.
          </h1>
          <p className="max-w-2xl mx-auto text-white/90 text-base md:text-lg leading-relaxed mb-8 md:mb-10">
            Curated journeys, honest pricing, and zero hassle. Your perfect getaway awaits.
          </p>

          {/* CTA Button */}
          <div className="mb-8 md:mb-12">
            <button
              onClick={scrollToExplore}
              className="inline-flex items-center gap-3 bg-accent-warm hover:bg-accent-warm/90 text-white font-semibold py-4 px-8 md:py-5 md:px-10 rounded-full transition-all duration-300 hover:scale-105 hover:shadow-2xl focus:outline-none focus:ring-4 focus:ring-white/30"
            >
              Explore Destinations
              <ChevronDown className="h-5 w-5 rotate-90" strokeWidth={2} />
            </button>
          </div>
        </div>
      </section>

      {/* Search band below hero */}
      <section className="relative z-10 bg-surface border-t border-b border-cloud/10 shadow-lg">
        <div className="container mx-auto px-4 py-8 md:py-10">
          <div className="max-w-4xl mx-auto">
            {/* Search Header */}
            <div className="text-center mb-6">
              <h2 className="text-xl md:text-2xl font-semibold text-ink mb-2">Find Your Perfect Trip</h2>
              <p className="text-slate text-sm md:text-base">Search destinations or browse by category</p>
            </div>

            {/* Search Bar */}
            <div className="relative mb-6">
              <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-slate" strokeWidth={1.75} />
              </div>
              <Input
                type="text"
                placeholder="Search destinations, activities, or experiences..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-14 pr-36 h-14 md:h-16 text-base md:text-lg rounded-2xl border-cloud/20 bg-surface text-ink placeholder:text-slate/70 shadow-e1 focus:shadow-e2 focus:border-accent-warm/30 transition-all"
              />
              <Button
                onClick={handleSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 h-11 px-8 md:px-10 bg-accent-warm hover:bg-accent-warm/90 text-white font-semibold rounded-xl transition-all duration-200 hover:scale-105"
              >
                Search
              </Button>
            </div>

            {/* Popular Categories */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              {quickChips.map((chip, index) => (
                <button
                  key={chip}
                  onClick={() => window.location.href = `/explore?q=${encodeURIComponent(chip)}`}
                  className="px-5 py-3 rounded-full bg-gradient-to-r from-cloud/30 to-cloud/10 text-ink border border-cloud/20 hover:border-accent-warm/30 hover:bg-accent-warm/5 transition-all duration-200 text-sm font-medium hover:scale-105 shadow-sm"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
