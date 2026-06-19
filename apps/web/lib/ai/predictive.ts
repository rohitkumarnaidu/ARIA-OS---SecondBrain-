import { api } from '@/lib/api'
import type {
  TaskCompletionForecast,
  HabitCompletionForecast,
  SleepInsight,
  SmartSlotResponse,
} from '@/lib/types'

export const predictive = {
  async taskCompletion(): Promise<TaskCompletionForecast> {
    return api.get<TaskCompletionForecast>('/api/v1/predictions/tasks')
  },

  async habits(): Promise<HabitCompletionForecast> {
    return api.get<HabitCompletionForecast>('/api/v1/predictions/habits')
  },

  async sleep(): Promise<SleepInsight> {
    return api.get<SleepInsight>('/api/v1/predictions/sleep')
  },

  async smartSlots(): Promise<SmartSlotResponse> {
    return api.get<SmartSlotResponse>('/api/v1/predictions/slots')
  },
}
