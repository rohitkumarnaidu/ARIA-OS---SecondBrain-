import { create } from 'zustand'
import { goalService } from '@/lib/services'
import type { Goal, GoalCreate, GoalUpdate } from '@/lib/types'

interface GoalStore {
  items: Goal[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Goal | undefined
  create: (data: GoalCreate) => Promise<void>
  update: (id: string, data: GoalUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useGoalStore = create<GoalStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await goalService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load goals'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await goalService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create goal'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await goalService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update goal'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await goalService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete goal'
      set({ error: message, loading: false })
    }
  },
}))
