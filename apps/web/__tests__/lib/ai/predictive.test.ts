import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { predictive } from '@/lib/ai/predictive'

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn(),
  },
}))

describe('predictive', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
    predictive.clearCache()
    Object.defineProperty(navigator, 'onLine', { value: true, configurable: true })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // ─── taskCompletion ──────────────────────────────────────────────────────

  it('taskCompletion fetches and returns data', async () => {
    const { api } = await import('@/lib/api')
    const mockData = {
      total_pending: 10,
      high_completion: 3,
      at_risk_count: 2,
      predictions: [{ task_id: '1', probability: 0.8 }],
    }
    vi.mocked(api.get).mockResolvedValue(mockData)

    const result = await predictive.taskCompletion()
    expect(result).toEqual(mockData)
    expect(api.get).toHaveBeenCalledWith('/api/v1/predictions/tasks')
  })

  it('taskCompletion falls back on API error', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockRejectedValue(new Error('API down'))

    const result = await predictive.taskCompletion()
    expect(result).toEqual({
      total_pending: 0,
      high_completion: 0,
      at_risk_count: 0,
      predictions: [],
    })
  })

  it('taskCompletion caches results and does not re-fetch', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_pending: 5, high_completion: 2, at_risk_count: 0, predictions: [],
    })

    await predictive.taskCompletion()
    await predictive.taskCompletion()

    expect(api.get).toHaveBeenCalledTimes(1)
  })

  it('taskCompletion respects cache TTL', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_pending: 1, high_completion: 1, at_risk_count: 0, predictions: [],
    })

    await predictive.taskCompletion()
    vi.advanceTimersByTime(6 * 60 * 1000)
    await predictive.taskCompletion()

    expect(api.get).toHaveBeenCalledTimes(2)
  })

  // ─── habits ──────────────────────────────────────────────────────────────

  it('habits returns empty fallback when API fails', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockRejectedValue(new Error('fail'))

    const result = await predictive.habits()
    expect(result).toEqual({
      total_active: 0,
      at_risk_count: 0,
      predictions: [],
    })
  })

  it('habits fetches from correct endpoint', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_active: 5, at_risk_count: 1, predictions: [],
    })

    const result = await predictive.habits()
    expect(api.get).toHaveBeenCalledWith('/api/v1/predictions/habits')
    expect(result.total_active).toBe(5)
  })

  // ─── sleep ───────────────────────────────────────────────────────────────

  it('sleep returns fallback when API unavailable', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockRejectedValue(new Error('fail'))

    const result = await predictive.sleep()
    expect(result).toEqual({
      average_score: 0,
      average_duration: 0,
      trend: 'stable',
      recommendation: 'Track more sleep data for personalized insights.',
    })
  })

  it('sleep fetches from correct endpoint', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      average_score: 75, average_duration: 7.5, trend: 'improving', recommendation: 'Keep it up!',
    })

    const result = await predictive.sleep()
    expect(api.get).toHaveBeenCalledWith('/api/v1/predictions/sleep')
    expect(result.average_score).toBe(75)
  })

  // ─── smartSlots ──────────────────────────────────────────────────────────

  it('smartSlots returns fallback when API fails', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockRejectedValue(new Error('fail'))

    const result = await predictive.smartSlots()
    expect(result).toEqual({ slots: [], best_hour: 9, best_day: 1 })
  })

  it('smartSlots fetches from correct endpoint', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      slots: [{ start: '09:00', end: '10:00' }], best_hour: 9, best_day: 1,
    })

    const result = await predictive.smartSlots()
    expect(api.get).toHaveBeenCalledWith('/api/v1/predictions/slots')
    expect(result.slots).toHaveLength(1)
  })

  // ─── Deduplication ───────────────────────────────────────────────────────

  it('deduplicates concurrent requests', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_pending: 3, high_completion: 1, at_risk_count: 0, predictions: [],
    })

    const [r1, r2] = await Promise.all([
      predictive.taskCompletion(),
      predictive.taskCompletion(),
    ])

    expect(api.get).toHaveBeenCalledTimes(1)
    expect(r1).toEqual(r2)
  })

  // ─── clearCache / invalidate ─────────────────────────────────────────────

  it('clearCache removes all cached entries', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_pending: 1, high_completion: 1, at_risk_count: 0, predictions: [],
    })

    await predictive.taskCompletion()
    predictive.clearCache()
    await predictive.taskCompletion()

    expect(api.get).toHaveBeenCalledTimes(2)
  })

  it('invalidate with no args clears all cache', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_pending: 1, high_completion: 1, at_risk_count: 0, predictions: [],
    })

    await predictive.taskCompletion()
    predictive.invalidate()
    await predictive.taskCompletion()

    expect(api.get).toHaveBeenCalledTimes(2)
  })

  it('invalidate with keys clears specific cache entries', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValue({
      total_pending: 1, high_completion: 1, at_risk_count: 0, predictions: [],
    })

    await predictive.taskCompletion()
    await predictive.habits()
    expect(api.get).toHaveBeenCalledTimes(2)

    predictive.invalidate(['tasks'])
    await predictive.taskCompletion()
    await predictive.habits()

    // tasks should be refetched, habits cached
    expect(api.get).toHaveBeenCalledTimes(3)
  })

  // ─── Offline behavior ────────────────────────────────────────────────────

  it('uses fallback default when offline', async () => {
    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true })
    // When offline, fallback runs and returns default values
    const result = await predictive.taskCompletion()
    expect(result.total_pending).toBe(0)
  })

  it('uses fallback default when offline and cache expired', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockResolvedValueOnce({
      total_pending: 5, high_completion: 2, at_risk_count: 0, predictions: [],
    })
    await predictive.taskCompletion()

    // Advance past TTL so cache expires
    vi.advanceTimersByTime(6 * 60 * 1000)

    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true })

    const result = await predictive.taskCompletion()
    expect(result.total_pending).toBe(0)
  })

  it('returns fallback default when offline with no cache', async () => {
    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true })
    const result = await predictive.sleep()
    expect(result.average_score).toBe(0)
    expect(result.trend).toBe('stable')
  })

  it('returns fallback when online fetch fails', async () => {
    const { api } = await import('@/lib/api')
    vi.mocked(api.get).mockRejectedValue(new Error('fail'))

    const result = await predictive.taskCompletion()
    expect(result.total_pending).toBe(0)
  })
})
