'use client'

import { memo } from 'react'
import { motion } from 'framer-motion'
import { BookOpen, ExternalLink, Clock, Trash2 } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import type { Course } from '@/lib/types'

const statusConfig: Record<string, { label: string; variant: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline' }> = {
  not_started: { label: 'Not Started', variant: 'outline' },
  in_progress: { label: 'In Progress', variant: 'info' },
  completed: { label: 'Completed', variant: 'success' },
  dropped: { label: 'Dropped', variant: 'error' },
  abandoned: { label: 'Abandoned', variant: 'warning' },
}

interface CourseCardProps {
  course: Course
  onDelete?: (id: string) => void
  onEdit?: (course: Course) => void
}

export const CourseCard = memo(function CourseCard({ course, onDelete, onEdit }: CourseCardProps) {
  const status = statusConfig[course.status] || statusConfig.not_started
  const progress = course.total_videos
    ? Math.round((course.completed_videos / course.total_videos) * 100)
    : 0

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="card card-interactive group"
      role="article"
      aria-label={`Course: ${course.title}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0 flex-1">
          <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
            <BookOpen size={20} className="text-accent-primary" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <h3
              className="font-medium text-text-primary truncate group-hover:text-accent-primary transition-colors cursor-pointer"
              onClick={() => onEdit?.(course)}
              onKeyDown={(e) => { if (e.key === 'Enter') onEdit?.(course) }}
              tabIndex={0}
              role="button"
              aria-label={`Edit ${course.title}`}
            >
              {course.title}
            </h3>
            <p className="text-sm text-text-tertiary mt-0.5">{course.platform}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Badge variant={status.variant}>{status.label}</Badge>
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(course.id)}
              aria-label={`Delete course: ${course.title}`}
            >
              <Trash2 size={16} className="text-accent-error" />
            </Button>
          )}
        </div>
      </div>

      {course.total_videos && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-text-tertiary mb-1.5">
            <span>{course.completed_videos} / {course.total_videos} videos</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-background-elevated overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={cn(
                'h-full rounded-full',
                progress === 100 ? 'bg-accent-success' : 'bg-accent-primary',
              )}
            />
          </div>
        </div>
      )}

      <div className="flex items-center gap-3 mt-3 flex-wrap">
        {course.daily_minutes_needed && (
          <span className="flex items-center gap-1 text-xs text-text-tertiary">
            <Clock size={12} aria-hidden="true" />
            {course.daily_minutes_needed} min/day needed
          </span>
        )}
        {course.url && (
          <a
            href={course.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-accent-primary hover:text-accent-secondary transition-colors"
            aria-label={`Open course URL: ${course.title}`}
          >
            <ExternalLink size={12} aria-hidden="true" />
            Open
          </a>
        )}
        {course.deadline && (
          <span className="flex items-center gap-1 text-xs text-text-tertiary ml-auto">
            Due {new Date(course.deadline).toLocaleDateString()}
          </span>
        )}
      </div>
    </motion.div>
  )
})
