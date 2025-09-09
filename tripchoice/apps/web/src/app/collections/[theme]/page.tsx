import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getPackages } from '@/lib/cms'
import { Package } from '@/types'
import { ExploreContent } from '@/components/explore-content'

interface CollectionsPageProps {
  params: {
    theme: string
  }
}

const THEME_CONFIGS = {
  weekend: {
    title: 'Weekend Getaways',
    description: 'Perfect short trips for your weekend adventures',
    filter: { themes: ['Weekend'], duration_days: { _lte: 3 } }
  },
  honeymoon: {
    title: 'Honeymoon Destinations',
    description: 'Romantic getaways for your special moments',
    filter: { themes: ['Honeymoon'] }
  },
  adventure: {
    title: 'Adventure Trips',
    description: 'Thrilling experiences for the adventurous soul',
    filter: { themes: ['Adventure'] }
  },
  cultural: {
    title: 'Cultural Journeys',
    description: 'Immerse yourself in rich cultural experiences',
    filter: { themes: ['Cultural'] }
  },
  beach: {
    title: 'Beach Holidays',
    description: 'Relaxing beach destinations for ultimate unwind',
    filter: { themes: ['Beach'] }
  },
  mountains: {
    title: 'Mountain Escapes',
    description: 'Breathtaking mountain destinations and treks',
    filter: { themes: ['Mountains'] }
  }
}

export async function generateMetadata({ params }: CollectionsPageProps): Promise<Metadata> {
  const theme = params.theme as keyof typeof THEME_CONFIGS
  const config = THEME_CONFIGS[theme]

  if (!config) {
    return {
      title: 'Collection Not Found - TripChoice'
    }
  }

  return {
    title: `${config.title} - TripChoice`,
    description: config.description,
    keywords: `${params.theme} travel, ${params.theme} destinations, ${params.theme} packages`,
    openGraph: {
      title: config.title,
      description: config.description,
      url: `https://tripchoice.com/collections/${params.theme}`,
      type: 'website',
    }
  }
}

export default async function CollectionsPage({ params }: CollectionsPageProps) {
  const theme = params.theme as keyof typeof THEME_CONFIGS
  const config = THEME_CONFIGS[theme]

  if (!config) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-surface">
      {/* Collection Header */}
      <div className="bg-gradient-to-br from-cool via-cool/80 to-ink text-surface py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl lg:text-7xl font-bold mb-6 leading-tight">
            {config.title}
          </h1>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            {config.description}
          </p>
        </div>
      </div>

      {/* Collection Content */}
      <div className="py-8">
        <ExploreContent />
      </div>
    </div>
  )
}

