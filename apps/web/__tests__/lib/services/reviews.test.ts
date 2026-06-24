import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { reviewService } from '@/lib/services/reviews'
import type { WeeklyReview } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockReview = {
  id: 'rev-1',
  week_start: '2026-06-22',
  summary: 'Good week',
  tasks_completed: 10,
} as WeeklyReview

describe('reviewService', () => {
  describe('list', () => {
    it('returns an array of reviews', async () => {
      mockedApi.get.mockResolvedValue([mockReview])
      const result = await reviewService.list()
      expect(result).toEqual([mockReview])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/reviews')
    })
  })

  describe('get', () => {
    it('returns a single review', async () => {
      mockedApi.get.mockResolvedValue(mockReview)
      const result = await reviewService.get('rev-1')
      expect(result).toEqual(mockReview)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/reviews/rev-1')
    })
  })

  describe('getLatest', () => {
    it('returns the latest review', async () => {
      mockedApi.get.mockResolvedValue(mockReview)
      const result = await reviewService.getLatest()
      expect(result).toEqual(mockReview)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/reviews/latest')
    })
  })
})
