'use client'

import { memo,  forwardRef  } from 'react'
import { motion } from 'framer-motion'
import { cn } from './utils'

interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  label?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeMap = {
  sm: { track: 'h-5 w-9', knob: 'h-3.5 w-3.5', translate: 'translateX(100%)' },
  md: { track: 'h-6 w-11', knob: 'h-5 w-5', translate: 'translateX(100%)' },
  lg: { track: 'h-7 w-14', knob: 'h-6 w-6', translate: 'translateX(112%)' },
}

const Toggle = memo(forwardRef<HTMLButtonElement, ToggleProps>(
  ({ checked, onChange, disabled = false, label, size = 'md', className }, ref) => {
    const id = `toggle-${Math.random().toString(36).slice(2, 9)}`
    const dims = sizeMap[size]

    return (
      <label
        htmlFor={id}
        className={cn(
          'inline-flex items-center gap-3 cursor-pointer select-none',
          disabled && 'opacity-50 cursor-not-allowed',
          className,
        )}
      >
        <button
          ref={ref}
          id={id}
          role="switch"
          aria-checked={checked}
          aria-disabled={disabled || undefined}
          disabled={disabled}
          onClick={() => { if (!disabled) onChange(!checked) }}
          onKeyDown={(e) => { if ((e.key === 'Enter' || e.key === ' ') && !disabled) { e.preventDefault(); onChange(!checked) } }}
          className={cn(
            'relative inline-flex shrink-0 rounded-full border-2 border-transparent transition-colors duration-200',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background)]',
            dims.track,
          )}
          style={{ background: checked ? 'var(--accent-primary)' : 'var(--surface-tertiary)' }}
        >
          <motion.span
            layout
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className={cn(
              'pointer-events-none block rounded-full shadow-lg ring-0',
              dims.knob,
            )}
            style={{
              background: '#FFFFFF',
              transform: checked ? dims.translate : 'translateX(0)',
            }}
          />
        </button>
        {label && (
          <span className="text-sm" style={{ color: 'var(--text-primary)' }}>
            {label}
          </span>
        )}
      </label>
    )
  },
)
)
Toggle.displayName = 'Toggle'

export { Toggle }
export type { ToggleProps }
