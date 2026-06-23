'use client'

import { memo, useState, useEffect } from 'react'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, X } from 'lucide-react'

interface ThinkingIndicatorProps {
  state: 'idle' | 'thinking' | 'complete' | 'error' | 'cancelled'
  messages?: string[]
  className?: string
}

const dotVariants = {
  hidden: { opacity: 0, scale: 0.5 },
  visible: (i: number) => ({
    opacity: 0.8,
    scale: 1,
    transition: { delay: i * 0.12, duration: 0.25, ease: 'easeOut' },
  }),
  exit: { opacity: 0, scale: 0.5, transition: { duration: 0.15 } },
}

export const ThinkingIndicator = memo(function ThinkingIndicator({ state, messages, className }: ThinkingIndicatorProps) {
  const [msgIndex, setMsgIndex] = useState(0)

  useEffect(() => {
    if (state !== 'thinking' || !messages?.length) return
    const interval = setInterval(() => {
      setMsgIndex((i) => (i + 1) % messages.length)
    }, 1200)
    return () => clearInterval(interval)
  }, [state, messages])

  if (state === 'idle') return null

  const ariaLabel =
    state === 'thinking'
      ? messages?.[msgIndex] ?? 'Thinking'
      : state === 'complete'
        ? 'Complete'
        : state === 'error'
          ? 'Error'
          : 'Cancelled'

  return (
    <div role="status" aria-label={ariaLabel} className={clsx('flex items-center gap-2 min-h-[20px]', className)}>
      <AnimatePresence mode="wait">
        {state === 'thinking' && (
          <motion.div
            key="thinking"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2"
          >
            <div className="flex gap-1" aria-hidden="true">
              {[0, 1, 2].map((i) => (
                <motion.span
                  key={i}
                  custom={i}
                  variants={dotVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  className="w-1.5 h-1.5 rounded-full"
                  style={{
                    backgroundColor: 'var(--accent-neon)',
                    animation: `bounce 1.4s ease-in-out infinite ${i * 0.2}s`,
                  }}
                />
              ))}
            </div>
            {messages?.[msgIndex] && (
              <span className="text-xs font-mono" style={{ color: 'var(--accent-neon)', opacity: 0.7 }}>{messages[msgIndex]}</span>
            )}
          </motion.div>
        )}

        {state === 'complete' && (
          <motion.div
            key="complete"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
          >
            <span className="flex items-center justify-center w-4 h-4 rounded-full bg-accent-success/20">
              <Check size={10} className="text-accent-success" strokeWidth={3} aria-hidden="true" />
            </span>
          </motion.div>
        )}

        {state === 'error' && (
          <motion.div
            key="error"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
          >
            <span className="flex items-center justify-center w-4 h-4 rounded-full bg-accent-error/20">
              <X size={10} className="text-accent-error" strokeWidth={3} aria-hidden="true" />
            </span>
          </motion.div>
        )}

        {state === 'cancelled' && (
          <motion.div
            key="cancelled"
            initial={{ opacity: 0.8 }}
            animate={{ opacity: 0.35 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-1"
            aria-hidden="true"
          >
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: 'var(--text-tertiary)', opacity: 0.4 }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
})

export type { ThinkingIndicatorProps }
