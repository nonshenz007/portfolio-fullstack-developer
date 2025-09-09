'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { Personalization } from '@/types'
import { analytics } from '@/lib/analytics'

const PERSONALIZATION_KEY = 'tc_profile'
const FIRST_VISIT_KEY = 'tripchoice_first_visit'

interface PersonalizationContextType {
  personalization: Personalization | null
  isLoading: boolean
  hasCompletedSetup: boolean
  isFirstVisit: boolean
  mounted: boolean
  savePersonalization: (data: Personalization) => Promise<void>
  updatePersonalization: (updates: Partial<Personalization>) => Promise<void>
  clearPersonalization: () => Promise<void>
  markSetupComplete: () => void
}

const PersonalizationContext = createContext<PersonalizationContextType | undefined>({
  personalization: null,
  isLoading: true,
  hasCompletedSetup: false,
  isFirstVisit: false,
  mounted: false,
  savePersonalization: async () => {},
  updatePersonalization: async () => {},
  clearPersonalization: async () => {},
  markSetupComplete: () => {},
})

export function usePersonalizationContext() {
  const context = useContext(PersonalizationContext)
  if (context === undefined) {
    throw new Error('usePersonalizationContext must be used within a PersonalizationProvider')
  }
  return context
}

interface PersonalizationProviderProps {
  children: React.ReactNode
}

export function PersonalizationProvider({ children }: PersonalizationProviderProps) {
  const [personalization, setPersonalization] = useState<Personalization | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasCompletedSetup, setHasCompletedSetup] = useState(false)
  const [isFirstVisit, setIsFirstVisit] = useState(false)
  const [mounted, setMounted] = useState(false)

  // Load personalization data on mount
  useEffect(() => {
    const loadPersonalization = () => {
      try {
        const stored = localStorage.getItem(PERSONALIZATION_KEY)
        const firstVisit = localStorage.getItem(FIRST_VISIT_KEY)

        if (stored) {
          const data = JSON.parse(stored)
          setPersonalization(data)
          setHasCompletedSetup(true)
        }

        // Check if this is a first-time visitor (no personalization and no first visit flag)
        setIsFirstVisit(!firstVisit && !stored)

      } catch (error) {
        console.error('Failed to load personalization:', error)
        setIsFirstVisit(true) // Default to first visit on error
      } finally {
        setIsLoading(false)
        setMounted(true)
      }
    }

    // Use setTimeout to ensure DOM is ready
    const timer = setTimeout(loadPersonalization, 0)

    return () => {
      clearTimeout(timer)
    }
  }, [])

  // Save personalization data
  const savePersonalization = useCallback(async (data: Personalization) => {
    try {
      // Save to localStorage
      localStorage.setItem(PERSONALIZATION_KEY, JSON.stringify(data))
      localStorage.setItem(FIRST_VISIT_KEY, 'true')

      // Update state
      setPersonalization(data)
      setHasCompletedSetup(true)
      setIsFirstVisit(false)

      // Track analytics
      analytics.trackPersonalizationSaved(data.persona, data.vibe, data.homeCity)
    } catch (error) {
      console.error('❌ Failed to save personalization:', error)
      throw error
    }
  }, [])

  // Update specific fields
  const updatePersonalization = useCallback(async (updates: Partial<Personalization>) => {
    if (!personalization) {
      throw new Error('No personalization data to update')
    }

    const updated = { ...personalization, ...updates }
    await savePersonalization(updated)
  }, [personalization, savePersonalization])

  // Clear personalization data
  const clearPersonalization = useCallback(async () => {
    try {
      localStorage.removeItem(PERSONALIZATION_KEY)
      localStorage.removeItem(FIRST_VISIT_KEY)

      setPersonalization(null)
      setHasCompletedSetup(false)
      setIsFirstVisit(true)

      console.log('✅ Personalization cleared')
    } catch (error) {
      console.error('❌ Failed to clear personalization:', error)
      throw error
    }
  }, [])

  // Mark setup as complete (without saving data)
  const markSetupComplete = useCallback(() => {
    localStorage.setItem(FIRST_VISIT_KEY, 'true')
    setIsFirstVisit(false)
  }, [])

  const value: PersonalizationContextType = {
    personalization,
    isLoading,
    hasCompletedSetup,
    isFirstVisit,
    mounted,
    savePersonalization,
    updatePersonalization,
    clearPersonalization,
    markSetupComplete,
  }

  return (
    <PersonalizationContext.Provider value={value}>
      {children}
    </PersonalizationContext.Provider>
  )
}
