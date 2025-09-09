"use client"

import { useEffect, useMemo, useRef, useState, useCallback } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import Image from 'next/image'

type IntroOverlayProps = {
  force?: boolean
}

// Small helper hook to check if intro has been seen
export function useIntroSeen(): boolean {
  const [seen, setSeen] = useState<boolean>(false)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const v = localStorage.getItem('tc_intro_seen')
        setSeen(v === 'true')
      } catch {
        setSeen(false)
      }
    }
  }, [])
  return seen
}

export default function IntroOverlay({ force = false }: IntroOverlayProps) {
  const reduceMotion = useReducedMotion()
  const [show, setShow] = useState(false)
  const [revealing, setRevealing] = useState(false)
  const [name, setName] = useState<string | null>(null)
  const [imgError, setImgError] = useState(false)
  const [srcIndex, setSrcIndex] = useState(0)
  const allowSkipRef = useRef(true)

  // Determine if we should display the intro
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      const forceQuery = params.get('intro') === '1'
      const hash = window.location.hash || ''
      const forceHash = hash.includes('intro=1') || hash.includes('#intro')
      const envForce = process.env.NEXT_PUBLIC_ALWAYS_INTRO === '1'
      // Tauri hint: allow forcing via env as well
      const tauriForce = process.env.NEXT_PUBLIC_TAURI_FORCE_INTRO === '1'
      const seen = localStorage.getItem('tc_intro_seen') === 'true'
      if (forceQuery || forceHash || envForce || tauriForce || force || !seen) setShow(true)

      // Pull name if available
      try {
        const profile = localStorage.getItem('tc_profile')
        if (profile) {
          const parsed = JSON.parse(profile)
          if (parsed && typeof parsed.name === 'string' && parsed.name.trim()) {
            setName(parsed.name.trim())
          }
        }
      } catch {}
    }
  }, [force])

  // While overlay is shown, blur + scale the underlying hero and set clip-path base
  useEffect(() => {
    const shell = document.getElementById('page-shell')
    if (!shell) return
    if (show && !revealing) {
      shell.classList.add('intro-active')
      shell.style.setProperty('--intro-scale', '0.96')
      shell.style.setProperty('--intro-trx', '0px')
      shell.style.setProperty('--intro-try', '0px')
      shell.style.setProperty('--intro-clip', reduceMotion ? '140%' : '0%')
    }
    return () => {
      // Clean up if unmounted early
      shell.classList.remove('intro-active')
      shell.classList.remove('intro-revealing')
      shell.style.removeProperty('--intro-scale')
      shell.style.removeProperty('--intro-trx')
      shell.style.removeProperty('--intro-try')
      shell.style.removeProperty('--intro-clip')
    }
  }, [show, revealing, reduceMotion])

  // Remove tilt/parallax per spec

  const finish = useCallback(() => {
    // Prevent double-activation
    if (!allowSkipRef.current) return
    allowSkipRef.current = false

    try { if (typeof window !== 'undefined') localStorage.setItem('tc_intro_seen', 'true') } catch {}

    const shell = document.getElementById('page-shell')
    if (shell) {
      if (!reduceMotion) {
        // Trigger clipPath expansion + unblur/scale
        shell.classList.add('intro-revealing')
        shell.style.setProperty('--intro-clip', '140%')
        shell.style.setProperty('--intro-scale', '1')
        shell.style.setProperty('--intro-trx', '0px')
        shell.style.setProperty('--intro-try', '0px')
      } else {
        shell.classList.remove('intro-active')
      }
    }

    setRevealing(true)
    const doneDelay = reduceMotion ? 250 : 520
    window.setTimeout(() => setShow(false), doneDelay)
  }, [reduceMotion])

  // Keyboard shortcuts (Enter/Click to continue)
  useEffect(() => {
    if (!show) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        e.preventDefault()
        finish()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [show, finish])

  const overline = useMemo(() => (name ? `Hi ${name},` : null), [name])

  if (!show) return null

  // Timings per spec
  const t = {
    backdropIn: 0.3, // 0–300ms
    markDrawDelay: 0.15, // 150ms start
    markDrawDur: 0.65, // until ~800ms
    wordDelay: 0.8, // 800–1200
    wordDur: 0.4,
    sheenDelay: 1.2, // 1200–1600
    sheenDur: 0.4,
    taglineDelay: 1.4, // 1400–1800
    taglineDur: 0.4,
    ctaDelay: 1.8, // 1800–2000
    ctaDur: 0.2,
  }

  return (
    <AnimatePresence>
      <motion.div
        className="intro-root"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: reduceMotion ? 0.2 : t.backdropIn, ease: [0.2, 0.8, 0.2, 1] }}
      >
        {/* Backdrop ink with faint cool conic gradient */}
        <div aria-hidden className="intro-backdrop" />

        {/* Grain texture */}
        <div aria-hidden className="intro-grain" />

        {/* Content */}
        <div className={`intro-content${revealing ? ' intro-compress' : ''}`} role="dialog" aria-modal="true" aria-label="Welcome">
          {overline && (
            <motion.div
              className="intro-overline"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.32, ease: [0.2, 0.8, 0.2, 1] }}
            >
              {overline}
            </motion.div>
          )}

          {/* Logo image with graceful fallback and pulse rings */}
          <div className="intro-mark-wrap" aria-live="polite">
            <div className="intro-logo-frame">
              {/* Subtle halo behind the logo */}
              <div className="intro-halo" aria-hidden />
              {/* Pulse rings */}
              <div className={`ring outer ${reduceMotion ? '' : 'ringPulse'}`} aria-hidden />
              <div className={`ring inner ${reduceMotion ? '' : 'ringPulse'}`} aria-hidden />
              {/* Fixed box for CLS with elegant backplate */}
              <div className="intro-logo-card">
                {!imgError ? (
                  <Image
                    src={"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 80'><rect width='100%' height='100%' rx='12' fill='%23071C3C'/><text x='50%' y='58%' font-family='Inter, Arial, sans-serif' font-size='42' font-weight='700' fill='black' opacity='0' text-anchor='middle'>.</text><text x='50%' y='58%' font-family='Inter, Arial, sans-serif' font-size='42' font-weight='700' fill='white' text-anchor='middle'>TripChoice</text></svg>"}
                    alt="TripChoice"
                    fill
                    sizes="128px"
                    priority
                    className="intro-logo-image"
                    onError={() => setImgError(true)}
                  />
                ) : (
                  <h1 className="font-display text-3xl tracking-tight text-ink">tripchoice</h1>
                )}
              </div>
            </div>
          </div>

          {/* Wordmark */}
          {/* Keep subtle fade for brand name if image failed (handled above). No separate wordmark animation. */}

          {/* Tagline typing */}
          <motion.div
            className="intro-tagline"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.24 }}
          >
            <span>Trips made personal.</span>
          </motion.div>

          {/* CTA */}
          <motion.button
            className="intro-cta"
            role="button"
            aria-label="Continue"
            onClick={finish}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.2, ease: [0.2, 0.8, 0.2, 1] }}
          >
            Continue
            <span className="intro-cta-hint" aria-live="polite">Press Enter</span>
          </motion.button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
