'use client'

import { useState } from 'react'
import { Bus, Train, Plane, Car } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Variant } from '@/types'
import { formatCurrency } from '@/lib/utils'
import { analytics } from '@/lib/analytics'

interface VariantTabsProps {
  variants: Variant[]
  basePrice: number
  onVariantChange?: (variant: Variant | null) => void
  selectedVariant?: Variant | null
}

const VARIANT_ICONS = {
  bus: Bus,
  train: Train,
  flight: Plane,
  cab: Car,
}

export function VariantTabs({
  variants,
  basePrice,
  onVariantChange,
  selectedVariant
}: VariantTabsProps) {
  const [activeTab, setActiveTab] = useState<string>('')

  // Group variants by type
  const variantsByType = variants.reduce((acc, variant) => {
    if (!acc[variant.type]) {
      acc[variant.type] = []
    }
    acc[variant.type].push(variant)
    return acc
  }, {} as Record<string, Variant[]>)

  const handleTabChange = (type: string) => {
    setActiveTab(type)

    // Find the first variant of this type or null if no variants
    const variant = variantsByType[type]?.[0] || null

    if (onVariantChange) {
      onVariantChange(variant)
    }

    // Track analytics
    if (variant) {
      analytics.trackVariantSelected('package-slug', variant.type, variant.id)
    }
  }

  const calculateVariantPrice = (variant: Variant) => {
    return basePrice + variant.adj_pp
  }

  return (
    <div className="w-full">
      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <TabsList className="grid w-full grid-cols-4 mb-4">
          {Object.keys(variantsByType).map((type) => {
            const Icon = VARIANT_ICONS[type as keyof typeof VARIANT_ICONS]
            return (
              <TabsTrigger
                key={type}
                value={type}
                className="flex items-center space-x-2 data-[state=active]:bg-accent-cool data-[state=active]:text-surface"
              >
                {Icon && <Icon className="h-4 w-4" />}
                <span className="capitalize">{type}</span>
              </TabsTrigger>
            )
          })}
        </TabsList>

        {Object.entries(variantsByType).map(([type, typeVariants]) => (
          <TabsContent key={type} value={type} className="mt-0">
            <div className="space-y-3">
              {typeVariants.map((variant) => {
                const variantPrice = calculateVariantPrice(variant)
                const isSelected = selectedVariant?.id === variant.id

                return (
                  <div
                    key={variant.id}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                      isSelected
                        ? 'border-accent-cool bg-accent-cool/5'
                        : 'border-cloud hover:border-accent-cool/50 hover:bg-accent-cool/5'
                    }`}
                    onClick={() => {
                      if (onVariantChange) {
                        onVariantChange(variant)
                      }
                      analytics.trackVariantSelected('package-slug', variant.type, variant.id)
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-semibold text-ink">
                            {variant.subclass}
                          </h4>
                          {variant.vendor_notes && (
                            <span className="text-xs bg-cloud px-2 py-1 rounded-full text-slate">
                              {variant.vendor_notes}
                            </span>
                          )}
                        </div>

                        <div className="text-sm text-slate">
                          <div className="flex items-center space-x-4">
                            <span>Base price: {formatCurrency(basePrice)}</span>
                            <span className="text-accent-warm font-medium">
                              +{formatCurrency(variant.adj_pp)} ({variant.adj_pp > 0 ? 'premium' : 'discount'})
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-lg font-bold text-ink">
                          {formatCurrency(variantPrice)}
                        </div>
                        <div className="text-sm text-slate">per person</div>
                      </div>
                    </div>

                    {isSelected && (
                      <div className="mt-3 pt-3 border-t border-cloud">
                        <div className="flex items-center text-accent-cool text-sm font-medium">
                          <div className="w-2 h-2 bg-accent-cool rounded-full mr-2"></div>
                          Selected option
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </TabsContent>
        ))}
      </Tabs>

      {activeTab === '' && (
        <div className="text-center py-8 text-slate">
          <p>Select a travel option above to see pricing details</p>
        </div>
      )}
    </div>
  )
}
