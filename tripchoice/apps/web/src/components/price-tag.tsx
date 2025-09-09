'use client'

import { useState } from 'react'
import { ChevronDown, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { PriceBreakdown } from '@/types'
import { formatCurrency } from '@/lib/utils'
import { cn } from '@/lib/utils'

interface PriceTagProps {
  breakdown: PriceBreakdown
  pax?: number
  showBreakdown?: boolean
  className?: string
}

export function PriceTag({
  breakdown,
  pax = 1,
  showBreakdown = true,
  className
}: PriceTagProps) {
  const [showDetails, setShowDetails] = useState(false)

  const totalPerPerson = breakdown.total
  const totalForGroup = totalPerPerson * pax

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Main Price Display */}
          <div className="text-center">
            <div className="text-3xl font-bold text-ink mb-1">
              {totalPerPerson > 0 ? (
                <>From {formatCurrency(totalPerPerson)}</>
              ) : (
                'Contact us'
              )}
            </div>
            {totalPerPerson > 0 && (
              <div className="text-slate text-sm">
                per person {pax > 1 && `(₹${totalForGroup.toLocaleString('en-IN')} for ${pax} people)`}
              </div>
            )}
          </div>

          {/* Price Breakdown Toggle */}
          {showBreakdown && (
            <div className="text-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="text-accent-cool hover:text-accent-cool/80"
              >
                <Info className="h-4 w-4 mr-2" />
                Price breakdown
                <ChevronDown
                  className={cn(
                    "h-4 w-4 ml-2 transition-transform",
                    showDetails && "rotate-180"
                  )}
                />
              </Button>
            </div>
          )}

          {/* Detailed Breakdown */}
          {showDetails && (
            <div className="space-y-3 pt-4 border-t border-cloud">
              <div className="space-y-2">
                {/* Base Price */}
                <div className="flex justify-between items-center">
                  <span className="text-slate text-sm">Base price</span>
                  <span className="text-ink font-medium">
                    {formatCurrency(breakdown.basePrice)}
                  </span>
                </div>

                {/* Season Multiplier */}
                {breakdown.seasonMultiplier !== 1 && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate text-sm">
                      Season ({breakdown.seasonMultiplier > 1 ? 'Peak' : 'Low'})
                    </span>
                    <span className={cn(
                      "text-sm font-medium",
                      breakdown.seasonMultiplier > 1 ? "text-red-600" : "text-green-600"
                    )}>
                      {breakdown.seasonMultiplier > 1 ? '+' : ''}
                      {((breakdown.seasonMultiplier - 1) * 100).toFixed(0)}%
                    </span>
                  </div>
                )}

                {/* Weekend Multiplier */}
                {breakdown.weekendMultiplier !== 1 && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate text-sm">Weekend</span>
                    <span className="text-red-600 text-sm font-medium">
                      +{((breakdown.weekendMultiplier - 1) * 100).toFixed(0)}%
                    </span>
                  </div>
                )}

                {/* Origin Multiplier */}
                {breakdown.originMultiplier !== 1 && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate text-sm">Origin adjustment</span>
                    <span className={cn(
                      "text-sm font-medium",
                      breakdown.originMultiplier > 1 ? "text-red-600" : "text-green-600"
                    )}>
                      {breakdown.originMultiplier > 1 ? '+' : ''}
                      {((breakdown.originMultiplier - 1) * 100).toFixed(0)}%
                    </span>
                  </div>
                )}

                {/* Variant Delta */}
                {breakdown.variantDelta !== 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate text-sm">Travel option</span>
                    <span className={cn(
                      "text-sm font-medium",
                      breakdown.variantDelta > 0 ? "text-red-600" : "text-green-600"
                    )}>
                      {breakdown.variantDelta > 0 ? '+' : ''}
                      {formatCurrency(breakdown.variantDelta)}
                    </span>
                  </div>
                )}

                {/* Rooming Delta */}
                {breakdown.roomingDelta !== 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate text-sm">Rooming</span>
                    <span className={cn(
                      "text-sm font-medium",
                      breakdown.roomingDelta > 0 ? "text-red-600" : "text-green-600"
                    )}>
                      {breakdown.roomingDelta > 0 ? '+' : ''}
                      {formatCurrency(breakdown.roomingDelta)}
                    </span>
                  </div>
                )}

                {/* Discounts */}
                {breakdown.discounts > 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-slate text-sm">Discounts</span>
                    <span className="text-green-600 text-sm font-medium">
                      -{formatCurrency(breakdown.discounts)}
                    </span>
                  </div>
                )}
              </div>

              {/* Total Separator */}
              <div className="border-t border-cloud pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-ink font-semibold">Total per person</span>
                  <span className="text-ink font-bold text-lg">
                    {formatCurrency(totalPerPerson)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Flash Sale Indicator */}
          {breakdown.discounts > 0 && (
            <div className="bg-accent-warm/10 border border-accent-warm/20 rounded-lg p-3">
              <div className="flex items-center justify-center text-accent-warm text-sm font-medium">
                🎉 Flash sale discount applied!
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
