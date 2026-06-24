import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useAuth } from '@/hooks/useAuth'

const mockGetSession = vi.fn()
const mockOnAuthStateChange = vi.fn()

vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: (...args: unknown[]) => mockGetSession(...args),
      onAuthStateChange: (...args: unknown[]) => mockOnAuthStateChange(...args),
    },
  },
  isUsingPlaceholders: false,
}))

const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  app_metadata: {},
  user_metadata: {},
  aud: 'authenticated',
  created_at: '2026-01-01T00:00:00Z',
}

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetSession.mockResolvedValue({ data: { session: null }, error: null })
    mockOnAuthStateChange.mockReturnValue({
      data: { subscription: { unsubscribe: vi.fn() } },
    })
  })

  it('should return loading as true initially', () => {
    mockGetSession.mockReturnValue(new Promise(() => {}))
    const { result } = renderHook(() => useAuth())
    expect(result.current.loading).toBe(true)
    expect(result.current.user).toBeNull()
  })

  it('should set user when session exists', async () => {
    mockGetSession.mockResolvedValue({
      data: { session: { user: mockUser } },
      error: null,
    })
    const { result } = renderHook(() => useAuth())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user).toEqual(mockUser)
  })

  it('should set user to null when no session', async () => {
    const { result } = renderHook(() => useAuth())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user).toBeNull()
  })

  it('should update user on auth state change', async () => {
    mockGetSession.mockResolvedValue({ data: { session: null }, error: null })
    const { result } = renderHook(() => useAuth())
    await waitFor(() => expect(result.current.loading).toBe(false))

    const [callback] = mockOnAuthStateChange.mock.calls[0]
    act(() => {
      callback('SIGNED_IN', { user: mockUser })
    })
    expect(result.current.user).toEqual(mockUser)
    expect(result.current.loading).toBe(false)
  })

  it('should set user to null on SIGNED_OUT', async () => {
    mockGetSession.mockResolvedValue({
      data: { session: { user: mockUser } },
      error: null,
    })
    const { result } = renderHook(() => useAuth())
    await waitFor(() => expect(result.current.user).toEqual(mockUser))

    const [callback] = mockOnAuthStateChange.mock.calls[0]
    act(() => {
      callback('SIGNED_OUT', { session: null })
    })
    expect(result.current.user).toBeNull()
  })

  it('should unsubscribe on unmount', () => {
    const unsubscribe = vi.fn()
    mockOnAuthStateChange.mockReturnValue({
      data: { subscription: { unsubscribe } },
    })
    const { unmount } = renderHook(() => useAuth())
    unmount()
    expect(unsubscribe).toHaveBeenCalledOnce()
  })
})
