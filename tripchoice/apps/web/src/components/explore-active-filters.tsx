'use client'

import { X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

const THEMES = [
  { id: 'weekend', label: 'Weekend Getaway' },
  { id: 'budget', label: 'Budget Friendly' },
  { id: 'visa-free', label: 'Visa Free' },
  { id: 'honeymoon', label: 'Honeymoon' },
  { id: 'mountains', label: 'Mountains' },
  { id: 'beach', label: 'Beach' },
  { id: 'adventure', label: 'Adventure' },
  { id: 'cultural', label: 'Cultural' }
]

const DESTINATIONS = [
  { id: 'goa', label: 'Goa' },
  { id: 'kerala', label: 'Kerala' },
  { id: 'kashmir', label: 'Kashmir' },
  { id: 'bali', label: 'Bali' },
  { id: 'dubai', label: 'Dubai' },
  { id: 'danang', label: 'Da Nang' },
  { id: 'udaipur', label: 'Udaipur' },
  { id: 'rajasthan', label: 'Rajasthan' },
  { id: 'himachal', label: 'Himachal' }
]

const PRICE_RANGES = [
  { label: 'Under ₹10k', value: '0-10000' },
  { label: '₹10k - ₹20k', value: '10000-20000' },
  { label: '₹20k - ₹30k', value: '20000-30000' },
  { label: '₹30k+', value: '30000-999999' },
]

interface ExploreActiveFiltersProps {
  selectedThemes: string[]
  setSelectedThemes: React.Dispatch<React.SetStateAction<string[]>>
  selectedDestinations: string[]
  setSelectedDestinations: React.Dispatch<React.SetStateAction<string[]>>
  priceRange: string
  setPriceRange: React.Dispatch<React.SetStateAction<string>>
  domesticFilter: 'all' | 'domestic' | 'international'
  setDomesticFilter: React.Dispatch<React.SetStateAction<'all' | 'domestic' | 'international'>>
}

export function ExploreActiveFilters({
  selectedThemes,
  setSelectedThemes,
  selectedDestinations,
  setSelectedDestinations,
  priceRange,
  setPriceRange,
  domesticFilter,
  setDomesticFilter
}: ExploreActiveFiltersProps) {
  const removeTheme = (themeId: string) => {
    setSelectedThemes(prev => prev.filter(t => t !== themeId))
  }

  const removeDestination = (destinationId: string) => {
    setSelectedDestinations(prev => prev.filter(d => d !== destinationId))
  }

  const getActiveFiltersCount = () => {
    return (selectedThemes.length +
            selectedDestinations.length +
            (priceRange !== 'any' ? 1 : 0) +
            (domesticFilter !== 'all' ? 1 : 0))
  }

  if (getActiveFiltersCount() === 0) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-2 mb-6">
      {selectedThemes.map((themeId) => {
        const theme = THEMES.find(t => t.id === themeId)
        return theme ? (
          <Badge
            key={themeId}
            variant="secondary"
            className="bg-accent-cool/10 text-accent-cool hover:bg-accent-cool/20 cursor-pointer"
            onClick={() => removeTheme(themeId)}
          >
            {theme.label}
            <X className="h-3 w-3 ml-1" />
          </Badge>
        ) : null
      })}

      {selectedDestinations.map((destId) => {
        const dest = DESTINATIONS.find(d => d.id === destId)
        return dest ? (
          <Badge
            key={destId}
            variant="secondary"
            className="bg-slate-100 text-slate-800 hover:bg-slate-200 cursor-pointer"
            onClick={() => removeDestination(destId)}
          >
            {dest.label}
            <X className="h-3 w-3 ml-1" />
          </Badge>
        ) : null
      })}

      {priceRange !== 'any' && (
        <Badge
          variant="secondary"
          className="bg-cloud/20 text-ink hover:bg-cloud/30 cursor-pointer"
          onClick={() => setPriceRange('any')}
        >
          {PRICE_RANGES.find(r => r.value === priceRange)?.label}
          <X className="h-3 w-3 ml-1" />
        </Badge>
      )}

      {domesticFilter !== 'all' && (
        <Badge
          variant="secondary"
          className="bg-accent-cool/10 text-accent-cool hover:bg-accent-cool/20 cursor-pointer"
          onClick={() => setDomesticFilter('all')}
        >
          {domesticFilter === 'domestic' ? 'Domestic' : 'International'}
          <X className="h-3 w-3 ml-1" />
        </Badge>
      )}
    </div>
  )
}


