'use client'

import { useState } from 'react'
import Image from 'next/image'
import { TrendingUp, MapPin, Star, ArrowRight, Flame, Clock, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface TrendingDestination {
  id: string
  name: string
  location: string
  image: string
  rating: number
  reviews: number
  price: number
  duration: string
  trending: boolean
  popular: boolean
  description: string
  highlights: string[]
}

export function TrendingDestinations() {

  const destinations = [
    {
      id: 'jammu-kashmir-4n4d',
      name: 'Kashmir Valley',
      location: 'Kashmir, India',
      image: '/images/kashmir/kashmir-dal-lake-hd.jpg',
      rating: 4.9,
      reviews: 2847,
      price: 25999,
      duration: '6 Days 5 Nights',
      description: 'Experience the paradise on earth with houseboats, gardens, and snow-capped mountains.',
    },
    {
      id: 'goa-beach-3n',
      name: 'Goa Beaches',
      location: 'Goa, India',
      image: '/images/goa/goa-beach-main.jpg',
      rating: 4.7,
      reviews: 3456,
      price: 18999,
      duration: '5 Days 4 Nights',
      description: 'Sun, sand, and sea await you in this coastal paradise with vibrant nightlife.',
    },
    {
      id: 'dubai-city-lights-4d',
      name: 'Dubai Luxury',
      location: 'Dubai, UAE',
      image: '/images/dubai/dubai-skyline-hd.jpg',
      rating: 4.8,
      reviews: 1250,
      price: 89999,
      duration: '6 Days 5 Nights',
      description: 'Experience ultimate luxury in the city of gold with world-class attractions.',
    },
    {
      id: 'thailand-bangkok-5n',
      name: 'Thailand Paradise',
      location: 'Bangkok & Phuket',
      image: '/images/thailand/thailand-islands-hd.jpg',
      rating: 4.6,
      reviews: 2100,
      price: 45999,
      duration: '7 Days 6 Nights',
      description: 'From bustling Bangkok streets to pristine Phuket beaches.',
    },
    {
      id: 'singapore-city-4n',
      name: 'Singapore Wonders',
      location: 'Singapore',
      image: '/images/singapore/singapore-skyline-hd.jpg',
      rating: 4.7,
      reviews: 1800,
      price: 55999,
      duration: '5 Days 4 Nights',
      description: 'A perfect blend of culture, cuisine, and cutting-edge attractions.',
    },
    {
      id: 'kerala-backwaters-5n',
      name: 'Kerala Backwaters',
      location: 'Kerala, India',
      image: '/images/kerala/kerala-backwaters-hd.jpg',
      rating: 4.8,
      reviews: 2198,
      price: 22999,
      duration: '7 Days 6 Nights',
      description: 'Cruise through serene backwaters and experience authentic culture.',
    }
  ]

  return (
    <div className="space-y-16 relative">
      {/* Creative Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-blue-400/10 to-purple-400/10 rounded-full blur-3xl animate-pulse delay-100"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-r from-orange-400/8 to-red-400/8 rounded-full blur-3xl animate-pulse delay-500"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gradient-to-r from-green-400/6 to-teal-400/6 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Section Header with Creative Design */}
      <div className="text-center space-y-8 relative z-10">
        <div className="relative">
          <div className="inline-flex items-center gap-3 bg-gradient-to-r from-amber-100 via-orange-100 to-red-100 text-orange-800 px-8 py-4 rounded-full text-lg font-bold shadow-lg border border-orange-200/50">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce delay-0"></div>
              <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce delay-100"></div>
              <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce delay-200"></div>
            </div>
            🔥 TRENDING NOW
          </div>
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-pink-500 to-rose-500 rounded-full animate-ping"></div>
        </div>

        <div className="space-y-4">
          <h2 className="text-5xl md:text-7xl font-black bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 bg-clip-text text-transparent leading-tight">
            HOT
            <span className="block bg-gradient-to-r from-orange-600 via-red-600 to-pink-600 bg-clip-text text-transparent">
              DESTINATIONS
            </span>
          </h2>
          <div className="flex items-center justify-center gap-4 text-slate-600">
            <div className="h-px bg-gradient-to-r from-transparent to-slate-300 w-16"></div>
            <span className="text-sm font-medium tracking-wider">✨ MOST POPULAR THIS SEASON</span>
            <div className="h-px bg-gradient-to-l from-transparent to-slate-300 w-16"></div>
          </div>
        </div>
      </div>

      {/* Creative Mosaic Grid Layout */}
      <div className="relative z-10">
        {/* Featured Large Card */}
        <div className="grid lg:grid-cols-5 gap-6 mb-12">
          <div className="lg:col-span-3">
            <div
              onClick={() => window.location.href = `/package/${destinations[0].id}`}
              className="group relative bg-white rounded-3xl shadow-2xl hover:shadow-3xl transition-all duration-700 transform hover:-translate-y-3 hover:rotate-1 overflow-hidden border border-slate-200/50 cursor-pointer"
            >
              <div className="relative h-80 overflow-hidden">
                <img
                  src={destinations[0].image}
                  alt={destinations[0].name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>

                {/* Floating Elements */}
                <div className="absolute top-6 left-6">
                  <div className="bg-white/90 backdrop-blur-sm rounded-2xl px-4 py-2 shadow-xl">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm font-bold text-slate-900">#1 TRENDING</span>
                    </div>
                  </div>
                </div>

                <div className="absolute top-6 right-6">
                  <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-2xl shadow-xl font-bold">
                    ₹{destinations[0].price.toLocaleString()}
                  </div>
                </div>

                <div className="absolute bottom-6 left-6 right-6">
                  <div className="space-y-2">
                    <h3 className="text-2xl font-bold text-white">{destinations[0].name}</h3>
                    <div className="flex items-center gap-4 text-white/90">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        <span className="text-sm">{destinations[0].location}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm font-semibold">{destinations[0].rating}</span>
                        <span className="text-xs">({destinations[0].reviews.toLocaleString()})</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Side Cards */}
          <div className="lg:col-span-2 space-y-6">
            {[destinations[1], destinations[2]].map((destination, index) => (
                          <div
              key={destination.id}
              onClick={() => window.location.href = `/package/${destination.id}`}
              className="group bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 overflow-hidden border border-slate-200/50 cursor-pointer"
            >
                <div className="relative h-36 overflow-hidden">
                  <img
                    src={destination.image}
                    alt={destination.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>

                  <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-xl px-3 py-1 shadow-lg">
                    <span className="text-sm font-bold text-slate-900">₹{destination.price.toLocaleString()}</span>
                  </div>

                  <div className="absolute bottom-3 left-3">
                    <h4 className="text-lg font-bold text-white">{destination.name}</h4>
                    <div className="flex items-center gap-1 text-white/80 text-sm">
                      <MapPin className="w-3 h-3" />
                      <span>{destination.location}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Row - Creative Layout */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {destinations.slice(3).map((destination, index) => (
            <div
              key={destination.id}
              onClick={() => window.location.href = `/package/${destination.id}`}
              className={`group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 hover:scale-105 overflow-hidden border border-slate-200/50 cursor-pointer animate-fade-in-up ${
                index % 2 === 0 ? 'hover:rotate-1' : 'hover:-rotate-1'
              }`}
              style={{ animationDelay: `${(index + 3) * 200}ms` }}
            >
              <div className="relative h-48 overflow-hidden">
                <img
                  src={destination.image}
                  alt={destination.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                {/* Creative Badge */}
                <div className={`absolute top-4 left-4 ${index % 3 === 0 ? 'bg-gradient-to-r from-blue-500 to-purple-500' : index % 3 === 1 ? 'bg-gradient-to-r from-green-500 to-teal-500' : 'bg-gradient-to-r from-pink-500 to-rose-500'} text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg`}>
                  {index % 3 === 0 ? '🌊 BEACH' : index % 3 === 1 ? '🏔️ MOUNTAIN' : '🏛️ CULTURE'}
                </div>

                <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-xl px-3 py-2 shadow-lg opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                    <span className="text-sm font-bold text-slate-900">{destination.rating}</span>
                  </div>
                </div>

                <div className="absolute bottom-4 left-4 right-4">
                  <div className="space-y-1">
                    <h4 className="text-lg font-bold text-white drop-shadow-lg">{destination.name}</h4>
                    <div className="flex items-center gap-2 text-white/90 text-sm">
                      <MapPin className="w-3 h-3" />
                      <span>{destination.location}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-slate-500">
                    <span className="font-medium text-slate-900">₹{destination.price.toLocaleString()}</span>
                  </div>
                  <Button
                    size="sm"
                    className="bg-slate-900 hover:bg-slate-800 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Creative Call to Action */}
      <div className="text-center pt-12 relative z-10">
        <div className="relative">
          <div
            onClick={() => window.location.href = '/explore'}
            className="group inline-flex items-center gap-4 px-12 py-6 bg-ink text-surface-light rounded-full shadow-e3 hover:shadow-e3 transition-all duration-250 hover:-translate-y-0.5 cursor-pointer border border-cloud/20 hover:bg-accent-cool focus:outline-none focus:ring-2 focus:ring-accent-cool/40 active:scale-95"
          >
            <div className="flex space-x-2">
              <div className="w-3 h-3 bg-white rounded-full animate-bounce delay-0"></div>
              <div className="w-3 h-3 bg-white rounded-full animate-bounce delay-100"></div>
              <div className="w-3 h-3 bg-white rounded-full animate-bounce delay-200"></div>
            </div>
            <span className="font-black text-xl tracking-wide">DISCOVER ALL HOT SPOTS</span>
            <ArrowRight className="w-6 h-6 transform group-hover:translate-x-2 transition-transform duration-300" />
          </div>

          {/* Floating decorative elements */}
          <div className="absolute -top-4 -left-4 w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-bounce delay-300 opacity-60"></div>
          <div className="absolute -bottom-4 -right-4 w-6 h-6 bg-gradient-to-r from-orange-400 to-red-400 rounded-full animate-bounce delay-500 opacity-60"></div>
        </div>
      </div>
    </div>
  )
}
