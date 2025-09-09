'use client'

import { useState, useEffect } from 'react'
import { Plane, Train, Bus, Car, Star, Wifi, Utensils, Bed, Shield, Crown, Clock, Users, MapPin, CheckCircle, AlertTriangle, Leaf, Award, Calendar, CreditCard, ShieldCheck, TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getVariants } from '@/lib/cms'
import { analytics } from '@/lib/analytics'
import { cn } from '@/lib/utils'

interface VariantSelectorProps {
  packageId: string
  onVariantChange?: (variant: any) => void
}

const VARIANT_ICONS = {
  flight: Plane,
  train: Train,
  bus: Bus,
  cab: Car
}

const AMENITY_ICONS = {
  'Personal cabin': Crown,
  'Premium dining': Utensils,
  'Lounge access': Star,
  'WiFi': Wifi,
  'Entertainment': Star,
  'Reclining seats': Bed,
  'Premium meals': Utensils,
  'Reading lights': Star,
  'Storage': Star,
  'AC compartment': Shield,
  'Meals included': Utensils,
  'Blankets': Bed,
  'Basic meals': Utensils,
  'Berth seats': Bed,
  'Power outlets': Star,
  'USB charging': Star,
  'Foot rest': Star,
  'Window seat': Star,
  'Privacy curtain': Star,
  'Personal attendant': Star,
  'Newspaper': Star,
  'Emergency kit': Shield,
  'Safety briefing': ShieldCheck
}

const TIER_COLORS = {
  'Executive': 'from-purple-600 to-pink-600',
  'First Class': 'from-amber-500 to-orange-600',
  'AC 2-Tier': 'from-blue-600 to-indigo-600',
  'AC 3-Tier': 'from-emerald-600 to-teal-600',
  'Sleeper': 'from-slate-600 to-gray-600'
}

