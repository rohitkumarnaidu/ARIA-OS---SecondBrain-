'use client'

import { useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { formatDistanceToNow, parseISO } from 'date-fns'
import { CheckCircle, ChevronRight, Activity } from 'lucide-react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/utils'

interface TaskItem {
  id: string
  title: string
  priority: string
  due_date?: string
  status: string
}

interface TaskPreviewListProps {
  tasks: TaskItem[]
}

const priorityConfig: Record<string, { label: string; bg: string; text: string; border: string }> = {
  urgent: { label: 'P0', bg: 'bg-priority-urgent/10', text: 'text-priority-urgent', border: 'border-priority-urgent/20' },
  high: { label: 'P1', bg: 'bg-priority-high/10', text: 'text-priority-high', border: 'border-priority-high/20' },
  medium: { label: 'P2', bg: 'bg-accent-info/10', text: 'text-accent-info', border: 'border-accent-info/20' },
  low: { label: 'P3', bg: 'bg-text-tertiary/10', text: 'text-text-tertiary', border: 'border-text-tertiary/20' },
}

const statusDot: Record<string, string> = {
  pending: 'bg-priority-medium',
  in_progress: 'bg-accent-info',
  completed: 'bg-accent-success',
  cancelled: 'bg-text-tertiary',
}

const containerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.08,
    },
  },
}

const taskVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
}

export function TaskPreviewList({ tasks }: TaskPreviewListProps) {
  const router = useRouter()

  const handleClick = useCallback(() => {
    router.push('/tasks')
  }, [router])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
            <Activity size={20} className="text-accent-primary" />
          </div>
          <div>
            <h2 className="text-lg font-display font-semibold text-text-primary">Priority Tasks</h2>
            <p className="text-xs text-text-tertiary">Your focus list for today</p>
          </div>
        </div>
        <Button
          onClick={handleClick}
          variant="ghost" className="gap-1.5"
          aria-label="View all tasks"
        >
          View all <ChevronRight size={16} />
        </Button>
      </div>

      {tasks.length > 0 ? (
        <motion.div
          variants={containerVariants}
          initial="initial"
          animate="animate"
          className="space-y-3"
        >
          {tasks.slice(0, 5).map((task, index) => {
            const priority = priorityConfig[task.priority] || priorityConfig.low
            const dotColor = statusDot[task.status] || 'bg-text-tertiary'
            return (
              <motion.div
                key={task.id}
                variants={taskVariants}
                onClick={handleClick}
                className="group flex items-center gap-4 p-4 rounded-xl bg-background-elevated/50 border border-transparent hover:border-accent-primary/20 hover:bg-background-elevated transition-all duration-200 cursor-pointer"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleClick() }}
                aria-label={`View task: ${task.title}`}
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary/20 to-accent-primary/5 flex items-center justify-center text-accent-primary font-display font-semibold text-sm">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-text-primary font-medium truncate group-hover:text-accent-primary transition-colors">
                    {task.title}
                  </div>
                  <div className="text-xs text-text-tertiary flex items-center gap-2 mt-0.5">
                    <span className={cn('w-2 h-2 rounded-full', dotColor)} aria-hidden="true" />
                    <span className="capitalize">{task.status.replace('_', ' ')}</span>
                    {task.due_date && (
                      <>
                        <span className="w-1 h-1 rounded-full bg-text-tertiary" aria-hidden="true" />
                        <span>{formatDistanceToNow(parseISO(task.due_date), { addSuffix: true })}</span>
                      </>
                    )}
                  </div>
                </div>
                <div className={cn('px-2.5 py-1 rounded-md text-xs font-medium border', priority.bg, priority.text, priority.border)}>
                  {priority.label}
                </div>
              </motion.div>
            )
          })}
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-10"
        >
          <div className="w-16 h-16 rounded-2xl bg-accent-success/10 flex items-center justify-center mx-auto mb-4">
            <CheckCircle size={32} className="text-accent-success" />
          </div>
          <p className="text-text-primary font-medium">All caught up!</p>
          <p className="text-text-tertiary text-sm mt-1">No tasks for today</p>
          <Button
            onClick={() => router.push('/tasks')}
            variant="primary" className="mt-4"
            aria-label="Add a new task"
          >
            Add Task
          </Button>
        </motion.div>
      )}
    </div>
  )
}
