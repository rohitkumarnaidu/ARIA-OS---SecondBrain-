import { create } from 'zustand'
import { roadmapService } from '@/lib/services'

interface Milestone {
  id: string
  skill: string
  category: string
  targetDate: string
  progress: number
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold'
  isRecommended?: boolean
}

interface RoadmapStore {
  milestones: Milestone[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  add: (data: Partial<Milestone>) => Promise<void>
  update: (id: string, data: Partial<Milestone>) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useRoadmapStore = create<RoadmapStore>((set, get) => ({
  milestones: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await roadmapService.list()
      set({ milestones: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load roadmap'
      set({ error: message, loading: false })
    }
  },

  add: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await roadmapService.create(data)
      set({ milestones: [created, ...get().milestones], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add milestone'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    try {
      const updated = await roadmapService.update(id, data)
      set({ milestones: get().milestones.map(m => m.id === id ? { ...m, ...updated } : m) })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update milestone'
      set({ error: message })
    }
  },

  remove: async (id) => {
    try {
      await roadmapService.delete(id)
      set({ milestones: get().milestones.filter(m => m.id !== id) })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete milestone'
      set({ error: message })
    }
  },
}))
