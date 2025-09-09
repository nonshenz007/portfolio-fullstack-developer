'use client'

import { useState } from 'react'
import { Share2, Facebook, Twitter, Instagram, Copy, Check, Heart, Bookmark } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SocialShareProps {
  url?: string
  title?: string
  description?: string
  className?: string
}

export function SocialShare({
  url = typeof window !== 'undefined' ? window.location.href : '',
  title = 'Check out this amazing travel destination!',
  description = 'Discover incredible travel packages with TripChoice',
  className
}: SocialShareProps) {
  const [copied, setCopied] = useState(false)
  const [liked, setLiked] = useState(false)
  const [saved, setSaved] = useState(false)

  const shareUrls = {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
    twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
    whatsapp: `https://wa.me/?text=${encodeURIComponent(`${title} ${url}`)}`
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const openShare = (platform: keyof typeof shareUrls) => {
    window.open(shareUrls[platform], '_blank', 'width=600,height=400')
  }

  return (
    <div className={cn("flex items-center space-x-3", className)}>
      {/* Like Button */}
      <button
        onClick={() => setLiked(!liked)}
        className={cn(
          "flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-200 hover:scale-105",
          liked
            ? "bg-red-50 text-red-600 border border-red-200"
            : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
        )}
      >
        <Heart className={cn("w-4 h-4", liked && "fill-current")} />
        <span className="text-sm font-medium">{liked ? 'Liked' : 'Like'}</span>
      </button>

      {/* Save Button */}
      <button
        onClick={() => setSaved(!saved)}
        className={cn(
          "flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-200 hover:scale-105",
          saved
            ? "bg-blue-50 text-blue-600 border border-blue-200"
            : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
        )}
      >
        <Bookmark className={cn("w-4 h-4", saved && "fill-current")} />
        <span className="text-sm font-medium">{saved ? 'Saved' : 'Save'}</span>
      </button>

      {/* Share Button */}
      <div className="relative">
        <button
          className="flex items-center space-x-2 px-4 py-2 rounded-full bg-accent-cool text-white hover:bg-accent-cool/90 transition-all duration-200 hover:scale-105"
          onClick={() => {
            // Toggle share menu - for now just open WhatsApp
            openShare('whatsapp')
          }}
        >
          <Share2 className="w-4 h-4" />
          <span className="text-sm font-medium">Share</span>
        </button>
      </div>

      {/* Copy Link Button */}
      <button
        onClick={copyToClipboard}
        className="flex items-center space-x-2 px-4 py-2 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200 transition-all duration-200 hover:scale-105"
      >
        {copied ? (
          <>
            <Check className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-600">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="w-4 h-4" />
            <span className="text-sm font-medium">Copy Link</span>
          </>
        )}
      </button>
    </div>
  )
}
