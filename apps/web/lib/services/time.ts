import { api } from '@/lib/api'
import type { TimeEntry, TimeEntryCreate, TimeEntryUpdate } from '@/lib/types'

const BASE = '/api/v1/time'

export const timeService = {
  list: () => api.get<TimeEntry[]>(BASE),
  get: (id: string) => api.get<TimeEntry>(`${BASE}/${id}`),
  create: (data: TimeEntryCreate) => api.post<TimeEntry>(BASE, data),
  update: (id: string, data: TimeEntryUpdate) => api.put<TimeEntry>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
  stop: (entryId: string) => api.post<TimeEntry>(`${BASE}/stop`, { entry_id: entryId }),
  dailyStats: (date?: string) =>
    api.get<{ date: string; total_minutes: number; entries: TimeEntry[] }>(`${BASE}/stats/daily`, {
      params: date ? { date } : undefined,
    }),
}
