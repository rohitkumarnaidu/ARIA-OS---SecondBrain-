'use client'

import { cn } from '@/components/ui/utils'

interface ScoreTooltipProps {
  criteria: { label: string; value: number }[]
  className?: string
}

const barColor = (value: number) => {
  if (value >= 90) return 'var(--accent-neon)'
  if (value >= 70) return 'var(--accent-primary)'
  if (value >= 50) return 'var(--accent-warning)'
  return 'var(--accent-error)'
}

export function ScoreTooltip({ criteria, className }: ScoreTooltipProps) {
  return (
    <div
      className={cn(
        'min-w-[200px] p-3 rounded-xl backdrop-blur-2xl z-50',
        'bg-[var(--glass-heavy)] border border-[var(--glass-medium)]',
        className
      )}
    >
      <p className="text-[11px] font-semibold text-[var(--text-tertiary)] uppercase tracking-wider mb-2">
        Match Breakdown
      </p>
      <div className="space-y-2">
        {criteria.map((c) => (
          <div key={c.label}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-[var(--text-secondary)]">{c.label}</span>
              <span
                className="text-xs font-semibold tabular-nums"
                style={{ color: barColor(c.value) }}
              >
                {c.value}%
              </span>
            </div>
            <div className="h-1 rounded-full bg-[var(--background-elevated)] overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${c.value}%`,
                  backgroundColor: barColor(c.value),
                  boxShadow: `0 0 6px ${barColor(c.value)}`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
