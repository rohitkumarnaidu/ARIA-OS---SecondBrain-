'use client'

import { ButtonHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'
import { Loader2 } from 'lucide-react'

const variants = {
  primary: 'bg-accent-primary text-white hover:bg-accent-primaryHover shadow-glow-sm hover:shadow-glow',
  secondary: 'bg-background-elevated text-text-primary border border-border hover:bg-border',
  ghost: 'bg-transparent text-text-secondary hover:text-text-primary hover:bg-background-elevated',
  danger: 'bg-accent-error text-white hover:bg-accent-errorHover',
  outline: 'bg-transparent text-text-primary border border-border hover:bg-background-elevated',
} as const

const sizes = {
  sm: 'h-9 px-3 text-sm min-w-[36px] gap-1.5',
  md: 'h-11 px-4 text-sm min-w-[44px] gap-2',
  lg: 'h-12 px-6 text-base min-w-[48px] gap-2.5',
} as const

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants
  size?: keyof typeof sizes
  loading?: boolean
  icon?: React.ReactNode
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, icon, disabled, children, ...props }, ref) => (
    <button
      ref={ref}
      className={clsx(
        'inline-flex items-center justify-center font-medium rounded-lg',
        'transition-all duration-200 ease-out',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'active:scale-[0.98]',
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={disabled || loading}
      aria-disabled={disabled || loading || undefined}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && <Loader2 size={16} className="animate-spin" aria-hidden="true" />}
      {!loading && icon && <span aria-hidden="true">{icon}</span>}
      {children}
    </button>
  ),
)

Button.displayName = 'Button'
export type { ButtonProps }
