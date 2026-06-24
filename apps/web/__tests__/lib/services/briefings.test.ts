import { describe, it, expect, vi, beforeEach } from 'vitest'
import { briefingService } from '@/lib/services/briefings'

const mockGet = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('briefingService', () => {
  describe('list', () => {
    it('returns briefing list', async () => {
      const briefings = [{ id: '1', date: '2026-06-24', summary: 'Good day' }]
      mockGet.mockResolvedValueOnce(briefings)
      const result = await briefingService.list()
      expect(result).toEqual(briefings)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/briefings')
    })

    it('returns empty array when no briefings', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await briefingService.list()
      expect(result).toEqual([])
    })
  })

  describe('get', () => {
    it('returns a single briefing by id', async () => {
      const briefing = { id: '1', date: '2026-06-24', summary: 'Good day' }
      mockGet.mockResolvedValueOnce(briefing)
      const result = await briefingService.get('1')
      expect(result).toEqual(briefing)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/briefings/1')
    })

    it('handles not found', async () => {
      mockGet.mockRejectedValueOnce(new Error('Not found'))
      await expect(briefingService.get('999')).rejects.toThrow('Not found')
    })
  })

  describe('getToday', () => {
    it('returns today briefing', async () => {
      const briefing = { id: '1', date: '2026-06-24', summary: 'Today briefing' }
      mockGet.mockResolvedValueOnce(briefing)
      const result = await briefingService.getToday()
      expect(result).toEqual(briefing)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/briefings/today')
    })

    it('handles missing today briefing', async () => {
      mockGet.mockRejectedValueOnce(new Error('No briefing for today'))
      await expect(briefingService.getToday()).rejects.toThrow('No briefing for today')
    })
  })
})
