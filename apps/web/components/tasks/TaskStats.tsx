'use client'

import { motion } from 'framer-motion'
import { ListTodo, Layers, CheckCircle } from 'lucide-react'
import { cn } from '@/components/ui/utils'

interface TaskStatsProps {
  stats: { todo: number; inProgress: number; done: number }
}

const statCards = [
  { label: 'To Do', key: 'todo' as const, icon: ListTodo, color: 'text-accent-primary' },
  { label: 'In Progress', key: 'inProgress' as const, icon: Layers, color: 'text-accent-warning' },
  { label: 'Done', key: 'done' as const, icon: CheckCircle, color: 'text-accent-success' },
]

export function TaskStats({ stats }: TaskStatsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="grid grid-cols-3 gap-4"
    >
      {statCards.map((card, i) => (
        <motion.div
          key={card.key}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 + i * 0.05 }}
          className="card cursor-pointer hover:border-accent-primary/30 transition-all duration-300"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">
              {card.label}
            </span>
            <card.icon size={18} className={cn(card.color, 'opacity-60 group-hover:opacity-100 transition-opacity')} />
          </div>
          <motion.div
            key={stats[card.key]}
            initial={{ y: -8, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.2 }}
            className="text-3xl font-display font-bold text-text-primary"
          >
            {stats[card.key]}
          </motion.div>
        </motion.div>
      ))}
    </motion.div>
  )
}
