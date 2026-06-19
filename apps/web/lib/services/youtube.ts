import { api } from '@/lib/api'
import type { Video, VideoCreate, VideoUpdate } from '@/lib/types'

const BASE = '/api/v1/videos'

export const youtubeService = {
  list: () => api.get<Video[]>(BASE),
  create: (data: VideoCreate) => api.post<Video>(BASE, data),
  update: (id: string, data: VideoUpdate) => api.put<Video>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
