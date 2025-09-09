
'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import Image from 'next/image'

export function ModernExploreHero() {
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = () => {
    if (searchQuery.trim()) {
      window.location.href = `/explore?q=${encodeURIComponent(searchQuery.trim())}`
    }
  }

  return (
    <section className="relative text-white py-24 overflow-hidden">
      {/* Background photo */}
      <div className="absolute inset-0 -z-10">
        <Image
          src="https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=2400&q=80"
          alt="Dramatic mountain landscape at sunrise"
          fill
          priority
          sizes="100vw"
          className="object-cover"
        />
      </div>
      {/* Gradient scrim for contrast */}
      <div className="absolute inset-0 -z-0 bg-gradient-to-br from-blue-950/80 via-blue-900/60 to-indigo-950/85" />

      {/* Subtle floating elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-16 h-16 bg-white/5 rounded-full blur-lg"></div>
        <div className="absolute top-40 right-32 w-12 h-12 bg-white/10 rounded-full blur-lg"></div>
        <div className="absolute bottom-32 left-1/3 w-20 h-20 bg-white/5 rounded-full blur-lg"></div>
        <div className="absolute top-1/2 right-20 w-14 h-14 bg-white/10 rounded-full blur-lg"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Main Heading */}
          <div className="space-y-4">
            <div className="inline-block px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 text-white font-medium text-sm mb-4">
              Your Journey Starts Here
            </div>
            <h1 className="text-5xl md:text-7xl font-bold leading-tight text-white">
              Discover Your Next Adventure
            </h1>
            <p className="text-xl md:text-2xl text-white/90 max-w-3xl mx-auto leading-relaxed">
              Explore curated travel packages from India's finest destinations to exotic international getaways
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto">
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-6 w-6 text-gray-400 group-hover:text-white transition-colors duration-300" />
              </div>
              <Input
                type="search"
                placeholder="Search destinations, themes, or experiences..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleSearch()
                  }
                }}
                className="pl-12 pr-32 h-16 text-lg rounded-full bg-white/90 backdrop-blur-sm text-gray-900 placeholder-gray-500 border border-white/20 shadow-2xl hover:shadow-white/20 transition-all duration-300 focus:ring-4 focus:ring-white/30"
              />
              <Button
                onClick={handleSearch}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-12 px-8 bg-slate-900 hover:bg-slate-800 text-white rounded-full font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              >
                Search
              </Button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid md:grid-cols-3 gap-8 pt-16">
            <div className="text-center">
              <div className="text-4xl font-bold text-white">500+</div>
              <div className="text-white/80">Destinations</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white">50,000+</div>
              <div className="text-white/80">Happy Travelers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white">4.8/5</div>
              <div className="text-white/80">Customer Rating</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
