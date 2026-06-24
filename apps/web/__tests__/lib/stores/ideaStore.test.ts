import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useIdeaStore } from '@/lib/stores/ideaStore'
import { ideaService } from '@/lib/services/ideas'

vi.mock('@/lib/services/ideas', () => ({
  ideaService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockIdea = {
  id: '1',
  user_id: 'user1',
  title: 'Test Idea',
  status: 'raw',
  created_at: '2026-01-01T00:00:00Z',
}

describe('ideaStore', () => {
  beforeEach(() => {
    useIdeaStore.setState(useIdeaStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useIdeaStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load ideas', async () => {
    vi.mocked(ideaService.list).mockResolvedValue([mockIdea])
    await useIdeaStore.getState().fetch()
    const state = useIdeaStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].title).toBe('Test Idea')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(ideaService.list).mockRejectedValue(new Error('Network error'))
    await useIdeaStore.getState().fetch()
    expect(useIdeaStore.getState().error).toBe('Network error')
    expect(useIdeaStore.getState().loading).toBe(false)
  })

  it('getById should return the correct idea', async () => {
    vi.mocked(ideaService.list).mockResolvedValue([mockIdea])
    await useIdeaStore.getState().fetch()
    const found = useIdeaStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test Idea')
  })

  it('create should add an idea', async () => {
    vi.mocked(ideaService.create).mockResolvedValue(mockIdea)
    await useIdeaStore.getState().create({ title: 'Test Idea' })
    expect(useIdeaStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(ideaService.create).mockRejectedValue(new Error('Create failed'))
    await useIdeaStore.getState().create({ title: 'Test Idea' })
    expect(useIdeaStore.getState().error).toBe('Create failed')
  })

  it('update should modify an idea', async () => {
    vi.mocked(ideaService.list).mockResolvedValue([mockIdea])
    vi.mocked(ideaService.update).mockResolvedValue({ ...mockIdea, title: 'Updated' })
    await useIdeaStore.getState().fetch()
    await useIdeaStore.getState().update('1', { title: 'Updated' })
    expect(useIdeaStore.getState().items[0].title).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(ideaService.update).mockRejectedValue(new Error('Update failed'))
    await useIdeaStore.getState().update('1', { title: 'Updated' })
    expect(useIdeaStore.getState().error).toBe('Update failed')
  })

  it('remove should delete an idea', async () => {
    vi.mocked(ideaService.list).mockResolvedValue([mockIdea])
    vi.mocked(ideaService.delete).mockResolvedValue({ message: 'Deleted' })
    await useIdeaStore.getState().fetch()
    await useIdeaStore.getState().remove('1')
    expect(useIdeaStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(ideaService.delete).mockRejectedValue(new Error('Delete failed'))
    await useIdeaStore.getState().remove('1')
    expect(useIdeaStore.getState().error).toBe('Delete failed')
  })
})
