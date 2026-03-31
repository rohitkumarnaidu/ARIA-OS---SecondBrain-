import { create } from 'zustand'
import { supabase } from './supabase'

export interface Task {
  id: string
  user_id: string
  title: string
  description?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  category: 'study' | 'project' | 'habit' | 'personal' | 'income'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  estimated_minutes?: number
  due_date?: string
  goal_id?: string
  project_id?: string
  completed_at?: string
  missed_count: number
  dependency_id?: string
  is_recurring: boolean
  recurring_frequency?: string
  created_at: string
  updated_at: string
}

interface TaskStore {
  tasks: Task[]
  loading: boolean
  error: string | null
  fetchTasks: () => Promise<void>
  addTask: (task: Partial<Task>) => Promise<void>
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>
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
      const { data, error } = await supabase
        .from('tasks')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      set({ tasks: data || [], loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  addTask: async (task) => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase
        .from('tasks')
        .insert(task)
        .select()
        .single()
      
      if (error) throw error
      set({ tasks: [data, ...get().tasks], loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  updateTask: async (id, updates) => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase
        .from('tasks')
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      
      if (error) throw error
      set({
        tasks: get().tasks.map(t => t.id === id ? data : t),
        loading: false
      })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  deleteTask: async (id) => {
    set({ loading: true, error: null })
    try {
      const { error } = await supabase
        .from('tasks')
        .delete()
        .eq('id', id)
      
      if (error) throw error
      set({
        tasks: get().tasks.filter(t => t.id !== id),
        loading: false
      })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  completeTask: async (id) => {
    await get().updateTask(id, {
      status: 'completed',
      completed_at: new Date().toISOString()
    })
  },
}))