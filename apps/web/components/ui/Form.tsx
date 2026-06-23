'use client'

import { memo,  createContext, useContext, useId, type ReactNode, type HTMLAttributes  } from 'react'
import { cn } from './utils'

interface FormFieldContextValue {
  id: string
  name?: string
  error?: string
}

const FormFieldContext = createContext<FormFieldContextValue | null>(null)

function useFormField() {
  const ctx = useContext(FormFieldContext)
  if (!ctx) throw new Error('FormField components must be used within a FormField')
  return ctx
}

interface FormFieldProps {
  name?: string
  error?: string
  children: ReactNode
  className?: string
}

const FormField = memo(function FormField({ name, error, children, className }: FormFieldProps) {
  const id = useId()
  return (
    <FormFieldContext.Provider value={{ id, name, error }}>
      <div className={cn('space-y-1.5', className)}>
        {children}
      </div>
    </FormFieldContext.Provider>
  )
})

FormField.displayName = 'FormField'

interface FormLabelProps extends HTMLAttributes<HTMLLabelElement> {
  children: ReactNode
}

const FormLabel = memo(function FormLabel({ children, className, ...props }: FormLabelProps) {
  const { id, error } = useFormField()
  return (
    <label
      htmlFor={id}
      className={cn(
        'block text-sm font-medium',
        error ? 'text-accent-error' : 'text-text-primary',
        className,
      )}
      {...props}
    >
      {children}
    </label>
  )
})

FormLabel.displayName = 'FormLabel'

interface FormControlProps {
  children: ReactNode
  className?: string
}

const FormControl = memo(function FormControl({ children, className }: FormControlProps) {
  const { id, error } = useFormField()
  return (
    <div
      className={cn('relative', className)}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-message` : undefined}
    >
      {children}
    </div>
  )
})

FormControl.displayName = 'FormControl'

interface FormMessageProps {
  children?: ReactNode
  className?: string
}

const FormMessage = memo(function FormMessage({ children, className }: FormMessageProps) {
  const { id, error } = useFormField()
  const msg = children ?? error
  if (!msg) return null
  return (
    <p
      id={`${id}-message`}
      className={cn('text-sm', error ? 'text-accent-error' : 'text-text-tertiary', className)}
      role={error ? 'alert' : undefined}
    >
      {msg}
    </p>
  )
})

FormMessage.displayName = 'FormMessage'

interface FormDescriptionProps {
  children: ReactNode
  className?: string
}

const FormDescription = memo(function FormDescription({ children, className }: FormDescriptionProps) {
  const { id } = useFormField()
  return (
    <p
      id={`${id}-description`}
      className={cn('text-sm text-text-tertiary', className)}
    >
      {children}
    </p>
  )
})

FormDescription.displayName = 'FormDescription'

export { FormField, FormLabel, FormControl, FormMessage, FormDescription }
export type { FormFieldProps, FormLabelProps, FormControlProps, FormMessageProps, FormDescriptionProps }
