import { Metadata } from 'next'
import { NewsletterSignup } from '@/components/newsletter-signup'

export const metadata: Metadata = {
  title: 'About | TripChoice',
  description: 'Learn about TripChoice — curated travel packages at honest prices, crafted by real travel experts who have personally visited 50+ countries.'
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-surface pt-16 md:pt-20">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-accent-cool/10 via-surface to-accent-warm/10 py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="text-sm text-accent-cool/80 mb-2">Who We Are</div>
          <h1 className="font-display text-5xl md:text-6xl font-semibold tracking-tight text-ink leading-[1.05] mb-4">
            Your Trusted Travel Partner
          </h1>
          <p className="text-slate text-lg leading-snug max-w-3xl mx-auto">
            Founded with a simple belief: travel should be effortless, memorable, and transformative.
            We've personally visited 50+ countries and crafted 25,000+ dream vacations.
          </p>
        </div>
      </section>

      {/* Our Story */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Our Story</h2>
            <p className="text-slate text-lg">How TripChoice became India's most trusted travel curator</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-accent-cool/10 to-accent-warm/10 p-6 rounded-2xl">
                <h3 className="text-xl font-semibold text-ink mb-3">The Beginning</h3>
                <p className="text-slate leading-relaxed">
                  TripChoice started as a passion project when our founder Amal realized that great travel experiences
                  were often hidden behind complicated booking processes and hidden costs. Having traveled extensively
                  across the globe, Amal wanted to create a platform that makes premium travel accessible to everyone.
                </p>
              </div>

              <div className="bg-gradient-to-r from-accent-warm/10 to-orange-100/10 p-6 rounded-2xl">
                <h3 className="text-xl font-semibold text-ink mb-3">Our Mission</h3>
                <p className="text-slate leading-relaxed">
                  To democratize exceptional travel experiences by combining expert curation with transparent pricing.
                  We believe every traveler deserves a trip that's not just a vacation, but a transformative journey.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-gradient-to-r from-blue-100/10 to-accent-cool/10 p-6 rounded-2xl">
                <h3 className="text-xl font-semibold text-ink mb-3">Our Vision</h3>
                <p className="text-slate leading-relaxed">
                  To be India's most trusted travel partner, known for creating life-changing experiences that exceed
                  expectations. We envision a world where travel planning is effortless and every journey creates lasting memories.
                </p>
              </div>

              <div className="bg-gradient-to-r from-green-100/10 to-accent-warm/10 p-6 rounded-2xl">
                <h3 className="text-xl font-semibold text-ink mb-3">Our Values</h3>
                <ul className="text-slate leading-relaxed space-y-2">
                  <li><strong className="text-ink">Transparency:</strong> Clear pricing, honest communication</li>
                  <li><strong className="text-ink">Excellence:</strong> Only the best destinations and experiences</li>
                  <li><strong className="text-ink">Personalization:</strong> Every trip tailored to your preferences</li>
                  <li><strong className="text-ink">Sustainability:</strong> Responsible tourism practices</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Expertise */}
      <section className="bg-gradient-to-r from-slate-50 to-white py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Why Choose TripChoice?</h2>
            <p className="text-slate text-lg max-w-2xl mx-auto">What sets us apart in the world of travel</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-e1 border border-cloud/20">
              <div className="w-12 h-12 bg-accent-cool/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent-cool" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-3">Expert Curation</h3>
              <p className="text-slate leading-relaxed">
                Every package is personally researched and experienced by our travel experts.
                No generic itineraries — only authentic, memorable experiences.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-e1 border border-cloud/20">
              <div className="w-12 h-12 bg-accent-warm/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent-warm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-3">Transparent Pricing</h3>
              <p className="text-slate leading-relaxed">
                Clear "From ₹" pricing with all major components included. No hidden fees,
                no surprises — just honest, competitive pricing.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-e1 border border-cloud/20">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-3">24/7 Support</h3>
              <p className="text-slate leading-relaxed">
                Round-the-clock assistance via WhatsApp, email, and phone. Our experts are
                always just a message away to ensure your trip runs smoothly.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-e1 border border-cloud/20">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-3">Personalized Service</h3>
              <p className="text-slate leading-relaxed">
                Every recommendation is tailored to your preferences, budget, and travel style.
                We're not just booking trips — we're crafting experiences.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-e1 border border-cloud/20">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-3">Quality Guarantee</h3>
              <p className="text-slate leading-relaxed">
                We stand behind every trip we plan. If anything falls short of your expectations,
                we'll work tirelessly to make it right — no questions asked.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-e1 border border-cloud/20">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-ink mb-3">Global Network</h3>
              <p className="text-slate leading-relaxed">
                Direct partnerships with hotels, airlines, and local operators worldwide.
                This means better rates, exclusive experiences, and insider access for you.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Meet Our Expert */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Meet Our Travel Expert</h2>
          <p className="text-slate text-lg max-w-2xl mx-auto">The heart and soul of TripChoice</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-e1 p-8 border border-cloud/20">
            <div className="flex flex-col md:flex-row items-center gap-8">
              <div className="w-32 h-32 bg-gradient-to-br from-accent-cool to-accent-warm rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-3xl font-bold text-white">A</span>
              </div>

              <div className="flex-1 text-center md:text-left">
                <h3 className="text-2xl font-semibold text-ink mb-2">Amal</h3>
                <p className="text-accent-cool font-medium mb-4">Lead Travel Consultant & Founder</p>
                <p className="text-slate leading-relaxed mb-4">
                  With over 15 years in luxury travel and having personally visited 50+ countries,
                  Amal brings unparalleled expertise to every TripChoice experience. Her passion for
                  creating transformative journeys has helped thousands of travelers discover their
                  dream destinations.
                </p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-accent-cool">50+</div>
                    <div className="text-sm text-slate">Countries Visited</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-accent-cool">25k+</div>
                    <div className="text-sm text-slate">Trips Planned</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-accent-cool">15+</div>
                    <div className="text-sm text-slate">Years Experience</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-accent-cool">4.9/5</div>
                    <div className="text-sm text-slate">Customer Rating</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Impact */}
      <section className="bg-gradient-to-r from-accent-cool/5 to-accent-warm/5 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Our Impact</h2>
            <p className="text-slate text-lg">Numbers that tell our story</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-accent-cool mb-2">25,000+</div>
              <div className="text-slate">Dream Trips Created</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-accent-warm mb-2">50+</div>
              <div className="text-slate">Countries Explored</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">4.9/5</div>
              <div className="text-slate">Average Rating</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-green-600 mb-2">1.5h</div>
              <div className="text-slate">Avg Response Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Promise */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-6">Our Promise to You</h2>
          <blockquote className="border-l-4 border-accent-cool pl-8 text-xl text-ink/90 leading-relaxed italic mb-8">
            "Travel should be about creating memories, not managing logistics. We promise to handle every detail
            with care, transparency, and expertise so you can focus on what matters most — experiencing the world
            and creating stories that will last a lifetime."
          </blockquote>
          <p className="text-slate text-lg">- Amal, Founder & Lead Travel Consultant</p>
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          <NewsletterSignup />
        </div>
      </section>

      {/* Call to Action */}
      <section className="bg-gradient-to-r from-accent-cool/10 to-accent-warm/10 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink mb-4">Ready to Start Your Journey?</h2>
          <p className="text-slate text-lg mb-8 max-w-2xl mx-auto">
            Let's discuss your dream destination and create a personalized travel experience that exceeds your expectations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://wa.me/919447003974"
              className="inline-block px-8 py-4 rounded-full bg-green-600 text-white hover:bg-green-700 font-semibold transition-colors"
            >
              Chat on WhatsApp
            </a>
            <a
              href="/explore"
              className="inline-block px-8 py-4 rounded-full bg-accent-cool text-white hover:bg-accent-cool/90 font-semibold transition-colors"
            >
              Explore Destinations
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
