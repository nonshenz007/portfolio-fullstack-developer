'use client'

import { Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PackageCard } from '@/components/package-card'
import { Package } from '@/types'

interface ExplorePackagesGridProps {
  packages: Package[]
  isLoading: boolean
  viewMode: 'grid' | 'list'
  clearAllFilters: () => void
}

export function ExplorePackagesGrid({
  packages,
  isLoading,
  viewMode,
  clearAllFilters
}: ExplorePackagesGridProps) {
  if (isLoading) {
    return (
      <div className={`grid gap-6 ${
        viewMode === 'grid'
          ? 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
          : 'grid-cols-1'
      }`}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-xl animate-pulse">
            <div className="aspect-[4/3] bg-slate-200 rounded-xl mb-4" />
            <div className="space-y-3">
              <div className="h-6 bg-slate-200 rounded w-3/4" />
              <div className="h-4 bg-slate-200 rounded w-1/2" />
              <div className="h-4 bg-slate-200 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (packages.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-100 rounded-full mb-4">
          <Search className="h-8 w-8 text-slate-400" />
        </div>
        <h3 className="text-xl font-semibold text-slate-900 mb-2">No destinations found</h3>
        <p className="text-slate-600 mb-6 max-w-md mx-auto">
          We couldn't find any packages matching your criteria. Try adjusting your filters or search terms.
        </p>
        <Button onClick={clearAllFilters} className="border border-cloud/50 hover:bg-cloud/20 text-ink bg-transparent">
          <X className="h-4 w-4 mr-2" />
          Clear All Filters
        </Button>
      </div>
    )
  }

  return (
    <div className={`grid gap-6 ${
      viewMode === 'grid'
        ? 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
        : 'grid-cols-1'
    }`}>
      {packages.map((pkg, index) => (
        <div
          key={pkg.id}
          className="animate-fade-in"
          style={{ animationDelay: `${index * 0.1}s` }}
        >
          <PackageCard pkg={pkg} />
        </div>
      ))}
    </div>
  )
}


