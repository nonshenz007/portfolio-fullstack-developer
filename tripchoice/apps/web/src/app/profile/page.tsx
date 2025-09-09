'use client'

import { useRouter } from 'next/navigation'
import { Header } from '@/components/header'

export default function ProfilePage() {
  const router = useRouter()

  return (
    <>
      <Header />
      <main id="main-content" className="pt-20">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold text-gray-900 mb-8">Your Profile</h1>
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <div className="text-6xl mb-4">👤</div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Profile Coming Soon</h2>
              <p className="text-gray-600 mb-6">
                Manage your travel preferences, saved trips, and account settings.
              </p>
              <button
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
                onClick={() => router.back()}
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}