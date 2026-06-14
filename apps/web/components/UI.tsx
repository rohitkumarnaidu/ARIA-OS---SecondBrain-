'use client'

import { ButtonHTMLAttributes, InputHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'

// Accessible Button - minimum 44px touch target, focus states
export const Button = forwardRef<HTMLButtonElement, ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
}>(function Button({ 
  className, 
  variant = 'primary', 
  size = 'md', 
  isLoading, 
  disabled, 
  children,
  ...props 
}, ref) {
  const variants = {
    primary: 'bg-accent-primary hover:bg-accent-primary-hover text-white',
    secondary: 'bg-background-elevated hover:bg-border text-text-primary border border-border',
    ghost: 'bg-transparent hover:bg-background-elevated text-text-secondary hover:text-text-primary',
    danger: 'bg-accent-error hover:bg-accent-error-hover text-white',
  }
  
  const sizes = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-touch px-4 text-base min-w-[44px]',
    lg: 'h-12 px-6 text-lg',
  }
  
  return (
    <button
      ref={ref}
      className={clsx(
        'inline-flex items-center justify-center font-medium rounded-lg',
        'transition-all duration-200 ease-out',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background-dark',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'active:scale-[0.98]',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4\" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </button>
  )
})

// Accessible Input - minimum 44px height, visible labels, error states
export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & {
  label?: string
  error?: string
  helperText?: string
}>(function Input({ 
  className, 
  label, 
  error, 
  helperText,
  id,
  required,
  ...props 
}, ref) {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
  
  return (
    <div className="space-y-1.5">
      {label && (
        <label 
          htmlFor={inputId} 
          className="block text-sm font-medium text-text-primary"
        >
          {label}
          {required && <span className="text-accent-error ml-1" aria-hidden="true">*</span>}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        required={required}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
        className={clsx(
          'w-full h-input px-4 rounded-lg',
          'bg-background-input border text-text-primary placeholder:text-text-tertiary',
          'transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error 
            ? 'border-accent-error focus:ring-accent-error focus:shadow-focus-error' 
            : 'border-border hover:border-border-light',
          className
        )}
        {...props}
      />
      {error && (
        <p id={`${inputId}-error`} className="text-sm text-accent-error" role="alert">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={`${inputId}-helper`} className="text-sm text-text-tertiary">
          {helperText}
        </p>
      )}
    </div>
  )
})

// Select with proper accessibility
export const Select = forwardRef<HTMLSelectElement, InputHTMLAttributes<HTMLSelectElement> & {
  label?: string
  error?: string
  options: { value: string; label: string }[]
}>(function Select({ 
  className, 
  label, 
  error, 
  id,
  options,
  required,
  ...props 
}, ref) {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`
  
  return (
    <div className="space-y-1.5">
      {label && (
        <label 
          htmlFor={selectId} 
          className="block text-sm font-medium text-text-primary"
        >
          {label}
          {required && <span className="text-accent-error ml-1" aria-hidden="true">*</span>}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        required={required}
        aria-invalid={error ? 'true' : undefined}
        className={clsx(
          'w-full h-input px-4 rounded-lg appearance-none',
          'bg-background-input border text-text-primary',
          'bg-[url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 24 24\' stroke=\'%2394A3B8\'%3E%3Cpath stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'2\' d=\'M19 9l-7 7-7-7\'%3E%3C/path%3E%3C/svg%3E")] bg-no-repeat bg-[right_12px_center] bg-[length:20px]',
          'transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error 
            ? 'border-accent-error focus:ring-accent-error focus:shadow-focus-error' 
            : 'border-border hover:border-border-light',
          className
        )}
        {...props}
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-sm text-accent-error" role="alert">
          {error}
        </p>
      )}
    </div>
  )
})

// Accessible Card component
export function Card({ 
  children, 
  className,
  interactive = false,
  onClick,
}: { 
  children: React.ReactNode
  className?: string
  interactive?: boolean
  onClick?: () => void
}) {
  const Component = interactive ? 'button' : 'div'
  
  return (
    <Component
      onClick={onClick}
      className={clsx(
        'bg-background-card border border-border rounded-xl p-4',
        interactive && 'cursor-pointer transition-all duration-200 hover:border-border-light hover:shadow-md',
        className
      )}
    >
      {children}
    </Component>
  )
}

// Loading skeleton - proper progressive loading
export function Skeleton({ className }: { className?: string }) {
  return (
    <div 
      className={clsx(
        'animate-pulse bg-background-elevated rounded',
        className
      )} 
      aria-hidden="true"
    />
  )
}

// Empty state with proper guidance
export function EmptyState({ 
  title, 
  description, 
  action 
}: { 
  title: string
  description?: string
  action?: { label: string; onClick: () => void }
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      {description && (
        <p className="text-text-secondary mb-4 max-w-sm">{description}</p>
      )}
      {action && (
        <Button onClick={action.onClick} variant="primary">
          {action.label}
        </Button>
      )}
    </div>
  )
}

// Toast notification for success/error feedback
export function Toast({ 
  type, 
  message, 
  onDismiss 
}: { 
  type: 'success' | 'error' | 'info'
  message: string
  onDismiss: () => void
}) {
  const colors = {
    success: 'bg-accent-success/10 border-accent-success text-accent-success',
    error: 'bg-accent-error/10 border-accent-error text-accent-error',
    info: 'bg-accent-info/10 border-accent-info text-accent-info',
  }
  
  return (
    <div 
      role="alert"
      aria-live="polite"
      className={clsx(
        'fixed bottom-4 right-4 z-toast flex items-center gap-3 px-4 py-3 rounded-lg border',
        'animate-[slideIn_0.3s_ease-out]',
        colors[type]
      )}
    >
      <span className="text-sm font-medium">{message}</span>
      <button 
        onClick={onDismiss}
        className="p-1 hover:opacity-80"
        aria-label="Dismiss"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}