import { api } from '@/lib/api'

const BASE = '/api/v1/analytics'

/**
 * Analytics service — mock-first.
 * Returns placeholder summaries until the backend analytics endpoints are built.
 */
export const analyticsService = {
  /** Summary of completed tasks, habits, sleep averages for a date range */
  getDailySummary: (date: string) =>
    api.get<{
      date: string
      tasks_completed: number
      habits_completed: number
      sleep_score: number | null
      focus_minutes: number
    }>(`${BASE}/daily`, { params: { date } }),

  /** Weekly trend data for the dashboard charts */
  getWeeklyTrends: (weekStart: string) =>
    api.get<{
      week_start: string
      task_completion_rate: number
      habit_consistency: number
      avg_sleep_score: number
      total_focus_hours: number
    }>(`${BASE}/weekly`, { params: { week_start: weekStart } }),

  /** Aggregated stats over a custom period */
  getStats: (startDate: string, endDate: string) =>
    api.get<{
      start_date: string
      end_date: string
      tasks: { total: number; completed: number; by_priority: Record<string, number> }
      habits: { total: number; consistency: number; best_streak: number }
      sleep: { avg_duration: number; avg_score: number; total_debt: number }
      time: { total_minutes: number; deep_work_minutes: number }
      projects: { total: number; completed: number }
      ideas: { total: number; by_stage: Record<string, number> }
      income: { total: number; hourly_rate_avg: number }
    }>(`${BASE}/stats`, { params: { start_date: startDate, end_date: endDate } }),
}
