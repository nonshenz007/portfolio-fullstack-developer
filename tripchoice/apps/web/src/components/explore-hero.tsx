'use client'

import { useState, useEffect, useMemo } from 'react'
import { Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { analytics } from '@/lib/analytics'
import { Personalization } from '@/types'

export function ExploreHero() {
  const [searchQuery, setSearchQuery] = useState('')
  const [personalization, setPersonalization] = useState<Personalization | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('tc_profile')
    if (stored) {
      try {
        const profile = JSON.parse(stored)
        setPersonalization(profile)
      } catch (error) {
        console.error('Error parsing personalization data:', error)
      }
    }
  }, [])

  // Comprehensive search suggestions based on all destinations and themes
  const allSuggestions = [
    // Destinations
    'Goa', 'Kerala', 'Kashmir', 'Rajasthan', 'Himachal Pradesh', 'Andaman & Nicobar',
    'Thailand', 'Singapore', 'Malaysia', 'Dubai', 'Vietnam', 'Japan', 'Europe',
    'Paris', 'Amsterdam', 'South Africa', 'Bhutan', 'Nepal', 'Sri Lanka', 'Maldives',
    'Iceland', 'New Zealand', 'Australia', 'Uttarakhand', 'Maharashtra', 'Karnataka',
    'Punjab', 'Coorg', 'Mysore', 'Ajanta', 'Ellora', 'Rishikesh', 'Haridwar',
    'Jaipur', 'Udaipur', 'Shimla', 'Manali', 'Port Blair', 'Havelock Island',
    'Bangkok', 'Pattaya', 'Kuala Lumpur', 'Penang', 'Tokyo', 'Kyoto',
    'Cape Town', 'Paro', 'Thimphu', 'Kathmandu', 'Pokhara', 'Colombo', 'Kandy',
    'Male', 'Reykjavik', 'Queenstown', 'Sydney',

    // Themes & Activities
    'Beach', 'Mountains', 'Culture', 'Adventure', 'Weekend', 'Family', 'Honeymoon',
    'Luxury', 'Budget', 'Mid-range', 'Backwaters', 'Temple', 'Heritage', 'Royal',
    'Desert', 'Safari', 'Wildlife', 'Ayurveda', 'Yoga', 'Spiritual', 'Wellness',
    'Water Sports', 'Skiing', 'Trekking', 'Scuba Diving', 'Snorkeling', 'Cruise',
    'City Tour', 'Food Tour', 'Wine Tasting', 'Photography', 'Shopping',

    // Categories
    'Domestic', 'International', 'North India', 'South India', 'East India', 'West India',
    'Southeast Asia', 'Middle East', 'Europe', 'Africa', 'Asia Pacific',
    'Romantic', 'Group Tours', 'Solo Travel', 'Corporate', 'Student',

    // Experiences
    'Northern Lights', 'Great Barrier Reef', 'Safari', 'Cultural Immersion',
    'Adventure Sports', 'Relaxation', 'Historical Sites', 'Nature', 'Urban Exploration'
  ]

  // Generate search suggestions
  const suggestions = useMemo(() => {
    if (!searchQuery.trim()) return []

    const query = searchQuery.toLowerCase()
    const results = allSuggestions.filter(suggestion =>
      suggestion.toLowerCase().includes(query)
    )

    return results.slice(0, 6) // Limit to 6 suggestions
  }, [searchQuery])

  useEffect(() => {
    setShowSuggestions(searchQuery.trim().length > 0 && suggestions.length > 0)
  }, [searchQuery, suggestions])

  const handleSearch = () => {
    if (searchQuery.trim()) {
      analytics.trackSearchPerformed(searchQuery, {})
      // Navigate to explore page with search query
      window.location.href = `/explore?q=${encodeURIComponent(searchQuery)}`
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion)
    setShowSuggestions(false)
    analytics.trackSearchPerformed(suggestion, { source: 'suggestion' })
    setTimeout(() => {
      window.location.href = `/explore?q=${encodeURIComponent(suggestion)}`
    }, 100)
  }

  const handleInputFocus = () => {
    if (searchQuery.trim() && suggestions.length > 0) {
      setShowSuggestions(true)
    }
  }

  const handleInputBlur = () => {
    // Delay hiding suggestions to allow click events
    setTimeout(() => setShowSuggestions(false), 150)
  }

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white py-16 lg:py-24">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-5xl mx-auto">
          {/* Personalized Welcome */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              {personalization?.name ? (
                <>
                  Welcome back,<br />
                  <span className="text-accent-cool">{personalization.name}</span>
                </>
              ) : (
                <>
                  Plan less.<br />
                  <span className="text-accent-cool">Travel more.</span>
                </>
              )}
            </h1>
          </div>

          {/* Subtitle */}
          <p className="text-lg md:text-xl lg:text-2xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            Discover curated travel packages from India's finest destinations to exotic international getaways
          </p>

          {/* Enhanced Search Bar */}
          <div className="max-w-3xl mx-auto mb-8 px-4">
            <div className="relative">
              <form
                role="search"
                aria-label="Explore packages search"
                className="relative"
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSearch()
                }}
              >
                {/* Search Input with improved styling */}
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 sm:pl-6 flex items-center pointer-events-none z-10">
                    <Search className="h-5 w-5 sm:h-6 sm:w-6 text-slate-400" />
                  </div>
                  <Input
                    type="search"
                    aria-label="Search destinations, themes, or experiences"
                    placeholder="Search destinations, themes, or experiences..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleSearch()
                      }
                    }}
                    onFocus={handleInputFocus}
                    onBlur={handleInputBlur}
                    className="pl-12 sm:pl-16 pr-20 sm:pr-32 h-14 sm:h-16 text-base sm:text-lg rounded-2xl border-2 border-slate-600 focus:border-accent-cool bg-white text-slate-900 placeholder-slate-500 shadow-2xl focus:shadow-accent-cool/20 transition-all duration-300 focus:ring-0 focus:outline-none"
                  />
                  <Button
                    type="submit"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 h-10 sm:h-12 px-4 sm:px-8 bg-accent-cool hover:bg-accent-cool/90 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 z-10 text-sm sm:text-base"
                  >
                    <Search className="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" />
                    <span className="hidden sm:inline">Search</span>
                  </Button>
                </div>

                {/* Enhanced Search Suggestions */}
                {showSuggestions && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden z-[60] max-h-80 overflow-y-auto">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="w-full px-6 py-3 text-left hover:bg-slate-50 transition-colors border-b border-slate-100 last:border-b-0 flex items-center gap-3 group focus:bg-slate-50 focus:outline-none"
                      >
                        <div className="w-7 h-7 bg-accent-cool/10 rounded-lg flex items-center justify-center group-hover:bg-accent-cool/20 transition-colors flex-shrink-0">
                          <Search className="h-3.5 w-3.5 text-accent-cool" />
                        </div>
                        <span className="text-slate-900 font-medium text-sm truncate">{suggestion}</span>
                      </button>
                    ))}
                    {suggestions.length === 0 && searchQuery.trim() && (
                      <div className="px-6 py-3 text-slate-500 text-sm">
                        No suggestions found for "{searchQuery}"
                      </div>
                    )}
                  </div>
                )}
              </form>
            </div>

            {/* Popular Search Tags - Enhanced */}
            <div className="flex flex-wrap justify-center gap-2 sm:gap-3 mt-6 sm:mt-8 px-2">
              {['Beach', 'Mountains', 'International', 'Adventure', 'Luxury', 'Culture', 'Honeymoon', 'Kashmir', 'Goa', 'Dubai'].map((tag) => (
                <button
                  key={tag}
                  onClick={() => handleSuggestionClick(tag)}
                  className="px-4 sm:px-6 py-2 sm:py-3 bg-white/15 hover:bg-white/25 rounded-full text-xs sm:text-sm font-medium text-white hover:text-accent-cool transition-all duration-200 border border-white/30 hover:border-accent-cool/50 backdrop-blur-sm"
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
