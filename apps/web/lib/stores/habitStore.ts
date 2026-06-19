import { create } from 'zustand'
import { habitService } from '@/lib/services'
import type { Habit, HabitCreate, HabitUpdate, HabitLog } from '@/lib/types'

interface HabitStore {
  items: Habit[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Habit | undefined
  create: (data: HabitCreate) => Promise<void>
  update: (id: string, data: HabitUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
  log: (habitId: string, data: { date: string; completed: boolean; note?: string }) => Promise<HabitLog | undefined>
}

export const useHabitStore = create<HabitStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await habitService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load habits'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await habitService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create habit'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await habitService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update habit'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await habitService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete habit'
      set({ error: message, loading: false })
    }
  },

  log: async (habitId, data) => {
    set({ loading: true, error: null })
    try {
      const result = await habitService.log(habitId, data)
      set({ loading: false })
      return result
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to log habit'
      set({ error: message, loading: false })
    }
  },
}))
