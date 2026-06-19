import { create } from 'zustand'
import { analyticsService } from '@/lib/services'

interface DailySummary {
  date: string
  tasks_completed: number
  habits_completed: number
  sleep_score: number | null
  focus_minutes: number
}

interface WeeklyTrends {
  week_start: string
  task_completion_rate: number
  habit_consistency: number
  avg_sleep_score: number
  total_focus_hours: number
}

interface AggregatedStats {
  start_date: string
  end_date: string
  tasks: { total: number; completed: number; by_priority: Record<string, number> }
  habits: { total: number; consistency: number; best_streak: number }
  sleep: { avg_duration: number; avg_score: number; total_debt: number }
  time: { total_minutes: number; deep_work_minutes: number }
  projects: { total: number; completed: number }
  ideas: { total: number; by_stage: Record<string, number> }
  income: { total: number; hourly_rate_avg: number }
}

interface AnalyticsStore {
  dailySummary: DailySummary | null
  weeklyTrends: WeeklyTrends | null
  stats: AggregatedStats | null
  loading: boolean
  error: string | null
  fetchDailySummary: (date: string) => Promise<void>
  fetchWeeklyTrends: (weekStart: string) => Promise<void>
  fetchStats: (startDate: string, endDate: string) => Promise<void>
}

export const useAnalyticsStore = create<AnalyticsStore>((set) => ({
  dailySummary: null,
  weeklyTrends: null,
  stats: null,
  loading: false,
  error: null,

  fetchDailySummary: async (date) => {
    set({ loading: true, error: null })
    try {
      const data = await analyticsService.getDailySummary(date)
      set({ dailySummary: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load daily summary'
      set({ error: message, loading: false })
    }
  },

  fetchWeeklyTrends: async (weekStart) => {
    set({ loading: true, error: null })
    try {
      const data = await analyticsService.getWeeklyTrends(weekStart)
      set({ weeklyTrends: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load weekly trends'
      set({ error: message, loading: false })
    }
  },

  fetchStats: async (startDate, endDate) => {
    set({ loading: true, error: null })
    try {
      const data = await analyticsService.getStats(startDate, endDate)
      set({ stats: data, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load stats'
      set({ error: message, loading: false })
    }
  },
}))
