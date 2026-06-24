import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useReviewStore } from '@/lib/stores/reviewStore'

const mockList = vi.fn()
const mockGetLatest = vi.fn()

vi.mock('@/lib/services/reviews', () => ({
  reviewService: {
    list: (...args: unknown[]) => mockList(...args),
    getLatest: (...args: unknown[]) => mockGetLatest(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  useReviewStore.setState({ items: [], latest: null, loading: false, error: null })
})

describe('reviewStore', () => {
  it('has correct initial state', () => {
    const s = useReviewStore.getState()
    expect(s.items).toEqual([])
    expect(s.latest).toBeNull()
    expect(s.loading).toBe(false)
    expect(s.error).toBeNull()
  })

  it('fetch loads reviews', async () => {
    const items = [{ id: 'r1', title: 'Week 3 Review', weekStart: '2026-W03' }]
    mockList.mockResolvedValueOnce(items)
    await useReviewStore.getState().fetch()
    const s = useReviewStore.getState()
    expect(s.items).toEqual(items)
    expect(s.loading).toBe(false)
  })

  it('fetch sets error on failure', async () => {
    mockList.mockRejectedValueOnce(new Error('Server error'))
    await useReviewStore.getState().fetch()
    expect(useReviewStore.getState().error).toBe('Server error')
  })

  it('getById returns matching review', () => {
    useReviewStore.setState({ items: [{ id: 'r1', title: 'Review 1' }, { id: 'r2', title: 'Review 2' }] })
    expect(useReviewStore.getState().getById('r1')).toBeDefined()
    expect(useReviewStore.getState().getById('r1').title).toBe('Review 1')
    expect(useReviewStore.getState().getById('missing')).toBeUndefined()
  })

  it('getLatest loads the latest review', async () => {
    const review = { id: 'r3', title: 'Latest Review', weekStart: '2026-W05' }
    mockGetLatest.mockResolvedValueOnce(review)
    await useReviewStore.getState().getLatest()
    const s = useReviewStore.getState()
    expect(s.latest).toEqual(review)
    expect(s.loading).toBe(false)
  })

  it('getLatest sets error on failure', async () => {
    mockGetLatest.mockRejectedValueOnce(new Error('No review found'))
    await useReviewStore.getState().getLatest()
    expect(useReviewStore.getState().error).toBe('No review found')
  })
})
