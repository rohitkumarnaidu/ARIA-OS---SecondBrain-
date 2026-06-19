import { api } from '@/lib/api'
import type { Goal, GoalCreate, GoalUpdate } from '@/lib/types'

const BASE = '/api/v1/goals'

export const goalService = {
  list: () => api.get<Goal[]>(BASE),
  get: (id: string) => api.get<Goal>(`${BASE}/${id}`),
  create: (data: GoalCreate) => api.post<Goal>(BASE, data),
  update: (id: string, data: GoalUpdate) => api.put<Goal>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
