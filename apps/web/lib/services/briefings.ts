import { api } from '@/lib/api'
import type { DailyBriefing } from '@/lib/types'

const BASE = '/api/v1/briefings'

export const briefingService = {
  list: () => api.get<DailyBriefing[]>(BASE),
  get: (id: string) => api.get<DailyBriefing>(`${BASE}/${id}`),
  getToday: () => api.get<DailyBriefing>(`${BASE}/today`),
}
