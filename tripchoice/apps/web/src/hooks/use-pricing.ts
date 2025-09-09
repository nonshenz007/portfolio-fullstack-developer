'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { getPrice, isPricingAvailable } from '@/lib/pricing'
import { getPriceRules, getActiveFlashSales } from '@/lib/cms'
import { Package, Variant, PriceBreakdown } from '@/types'

interface PricingOptions {
  package: Package
  variant?: Variant
  date: Date
  pax: number
  originCity?: string
}

export function usePricing(options: PricingOptions) {
  const { package: pkg, variant, date, pax, originCity = 'Mumbai' } = options

  // Fetch price rules and flash sales
  const priceRulesQuery = useQuery({
    queryKey: ['price-rules', pkg.id],
    queryFn: () => getPriceRules(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  })

  const flashSalesQuery = useQuery({
    queryKey: ['flash-sales'],
    queryFn: () => getActiveFlashSales(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Calculate price when all data is available
  const priceBreakdown = React.useMemo(() => {
    if (!isPricingAvailable(pkg, variant?.type || 'flight', date, pax, originCity)) {
      return null
    }

    // Calculate base price using the getPrice function
    const priceResult = getPrice(
      pkg,
      variant?.type || 'flight',
      date,
      pax,
      originCity
    )

    if (!priceResult) return null

    // Apply flash sale discount if available
    const currentFlashSale = flashSalesQuery.data?.[0] || null
    let breakdown = priceResult.breakdown

    if (currentFlashSale && currentFlashSale.packages?.includes(pkg.id)) {
      const additionalDiscount = breakdown.total * (currentFlashSale.discount_percent / 100)
      breakdown = {
        ...breakdown,
        discounts: breakdown.discounts + additionalDiscount,
        total: breakdown.total - additionalDiscount
      }
    }

    return breakdown
  }, [pkg, variant, date, pax, originCity, flashSalesQuery.data])

  return {
    priceBreakdown,
    flashSale: flashSalesQuery.data?.[0] || null,
    isLoading: priceRulesQuery.isLoading || flashSalesQuery.isLoading,
    error: priceRulesQuery.error || flashSalesQuery.error,
    refetch: () => {
      priceRulesQuery.refetch()
      flashSalesQuery.refetch()
    },
  }
}

export function usePriceBreakdown(options: PricingOptions) {
  const { priceBreakdown, isLoading, error, flashSale } = usePricing(options)

  const totalPerPerson = priceBreakdown?.total || 0
  const totalForGroup = totalPerPerson * options.pax

  const hasDiscount = (priceBreakdown?.discounts || 0) > 0

  return {
    breakdown: priceBreakdown,
    totalPerPerson,
    totalForGroup,
    hasDiscount,
    flashSale,
    isLoading,
    error,
  }
}
