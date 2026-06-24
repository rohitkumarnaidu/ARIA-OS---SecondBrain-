import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { timeService } from '@/lib/services/time'
import type { TimeEntry, TimeEntryCreate, TimeEntryUpdate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockEntry = { id: 'tm-1', task_id: 't-1', duration_minutes: 25, date: '2026-06-23' } as TimeEntry
const mockCreate = { duration_minutes: 25, date: '2026-06-23' } as TimeEntryCreate
const mockUpdate = { duration_minutes: 30 } as TimeEntryUpdate

describe('timeService', () => {
  describe('list', () => {
    it('returns an array of time entries', async () => {
      mockedApi.get.mockResolvedValue([mockEntry])
      const result = await timeService.list()
      expect(result).toEqual([mockEntry])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/time')
    })
  })

  describe('get', () => {
    it('returns a single time entry', async () => {
      mockedApi.get.mockResolvedValue(mockEntry)
      const result = await timeService.get('tm-1')
      expect(result).toEqual(mockEntry)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/time/tm-1')
    })
  })

  describe('create', () => {
    it('creates and returns a time entry', async () => {
      mockedApi.post.mockResolvedValue(mockEntry)
      const result = await timeService.create(mockCreate)
      expect(result).toEqual(mockEntry)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/time', mockCreate)
    })
  })

  describe('update', () => {
    it('updates and returns the time entry', async () => {
      mockedApi.put.mockResolvedValue(mockEntry)
      const result = await timeService.update('tm-1', mockUpdate)
      expect(result).toEqual(mockEntry)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/time/tm-1', mockUpdate)
    })
  })

  describe('delete', () => {
    it('deletes and returns a message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await timeService.delete('tm-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/time/tm-1')
    })
  })

  describe('stop', () => {
    it('posts to stop endpoint with entry_id', async () => {
      const stopped = { ...mockEntry, stopped_at: '2026-06-23T10:00:00Z' }
      mockedApi.post.mockResolvedValue(stopped)
      const result = await timeService.stop('tm-1')
      expect(result).toEqual(stopped)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/time/stop', { entry_id: 'tm-1' })
    })
  })

  describe('dailyStats', () => {
    it('returns daily stats without date param', async () => {
      const stats = { date: '2026-06-23', total_minutes: 120, entries: [mockEntry] }
      mockedApi.get.mockResolvedValue(stats)
      const result = await timeService.dailyStats()
      expect(result).toEqual(stats)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/time/stats/daily', { params: undefined })
    })

    it('returns daily stats with date param', async () => {
      const stats = { date: '2026-06-22', total_minutes: 90, entries: [] }
      mockedApi.get.mockResolvedValue(stats)
      const result = await timeService.dailyStats('2026-06-22')
      expect(result).toEqual(stats)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/time/stats/daily', { params: { date: '2026-06-22' } })
    })
  })
})
