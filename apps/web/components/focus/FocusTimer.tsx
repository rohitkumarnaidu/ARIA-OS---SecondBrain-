'use client'

import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import type { FocusSessionStatus, FocusPhase } from '@/types/focus'

interface FocusTimerProps {
  remainingSeconds: number
  status: FocusSessionStatus
  phase: FocusPhase
  className?: string
}

export function FocusTimer({ remainingSeconds, status, phase, className }: FocusTimerProps): JSX.Element {
  const minutes = Math.floor(Math.max(0, remainingSeconds) / 60)
  const seconds = Math.max(0, remainingSeconds) % 60

  const timeDisplay = useMemo(() => {
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }, [minutes, seconds])

  const colorClass = useMemo(() => {
    if (phase === 'break') return 'text-accent-success'
    if (remainingSeconds <= 10) return 'text-accent-error'
    if (remainingSeconds <= 60) return 'text-accent-warning'
    return 'text-accent-primary'
  }, [remainingSeconds, phase])

  const showPulse = status === 'running' && phase === 'work' && remainingSeconds <= 30 && remainingSeconds > 0

  return (
    <motion.div
      className={cn('relative flex items-center justify-center', className)}
      animate={showPulse ? { scale: [1, 1.03, 1] } : { scale: 1 }}
      transition={
        showPulse
          ? { duration: 1.2, repeat: Infinity, ease: 'easeInOut' }
          : { duration: 0.3 }
      }
    >
      <motion.span
        className={cn(
          'font-mono font-bold tracking-tighter select-none',
          'text-[72px] leading-none md:text-[96px]',
          colorClass,
        )}
        key={timeDisplay}
        initial={{ opacity: 0.6, y: 2 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.1 }}
        aria-live="polite"
        aria-label={
          phase === 'work'
            ? `${minutes} minutes ${seconds} seconds remaining in work session`
            : `${minutes} minutes ${seconds} seconds remaining in break`
        }
      >
        {minutes.toString().padStart(2, '0')}
        <motion.span
          className="inline-block"
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1, repeat: Infinity, ease: 'steps(1)' }}
        >
          :
        </motion.span>
        {seconds.toString().padStart(2, '0')}
      </motion.span>
    </motion.div>
  )
}
