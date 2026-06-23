'use client'

import { type ReactNode } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { cn } from '@/components/ui/utils'

export interface PulseGlowProps {
  children: ReactNode
  color?: string
  className?: string
  active?: boolean
}

export function PulseGlow({ children, color, className, active = true }: PulseGlowProps) {
  const reduced = useReducedMotion()
  const isActive = active && !reduced

  return (
    <div className={cn('relative inline-flex', className)}>
      {isActive && (
        <motion.div
          className="pointer-events-none absolute -inset-[3px] rounded-[inherit]"
          style={{
            background: color ?? 'var(--accent-primary)',
            opacity: 0.15,
            filter: 'blur(8px)',
            willChange: 'transform, opacity',
          }}
          animate={{
            opacity: [0.1, 0.2, 0.1],
            scale: [1, 1.04, 1],
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          aria-hidden="true"
        />
      )}
      {children}
    </div>
  )
}
