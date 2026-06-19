'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft, CheckCircle, Calendar, Loader2, AlertCircle, Clock, Trash2,
  ListChecks, Plus, FileText, History, X,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore } from '@/lib/stores/taskStore'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/Button'
import { cn } from '@/components/ui/utils'
import type { Task } from '@/lib/types'

const priorityColors: Record<string, string> = {
  urgent: 'bg-priority-urgent text-white',
  high: 'bg-priority-high text-white',
  medium: 'bg-priority-medium text-black',
  low: 'bg-priority-low text-black',
}

const statusColors: Record<string, string> = {
  pending: 'bg-accent-warning/10 text-accent-warning border-accent-warning/20',
  in_progress: 'bg-accent-primary/10 text-accent-primary border-accent-primary/20',
  completed: 'bg-accent-success/10 text-accent-success border-accent-success/20',
}

interface SubTask {
  id: string
  text: string
  done: boolean
}

const STORAGE_PREFIX = 'task-subtasks-'
const NOTES_PREFIX = 'task-notes-'

export default function TaskDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const { tasks, updateTask, deleteTask, completeTask } = useTaskStore()
  const [task, setTask] = useState<Task | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [description, setDescription] = useState('')
  const [saving, setSaving] = useState(false)
  const [subtasks, setSubtasks] = useState<SubTask[]>([])
  const [newSubtask, setNewSubtask] = useState('')
  const [notes, setNotes] = useState('')
  const [notesSaving, setNotesSaving] = useState(false)
  const [completed, setCompleted] = useState(false)

  const taskId = params.id as string

  useEffect(() => {
    if (!user) return

    const local = tasks.find(t => t.id === taskId)
    if (local) {
      setTask(local)
      setDescription(local.description ?? '')
      setCompleted(local.status === 'completed')
      setLoading(false)
      return
    }

    supabase
      .from('tasks')
      .select('*')
      .eq('id', taskId)
      .single()
      .then(({ data, error: err }) => {
        if (err) setError(err.message)
        else if (data) {
          setTask(data)
          setDescription(data.description ?? '')
          setCompleted(data.status === 'completed')
        }
        setLoading(false)
      })
  }, [taskId, user, tasks])

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_PREFIX + taskId)
      if (saved) setSubtasks(JSON.parse(saved))
    } catch { /* ignore */ }
  }, [taskId])

  useEffect(() => {
    try {
      const saved = localStorage.getItem(NOTES_PREFIX + taskId)
      if (saved) setNotes(saved)
    } catch { /* ignore */ }
  }, [taskId])

  useEffect(() => {
    localStorage.setItem(STORAGE_PREFIX + taskId, JSON.stringify(subtasks))
  }, [subtasks, taskId])

  const handleDescriptionSave = async () => {
    if (!task) return
    setSaving(true)
    await updateTask(task.id, { description: description || undefined })
    setSaving(false)
  }

  const handleNotesSave = useCallback(async () => {
    if (!task) return
    setNotesSaving(true)
    localStorage.setItem(NOTES_PREFIX + task.id, notes)
    await new Promise(r => setTimeout(r, 200))
    setNotesSaving(false)
  }, [task, notes])

  const addSubtask = () => {
    if (!newSubtask.trim()) return
    setSubtasks(prev => [...prev, { id: crypto.randomUUID(), text: newSubtask.trim(), done: false }])
    setNewSubtask('')
  }

  const toggleSubtask = (id: string) => {
    setSubtasks(prev => prev.map(st => st.id === id ? { ...st, done: !st.done } : st))
  }

  const deleteSubtask = (id: string) => {
    setSubtasks(prev => prev.filter(st => st.id !== id))
  }

  const handleComplete = async () => {
    if (!task) return
    await completeTask(task.id)
    setCompleted(true)
    setTask(prev => prev ? { ...prev, status: 'completed' } : null)
  }

  const activityItems = [
    ...(task?.created_at ? [{ icon: 'plus', label: 'Task created', date: task.created_at }] : []),
    ...(task?.completed_at ? [{ icon: 'check', label: 'Task completed', date: task.completed_at }] : []),
    ...(task?.updated_at ? [{ icon: 'edit', label: 'Last updated', date: task.updated_at }] : []),
  ]

  const subtaskProgress = subtasks.length > 0
    ? Math.round((subtasks.filter(s => s.done).length / subtasks.length) * 100)
    : 0

  if (loading || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-accent-primary animate-spin" />
      </div>
    )
  }

  if (error || !task) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <AlertCircle className="w-12 h-12 text-accent-error" />
        <p className="text-text-secondary">{error || 'Task not found'}</p>
        <Button asChild variant="secondary"><Link href="/tasks">Back to Tasks</Link></Button>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-8">
      <nav className="flex items-center gap-2 text-sm text-text-secondary" aria-label="Breadcrumb">
        <Link href="/tasks" className="hover:text-text-primary transition-colors">Tasks</Link>
        <span aria-hidden="true">/</span>
        <span className="text-text-primary truncate">{task.title}</span>
      </nav>

      <Link
        href="/tasks"
        className="inline-flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary transition-colors w-fit"
      >
        <ArrowLeft size={16} />
        Back to tasks
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6 space-y-6"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-3 flex-1 min-w-0">
            <h1 className={cn('text-2xl font-display font-bold break-words', completed && 'line-through text-text-secondary')}>
              {task.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`px-2.5 py-1 rounded-md text-xs font-medium ${priorityColors[task.priority] ?? ''}`}>
                {task.priority.toUpperCase()}
              </span>
              <span className={`px-2.5 py-1 rounded-md text-xs font-medium border ${statusColors[task.status] ?? ''}`}>
                {task.status === 'in_progress' ? 'In Progress' : task.status.charAt(0).toUpperCase() + task.status.slice(1)}
              </span>
              <span className="px-2.5 py-1 rounded-md text-xs text-text-tertiary border border-border capitalize">
                {task.category}
              </span>
              {task.due_date && (
                <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs text-text-tertiary border border-border">
                  <Calendar size={12} />
                  {new Date(task.due_date).toLocaleDateString()}
                </span>
              )}
              {task.estimated_minutes && (
                <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs text-text-tertiary border border-border">
                  <Clock size={12} />
                  {task.estimated_minutes} min
                </span>
              )}
            </div>
          </div>

          {!completed && (
            <Button variant="primary" onClick={handleComplete} className="flex-shrink-0">
              <CheckCircle size={16} />
              Mark Complete
            </Button>
          )}
          {completed && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent-success/10 border border-accent-success/20 text-accent-success text-sm font-medium flex-shrink-0">
              <CheckCircle size={16} />
              Completed
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-border">
          <label htmlFor="task-description" className="block text-sm font-medium text-text-primary mb-2">
            Description
          </label>
          <textarea
            id="task-description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            onBlur={handleDescriptionSave}
            className="input min-h-[100px] resize-y"
            placeholder="No description yet. Add one..."
            rows={4}
          />
          {saving && <p className="text-xs text-text-tertiary mt-1">Saving...</p>}
        </div>

        <div className="pt-4 border-t border-border">
          <div className="flex items-center gap-2 mb-3">
            <ListChecks size={16} className="text-accent-secondary" />
            <h2 className="text-sm font-medium text-text-primary">Subtasks</h2>
            {subtasks.length > 0 && (
              <span className="text-xs text-text-tertiary">
                ({subtasks.filter(s => s.done).length}/{subtasks.length})
              </span>
            )}
          </div>

          {subtasks.length > 0 && (
            <div className="mb-3 w-full bg-background-elevated rounded-full h-1.5 overflow-hidden" role="progressbar" aria-valuenow={subtaskProgress} aria-valuemin={0} aria-valuemax={100}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${subtaskProgress}%` }}
                transition={{ duration: 0.5 }}
                className="h-full rounded-full bg-gradient-to-r from-accent-secondary to-accent-neon"
              />
            </div>
          )}

          <div className="space-y-1 mb-3">
            <AnimatePresence>
              {subtasks.map(st => (
                <motion.div
                  key={st.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                  className="flex items-center gap-2 group"
                >
                  <input
                    type="checkbox"
                    checked={st.done}
                    onChange={() => toggleSubtask(st.id)}
                    className="w-4 h-4 rounded border-border text-accent-secondary focus:ring-accent-secondary flex-shrink-0"
                    aria-label={`Mark "${st.text}" as ${st.done ? 'incomplete' : 'complete'}`}
                  />
                  <span className={cn('flex-1 text-sm', st.done && 'line-through text-text-tertiary')}>
                    {st.text}
                  </span>
                  <button
                    onClick={() => deleteSubtask(st.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-background-elevated rounded transition-all"
                    aria-label={`Delete subtask: ${st.text}`}
                  >
                    <X size={12} className="text-text-tertiary" />
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newSubtask}
              onChange={e => setNewSubtask(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') addSubtask() }}
              className="input flex-1 text-sm"
              placeholder="Add a subtask..."
              aria-label="New subtask"
            />
            <Button variant="outline" size="sm" onClick={addSubtask} disabled={!newSubtask.trim()}>
              <Plus size={14} />
              Add
            </Button>
          </div>
        </div>

        <div className="pt-4 border-t border-border">
          <div className="flex items-center gap-2 mb-3">
            <FileText size={16} className="text-accent-primary" />
            <h2 className="text-sm font-medium text-text-primary">Notes</h2>
            {notesSaving && <span className="text-xs text-text-tertiary">Saving...</span>}
          </div>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            onBlur={handleNotesSave}
            className="input min-h-[80px] resize-y"
            placeholder="Add notes about this task..."
            rows={3}
          />
        </div>

        {activityItems.length > 0 && (
          <div className="pt-4 border-t border-border">
            <div className="flex items-center gap-2 mb-3">
              <History size={16} className="text-text-tertiary" />
              <h2 className="text-sm font-medium text-text-primary">Activity</h2>
            </div>
            <div className="space-y-2">
              {activityItems.map((item, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <div className="w-6 h-6 rounded-full bg-background-elevated flex items-center justify-center flex-shrink-0">
                    <div className="w-1.5 h-1.5 rounded-full bg-accent-primary" />
                  </div>
                  <span className="text-text-primary">{item.label}</span>
                  <span className="text-text-tertiary ml-auto">{new Date(item.date).toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-border text-sm">
          <div>
            <p className="text-text-tertiary mb-1">Created</p>
            <p className="text-text-primary">{new Date(task.created_at).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-text-tertiary mb-1">Updated</p>
            <p className="text-text-primary">{new Date(task.updated_at).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-text-tertiary mb-1">Priority</p>
            <p className="text-text-primary capitalize">{task.priority}</p>
          </div>
          <div>
            <p className="text-text-tertiary mb-1">Status</p>
            <p className="text-text-primary capitalize">{task.status.replace('_', ' ')}</p>
          </div>
        </div>
      </motion.div>

      <div className="flex gap-3">
        <Button
          variant="destructive"
          onClick={async () => {
            if (window.confirm('Delete this task indefinitely?')) {
              localStorage.removeItem(STORAGE_PREFIX + taskId)
              localStorage.removeItem(NOTES_PREFIX + taskId)
              await deleteTask(task.id)
              router.push('/tasks')
            }
          }}
        >
          <Trash2 size={16} />
          Delete Task
        </Button>
      </div>
    </div>
  )
}
