'use client'

import { usePersonalizationContext } from '@/contexts/PersonalizationContext'

// Backward compatibility hook that uses the new context
export function usePersonalization() {
  const {
    personalization,
    isLoading,
    savePersonalization,
    clearPersonalization,
    updatePersonalization,
    hasCompletedSetup,
  } = usePersonalizationContext()

  return {
    personalization,
    isLoading,
    savePersonalization,
    clearPersonalization,
    updatePersonalization,
    hasPersonalization: hasCompletedSetup,
  }
}
