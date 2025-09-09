"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { PersonalizeModal } from '@/components/personalize-modal'
import { Menu, X, Search, User } from 'lucide-react'

export function Header() {
  const [showPersonalizeModal, setShowPersonalizeModal] = useState(false)
  const [userName, setUserName] = useState<string | null>(null)
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const pathname = usePathname()
  
  // Check if we're on the homepage
  const isHomepage = pathname === '/'

  const navigationItems = [
    { href: '/', label: 'Home' },
    { href: '/explore', label: 'Explore' },
    { href: '/favorites', label: 'Favorites' },
    { href: '/profile', label: 'Profile' },
  ]

  useEffect(() => {
    // Only access localStorage on client side
    if (typeof window !== 'undefined') {
      const profile = localStorage.getItem('tc_profile')
      const hasVisited = localStorage.getItem('tc_visited')

      if (profile) {
        try {
          const { name } = JSON.parse(profile)
          setUserName(name)
        } catch (e) {
          console.warn('Failed to parse profile')
        }
      }

      // Auto-open modal on first visit
      if (!hasVisited && !profile) {
        setShowPersonalizeModal(true)
        localStorage.setItem('tc_visited', 'true')
      }
    }
  }, [])

  // Handle scroll effect for dynamic header
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY
      setScrolled(scrollPosition > 50)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on escape key or outside click
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false)
        setShowSearch(false)
      }
    }

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Element
      if (mobileMenuOpen && !target.closest('header')) {
        setMobileMenuOpen(false)
      }
    }

    if (mobileMenuOpen) {
      document.addEventListener('keydown', handleEscape)
      document.addEventListener('click', handleClickOutside)
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('click', handleClickOutside)
    }
  }, [mobileMenuOpen])

  const handlePersonalizeClose = (open: boolean) => {
    setShowPersonalizeModal(open)

    // Refresh user name after modal closes
    if (!open && typeof window !== 'undefined') {
      const profile = localStorage.getItem('tc_profile')
      if (profile) {
        try {
          const { name } = JSON.parse(profile)
          setUserName(name)
        } catch (e) {
          console.warn('Failed to parse profile')
        }
      }
    }
  }

  const transparent = isHomepage && !scrolled

  // On the homepage at the very top, do not render the default header.
  // A transparent overlay header is rendered by the HeroMasthead instead.
  if (transparent) {
    return (
      <>
        <PersonalizeModal 
          open={showPersonalizeModal} 
          onOpenChange={handlePersonalizeClose}
        />
      </>
    )
  }

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 bg-white shadow-lg border-b border-gray-200`}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Brand */}
            <Link
              href="/"
              aria-label="TripChoice home"
              className={`focus:outline-none focus:ring-2 rounded p-1 transition-all duration-300 ${
                transparent ? 'focus:ring-white/60 focus:ring-offset-0' : 'focus:ring-gray-500 focus:ring-offset-2'
              }`}
            >
              <span className={`font-serif text-2xl md:text-3xl font-medium transition-all duration-300 ${
                transparent ? 'text-white drop-shadow-sm' : 'text-gray-900'
              }`}>
                TripChoice
              </span>
            </Link>

            {/* Center Navigation */}
            <nav className="hidden lg:flex items-center gap-8" role="navigation" aria-label="Main navigation">
              {navigationItems.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`px-4 py-2 text-sm font-medium transition-all duration-300 ${
                      transparent
                        ? isActive
                          ? 'text-white border-b-2 border-white'
                          : 'text-white/90 hover:text-white'
                        : isActive
                          ? 'text-gray-900 border-b-2 border-gray-900'
                          : 'text-gray-600 hover:text-gray-900'
                    }`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </nav>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
              {/* Search */}
              <button
                onClick={() => setShowSearch(!showSearch)}
                className={`p-2 transition-all duration-300 focus:outline-none focus:ring-2 ${
                  transparent
                    ? 'focus:ring-white/60 focus:ring-offset-0 text-white hover:text-white'
                    : 'focus:ring-gray-500 focus:ring-offset-2 text-gray-600 hover:text-gray-900'
                }`}
                aria-label="Search destinations"
              >
                <Search className={`w-5 h-5 ${transparent ? 'text-white' : ''}`} />
              </button>

              {/* User Action */}
              <button
                onClick={() => setShowPersonalizeModal(true)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 rounded ${
                  transparent
                    ? 'text-white border border-white/40 hover:bg-white/10 focus:ring-white/60 focus:ring-offset-0'
                    : 'text-gray-900 border border-gray-300 hover:bg-gray-50 focus:ring-gray-500 focus:ring-offset-2'
                }`}
                suppressHydrationWarning
              >
                <User className={`w-4 h-4 ${transparent ? 'text-white' : ''}`} />
                <span className="hidden sm:inline">
                  {userName ? `Hi ${userName}` : 'Get Started'}
                </span>
              </button>

              {/* Mobile Menu */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className={`lg:hidden p-2 transition-all duration-300 focus:outline-none focus:ring-2 ${
                  transparent
                    ? 'focus:ring-white/60 focus:ring-offset-0 text-white hover:text-white'
                    : 'focus:ring-gray-500 focus:ring-offset-2 text-gray-600 hover:text-gray-900'
                }`}
                aria-label="Toggle mobile menu"
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? <X className={`w-6 h-6 ${transparent ? 'text-white' : ''}`} /> : <Menu className={`w-6 h-6 ${transparent ? 'text-white' : ''}`} />}
              </button>
            </div>
          </div>
        </div>

        {/* Search Overlay */}
        {showSearch && (
          <div className="absolute top-full left-0 right-0 border-b transition-all duration-300 bg-white shadow-lg border-gray-200">
            <div className="max-w-7xl mx-auto px-6 lg:px-8 py-6">
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Where would you like to go?"
                    className="w-full pl-12 pr-16 py-3 text-base rounded transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-gray-500 bg-white border border-gray-300 text-gray-900 placeholder-gray-500"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const query = e.currentTarget.value.trim()
                        if (query) {
                          window.location.href = `/explore?q=${encodeURIComponent(query)}`
                          setShowSearch(false)
                        }
                      }
                    }}
                  />
                  <button
                    onClick={(e) => {
                      const input = e.currentTarget.previousElementSibling as HTMLInputElement
                      const query = input?.value.trim()
                      if (query) {
                        window.location.href = `/explore?q=${encodeURIComponent(query)}`
                        setShowSearch(false)
                      }
                    }}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                  >
                    Go
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className={`lg:hidden absolute top-full left-0 right-0 border-b transition-all duration-300 ${
            transparent ? 'bg-white/95 backdrop-blur-sm border-white/20' : 'bg-white shadow-lg border-gray-200'
          }`}>
            <div className="max-w-7xl mx-auto px-6 py-4">
              <nav className="space-y-2" role="navigation" aria-label="Mobile navigation">
                {navigationItems.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`block px-4 py-3 text-base font-medium transition-all duration-300 ${
                        isActive
                          ? 'text-gray-900 border-l-4 border-gray-900 bg-gray-50'
                          : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                      }`}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      {item.label}
                    </Link>
                  )
                })}
              </nav>
            </div>
          </div>
        )}
      </header>

      {/* Skip to content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-accent-cool text-white px-4 py-2 rounded-lg z-50 focus:ring-2 focus:ring-accent-cool focus:ring-offset-2"
      >
        Skip to content
      </a>

      <PersonalizeModal 
        open={showPersonalizeModal} 
        onOpenChange={handlePersonalizeClose}
      />
    </>
  )
}
