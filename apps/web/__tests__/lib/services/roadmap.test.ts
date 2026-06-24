import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { roadmapService } from '@/lib/services/roadmap'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockMilestone = {
  id: 'ms-1',
  skill: 'TypeScript',
  category: 'engineering',
  targetDate: '2026-08-01',
  progress: 50,
  status: 'in_progress',
  isRecommended: true,
}

describe('roadmapService', () => {
  describe('list', () => {
    it('returns an array of milestones', async () => {
      mockedApi.get.mockResolvedValue([mockMilestone])
      const result = await roadmapService.list()
      expect(result).toEqual([mockMilestone])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/roadmap')
    })
  })

  describe('create', () => {
    it('creates and returns a milestone', async () => {
      mockedApi.post.mockResolvedValue(mockMilestone)
      const result = await roadmapService.create({ skill: 'TypeScript', status: 'not_started' })
      expect(result).toEqual(mockMilestone)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/roadmap', { skill: 'TypeScript', status: 'not_started' })
    })
  })

  describe('update', () => {
    it('updates and returns the milestone', async () => {
      const update = { progress: 80 }
      const updated = { ...mockMilestone, progress: 80 }
      mockedApi.put.mockResolvedValue(updated)
      const result = await roadmapService.update('ms-1', update)
      expect(result).toEqual(updated)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/roadmap/ms-1', update)
    })
  })

  describe('delete', () => {
    it('deletes and returns a message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await roadmapService.delete('ms-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/roadmap/ms-1')
    })
  })
})
