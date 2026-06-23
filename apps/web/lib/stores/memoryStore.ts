import { create } from 'zustand'
import { memoryService } from '@/lib/services'
import type { Memory, MemoryCreate, MemoryUpdate } from '@/lib/types'

interface MemoryStore {
  items: Memory[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Memory | undefined
  create: (data: MemoryCreate) => Promise<void>
  update: (id: string, data: MemoryUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useMemoryStore = create<MemoryStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await memoryService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load memories'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await memoryService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create memory'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await memoryService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update memory'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await memoryService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete memory'
      set({ error: message, loading: false })
    }
  },
}))
