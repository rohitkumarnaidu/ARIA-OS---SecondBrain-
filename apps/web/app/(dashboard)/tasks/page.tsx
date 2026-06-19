'use client'

import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import {
  Plus, Check, X, Trash2, Grid3X3, List, GripVertical, Calendar,
  Sparkles, ArrowRight, ChevronDown, MoreHorizontal,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DndContext, DragOverlay, closestCorners, useSensor, useSensors,
  PointerSensor, KeyboardSensor, useDroppable, useDraggable,
  type DragStartEvent, type DragEndEvent, type DragOverEvent,
} from '@dnd-kit/core'
import {
  SortableContext, verticalListSortingStrategy, useSortable,
  sortableKeyboardCoordinates, arrayMove,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { formatDistanceToNow, format, isPast, isToday, isTomorrow } from 'date-fns'

import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Dialog } from '@/components/ui/Dialog'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/components/ui/utils'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore } from '@/lib/stores/taskStore'
import type { Task, TaskPriority, TaskStatus, TaskCategory } from '@/types/task'

/* ─── Types ─────────────────────────────────────── */

type ColumnId = 'backlog' | 'in_progress' | 'review' | 'done'

interface KanbanTask extends Task {
  column: ColumnId
  tags: string[]
}

interface ColumnDef {
  id: ColumnId
  title: string
  accentVar: string
  bgClass: string
  borderClass: string
}

/* ─── Constants ─────────────────────────────────── */

const COLUMNS: ColumnDef[] = [
  {
    id: 'backlog',
    title: 'Backlog',
    accentVar: '--accent-info',
    bgClass: 'bg-accent-info/5',
    borderClass: 'border-accent-info/20',
  },
  {
    id: 'in_progress',
    title: 'In Progress',
    accentVar: '--accent-primary',
    bgClass: 'bg-accent-primary/5',
    borderClass: 'border-accent-primary/20',
  },
  {
    id: 'review',
    title: 'Review',
    accentVar: '--accent-warning',
    bgClass: 'bg-accent-warning/5',
    borderClass: 'border-accent-warning/20',
  },
  {
    id: 'done',
    title: 'Done',
    accentVar: '--accent-success',
    bgClass: 'bg-accent-success/5',
    borderClass: 'border-accent-success/20',
  },
]

const PRIORITY_BORDER: Record<TaskPriority, string> = {
  urgent: 'var(--accent-error)',
  high: 'var(--accent-warning)',
  medium: 'var(--accent-primary)',
  low: 'var(--text-tertiary)',
}

const PRIORITY_VARIANT: Record<TaskPriority, 'error' | 'warning' | 'info' | 'outline'> = {
  urgent: 'error',
  high: 'warning',
  medium: 'info',
  low: 'outline',
}

const CATEGORY_VARIANT: Record<TaskCategory, 'default' | 'success' | 'warning' | 'info' | 'outline'> = {
  study: 'info',
  project: 'warning',
  habit: 'success',
  personal: 'default',
  income: 'outline',
}

const ALL_TAGS = ['study', 'project', 'coding', 'devops', 'docs', 'design', 'backend', 'frontend', 'writing', 'testing']

const COLUMN_IDS: ColumnId[] = ['backlog', 'in_progress', 'review', 'done']

function columnToStatus(col: ColumnId): TaskStatus {
  switch (col) {
    case 'backlog': return 'pending'
    case 'in_progress': return 'in_progress'
    case 'review': return 'pending'
    case 'done': return 'completed'
  }
}

/* ─── Helpers ───────────────────────────────────── */

function formatDueDate(dateStr: string): string | null {
  const date = new Date(dateStr)
  if (isToday(date)) return 'Due today'
  if (isTomorrow(date)) return 'Due tomorrow'
  if (isPast(date)) return `Overdue by ${Math.abs(Math.floor((Date.now() - date.getTime()) / 86400000))}d`
  return `Due ${format(date, 'MMM d')}`
}

function getPriorityColorBar(priority: TaskPriority): string {
  return PRIORITY_BORDER[priority]
}

/* ─── Sortable Kanban Card ──────────────────────── */

interface SortableKanbanCardProps {
  task: KanbanTask
  isSelected: boolean
  isFocused: boolean
  onToggleSelect: (id: string) => void
  onClick: (id: string) => void
}

