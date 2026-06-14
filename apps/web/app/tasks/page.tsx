'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useTaskStore, Task } from '@/lib/taskStore'
import { 
  Plus, CheckCircle, Clock, Trash2, Edit2, 
  X, Loader2, AlertCircle, ListTodo, Layers, 
  ArrowDown, ArrowUp, GripVertical, Calendar
} from 'lucide-react'
import clsx from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'

const priorities = ['low', 'medium', 'high', 'urgent'] as const
const categories = ['study', 'project', 'habit', 'personal', 'income'] as const

export default function TasksPage() {
  const { user, loading: authLoading } = useAuth()
  const { tasks, fetchTasks, addTask, updateTask, deleteTask, completeTask } = useTaskStore()
  const router = useRouter()
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [mounted, setMounted] = useState(false)
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')

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

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchTasks()
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

  const getPriorityStyles = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-priority-urgent/10 text-priority-urgent border-priority-urgent/20'
      case 'high': return 'bg-priority-high/10 text-priority-high border-priority-high/20'
      case 'medium': return 'bg-priority-medium/10 text-priority-medium border-priority-medium/20'
      case 'low': return 'bg-priority-low/10 text-priority-low border-priority-low/20'
      default: return 'bg-background-elevated text-text-secondary border-border'
    }
  }

  const getCategoryIcon = (category: string) => {
    return category
  }

  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress')
  const completedTasks = tasks.filter(t => t.status === 'completed')

  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(t => t.status === filter)

  if (!mounted || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="relative">
          <div className="w-12 h-12 rounded-xl border-2 border-accent-primary/30 animate-pulse-glow" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div className="space-y-1">
          <h1 className="text-3xl font-display font-bold">
            <span className="text-gradient">Tasks</span>
          </h1>
          <p className="text-text-secondary">Manage your tasks and stay productive</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary gap-2"
        >
          <Plus size={20} />
          Add Task
        </button>
      </motion.div>

      {/* Stats Cards */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-3 gap-4"
      >
        {[
          { label: 'To Do', count: pendingTasks.length, icon: ListTodo, color: 'accent-primary' },
          { label: 'In Progress', count: inProgressTasks.length, icon: Layers, color: 'accent-warning' },
          { label: 'Done', count: completedTasks.length, icon: CheckCircle, color: 'accent-success' },
        ].map((stat, i) => (
          <motion.div 
            key={stat.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className="card group cursor-pointer hover:border-accent-primary/30 transition-all duration-300"
            onClick={() => setFilter(stat.label.toLowerCase().replace(' ', '_') as any)}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-text-tertiary uppercase tracking-wider">{stat.label}</span>
              <stat.icon size={18} className={`text-${stat.color} opacity-60 group-hover:opacity-100 transition-opacity`} />
            </div>
            <div className="text-3xl font-display font-bold text-text-primary">{stat.count}</div>
          </motion.div>
        ))}
      </motion.div>

      {/* Filter Tabs */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex gap-2 overflow-x-auto no-scrollbar pb-2"
      >
        {[
          { label: 'All Tasks', value: 'all', count: tasks.length },
          { label: 'To Do', value: 'pending', count: pendingTasks.length },
          { label: 'In Progress', value: 'in_progress', count: inProgressTasks.length },
          { label: 'Done', value: 'completed', count: completedTasks.length },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setFilter(tab.value as any)}
            className={clsx(
              'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200',
              filter === tab.value 
                ? 'bg-accent-primary text-white shadow-glow-sm' 
                : 'bg-background-elevated text-text-secondary hover:text-text-primary border border-border hover:border-border-light'
            )}
          >
            {tab.label}
            <span className={clsx(
              'ml-2 px-1.5 py-0.5 rounded text-xs',
              filter === tab.value ? 'bg-white/20' : 'bg-background-card'
            )}>
              {tab.count}
            </span>
          </button>
        ))}
      </motion.div>

      {/* Tasks List */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="space-y-3"
      >
        <AnimatePresence mode="popLayout">
          {filteredTasks.length > 0 ? (
            filteredTasks.map((task, index) => (
              <motion.div
                key={task.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: index * 0.05 }}
                className={clsx(
                  'card card-interactive group',
                  task.status === 'completed' && 'opacity-60'
                )}
              >
                <div className="flex items-start gap-4">
                  {/* Drag Handle */}
                  <div className="flex-shrink-0 mt-1">
                    <GripVertical size={16} className="text-text-tertiary opacity-30 group-hover:opacity-100 transition-opacity cursor-grab" />
                  </div>

                  {/* Priority Indicator */}
                  <div className={clsx(
                    'flex-shrink-0 w-1.5 h-12 rounded-full',
                    task.priority === 'urgent' ? 'bg-priority-urgent' :
                    task.priority === 'high' ? 'bg-priority-high' :
                    task.priority === 'medium' ? 'bg-priority-medium' :
                    'bg-priority-low'
                  )} />

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <h3 className={clsx(
                          'font-medium text-text-primary group-hover:text-accent-primary transition-colors',
                          task.status === 'completed' && 'line-through text-text-secondary'
                        )}>
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className="text-sm text-text-tertiary line-clamp-2">{task.description}</p>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {task.status !== 'completed' && (
                          <button
                            onClick={() => completeTask(task.id)}
                            className="p-2 rounded-lg hover:bg-accent-success/10 touch-target"
                            aria-label="Complete task"
                          >
                            <CheckCircle size={16} className="text-accent-success" />
                          </button>
                        )}
                        <button
                          onClick={() => setEditingTask(task)}
                          className="p-2 rounded-lg hover:bg-background-elevated touch-target"
                          aria-label="Edit task"
                        >
                          <Edit2 size={16} className="text-text-tertiary" />
                        </button>
                        <button
                          onClick={() => deleteTask(task.id)}
                          className="p-2 rounded-lg hover:bg-accent-error/10 touch-target"
                          aria-label="Delete task"
                        >
                          <Trash2 size={16} className="text-accent-error" />
                        </button>
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="flex items-center gap-2 mt-3 flex-wrap">
                      <span className={clsx(
                        'px-2.5 py-1 rounded-md text-xs font-medium border',
                        getPriorityStyles(task.priority)
                      )}>
                        {task.priority}
                      </span>
                      <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-background-elevated text-text-secondary border border-border capitalize">
                        {task.category}
                      </span>
                      {task.estimated_minutes && (
                        <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs text-text-tertiary">
                          <Clock size={12} />
                          {task.estimated_minutes} min
                        </span>
                      )}
                      {task.due_date && (
                        <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs text-text-tertiary">
                          <Calendar size={12} />
                          {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="card text-center py-16"
            >
              <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 flex items-center justify-center mx-auto mb-4">
                <ListTodo size={40} className="text-accent-primary" />
              </div>
              <h3 className="text-lg font-display font-semibold text-text-primary mb-2">No tasks found</h3>
              <p className="text-text-tertiary mb-6">Start by adding your first task</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="btn btn-primary mx-auto"
              >
                <Plus size={20} />
                Create Task
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Add Task Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-task-title"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-lg shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 id="add-task-title" className="text-xl font-display font-semibold text-text-primary">Create New Task</h2>
                <button 
                  onClick={() => setShowAddModal(false)} 
                  className="p-2 hover:bg-background-elevated rounded-lg touch-target"
                  aria-label="Close modal"
                >
                  <X size={20} className="text-text-tertiary" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="task-title" className="block text-sm font-medium text-text-primary mb-2">
                    Title <span className="text-accent-error">*</span>
                  </label>
                  <input
                    id="task-title"
                    type="text"
                    value={newTask.title}
                    onChange={e => setNewTask({ ...newTask, title: e.target.value })}
                    className="input"
                    placeholder="What needs to be done?"
                    autoFocus
                  />
                </div>

                <div>
                  <label htmlFor="task-description" className="block text-sm font-medium text-text-primary mb-2">
                    Description
                  </label>
                  <textarea
                    id="task-description"
                    value={newTask.description}
                    onChange={e => setNewTask({ ...newTask, description: e.target.value })}
                    className="input min-h-[80px] resize-none"
                    placeholder="Add more details..."
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="task-priority" className="block text-sm font-medium text-text-primary mb-2">
                      Priority
                    </label>
                    <select
                      id="task-priority"
                      value={newTask.priority}
                      onChange={e => setNewTask({ ...newTask, priority: e.target.value as any })}
                      className="input"
                    >
                      {priorities.map(p => (
                        <option key={p} value={p} className="capitalize">{p}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="task-category" className="block text-sm font-medium text-text-primary mb-2">
                      Category
                    </label>
                    <select
                      id="task-category"
                      value={newTask.category}
                      onChange={e => setNewTask({ ...newTask, category: e.target.value as any })}
                      className="input capitalize"
                    >
                      {categories.map(c => (
                        <option key={c} value={c} className="capitalize">{c}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="task-time" className="block text-sm font-medium text-text-primary mb-2">
                      Est. Minutes
                    </label>
                    <input
                      id="task-time"
                      type="number"
                      value={newTask.estimated_minutes}
                      onChange={e => setNewTask({ ...newTask, estimated_minutes: parseInt(e.target.value) || 30 })}
                      className="input"
                      min={5}
                      max={480}
                    />
                  </div>

                  <div>
                    <label htmlFor="task-due" className="block text-sm font-medium text-text-primary mb-2">
                      Due Date
                    </label>
                    <input
                      id="task-due"
                      type="date"
                      value={newTask.due_date}
                      onChange={e => setNewTask({ ...newTask, due_date: e.target.value })}
                      className="input"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <input
                    type="checkbox"
                    id="task-recurring"
                    checked={newTask.is_recurring}
                    onChange={e => setNewTask({ ...newTask, is_recurring: e.target.checked })}
                    className="w-4 h-4 rounded border-border text-accent-primary focus:ring-accent-primary"
                  />
                  <label htmlFor="task-recurring" className="text-sm text-text-secondary">
                    Make this a recurring task
                  </label>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button 
                  onClick={() => setShowAddModal(false)} 
                  className="btn btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleAddTask}
                  disabled={!newTask.title.trim()}
                  className="btn btn-primary flex-1"
                >
                  Create Task
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edit Task Modal */}
      <AnimatePresence>
        {editingTask && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4"
            role="dialog"
            aria-modal="true"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-lg"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-display font-semibold text-text-primary">Edit Task</h2>
                <button 
                  onClick={() => setEditingTask(null)} 
                  className="p-2 hover:bg-background-elevated rounded-lg touch-target"
                >
                  <X size={20} className="text-text-tertiary" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Title</label>
                  <input
                    type="text"
                    value={editingTask.title}
                    onChange={e => setEditingTask({ ...editingTask, title: e.target.value })}
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">Description</label>
                  <textarea
                    value={editingTask.description || ''}
                    onChange={e => setEditingTask({ ...editingTask, description: e.target.value })}
                    className="input min-h-[80px] resize-none"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Priority</label>
                    <select
                      value={editingTask.priority}
                      onChange={e => setEditingTask({ ...editingTask, priority: e.target.value as any })}
                      className="input"
                    >
                      {priorities.map(p => (
                        <option key={p} value={p} className="capitalize">{p}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">Category</label>
                    <select
                      value={editingTask.category}
                      onChange={e => setEditingTask({ ...editingTask, category: e.target.value as any })}
                      className="input capitalize"
                    >
                      {categories.map(c => (
                        <option key={c} value={c} className="capitalize">{c}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={() => setEditingTask(null)} className="btn btn-secondary flex-1">
                  Cancel
                </button>
                <button onClick={handleUpdateTask} className="btn btn-primary flex-1">
                  Save Changes
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}