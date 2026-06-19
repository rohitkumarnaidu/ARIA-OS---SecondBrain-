import { api } from '@/lib/api'
import type { Habit, HabitCreate, HabitUpdate, HabitLog } from '@/lib/types'

const BASE = '/api/v1/habits'

export const habitService = {
  list: () => api.get<Habit[]>(BASE),
  get: (id: string) => api.get<Habit>(`${BASE}/${id}`),
  create: (data: HabitCreate) => api.post<Habit>(BASE, data),
  update: (id: string, data: HabitUpdate) => api.put<Habit>(`${BASE}/${id}`, data),
  delete: (id: string) => api.delete<{ message: string }>(`${BASE}/${id}`),
  log: (habitId: string, data: { date: string; completed: boolean; note?: string }) =>
    api.post<HabitLog>(`${BASE}/${habitId}/log`, data),
}
