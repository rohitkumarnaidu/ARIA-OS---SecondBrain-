import { forwardRef, InputHTMLAttributes, useId } from 'react'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'size' | 'onChange'> {
  size?: 'sm' | 'md'
  indeterminate?: boolean
  error?: boolean
  label?: string
  onChange?: (checked: boolean) => void
}

const boxSizes = { sm: 'h-4 w-4', md: 'h-5 w-5' }
const iconSizes = { sm: 'h-3 w-3', md: 'h-3.5 w-3.5' }

const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, size = 'md', indeterminate, error, disabled, label, checked, onChange, id, ...props }, ref) => {
    const genId = useId()
    const inputId = id || genId

    return (
      <label
        htmlFor={inputId}
        className={clsx(
          'inline-flex items-center gap-2 select-none',
          disabled ? 'cursor-not-allowed' : 'cursor-pointer',
          className
        )}
      >
        <span className="relative inline-flex items-center justify-center">
          <input
            ref={ref}
            id={inputId}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            onChange={(e) => onChange?.(e.target.checked)}
            aria-checked={indeterminate ? 'mixed' : checked}
            aria-invalid={error}
            aria-disabled={disabled}
            className="sr-only peer"
            {...props}
          />
          <span
            className={clsx(
              'flex items-center justify-center rounded transition-colors',
              boxSizes[size],
              disabled && 'opacity-40',
              error && !checked
                ? 'border-accent-error'
                : 'border-border-default',
              checked || indeterminate
                ? 'bg-accent-primary border-accent-primary'
                : 'bg-transparent border-2',
              !disabled && !error && 'peer-hover:border-accent-primary',
              !disabled && checked && 'peer-hover:bg-accent-primary-hover peer-hover:border-accent-primary-hover',
              !disabled && 'peer-focus-visible:ring-2 peer-focus-visible:ring-accent-primary/80 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-background-page'
            )}
          >
            <AnimatePresence mode="wait">
              {indeterminate ? (
                <motion.svg
                  key="indeterminate"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                  className={clsx('text-white', iconSizes[size])}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                >
                  <line x1="5" y1="12" x2="19" y2="12" />
                </motion.svg>
              ) : checked ? (
                <motion.svg
                  key="checked"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                  className={clsx('text-white', iconSizes[size])}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </motion.svg>
              ) : null}
            </AnimatePresence>
          </span>
        </span>
        {label && (
          <span className={clsx(
            'text-body text-text-primary',
            disabled && 'text-text-disabled'
          )}>
            {label}
          </span>
        )}
      </label>
    )
  }
)

Checkbox.displayName = 'Checkbox'

export { Checkbox }
export type { CheckboxProps }
