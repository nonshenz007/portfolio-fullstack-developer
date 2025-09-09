'use client'

import { useState } from 'react'

interface FunctionalFiltersProps {
  className?: string
}

export function FunctionalFilters({ className = "" }: FunctionalFiltersProps) {
  const [selectedThemes, setSelectedThemes] = useState<string[]>([])

  const themes = [
    'Adventure', 'Beach', 'Culture', 'Luxury', 'Nature', 'Romance',
    'Family', 'Solo', 'Weekend', 'Budget', 'Mountains', 'Heritage'
  ]

  const priceRanges = [
    { label: 'Under ₹15k', value: '0-15000' },
    { label: '₹15k - ₹30k', value: '15000-30000' },
    { label: '₹30k - ₹50k', value: '30000-50000' },
    { label: 'Above ₹50k', value: '50000-999999' }
  ]

  const toggleTheme = (theme: string) => {
    setSelectedThemes(prev =>
      prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme]
    )
  }

  const applyFilters = () => {
    const params = new URLSearchParams()
    if (selectedThemes.length > 0) {
      params.set('themes', selectedThemes.join(','))
    }
    
    const url = params.toString() ? `/explore?${params.toString()}` : '/explore'
    window.location.href = url
  }

  const handlePriceFilter = (priceRange: string) => {
    window.location.href = `/explore?price=${priceRange}`
  }

  const handleQuickFilter = (filter: string) => {
    window.location.href = `/explore?q=${encodeURIComponent(filter)}`
  }

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Quick Filters */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Quick Filters</h3>
        <div className="flex flex-wrap gap-3">
          {['Weekend Getaway', 'Budget Friendly', 'Luxury', 'Adventure', 'Beach', 'Mountains'].map((filter) => (
            <button
              key={filter}
              onClick={() => handleQuickFilter(filter)}
              className="px-4 py-2 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors text-sm font-medium"
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Budget Range</h3>
        <div className="grid grid-cols-2 gap-3">
          {priceRanges.map((range) => (
            <button
              key={range.value}
              onClick={() => handlePriceFilter(range.value)}
              className="p-3 text-center border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Themes */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Travel Themes</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {themes.map((theme) => (
            <button
              key={theme}
              onClick={() => toggleTheme(theme)}
              className={`p-3 text-center rounded-lg border transition-colors ${
                selectedThemes.includes(theme)
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {theme}
            </button>
          ))}
        </div>
        
        {selectedThemes.length > 0 && (
          <div className="mt-4 flex gap-3">
            <button
              onClick={applyFilters}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Apply Filters ({selectedThemes.length})
            </button>
            <button
              onClick={() => setSelectedThemes([])}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear
            </button>
          </div>
        )}
      </div>

      {/* Travel Type */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Travel Type</h3>
        <div className="space-y-2">
          <button
            onClick={() => window.location.href = '/explore?domestic=domestic'}
            className="w-full p-3 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <div className="font-medium">Domestic</div>
            <div className="text-sm text-gray-600">Explore India</div>
          </button>
          <button
            onClick={() => window.location.href = '/explore?domestic=international'}
            className="w-full p-3 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <div className="font-medium">International</div>
            <div className="text-sm text-gray-600">Global destinations</div>
          </button>
        </div>
      </div>
    </div>
  )
}