function SortableKanbanCard({
  task,
  isSelected,
  isFocused,
  onToggleSelect,
  onClick,
}: SortableKanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id })

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const dueDateInfo = task.due_date ? formatDueDate(task.due_date) : null
  const priorityBarColor = getPriorityColorBar(task.priority)
  const isCompleted = task.column === 'done'

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, height: 0, marginBottom: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div
        ref={setNodeRef}
        style={style}
        className={cn(
          'group relative rounded-lg border border-border bg-background-card backdrop-blur-sm transition-all',
          'hover:border-border-light hover:shadow-glow-sm',
          isDragging && 'opacity-40 ring-2 ring-accent-primary shadow-glow-lg z-50',
          isSelected && 'ring-2 ring-accent-primary/50 border-accent-primary/30',
          isFocused && 'ring-2 ring-accent-primary/60 border-accent-primary/40',
          isCompleted && 'opacity-70',
        )}
        onClick={() => onClick(task.id)}
        role="option"
        aria-selected={isSelected}
        aria-label={`Task: ${task.title}`}
      >
        {/* Priority color bar */}
        <div
          className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-lg"
          style={{ backgroundColor: priorityBarColor }}
        />

        <div className="p-3 pl-4">
          {/* Header: checkbox + title + actions */}
          <div className="flex items-start gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); onToggleSelect(task.id) }}
              className={cn(
                'flex-shrink-0 w-4 h-4 mt-0.5 rounded border-2 transition-all',
                'opacity-0 group-hover:opacity-100 focus:opacity-100',
                isSelected && 'opacity-100',
                isSelected
                  ? 'bg-accent-primary border-accent-primary'
                  : 'border-border hover:border-accent-primary/50',
              )}
              aria-label={isSelected ? `Deselect ${task.title}` : `Select ${task.title}`}
              type="button"
            >
              {isSelected && (
                <Check size={14} className="text-white -ml-[1px] -mt-[1px]" strokeWidth={3} />
              )}
            </button>

            <div className="flex-1 min-w-0 space-y-1">
              <div className="flex items-start justify-between gap-2">
                <p
                  className={cn(
                    'text-sm font-medium text-text-primary leading-snug line-clamp-2',
                    isCompleted && 'line-through text-text-secondary',
                  )}
                >
                  {task.title}
                </p>
              </div>

              {/* Description preview */}
              {task.description && !isCompleted && (
                <p className="text-xs text-text-tertiary line-clamp-1 leading-relaxed">
                  {task.description}
                </p>
              )}

              {/* Meta row: priority badge, tags, due date */}
              <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
                <span
                  className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
                  style={{
                    backgroundColor: `color-mix(in oklab, ${priorityBarColor} 20%, transparent)`,
                    color: priorityBarColor,
                  }}
                >
                  {task.priority === 'urgent' ? 'P0' : task.priority === 'high' ? 'P1' : task.priority === 'medium' ? 'P2' : 'P3'}
                </span>

                {task.tags.slice(0, 2).map(tag => (
                  <Badge key={tag} variant="outline" className="text-[10px] px-1.5 py-0">{tag}</Badge>
                ))}
                {task.tags.length > 2 && (
                  <span className="text-[10px] text-text-tertiary">+{task.tags.length - 2}</span>
                )}
              </div>

              {/* Due date */}
              {dueDateInfo && (
                <div className="flex items-center gap-1 mt-1">
                  <Calendar size={11} className="text-text-tertiary" />
                  <span
                    className={cn(
                      'text-[11px]',
                      dueDateInfo.startsWith('Overdue') || dueDateInfo === 'Due today'
                        ? 'text-accent-error'
                        : dueDateInfo === 'Due tomorrow'
                          ? 'text-accent-warning'
                          : 'text-text-tertiary',
                    )}
                  >
                    {dueDateInfo}
                  </span>
                </div>
              )}
            </div>

            {/* Drag handle */}
            <button
              className="flex-shrink-0 mt-0.5 p-0.5 rounded cursor-grab active:cursor-grabbing opacity-0 group-hover:opacity-100 hover:bg-glass-heavy transition-all focus:opacity-100"
              aria-label="Drag to reorder"
              {...attributes}
              {...listeners}
              type="button"
            >
              <GripVertical size={14} className="text-text-tertiary" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

/* ─── Drag Overlay Card ─────────────────────────── */

