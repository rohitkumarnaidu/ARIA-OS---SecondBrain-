import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { resourceService } from '@/lib/services/resources'
import type { Resource, ResourceCreate, ResourceUpdate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mock = { id: 'res-1', title: 'React Docs', url: 'https://react.dev', tags: ['react'] } as Resource
const mockCreate = { title: 'New Resource', url: 'https://example.com' } as ResourceCreate
const mockUpdate = { tags: ['react', 'frontend'] } as ResourceUpdate

describe('resourceService', () => {
  describe('list', () => {
    it('returns array', async () => {
      mockedApi.get.mockResolvedValue([mock])
      const result = await resourceService.list()
      expect(result).toEqual([mock])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/resources')
    })
  })

  describe('get', () => {
    it('returns single', async () => {
      mockedApi.get.mockResolvedValue(mock)
      const result = await resourceService.get('res-1')
      expect(result).toEqual(mock)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/resources/res-1')
    })
  })

  describe('create', () => {
    it('creates and returns', async () => {
      mockedApi.post.mockResolvedValue(mock)
      const result = await resourceService.create(mockCreate)
      expect(result).toEqual(mock)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/resources', mockCreate)
    })
  })

  describe('update', () => {
    it('updates and returns', async () => {
      mockedApi.put.mockResolvedValue(mock)
      const result = await resourceService.update('res-1', mockUpdate)
      expect(result).toEqual(mock)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/resources/res-1', mockUpdate)
    })
  })

  describe('delete', () => {
    it('deletes and returns message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await resourceService.delete('res-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/resources/res-1')
    })
  })
})
