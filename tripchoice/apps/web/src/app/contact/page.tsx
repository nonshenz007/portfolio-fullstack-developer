import { Metadata } from 'next'
import { ContactForm } from '@/components/ContactForm'
import { ConciergeCard } from '@/components/ConciergeCard'
import { MobileCTAFooter } from '@/components/MobileCTAFooter'
import { contactSchemas, injectJSONLD } from '@/lib/schema'

export const metadata: Metadata = {
  title: 'Contact | TripChoice',
  description: 'Talk to a Trip Concierge. Real humans. Honest advice. 10–6 IST.'
}

export default function ContactPage() {
  const jsonld = contactSchemas()

  return (
    <div className="min-h-screen bg-surface pt-16 md:pt-20">
      {/* Hero strip */}
      <section className="py-12 border-b border-cloud/20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="font-display text-4xl md:text-5xl font-extrabold tracking-tight text-ink">Talk to a Trip Concierge.</h1>
          <p className="text-slate text-base md:text-lg mt-2">Real humans. Honest advice. 10–6 IST.</p>
        </div>
      </section>

      {/* Body */}
      <section className="container mx-auto px-4 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          <div className="lg:col-span-2">
            <ContactForm />
          </div>
          <div>
            <ConciergeCard />
          </div>
        </div>
      </section>

      {/* Sticky mobile footer CTA */}
      <MobileCTAFooter />

      {/* JSON-LD */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: injectJSONLD(jsonld) }} />
    </div>
  )
}

