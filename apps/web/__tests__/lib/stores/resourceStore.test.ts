import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useResourceStore } from '@/lib/stores/resourceStore'
import { resourceService } from '@/lib/services/resources'

vi.mock('@/lib/services/resources', () => ({
  resourceService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockResource = {
  id: '1',
  user_id: 'user1',
  title: 'Test Resource',
  resource_type: 'article',
  is_archived: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('resourceStore', () => {
  beforeEach(() => {
    useResourceStore.setState(useResourceStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useResourceStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load resources', async () => {
    vi.mocked(resourceService.list).mockResolvedValue([mockResource])
    await useResourceStore.getState().fetch()
    const state = useResourceStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].title).toBe('Test Resource')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(resourceService.list).mockRejectedValue(new Error('Network error'))
    await useResourceStore.getState().fetch()
    expect(useResourceStore.getState().error).toBe('Network error')
    expect(useResourceStore.getState().loading).toBe(false)
  })

  it('getById should return the correct resource', async () => {
    vi.mocked(resourceService.list).mockResolvedValue([mockResource])
    await useResourceStore.getState().fetch()
    const found = useResourceStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test Resource')
  })

  it('create should add a resource', async () => {
    vi.mocked(resourceService.create).mockResolvedValue(mockResource)
    await useResourceStore.getState().create({ title: 'Test Resource', resource_type: 'article' })
    expect(useResourceStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(resourceService.create).mockRejectedValue(new Error('Create failed'))
    await useResourceStore.getState().create({ title: 'Test Resource', resource_type: 'article' })
    expect(useResourceStore.getState().error).toBe('Create failed')
  })

  it('update should modify a resource', async () => {
    vi.mocked(resourceService.list).mockResolvedValue([mockResource])
    vi.mocked(resourceService.update).mockResolvedValue({ ...mockResource, title: 'Updated' })
    await useResourceStore.getState().fetch()
    await useResourceStore.getState().update('1', { title: 'Updated' })
    expect(useResourceStore.getState().items[0].title).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(resourceService.update).mockRejectedValue(new Error('Update failed'))
    await useResourceStore.getState().update('1', { title: 'Updated' })
    expect(useResourceStore.getState().error).toBe('Update failed')
  })

  it('remove should delete a resource', async () => {
    vi.mocked(resourceService.list).mockResolvedValue([mockResource])
    vi.mocked(resourceService.delete).mockResolvedValue({ message: 'Deleted' })
    await useResourceStore.getState().fetch()
    await useResourceStore.getState().remove('1')
    expect(useResourceStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(resourceService.delete).mockRejectedValue(new Error('Delete failed'))
    await useResourceStore.getState().remove('1')
    expect(useResourceStore.getState().error).toBe('Delete failed')
  })
})
