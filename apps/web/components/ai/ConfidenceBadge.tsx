'use client'

import { memo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface ConfidenceBadgeProps {
  value: number
  label?: string
  showTooltip?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

function getConfidenceLevel(value: number): { color: string; bg: string; label: string } {
  if (value >= 85) {
    return {
      color: 'var(--accent-success)',
      bg: 'var(--accent-success)',
      label: 'High confidence',
    }
  }
  if (value >= 60) {
    return {
      color: 'var(--accent-warning)',
      bg: 'var(--accent-warning)',
      label: 'Medium confidence',
    }
  }
  return {
    color: 'var(--accent-error)',
    bg: 'var(--accent-error)',
    label: 'Low confidence',
  }
}

const sizeMap = {
  sm: 'w-2 h-2',
  md: 'w-2.5 h-2.5',
  lg: 'w-3 h-3',
}

const textSizeMap = {
  sm: 'text-[10px]',
  md: 'text-xs',
  lg: 'text-sm',
}

const ConfidenceBadge = memo(function ConfidenceBadge({
  value,
  label,
  showTooltip = true,
  size = 'md',
  className,
}: ConfidenceBadgeProps) {
  const [isHovered, setIsHovered] = useState(false)
  const clamped = Math.min(100, Math.max(0, value))
  const level = getConfidenceLevel(clamped)

  return (
    <div
      className={cn('inline-flex items-center gap-1.5 relative', className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span
        className={cn(
          'inline-block rounded-full shrink-0',
          sizeMap[size],
        )}
        style={{ backgroundColor: level.color }}
        aria-hidden="true"
      />

      {label && (
        <span
          className={cn(
            'font-medium',
            textSizeMap[size],
          )}
          style={{ color: level.color }}
        >
          {label}
        </span>
      )}

      <span
        className={cn(
          'font-mono font-medium',
          textSizeMap[size],
        )}
        style={{ color: level.color }}
      >
        {clamped}%
      </span>

      {showTooltip && (
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ opacity: 0, y: 4, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 4, scale: 0.95 }}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              className={cn(
                'absolute bottom-full left-1/2 -translate-x-1/2 mb-2',
                'px-2 py-1 rounded-md text-xs whitespace-nowrap shadow-lg pointer-events-none',
              )}
              style={{
                backgroundColor: 'var(--popover)',
                border: '1px solid var(--border)',
                color: 'var(--popover-foreground)',
              }}
              role="tooltip"
            >
              <span style={{ color: level.color }}>{level.label}</span>
              {' · '}
              <span className="text-[var(--text-tertiary)]">
                Score: {clamped}/100
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      )}

      <span className="sr-only">Confidence: {clamped}% - {level.label}</span>
    </div>
  )
})

export { ConfidenceBadge }
export type { ConfidenceBadgeProps }
