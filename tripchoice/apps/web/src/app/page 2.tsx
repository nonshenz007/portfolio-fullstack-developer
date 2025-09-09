import { Metadata } from 'next'
import { HeroMasthead } from '@/components/HeroMasthead'
import Image from 'next/image'
import { SafeImage } from '@/components/safe-image'
import { FlashRibbon } from '@/components/flash-ribbon'
import { EditorialTile } from '@/components/EditorialTile'
import { Button } from '@/components/ui/button'
import { Magnetic } from '@/components/magnetic'
import { WelcomeOverlayNew } from '@/components/welcome-overlay-new'
import { SearchSection } from '@/components/search-section'
import { PersonalizationProvider } from '@/contexts/PersonalizationContext'
import { getPackages, getActiveFlashSales } from '@/lib/cms'
import { Package, FlashSale } from '@/types'
import { generateFAQStructuredData } from '@/lib/structured-data'
import { Reveal } from '@/components/reveal'
import { SectionTitleReveal } from '@/components/SectionTitleReveal'

// Client component to handle personalization loading
function HomePageClient({ packages, flashSale }: { packages: Package[], flashSale: FlashSale | null }) {
  const faqs = [
    {
      question: "How do I book a trip with TripChoice?",
      answer: "Simply browse our curated packages, select your preferred option, and click the WhatsApp button to connect with our travel experts. We'll guide you through the booking process and answer any questions you have."
    },
    {
      question: "Are the prices shown all-inclusive?",
      answer: "Yes, our 'From ₹' pricing includes all major components like accommodation, transportation, and activities. Some optional add-ons may be available for customization."
    },
    {
      question: "Can I customize my travel package?",
      answer: "Absolutely! All our packages can be customized based on your preferences, budget, and requirements. Contact us via WhatsApp to discuss your specific needs."
    },
    {
      question: "What documents do I need for international travel?",
      answer: "Requirements vary by destination. Generally, you'll need a valid passport, visa (if required), and travel insurance. We'll provide a complete checklist once you book with us."
    },
    {
      question: "How far in advance should I book?",
      answer: "We recommend booking 2-3 weeks in advance for domestic trips and 4-6 weeks for international destinations to ensure availability and best rates."
    }
  ]

  return (
    <main className="min-h-screen">
      {/* Flash Sale Ribbon */}
      {flashSale && <FlashRibbon flashSale={flashSale} />}

      {/* Welcome overlay kept (separate from intro overlay) */}
      <WelcomeOverlayNew delayMs={1700} />

      {/* Hero Masthead */}
      <HeroMasthead />

      {/* Search band below hero */}
      <SearchSection />

      {/* Cinematic Collections + Featured */}
      <div id="explore-section" className="pt-16 pb-20 space-y-24">
        <div id="deals-section" className="absolute -top-20"></div>

        {/* First section title with scroll choreography */}
        <section className="container mx-auto px-4 relative">
          <div className="relative">
            <SectionTitleReveal>
              <div className="text-center mb-12">
                <div className="text-sm text-accent-cool/80 mb-2">Curations</div>
                <h2 className="text-ink text-5xl lg:text-6xl font-display font-extrabold tracking-tight mb-3 leading-[1.05]">Weekend Getaways</h2>
                <p className="text-slate text-lg max-w-3xl mx-auto leading-snug">Short escapes that feel big. Perfectly planned and zero stress.</p>
              </div>
            </SectionTitleReveal>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              <a href="/collections/weekend" className="group relative rounded-2xl overflow-hidden shadow-e2">
                <SafeImage src="https://source.unsplash.com/1200x800/?goa%20beach%20sunset" alt="Goa Beach Weekend Getaway" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.03] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/20 to-transparent" />
                <div className="absolute bottom-5 left-5">
                  <div className="text-surface/90 text-sm mb-1">Weekend</div>
                  <div className="text-surface font-display text-2xl font-semibold">Goa beaches</div>
                  <div className="text-surface/70 text-xs">From ₹14,999</div>
                </div>
              </a>

              <a href="/collections/mountains" className="group relative rounded-2xl overflow-hidden shadow-e2">
                <SafeImage src="https://source.unsplash.com/1200x800/?kashmir%20mountains" alt="Kashmir Mountains and Valleys" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.03] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/20 to-transparent" />
                <div className="absolute bottom-5 left-5">
                  <div className="text-surface/90 text-sm mb-1">Mountains</div>
                  <div className="text-surface font-display text-2xl font-semibold">Kashmir valleys</div>
                  <div className="text-surface/70 text-xs">From ₹28,500</div>
                </div>
              </a>

              <a href="/collections/beach" className="group relative rounded-2xl overflow-hidden shadow-e2">
                <SafeImage src="https://source.unsplash.com/1200x800/?thailand%20beach" alt="Pattaya Beach Thailand" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.03] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/20 to-transparent" />
                <div className="absolute bottom-5 left-5">
                  <div className="text-surface/90 text-sm mb-1">International</div>
                  <div className="text-surface font-display text-2xl font-semibold">Thailand</div>
                  <div className="text-surface/70 text-xs">From ₹35,999</div>
                </div>
              </a>

              <a href="/collections/luxury" className="group relative rounded-2xl overflow-hidden shadow-e2">
                <SafeImage src="https://source.unsplash.com/1200x800/?dubai%20burj%20khalifa%20skyline" alt="Dubai Luxury Experience" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.03] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/20 to-transparent" />
                <div className="absolute bottom-5 left-5">
                  <div className="text-surface/90 text-sm mb-1">Luxury</div>
                  <div className="text-surface font-display text-2xl font-semibold">Dubai opulence</div>
                  <div className="text-surface/70 text-xs">From ₹85,000</div>
                </div>
              </a>

              <a href="/collections/adventure" className="group relative rounded-2xl overflow-hidden shadow-e2">
                <SafeImage src="https://source.unsplash.com/1200x800/?kerala%20backwaters%20houseboat" alt="Kerala Backwaters Adventure" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.03] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/20 to-transparent" />
                <div className="absolute bottom-5 left-5">
                  <div className="text-surface/90 text-sm mb-1">Adventure</div>
                  <div className="text-surface font-display text-2xl font-semibold">Kerala backwaters</div>
                  <div className="text-surface/70 text-xs">From ₹16,999</div>
                </div>
              </a>

              <a href="/collections/cultural" className="group relative rounded-2xl overflow-hidden shadow-e2">
                <SafeImage src="https://source.unsplash.com/1200x800/?rajasthan%20palace" alt="Rajasthan Royal Heritage" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.03] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-ink/20 to-transparent" />
                <div className="absolute bottom-5 left-5">
                  <div className="text-surface/90 text-sm mb-1">Heritage</div>
                  <div className="text-surface font-display text-2xl font-semibold">Rajasthan palaces</div>
                  <div className="text-surface/70 text-xs">From ₹22,999</div>
                </div>
              </a>
            </div>
          </div>
        </section>

        {/* Flash CTA */}
        {flashSale && (
          <section className="container mx-auto px-4 relative">
            <div className="relative overflow-hidden rounded-2xl border border-cloud/20 bg-gradient-to-r from-accent-warm/15 via-surface to-accent-cool/10 p-8 md:p-10 shadow-e1">
              <div
                className="absolute inset-0 mix-blend-overlay"
                style={{
                  backgroundImage:
                    "radial-gradient(1px 1px at 10% 20%, rgba(7,28,60,.05) 1px, transparent 1px),radial-gradient(1px 1px at 30% 60%, rgba(6,71,174,.05) 1px, transparent 1px)",
                  backgroundSize: '64px 64px',
                  opacity: 0.05,
                }}
              />
              <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div>
                  <div className="text-sm text-ink/70 mb-1">Limited time</div>
                  <h3 className="text-ink text-3xl md:text-4xl font-display font-semibold">{flashSale.name}</h3>
                </div>
                <Magnetic>
                  <div className="inline-block">
                    <Button asChild className="rounded-full bg-ink text-surface hover:bg-ink/90 px-6 py-3">
                      <a href="#deals-section">Grab the offer</a>
                    </Button>
                  </div>
                </Magnetic>
              </div>
            </div>
          </section>
        )}

        {/* Popular Destinations */}
        <section className="container mx-auto px-4 relative">
          <div className="relative">
            <Reveal className="text-center mb-12">
              <div className="text-sm text-accent-cool/80 mb-2">Popular Destinations</div>
              <h2 className="text-ink text-5xl lg:text-6xl font-display font-semibold tracking-tight mb-3 leading-[1.05]">Where dreams take flight</h2>
              <p className="text-slate text-lg max-w-3xl mx-auto leading-snug">From snow-capped mountains to pristine beaches, discover the world's most breathtaking destinations.</p>
            </Reveal>

            {/* Popular Destinations Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
              <div className="group relative rounded-xl overflow-hidden shadow-e1 cursor-pointer">
                <SafeImage src="https://source.unsplash.com/1200x800/?kashmir%20valley" alt="Kashmir Paradise" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.05] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/60 via-ink/20 to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="text-surface font-display text-lg font-semibold">Kashmir</div>
                  <div className="text-surface/80 text-xs">Heaven on Earth</div>
                </div>
              </div>

              <div className="group relative rounded-xl overflow-hidden shadow-e1 cursor-pointer">
                <SafeImage src="https://source.unsplash.com/1200x800/?goa%20beach%20sunset" alt="Goa Beaches" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.05] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/60 via-ink/20 to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="text-surface font-display text-lg font-semibold">Goa</div>
                  <div className="text-surface/80 text-xs">Beach Paradise</div>
                </div>
              </div>

              <div className="group relative rounded-xl overflow-hidden shadow-e1 cursor-pointer">
                <SafeImage src="https://source.unsplash.com/1200x800/?kerala%20backwaters%20houseboat" alt="Kerala Backwaters" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.05] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/60 via-ink/20 to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="text-surface font-display text-lg font-semibold">Kerala</div>
                  <div className="text-surface/80 text-xs">God's Own Country</div>
                </div>
              </div>

              <div className="group relative rounded-xl overflow-hidden shadow-e1 cursor-pointer">
                <SafeImage src="https://source.unsplash.com/1200x800/?dubai%20desert%20safari" alt="Dubai Luxury" ratio="4:3" className="transition-transform duration-300 group-hover:scale-[1.05] cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/60 via-ink/20 to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="text-surface font-display text-lg font-semibold">Dubai</div>
                  <div className="text-surface/80 text-xs">City of Gold</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Now using EditorialTile */}
        <section className="container mx-auto px-4 relative">
          <div className="relative">
            <Reveal className="text-center mb-12">
              <div className="text-sm text-accent-cool/80 mb-2">Editor's Choice</div>
              <h2 className="text-ink text-5xl lg:text-6xl font-display font-semibold tracking-tight mb-3 leading-[1.05]">Curated experiences this month</h2>
              <p className="text-slate text-lg max-w-3xl mx-auto leading-snug">Handpicked by our travel experts — perfect for every mood and moment.</p>
            </Reveal>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-6">
              {packages.slice(0, 6).map((pkg, index) => (
                <Reveal key={pkg.id} delay={index * 0.05}>
                  <EditorialTile pkg={pkg} />
                </Reveal>
              ))}
            </div>
            <div className="text-center">
              <Magnetic>
                <div className="inline-block">
                  <Button asChild className="bg-ink hover:bg-ink/90 text-surface rounded-full px-6 py-3">
                    <a href="/explore" className="flex items-center gap-3">Discover all adventures</a>
                  </Button>
                </div>
              </Magnetic>
            </div>
          </div>
        </section>

      {/* Why TripChoice — photo-backed split hero */}
      <section className="relative py-20 overflow-hidden">
        <div className="container mx-auto px-4 relative">
          <div className="grid lg:grid-cols-12 gap-10 items-center">
            {/* Photo side */}
            <div className="lg:col-span-6 order-last lg:order-first">
              <div className="relative rounded-3xl overflow-hidden shadow-e2 bg-cloud">
                <SafeImage src="https://source.unsplash.com/1200x800/?kashmir%20scenic%20lake" alt="Scenic mountain lake in Kashmir" ratio="16:10" className="cinematic-grade" />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/40 via-ink/10 to-transparent" />
              </div>
            </div>

            {/* Content side */}
            <div className="lg:col-span-6 text-center lg:text-left">
              <div className="text-sm text-accent-cool/80 mb-3">Why TripChoice</div>
              <h2 className="text-ink text-4xl md:text-5xl lg:text-6xl font-display font-extrabold leading-[1.05] mb-4">
                Travel that feels considered.
              </h2>
              <p className="text-slate text-lg leading-relaxed mb-6 max-w-xl mx-auto lg:mx-0">
                Human experts plan end‑to‑end itineraries with transparency and taste. You just show up.
              </p>

              {/* Feature badges */}
              <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 mb-8">
                <span className="inline-flex items-center gap-2 rounded-full border border-cloud/60 bg-surface px-3 py-2 text-ink text-sm shadow-e1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7"/></svg>
                  Curated stays & routes
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-cloud/60 bg-surface px-3 py-2 text-ink text-sm shadow-e1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/></svg>
                  Transparent pricing
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-cloud/60 bg-surface px-3 py-2 text-ink text-sm shadow-e1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
                  Human concierge
                </span>
              </div>

              {/* Enhanced Metrics */}
              <div className="grid grid-cols-3 gap-4 max-w-xl mx-auto lg:mx-0 mb-6">
                <div className="rounded-xl bg-surface border border-cloud/40 p-4 text-center shadow-e1 hover:shadow-e2 transition-shadow">
                  <div className="text-ink font-bold text-2xl">4.9/5</div>
                  <div className="text-slate text-xs mt-1">Avg. satisfaction</div>
                  <div className="text-accent-cool text-xs mt-1">★★★★★</div>
                </div>
                <div className="rounded-xl bg-surface border border-cloud/40 p-4 text-center shadow-e1 hover:shadow-e2 transition-shadow">
                  <div className="text-ink font-bold text-2xl">25k+</div>
                  <div className="text-slate text-xs mt-1">Trips planned</div>
                  <div className="text-accent-warm text-xs mt-1">Since 2020</div>
                </div>
                <div className="rounded-xl bg-surface border border-cloud/40 p-4 text-center shadow-e1 hover:shadow-e2 transition-shadow">
                  <div className="text-ink font-bold text-2xl">1.5h</div>
                  <div className="text-slate text-xs mt-1">Avg. response</div>
                  <div className="text-accent-cool text-xs mt-1">24/7 support</div>
                </div>
              </div>

              {/* Enhanced Testimonials */}
              <div className="space-y-6 mb-8">
                <div className="flex items-center justify-center lg:justify-start gap-4">
                  <Image src="https://source.unsplash.com/96x96/?mountains" alt="Satisfied TripChoice customer testimonial" width={48} height={48} className="h-12 w-12 rounded-full object-cover shadow-lg" unoptimized />
                  <div className="text-left">
                    <p className="text-ink text-base font-medium">“We just showed up and every day unfolded perfectly.”</p>
                    <p className="text-slate text-sm">Ananya S., honeymoon in Kashmir</p>
                  </div>
                </div>

                <div className="flex items-center justify-center lg:justify-start gap-4">
                  <Image src="https://source.unsplash.com/96x96/?beach" alt="Satisfied TripChoice customer testimonial" width={48} height={48} className="h-12 w-12 rounded-full object-cover shadow-lg" unoptimized />
                  <div className="text-left">
                    <p className="text-ink text-base font-medium">“From serene Anjuna beaches to lively Baga nightlife - pure magic!”</p>
                    <p className="text-slate text-sm">Rahul K., Goa North & South</p>
                  </div>
                </div>

                <div className="flex items-center justify-center lg:justify-start gap-4">
                  <Image src="https://source.unsplash.com/96x96/?city%20skyline" alt="Satisfied TripChoice customer testimonial" width={48} height={48} className="h-12 w-12 rounded-full object-cover shadow-lg" unoptimized />
                  <div className="text-left">
                    <p className="text-ink text-base font-medium">“Ultimate luxury experience! Worth every penny.”</p>
                    <p className="text-slate text-sm">Rajesh G., Dubai Luxury</p>
                  </div>
                </div>
              </div>

              <Magnetic>
                <div className="inline-block">
                  <Button asChild className="rounded-full bg-accent-warm hover:bg-accent-warm/90 text-white px-6 py-3">
                    <a href="/contact">Plan my trip</a>
                  </Button>
                </div>
              </Magnetic>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="container mx-auto px-4 relative">
        <div className="relative">
          <Reveal className="text-center mb-10">
            <div className="text-sm text-accent-cool/80 mb-2">FAQ</div>
            <h2 className="text-ink text-4xl md:text-5xl font-display font-semibold tracking-tight mb-2">Questions, answered</h2>
            <p className="text-slate max-w-2xl mx-auto">Short, honest answers to help you book faster.</p>
          </Reveal>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {faqs.map((f, i) => (
              <Reveal key={i} delay={i * 0.05}>
                <div className="rounded-2xl border border-cloud/20 bg-surface p-6 shadow-e1 hover:shadow-e2 transition-shadow">
                  <h3 className="text-ink font-semibold text-lg mb-2">{f.question}</h3>
                  <p className="text-slate leading-relaxed">{f.answer}</p>
                </div>
              </Reveal>
            ))}
          </div>
          <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateFAQStructuredData(faqs)) }} />
        </div>
      </section>

      {/* End homepage content */}
    </div>
    </main>
  )
}

export const metadata: Metadata = {
  title: 'TripChoice - Plan less. Travel more.',
  description: 'Curated travel packages at honest prices. Find your perfect getaway from Goa to Dubai.',
}



async function getFeaturedPackages(): Promise<Package[]> {
  try {
    const packages = await getPackages({ limit: 6 })
    return packages.length > 0 ? packages : []
  } catch (error) {
    console.warn('CMS not available, using fallback data:', error)
    return []
  }
}

async function getCurrentFlashSale(): Promise<FlashSale | null> {
  try {
    const flashSales = await getActiveFlashSales()
    return flashSales[0] || null
  } catch (error) {
    console.warn('CMS not available for flash sales:', error)
    return null
  }
}

export default async function HomePage() {
  const [packages, flashSale] = await Promise.all([
    getFeaturedPackages(),
    getCurrentFlashSale(),
  ])

  return (
    <PersonalizationProvider>
      <HomePageClient packages={packages} flashSale={flashSale} />
    </PersonalizationProvider>
  )
}
