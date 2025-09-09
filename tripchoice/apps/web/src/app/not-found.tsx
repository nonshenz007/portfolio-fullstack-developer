import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface text-ink">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-accent-midnight mb-4">404</h1>
        <h2 className="text-2xl font-bold mb-4">Page Not Found</h2>
        <p className="text-slate mb-8">The page you're looking for doesn't exist.</p>
        <Link
          href="/"
          className="px-6 py-3 bg-ink text-surface rounded-lg hover:bg-ink/90 transition-colors font-semibold"
        >
          Go Home
        </Link>
      </div>
    </div>
  )
}
