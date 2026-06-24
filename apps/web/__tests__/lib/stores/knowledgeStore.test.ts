import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useKnowledgeStore } from '@/lib/stores/knowledgeStore'

const mockList = vi.fn()
const mockSearch = vi.fn()

vi.mock('@/lib/services/knowledge', () => ({
  knowledgeService: {
    list: (...args: unknown[]) => mockList(...args),
    search: (...args: unknown[]) => mockSearch(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useKnowledgeStore.setState({ nodes: [], edges: [], loading: false, error: null, searchQuery: '' })
})

describe('knowledgeStore', () => {
  it('has correct initial state', () => {
    const s = useKnowledgeStore.getState()
    expect(s.nodes).toEqual([])
    expect(s.edges).toEqual([])
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
    expect(s.searchQuery).toBe('')
  })

  it('fetch loads graph data', async () => {
    const data = { nodes: [{ id: 'n1', label: 'Concept' }], edges: [{ source: 'n1', target: 'n2' }] }
    mockList.mockResolvedValueOnce(data)
    await useKnowledgeStore.getState().fetch()
    const s = useKnowledgeStore.getState()
    expect(s.nodes).toEqual(data.nodes)
    expect(s.edges).toEqual(data.edges)
    expect(s.loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('Graph unavailable'))
    await useKnowledgeStore.getState().fetch()
    expect(useKnowledgeStore.getState().error).toBe('Graph unavailable')
  })

  it('search sets searchQuery and returns nodes', async () => {
    const results = [{ id: 'n2', label: 'Result' }]
    mockSearch.mockResolvedValueOnce(results)
    await useKnowledgeStore.getState().search('machine learning')
    const s = useKnowledgeStore.getState()
    expect(s.searchQuery).toBe('machine learning')
    expect(s.nodes).toEqual(results)
    expect(s.loading).toBe(false)
  })

  it('search sets error on failure', async () => {
    mockSearch.mockRejectedValueOnce(new Error('Search failed'))
    await useKnowledgeStore.getState().search('bad query')
    expect(useKnowledgeStore.getState().error).toBe('Search failed')
  })

  it('setSearchQuery updates query string', () => {
    useKnowledgeStore.getState().setSearchQuery('neural networks')
    expect(useKnowledgeStore.getState().searchQuery).toBe('neural networks')
  })
})
