'use client'

import { InputHTMLAttributes, forwardRef, useId } from 'react'
import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, required, ...props }, ref) => {
    const genId = useId()
    const inputId = id || genId

    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-text-primary">
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
            'w-full h-11 px-4 rounded-lg bg-background-input border text-text-primary placeholder:text-text-tertiary',
            'transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error ? 'border-accent-error focus:ring-accent-error' : 'border-border hover:border-border-light',
            className,
          )}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-accent-error" role="alert">{error}</p>
        )}
        {helperText && !error && (
          <p id={`${inputId}-helper`} className="text-sm text-text-tertiary">{helperText}</p>
        )}
      </div>
    )
  },
)

Input.displayName = 'Input'
export type { InputProps }
