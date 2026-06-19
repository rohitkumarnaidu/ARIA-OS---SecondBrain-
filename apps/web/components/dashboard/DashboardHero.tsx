'use client'

import { useMemo } from 'react'
import { format, isBefore, isAfter, setHours } from 'date-fns'
import { Sparkles, Brain } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface DashboardHeroProps {
  userName?: string
}

export function DashboardHero({ userName = 'there' }: DashboardHeroProps) {
  const greeting = useMemo(() => {
    const now = new Date()
    if (isBefore(now, setHours(now, 12)) && isAfter(now, setHours(now, 5))) return 'Good morning'
    if (isBefore(now, setHours(now, 14)) && isAfter(now, setHours(now, 12))) return 'Good afternoon'
    if (isBefore(now, setHours(now, 17)) && isAfter(now, setHours(now, 14))) return 'Good afternoon'
    return 'Good evening'
  }, [])

  const today = useMemo(() => format(new Date(), 'EEEE, MMMM d'), [])

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-background-card via-background-elevated to-background-card border border-border">
      <div className="absolute inset-0 bg-grid opacity-50" aria-hidden="true" />
      <div className="relative p-6 md:p-8">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2"
            >
              <Sparkles size={16} className="text-accent-neon" />
              <time
                dateTime={format(new Date(), 'yyyy-MM-dd')}
                className="text-xs font-medium text-text-tertiary tracking-wider uppercase"
              >
                {today}
              </time>
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-3xl md:text-4xl font-display font-bold"
            >
              <span className="text-gradient">{greeting}</span>
              <span className="text-text-primary">, {userName}</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-text-secondary max-w-md"
            >
              Your AI-powered productivity command center. Let&apos;s make today count.
            </motion.p>
          </div>

          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="hidden md:block relative"
            aria-label="ARIA avatar"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-primary to-accent-neon p-0.5">
              <div className="w-full h-full rounded-2xl bg-background-card flex items-center justify-center">
                <Brain size={28} className="text-accent-primary" />
              </div>
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-accent-neon rounded-full animate-pulse" aria-hidden="true" />
          </motion.div>
        </div>
      </div>
    </div>
  )
}
