'use client'

import { forwardRef, useId, type TextareaHTMLAttributes } from 'react'
import { cn } from './utils'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  helperText?: string
  maxLength?: number
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, maxLength, id, required, value, defaultValue, ...props }, ref) => {
    const genId = useId()
    const textareaId = id || genId
    const charCount = typeof value === 'string' ? value.length : typeof defaultValue === 'string' ? defaultValue.length : 0

    return (
      <div className="space-y-1.5">
        {label && (
          <div className="flex items-center justify-between">
            <label htmlFor={textareaId} className="block text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
              {label}
              {required && <span className="ml-1" style={{ color: 'var(--accent-error)' }} aria-hidden="true">*</span>}
            </label>
            {maxLength && (
              <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                {charCount}/{maxLength}
              </span>
            )}
          </div>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          required={required}
          maxLength={maxLength}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? `${textareaId}-error` : helperText ? `${textareaId}-helper` : undefined}
          className={cn(
            'w-full min-h-[100px] px-4 py-3 rounded-lg text-sm resize-y transition-all duration-200',
            'bg-background-input border text-text-primary placeholder:text-text-tertiary',
            'focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error ? 'border-accent-error focus:ring-accent-error' : 'border-border hover:border-border-light',
            className,
          )}
          value={value}
          defaultValue={defaultValue}
          {...props}
        />
        {error && (
          <p id={`${textareaId}-error`} className="text-sm" style={{ color: 'var(--accent-error)' }} role="alert">{error}</p>
        )}
        {helperText && !error && (
          <p id={`${textareaId}-helper`} className="text-sm" style={{ color: 'var(--text-tertiary)' }}>{helperText}</p>
        )}
      </div>
    )
  },
)

Textarea.displayName = 'Textarea'

export { Textarea }
export type { TextareaProps }
