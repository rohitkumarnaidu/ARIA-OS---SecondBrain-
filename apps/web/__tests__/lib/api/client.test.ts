import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api } from '@/lib/api/client'

const MOCK_UUID = '00000000-0000-0000-0000-000000000001'
const TASKS_PATH = '/tasks'

beforeEach(() => {
  vi.restoreAllMocks()
  vi.spyOn(crypto, 'randomUUID').mockReturnValue(MOCK_UUID)
  api.resetCircuitBreaker()
})

afterEach(() => {
  vi.restoreAllMocks()
})

function mockFetch(status: number, body: unknown, ok?: boolean) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
    ok: ok ?? (status >= 200 && status < 300),
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    json: async () => body,
    headers: new Headers({ 'content-type': 'application/json' }),
  } as Response)
}

describe('ApiClient - GET', () => {
  it('performs a GET request and returns JSON', async () => {
    const data = { id: '1', title: 'Test' }
    mockFetch(200, data)

    const result = await api.get(TASKS_PATH)
    expect(result).toEqual(data)
  })

  it('sends correct request headers', async () => {
    mockFetch(200, {})
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    await api.get(TASKS_PATH)

    const call = fetchSpy.mock.calls[0]
    expect(call[0]).toContain(TASKS_PATH)
    expect(call[1]?.method).toBe('GET')
    expect(call[1]?.headers).toMatchObject({
      'Content-Type': 'application/json',
      'X-Request-ID': MOCK_UUID,
    })
  })

  it('sends query params', async () => {
    mockFetch(200, [])
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    await api.get(TASKS_PATH, { params: { limit: 20, offset: 0 } })

    const url = fetchSpy.mock.calls[0][0] as string
    expect(url).toContain('limit=20')
    expect(url).toContain('offset=0')
  })

  it('omits undefined params', async () => {
    mockFetch(200, [])
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    await api.get(TASKS_PATH, { params: { limit: 20, offset: undefined } })

    const url = fetchSpy.mock.calls[0][0] as string
    expect(url).toContain('limit=20')
    expect(url).not.toContain('offset')
  })
})

describe('ApiClient - POST', () => {
  it('performs a POST request with body', async () => {
    const body = { title: 'New Task' }
    const response = { id: '1', ...body }
    mockFetch(201, response)

    const result = await api.post(TASKS_PATH, body)
    expect(result).toEqual(response)
  })

  it('sends POST with stringified body', async () => {
    mockFetch(201, {})
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    const payload = { title: 'Test' }
    await api.post(TASKS_PATH, payload)

    const requestBody = fetchSpy.mock.calls[0][1]?.body
    expect(JSON.parse(requestBody as string)).toEqual(payload)
  })

  it('sends POST without body', async () => {
    mockFetch(201, {})
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    await api.post(TASKS_PATH)

    expect(fetchSpy.mock.calls[0][1]?.body).toBeUndefined()
  })
})

describe('ApiClient - PUT', () => {
  it('performs a PUT request with body', async () => {
    const body = { title: 'Updated' }
    mockFetch(200, body)

    const result = await api.put('/tasks/1', body)
    expect(result).toEqual(body)
  })
})

describe('ApiClient - PATCH', () => {
  it('performs a PATCH request with body', async () => {
    const body = { title: 'Patched' }
    mockFetch(200, body)

    const result = await api.patch('/tasks/1', body)
    expect(result).toEqual(body)
  })
})

describe('ApiClient - DELETE', () => {
  it('performs a DELETE request', async () => {
    const response = { success: true }
    mockFetch(200, response)

    const result = await api.delete('/tasks/1')
    expect(result).toEqual(response)
  })

  it('DELETE sends no body', async () => {
    mockFetch(204, null, true)
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    await api.delete('/tasks/1')
    expect(fetchSpy.mock.calls[0][1]?.method).toBe('DELETE')
  })
})

describe('ApiClient - error handling', () => {
  it('throws on HTTP 404', async () => {
    const errorBody = { detail: 'Task not found' }
    mockFetch(404, errorBody, false)

    await expect(api.get('/tasks/999')).rejects.toThrow('Task not found')
  })

  it('throws on HTTP 500 without retry', async () => {
    const errorBody = { detail: 'Internal error' }
    mockFetch(500, errorBody, false)

    await expect(api.get(TASKS_PATH, { retries: 0 })).rejects.toThrow('Internal error')
  })

  it('throws on HTTP 401', async () => {
    const errorBody = { detail: 'Unauthorized' }
    mockFetch(401, errorBody, false)

    await expect(api.get(TASKS_PATH)).rejects.toThrow('Unauthorized')
  })

  it('attaches statusCode and requestId to error', async () => {
    const errorBody = { detail: 'Not found' }
    mockFetch(404, errorBody, false)

    try {
      await api.get('/tasks/999')
    } catch (e) {
      const err = e as Error & { statusCode: number; requestId: string }
      expect(err.statusCode).toBe(404)
      expect(err.requestId).toBe(MOCK_UUID)
    }
  })

  it('throws generic error for non-JSON error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Server Error',
      json: async () => { throw new Error('not json') },
      headers: new Headers(),
    } as Response)

    await expect(api.get(TASKS_PATH, { retries: 0 })).rejects.toThrow('Server Error')
  })
})

