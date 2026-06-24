import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useStoreSync } from '@/hooks/useStoreSync'

const mockUseRealtime = vi.fn()

vi.mock('@/hooks/useRealtime', () => ({
  useRealtime: (...args: unknown[]) => mockUseRealtime(...args),
}))

const mockFetchTasks = vi.fn()
const mockFetchHabits = vi.fn()

vi.mock('@/lib/stores/taskStore', () => ({
  useTaskStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({ fetchTasks: mockFetchTasks }),
}))

vi.mock('@/lib/stores/habitStore', () => ({
  useHabitStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({ fetch: mockFetchHabits }),
}))

describe('useStoreSync', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should call useRealtime for tasks, habits, and habit_logs tables', () => {
    renderHook(() => useStoreSync('user-123'))
    expect(mockUseRealtime).toHaveBeenCalledTimes(3)
    expect(mockUseRealtime).toHaveBeenCalledWith(
      expect.objectContaining({ table: 'tasks', userId: 'user-123' })
    )
    expect(mockUseRealtime).toHaveBeenCalledWith(
      expect.objectContaining({ table: 'habits', userId: 'user-123' })
    )
    expect(mockUseRealtime).toHaveBeenCalledWith(
      expect.objectContaining({ table: 'habit_logs', userId: 'user-123' })
    )
  })

  it('should pass empty string when userId is undefined', () => {
    renderHook(() => useStoreSync())
    mockUseRealtime.mock.calls.forEach(([opts]) => {
      expect(opts.userId).toBe('')
    })
  })

  it('should call fetchTasks on task insert, update, delete', () => {
    renderHook(() => useStoreSync('user-123'))
    const taskCallbacks = mockUseRealtime.mock.calls[0][0]
    taskCallbacks.onInsert()
    taskCallbacks.onUpdate()
    taskCallbacks.onDelete()
    expect(mockFetchTasks).toHaveBeenCalledTimes(3)
  })

  it('should call fetchHabits on habit insert, update, delete', () => {
    renderHook(() => useStoreSync('user-123'))
    const habitCallbacks = mockUseRealtime.mock.calls[1][0]
    habitCallbacks.onInsert()
    habitCallbacks.onUpdate()
    habitCallbacks.onDelete()
    expect(mockFetchHabits).toHaveBeenCalledTimes(3)
  })

  it('should call fetchHabits on habit_logs insert, update, delete', () => {
    renderHook(() => useStoreSync('user-123'))
    const logCallbacks = mockUseRealtime.mock.calls[2][0]
    logCallbacks.onInsert()
    logCallbacks.onUpdate()
    logCallbacks.onDelete()
    expect(mockFetchHabits).toHaveBeenCalledTimes(3)
  })
})
