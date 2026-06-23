'use client'

import { useEffect, useRef } from 'react'
import { motion, useMotionValue, useTransform, useReducedMotion, animate } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { MOTION_DURATION } from '@/lib/motion/constants'

export interface AnimatedNumberProps {
  value: number
  duration?: number
  formatFn?: (n: number) => string
  className?: string
}

export function AnimatedNumber({ value, duration = MOTION_DURATION.slower, formatFn, className }: AnimatedNumberProps) {
  const reduced = useReducedMotion()
  const motionValue = useMotionValue(reduced ? value : 0)
  const prevValueRef = useRef(0)

  const rounded = useTransform(motionValue, (v) => Math.round(v))
  const displayValue = useTransform(rounded, (v) => formatFn ? formatFn(v) : String(v))

  useEffect(() => {
    if (reduced) {
      motionValue.set(value)
      return
    }

    const controls = animate(prevValueRef.current, value, {
      duration,
      ease: 'easeOut',
      onUpdate: (latest) => motionValue.set(latest),
    })

    prevValueRef.current = value
    return () => controls.stop()
  }, [value, duration, reduced, motionValue])

  return <motion.span className={cn('tabular-nums', className)}>{displayValue}</motion.span>
}
