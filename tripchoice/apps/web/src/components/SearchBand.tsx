'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'

export function SearchBand() {
  const [selectedChips, setSelectedChips] = useState<Set<string>>(new Set())
  const chips = ['Weekend', 'Under ₹15k', 'Visa-free', 'Honeymoon', 'Mountains']

  const toggleChip = (chip: string) => {
    const newSelected = new Set(selectedChips)
    if (newSelected.has(chip)) {
      newSelected.delete(chip)
    } else {
      newSelected.add(chip)
    }
    setSelectedChips(newSelected)
  }

  return (
    <section className="bg-white border-b shadow-sm -mt-8 relative z-10">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="relative mb-6">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Where do you want to go?"
              onKeyDown={(e) => {
                const t = e.currentTarget as HTMLInputElement
                if (e.key === 'Enter' && t.value.trim()) window.location.href = `/explore?query=${encodeURIComponent(t.value.trim())}`
              }}
              className="w-full pl-12 pr-32 h-14 text-base rounded-full border border-gray-300 bg-white text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 outline-none"
            />
            <button
              onClick={(e) => {
                const input = (e.currentTarget.previousElementSibling as HTMLInputElement)
                if (input && input.value.trim()) window.location.href = `/explore?query=${encodeURIComponent(input.value.trim())}`
              }}
              className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-full transition-colors"
            >
              Search
            </button>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {chips.map((chip) => {
              const isSelected = selectedChips.has(chip)
              return (
                <button
                  key={chip}
                  onClick={() => toggleChip(chip)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:border-blue-500'
                  }`}
                >
                  {chip}
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

