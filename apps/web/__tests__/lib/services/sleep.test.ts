import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { sleepService } from '@/lib/services/sleep'
import type { SleepLog, SleepLogCreate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockLog = { id: 'sl-1', date: '2026-06-23', duration_hours: 7.5, score: 85 } as SleepLog
const mockCreate = { date: '2026-06-23', duration_hours: 8 } as SleepLogCreate

describe('sleepService', () => {
  describe('list', () => {
    it('returns an array of sleep logs', async () => {
      mockedApi.get.mockResolvedValue([mockLog])
      const result = await sleepService.list()
      expect(result).toEqual([mockLog])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/sleep')
    })
  })

  describe('get', () => {
    it('returns a single sleep log', async () => {
      mockedApi.get.mockResolvedValue(mockLog)
      const result = await sleepService.get('sl-1')
      expect(result).toEqual(mockLog)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/sleep/sl-1')
    })
  })

  describe('create', () => {
    it('creates and returns a sleep log', async () => {
      mockedApi.post.mockResolvedValue(mockLog)
      const result = await sleepService.create(mockCreate)
      expect(result).toEqual(mockLog)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/sleep', mockCreate)
    })
  })

  describe('delete', () => {
    it('deletes and returns a message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await sleepService.delete('sl-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/sleep/sl-1')
    })
  })
})
