import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ideaService } from '@/lib/services/ideas'

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

describe('ideaService', () => {
  describe('list', () => {
    it('returns idea list', async () => {
      const ideas = [{ id: '1', title: 'New app idea', stage: 'raw' }]
      mockGet.mockResolvedValueOnce(ideas)
      const result = await ideaService.list()
      expect(result).toEqual(ideas)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/ideas')
    })

    it('returns empty array when no ideas', async () => {
      mockGet.mockResolvedValueOnce([])
      const result = await ideaService.list()
      expect(result).toEqual([])
    })
  })

  describe('get', () => {
    it('returns a single idea', async () => {
      const idea = { id: '1', title: 'New app idea', stage: 'raw' }
      mockGet.mockResolvedValueOnce(idea)
      const result = await ideaService.get('1')
      expect(result).toEqual(idea)
      expect(mockGet).toHaveBeenCalledWith('/api/v1/ideas/1')
    })

    it('returns null when not found', async () => {
      mockGet.mockResolvedValueOnce(null)
      const result = await ideaService.get('999')
      expect(result).toBeNull()
    })
  })

  describe('create', () => {
    it('creates and returns idea', async () => {
      const data = { title: 'Build a chatbot', description: 'AI tutor' }
      const created = { id: '2', ...data, stage: 'raw' }
      mockPost.mockResolvedValueOnce(created)
      const result = await ideaService.create(data)
      expect(result).toEqual(created)
      expect(mockPost).toHaveBeenCalledWith('/api/v1/ideas', data)
    })

    it('handles validation error', async () => {
      mockPost.mockRejectedValueOnce(new Error('Title required'))
      await expect(ideaService.create({ title: '' })).rejects.toThrow('Title required')
    })
  })

  describe('update', () => {
    it('updates and returns idea', async () => {
      const data = { stage: 'validating' }
      const updated = { id: '1', title: 'New app idea', stage: 'validating' }
      mockPut.mockResolvedValueOnce(updated)
      const result = await ideaService.update('1', data)
      expect(result).toEqual(updated)
      expect(mockPut).toHaveBeenCalledWith('/api/v1/ideas/1', data)
    })

    it('handles not found on update', async () => {
      mockPut.mockRejectedValueOnce(new Error('Idea not found'))
      await expect(ideaService.update('999', { title: 'Nope' })).rejects.toThrow('Idea not found')
    })
  })

  describe('delete', () => {
    it('deletes idea', async () => {
      mockDelete.mockResolvedValueOnce({ message: 'Deleted' })
      const result = await ideaService.delete('1')
      expect(result).toEqual({ message: 'Deleted' })
      expect(mockDelete).toHaveBeenCalledWith('/api/v1/ideas/1')
    })

    it('handles not found on delete', async () => {
      mockDelete.mockRejectedValueOnce(new Error('Not found'))
      await expect(ideaService.delete('999')).rejects.toThrow('Not found')
    })
  })
})
