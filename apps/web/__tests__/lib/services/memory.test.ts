import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { memoryService } from '@/lib/services/memory'
import type { Memory, MemoryCreate, MemoryUpdate } from '@/lib/types'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

const mockMemory = { id: 'mem-1', content: 'test', type: 'fact', created_at: '2026-01-01' } as Memory
const mockMemoryCreate = { content: 'new memory', type: 'fact' } as MemoryCreate
const mockMemoryUpdate = { content: 'updated' } as MemoryUpdate

describe('memoryService', () => {
  describe('list', () => {
    it('returns an array of memories', async () => {
      mockedApi.get.mockResolvedValue([mockMemory])
      const result = await memoryService.list()
      expect(result).toEqual([mockMemory])
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/memory')
    })
  })

  describe('get', () => {
    it('returns a single memory', async () => {
      mockedApi.get.mockResolvedValue(mockMemory)
      const result = await memoryService.get('mem-1')
      expect(result).toEqual(mockMemory)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/memory/mem-1')
    })
  })

  describe('create', () => {
    it('creates and returns a memory', async () => {
      mockedApi.post.mockResolvedValue(mockMemory)
      const result = await memoryService.create(mockMemoryCreate)
      expect(result).toEqual(mockMemory)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/memory', mockMemoryCreate)
    })
  })

  describe('update', () => {
    it('updates and returns the memory', async () => {
      mockedApi.put.mockResolvedValue(mockMemory)
      const result = await memoryService.update('mem-1', mockMemoryUpdate)
      expect(result).toEqual(mockMemory)
      expect(mockedApi.put).toHaveBeenCalledWith('/api/v1/memory/mem-1', mockMemoryUpdate)
    })
  })

  describe('delete', () => {
    it('deletes the memory and returns a message', async () => {
      mockedApi.delete.mockResolvedValue({ message: 'deleted' })
      const result = await memoryService.delete('mem-1')
      expect(result).toEqual({ message: 'deleted' })
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/memory/mem-1')
    })
  })

  describe('consolidate', () => {
    it('posts to consolidate and returns status', async () => {
      const resp = { status: 'ok', total: 5, by_type: { fact: 3 } }
      mockedApi.post.mockResolvedValue(resp)
      const result = await memoryService.consolidate()
      expect(result).toEqual(resp)
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/memory/consolidate')
    })
  })
})
