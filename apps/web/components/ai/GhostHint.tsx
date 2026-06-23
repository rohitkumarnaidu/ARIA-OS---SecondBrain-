'use client'

import { memo, useEffect, useCallback, useRef } from 'react'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'

interface GhostHintProps {
  text: string
  state: 'hidden' | 'visible' | 'filled' | 'dismissed'
  onAccept?: () => void
  onDismiss?: () => void
  className?: string
}

const GhostHint = memo(function GhostHint({ text, state, onAccept, onDismiss, className }: GhostHintProps) {
  const acceptRef = useRef(onAccept)
  const dismissRef = useRef(onDismiss)

  useEffect(() => {
    acceptRef.current = onAccept
  }, [onAccept])

  useEffect(() => {
    dismissRef.current = onDismiss
  }, [onDismiss])

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Tab') {
      if (state === 'visible' && acceptRef.current) {
        e.preventDefault()
        acceptRef.current()
      }
    }
    if (e.key === 'Escape') {
      if (state === 'visible' && dismissRef.current) {
        dismissRef.current()
      }
    }
  }, [state])

  useEffect(() => {
    if (state === 'visible') {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [state, handleKeyDown])

  return (
    <AnimatePresence>
      {state !== 'hidden' && (
        <motion.div
          key={state}
          initial={state === 'visible' ? { opacity: 0, y: -4 } : false}
          animate={{
            opacity: state === 'dismissed' ? 0 : state === 'filled' ? 1 : 1,
            y: state === 'dismissed' ? -4 : state === 'filled' ? 0 : 0,
            scale: state === 'filled' ? 0.97 : 1,
          }}
          exit={{ opacity: 0, y: -4, transition: { duration: 0.15 } }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          className={clsx(
            'flex items-center justify-between text-xs h-6',
            state === 'filled' && 'text-accent-primary',
            state === 'visible' && 'text-text-tertiary',
            className,
          )}
          aria-live="polite"
        >
          <span className={clsx('italic truncate', state === 'filled' && 'line-through decoration-accent-primary/30')}>
            {text}
          </span>
          {state === 'visible' && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="shrink-0 ml-2 px-1.5 py-0.5 rounded text-[10px] leading-none font-mono"
              style={{
                color: 'var(--accent-primary)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                backgroundColor: 'rgba(99, 102, 241, 0.08)',
              }}
            >
              Tab &#x21E5;
            </motion.span>
          )}
          {state === 'filled' && (
            <span className="shrink-0 ml-2 text-accent-primary text-[10px] font-medium">Accepted</span>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  )
})

export { GhostHint }
export type { GhostHintProps }
