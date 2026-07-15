'use client'

import { memo } from 'react'
import { motion } from 'framer-motion'
import { Target, Calendar, Trash2, PauseCircle, CheckCircle2 } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import type { Goal } from '@/lib/types'

const statusConfig: Record<string, { label: string; variant: 'default' | 'success' | 'warning' | 'info' | 'outline' }> = {
  active: { label: 'Active', variant: 'success' },
  paused: { label: 'Paused', variant: 'warning' },
  completed: { label: 'Completed', variant: 'info' },
  abandoned: { label: 'Abandoned', variant: 'outline' },
}

interface GoalCardProps {
  goal: Goal
  onEdit?: (goal: Goal) => void
  onDelete?: (id: string) => void
  onTogglePause?: (id: string) => void
}

export const GoalCard = memo(function GoalCard({ goal, onEdit, onDelete, onTogglePause }: GoalCardProps) {
  const status = statusConfig[goal.status] || statusConfig.active

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="card card-interactive group"
      role="article"
      aria-label={`Goal: ${goal.title}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
            <Target size={20} className="text-accent-primary" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <h3
              className="font-medium text-text-primary truncate group-hover:text-accent-primary transition-colors cursor-pointer"
              onClick={() => onEdit?.(goal)}
              onKeyDown={(e) => { if (e.key === 'Enter') onEdit?.(goal) }}
              tabIndex={0}
              role="button"
              aria-label={`Edit ${goal.title}`}
            >
              {goal.title}
            </h3>
            {goal.description && (
              <p className="text-sm text-text-tertiary mt-0.5 line-clamp-2">{goal.description}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          {onTogglePause && goal.status === 'active' && (
            <Button variant="ghost" size="sm" onClick={() => onTogglePause(goal.id)} aria-label="Pause goal">
              <PauseCircle size={16} className="text-accent-warning" />
            </Button>
          )}
          {onDelete && (
            <Button variant="ghost" size="sm" onClick={() => onDelete(goal.id)} aria-label={`Delete goal: ${goal.title}`}>
              <Trash2 size={16} className="text-accent-error" />
            </Button>
          )}
        </div>
      </div>

      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-text-tertiary mb-1.5">
          <span>Progress</span>
          <span>{Math.round(goal.progress)}%</span>
        </div>
        <div className="w-full h-2 rounded-full bg-background-elevated overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(goal.progress, 100)}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className={cn(
              'h-full rounded-full',
              goal.progress >= 100 ? 'bg-accent-success' : 'bg-accent-primary',
            )}
          />
        </div>
      </div>

      <div className="flex items-center gap-3 mt-3 flex-wrap">
        <Badge variant={status.variant}>{status.label}</Badge>
        {goal.category && (
          <span className="px-2 py-0.5 rounded text-xs bg-background-elevated text-text-secondary border border-border capitalize">
            {goal.category}
          </span>
        )}
        {goal.target_date && (
          <span className="flex items-center gap-1 text-xs text-text-tertiary">
            <Calendar size={12} aria-hidden="true" />
            {new Date(goal.target_date).toLocaleDateString()}
          </span>
        )}
        {goal.hours_per_day && (
          <span className="flex items-center gap-1 text-xs text-text-tertiary ml-auto">
            {goal.hours_per_day}h/day
          </span>
        )}
      </div>

      {goal.milestones && goal.milestones.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border space-y-1.5">
          {goal.milestones.slice(0, 3).map((ms) => (
            <div key={ms.id} className="flex items-center gap-2 text-xs">
              <CheckCircle2
                size={12}
                className={ms.completed ? 'text-accent-success' : 'text-text-tertiary'}
                aria-hidden="true"
              />
              <span className={cn(ms.completed ? 'text-text-secondary line-through' : 'text-text-tertiary')}>
                {ms.title}
              </span>
            </div>
          ))}
          {goal.milestones.length > 3 && (
            <p className="text-xs text-text-tertiary pl-5">+{goal.milestones.length - 3} more</p>
          )}
        </div>
      )}
    </motion.div>
  )
})
