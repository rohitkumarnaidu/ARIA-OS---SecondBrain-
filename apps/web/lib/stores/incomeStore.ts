import { create } from 'zustand'
import { incomeService } from '@/lib/services'
import type { IncomeEntry, IncomeEntryCreate } from '@/lib/types'

interface IncomeStore {
  items: IncomeEntry[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => IncomeEntry | undefined
  create: (data: IncomeEntryCreate) => Promise<void>
  update: (id: string, data: Partial<IncomeEntryCreate>) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useIncomeStore = create<IncomeStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await incomeService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load income entries'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await incomeService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create income entry'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await incomeService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update income entry'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await incomeService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete income entry'
      set({ error: message, loading: false })
    }
  },
}))
