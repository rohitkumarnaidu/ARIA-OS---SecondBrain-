'use client'

import { useState, useRef, useCallback, type ChangeEvent } from 'react'
import { cn } from './utils'

interface SliderProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  className?: string
}

function Slider({ value, onChange, min = 0, max = 100, step = 1, disabled = false, className }: SliderProps) {
  const [showTooltip, setShowTooltip] = useState(false)
  const trackRef = useRef<HTMLDivElement>(null)

  const pct = ((value - min) / (max - min)) * 100

  const handleInput = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      onChange(Number(e.target.value))
    },
    [onChange],
  )

  return (
    <div
      className={cn('relative pt-6 pb-2', disabled && 'opacity-50 pointer-events-none', className)}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div
        ref={trackRef}
        className="relative h-2 rounded-full cursor-pointer"
        style={{ background: 'var(--surface-tertiary)' }}
      >
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-[width] duration-150"
          style={{ width: `${pct}%`, background: 'var(--accent-primary)' }}
        />
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-5 h-5 rounded-full border-2 transition-shadow duration-200"
          style={{
            left: `${pct}%`,
            background: 'var(--background)',
            borderColor: 'var(--accent-primary)',
            boxShadow: showTooltip ? '0 0 12px var(--accent-glow-color)' : '0 2px 4px rgba(0,0,0,0.3)',
          }}
        />
      </div>

      <input
        type="range"
        value={value}
        onChange={handleInput}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        className="absolute inset-0 w-full h-2 opacity-0 cursor-pointer"
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        aria-label="Slider"
      />

      {showTooltip && (
        <div
          className="absolute -top-1 -translate-x-1/2 px-2 py-1 rounded text-xs font-medium pointer-events-none whitespace-nowrap"
          style={{
            left: `${pct}%`,
            background: 'var(--accent-primary)',
            color: '#fff',
          }}
        >
          {value}
        </div>
      )}

      <div className="flex justify-between mt-1">
        <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{min}</span>
        <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{max}</span>
      </div>
    </div>
  )
}

Slider.displayName = 'Slider'

export { Slider }
export type { SliderProps }
