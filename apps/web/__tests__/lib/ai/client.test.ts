import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { AIStreamClient, aiStream } from '@/lib/ai/client'
import { ApiError, NetworkError, TimeoutError } from '@/lib/api/errors'

function mockFetch(opts?: { ok?: boolean; status?: number; body?: unknown; contentType?: string }): void {
  const { ok = true, status = 200, body = { message: 'ok' }, contentType = 'application/json' } = opts || {}
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok,
    status,
    headers: new Headers({ 'content-type': contentType }),
    json: () => Promise.resolve(body),
    body: null,
  } as Response)
}

function mockStreamFetch(chunks: string[]): void {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk))
      }
      controller.close()
    },
  })
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    headers: new Headers({ 'content-type': 'text/event-stream' }),
    body: stream,
  } as unknown as Response)
}

describe('AIStreamClient', () => {
  let client: AIStreamClient
  let onChunk: ReturnType<typeof vi.fn>
  let onDone: ReturnType<typeof vi.fn>
  let onError: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
    client = new AIStreamClient()
    client.resetCircuitBreaker()
    onChunk = vi.fn()
    onDone = vi.fn()
    onError = vi.fn()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // ─── Circuit Breaker ──────────────────────────────────────────────────────

  it('circuit breaker starts closed', () => {
    expect(client.getCircuitBreakerState()).toBe('closed')
  })

  it('circuit breaker opens after 5 failures and blocks requests', async () => {
    for (let i = 0; i < 5; i++) {
      client['recordFailure']()
    }
    expect(client.getCircuitBreakerState()).toBe('open')

    await client.sendMessage('hello', undefined, onChunk, onDone, onError)
    expect(onError).toHaveBeenCalledWith(
      new Error('AI service temporarily unavailable. Please try again in a minute.')
    )
    expect(onChunk).not.toHaveBeenCalled()
  })

  it('circuit breaker transitions half-open after 60s cooldown', async () => {
    for (let i = 0; i < 5; i++) {
      client['recordFailure']()
    }
    expect(client.getCircuitBreakerState()).toBe('open')

    vi.advanceTimersByTime(61000)
    mockFetch()

    await client.sendMessage('hello', undefined, onChunk, onDone, onError)
    expect(onDone).toHaveBeenCalledWith('ok')
    expect(client.getCircuitBreakerState()).toBe('closed')
  })

  it('circuit breaker does not transition half-open before 60s', async () => {
    for (let i = 0; i < 5; i++) {
      client['recordFailure']()
    }
    vi.advanceTimersByTime(30000)
    expect(client['isCircuitOpen']()).toBe(true)
    expect(client.getCircuitBreakerState()).toBe('open')
  })

  it('recordSuccess resets circuit breaker', () => {
    for (let i = 0; i < 4; i++) {
      client['recordFailure']()
    }
    expect(client['circuitBreaker'].failures).toBe(4)
    client['recordSuccess']()
    expect(client['circuitBreaker'].failures).toBe(0)
    expect(client['circuitBreaker'].state).toBe('closed')
  })

  it('resetCircuitBreaker restores defaults', () => {
    client['circuitBreaker'] = { failures: 99, lastFailureTime: Date.now(), state: 'open' }
    client.resetCircuitBreaker()
    expect(client.getCircuitBreakerState()).toBe('closed')
    expect(client['circuitBreaker'].failures).toBe(0)
    expect(client['circuitBreaker'].lastFailureTime).toBeNull()
  })

  // ─── sendMessage – success ───────────────────────────────────────────────

  it('sendMessage handles success with JSON response', async () => {
    mockFetch({ body: { message: 'Hello, world!' } })
    await client.sendMessage('hello', undefined, onChunk, onDone, onError)
    expect(onChunk).toHaveBeenCalledWith('Hello, world!')
    expect(onDone).toHaveBeenCalledWith('Hello, world!')
    expect(onError).not.toHaveBeenCalled()
  })

  it('sendMessage passes threadId in request body', async () => {
    let capturedBody = ''
    globalThis.fetch = vi.fn().mockImplementation(async (_url: string, opts: RequestInit) => {
      capturedBody = opts.body as string
      return {
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ message: 'ok' }),
      } as Response
    })

    await client.sendMessage('hello', 'thread-123', onChunk, onDone, onError)
    const parsed = JSON.parse(capturedBody)
    expect(parsed.conversation_id).toBe('thread-123')
    expect(parsed.message).toBe('hello')
  })

  it('sendMessage reads content field from JSON response', async () => {
    mockFetch({ body: { content: 'from content field' } })
    await client.sendMessage('hi', undefined, onChunk, onDone, onError)
    expect(onDone).toHaveBeenCalledWith('from content field')
  })

  it('sendMessage falls back to JSON.stringify if message/content missing', async () => {
    mockFetch({ body: { unexpected: 'data' } })
    await client.sendMessage('hi', undefined, onChunk, onDone, onError)
    expect(onDone).toHaveBeenCalledWith(expect.stringContaining('unexpected'))
  })

  // ─── Streaming ───────────────────────────────────────────────────────────

  it('sendMessage handles SSE streaming chunks', async () => {
    mockStreamFetch([
      'data: {"content":"Hello"}\n',
      'data: {"content":" world","agent":"planner"}\n',
      'data: [DONE]\n',
    ])

    await client.sendMessage('hi', undefined, onChunk, onDone, onError)
    expect(onChunk).toHaveBeenCalledTimes(2)
    expect(onChunk).toHaveBeenNthCalledWith(1, 'Hello', undefined)
    expect(onChunk).toHaveBeenNthCalledWith(2, ' world', 'planner')
    expect(onDone).toHaveBeenCalledWith('Hello world')
  })

  it('sendMessage handles streaming with delta field', async () => {
    mockStreamFetch([
      'data: {"delta":"yes"}\n',
      'data: {"delta":" indeed"}\n',
    ])
    await client.sendMessage('hi', undefined, onChunk, onDone, onError)
    expect(onDone).toHaveBeenCalledWith('yes indeed')
  })

  it('sendMessage handles non-JSON SSE data', async () => {
    mockStreamFetch(['data: raw text\n'])
    await client.sendMessage('hi', undefined, onChunk, onDone, onError)
    expect(onChunk).toHaveBeenCalledWith('raw text')
    expect(onDone).toHaveBeenCalledWith('raw text')
  })

  // ─── Errors ──────────────────────────────────────────────────────────────

  it('sendMessage handles 4xx client error immediately', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: () => Promise.resolve({ detail: 'Bad request', error_code: 'BAD_REQ', request_id: 'r1', timestamp: 'now' }),
    } as Response)

    await client.sendMessage('bad', undefined, onChunk, onDone, onError)
    expect(onError).toHaveBeenCalledWith(expect.any(ApiError))
    expect(onError.mock.calls[0][0].message).toBe('Bad request')
    expect(onError.mock.calls[0][0].statusCode).toBe(400)
  })

  it('sendMessage retries on 5xx and then succeeds', async () => {
    let attempts = 0
    globalThis.fetch = vi.fn().mockImplementation(async () => {
      attempts++
      if (attempts <= 2) {
        return {
          ok: false,
          status: 502,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: () => Promise.resolve({ detail: 'Bad gateway', error_code: 'SRV_ERR', request_id: 'r1', timestamp: 'now' }),
        } as Response
      }
      return {
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ message: 'recovered' }),
      } as Response
    })

    const sendPromise = client.sendMessage('hello', undefined, onChunk, onDone, onError)
    await vi.advanceTimersByTimeAsync(5000)
    await sendPromise

    expect(attempts).toBe(3)
    expect(onDone).toHaveBeenCalledWith('recovered')
  })

  it('sendMessage fails after exhausting retries on 5xx', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: () => Promise.resolve({ detail: 'Service unavailable', error_code: 'SRV_ERR', request_id: 'r1', timestamp: 'now' }),
    } as Response)

    const sendPromise = client.sendMessage('hello', undefined, onChunk, onDone, onError)
    await vi.advanceTimersByTimeAsync(10000)
    await sendPromise

    expect(onError).toHaveBeenCalledWith(expect.any(ApiError))
    expect(onError.mock.calls[0][0].message).toBe('Service unavailable')
  })

  it('sendMessage handles network error and returns NetworkError', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
    await client.sendMessage('hello', undefined, onChunk, onDone, onError)
    expect(onError).toHaveBeenCalledWith(expect.any(NetworkError))
    expect(onError.mock.calls[0][0].message).toContain('AI service unreachable')
  })

  it('sendMessage does NOT retry on TypeError (bubbles immediately)', async () => {
    let attempts = 0
    globalThis.fetch = vi.fn().mockImplementation(async () => {
      attempts++
      throw new TypeError('Failed to fetch')
    })

    await client.sendMessage('hello', undefined, onChunk, onDone, onError)
    // TypeError is not retried (attempt < MAX_RETRIES && !(error instanceof TypeError) → false)
    expect(attempts).toBe(1)
  })

  it('sendMessage handles missing response body in stream', async () => {
    // The missing body causes a throw → retry loop → eventually NetworkError
    // because the error is a regular Error (not TypeError), it IS retried
    const expectedDelay = 1000 + 2000 + 4000 // 3 retries
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'text/event-stream' }),
      body: null,
    } as unknown as Response)

    const sendPromise = client.sendMessage('hello', undefined, onChunk, onDone, onError)
    await vi.advanceTimersByTimeAsync(expectedDelay + 1000)
    await sendPromise

    expect(onError).toHaveBeenCalledWith(expect.any(NetworkError))
  })

  // ─── cancel ──────────────────────────────────────────────────────────────

  it('cancel is safe and does not emit callbacks', async () => {
    client.cancel()
    expect(onChunk).not.toHaveBeenCalled()
    expect(onDone).not.toHaveBeenCalled()
    expect(onError).not.toHaveBeenCalled()
  })

  it('cancel is safe when no request in-flight', () => {
    expect(() => client.cancel()).not.toThrow()
  })

  it('sendMessage does not retry on abort', async () => {
    const fetchSpy = vi.fn().mockImplementation(async (_url: string, opts: RequestInit) => {
      return new Promise<Response>((_resolve, reject) => {
        setTimeout(() => reject(new DOMException('Aborted', 'AbortError')), 10)
      })
    })
    globalThis.fetch = fetchSpy

    client.sendMessage('hello', undefined, onChunk, onDone, onError)
    client.cancel()
    await vi.advanceTimersByTimeAsync(5000)

    expect(fetchSpy).toHaveBeenCalledTimes(1)
  })

  it('cancel is safe when called multiple times', () => {
    expect(() => {
      client.cancel()
      client.cancel()
      client.cancel()
    }).not.toThrow()
  })

  // ─── getCircuitBreakerState ──────────────────────────────────────────────

  it('getCircuitBreakerState returns current state string', () => {
    expect(client.getCircuitBreakerState()).toBe('closed')
    client['circuitBreaker'].state = 'open'
    expect(client.getCircuitBreakerState()).toBe('open')
  })
})
