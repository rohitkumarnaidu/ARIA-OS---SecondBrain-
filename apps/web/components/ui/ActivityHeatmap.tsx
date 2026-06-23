'use client'

import { memo,  useMemo, useState  } from 'react'
import { cn } from './utils'

interface ActivityHeatmapProps {
  data: { date: string; count: number }[]
  className?: string
}

interface DayCell {
  date: string
  count: number
  dayOfWeek: number
  weekIndex: number
}

const CELL_SIZE = 12
const CELL_GAP = 2
const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const MONTH_LABELS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]

function getIntensity(count: number): number {
  if (count === 0) return 0
  if (count <= 3) return 1
  if (count <= 7) return 2
  if (count <= 15) return 3
  return 4
}

const intensityColors = [
  'bg-[var(--surface-tertiary)]',
  'bg-[var(--accent-primary)]/20',
  'bg-[var(--accent-primary)]/40',
  'bg-[var(--accent-primary)]/60',
  'bg-[var(--accent-primary)]/85',
]

const ActivityHeatmap = memo(function ActivityHeatmap({ data, className }: ActivityHeatmapProps) {
  const [tooltip, setTooltip] = useState<{ date: string; count: number; x: number; y: number } | null>(null)

  const lookup = useMemo(() => {
    const map = new Map<string, number>()
    for (const entry of data) {
      map.set(entry.date, entry.count)
    }
    return map
  }, [data])

  const cells = useMemo(() => {
    const result: DayCell[] = []
    const now = new Date()
    const end = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const start = new Date(end)
    start.setDate(start.getDate() - 364)
    start.setHours(0, 0, 0, 0)

    const current = new Date(start)
    while (current <= end) {
      const dateStr = current.toISOString().slice(0, 10)
      const dayOfWeek = current.getDay()
      const dayIndex = dayOfWeek === 0 ? 6 : dayOfWeek - 1
      const diffMs = current.getTime() - start.getTime()
      const weekIndex = Math.floor(diffMs / (7 * 24 * 60 * 60 * 1000))

      result.push({
        date: dateStr,
        count: lookup.get(dateStr) ?? 0,
        dayOfWeek: dayIndex,
        weekIndex,
      })

      current.setDate(current.getDate() + 1)
    }
    return result
  }, [lookup])

  const weeks = useMemo(() => {
    const grouped: DayCell[][] = []
    for (const cell of cells) {
      if (!grouped[cell.weekIndex]) grouped[cell.weekIndex] = []
      grouped[cell.weekIndex].push(cell)
    }
    return grouped
  }, [cells])

  const monthMarkers = useMemo(() => {
    const markers: { label: string; weekIndex: number }[] = []
    let lastMonth = -1
    for (const cell of cells) {
      const month = new Date(cell.date).getMonth()
      if (month !== lastMonth) {
        markers.push({ label: MONTH_LABELS[month], weekIndex: cell.weekIndex })
        lastMonth = month
      }
    }
    return markers
  }, [cells])

  const totalWidth = weeks.length * (CELL_SIZE + CELL_GAP)

  return (
    <div className={cn('select-none', className)}>
      <div className="relative" style={{ paddingLeft: 36 }}>
        <div className="flex gap-[2px] mb-1" style={{ marginLeft: 0 }} aria-hidden="true">
          {monthMarkers.map((m, i) => (
            <div
              key={`${m.label}-${i}`}
              className="text-[10px] font-medium text-[var(--text-tertiary)] leading-none"
              style={{
                position: 'absolute',
                left: 36 + m.weekIndex * (CELL_SIZE + CELL_GAP),
                top: 0,
              }}
            >
              {m.label}
            </div>
          ))}
        </div>

        <div className="flex gap-1" style={{ marginTop: 14 }}>
          <div className="flex flex-col gap-[2px] mr-1" aria-hidden="true">
            {DAY_LABELS.map((label, i) => (
              <div
                key={label}
                className="text-[10px] font-medium leading-none text-[var(--text-tertiary)]"
                style={{ height: CELL_SIZE, display: 'flex', alignItems: 'center' }}
              >
                {i % 2 === 0 ? label : ''}
              </div>
            ))}
          </div>

          <div className="flex gap-[2px]" role="grid" aria-label="Activity heatmap">
            {weeks.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-[2px]" role="row">
                {week.map((cell) => {
                  const level = getIntensity(cell.count)
                  const isToday = cell.date === new Date().toISOString().slice(0, 10)

                  return (
                    <div
                      key={cell.date}
                      role="gridcell"
                      aria-label={`${cell.date}: ${cell.count} activities`}
                      className={cn(
                        'rounded-[2px] transition-colors duration-150',
                        intensityColors[level],
                        isToday && 'ring-1 ring-[var(--accent-primary)]',
                      )}
                      style={{ width: CELL_SIZE, height: CELL_SIZE }}
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect()
                        setTooltip({ date: cell.date, count: cell.count, x: rect.left, y: rect.bottom + 4 })
                      }}
                      onMouseLeave={() => setTooltip(null)}
                    />
                  )
                })}
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-1 mt-2 justify-end" aria-hidden="true">
          <span className="text-[10px] text-[var(--text-tertiary)]">Less</span>
          {[0, 1, 2, 3, 4].map((level) => (
            <div
              key={level}
              className={cn('rounded-[2px]', intensityColors[level])}
              style={{ width: CELL_SIZE, height: CELL_SIZE }}
            />
          ))}
          <span className="text-[10px] text-[var(--text-tertiary)]">More</span>
        </div>
      </div>

      {tooltip && (
        <div
          className="fixed z-[var(--z-tooltip)] px-2 py-1 rounded-md text-xs shadow-lg pointer-events-none"
          style={{
            left: tooltip.x,
            top: tooltip.y,
            backgroundColor: 'var(--popover)',
            border: '1px solid var(--border)',
            color: 'var(--popover-foreground)',
          }}
          role="tooltip"
        >
          {tooltip.count} activities on {tooltip.date}
        </div>
      )}
    </div>
  )
})

export { ActivityHeatmap }
export type { ActivityHeatmapProps }
