'use client'

import { useState, useEffect } from 'react'
import { PersonalizationModal } from './personalization-modal'
import { usePersonalizationContext } from '@/contexts/PersonalizationContext'
import { Personalization } from '@/types'
import { Button } from '@/components/ui/button'
import { X, User, Target, MapPin } from 'lucide-react'

interface WelcomeOverlayNewProps {
  // Optional delay before showing the overlay (ms)
  delayMs?: number
}

export function WelcomeOverlayNew({ delayMs = 0 }: WelcomeOverlayNewProps) {
  const {
    isLoading,
    isFirstVisit,
    hasCompletedSetup,
    personalization,
    savePersonalization,
    markSetupComplete,
    mounted
  } = usePersonalizationContext()

  const [showWizard, setShowWizard] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  // Show welcome overlay for first-time visitors
  useEffect(() => {
    if (!isLoading && isFirstVisit && !hasCompletedSetup) {
      if (delayMs > 0) {
        const t = setTimeout(() => setIsVisible(true), delayMs)
        return () => clearTimeout(t)
      }
      setIsVisible(true)
    }
  }, [isLoading, isFirstVisit, hasCompletedSetup, delayMs])

  // Open personalization immediately after splash completes
  useEffect(() => {
    const onSplashDone = () => {
      if (isFirstVisit && !hasCompletedSetup) {
        setIsVisible(false)
        setShowWizard(true)
      }
    }
    window.addEventListener('tc:splash-done' as any, onSplashDone)
    return () => window.removeEventListener('tc:splash-done' as any, onSplashDone)
  }, [isFirstVisit, hasCompletedSetup])

  const handleStartPersonalization = () => {
    setShowWizard(true)
  }

  const handleSkip = () => {
    markSetupComplete()
    setIsVisible(false)
  }

  const handleWizardComplete = async (data: Personalization) => {
    try {
      await savePersonalization(data)
      console.log('Personalization completed successfully:', data.name)

      // Small delay to ensure state updates are processed
      setTimeout(() => {
        setShowWizard(false)
        setIsVisible(false)
        console.log('Wizard and overlay closed after personalization completion')
      }, 100)
    } catch (error) {
      console.error('Failed to save personalization:', error)
      // Keep the wizard open on error so user can try again
      setShowWizard(true)
    }
  }

  const handleWizardClose = () => {
    setShowWizard(false)
  }

  // During hydration, render an empty container to match server HTML
  // This prevents hydration mismatches while maintaining proper SSR behavior
  if (isLoading || !mounted) {
    return <div className="welcome-overlay-placeholder" style={{ display: 'none' }} />
  }

  // Don't show overlay if user has completed setup or isn't a first-time visitor
  if (!isFirstVisit || hasCompletedSetup) {
    return <div className="welcome-overlay-placeholder" style={{ display: 'none' }} />
  }

  return (
    <>
      {isVisible && (
        <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-300">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-cloud/20 bg-gradient-to-r from-accent-warm/5 to-accent-cool/5">
              <h2 className="text-xl font-semibold text-ink">Welcome to TripChoice</h2>
              <button
                onClick={handleSkip}
                className="text-slate hover:text-ink transition-colors p-2 hover:bg-cloud/20 rounded-full"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Hero Section */}
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-accent-warm to-accent-cool rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <User className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-ink mb-3">
                  Let's create your perfect journey
                </h3>
                <p className="text-slate text-base leading-relaxed max-w-sm mx-auto">
                  Share your preferences and we'll curate personalized travel recommendations just for you.
                </p>
              </div>

              {/* Benefits */}
              <div className="grid grid-cols-1 gap-4">
                <div className="flex items-start space-x-4 p-4 bg-gradient-to-r from-accent-cool/10 to-transparent rounded-xl border border-accent-cool/20">
                  <div className="w-10 h-10 bg-accent-cool/20 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Target className="w-5 h-5 text-accent-cool" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-ink mb-1">Smart Recommendations</p>
                    <p className="text-xs text-slate leading-relaxed">Get destinations that match your style and budget</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4 p-4 bg-gradient-to-r from-accent-warm/10 to-transparent rounded-xl border border-accent-warm/20">
                  <div className="w-10 h-10 bg-accent-warm/20 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5">
                    <MapPin className="w-5 h-5 text-accent-warm" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-ink mb-1">Lightning Fast Setup</p>
                    <p className="text-xs text-slate leading-relaxed">Complete in under 2 minutes, no commitment required</p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-3 pt-2">
                <Button
                  onClick={handleStartPersonalization}
                  className="w-full bg-gradient-to-r from-accent-warm to-accent-warm/90 hover:from-accent-warm/90 hover:to-accent-warm text-white font-semibold py-4 rounded-xl transition-all duration-200 hover:scale-[1.02] hover:shadow-lg"
                >
                  Start Personalization
                </Button>

                <Button
                  onClick={handleSkip}
                  variant="ghost"
                  className="w-full text-slate hover:text-ink hover:bg-cloud/20 py-3 rounded-xl transition-colors"
                >
                  Skip for now
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Personalization Modal */}
      <PersonalizationModal
        isOpen={showWizard}
        onComplete={handleWizardComplete}
        onClose={handleWizardClose}
      />
    </>
  )
}
