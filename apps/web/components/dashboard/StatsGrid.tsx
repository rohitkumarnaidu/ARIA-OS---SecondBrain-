'use client'

import type { ElementType } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'

interface StatCard {
  label: string
  value: string | number
  icon: ElementType
  trend?: 'up' | 'down'
}

interface StatsGridProps {
  stats: StatCard[]
}

const containerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

const accentMap: Record<string, string> = {
  Productivity: 'accent-primary',
  'Tasks Today': 'accent-secondary',
  'Active Courses': 'accent-info',
  'Active Goals': 'accent-neon',
}

const glowMap: Record<string, string> = {
  Productivity: 'shadow-glow-sm',
  'Tasks Today': 'shadow-glow-sm',
  'Active Courses': '',
  'Active Goals': 'shadow-glow-sm',
}

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="grid grid-cols-2 lg:grid-cols-4 gap-4"
    >
      {stats.map((stat) => {
        const accent = accentMap[stat.label] || 'accent-primary'
        const glow = glowMap[stat.label] || ''
        return (
          <motion.div
            key={stat.label}
            variants={cardVariants}
            className={cn(
              'card relative group transition-all duration-300',
              glow && 'hover:shadow-glow-sm',
            )}
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
                {stat.label}
              </span>
              <div className={cn('flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity')}>
                {stat.trend === 'up' && <TrendingUp size={14} className={cn('text-accent-success')} />}
                {stat.trend === 'down' && <TrendingDown size={14} className={cn('text-accent-error')} />}
                <stat.icon size={18} className={cn('text-text-tertiary group-hover:text-[var(--accent-primary)] transition-colors')} />
              </div>
            </div>
            <div className="text-2xl font-display font-bold text-text-primary mb-1">
              {stat.value}
            </div>
          </motion.div>
        )
      })}
    </motion.div>
  )
}
