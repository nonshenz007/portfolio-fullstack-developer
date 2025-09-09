"use client"

export function SearchSection() {
  return (
    <section className="relative z-10 bg-surface border-t border-b border-cloud/10 shadow-lg">
      <div className="container mx-auto px-4 py-8 md:py-10">
        <div className="max-w-4xl mx-auto">
          <div className="relative mb-6">
            <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-slate" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search destinations, activities, or experiences..."
              onKeyDown={(e) => {
                const t = e.currentTarget as HTMLInputElement
                if (e.key === 'Enter' && t.value.trim()) window.location.href = `/explore?q=${encodeURIComponent(t.value.trim())}`
              }}
              className="w-full pl-14 pr-36 h-14 md:h-14 text-base md:text-lg rounded-full border border-cloud/20 bg-surface text-ink placeholder:text-slate/70 shadow-e1 focus:shadow-e2 focus:border-accent-cool/40 outline-none"
            />
            <button
              onClick={(e) => {
                const input = (e.currentTarget.previousElementSibling as HTMLInputElement)
                if (input && input.value.trim()) window.location.href = `/explore?q=${encodeURIComponent(input.value.trim())}`
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 h-11 px-8 md:px-10 bg-ink hover:bg-ink/90 text-surface font-semibold rounded-xl transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-accent-cool focus:ring-offset-2 focus:ring-offset-surface"
            >
              Search
            </button>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {['Weekend', 'Under ₹15k', 'Visa-free', 'Honeymoon', 'Mountains'].map((chip) => (
              <button
                key={chip}
                onClick={() => (window.location.href = `/explore?q=${encodeURIComponent(chip)}`)}
                className="px-5 py-3 rounded-full bg-gradient-to-r from-cloud/30 to-cloud/10 text-ink border border-cloud/20 hover:border-accent-cool/40 hover:bg-accent-cool/5 transition-all duration-200 text-sm font-medium hover:scale-105 shadow-sm focus:outline-none focus:ring-2 focus:ring-accent-cool focus:ring-offset-2 focus:ring-offset-surface"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
