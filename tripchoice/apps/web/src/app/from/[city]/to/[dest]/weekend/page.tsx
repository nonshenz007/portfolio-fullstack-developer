import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getPackages } from '@/lib/cms'
import { Package } from '@/types'
import { ExploreContent } from '@/components/explore-content'

interface WeekendPageProps {
  params: {
    city: string
    dest: string
  }
}

export async function generateMetadata({ params }: WeekendPageProps): Promise<Metadata> {
  const originCity = decodeURIComponent(params.city)
  const destination = decodeURIComponent(params.dest)

  return {
    title: `Weekend Trip from ${originCity} to ${destination} - TripChoice`,
    description: `Plan your perfect weekend getaway from ${originCity} to ${destination}. Curated packages for short trips and quick escapes.`,
    keywords: `weekend trip ${originCity} to ${destination}, short trip ${originCity} ${destination}, weekend getaway`,
    openGraph: {
      title: `Weekend Trip: ${originCity} to ${destination}`,
      description: `Discover amazing weekend packages from ${originCity} to ${destination}`,
      url: `https://tripchoice.com/from/${params.city}/to/${params.dest}/weekend`,
      type: 'website',
    }
  }
}

export default async function WeekendPage({ params }: WeekendPageProps) {
  const originCity = decodeURIComponent(params.city)
  const destination = decodeURIComponent(params.dest)

  return (
    <div className="min-h-screen bg-surface">
      {/* Route Header */}
      <div className="bg-gradient-to-br from-warm via-warm/80 to-cool text-ink py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="bg-surface/20 backdrop-blur-sm rounded-full px-4 py-2">
              <span className="text-sm font-medium">🏠 {originCity}</span>
            </div>
            <div className="text-2xl">✈️</div>
            <div className="bg-surface/20 backdrop-blur-sm rounded-full px-4 py-2">
              <span className="text-sm font-medium">🏖️ {destination}</span>
            </div>
          </div>

          <h1 className="text-5xl lg:text-7xl font-bold mb-6 leading-tight">
            Weekend Getaway
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Perfect weekend packages from {originCity} to {destination}.
            Quick escapes for your short trips and spontaneous adventures.
          </p>
        </div>
      </div>

      {/* Route Content */}
      <div className="py-8">
        <ExploreContent />
      </div>
    </div>
  )
}

