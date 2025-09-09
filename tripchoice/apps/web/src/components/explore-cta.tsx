'use client'

import { Users, Phone } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function ExploreCTA() {
  return (
    <section className="py-16 bg-blue-50">
      <div className="container mx-auto px-4 text-center">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold text-gray-900">
              Ready to Start Your Adventure?
            </h2>
            <p className="text-lg text-gray-600">
              Join thousands of happy travelers who've discovered their dream destinations with TripChoice
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold">
              <Users className="w-5 h-5 mr-2" />
              Plan My Trip
            </Button>
            <Button variant="outline" className="px-8 py-3 font-semibold border-2">
              <Phone className="w-5 h-5 mr-2" />
              Get Expert Help
            </Button>
          </div>

          <div className="grid md:grid-cols-3 gap-8 pt-8 text-sm text-gray-600">
            <div>✓ 24/7 Support</div>
            <div>✓ Best Price Guarantee</div>
            <div>✓ Flexible Booking</div>
          </div>
        </div>
      </div>
    </section>
  )
}