'use client'

import { useState, useEffect } from 'react'
import { Clock, Sparkles } from 'lucide-react'
import { FlashSale } from '@/types'
import { getCountdownTime } from '@/lib/utils'

interface FlashRibbonProps {
  flashSale: FlashSale | null
  className?: string
}

export function FlashRibbon({ flashSale, className }: FlashRibbonProps) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })
  const [isVisible, setIsVisible] = useState(true)
  const [hasScrolled, setHasScrolled] = useState(false)

  useEffect(() => {
    if (!flashSale) return

    const updateCountdown = () => {
      const countdown = getCountdownTime(new Date(flashSale.end_at))
      setTimeLeft(countdown)

      if (countdown.days === 0 && countdown.hours === 0 &&
          countdown.minutes === 0 && countdown.seconds === 0) {
        setIsVisible(false)
      }
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [flashSale])

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY
      if (scrollY > 100 && !hasScrolled) {
        setHasScrolled(true)
      } else if (scrollY <= 100 && hasScrolled) {
        setHasScrolled(false)
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [hasScrolled])

  if (!flashSale || !isVisible) return null

  const handleClick = () => {
    const dealsSection = document.getElementById('deals-section')
    if (dealsSection) {
      dealsSection.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <div
      className={`fixed top-16 left-0 right-0 z-40 bg-accent-warm text-white transition-all duration-300 ease-out cursor-pointer hover:shadow-e2 ${
        hasScrolled ? 'opacity-0 pointer-events-none' : 'opacity-100'
      } ${className || ''}`}
      onClick={handleClick}
    >
      <div className="px-6 py-2 backdrop-blur-sm">
        <div className="container mx-auto flex items-center justify-center gap-4 text-sm font-medium">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            <span className="font-bold">{flashSale.discount_percent}% off {flashSale.name}</span>
          </div>
          
          <div className="flex items-center gap-2">
            <span>ends in</span>
            <div className="font-mono font-bold">
              {timeLeft.days.toString().padStart(2, '0')}:
              {timeLeft.hours.toString().padStart(2, '0')}:
              {timeLeft.minutes.toString().padStart(2, '0')}:
              {timeLeft.seconds.toString().padStart(2, '0')}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}