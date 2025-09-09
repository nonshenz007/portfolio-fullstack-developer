'use client'

import { useState } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

interface SafeImageProps {
  src: string
  alt: string
  ratio: '4:3' | '16:9' | '16:10'
  priority?: boolean
  className?: string
  sizes?: string
}

export function SafeImage({ 
  src, 
  alt, 
  ratio, 
  priority = false, 
  className,
  sizes = "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px"
}: SafeImageProps) {
  const [imageError, setImageError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const aspectMap: Record<SafeImageProps['ratio'], string> = {
    '4:3': 'aspect-[4/3]',
    '16:9': 'aspect-[16/9]',
    '16:10': 'aspect-[16/10]'
  }
  const aspectRatio = aspectMap[ratio]

  // Get destination initials from alt text
  const getDestinationInitials = (altText: string) => {
    const words = altText.split(' ').filter(word => word.length > 2)
    return words.slice(0, 2).map(word => word.charAt(0).toUpperCase()).join('')
  }

  // Generate beautiful gradients based on destination
  const getGradientFromAlt = (altText: string) => {
    const lowerAlt = altText.toLowerCase()
    if (lowerAlt.includes('kashmir') || lowerAlt.includes('mountain') || lowerAlt.includes('snow')) {
      return 'from-blue-600 via-indigo-600 to-purple-700'
    }
    if (lowerAlt.includes('goa') || lowerAlt.includes('beach') || lowerAlt.includes('ocean')) {
      return 'from-cyan-500 via-blue-500 to-indigo-600'
    }
    if (lowerAlt.includes('kerala') || lowerAlt.includes('backwater') || lowerAlt.includes('nature')) {
      return 'from-emerald-500 via-green-500 to-teal-600'
    }
    if (lowerAlt.includes('rajasthan') || lowerAlt.includes('desert') || lowerAlt.includes('palace')) {
      return 'from-orange-500 via-amber-500 to-yellow-600'
    }
    if (lowerAlt.includes('dubai') || lowerAlt.includes('luxury') || lowerAlt.includes('city')) {
      return 'from-purple-500 via-pink-500 to-rose-600'
    }
    if (lowerAlt.includes('thailand') || lowerAlt.includes('temple') || lowerAlt.includes('asia')) {
      return 'from-yellow-500 via-orange-500 to-red-600'
    }
    return 'from-slate-500 via-gray-500 to-zinc-600'
  }

  if (imageError || !src || src === 'TBD') {
    return (
      <div className={cn(
        aspectRatio,
        `bg-gradient-to-br ${getGradientFromAlt(alt)} flex items-center justify-center relative overflow-hidden group cursor-pointer`,
        className
      )}>
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse transform -skew-x-12"></div>
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/10 to-transparent animate-pulse transform skew-y-12" style={{ animationDelay: '1s' }}></div>
        </div>

        {/* Floating particles effect */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-white/30 rounded-full animate-bounce" style={{ animationDelay: '0s', animationDuration: '3s' }}></div>
          <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-white/30 rounded-full animate-bounce" style={{ animationDelay: '1s', animationDuration: '3s' }}></div>
          <div className="absolute bottom-1/3 left-1/3 w-1 h-1 bg-white/30 rounded-full animate-bounce" style={{ animationDelay: '2s', animationDuration: '3s' }}></div>
        </div>

        <div className="text-center text-white relative z-10 transform group-hover:scale-105 transition-transform duration-300">
          <div className="text-3xl md:text-5xl font-bold mb-3 animate-pulse">
            {getDestinationInitials(alt)}
          </div>
          <div className="text-sm md:text-lg font-medium opacity-90 mb-2">
            {alt.split(' ').slice(0, 3).join(' ')}
          </div>
          <div className="text-xs md:text-sm opacity-75">
            Experience the magic • Coming soon
          </div>

          {/* Hover effect border */}
          <div className="absolute inset-0 border-2 border-white/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(aspectRatio, "relative overflow-hidden group cursor-pointer", className)}>
      {/* Enhanced Loading placeholder */}
      {isLoading && (
        <div className="absolute inset-0 bg-gradient-to-br from-slate-100 via-slate-200 to-slate-300 flex items-center justify-center">
          <div className="flex flex-col items-center space-y-3">
            {/* Spinning loader */}
            <div className="relative">
              <div className="w-12 h-12 border-3 border-slate-300 border-t-accent-cool rounded-full animate-spin"></div>
              <div className="absolute inset-2 border-2 border-transparent border-t-slate-400 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '0.8s' }}></div>
            </div>
            <div className="text-xs text-slate-500 font-medium">Loading beauty...</div>
          </div>
        </div>
      )}

      <Image
        src={src}
        alt={alt}
        fill
        className={cn(
          "object-cover transition-all duration-500 transform group-hover:scale-105",
          isLoading ? "opacity-0 scale-95" : "opacity-100 scale-100"
        )}
        sizes={sizes}
        priority={priority}
        // Force direct loading to avoid optimizer/network issues with remote sources
        unoptimized={src.startsWith('http')}
        referrerPolicy="no-referrer"
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setImageError(true)
          setIsLoading(false)
        }}
      />

      {/* Hover overlay with subtle effects */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

      {/* Subtle shine effect on hover */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-pulse transform -skew-x-12 transition-opacity duration-300"></div>
    </div>
  )
}
