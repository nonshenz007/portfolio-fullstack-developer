'use client'

import { useState, useEffect } from 'react'
import { Calendar, Users, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Magnetic } from '@/components/magnetic'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { getPrice } from '@/lib/pricing'
import { Package } from '@/types'
import { cn } from '@/lib/utils'

interface PriceBoxProps {
  pkg: Package
  selectedVariant?: any
}

export function PriceBox({ pkg, selectedVariant }: PriceBoxProps) {
  const [date, setDate] = useState(() => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().split('T')[0]
  })
  const [pax, setPax] = useState(2)
  const [originCity, setOriginCity] = useState('Mumbai')
  const [showBreakdown, setShowBreakdown] = useState(false)

  // Get user's city from localStorage if available
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const profile = localStorage.getItem('tc_profile')
      if (profile) {
        try {
          const { city } = JSON.parse(profile)
          if (city) setOriginCity(city)
        } catch (e) {
          // Ignore parsing errors
        }
      }
    }
  }, [])

  const priceResult = getPrice(pkg, selectedVariant?.type || 'flight', new Date(date), pax, originCity)
  const hasValidPrice = priceResult && priceResult.pp > 0

  return (
    <div className="bg-surface border border-cloud/20 rounded-xl p-6 shadow-e2 sticky top-24">
      {/* Price Display */}
      <div className="text-center mb-6">
        {hasValidPrice ? (
          <>
            <div className="text-3xl font-bold text-ink mb-1">
              ₹{priceResult.pp.toLocaleString('en-IN')}
            </div>
            <div className="text-sm text-slate">per person</div>
            {priceResult.breakdown.discounts > 0 && (
              <div className="text-sm text-green-600 font-medium">
                Save ₹{priceResult.breakdown.discounts.toLocaleString('en-IN')}
              </div>
            )}
          </>
        ) : (
          <>
            <div className="text-2xl font-bold text-ink mb-1">
              Contact us
            </div>
            <div className="text-sm text-slate">for pricing</div>
          </>
        )}
        
        {hasValidPrice && (
          <button
            onClick={() => setShowBreakdown(!showBreakdown)}
            className="text-xs text-accent-cool hover:underline mt-2 flex items-center gap-1 mx-auto"
          >
            <Info className="h-3 w-3" />
            Price breakdown
          </button>
        )}
      </div>

      {/* Price Breakdown */}
      {showBreakdown && hasValidPrice && (
        <div className="bg-cloud/10 rounded-lg p-4 mb-6 text-sm">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate">Base price</span>
              <span className="text-ink">₹{priceResult.breakdown.basePrice.toLocaleString('en-IN')}</span>
            </div>
            {priceResult.breakdown.seasonMultiplier !== 1 && (
              <div className="flex justify-between">
                <span className="text-slate">Season adjustment</span>
                <span className="text-ink">×{priceResult.breakdown.seasonMultiplier}</span>
              </div>
            )}
            {priceResult.breakdown.weekendMultiplier !== 1 && (
              <div className="flex justify-between">
                <span className="text-slate">Weekend premium</span>
                <span className="text-ink">×{priceResult.breakdown.weekendMultiplier}</span>
              </div>
            )}
            {priceResult.breakdown.variantDelta !== 0 && (
              <div className="flex justify-between">
                <span className="text-slate">Transport adjustment</span>
                <span className="text-ink">
                  {priceResult.breakdown.variantDelta > 0 ? '+' : ''}₹{priceResult.breakdown.variantDelta.toLocaleString('en-IN')}
                </span>
              </div>
            )}
            {priceResult.breakdown.discounts > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discounts</span>
                <span>-₹{priceResult.breakdown.discounts.toLocaleString('en-IN')}</span>
              </div>
            )}
            <hr className="border-cloud/30" />
            <div className="flex justify-between font-semibold">
              <span className="text-ink">Total per person</span>
              <span className="text-ink">₹{priceResult.pp.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
      )}

      {/* Form Controls */}
      <div className="space-y-4 mb-6">
        {/* Date Picker */}
        <div className="space-y-2">
          <Label htmlFor="date" className="text-sm font-medium text-ink flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Travel Date
          </Label>
          <Input
            id="date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            className="border-cloud/30 focus:border-accent-cool"
          />
        </div>

        {/* Pax Selector */}
        <div className="space-y-2">
          <Label htmlFor="pax" className="text-sm font-medium text-ink flex items-center gap-2">
            <Users className="h-4 w-4" />
            Travelers
          </Label>
          <Select value={pax.toString()} onValueChange={(value) => setPax(Number(value))}>
            <SelectTrigger className="border-cloud/30 focus:border-accent-cool">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Array.from({ length: pkg.max_pax - pkg.min_pax + 1 }, (_, i) => {
                const count = pkg.min_pax + i
                return (
                  <SelectItem key={count} value={count.toString()}>
                    {count} {count === 1 ? 'person' : 'people'}
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </div>

        {/* Origin City */}
        <div className="space-y-2">
          <Label htmlFor="origin" className="text-sm font-medium text-ink">
            From City
          </Label>
          <Select value={originCity} onValueChange={setOriginCity}>
            <SelectTrigger className="border-cloud/30 focus:border-accent-cool">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad'].map((city) => (
                <SelectItem key={city} value={city}>
                  {city}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Total Price for Group */}
      {hasValidPrice && pax > 1 && (
        <div className="bg-accent-warm/10 rounded-lg p-3 mb-6">
          <div className="text-center">
            <div className="text-sm text-slate">Total for {pax} people</div>
            <div className="text-xl font-bold text-accent-warm">
              ₹{(priceResult.pp * pax).toLocaleString('en-IN')}
            </div>
          </div>
        </div>
      )}

      {/* CTA Button */}
      <Magnetic>
        <Button
          className="w-full bg-accent-warm hover:bg-accent-warm/90 text-white font-semibold py-4 text-lg shadow-e2 hover:shadow-e3 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-accent-cool"
          onClick={() => {
            // This will be handled by WhatsAppCTA component
            const event = new CustomEvent('whatsapp-enquiry', {
              detail: { pkg, selectedVariant, date, pax, originCity }
            })
            window.dispatchEvent(event)
          }}
        >
          Enquire on WhatsApp
        </Button>
      </Magnetic>

      <p className="text-xs text-slate text-center mt-3">
        Instant response • Best price guaranteed
      </p>
    </div>
  )
}
