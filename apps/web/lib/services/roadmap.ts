import { api } from '@/lib/api'

interface Milestone {
  id: string
  skill: string
  category: string
  targetDate: string
  progress: number
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold'
  isRecommended?: boolean
}

const BASE = '/api/v1/roadmap'

export const roadmapService = {
  list: () => api.get<Milestone[]>(BASE),
  create: (data: Partial<Milestone>) => api.post<Milestone>(BASE, data),
  update: (id: string, data: Partial<Milestone>) => api.put<Milestone>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
