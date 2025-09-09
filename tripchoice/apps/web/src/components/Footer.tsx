"use client"

import Link from 'next/link'
import { Phone, Mail, MessageCircle } from 'lucide-react'

export function Footer() {
  return (
    <footer className="bg-surface border-t border-cloud/10 py-12 md:py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xl md:text-2xl font-display font-bold tracking-tight text-ink">TripChoice</span>
            </div>
            <p className="text-slate text-sm leading-relaxed max-w-md">
              Curated travel packages at honest prices. Find your perfect getaway with transparent pricing and human support.
            </p>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-small text-slate mb-4">Contact</h3>
            <div className="space-y-3">
              <a
                href="tel:+919447003974"
                className="flex items-center gap-3 text-slate hover:text-ink transition-colors text-sm"
              >
                <Phone className="h-4 w-4" strokeWidth={1.5} />
                +91 94470 03974
              </a>
              <a
                href="mailto:hello@tripchoice.com"
                className="flex items-center gap-3 text-slate hover:text-ink transition-colors text-sm"
              >
                <Mail className="h-4 w-4" strokeWidth={1.5} />
                hello@tripchoice.com
              </a>
              <a
                href="https://wa.me/919447003974"
                className="flex items-center gap-3 text-slate hover:text-ink transition-colors text-sm"
                target="_blank"
                rel="noopener noreferrer"
              >
                <MessageCircle className="h-4 w-4" strokeWidth={1.5} />
                WhatsApp
              </a>
            </div>
          </div>

          {/* Links */}
          <div>
            <h3 className="font-semibold text-small text-slate mb-4">Company</h3>
            <div className="space-y-3">
              <Link
                href="/about"
                className="block text-slate hover:text-ink transition-colors text-sm"
              >
                About
              </Link>
              <Link
                href="/contact"
                className="block text-slate hover:text-ink transition-colors text-sm"
              >
                Contact
              </Link>
              <Link
                href="/policies"
                className="block text-slate hover:text-ink transition-colors text-sm"
              >
                Policies
              </Link>
              <Link
                href="/credits"
                className="block text-slate hover:text-ink transition-colors text-sm"
              >
                Image Credits
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-cloud/10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-cloud text-meta">
              © 2024 TripChoice. All rights reserved.
            </p>
            <p className="text-cloud text-meta">
              Made with ❤️ for travelers
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
