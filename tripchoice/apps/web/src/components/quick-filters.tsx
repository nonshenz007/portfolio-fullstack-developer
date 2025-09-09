'use client'

import { useState } from 'react'
import { Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function QuickFilters() {
  const [selectedThemes, setSelectedThemes] = useState<string[]>([])

  const themes = [
    'Adventure', 'Beach', 'Culture', 'Luxury', 'Nature', 'Romance',
    'Family', 'Solo', 'Group', 'Wellness', 'Food', 'Shopping'
  ]

  const toggleTheme = (theme: string) => {
    setSelectedThemes(prev =>
      prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme]
    )
  }

  return (
    <div className="space-y-12">
      {/* Section Header */}
      <div className="text-center space-y-4">
        <div className="inline-block px-4 py-2 bg-slate-200 text-slate-700 rounded-full text-sm font-medium mb-4">
          Smart Filters
        </div>
        <h2 className="text-4xl md:text-5xl font-bold text-slate-900">
          Find Your Perfect Trip
        </h2>
        <p className="text-slate-700 text-lg max-w-2xl mx-auto">
          Filter by your preferences and discover amazing experiences tailored just for you
        </p>
      </div>

      {/* Theme Filters */}
      <div className="space-y-6">
        <h3 className="text-2xl font-semibold text-slate-900 text-center">Popular Themes</h3>
        <div className="flex flex-wrap justify-center gap-4">
          {themes.map((theme, index) => (
            <button
              key={theme}
              onClick={() => {
                // Toggle local state for visual feedback
                toggleTheme(theme)
                // Navigate to explore page with theme filter
                const currentThemes = selectedThemes.includes(theme) 
                  ? selectedThemes.filter(t => t !== theme)
                  : [...selectedThemes, theme]
                
                if (currentThemes.length > 0) {
                  window.location.href = `/explore?themes=${currentThemes.join(',')}`
                } else {
                  window.location.href = '/explore'
                }
              }}
              className={`px-6 py-3 rounded-full font-medium transition-all duration-300 transform hover:scale-105 hover:shadow-lg ${
                selectedThemes.includes(theme)
                  ? 'bg-slate-900 text-white shadow-xl scale-105'
                  : 'bg-white text-slate-800 border border-slate-300 hover:border-slate-400 hover:bg-slate-50'
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {theme}
            </button>
          ))}
        </div>
      </div>

      {/* Quick Categories */}
      <div className="grid md:grid-cols-3 gap-8">
        <div 
          onClick={() => window.location.href = '/explore?price=0-25000'}
          className="bg-white rounded-2xl p-8 border border-slate-200 hover:border-slate-300 transition-all duration-300 transform hover:scale-105 hover:shadow-xl group cursor-pointer"
        >
          <div className="text-3xl mb-4">💰</div>
          <h4 className="text-xl font-semibold text-slate-900 mb-3 group-hover:text-slate-700 transition-colors">Budget Friendly</h4>
          <p className="text-slate-700 mb-6 leading-relaxed">Great deals under ₹25,000 for amazing value</p>
          <Button variant="default" size="sm" className="bg-slate-900 text-white hover:bg-slate-800 transition-all duration-300">
            Explore Deals →
          </Button>
        </div>

        <div 
          onClick={() => window.location.href = '/explore?duration=1-4&themes=Weekend'}
          className="bg-white rounded-2xl p-8 border border-slate-200 hover:border-slate-300 transition-all duration-300 transform hover:scale-105 hover:shadow-xl group cursor-pointer"
        >
          <div className="text-3xl mb-4">🏖️</div>
          <h4 className="text-xl font-semibold text-slate-900 mb-3 group-hover:text-slate-700 transition-colors">Weekend Getaways</h4>
          <p className="text-slate-700 mb-6 leading-relaxed">Perfect 2-3 day trips for quick refreshers</p>
          <Button variant="default" size="sm" className="bg-slate-900 text-white hover:bg-slate-800 transition-all duration-300">
            Quick Trips →
          </Button>
        </div>

        <div 
          onClick={() => window.location.href = '/explore?q=last minute deals'}
          className="bg-white rounded-2xl p-8 border border-slate-200 hover:border-slate-300 transition-all duration-300 transform hover:scale-105 hover:shadow-xl group cursor-pointer"
        >
          <div className="text-3xl mb-4">⚡</div>
          <h4 className="text-xl font-semibold text-slate-900 mb-3 group-hover:text-slate-700 transition-colors">Last Minute Deals</h4>
          <p className="text-slate-700 mb-6 leading-relaxed">Book today, travel tomorrow at great rates</p>
          <Button variant="default" size="sm" className="bg-slate-900 text-white hover:bg-slate-800 transition-all duration-300">
            Flash Sales →
          </Button>
        </div>
      </div>
    </div>
  )
}
