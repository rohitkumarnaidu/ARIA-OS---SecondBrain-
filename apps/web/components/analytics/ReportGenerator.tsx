'use client'

import { useState, useCallback, useMemo } from 'react'
import { format, subDays } from 'date-fns'
import { Download, FileSpreadsheet, FileJson, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/utils'

interface ReportGeneratorProps {
  onExport: (format: 'csv' | 'json', metrics: string[], dateRange: { start: string; end: string }) => void
}

const METRICS = [
  { id: 'tasks', label: 'Tasks' },
  { id: 'courses', label: 'Courses' },
  { id: 'habits', label: 'Habits' },
  { id: 'sleep', label: 'Sleep' },
  { id: 'income', label: 'Income' },
  { id: 'focus', label: 'Focus' },
  { id: 'goals', label: 'Goals' },
] as const

const PRESETS = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '90d', days: 90 },
] as const

export function ReportGenerator({ onExport }: ReportGeneratorProps) {
  const [selectedMetrics, setSelectedMetrics] = useState<Set<string>>(new Set(['tasks', 'focus']))
  const [preset, setPreset] = useState<number>(7)
  const [custom, setCustom] = useState(false)
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 7), 'yyyy-MM-dd'))
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [loading, setLoading] = useState<'csv' | 'json' | null>(null)

  const toggleMetric = useCallback((id: string) => {
    setSelectedMetrics((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const handlePreset = useCallback((days: number) => {
    setPreset(days)
    setCustom(false)
    setStartDate(format(subDays(new Date(), days), 'yyyy-MM-dd'))
    setEndDate(format(new Date(), 'yyyy-MM-dd'))
  }, [])

  const handleCustom = useCallback(() => {
    setCustom(true)
  }, [])

  const handleExport = useCallback(
    async (format: 'csv' | 'json') => {
      setLoading(format)
      await new Promise((r) => setTimeout(r, 800))

      const metrics = Array.from(selectedMetrics)
      const dateRange = { start: startDate, end: endDate }

      const mockData = metrics.reduce(
        (acc, m) => ({
          ...acc,
          [m]: Math.floor(Math.random() * 100),
        }),
        {} as Record<string, number>,
      )

      if (format === 'csv') {
        const header = `Report,Date Range,${metrics.join(',')}\n`
        const row = `Analytics,${startDate} to ${endDate},${metrics.map(() => Math.floor(Math.random() * 100)).join(',')}\n`
        const blob = new Blob([header + row], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `analytics-report-${startDate}-to-${endDate}.csv`
        a.click()
        URL.revokeObjectURL(url)
      } else {
        const json = { dateRange, metrics: mockData, generatedAt: new Date().toISOString() }
        const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `analytics-report-${startDate}-to-${endDate}.json`
        a.click()
        URL.revokeObjectURL(url)
      }

      onExport(format, metrics, dateRange)
      setLoading(null)
    },
    [selectedMetrics, startDate, endDate, onExport],
  )

  const dateLabel = useMemo(() => {
    if (custom) return `${startDate} — ${endDate}`
    return `Last ${preset} days`
  }, [custom, preset, startDate, endDate])

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
          <Download size={20} className="text-accent-primary" />
        </div>
        <div>
          <h2 className="text-lg font-display font-semibold text-text-primary">Report Generator</h2>
          <p className="text-xs text-text-tertiary">Export your analytics data</p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-2 block">
            Date Range
          </label>
          <div className="flex items-center gap-2 mb-2">
            {PRESETS.map((p) => (
              <button
                key={p.days}
                onClick={() => handlePreset(p.days)}
                className={cn(
                  'px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200',
                  !custom && preset === p.days
                    ? 'bg-accent-primary/15 text-accent-primary'
                    : 'bg-background-elevated text-text-tertiary hover:text-text-secondary',
                )}
              >
                {p.label}
              </button>
            ))}
            <button
              onClick={handleCustom}
              className={cn(
                'px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200',
                custom
                  ? 'bg-accent-primary/15 text-accent-primary'
                  : 'bg-background-elevated text-text-tertiary hover:text-text-secondary',
              )}
            >
              Custom
            </button>
          </div>
          {custom && (
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="input text-xs flex-1"
              />
              <span className="text-text-tertiary text-xs">to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="input text-xs flex-1"
              />
            </div>
          )}
        </div>

        <div>
          <label className="text-xs font-medium text-text-tertiary uppercase tracking-wider mb-2 block">
            Metrics
          </label>
          <div className="flex flex-wrap gap-2">
            {METRICS.map((m) => (
              <button
                key={m.id}
                onClick={() => toggleMetric(m.id)}
                className={cn(
                  'px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200 border',
                  selectedMetrics.has(m.id)
                    ? 'bg-accent-primary/15 text-accent-primary border-accent-primary/30'
                    : 'bg-background-elevated text-text-tertiary border-border hover:text-text-secondary',
                )}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        <div className="pt-2">
          <p className="text-[10px] text-text-disabled mb-3">
            {selectedMetrics.size} metric{selectedMetrics.size !== 1 ? 's' : ''} selected &middot; {dateLabel}
          </p>
          <div className="flex gap-2">
            <Button
              onClick={() => handleExport('csv')}
              disabled={selectedMetrics.size === 0 || loading !== null}
              variant="primary" size="sm" className="flex-1"
            >
              {loading === 'csv' ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <FileSpreadsheet size={14} />
              )}
              CSV
            </Button>
            <Button
              onClick={() => handleExport('json')}
              disabled={selectedMetrics.size === 0 || loading !== null}
              variant="secondary" size="sm" className="flex-1"
            >
              {loading === 'json' ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <FileJson size={14} />
              )}
              JSON
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
