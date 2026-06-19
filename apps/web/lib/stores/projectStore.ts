import { create } from 'zustand'
import { projectService } from '@/lib/services'
import type { Project, ProjectCreate, ProjectUpdate } from '@/lib/types'

interface ProjectStore {
  items: Project[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Project | undefined
  create: (data: ProjectCreate) => Promise<void>
  update: (id: string, data: ProjectUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await projectService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load projects'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await projectService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create project'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await projectService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update project'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await projectService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete project'
      set({ error: message, loading: false })
    }
  },
}))
