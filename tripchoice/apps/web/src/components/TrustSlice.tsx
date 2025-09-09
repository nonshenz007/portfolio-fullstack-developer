'use client'

import { Star } from 'lucide-react'

export function TrustSlice() {
  return (
    <section className="py-16 bg-white border-t border-gray-100">
      <div className="container mx-auto px-6">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-center">
          {/* Rating */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              <span className="text-2xl font-light text-gray-900">4.9</span>
              <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            </div>
            <span className="text-gray-600 font-light">Trusted by 50k+ travelers</span>
          </div>

          {/* Features */}
          <div className="flex items-center gap-6 text-gray-600 font-light">
            <span>Transparent pricing</span>
            <span>•</span>
            <span>Human support</span>
            <span>•</span>
            <span>Easy cancellation</span>
          </div>
        </div>
      </div>
    </section>
  )
}
