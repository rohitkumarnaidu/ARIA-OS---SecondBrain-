'use client'

import { memo } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { AreaChart, Area, ResponsiveContainer } from 'recharts'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import type { KPIMetric } from '@/types/analytics'

const trendConfig = {
  up: { icon: TrendingUp, color: 'text-accent-success' },
  down: { icon: TrendingDown, color: 'text-accent-error' },
  neutral: { icon: Minus, color: 'text-text-tertiary' },
} as const

export const KPITile = memo(function KPITile({ metric }: { metric: KPIMetric }) {
  const TrendIcon = trendConfig[metric.trend].icon

  return (
    <motion.div
      whileHover={{ y: -2 }}
      className={cn(
        'card relative group transition-all duration-300',
        'hover:shadow-glow-sm hover:border-accent-primary/30',
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-accent-primary/10 flex items-center justify-center">
            <metric.icon size={16} className="text-accent-primary" />
          </div>
          <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
            {metric.label}
          </span>
        </div>
        <div className={cn('flex items-center gap-1', trendConfig[metric.trend].color)}>
          <TrendIcon size={14} />
          {metric.trendValue && (
            <span className="text-[10px] font-semibold">{metric.trendValue}</span>
          )}
        </div>
      </div>

      <div className="text-2xl font-display font-bold text-text-primary mb-1">
        {metric.value}
      </div>

      <div className="h-10 -mx-1 -mb-1">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={metric.sparklineData}>
            <defs>
              <linearGradient id={`sparkline-${metric.label}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--accent-primary)" stopOpacity={0.4} />
                <stop offset="100%" stopColor="var(--accent-primary)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke="var(--accent-primary)"
              strokeWidth={1.5}
              fill={`url(#sparkline-${metric.label})`}
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
})
