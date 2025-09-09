'use client'

import { useState } from 'react'
import { Mail, Check, X, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

export function NewsletterSignup() {
  const [email, setEmail] = useState('')
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || isLoading) return

    setIsLoading(true)

    // Simulate API call
    setTimeout(() => {
      setIsSubscribed(true)
      setIsLoading(false)
      setShowModal(true)

      // Hide success modal after 3 seconds
      setTimeout(() => {
        setShowModal(false)
        setEmail('')
      }, 3000)
    }, 1500)
  }

  return (
    <>
      <div className="bg-gradient-to-r from-accent-cool/10 via-accent-warm/5 to-accent-cool/10 rounded-2xl p-8 border border-accent-cool/20">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-accent-cool/10 rounded-full mb-4">
            <Mail className="w-6 h-6 text-accent-cool" />
          </div>

          <h3 className="text-xl font-semibold text-ink mb-2">
            Get Travel Inspiration
          </h3>
          <p className="text-slate mb-6 max-w-md mx-auto">
            Join 15,000+ travelers who receive exclusive deals, destination guides, and travel tips directly in their inbox.
          </p>

          <form onSubmit={handleSubscribe} className="max-w-md mx-auto">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cool focus:border-transparent text-sm"
                  required
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Sparkles className="w-4 h-4 text-slate-400" />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || !email}
                className={cn(
                  "px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2",
                  isLoading
                    ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                    : "bg-accent-cool hover:bg-accent-cool/90 text-white hover:shadow-lg transform hover:scale-105"
                )}
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Joining...</span>
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4" />
                    <span>Join Now</span>
                  </>
                )}
              </button>
            </div>

            <p className="text-xs text-slate-500 mt-3 text-center">
              No spam, unsubscribe anytime. We respect your privacy.
            </p>
          </form>
        </div>
      </div>

      {/* Success Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-in fade-in duration-300">
          <div className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center shadow-2xl animate-in zoom-in-95 duration-300">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <Check className="w-8 h-8 text-green-600" />
            </div>

            <h3 className="text-xl font-semibold text-ink mb-2">
              Welcome to TripChoice! 🎉
            </h3>

            <p className="text-slate mb-4">
              Thank you for subscribing! Check your inbox for your welcome gift - exclusive travel deals worth ₹5,000.
            </p>

            <div className="bg-gradient-to-r from-accent-cool/10 to-accent-warm/10 rounded-lg p-4 mb-4">
              <div className="text-sm font-medium text-ink">What you'll receive:</div>
              <ul className="text-sm text-slate mt-2 space-y-1">
                <li>• Weekly destination spotlights</li>
                <li>• Exclusive flash sale alerts</li>
                <li>• Travel planning tips & guides</li>
                <li>• Special member-only discounts</li>
              </ul>
            </div>

            <button
              onClick={() => setShowModal(false)}
              className="w-full bg-accent-cool hover:bg-accent-cool/90 text-white py-3 px-6 rounded-lg font-medium transition-colors"
            >
              Start Exploring
            </button>
          </div>
        </div>
      )}
    </>
  )
}
