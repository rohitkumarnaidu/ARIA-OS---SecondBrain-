import { api } from '@/lib/api'
import type { Memory, MemoryCreate, MemoryUpdate } from '@/lib/types'

const BASE = '/api/v1/memory'

export const memoryService = {
  list: () => api.get<Memory[]>(BASE),
  get: (id: string) => api.get<Memory>(`${BASE}/${id}`),
  create: (data: MemoryCreate) => api.post<Memory>(BASE, data),
  update: (id: string, data: MemoryUpdate) => api.put<Memory>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
  consolidate: () => api.post<{ status: string; total: number; by_type: Record<string, unknown> }>(`${BASE}/consolidate`),
}
