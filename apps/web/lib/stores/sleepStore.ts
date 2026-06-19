import { create } from 'zustand'
import { sleepService } from '@/lib/services'
import type { SleepLog, SleepLogCreate } from '@/lib/types'

interface SleepStore {
  items: SleepLog[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => SleepLog | undefined
  create: (data: SleepLogCreate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useSleepStore = create<SleepStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await sleepService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load sleep logs'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await sleepService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create sleep log'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await sleepService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete sleep log'
      set({ error: message, loading: false })
    }
  },
}))
