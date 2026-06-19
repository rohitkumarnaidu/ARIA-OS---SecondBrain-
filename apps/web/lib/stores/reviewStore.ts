import { create } from 'zustand'
import { reviewService } from '@/lib/services'
import type { WeeklyReview } from '@/lib/types'

interface ReviewStore {
  items: WeeklyReview[]
  latest: WeeklyReview | null
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  getById: (id: string) => WeeklyReview | undefined
  getLatest: () => Promise<void>
}

export const useReviewStore = create<ReviewStore>((set, get) => ({
  items: [],
  latest: null,
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await reviewService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load reviews'
      set({ error: message, loading: false })
    }
  },

  getById: (id) => get().items.find(i => i.id === id),

  getLatest: async () => {
    set({ loading: true, error: null })
    try {
      const review = await reviewService.getLatest()
      set({ latest: review, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load latest review'
      set({ error: message, loading: false })
    }
  },
}))