function DragOverlayCard({ task }: { task: KanbanTask }) {
  const priorityBarColor = getPriorityColorBar(task.priority)
  const dueDateInfo = task.due_date ? formatDueDate(task.due_date) : null

  return (
    <div
      className="rounded-lg border-2 border-accent-primary/40 bg-background-card shadow-glow-lg rotate-[3deg] scale-105 opacity-90"
      style={{ width: 'var(--card-width, 280px)' }}
    >
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-lg"
        style={{ backgroundColor: priorityBarColor }}
      />
      <div className="p-3 pl-4">
        <p className="text-sm font-medium text-text-primary line-clamp-2">{task.title}</p>
        <div className="flex items-center gap-1.5 mt-1.5">
          <span
            className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase"
            style={{
              backgroundColor: `color-mix(in oklab, ${priorityBarColor} 20%, transparent)`,
              color: priorityBarColor,
            }}
          >
            {task.priority === 'urgent' ? 'P0' : task.priority === 'high' ? 'P1' : task.priority === 'medium' ? 'P2' : 'P3'}
          </span>
          {dueDateInfo && (
            <span className="text-[11px] text-text-tertiary">
              <Calendar size={11} className="inline mr-1 -mt-0.5" />
              {dueDateInfo}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── Inline Add Form ───────────────────────────── */

interface InlineAddFormProps {
  columnId: ColumnId
  onSubmit: (title: string, column: ColumnId) => void
  onCancel: () => void
}

function InlineAddForm({ columnId, onSubmit, onCancel }: InlineAddFormProps) {
  const [title, setTitle] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = useCallback(() => {
    if (!title.trim()) return
    onSubmit(title.trim(), columnId)
    setTitle('')
  }, [title, columnId, onSubmit])

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="px-3 pb-3"
    >
      <div className="bg-background-card rounded-lg border border-border p-2 space-y-2">
        <input
          ref={inputRef}
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); if (e.key === 'Escape') onCancel() }}
          placeholder="Task title..."
          className="w-full bg-transparent text-sm text-text-primary placeholder:text-text-tertiary outline-none border-none"
          aria-label="New task title"
        />
        <div className="flex items-center gap-2">
          <Button variant="primary" size="sm" onClick={handleSubmit} disabled={!title.trim()}>
            <Plus size={14} />
            Add
          </Button>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </div>
    </motion.div>
  )
}

/* ─── AI Suggestion Card ────────────────────────── */

interface AISuggestion {
  visible: boolean
  taskTitle: string
  fromColumn: string
  toColumn: string
  reason: string
}

interface AISuggestionCardProps {
  suggestion: AISuggestion
  onAccept: () => void
  onDismiss: () => void
}

function AISuggestionCard({ suggestion, onAccept, onDismiss }: AISuggestionCardProps) {
  if (!suggestion.visible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className="relative overflow-hidden rounded-xl border-2 border-accent-success/30 bg-background-card shadow-neon-sm p-4"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-accent-success/[0.03] to-transparent pointer-events-none" />
      <div className="flex items-start gap-3 relative z-10">
        <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-accent-success/15 flex items-center justify-center">
          <Sparkles size={18} className="text-accent-success" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-text-primary font-medium">
            <span className="text-accent-success font-semibold">AI suggests</span> moving{' '}
            <span className="font-semibold">&ldquo;{suggestion.taskTitle}&rdquo;</span>{' '}
            to <span className="font-semibold">{suggestion.toColumn}</span>
          </p>
          <p className="text-xs text-text-tertiary mt-1">{suggestion.reason}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Button variant="primary" size="sm" onClick={onAccept}>
            <ArrowRight size={14} />
            Accept
          </Button>
          <Button variant="ghost" size="sm" onClick={onDismiss}>
            <X size={14} />
          </Button>
        </div>
      </div>
    </motion.div>
  )
}

/* ─── Bulk Action Bar ───────────────────────────── */

interface BulkActionBarProps {
  count: number
  onComplete: () => void
  onMove: (column: ColumnId) => void
  onDelete: () => void
  onClear: () => void
}

