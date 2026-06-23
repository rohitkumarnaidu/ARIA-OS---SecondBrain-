'use client'

import { memo, useState, useEffect, useRef } from 'react'
import { clsx } from 'clsx'
import { motion, useReducedMotion } from 'framer-motion'

interface StreamingTextProps {
  text: string
  isStreaming: boolean
  speed?: number
  className?: string
}

export const StreamingText = memo(function StreamingText({ text, isStreaming, speed = 30, className }: StreamingTextProps) {
  const [revealedCount, setRevealedCount] = useState(0)
  const reduced = useReducedMotion()
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const prevTextRef = useRef(text)

  const effectiveSpeed = reduced ? 0 : speed

  useEffect(() => {
    setRevealedCount(0)
    prevTextRef.current = text
  }, [text])

  useEffect(() => {
    if (!isStreaming || reduced) {
      if (!isStreaming) {
        setRevealedCount(text.length)
      }
      return
    }

    intervalRef.current = setInterval(() => {
      setRevealedCount((prev) => {
        if (prev >= text.length) {
          if (intervalRef.current) clearInterval(intervalRef.current)
          return text.length
        }
        return prev + 1
      })
    }, effectiveSpeed)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isStreaming, text, effectiveSpeed, reduced])

  // Sync revealedCount when streaming ends externally
  useEffect(() => {
    if (!isStreaming && revealedCount < text.length) {
      setRevealedCount(text.length)
    }
  }, [isStreaming, text.length, revealedCount])

  const visible = reduced ? text : text.slice(0, revealedCount)
  const remaining = reduced ? '' : text.slice(revealedCount)

  return (
    <span className={clsx('relative inline', className)}>
      {reduced ? (
        <span className="text-text-primary">{text}</span>
      ) : (
        <>
          {visible.split('').map((char, i) => (
            <motion.span
              key={`${i}-${char}`}
              initial={{ filter: 'blur(2px)', opacity: 0, y: 1 }}
              animate={{ filter: 'blur(0px)', opacity: 1, y: 0 }}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              className="inline whitespace-pre text-text-primary"
            >
              {char}
            </motion.span>
          ))}
          {remaining && (
            <span className="opacity-0 pointer-events-none select-none" aria-hidden="true">
              {remaining}
            </span>
          )}
          {isStreaming && revealedCount < text.length && (
            <motion.span
              aria-hidden="true"
              className="inline-block w-[2px] h-[1em] ml-[1px] align-middle"
              style={{ backgroundColor: 'var(--accent-primary)' }}
              animate={{ opacity: [1, 0.15, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut' }}
            />
          )}
        </>
      )}
      {!isStreaming && revealedCount >= text.length && (
        <span
          aria-hidden="true"
          className="inline-block w-[2px] h-[1em] ml-[1px] align-middle"
          style={{ backgroundColor: 'transparent' }}
        />
      )}
    </span>
  )
})

export type { StreamingTextProps }
