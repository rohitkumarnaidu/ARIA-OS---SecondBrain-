import { cn } from './utils'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circle' | 'card' | 'chart' | 'table-row'
}

function Skeleton({ className, variant = 'text' }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse bg-background-elevated',
        variant === 'text' && 'h-4 rounded w-full',
        variant === 'circle' && 'rounded-full w-10 h-10',
        variant === 'card' && 'h-32 rounded-xl w-full',
        variant === 'chart' && 'h-48 rounded-lg w-full',
        variant === 'table-row' && 'h-12 rounded w-full',
        className,
      )}
      aria-hidden="true"
      role="presentation"
    />
  )
}

export { Skeleton }
export type { SkeletonProps }
