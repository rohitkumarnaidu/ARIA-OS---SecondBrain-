import { api } from '@/lib/api'
import type { Memory, MemoryCreate } from '@/lib/types'

const BASE = '/api/v1/memory'

export const memoryService = {
  list: () => api.get<Memory[]>(BASE),
  get: (id: string) => api.get<Memory>(`${BASE}/${id}`),
  create: (data: MemoryCreate) => api.post<Memory>(BASE, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
