'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Personalization } from '@/types'
import { personalizationSchema, PersonalizationInput } from '@/lib/validations'
import { useToast } from '@/hooks/use-toast'
import { CheckCircle, ArrowRight, ArrowLeft, X } from 'lucide-react'

// Enhanced option interfaces
interface Option {
  value: string
  label: string
  emoji?: string
  description?: string
  category?: string
}

const STEPS = [
  {
    id: 'basics',
    title: 'Tell us about yourself',
    subtitle: 'Help us understand who you are'
  },
  {
    id: 'travel-style',
    title: 'Your travel style',
    subtitle: 'What kind of trips do you enjoy?'
  },
  {
    id: 'preferences',
    title: 'Travel preferences',
    subtitle: 'Your budget and travel frequency'
  },
  {
    id: 'location',
    title: 'Where are you from?',
    subtitle: 'Your home city for better recommendations'
  }
]

const GENDER_OPTIONS: Option[] = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer-not-to-say', label: 'Prefer not to say' },
]

const AGE_OPTIONS: Option[] = [
  { value: '18-25', label: '18-25' },
  { value: '26-35', label: '26-35' },
  { value: '36-45', label: '36-45' },
  { value: '46-55', label: '46-55' },
  { value: '56+', label: '56+' },
]

const PERSONA_OPTIONS: Option[] = [
  { value: 'solo', label: 'Solo traveler' },
  { value: 'couple', label: 'Couple' },
  { value: 'family', label: 'Family' },
  { value: 'friends', label: 'Friends' },
]

const TRAVEL_STYLE_OPTIONS: Option[] = [
  { value: 'chill', label: 'Relaxation & Wellness' },
  { value: 'adventure', label: 'Adventure & Exploration' },
  { value: 'cultural', label: 'Culture & History' },
  { value: 'nature', label: 'Nature & Outdoors' },
  { value: 'city', label: 'City & Urban' },
  { value: 'food', label: 'Food & Cuisine' },
]

const BUDGET_OPTIONS: Option[] = [
  { value: 'budget', label: 'Budget (₹10k-25k)' },
  { value: 'mid-range', label: 'Mid-range (₹25k-50k)' },
  { value: 'luxury', label: 'Luxury (₹50k+)' },
]

const TRAVEL_FREQUENCY_OPTIONS: Option[] = [
  { value: 'first-time', label: 'First time traveler' },
  { value: 'occasional', label: '1-2 trips per year' },
  { value: 'frequent', label: '3-5 trips per year' },
  { value: 'expert', label: 'Frequent traveler' },
]

interface PersonalizationWizardProps {
  isOpen: boolean
  onComplete: (data: Personalization) => void
  onClose: () => void
  initialData?: Personalization
}

