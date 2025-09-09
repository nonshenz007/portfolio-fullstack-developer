"use client"

import { useEffect } from 'react'
import { usePerformanceMonitor, preloadCriticalResources } from '@/lib/performance'

export function PerformanceMonitor() {
  usePerformanceMonitor()

  useEffect(() => {
    // Preload critical resources on mount
    preloadCriticalResources()

    // Monitor Core Web Vitals
    if (typeof window !== 'undefined' && 'web-vitals' in window) {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS(console.log)
        getFID(console.log)
        getFCP(console.log)
        getLCP(console.log)
        getTTFB(console.log)
      })
    }
  }, [])

  return null // This component doesn't render anything
}
