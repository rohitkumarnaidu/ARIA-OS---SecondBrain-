import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useSleepStore } from '@/lib/stores/sleepStore'
import { sleepService } from '@/lib/services/sleep'

vi.mock('@/lib/services/sleep', () => ({
  sleepService: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockSleepLog = {
  id: '1',
  user_id: 'user1',
  bedtime: '2026-01-01T23:00:00Z',
  wake_time: '2026-01-02T07:00:00Z',
  quality_rating: 4,
  duration_hours: 8,
  sleep_score: 85,
  sleep_debt: 0,
  created_at: '2026-01-01T00:00:00Z',
}

describe('sleepStore', () => {
  beforeEach(() => {
    useSleepStore.setState(useSleepStore.getInitialState())
    vi.clearAllMocks()
  })

  it('should have correct initial state', () => {
    const state = useSleepStore.getState()
    expect(state.items).toEqual([])
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('fetch should load sleep logs', async () => {
    vi.mocked(sleepService.list).mockResolvedValue([mockSleepLog])
    await useSleepStore.getState().fetch()
    const state = useSleepStore.getState()
    expect(state.items).toHaveLength(1)
    expect(state.items[0].sleep_score).toBe(85)
    expect(state.loading).toBe(false)
  })

  it('fetch should handle errors', async () => {
    vi.mocked(sleepService.list).mockRejectedValue(new Error('Network error'))
    await useSleepStore.getState().fetch()
    expect(useSleepStore.getState().error).toBe('Network error')
    expect(useSleepStore.getState().loading).toBe(false)
  })

  it('getById should return the correct sleep log', async () => {
    vi.mocked(sleepService.list).mockResolvedValue([mockSleepLog])
    await useSleepStore.getState().fetch()
    const found = useSleepStore.getState().getById('1')
    expect(found).toBeDefined()
    expect(found!.quality_rating).toBe(4)
  })

  it('create should add a sleep log', async () => {
    vi.mocked(sleepService.create).mockResolvedValue(mockSleepLog)
    await useSleepStore.getState().create({
      bedtime: '2026-01-01T23:00:00Z',
      wake_time: '2026-01-02T07:00:00Z',
      quality_rating: 4,
    })
    expect(useSleepStore.getState().items).toHaveLength(1)
  })

  it('create should handle errors', async () => {
    vi.mocked(sleepService.create).mockRejectedValue(new Error('Create failed'))
    await useSleepStore.getState().create({
      bedtime: '2026-01-01T23:00:00Z',
      wake_time: '2026-01-02T07:00:00Z',
      quality_rating: 4,
    })
    expect(useSleepStore.getState().error).toBe('Create failed')
  })

  it('remove should delete a sleep log', async () => {
    vi.mocked(sleepService.list).mockResolvedValue([mockSleepLog])
    vi.mocked(sleepService.delete).mockResolvedValue({ message: 'Deleted' })
    await useSleepStore.getState().fetch()
    await useSleepStore.getState().remove('1')
    expect(useSleepStore.getState().items).toHaveLength(0)
  })

  it('remove should handle errors', async () => {
    vi.mocked(sleepService.delete).mockRejectedValue(new Error('Delete failed'))
    await useSleepStore.getState().remove('1')
    expect(useSleepStore.getState().error).toBe('Delete failed')
  })
})
