'use client'

import { Check, X } from 'lucide-react'

interface InclusionsExclusionsProps {
  inclusions: string[]
  exclusions?: string[]
}

export function InclusionsExclusions({ inclusions, exclusions = [] }: InclusionsExclusionsProps) {
  return (
    <div className="space-y-6">
      <h3 className="text-h3 font-semibold text-ink">What's Included</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Inclusions */}
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <h4 className="font-semibold text-green-800 mb-4 flex items-center gap-2">
            <Check className="h-5 w-5" />
            Included
          </h4>
          <div className="space-y-3">
            {inclusions.map((inclusion, index) => (
              <div key={index} className="flex items-start gap-3">
                <Check className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-green-700 text-sm leading-relaxed">{inclusion}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Exclusions */}
        {exclusions.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <h4 className="font-semibold text-red-800 mb-4 flex items-center gap-2">
              <X className="h-5 w-5" />
              Not Included
            </h4>
            <div className="space-y-3">
              {exclusions.map((exclusion, index) => (
                <div key={index} className="flex items-start gap-3">
                  <X className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                  <span className="text-red-700 text-sm leading-relaxed">{exclusion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Additional Info */}
      <div className="bg-cloud/10 rounded-xl p-4">
        <p className="text-sm text-slate">
          <strong>Note:</strong> All inclusions are subject to availability and may vary based on your selected travel dates and group size. 
          Please confirm specific details during booking.
        </p>
      </div>
    </div>
  )
}