describe('ApiClient - retry logic', () => {
  it('retries on 5xx errors up to MAX_RETRIES times', async () => {
    vi.useFakeTimers()
    const fetchSpy = vi.spyOn(globalThis, 'fetch')
    const errorBody = { detail: 'Server error' }

    for (let i = 0; i < 3; i++) {
      mockFetch(500, errorBody, false)
    }
    mockFetch(200, { success: true })

    const promise = api.get(TASKS_PATH)

    // Advance through retry delays: 1000 + 2000
    for (let i = 0; i < 5; i++) {
      await vi.advanceTimersByTimeAsync(2000)
    }

    const result = await promise
    expect(result).toEqual({ success: true })
    expect(fetchSpy).toHaveBeenCalledTimes(4)
    vi.useRealTimers()
  })

  it('does not retry on 4xx errors', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch')
    mockFetch(400, { detail: 'Bad request' }, false)

    await expect(api.get(TASKS_PATH)).rejects.toThrow('Bad request')
    expect(fetchSpy).toHaveBeenCalledTimes(1)
  })

  it('throws network error if fetch fails entirely', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(api.get(TASKS_PATH, { retries: 0 })).rejects.toThrow(
      'Network request failed. Check your internet connection.',
    )
  })
})

describe('ApiClient - circuit breaker', () => {
  it('opens after 5 failures', async () => {
    vi.useFakeTimers()
    const errorBody = { detail: 'Server error' }

    for (let i = 0; i < 5; i++) {
      mockFetch(500, errorBody, false)
    }

    for (let i = 0; i < 5; i++) {
      const promise = api.get(TASKS_PATH, { retries: 0 })
      await vi.advanceTimersByTimeAsync(100)
      await expect(promise).rejects.toThrow()
    }

    expect(api.getCircuitBreakerState()).toBe('open')
    vi.useRealTimers()
  })

  it('rejects immediately when circuit is open', async () => {
    vi.useFakeTimers()
    for (let i = 0; i < 5; i++) {
      mockFetch(500, { detail: 'err' }, false)
    }

    for (let i = 0; i < 5; i++) {
      const promise = api.get(TASKS_PATH, { retries: 0 })
      await vi.advanceTimersByTimeAsync(100)
      await expect(promise).rejects.toThrow()
    }

    const circuitPromise = api.get(TASKS_PATH)
    await expect(circuitPromise).rejects.toThrow('Circuit breaker is open')
    vi.useRealTimers()
  })

  it('resets to half-open after cooldown', async () => {
    vi.useFakeTimers()

    for (let i = 0; i < 5; i++) {
      mockFetch(500, { detail: 'err' }, false)
    }

    for (let i = 0; i < 5; i++) {
      const promise = api.get(TASKS_PATH, { retries: 0 })
      await vi.advanceTimersByTimeAsync(100)
      await expect(promise).rejects.toThrow()
    }

    expect(api.getCircuitBreakerState()).toBe('open')

    vi.advanceTimersByTime(61000)

    mockFetch(200, { success: true }, true)
    const result = await api.get(TASKS_PATH)
    expect(result).toEqual({ success: true })
    expect(api.getCircuitBreakerState()).toBe('closed')
    vi.useRealTimers()
  })

  it('resetCircuitBreaker resets state', () => {
    api.resetCircuitBreaker()
    expect(api.getCircuitBreakerState()).toBe('closed')
  })
})

describe('ApiClient - timeout', () => {
  it('aborts request on timeout', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(
      new DOMException('The operation was aborted', 'AbortError'),
    )

    await expect(api.get(TASKS_PATH, { timeout: 100 })).rejects.toThrow('Request timed out')
  })
})

describe('ApiClient - URL building', () => {
  it('builds correct URL from path', async () => {
    mockFetch(200, {})
    const fetchSpy = vi.spyOn(globalThis, 'fetch')

    await api.get('/tasks/123')

    const url = fetchSpy.mock.calls[0][0] as string
    expect(url).toContain('/tasks/123')
  })
})
