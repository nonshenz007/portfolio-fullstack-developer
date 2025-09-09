'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'

interface FunctionalSearchProps {
  placeholder?: string
  className?: string
  onSearch?: (query: string) => void
}

export function FunctionalSearch({ 
  placeholder = "Search destinations...", 
  className = "",
  onSearch 
}: FunctionalSearchProps) {
  const [query, setQuery] = useState('')

  const handleSearch = () => {
    const trimmedQuery = query.trim()
    if (trimmedQuery) {
      if (onSearch) {
        onSearch(trimmedQuery)
      } else {
        // Default behavior: navigate to explore page with search query
        window.location.href = `/explore?q=${encodeURIComponent(trimmedQuery)}`
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSearch()
    }
  }

  return (
    <div className={`relative ${className}`}>
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-gray-400" />
      </div>
      <input
        type="text"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        className="w-full pl-12 pr-20 py-3 text-base rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <button
        onClick={handleSearch}
        className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-1.5 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors text-sm font-medium"
      >
        Search
      </button>
    </div>
  )
}