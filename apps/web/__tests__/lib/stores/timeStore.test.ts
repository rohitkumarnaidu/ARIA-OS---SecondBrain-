import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTimeStore } from '@/lib/stores/timeStore'
import { timeService } from '@/lib/services/time'

vi.mock('@/lib/services/time', () => ({
  timeService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    stop: vi.fn(),
    dailyStats: vi.fn(),
  },
}))

const mockEntry = {
  id: '1',
  user_id: 'user1',
  start_time: '2026-01-01T09:00:00Z',
  end_time: '2026-01-01T10:00:00Z',
  duration_minutes: 60,
  is_deep_work: true,
  category: 'coding',
  created_at: '2026-01-01T00:00:00Z',
}

const mockDailyStats = {
  date: '2026-01-01',
  total_minutes: 480,
  entries: [mockEntry],
}

describe('timeStore', () => {
  beforeEach(() => {
    useTimeStore.setState(useTimeStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useTimeStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
    expect(state.dailyStats).toBeNull()
  })

  it('fetch should load time entries', async () => {
    vi.mocked(timeService.list).mockResolvedValue([mockEntry])
    await useTimeStore.getState().fetch()
    const state = useTimeStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].duration_minutes).toBe(60)
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(timeService.list).mockRejectedValue(new Error('Network error'))
    await useTimeStore.getState().fetch()
    expect(useTimeStore.getState().error).toBe('Network error')
    expect(useTimeStore.getState().loading).toBe(false)
  })

  it('getById should return the correct entry', async () => {
    vi.mocked(timeService.list).mockResolvedValue([mockEntry])
    await useTimeStore.getState().fetch()
    const found = useTimeStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.category).toBe('coding')
  })

  it('create should add a time entry', async () => {
    vi.mocked(timeService.create).mockResolvedValue(mockEntry)
    await useTimeStore.getState().create({
      start_time: '2026-01-01T09:00:00Z',
      is_deep_work: true,
    })
    expect(useTimeStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(timeService.create).mockRejectedValue(new Error('Create failed'))
    await useTimeStore.getState().create({
      start_time: '2026-01-01T09:00:00Z',
      is_deep_work: true,
    })
    expect(useTimeStore.getState().error).toBe('Create failed')
  })

  it('update should modify a time entry', async () => {
    vi.mocked(timeService.list).mockResolvedValue([mockEntry])
    vi.mocked(timeService.update).mockResolvedValue({ ...mockEntry, duration_minutes: 90 })
    await useTimeStore.getState().fetch()
    await useTimeStore.getState().update('1', { duration_minutes: 90 })
    expect(useTimeStore.getState().items[0].duration_minutes).toBe(90)
  })

  it('update should handle errors', async () => {
    vi.mocked(timeService.update).mockRejectedValue(new Error('Update failed'))
    await useTimeStore.getState().update('1', { duration_minutes: 90 })
    expect(useTimeStore.getState().error).toBe('Update failed')
  })

  it('remove should delete a time entry', async () => {
    vi.mocked(timeService.list).mockResolvedValue([mockEntry])
    vi.mocked(timeService.delete).mockResolvedValue({ message: 'Deleted' })
    await useTimeStore.getState().fetch()
    await useTimeStore.getState().remove('1')
    expect(useTimeStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(timeService.delete).mockRejectedValue(new Error('Delete failed'))
    await useTimeStore.getState().remove('1')
    expect(useTimeStore.getState().error).toBe('Delete failed')
  })

  it('stop should stop a time entry', async () => {
    vi.mocked(timeService.list).mockResolvedValue([mockEntry])
    vi.mocked(timeService.stop).mockResolvedValue({ ...mockEntry, end_time: '2026-01-01T11:00:00Z' })
    await useTimeStore.getState().fetch()
    await useTimeStore.getState().stop('1')
    expect(useTimeStore.getState().items[0].end_time).toBe('2026-01-01T11:00:00Z')
  })

  it('stop should handle errors', async () => {
    vi.mocked(timeService.stop).mockRejectedValue(new Error('Stop failed'))
    await useTimeStore.getState().stop('1')
    expect(useTimeStore.getState().error).toBe('Stop failed')
  })

  it('fetchDailyStats should load daily stats', async () => {
    vi.mocked(timeService.dailyStats).mockResolvedValue(mockDailyStats)
    await useTimeStore.getState().fetchDailyStats('2026-01-01')
    const state = useTimeStore.getState()
    expect(state.dailyStats).toBeDefined()
    expect(state.dailyStats!.total_minutes).toBe(480)
    expect(state.loading).toBe(false)
  })

  it('fetchDailyStats should handle errors', async () => {
    vi.mocked(timeService.dailyStats).mockRejectedValue(new Error('Stats failed'))
    await useTimeStore.getState().fetchDailyStats('2026-01-01')
    expect(useTimeStore.getState().error).toBe('Stats failed')
    expect(useTimeStore.getState().loading).toBe(false)
  })
})
