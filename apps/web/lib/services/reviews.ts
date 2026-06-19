import { api } from '@/lib/api'
import type { WeeklyReview } from '@/lib/types'

const BASE = '/api/v1/reviews'

export const reviewService = {
  list: () => api.get<WeeklyReview[]>(BASE),
  get: (id: string) => api.get<WeeklyReview>(`${BASE}/${id}`),
  getLatest: () => api.get<WeeklyReview>(`${BASE}/latest`),
}
