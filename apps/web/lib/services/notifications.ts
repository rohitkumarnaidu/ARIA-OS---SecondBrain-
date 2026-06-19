import { api } from '@/lib/api'
import type { AppNotification } from '@/lib/types'

const BASE = '/api/v1/notifications'

export const notificationService = {
  list: () => api.get<AppNotification[]>(BASE),
  markRead: (id: string) => api.patch<AppNotification>(`${BASE}/${id}/read`),
  markAllRead: () => api.post<{ message: string }>(`${BASE}/read-all`),
}
