import { create } from 'zustand'
import { youtubeService } from '@/lib/services'
import type { Video, VideoCreate, VideoUpdate } from '@/lib/types'

interface YoutubeStore {
  items: Video[]
  loading: boolean
  error: string | null
  fetch: () => Promise<void>
  create: (data: VideoCreate) => Promise<void>
  update: (id: string, data: VideoUpdate) => Promise<void>
  remove: (id: string) => Promise<void>
}

export const useYoutubeStore = create<YoutubeStore>((set, get) => ({
  items: [],
  loading: false,
  error: null,

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await youtubeService.list()
      set({ items: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load videos'
      set({ error: message, loading: false })
    }
  },

  create: async (data) => {
    set({ loading: true, error: null })
    try {
      const created = await youtubeService.create(data)
      set({ items: [created, ...get().items], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add video'
      set({ error: message, loading: false })
    }
  },

  update: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updated = await youtubeService.update(id, data)
      set({ items: get().items.map(i => i.id === id ? updated : i), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update video'
      set({ error: message, loading: false })
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null })
    try {
      await youtubeService.delete(id)
      set({ items: get().items.filter(i => i.id !== id), loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete video'
      set({ error: message, loading: false })
    }
  },
}))
