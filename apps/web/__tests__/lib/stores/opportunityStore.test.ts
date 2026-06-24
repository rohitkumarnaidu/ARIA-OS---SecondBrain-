import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useOpportunityStore } from '@/lib/stores/opportunityStore'
import { opportunityService } from '@/lib/services/opportunities'

vi.mock('@/lib/services/opportunities', () => ({
  opportunityService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockOpportunity = {
  id: '1',
  user_id: 'user1',
  title: 'Test Internship',
  url: 'https://example.com',
  opportunity_type: 'internship',
  status: 'saved' as const,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('opportunityStore', () => {
  beforeEach(() => {
    useOpportunityStore.setState(useOpportunityStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useOpportunityStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load opportunities', async () => {
    vi.mocked(opportunityService.list).mockResolvedValue([mockOpportunity])
    await useOpportunityStore.getState().fetch()
    const state = useOpportunityStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].title).toBe('Test Internship')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(opportunityService.list).mockRejectedValue(new Error('Network error'))
    await useOpportunityStore.getState().fetch()
    expect(useOpportunityStore.getState().error).toBe('Network error')
    expect(useOpportunityStore.getState().loading).toBe(false)
  })

  it('getById should return the correct opportunity', async () => {
    vi.mocked(opportunityService.list).mockResolvedValue([mockOpportunity])
    await useOpportunityStore.getState().fetch()
    const found = useOpportunityStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test Internship')
  })

  it('create should add an opportunity', async () => {
    vi.mocked(opportunityService.create).mockResolvedValue(mockOpportunity)
    await useOpportunityStore.getState().create({
      title: 'Test Internship',
      url: 'https://example.com',
      opportunity_type: 'internship',
    })
    expect(useOpportunityStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(opportunityService.create).mockRejectedValue(new Error('Create failed'))
    await useOpportunityStore.getState().create({
      title: 'Test Internship',
      url: 'https://example.com',
      opportunity_type: 'internship',
    })
    expect(useOpportunityStore.getState().error).toBe('Create failed')
  })

  it('update should modify an opportunity', async () => {
    vi.mocked(opportunityService.list).mockResolvedValue([mockOpportunity])
    vi.mocked(opportunityService.update).mockResolvedValue({ ...mockOpportunity, title: 'Updated' })
    await useOpportunityStore.getState().fetch()
    await useOpportunityStore.getState().update('1', { title: 'Updated' })
    expect(useOpportunityStore.getState().items[0].title).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(opportunityService.update).mockRejectedValue(new Error('Update failed'))
    await useOpportunityStore.getState().update('1', { title: 'Updated' })
    expect(useOpportunityStore.getState().error).toBe('Update failed')
  })

  it('remove should delete an opportunity', async () => {
    vi.mocked(opportunityService.list).mockResolvedValue([mockOpportunity])
    vi.mocked(opportunityService.delete).mockResolvedValue({ message: 'Deleted' })
    await useOpportunityStore.getState().fetch()
    await useOpportunityStore.getState().remove('1')
    expect(useOpportunityStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(opportunityService.delete).mockRejectedValue(new Error('Delete failed'))
    await useOpportunityStore.getState().remove('1')
    expect(useOpportunityStore.getState().error).toBe('Delete failed')
  })
})
