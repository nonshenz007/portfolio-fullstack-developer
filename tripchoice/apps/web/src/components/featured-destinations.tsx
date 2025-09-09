'use client'

import { useState } from 'react'
import { MapPin, Star, Clock, IndianRupee, Users, Heart } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { WeatherWidget } from '@/components/weather-widget'

interface Destination {
  id: string
  name: string
  image: string
  rating: number
  reviews: number
  price: number
  duration: string
  description: string
  tags: string[]
  featured: boolean
}

export function FeaturedDestinations() {
  const [likedDestinations, setLikedDestinations] = useState<string[]>([])

  const featuredDestinations: Destination[] = [
    {
      id: 'kashmir',
      name: 'Kashmir Valley',
      image: 'https://source.unsplash.com/1200x800/?kashmir%20mountains',
      rating: 4.9,
      reviews: 2847,
      price: 25999,
      duration: '6 Days 5 Nights',
      description: 'Experience the paradise on earth with houseboats, gardens, and snow-capped mountains.',
      tags: ['Adventure', 'Nature', 'Culture'],
      featured: true
    },
    {
      id: 'goa',
      name: 'Goa Beaches',
      image: 'https://source.unsplash.com/1200x800/?goa%20beach%20sunset',
      rating: 4.7,
      reviews: 3456,
      price: 18999,
      duration: '5 Days 4 Nights',
      description: 'Sun, sand, and sea await you in this coastal paradise with vibrant nightlife.',
      tags: ['Beach', 'Party', 'Relaxation'],
      featured: true
    },
    {
      id: 'kerala',
      name: 'Kerala Backwaters',
      image: 'https://source.unsplash.com/1200x800/?kerala%20backwaters%20houseboat',
      rating: 4.8,
      reviews: 2198,
      price: 22999,
      duration: '7 Days 6 Nights',
      description: 'Cruise through serene backwaters and experience authentic Kerala culture.',
      tags: ['Backwaters', 'Culture', 'Relaxation'],
      featured: true
    },
    {
      id: 'rajasthan',
      name: 'Rajasthan Heritage',
      image: 'https://source.unsplash.com/1200x800/?rajasthan%20palace%20heritage',
      rating: 4.6,
      reviews: 1876,
      price: 31999,
      duration: '8 Days 7 Nights',
      description: 'Explore royal palaces, deserts, and rich cultural heritage of Rajasthan.',
      tags: ['Heritage', 'Culture', 'Desert'],
      featured: true
    }
  ]

  const toggleLike = (destinationId: string) => {
    setLikedDestinations(prev =>
      prev.includes(destinationId)
        ? prev.filter(id => id !== destinationId)
        : [...prev, destinationId]
    )
  }

  return (
    <div className="space-y-12">
      {/* Section Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 bg-accent-cool/10 text-accent-cool px-4 py-2 rounded-full text-sm font-medium">
          <MapPin className="w-4 h-4" />
          Featured Destinations
        </div>
        <h2 className="text-4xl lg:text-5xl font-bold text-ink">
          Most Popular Adventures
        </h2>
        <p className="text-xl text-slate max-w-2xl mx-auto">
          Discover handpicked destinations loved by thousands of travelers worldwide
        </p>
      </div>

      {/* Featured Destinations Grid */}
      <div className="grid lg:grid-cols-2 gap-8">
        {featuredDestinations.map((destination) => (
          <div key={destination.id} className="group relative">
            {/* Main Card */}
            <div className="bg-white rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden border border-slate-200">
              {/* Image Section */}
              <div className="relative h-64 overflow-hidden">
                <img
                  src={destination.image}
                  alt={destination.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>

                {/* Overlay Content */}
                <div className="absolute top-4 left-4 flex gap-2">
                  <Badge className="bg-accent-cool text-white">
                    Featured
                  </Badge>
                  {destination.featured && (
                    <Badge variant="secondary" className="bg-white/20 text-white backdrop-blur-sm">
                      🔥 Hot Deal
                    </Badge>
                  )}
                </div>

                {/* Like Button */}
                <button
                  onClick={() => toggleLike(destination.id)}
                  className="absolute top-4 right-4 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"
                >
                  <Heart
                    className={`w-5 h-5 ${
                      likedDestinations.includes(destination.id)
                        ? 'text-red-500 fill-red-500'
                        : 'text-white'
                    }`}
                  />
                </button>

                {/* Price Tag */}
                <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-xl px-4 py-2">
                  <div className="text-sm text-slate-600">Starting from</div>
                  <div className="text-xl font-bold text-ink">₹{destination.price.toLocaleString()}</div>
                </div>
              </div>

              {/* Content Section */}
              <div className="p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="text-2xl font-bold text-ink">{destination.name}</h3>
                    <div className="flex items-center gap-4 text-sm text-slate-600">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        <span className="font-medium">{destination.rating}</span>
                        <span>({destination.reviews.toLocaleString()} reviews)</span>
                      </div>
                    </div>
                  </div>
                </div>

                <p className="text-slate-600 leading-relaxed">{destination.description}</p>

                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                  {destination.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary" className="bg-slate-100 text-slate-700">
                      {tag}
                    </Badge>
                  ))}
                </div>

                {/* Duration & CTA */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                  <div className="flex items-center gap-2 text-sm text-slate-600">
                    <Clock className="w-4 h-4" />
                    {destination.duration}
                  </div>
                  <Button className="bg-accent-cool hover:bg-accent-cool/90 text-white px-6 py-2 rounded-xl font-semibold">
                    Explore Now
                  </Button>
                </div>
              </div>
            </div>

            {/* Weather Widget Overlay */}
            <div className="absolute -top-4 -right-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <WeatherWidget destination={destination.name} compact />
            </div>
          </div>
        ))}
      </div>


    </div>
  )
}
