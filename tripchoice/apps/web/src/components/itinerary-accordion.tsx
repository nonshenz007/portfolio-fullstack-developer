'use client'

import { useState } from 'react'
import { ChevronDown, MapPin, Clock } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getItineraryDays } from '@/lib/cms'
import { cn } from '@/lib/utils'

interface ItineraryAccordionProps {
  packageId: string
}

export function ItineraryAccordion({ packageId }: ItineraryAccordionProps) {
  const [openDays, setOpenDays] = useState<Set<number>>(new Set([1])) // First day open by default

  const { data: itinerary = [], isLoading } = useQuery({
    queryKey: ['itinerary', packageId],
    queryFn: () => getItineraryDays(packageId),
    enabled: !!packageId,
  })

  const toggleDay = (dayNumber: number) => {
    const newOpenDays = new Set(openDays)
    if (newOpenDays.has(dayNumber)) {
      newOpenDays.delete(dayNumber)
    } else {
      newOpenDays.add(dayNumber)
    }
    setOpenDays(newOpenDays)
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-h3 font-semibold text-ink">Itinerary</h3>
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="border border-cloud/20 rounded-xl p-4">
              <div className="h-6 bg-cloud/20 rounded animate-pulse mb-2" />
              <div className="h-4 bg-cloud/20 rounded animate-pulse w-3/4" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (itinerary.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-h3 font-semibold text-ink">Itinerary</h3>
        <div className="text-center py-8 text-slate">
          <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>Detailed itinerary coming soon</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-h3 font-semibold text-ink">Day-by-Day Itinerary</h3>
      
      <div className="space-y-3">
        {itinerary.map((day) => {
          const isOpen = openDays.has(day.day_number)
          
          return (
            <div
              key={day.id}
              className="border border-cloud/20 rounded-xl overflow-hidden transition-all duration-200 hover:border-cloud/40"
            >
              {/* Day Header */}
              <button
                onClick={() => toggleDay(day.day_number)}
                className="w-full p-4 text-left flex items-center justify-between hover:bg-cloud/5 transition-colors duration-200"
              >
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 bg-accent-cool text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {day.day_number}
                  </div>
                  <div>
                    <h4 className="font-semibold text-ink">{day.title}</h4>
                    <p className="text-sm text-slate">
                      {day.bullets.length} activities planned
                    </p>
                  </div>
                </div>
                
                <ChevronDown
                  className={cn(
                    "h-5 w-5 text-slate transition-transform duration-200",
                    isOpen && "rotate-180"
                  )}
                />
              </button>

              {/* Day Content */}
              {isOpen && (
                <div className="px-4 pb-4">
                  <div className="pl-12 space-y-3">
                    {day.bullets.map((bullet, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-accent-warm rounded-full mt-2 flex-shrink-0" />
                        <p className="text-slate leading-relaxed">{bullet}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Expand All / Collapse All */}
      <div className="flex justify-center pt-4">
        <button
          onClick={() => {
            if (openDays.size === itinerary.length) {
              setOpenDays(new Set())
            } else {
              setOpenDays(new Set(itinerary.map(day => day.day_number)))
            }
          }}
          className="text-sm text-accent-cool hover:underline"
        >
          {openDays.size === itinerary.length ? 'Collapse all' : 'Expand all'}
        </button>
      </div>
    </div>
  )
}