'use client'

import { memo } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'

interface GoalProgressProps {
  current: number
  target: number
  label?: string
  className?: string
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

const sizeConfig = {
  sm: { bar: 'h-1.5', text: 'text-xs', icon: 12 },
  md: { bar: 'h-2', text: 'text-sm', icon: 14 },
  lg: { bar: 'h-3', text: 'text-base', icon: 16 },
}

export const GoalProgress = memo(function GoalProgress({
  current,
  target,
  label,
  className,
  showPercentage = true,
  size = 'md',
  loading,
}: GoalProgressProps) {
  const percentage = target > 0 ? Math.min((current / target) * 100, 100) : 0
  const config = sizeConfig[size]
  const isComplete = percentage >= 100

  if (loading) {
    return (
      <div className={cn('space-y-1.5', className)}>
        {label && <Skeleton variant="text" className="w-24" />}
        <Skeleton variant="text" className={cn('w-full rounded-full', config.bar)} />
        {showPercentage && <Skeleton variant="text" className="w-12" />}
      </div>
    )
  }

  return (
    <div className={cn('space-y-1.5', className)} role="progressbar" aria-valuenow={current} aria-valuemin={0} aria-valuemax={target} aria-label={label || 'Progress'}>
      {label && (
        <div className="flex items-center justify-between">
          <span className={cn(config.text, 'text-text-secondary font-medium')}>{label}</span>
        </div>
      )}
      <div className={cn('w-full rounded-full bg-background-elevated overflow-hidden', config.bar)}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className={cn(
            'h-full rounded-full transition-colors duration-300',
            isComplete ? 'bg-accent-success' : 'bg-accent-primary',
          )}
        />
      </div>
      {showPercentage && (
        <div className="flex items-center justify-between">
          <span className={cn(config.text, 'text-text-tertiary')}>
            {current} / {target}
          </span>
          <span className={cn(config.text, isComplete ? 'text-accent-success' : 'text-accent-primary', 'font-medium')}>
            {Math.round(percentage)}%
          </span>
        </div>
      )}
    </div>
  )
})
