import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useHabitStore } from '@/lib/stores/habitStore'
import { habitService } from '@/lib/services/habits'

vi.mock('@/lib/services/habits', () => ({
  habitService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    log: vi.fn(),
  },
}))

const mockHabit = {
  id: '1',
  user_id: 'user1',
  name: 'Read',
  frequency: 'daily' as const,
  is_active: true,
  current_streak: 0,
  best_streak: 0,
  consistency_percentage: 0,
  created_at: '2026-01-01T00:00:00Z',
}

const mockHabitLog = {
  id: 'log1',
  user_id: 'user1',
  habit_id: '1',
  date: '2026-01-01',
  completed: true,
  created_at: '2026-01-01T00:00:00Z',
}

describe('habitStore', () => {
  beforeEach(() => {
    useHabitStore.setState(useHabitStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useHabitStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load habits', async () => {
    vi.mocked(habitService.list).mockResolvedValue([mockHabit])
    await useHabitStore.getState().fetch()
    const state = useHabitStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].name).toBe('Read')
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(habitService.list).mockRejectedValue(new Error('Network error'))
    await useHabitStore.getState().fetch()
    expect(useHabitStore.getState().error).toBe('Network error')
    expect(useHabitStore.getState().loading).toBe(false)
  })

  it('getById should return the correct habit', async () => {
    vi.mocked(habitService.list).mockResolvedValue([mockHabit])
    await useHabitStore.getState().fetch()
    const found = useHabitStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.name).toBe('Read')
  })

  it('create should add a habit', async () => {
    vi.mocked(habitService.create).mockResolvedValue(mockHabit)
    await useHabitStore.getState().create({ name: 'Read' })
    expect(useHabitStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(habitService.create).mockRejectedValue(new Error('Create failed'))
    await useHabitStore.getState().create({ name: 'Read' })
    expect(useHabitStore.getState().error).toBe('Create failed')
  })

  it('update should modify a habit', async () => {
    vi.mocked(habitService.list).mockResolvedValue([mockHabit])
    vi.mocked(habitService.update).mockResolvedValue({ ...mockHabit, name: 'Updated' })
    await useHabitStore.getState().fetch()
    await useHabitStore.getState().update('1', { name: 'Updated' })
    expect(useHabitStore.getState().items[0].name).toBe('Updated')
  })

  it('update should handle errors', async () => {
    vi.mocked(habitService.update).mockRejectedValue(new Error('Update failed'))
    await useHabitStore.getState().update('1', { name: 'Updated' })
    expect(useHabitStore.getState().error).toBe('Update failed')
  })

  it('remove should delete a habit', async () => {
    vi.mocked(habitService.list).mockResolvedValue([mockHabit])
    vi.mocked(habitService.delete).mockResolvedValue({ message: 'Deleted' })
    await useHabitStore.getState().fetch()
    await useHabitStore.getState().remove('1')
    expect(useHabitStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(habitService.delete).mockRejectedValue(new Error('Delete failed'))
    await useHabitStore.getState().remove('1')
    expect(useHabitStore.getState().error).toBe('Delete failed')
  })

  it('log should record a habit log', async () => {
    vi.mocked(habitService.log).mockResolvedValue(mockHabitLog)
    const result = await useHabitStore.getState().log('1', { date: '2026-01-01', completed: true })
    expect(result).toBeDefined()
    expect(result!.completed).toBe(true)
    expect(useHabitStore.getState().loading).toBe(false)
  })

  it('log should handle errors', async () => {
    vi.mocked(habitService.log).mockRejectedValue(new Error('Log failed'))
    await useHabitStore.getState().log('1', { date: '2026-01-01', completed: true })
    expect(useHabitStore.getState().error).toBe('Log failed')
    expect(useHabitStore.getState().loading).toBe(false)
  })
})
