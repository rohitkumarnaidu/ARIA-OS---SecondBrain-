import { api } from '@/lib/api'
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types'

const BASE = '/api/v1/tasks'

export const taskService = {
  list: () => api.get<Task[]>(BASE),
  get: (id: string) => api.get<Task>(`${BASE}/${id}`),
  create: (data: TaskCreate) => api.post<Task>(BASE, data),
  update: (id: string, data: TaskUpdate) => api.put<Task>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
  complete: (id: string) => api.post<Task>(`${BASE}/${id}/complete`),
}
