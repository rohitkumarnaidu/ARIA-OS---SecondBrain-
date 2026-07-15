import { ApiError, NetworkError, TimeoutError } from '@/lib/api/errors'

const AI_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const DEFAULT_TIMEOUT = 30000
const MAX_RETRIES = 3
const RETRY_DELAYS = [1000, 2000, 4000]

interface CircuitBreakerState {
  failures: number
  lastFailureTime: number | null
  state: 'closed' | 'open' | 'half-open'
}

function generateRequestId(): string {
  return crypto.randomUUID()
}

async function fetchWithTimeout(url: string, options: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, { ...options, signal: controller.signal })
    return response
  } finally {
    clearTimeout(timer)
  }
}

export class AIStreamClient {
  private abortController: AbortController | null = null
  private circuitBreaker: CircuitBreakerState = { failures: 0, lastFailureTime: null, state: 'closed' }

  private isCircuitOpen(): boolean {
    if (this.circuitBreaker.state === 'open') {
      const now = Date.now()
      if (this.circuitBreaker.lastFailureTime && now - this.circuitBreaker.lastFailureTime > 60000) {
        this.circuitBreaker.state = 'half-open'
        return false
      }
      return true
    }
    return false
  }

  private recordFailure(): void {
    this.circuitBreaker.failures++
    this.circuitBreaker.lastFailureTime = Date.now()
    if (this.circuitBreaker.failures >= 5) {
      this.circuitBreaker.state = 'open'
    }
  }

  private recordSuccess(): void {
    this.circuitBreaker.failures = 0
    this.circuitBreaker.state = 'closed'
  }

  async sendMessage(
    message: string,
    threadId: string | undefined,
    onChunk: (chunk: string, agent?: string) => void,
    onDone: (fullText: string) => void,
    onError: (error: Error) => void,
  ): Promise<void> {
    if (this.isCircuitOpen()) {
      onError(new Error('AI service temporarily unavailable. Please try again in a minute.'))
      return
    }

    this.abortController = new AbortController()
    const requestId = generateRequestId()
    const fullText: string[] = []
    const params = new URLSearchParams({ stream: 'true' })

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        const response = await fetchWithTimeout(
          `${AI_API_BASE}/api/v1/chat/?${params}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Request-ID': requestId,
            },
            body: JSON.stringify({ message, conversation_id: threadId }),
            signal: this.abortController.signal,
          },
          DEFAULT_TIMEOUT,
        )

        if (!response.ok) {
          const errorBody = await response.json().catch(() => ({ detail: response.statusText }))
          if (response.status >= 500) {
            this.recordFailure()
            if (attempt < MAX_RETRIES) {
              await new Promise(r => setTimeout(r, RETRY_DELAYS[attempt]))
              continue
            }
          }
          throw new ApiError(
            errorBody.detail || `Chat request failed (${response.status})`,
            response.status,
            errorBody.error_code || 'AI_CHAT_ERROR',
            requestId,
            new Date().toISOString(),
          )
        }

        this.recordSuccess()
        const contentType = response.headers.get('content-type') || ''

        if (contentType.includes('text/event-stream')) {
          const reader = response.body?.getReader()
          const decoder = new TextDecoder()
          if (!reader) throw new Error('No response body from AI stream')

          let buffer = ''
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6).trim()
                if (data === '[DONE]') continue
                try {
                  const parsed = JSON.parse(data)
                  if (parsed.done) {
                    onDone(parsed.full_response || fullText.join(''))
                    return
                  }
                  const chunk = parsed.token || parsed.content || parsed.delta || ''
                  if (chunk) {
                    fullText.push(chunk)
                    onChunk(chunk, parsed.agent)
                  }
                } catch {
                  fullText.push(data)
                  onChunk(data)
                }
              }
            }
          }

          onDone(fullText.join(''))
        } else {
          const data = await response.json()
          const text = data.message || data.content || JSON.stringify(data)
          fullText.push(text)
          onChunk(text)
          onDone(text)
        }
        return
      } catch (error: unknown) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }
        if (error instanceof ApiError) {
          onError(error)
          return
        }
        if (attempt < MAX_RETRIES && !(error instanceof TypeError)) {
          await new Promise(r => setTimeout(r, RETRY_DELAYS[attempt]))
          continue
        }
        this.recordFailure()
        onError(new NetworkError('AI service unreachable. Check your connection and try again.'))
        return
      }
    }
  }

  cancel(): void {
    this.abortController?.abort()
    this.abortController = null
  }

  getCircuitBreakerState(): string {
    return this.circuitBreaker.state
  }

  resetCircuitBreaker(): void {
    this.circuitBreaker = { failures: 0, lastFailureTime: null, state: 'closed' }
  }
}

export const aiStream = new AIStreamClient()
