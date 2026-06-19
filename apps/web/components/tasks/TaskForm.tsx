'use client'

import { useState, type FormEvent } from 'react'
import { motion } from 'framer-motion'
import { X, Loader2 } from 'lucide-react'
import { cn } from '@/components/ui/utils'
import { Button } from '@/components/ui/Button'
import type { Task, TaskFormData, TaskPriority, TaskCategory, TaskStatus } from '@/types/task'

const priorities: TaskPriority[] = ['low', 'medium', 'high', 'urgent']
const categories: TaskCategory[] = ['study', 'project', 'habit', 'personal', 'income']
const statuses: TaskStatus[] = ['pending', 'in_progress', 'completed']

interface TaskFormProps {
  mode: 'add' | 'edit'
  initialData?: Task
  onSubmit: (data: TaskFormData) => void
  onCancel: () => void
}

export function TaskForm({ mode, initialData, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title ?? '')
  const [description, setDescription] = useState(initialData?.description ?? '')
  const [status, setStatus] = useState<TaskStatus>(initialData?.status ?? 'pending')
  const [priority, setPriority] = useState<TaskPriority>(initialData?.priority ?? 'medium')
  const [category, setCategory] = useState<TaskCategory>((initialData?.category as TaskCategory) ?? 'personal')
  const [dueDate, setDueDate] = useState(initialData?.due_date ?? '')
  const [recurring, setRecurring] = useState(initialData?.is_recurring ?? false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setSubmitting(true)
    try {
      onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        category,
        due_date: dueDate || undefined,
        is_recurring: recurring,
      })
    } finally {
      setSubmitting(false)
    }
  }

  const isEdit = mode === 'edit'

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="task-form-title"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-lg shadow-2xl"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 id="task-form-title" className="text-xl font-display font-semibold text-text-primary">
            {isEdit ? 'Edit Task' : 'Create New Task'}
          </h2>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-background-elevated rounded-lg touch-target"
            aria-label="Close modal"
          >
            <X size={20} className="text-text-tertiary" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="task-title" className="block text-sm font-medium text-text-primary mb-2">
              Title <span className="text-accent-error">*</span>
            </label>
            <input
              id="task-title"
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="input"
              placeholder="What needs to be done?"
              autoFocus
              required
            />
          </div>

          <div>
            <label htmlFor="task-description" className="block text-sm font-medium text-text-primary mb-2">
              Description
            </label>
            <textarea
              id="task-description"
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="input min-h-[80px] resize-none"
              placeholder="Add more details..."
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="task-status" className="block text-sm font-medium text-text-primary mb-2">
                Status
              </label>
              <select
                id="task-status"
                value={status}
                onChange={e => setStatus(e.target.value as TaskStatus)}
                className="input capitalize"
              >
                {statuses.map(s => (
                  <option key={s} value={s} className="capitalize">
                    {s === 'in_progress' ? 'In Progress' : s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="task-priority" className="block text-sm font-medium text-text-primary mb-2">
                Priority
              </label>
              <select
                id="task-priority"
                value={priority}
                onChange={e => setPriority(e.target.value as TaskPriority)}
                className="input capitalize"
              >
                {priorities.map(p => (
                  <option key={p} value={p} className="capitalize">
                    {p === 'urgent' ? 'P0 - Urgent' : p === 'high' ? 'P1 - High' : p === 'medium' ? 'P2 - Medium' : 'P3 - Low'}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="task-category" className="block text-sm font-medium text-text-primary mb-2">
                Category
              </label>
              <select
                id="task-category"
                value={category}
                onChange={e => setCategory(e.target.value as TaskCategory)}
                className="input capitalize"
              >
                {categories.map(c => (
                  <option key={c} value={c} className="capitalize">{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="task-due" className="block text-sm font-medium text-text-primary mb-2">
                Due Date
              </label>
              <input
                id="task-due"
                type="date"
                value={dueDate}
                onChange={e => setDueDate(e.target.value)}
                className="input"
              />
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <input
              type="checkbox"
              id="task-recurring"
              checked={recurring}
              onChange={e => setRecurring(e.target.checked)}
              className="w-4 h-4 rounded border-border text-accent-primary focus:ring-accent-primary"
            />
            <label htmlFor="task-recurring" className="text-sm text-text-secondary">
              Make this a recurring task
            </label>
          </div>

          <div className="flex gap-3 mt-6">
            <Button type="button" variant="outline" className="flex-1" onClick={onCancel}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={!title.trim()}
              loading={submitting}
            >
              {isEdit ? 'Save Changes' : 'Create Task'}
            </Button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  )
}
