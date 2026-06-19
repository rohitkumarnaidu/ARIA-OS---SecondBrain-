'use client'

import { useState, useMemo, useCallback } from 'react'
import { Clock } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import type { HeatmapCell } from '@/types/analytics'

interface FocusHeatmapProps {
  data: HeatmapCell[]
}

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const HOURS = Array.from({ length: 17 }, (_, i) => i + 6)

function getIntensity(value: number): string {
  if (value === 0) return 'bg-accent-primary/5'
  if (value <= 1) return 'bg-accent-primary/20'
  if (value <= 3) return 'bg-accent-primary/40'
  if (value <= 5) return 'bg-accent-primary/65'
  return 'bg-accent-primary shadow-glow-sm'
}

export function FocusHeatmap({ data }: FocusHeatmapProps) {
  const [tooltip, setTooltip] = useState<{ text: string; x: number; y: number } | null>(null)

  const dataMap = useMemo(() => {
    const map = new Map<string, number>()
    for (const cell of data) {
      map.set(`${cell.day}-${cell.hour}`, cell.value)
    }
    return map
  }, [data])

  const getValue = useCallback(
    (day: string, hour: number) => dataMap.get(`${day}-${hour}`) ?? 0,
    [dataMap],
  )

  const handleMouseEnter = useCallback(
    (e: React.MouseEvent<HTMLDivElement>, day: string, hour: number, value: number) => {
      const rect = e.currentTarget.getBoundingClientRect()
      setTooltip({
        text: `${day} ${hour}:00 — ${value} ${value === 1 ? 'hour' : 'hours'} focused`,
        x: rect.left + rect.width / 2,
        y: rect.top - 8,
      })
    },
    [],
  )

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
          <Clock size={20} className="text-accent-primary" />
        </div>
        <div>
          <h2 className="text-lg font-display font-semibold text-text-primary">Focus Heatmap</h2>
          <p className="text-xs text-text-tertiary">Deep work intensity by time & day</p>
        </div>
      </div>

      <div className="overflow-x-auto pb-2 no-scrollbar">
        <div className="min-w-[560px]">
          <div className="flex gap-1 mb-1">
            <div className="w-10 shrink-0" />
            {DAYS.map((day) => (
              <div
                key={day}
                className="flex-1 text-[10px] font-medium text-text-tertiary text-center h-4 leading-4"
              >
                {day}
              </div>
            ))}
          </div>

          {HOURS.map((hour) => (
            <div key={hour} className="flex gap-1 mb-[3px]">
              <div className="w-10 shrink-0 text-[10px] font-medium text-text-tertiary leading-5 text-right pr-2">
                {hour}
              </div>
              {DAYS.map((day) => {
                const value = getValue(day, hour)
                return (
                  <div
                    key={`${day}-${hour}`}
                    className={cn(
                      'flex-1 aspect-[3/2] rounded-sm transition-all duration-200 cursor-pointer',
                      'hover:scale-110 hover:z-10 relative',
                      getIntensity(value),
                    )}
                    onMouseEnter={(e) => handleMouseEnter(e, day, hour, value)}
                    onMouseLeave={() => setTooltip(null)}
                    role="gridcell"
                    aria-label={`${day} ${hour}:00 — ${value} hours`}
                  />
                )
              })}
            </div>
          ))}

          <div className="flex items-center gap-2 mt-4 text-[10px] text-text-tertiary">
            <span>Low</span>
            <div className="w-4 h-4 rounded-sm bg-accent-primary/5" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary/20" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary/40" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary/65" />
            <div className="w-4 h-4 rounded-sm bg-accent-primary shadow-glow-sm" />
            <span>High</span>
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
