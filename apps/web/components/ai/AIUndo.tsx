'use client'

import { memo, useEffect, useId, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface AIUndoProps {
  message: string
  onUndo: () => void
  onExpired: () => void
  duration?: number
}

const DURATION = 10000

const AIUndo = memo(function AIUndo({ message, onUndo, onExpired, duration = DURATION }: AIUndoProps) {
  const [timeLeft, setTimeLeft] = useState(duration)
  const [visible, setVisible] = useState(true)
  const expiredCalled = useRef(false)
  const clipId = useId()
  const startTime = useRef(Date.now())

  useEffect(() => {
    startTime.current = Date.now()
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime.current
      const remaining = Math.max(0, duration - elapsed)
      setTimeLeft(remaining)

      if (remaining <= 0 && !expiredCalled.current) {
        expiredCalled.current = true
        setVisible(false)
        onExpired()
      }
    }, 50)

    return () => clearInterval(interval)
  }, [duration, onExpired])

  const radius = 16
  const circumference = 2 * Math.PI * radius
  const progress = timeLeft / duration
  const offset = circumference * (1 - progress)

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 32, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 16, scale: 0.95 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[var(--z-tooltip)] min-w-[320px] max-w-[480px]"
          role="alert"
          aria-live="polite"
        >
          <div
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg',
              'backdrop-blur-[20px]',
            )}
            style={{
              backgroundColor: 'var(--glass-heavy)',
              border: '1px solid var(--border-light)',
            }}
          >
            <div className="relative w-9 h-9 shrink-0" aria-hidden="true">
              <svg width="36" height="36" viewBox="0 0 36 36" className="-rotate-90">
                <clipPath id={clipId}>
                  <circle cx="18" cy="18" r={radius} />
                </clipPath>
                <circle
                  cx="18" cy="18" r={radius}
                  fill="none"
                  stroke="var(--surface-tertiary)"
                  strokeWidth="3"
                />
                <motion.circle
                  cx="18" cy="18" r={radius}
                  fill="none"
                  stroke="var(--accent-warning)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                />
              </svg>
            </div>

            <p className="flex-1 text-sm text-[var(--text-primary)] min-w-0">
              {message}
            </p>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => {
                expiredCalled.current = true
                setVisible(false)
                onUndo()
              }}
              className={cn(
                'shrink-0 px-3 py-1.5 rounded-lg text-xs font-semibold',
                'transition-all duration-200',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background)]',
                'min-h-[36px]',
              )}
              style={{
                backgroundColor: 'var(--accent-warning)',
                color: 'var(--background)',
              }}
              aria-label="Undo action"
            >
              Undo
            </motion.button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
})

export { AIUndo }
export type { AIUndoProps }
