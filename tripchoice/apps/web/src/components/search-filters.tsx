'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Filter, X, SlidersHorizontal } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchFiltersProps {
  className?: string
  onFiltersChange?: (filters: any) => void
}

export function SearchFilters({ className, onFiltersChange }: SearchFiltersProps) {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [isOpen, setIsOpen] = useState(false)
  const [domesticFilter, setDomesticFilter] = useState<'all' | 'domestic' | 'international'>('all')
  const [selectedThemes, setSelectedThemes] = useState<string[]>([])
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 100000])
  const [durationRange, setDurationRange] = useState<[number, number]>([1, 15])
  const [minRating, setMinRating] = useState(0)

  const themes = [
    'Beach', 'Mountains', 'Culture', 'Adventure', 'Luxury', 'Family',
    'Honeymoon', 'Nature', 'Heritage', 'Spiritual', 'Relaxation', 'Food'
  ]

  const destinations = [
    'Kashmir', 'Goa', 'Kerala', 'Rajasthan', 'Himachal', 'Thailand',
    'Dubai', 'Singapore', 'Malaysia', 'Vietnam', 'Japan', 'Europe'
  ]

  // Read URL parameters on mount
  useEffect(() => {
    const domestic = searchParams.get('domestic') as 'all' | 'domestic' | 'international' || 'all'
    const themesParam = searchParams.get('themes')?.split(',') || []
    const priceParam = searchParams.get('price')
    const durationParam = searchParams.get('duration')
    const ratingParam = searchParams.get('rating')

    setDomesticFilter(domestic)
    setSelectedThemes(themesParam)

    if (priceParam) {
      const [min, max] = priceParam.split('-').map(Number)
      setPriceRange([min || 0, max || 100000])
    }

    if (durationParam) {
      const [min, max] = durationParam.split('-').map(Number)
      setDurationRange([min || 1, max || 15])
    }

    if (ratingParam) {
      setMinRating(Number(ratingParam))
    }
  }, [searchParams])

  // Update URL when filters change
  const updateFilters = () => {
    const params = new URLSearchParams(searchParams.toString())

    if (domesticFilter !== 'all') {
      params.set('domestic', domesticFilter)
    } else {
      params.delete('domestic')
    }

    if (selectedThemes.length > 0) {
      params.set('themes', selectedThemes.join(','))
    } else {
      params.delete('themes')
    }

    if (priceRange[0] > 0 || priceRange[1] < 100000) {
      params.set('price', `${priceRange[0]}-${priceRange[1]}`)
    } else {
      params.delete('price')
    }

    if (durationRange[0] > 1 || durationRange[1] < 15) {
      params.set('duration', `${durationRange[0]}-${durationRange[1]}`)
    } else {
      params.delete('duration')
    }

    if (minRating > 0) {
      params.set('rating', minRating.toString())
    } else {
      params.delete('rating')
    }

    router.replace(`/explore?${params.toString()}`, { scroll: false })
    onFiltersChange?.({
      domestic: domesticFilter,
      themes: selectedThemes,
      priceRange,
      durationRange,
      minRating
    })
  }

  // Auto-update when filters change
  useEffect(() => {
    const timer = setTimeout(updateFilters, 500)
    return () => clearTimeout(timer)
  }, [domesticFilter, selectedThemes, priceRange, durationRange, minRating])

  const clearAllFilters = () => {
    setDomesticFilter('all')
    setSelectedThemes([])
    setPriceRange([0, 100000])
    setDurationRange([1, 15])
    setMinRating(0)
    router.replace('/explore', { scroll: false })
  }

  const toggleTheme = (theme: string) => {
    setSelectedThemes(prev =>
      prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme]
    )
  }

  const hasActiveFilters = domesticFilter !== 'all' ||
                          selectedThemes.length > 0 ||
                          priceRange[0] > 0 ||
                          priceRange[1] < 100000 ||
                          durationRange[0] > 1 ||
                          durationRange[1] < 15 ||
                          minRating > 0

  return (
    <div className={cn("relative", className)}>
      {/* Filter Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-200",
          hasActiveFilters
            ? "bg-accent-cool/10 border-accent-cool text-accent-cool"
            : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
        )}
      >
        <SlidersHorizontal className="w-4 h-4" />
        <span>Filters</span>
        {hasActiveFilters && (
          <span className="bg-accent-cool text-white text-xs px-2 py-1 rounded-full">
            Active
          </span>
        )}
      </button>

      {/* Filter Panel */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-6 z-50">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-ink">Filters</h3>
            {hasActiveFilters && (
              <button
                onClick={clearAllFilters}
                className="text-sm text-accent-cool hover:text-accent-cool/80 font-medium"
              >
                Clear all
              </button>
            )}
          </div>

          {/* Domestic/International Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Travel Type
            </label>
            <div className="flex gap-2">
              {[
                { value: 'all', label: 'All' },
                { value: 'domestic', label: 'Domestic' },
                { value: 'international', label: 'International' }
              ].map(option => (
                <button
                  key={option.value}
                  onClick={() => setDomesticFilter(option.value as any)}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    domesticFilter === option.value
                      ? "bg-accent-cool text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Theme Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Themes
            </label>
            <div className="grid grid-cols-2 gap-2">
              {themes.map(theme => (
                <button
                  key={theme}
                  onClick={() => toggleTheme(theme)}
                  className={cn(
                    "px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    selectedThemes.includes(theme)
                      ? "bg-accent-cool text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  {theme}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Price Range: ₹{priceRange[0].toLocaleString()} - ₹{priceRange[1].toLocaleString()}
            </label>
            <div className="px-2">
              <div className="relative">
                <input
                  type="range"
                  min="0"
                  max="100000"
                  step="5000"
                  value={priceRange[0]}
                  onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
                  className="absolute w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
                <input
                  type="range"
                  min="0"
                  max="100000"
                  step="5000"
                  value={priceRange[1]}
                  onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                  className="absolute w-full h-2 bg-accent-cool rounded-lg appearance-none cursor-pointer slider-thumb"
                />
              </div>
            </div>
          </div>

          {/* Duration Range */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Duration: {durationRange[0]} - {durationRange[1]} days
            </label>
            <div className="px-2">
              <input
                type="range"
                min="1"
                max="15"
                value={durationRange[0]}
                onChange={(e) => setDurationRange([Number(e.target.value), durationRange[1]])}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer slider-thumb"
              />
              <input
                type="range"
                min="1"
                max="15"
                value={durationRange[1]}
                onChange={(e) => setDurationRange([durationRange[0], Number(e.target.value)])}
                className="w-full h-2 bg-accent-cool rounded-lg appearance-none cursor-pointer slider-thumb"
              />
            </div>
          </div>

          {/* Rating Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Minimum Rating
            </label>
            <div className="flex gap-2">
              {[0, 3, 4, 4.5].map(rating => (
                <button
                  key={rating}
                  onClick={() => setMinRating(rating)}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    minRating === rating
                      ? "bg-yellow-400 text-white"
                      : "bg-yellow-50 text-yellow-700 hover:bg-yellow-100"
                  )}
                >
                  {rating === 0 ? 'All' : `${rating}+`} ⭐
                </button>
              ))}
            </div>
          </div>

          {/* Close Button */}
          <div className="flex justify-end">
            <button
              onClick={() => setIsOpen(false)}
              className="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
