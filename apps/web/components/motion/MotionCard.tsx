'use client'

import { type ReactNode } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { cardHover } from '@/lib/motion/variants'
import { spring, springGentle } from '@/lib/motion/transitions'

export interface MotionCardProps {
  children: ReactNode
  className?: string
  hoverScale?: number
  tapScale?: number
}

export function MotionCard({ children, className, hoverScale = 1.02, tapScale = 0.98 }: MotionCardProps) {
  const reduced = useReducedMotion()

  if (reduced) {
    return <div className={cn(className)}>{children}</div>
  }

  return (
    <motion.div
      className={cn(
        'relative rounded-xl bg-background-card border border-border',
        'transition-shadow duration-300',
        className,
      )}
      initial="rest"
      whileHover="hover"
      whileTap="tap"
      variants={{
        rest: {
          scale: 1,
          boxShadow: 'var(--shadow-elevation-1, 0 1px 3px rgba(0,0,0,0.1))',
        },
        hover: {
          scale: hoverScale,
          boxShadow: 'var(--shadow-glow-sm)',
          transition: springGentle,
        },
        tap: {
          scale: tapScale,
          transition: spring,
        },
      }}
      style={{ willChange: 'transform' }}
    >
      {children}
    </motion.div>
  )
}
