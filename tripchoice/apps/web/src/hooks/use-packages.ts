import { useQuery } from '@tanstack/react-query'
import { getPackages, getPackage, getItineraryDays, getVariants, getReviews, PackageFilters } from '@/lib/cms'
import { Package, ItineraryDay, Variant, Review } from '@/types'

export function usePackages(filters?: PackageFilters) {
  return useQuery({
    queryKey: ['packages', filters],
    queryFn: () => getPackages(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function usePackage(slug: string) {
  return useQuery({
    queryKey: ['package', slug],
    queryFn: () => getPackage(slug),
    enabled: !!slug,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export function usePackageDetails(slug: string) {
  const packageQuery = usePackage(slug)

  const itineraryQuery = useQuery({
    queryKey: ['itinerary', packageQuery.data?.id],
    queryFn: () => packageQuery.data?.id ? getItineraryDays(packageQuery.data.id) : Promise.resolve([]),
    enabled: !!packageQuery.data?.id,
    staleTime: 10 * 60 * 1000,
  })

  const variantsQuery = useQuery({
    queryKey: ['variants', packageQuery.data?.id],
    queryFn: () => packageQuery.data?.id ? getVariants(packageQuery.data.id) : Promise.resolve([]),
    enabled: !!packageQuery.data?.id,
    staleTime: 10 * 60 * 1000,
  })

  const reviewsQuery = useQuery({
    queryKey: ['reviews', packageQuery.data?.id],
    queryFn: () => packageQuery.data?.id ? getReviews(packageQuery.data.id) : Promise.resolve([]),
    enabled: !!packageQuery.data?.id,
    staleTime: 15 * 60 * 1000, // 15 minutes for reviews
  })

  return {
    package: packageQuery.data,
    itinerary: itineraryQuery.data || [],
    variants: variantsQuery.data || [],
    reviews: reviewsQuery.data || [],
    isLoading: packageQuery.isLoading || itineraryQuery.isLoading || variantsQuery.isLoading || reviewsQuery.isLoading,
    error: packageQuery.error || itineraryQuery.error || variantsQuery.error || reviewsQuery.error,
  }
}

export function useFeaturedPackages() {
  return usePackages({ limit: 6 })
}

export function useWeekendPackages() {
  return usePackages({
    themes: ['Weekend'],
    limit: 3
  })
}

export function useInternationalPackages() {
  return usePackages({
    domestic: 'international',
    limit: 3
  })
}
