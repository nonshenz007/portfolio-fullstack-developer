import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Documentation | TripChoice',
  description: 'Complete guide to using TripChoice - your trusted travel partner for curated travel experiences.'
}

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-surface pt-16 md:pt-20">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-accent-cool/10 via-surface to-accent-warm/10 py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="text-sm text-accent-cool/80 mb-2">Documentation</div>
          <h1 className="font-display text-5xl md:text-6xl font-semibold tracking-tight text-ink leading-[1.05] mb-4">
            Travel Made Simple
          </h1>
          <p className="text-slate text-lg leading-snug max-w-3xl mx-auto">
            Everything you need to know about planning your perfect trip with TripChoice
          </p>
        </div>
      </section>

      {/* Quick Links */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            href="/docs/getting-started"
            className="group bg-white rounded-xl p-6 shadow-e1 border border-cloud/20 hover:shadow-e2 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 bg-accent-cool/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-accent-cool/20 transition-colors">
              <svg className="w-6 h-6 text-accent-cool" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Getting Started</h3>
            <p className="text-slate leading-relaxed">Learn the basics of planning your trip and making the most of TripChoice</p>
          </Link>

          <Link
            href="/docs/packages"
            className="group bg-white rounded-xl p-6 shadow-e1 border border-cloud/20 hover:shadow-e2 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 bg-accent-warm/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-accent-warm/20 transition-colors">
              <svg className="w-6 h-6 text-accent-warm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Travel Packages</h3>
            <p className="text-slate leading-relaxed">Explore our curated packages and understand what's included</p>
          </Link>

          <Link
            href="/docs/booking"
            className="group bg-white rounded-xl p-6 shadow-e1 border border-cloud/20 hover:shadow-e2 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Booking Process</h3>
            <p className="text-slate leading-relaxed">Step-by-step guide to booking your perfect travel experience</p>
          </Link>

          <Link
            href="/docs/payment"
            className="group bg-white rounded-xl p-6 shadow-e1 border border-cloud/20 hover:shadow-e2 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Payment & Pricing</h3>
            <p className="text-slate leading-relaxed">Understand our transparent pricing and payment options</p>
          </Link>

          <Link
            href="/docs/support"
            className="group bg-white rounded-xl p-6 shadow-e1 border border-cloud/20 hover:shadow-e2 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Support & FAQ</h3>
            <p className="text-slate leading-relaxed">Get help with common questions and contact our support team</p>
          </Link>

          <Link
            href="/docs/safety"
            className="group bg-white rounded-xl p-6 shadow-e1 border border-cloud/20 hover:shadow-e2 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-orange-200 transition-colors">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-ink mb-2">Travel Safety</h3>
            <p className="text-slate leading-relaxed">Important information about travel safety and our commitments</p>
          </Link>
        </div>
      </section>

      {/* Popular Topics */}
      <section className="bg-gradient-to-r from-slate-50 to-white py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Popular Topics</h2>
            <p className="text-slate text-lg max-w-2xl mx-auto">Most frequently asked questions and helpful guides</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-ink">Planning Your Trip</h3>
              <ul className="space-y-3">
                <li>
                  <Link href="/docs/getting-started#choosing-destination" className="text-slate hover:text-accent-cool transition-colors">
                    How to choose the right destination for your trip
                  </Link>
                </li>
                <li>
                  <Link href="/docs/packages#budget-planning" className="text-slate hover:text-accent-cool transition-colors">
                    Budget planning and cost breakdown
                  </Link>
                </li>
                <li>
                  <Link href="/docs/packages#group-sizes" className="text-slate hover:text-accent-cool transition-colors">
                    Understanding group sizes and pricing
                  </Link>
                </li>
                <li>
                  <Link href="/docs/booking#customization" className="text-slate hover:text-accent-cool transition-colors">
                    Customizing your travel package
                  </Link>
                </li>
              </ul>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-ink">During Your Trip</h3>
              <ul className="space-y-3">
                <li>
                  <Link href="/docs/support#emergency" className="text-slate hover:text-accent-cool transition-colors">
                    Emergency contact information
                  </Link>
                </li>
                <li>
                  <Link href="/docs/support#local-support" className="text-slate hover:text-accent-cool transition-colors">
                    24/7 local support and assistance
                  </Link>
                </li>
                <li>
                  <Link href="/docs/safety#health-safety" className="text-slate hover:text-accent-cool transition-colors">
                    Health and safety guidelines
                  </Link>
                </li>
                <li>
                  <Link href="/docs/support#changes" className="text-slate hover:text-accent-cool transition-colors">
                    Making changes during your trip
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Support */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-6">Still Need Help?</h2>
          <p className="text-slate text-lg mb-8 max-w-2xl mx-auto">
            Can't find what you're looking for? Our travel experts are here to help you plan the perfect trip.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://wa.me/919447003974"
              className="inline-block px-8 py-4 rounded-full bg-green-600 text-white hover:bg-green-700 font-semibold transition-colors"
            >
              Chat on WhatsApp
            </a>
            <a
              href="/contact"
              className="inline-block px-8 py-4 rounded-full bg-accent-cool text-white hover:bg-accent-cool/90 font-semibold transition-colors"
            >
              Contact Support
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
