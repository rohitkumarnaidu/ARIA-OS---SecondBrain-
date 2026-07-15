'use client'

import { memo, useMemo } from 'react'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'

interface HabitCalendarProps {
  year: number
  month: number
  completions: Set<string>
  loading?: boolean
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export const HabitCalendar = memo(function HabitCalendar({
  year,
  month,
  completions,
  loading,
}: HabitCalendarProps) {
  const daysInMonth = useMemo(() => {
    return new Date(year, month, 0).getDate()
  }, [year, month])

  const firstDayOfWeek = useMemo(() => {
    return new Date(year, month - 1, 1).getDay()
  }, [year, month])

  const yesterday = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() - 1)
    return d.toISOString().split('T')[0]
  }, [])

  const today = useMemo(() => {
    return new Date().toISOString().split('T')[0]
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton variant="text" className="w-48" />
        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: 35 }).map((_, i) => (
            <Skeleton key={i} variant="text" className="h-8 w-8 rounded" />
          ))}
        </div>
      </div>
    )
  }

  const cells: { day: number; dateStr: string; isToday: boolean; isPast: boolean }[] = []
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    cells.push({
      day,
      dateStr,
      isToday: dateStr === today,
      isPast: dateStr <= yesterday,
    })
  }

  const blanks = Array.from({ length: firstDayOfWeek }).fill(null) as null[]

  return (
    <div role="grid" aria-label={`Habit calendar for ${month}/${year}`}>
      <div className="grid grid-cols-7 gap-1 mb-1">
        {DAYS.map((d) => (
          <div key={d} className="text-center text-xs font-medium text-text-tertiary py-1">
            {d}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {blanks.map((_, i) => (
          <div key={`blank-${i}`} className="h-8 w-8" />
        ))}
        {cells.map((cell) => {
          const completed = completions.has(cell.dateStr)
          return (
            <div
              key={cell.dateStr}
              className={cn(
                'h-8 w-8 rounded-md flex items-center justify-center text-xs transition-colors',
                completed && !cell.isToday
                  ? 'bg-accent-success text-white'
                  : cell.isToday && completed
                    ? 'bg-accent-primary text-white ring-2 ring-accent-primary/50'
                    : cell.isToday
                      ? 'bg-accent-primary/10 text-text-primary border border-accent-primary/30'
                      : cell.isPast
                        ? 'bg-background-elevated text-text-tertiary'
                        : 'bg-background-elevated/50 text-text-tertiary',
              )}
              role="gridcell"
              aria-label={`${cell.dateStr}${completed ? ' — completed' : ''}`}
              title={`${cell.dateStr}${completed ? ' ✓' : ''}`}
            >
              {cell.day}
            </div>
          )
        })}
      </div>
    </div>
  )
})
