'use client'

import { useState, useEffect } from 'react'
import { X, User, MapPin, Heart, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Personalization } from '@/types'

interface PersonalizationModalProps {
  isOpen: boolean
  onClose: () => void
  onComplete: (profile: Personalization) => void
}

const PERSONAS = [
  { value: 'solo', label: 'Solo Traveler', icon: '🧑', description: 'Exploring on my own' },
  { value: 'couple', label: 'Couple', icon: '👫', description: 'Romantic getaway' },
  { value: 'family', label: 'Family', icon: '👨‍👩‍👧‍👦', description: 'Family vacation' },
  { value: 'friends', label: 'Friends', icon: '👥', description: 'Group adventure' }
]

const VIBES = [
  { value: 'adventure', label: 'Adventure', icon: '🏔️', description: 'Thrilling experiences' },
  { value: 'relaxation', label: 'Relaxation', icon: '🏖️', description: 'Peaceful getaways' },
  { value: 'culture', label: 'Culture', icon: '🏛️', description: 'Historical & cultural' },
  { value: 'nature', label: 'Nature', icon: '🌳', description: 'Natural wonders' },
  { value: 'luxury', label: 'Luxury', icon: '🏨', description: 'Premium experiences' },
  { value: 'budget', label: 'Budget', icon: '💰', description: 'Value for money' }
]

export function PersonalizationModal({ isOpen, onClose, onComplete }: PersonalizationModalProps) {
  const [step, setStep] = useState(1)
  const [profile, setProfile] = useState<Partial<Personalization>>({
    name: '',
    persona: '',
    vibe: '',
    homeCity: '',
    ageRange: '26-35',
    gender: 'prefer-not-to-say',
    budgetPreference: 'mid-range',
    travelFrequency: 'occasional'
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  // Check if profile is complete
  const isProfileComplete = profile.name && profile.persona && profile.vibe && profile.homeCity

  const updateProfile = (field: keyof Personalization, value: string) => {
    setProfile(prev => ({ ...prev, [field]: value }))
  }

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const handleComplete = async () => {
    if (!isProfileComplete) return

    setIsSubmitting(true)
    try {
      // Save to localStorage
      const completeProfile: Personalization = {
        name: profile.name!,
        persona: profile.persona!,
        vibe: profile.vibe!,
        homeCity: profile.homeCity!,
        ageRange: profile.ageRange!,
        gender: profile.gender!,
        budgetPreference: profile.budgetPreference!,
        travelFrequency: profile.travelFrequency!
      }

      localStorage.setItem('tc_profile', JSON.stringify(completeProfile))
      onComplete(completeProfile)
      onClose()
    } catch (error) {
      console.error('Error saving profile:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-warm/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="w-8 h-8 text-warm" />
              </div>
              <h2 className="text-2xl font-bold text-ink mb-2">Welcome to TripChoice!</h2>
              <p className="text-slate">Let's personalize your travel experience</p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-ink font-medium">What's your name? *</Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter your name"
                  value={profile.name || ''}
                  onChange={(e) => updateProfile('name', e.target.value)}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="city" className="text-ink font-medium">Where are you from? *</Label>
                <div className="relative mt-2">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate" />
                  <Input
                    id="city"
                    type="text"
                    placeholder="Your home city"
                    value={profile.homeCity || ''}
                    onChange={(e) => updateProfile('homeCity', e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-cool/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="w-8 h-8 text-cool" />
              </div>
              <h2 className="text-2xl font-bold text-ink mb-2">Who are you traveling with?</h2>
              <p className="text-slate">Help us recommend the perfect experiences</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {PERSONAS.map((persona) => (
                <button
                  key={persona.value}
                  onClick={() => updateProfile('persona', persona.value)}
                  className={`p-4 rounded-lg border-2 text-left transition-all duration-250 ease-out ${
                    profile.persona === persona.value
                      ? 'border-warm bg-warm/5 text-ink'
                      : 'border-slate/20 hover:border-slate/30 bg-surface text-slate hover:text-ink'
                  }`}
                >
                  <div className="text-2xl mb-2">{persona.icon}</div>
                  <div className="font-medium text-sm">{persona.label}</div>
                  <div className="text-xs opacity-70 mt-1">{persona.description}</div>
                </button>
              ))}
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-warm/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-warm" />
              </div>
              <h2 className="text-2xl font-bold text-ink mb-2">What's your travel vibe?</h2>
              <p className="text-slate">Tell us what kind of experiences excite you</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {VIBES.map((vibe) => (
                <button
                  key={vibe.value}
                  onClick={() => updateProfile('vibe', vibe.value)}
                  className={`p-4 rounded-lg border-2 text-left transition-all duration-250 ease-out ${
                    profile.vibe === vibe.value
                      ? 'border-warm bg-warm/5 text-ink'
                      : 'border-slate/20 hover:border-slate/30 bg-surface text-slate hover:text-ink'
                  }`}
                >
                  <div className="text-2xl mb-2">{vibe.icon}</div>
                  <div className="font-medium text-sm">{vibe.label}</div>
                  <div className="text-xs opacity-70 mt-1">{vibe.description}</div>
                </button>
              ))}
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-surface border-2 border-slate/20">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="sr-only">Personalize Your Experience</DialogTitle>
            <div className="flex space-x-2">
              {[1, 2, 3].map((stepNum) => (
                <div
                  key={stepNum}
                  className={`w-2 h-2 rounded-full transition-colors duration-250 ${
                    stepNum <= step ? 'bg-warm' : 'bg-slate/20'
                  }`}
                />
              ))}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="py-6">
          {renderStepContent()}

          <div className="flex justify-between mt-8">
            {step > 1 ? (
              <Button
                variant="outline"
                onClick={handleBack}
                className="border-slate/20 hover:bg-slate/5"
              >
                Back
              </Button>
            ) : (
              <div />
            )}

            {step < 3 ? (
              <Button
                onClick={handleNext}
                disabled={!((step === 1 && profile.name && profile.homeCity) ||
                          (step === 2 && profile.persona))}
                className="bg-warm hover:bg-warm/90"
              >
                Next
              </Button>
            ) : (
              <Button
                onClick={handleComplete}
                disabled={!isProfileComplete || isSubmitting}
                className="bg-warm hover:bg-warm/90"
              >
                {isSubmitting ? 'Saving...' : 'Get Started'}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}