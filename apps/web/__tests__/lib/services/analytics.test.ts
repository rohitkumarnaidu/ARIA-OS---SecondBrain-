import { describe, it, expect, vi, beforeEach } from 'vitest'
import { analyticsService } from '@/lib/services/analytics'

const mockGet = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('analyticsService', () => {
  describe('getDailySummary', () => {
    it('returns daily summary for a date', async () => {
      const summary = {
        date: '2026-06-24',
        tasks_completed: 5,
        habits_completed: 3,
        sleep_score: 78,
        focus_minutes: 120,
      }
      mockGet.mockResolvedValueOnce(summary)
      const result = await analyticsService.getDailySummary('2026-06-24')
      expect(result).toEqual(summary)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/analytics/daily', { params: { date: '2026-06-24' } })
    })

    it('returns null sleep_score when no sleep data', async () => {
      const summary = { date: '2026-06-24', tasks_completed: 0, habits_completed: 0, sleep_score: null, focus_minutes: 0 }
      mockGet.mockResolvedValueOnce(summary)
      const result = await analyticsService.getDailySummary('2026-06-24')
      expect(result.sleep_score).toBeNull()
    })
  })

  describe('getWeeklyTrends', () => {
    it('returns weekly trends for a week start', async () => {
      const trends = {
        week_start: '2026-06-22',
        task_completion_rate: 0.85,
        habit_consistency: 0.75,
        avg_sleep_score: 72,
        total_focus_hours: 14.5,
      }
      mockGet.mockResolvedValueOnce(trends)
      const result = await analyticsService.getWeeklyTrends('2026-06-22')
      expect(result).toEqual(trends)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/analytics/weekly', { params: { week_start: '2026-06-22' } })
    })
  })

  describe('getStats', () => {
    it('returns aggregated stats over a period', async () => {
      const stats = {
        start_date: '2026-06-01',
        end_date: '2026-06-30',
        tasks: { total: 20, completed: 15, by_priority: { high: 5, medium: 10 } },
        habits: { total: 10, consistency: 0.8, best_streak: 7 },
        sleep: { avg_duration: 7.5, avg_score: 75, total_debt: 2 },
        time: { total_minutes: 3000, deep_work_minutes: 600 },
        projects: { total: 3, completed: 1 },
        ideas: { total: 5, by_stage: { raw: 3, validating: 2 } },
        income: { total: 5000, hourly_rate_avg: 50 },
      }
      mockGet.mockResolvedValueOnce(stats)
      const result = await analyticsService.getStats('2026-06-01', '2026-06-30')
      expect(result).toEqual(stats)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/analytics/stats', {
        params: { start_date: '2026-06-01', end_date: '2026-06-30' },
      })
    })

    it('handles API error', async () => {
      mockGet.mockRejectedValueOnce(new Error('Server error'))
      await expect(analyticsService.getStats('bad', 'date')).rejects.toThrow('Server error')
    })
  })
})
