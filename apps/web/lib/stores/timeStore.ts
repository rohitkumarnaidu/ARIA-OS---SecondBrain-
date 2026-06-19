import { create } from 'zustand'
import { timeService } from '@/lib/services'
import type { TimeEntry, TimeEntryCreate, TimeEntryUpdate } from '@/lib/types'

interface DailyStats {
  date: string
  total_minutes: number
  entries: TimeEntry[]
}

interface TimeStore {
  items: TimeEntry[]
  loading: boolean
  error: string | null
  dailyStats: DailyStats | null
  fetch: () => Promise<void>
  getById: (id: string) => TimeEntry | undefined
  create: (data: TimeEntryCreate) => Promise<void>
  update: (id: string, data: TimeEntryUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
  stop: (entryId: string) => Promise<void>
  fetchDailyStats: (date?: string) => Promise<void>
}

export const useTimeStore = create<TimeStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,
  dailyStats: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await timeService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load time entries'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await timeService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create time entry'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await timeService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update time entry'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await timeService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete time entry'
      set({ error: message, loading: false })
    }
  },

  stop: async (entryId) => {
    set({ loading: true, error: null })
    try {
      const updated = await timeService.stop(entryId)
      set({ items: get().items.map(i => i.id === entryId ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to stop time entry'
      set({ error: message, loading: false })
    }
  },

  fetchDailyStats: async (date) => {
    set({ loading: true, error: null })
    try {
      const stats = await timeService.dailyStats(date)
      set({ dailyStats: stats, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load daily stats'
      set({ error: message, loading: false })
    }
  },
}))
