'use client'

import { useState } from 'react'
import Image from 'next/image'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { SafeImage } from '@/components/safe-image'
import { cn } from '@/lib/utils'

interface Gallery16x9Props {
  images: string[]
  alt: string
  priority?: boolean
}

export function Gallery16x9({ images, alt, priority = false }: Gallery16x9Props) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const validImages = images.filter(img => img && img !== 'TBD')

  if (validImages.length === 0) {
    return (
      <div className="aspect-[16/9] bg-gradient-to-br from-ink to-accent-cool flex items-center justify-center">
        <div className="text-center text-white">
          <div className="text-4xl mb-2">🏝️</div>
          <p className="text-lg font-medium">Beautiful Destination</p>
        </div>
      </div>
    )
  }

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % validImages.length)
  }

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + validImages.length) % validImages.length)
  }

  return (
    <div className="relative aspect-[16/9] overflow-hidden bg-ink">
      {/* Main Image */}
      <SafeImage
        src={validImages[currentIndex]}
        alt={`${alt} - Image ${currentIndex + 1}`}
        ratio="16:9"
        priority={priority}
        className="w-full h-full object-cover"
      />

      {/* Navigation Arrows */}
      {validImages.length > 1 && (
        <>
          <button
            onClick={prevImage}
            className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-surface/90 backdrop-blur-sm rounded-full p-2 shadow-e2 hover:bg-surface transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-accent-cool"
            aria-label="Previous image"
          >
            <ChevronLeft className="h-5 w-5 text-ink" />
          </button>
          
          <button
            onClick={nextImage}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-surface/90 backdrop-blur-sm rounded-full p-2 shadow-e2 hover:bg-surface transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-accent-cool"
            aria-label="Next image"
          >
            <ChevronRight className="h-5 w-5 text-ink" />
          </button>
        </>
      )}

      {/* Dots Indicator */}
      {validImages.length > 1 && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
          {validImages.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={cn(
                "w-2 h-2 rounded-full transition-all duration-200",
                index === currentIndex
                  ? "bg-white shadow-e1"
                  : "bg-white/50 hover:bg-white/75"
              )}
              aria-label={`Go to image ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-ink/30 via-transparent to-transparent pointer-events-none" />
    </div>
  )
}