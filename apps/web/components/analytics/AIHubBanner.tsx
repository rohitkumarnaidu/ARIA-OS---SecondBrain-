'use client'

import { useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { Button } from '@/components/ui/Button'

interface AIHubBannerProps {
  insight?: string
}

export function AIHubBanner({ insight }: AIHubBannerProps) {
  const router = useRouter()

  const handleViewAnalysis = useCallback(() => {
    router.push('/chat')
  }, [router])

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-accent-primary/20 bg-gradient-to-br from-accent-primary/10 via-accent-primary/5 to-background-card"
    >
      <div className="absolute inset-0 bg-grid opacity-30" aria-hidden="true" />

      <div className="absolute top-0 right-0 w-48 h-48 bg-accent-primary/15 rounded-full blur-3xl -translate-y-1/4 translate-x-1/4" aria-hidden="true" />

      <div className="relative p-5 md:p-6 flex items-center justify-between gap-4">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-neon p-0.5 shrink-0">
            <div className="w-full h-full rounded-xl bg-background-card flex items-center justify-center">
              <Sparkles size={18} className="text-white" />
            </div>
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-display font-semibold text-text-primary mb-1">
              AI Intelligence Hub
            </h3>
            <p className="text-xs text-text-secondary leading-relaxed line-clamp-2">
              {insight || 'Your weekly performance is up 12%. Keep the momentum going with focused deep work sessions.'}
            </p>
          </div>
        </div>

        <Button
          onClick={handleViewAnalysis}
          variant="primary"
          className={cn(
            'text-xs gap-1.5 shrink-0',
            'animate-shimmer',
          )}
        >
          View Full Analysis
          <ArrowRight size={14} />
        </Button>
      </div>
    </motion.div>
  )
}
