import { create } from 'zustand'
import { briefingService } from '@/lib/services'
import type { DailyBriefing } from '@/lib/types'

interface BriefingStore {
  items: DailyBriefing[]
  today: DailyBriefing | null
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => DailyBriefing | undefined
  getToday: () => Promise<void>
}

export const useBriefingStore = create<BriefingStore>((set, get) => ({
  items: [],
  today: null,
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await briefingService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load briefings'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  getToday: async () => {
    set({ loading: true, error: null })
    try {
      const briefing = await briefingService.getToday()
      set({ today: briefing, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load today briefing'
      set({ error: message, loading: false })
    }
  },
}))
