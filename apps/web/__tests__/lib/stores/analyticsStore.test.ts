import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAnalyticsStore } from '@/lib/stores/analyticsStore'

const mockGetDailySummary = vi.fn()
const mockGetWeeklyTrends = vi.fn()
const mockGetStats = vi.fn()

vi.mock('@/lib/services/analytics', () => ({
  analyticsService: {
    getDailySummary: (...args: unknown[]) => mockGetDailySummary(...args),
    getWeeklyTrends: (...args: unknown[]) => mockGetWeeklyTrends(...args),
    getStats: (...args: unknown[]) => mockGetStats(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useAnalyticsStore.setState({ dailySummary: null, weeklyTrends: null, stats: null, loading: false, error: null })
})

describe('analyticsStore', () => {
  it('has correct initial state', () => {
    const s = useAnalyticsStore.getState()
    expect(s.dailySummary).toBeNull()
    expect(s.weeklyTrends).toBeNull()
    expect(s.stats).toBeNull()
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetchDailySummary loads summary', async () => {
    const summary = { date: '2026-01-15', tasks_completed: 5, habits_completed: 3, sleep_score: 78, focus_minutes: 120 }
    mockGetDailySummary.mockResolvedValueOnce(summary)
    await useAnalyticsStore.getState().fetchDailySummary('2026-01-15')
    const s = useAnalyticsStore.getState()
    expect(s.dailySummary).toEqual(summary)
    expect(s.loading).toBe(false)
  })

  it('fetchDailySummary sets error on failure', async () => {
    mockGetDailySummary.mockRejectedValueOnce(new Error('API error'))
    await useAnalyticsStore.getState().fetchDailySummary('bad-date')
    expect(useAnalyticsStore.getState().error).toBe('API error')
  })

  it('fetchWeeklyTrends loads trends', async () => {
    const trends = { week_start: '2026-W03', task_completion_rate: 0.8, habit_consistency: 0.7, avg_sleep_score: 75, total_focus_hours: 20 }
    mockGetWeeklyTrends.mockResolvedValueOnce(trends)
    await useAnalyticsStore.getState().fetchWeeklyTrends('2026-W03')
    expect(useAnalyticsStore.getState().weeklyTrends).toEqual(trends)
  })

  it('fetchWeeklyTrends sets error on failure', async () => {
    mockGetWeeklyTrends.mockRejectedValueOnce(new Error('No data'))
    await useAnalyticsStore.getState().fetchWeeklyTrends('bad')
    expect(useAnalyticsStore.getState().error).toBe('No data')
  })

  it('fetchStats loads aggregated stats', async () => {
    const stats = {
      start_date: '2026-01-01', end_date: '2026-01-31',
      tasks: { total: 10, completed: 8, by_priority: { high: 5, low: 5 } },
      habits: { total: 5, consistency: 0.9, best_streak: 7 },
      sleep: { avg_duration: 7.5, avg_score: 80, total_debt: 2 },
      time: { total_minutes: 3000, deep_work_minutes: 600 },
      projects: { total: 3, completed: 1 },
      ideas: { total: 12, by_stage: { raw: 5, validating: 4, building: 3 } },
      income: { total: 5000, hourly_rate_avg: 50 },
    }
    mockGetStats.mockResolvedValueOnce(stats)
    await useAnalyticsStore.getState().fetchStats('2026-01-01', '2026-01-31')
    expect(useAnalyticsStore.getState().stats).toEqual(stats)
  })

  it('fetchStats sets error on failure', async () => {
    mockGetStats.mockRejectedValueOnce(new Error('Stats unavailable'))
    await useAnalyticsStore.getState().fetchStats('', '')
    expect(useAnalyticsStore.getState().error).toBe('Stats unavailable')
  })
})
