'use client'

import { memo } from 'react'
import { AreaChart, Area, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/components/ui/utils'

interface SparklinePoint {
  timestamp: string
  value: number
}

interface MetricWithSparkline {
  current: number
  sparkline: SparklinePoint[]
  trend: 'up' | 'down' | 'neutral'
  changePercent: number
}

interface REDMetricsCardProps {
  rate: MetricWithSparkline
  errors: MetricWithSparkline
  duration: {
    p50: MetricWithSparkline
    p95: MetricWithSparkline
    p99: MetricWithSparkline
  }
  loading?: boolean
}

function formatMetric(value: number, type: 'rate' | 'errors' | 'duration'): string {
  if (type === 'rate') return value.toFixed(4)
  if (type === 'errors') return `${value.toFixed(1)}%`
  return `${Math.round(value)}ms`
}

const trendConfig = {
  up: { icon: TrendingUp, color: 'text-accent-success' },
  down: { icon: TrendingDown, color: 'text-accent-error' },
  neutral: { icon: Minus, color: 'text-text-tertiary' },
} as const

const MetricTile = memo(function MetricTile({
  title,
  metric,
  type,
  color,
  index,
}: {
  title: string
  metric: MetricWithSparkline
  type: 'rate' | 'errors' | 'duration'
  color: string
  index: number
}) {
  const TrendIcon = trendConfig[metric.trend].icon
  const gradientId = `metric-sparkline-${title.replace(/\s+/g, '-')}`

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
    >
      <Card className="group hover:shadow-glow-sm hover:border-accent-primary/30 transition-all duration-300">
        <div className="flex items-start justify-between mb-2">
          <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">{title}</span>
          <div className={cn('flex items-center gap-1', trendConfig[metric.trend].color)}>
            <TrendIcon size={14} />
            <span className="text-[10px] font-semibold">
              {metric.changePercent > 0 ? '+' : ''}{metric.changePercent}%
            </span>
          </div>
        </div>
        <div className="text-2xl font-display font-bold text-text-primary mb-1">
          {formatMetric(metric.current, type)}
        </div>
        <div className="h-10 -mx-1 -mb-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={metric.sparkline.length > 0 ? metric.sparkline : [{ value: 0 }]}>
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={1.5}
                fill={`url(#${gradientId})`}
                dot={false}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </motion.div>
  )
})

function LoadingState() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4">
            <Skeleton variant="text" className="w-20 h-3 mb-3" />
            <Skeleton variant="text" className="w-32 h-7 mb-2" />
            <Skeleton variant="chart" className="h-10" />
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4">
            <Skeleton variant="text" className="w-20 h-3 mb-3" />
            <Skeleton variant="text" className="w-32 h-7 mb-2" />
            <Skeleton variant="chart" className="h-10" />
          </Card>
        ))}
      </div>
    </div>
  )
}

export function REDMetricsCard({ rate, errors, duration, loading }: REDMetricsCardProps) {
  if (loading) return <LoadingState />

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricTile title="Rate" metric={rate} type="rate" color="var(--accent-primary)" index={0} />
        <MetricTile title="Error Rate" metric={errors} type="errors" color="var(--accent-error)" index={1} />
        <MetricTile title="Duration P50" metric={duration.p50} type="duration" color="var(--accent-secondary)" index={2} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MetricTile title="Duration P95" metric={duration.p95} type="duration" color="var(--accent-warning)" index={3} />
        <MetricTile title="Duration P99" metric={duration.p99} type="duration" color="var(--accent-danger)" index={4} />
      </div>
    </div>
  )
}
