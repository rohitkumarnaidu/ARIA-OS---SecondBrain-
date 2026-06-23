import { memo,  type HTMLAttributes, type ReactNode  } from 'react'
import { cn } from './utils'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'interactive' | 'compact' | 'highlight'
}

const Card = memo(function Card({ className, variant = 'default', ...props }: CardProps) {
  return (
    <div
      className={cn(
        'contain-layout contain-paint rounded-xl backdrop-blur-[20px] shadow-[0_4px_24px_rgba(0,0,0,0.2)]',
        'bg-background-card border border-border',
        variant === 'default' && 'p-4',
        variant === 'interactive' && [
          'p-4 cursor-pointer transition-all duration-300',
          'hover:border-border-light hover:-translate-y-0.5',
          'hover:shadow-[0_8px_32px_rgba(0,0,0,0.3),0_0_20px_var(--accent-glow-color-soft)]',
          'relative overflow-hidden',
          'before:content-[""] before:absolute before:inset-0 before:pointer-events-none',
          'before:bg-gradient-to-br before:from-[var(--accent-primary)]/8 before:to-transparent',
          'before:opacity-0 before:transition-opacity before:duration-300',
          'hover:before:opacity-100',
        ].join(' '),
        variant === 'compact' && 'p-3 text-sm',
        variant === 'highlight' && [
          'p-4 bg-background-elevated',
          'border-l-4 border-l-accent-primary',
        ].join(' '),
        className,
      )}
      {...props}
    />
  )
})

const CardHeader = memo(function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('flex items-center justify-between mb-4', className)}>{children}</div>
})

const CardTitle = memo(function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={cn('text-lg font-semibold text-[var(--foreground)]', className)}>{children}</h3>
})

const CardContent = memo(function CardContent({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn(className)}>{children}</div>
})

const CardFooter = memo(function CardFooter({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('flex items-center px-6 pb-6', className)} data-slot="card-footer">{children}</div>
})

const CardDescription = memo(function CardDescription({ children, className }: { children: ReactNode; className?: string }) {
  return <p className={cn('text-sm text-[var(--text-secondary)]', className)} data-slot="card-description">{children}</p>
})

export { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription }
export type { CardProps }
