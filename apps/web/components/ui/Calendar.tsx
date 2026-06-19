'use client'

import { useMemo, useCallback } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from './utils'

interface CalendarProps {
  value?: Date
  onChange?: (date: Date) => void
  minDate?: Date
  maxDate?: Date
  disabledDates?: Date[]
  className?: string
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

function isSameDay(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function isDateDisabled(date: Date, minDate?: Date, maxDate?: Date, disabledDates?: Date[]): boolean {
  if (minDate && date < new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate())) return true
  if (maxDate && date > new Date(maxDate.getFullYear(), maxDate.getMonth(), maxDate.getDate())) return true
  if (disabledDates) return disabledDates.some((d) => isSameDay(d, date))
  return false
}

function Calendar({ value, onChange, minDate, maxDate, disabledDates, className }: CalendarProps) {
  const today = useMemo(() => new Date(), [])
  const currentYear = today.getFullYear()
  const currentMonth = today.getMonth()

  const viewDate = useMemo(() => value ?? today, [value, today])
  const viewYear = viewDate.getFullYear()
  const viewMonth = viewDate.getMonth()

  const grid = useMemo(() => {
    const firstDay = new Date(viewYear, viewMonth, 1)
    const startOffset = firstDay.getDay()
    const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate()
    const weeks: (number | null)[][] = []
    let week: (number | null)[] = []

    for (let i = 0; i < startOffset; i++) week.push(null)
    for (let d = 1; d <= daysInMonth; d++) {
      week.push(d)
      if (week.length === 7) { weeks.push(week); week = [] }
    }
    if (week.length > 0) { while (week.length < 7) week.push(null); weeks.push(week) }
    return weeks
  }, [viewYear, viewMonth])

  const navigate = useCallback(
    (delta: number) => {
      if (!onChange) return
      const next = new Date(viewYear, viewMonth + delta, 1)
      if (minDate && next < new Date(minDate.getFullYear(), minDate.getMonth(), 1)) return
      if (maxDate) {
        const lastOfNext = new Date(next.getFullYear(), next.getMonth() + 1, 0)
        if (lastOfNext > maxDate && next > maxDate) return
      }
      onChange(next)
    },
    [viewYear, viewMonth, onChange, minDate, maxDate],
  )

  const canGoPrev = useMemo(() => {
    if (!minDate || !onChange) return true
    return new Date(viewYear, viewMonth - 1, 1) >= new Date(minDate.getFullYear(), minDate.getMonth(), 1)
  }, [viewYear, viewMonth, minDate, onChange])

  const canGoNext = useMemo(() => {
    if (!maxDate || !onChange) return true
    return new Date(viewYear, viewMonth + 1, 1) <= new Date(maxDate.getFullYear(), maxDate.getMonth(), 1)
  }, [viewYear, viewMonth, maxDate, onChange])

  const handleSelect = (day: number) => {
    if (!onChange) return
    const date = new Date(viewYear, viewMonth, day)
    if (isDateDisabled(date, minDate, maxDate, disabledDates)) return
    onChange(date)
  }

  const dayBtn = cn(
    'flex items-center justify-center h-9 w-9 rounded-lg text-sm transition-all duration-150',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--background)]',
  )

  return (
    <div className={cn('w-fit', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-1">
        <button
          onClick={() => navigate(-1)}
          disabled={!canGoPrev}
          className={cn(dayBtn, 'text-text-secondary hover:bg-[var(--glass-heavy)] disabled:opacity-30 disabled:pointer-events-none')}
          aria-label="Previous month"
        >
          <ChevronLeft size={16} />
        </button>
        <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
          {MONTHS[viewMonth]} {viewYear}
        </span>
        <button
          onClick={() => navigate(1)}
          disabled={!canGoNext}
          className={cn(dayBtn, 'text-text-secondary hover:bg-[var(--glass-heavy)] disabled:opacity-30 disabled:pointer-events-none')}
          aria-label="Next month"
        >
          <ChevronRight size={16} />
        </button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 gap-1 mb-1">
        {DAYS.map((d) => (
          <div key={d} className="flex items-center justify-center h-9 w-9 text-xs font-medium" style={{ color: 'var(--text-tertiary)' }}>
            {d}
          </div>
        ))}
      </div>

      {/* Day grid */}
      <div className="grid grid-cols-7 gap-1">
        {grid.map((week, wi) =>
          week.map((day, di) => {
            if (day === null) return <div key={`empty-${wi}-${di}`} className="h-9 w-9" />

            const date = new Date(viewYear, viewMonth, day)
            const isToday = isSameDay(date, today)
            const isSelected = value && isSameDay(date, value)
            const disabled = isDateDisabled(date, minDate, maxDate, disabledDates)

            return (
              <button
                key={`${wi}-${di}`}
                onClick={() => handleSelect(day)}
                disabled={disabled}
                className={cn(
                  dayBtn,
                  isSelected && !disabled
                    ? 'bg-[var(--accent-primary)] text-white'
                    : isToday
                      ? 'border border-[var(--accent-primary)] text-text-primary'
                      : 'text-text-secondary hover:bg-[var(--glass-heavy)] hover:text-text-primary',
                  disabled && 'opacity-30 pointer-events-none line-through',
                )}
              >
                {day}
              </button>
            )
          }),
        )}
      </div>
    </div>
  )
}

Calendar.displayName = 'Calendar'

export { Calendar }
export type { CalendarProps }
