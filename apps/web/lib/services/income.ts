import { api } from '@/lib/api'
import type { IncomeEntry, IncomeEntryCreate } from '@/lib/types'

const BASE = '/api/v1/income'

export const incomeService = {
  list: () => api.get<IncomeEntry[]>(BASE),
  get: (id: string) => api.get<IncomeEntry>(`${BASE}/${id}`),
  create: (data: IncomeEntryCreate) => api.post<IncomeEntry>(BASE, data),
  update: (id: string, data: Partial<IncomeEntryCreate>) => api.put<IncomeEntry>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
}
