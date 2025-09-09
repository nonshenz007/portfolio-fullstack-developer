import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Contact | TripChoice',
  description: 'Get in touch with TripChoice via WhatsApp or email. We’re here to help plan your next trip.'
}

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-surface">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-accent-cool/10 via-surface to-accent-warm/10 py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="text-sm text-accent-cool/80 mb-2">Get in Touch</div>
          <h1 className="font-display text-5xl md:text-6xl font-semibold tracking-tight text-ink leading-[1.05] mb-4">
            Let's Plan Your Dream Trip
          </h1>
          <p className="text-slate text-lg leading-snug max-w-2xl mx-auto">
            Our travel experts are here to craft personalized experiences that match your vision, budget, and timeline.
          </p>
        </div>
      </section>

      <section className="container mx-auto px-4 py-16">
        {/* Contact Methods */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="rounded-xl border border-cloud/30 bg-surface p-8 shadow-e1 hover:shadow-e2 transition-shadow">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.465 3.488"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">WhatsApp Support</h3>
            <p className="text-slate mb-4">Instant quotes, quick questions, and real-time assistance</p>
            <a
              href="https://wa.me/919447003974"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-6 py-3 rounded-full bg-green-600 text-white hover:bg-green-700 font-semibold transition-colors"
            >
              +91 94470 03974
            </a>
          </div>

          <div className="rounded-xl border border-cloud/30 bg-surface p-8 shadow-e1 hover:shadow-e2 transition-shadow">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Email Support</h3>
            <p className="text-slate mb-4">Detailed inquiries, custom packages, and complex planning</p>
            <div className="space-y-2">
              <a href="mailto:hello@tripchoice.com" className="block text-accent-cool font-semibold hover:text-accent-cool/80">hello@tripchoice.com</a>
              <a href="mailto:support@tripchoice.com" className="block text-accent-cool font-semibold hover:text-accent-cool/80">support@tripchoice.com</a>
            </div>
          </div>

          <div className="rounded-xl border border-cloud/30 bg-surface p-8 shadow-e1 hover:shadow-e2 transition-shadow">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Office Hours</h3>
            <p className="text-slate mb-4">When our team is available to assist you</p>
            <div className="space-y-1">
              <p className="text-slate"><span className="font-medium">Mon–Sat:</span> 9:00 AM – 8:00 PM IST</p>
              <p className="text-slate"><span className="font-medium">Sunday:</span> 10:00 AM – 6:00 PM IST</p>
              <p className="text-slate"><span className="font-medium">Response:</span> Within 1.5 hours</p>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Meet Our Travel Expert</h2>
            <p className="text-slate text-lg max-w-2xl mx-auto">Our experienced travel consultant has personally visited 50+ countries and planned over 25,000 trips.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-1 gap-8 max-w-md mx-auto">
            <div className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-accent-cool to-accent-warm rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl font-bold text-white">A</span>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-2">Amal</h3>
              <p className="text-accent-cool font-medium mb-2">Lead Travel Consultant</p>
              <p className="text-slate text-sm">15+ years in luxury travel, specializes in international and domestic destinations</p>
            </div>
          </div>

          <div className="text-center mt-8">
            <p className="text-slate text-sm italic">Additional team members coming soon!</p>
          </div>
        </div>

        {/* Office Locations */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Visit Our Offices</h2>
            <p className="text-slate text-lg">Meet us in person for detailed trip planning and custom itineraries.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="rounded-xl border border-cloud/30 bg-surface p-8 shadow-e1">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-ink mb-2">Kozhikode Office</h3>
                  <p className="text-slate mb-2">MG Road, Near Mananchira Square, Kozhikode - 673001</p>
                  <p className="text-slate mb-2"><span className="font-medium">Phone:</span> +91 495 123 4567</p>
                  <p className="text-slate"><span className="font-medium">Hours:</span> Mon-Sat 9 AM - 7 PM</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-cloud/30 bg-surface p-8 shadow-e1">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-ink mb-2">Cochin Office</h3>
                  <p className="text-slate mb-2">MG Road, Near Dutch Cemetery, Kochi - 682035</p>
                  <p className="text-slate mb-2"><span className="font-medium">Phone:</span> +91 484 987 6543</p>
                  <p className="text-slate"><span className="font-medium">Hours:</span> Mon-Sat 9 AM - 7 PM</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center bg-gradient-to-r from-accent-cool/10 to-accent-warm/10 rounded-2xl p-8">
          <h2 className="text-2xl md:text-3xl font-display font-semibold text-ink mb-4">Ready to Start Planning?</h2>
          <p className="text-slate mb-6 max-w-xl mx-auto">Let's discuss your dream destination and create a personalized itinerary that exceeds your expectations.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/explore" className="inline-block px-8 py-4 rounded-full bg-accent-cool text-white hover:bg-accent-cool/90 font-semibold transition-colors">
              Explore Packages
            </Link>
            <a
              href="https://wa.me/919447003974"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-8 py-4 rounded-full bg-green-600 text-white hover:bg-green-700 font-semibold transition-colors"
            >
              Chat on WhatsApp
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
