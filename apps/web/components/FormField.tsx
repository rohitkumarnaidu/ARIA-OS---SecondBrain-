import { useId } from 'react'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'

interface FormFieldProps {
  label: string
  required?: boolean
  helperText?: string
  error?: string
  characterCount?: { current: number; max: number }
  layout?: 'vertical' | 'horizontal'
  htmlFor?: string
  children: React.ReactNode
  className?: string
}

const shakeVariants = {
  initial: { x: 0 },
  shake: {
    x: [0, -4, 4, -4, 4, 0],
    transition: { duration: 0.3, ease: 'easeInOut' },
  },
}

function FormField({
  label,
  required,
  helperText,
  error,
  characterCount,
  layout = 'vertical',
  htmlFor,
  children,
  className,
}: FormFieldProps) {
  const genId = useId()
  const fieldId = htmlFor || genId
  const messageId = `${fieldId}-message`
  const characterCountId = `${fieldId}-count`

  return (
    <div
      className={clsx(
        layout === 'horizontal'
          ? 'grid grid-cols-[180px_1fr] gap-4 items-start'
          : 'flex flex-col',
        className
      )}
    >
      <label
        htmlFor={fieldId}
        className={clsx(
          'text-label text-text-secondary',
          layout === 'horizontal' && 'pt-3'
        )}
      >
        {label}
        {required && (
          <span className="text-accent-error ml-0.5" aria-hidden="true">*</span>
        )}
        {required && <span className="sr-only">(required)</span>}
      </label>

      <div className="flex flex-col">
        {children}

        <div className="flex items-center justify-between mt-1">
          <AnimatePresence mode="wait">
            {error ? (
              <motion.p
                key="error"
                variants={shakeVariants}
                initial="initial"
                animate="shake"
                exit="initial"
                id={messageId}
                role="alert"
                aria-live="polite"
                className="text-caption text-accent-error"
              >
                {error}
              </motion.p>
            ) : helperText ? (
              <p
                key="helper"
                id={messageId}
                className="text-caption text-text-tertiary"
              >
                {helperText}
              </p>
            ) : null}
          </AnimatePresence>

          {characterCount && (
            <p
              id={characterCountId}
              className={clsx(
                'text-caption ml-auto',
                characterCount.current > characterCount.max
                  ? 'text-accent-error'
                  : 'text-text-tertiary'
              )}
            >
              {characterCount.current}/{characterCount.max}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

FormField.displayName = 'FormField'

export { FormField }
export type { FormFieldProps }
