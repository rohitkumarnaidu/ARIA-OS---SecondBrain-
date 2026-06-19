import { create } from 'zustand'
import { ideaService } from '@/lib/services'
import type { Idea, IdeaCreate, IdeaUpdate } from '@/lib/types'

interface IdeaStore {
  items: Idea[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Idea | undefined
  create: (data: IdeaCreate) => Promise<void>
  update: (id: string, data: IdeaUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useIdeaStore = create<IdeaStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await ideaService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load ideas'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await ideaService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create idea'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await ideaService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update idea'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await ideaService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete idea'
      set({ error: message, loading: false })
    }
  },
}))
