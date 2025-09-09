'use client'

export function ExploreSearchSection() {
  return (
    <div className="max-w-2xl mx-auto mb-16">
      <div className="relative">
        <input
          type="text"
          placeholder="Search destinations, themes, or experiences..."
          className="w-full px-6 py-4 text-lg rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-lg"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              const query = e.currentTarget.value.trim()
              if (query) {
                window.location.href = `/explore?q=${encodeURIComponent(query)}`
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
            }
          }}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </div>

      {/* Quick filter chips */}
      <div className="flex flex-wrap justify-center gap-3 mt-6">
        {[
          { label: 'Weekend Trips', query: 'weekend' },
          { label: 'Under ₹20k', query: 'budget' },
          { label: 'Beach Destinations', query: 'beach' },
          { label: 'Mountain Escapes', query: 'mountains' },
          { label: 'Cultural Tours', query: 'culture' }
        ].map((chip) => (
          <button
            key={chip.label}
            onClick={() => window.location.href = `/explore?q=${encodeURIComponent(chip.query)}`}
            className="px-4 py-2 bg-white border border-gray-200 rounded-full hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm"
          >
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  )
}