import { api } from '@/lib/api'
import type { Project, ProjectCreate, ProjectUpdate } from '@/lib/types'

const BASE = '/api/v1/projects'

export const projectService = {
  list: () => api.get<Project[]>(BASE),
  get: (id: string) => api.get<Project>(`${BASE}/${id}`),
  create: (data: ProjectCreate) => api.post<Project>(BASE, data),
  update: (id: string, data: ProjectUpdate) => api.put<Project>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
