'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Search } from 'lucide-react'

export function HeroMasthead() {
  const [name, setName] = useState<string | null>(null)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    try {
      const raw = localStorage.getItem('tc_profile')
      if (!raw) return
      const parsed = JSON.parse(raw)
      setName(typeof parsed?.name === 'string' && parsed.name.trim() ? parsed.name.trim() : null)
    } catch {
      setName(null)
    }
  }, [])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleSearch = (query: string) => {
    if (query.trim()) {
      window.location.href = `/explore?q=${encodeURIComponent(query.trim())}`
    }
  }

  return (
    <section 
      className="relative z-0 h-screen text-white overflow-hidden bg-gradient-to-br from-slate-800 via-slate-700 to-slate-900 mt-[-4rem] pt-16"
      style={{
        backgroundImage: `linear-gradient(135deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.3) 100%), url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >

      {/* Transparent header overlay for homepage */}
      <div className={`fixed top-0 left-0 right-0 z-50 bg-transparent transition-opacity duration-200 ${scrolled ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}> 
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" aria-label="TripChoice home" className="p-1">
              <span className="font-serif text-2xl md:text-3xl font-medium text-white drop-shadow-sm">TripChoice</span>
            </Link>
            <nav className="hidden lg:flex items-center gap-8">
              {[
                { href: '/', label: 'Home' },
                { href: '/explore', label: 'Explore' },
                { href: '/favorites', label: 'Favorites' },
                { href: '/profile', label: 'Profile' },
              ].map((item) => (
                <Link key={item.href} href={item.href} className="px-4 py-2 text-sm font-medium text-white/90 hover:text-white border-b-2 border-transparent hover:border-white/70 transition">
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="flex items-center gap-4">
              <Link href="/explore" className="p-2 text-white hover:text-white/90">
                <Search className="w-5 h-5" />
                <span className="sr-only">Search</span>
              </Link>
              <Link href="/profile" className="px-4 py-2 text-sm font-medium text-white border border-white/40 rounded hover:bg-white/10 transition">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-8">
        <div className="text-center space-y-8 max-w-4xl mx-auto">
          {/* Hero Typography */}
          <div className="space-y-2">
            <h1 className="text-5xl md:text-7xl font-serif font-normal text-white leading-tight">
              Plan less.
            </h1>
            <h1 className="text-5xl md:text-7xl font-serif font-normal text-white leading-tight">
              Travel more.
            </h1>
          </div>
          
          <p className="text-lg md:text-xl text-white/90 font-normal mt-6">
            Trips made personal.
          </p>

          {/* Premium Search Bar */}
          <div className="max-w-xl mx-auto mt-12">
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-gray-500 group-focus-within:text-gray-700 transition-colors" />
              </div>
              <input
                type="search"
                placeholder="Search destinations"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch(e.currentTarget.value)
                  }
                }}
                className="w-full pl-12 pr-4 h-12 text-base rounded-full bg-white/95 backdrop-blur-sm text-gray-900 placeholder-gray-500 border-0 shadow-md focus:shadow-lg focus:ring-1 focus:ring-white/30 outline-none font-normal transition-all duration-300"
              />
            </div>
          </div>

          {/* Elegant Filter Pills */}
          <div className="flex flex-wrap items-center justify-center gap-3 mt-8">
            {[
              { label: 'Weekend', query: 'weekend' },
              { label: 'Under ₹15k', query: 'budget' },
              { label: 'Visa-free', query: 'visa free' },
              { label: 'Honeymoon', query: 'honeymoon' }
            ].map((filter) => (
              <button
                key={filter.label}
                onClick={() => window.location.href = `/explore?q=${encodeURIComponent(filter.query)}`}
                className="px-4 py-2 bg-white/15 backdrop-blur-sm text-white/90 rounded-full hover:bg-white/25 hover:text-white transition-all duration-300 border border-white/20 hover:border-white/40 font-normal text-sm"
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Subtle scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-1 h-8 bg-white/30 rounded-full"></div>
      </div>


    </section>
  )
}
