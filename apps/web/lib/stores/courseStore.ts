import { create } from 'zustand'
import { courseService } from '@/lib/services'
import type { Course, CourseCreate, CourseUpdate } from '@/lib/types'

interface CourseStore {
  items: Course[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => Course | undefined
  create: (data: CourseCreate) => Promise<void>
  update: (id: string, data: CourseUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useCourseStore = create<CourseStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await courseService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load courses'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await courseService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create course'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await courseService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update course'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await courseService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete course'
      set({ error: message, loading: false })
    }
  },
}))
