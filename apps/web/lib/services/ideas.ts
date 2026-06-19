import { api } from '@/lib/api'
import type { Idea, IdeaCreate, IdeaUpdate } from '@/lib/types'

const BASE = '/api/v1/ideas'

export const ideaService = {
  list: () => api.get<Idea[]>(BASE),
  get: (id: string) => api.get<Idea>(`${BASE}/${id}`),
  create: (data: IdeaCreate) => api.post<Idea>(BASE, data),
  update: (id: string, data: IdeaUpdate) => api.put<Idea>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
