'use client'

import { type ReactNode } from 'react'
import { motion, AnimatePresence, useReducedMotion, type Variants } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { fadeIn, fadeInUp, fadeInDown, scaleIn, slideUp } from '@/lib/motion/variants'

const variantMap: Record<string, Variants> = {
  fade: fadeIn,
  slideUp: fadeInUp,
  slideDown: fadeInDown,
  scale: scaleIn,
  slide: slideUp,
}

export interface PageTransitionProps {
  children: ReactNode
  className?: string
  variant?: 'fade' | 'slideUp' | 'slideDown' | 'scale' | 'slide'
}

export function PageTransition({ children, className, variant = 'fade' }: PageTransitionProps) {
  const reduced = useReducedMotion()
  const vars = reduced ? fadeIn : variantMap[variant] ?? fadeIn

  return (
    <AnimatePresence mode="wait">
      <motion.div
        className={cn(className)}
        variants={vars}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
