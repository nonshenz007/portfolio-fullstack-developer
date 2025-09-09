'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Star, MessageCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getReviews } from '@/lib/cms'
import { Button } from '@/components/ui/button'

interface ReviewsStubProps {
  packageId: string
  rating: number
  count: number
}

export function ReviewsStub({ packageId, rating, count }: ReviewsStubProps) {
  const [showAll, setShowAll] = useState(false)

  const { data: reviews = [], isLoading } = useQuery({
    queryKey: ['reviews', packageId],
    queryFn: () => getReviews(packageId),
    enabled: !!packageId,
  })

  const displayedReviews = showAll ? reviews : reviews.slice(0, 3)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-h3 font-semibold text-ink">Guest Reviews</h3>
        <div className="space-y-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="border border-cloud/20 rounded-xl p-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-cloud/20 rounded-full animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-cloud/20 rounded animate-pulse w-1/3" />
                  <div className="h-4 bg-cloud/20 rounded animate-pulse" />
                  <div className="h-4 bg-cloud/20 rounded animate-pulse w-2/3" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-h3 font-semibold text-ink">Guest Reviews</h3>
        <div className="flex items-center gap-2 bg-cloud/10 px-4 py-2 rounded-xl">
          <Star className="h-4 w-4 fill-accent-warm text-accent-warm" />
          <span className="font-bold text-ink">{rating.toFixed(1)}</span>
          <span className="text-slate text-sm">({count} reviews)</span>
        </div>
      </div>

      {reviews.length === 0 ? (
        <div className="text-center py-12 bg-cloud/5 rounded-xl">
          <MessageCircle className="h-12 w-12 text-cloud mx-auto mb-4" />
          <h4 className="font-semibold text-ink mb-2">No reviews yet</h4>
          <p className="text-slate">Be the first to share your experience!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {displayedReviews.map((review) => (
            <div key={review.id} className="border border-cloud/20 rounded-xl p-6 hover:border-cloud/40 transition-colors duration-200">
              <div className="flex items-start gap-4">
                {/* Avatar */}
                <div className="w-10 h-10 bg-gradient-to-br from-accent-cool to-accent-warm rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="font-bold text-white text-sm">
                    {review.author_name.charAt(0).toUpperCase()}
                  </span>
                </div>

                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h5 className="font-semibold text-ink">{review.author_name}</h5>
                      <p className="text-xs text-slate">{review.source}</p>
                    </div>
                    <div className="flex items-center">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={`h-4 w-4 ${
                            i < review.rating
                              ? 'fill-accent-warm text-accent-warm'
                              : 'text-cloud'
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Review Text */}
                  <p className="text-slate leading-relaxed">{review.text}</p>

                  {/* Media */}
                  {review.media && (
                    <div className="mt-4">
                      <Image
                        src={review.media}
                        alt="Review photo"
                        width={96}
                        height={96}
                        className="w-24 h-24 object-cover rounded-lg"
                        sizes="96px"
                        unoptimized={true}
                        referrerPolicy="no-referrer"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Show More/Less Button */}
          {reviews.length > 3 && (
            <div className="text-center">
              <Button
                variant="outline"
                onClick={() => setShowAll(!showAll)}
                className="border-cloud/30 hover:border-accent-cool/50"
              >
                {showAll ? 'Show less' : `Show all ${reviews.length} reviews`}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
