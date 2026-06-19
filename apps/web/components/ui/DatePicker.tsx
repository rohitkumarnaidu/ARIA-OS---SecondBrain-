'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CalendarIcon } from 'lucide-react'
import { cn } from './utils'
import { Calendar } from './Calendar'

interface DatePickerProps {
  value?: Date
  onChange?: (date: Date) => void
  minDate?: Date
  maxDate?: Date
  disabled?: boolean
  className?: string
  placeholder?: string
}

function formatDate(date: Date): string {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`
}

function DatePicker({ value, onChange, minDate, maxDate, disabled = false, className, placeholder = 'Pick a date' }: DatePickerProps) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
      setOpen(false)
    }
  }, [])

  useEffect(() => {
    if (open) document.addEventListener('mousedown', handleClickOutside)
    else document.removeEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open, handleClickOutside])

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => { if (!disabled) setOpen(!open) }}
        disabled={disabled}
        className={cn(
          'flex items-center w-full rounded-lg px-3 py-2 text-sm transition-colors',
          'bg-background-input border border-border',
          'hover:border-border-light',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          disabled && 'opacity-50 cursor-not-allowed',
        )}
        style={{ minHeight: '44px' }}
      >
        <CalendarIcon size={16} className="mr-2 shrink-0" style={{ color: 'var(--text-tertiary)' }} />
        <span style={{ color: value ? 'var(--text-primary)' : 'var(--text-tertiary)' }}>
          {value ? formatDate(value) : placeholder}
        </span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.95 }}
            transition={{ duration: 0.12 }}
            className="absolute left-0 mt-1 z-popover rounded-xl p-4"
            style={{ background: 'var(--background-card)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-elevation-3)' }}
          >
            <Calendar
              value={value}
              onChange={(date) => { onChange?.(date); setOpen(false) }}
              minDate={minDate}
              maxDate={maxDate}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

DatePicker.displayName = 'DatePicker'

export { DatePicker }
export type { DatePickerProps }
