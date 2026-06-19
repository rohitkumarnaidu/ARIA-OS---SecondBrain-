import { api } from '@/lib/api'
import type { Resource, ResourceCreate, ResourceUpdate } from '@/lib/types'

const BASE = '/api/v1/resources'

export const resourceService = {
  list: () => api.get<Resource[]>(BASE),
  get: (id: string) => api.get<Resource>(`${BASE}/${id}`),
  create: (data: ResourceCreate) => api.post<Resource>(BASE, data),
  update: (id: string, data: ResourceUpdate) => api.put<Resource>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
