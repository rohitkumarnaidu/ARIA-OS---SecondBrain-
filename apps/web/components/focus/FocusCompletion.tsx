'use client'

import { motion } from 'framer-motion'
import { useEffect, useRef } from 'react'
import { Check, Clock, Target, Hash } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/utils'

interface FocusCompletionProps {
  totalSeconds: number
  cyclesCompleted: number
  objective: string
  onStartAnother: () => void
  onReviewSession: () => void
}

function formatDuration(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m ${totalSeconds % 60}s`
}

export function FocusCompletion({
  totalSeconds,
  cyclesCompleted,
  objective,
  onStartAnother,
  onReviewSession,
}: FocusCompletionProps): JSX.Element {
  const focusScore = Math.min(100, Math.round((cyclesCompleted / 4) * 85 + 15))
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    const previousFocus = document.activeElement as HTMLElement
    const focusable = container.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    if (focusable.length) focusable[0].focus()

    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { onStartAnother(); return }
      if (e.key === 'Tab') {
        const current = container.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
        if (!current.length) return
        const first = current[0]
        const last = current[current.length - 1]
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first.focus()
        }
      }
    }
    document.addEventListener('keydown', handleKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleKey)
      document.body.style.overflow = ''
      previousFocus?.focus()
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Session complete"
    >
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="absolute inset-0 bg-black/70 backdrop-blur-xl"
        aria-hidden="true"
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.85, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 250, damping: 25, delay: 0.1 }}
        className={cn(
          'relative w-full max-w-lg rounded-2xl border border-accent-primary/20 p-8 text-center',
          'bg-glass-heavy backdrop-blur-2xl',
          'shadow-[var(--shadow-neon)]',
        )}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 350, damping: 20, delay: 0.3 }}
          className="mx-auto mb-6 flex size-20 items-center justify-center rounded-full bg-accent-success/20"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, type: 'spring', stiffness: 300, damping: 15 }}
          >
            <Check size={40} className="text-accent-success" strokeWidth={2.5} />
          </motion.div>
        </motion.div>

        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-2 font-display text-3xl font-semibold text-text-primary"
        >
          Session Complete!
        </motion.h2>

        {objective && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="mb-6 text-text-secondary text-sm"
          >
            &ldquo;{objective}&rdquo;
          </motion.p>
        )}

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8 grid grid-cols-3 gap-4"
        >
          <div className="rounded-xl bg-surface-secondary/50 p-3">
            <Clock size={18} className="mx-auto mb-1 text-accent-secondary" />
            <div className="text-lg font-semibold text-text-primary">{formatDuration(totalSeconds)}</div>
            <div className="text-xs text-text-tertiary">Duration</div>
          </div>
          <div className="rounded-xl bg-surface-secondary/50 p-3">
            <Hash size={18} className="mx-auto mb-1 text-accent-warning" />
            <div className="text-lg font-semibold text-text-primary">{cyclesCompleted}</div>
            <div className="text-xs text-text-tertiary">Cycles</div>
          </div>
          <div className="rounded-xl bg-surface-secondary/50 p-3">
            <Target size={18} className="mx-auto mb-1 text-accent-neon" />
            <div className="text-lg font-semibold text-text-primary">{focusScore}%</div>
            <div className="text-xs text-text-tertiary">Focus Score</div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col gap-3 sm:flex-row sm:justify-center"
        >
          <Button variant="primary" size="lg" onClick={onStartAnother}>
            Start Another
          </Button>
          <Button variant="ghost" size="lg" onClick={onReviewSession}>
            Review Session
          </Button>
        </motion.div>
      </motion.div>
    </div>
  )
}
