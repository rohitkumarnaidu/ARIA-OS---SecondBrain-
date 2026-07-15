'use client'

import { memo } from 'react'
import { motion } from 'framer-motion'
import { Moon, Flame, Calendar, Clock, CheckCircle2, Trash2 } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import type { Habit } from '@/lib/types'

const frequencyLabels: Record<string, string> = {
  daily: 'Daily',
  weekly: 'Weekly',
  weekdays: 'Weekdays',
  weekends: 'Weekends',
  custom: 'Custom',
}

interface HabitCardProps {
  habit: Habit
  onLog?: (id: string) => void
  onEdit?: (habit: Habit) => void
  onDelete?: (id: string) => void
  todayLogged?: boolean
}

export const HabitCard = memo(function HabitCard({
  habit,
  onLog,
  onEdit,
  onDelete,
  todayLogged,
}: HabitCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn(
        'card card-interactive group',
        !habit.is_active && 'opacity-50',
      )}
      role="article"
      aria-label={`Habit: ${habit.name}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
            <Moon size={20} className="text-accent-primary" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h3
                className="font-medium text-text-primary truncate group-hover:text-accent-primary transition-colors cursor-pointer"
                onClick={() => onEdit?.(habit)}
                onKeyDown={(e) => { if (e.key === 'Enter') onEdit?.(habit) }}
                tabIndex={0}
                role="button"
                aria-label={`Edit ${habit.name}`}
              >
                {habit.name}
              </h3>
              {todayLogged && (
                <CheckCircle2 size={16} className="text-accent-success shrink-0" aria-label="Completed today" />
              )}
            </div>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <Badge variant="outline">{frequencyLabels[habit.frequency] || habit.frequency}</Badge>
              {habit.current_streak > 0 && (
                <span className="flex items-center gap-1 text-xs text-accent-warning">
                  <Flame size={12} aria-hidden="true" />
                  {habit.current_streak} day streak
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          {onLog && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onLog(habit.id)}
              aria-label={`Log ${habit.name}`}
              disabled={todayLogged}
            >
              <CheckCircle2 size={16} className={todayLogged ? 'text-text-tertiary' : 'text-accent-success'} />
            </Button>
          )}
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(habit.id)}
              aria-label={`Delete habit: ${habit.name}`}
            >
              <Trash2 size={16} className="text-accent-error" />
            </Button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 mt-3 flex-wrap text-xs text-text-tertiary">
        {habit.time_target_minutes && (
          <span className="flex items-center gap-1">
            <Clock size={12} aria-hidden="true" />
            {habit.time_target_minutes} min target
          </span>
        )}
        <span className="flex items-center gap-1">
          <Calendar size={12} aria-hidden="true" />
          Best streak: {habit.best_streak} days
        </span>
        {habit.consistency_percentage > 0 && (
          <span className="ml-auto text-accent-primary">
            {Math.round(habit.consistency_percentage)}% consistent
          </span>
        )}
      </div>
    </motion.div>
  )
})
