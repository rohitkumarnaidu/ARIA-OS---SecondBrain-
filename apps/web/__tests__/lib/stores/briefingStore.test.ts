import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useBriefingStore } from '@/lib/stores/briefingStore'

const mockList = vi.fn()
const mockGetToday = vi.fn()

vi.mock('@/lib/services/briefings', () => ({
  briefingService: {
    list: (...args: unknown[]) => mockList(...args),
    getToday: (...args: unknown[]) => mockGetToday(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useBriefingStore.setState({ items: [], today: null, loading: false, error: null })
})

describe('briefingStore', () => {
  it('has correct initial state', () => {
    const s = useBriefingStore.getState()
    expect(s.items).toEqual([])
    expect(s.today).toBeNull()
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetch loads briefings', async () => {
    const items = [{ id: 'b1', title: 'Morning Briefing', date: '2026-01-15' }]
    mockList.mockResolvedValueOnce(items)
    await useBriefingStore.getState().fetch()
    const s = useBriefingStore.getState()
    expect(s.items).toEqual(items)
    expect(s.loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('Server error'))
    await useBriefingStore.getState().fetch()
    expect(useBriefingStore.getState().error).toBe('Server error')
  })

  it('getById returns matching briefing', () => {
    useBriefingStore.setState({ items: [{ id: 'b1', title: 'Briefing 1' }, { id: 'b2', title: 'Briefing 2' }] })
    const found = useBriefingStore.getState().getById('b1')
    expect(found?.title).toBe('Briefing 1')
  })

  it('getById returns undefined for missing id', () => {
    useBriefingStore.setState({ items: [{ id: 'b1', title: 'Briefing 1' }] })
    expect(useBriefingStore.getState().getById('missing')).toBeUndefined()
  })

  it('getToday loads today briefing', async () => {
    const briefing = { id: 'today-1', title: 'Today Briefing', date: '2026-01-15' }
    mockGetToday.mockResolvedValueOnce(briefing)
    await useBriefingStore.getState().getToday()
    const s = useBriefingStore.getState()
    expect(s.today).toEqual(briefing)
    expect(s.loading).toBe(false)
  })

  it('getToday sets error on failure', async () => {
    mockGetToday.mockRejectedValueOnce(new Error('No briefing for today'))
    await useBriefingStore.getState().getToday()
    expect(useBriefingStore.getState().error).toBe('No briefing for today')
  })
})
