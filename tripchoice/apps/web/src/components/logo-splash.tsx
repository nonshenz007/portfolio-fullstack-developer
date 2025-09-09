'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'

interface LogoSplashProps {
  // How long to show the splash (ms) when auto-closing
  durationMs?: number
  // If true, keep splash until user clicks Continue
  requireClick?: boolean
}

// Lightweight splash that shows the brand logo briefly on first load
// Uses sessionStorage so it appears once per tab session
export function LogoSplash({ durationMs = 2200, requireClick = true }: LogoSplashProps) {
  const [visible, setVisible] = useState(false)
  const [closing, setClosing] = useState(false)
  const candidates = [
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 80'><rect width='100%' height='100%' rx='12' fill='%23071C3C'/><text x='50%' y='58%' font-family='Inter, Arial, sans-serif' font-size='42' font-weight='700' fill='white' text-anchor='middle'>TripChoice</text></svg>"
  ]
  const [srcIndex, setSrcIndex] = useState(0)

  useEffect(() => {
    const reduceMotion =
      typeof window !== 'undefined' &&
      window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches

    // Allow forcing the splash via ?intro=1 for debug/demo
    const params = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '')
    const forceIntro = params.get('intro') === '1'

    // Only show once per session unless forced
    const shownKey = 'tc_splash_shown'
    const alreadyShown = typeof window !== 'undefined' && sessionStorage.getItem(shownKey)

    if (forceIntro || !alreadyShown) {
      setVisible(true)

      // Auto-close only when not requiring a click
      if (!requireClick) {
        const t = setTimeout(() => handleClose(), reduceMotion ? 300 : durationMs)
        return () => clearTimeout(t)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [durationMs, requireClick])

  const handleClose = () => {
    const shownKey = 'tc_splash_shown'
    sessionStorage.setItem(shownKey, '1')
    // Begin cinematic close
    setClosing(true)
    try {
      // Notify any listeners (welcome overlay, etc.) while we animate out
      window.dispatchEvent(new CustomEvent('tc:splash-done'))
    } catch {}
    const reduceMotion =
      typeof window !== 'undefined' &&
      window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const closeDelay = reduceMotion ? 120 : 900
    setTimeout(() => setVisible(false), closeDelay)
  }

  // Keyboard: allow Enter/Space to continue
  useEffect(() => {
    if (!visible || !requireClick) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleClose()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [visible, requireClick])

  if (!visible) return null

  return (
    <div className={`fixed inset-0 z-[70] flex items-center justify-center bg-[#071C3C] transition-opacity duration-700 ${closing ? 'opacity-0' : 'opacity-100'}`}>
      {/* Subtle moving color wash for a premium feel */}
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(1200px 1200px at 50% 40%, rgba(13, 71, 174, 0.20), transparent 60%), radial-gradient(900px 900px at 75% 80%, rgba(237, 107, 8, 0.12), transparent 60%)',
          filter: 'saturate(1.1) contrast(1.02)'
        }}
      />
      {/* Film grain */}
      <div
        className="pointer-events-none absolute inset-0 mix-blend-overlay"
        style={{
          backgroundImage:
            "radial-gradient(1px 1px at 10% 20%, rgba(7,28,60,.06) 1px, transparent 1px),radial-gradient(1px 1px at 30% 60%, rgba(6,71,174,.06) 1px, transparent 1px),radial-gradient(1px 1px at 70% 80%, rgba(74,83,101,.06) 1px, transparent 1px)",
          backgroundSize: '64px 64px',
          opacity: 0.06,
        }}
      />

      <div className="text-center select-none relative z-10">
        {/* Try to use provided logo; fallback to brand wordmark */}
        <div className={`relative mx-auto w-[220px] h-[220px] md:w-[280px] md:h-[280px] transition-transform duration-700 ${closing ? 'scale-90 opacity-0' : 'scale-100 opacity-100'}`}>
          <Image
            src={candidates[Math.min(srcIndex, candidates.length - 1)]}
            alt="TripChoice logo"
            fill
            priority
            className="object-contain animate-scale-in p-6 md:p-8 drop-shadow-[0_8px_30px_rgba(0,0,0,0.25)]"
            sizes="(max-width: 768px) 220px, 280px"
            onError={() => {
              // Try next candidate, fallback to wordmark if all fail
              setSrcIndex((i) => Math.min(i + 1, candidates.length))
            }}
          />
          {/* Fallback mark (only if all image candidates fail) */}
          {srcIndex >= candidates.length && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="font-display text-4xl md:text-5xl tracking-tight text-white drop-shadow">
                trip<span className="text-[#F06421]">choice</span>
              </span>
            </div>
          )}
          {/* Ripple ring on exit for cinematic touch */}
          <div
            aria-hidden
            className={`absolute inset-0 flex items-center justify-center transition-transform duration-\[900ms\] ${closing ? 'scale-[12]' : 'scale-0'}`}
          >
            <div className="w-24 h-24 rounded-full border-2 border-white/30" />
          </div>
        </div>
        <div className="mt-4 text-white/80 text-sm animate-fade-in">We design your dreams</div>

        {requireClick && (
          <div className={`mt-8 transition-all duration-500 ${closing ? 'opacity-0 translate-y-1' : 'opacity-100'} animate-fade-in`} style={{ animationDelay: '400ms' }}>
            <button
              onClick={handleClose}
              className="bg-[#F06421] hover:bg-[#f47a3f] text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 hover:scale-[1.03] focus:outline-none focus:ring-2 focus:ring-white/70 focus:ring-offset-2 focus:ring-offset-[#071C3C]"
            >
              Continue
            </button>
            <div className="mt-3 text-white/60 text-xs">Press Enter to continue</div>
          </div>
        )}
      </div>

      {/* Cinematic top/bottom wave curtains on close */}
      <svg
        aria-hidden
        className={`pointer-events-none absolute left-0 top-0 w-full h-1/3 transition-transform duration-\[950ms\] ease-\[cubic-bezier\(.19\,1\,.\22\,1\)\] ${closing ? '-translate-y-full' : 'translate-y-0'}`}
        viewBox="0 0 100 50"
        preserveAspectRatio="none"
      >
        <path d="M0 0 H100 V35 Q50 45 0 35 Z" fill="#071C3C" />
      </svg>
      <svg
        aria-hidden
        className={`pointer-events-none absolute left-0 bottom-0 w-full h-1/3 transition-transform duration-\[950ms\] ease-\[cubic-bezier\(.19\,1\,.\22\,1\)\] ${closing ? 'translate-y-full' : 'translate-y-0'}`}
        viewBox="0 0 100 50"
        preserveAspectRatio="none"
      >
        <path d="M0 50 H100 V15 Q50 5 0 15 Z" fill="#071C3C" />
      </svg>
    </div>
  )
}
