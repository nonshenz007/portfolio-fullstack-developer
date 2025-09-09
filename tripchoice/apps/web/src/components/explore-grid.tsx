'use client'

import { useState, useMemo } from 'react'
import { usePackages } from '@/hooks/use-packages'
import { Package } from '@/types'
import { PackageFilters } from '@/lib/cms'
import { ExplorePackagesGrid } from '@/components/explore-packages-grid'

export function ExploreGrid() {
  const [filters, setFilters] = useState<PackageFilters>({
    limit: 20
  })

  const { data: packages = [], isLoading, error } = usePackages(filters)

    if (error) {
    return (
      <div className="text-center py-16">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h3>
        <p className="text-gray-600">Failed to load travel packages. Please try again later.</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {packages.length > 0 && !isLoading && (
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Explore Destinations</h2>
          <p className="text-gray-600">Found {packages.length} amazing destinations for you</p>
        </div>
      )}

      <ExplorePackagesGrid
        packages={packages as Package[]}
        isLoading={isLoading}
        viewMode="grid"
        clearAllFilters={() => setFilters({ limit: 20 })}
      />

      {isLoading && (
        <div className="text-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading destinations...</h3>
          <p className="text-gray-600">Finding the perfect places for your journey</p>
        </div>
      )}

      {!isLoading && packages.length === 0 && (
        <div className="text-center py-16">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No destinations found</h3>
          <p className="text-gray-600">Try adjusting your search criteria</p>
        </div>
      )}
    </div>
  )
}
