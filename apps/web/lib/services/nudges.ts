import { api } from '@/lib/api'
import type { NudgeEntry } from '@/lib/types'

const BASE = '/api/v1/notifications/nudges'

export const nudgeService = {
  list: (params?: { limit?: number; offset?: number; read?: boolean }) =>
    api.get<NudgeEntry[]>(BASE, { params }),
  markRead: (id: string) => api.patch<{ status: string }>(`/api/v1/notifications/${id}/read`),
  markAllRead: () => api.post<{ message: string }>(`/api/v1/notifications/read-all`),
}
