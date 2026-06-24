import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useRealtime } from '@/hooks/useRealtime'

const mockChannelOn = vi.fn()
const mockChannelSubscribe = vi.fn()
const mockRemoveChannel = vi.fn()
const channelObject = { on: mockChannelOn, subscribe: mockChannelSubscribe }
mockChannelOn.mockReturnValue(channelObject)
mockChannelSubscribe.mockReturnValue(channelObject)
const mockChannel = vi.fn(() => channelObject)

vi.mock('@/lib/supabase', () => ({
  supabase: {
    channel: (...args: unknown[]) => mockChannel(...args),
    removeChannel: (...args: unknown[]) => mockRemoveChannel(...args),
  },
}))

describe('useRealtime', () => {
  const options = {
    table: 'tasks',
    userId: 'user-123',
    onInsert: vi.fn(),
    onUpdate: vi.fn(),
    onDelete: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(mockChannelOn).mockReturnValue(channelObject)
    vi.mocked(mockChannelSubscribe).mockReturnValue(channelObject)
  })

  it('should create channel with correct table name', () => {
    renderHook(() => useRealtime(options))
    expect(mockChannel).toHaveBeenCalledWith('tasks_changes')
  })

  it('should subscribe to INSERT, UPDATE, DELETE events', () => {
    renderHook(() => useRealtime(options))
    const calls = mockChannelOn.mock.calls
    expect(calls[0][0]).toBe('postgres_changes')
    expect(calls[0][1].event).toBe('INSERT')
    expect(calls[1][1].event).toBe('UPDATE')
    expect(calls[2][1].event).toBe('DELETE')
  })

  it('should call onInsert when INSERT event fires', () => {
    const onInsert = vi.fn()
    renderHook(() => useRealtime({ ...options, onInsert }))

    const insertCallback = mockChannelOn.mock.calls[0][2]
    insertCallback({ new: { id: '1', title: 'New Task' } })
    expect(onInsert).toHaveBeenCalledWith({ id: '1', title: 'New Task' })
  })

  it('should call onUpdate when UPDATE event fires', () => {
    const onUpdate = vi.fn()
    renderHook(() => useRealtime({ ...options, onUpdate }))

    const updateCallback = mockChannelOn.mock.calls[1][2]
    updateCallback({ new: { id: '1', status: 'completed' } })
    expect(onUpdate).toHaveBeenCalledWith({ id: '1', status: 'completed' })
  })

  it('should call onDelete when DELETE event fires with old data', () => {
    const onDelete = vi.fn()
    renderHook(() => useRealtime({ ...options, onDelete }))

    const deleteCallback = mockChannelOn.mock.calls[2][2]
    deleteCallback({ old: { id: '1' } })
    expect(onDelete).toHaveBeenCalledWith({ id: '1' })
  })

  it('should not setup subscription when userId is empty', () => {
    renderHook(() => useRealtime({ ...options, userId: '' }))
    expect(mockChannel).not.toHaveBeenCalled()
  })

  it('should remove channel on unmount', () => {
    const { unmount } = renderHook(() => useRealtime(options))
    const channelInstance = mockChannel.mock.results[0]?.value
    unmount()
    expect(mockRemoveChannel).toHaveBeenCalledWith(channelInstance)
  })

  it('should handle missing callbacks gracefully', () => {
    renderHook(() => useRealtime({ table: 'tasks', userId: 'user-123' }))

    const insertCallback = mockChannelOn.mock.calls[0][2]
    expect(() => {
      insertCallback({ new: { id: '1' } })
    }).not.toThrow()
  })

  it('should call subscribe on the channel', () => {
    renderHook(() => useRealtime(options))
    expect(mockChannelSubscribe).toHaveBeenCalled()
  })
})