export function PersonalizationWizard({
  isOpen,
  onComplete,
  onClose,
  initialData
}: PersonalizationWizardProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState<PersonalizationInput>({
    name: '',
    gender: 'prefer-not-to-say',
    ageRange: '18-25',
    persona: 'solo',
    vibe: 'chill',
    homeCity: '',
    budgetPreference: 'mid-range',
    travelFrequency: 'occasional',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()

  // Initialize form data from initial data or localStorage
  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        gender: (initialData as any).gender || '',
        ageRange: (initialData as any).ageRange || '',
        persona: initialData.persona as any || '',
        vibe: initialData.vibe as any || '',
        homeCity: initialData.homeCity || '',
        budgetPreference: (initialData as any).budgetPreference || '',
        travelFrequency: (initialData as any).travelFrequency || '',
      })
    }
  }, [initialData])

  // Reset to first step when modal opens
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0)
      setErrors({})
    }
  }, [isOpen])

  const updateFormData = useCallback((field: keyof PersonalizationInput, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }, [errors])

  const validateCurrentStep = useCallback((): boolean => {
    const stepFields = getStepFields(currentStep)
    const stepData = Object.fromEntries(
      Object.entries(formData).filter(([key]) => stepFields.includes(key as keyof PersonalizationInput))
    )

    try {
      // For step 0, only require name and ageRange (make gender optional)
      if (currentStep === 0) {
        if (!stepData.name || stepData.name.trim() === '') {
          setErrors({ name: 'Name is required' })
          return false
        }
        if (!stepData.ageRange || stepData.ageRange === '') {
          setErrors({ ageRange: 'Please select your age range' })
          return false
        }
        setErrors({})
        return true
      }

      // For other steps, validate required fields
      const requiredFields = stepFields.filter(field => {
        if (currentStep === 1 && field === 'persona') return true
        if (currentStep === 2 && ['vibe', 'budgetPreference', 'travelFrequency'].includes(field)) return true
        if (currentStep === 3 && field === 'homeCity') return true
        return false
      })

      const missingFields = requiredFields.filter(field => !stepData[field] || stepData[field] === '')
      if (missingFields.length > 0) {
        const validationErrors: Record<string, string> = {}
        missingFields.forEach(field => {
          validationErrors[field] = `${field === 'homeCity' ? 'Home city' : field} is required`
        })
        setErrors(validationErrors)
        return false
      }

      setErrors({})
      return true
    } catch (error: any) {
      console.error('Validation error:', error)
      setErrors({ general: 'Please fill in all required fields' })
      return false
    }
  }, [currentStep, formData])

  const getStepFields = (step: number): (keyof PersonalizationInput)[] => {
    switch (step) {
      case 0: return ['name', 'gender', 'ageRange']
      case 1: return ['persona']
      case 2: return ['vibe', 'budgetPreference', 'travelFrequency']
      case 3: return ['homeCity']
      default: return []
    }
  }

  const handleNext = () => {
    if (validateCurrentStep()) {
      if (currentStep < STEPS.length - 1) {
        setCurrentStep(prev => prev + 1)
      }
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleComplete = async () => {
    if (!validateCurrentStep()) return

    setIsSubmitting(true)

    try {
      // Validate entire form
      const result = personalizationSchema.parse(formData)

      // Create personalization object
      const personalization: Personalization = {
        name: result.name,
        gender: result.gender,
        ageRange: result.ageRange,
        persona: result.persona,
        vibe: result.vibe,
        homeCity: result.homeCity,
        budgetPreference: result.budgetPreference,
        travelFrequency: result.travelFrequency,
      }

      // Save to localStorage (client-side only)
      if (typeof window !== 'undefined') {
        localStorage.setItem('tc_profile', JSON.stringify(personalization))
        localStorage.setItem('tripchoice_first_visit', 'true')
      }

      // Success toast removed to keep UX minimal

      // Call completion handler
      onComplete(personalization)

    } catch (error) {
      console.error('Error completing personalization:', error)

      // Show specific error messages based on validation failures
      if (error instanceof Error && error.message.includes('Name is required')) {
        toast({
          title: "Name is required",
          description: "Please tell us your name so we can personalize your experience!",
          variant: "destructive",
        })
      } else if (error instanceof Error && error.message.includes('Home city is required')) {
        toast({
          title: "Home city needed",
          description: "We'll use this to find trips near you!",
          variant: "destructive",
        })
      } else if (error instanceof Error && error.message.includes('Please select')) {
        toast({
          title: "Almost there!",
          description: "Please complete all the required fields to continue.",
          variant: "destructive",
        })
      } else {
        toast({
          title: "Something went wrong",
          description: "Please try again or skip for now.",
          variant: "destructive",
        })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStepContent = () => {
    const step = STEPS[currentStep]

    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
          <div className="text-center mb-8">
              {/* Removed emoji greeting */}
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{step.title}</h2>
              <p className="text-gray-600 text-lg">We'll use this to create your perfect travel recommendations!</p>
            </div>

            <div className="space-y-6">
              <div className="relative">
                <Label htmlFor="name" className="text-sm font-semibold text-gray-800 mb-2 block">
                  What's your name? <span className="text-red-500">*</span>
                  {formData.name && !errors.name && <span className="ml-2 text-green-600">✓</span>}
                </Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={(e) => updateFormData('name', e.target.value)}
                  className={`transition-all duration-200 text-lg py-3 px-4 rounded-xl border-2 ${
                    errors.name
                      ? 'border-red-400 bg-red-50 focus:border-red-500'
                      : formData.name
                        ? 'border-green-400 bg-green-50 focus:border-green-500'
                        : 'border-gray-300 focus:border-blue-500'
                  }`}
                />
                {/* Removed encouraging emoji message */}
                {errors.name && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.name}</p>}
              </div>

              <div>
                <Label className="text-sm font-semibold text-gray-800 mb-4 block">
                  What's your gender? <span className="text-gray-500 font-normal">(Optional)</span>
                </Label>
                <div className="grid grid-cols-2 gap-4">
                  {GENDER_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => updateFormData('gender', option.value)}
                      className={`p-4 text-center border-2 rounded-xl transition-all duration-200 transform hover:scale-105 ${
                        formData.gender === option.value
                          ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-lg'
                          : 'border-gray-200 hover:border-blue-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="text-2xl mb-1">{option.emoji}</div>
                      <div className="font-medium">{option.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-sm font-semibold text-gray-800 mb-4 block">
                  What's your age range? <span className="text-red-500">*</span>
                  {formData.ageRange && !errors.ageRange && <span className="ml-2 text-green-600">✓</span>}
                </Label>
                <div className="grid grid-cols-2 gap-4">
                  {AGE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => updateFormData('ageRange', option.value)}
                      className={`p-4 text-center border-2 rounded-xl transition-all duration-200 transform hover:scale-105 ${
                        formData.ageRange === option.value
                          ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-lg'
                          : 'border-gray-200 hover:border-blue-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="text-2xl mb-1">{option.emoji}</div>
                      <div className="font-medium">{option.label}</div>
                    </button>
                  ))}
                </div>
                {errors.ageRange && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.ageRange}</p>}
              </div>
            </div>
          </div>
        )

      case 1:
        return (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-100 to-blue-100 rounded-full mb-4">
                <span className="text-2xl">👥</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{step.title}</h2>
              <p className="text-gray-600 text-lg">Tell us who you're traveling with so we can suggest the perfect destinations!</p>
            </div>

            <div>
              <Label className="text-sm font-semibold text-gray-800 mb-4 block">
                Who will be traveling? <span className="text-red-500">*</span>
                {formData.persona && !errors.persona && <span className="ml-2 text-green-600">✓</span>}
              </Label>
              <div className="grid grid-cols-2 gap-4">
                {PERSONA_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => updateFormData('persona', option.value)}
                    className={`p-6 text-center border-2 rounded-xl transition-all duration-200 transform hover:scale-105 ${
                      formData.persona === option.value
                        ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-lg'
                        : 'border-gray-200 hover:border-blue-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="text-3xl mb-2">{option.emoji}</div>
                    <div className="font-semibold text-lg">{option.label}</div>
                    <div className="text-sm text-gray-600 mt-1">{option.description}</div>
                  </button>
                ))}
              </div>
              {errors.persona && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.persona}</p>}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-100 to-pink-100 rounded-full mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{step.title}</h2>
              <p className="text-gray-600 text-lg">Help us understand what kind of travel experiences you love!</p>
            </div>

            <div className="space-y-6">
              <div>
                <Label className="text-sm font-semibold text-gray-800 mb-4 block">
                  What type of travel experiences do you enjoy? <span className="text-red-500">*</span>
                  {formData.vibe && !errors.vibe && <span className="ml-2 text-green-600">✓</span>}
                </Label>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { value: 'chill', label: 'Relaxation & Wellness', emoji: '🏖️', desc: 'Spa days, beaches, peaceful retreats' },
                    { value: 'adventure', label: 'Adventure & Exploration', emoji: '🏔️', desc: 'Hiking, thrill activities, new challenges' },
                    { value: 'cultural', label: 'Culture & History', emoji: '🏛️', desc: 'Museums, heritage sites, local traditions' },
                    { value: 'nature', label: 'Nature & Outdoors', emoji: '🌲', desc: 'Wildlife, landscapes, outdoor activities' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => updateFormData('vibe', option.value)}
                      className={`p-5 text-center border-2 rounded-xl transition-all duration-200 transform hover:scale-105 ${
                        formData.vibe === option.value
                          ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-lg'
                          : 'border-gray-200 hover:border-blue-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="text-3xl mb-2">{option.emoji}</div>
                      <div className="font-semibold text-lg">{option.label}</div>
                      <div className="text-sm text-gray-600 mt-1">{option.desc}</div>
                    </button>
                  ))}
                </div>
                {errors.vibe && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.vibe}</p>}
              </div>

              <div>
                <Label className="text-sm font-semibold text-gray-800 mb-4 block">
                  What's your preferred budget range? <span className="text-red-500">*</span>
                  {formData.budgetPreference && !errors.budgetPreference && <span className="ml-2 text-green-600">✓</span>}
                </Label>
                <div className="grid grid-cols-1 gap-4">
                  {BUDGET_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => updateFormData('budgetPreference', option.value)}
                      className={`p-5 text-center border-2 rounded-xl transition-all duration-200 transform hover:scale-105 ${
                        formData.budgetPreference === option.value
                          ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-lg'
                          : 'border-gray-200 hover:border-blue-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="text-3xl mb-2">{option.emoji}</div>
                      <div className="font-semibold text-lg">{option.label}</div>
                      <div className="text-sm text-gray-600 mt-1">{option.description}</div>
                    </button>
                  ))}
                </div>
                {errors.budgetPreference && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.budgetPreference}</p>}
              </div>

              <div>
                <Label className="text-sm font-semibold text-gray-800 mb-4 block">
                  How often do you travel? <span className="text-red-500">*</span>
                  {formData.travelFrequency && !errors.travelFrequency && <span className="ml-2 text-green-600">✓</span>}
                </Label>
                <div className="grid grid-cols-1 gap-4">
                  {TRAVEL_FREQUENCY_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => updateFormData('travelFrequency', option.value)}
                      className={`p-4 text-center border-2 rounded-xl transition-all duration-200 transform hover:scale-105 ${
                        formData.travelFrequency === option.value
                          ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-lg'
                          : 'border-gray-200 hover:border-blue-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <div className="text-2xl mb-1">{option.emoji}</div>
                      <div className="font-semibold text-lg">{option.label}</div>
                      <div className="text-sm text-gray-600 mt-1">{option.description}</div>
                    </button>
                  ))}
                </div>
                {errors.travelFrequency && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.travelFrequency}</p>}
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full mb-4">
                <span className="text-2xl">🏠</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{step.title}</h2>
              <p className="text-gray-600 text-lg">This helps us find trips that are perfect for you!</p>
            </div>

            <div className="space-y-6">
              <div className="relative">
                <Label htmlFor="homeCity" className="text-sm font-semibold text-gray-800 mb-2 block">
                  Where are you located? <span className="text-red-500">*</span>
                  {formData.homeCity && !errors.homeCity && <span className="ml-2 text-green-600">✓</span>}
                </Label>
                <Input
                  id="homeCity"
                  type="text"
                  placeholder="Enter your city (e.g., Mumbai, Delhi, Bangalore)"
                  value={formData.homeCity}
                  onChange={(e) => updateFormData('homeCity', e.target.value)}
                  className={`transition-all duration-200 text-lg py-3 px-4 rounded-xl border-2 ${
                    errors.homeCity
                      ? 'border-red-400 bg-red-50 focus:border-red-500'
                      : formData.homeCity
                        ? 'border-green-400 bg-green-50 focus:border-green-500'
                        : 'border-gray-300 focus:border-blue-500'
                  }`}
                />
                {formData.homeCity && !errors.homeCity && (
                  <div className="flex items-center mt-2 text-green-600">
                    <span className="text-sm">We'll find trips near {formData.homeCity}.</span>
                  </div>
                )}
                {errors.homeCity && <p className="text-sm text-red-600 mt-2 flex items-center"><span className="mr-1">⚠️</span>{errors.homeCity}</p>}
              </div>

              {/* Removed celebratory callout */}
            </div>
          </div>
        )

      default:
        return null
    }
  }

  const progress = ((currentStep + 1) / STEPS.length) * 100

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-white/20">
        {/* Header */}
        <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 text-white p-8">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative">
            <button
              onClick={onClose}
              className="absolute top-0 right-0 text-white/70 hover:text-white transition-colors p-2"
            >
              <X className="w-6 h-6" />
            </button>
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">✈️ Let's Plan Your Dream Trip</h2>
              <p className="text-blue-100 text-sm">Just a few quick questions to get you started!</p>
            </div>
          </div>
        </div>

        {/* Simple step indicator */}
        <div className="px-8 py-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Step {currentStep + 1} of {STEPS.length}</span>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto max-h-[calc(90vh-200px)]">
          {renderStepContent()}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-8 py-6 bg-gradient-to-r from-blue-50 to-purple-50">
          {/* Validation Error Message */}
          {Object.keys(errors).length > 0 && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center text-red-700">
                <span className="mr-2">⚠️</span>
                <span className="text-sm font-medium">Please complete the required fields above to continue</span>
              </div>
            </div>
          )}
          <div className="flex justify-between items-center">
            <Button
              type="button"
              variant="ghost"
              onClick={handlePrev}
              disabled={currentStep === 0}
              className={`transition-all duration-200 px-6 py-3 rounded-xl ${
                currentStep === 0
                  ? 'text-gray-300 cursor-not-allowed'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-white/50'
              }`}
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </Button>

            {currentStep < STEPS.length - 1 ? (
              <Button
                type="button"
                onClick={handleNext}
                disabled={Object.keys(errors).length > 0}
                className={`px-8 py-3 rounded-xl shadow-lg transition-all duration-200 ${
                  Object.keys(errors).length > 0
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {Object.keys(errors).length > 0 ? 'Complete Required Fields' : 'Next'}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            ) : (
              <Button
                type="button"
                onClick={handleComplete}
                disabled={isSubmitting}
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 disabled:transform-none"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Creating Your Experience...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Complete Setup
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
