import { create } from 'zustand'
import { taskService } from '@/lib/services'
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types'

interface TaskStore {
  tasks: Task[]
  loading: boolean
  error: string | null
  fetchTasks: () => Promise<void>
  getById: (id: string) => Task | undefined
  addTask: (task: TaskCreate) => Promise<void>
  updateTask: (id: string, updates: TaskUpdate) => Promise<void>
  deleteTask: (id: string) => Promise<void>
  completeTask: (id: string) => Promise<void>
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null })
    try {
      const data = await taskService.list()
      set({ tasks: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load tasks'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().tasks.find(t => t.id === id),

  addTask: async (task) => {
    set({ loading: true, error: null })
    try {
      const created = await taskService.create(task)
      set({ tasks: [created, ...get().tasks], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create task'
      set({ error: message, loading: false })
    }
  },

  updateTask: async (id, updates) => {
    set({ loading: true, error: null })
    try {
      const updated = await taskService.update(id, updates)
      set({ tasks: get().tasks.map(t => t.id === id ? updated : t), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update task'
      set({ error: message, loading: false })
    }
  },

  deleteTask: async (id) => {
    set({ loading: true, error: null })
    try {
      await taskService.delete(id)
      set({ tasks: get().tasks.filter(t => t.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete task'
      set({ error: message, loading: false })
    }
  },

  completeTask: async (id) => {
    set({ loading: true, error: null })
    try {
      const updated = await taskService.complete(id)
      set({ tasks: get().tasks.map(t => t.id === id ? updated : t), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to complete task'
      set({ error: message, loading: false })
    }
  },
}))
