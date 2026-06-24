import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'
import { knowledgeService } from '@/lib/services/knowledge'
import type { GraphNode, GraphEdge } from '@/components/knowledge'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() }
}))

const mockedApi = vi.mocked(api)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('knowledgeService', () => {
  describe('list', () => {
    it('returns nodes and edges', async () => {
      const data = { nodes: [{ id: '1' } as GraphNode], edges: [{ id: 'e1' } as GraphEdge] }
      mockedApi.get.mockResolvedValue(data)
      const result = await knowledgeService.list()
      expect(result).toEqual(data)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/knowledge')
    })
  })

  describe('get', () => {
    it('returns a single node', async () => {
      const node = { id: '1' } as GraphNode
      mockedApi.get.mockResolvedValue(node)
      const result = await knowledgeService.get('1')
      expect(result).toEqual(node)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/knowledge/1')
    })
  })

  describe('search', () => {
    it('returns matching nodes', async () => {
      const nodes = [{ id: '1', label: 'test' } as GraphNode]
      mockedApi.get.mockResolvedValue(nodes)
      const result = await knowledgeService.search('test')
      expect(result).toEqual(nodes)
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/knowledge/search', { params: { q: 'test' } })
    })
  })
})
