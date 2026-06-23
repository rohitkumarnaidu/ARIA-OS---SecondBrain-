import { memo } from 'react'
import { Skeleton } from './Skeleton'
import { cn } from './utils'

interface LoadingScreenProps {
  variant?: 'page' | 'card' | 'list' | 'detail'
  label?: string
  count?: number
  className?: string
}

const TextLine = memo(function TextLine({ width }: { width: string }) {
  return <Skeleton variant="text" className={cn('h-3.5', width)} />
})

const CardSkeleton = memo(function CardSkeleton() {
  return (
    <div className="rounded-xl border border-border p-5 space-y-3">
      <Skeleton className="h-5 w-3/5" variant="text" />
      <TextLine width="w-full" />
      <TextLine width="w-full" />
      <TextLine width="w-2/3" />
    </div>
  )
})

const ListRow = memo(function ListRow() {
  return (
    <div className="flex items-center gap-4 py-3.5 px-4 rounded-xl border border-border min-h-[44px]">
      <Skeleton className="h-4 w-4 shrink-0 rounded" />
      <Skeleton className="h-4 flex-1" variant="text" />
      <Skeleton className="h-5 w-16 shrink-0 rounded-full" />
    </div>
  )
})

export const LoadingScreen = memo(function LoadingScreen({ variant = 'page', label, count = 5, className }: LoadingScreenProps) {
  const ariaLabel = label || `Loading ${variant}`

  if (variant === 'card') {
    return (
      <div className={cn('flex items-center justify-center p-8', className)} role="status" aria-label={ariaLabel}>
        <CardSkeleton />
      </div>
    )
  }

  if (variant === 'list') {
    return (
      <div className={cn('space-y-2', className)} role="status" aria-label={ariaLabel}>
        {Array.from({ length: count }).map((_, i) => (
          <ListRow key={i} />
        ))}
      </div>
    )
  }

  if (variant === 'detail') {
    return (
      <div className={cn('space-y-6', className)} role="status" aria-label={ariaLabel}>
        <Skeleton className="h-4 w-16" variant="text" />
        <Skeleton className="h-8 w-2/3" variant="text" />
        <div className="flex gap-4 flex-wrap">
          <Skeleton className="h-5 w-24 rounded-full" />
          <Skeleton className="h-5 w-32 rounded-full" />
          <Skeleton className="h-5 w-20 rounded-full" />
        </div>
        <div className="rounded-xl border border-border p-6 space-y-3">
          <TextLine width="w-full" />
          <TextLine width="w-full" />
          <TextLine width="w-3/4" />
          <TextLine width="w-full" />
          <TextLine width="w-1/2" />
        </div>
      </div>
    )
  }

  return (
    <div className={cn('flex gap-6 p-6 min-h-0', className)} role="status" aria-label={ariaLabel}>
      <div className="w-56 shrink-0 space-y-3 max-sm:hidden">
        <Skeleton className="h-4 w-20" variant="text" />
        <Skeleton className="h-10 w-full rounded-lg" />
        <Skeleton className="h-10 w-full rounded-lg" />
        <Skeleton className="h-10 w-4/5 rounded-lg" />
        <Skeleton className="h-10 w-full rounded-lg" />
      </div>
      <div className="flex-1 space-y-6">
        <Skeleton className="h-7 w-48" variant="text" />
        <div className="grid gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <div className="space-y-2">
          <TextLine width="w-full" />
          <TextLine width="w-5/6" />
        </div>
      </div>
    </div>
  )
})
