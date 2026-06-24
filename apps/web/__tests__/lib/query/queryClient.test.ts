import { describe, it, expect } from 'vitest'
import { makeQueryClient } from '@/lib/query/queryClient'

describe('makeQueryClient', () => {
  it('creates a QueryClient instance', () => {
    const client = makeQueryClient()
    expect(client).toBeDefined()
    expect(client.getDefaultOptions()).toBeDefined()
  })

  it('has default staleTime of 30s', () => {
    const client = makeQueryClient()
    const defaultOptions = client.getDefaultOptions()
    expect(defaultOptions.queries?.staleTime).toBe(30 * 1000)
  })

  it('has default gcTime of 5 minutes', () => {
    const client = makeQueryClient()
    const defaultOptions = client.getDefaultOptions()
    expect(defaultOptions.queries?.gcTime).toBe(5 * 60 * 1000)
  })

  it('has retry count of 2', () => {
    const client = makeQueryClient()
    const defaultOptions = client.getDefaultOptions()
    expect(defaultOptions.queries?.retry).toBe(2)
  })

  it('has retryDelay with exponential backoff', () => {
    const client = makeQueryClient()
    const defaultOptions = client.getDefaultOptions()
    const retryDelay = defaultOptions.queries?.retryDelay as (attempt: number) => number
    expect(typeof retryDelay).toBe('function')
    expect(retryDelay(0)).toBe(1000)
    expect(retryDelay(1)).toBe(2000)
    expect(retryDelay(2)).toBe(4000)
    expect(retryDelay(10)).toBe(10000) // capped at 10s
  })

  it('has refetchOnWindowFocus set to false', () => {
    const client = makeQueryClient()
    const defaultOptions = client.getDefaultOptions()
    expect(defaultOptions.queries?.refetchOnWindowFocus).toBe(false)
  })

  it('defines mutations.onError handler', () => {
    const client = makeQueryClient()
    const defaultOptions = client.getDefaultOptions()
    expect(defaultOptions.mutations?.onError).toBeDefined()
    expect(typeof defaultOptions.mutations?.onError).toBe('function')
  })

  it('creates independent instances', () => {
    const client1 = makeQueryClient()
    const client2 = makeQueryClient()
    expect(client1).not.toBe(client2)
  })
})
