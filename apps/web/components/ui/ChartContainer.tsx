'use client'

import { memo,  type ReactElement  } from 'react'
import { ResponsiveContainer, type TooltipProps } from 'recharts'
import {
  type ValueType,
  type NameType,
} from 'recharts/types/component/DefaultTooltipContent'
import { cn } from './utils'

interface ChartContainerProps {
  title?: string
  description?: string
  height?: number
  children: ReactElement
  className?: string
}

const ChartTooltipContent = memo(function ChartTooltipContent({
  active,
  payload,
  label,
}: TooltipProps<ValueType, NameType>) {
  if (!active || !payload?.length) return null

  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg border"
      style={{
        backgroundColor: 'var(--popover)',
        borderColor: 'var(--border)',
        color: 'var(--popover-foreground)',
      }}
    >
      <p className="font-medium mb-1 text-text-primary">{label}</p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2">
          <span
            className="inline-block w-2 h-2 rounded-full shrink-0"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-text-secondary">{entry.name}:</span>
          <span className="font-medium text-text-primary">
            {typeof entry.value === 'number' ? entry.value.toLocaleString() : String(entry.value)}
          </span>
        </div>
      ))}
    </div>
  )
})

const ChartContainer = memo(function ChartContainer({
  title,
  description,
  height = 300,
  children,
  className,
}: ChartContainerProps) {
  return (
    <div className={cn('flex flex-col', className)}>
      {(title || description) && (
        <div className="mb-3">
          {title && (
            <h3 className="text-sm font-semibold text-text-primary font-display">
              {title}
            </h3>
          )}
          {description && (
            <p className="text-xs text-text-secondary mt-0.5">
              {description}
            </p>
          )}
        </div>
      )}
      <div style={{ height, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  )
})

export { ChartContainer, ChartTooltipContent }
export type { ChartContainerProps }
