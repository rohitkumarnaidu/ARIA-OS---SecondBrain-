'use client'

import { Clock, Zap, TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from 'recharts'
import type { SmartSlot } from '@/lib/types'

const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const HOUR_LABELS: Record<number, string> = {
  6: '6a', 7: '7a', 8: '8a', 9: '9a', 10: '10a', 11: '11a',
  12: '12p', 13: '1p', 14: '2p', 15: '3p', 16: '4p', 17: '5p',
  18: '6p', 19: '7p', 20: '8p', 21: '9p', 22: '10p',
}

interface SmartScheduleCardProps {
  slots: SmartSlot[]
  bestHour: number
  bestDay: number
  loading: boolean
}

export function SmartScheduleCard({ slots, bestHour, bestDay, loading }: SmartScheduleCardProps) {
  const topSlots = slots.slice(0, 7)
  const maxScore = Math.max(...topSlots.map(s => s.productivity_score), 1)

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--background-card)] p-5">
      <div className="flex items-center gap-2 mb-4">
        <Zap size={16} className="text-[var(--accent-neon)]" aria-hidden="true" />
        <h2 className="text-sm font-display font-semibold text-[var(--text-primary)]">Smart Schedule</h2>
      </div>

      {loading ? (
        <div className="h-[180px] flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : slots.length === 0 ? (
        <p className="text-xs text-[var(--text-tertiary)] text-center py-8">
          Log time entries to discover your peak productivity hours
        </p>
      ) : (
        <>
          <div className="flex items-center gap-4 mb-4 text-xs text-[var(--text-tertiary)]">
            <span className="flex items-center gap-1">
              <Clock size={12} />
              Best time: <strong className="text-[var(--text-primary)]">{HOUR_LABELS[bestHour] || `${bestHour}:00`}</strong>
            </span>
            <span className="flex items-center gap-1">
              <TrendingUp size={12} />
              Best day: <strong className="text-[var(--text-primary)]">{DAY_NAMES[bestDay]}</strong>
            </span>
          </div>

          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={topSlots} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
              <XAxis
                dataKey="hour"
                tickFormatter={(h: number) => HOUR_LABELS[h] || `${h}h`}
                axisLine={false}
                tickLine={false}
                tick={{ fill: 'var(--text-tertiary)', fontSize: 10, fontFamily: 'JetBrains Mono' }}
              />
              <YAxis hide domain={[0, maxScore]} />
              <Bar dataKey="productivity_score" radius={[3, 3, 0, 0]} maxBarSize={28}>
                {topSlots.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.hour === bestHour ? 'var(--accent-neon)' : 'var(--accent-primary)'}
                    opacity={entry.hour === bestHour ? 1 : 0.4}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          <div className="flex flex-wrap gap-2 mt-3">
            {topSlots.slice(0, 3).map(s => (
              <span key={`${s.day_of_week}-${s.hour}`} className="text-[10px] font-mono text-[var(--text-tertiary)] bg-[var(--background-elevated)] px-2 py-1 rounded">
                {DAY_NAMES[s.day_of_week]} {HOUR_LABELS[s.hour] || `${s.hour}:00`} &middot; {s.productivity_score.toFixed(0)}%
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
