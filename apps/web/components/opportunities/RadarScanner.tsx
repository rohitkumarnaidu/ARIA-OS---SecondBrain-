'use client'

import { useMemo } from 'react'
import { cn } from '@/components/ui/utils'

export interface RadarSignal {
  id: string
  angle: number
  radius: number
  status: 'new' | 'viewed' | 'saved'
  label: string
}

interface RadarScannerProps {
  signals: RadarSignal[]
  className?: string
}

const ringSizes = [12, 24, 36, 48]

function SignalDot({ signal }: { signal: RadarSignal }) {
  const angleRad = ((signal.angle - 90) * Math.PI) / 180
  const pct = signal.radius * 44
  const x = 50 + pct * Math.cos(angleRad)
  const y = 50 + pct * Math.sin(angleRad)

  const colorMap = {
    new: 'var(--accent-neon)',
    viewed: 'var(--accent-primary)',
    saved: 'var(--accent-warning)',
  } as const

  const shadowMap = {
    new: '0 0 0 0 var(--accent-neon)',
    viewed: '0 0 0 0 var(--accent-primary)',
    saved: '0 0 0 0 var(--accent-warning)',
  } as const

  return (
    <div
      className={cn(
        'absolute w-3 h-3 -translate-x-1/2 -translate-y-1/2 rounded-full z-10',
        signal.status === 'new' && 'animate-ping-green'
      )}
      style={{
        left: `${x}%`,
        top: `${y}%`,
        backgroundColor: colorMap[signal.status],
        boxShadow: shadowMap[signal.status],
        animation: signal.status === 'new'
          ? 'ping-green 2s ease-in-out infinite'
          : undefined,
      }}
      title={signal.label}
    />
  )
}

export function RadarScanner({ signals, className }: RadarScannerProps) {
  const quadrantLabels = useMemo(() => [
    { label: 'Strategic', x: 75, y: 25 },
    { label: 'Financial', x: 75, y: 75 },
    { label: 'Partnership', x: 25, y: 75 },
    { label: 'Career', x: 25, y: 25 },
  ], [])

  return (
    <div className={cn('relative w-full max-w-[400px] mx-auto', className)}>
      <style>
        {`
          @keyframes scan-spin {
            to { transform: rotate(360deg) }
          }
          @keyframes ping-green {
            0% { box-shadow: 0 0 0 0 var(--accent-neon); }
            100% { box-shadow: 0 0 0 12px transparent; }
          }
        `}
      </style>
      <div className="relative aspect-square w-full">
        <div className="absolute inset-4 rounded-full border border-[var(--border-subtle)] bg-[var(--background-dark)]">
          {ringSizes.map((size, i) => (
            <div
              key={i}
              className="absolute rounded-full border"
              style={{
                inset: `${size}%`,
                borderColor: `color-mix(in oklab, var(--accent-primary) ${20 - i * 4}%, transparent)`,
              }}
            />
          ))}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `conic-gradient(from 0deg, transparent 355deg, var(--accent-primary) 359deg, transparent 360deg)`,
              animation: 'scan-spin 4s linear infinite',
              mask: 'radial-gradient(farthest-side, transparent calc(50% - 1px), black calc(50% - 1px), black 50%, transparent 50%)',
              WebkitMask: 'radial-gradient(farthest-side, transparent calc(50% - 1px), black calc(50% - 1px), black 50%, transparent 50%)',
            }}
          />
          {signals.map((signal) => (
            <SignalDot key={signal.id} signal={signal} />
          ))}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-[var(--accent-primary)] shadow-[0_0_8px_var(--accent-primary)]" />
        </div>
        {quadrantLabels.map((q) => (
          <span
            key={q.label}
            className="absolute text-[10px] font-medium text-[var(--text-tertiary)] uppercase tracking-widest"
            style={{ left: `${q.x}%`, top: `${q.y}%`, transform: 'translate(-50%, -50%)' }}
          >
            {q.label}
          </span>
        ))}
      </div>
    </div>
  )
}
