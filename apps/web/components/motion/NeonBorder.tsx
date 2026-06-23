'use client'

import { type ReactNode } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { DURATION } from '@/lib/motion/constants'

export interface NeonBorderProps {
  children: ReactNode
  color?: string
  className?: string
  speed?: number
}

export function NeonBorder({ children, color, className, speed = DURATION.slower }: NeonBorderProps) {
  const reduced = useReducedMotion()
  const neonColor = color ?? 'var(--accent-primary)'

  return (
    <div className={cn('relative', className)}>
      {!reduced && (
        <motion.div
          className="pointer-events-none absolute inset-0 rounded-[inherit]"
          style={{
            border: '1px solid transparent',
            borderRadius: 'inherit',
            willChange: 'box-shadow, opacity',
          }}
          animate={{
            boxShadow: [
              `0 0 6px ${neonColor}, 0 0 12px ${neonColor}, inset 0 0 6px ${neonColor}`,
              `0 0 2px ${neonColor}, 0 0 4px ${neonColor}, inset 0 0 2px ${neonColor}`,
              `0 0 6px ${neonColor}, 0 0 12px ${neonColor}, inset 0 0 6px ${neonColor}`,
            ],
          }}
          transition={{
            duration: speed / 1000,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          aria-hidden="true"
        />
      )}
      <div className="relative z-[1]">{children}</div>
    </div>
  )
}
