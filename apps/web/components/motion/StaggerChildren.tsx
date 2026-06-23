'use client'

import { Children, isValidElement, type ReactNode } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { fadeInUp } from '@/lib/motion/variants'

export interface StaggerChildrenProps {
  children: ReactNode
  staggerDelay?: number
  className?: string
}

export function StaggerChildren({ children, staggerDelay = 0.05, className }: StaggerChildrenProps) {
  const reduced = useReducedMotion()
  const items = Children.toArray(children).filter(isValidElement)

  if (reduced) {
    return <div className={cn(className)}>{children}</div>
  }

  return (
    <motion.div
      className={cn(className)}
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: staggerDelay,
            delayChildren: 0.05,
          },
        },
      }}
      initial="hidden"
      animate="visible"
    >
      {items.map((child, i) => (
        <motion.div key={i} variants={fadeInUp}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}
