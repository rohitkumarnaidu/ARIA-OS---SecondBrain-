'use client'

import { useEffect } from 'react'
import * as Sentry from '@sentry/nextjs'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    Sentry.captureException(error)
  }, [error])

  return (
    <html lang="en">
      <body className="bg-background-dark text-text-primary">
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="max-w-md w-full text-center space-y-6">
            <h1 className="text-2xl font-display font-bold">Something went wrong</h1>
            <p className="text-text-secondary text-sm">A critical error occurred. Please try again.</p>
            <button
              onClick={reset}
              className="inline-flex items-center gap-2 bg-accent-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-accent-primaryHover transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
