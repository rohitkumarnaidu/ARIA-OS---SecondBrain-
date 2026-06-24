import { describe, it, expect, vi, beforeEach } from 'vitest'
import { habitService } from '@/lib/services/habits'

const mockGet = vi.fn()
const mockPost = vi.fn()
const mockPut = vi.fn()
const mockDelete = vi.fn()

vi.mock('@/lib/api', () => ({
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    put: (...args: unknown[]) => mockPut(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

describe('habitService', () => {
  describe('list', () => {
    it('returns habit list', async () => {
      const habits = [{ id: '1', name: 'Morning run', frequency: 'daily' }]
      mockGet.mockResolvedValueOnce(habits)
      const result = await habitService.list()
      expect(result).toEqual(habits)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/habits')
    })

    it('returns empty array when no habits', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await habitService.list()
      expect(result).toEqual([])
    })
  })

  describe('get', () => {
    it('returns a single habit', async () => {
      const habit = { id: '1', name: 'Morning run', frequency: 'daily' }
      mockGet.mockResolvedValueOnce(habit)
      const result = await habitService.get('1')
      expect(result).toEqual(habit)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/habits/1')
    })

    it('returns null when not found', async () => {
      mockGet.mockResolvedValueOnce(null)
      const result = await habitService.get('999')
      expect(result).toBeNull()
    })
  })

  describe('create', () => {
    it('creates and returns habit', async () => {
      const data = { name: 'Read 30 mins', frequency: 'daily' }
      const created = { id: '2', ...data }
      mockPost.mockResolvedValueOnce(created)
      const result = await habitService.create(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/habits', data)
    })

    it('handles validation error', async () => {
      mockPost.mockRejectedValueOnce(new Error('Name required'))
      await expect(habitService.create({ name: '' })).rejects.toThrow('Name required')
    })
  })

  describe('update', () => {
    it('updates and returns habit', async () => {
      const data = { frequency: 'weekly' }
      const updated = { id: '1', name: 'Morning run', frequency: 'weekly' }
      mockPut.mockResolvedValueOnce(updated)
      const result = await habitService.update('1', data)
      expect(result).toEqual(updated)
      expect(mockPut).toHaveBeenCalledWith('/api/v1/habits/1', data)
    })

    it('handles not found on update', async () => {
      mockPut.mockRejectedValueOnce(new Error('Habit not found'))
      await expect(habitService.update('999', { name: 'Nope' })).rejects.toThrow('Habit not found')
    })
  })

  describe('delete', () => {
    it('deletes habit', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await habitService.delete('1')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/habits/1')
    })

    it('handles not found on delete', async () => {
      mockDelete.mockRejectedValueOnce(new Error('Not found'))
      await expect(habitService.delete('999')).rejects.toThrow('Not found')
    })
  })

  describe('log', () => {
    it('logs habit completion', async () => {
      const logData = { date: '2026-06-24', completed: true, note: 'Felt great' }
      const logResult = { id: 'log1', habit_id: '1', ...logData }
      mockPost.mockResolvedValueOnce(logResult)
      const result = await habitService.log('1', logData)
      expect(result).toEqual(logResult)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/habits/1/log', logData)
    })

    it('logs without optional note', async () => {
      const logData = { date: '2026-06-24', completed: false }
      mockPost.mockResolvedValueOnce({ id: 'log2', habit_id: '1', ...logData })
      const result = await habitService.log('1', logData)
      expect(result).toEqual({ id: 'log2', habit_id: '1', ...logData })
    })

    it('handles API error on log', async () => {
      mockPost.mockRejectedValueOnce(new Error('Log failed'))
      await expect(habitService.log('1', { date: 'bad', completed: true })).rejects.toThrow('Log failed')
    })
  })
})
