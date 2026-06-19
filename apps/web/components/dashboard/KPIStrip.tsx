'use client'

import { useMemo } from 'react'
import { Area, AreaChart, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { motion } from 'framer-motion'

interface KPIDataPoint {
  value: number
}

export interface KPIItem {
  label: string
  value: string
  trend: 'up' | 'down' | 'neutral'
  data: KPIDataPoint[]
  color: string
}

interface KPIStripProps {
  items: KPIItem[]
}

export function KPIStrip({ items }: KPIStripProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {items.map((item, i) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06 }}
          className="card group"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-text-tertiary uppercase tracking-wider font-medium">{item.label}</span>
            <div className="flex items-center gap-1">
              {item.trend === 'up' && <TrendingUp size={14} className="text-accent-success" />}
              {item.trend === 'down' && <TrendingDown size={14} className="text-accent-error" />}
            </div>
          </div>
          <div className="text-2xl font-display font-bold text-text-primary mb-2">{item.value}</div>
          <div className="h-8">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={item.data} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id={`sparkline-${i}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={item.color} stopOpacity={0.3} />
                    <stop offset="100%" stopColor={item.color} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke={item.color}
                  strokeWidth={2}
                  fill={`url(#sparkline-${i})`}
                  dot={false}
                  activeDot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
