'use client'

import { memo, useMemo } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import type { IncomeEntry } from '@/lib/types'

interface IncomeChartProps {
  entries: IncomeEntry[]
  loading?: boolean
  period?: 'week' | 'month'
  className?: string
}

export const IncomeChart = memo(function IncomeChart({
  entries,
  loading,
  period = 'month',
  className,
}: IncomeChartProps) {
  const chartData = useMemo(() => {
    if (!entries || entries.length === 0) return []

    const grouped = new Map<string, number>()
    for (const entry of entries) {
      const date = entry.date.slice(0, period === 'month' ? 7 : 10)
      grouped.set(date, (grouped.get(date) || 0) + entry.amount)
    }

    return Array.from(grouped.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-12)
  }, [entries, period])

  const maxValue = useMemo(() => {
    return Math.max(...chartData.map(([, v]) => v), 1)
  }, [chartData])

  if (loading) {
    return (
      <div className={cn('space-y-3', className)} role="region" aria-label="Income chart loading">
        <Skeleton variant="chart" className="h-48 w-full" />
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)} role="region" aria-label="Income chart">
        <p className="text-text-tertiary text-sm">No income data to display</p>
      </div>
    )
  }

  return (
    <div className={cn('space-y-2', className)} role="region" aria-label={`Income chart by ${period}`}>
      <div className="flex items-end gap-1.5 h-48">
        {chartData.map(([label, value]) => {
          const height = (value / maxValue) * 100
          const dateLabel = period === 'month'
            ? new Date(label + '-02').toLocaleDateString(undefined, { month: 'short' })
            : new Date(label).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })

          return (
            <div
              key={label}
              className="flex-1 flex flex-col items-center gap-1 group"
            >
              <span className="text-[10px] text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity">
                ${Math.round(value)}
              </span>
              <motion.div
                initial={{ height: 0 }}
                animate={{ height: `${height}%` }}
                transition={{ duration: 0.4, ease: 'easeOut' }}
                className="w-full rounded-t-md bg-gradient-to-t from-accent-success/60 to-accent-success/30 hover:from-accent-success/80 hover:to-accent-success/50 transition-colors cursor-pointer"
                style={{ minHeight: height > 0 ? 4 : 0 }}
                role="img"
                aria-label={`${dateLabel}: $${Math.round(value)}`}
              />
              <span className="text-[10px] text-text-tertiary truncate w-full text-center">
                {dateLabel}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
})
