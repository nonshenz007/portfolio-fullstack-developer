export interface Package {
  id: string
  slug: string
  title: string
  summary: string
  destinations: string[]
  themes: string[]
  duration_days: number
  base_price_pp: number
  min_pax: number
  max_pax: number
  hero: string // Directus file URL
  gallery: string[] // Directus file URLs
  inclusions: string[]
  exclusions: string[]
  policies: string
  domestic: boolean
  rating: number
  ratings_count: number
  status: 'draft' | 'published'
  created_at: string
  updated_at: string
}

export interface ItineraryDay {
  id: string
  package: string // Package ID
  day_number: number
  title: string
  bullets: string[]
}

export interface Variant {
  id: string
  package: string // Package ID
  type: 'bus' | 'train' | 'flight' | 'cab' | 'hotel'
  subclass: string
  adj_pp: number
  vendor_notes: string
  // Additional properties for enhanced variant display
  journeyTime?: string
  availability?: string
  safetyRating?: number
  environmentalImpact?: string
  cancellationPolicy?: string
  baggageAllowance?: string
  onboardServices?: string
  customerRating?: number
  totalReviews?: number
  tier?: string
  amenities?: string[]
}

export interface PriceRule {
  id: string
  scope: 'global' | 'package'
  package?: string // Package ID, nullable for global rules
  type: 'season' | 'weekend' | 'origin' | 'custom'
  start_date: string
  end_date: string
  multiplier: number
  delta: number
  conditions: Record<string, any>
}

export interface Inventory {
  id: string
  package: string // Package ID
  date: string
  seats_total: number
  seats_sold: number
}

export interface FlashSale {
  id: string
  name: string
  packages: string[] // Package IDs
  discount_percent: number
  start_at: string
  end_at: string
  seat_cap: number
}

export interface Review {
  id: string
  package: string // Package ID
  rating: number
  text: string
  author_name: string
  source: string
  media?: string // Directus file URL
}

export interface Page {
  id: string
  slug: string
  title: string
  body: string // Markdown
  og_image?: string // Directus file URL
}

export interface Personalization {
  name: string
  gender: 'male' | 'female' | 'other' | 'prefer-not-to-say'
  ageRange: '18-25' | '26-35' | '36-45' | '46-55' | '56+'
  persona: string
  vibe: string
  homeCity: string
  budgetPreference: 'budget' | 'mid-range' | 'luxury' | 'flexible'
  travelFrequency: 'first-time' | 'occasional' | 'frequent' | 'expert'
}

export interface PriceBreakdown {
  basePrice: number
  seasonMultiplier: number
  weekendMultiplier: number
  originMultiplier: number
  variantDelta: number
  roomingDelta: number
  discounts: number
  total: number
  currency: string
}

export interface WhatsAppPayload {
  package: string // Package slug
  variant?: string // Variant ID
  date?: string
  pax?: number
  utm?: Record<string, string>
}

export type Theme = 'Weekend' | 'Under ₹15k' | 'Visa-free' | 'Honeymoon' | 'Mountains' | 'Beach' | 'Adventure' | 'Cultural'
export type Destination = 'Goa' | 'Kerala' | 'Kashmir' | 'Bali' | 'Dubai' | 'Da Nang'
