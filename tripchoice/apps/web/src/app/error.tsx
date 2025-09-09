'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface text-ink">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
        <p className="text-slate mb-8">An error occurred while loading the page.</p>
        <button
          onClick={() => reset()}
          className="px-6 py-3 bg-accent-warm text-white rounded-lg hover:bg-accent-warm/90 transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
