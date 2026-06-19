import { create } from 'zustand'
import { opportunityService } from '@/lib/services'
import type { Opportunity, OpportunityCreate, OpportunityUpdate } from '@/lib/types'

interface OpportunityStore {
  items: Opportunity[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Opportunity | undefined
  create: (data: OpportunityCreate) => Promise<void>
  update: (id: string, data: OpportunityUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useOpportunityStore = create<OpportunityStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await opportunityService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load opportunities'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await opportunityService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create opportunity'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await opportunityService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update opportunity'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await opportunityService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete opportunity'
      set({ error: message, loading: false })
    }
  },
}))
