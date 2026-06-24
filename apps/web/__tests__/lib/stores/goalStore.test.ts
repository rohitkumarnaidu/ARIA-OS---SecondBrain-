import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useGoalStore } from '@/lib/stores/goalStore'
import { goalService } from '@/lib/services/goals'

vi.mock('@/lib/services/goals', () => ({
  goalService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockGoal = {
  id: '1',
  user_id: 'user1',
  title: 'Test Goal',
  status: 'active' as const,
  progress: 0,
  created_at: '2026-01-01T00:00:00Z',
}

describe('goalStore', () => {
  beforeEach(() => {
    useGoalStore.setState(useGoalStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useGoalStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load goals', async () => {
    vi.mocked(goalService.list).mockResolvedValue([mockGoal])
    await useGoalStore.getState().fetch()
    const state = useGoalStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].title).toBe('Test Goal')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(goalService.list).mockRejectedValue(new Error('Network error'))
    await useGoalStore.getState().fetch()
    expect(useGoalStore.getState().error).toBe('Network error')
    expect(useGoalStore.getState().loading).toBe(false)
  })

  it('getById should return the correct goal', async () => {
    vi.mocked(goalService.list).mockResolvedValue([mockGoal])
    await useGoalStore.getState().fetch()
    const found = useGoalStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.title).toBe('Test Goal')
  })

  it('create should add a goal', async () => {
    vi.mocked(goalService.create).mockResolvedValue(mockGoal)
    await useGoalStore.getState().create({ title: 'Test Goal' })
    expect(useGoalStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(goalService.create).mockRejectedValue(new Error('Create failed'))
    await useGoalStore.getState().create({ title: 'Test Goal' })
    expect(useGoalStore.getState().error).toBe('Create failed')
  })

  it('update should modify a goal', async () => {
    vi.mocked(goalService.list).mockResolvedValue([mockGoal])
    vi.mocked(goalService.update).mockResolvedValue({ ...mockGoal, title: 'Updated' })
    await useGoalStore.getState().fetch()
    await useGoalStore.getState().update('1', { title: 'Updated' })
    expect(useGoalStore.getState().items[0].title).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(goalService.update).mockRejectedValue(new Error('Update failed'))
    await useGoalStore.getState().update('1', { title: 'Updated' })
    expect(useGoalStore.getState().error).toBe('Update failed')
  })

  it('remove should delete a goal', async () => {
    vi.mocked(goalService.list).mockResolvedValue([mockGoal])
    vi.mocked(goalService.delete).mockResolvedValue({ message: 'Deleted' })
    await useGoalStore.getState().fetch()
    await useGoalStore.getState().remove('1')
    expect(useGoalStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(goalService.delete).mockRejectedValue(new Error('Delete failed'))
    await useGoalStore.getState().remove('1')
    expect(useGoalStore.getState().error).toBe('Delete failed')
  })
})
