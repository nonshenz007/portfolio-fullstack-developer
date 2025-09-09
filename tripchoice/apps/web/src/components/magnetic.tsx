'use client'

import React, { useEffect, useRef } from 'react'

interface MagneticProps extends React.HTMLAttributes<HTMLDivElement> {
  strength?: number // max px offset
  disabled?: boolean
}

export function Magnetic({ children, strength = 4, disabled, className, ...rest }: MagneticProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const reduce = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (disabled || reduce) return

    let raf = 0

    const onMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2
      const dx = Math.max(-strength, Math.min(strength, (e.clientX - cx) / 24))
      const dy = Math.max(-strength, Math.min(strength, (e.clientY - cy) / 24))
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        el.style.transform = `translate(${dx}px, ${dy}px)`
      })
    }

    const onLeave = () => {
      cancelAnimationFrame(raf)
      el.style.transform = 'translate(0px, 0px)'
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)

    return () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
      cancelAnimationFrame(raf)
    }
  }, [strength, disabled])

  return (
    <div ref={ref} className={className} {...rest}>
      {children}
    </div>
  )
}

