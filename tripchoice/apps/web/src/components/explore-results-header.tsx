'use client'

import { TrendingUp, Grid3X3, List } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const SORT_OPTIONS = [
  { value: 'popularity', label: 'Most Popular', desc: 'Trending destinations' },
  { value: 'rating', label: 'Highest Rated', desc: 'Best reviewed packages' },
  { value: 'price-low', label: 'Price: Low to High', desc: 'Budget-friendly first' },
  { value: 'price-high', label: 'Price: High to Low', desc: 'Premium first' },
  { value: 'duration', label: 'Shortest Duration', desc: 'Quick getaways' },
  { value: 'newest', label: 'Recently Added', desc: 'Latest packages' }
]

interface ExploreResultsHeaderProps {
  packages: any[]
  isLoading: boolean
  filters: any
  onClearFilters: () => void
  viewMode?: 'grid' | 'list'
  onViewModeChange?: (mode: 'grid' | 'list') => void
}

export function ExploreResultsHeader({
  packages,
  isLoading,
  filters,
  onClearFilters,
  viewMode = 'grid',
  onViewModeChange
}: ExploreResultsHeaderProps) {
  // Calculate active filters count
  const activeFiltersCount = [
    filters.search,
    filters.domestic !== 'all',
    filters.themes.length > 0,
    filters.priceRange.min > 0 || filters.priceRange.max < 50000,
    filters.durationRange.min > 1 || filters.durationRange.max < 15,
    filters.minRating > 0,
    filters.sortBy !== 'popular'
  ].filter(Boolean).length

  return (
    <header className="flex flex-col gap-4 mb-8">
      {/* Results summary */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-accent-cool" />
            <h2 className="text-ink font-semibold">
              {isLoading ? 'Discovering destinations...' : `${packages.length} amazing destinations`}
            </h2>
          </div>
          {activeFiltersCount > 0 && (
            <Badge variant="secondary" className="bg-accent-cool/10 text-accent-cool">
              {activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} applied
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="hidden sm:flex bg-cloud/10 rounded-lg p-1 border border-cloud/20">
            <button
              type="button"
              aria-label="Grid view"
              onClick={() => onViewModeChange?.('grid')}
              className={`px-2 py-1 rounded-md ${viewMode === 'grid' ? 'bg-white shadow-e1' : 'hover:bg-cloud/20'}`}
            >
              <Grid3X3 className="h-4 w-4" />
            </button>
            <button
              type="button"
              aria-label="List view"
              onClick={() => onViewModeChange?.('list')}
              className={`px-2 py-1 rounded-md ${viewMode === 'list' ? 'bg-white shadow-e1' : 'hover:bg-cloud/20'}`}
            >
              <List className="h-4 w-4" />
            </button>
          </div>

          {activeFiltersCount > 0 && (
            <Button variant="ghost" size="sm" onClick={onClearFilters} className="text-slate hover:text-ink">
              Clear all filters
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
