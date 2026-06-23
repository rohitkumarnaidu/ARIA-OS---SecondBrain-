import { api } from '@/lib/api'
import type { Automation } from '@/types/automation'

const BASE = '/api/v1/automation'

export const automationService = {
  list: () => api.get<Automation[]>(BASE),
  triggerBriefing: () => api.post<{ message: string }>(`${BASE}/trigger/briefing`),
  triggerRadar: () => api.post<{ message: string }>(`${BASE}/trigger/radar`),
  triggerWeeklyReview: () => api.post<{ message: string }>(`${BASE}/trigger/weekly-review`),
  triggerSleepAnalysis: () => api.post<{ message: string }>(`${BASE}/trigger/sleep-analysis`),
  triggerBedtime: () => api.post<{ message: string }>(`${BASE}/trigger/sleep-bedtime`),
  triggerNudges: () => api.post<{ message: string }>(`${BASE}/trigger/nudges`),
}
