'use client'

import { forwardRef } from 'react'
import { motion } from 'framer-motion'
import { cn } from './utils'

interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  label?: string
  id?: string
  className?: string
}

const Switch = forwardRef<HTMLButtonElement, SwitchProps>(
  ({ checked, onChange, disabled = false, label, id, className }, ref) => {
    const switchId = id || `switch-${Math.random().toString(36).slice(2, 9)}`

    return (
      <label
        htmlFor={switchId}
        className={cn(
          'inline-flex items-center gap-3 cursor-pointer',
          disabled && 'opacity-50 cursor-not-allowed',
          className,
        )}
      >
        <button
          ref={ref}
          id={switchId}
          role="switch"
          aria-checked={checked}
          aria-disabled={disabled || undefined}
          disabled={disabled}
          onClick={() => { if (!disabled) onChange(!checked) }}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (!disabled) onChange(!checked) } }}
          className={cn(
            'relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 border-transparent transition-colors',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2',
            'focus-visible:ring-offset-[var(--background)]',
          )}
          style={{
            background: checked ? 'var(--accent-primary)' : 'var(--surface-tertiary)',
          }}
        >
          <motion.span
            layout
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="pointer-events-none block h-5 w-5 rounded-full shadow-lg ring-0"
            style={{
              background: '#FFFFFF',
              transform: checked ? 'translateX(100%)' : 'translateX(0)',
            }}
          />
        </button>
        {label && (
          <span className="text-sm select-none" style={{ color: 'var(--text-primary)' }}>
            {label}
          </span>
        )}
      </label>
    )
  },
)

Switch.displayName = 'Switch'

export { Switch }
export type { SwitchProps }
