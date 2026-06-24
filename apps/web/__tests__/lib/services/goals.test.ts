import { describe, it, expect, vi, beforeEach } from 'vitest'
import { goalService } from '@/lib/services/goals'

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

describe('goalService', () => {
  describe('list', () => {
    it('returns goal list', async () => {
      const goals = [{ id: '1', title: 'Learn Rust', status: 'active' }]
      mockGet.mockResolvedValueOnce(goals)
      const result = await goalService.list()
      expect(result).toEqual(goals)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/goals')
    })

    it('returns empty array when no goals', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await goalService.list()
      expect(result).toEqual([])
    })
  })

  describe('get', () => {
    it('returns a single goal', async () => {
      const goal = { id: '1', title: 'Learn Rust', status: 'active' }
      mockGet.mockResolvedValueOnce(goal)
      const result = await goalService.get('1')
      expect(result).toEqual(goal)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/goals/1')
    })

    it('returns null when not found', async () => {
      mockGet.mockResolvedValueOnce(null)
      const result = await goalService.get('999')
      expect(result).toBeNull()
    })
  })

  describe('create', () => {
    it('creates and returns goal', async () => {
      const data = { title: 'Run a marathon', deadline: '2026-12-31' }
      const created = { id: '2', ...data, status: 'active' }
      mockPost.mockResolvedValueOnce(created)
      const result = await goalService.create(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/goals', data)
    })

    it('handles validation error', async () => {
      mockPost.mockRejectedValueOnce(new Error('Title required'))
      await expect(goalService.create({ title: '' })).rejects.toThrow('Title required')
    })
  })

  describe('update', () => {
    it('updates and returns goal', async () => {
      const data = { status: 'completed' }
      const updated = { id: '1', title: 'Learn Rust', status: 'completed' }
      mockPut.mockResolvedValueOnce(updated)
      const result = await goalService.update('1', data)
      expect(result).toEqual(updated)
      expect(mockPut).toHaveBeenCalledWith('/api/v1/goals/1', data)
    })

    it('handles not found on update', async () => {
      mockPut.mockRejectedValueOnce(new Error('Goal not found'))
      await expect(goalService.update('999', { title: 'Nope' })).rejects.toThrow('Goal not found')
    })
  })

  describe('delete', () => {
    it('deletes goal', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await goalService.delete('1')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/goals/1')
    })

    it('handles not found on delete', async () => {
      mockDelete.mockRejectedValueOnce(new Error('Not found'))
      await expect(goalService.delete('999')).rejects.toThrow('Not found')
    })
  })
})
