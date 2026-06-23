'use client'

import { memo,  forwardRef, type ButtonHTMLAttributes, type ReactNode  } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { Loader2 } from 'lucide-react'
import { cn } from './utils'

const buttonVariants = cva(
  [
    'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium',
    'transition-all duration-200 ease-out',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
    'disabled:pointer-events-none disabled:opacity-50',
    'active:scale-[0.98]',
    '[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*="size-"])]:size-4',
    'gap-2',
  ],
  {
    variants: {
      variant: {
        primary: [
          'bg-[var(--accent-primary)] text-white',
          'hover:bg-[var(--accent-primary-hover)]',
          'shadow-glow-sm',
        ],
        default: [
          'bg-[var(--accent-primary)] text-white',
          'hover:bg-[var(--accent-primary-hover)]',
          'shadow-glow-sm',
          'aria-invalid:border-destructive aria-invalid:ring-[var(--destructive)]/20',
        ],
        destructive: [
          'bg-destructive text-destructive-foreground',
          'hover:bg-[var(--accent-error-hover)]',
        ],
        outline: [
          'border border-border bg-transparent text-foreground',
          'hover:bg-[var(--accent)]/5 hover:border-border-light',
        ],
        secondary: [
          'bg-secondary text-secondary-foreground',
          'hover:bg-[var(--secondary)]/80',
        ],
        ghost: [
          'text-text-secondary',
          'hover:bg-[var(--accent)]/10 hover:text-foreground',
        ],
        link: [
          'text-accent-primary underline-offset-4',
          'hover:underline',
        ],
      },
      size: {
        default: 'h-9 px-4 py-2 has-[>svg]:px-3',
        sm: 'h-8 rounded-md px-3 text-xs has-[>svg]:px-2.5',
        lg: 'h-10 rounded-md px-6 has-[>svg]:px-4',
        icon: 'size-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
  icon?: ReactNode
}

const Button = memo(forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading, icon, disabled, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        data-slot="button"
        aria-disabled={disabled || loading || undefined}
        aria-busy={loading || undefined}
        {...props}
      >
        {loading && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
        {!loading && icon && <span aria-hidden="true">{icon}</span>}
        {children}
      </Comp>
    )
  },
)
)
Button.displayName = 'Button'

export { Button, buttonVariants }
export type { ButtonProps }
