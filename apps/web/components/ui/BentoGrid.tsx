'use client'

import { memo,  type ReactNode  } from 'react'
import { cn } from './utils'

interface BentoGridProps {
  children: ReactNode
  className?: string
  cols?: 2 | 3 | 4
}

interface BentoCardProps {
  children: ReactNode
  className?: string
  span?: 1 | 2 | 4
}

const BentoGrid = memo(function BentoGrid({ children, className, cols = 3 }: BentoGridProps) {
  return (
    <div
      className={cn(
        'grid gap-4 auto-rows-auto',
        {
          'grid-cols-1 md:grid-cols-2': cols === 2,
          'grid-cols-1 md:grid-cols-2 lg:grid-cols-3': cols === 3,
          'grid-cols-1 md:grid-cols-2 lg:grid-cols-4': cols === 4,
        },
        '[&_.bento-span-2]:col-span-1 md:[&_.bento-span-2]:col-span-2',
        '[&_.bento-span-4]:col-span-1 md:[&_.bento-span-4]:col-span-2 lg:[&_.bento-span-4]:col-span-4',
        className,
      )}
    >
      {children}
    </div>
  )
})

const BentoCard = memo(function BentoCard({ children, className, span = 1 }: BentoCardProps) {
  return (
    <div
      className={cn(
        'bg-card border border-border rounded-xl p-4',
        'backdrop-blur-[20px] shadow-[0_4px_24px_rgba(0,0,0,0.2)]',
        'transition-all duration-300',
        'hover:border-border-light',
        span === 1 && 'col-span-1',
        span === 2 && 'bento-span-2',
        span === 4 && 'bento-span-4',
        className,
      )}
    >
      {children}
    </div>
  )
})

export { BentoGrid, BentoCard }
export type { BentoGridProps, BentoCardProps }
