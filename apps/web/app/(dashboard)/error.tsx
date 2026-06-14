'use client'

import { useEffect } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('[Route Error]', error.message, error.digest)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background-dark p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full text-center space-y-6"
      >
        <div className="w-20 h-20 rounded-2xl bg-accent-error/10 flex items-center justify-center mx-auto">
          <AlertTriangle size={40} className="text-accent-error" />
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl font-display font-bold text-text-primary">
            Something went wrong
          </h1>
          <p className="text-text-secondary text-sm">
            An unexpected error occurred. This has been logged and we will look into it.
          </p>
        </div>

        {error.digest && (
          <p className="text-xs text-text-tertiary font-mono">
            Error ID: {error.digest}
          </p>
        )}

        <div className="flex items-center justify-center gap-3">
          <button
            onClick={reset}
            className="btn btn-primary gap-2"
          >
            <RefreshCw size={16} />
            Try again
          </button>
          <Link
            href="/dashboard"
            className="btn btn-secondary gap-2"
          >
            <Home size={16} />
            Go to Dashboard
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
