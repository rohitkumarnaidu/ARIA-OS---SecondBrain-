import { api } from '@/lib/api'
import type { SleepLog, SleepLogCreate } from '@/lib/types'

const BASE = '/api/v1/sleep'

export const sleepService = {
  list: () => api.get<SleepLog[]>(BASE),
  get: (id: string) => api.get<SleepLog>(`${BASE}/${id}`),
  create: (data: SleepLogCreate) => api.post<SleepLog>(BASE, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