function BulkActionBar({ count, onComplete, onMove, onDelete, onClear }: BulkActionBarProps) {
  const [moveOpen, setMoveOpen] = useState(false)
  const moveRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (moveRef.current && !moveRef.current.contains(e.target as Node)) setMoveOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 40, scale: 0.95 }}
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
    >
      <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-background-card border-2 border-accent-primary/30 shadow-glow-lg backdrop-blur-xl">
        <span className="text-sm text-text-primary font-medium whitespace-nowrap">
          {count} selected
        </span>
        <div className="w-px h-6 bg-border" />
        <Button variant="primary" size="sm" onClick={onComplete}>
          <Check size={14} />
          Complete
        </Button>

        <div className="relative" ref={moveRef}>
          <Button variant="outline" size="sm" onClick={() => setMoveOpen(!moveOpen)}>
            <ArrowRight size={14} />
            Move to&hellip;
            <ChevronDown size={12} className={cn('transition-transform', moveOpen && 'rotate-180')} />
          </Button>
          <AnimatePresence>
            {moveOpen && (
              <motion.div
                initial={{ opacity: 0, y: -4, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -4, scale: 0.95 }}
                className="absolute bottom-full left-0 mb-2 w-44 rounded-xl bg-background-card border border-border shadow-glow overflow-hidden z-50"
              >
                {COLUMNS.map(col => (
                  <button
                    key={col.id}
                    onClick={() => { onMove(col.id); setMoveOpen(false) }}
                    className="w-full text-left px-4 py-2.5 text-sm text-text-primary hover:bg-glass-heavy transition-colors"
                    type="button"
                  >
                    {col.title}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <Button variant="destructive" size="sm" onClick={onDelete}>
          <Trash2 size={14} />
          Delete
        </Button>

        <div className="w-px h-6 bg-border" />
        <button
          onClick={onClear}
          className="text-xs text-text-tertiary hover:text-text-primary transition-colors"
          aria-label="Clear selection"
          type="button"
        >
          <X size={16} />
        </button>
      </div>
    </motion.div>
  )
}

/* ─── List View ─────────────────────────────────── */

interface ListViewProps {
  tasks: KanbanTask[]
  selectedIds: Set<string>
  focusedIndex: number
  onToggleSelect: (id: string) => void
  onClick: (id: string) => void
}

const STATUS_LABEL: Record<ColumnId, string> = {
  backlog: 'Backlog',
  in_progress: 'In Progress',
  review: 'Review',
  done: 'Done',
}

function ListView({ tasks, selectedIds, focusedIndex, onToggleSelect, onClick }: ListViewProps) {
  return (
    <div className="bg-background-card rounded-xl border border-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm" role="grid" aria-label="Task list">
          <thead>
            <tr className="border-b border-border bg-surface-primary">
              <th className="w-10 px-4 py-3 text-left" role="columnheader">
                <span className="sr-only">Select</span>
              </th>
              <th className="px-2 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider" role="columnheader">Task</th>
              <th className="px-2 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider hidden sm:table-cell" role="columnheader">Status</th>
              <th className="px-2 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider hidden md:table-cell" role="columnheader">Priority</th>
              <th className="px-2 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider hidden lg:table-cell" role="columnheader">Due</th>
            </tr>
          </thead>
          <tbody>
            {tasks.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-text-tertiary">
                  No tasks yet. Press <kbd className="px-1.5 py-0.5 rounded bg-glass-heavy text-text-secondary text-[11px] font-mono">n</kbd> to add one.
                </td>
              </tr>
            )}
            {tasks.map((task, idx) => {
              const isSelected = selectedIds.has(task.id)
              const isFocused = focusedIndex === idx
              const priorityBarColor = getPriorityColorBar(task.priority)

              return (
                <tr
                  key={task.id}
                  onClick={() => onClick(task.id)}
                  className={cn(
                    'border-b border-border/50 transition-colors cursor-pointer',
                    'hover:bg-glass-light',
                    isFocused && 'bg-accent-primary/5',
                    isSelected && 'bg-accent-primary/10',
                    task.column === 'done' && 'opacity-60',
                  )}
                  role="row"
                  aria-selected={isSelected}
                >
                  <td className="w-10 px-4 py-3" role="gridcell">
                    <button
                      onClick={(e) => { e.stopPropagation(); onToggleSelect(task.id) }}
                      className={cn(
                        'w-4 h-4 rounded border-2 transition-all',
                        isSelected ? 'bg-accent-primary border-accent-primary' : 'border-border hover:border-accent-primary/50',
                      )}
                      aria-label={`Select ${task.title}`}
                      type="button"
                    >
                      {isSelected && <Check size={14} className="text-white -ml-[1px] -mt-[1px]" strokeWidth={3} />}
                    </button>
                  </td>
                  <td className="px-2 py-3" role="gridcell">
                    <div className="flex items-center gap-2">
                      <div className="w-1 h-8 rounded-full flex-shrink-0" style={{ backgroundColor: priorityBarColor }} />
                      <span className={cn('text-text-primary font-medium', task.column === 'done' && 'line-through')}>
                        {task.title}
                      </span>
                    </div>
                  </td>
                  <td className="px-2 py-3 hidden sm:table-cell" role="gridcell">
                    <span
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                      style={{
                        backgroundColor: `color-mix(in oklab, ${
                          task.column === 'backlog' ? 'var(--accent-info)' :
                          task.column === 'in_progress' ? 'var(--accent-primary)' :
                          task.column === 'review' ? 'var(--accent-warning)' :
                          'var(--accent-success)'
                        } 15%, transparent)`,
                        color: task.column === 'backlog' ? 'var(--accent-info)' :
                          task.column === 'in_progress' ? 'var(--accent-primary)' :
                          task.column === 'review' ? 'var(--accent-warning)' :
                          'var(--accent-success)',
                      }}
                    >
                      {STATUS_LABEL[task.column]}
                    </span>
                  </td>
                  <td className="px-2 py-3 hidden md:table-cell" role="gridcell">
                    <span className="text-xs font-medium capitalize" style={{ color: priorityBarColor }}>
                      {task.priority}
                    </span>
                  </td>
                  <td className="px-2 py-3 hidden lg:table-cell" role="gridcell">
                    <span className="text-xs text-text-tertiary">
                      {task.due_date ? format(new Date(task.due_date), 'MMM d') : '—'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

/* ─── Create Task Modal (Inline Add Form) ───────── */

interface CreateTaskModalProps {
  open: boolean
  onClose: () => void
  onSubmit: (title: string, description: string, priority: TaskPriority, category: TaskCategory, dueDate: string | null, column: ColumnId) => void
}

function CreateTaskModal({ open, onClose, onSubmit }: CreateTaskModalProps) {
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState<TaskPriority>('medium')
  const [category, setCategory] = useState<TaskCategory>('study')
  const [dueDate, setDueDate] = useState('')

  const handleSubmit = useCallback(() => {
    if (!title.trim()) return
    onSubmit(title.trim(), '', priority, category, dueDate || null, 'backlog')
    setTitle('')
    setPriority('medium')
    setCategory('study')
    setDueDate('')
    onClose()
  }, [title, priority, category, dueDate, onSubmit, onClose])

  return (
    <Dialog open={open} onClose={onClose} title="Create Task" size="md">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1.5">Title</label>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleSubmit() }}
            className="w-full bg-surface-primary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary outline-none focus:border-accent-primary/50 focus:ring-1 focus:ring-accent-primary/20 transition-all"
            placeholder="What needs to be done?"
            autoFocus
            aria-label="Task title"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Priority</label>
            <select
              value={priority}
              onChange={e => setPriority(e.target.value as TaskPriority)}
              className="w-full bg-surface-primary border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-primary/50"
              aria-label="Priority"
            >
              <option value="urgent">P0 - Urgent</option>
              <option value="high">P1 - High</option>
              <option value="medium">P2 - Medium</option>
              <option value="low">P3 - Low</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">Category</label>
            <select
              value={category}
              onChange={e => setCategory(e.target.value as TaskCategory)}
              className="w-full bg-surface-primary border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-primary/50"
              aria-label="Category"
            >
              <option value="study">Study</option>
              <option value="project">Project</option>
              <option value="habit">Habit</option>
              <option value="personal">Personal</option>
              <option value="income">Income</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1.5">Due Date</label>
          <input
            type="date"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
            className="w-full bg-surface-primary border border-border rounded-lg px-3 py-2 text-sm text-text-primary outline-none focus:border-accent-primary/50"
            aria-label="Due date"
          />
        </div>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>Cancel</Button>
          <Button variant="primary" className="flex-1" onClick={handleSubmit} disabled={!title.trim()}>
            <Plus size={16} />
            Create Task
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

/* ─── Column Component ──────────────────────────── */

interface ColumnContainerProps {
  column: ColumnDef
  tasks: KanbanTask[]
  selectedIds: Set<string>
  focusedTaskId: string | null
  isAdding: boolean
  onAddStart: () => void
  onAddCancel: () => void
  onAddSubmit: (title: string, column: ColumnId) => void
  onToggleSelect: (id: string) => void
  onClickCard: (id: string) => void
  onToggleSelectAll: () => void
}

function ColumnContainer({
  column,
  tasks,
  selectedIds,
  focusedTaskId,
  isAdding,
  onAddStart,
  onAddCancel,
  onAddSubmit,
  onToggleSelect,
  onClickCard,
  onToggleSelectAll,
}: ColumnContainerProps) {
  const { setNodeRef, isOver } = useDroppable({ id: `column-${column.id}` })
  const columnSelectedCount = tasks.filter(t => selectedIds.has(t.id)).length
  const allSelected = tasks.length > 0 && columnSelectedCount === tasks.length

  return (
    <div
      className={cn(
        'flex flex-col rounded-xl border transition-all duration-200 min-w-[260px] w-[280px] flex-shrink-0',
        column.borderClass,
        column.bgClass,
        isOver && 'ring-2 ring-accent-primary/30 shadow-glow-sm',
      )}
      role="listbox"
      aria-label={`${column.title} column`}
      aria-describedby={`col-count-${column.id}`}
    >
      {/* Column header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: `var(${column.accentVar})` }} />
          <h3 className="text-sm font-display font-semibold text-text-primary">{column.title}</h3>
          <span
            id={`col-count-${column.id}`}
            className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-[11px] font-medium bg-glass-heavy text-text-secondary"
          >
            {tasks.length}
          </span>
        </div>
        {tasks.length > 0 && (
          <button
            onClick={(e) => { e.stopPropagation(); onToggleSelectAll() }}
            className={cn(
              'w-4 h-4 rounded border-2 transition-all flex-shrink-0',
              allSelected ? 'bg-accent-primary border-accent-primary' : 'border-border hover:border-accent-primary/50',
            )}
            aria-label={allSelected ? 'Deselect all tasks' : 'Select all tasks'}
            type="button"
          >
            {allSelected && <Check size={14} className="text-white -ml-[1px] -mt-[1px]" strokeWidth={3} />}
          </button>
        )}
      </div>

      {/* Task list */}
      <div
        ref={setNodeRef}
        className="flex-1 space-y-1.5 p-2 overflow-y-auto min-h-[200px] max-h-[calc(100vh-320px)]"
      >
        <SortableContext items={tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
          <AnimatePresence mode="popLayout">
            {tasks.length === 0 && (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-xs text-text-tertiary">No tasks</p>
                <p className="text-[11px] text-text-tertiary/60 mt-0.5">Drop tasks here or add one</p>
              </div>
            )}
            {tasks.map(task => (
              <SortableKanbanCard
                key={task.id}
                task={task}
                isSelected={selectedIds.has(task.id)}
                isFocused={focusedTaskId === task.id}
                onToggleSelect={onToggleSelect}
                onClick={onClickCard}
              />
            ))}
          </AnimatePresence>
        </SortableContext>
      </div>

      {/* Add card footer */}
      <div className="border-t border-border/50 px-3 py-2">
        {isAdding ? (
          <InlineAddForm columnId={column.id} onSubmit={onAddSubmit} onCancel={onAddCancel} />
        ) : (
          <button
            onClick={onAddStart}
            className="w-full flex items-center gap-2 px-2 py-2 rounded-lg text-xs text-text-tertiary hover:text-text-secondary hover:bg-glass-light transition-all"
            type="button"
            aria-label={`Add card to ${column.title}`}
          >
            <Plus size={14} />
            <span>Add Card</span>
            <kbd className="ml-auto px-1 py-0.5 rounded bg-glass-heavy text-text-tertiary text-[10px] font-mono">n</kbd>
          </button>
        )}
      </div>
    </div>
  )
}

/* ─── Main Page ─────────────────────────────────── */

export default function TasksPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const { tasks, loading, error, fetchTasks, addTask, updateTask, deleteTask, completeTask } = useTaskStore()

  const [mounted, setMounted] = useState(false)
  const [initialLoaded, setInitialLoaded] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!authLoading && user) {
      fetchTasks().finally(() => setInitialLoaded(true))
    }
  }, [authLoading, user, fetchTasks])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [authLoading, user, router])

  /* ── State ──────────────────────────────────── */

  const [viewMode, setViewMode] = useState<'board' | 'list'>('board')
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [focusedIndex, setFocusedIndex] = useState(-1)
  const [activeDragTask, setActiveDragTask] = useState<KanbanTask | null>(null)
  const [addingToColumn, setAddingToColumn] = useState<ColumnId | null>(null)
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null)
  const [suggestion, setSuggestion] = useState<AISuggestion>({
    visible: true,
    taskTitle: 'Complete Docker course',
    fromColumn: 'Backlog',
    toColumn: 'In Progress',
    reason: "it's been in Backlog for 5 days and has a due date next week",
  })

  /* ── Persist view mode ──────────────────────── */

  useEffect(() => {
    const saved = localStorage.getItem('task-view-mode')
    if (saved === 'board' || saved === 'list') setViewMode(saved)
  }, [])

  const handleViewToggle = useCallback((mode: 'board' | 'list') => {
    setViewMode(mode)
    setSelectedIds(new Set())
    setFocusedIndex(-1)
    localStorage.setItem('task-view-mode', mode)
  }, [])

  /* ── Derived data ───────────────────────────── */

  const allTasks = useMemo(() => {
    return tasks.map(t => {
      const col: ColumnId = t.status === 'completed' ? 'done' : t.status === 'in_progress' ? 'in_progress' : 'backlog'
      return { ...t, column: col, tags: t.tags ?? [] } as KanbanTask
    })
  }, [tasks])

  const tasksByColumn = useMemo(() => {
    const grouped: Record<ColumnId, KanbanTask[]> = { backlog: [], in_progress: [], review: [], done: [] }
    for (const t of allTasks) {
      grouped[t.column].push(t)
    }
    return grouped
  }, [allTasks])

  /* ── DnD Sensors ────────────────────────────── */

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  /* ── Find column for a task ──────────────────── */

  const findColumnForTask = useCallback((taskId: string): ColumnId | null => {
    for (const col of COLUMN_IDS) {
      if (tasksByColumn[col].some(t => t.id === taskId)) return col
    }
    return null
  }, [tasksByColumn])

  /* ── DnD Handlers ───────────────────────────── */

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const taskId = String(event.active.id)
    for (const col of COLUMN_IDS) {
      const found = tasksByColumn[col].find(t => t.id === taskId)
      if (found) {
        setActiveDragTask(found)
        return
      }
    }
  }, [tasksByColumn])

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    setActiveDragTask(null)
    const { active, over } = event
    if (!over || active.id === over.id) return

    const activeId = String(active.id)
    const overId = String(over.id)

    const sourceCol = findColumnForTask(activeId)
    if (!sourceCol) return

    let destCol: ColumnId | null = null

    if (overId.startsWith('column-')) {
      destCol = overId.replace('column-', '') as ColumnId
    } else {
      destCol = findColumnForTask(overId)
    }

    if (!destCol || sourceCol === destCol) return

    updateTask(activeId, {
      status: columnToStatus(destCol),
      completed_at: destCol === 'done' ? new Date().toISOString() : undefined,
    })
    setSelectedIds(new Set())
  }, [findColumnForTask, updateTask])

  const handleDragCancel = useCallback(() => {
    setActiveDragTask(null)
  }, [])

  /* ── Card operations ─────────────────────────── */

  const handleAddTask = useCallback((title: string, column: ColumnId) => {
    addTask({ title, status: columnToStatus(column), priority: 'medium', tags: [] })
    setAddingToColumn(null)
  }, [addTask])

  const handleCreateTask = useCallback((
    title: string,
    _description: string,
    priority: TaskPriority,
    category: TaskCategory,
    dueDate: string | null,
    column: ColumnId,
  ) => {
    addTask({
      title,
      description: _description,
      priority,
      category,
      status: columnToStatus(column),
      due_date: dueDate ?? undefined,
      tags: [category],
    })
  }, [addTask])

  const handleCompleteSelected = useCallback(() => {
    selectedIds.forEach(id => completeTask(id))
    setSelectedIds(new Set())
  }, [selectedIds, completeTask])

  const handleBulkMove = useCallback((targetCol: ColumnId) => {
    selectedIds.forEach(id => {
      updateTask(id, {
        status: columnToStatus(targetCol),
        completed_at: targetCol === 'done' ? new Date().toISOString() : undefined,
      })
    })
    setSelectedIds(new Set())
  }, [selectedIds, updateTask])

  const handleDeleteSelected = useCallback(() => {
    selectedIds.forEach(id => deleteTask(id))
    setSelectedIds(new Set())
  }, [selectedIds, deleteTask])

  const handleAcceptSuggestion = useCallback(() => {
    const targetTask = allTasks.find(t => t.title === suggestion.taskTitle && t.column === 'backlog')
    if (targetTask) {
      updateTask(targetTask.id, { status: 'in_progress' })
    }
    setSuggestion(s => ({ ...s, visible: false }))
  }, [suggestion.taskTitle, allTasks, updateTask])

  const handleDismissSuggestion = useCallback(() => {
    setSuggestion(s => ({ ...s, visible: false }))
  }, [])

  /* ── Selection handlers ───────────────────────── */

  const handleToggleSelect = useCallback((id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }, [])

  const handleToggleSelectAll = useCallback(() => {
    const allIds = new Set(allTasks.map(t => t.id))
    if (selectedIds.size === allIds.size) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(allIds)
    }
  }, [allTasks, selectedIds])

  const handleClickCard = useCallback((id: string) => {
    router.push(`/tasks/${id}`)
  }, [router])

  /* ── Keyboard Shortcuts ───────────────────────── */

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement).tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return

      switch (e.key) {
        case 'n':
          e.preventDefault()
          if (addingToColumn) return
          setCreateModalOpen(true)
          break

        case 'j':
          e.preventDefault()
          setFocusedIndex(p => (p < allTasks.length - 1 ? p + 1 : 0))
          break

        case 'k':
          e.preventDefault()
          setFocusedIndex(p => (p > 0 ? p - 1 : allTasks.length - 1))
          break

        case 'Enter': {
          if (focusedIndex >= 0 && focusedIndex < allTasks.length) {
            e.preventDefault()
            router.push(`/tasks/${allTasks[focusedIndex].id}`)
          }
          break
        }

        case 'c': {
          if (focusedIndex >= 0 && focusedIndex < allTasks.length) {
            e.preventDefault()
            const task = allTasks[focusedIndex]
            if (task.column !== 'done') {
              completeTask(task.id)
            }
          }
          break
        }

        case 'd': {
          if (focusedIndex >= 0 && focusedIndex < allTasks.length) {
            e.preventDefault()
            const task = allTasks[focusedIndex]
            setPendingDeleteId(task.id)
            setDeleteConfirmOpen(true)
          }
          break
        }
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [allTasks, focusedIndex, router, addingToColumn, completeTask])

  const handleConfirmDelete = useCallback(() => {
    const id = pendingDeleteId
    if (!id) return
    deleteTask(id)
    setDeleteConfirmOpen(false)
    setPendingDeleteId(null)
    setSelectedIds(prev => {
      const next = new Set(prev)
      next.delete(id)
      return next
    })
  }, [pendingDeleteId, deleteTask])

  /* ── Loading / Error guards ────────────────── */

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (!initialLoaded) {
    return (
      <div className="min-h-screen bg-background-dark flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  /* ── Render ──────────────────────────────────── */

  return (
    <div className="flex flex-col gap-4 p-4 sm:p-6 min-h-screen">
      {/* Header */}
      <PageHeader
        title="Tasks"
        description="Manage your work across all stages"
        actions={
          <div className="flex items-center gap-2">
            <div className="flex items-center rounded-lg border border-border bg-background-card p-0.5" role="radiogroup" aria-label="View mode">
              <button
                onClick={() => handleViewToggle('board')}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
                  viewMode === 'board'
                    ? 'bg-accent-primary text-white shadow-glow-sm'
                    : 'text-text-secondary hover:text-text-primary',
                )}
                role="radio"
                aria-checked={viewMode === 'board'}
                type="button"
              >
                <Grid3X3 size={14} />
                Board
              </button>
              <button
                onClick={() => handleViewToggle('list')}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
                  viewMode === 'list'
                    ? 'bg-accent-primary text-white shadow-glow-sm'
                    : 'text-text-secondary hover:text-text-primary',
                )}
                role="radio"
                aria-checked={viewMode === 'list'}
                type="button"
              >
                <List size={14} />
                List
              </button>
            </div>
            <Button variant="primary" onClick={() => setCreateModalOpen(true)}>
              <Plus size={16} />
              Add Task
            </Button>
          </div>
        }
      />

      {/* Error banner */}
      {error && (
        <div className="rounded-lg bg-accent-error/10 border border-accent-error/20 px-4 py-3">
          <p className="text-sm text-accent-error">{error}</p>
        </div>
      )}

      {/* AI Suggestion */}
      <AnimatePresence>
        <AISuggestionCard
          suggestion={suggestion}
          onAccept={handleAcceptSuggestion}
          onDismiss={handleDismissSuggestion}
        />
      </AnimatePresence>

      {/* Board View */}
      {viewMode === 'board' && (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
          onDragCancel={handleDragCancel}
        >
          <div className="flex gap-4 overflow-x-auto pb-4 flex-1" style={{ scrollbarWidth: 'thin' }}>
            {COLUMNS.map(col => (
              <ColumnContainer
                key={col.id}
                column={col}
                tasks={tasksByColumn[col.id]}
                selectedIds={selectedIds}
                focusedTaskId={focusedIndex >= 0 && focusedIndex < allTasks.length ? allTasks[focusedIndex].id : null}
                isAdding={addingToColumn === col.id}
                onAddStart={() => setAddingToColumn(col.id)}
                onAddCancel={() => setAddingToColumn(null)}
                onAddSubmit={handleAddTask}
                onToggleSelect={handleToggleSelect}
                onClickCard={handleClickCard}
                onToggleSelectAll={() => {
                  const colTaskIds = tasksByColumn[col.id].map(t => t.id)
                  const allColSelected = colTaskIds.every(id => selectedIds.has(id))
                  if (allColSelected) {
                    setSelectedIds(prev => {
                      const next = new Set(prev)
                      colTaskIds.forEach(id => next.delete(id))
                      return next
                    })
                  } else {
                    setSelectedIds(prev => {
                      const next = new Set(prev)
                      colTaskIds.forEach(id => next.add(id))
                      return next
                    })
                  }
                }}
              />
            ))}
          </div>

          <DragOverlay>
            {activeDragTask && <DragOverlayCard task={activeDragTask} />}
          </DragOverlay>
        </DndContext>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <ListView
          tasks={allTasks}
          selectedIds={selectedIds}
          focusedIndex={focusedIndex}
          onToggleSelect={handleToggleSelect}
          onClick={handleClickCard}
        />
      )}

      {/* Bulk Action Bar */}
      <AnimatePresence>
        {selectedIds.size > 0 && (
          <BulkActionBar
            count={selectedIds.size}
            onComplete={handleCompleteSelected}
            onMove={handleBulkMove}
            onDelete={handleDeleteSelected}
            onClear={() => setSelectedIds(new Set())}
          />
        )}
      </AnimatePresence>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} title="Delete Task" size="sm">
        <div className="space-y-4">
          <p className="text-sm text-text-secondary">
            Are you sure you want to delete this task? This action cannot be undone.
          </p>
          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={() => setDeleteConfirmOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" className="flex-1" onClick={handleConfirmDelete}>
              <Trash2 size={16} />
              Delete
            </Button>
          </div>
        </div>
      </Dialog>

      {/* Create Task Modal */}
      <CreateTaskModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreateTask}
      />

      {/* Keyboard shortcut hints */}
      <div className="fixed bottom-4 right-4 z-40 hidden lg:flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-primary/80 backdrop-blur-md border border-border text-[10px] text-text-tertiary">
        <span><kbd className="px-1 py-0.5 rounded bg-glass-heavy font-mono">n</kbd> New</span>
        <span><kbd className="px-1 py-0.5 rounded bg-glass-heavy font-mono">j</kbd> / <kbd className="px-1 py-0.5 rounded bg-glass-heavy font-mono">k</kbd> Nav</span>
        <span><kbd className="px-1 py-0.5 rounded bg-glass-heavy font-mono">Enter</kbd> Open</span>
        <span><kbd className="px-1 py-0.5 rounded bg-glass-heavy font-mono">c</kbd> Complete</span>
        <span><kbd className="px-1 py-0.5 rounded bg-glass-heavy font-mono">d</kbd> Delete</span>
      </div>
    </div>
  )
}
