import { create } from 'zustand'
import { resourceService } from '@/lib/services'
import type { Resource, ResourceCreate, ResourceUpdate } from '@/lib/types'

interface ResourceStore {
  items: Resource[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Resource | undefined
  create: (data: ResourceCreate) => Promise<void>
  update: (id: string, data: ResourceUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useResourceStore = create<ResourceStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await resourceService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load resources'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await resourceService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create resource'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await resourceService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update resource'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await resourceService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete resource'
      set({ error: message, loading: false })
    }
  },
}))
