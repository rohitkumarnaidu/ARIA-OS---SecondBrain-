import { describe, it, expect } from 'vitest'
import { ApiError, NetworkError, TimeoutError, type ApiErrorResponse } from '@/lib/api/errors'

describe('ApiError', () => {
  const defaultArgs: ConstructorParameters<typeof ApiError> = [
    'Not found',
    404,
    'NOT_FOUND',
    'req-123',
    '2026-06-24T12:00:00Z',
  ]

  it('creates an error with all fields', () => {
    const err = new ApiError(...defaultArgs)
    expect(err).toBeInstanceOf(Error)
    expect(err.name).toBe('ApiError')
    expect(err.message).toBe('Not found')
    expect(err.statusCode).toBe(404)
    expect(err.errorCode).toBe('NOT_FOUND')
    expect(err.requestId).toBe('req-123')
    expect(err.timestamp).toBe('2026-06-24T12:00:00Z')
  })

  it('isClientError returns true for 4xx', () => {
    expect(new ApiError(...defaultArgs).isClientError).toBe(true)
    expect(new ApiError('err', 500, 'ERR', 'r', 't').isClientError).toBe(false)
  })

  it('isServerError returns true for 5xx', () => {
    expect(new ApiError('err', 500, 'ERR', 'r', 't').isServerError).toBe(true)
    expect(new ApiError(...defaultArgs).isServerError).toBe(false)
  })

  it('isNotFound returns true for 404', () => {
    expect(new ApiError(...defaultArgs).isNotFound).toBe(true)
    expect(new ApiError('err', 403, 'ERR', 'r', 't').isNotFound).toBe(false)
  })

  it('isRateLimited returns true for 429', () => {
    expect(new ApiError('err', 429, 'ERR', 'r', 't').isRateLimited).toBe(true)
    expect(new ApiError(...defaultArgs).isRateLimited).toBe(false)
  })

  it('isUnauthorized returns true for 401', () => {
    expect(new ApiError('err', 401, 'ERR', 'r', 't').isUnauthorized).toBe(true)
    expect(new ApiError(...defaultArgs).isUnauthorized).toBe(false)
  })

  it('isForbidden returns true for 403', () => {
    expect(new ApiError('err', 403, 'ERR', 'r', 't').isForbidden).toBe(true)
    expect(new ApiError(...defaultArgs).isForbidden).toBe(false)
  })

  it('isValidationError returns true for 422', () => {
    expect(new ApiError('err', 422, 'ERR', 'r', 't').isValidationError).toBe(true)
    expect(new ApiError(...defaultArgs).isValidationError).toBe(false)
  })

  it('fromResponse creates ApiError from ApiErrorResponse', () => {
    const response: ApiErrorResponse = {
      detail: 'Task not found',
      error_code: 'TASK_NOT_FOUND',
      request_id: 'req-456',
      timestamp: '2026-06-24T13:00:00Z',
    }
    const err = ApiError.fromResponse(response, 404)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.message).toBe('Task not found')
    expect(err.statusCode).toBe(404)
    expect(err.errorCode).toBe('TASK_NOT_FOUND')
    expect(err.requestId).toBe('req-456')
    expect(err.timestamp).toBe('2026-06-24T13:00:00Z')
  })

  it('instanceof narrowing works', () => {
    const err = new ApiError('test', 400, 'ERR', 'r', 't')
    expect(err instanceof ApiError).toBe(true)
    expect(err instanceof Error).toBe(true)
  })
})

describe('NetworkError', () => {
  it('creates with default message', () => {
    const err = new NetworkError()
    expect(err).toBeInstanceOf(Error)
    expect(err.name).toBe('NetworkError')
    expect(err.message).toBe('Network request failed. Check your internet connection.')
  })

  it('creates with custom message', () => {
    const err = new NetworkError('Custom message')
    expect(err.message).toBe('Custom message')
  })

  it('instanceof narrowing works', () => {
    const err = new NetworkError()
    expect(err instanceof NetworkError).toBe(true)
    expect(err instanceof Error).toBe(true)
  })
})

describe('TimeoutError', () => {
  it('creates with default message', () => {
    const err = new TimeoutError()
    expect(err).toBeInstanceOf(Error)
    expect(err.name).toBe('TimeoutError')
    expect(err.message).toBe('Request timed out. Please try again.')
  })

  it('creates with custom message', () => {
    const err = new TimeoutError('Custom timeout')
    expect(err.message).toBe('Custom timeout')
  })

  it('instanceof narrowing works', () => {
    const err = new TimeoutError()
    expect(err instanceof TimeoutError).toBe(true)
    expect(err instanceof Error).toBe(true)
  })
})
