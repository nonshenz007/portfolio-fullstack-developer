'use client'

import { useState, useMemo, useCallback, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { PackageCard } from '@/components/package-card'
import { usePackages } from '@/hooks/use-packages'
import { Package, PackageFilters } from '@/types'
import { analytics } from '@/lib/analytics'
import { cn } from '@/lib/utils'

export function ExploreContent() {
  const searchParams = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedThemes, setSelectedThemes] = useState<string[]>([])
  const [selectedDestinations, setSelectedDestinations] = useState<string[]>([])
  const [priceRange, setPriceRange] = useState('any')
  const [domesticFilter, setDomesticFilter] = useState<'all' | 'domestic' | 'international'>('all')
  const [sortBy, setSortBy] = useState('popular')

  // Read URL parameters on mount and when they change
  useEffect(() => {
    const q = searchParams.get('q') || ''
    const themes = searchParams.get('themes')?.split(',') || []
    const domestic = searchParams.get('domestic') as 'all' | 'domestic' | 'international' || 'all'
    const price = searchParams.get('price')
    const sort = searchParams.get('sort') || 'popular'

    setSearchQuery(q)
    setSelectedThemes(themes)
    setDomesticFilter(domestic)

    if (price) {
      const [min, max] = price.split('-').map(Number)
      if (min && max) {
        setPriceRange(`${min}-${max}`)
      }
    }

    setSortBy(sort)
  }, [searchParams])

  // Build filters object using proper PackageFilters format
  const filters = useMemo((): PackageFilters => {
    const filterObj: PackageFilters = {}

    if (searchQuery.trim()) {
      filterObj.search = searchQuery.trim()
    }

    if (domesticFilter !== 'all') {
      filterObj.domestic = domesticFilter
    }

    if (priceRange && priceRange !== 'any') {
      const [min, max] = priceRange.split('-').map(Number)
      if (min !== undefined && max !== undefined) {
        filterObj.priceRange = { min, max }
      }
    }

    if (selectedThemes.length > 0) {
      filterObj.themes = selectedThemes
    }

    if (selectedDestinations.length > 0) {
      filterObj.destinations = selectedDestinations
    }

    if (sortBy !== 'popular') {
      filterObj.sortBy = sortBy as 'price-low' | 'price-high' | 'rating' | 'duration' | 'popular'
    }

    return filterObj
  }, [searchQuery, domesticFilter, priceRange, selectedThemes, selectedDestinations, sortBy])

  const handleSearch = useCallback(() => {
    analytics.trackSearchPerformed(searchQuery, {
      themes: selectedThemes,
      destinations: selectedDestinations,
      domestic: domesticFilter,
      priceRange,
    })
  }, [searchQuery, selectedThemes, selectedDestinations, domesticFilter, priceRange])

  const clearAllFilters = useCallback(() => {
    setSearchQuery('')
    setSelectedThemes([])
    setSelectedDestinations([])
    setPriceRange('any')
    setDomesticFilter('all')
  }, [])

  const { data: packages = [], isLoading, error } = usePackages(filters)

  // Packages are already sorted by the CMS, so we just use them as-is
  const sortedPackages = useMemo(() => {
    return packages || []
  }, [packages])

  if (error) {
    return (
      <div className="text-center py-16">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
          <div className="h-8 w-8 text-red-600">!</div>
        </div>
        <h3 className="text-xl font-semibold text-slate-900 mb-2">Something went wrong</h3>
        <p className="text-slate-600 mb-6">Failed to load travel packages. Please try again later.</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-primary">
      {/* Sticky Filter Bar - slides under header */}
      <div className="sticky top-16 z-30 bg-surface-primary/95 backdrop-blur-xl border-b border-cloud/10 px-4 py-3">
        <div className="container mx-auto">
          <div className="flex items-center gap-4">
            {/* Search Field */}
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search destinations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleSearch()
                  }
                }}
                className="w-full h-10 pl-4 pr-12 rounded-full bg-cloud/10 border border-cloud/20 focus:border-accent-cool focus:bg-surface-primary text-ink placeholder:text-slate/60 transition-all duration-300"
              />
            </div>

            {/* Domestic/International Toggle */}
            <div className="flex bg-cloud/10 rounded-full p-1">
              <button
                onClick={() => setDomesticFilter('domestic')}
                className={cn(
                  "px-4 py-1.5 text-sm font-medium rounded-full transition-all duration-200",
                  domesticFilter === 'domestic'
                    ? "bg-ink text-surface shadow-sm"
                    : "text-slate hover:text-ink"
                )}
              >
                Domestic
              </button>
              <button
                onClick={() => setDomesticFilter('international')}
                className={cn(
                  "px-4 py-1.5 text-sm font-medium rounded-full transition-all duration-200",
                  domesticFilter === 'international'
                    ? "bg-ink text-surface shadow-sm"
                    : "text-slate hover:text-ink"
                )}
              >
                International
              </button>
            </div>

            {/* Theme Tags - Horizontal List */}
            <div className="hidden lg:flex items-center gap-2">
              {['Weekend', 'Honeymoon', 'Mountains', 'Beach', 'Adventure'].map((theme) => (
                <button
                  key={theme}
                  onClick={() => {
                    if (selectedThemes.includes(theme)) {
                      setSelectedThemes(selectedThemes.filter(t => t !== theme))
                    } else {
                      setSelectedThemes([...selectedThemes, theme])
                    }
                  }}
                  className={cn(
                    "px-3 py-1.5 text-sm font-medium rounded-full transition-all duration-200",
                    selectedThemes.includes(theme)
                      ? "bg-accent-warm text-white shadow-sm"
                      : "bg-cloud/10 text-slate hover:text-ink hover:bg-cloud/20"
                )}
              >
                {theme}
              </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Results Grid - Phone-first: 1-col mobile, 2-col tablet, 3-col desktop */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ? (
            // Loading skeleton
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="space-y-4">
                <div className="aspect-[4/3] bg-cloud/20 rounded-3xl" />
                <div className="space-y-2 px-4">
                  <div className="h-4 bg-cloud/20 rounded" />
                  <div className="h-4 bg-cloud/20 rounded w-3/4" />
                </div>
              </div>
            ))
          ) : sortedPackages.length > 0 ? (
            sortedPackages.map((pkg) => (
              <PackageCard key={pkg.id} pkg={pkg} />
            ))
          ) : (
            // Empty state
            <div className="col-span-full text-center py-16">
              <h3 className="text-xl font-semibold text-ink mb-2">No destinations found</h3>
              <p className="text-slate mb-6">Try adjusting your filters or search terms</p>
              <button
                onClick={clearAllFilters}
                className="px-6 py-3 bg-ink text-surface font-medium rounded-full hover:bg-ink/90 transition-colors duration-300"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>

        {sortedPackages.length > 0 && !isLoading && (
          <div className="text-center mt-12">
            <p className="text-slate text-sm">
              Showing {sortedPackages.length} destinations
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
