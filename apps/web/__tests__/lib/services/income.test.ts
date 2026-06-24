import { describe, it, expect, vi, beforeEach } from 'vitest'
import { incomeService } from '@/lib/services/income'

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

describe('incomeService', () => {
  describe('list', () => {
    it('returns income entry list', async () => {
      const entries = [{ id: '1', amount: 500, source: 'Freelance', date: '2026-06-24' }]
      mockGet.mockResolvedValueOnce(entries)
      const result = await incomeService.list()
      expect(result).toEqual(entries)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/income')
    })

    it('returns empty array when no entries', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await incomeService.list()
      expect(result).toEqual([])
    })
  })

  describe('get', () => {
    it('returns a single income entry', async () => {
      const entry = { id: '1', amount: 500, source: 'Freelance', date: '2026-06-24' }
      mockGet.mockResolvedValueOnce(entry)
      const result = await incomeService.get('1')
      expect(result).toEqual(entry)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/income/1')
    })

    it('returns null when not found', async () => {
      mockGet.mockResolvedValueOnce(null)
      const result = await incomeService.get('999')
      expect(result).toBeNull()
    })
  })

  describe('create', () => {
    it('creates and returns income entry', async () => {
      const data = { amount: 1000, source: 'Client project', date: '2026-06-24', hours_worked: 10 }
      const created = { id: '2', ...data }
      mockPost.mockResolvedValueOnce(created)
      const result = await incomeService.create(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/income', data)
    })

    it('handles validation error', async () => {
      mockPost.mockRejectedValueOnce(new Error('Amount required'))
      await expect(incomeService.create({ amount: 0 } as any)).rejects.toThrow('Amount required')
    })
  })

  describe('update', () => {
    it('updates and returns income entry', async () => {
      const data = { amount: 600 }
      const updated = { id: '1', amount: 600, source: 'Freelance', date: '2026-06-24' }
      mockPut.mockResolvedValueOnce(updated)
      const result = await incomeService.update('1', data)
      expect(result).toEqual(updated)
      expect(mockPut).toHaveBeenCalledWith('/api/v1/income/1', data)
    })

    it('handles not found on update', async () => {
      mockPut.mockRejectedValueOnce(new Error('Entry not found'))
      await expect(incomeService.update('999', { amount: 100 })).rejects.toThrow('Entry not found')
    })
  })

  describe('delete', () => {
    it('deletes income entry', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await incomeService.delete('1')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/income/1')
    })

    it('handles not found on delete', async () => {
      mockDelete.mockRejectedValueOnce(new Error('Not found'))
      await expect(incomeService.delete('999')).rejects.toThrow('Not found')
    })
  })
})
