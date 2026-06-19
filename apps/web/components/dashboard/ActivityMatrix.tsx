'use client'

import { useMemo, useState } from 'react'
import { format, subDays, startOfDay } from 'date-fns'
import { TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface ActivityData {
  date: string
  count: number
}

interface ActivityMatrixProps {
  data: ActivityData[]
}

const TOTAL_CELLS = 84
const COLS = 7

function getIntensityClass(count: number): string {
  if (count === 0) return 'bg-accent-primary/5'
  if (count <= 2) return 'bg-accent-primary/25'
  if (count <= 5) return 'bg-accent-primary/50'
  if (count <= 10) return 'bg-accent-primary/75'
  return 'bg-accent-primary shadow-glow-sm'
}

export function ActivityMatrix({ data }: ActivityMatrixProps) {
  const [tooltip, setTooltip] = useState<{ text: string; x: number; y: number } | null>(null)

  const dataMap = useMemo(() => {
    const map = new Map<string, number>()
    for (const entry of data) {
      map.set(entry.date, (map.get(entry.date) || 0) + entry.count)
    }
    return map
  }, [data])

  const { cells, monthLabels } = useMemo(() => {
    const today = startOfDay(new Date())
    const dates = Array.from({ length: TOTAL_CELLS }, (_, i) => subDays(today, TOTAL_CELLS - 1 - i))

    const cells = dates.map((date) => {
      const dateStr = format(date, 'yyyy-MM-dd')
      const count = dataMap.get(dateStr) || 0
      return { date, dateStr, count }
    })

    const monthLabels: { label: string; col: number; span: number }[] = []
    let monthStart = 0
    for (let i = 0; i <= TOTAL_CELLS; i++) {
      const d = i < TOTAL_CELLS ? cells[i].date : null
      const startMonth = cells[monthStart].date.getMonth()
      const currentMonth = d ? d.getMonth() : -1
      if (currentMonth !== startMonth || d === null) {
        const startCol = monthStart % COLS
        const endCell = i - 1
        const endCol = endCell % COLS
        monthLabels.push({
          label: format(cells[monthStart].date, 'MMM'),
          col: startCol,
          span: endCol >= startCol ? endCol - startCol + 1 : COLS - startCol,
        })
        monthStart = i
      }
    }

    return { cells, monthLabels }
  }, [dataMap])

  const rows = useMemo(() => {
    const result: typeof cells[] = []
    for (let i = 0; i < TOTAL_CELLS; i += COLS) {
      result.push(cells.slice(i, i + COLS))
    }
    return result
  }, [cells])

  const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>, count: number, dateStr: string) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setTooltip({
      text: `${count} ${count === 1 ? 'activity' : 'activities'} on ${format(new Date(dateStr + 'T00:00:00'), 'MMM d')}`,
      x: rect.left + rect.width / 2,
      y: rect.top - 8,
    })
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
            <TrendingUp size={20} className="text-accent-secondary" />
          </div>
          <div>
            <h2 className="text-lg font-display font-semibold text-text-primary">Activity Matrix</h2>
            <p className="text-xs text-text-tertiary">Your productivity over time</p>
          </div>
        </div>
        <span className="text-xs text-text-tertiary">Last 12 weeks</span>
      </div>

      <div className="overflow-x-auto pb-2 no-scrollbar">
        <div className="min-w-[600px]">
          <div className="grid grid-cols-7 mb-1" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
            {Array.from({ length: COLS }).map((_, col) => {
              const label = monthLabels.find((m) => m.col === col)
              return (
                <div
                  key={col}
                  className="text-[10px] font-medium text-text-tertiary text-center h-4 leading-4"
                >
                  {label ? label.label : ''}
                </div>
              )
            })}
          </div>

          <div
            className="grid gap-[3px]"
            style={{
              gridTemplateColumns: `repeat(${COLS}, 1fr)`,
              gridTemplateRows: `repeat(${rows.length}, 1fr)`,
            }}
          >
            {cells.map((cell, i) => (
              <div
                key={cell.dateStr}
                className={cn(
                  'aspect-square rounded-sm transition-all duration-200 cursor-pointer hover:scale-125 hover:z-10 relative',
                  getIntensityClass(cell.count),
                )}
                onMouseEnter={(e) => handleMouseEnter(e, cell.count, cell.dateStr)}
                onMouseLeave={() => setTooltip(null)}
                role="gridcell"
                aria-label={`${cell.count} activities on ${format(cell.date, 'MMM d, yyyy')}`}
              />
            ))}
          </div>

          <div className="flex items-center gap-2 mt-4 text-xs text-text-tertiary">
            <span>Less</span>
            <div className="w-4 h-4 rounded-sm bg-accent-primary/5" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary/25" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary/50" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary/75" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary shadow-glow-sm" />
            <span className="ml-1">More</span>
          </div>
        </div>
      </div>

      {tooltip && (
        <div
          className="fixed z-tooltip px-3 py-1.5 rounded-lg bg-background-elevated border border-border text-xs text-text-primary whitespace-nowrap pointer-events-none shadow-glow-sm"
          style={{
            left: tooltip.x,
            top: tooltip.y,
            transform: 'translate(-50%, -100%)',
          }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  )
}
