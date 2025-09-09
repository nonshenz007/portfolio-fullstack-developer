'use client'

import { useState, useCallback } from 'react'
import { X, SlidersHorizontal, ChevronDown } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { analytics } from '@/lib/analytics'
import { cn } from '@/lib/utils'

interface FiltersBarProps {
  onFiltersChange?: (filters: FilterState) => void
}

export interface FilterState {
  search?: string
  domestic: 'all' | 'domestic' | 'international'
  themes: string[]
  priceRange: { min: number; max: number }
  durationRange: { min: number; max: number }
  minRating: number
  sortBy: 'price-low' | 'price-high' | 'rating' | 'duration' | 'popular'
}

const THEME_CHIPS = ['Weekend', 'Honeymoon', 'Mountains', 'Beach', 'Adventure', 'Culture', 'International', 'Family']

export function FiltersBar({ onFiltersChange }: FiltersBarProps) {
  const [filters, setFilters] = useState<FilterState>({
    domestic: 'all',
    themes: [],
    priceRange: { min: 0, max: 50000 },
    durationRange: { min: 1, max: 15 },
    minRating: 0,
    sortBy: 'popular'
  })

  const [advancedOpen, setAdvancedOpen] = useState(false)

  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    const updated = { ...filters, ...newFilters }
    setFilters(updated)
    onFiltersChange?.(updated)
  }, [filters, onFiltersChange])



  const toggleTheme = useCallback((theme: string) => {
    const newThemes = filters.themes.includes(theme)
      ? filters.themes.filter(t => t !== theme)
      : [...filters.themes, theme]
    
    updateFilters({ themes: newThemes })
    analytics.trackFilterApplied('theme', theme)
  }, [filters.themes, updateFilters])

  const setDomesticFilter = useCallback((domestic: FilterState['domestic']) => {
    updateFilters({ domestic })
    analytics.trackFilterApplied('domestic', domestic)
  }, [updateFilters])

  const handlePriceRangeChange = useCallback((value: number[]) => {
    updateFilters({ priceRange: { min: value[0], max: value[1] } })
    analytics.trackFilterApplied('price_range', `${value[0]}-${value[1]}`)
  }, [updateFilters])

  const handleDurationRangeChange = useCallback((value: number[]) => {
    updateFilters({ durationRange: { min: value[0], max: value[1] } })
    analytics.trackFilterApplied('duration_range', `${value[0]}-${value[1]}`)
  }, [updateFilters])

  const handleMinRatingChange = useCallback((rating: string) => {
    const ratingValue = parseFloat(rating)
    updateFilters({ minRating: ratingValue })
    analytics.trackFilterApplied('min_rating', ratingValue)
  }, [updateFilters])

  const handleSortChange = useCallback((sortBy: FilterState['sortBy']) => {
    updateFilters({ sortBy })
    analytics.trackFilterApplied('sort_by', sortBy)
  }, [updateFilters])

  const clearAllFilters = useCallback(() => {
    const cleared: FilterState = {
      search: '',
      domestic: 'all',
      themes: [],
      priceRange: { min: 0, max: 50000 },
      durationRange: { min: 1, max: 15 },
      minRating: 0,
      sortBy: 'popular'
    }
    setFilters(cleared)
    onFiltersChange?.(cleared)
  }, [onFiltersChange])

  const hasActiveFilters = filters.domestic !== 'all' ||
    filters.themes.length > 0 ||
    filters.priceRange.min > 0 ||
    filters.priceRange.max < 50000 ||
    filters.durationRange.min > 1 ||
    filters.durationRange.max < 15 ||
    filters.minRating > 0 ||
    filters.sortBy !== 'popular';

  return (
    <div className="sticky top-20 z-40 bg-white/98 backdrop-blur-md border-b border-slate-200/80 shadow-lg">
      <div className="container mx-auto px-4 py-5">
        <div className="space-y-6">
          {/* Header with Quick Filters */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            {/* Domestic Toggle */}
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="flex bg-slate-100 rounded-xl p-1 border border-slate-200">
                <button
                  onClick={() => setDomesticFilter('domestic')}
                  className={cn(
                    "px-3 sm:px-6 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200",
                    filters.domestic === 'domestic'
                      ? "bg-accent-cool text-white shadow-lg"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  )}
                >
                  Domestic
                </button>
                <button
                  onClick={() => setDomesticFilter('international')}
                  className={cn(
                    "px-3 sm:px-6 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200",
                    filters.domestic === 'international'
                      ? "bg-accent-cool text-white shadow-lg"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  )}
                >
                  International
                </button>
              </div>

              {/* Clear Filters */}
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearAllFilters}
                  className="text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200"
                >
                  <X className="h-4 w-4 mr-2" strokeWidth={1.75} />
                  Clear all filters
                </Button>
              )}
            </div>

            {/* Sort Dropdown */}
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-slate-700">Sort by:</span>
              <Select value={filters.sortBy} onValueChange={handleSortChange}>
                <SelectTrigger className="w-52 border-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="popular">Most Popular</SelectItem>
                  <SelectItem value="rating">Highest Rated</SelectItem>
                  <SelectItem value="price-low">Price: Low to High</SelectItem>
                  <SelectItem value="price-high">Price: High to Low</SelectItem>
                  <SelectItem value="duration">Duration: Short to Long</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Theme Chips */}
          <div className="flex items-center gap-2 sm:gap-3 overflow-x-auto pb-2 scrollbar-hide">
            {THEME_CHIPS.map((theme) => (
              <button
                key={theme}
                onClick={() => toggleTheme(theme)}
                className={cn(
                  "flex-shrink-0 px-3 sm:px-5 py-2 sm:py-2.5 text-xs sm:text-sm font-medium rounded-xl transition-all duration-200 border",
                  filters.themes.includes(theme)
                    ? "bg-accent-warm text-white border-accent-warm shadow-lg"
                    : "bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border-slate-200 hover:border-slate-300"
                )}
              >
                {theme}
              </button>
            ))}
          </div>

          {/* Advanced Filters Section */}
          <Collapsible open={advancedOpen} onOpenChange={setAdvancedOpen}>
            <CollapsibleTrigger asChild>
              <button className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors group">
                <SlidersHorizontal className="h-4 w-4" strokeWidth={1.75} />
                Advanced Filters
                <ChevronDown className={cn(
                  "h-4 w-4 transition-transform duration-200",
                  advancedOpen && "rotate-180"
                )} strokeWidth={1.75} />
              </button>
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-6 pt-6 border-t border-slate-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Price Range */}
                <div className="space-y-4">
                  <label className="text-sm font-semibold text-slate-900">Price Range (₹)</label>
                  <div className="px-2">
                    <Slider
                      value={[filters.priceRange.min, filters.priceRange.max]}
                      onValueChange={handlePriceRangeChange}
                      max={50000}
                      min={0}
                      step={1000}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-slate-600 mt-3 font-medium">
                      <span>₹{filters.priceRange.min.toLocaleString()}</span>
                      <span>₹{filters.priceRange.max.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Duration Range */}
                <div className="space-y-4">
                  <label className="text-sm font-semibold text-slate-900">Duration (Days)</label>
                  <div className="px-2">
                    <Slider
                      value={[filters.durationRange.min, filters.durationRange.max]}
                      onValueChange={handleDurationRangeChange}
                      max={15}
                      min={1}
                      step={1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-slate-600 mt-3 font-medium">
                      <span>{filters.durationRange.min} days</span>
                      <span>{filters.durationRange.max} days</span>
                    </div>
                  </div>
                </div>

                {/* Minimum Rating */}
                <div className="space-y-4">
                  <label className="text-sm font-semibold text-slate-900">Minimum Rating</label>
                  <Select value={filters.minRating.toString()} onValueChange={handleMinRatingChange}>
                    <SelectTrigger className="w-full border-slate-200">
                      <SelectValue placeholder="Any rating" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">Any rating</SelectItem>
                      <SelectItem value="3">3+ stars</SelectItem>
                      <SelectItem value="3.5">3.5+ stars</SelectItem>
                      <SelectItem value="4">4+ stars</SelectItem>
                      <SelectItem value="4.5">4.5+ stars</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </div>
    </div>
  )
}
