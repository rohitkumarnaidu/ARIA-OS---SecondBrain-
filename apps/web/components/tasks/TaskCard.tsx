'use client'

import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, CheckCircle, Edit2, Trash2, Calendar, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { motion } from 'framer-motion'
import { cn } from '@/components/ui/utils'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import type { Task, TaskPriority } from '@/types/task'

const priorityConfig: Record<TaskPriority, { label: string; badgeVariant: 'error' | 'warning' | 'info' | 'outline'; barClass: string }> = {
  urgent: { label: 'P0', badgeVariant: 'error', barClass: 'bg-priority-urgent' },
  high: { label: 'P1', badgeVariant: 'warning', barClass: 'bg-priority-high' },
  medium: { label: 'P2', badgeVariant: 'info', barClass: 'bg-priority-medium' },
  low: { label: 'P3', badgeVariant: 'outline', barClass: 'bg-priority-low' },
}

interface TaskCardProps {
  task: Task
  onComplete: (id: string) => void
  onEdit: (task: Task) => void
  onDelete: (id: string) => void
}

export function TaskCard({ task, onComplete, onEdit, onDelete }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const priority = priorityConfig[task.priority]
  const isCompleted = task.status === 'completed'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn(
        'card card-interactive group',
        isDragging && 'opacity-50 ring-2 ring-accent-primary',
        isCompleted && 'opacity-60',
      )}
      ref={setNodeRef}
      style={style}
    >
      <div className="flex items-start gap-4">
        <button
          className="flex-shrink-0 mt-1 cursor-grab active:cursor-grabbing touch-target flex items-center justify-center"
          aria-label="Drag to reorder"
          {...attributes}
          {...listeners}
        >
          <GripVertical size={16} className="text-text-tertiary opacity-30 group-hover:opacity-100 transition-opacity" />
        </button>

        <div className={cn('flex-shrink-0 w-1.5 h-12 rounded-full', priority.barClass)} />

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-1">
              <h3
                className={cn(
                  'font-medium text-text-primary group-hover:text-accent-primary transition-colors',
                  isCompleted && 'line-through text-text-secondary',
                )}
              >
                {task.title}
              </h3>
              {task.description && (
                <p className="text-sm text-text-tertiary line-clamp-2">{task.description}</p>
              )}
            </div>

            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {!isCompleted && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onComplete(task.id)}
                  aria-label="Complete task"
                >
                  <CheckCircle size={16} className="text-accent-success" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(task)}
                aria-label="Edit task"
              >
                <Edit2 size={16} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(task.id)}
                aria-label="Delete task"
              >
                <Trash2 size={16} className="text-accent-error" />
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2 mt-3 flex-wrap">
            <Badge variant={priority.badgeVariant}>{priority.label}</Badge>
            <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-background-elevated text-text-secondary border border-border capitalize">
              {task.category}
            </span>
            {task.due_date && (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs text-text-tertiary" title={new Date(task.due_date).toLocaleDateString()}>
                <Calendar size={12} />
                {formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}
              </span>
            )}
            {task.estimated_minutes && (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs text-text-tertiary">
                <Clock size={12} />
                {task.estimated_minutes} min
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
