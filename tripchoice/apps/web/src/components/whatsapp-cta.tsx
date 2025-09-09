'use client'

import { useEffect, useState } from 'react'
import { MessageCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { analytics } from '@/lib/analytics'
import { Package } from '@/types'

interface WhatsAppCTAProps {
  pkg: Package
}

export function WhatsAppCTA({ pkg }: WhatsAppCTAProps) {
  const router = useRouter()
  const [enquiryData, setEnquiryData] = useState<any>(null)

  // Listen for enquiry events from PriceBox
  useEffect(() => {
    const handleEnquiry = (event: CustomEvent) => {
      setEnquiryData(event.detail)
      handleWhatsAppClick(event.detail)
    }

    window.addEventListener('whatsapp-enquiry', handleEnquiry as EventListener)
    return () => window.removeEventListener('whatsapp-enquiry', handleEnquiry as EventListener)
  }, [])

  const buildWhatsAppURL = (data: any) => {
    const whatsappNumber = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || '919447003974'
    
    // Build message text
    const variant = data.selectedVariant ? ` (${data.selectedVariant.type})` : ''
    const dates = data.date ? `, dates ${new Date(data.date).toLocaleDateString()}` : ''
    const pax = data.pax ? `, pax ${data.pax}` : ''
    
    // Get UTM source from URL search params
    const utmSource = typeof window !== 'undefined' && window.location.search
      ? new URLSearchParams(window.location.search).get('utm_source') || 'website'
      : 'website'

    const message = `${pkg.title}${variant}${dates}${pax} — from ${utmSource}`
    
    // Build URL with UTM parameters
    const utmParams = new URLSearchParams({
      utm_source: utmSource || 'website',
      utm_medium: 'whatsapp',
      utm_campaign: 'package_enquiry',
      utm_content: pkg.slug
    })

    return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}&${utmParams.toString()}`
  }

  const handleWhatsAppClick = (data: any) => {
    const whatsappUrl = buildWhatsAppURL(data)
    
    // Track analytics
    analytics.trackWhatsAppClick(pkg.slug, {
      variant: data.selectedVariant?.id,
      date: data.date,
      pax: data.pax,
      utm_source: 'website'
    })

    // Open WhatsApp
    window.open(whatsappUrl, '_blank')
  }

  const handleDirectClick = () => {
    const defaultData = {
      pkg,
      selectedVariant: null,
      date: new Date().toISOString().split('T')[0],
      pax: 2,
      originCity: 'Mumbai'
    }
    handleWhatsAppClick(defaultData)
  }

  return (
    <>
      {/* Mobile Sticky Bottom Bar */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-surface/95 backdrop-blur-xl border-t border-cloud/20 p-4 z-40">
        <Button
          onClick={handleDirectClick}
          className="w-full bg-accent-warm hover:bg-accent-warm/90 text-white font-semibold py-4 text-lg shadow-e2 focus:outline-none focus:ring-2 focus:ring-accent-cool"
        >
          <MessageCircle className="h-5 w-5 mr-2" />
          Enquire on WhatsApp
        </Button>
      </div>

      {/* Add bottom padding to prevent content overlap on mobile */}
      <div className="lg:hidden h-20" />
    </>
  )
}