const TIER_BADGES = {
  'Executive': { icon: Crown, text: 'Luxury', bg: 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800' },
  'First Class': { icon: Award, text: 'Premium', bg: 'bg-gradient-to-r from-amber-100 to-orange-100 text-amber-800' },
  'AC 2-Tier': { icon: Shield, text: 'Standard', bg: 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800' },
  'AC 3-Tier': { icon: CheckCircle, text: 'Economy', bg: 'bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-800' },
  'Sleeper': { icon: Bed, text: 'Budget', bg: 'bg-gradient-to-r from-slate-100 to-gray-100 text-slate-800' }
}

export function VariantSelector({ packageId, onVariantChange }: VariantSelectorProps) {
  const [selectedVariant, setSelectedVariant] = useState<any>(null)
  const [hoveredVariant, setHoveredVariant] = useState<any>(null)
  const [expandedVariant, setExpandedVariant] = useState<string | null>(null)

  const { data: variants = [], isLoading } = useQuery({
    queryKey: ['variants', packageId],
    queryFn: () => getVariants(packageId),
    enabled: !!packageId,
  })

  // Group variants by type
  const groupedVariants = variants.reduce((acc, variant) => {
    const type = variant.type
    if (!acc[type]) acc[type] = []
    acc[type].push(variant)
    return acc
  }, {} as Record<string, any[]>)

  // Auto-select first variant
  useEffect(() => {
    if (variants.length > 0 && !selectedVariant) {
      const defaultVariant = variants.find(v => v.type === 'train' && v.tier === 'AC 2-Tier') || variants[0]
      setSelectedVariant(defaultVariant)
      onVariantChange?.(defaultVariant)
    }
  }, [variants, selectedVariant, onVariantChange])

  const handleVariantSelect = (variant: any) => {
    setSelectedVariant(variant)
    onVariantChange?.(variant)
    analytics.trackVariantSelected(packageId, variant.type, variant.id)
  }

  const toggleExpanded = (variantId: string) => {
    setExpandedVariant(expandedVariant === variantId ? null : variantId)
  }

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="border-b border-slate-200 pb-6">
          <h3 className="text-2xl font-bold text-slate-900 mb-2">Choose Your Transport</h3>
          <p className="text-slate-600">Compare options and select the best travel experience for your journey</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="border border-slate-200 rounded-xl p-6 animate-pulse">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-slate-200 rounded-xl" />
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-slate-200 rounded w-3/4" />
                  <div className="h-3 bg-slate-200 rounded w-1/2" />
                </div>
              </div>
              <div className="space-y-3">
                <div className="h-3 bg-slate-200 rounded w-full" />
                <div className="h-3 bg-slate-200 rounded w-2/3" />
                <div className="h-3 bg-slate-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (variants.length === 0) {
    return null
  }

  return (
    <div className="space-y-8 relative">
      {/* Professional Header */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Transportation Options</h3>
        <p className="text-gray-600">Compare and select your preferred mode of transport</p>
      </div>

      {/* Transport Options */}
      {Object.entries(groupedVariants).map(([type, typeVariants]) => (
        <div key={type} className="space-y-6">
          {/* Professional Type Header */}
          <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {type === 'train' && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Train className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">Rail Travel Options</h4>
                      <p className="text-sm text-gray-600">Choose your preferred train service</p>
                    </div>
                  </div>
                )}
                {type === 'flight' && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-sky-100 rounded-lg">
                      <Plane className="h-5 w-5 text-sky-600" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">Air Travel</h4>
                      <p className="text-sm text-gray-600">Direct flights with modern aircraft</p>
                    </div>
                  </div>
                )}
                {type === 'bus' && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Bus className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">Coach Service</h4>
                      <p className="text-sm text-gray-600">Reliable bus transportation</p>
                    </div>
                  </div>
                )}
                {type === 'cab' && (
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <Car className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">Private Transfer</h4>
                      <p className="text-sm text-gray-600">Door-to-door transportation</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="text-right">
                <div className="text-lg font-bold text-gray-800">{typeVariants.length}</div>
                <div className="text-sm text-gray-500">Options</div>
              </div>
            </div>
          </div>

                    {/* Professional Variant Cards - Fixed Layout */}
          <div className={cn(
            type === 'train'
              ? "grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-2"
              : "grid gap-6 grid-cols-1 md:grid-cols-2"
          )}>
            {typeVariants.map((variant) => {
          const Icon = VARIANT_ICONS[variant.type as keyof typeof VARIANT_ICONS] || Car
          const isSelected = selectedVariant?.id === variant.id
              const isExpanded = expandedVariant === variant.id
              const tierBadge = variant.tier ? TIER_BADGES[variant.tier as keyof typeof TIER_BADGES] : null

          return (
                <div
              key={variant.id}
              className={cn(
                    "border-2 rounded-xl transition-all duration-300 overflow-hidden min-h-[320px]",
                isSelected
                      ? "border-blue-500 bg-blue-50 shadow-lg scale-105"
                      : "border-gray-200 hover:border-gray-300 hover:shadow-md bg-white"
                  )}
                >
                                    {/* Main Card Content */}
                  <div className="p-6">
                                        {/* Header Section - Compact Layout */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          "p-3 rounded-lg",
                          isSelected
                            ? "bg-blue-500 text-white"
                            : "bg-blue-100 text-blue-600"
                        )}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                          <h4 className="text-lg font-bold text-gray-900 capitalize">
                            {variant.subclass}
                          </h4>
                          <p className="text-sm text-gray-600">{variant.type} service</p>
                        </div>
                      </div>

                      {/* Tier Badge */}
                      {tierBadge && (
                        <div className={cn(
                          "px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1",
                          tierBadge.bg
                        )}>
                          <tierBadge.icon className="h-3 w-3" />
                          <span>{tierBadge.text}</span>
                        </div>
                      )}
                    </div>

                    {/* Key Information - Simplified Layout */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                      <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                        <Clock className="h-4 w-4 text-blue-500" />
                        <div>
                          <div className="text-sm font-semibold text-gray-900">{variant.journeyTime}</div>
                          <div className="text-xs text-gray-500">Duration</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                        <ShieldCheck className="h-4 w-4 text-green-500" />
                        <div>
                          <div className="text-sm font-semibold text-gray-900">{variant.safetyRating}/5</div>
                          <div className="text-xs text-gray-500">Safety</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                        <Users className="h-4 w-4 text-purple-500" />
                        <div>
                          <div className="text-sm font-semibold text-gray-900">{variant.customerRating}</div>
                          <div className="text-xs text-gray-500">Rating</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                        <Leaf className="h-4 w-4 text-emerald-500" />
                        <div>
                          <div className="text-sm font-semibold text-gray-900 capitalize">{variant.environmentalImpact}</div>
                          <div className="text-xs text-gray-500">Impact</div>
                        </div>
                      </div>
                    </div>

                    {/* Price Section - Compact Layout */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        {variant.adj_pp !== 0 ? (
                          <span className={cn(
                            "text-lg font-bold",
                            variant.adj_pp > 0 ? "text-orange-600" : "text-green-600"
                          )}>
                            {variant.adj_pp > 0 ? '+' : ''}₹{Math.abs(variant.adj_pp).toLocaleString('en-IN')}
                          </span>
                        ) : (
                          <span className="text-lg font-bold text-gray-900">Standard</span>
                        )}

                        <div className={cn(
                          "px-2 py-1 rounded-full text-xs font-medium",
                          variant.availability === 'High' ? 'bg-green-100 text-green-800' :
                          variant.availability === 'Good' ? 'bg-yellow-100 text-yellow-800' :
                          variant.availability === 'Limited' ? 'bg-orange-100 text-orange-800' :
                          'bg-blue-100 text-blue-800'
                        )}>
                          {variant.availability}
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleVariantSelect(variant)
                        }}
                        className={cn(
                          "px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-200",
                          isSelected
                            ? "bg-blue-500 text-white"
                            : "bg-blue-600 text-white hover:bg-blue-700"
                        )}
                      >
                        {isSelected ? 'Selected' : 'Select'}
                      </button>
                    </div>

                    {/* Expand/Collapse Button */}
                    <button
                      onClick={() => toggleExpanded(variant.id)}
                      className="w-full flex items-center justify-center gap-1 py-2 text-xs text-gray-600 hover:text-gray-800 transition-colors"
                    >
                      <span>{isExpanded ? 'Hide Details' : 'More Details'}</span>
                      <svg
                        className={cn(
                          "h-3 w-3 transition-transform duration-200",
                          isExpanded ? "rotate-180" : ""
                        )}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 bg-gray-50 p-4 space-y-3">
                      {/* Amenities */}
                      {variant.amenities && (
                        <div>
                          <h5 className="font-semibold text-slate-900 mb-3">Included Amenities</h5>
                          <div className="grid grid-cols-2 gap-2">
                            {variant.amenities.map((amenity: string) => {
                              const AmenityIcon = AMENITY_ICONS[amenity as keyof typeof AMENITY_ICONS] || Star
                              return (
                                <div key={amenity} className="flex items-center gap-2 text-sm text-slate-700">
                                  <AmenityIcon className="h-4 w-4 text-slate-400" />
                                  <span>{amenity}</span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}

                      {/* Additional Services */}
                      {variant.baggageAllowance && (
                        <div className="flex items-center gap-2 text-sm text-slate-700">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span><strong>Baggage:</strong> {variant.baggageAllowance}</span>
                        </div>
                      )}

                      {variant.onboardServices && (
                        <div className="flex items-center gap-2 text-sm text-slate-700">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span><strong>Services:</strong> {variant.onboardServices}</span>
                        </div>
                      )}

                      {/* Cancellation Policy */}
                      <div>
                        <h5 className="font-semibold text-slate-900 mb-2">Cancellation Policy</h5>
                        <p className="text-sm text-slate-600">{variant.cancellationPolicy}</p>
                      </div>

                      {/* Vendor Notes */}
                      <div>
                        <h5 className="font-semibold text-slate-900 mb-2">Service Details</h5>
                        <p className="text-sm text-slate-600">{variant.vendor_notes}</p>
                      </div>
                  </div>
                  )}
                </div>
              )
            })}
                </div>
              </div>
      ))}

                  {/* Professional Summary Section */}
      {selectedVariant && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CheckCircle className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-gray-900 mb-3">Selected Transportation</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Transport:</span>
                  <span className="ml-2 font-medium text-gray-900">{selectedVariant.subclass}</span>
                </div>
                <div>
                  <span className="text-gray-500">Duration:</span>
                  <span className="ml-2 font-medium text-gray-900">{selectedVariant.journeyTime}</span>
                </div>
                <div>
                  <span className="text-gray-500">Price Adjustment:</span>
                  <span className={cn(
                    "ml-2 font-medium",
                    selectedVariant.adj_pp > 0 ? "text-orange-600" : selectedVariant.adj_pp < 0 ? "text-green-600" : "text-gray-900"
                  )}>
                    {selectedVariant.adj_pp > 0 ? '+' : selectedVariant.adj_pp < 0 ? '-' : ''}₹{Math.abs(selectedVariant.adj_pp).toLocaleString('en-IN')}
                  </span>
                </div>
              </div>
            </div>
      </div>
        </div>
      )}
    </div>
  )
}