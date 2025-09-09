'use client'

export function HomepageSearch() {
  return (
    <div className="max-w-lg mx-auto mb-8">
      <div className="relative">
        <input
          type="text"
          placeholder="Where do you want to go?"
          className="w-full px-6 py-4 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50"
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
          className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </div>
    </div>
  )
}