'use client'

import { type ReactNode } from 'react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { stagger, listItem } from '@/lib/motion/variants'

export interface AnimatedListProps {
  items: ReactNode[]
  className?: string
  itemClassName?: string
}

export function AnimatedList({ items, className, itemClassName }: AnimatedListProps) {
  const reduced = useReducedMotion()

  if (reduced) {
    return (
      <div className={cn(className)}>
        {items.map((item, i) => (
          <div key={i} className={cn(itemClassName)}>{item}</div>
        ))}
      </div>
    )
  }

  return (
    <motion.div
      className={cn(className)}
      variants={stagger}
      initial="hidden"
      animate="visible"
    >
      <AnimatePresence mode="popLayout">
        {items.map((item, i) => (
          <motion.div
            key={i}
            className={cn(itemClassName)}
            variants={listItem}
            layout
          >
            {item}
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  )
}
