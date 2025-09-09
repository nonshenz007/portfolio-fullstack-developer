"use client"

import { ReactNode } from 'react'
import { useIntersectionObserver } from '@/lib/performance'

interface LazyWrapperProps {
  children: ReactNode
  fallback?: ReactNode
  className?: string
}

export function LazyWrapper({
  children,
  fallback = null,
  className = ''
}: LazyWrapperProps) {
  const [ref, isIntersecting] = useIntersectionObserver()

  return (
    <div ref={ref as any} className={className}>
      {isIntersecting ? children : fallback}
    </div>
  )
}
