'use client'

import { Search, X, SlidersHorizontal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const THEMES = [
  { id: 'weekend', label: 'Weekend Getaway', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  { id: 'budget', label: 'Budget Friendly', color: 'bg-green-50 text-green-700 border-green-200' },
  { id: 'visa-free', label: 'Visa Free', color: 'bg-purple-50 text-purple-700 border-purple-200' },
  { id: 'honeymoon', label: 'Honeymoon', color: 'bg-pink-50 text-pink-700 border-pink-200' },
  { id: 'mountains', label: 'Mountains', color: 'bg-slate-50 text-slate-700 border-slate-200' },
  { id: 'beach', label: 'Beach', color: 'bg-cyan-50 text-cyan-700 border-cyan-200' },
  { id: 'adventure', label: 'Adventure', color: 'bg-orange-50 text-orange-700 border-orange-200' },
  { id: 'cultural', label: 'Cultural', color: 'bg-sky-50 text-sky-700 border-sky-200' }
]

const DESTINATIONS = [
  { id: 'goa', label: 'Goa', region: 'West India' },
  { id: 'kerala', label: 'Kerala', region: 'South India' },
  { id: 'kashmir', label: 'Kashmir', region: 'North India' },
  { id: 'bali', label: 'Bali', region: 'Indonesia' },
  { id: 'dubai', label: 'Dubai', region: 'UAE' },
  { id: 'danang', label: 'Da Nang', region: 'Vietnam' },
  { id: 'udaipur', label: 'Udaipur', region: 'West India' },
  { id: 'rajasthan', label: 'Rajasthan', region: 'North India' },
  { id: 'himachal', label: 'Himachal', region: 'North India' }
]

const PRICE_RANGES = [
  { label: 'Under ₹10k', value: '0-10000', color: 'bg-emerald-50 text-emerald-700' },
  { label: '₹10k - ₹20k', value: '10000-20000', color: 'bg-green-50 text-green-700' },
  { label: '₹20k - ₹30k', value: '20000-30000', color: 'bg-sky-50 text-sky-700' },
  { label: '₹30k+', value: '30000-999999', color: 'bg-orange-50 text-orange-700' },
]

const SORT_OPTIONS = [
  { value: 'popularity', label: 'Most Popular', desc: 'Trending destinations' },
  { value: 'rating', label: 'Highest Rated', desc: 'Best reviewed packages' },
  { value: 'price-low', label: 'Price: Low to High', desc: 'Budget-friendly first' },
  { value: 'price-high', label: 'Price: High to Low', desc: 'Premium first' },
  { value: 'duration', label: 'Shortest Duration', desc: 'Quick getaways' },
  { value: 'newest', label: 'Recently Added', desc: 'Latest packages' }
]

const SAVED_FILTERS = [
  { id: 'weekend-special', name: 'Weekend Special', filters: { themes: ['weekend'], priceRange: '0-15000' } },
  { id: 'luxury-escape', name: 'Luxury Escape', filters: { themes: ['honeymoon'], priceRange: '30000-999999' } },
  { id: 'budget-adventure', name: 'Budget Adventure', filters: { themes: ['adventure'], priceRange: '0-15000' } },
  { id: 'cultural-journey', name: 'Cultural Journey', filters: { themes: ['cultural'], domestic: true } }
]

interface ExploreFiltersProps {
  searchQuery: string
  setSearchQuery: React.Dispatch<React.SetStateAction<string>>
  selectedThemes: string[]
  setSelectedThemes: React.Dispatch<React.SetStateAction<string[]>>
  selectedDestinations: string[]
  setSelectedDestinations: React.Dispatch<React.SetStateAction<string[]>>
  priceRange: string
  setPriceRange: React.Dispatch<React.SetStateAction<string>>
  domesticFilter: 'all' | 'domestic' | 'international'
  setDomesticFilter: React.Dispatch<React.SetStateAction<'all' | 'domestic' | 'international'>>
  sortBy: string
  setSortBy: React.Dispatch<React.SetStateAction<string>>
  isFiltersOpen: boolean
  setIsFiltersOpen: React.Dispatch<React.SetStateAction<boolean>>
  getActiveFiltersCount: () => number
  clearAllFilters: () => void
  handleSearch: () => void
}

export function ExploreFilters({
  searchQuery,
  setSearchQuery,
  selectedThemes,
  setSelectedThemes,
  selectedDestinations,
  setSelectedDestinations,
  priceRange,
  setPriceRange,
  domesticFilter,
  setDomesticFilter,
  sortBy,
  setSortBy,
  isFiltersOpen,
  setIsFiltersOpen,
  getActiveFiltersCount,
  clearAllFilters,
  handleSearch
}: ExploreFiltersProps) {
  const toggleTheme = (themeId: string) => {
    setSelectedThemes(prev =>
      prev.includes(themeId)
        ? prev.filter(t => t !== themeId)
        : [...prev, themeId]
    )
  }

  const toggleDestination = (destinationId: string) => {
    setSelectedDestinations(prev =>
      prev.includes(destinationId)
        ? prev.filter(d => d !== destinationId)
        : [...prev, destinationId]
    )
  }

  const FilterContent = () => (
    <aside className="space-y-6">
      {/* Search */}
      <Card interactive={false} className="shadow-none">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search & Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              type="search"
              placeholder="Search destinations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  handleSearch()
                }
              }}
              className="pl-10 h-12"
            />
          </div>

          {/* Travel Type */}
          <div>
            <h4 className="text-sm font-semibold mb-3">Travel Type</h4>
            <div className="grid grid-cols-1 gap-2">
              {[
                { value: 'all', label: 'All Destinations', desc: 'Domestic & International' },
              { value: 'domestic', label: 'Domestic', desc: 'Indian destinations' },
              { value: 'international', label: 'International', desc: 'Global adventures' }
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setDomesticFilter(option.value as any)}
                  className={`p-3 text-left rounded-lg border hover:bg-cloud/20 ${
                    domesticFilter === option.value
                      ? 'border-accent-cool/50 bg-accent-cool/10 text-ink'
                      : 'border-cloud/40 hover:border-cloud/60'
                  }`}
                >
                  <div className="font-medium">{option.label}</div>
                  <div className="text-xs text-slate-600 mt-1">{option.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div>
            <h4 className="text-sm font-semibold mb-3">Budget Range</h4>
            <div className="grid grid-cols-2 gap-2">
              {PRICE_RANGES.map((range) => (
                <button
                  key={range.value}
                  onClick={() => setPriceRange(range.value)}
                  className={`p-3 text-center rounded-lg border hover:bg-cloud/20 ${
                    priceRange === range.value
                      ? 'border-accent-cool/50 bg-accent-cool/10 text-ink'
                      : 'border-cloud/40 hover:border-cloud/60'
                  }`}
                >
                  <div className="font-medium text-sm">{range.label}</div>
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Themes */}
      <Card interactive={false} className="shadow-none">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Travel Themes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            {THEMES.map((theme) => (
              <button
                key={theme.id}
                onClick={() => toggleTheme(theme.id)}
                className={`p-3 text-center rounded-lg border hover:bg-cloud/20 ${
                  selectedThemes.includes(theme.id)
                    ? 'border-accent-cool/50 bg-accent-cool/10'
                    : 'border-cloud/40 hover:border-cloud/60'
                }`}
              >
                <div className="font-medium text-sm">{theme.label}</div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Destinations */}
      <Card interactive={false} className="shadow-none">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">Popular Destinations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {DESTINATIONS.map((destination) => (
              <button
                key={destination.id}
                onClick={() => toggleDestination(destination.id)}
                className={`w-full p-3 text-left rounded-lg border hover:bg-cloud/20 ${
                  selectedDestinations.includes(destination.id)
                    ? 'border-accent-cool/50 bg-accent-cool/10'
                    : 'border-cloud/40 hover:border-cloud/60'
                }`}
              >
                <div>
                  <div className="font-medium">{destination.label}</div>
                  <div className="text-xs text-slate-600">{destination.region}</div>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Clear Filters */}
      {getActiveFiltersCount() > 0 && (
        <Button
          variant="outline"
          onClick={clearAllFilters}
          className="w-full h-12 border-2 border-cloud/50 hover:border-cloud/70 hover:bg-cloud/20 text-ink"
        >
          <X className="h-4 w-4 mr-2" />
          Clear All Filters ({getActiveFiltersCount()})
        </Button>
      )}
    </aside>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:block w-60 flex-shrink-0">
        <div className="sticky top-24">
          <FilterContent />
        </div>
      </div>

      {/* Mobile Filter Button */}
      <div className="lg:hidden mb-6">
        <Sheet open={isFiltersOpen} onOpenChange={setIsFiltersOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" className="w-full h-12">
              <SlidersHorizontal className="h-5 w-5 mr-2" />
              Filters {getActiveFiltersCount() > 0 && `(${getActiveFiltersCount()})`}
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-full sm:w-96 overflow-y-auto">
            <div className="py-6">
              <FilterContent />
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </>
  )
}
