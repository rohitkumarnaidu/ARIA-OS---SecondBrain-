import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { projectService } from '@/lib/services/projects'
import type { Project, ProjectCreate, ProjectUpdate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mock = { id: 'proj-1', name: 'ARIA OS', status: 'active', phase: 'development' } as Project
const mockCreate = { name: 'New Project', status: 'active' } as ProjectCreate
const mockUpdate = { phase: 'testing' } as ProjectUpdate

describe('projectService', () => {
  describe('list', () => {
    it('returns array', async () => {
      mockedApi.get.mockResolvedValue([mock])
      const result = await projectService.list()
      expect(result).toEqual([mock])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/projects')
    })
  })

  describe('get', () => {
    it('returns single', async () => {
      mockedApi.get.mockResolvedValue(mock)
      const result = await projectService.get('proj-1')
      expect(result).toEqual(mock)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/projects/proj-1')
    })
  })

  describe('create', () => {
    it('creates and returns', async () => {
      mockedApi.post.mockResolvedValue(mock)
      const result = await projectService.create(mockCreate)
      expect(result).toEqual(mock)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/projects', mockCreate)
    })
  })

  describe('update', () => {
    it('updates and returns', async () => {
      mockedApi.put.mockResolvedValue(mock)
      const result = await projectService.update('proj-1', mockUpdate)
      expect(result).toEqual(mock)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/projects/proj-1', mockUpdate)
    })
  })

  describe('delete', () => {
    it('deletes and returns message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await projectService.delete('proj-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/projects/proj-1')
    })
  })
})
