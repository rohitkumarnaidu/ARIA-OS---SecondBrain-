const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const DEFAULT_TIMEOUT = 30000
const MAX_RETRIES = 3
const RETRY_DELAYS = [1000, 2000, 4000]

interface RequestConfig extends RequestInit {
  timeout?: number
  retries?: number
  params?: Record<string, string | number | boolean | undefined>
}

interface CircuitBreakerState {
  failures: number
  lastFailureTime: number | null
  state: 'closed' | 'open' | 'half-open'
}

class ApiClient {
  private circuitBreaker: CircuitBreakerState = {
    failures: 0,
    lastFailureTime: null,
    state: 'closed',
  }

  private readonly threshold = 5
  private readonly cooldown = 60000

  private generateRequestId(): string {
    return crypto.randomUUID()
  }

  private isCircuitOpen(): boolean {
    if (this.circuitBreaker.state === 'open') {
      const now = Date.now()
      if (this.circuitBreaker.lastFailureTime && (now - this.circuitBreaker.lastFailureTime) > this.cooldown) {
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
    if (this.circuitBreaker.failures >= this.threshold) {
      this.circuitBreaker.state = 'open'
    }
  }

  private recordSuccess(): void {
    this.circuitBreaker.failures = 0
    this.circuitBreaker.state = 'closed'
  }

  private buildUrl(path: string, params?: Record<string, string | number | boolean | undefined>): string {
    const url = new URL(`${API_BASE_URL}${path}`)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.set(key, String(value))
        }
      })
    }
    return url.toString()
  }

  private async request<T>(path: string, config: RequestConfig = {}): Promise<T> {
    if (this.isCircuitOpen()) {
      throw new Error('Circuit breaker is open. Service temporarily unavailable.')
    }

    const { timeout = DEFAULT_TIMEOUT, retries = MAX_RETRIES, params, ...fetchConfig } = config
    const requestId = this.generateRequestId()
    const url = this.buildUrl(path, params)

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    let lastError: Error | null = null

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          ...fetchConfig,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            'X-Request-ID': requestId,
            ...fetchConfig.headers,
          },
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          if (response.status >= 500) {
            this.recordFailure()
          }
          const errorBody = await response.json().catch(() => ({ detail: response.statusText }))
          const error = new Error(errorBody.detail || `HTTP ${response.status}`)
          ;(error as any).statusCode = response.status
          ;(error as any).requestId = requestId
          throw error
        }

        this.recordSuccess()
        return await response.json()
      } catch (error: unknown) {
        lastError = error as Error

        if (error instanceof DOMException && error.name === 'AbortError') {
          throw new Error('Request timed out. Please try again.')
        }

        if (attempt < retries && (error as any)?.statusCode >= 500) {
          const delay = RETRY_DELAYS[attempt] || RETRY_DELAYS[RETRY_DELAYS.length - 1]
          await new Promise(resolve => setTimeout(resolve, delay))
          continue
        }

        if ((error as any)?.statusCode) {
          throw error
        }

        throw new Error('Network request failed. Check your internet connection.')
      }
    }

    throw lastError || new Error('Request failed')
  }

  async get<T>(path: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, { ...config, method: 'GET' })
  }

  async post<T>(path: string, body?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, {
      ...config,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async put<T>(path: string, body?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, {
      ...config,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async patch<T>(path: string, body?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, {
      ...config,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async delete<T>(path: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(path, { ...config, method: 'DELETE' })
  }

  getCircuitBreakerState(): string {
    return this.circuitBreaker.state
  }

  resetCircuitBreaker(): void {
    this.circuitBreaker = { failures: 0, lastFailureTime: null, state: 'closed' }
  }
}

export const api = new ApiClient()
export type { RequestConfig }
