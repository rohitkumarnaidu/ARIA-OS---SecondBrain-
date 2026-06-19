'use client'

import { useEffect } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { createLogger } from '@/lib/utils/logger'

const log = createLogger('route-error')

interface ModuleErrorProps {
  error: Error & { digest?: string }
  reset: () => void
  name?: string
}

export function ModuleError({ error, reset, name = 'page' }: ModuleErrorProps) {
  useEffect(() => {
    log.error(`Route error in ${name}`, { message: error.message, digest: error.digest })
  }, [error, name])

  return (
    <div className="min-h-[50vh] flex items-center justify-center p-4" role="alert">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full text-center space-y-6"
      >
        <div className="w-16 h-16 rounded-2xl bg-accent-error/10 flex items-center justify-center mx-auto">
          <AlertTriangle size={32} className="text-accent-error" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-display font-bold text-text-primary">
            Failed to load {name}
          </h1>
          <p className="text-text-secondary text-sm">
            An unexpected error occurred. This has been logged.
          </p>
        </div>
        {error.digest && (
          <p className="text-xs text-text-tertiary font-mono">Error ID: {error.digest}</p>
        )}
        <div className="flex items-center justify-center gap-3">
          <Button onClick={reset} variant="primary">
            <RefreshCw size={16} /> Try again
          </Button>
          <Button asChild variant="secondary">
            <Link href="/dashboard">
              <Home size={16} /> Dashboard
            </Link>
          </Button>
        </div>
      </motion.div>
    </div>
  )
}
