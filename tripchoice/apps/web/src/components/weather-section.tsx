'use client'

import { WeatherWidget } from '@/components/weather-widget'

export function WeatherSection() {
  return (
    <section className="py-16 bg-gradient-to-r from-slate-50 to-white relative">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl lg:text-4xl font-bold text-ink mb-4">
            Check Live Weather
          </h2>
          <p className="text-lg text-slate max-w-2xl mx-auto">
            Plan your perfect trip with real-time weather updates
          </p>
        </div>
        <div className="grid md:grid-cols-4 gap-6">
          <WeatherWidget destination="Kashmir" />
          <WeatherWidget destination="Goa" />
          <WeatherWidget destination="Kerala" />
          <WeatherWidget destination="Rajasthan" />
        </div>
      </div>
    </section>
  )
}