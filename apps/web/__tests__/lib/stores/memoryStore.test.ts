import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMemoryStore } from '@/lib/stores/memoryStore'

const mockList = vi.fn()
const mockCreate = vi.fn()
const mockUpdate = vi.fn()
const mockDelete = vi.fn()

vi.mock('@/lib/services/memory', () => ({
  memoryService: {
    list: (...args: unknown[]) => mockList(...args),
    create: (...args: unknown[]) => mockCreate(...args),
    update: (...args: unknown[]) => mockUpdate(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useMemoryStore.setState({ items: [], loading: false, error: null })
})

describe('memoryStore', () => {
  it('has correct initial state', () => {
    const s = useMemoryStore.getState()
    expect(s.items).toEqual([])
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetch loads memories', async () => {
    const items = [{ id: 'm1', content: 'Important memory' }]
    mockList.mockResolvedValueOnce(items)
    await useMemoryStore.getState().fetch()
    expect(useMemoryStore.getState().items).toEqual(items)
    expect(useMemoryStore.getState().loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('DB error'))
    await useMemoryStore.getState().fetch()
    expect(useMemoryStore.getState().error).toBe('DB error')
  })

  it('getById returns matching memory', () => {
    useMemoryStore.setState({ items: [{ id: 'm1', content: 'A' }, { id: 'm2', content: 'B' }] })
    expect(useMemoryStore.getState().getById('m1')?.content).toBe('A')
    expect(useMemoryStore.getState().getById('missing')).toBeUndefined()
  })

  it('create prepends a memory', async () => {
    const created = { id: 'm3', content: 'New memory' }
    mockCreate.mockResolvedValueOnce(created)
    await useMemoryStore.getState().create({ content: 'New memory' })
    expect(useMemoryStore.getState().items).toEqual([created])
  })

  it('create sets error on failure', async () => {
    mockCreate.mockRejectedValueOnce(new Error('Creation failed'))
    await useMemoryStore.getState().create({ content: '' })
    expect(useMemoryStore.getState().error).toBe('Creation failed')
  })

  it('update replaces matching memory in place', async () => {
    useMemoryStore.setState({ items: [{ id: 'm1', content: 'Old' }, { id: 'm2', content: 'Other' }] })
    const updated = { id: 'm1', content: 'Updated' }
    mockUpdate.mockResolvedValueOnce(updated)
    await useMemoryStore.getState().update('m1', { content: 'Updated' })
    expect(useMemoryStore.getState().items).toEqual([updated, { id: 'm2', content: 'Other' }])
  })

  it('update sets error on failure', async () => {
    useMemoryStore.setState({ items: [{ id: 'm1', content: 'Old' }] })
    mockUpdate.mockRejectedValueOnce(new Error('Not found'))
    await useMemoryStore.getState().update('m1', { content: 'New' })
    expect(useMemoryStore.getState().error).toBe('Not found')
  })

  it('remove filters out deleted memory', async () => {
    useMemoryStore.setState({ items: [{ id: 'm1', content: 'A' }, { id: 'm2', content: 'B' }] })
    mockDelete.mockResolvedValueOnce({})
    await useMemoryStore.getState().remove('m1')
    expect(useMemoryStore.getState().items).toEqual([{ id: 'm2', content: 'B' }])
  })

  it('remove sets error on failure', async () => {
    mockDelete.mockRejectedValueOnce(new Error('Delete failed'))
    await useMemoryStore.getState().remove('x')
    expect(useMemoryStore.getState().error).toBe('Delete failed')
  })
})
