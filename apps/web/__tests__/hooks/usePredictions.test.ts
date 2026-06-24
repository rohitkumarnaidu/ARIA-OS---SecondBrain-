import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { usePredictions } from '@/hooks/usePredictions'

const mockTaskCompletion = vi.fn()
const mockHabits = vi.fn()
const mockSleep = vi.fn()
const mockSmartSlots = vi.fn()

vi.mock('@/lib/ai', () => ({
  predictive: {
    taskCompletion: (...args: unknown[]) => mockTaskCompletion(...args),
    habits: (...args: unknown[]) => mockHabits(...args),
    sleep: (...args: unknown[]) => mockSleep(...args),
    smartSlots: (...args: unknown[]) => mockSmartSlots(...args),
  },
}))

const taskData = {
  total_pending: 5,
  high_completion: 3,
  at_risk_count: 1,
  predictions: [],
}
const habitData = { total_active: 4, at_risk_count: 0, predictions: [] }
const sleepData = {
  average_score: 78,
  average_duration: 7.5,
  trend: 'stable',
  recommendation: 'Keep it up',
}
const slotsData = { slots: [], best_hour: 9, best_day: 1 }

describe('usePredictions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockTaskCompletion.mockResolvedValue(taskData)
    mockHabits.mockResolvedValue(habitData)
    mockSleep.mockResolvedValue(sleepData)
    mockSmartSlots.mockResolvedValue(slotsData)
  })

  it('should return loading as true initially', () => {
    mockTaskCompletion.mockReturnValue(new Promise(() => {}))
    const { result } = renderHook(() => usePredictions())
    expect(result.current.loading).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('should fetch all predictions on mount', async () => {
    const { result } = renderHook(() => usePredictions())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(mockTaskCompletion).toHaveBeenCalledOnce()
    expect(mockHabits).toHaveBeenCalledOnce()
    expect(mockSleep).toHaveBeenCalledOnce()
    expect(mockSmartSlots).toHaveBeenCalledOnce()
  })

  it('should set all prediction data on success', async () => {
    const { result } = renderHook(() => usePredictions())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.tasks).toEqual(taskData)
    expect(result.current.habits).toEqual(habitData)
    expect(result.current.sleep).toEqual(sleepData)
    expect(result.current.slots).toEqual(slotsData)
    expect(result.current.error).toBeNull()
  })

  it('should handle partial failures gracefully', async () => {
    mockTaskCompletion.mockRejectedValue(new Error('API error'))
    const { result } = renderHook(() => usePredictions())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.tasks).toBeNull()
    expect(result.current.habits).toEqual(habitData)
    expect(result.current.error).toContain('API error')
  })

  it('should aggregate multiple errors', async () => {
    mockTaskCompletion.mockRejectedValue(new Error('Tasks failed'))
    mockHabits.mockRejectedValue(new Error('Habits failed'))
    const { result } = renderHook(() => usePredictions())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toContain('Tasks failed')
    expect(result.current.error).toContain('Habits failed')
  })

  it('should handle all failures', async () => {
    mockTaskCompletion.mockRejectedValue(new Error('Fail'))
    mockHabits.mockRejectedValue(new Error('Fail'))
    mockSleep.mockRejectedValue(new Error('Fail'))
    mockSmartSlots.mockRejectedValue(new Error('Fail'))
    const { result } = renderHook(() => usePredictions())
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.tasks).toBeNull()
    expect(result.current.habits).toBeNull()
    expect(result.current.sleep).toBeNull()
    expect(result.current.slots).toBeNull()
    expect(result.current.error).toBeTruthy()
  })

  it('should not update state after unmount', async () => {
    let resolvePromise!: (v: typeof taskData) => void
    mockTaskCompletion.mockReturnValue(new Promise((resolve) => {
      resolvePromise = resolve
    }))
    const { result, unmount } = renderHook(() => usePredictions())
    unmount()
    resolvePromise!(taskData)

    await vi.waitFor(() => expect(result.current.loading).toBe(true))
  })
})
