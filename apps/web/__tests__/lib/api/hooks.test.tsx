import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import type { ReactNode } from 'react'

vi.mock('@/lib/api/client', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

const { useApiQuery, useApiMutation, useApiInfiniteQuery } = await import('@/lib/api/hooks')
const { api } = await import('@/lib/api/client')

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  })
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )
  }
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('useApiQuery', () => {
  it('returns loading state initially then data', async () => {
    const mockData = [{ id: '1', title: 'Task' }]
    ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue(mockData)

    const { result } = renderHook(
      () => useApiQuery(['tasks'], '/tasks'),
      { wrapper: createWrapper() },
    )

    expect(result.current.isPending).toBe(true)

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual(mockData)
  })

  it('returns error state when request fails', async () => {
    const error = new Error('Network error')
    ;(api.get as ReturnType<typeof vi.fn>).mockRejectedValue(error)

    const { result } = renderHook(
      () => useApiQuery(['tasks'], '/tasks', undefined, { retry: false }),
      { wrapper: createWrapper() },
    )

    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(result.current.error).toBeDefined()
  })

  it('passes params to api.get', async () => {
    ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue([])

    renderHook(
      () => useApiQuery(['tasks'], '/tasks', { params: { limit: 10 } }),
      { wrapper: createWrapper() },
    )

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/tasks', { params: { limit: 10 } })
    })
  })

  it('merges custom options', async () => {
    ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue([])

    renderHook(
      () => useApiQuery(['tasks'], '/tasks', undefined, { staleTime: 5000 }),
      { wrapper: createWrapper() },
    )
  })
})

describe('useApiMutation', () => {
  it('calls api.post on mutate by default', async () => {
    const mockResponse = { id: '1' }
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse)

    const { result } = renderHook(
      () => useApiMutation('/tasks'),
      { wrapper: createWrapper() },
    )

    result.current.mutate({ title: 'New Task' })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(api.post).toHaveBeenCalledWith('/tasks', { title: 'New Task' })
  })

  it('calls api.delete when method is delete', async () => {
    ;(api.delete as ReturnType<typeof vi.fn>).mockResolvedValue({ success: true })

    const { result } = renderHook(
      () => useApiMutation('/tasks/1', 'delete'),
      { wrapper: createWrapper() },
    )

    result.current.mutate(undefined as unknown as void)

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(api.delete).toHaveBeenCalledWith('/tasks/1')
  })

  it('handles mutation error', async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Failed'))

    const { result } = renderHook(
      () => useApiMutation('/tasks'),
      { wrapper: createWrapper() },
    )

    result.current.mutate({ title: 'Fail' })

    await waitFor(() => expect(result.current.isError).toBe(true))
  })

  it('calls onSuccess callback', async () => {
    const mockResponse = { id: '1' }
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse)
    const onSuccess = vi.fn()

    const { result } = renderHook(
      () => useApiMutation('/tasks', 'post', { onSuccess }),
      { wrapper: createWrapper() },
    )

    result.current.mutate({ title: 'Task' })

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled()
    })
  })
})

describe('useApiInfiniteQuery', () => {
  it('fetches first page', async () => {
    const mockData = { data: [{ id: '1' }], count: 1 }
    ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue(mockData)

    const { result } = renderHook(
      () => useApiInfiniteQuery(['items'], '/items', 20),
      { wrapper: createWrapper() },
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.pages[0]).toEqual(mockData)
  })

  it('passes limit and offset params', async () => {
    ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: [], count: 0 })

    renderHook(
      () => useApiInfiniteQuery(['items'], '/items', 10),
      { wrapper: createWrapper() },
    )

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/items', { params: { limit: 10, offset: 0 } })
    })
  })
})
