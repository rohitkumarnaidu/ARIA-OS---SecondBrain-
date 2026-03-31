'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore, Task } from '@/lib/taskStore'
import { 
  Plus, CheckCircle, Clock, Trash2, Edit2, 
  X, ChevronDown, Loader2
} from 'lucide-react'
import clsx from 'clsx'

const priorities = ['low', 'medium', 'high', 'urgent'] as const
const categories = ['study', 'project', 'habit', 'personal', 'income'] as const
const statuses = ['pending', 'in_progress', 'completed', 'cancelled'] as const

export default function TasksPage() {
  const { user, loading: authLoading } = useAuth()
  const { tasks, fetchTasks, addTask, updateTask, deleteTask, completeTask, loading } = useTaskStore()
  const router = useRouter()
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [mounted, setMounted] = useState(false)

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium' as typeof priorities[number],
    category: 'personal' as typeof categories[number],
    estimated_minutes: 30,
    due_date: '',
    dependency_id: '',
    is_recurring: false,
    recurring_frequency: 'daily',
  })

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchTasks()
    }
  }, [user, authLoading, router, fetchTasks])

  const handleAddTask = async () => {
    if (!newTask.title.trim()) return
    
    await addTask({
      ...newTask,
      due_date: newTask.due_date || undefined,
      dependency_id: newTask.dependency_id || undefined,
      is_recurring: newTask.is_recurring,
      recurring_frequency: newTask.is_recurring ? newTask.recurring_frequency : undefined,
      status: 'pending',
    })
    
    setNewTask({
      title: '',
      description: '',
      priority: 'medium',
      category: 'personal',
      estimated_minutes: 30,
      due_date: '',
      dependency_id: '',
      is_recurring: false,
      recurring_frequency: 'daily',
    })
    setShowAddModal(false)
  }

  const handleUpdateTask = async () => {
    if (!editingTask) return
    
    await updateTask(editingTask.id, {
      title: editingTask.title,
      description: editingTask.description,
      priority: editingTask.priority,
      category: editingTask.category,
      estimated_minutes: editingTask.estimated_minutes,
      due_date: editingTask.due_date,
    })
    
    setEditingTask(null)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-priority-urgent text-white'
      case 'high': return 'bg-priority-high text-white'
      case 'medium': return 'bg-priority-medium text-black'
      case 'low': return 'bg-priority-low text-white'
      default: return 'bg-background-elevated text-text-secondary'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle size={18} className="text-accent-secondary" />
      case 'in_progress': return <Clock size={18} className="text-accent-info" />
      default: return <Clock size={18} className="text-text-muted" />
    }
  }

  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress')
  const completedTasks = tasks.filter(t => t.status === 'completed')

  if (!mounted || authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin w-8 h-8 text-accent-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Tasks</h1>
          <p className="text-text-secondary">Manage your tasks and stay productive</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90 transition-colors"
        >
          <Plus size={20} />
          Add Task
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{pendingTasks.length}</div>
          <div className="text-text-secondary text-sm">Pending</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{inProgressTasks.length}</div>
          <div className="text-text-secondary text-sm">In Progress</div>
        </div>
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="text-2xl font-bold text-text-primary">{completedTasks.length}</div>
          <div className="text-text-secondary text-sm">Completed</div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-3 gap-6">
        {/* Pending Column */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-text-primary">To Do</h2>
            <span className="text-text-muted text-sm">{pendingTasks.length}</span>
          </div>
          <div className="space-y-3">
            {pendingTasks.map(task => (
              <div key={task.id} className="bg-background-elevated rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-text-primary font-medium">{task.title}</h3>
                  <div className="flex gap-1">
                    <button
                      onClick={() => setEditingTask(task)}
                      className="p-1 hover:bg-background-card rounded"
                    >
                      <Edit2 size={14} className="text-text-muted" />
                    </button>
                    <button
                      onClick={() => deleteTask(task.id)}
                      className="p-1 hover:bg-background-card rounded"
                    >
                      <Trash2 size={14} className="text-accent-error" />
                    </button>
                  </div>
                </div>
                {task.description && (
                  <p className="text-text-muted text-sm mb-2 line-clamp-2">{task.description}</p>
                )}
                <div className="flex items-center gap-2">
                  <span className={clsx('text-xs px-2 py-1 rounded', getPriorityColor(task.priority))}>
                    {task.priority}
                  </span>
                  <span className="text-xs text-text-muted">{task.category}</span>
                  {task.estimated_minutes && (
                    <span className="text-xs text-text-muted ml-auto">{task.estimated_minutes} min</span>
                  )}
                </div>
                <button
                  onClick={() => completeTask(task.id)}
                  className="w-full mt-3 text-sm text-accent-secondary hover:underline"
                >
                  Mark Complete
                </button>
              </div>
            ))}
            {pendingTasks.length === 0 && (
              <div className="text-center py-8 text-text-muted">No tasks</div>
            )}
          </div>
        </div>

        {/* In Progress Column */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-text-primary">In Progress</h2>
            <span className="text-text-muted text-sm">{inProgressTasks.length}</span>
          </div>
          <div className="space-y-3">
            {inProgressTasks.map(task => (
              <div key={task.id} className="bg-background-elevated rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-text-primary font-medium">{task.title}</h3>
                  <button
                    onClick={() => completeTask(task.id)}
                    className="p-1 hover:bg-background-card rounded"
                  >
                    <CheckCircle size={16} className="text-accent-secondary" />
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <span className={clsx('text-xs px-2 py-1 rounded', getPriorityColor(task.priority))}>
                    {task.priority}
                  </span>
                  <span className="text-xs text-text-muted">{task.category}</span>
                </div>
              </div>
            ))}
            {inProgressTasks.length === 0 && (
              <div className="text-center py-8 text-text-muted">No tasks</div>
            )}
          </div>
        </div>

        {/* Completed Column */}
        <div className="bg-background-card border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-text-primary">Done</h2>
            <span className="text-text-muted text-sm">{completedTasks.length}</span>
          </div>
          <div className="space-y-3">
            {completedTasks.map(task => (
              <div key={task.id} className="bg-background-elevated rounded-lg p-4 opacity-75">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-text-primary font-medium line-through">{task.title}</h3>
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="p-1 hover:bg-background-card rounded"
                  >
                    <Trash2 size={14} className="text-text-muted" />
                  </button>
                </div>
                <div className="text-xs text-text-muted">
                  Completed {task.completed_at ? new Date(task.completed_at).toLocaleDateString() : 'recently'}
                </div>
              </div>
            ))}
            {completedTasks.length === 0 && (
              <div className="text-center py-8 text-text-muted">No completed tasks</div>
            )}
          </div>
        </div>
      </div>

      {/* Add Task Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Add Task</h2>
              <button onClick={() => setShowAddModal(false)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-text-secondary text-sm mb-1">Title</label>
                <input
                  type="text"
                  value={newTask.title}
                  onChange={e => setNewTask({ ...newTask, title: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  placeholder="Enter task title"
                />
              </div>
              
              <div>
                <label className="block text-text-secondary text-sm mb-1">Description</label>
                <textarea
                  value={newTask.description}
                  onChange={e => setNewTask({ ...newTask, description: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  rows={3}
                  placeholder="Optional description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Priority</label>
                  <select
                    value={newTask.priority}
                    onChange={e => setNewTask({ ...newTask, priority: e.target.value as any })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  >
                    {priorities.map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Category</label>
                  <select
                    value={newTask.category}
                    onChange={e => setNewTask({ ...newTask, category: e.target.value as any })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  >
                    {categories.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Est. Minutes</label>
                  <input
                    type="number"
                    value={newTask.estimated_minutes}
                    onChange={e => setNewTask({ ...newTask, estimated_minutes: parseInt(e.target.value) || 30 })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                    min={5}
                    step={5}
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Due Date</label>
                  <input
                    type="date"
                    value={newTask.due_date}
                    onChange={e => setNewTask({ ...newTask, due_date: e.target.value })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_recurring"
                  checked={newTask.is_recurring}
                  onChange={e => setNewTask({ ...newTask, is_recurring: e.target.checked })}
                  className="rounded border-border"
                />
                <label htmlFor="is_recurring" className="text-text-secondary text-sm">Recurring Task</label>
                {newTask.is_recurring && (
                  <select
                    value={newTask.recurring_frequency}
                    onChange={e => setNewTask({ ...newTask, recurring_frequency: e.target.value })}
                    className="ml-2 bg-background-dark border border-border rounded-lg px-3 py-1 text-text-primary text-sm"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                )}
              </div>

              <button
                onClick={handleAddTask}
                className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90 transition-colors"
              >
                Add Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Edit Task</h2>
              <button onClick={() => setEditingTask(null)} className="text-text-muted hover:text-text-primary">
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-text-secondary text-sm mb-1">Title</label>
                <input
                  type="text"
                  value={editingTask.title}
                  onChange={e => setEditingTask({ ...editingTask, title: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                />
              </div>
              
              <div>
                <label className="block text-text-secondary text-sm mb-1">Description</label>
                <textarea
                  value={editingTask.description || ''}
                  onChange={e => setEditingTask({ ...editingTask, description: e.target.value })}
                  className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Priority</label>
                  <select
                    value={editingTask.priority}
                    onChange={e => setEditingTask({ ...editingTask, priority: e.target.value as any })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  >
                    {priorities.map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Category</label>
                  <select
                    value={editingTask.category}
                    onChange={e => setEditingTask({ ...editingTask, category: e.target.value as any })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  >
                    {categories.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Est. Minutes</label>
                  <input
                    type="number"
                    value={editingTask.estimated_minutes || 30}
                    onChange={e => setEditingTask({ ...editingTask, estimated_minutes: parseInt(e.target.value) || 30 })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                    min={5}
                  />
                </div>
                <div>
                  <label className="block text-text-secondary text-sm mb-1">Due Date</label>
                  <input
                    type="date"
                    value={editingTask.due_date?.split('T')[0] || ''}
                    onChange={e => setEditingTask({ ...editingTask, due_date: e.target.value })}
                    className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary"
                  />
                </div>
              </div>

              <button
                onClick={handleUpdateTask}
                className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90 transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}