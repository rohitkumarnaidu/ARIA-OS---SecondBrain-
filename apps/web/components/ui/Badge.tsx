import { forwardRef, type ElementType, type HTMLAttributes } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cn } from './utils'

interface BadgeProps extends HTMLAttributes<HTMLElement> {
  asChild?: boolean
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline'
}

const variants = {
  default: 'bg-accent-primary/10 text-accent-secondary border-accent-primary/20',
  success: 'bg-accent-success/10 text-accent-success border-accent-success/20',
  warning: 'bg-accent-warning/10 text-accent-warning border-accent-warning/20',
  error: 'bg-accent-error/10 text-accent-error border-accent-error/20',
  info: 'bg-accent-info/10 text-accent-info border-accent-info/20',
  outline: 'text-foreground border-border',
} as const

const Badge = forwardRef<HTMLElement, BadgeProps>(
  ({ asChild = false, variant = 'default', className, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'span'

    return (
      <Comp
        ref={ref}
        className={cn(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
          'font-body',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
          'aria-invalid:ring-2 aria-invalid:ring-[var(--destructive)]/20 aria-invalid:border-destructive',
          variants[variant],
          className,
        )}
        data-slot="badge"
        {...props}
      >
        {children}
      </Comp>
    )
  },
)

Badge.displayName = 'Badge'

export { Badge }
