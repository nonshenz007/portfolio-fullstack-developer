'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { analytics } from '@/lib/analytics'
import { cn } from '@/lib/utils'

interface PersonalizeModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface ProfileData {
  name: string
  persona: string
  vibe: string
  city: string
}

const PERSONAS = ['Explorer', 'Adventurer', 'Relaxer', 'Culture Seeker', 'Foodie', 'Photographer']
const VIBES = ['Chill', 'Energetic', 'Romantic', 'Social', 'Solo', 'Family-friendly']

const CITIES = [
  'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Kochi'
]

export function PersonalizeModal({ open, onOpenChange }: PersonalizeModalProps) {
  const [formData, setFormData] = useState<ProfileData>({
    name: '',
    persona: '',
    vibe: '',
    city: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Load existing profile on mount
  useEffect(() => {
    if (open && typeof window !== 'undefined') {
      const saved = localStorage.getItem('tc_profile')
      if (saved) {
        try {
          const profile = JSON.parse(saved)
          setFormData(profile)
        } catch (e) {
          console.warn('Failed to parse saved profile')
        }
      }
    }
  }, [open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name.trim()) return

    setIsSubmitting(true)

    try {
      // Save to localStorage (client-side only)
      if (typeof window !== 'undefined') {
        localStorage.setItem('tc_profile', JSON.stringify(formData))
      }

      // Track analytics
      analytics.trackPersonalizationSaved(formData.persona, formData.vibe, formData.city)

      // Close modal immediately after save
      onOpenChange(false)

    } catch (error) {
      console.error('Failed to save profile:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-lg bg-surface border-cloud/20 rounded-2xl overflow-hidden p-0">
          <div className="relative">
            <div
              className="absolute inset-0 mix-blend-overlay"
              style={{
                backgroundImage:
                  "radial-gradient(1px 1px at 10% 20%, rgba(7,28,60,.05) 1px, transparent 1px),radial-gradient(1px 1px at 30% 60%, rgba(6,71,174,.05) 1px, transparent 1px)",
                backgroundSize: '64px 64px',
                opacity: 0.03,
              }}
            />
            <div className="relative p-6 md:p-8">
              <DialogHeader className="mb-3">
                <div className="text-xs text-accent-cool/80">Let’s tailor this</div>
                <DialogTitle className="font-display text-3xl md:text-4xl font-semibold tracking-tight text-ink">
                  Your travel profile
                </DialogTitle>
              </DialogHeader>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name - Required */}
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm font-medium text-ink">Name <span className="text-accent-warm">*</span></Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="What should we call you?"
                    className="border-cloud/30 focus:border-accent-cool"
                    required
                  />
                </div>

                {/* Persona chips */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-ink">Travel persona</Label>
                  <div className="flex flex-wrap gap-2">
                    {PERSONAS.map((p) => (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setFormData(prev => ({ ...prev, persona: p }))}
                        className={cn(
                          'px-3 py-1.5 rounded-full text-sm border transition-colors',
                          formData.persona === p ? 'bg-ink text-surface border-ink' : 'bg-cloud/10 text-ink border-cloud/30 hover:bg-cloud/20'
                        )}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Vibe chips */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-ink">Preferred vibe</Label>
                  <div className="flex flex-wrap gap-2">
                    {VIBES.map((v) => (
                      <button
                        key={v}
                        type="button"
                        onClick={() => setFormData(prev => ({ ...prev, vibe: v }))}
                        className={cn(
                          'px-3 py-1.5 rounded-full text-sm border transition-colors',
                          formData.vibe === v ? 'bg-ink text-surface border-ink' : 'bg-cloud/10 text-ink border-cloud/30 hover:bg-cloud/20'
                        )}
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>

                {/* City */}
                <div className="space-y-2">
                  <Label htmlFor="city" className="text-sm font-medium text-ink">Home city</Label>
                  <Select value={formData.city} onValueChange={(value) => setFormData(prev => ({ ...prev, city: value }))}>
                    <SelectTrigger className="border-cloud/30 focus:border-accent-cool">
                      <SelectValue placeholder="Where are you based?" />
                    </SelectTrigger>
                    <SelectContent>
                      {CITIES.map((city) => (
                        <SelectItem key={city} value={city}>
                          {city}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Summary */}
                <div className="bg-cloud/10 rounded-xl p-4 text-sm text-slate">
                  {formData.name ? (
                    <span>
                      Hi <span className="text-ink font-medium">{formData.name}</span>
                      {formData.city && <> from <span className="text-ink font-medium">{formData.city}</span></>}, you’re a {formData.persona || '—'} who prefers {formData.vibe || '—'} vibes.
                    </span>
                  ) : (
                    <span>We’ll use this to recommend destinations and prices from your city.</span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-1">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => onOpenChange(false)}
                    className="flex-1 border-cloud/30 hover:border-accent-cool/50"
                  >
                    Skip for now
                  </Button>
                  <Button
                    type="submit"
                    disabled={!formData.name.trim() || isSubmitting}
                    className="flex-1 bg-accent-warm hover:bg-accent-warm/90 text-white font-semibold focus:ring-2 focus:ring-accent-cool"
                  >
                    {isSubmitting ? 'Saving...' : 'Save preferences'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Confetti removed */}
    </>
  )
}
